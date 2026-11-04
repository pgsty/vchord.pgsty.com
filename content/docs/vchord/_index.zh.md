---
title: "vchord 文档"
linkTitle: "vchord"
description: "基于 RaBitQ 量化技术，在 PostgreSQL 中实现可扩展、高速且磁盘友好的向量相似性检索。"
weight: 100
icon: fa-solid fa-layer-group
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/index.md
upstream_modified: true
aliases:
  - "/zh/vchord/"
  - "/zh/vectorchord/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

**`vchord`**（VectorChord）是基于 [`pgvector`](/zh/docs/vector/) 构建的 PostgreSQL 扩展，专为可扩展、高性能且磁盘友好的向量相似性检索设计。依托 **RaBitQ** 1-bit/4-bit/8-bit 量化技术，它提供倒排文件（`vchordrq`）与单层图（`vchordg`）两种索引访问方法，并原生支持多向量 MaxSim（`@#`）、球面范围查询（`<<->>`）以及外部聚类中心预计算。

## 核心章节导航

{{< cards >}}
{{< card title="快速上手" icon="fa-solid fa-rocket" link="/zh/docs/vchord/getting-started/" >}}
涵盖 `vchord` 整体架构概览、快速开始 SQL 教程、通过 Pigsty 原生包或 Docker（Obsolete） 容器部署安装，以及从 [`pgvecto.rs`](/zh/docs/vectors/) 迁移的完整指南。
{{< /card >}}
{{< card title="使用指南" icon="fa-solid fa-code" link="/zh/docs/vchord/usage/" >}}
详解 `vchordrq` 与 `vchordg` 索引构建、最近邻与球面范围检索、预过滤查询、索引预热、外部预计算构建与完整 SQL 参数参考。
{{< /card >}}
{{< card title="应用场景" icon="fa-solid fa-diagram-project" link="/zh/docs/vchord/use-case/" >}}
支持 ColBERT 多向量 MaxSim（`@#`）延迟交互与 ColPali 视觉文档检索，以及结合 [`vchord_bm25`](/zh/docs/bm25/) 与 [`pg_tokenizer`](/zh/docs/tokenizer/) 的 RRF 混合检索。
{{< /card >}}
{{< card title="基准测试与成本" icon="fa-solid fa-chart-line" link="/zh/docs/vchord/benchmark/" >}}
提供基于 GIST-1M、Cohere-10M 与 LAION-100M 标准数据集的可复现吞吐性能、召回精度、内存开销与云端 TCO 成本对比分析。
{{< /card >}}
{{< card title="运维管理" icon="fa-solid fa-sliders" link="/zh/docs/vchord/admin/" >}}
涵盖生产环境 GUC 参数调优、PostgreSQL 共享内存规划、I/O 并发设置、VACUUM 索引维护、Kubernetes（Obsolete） 部署与版本升级流程。
{{< /card >}}
{{< card title="用户案例" icon="fa-solid fa-earth-americas" link="/zh/docs/vchord/customer-stories/" >}}
深入了解牛津大学与 Earth Genome 团队如何利用 `vchord` 在单台 PostgreSQL 实例中高效存储并检索 30 亿地球观测嵌入向量。
{{< /card >}}
{{< /cards >}}

## 关键专题直达

{{< cards >}}
{{< card title="vchordrq 与 vchordg 索引选型" icon="fa-solid fa-sitemap" link="/zh/docs/vchord/usage/indexing/" >}}
深入对比磁盘友好型层次化 K-Means 倒排索引（`vchordrq`）与低延迟单层图索引（`vchordg`），掌握核心构建与查询参数配置。
{{< /card >}}
{{< card title="RaBitQ4 与 RaBitQ8 量化类型" icon="fa-solid fa-compress" link="/zh/docs/vchord/usage/quantization-types/" >}}
将 32 位浮点向量压缩为 4-bit（`rabitq4`）或 8-bit（`rabitq8`）原生量化存储类型，兼顾极高空间压缩比与严格理论误差下界。
{{< /card >}}
{{< card title="多向量 MaxSim (@#) 检索" icon="fa-solid fa-cubes" link="/zh/docs/vchord/usage/multi-vector-retrieval/" >}}
基于 WARP 动态剪枝对 `vector[]` 词元向量数组建立索引，在标准 SQL 中直接运行 ColBERTv2 延迟交互与 ColPali 视觉文档检索。
{{< /card >}}
{{< card title="外部预计算构建索引" icon="fa-solid fa-server" link="/zh/docs/vchord/usage/external-build/" >}}
将 K-Means 聚类质心计算卸载至外部 CPU 或 GPU 集群执行，仅需约 20 分钟即可完成 1 亿规模向量索引构建且零主库资源争用。
{{< /card >}}
{{< card title="生产参数调优与内存规划" icon="fa-solid fa-gauge-high" link="/zh/docs/vchord/usage/postgresql-tuning/" >}}
针对高并发生产负载精细调优 `probes`、`epsilon`、`ef_search`、`io_search`、`max_scan_tuples` 及 PostgreSQL 共享内存配置。
{{< /card >}}
{{< card title="从 pgvecto.rs 平滑迁移" icon="fa-solid fa-right-left" link="/zh/docs/vchord/admin/migration/" >}}
提供从 [`pgvecto.rs`](/zh/docs/vectors/)（`vectors` 扩展）或 [`pgvector`](/zh/docs/vector/) HNSW/IVFFlat 平滑迁移至 `vchord` 的数据类型与索引升级实操指南。
{{< /card >}}
{{< /cards >}}
