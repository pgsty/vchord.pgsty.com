---
title: "与 pgvectorscale 的基准测试对比"
linkTitle: "对比 pgvectorscale"
description: "对比 VectorChord 与 pgvectorscale 在内存与磁盘场景下的 QPS、Recall@10/100、索引构建时间及插入性能。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/pgvectorscale.md"
aliases:
  - "/zh/docs/benchmark/pgvectorscale/"
  - "/vectorchord/benchmark/pgvectorscale/"
icon: fa-solid fa-chart-column
---

在本节中，我们将 VectorChord 与提供向量相似性检索能力的 PostgreSQL 扩展 pgvectorscale 进行对比。我们将重点关注四个核心指标：QPS（每秒查询数）、Recall@10/100、索引构建时间（Index Building Time）以及数据插入时间（Insertion Time），并同时探讨内存与磁盘场景下的性能表现。如果您对我们的实现细节感兴趣，请参阅我们的博文《[PostgreSQL 上的向量检索：内存与磁盘方案的对比分析](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/)》。

## QPS 与召回率 {#qps--recall}

<a id="Memory"></a>
### 内存表现 {#memory}

<img src="/docs/images/laion-5m-qps-memory.png" alt="QPS on LAION 5m memory" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

上图展示了查询速度（QPS）与检索质量（Recall@10/100）之间的权衡关系。Recall@10 衡量在前 10 个返回结果中找到真实最近邻向量的比例。通常情况下，牺牲一定的召回率可以换取更高的 QPS，反之亦然。更优秀的系统能够在相同 QPS 下实现更高的召回率，或在相同召回率水平下提供更高的 QPS。我们的目标通常是在保持高召回率目标（例如 95%）的前提下最大化 QPS。

<a id="Disk"></a>
### 磁盘表现 {#disk}

<img src="/docs/images/laion-5m-qps-disk.png" alt="QPS on LAION 5m disk" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

一如既往，在高召回率区间（例如 Recall@10 > 95%），VectorChord 始终能够取得高于其他扩展的 QPS，而 pgvector 与 pgvectorscale 的 QPS 表现则较为接近，位列其后。

## 索引构建 {#index-building}

<img src="/docs/images/all-about-index-building.png" alt="All About Index Building" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

与 pgvectorscale 相比，VectorChord 能够更充分地利用 CPU 资源、减少内存占用，并大幅缩短索引构建时间。

## 数据插入时间 {#insertion-time}

<img src="/docs/images/pgvector-vchord-pgvectorscale-insert-performance.png" alt="Insertion Time" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

如图所示，在数据插入性能方面，VectorChord **（1565 次插入/秒）** 的表现远超 pgvector **（246 次插入/秒）** 和 pgvectorscale **（107 次插入/秒）**。对于大多数工作负载而言，100 次插入/秒已经足够；但如果您在生产环境中需要持续高频地写入大量向量（例如达到 500 次插入/秒），其他扩展的写入瓶颈就会成为一个棘手的问题。
