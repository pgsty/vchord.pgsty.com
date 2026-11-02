---
title: "VectorChord：在 AWS 上高性价比地上传与搜索 4 亿向量"
date: 2025-05-30
description: "使用 VectorChord 与 PostgreSQL 上传、构建索引并搜索 4 亿规模向量，包含硬件选型技巧与搜索性能调优建议"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws/"
  - "/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws/"
---

在本文中，我们将介绍一种利用真实世界的 [LAION-400M](https://laion.ai/blog/laion-400-open-dataset/) 数据集和 PostgreSQL 中的 VectorChord 扩展，以高性价比方式上传、构建索引并搜索大规模向量数据的方法。

我们将向您展示需要什么样的硬件配置，才能使用 VectorChord 在这一海量数据集上进行搜索，并确保您获得既准确又快速的搜索体验。

[VectorChord](https://github.com/tensorchord/VectorChord) 是一款 PostgreSQL 扩展，能够将高性能向量数据库能力直接引入您的 PostgreSQL 数据库中，并尽可能高度兼容热门的 pgvector 扩展接口。

本教程所使用的 VectorChord 版本必须为 `v0.3.0` 或更高版本。虽然 VectorChord 兼容大多数近期版本的 pgvector，但我们在测试中主要针对 `pgvector 0.8.0` 进行了全面验证。

## **数据集** {#dataset}

本实验使用的数据集是 [LAION-400M](https://laion.ai/blog/laion-400-open-dataset/)，这是一个包含约 4 亿条图像衍生向量的数据集。每条向量均为 512 维，由 [CLIP](https://openai.com/blog/clip/) 模型生成。

向量数据总量约为 400 GB。这些向量已经过归一化处理，因此可以使用多种距离度量方式（L2、余弦距离、点积）。为了与该数据集上的其他基准测试保持一致，并遵循 CLIP 嵌入本身的特性，我们在本实验中采用了余弦距离（cosine distance）度量。

LAION-400M 被划分为 409 个数据分块（chunks），每个分块包含约 100 万条向量。我们将按顺序处理并上传这些分块。

## **算法** {#algorithm}

在 4 亿条向量中进行搜索是一项巨大的挑战，尤其是庞大的数据量意味着绝大部分数据必须存储在磁盘而非内存中。我们需要专为这种规模量身定制的算法！处理大规模磁盘向量数据的一种流行且高效的方法是基于图的 [DiskANN](https://github.com/microsoft/DiskANN)，它以**低内存和低资源开销**而闻名。

然而，由于衍生自 [HNSW](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world)，DiskANN 也继承了一些固有缺点：

* [**索引构建缓慢**](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#experience-in-index-building)：对于大规模数据集，众所周知，使用 DiskANN 构建索引往往需要耗费漫长的时间。
    
* [**插入性能不佳**](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#insertion-performance-for-stream-generated-data)：对于流式插入的向量，更新基于图的索引需要遍历局部图结构。由于 DiskANN 的磁盘图必须加载到内存中，这一操作的代价更加高昂。
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743503547507/9847a9c4-fcaa-4d76-bf82-3f5c5e959ef4.png?auto=compress,format&format=webp)

VectorChord 通过其 VChordRQ 索引解决了这些问题。VChordRQ 将**基于聚类的索引（IVF）**与巧妙的数据压缩方案 [RaBitQ](https://arxiv.org/abs/2405.12497) 结合在一起。除了在[内存](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#vectors-in-memory-for-small-scale-data)和[磁盘](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#vectors-in-disk-for-large-scale-data)场景下均具备**更优的精度和更低的延迟**外，RaBitQ 的核心优势还在于它拥有严谨的准确度理论下界保证——这与传统的启发式压缩技术截然不同，帮助我们在准确度与效率之间实现了绝佳的平衡！

> [!TIP]
> 有关 VChordRQ（[VectorChord](https://github.com/tensorchord/VectorChord)）、HNSW（[pgvector](https://github.com/pgvector/pgvector)）与 StreamDiskANN（[pgvectorscale](https://github.com/timescale/pgvectorscale)）的更多对比，请参阅我们之前的[博客文章](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/)。

## **硬件配置** {#hardware}

根据我们的实验，以下云实例规格足以在可接受的延迟下完成该数据集的索引构建与查询：

* **实例类型**：AWS EC2 i8g.2xlarge（$501.0720 / 月）
    
* **CPU**：8 vCPUs (ARM64)
    
* **内存**：64GB
    
* **存储**：1875 GB NVMe SSD
    

该配置提供了必要的计算能力以及充裕的高速本地 NVMe 存储。64GB 内存则作为缓存以加速搜索查询。

> [!TIP]
> 我们使用了配备 **1875 GB** NVMe 存储的实例，尽管实际只需要约 **1014 GB**。这是 AWS 上能提供足够高速本地 SSD 的**最低**规格选项。如果能找到存储空间更贴合的机器，还可以进一步降低成本。

在该实例的 PostgreSQL 配置中，我们调整了 `shared_buffers` 参数：

* 在索引构建过程中设置为 48GB。
    
* 在搜索评估阶段上调至 54GB，以便缓存更多数据，提升搜索性能。
    

## **数据上传与索引构建** {#uploading-and-indexing}

VectorChord 的 VChordRQ 索引采用倒排文件（IVF）结构。虽然 VChordRQ 可以在索引构建过程中计算所需的聚类质心（centroids），但面对如此庞大的规模（4 亿向量），在系统外部预先计算好质心能够大幅加快索引构建速度。

针对 LAION-400M，我们在配备 `A10 GPU` 的实例上执行了外部 k-means 聚类步骤来确定这些质心，以加快计算速度：

* 聚类配置为 `nlist = 160000` 个聚类簇。
    
* 聚类共执行 25 次迭代，每次迭代耗时约 220 秒，总计约 1.5 小时。
    

计算出质心后，我们开始部署启用了 VectorChord 的 PostgreSQL 数据库。为了方便起见，我们使用了预构建的 Docker 镜像：

```sql
-- Mount PGDATA path to the NVMe SSD
-- sudo mount /dev/nvme1n1 /data
docker run --name vchord-pg17 \
-e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -v /data/pg:/var/lib/postgresql/data \
-d tensorchord/vchord-postgres:pg17-v0.3.0
```

该 Docker 镜像包含 `PostgreSQL 17`，并预装了 `pgvector 0.8.0` 和 `VectorChord 0.3.0`。

上传流程的核心在于：先将预计算的质心插入到一张专用表中，随后将 LAION 数据集分块中的向量插入主数据表。可以使用 Python 中的 `psycopg` 等客户端库，通过批量插入（batched inserts）高效完成这一操作。

首先，将质心插入质心表（例如 `laion_centroids`）：

```sql
-- The centroids table we created is:
-- CREATE TABLE laion_centroids (id SERIAL PRIMARY KEY, vector vector(512));
INSERT INTO laion_centroids (vector) VALUES ('[...centroid vector...]'); -- Insert all 160000 centroids
```

接着，将数据集中的向量插入主数据表（例如 `laion`）：

```sql
-- The data table we created is:
-- CREATE TABLE laion (id BIGINT PRIMARY KEY, embedding vector(512));
-- Note: VectorChord is compatible with pgvector's vector insert syntax.
INSERT INTO laion (id, embedding) VALUES (0, '[...vector data...]'); -- Batch inserts for chunks
```

插入所有数据后，我们构建 VectorChord 索引（`vchordrq`）。`vchordrq` 代表 [RaBitQ](https://arxiv.org/abs/2405.12497)，这是 VectorChord 基于 IVF 结构并结合量化与高效重排序打造的高度优化索引类型。

```sql
-- Note: The metric operator vector_cosine_ops is specified here, similar to pgvector. 
-- The $$ syntax is used to pass build options as a text block.
CREATE INDEX laion_embedding_idx ON laion USING vchordrq (embedding vector_cosine_ops) WITH (options = $$
[build.external]
table = 'public.laion_centroids' -- Link to the pre-computed centroids
$$);
```

下图展示了在数据上传和索引构建过程中，实例上的系统资源利用率（CPU、内存和磁盘占用）。磁盘占用曲线展示了数据写入阶段（初期陡增）以及随后的索引构建阶段（平稳增长），最终总占用略超 1TB。CPU 和内存曲线则反映了整个过程中消耗的计算与内存资源。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1745721010613/c5d20e21-6c6f-43d4-a915-aa121497d496.png)

## **基准真值数据（Ground Truth）** {#ground-truth-data}

为了准确衡量搜索性能和精度，与真值数据（ground truth）进行比对至关重要。LAION 数据集本身并未附带现成的真值数据。**我们非常感谢 Qdrant 团队公开了他们为该数据集**[教程](https://qdrant.tech/documentation/database-tutorials/large-scale-search/)**所准备的**[**真值数据**](https://github.com/qdrant/laion-400m-benchmark/blob/master/expected.py)。

他们的方法是对数据集中的前 100 条向量执行全表扫描最近邻搜索，找出每条查询向量的前 50 个真实最近邻。我们**使用了完全相同的真值文件**来评估 VectorChord 的搜索精度。

## **搜索查询** {#search-query}

VectorChord 搜索采用两个主要参数来控制性能与精度之间的权衡：`nprobe` 和 `epsilon`。

* **nprobe**：通过 `vchord.probes` 参数进行配置。该参数决定了在初始阶段搜索 IVF 索引中的多少个聚类簇（分区）。较高的 `nprobe` 会扩大搜索范围，有助于找到更优的结果，但也会增加延迟。
    
* **epsilon**：通过 `vchord.epsilon` 参数进行配置。该参数控制重排序的精度。从探测的 `nprobe` 个聚类簇中获取初始候选集后，VectorChord 会使用更精确的向量数据执行重排序。较大的 `epsilon` 意味着会考虑更多候选向量并进行重排序以获得更高的召回率，但同样会增加延迟。
    

在执行搜索查询之前，将这些参数设置为 PostgreSQL 会话变量：

```sql
-- Example settings
SET vchord.probes = 100; -- Configure nprobe
SET vchord.epsilon = 0.8; -- Configure epsilon

-- The search query itself uses the standard pgvector distance operator
SELECT id FROM laion ORDER BY embedding <=> '[...query_vector...]' LIMIT 50;
```

`ORDER BY embedding <=> '[...]'` 子句利用索引，根据指定的距离度量（与 CLIP 一致的余弦距离）查找近似最近邻。`LIMIT 50` 则返回前 50 条结果。

## **执行搜索请求** {#running-search-requests}

索引构建完成后，我们使用不同的 `nprobe` 和 `epsilon` 设置，在 100 条真值查询向量上运行了查询，以测试性能与精度之间的权衡关系。

我们以毫秒（ms）为单位表示搜索延迟。“冷缓存（Cold）”延迟是指目标向量数据需要从磁盘读取的情况，而“热缓存（Warm）”延迟则代表数据已经缓存在内存中。

以下是跨 100 条查询的平均延迟以及对应的 Precision@50 得分：

| **nprob / epsilon** | **冷缓存延迟 (ms)** | **热缓存延迟 (ms)** | **Precision@50** |
| --- | --- | --- | --- |
| 10 / 0.8 | **112.5** | **7.0** | 0.8192 |
| 100 / 0.8 | 194.2 | 15.0 | 0.9216 |
| 200 / 1.0 | 331.2 | 24.9 | 0.9438 |
| 400 / 1.5 | 970.9 | 51.6 | **0.9608** |
| 800 / 1.9 | 2174.0 | 2174.0 | **0.9662** |

上表清晰地展示了这种权衡关系：

* 增大 `nprobe` 和 `epsilon` 通常会带来更高的 Precision@50。
    
* 然而，这是以增加搜索延迟为代价的，在冷缓存场景下尤为明显——因为需要更多的磁盘 I/O 来从更多聚类簇中读取数据，并执行更广泛的重排序。
    
* 热缓存性能明显快得多，凸显了配备足够内存以缓存热点数据的重要性。
    
* 在热缓存下，可以在 50ms 以内的延迟下实现超过 90% 的精度；而若要在此基础上进一步追求极致召回率，则会根据所选参数带来数百毫秒甚至超过一秒的延迟。
    

下图展示了 VectorChord（冷缓存与热缓存）与 Qdrant 在每秒查询数（QPS）和 Precision@50 之间的权衡对比，其中 Qdrant 的数据引自其在同级别 8 vCPU、64 GB 机器上[公开发布的基准测试结果](https://qdrant.tech/documentation/database-tutorials/large-scale-search/#running-search-requests)，而非在同一台物理机器上重跑。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1745753692001/731cb592-86e6-4eef-ae0f-c699df421a33.png)

## **结论** {#conclusion}

在本教程中，我们展示了如何将 VectorChord 作为 PostgreSQL 扩展，在配备高速 NVMe SSD 的中小型硬件上，高性价比地上传、构建索引并搜索多达 4 亿条向量的庞大数据集。

通过结合使用 VectorChord 的 VChordRQ 索引与外部质心构建，我们成功从容应对了这一海量数据规模。在查询时合理设置 `nprobe` 和 `epsilon`，可以精确控制搜索速度与准确度之间的关键权衡，让用户能够根据自身业务需求灵活调优系统。

VectorChord 对 pgvector 接口的良好兼容性降低了现有 pgvector 用户的迁移门槛，而其 `vchordrq` 索引则在稳健、熟悉的 PostgreSQL 环境中直接提供了强大的大规模向量搜索能力。
