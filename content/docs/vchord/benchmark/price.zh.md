---
title: "价格基准测试"
linkTitle: "价格"
description: "使用 VectorChord，仅需每月 250 美元的单机配置即可在 1 亿条 768 维向量上实现 0.95 召回率下 131 QPS 的检索性能。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/price.md"
aliases:
  - "/zh/docs/benchmark/price/"
  - "/vectorchord/benchmark/price/"
---

使用 VectorChord，您可以在单台机器上对 1 亿条 768 维向量执行 Top-10 查询，在保持 0.95 召回率（Precision/Recall）的同时实现 131 的 QPS，而整套配置的月度成本仅为 250 美元。如果您对我们的技术实现细节感兴趣，请参阅我们的博文《[VectorChord：在 PostgreSQL 中仅需 1 美元存储 400k 向量](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)》。

这意味着您只需花费 1 美元即可存储 400k（40 万）条向量，从而实现显著的成本节约：在同等价格下，可存储的向量数量是 Pinecone（存储优化型实例）的 6 倍，是 pgvector/pgvecto.rs 的 26 倍。

<img src="/docs/images/price-benchmark.png" alt="Pricing Benchmark" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

在基于 MyScale 基准测试数据的向量存储月度成本对比中，下图清晰地展示了 VectorChord 极具竞争力的性价比——存储 1 亿条向量的月均成本仅需 247 美元。相比之下，尽管 Pinecone 采用了优化型存储，其月成本仍高达 1,600 美元；Qdrant 的月成本为 4,374 美元；而 pgvector/pgvecto.rs 的成本则更高，达到每月 6,580 美元。

<img src="/docs/images/price-benchmark-monthly.png" alt="Pricing Benchmark" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

> [!TIP]
> 上述价格基准测试于 2024 年 12 月 5 日执行。我们正在持续提升性能并优化成本。例如，VectorChord 0.2 在前代版本的基础上将索引体积缩减了 30%，并将索引构建速度提升了 50%。如果您想了解最新的基准测试数据，欢迎通过 [Discord](https://discord.gg/KqswhpVgdU) 联系我们。
