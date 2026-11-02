---
title: "Benchmark with Elasticsearch"
linkTitle: "Benchmarks with Elasticsearch"
description: "Here we present a comprehensive benchmark comparing our implementation of VectorChord-BM25 with ElasticSearch, focusing on two key metrics: QPS (Queries Per Sec"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/elasticsearch.md"
aliases:
  - "/vectorchord/benchmark/elasticsearch/"
---

Here we present a comprehensive benchmark comparing our implementation of VectorChord-BM25 with ElasticSearch, focusing on two key metrics: QPS (Queries Per Second) and NDCG@10 (Normalized Discounted Cumulative Gain at rank 10). If you are interested in the details of our implementation, please refer to our blog [VectorChord-BM25: Revolutionize PostgreSQL Search with BM25 Ranking — 3x Faster Than ElasticSearch](/blog/post/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/).

<a id="RPS"></a>
## RPS

<img src="/docs/images/es-vchord-bm25-rps.png" alt="RPS" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

We compare the Top1000 Queries Per Second (QPS)—a metric that measures how many queries a system can process per second while retrieving the top 1000 results for each query—between our implementation and ElasticSearch across various datasets from [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks). On average, our implementation achieves **3 times higher QPS** compared to ElasticSearch across the tested datasets, showcasing its efficiency and scalability.

<a id="ndcg-10"></a>
## NDCG@10

<img src="/docs/images/es-vchord-bm25-ndcg10.png" alt="NDCG@10" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

We have dedicated substantial effort to align VectorChord-BM25 with ElasticSearch’s behavior, ensuring a fair and precise comparison. As demonstrated in the table, our implementation achieves NDCG@10 scores that are comparable across most datasets, with certain cases even surpassing ElasticSearch (e.g., trec-covid and scifact).
