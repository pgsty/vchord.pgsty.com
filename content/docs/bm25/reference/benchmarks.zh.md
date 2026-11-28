---
title: "基准测试"
linkTitle: "基准测试"
description: "vchord_bm25 与混合检索已发布的吞吐量与相关性测试结果，以及对应的数据集、版本和出处。"
weight: 40
icon: fa-solid fa-chart-bar
---

本页汇总 vchord_bm25 已发布的测试结果，并注明测了什么、出自哪里。这些结果都是用 0.x 引擎测得的，当时 vchord_bm25 还没有改为基于 `tsvector` 重写；在依赖这些数字之前，请先用自己的数据复测。速度取决于词表、查询长度和 `LIMIT`；相关性主要取决于分词。

## 与 Elasticsearch 对比 {#elasticsearch}

TensorChord 于 2025 年 2 月在 [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks) 的 BEIR 数据集上对比了 VectorChord-BM25 0.1 与 Elasticsearch，并事先对齐了停用词、词干提取，以及标题与正文字段的合并方式。原文未说明硬件配置。出处：[VectorChord-BM25：比 Elasticsearch 快 3 倍](/zh/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/)。

| 指标 | VectorChord-BM25 | Elasticsearch |
| --- | --- | --- |
| Top-1000 每秒查询数，几何平均 | 112 | 49 |
| Top-10 每秒查询数，几何平均 | 272 | 341 |

需要返回大量结果时 VectorChord-BM25 更快，只取前 10 名时则较慢。NDCG@10 在大多数数据集上相当，在 trec-covid 和 scifact 上更高。

各数据集的 Top-1000 吞吐量：

![VectorChord-BM25 与 Elasticsearch 在 BEIR 数据集上的 Top-1000 每秒请求数](/docs/images/es-vchord-bm25-rps.png)

各数据集 Top-1000 结果的 NDCG@10：

![VectorChord-BM25 与 Elasticsearch 在 BEIR 数据集上的 NDCG@10](/docs/images/es-vchord-bm25-ndcg10.png)

## 混合检索质量 {#hybrid}

TensorChord 于 2025 年 3 月在四个 BEIR 数据集上测量了 NDCG@10，使用 vchord 0.3、VectorChord-BM25 0.2（搭配 pg_tokenizer 的 Unicode 分词器）、BGE-M3 向量、`k = 60` 的 RRF，以及 `bge-reranker-v2-m3` cross-encoder。出处：[基于 Postgres 原生 BM25 与 VectorChord 的混合检索](/zh/blog/hybrid-search-with-postgres-native-bm25-and-vectorchord/)，代码见 [xieydd/vectorchord-hybrid-search](https://github.com/xieydd/vectorchord-hybrid-search)。

| 数据集 | 向量检索 | BM25 | 两者 RRF | Cross-encoder 重排 |
| --- | --- | --- | --- | --- |
| FiQA-2018 | 0.403 | 0.253 | 0.376 | 0.427 |
| Quora | 0.884 | 0.787 | 0.870 | 0.891 |
| SCIDOCS | 0.161 | 0.156 | 0.173 | 0.179 |
| SciFact | 0.576 | 0.685 | 0.679 | 0.746 |

RRF 只在 SCIDOCS 上同时超过了两种单一方法；用 cross-encoder 对候选重排，在每个数据集上都得分最高。两路结果如何加权，见[混合检索](/zh/docs/bm25/usage/hybrid-search/#tuning)。

## 版本间对比 {#release-reports}

[1.3.0 性能报告](https://github.com/pgsty/vchord_bm25/blob/1.3.0/docs/performance/2026-11-24-bm25.zh-CN.md)在一个构造的 20,000 行语料上，分别于 macOS `arm64` 和 Linux `x86_64`（PostgreSQL 18）对比了 1.3.0 与 1.2.0：建索引产生的 WAL、查询计划及其缓冲区读取、索引维护，以及并行建索引的耗时与内存。
