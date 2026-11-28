---
title: "与 Elasticsearch 对比"
linkTitle: "对比 Elasticsearch"
description: "在 14 个 BEIR 数据集上对比 vchord_bm25 与 Elasticsearch：返回前 1,000 条和前 10 条结果时的每秒查询数，以及用 NDCG@10 衡量的排序质量。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/elasticsearch.md"
aliases:
  - "/docs/benchmark/elasticsearch/"
  - "/vectorchord/benchmark/elasticsearch/"
icon: fa-solid fa-magnifying-glass-chart
---

本页在 [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks) 的 BEIR 数据集上，对比用 [vchord_bm25](/zh/docs/bm25/) 在 PostgreSQL 里做 BM25 关键词检索与 Elasticsearch：两者每秒各能回答多少查询，排序结果是否一样好。数据出自 [VectorChord-BM25: 3x Faster Than Elasticsearch](/zh/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/)（2025 年 2 月），文章没有给出测试硬件。

<a id="RPS"></a>

## 每秒查询数 {#rps}

为了公平比较，两边使用相同的停用词表和词干提取器，Elasticsearch 也像 vchord_bm25 一样把每篇文档的标题和正文合成一个字段建索引。

<img src="/docs/images/es-vchord-bm25-rps.png" alt="14 个 BEIR 数据集上 vchord_bm25 与 Elasticsearch 返回前 1,000 条结果时的每秒查询数" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

谁更快取决于每条查询返回多少行：

| 每条查询返回 | vchord_bm25 | Elasticsearch |
| --- | --- | --- |
| 前 1,000 条 | 112 QPS | 49 QPS |
| 前 10 条 | 271.91 QPS | 341 QPS |

表中数字都是各数据集的平均值。返回前 1,000 条时，图中 14 个数据集里 vchord_bm25 有 12 个更快，climate-fever 和 arguana 两个更慢；按数据集逐个求平均，文章给出的吞吐是 Elasticsearch 的三倍。返回前 10 条时，Elasticsearch 快约 25%。

<a id="ndcg10"></a>

## 排序质量 {#ndcg-10}

<img src="/docs/images/es-vchord-bm25-ndcg10.png" alt="BEIR 数据集上 vchord_bm25 与 Elasticsearch 的 NDCG@10" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

文本处理一致时，两者在大多数数据集上的 NDCG@10 接近，在 trec-covid 和 scifact 上 vchord_bm25 更高。排序质量更多取决于分词而不是索引：停用词表和词干提取器对齐之前，vchord_bm25 在部分数据集上的 NDCG@10 明显偏低。文档和查询要用同一种方式分词，做法见 [vchord_bm25](/zh/docs/bm25/)。
