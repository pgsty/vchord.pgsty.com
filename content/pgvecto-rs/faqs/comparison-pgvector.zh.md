---
title: "与 pgvector 对比"
linkTitle: "pgvecto.rs 对比 pgvector"
description: "原文：2024 年 pgvector 与 pgvecto.rs 全面对比：PostgreSQL 向量检索选型指南。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/faqs/comparison-pgvector.md"
math: true
aliases:
  - "/faqs/comparison-pgvector/"
---

原文：[pgvector vs. pgvecto.rs in 2024: A Comprehensive Comparison for Vector Search in PostgreSQL](/zh/blog/post/pgvector-vs-pgvectors-in-2024-a-comprehensive-comparison-for-vector-search-in-postgresql/)

太长不看（TL; DR）：请直接跳转到[总结部分](#summary)，查看展示两者核心差异的对比表格。

<a id="Search"></a>
## 检索能力 {#search}

检索是数据库的核心能力，对于实现高效的数据获取、帮助用户快速查找所需信息至关重要。下面我们将展示 [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 与 pgvector 的性能表现，并重点对比二者提供的各项功能特性。

<a id="Filtering"></a>
### 过滤检索 {#filtering}

虽然 pgvector 和 [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 都支持在 PostgreSQL 中进行向量相似度检索，但 [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 更进一步，引入了来自 [OSDI 2023 的 VBASE 方法](https://www.usenix.org/conference/osdi23/presentation/zhang-qianxi)。

真实业务负载通常涉及**向量检索与关系型查询的结合**。向量检索擅长相似度匹配与相似向量召回，而关系型查询则支持对结构化数据执行复杂的连接（JOIN）、过滤（Filter）和聚合（Aggregation）。

`pgvecto.rs` 专为高效处理**单向量 TopK + 过滤 + 连接（Single-Vector TopK + Filter + Join）**场景而设计。

由于目前缺乏通用的关系型向量基准测试集，我们使用 `laion-768-5m-ip-probability` 数据集进行基准测试。该数据集衍生自 LAION 2B 图像数据集，包含 5,000,000 条向量和 10,000 条查询。

该数据集包含一个 `probability` 列，用于存储从 0 到 1 均匀分布生成的随机浮点数。选择率（ratio）为 0.01 意味着每次查询过滤后覆盖数据集的 1%（即 0.01 倍），便于开展针对性的选择率分析。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1707832203612/14235301-ff6e-401e-be2e-62f6ea29cebf.png?auto=compress,format&format=webp)

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1707832190249/b370b8e0-47a0-4aaf-a7b8-67bbd9f51314.png?auto=compress,format&format=webp)

我们在保持 `ef_search` 不变的前提下，展示了不同 `probability` 范围下的召回率（Recall）、延迟（毫秒）和每秒请求数（RPS）。`ef_search` 参数表示 k-NN（k 近邻）搜索期间使用的候选列表大小，决定了搜索精度与查询处理耗时之间的权衡。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1707279248378/4ebbb813-0593-4949-9898-9abdee58e4fc.png)

当结合 VBASE 使用时，[**pgvecto.rs**](https://github.com/tensorchord/pgvecto.rs/) 能够始终保持更高的召回率，尤其是在低选择率（高过滤比）场景下优势极为显著。

### 稀疏向量检索 {#sparse-vector-search}

稀疏向量是仅包含少量非零元素的高维向量，非常适用于传统信息检索（IR）场景。例如，一个拥有 32,000 个维度但仅有 2 个非零元素的向量就是典型的稀疏向量：


$$
S[1\times 32000]=\left[ \begin{matrix} 0 & 0 & 0.015 & 0 & 0 & 0 & 0 & \cdots & 0.543 & 0 \end{matrix} \right]
$$


稠密向量则是神经网络生成的嵌入向量（Embeddings），由文本嵌入模型生成，其中绝大多数或全部元素均为非零值。它们的维度通常较低（如 256 或 1536 维），远小于稀疏向量：


$$
D[1\times 256]=\left[ \begin{matrix} 0.342 & 1.774 & 0.087 & 0.870 & 0.001 & \cdots & 0.543 & 0.999 \end{matrix} \right]
$$


[pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 同时支持稠密向量检索和[稀疏向量检索](/zh/pgvecto-rs/use-case/sparse-vector/)。它提供了 [`svector`](/zh/pgvecto-rs/use-case/sparse-vector/) 数据类型，用于构建稀疏向量索引并执行高效检索：

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding svector(10) NOT NULL
);

INSERT INTO items (embedding) VALUES ('[0.1,0,0,0,0,0,0,0,0,0]');

CREATE INDEX your_index_name ON items USING vectors (embedding svector_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[0.3,0,0,0,0,0,0,0,0,0]' LIMIT 1;
```

### 向量维度上限 {#vector-dimensions}

[pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 扩展支持最高 65,535 维的向量，而 pgvector 扩展的 `vector` 索引最多仅支持 2,000 维。这一维度上限的差异使得 [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 能够直接处理 OpenAI 最新高维嵌入模型生成的向量。

<a id="single-instruction-multiple-data-simd"></a>
### 单指令多数据流（SIMD） {#single-instructionmultiple-data-simd}

`pgvecto.rs` 会在运行时动态检测并利用用户机器上可用的最优 SIMD（单指令多数据流）指令集；而 `pgvector` 则依赖编译器在编译期生成静态 SIMD 代码，无法在运行时针对宿主机的硬件特性自动选择更快的指令集。更快的向量距离计算使得 `pgvecto.rs` 的检索速度更具优势。

## 数据类型 {#data-types}

### 二值向量 {#binary-vector}

[`bvector`](/zh/pgvecto-rs/reference/vector-types/bvector/) 是 [pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 中的二值向量类型，表示每个分量仅取两个可能值（通常为 0 和 1）的向量。

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding bvector(3) NOT NULL
);

INSERT INTO items (embedding) VALUES ('[1,0,1]'), ('[0,1,0]');

CREATE INDEX your_index_name ON items USING vectors (embedding bvector_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[1,0,1]' LIMIT 5;
```

在配合特定嵌入模型（如 OpenAI 嵌入模型）使用时，二值向量具有显著优势：它能在保持理想召回精度的同时，大幅降低内存占用。

以下是 `bvector` 类型的性能基准测试，采用 [dbpedia-entities-openai3-text-embedding-3-large-3072-1M](https://huggingface.co/datasets/Qdrant/dbpedia-entities-openai3-text-embedding-3-large-3072-1M) 数据集，测试环境为 Google Cloud 上的 `n2-standard-8`（8 vCPU，32 GB 内存）虚拟机。

我们将 100 万条二值向量写入表中并建立索引，随后对每条查询运行 KNN 搜索。为 100 万条二值向量建立索引仅需约 600 MB 内存，而使用 `vector` 类型为相同数量的向量建立索引则需要约 18 GB 内存。如果结合采用[**自适应检索（Adaptive Retrieval）**](/zh/pgvecto-rs/use-case/adaptive-retrieval/)，`bvector` 的准确率可超过 95%。

![bvector](/pgvecto-rs/reference/vector-types/images/bvector.png)

<a id="fp16-int8"></a>
### FP16/INT8 {#fp16int8}

除二值向量外，[pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 还支持 [FP16（16 位浮点数）](/zh/pgvecto-rs/reference/vector-types/vecf16/)数据类型以及 INT8（8 位整数）量化存储。

<a id="Indexing"></a>
## 索引架构 {#indexing}

与 pgvector 相比，`pgvecto.rs` 采用了不同的索引架构设计。它独立于 PostgreSQL 管理索引的存储与内存，而不是像 pgvector 那样依赖 PostgreSQL 的原生页面存储引擎。

这是一种工程架构上的权衡。在开发初期，我们也曾尝试像 pgvector 一样基于 PostgreSQL 的页面存储（Page Storage）来实现分层可导航小世界（HNSW）图索引，但遇到了诸多制约其性能与功能的瓶颈：

* **并行化难题**：PostgreSQL 采用单语句单进程模型，且内部 API 并非线程安全，这给多线程并行带来了巨大挑战。构建向量索引属于计算密集型任务，并行化能显著提升性能；但我们在尝试并行化该过程时，频繁遭遇 `Too many shared buffer locked`（锁定的共享缓冲区过多）错误。
* **预写式日志（WAL）写放大**：插入一条 2 KB 的向量往往会产生超过 20 KB 的 WAL 日志。这一问题源于 HNSW 算法本身的特性——每插入一个节点都需要修改图中的多条边，而 PostgreSQL 会在 WAL 中逐条记录每一次页面修改，从而导致严重的 WAL 写放大。
* **锁竞争（Lock Contention）**：在遍历和更新 HNSW 图时，读写操作都需要对边列表加锁。由于 HNSW 采用分层结构，越高的层级包含的节点越少，导致高层节点在索引并发读写时极易成为锁竞争瓶颈，进而引发延迟升高和并发吞吐量下降。

为此，[pgvecto.rs](https://github.com/tensorchord/pgvecto.rs) 采用了类似 FreshDiskANN 与日志结构合并树（LSM-Tree）的架构设计。该架构由三个组件构成：写入段（Writing Segment）、增长段（Growing Segment）和封存段（Sealed Segment）。新写入的向量首先进入写入段，随后由后台进程异步转换为不可变的增长段，最后增长段会与封存段进行合并（类似于 LSM-Tree 中的 Compaction 过程）。这种设计带来了诸多优势：

* **非阻塞插入**：索引的后台构建与优化不会阻塞前台的数据插入操作。
* **批量更新图结构**：将对 HNSW 图的修改进行批量聚合处理，显著提升了写入吞吐量。
* **消除读写锁竞争**：由于封存段（Sealed Segment）是不可变的（Immutable），彻底缓解了并发检索时的读写锁竞争问题。

当然，这种独立存储方式也存在不足，其中最主要的一点是索引无法直接获得 PostgreSQL 开箱即用的预写式日志（WAL）支持。这意味着依赖 WAL 的时间点恢复（PITR）和物理复制（Physical Replication）无法直接作用于索引文件（注：这一限制已在后续的继任项目 VectorChord 中通过原生 PostgreSQL 存储引擎架构彻底解决）。

<a id="Summary"></a>
## 总结 {#summary}

下表汇总了 `pgvecto.rs` 与 `pgvector` 之间的主要区别：

| 特性 | pgvecto.rs | pgvector |
| --- | --- | --- |
| 过滤检索（Filtering） | 引入 VBASE 方法，专为向量检索结合关系型查询（如单向量 TopK + Filter + Join）深度优化。 | 应用过滤条件时可能出现召回结果不足的情况（例如原本指定 `LIMIT 10`，过滤后可能只返回 5 条结果）。 |
| 向量维度上限 | 最高支持 65,535 维。 | 索引最高支持 2,000 维（`vector` 类型）。 |
| SIMD 加速 | 在运行时根据宿主机硬件能力动态派发最优 SIMD 指令集，最大化计算性能。 | 依赖编译器在编译期生成的静态 SIMD 代码。 |
| 数据类型 | 提供丰富的数据类型支持：稠密向量、稀疏向量、二值向量、FP16（16 位浮点数）以及 INT8 量化。 | \- |
| 索引存储架构 | 独立于 PostgreSQL 管理索引的磁盘存储与内存映射。 | 依赖 PostgreSQL 原生页面存储引擎。 |
| WAL 支持 | 表数据支持预写式日志（WAL），索引的 WAL 支持尚在开发中。 | 表数据和索引均支持预写式日志（WAL）。 |
