---
title: "与 Elasticsearch 的基准测试对比"
linkTitle: "对比 Elasticsearch"
description: "全面对比 VectorChord-BM25 与 Elasticsearch 在 QPS 与 NDCG@10 两个核心指标上的基准测试表现。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/elasticsearch.md"
aliases:
  - "/vectorchord/benchmark/elasticsearch/"
---

本文展示了我们将 VectorChord-BM25 实现与 Elasticsearch 进行全面对比的基准测试结果，重点考察两个核心指标：QPS（每秒查询数）与 NDCG@10（前 10 位结果的归一化折损累计增益）。如果您对我们的技术实现细节感兴趣，请参阅我们的博文《[VectorChord-BM25：以比 Elasticsearch 快 3 倍的 BM25 排序彻底革新 PostgreSQL 搜索](/zh/blog/post/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/)》。

<a id="RPS"></a>
## RPS {#rps}

<img src="/docs/images/es-vchord-bm25-rps.png" alt="RPS" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

我们在来自 [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks) 的多个数据集上，对比了我们的实现与 Elasticsearch 的 Top-1000 每秒查询数（QPS）——该指标衡量系统在为每次查询检索前 1000 条结果时每秒能够处理的查询数量。在所有测试数据集上，我们的实现平均取得了 **比 Elasticsearch 高出 3 倍的 QPS**，充分展现了其卓越的执行效率与可扩展性。

<a id="ndcg-10"></a>
## NDCG@10 {#ndcg10}

<img src="/docs/images/es-vchord-bm25-ndcg10.png" alt="NDCG@10" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

我们投入了大量精力使 VectorChord-BM25 的评分行为与 Elasticsearch 保持对齐，以确保对比的公平性与准确性。如上表所示，我们的实现在绝大多数数据集上均取得了与 Elasticsearch 相当的 NDCG@10 得分，甚至在部分数据集（如 `trec-covid` 和 `scifact`）上超越了 Elasticsearch。
