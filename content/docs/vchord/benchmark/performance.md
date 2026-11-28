---
title: "Performance Benchmark"
linkTitle: "Performance"
description: "Queries per second of vchordrq on LAION image embeddings: 5 million vectors against other vector databases, 100 million vectors on one 4-vCPU server, and replicas up to 10,000 QPS."
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/performance.md"
aliases:
  - "/docs/benchmark/performance/"
  - "/vectorchord/benchmark/performance/"
icon: fa-solid fa-gauge-high
---

This page shows how many queries per second `vchordrq` answers at a given recall on the LAION datasets of 768-dimensional image embeddings: on one server with 5 million and with 100 million vectors, and on streaming replicas. The single-server runs are from [Store 400k Vectors for $1 in PostgreSQL](/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/) (December 2024).

<a id="QPS"></a><a id="qps"></a>

## LAION-5M against other vector databases {#laion-5m}

The run used the [MyScale benchmark](https://myscale.github.io/benchmark/) with one client thread on an AWS `r6a.xlarge` (4 vCPU, 32 GB of memory, 200 GB EBS). The index had 8,192 lists; PostgreSQL ran with `shared_buffers = 28GB`, `jit = off`, and `effective_io_concurrency = 200`, and the benchmark ran twice without prewarming. Results for the other systems come from the MyScale benchmark, on the hardware named in the legend.

<img src="/docs/images/laion-5m-top10.png" alt="Queries per second against top-10 recall on LAION-5M for vchord, MyScale, pgvector, pgvecto.rs, Pinecone, Qdrant, Weaviate, Zilliz, Elasticsearch, and OpenSearch" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

Between 0.97 and 0.98 top-10 recall, vchord answers more than three times as many queries per second as any other system in the chart. The post also reports top-100 results comparable to a Zilliz Performance 4CU instance at about $460 a month, against about $166 a month for the `r6a.xlarge`.

<a id="laion-100m-on-i4i-xlarge"></a>

## LAION-100M on one `i4i.xlarge` {#laion-100m-on-i4ixlarge}

The run used 100 million vectors on an AWS `i4i.xlarge`: 4 vCPU, 32 GB of memory, and a 937 GB NVMe SSD that holds the vectors and the index. With one query thread it answered 16.2 queries per second at 0.95 top-10 recall and 4.3 at 0.95 top-100 recall.

<img src="/docs/images/laion-100m-multi-thread.png" alt="Queries per second against search threads on LAION-100M for top 10 with 100 and 400 probes and top 100 with 200 probes" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

With more client threads and recall kept above 0.95, throughput grows to 131 queries per second at 16 threads for top 10 with 100 probes. The machine cost about $250 a month; see [Price](/docs/vchord/benchmark/price/).

<a id="Scalability"></a><a id="laion-100m--laion-5m"></a><a id="laion-replica-scaling"></a>

## Read replicas up to 10,000 QPS {#scalability}

Spreading queries over streaming replicas brought throughput to 10,000 queries per second with 7 `r7i.xlarge` replicas for LAION-5M and 2 `r7i.16xlarge` replicas for LAION-100M, at about 0.90–0.93 top-10 recall. [Scalability](/docs/vchord/admin/scalability/#results) has the setup, the client, and the per-replica results.

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="Throughput by number of client workers for LAION-5M on 5 to 15 replicas and LAION-100M on 2 replicas" style="width: 100%; height: auto; margin: 0 auto; display: block;" />
