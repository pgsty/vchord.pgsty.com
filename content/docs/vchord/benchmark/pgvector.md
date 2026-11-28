---
title: "Benchmark vs. pgvector"
linkTitle: "vs. pgvector"
description: "vchordrq against pgvector HNSW on GIST-1M (960 dimensions): queries per second at equal precision, index build time, insert time, and query completion time."
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/pgvector.md"
aliases:
  - "/docs/benchmark/pgvector/"
  - "/vectorchord/benchmark/pgvector/"
icon: fa-solid fa-scale-balanced
---

This page compares `vchordrq` with pgvector's HNSW index on GIST-1M, one million 960-dimensional vectors. It shows how much faster vchord answers queries at the same precision and how much less time it spends building and updating the index. The figures come from [Store 400k Vectors for $1 in PostgreSQL](/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/) (December 2024).

<a id="qps--recall"></a>

## Queries per second {#qps-and-recall}

<img src="/docs/images/gist-1m-top10.png" alt="Queries per second against mean precision for top 100 on GIST-1M, vchord IVF with RaBitQ against pgvector HNSW" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

For top-100 queries, vchord answers more than twice as many queries per second as pgvector HNSW at every precision where both were measured. The post does not name the hardware for this chart.

<a id="index-build-time--insert-time--query-completion-time"></a>

## Build, insert, and query time {#build-and-insert}

This run used an AWS `i4i.large` (2 vCPU, 16 GB of memory) and pgvector 0.8.0. It loaded 700,000 vectors, built the index, inserted the remaining 300,000, and then ran queries in one thread after a warm-up. vchord's k-means step ran on a separate machine and was imported as an [external build](/docs/vchord/usage/external-build/); the post does not say how long that step took.

| | vchord | pgvector 0.8.0 |
| --- | --- | --- |
| Index build | 186 s | 3,043 s |
| Insert | 145 s | 2,052 s |
| Query completion | 4.42 s | 28 s |

<img src="/docs/images/pgvector-vchord-compare.png" alt="Index build time, insert time, and query completion time for vchord and pgvector 0.8.0 on GIST-1M" style="width: 100%; height: auto; margin: 0 auto; display: block;" />
