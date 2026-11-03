---
title: "Performance Benchmarking"
linkTitle: "Performance"
description: "Here we present a comprehensive benchmark comparing our implementation of VectorChord with other vector databases, focusing on QPS and scalability.  If you are "
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/performance.md"
aliases:
  - "/docs/benchmark/performance/"
  - "/vectorchord/benchmark/performance/"
icon: fa-solid fa-gauge-high
---

Here we present a comprehensive benchmark comparing our implementation of VectorChord with other vector databases, focusing on QPS and scalability.  If you are interested in the details of our implementation, please refer to our blog [VectorChord: Store 400k Vectors for $1 in PostgreSQL](/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/).

<a id="QPS"></a>
## QPS

### LAION 5M

<img src="/docs/images/laion-5m-top10.png" alt="QPS on LAION 5M top 10" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

In LAION 5M dataset, VectorChord achieved more than 3x QPS at 0.95 recall compared to different vector databases, including MyScale, pgvector, pinecone, weaviate, qdrant and zilliz(milvus).

<a id="laion-100m-on-i4i-xlarge"></a>
### LAION 100M on `i4i.xlarge`

<img src="/docs/images/laion-100m-multi-thread.png" alt="QPS on LAION 100M" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

This setup utilizes 4 CPUs and 32 GB of memory, with 937 GB of SSD storage for the 100 million vectors. We achieved a QPS of 16.2 at a recall rate of 0.95 for the top 10 results and 4.3 at 0.95 for the top 100, using a single-threaded query. The results are truly impressive.

<a id="Scalability"></a>
## Scalability

If you are interested VectorChord scalable capability, you can refer our blog [Vector Search at 10,000 QPS in PostgreSQL with VectorChord](/blog/post/vector-search-at-10000-qps-in-postgresql-with-vectorchord/).

### LAION 100M && LAION 5M

| **dataset** | **minimal hardware for 10000+ QPS** | **number of vcpu** | **estimate cost per month** |
| --- | --- | --- | --- |
| LAION-5m | r7i.xlarge × 7 | 4 × 7 = 28 vcpu | $0.2646 × 7 × 720 = $1334 |
| LAION-100m | r7i.16xlarge × 2 | 64 × 2 = 128 vcpu | $4.2336 × 2 × 720 = $6096 |
{.wide .expand}

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="QPS on LAION 100M and LAION 5M" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

> [!TIP]
> The price benchmark is tested on December 5, 2024. We are ongoingly enhancing performance and optimizing costs. For example, VectorChord 0.2 builds on its predecessor with a 30% smaller index size and 50% faster builds. If you want to know the latest benchmark, please contact us at [discord](https://discord.gg/KqswhpVgdU).
