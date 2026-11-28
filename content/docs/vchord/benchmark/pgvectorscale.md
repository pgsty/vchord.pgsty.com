---
title: "Benchmark vs. pgvectorscale"
linkTitle: "vs. pgvectorscale"
description: "vchordrq against pgvectorscale and pgvector on LAION-5M: queries per second with the index in memory and on disk, index build time and memory, and insert rate."
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/pgvectorscale.md"
aliases:
  - "/docs/benchmark/pgvectorscale/"
  - "/vectorchord/benchmark/pgvectorscale/"
icon: fa-solid fa-chart-column
---

This page compares the three PostgreSQL vector extensions on LAION-5M (5 million 768-dimensional vectors, L2 distance): `vchordrq`, pgvectorscale's StreamingDiskANN, and pgvector's HNSW. It covers the questions that decide which one fits a workload: speed when the index fits in memory and when it does not, the time and memory an index build takes, and how fast new rows can be inserted. The figures come from [Vector Search Over PostgreSQL: A Comparative Analysis of Memory and Disk Solutions](/blog/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/) (April 2025), which used VectorChord 0.2.2, pgvector 0.8.0, and pgvectorscale 0.6.0 on PostgreSQL 17.

<a id="qps--recall"></a>

## Queries per second {#qps-and-recall}

Each system ran 10,000 test queries; the charts plot queries per second against top-10 and top-100 recall. vchord's index was built with an [external build](/docs/vchord/usage/external-build/).

<a id="Memory"></a>

### Index in memory {#memory}

An AWS `i4i.xlarge` (4 vCPU, 32 GiB of memory, 937 GB NVMe SSD) with `shared_buffers = 24GB`, enough to cache the whole index.

<img src="/docs/images/laion-5m-qps-memory.png" alt="Queries per second against recall at 10 and 100 on LAION-5M with the index in memory, for vchord, pgvector, and pgvectorscale" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

At recall above 0.95, vchord answers the most queries per second. pgvectorscale is faster than pgvector on the first query after a cold start, but pgvector overtakes it once the index is cached.

<a id="Disk"></a>

### Index on disk {#disk}

An AWS `c6id.large` (2 vCPU, 4 GiB of memory, 118 GB NVMe SSD) with `shared_buffers = 2GB`, so most reads go to disk. The indexes were built on a larger machine and restored, because 4 GiB is not enough to build them.

<img src="/docs/images/laion-5m-qps-disk.png" alt="Queries per second against recall at 10 and 100 on LAION-5M with the index on disk, for vchord, pgvector, and pgvectorscale" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

At recall above 0.95, vchord again answers the most queries per second; pgvector and pgvectorscale are close to each other.

## Index build {#index-building}

The build ran on an `i4i.xlarge` with `shared_buffers = 1GB`. vchord is shown twice: an internal build, where `CREATE INDEX` runs k-means itself, and an external build, where k-means ran on a separate machine with an A10 GPU. Both used 25 k-means iterations.

| | pgvector | pgvectorscale | vchord, internal | vchord, external |
| --- | --- | --- | --- | --- |
| Build time | 162 min | 187 min | 33 min | 15 min |
| CPU cores used | 100% | 25% | 100% | 100% |
| Peak memory | 2.1 GB | 15.2 GB | 9.8 GB | 1.1 GB |
| Disk after build | 40 GB | 28 GB | 41 GB | 41 GB |
{.wide}

<img src="/docs/images/all-about-index-building.png" alt="Core utilization, build time, disk usage, and memory usage of index builds for pgvector, pgvectorscale, and vchord internal and external builds" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

With k-means on the same `i4i.xlarge` instead of a GPU, the external build takes about 50 minutes. pgvectorscale uses the least disk.

## Insert rate {#insertion-time}

After the index was built on 5 million vectors, random vectors were inserted one row at a time on an `i4i.xlarge`:

| | Rows per second |
| --- | --- |
| vchord | 1,565 |
| pgvector | 246 |
| pgvectorscale | 107 |

<img src="/docs/images/pgvector-vchord-pgvectorscale-insert-performance.png" alt="Rows inserted per second into an existing index for vchord, pgvector, and pgvectorscale" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

A new row in `vchordrq` goes into the list of its nearest centroid, while a graph index searches the graph and adds edges for every row it inserts.
