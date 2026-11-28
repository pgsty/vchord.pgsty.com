---
title: "Benchmarks"
linkTitle: "Benchmarks"
description: "Published throughput and relevance measurements for vchord_bm25 and hybrid search, with their datasets, versions, and sources."
weight: 40
icon: fa-solid fa-chart-bar
---

These are the published measurements of vchord_bm25, with what was measured and where it comes from. They were taken with the 0.x engine, before vchord_bm25 was rewritten around `tsvector`; repeat them on your own data before relying on them. Speed depends on vocabulary, query length, and `LIMIT`; relevance depends mostly on tokenization.

## Against Elasticsearch {#elasticsearch}

TensorChord compared VectorChord-BM25 0.1 with Elasticsearch in February 2025 on the BEIR datasets of [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks), after aligning stop words, stemming, and how title and text fields are combined. The source does not state the hardware. Source: [VectorChord-BM25: 3x faster than Elasticsearch](/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/).

| Measure | VectorChord-BM25 | Elasticsearch |
| --- | --- | --- |
| Top-1000 queries per second, geometric mean | 112 | 49 |
| Top-10 queries per second, geometric mean | 272 | 341 |

VectorChord-BM25 was faster when many results were requested and slower for the top 10. NDCG@10 was comparable on most datasets and higher on trec-covid and scifact.

Per dataset, top-1000 throughput:

![Top-1000 requests per second of VectorChord-BM25 and Elasticsearch on BEIR datasets](/docs/images/es-vchord-bm25-rps.png)

Per dataset, NDCG@10 of the top-1000 results:

![NDCG@10 of VectorChord-BM25 and Elasticsearch on BEIR datasets](/docs/images/es-vchord-bm25-ndcg10.png)

## Hybrid search quality {#hybrid}

TensorChord measured NDCG@10 on four BEIR datasets in March 2025 with vchord 0.3, VectorChord-BM25 0.2 using pg_tokenizer's Unicode tokenizer, BGE-M3 embeddings, RRF with `k = 60`, and the `bge-reranker-v2-m3` cross-encoder. Source: [Hybrid search with Postgres native BM25 and VectorChord](/blog/hybrid-search-with-postgres-native-bm25-and-vectorchord/), code in [xieydd/vectorchord-hybrid-search](https://github.com/xieydd/vectorchord-hybrid-search).

| Dataset | Vector search | BM25 | RRF of both | Cross-encoder rerank |
| --- | --- | --- | --- | --- |
| FiQA-2018 | 0.403 | 0.253 | 0.376 | 0.427 |
| Quora | 0.884 | 0.787 | 0.870 | 0.891 |
| SCIDOCS | 0.161 | 0.156 | 0.173 | 0.179 |
| SciFact | 0.576 | 0.685 | 0.679 | 0.746 |

RRF beat both single methods only on SCIDOCS; reranking the candidates with a cross-encoder scored highest on every dataset. [Hybrid search](/docs/bm25/usage/hybrid-search/#tuning) shows how to weight the two lists.

## Release comparisons {#release-reports}

The [1.3.0 performance report](https://github.com/pgsty/vchord_bm25/blob/1.3.0/docs/performance/2026-11-24-bm25.zh-CN.md) (in Chinese) compares 1.3.0 with 1.2.0 on a constructed 20,000-row corpus, on macOS `arm64` and Linux `x86_64` with PostgreSQL 18: build WAL, query plans and their buffer reads, maintenance, and parallel build time and memory.
