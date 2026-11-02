---
title: "性能基准测试"
linkTitle: "性能"
description: "全面对比 VectorChord 与其他主流向量数据库在 QPS 与水平可扩展性方面的基准测试表现。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/performance.md"
aliases:
  - "/zh/docs/benchmark/performance/"
  - "/vectorchord/benchmark/performance/"
---

本文展示了我们将 VectorChord 实现与其他主流向量数据库进行全面对比的基准测试结果，重点考察 QPS（每秒查询数）与可扩展性。如果您对我们的技术实现细节感兴趣，请参阅我们的博文《[VectorChord：在 PostgreSQL 中仅需 1 美元存储 400k 向量](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)》。

<a id="QPS"></a>
## QPS {#qps}

### LAION 5M {#laion-5m}

<img src="/docs/images/laion-5m-top10.png" alt="QPS on LAION 5M top 10" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

在 LAION 5M 数据集上，在达到 0.95 召回率的前提下，VectorChord 取得了比 MyScale、pgvector、Pinecone、Weaviate、Qdrant 和 Zilliz（Milvus）等各类向量数据库高出 3 倍以上的 QPS。

<a id="laion-100m-on-i4i-xlarge"></a>
### `i4i.xlarge` 上的 LAION 100M {#laion-100m-on-i4ixlarge}

<img src="/docs/images/laion-100m-multi-thread.png" alt="QPS on LAION 100M" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

该测试环境配置为 4 核 CPU、32 GB 内存，并使用 937 GB 的 SSD 存储来容纳 1 亿条向量。在单线程查询下，我们在 Top-10 召回率达到 0.95 时实现了 16.2 的 QPS，在 Top-100 召回率达到 0.95 时实现了 4.3 的 QPS。这一表现令人印象深刻。

<a id="Scalability"></a>
## 可扩展性 {#scalability}

如果您对 VectorChord 的水平扩展能力感兴趣，请参阅我们的博文《[使用 VectorChord 在 PostgreSQL 中实现 10,000 QPS 的向量检索](/zh/blog/post/vector-search-at-10000-qps-in-postgresql-with-vectorchord/)》。

### LAION 100M 与 LAION 5M {#laion-100m--laion-5m}

| **数据集** | **达到 10,000+ QPS 的最低硬件配置** | **vCPU 数量** | **预估月度成本** |
| --- | --- | --- | --- |
| LAION-5m | r7i.xlarge × 7 | 4 × 7 = 28 vcpu | $0.2646 × 7 × 720 = $1334 |
| LAION-100m | r7i.16xlarge × 2 | 64 × 2 = 128 vcpu | $4.2336 × 2 × 720 = $6096 |

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="QPS on LAION 100M and LAION 5M" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

> [!TIP]
> 上述价格基准测试于 2024 年 12 月 5 日执行。我们正在持续提升性能并优化成本。例如，VectorChord 0.2 在前代版本的基础上将索引体积缩减了 30%，并将索引构建速度提升了 50%。如果您想了解最新的基准测试数据，欢迎通过 [Discord](https://discord.gg/KqswhpVgdU) 联系我们。
