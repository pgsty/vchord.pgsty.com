---
title: "VectorChord：在 PostgreSQL 中仅花 $1 存储 40 万向量"
date: 2024-12-05
description: "隆重推出 pgvecto.rs 的继任者 VectorChord。使用 VectorChord，您可以在 1 亿条 768 维向量数据集上以 0.95 的精度实现 131 QPS"
author: "[Ce Gao](https://github.com/gaocegege), [Jinjing Zhou](https://github.com/VoVAllen), [Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-store-400k-vectors-for-1-in-postgresql"
upstream_copyright: "© 2024 Ce Gao, Jinjing Zhou, Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/"
  - "/vectorchord-store-400k-vectors-for-1-in-postgresql/"
---

我们很高兴地宣布推出全新的 PostgreSQL 向量搜索扩展，为大规模向量管理提供极具性价比的解决方案。使用 [VectorChord](https://github.com/tensorchord/VectorChord)，您可以在 1 亿条 768 维向量数据集上执行 Top 10 查询时，以 0.95 的精度实现 131 QPS。整套环境可在单台机器上运行，每月成本仅为 $250。

这意味着您**只需花费 $1 即可存储 40 万条向量**，从而大幅节省成本：在同等价格下，可存储的向量数量是 Pinecone（存储优化型实例）的 6 倍，更是 pgvector/pgvecto.rs 的 26 倍。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733194327962/8b0f2610-af64-4104-98db-7f94416f354e.png)

基于 [MyScale 基准测试数据](https://myscale.github.io/benchmark/#/)的向量存储月度成本对比图清晰地显示，[VectorChord](https://github.com/tensorchord/VectorChord) 是极具性价比的选择，存储 1 亿条向量每月仅需 $247。相比之下，即便采用了优化存储，Pinecone 每月仍需 $1,600，Qdrant 定价为 $4,374，而 pgvector/[pgvecto.rs](/zh/docs/vectors/) 的成本更是高达 $6,580。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733194599461/eb1cf21d-4eb0-4427-8b39-bbb96d125182.png)

%[https://github.com/tensorchord/VectorChord] 

<a id="hnsw-s-problem"></a>
## HNSW 的痛点 {#hnsws-problem}

作为 pgvecto.rs 的继任者，VectorChord 从前代产品中汲取了宝贵的经验。虽然许多向量数据库或扩展（包括 pgvecto.rs）在 100 万左右的数据集规模下表现良好，但当规模扩展到更大体量（例如从 1,000 万增长到 1 亿）时，往往会难以为继。传统的基于 HNSW 的向量数据库在面对大规模数据集时面临着以下具体挑战：

* **漫长的索引构建时间**：为 500 万条记录构建索引通常需要超过 2 小时。
    
* **高昂的内存需求**：存储一个包含 1,000 万条向量的数据集可能需要高达 40GB 的内存。
    

<a id="vectorchord-s-solution-disk-friendly-ivf-rabitq"></a>
## VectorChord 的解决方案：磁盘友好的 IVF+RaBitQ {#vectorchords-solution-disk-friendly-ivfrabitq}

VectorChord 采用 IVF（倒排文件索引）结合 [RaBitQ](https://arxiv.org/pdf/2405.12497)\[1\] 量化技术，提供快速、可扩展且准确的向量搜索能力。该方法**将 32 位浮点向量压缩为紧凑的比特表示**，显著降低了计算开销。绝大部分距离比较都在这些压缩向量上进行，而全精度计算仅保留给针对小规模候选集的自适应重排序（reranking）阶段，从而同时兼顾了速度与召回率。

许多人认为 IVF 在召回率/速度权衡上不如 HNSW，且涉及繁琐的参数调优配置。实际上这是一个较为复杂的话题，我们在此先做简要说明，后续会发布专文进行深度剖析。

### IVF 与 HNSW 对比 {#ivf-vs-hnsw}

向量搜索算法的很大一部分耗时都花在距离计算上。为了提升速度，必须尽可能减少距离比较的次数。原始的 IVF 在这方面表现欠佳，通常需要扫描总向量数的 1% 到 5%，远高于 HNSW 所需的扫描量。

然而，RaBitQ 提出了一种创新方法，能够将 32 位浮点数的每个维度压缩至仅需 1 比特。虽然这种压缩会带来一定的精度损失，但它大幅降低了计算需求。结合快速扫描（fast scan）优化，我们可以实现**比传统向量距离计算快 100 倍以上的计算速度**。

您可能会担心召回率问题。我们可以通过对更多候选向量进行重排序来提高召回率，而全精度距离计算仅在重排序阶段才需要执行。RaBitQ 不仅保证了紧凑的理论误差界，同时在实测中也具备优秀的准确度。这正是 IVF 能够比 HNSW 更快的原因所在。

以下是我们在 GIST 数据集（包含 100 万条 960 维向量）上的初步基准测试结果。在相同召回率下，VectorChord 的 QPS 可以达到 pgvector 的两倍。更多细节将在下文的基准测试章节中展示。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288263095/3f2dcc75-a3e9-4d86-9515-7ab120f73c0c.png)

### 外部索引构建 {#external-index-build}

原始的 IVF 方法通常需要扫描数据集的 1%–5%，速度较慢。通过使用 RaBitQ 和快速扫描优化，VectorChord 大幅减少了需要执行全精度比较的向量数量，从而显著加快了计算速度。这种方法有助于打造一个稳定、可扩展且与 PostgreSQL 存储系统良好契合的向量搜索系统。因此，用户可以将 **PostgreSQL 的物理复制等原生特性**与 VectorChord 无缝结合使用。

由于构建在 IVF 之上，VectorChord **允许在数据库外部（例如在 GPU 上）执行 KMeans 聚类**，随后将结果轻松导入数据库。我们在 AWS i4i.large 实例（配备 2 vCPU 和 16 GB 内存）上进行了测试，以评估索引构建和插入耗时。测试使用的数据集为 GIST 1M：我们先插入 700,000 条向量并构建索引，然后再追加插入 300,000 条向量。在系统预热后，我们使用单线程执行查询，并在此过程中评估了索引构建时间和插入时间，结果如下：

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733302602422/57f0e7d6-5f48-484f-ac2a-5e999b7cd0fe.png)

通过利用独立机器执行 KMeans 聚类，VectorChord 仅需 186 秒即可完成索引构建，**速度比 pgvector 快 16 倍**。此外，其数据插入速度也比 pgvector 快 14 倍。众所周知，构建索引是向量数据库中最耗费资源的环节，需要大量计算并推高对 CPU 和内存的需求。通过利用算力更强的机器构建索引，再将其导入较小的机器提供查询服务，在单台机器上支撑数十亿规模的向量便成为了现实。

<a id="Benchmark"></a>
## 基准测试 {#benchmark}

我们使用 LAION 5M 和 100M 数据集进行了更多实验，以更全面地评估性能与成本。

### LAION 5M {#laion-5m}

我们在 LAION 5M 数据集上进行了实验，VectorChord 的表现令人鼓舞：与其他平台相比，它始终能够实现更高的每秒查询数（RPS）。当许多数据库在召回率提升时难以兼顾速度与精度之际，VectorChord 即便在高召回率水平下依然保持高效。这一特性使其非常适合同时需要快速响应与高精度的应用场景。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288538606/7f7ae3ef-5bda-4b3c-ace7-cf269511472f.png)

该实验采用 [MyScale 单线程基准测试](https://myscale.github.io/benchmark/#/)，在一台配备 4 vCPU、32GB 内存和 200GB EBS 存储的 `r6a.xlarge` 机器上运行。实验参数设置为：`nlist` 为 8192，`shared_buffers` 为 28GB，禁用 JIT，`effective_io_concurrency` 为 200。我们在未预热（prewarm）的情况下将实验运行了两次。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288473788/e47f3d44-84fc-4dc7-900b-a6b0cbe4db92.png)

我们使用的 `r6a.xlarge` 机器每月成本约为 $165.56，而 Zilliz Performance 4CU 的定价约为每月 $460。值得注意的是，我们在 LAION 5M 数据集的 Top 100 查询中实现了与之相当的性能表现。

### 单机运行 LAION 100M {#laion-100m-on-a-single-machine}

此外，得益于磁盘友好的索引设计，增加单台机器的磁盘容量即可按比例提升 VectorChord 所能容纳的最大向量数量，从而具备在单机上存储 10 亿甚至更多向量的潜力。

为了评估可扩展性，我们在 AWS `i4i.xlarge` 实例（每月仅需 $250 的经济型配置）上对 LAION 100M 数据集（768 维）进行了实验。

[![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733213906554/5021cb87-7337-4fe3-b29f-7b0fd5f28a08.png)](https://instances.vantage.sh/aws/ec2/i4i.xlarge?region=us-east-1&os=linux&cost_duration=monthly&reserved_term=Standard.noUpfront)

该实例仅配备 4 个 CPU 和 32 GB 内存，并使用 937 GB 的本地 SSD 来存储这 1 亿条向量。在此配置下，使用单线程查询时，我们在 Top 10 结果上实现了 16.2 QPS @ 0.95 召回率，在 Top 100 结果上实现了 4.3 QPS @ 0.95 召回率。以下是令人印象深刻的测试结果：

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733215378789/abdae62d-0085-4b38-97d3-43409d3d3f7b.png)

在保持召回率高于 0.95 的同时，我们还评估了这台 4 vCPU 机器上的多线程 QPS。在该场景下，随着并发请求线程数从 1 增加到 8，向量查询的 QPS 呈现出近似线性的增长，证明 VectorChord 具备出色的并发扩展能力。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288585680/c6de7df3-facd-456c-8268-b6799586bc6c.png)

# 总结 {#summary}

VectorChord 是一款专为高效向量搜索设计的全新 PostgreSQL 扩展。它让用户仅需花费 $1 即可存储 400,000 条向量，成本远低于同类竞争产品。通过结合 IVF 与 RaBitQ 量化技术，VectorChord 大幅优化了搜索速度与内存占用，非常适合大规模数据集场景。

我们在 [PGVecto.rs Cloud](/zh/cloud/) 上提供 VectorChord 的云端托管服务。我们的平台简化了部署与管理流程，让您能够轻松高效地扩展向量数据库解决方案。如果您对 VectorChord 有任何疑问，欢迎随时联系我们！您可以在我们的代码仓库中提交 Issue，或发送邮件至 [vectorchord-inquiry@tensorchord.ai](mailto:vectorchord-inquiry@tensorchord.ai)。

%[https://github.com/tensorchord/VectorChord] 

# 参考资料 {#references}

\[1\] Gao, Jianyang, and Cheng Long. "RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search." *Proceedings of the ACM on Management of Data* 2.3 (2024): 1-27.
