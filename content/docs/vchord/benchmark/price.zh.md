---
title: "价格基准"
linkTitle: "价格"
description: "2024 年 12 月，用一台装了 vchord 的 PostgreSQL 服务器承载 1 亿条 768 维向量要花多少钱，与 Pinecone、Qdrant 和全内存 pgvector 的对比。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/price.md"
aliases:
  - "/docs/benchmark/price/"
  - "/vectorchord/benchmark/price/"
icon: fa-solid fa-coins
---

本页比较在一台装了 vchord 的 PostgreSQL 服务器上存放 1 亿条 768 维向量的月成本，以及托管服务和全内存方案的月成本。数据出自 [Store 400k Vectors for $1 in PostgreSQL](/zh/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/)，云服务价格取 2024 年 12 月的标价。

## 每美元能存多少向量 {#vectors-per-dollar}

测试使用 LAION-100M 数据集（1 亿条 768 维向量），跑在一台 AWS `i4i.xlarge` 上：4 vCPU、32 GB 内存，向量和索引都放在一块 937 GB 的 NVMe SSD 上，每月约 250 美元。在 16 个客户端线程下，它以 0.95 的 top-10 召回率每秒回答 131 次查询；按线程数拆分的数据见[性能](/zh/docs/vchord/benchmark/performance/#laion-100m-on-i4ixlarge)。

折算下来，每月每美元能存 40 万条向量：是 Pinecone 存储优化型实例的 6 倍，是全内存 pgvector 或 pgvecto.rs HNSW 索引的 26 倍。

<img src="/docs/images/price-benchmark.png" alt="vchord、Pinecone、Qdrant 与全内存 pgvector 或 pgvecto.rs 每月每美元可存储的向量数" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

## 1 亿条向量的月成本 {#monthly-cost}

其他系统的成本根据 [MyScale benchmark](https://myscale.github.io/benchmark/) 的数据推算：

| 系统 | 每月费用 |
| --- | --- |
| vchord，一台 `i4i.xlarge` | $247 |
| Pinecone，存储优化型 | $1,600 |
| Qdrant | $4,374 |
| pgvector 或 pgvecto.rs，索引全部放在内存 | $6,580 |

<img src="/docs/images/price-benchmark-monthly.png" alt="在 vchord、Pinecone、Qdrant 与全内存 pgvector 或 pgvecto.rs 中存放 1 亿条 768 维向量的月成本" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

成本差距来自索引放在哪里。vchord 从 NVMe SSD 上回答查询，内存里只需要聚类中心和常用的列表；HNSW 索引要保持速度，就得把整张图放进内存。原理见[概览](/zh/docs/vchord/getting-started/overview/)。
