---
title: "性能基准"
linkTitle: "性能"
description: "vchordrq 在 LAION 图像嵌入上的每秒查询数：500 万条向量与其他向量数据库对比，1 亿条向量跑在一台 4 vCPU 服务器上，以及用副本达到 10,000 QPS。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/performance.md"
aliases:
  - "/docs/benchmark/performance/"
  - "/vectorchord/benchmark/performance/"
icon: fa-solid fa-gauge-high
---

本页给出 `vchordrq` 在 LAION 数据集（768 维图像嵌入）上、在给定召回率下每秒能回答多少次查询：单台服务器上的 500 万条和 1 亿条向量，以及流复制副本。单机测试出自 [Store 400k Vectors for $1 in PostgreSQL](/zh/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/)（2024 年 12 月）。

<a id="QPS"></a><a id="qps"></a>

## LAION-5M：与其他向量数据库对比 {#laion-5m}

测试用 [MyScale benchmark](https://myscale.github.io/benchmark/) 的单线程客户端，跑在一台 AWS `r6a.xlarge` 上（4 vCPU、32 GB 内存、200 GB EBS）。索引有 8,192 个列表，PostgreSQL 设置 `shared_buffers = 28GB`、`jit = off`、`effective_io_concurrency = 200`，未预热，跑了两轮。其他系统的结果来自 MyScale benchmark，硬件见图例。

<img src="/docs/images/laion-5m-top10.png" alt="LAION-5M 上 vchord、MyScale、pgvector、pgvecto.rs、Pinecone、Qdrant、Weaviate、Zilliz、Elasticsearch 与 OpenSearch 的每秒查询数与 top-10 召回率" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

在 0.97 到 0.98 的 top-10 召回率区间，vchord 的每秒查询数是图中其他任何系统的三倍以上。文章还提到，top-100 的结果与每月约 460 美元的 Zilliz Performance 4CU 实例相当，而 `r6a.xlarge` 每月约 166 美元。

<a id="laion-100m-on-i4i-xlarge"></a>

## LAION-100M：一台 `i4i.xlarge` {#laion-100m-on-i4ixlarge}

测试把 1 亿条向量放在一台 AWS `i4i.xlarge` 上：4 vCPU、32 GB 内存，向量和索引都在一块 937 GB 的 NVMe SSD 上。单个查询线程时，0.95 的 top-10 召回率下每秒 16.2 次查询，0.95 的 top-100 召回率下每秒 4.3 次。

<img src="/docs/images/laion-100m-multi-thread.png" alt="LAION-100M 上每秒查询数随查询线程数的变化：top 10 分别用 100 和 400 个探查列表，top 100 用 200 个" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

增加客户端线程、召回率保持在 0.95 以上时，top 10、100 个探查列表的配置在 16 个线程下达到每秒 131 次查询。这台机器每月约 250 美元，见[价格](/zh/docs/vchord/benchmark/price/)。

<a id="Scalability"></a><a id="laion-100m--laion-5m"></a><a id="laion-replica-scaling"></a>

## 用只读副本达到 10,000 QPS {#scalability}

把查询分摊到流复制副本上，LAION-5M 用 7 台 `r7i.xlarge` 副本、LAION-100M 用 2 台 `r7i.16xlarge` 副本，就达到了每秒 10,000 次查询，top-10 召回率约 0.90–0.93。部署方式、客户端配置和逐项结果见[可扩展性](/zh/docs/vchord/admin/scalability/#results)。

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="LAION-5M 在 5 到 15 台副本、LAION-100M 在 2 台副本上的吞吐随客户端 worker 数的变化" style="width: 100%; height: auto; margin: 0 auto; display: block;" />
