---
title: "与 pgvectorscale 对比"
linkTitle: "对比 pgvectorscale"
description: "在 LAION-5M 上对比 vchordrq、pgvectorscale 与 pgvector：索引在内存和在磁盘时的每秒查询数、建索引的时间与内存，以及插入速度。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/pgvectorscale.md"
aliases:
  - "/docs/benchmark/pgvectorscale/"
  - "/vectorchord/benchmark/pgvectorscale/"
icon: fa-solid fa-chart-column
---

本页在 LAION-5M（500 万条 768 维向量，L2 距离）上对比三个 PostgreSQL 向量扩展：`vchordrq`、pgvectorscale 的 StreamingDiskANN 和 pgvector 的 HNSW。比较的是决定选型的几个问题：索引放得进内存和放不进内存时各有多快，建一次索引要多少时间和内存，新行能以多快的速度插入。数据出自 [Vector Search Over PostgreSQL: A Comparative Analysis of Memory and Disk Solutions](/zh/blog/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/)（2025 年 4 月），测试版本为 VectorChord 0.2.2、pgvector 0.8.0、pgvectorscale 0.6.0，PostgreSQL 17。

<a id="qps--recall"></a>

## 每秒查询数 {#qps-and-recall}

每个系统跑 10,000 条测试查询，图中是每秒查询数与 top-10、top-100 召回率的关系。vchord 的索引用[外部构建](/zh/docs/vchord/usage/external-build/)建成。

<a id="Memory"></a>

### 索引在内存中 {#memory}

一台 AWS `i4i.xlarge`（4 vCPU、32 GiB 内存、937 GB NVMe SSD），`shared_buffers = 24GB`，足以缓存整个索引。

<img src="/docs/images/laion-5m-qps-memory.png" alt="索引在内存中时，LAION-5M 上 vchord、pgvector 与 pgvectorscale 的每秒查询数与 top-10、top-100 召回率" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

召回率在 0.95 以上时，vchord 的每秒查询数最高。冷启动后的第一次查询，pgvectorscale 比 pgvector 快；索引缓存好之后，pgvector 反超。

<a id="Disk"></a>

### 索引在磁盘上 {#disk}

一台 AWS `c6id.large`（2 vCPU、4 GiB 内存、118 GB NVMe SSD），`shared_buffers = 2GB`，大部分读取都要落到磁盘。4 GiB 内存不够建索引，所以索引在更大的机器上建好后再恢复过来。

<img src="/docs/images/laion-5m-qps-disk.png" alt="索引在磁盘上时，LAION-5M 上 vchord、pgvector 与 pgvectorscale 的每秒查询数与 top-10、top-100 召回率" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

召回率在 0.95 以上时，仍然是 vchord 的每秒查询数最高，pgvector 和 pgvectorscale 相差不大。

## 建索引 {#index-building}

在一台 `i4i.xlarge` 上建索引，`shared_buffers = 1GB`。vchord 分两种方式：内部构建由 `CREATE INDEX` 自己做 k-means；外部构建的 k-means 在另一台带 A10 GPU 的机器上完成。两者都做 25 轮 k-means 迭代。

| | pgvector | pgvectorscale | vchord 内部构建 | vchord 外部构建 |
| --- | --- | --- | --- | --- |
| 构建时间 | 162 分钟 | 187 分钟 | 33 分钟 | 15 分钟 |
| CPU 核利用率 | 100% | 25% | 100% | 100% |
| 内存峰值 | 2.1 GB | 15.2 GB | 9.8 GB | 1.1 GB |
| 构建后磁盘占用 | 40 GB | 28 GB | 41 GB | 41 GB |
{.wide}

<img src="/docs/images/all-about-index-building.png" alt="pgvector、pgvectorscale 以及 vchord 内部与外部构建的 CPU 利用率、构建时间、磁盘占用和内存占用" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

如果外部构建的 k-means 不用 GPU、而在同一台 `i4i.xlarge` 上跑，总共约 50 分钟。磁盘占用最少的是 pgvectorscale。

## 插入速度 {#insertion-time}

在 500 万条向量上建好索引后，在 `i4i.xlarge` 上逐行插入随机向量：

| | 每秒插入行数 |
| --- | --- |
| vchord | 1,565 |
| pgvector | 246 |
| pgvectorscale | 107 |

<img src="/docs/images/pgvector-vchord-pgvectorscale-insert-performance.png" alt="vchord、pgvector 与 pgvectorscale 向已有索引每秒插入的行数" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

`vchordrq` 的新行只需放进离它最近的聚类中心对应的列表；图索引每插入一行，都要先在图上搜索，再给它加边。
