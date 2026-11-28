---
title: "Price Benchmark"
linkTitle: "Price"
description: "What it cost in December 2024 to serve 100 million 768-dimensional vectors from one PostgreSQL server with vchord, compared with Pinecone, Qdrant, and in-memory pgvector."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/price.md"
aliases:
  - "/docs/benchmark/price/"
  - "/vectorchord/benchmark/price/"
icon: fa-solid fa-coins
---

This page compares the monthly cost of hosting 100 million 768-dimensional vectors on one PostgreSQL server with vchord against hosted and in-memory alternatives. The figures come from [Store 400k Vectors for $1 in PostgreSQL](/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/) and use cloud list prices from December 2024.

## Vectors per dollar {#vectors-per-dollar}

The run used the LAION-100M dataset (100 million vectors, 768 dimensions) on one AWS `i4i.xlarge`: 4 vCPU, 32 GB of memory, and a 937 GB NVMe SSD that holds the vectors and the index, for about $250 a month. It answered 131 queries per second at 0.95 top-10 recall with 16 client threads; the [Performance](/docs/vchord/benchmark/performance/#laion-100m-on-i4ixlarge) page has the per-thread figures.

That works out to 400,000 vectors stored per dollar per month: 6 times as many as Pinecone's storage-optimized instances and 26 times as many as an in-memory pgvector or pgvecto.rs HNSW index.

<img src="/docs/images/price-benchmark.png" alt="Vectors stored per dollar per month for vchord, Pinecone, Qdrant, and in-memory pgvector or pgvecto.rs" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

## Monthly cost for 100 million vectors {#monthly-cost}

Costs for the other systems are derived from the [MyScale benchmark](https://myscale.github.io/benchmark/) data:

| System | Monthly cost |
| --- | --- |
| vchord on one `i4i.xlarge` | $247 |
| Pinecone, storage-optimized | $1,600 |
| Qdrant | $4,374 |
| pgvector or pgvecto.rs, index in memory | $6,580 |

<img src="/docs/images/price-benchmark-monthly.png" alt="Monthly cost to store 100 million 768-dimensional vectors in vchord, Pinecone, Qdrant, and in-memory pgvector or pgvecto.rs" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

The cost advantage comes from where the index lives. vchord serves queries from an NVMe SSD with only the centroids and hot lists in memory, while an HNSW index needs memory for the whole graph to stay fast; see [Overview](/docs/vchord/getting-started/overview/).
