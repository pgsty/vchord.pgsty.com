---
title: "与 pgvector 对比"
linkTitle: "对比 pgvector"
description: "在 GIST-1M（960 维）上对比 vchordrq 与 pgvector HNSW：同等精度下的每秒查询数、建索引时间、插入时间和查询完成时间。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/benchmark/pgvector.md"
aliases:
  - "/docs/benchmark/pgvector/"
  - "/vectorchord/benchmark/pgvector/"
icon: fa-solid fa-scale-balanced
---

本页在 GIST-1M（100 万条 960 维向量）上对比 `vchordrq` 与 pgvector 的 HNSW 索引：同样精度下 vchord 回答查询快多少，建索引和更新索引又少花多少时间。数据出自 [Store 400k Vectors for $1 in PostgreSQL](/zh/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/)（2024 年 12 月）。

<a id="qps--recall"></a>

## 每秒查询数 {#qps-and-recall}

<img src="/docs/images/gist-1m-top10.png" alt="GIST-1M 上 top 100 查询的每秒查询数与平均精度：vchord（IVF + RaBitQ）对比 pgvector HNSW" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

对 top-100 查询，在两者都有测量值的每个精度上，vchord 的每秒查询数都是 pgvector HNSW 的两倍以上。文章没有给出这张图的测试硬件。

<a id="index-build-time--insert-time--query-completion-time"></a>

## 建索引、插入与查询时间 {#build-and-insert}

这一轮测试用一台 AWS `i4i.large`（2 vCPU、16 GB 内存）和 pgvector 0.8.0。先写入 70 万条向量、建索引，再插入剩下的 30 万条，预热后用单线程跑查询。vchord 的 k-means 在另一台机器上完成，再以[外部构建](/zh/docs/vchord/usage/external-build/)的方式导入；文章没有说明这一步耗时多少。

| | vchord | pgvector 0.8.0 |
| --- | --- | --- |
| 建索引 | 186 秒 | 3,043 秒 |
| 插入 | 145 秒 | 2,052 秒 |
| 查询完成 | 4.42 秒 | 28 秒 |

<img src="/docs/images/pgvector-vchord-compare.png" alt="GIST-1M 上 vchord 与 pgvector 0.8.0 的建索引时间、插入时间和查询完成时间" style="width: 100%; height: auto; margin: 0 auto; display: block;" />
