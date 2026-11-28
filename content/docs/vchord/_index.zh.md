---
title: "vchord 文档"
linkTitle: "vchord"
description: "在 PostgreSQL 中为 pgvector 向量列提供磁盘友好的近似最近邻索引。"
weight: 100
icon: fa-solid fa-layer-group
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/index.md
upstream_modified: true
aliases:
  - "/vchord/"
  - "/vectorchord/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

`vchord` 为 PostgreSQL 中的 [pgvector](/zh/docs/vector/) 向量列提供两种近似最近邻索引：`vchordrq` 内存占用小、数据超出内存也能扩展；`vchordg` 是面向低延迟检索的图索引。表和查询都不用改。当前版本为 [1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0)，支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19。

## 从这里开始 {#start}

- [概览](/zh/docs/vchord/getting-started/overview/) — 为什么用 vchord、两种索引怎么选，以及五分钟上手。
- [安装](/zh/docs/vchord/getting-started/installation/) — EL、Debian、Ubuntu 软件包，发布压缩包，或从源码构建。
- [vchordrq 索引](/zh/docs/vchord/usage/indexing/) — 主力索引怎样回答查询、怎样定规模、怎样调召回率。
- [过滤](/zh/docs/vchord/usage/filtering/) — 只取某个租户、类别、时间段内，或某个距离内的最近邻。
- [升级与迁移](/zh/docs/vchord/admin/migration/) — 原地升级 vchord，或从 pgvector、pgvecto.rs 迁移。
- [性能调优](/zh/docs/vchord/usage/postgresql-tuning/) — 并行构建、shared_buffers、重启后预热和磁盘读取。
{.cards}

## 深入了解 {#more}

- [vchordg 索引](/zh/docs/vchord/usage/graph-index/) — 图索引的工作方式与内存预算。
- [多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/) — 用 `@#` 做 ColBERT 式的 MaxSim 检索。
- [量化类型](/zh/docs/vchord/usage/quantization-types/) — 以每维 8 或 4 比特存储向量。
- [测量召回率](/zh/docs/vchord/usage/measure-recall/) — 用真实查询测量并调整召回率。
- [构建大型索引](/zh/docs/vchord/usage/partitioning-tuning/) — 上亿行乃至十亿行的索引构建。
- [外部构建](/zh/docs/vchord/usage/external-build/) — 在 GPU 上训练聚类中心再建索引。
- [基准测试](/zh/docs/vchord/benchmark/) — 与其他系统对比吞吐、召回率和成本。
- [应用案例](/zh/docs/vchord/use-case/) — 混合检索、ColBERT 重排、视觉文档检索。
- [客户案例](/zh/docs/vchord/customer-stories/) — 三台 PostgreSQL 服务器检索 32 亿条卫星嵌入。
{.cards}
