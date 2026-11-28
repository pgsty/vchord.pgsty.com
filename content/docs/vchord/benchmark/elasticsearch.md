---
title: "Benchmark vs. Elasticsearch"
linkTitle: "vs. Elasticsearch"
description: "vchord_bm25 against Elasticsearch on 14 BEIR datasets: queries per second for top 1,000 and top 10 results, and ranking quality as NDCG@10."
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/elasticsearch.md"
aliases:
  - "/docs/benchmark/elasticsearch/"
  - "/vectorchord/benchmark/elasticsearch/"
icon: fa-solid fa-magnifying-glass-chart
---

This page compares BM25 keyword search in PostgreSQL with [vchord_bm25](/docs/bm25/) against Elasticsearch on the BEIR datasets of [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks): how many queries each answers per second, and whether their rankings are equally good. The figures come from [VectorChord-BM25: 3x Faster Than Elasticsearch](/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/) (February 2025), which does not name the hardware.

<a id="RPS"></a>

## Queries per second {#rps}

For a fair comparison, both systems used the same stopword list and stemmer, and Elasticsearch indexed each document's title and text as one field, as vchord_bm25 does.

<img src="/docs/images/es-vchord-bm25-rps.png" alt="Top-1,000 queries per second of vchord_bm25 and Elasticsearch on 14 BEIR datasets" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

The result depends on how many rows a query returns:

| Results per query | vchord_bm25 | Elasticsearch |
| --- | --- | --- |
| Top 1,000 | 112 QPS | 49 QPS |
| Top 10 | 271.91 QPS | 341 QPS |

Each figure is an average over the datasets. For top 1,000, vchord_bm25 is faster on 12 of the 14 datasets in the chart and slower on climate-fever and arguana; averaged per dataset, the post reports three times Elasticsearch's throughput. For top 10, Elasticsearch is about 25% faster.

<a id="ndcg10"></a>

## Ranking quality {#ndcg-10}

<img src="/docs/images/es-vchord-bm25-ndcg10.png" alt="NDCG@10 of vchord_bm25 and Elasticsearch on BEIR datasets" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

With the same text processing, NDCG@10 is close on most datasets and higher for vchord_bm25 on trec-covid and scifact. Ranking quality depends on tokenization more than on the index: before the stopword lists and stemmers were aligned, vchord_bm25's NDCG@10 was much lower on some datasets. Tokenize documents and queries the same way, as described in [vchord_bm25](/docs/bm25/).
