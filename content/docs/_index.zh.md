---
title: "Vchord 文档中心"
linkTitle: "文档"
description: "PostgreSQL 向量检索、BM25 全文排序与分词扩展套件统一文档中心：涵盖 vchord、vchord_bm25、pg_tokenizer、pgvector、pgvecto.rs 与 pg_bestmatch。"
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://docs.vectorchord.ai/
upstream_modified: true
aliases:
  - "/cloud/"
  - "/cloud/pricing/price-plan/"
  - "/cloud/manage/apikey/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

## 扩展套件导航

{{< cards >}}
{{< card title="vchord" icon="fa-solid fa-layer-group" link="/zh/docs/vchord/" >}}
基于 [`pgvector`](/zh/docs/vector/) 构建的可扩展、磁盘友好向量检索扩展，提供 `vchordrq`（RaBitQ 倒排索引）、`vchordg`（RaBitQ 单层图索引）、多向量 MaxSim（`@#`）与球面范围查询。
{{< /card >}}
{{< card title="vchord_bm25" icon="fa-solid fa-magnifying-glass" link="/zh/docs/bm25/" >}}
PostgreSQL 原生 Okapi BM25 相关性排序索引（`bm25vector`、`<&>` 操作符与 Block-WeakAnd 块级剪枝扫描），赋能高性能全文与混合检索。
{{< /card >}}
{{< card title="pg_tokenizer" icon="fa-solid fa-language" link="/zh/docs/tokenizer/" >}}
独立的多语言文本分析器与词元 ID 编码流水线，支持 Unicode、正则、Jieba、Lindera、HuggingFace、LLMLingua-2、Snowball 词干提取及语料库训练自定义词表。
{{< /card >}}
{{< card title="pgvector" icon="fa-solid fa-circle-nodes" link="/zh/docs/vector/" >}}
PostgreSQL 开源向量相似性检索基础扩展（`vector`、`halfvec`、`bit`、`sparsevec` 数据类型），支持精确/近似最近邻搜索以及 HNSW 与 IVFFlat 索引。
{{< /card >}}
{{< card title="pgvecto.rs" icon="fa-solid fa-cube" link="/zh/docs/vectors/" >}}
[`vchord`](/zh/docs/vchord/) 前身 `pgvecto.rs`（`v0.1`–`v0.4`）的完整历史归档文档与平滑迁移参考手册。
{{< /card >}}
{{< card title="pg_bestmatch" icon="fa-solid fa-ranking-star" link="/zh/docs/bestmatch/" >}}
轻量级 BM25 稀疏向量生成扩展（`pg_bestmatch.rs`），支持将文本转化为带 BM25 权重的 [`pgvector`](/zh/docs/vector/) `sparsevec` 或 [`pgvecto.rs`](/zh/docs/vectors/) `svector` 稀疏向量。
{{< /card >}}
{{< /cards >}}

## vchord 核心文档导航

{{< cards >}}
{{< card title="快速上手" icon="fa-solid fa-rocket" link="/zh/docs/vchord/getting-started/" >}}
架构概览、快速开始教程、通过 Pigsty / Docker / 预编译包安装，以及从 [`pgvecto.rs`](/zh/docs/vectors/) 平滑迁移指南。
{{< /card >}}
{{< card title="使用与索引指南" icon="fa-solid fa-code" link="/zh/docs/vchord/usage/" >}}
使用 `vchordrq` 与 `vchordg` 构建索引、最近邻与球面范围检索、过滤查询、索引预热、外部构建与 SQL 参考。
{{< /card >}}
{{< card title="多向量与混合检索" icon="fa-solid fa-diagram-project" link="/zh/docs/vchord/use-case/" >}}
ColBERT 多向量 MaxSim（`@#`）延迟交互检索，以及结合 [`vchord_bm25`](/zh/docs/bm25/) 与 [`pg_tokenizer`](/zh/docs/tokenizer/) 的混合检索。
{{< /card >}}
{{< card title="基准测试与成本" icon="fa-solid fa-chart-line" link="/zh/docs/vchord/benchmark/" >}}
基于 GIST-1M、Cohere-10M 与 LAION-100M 数据集的可复现性能、召回率、内存开销与 TCO 成本对比。
{{< /card >}}
{{< card title="运维管理与调优" icon="fa-solid fa-sliders" link="/zh/docs/vchord/admin/" >}}
生产环境 GUC 参数调优、共享内存规划、I/O 并发设置、VACUUM 索引维护与版本升级流程。
{{< /card >}}
{{< card title="生产用户案例" icon="fa-solid fa-earth-americas" link="/zh/docs/vchord/customer-stories/" >}}
牛津大学如何利用 `vchord` 在单台 PostgreSQL 中存储并检索 30 亿地球观测嵌入向量。
{{< /card >}}
{{< /cards >}}

## 生态与项目信息

{{< cards >}}
{{< card title="关于 Vchord 套件" icon="fa-solid fa-circle-info" link="/zh/docs/about/" >}}
套件整体架构、六大扩展定位对比，以及 PGSTY 社区接手维护说明。
{{< /card >}}
{{< card title="开源致谢与版权" icon="fa-solid fa-scale-balanced" link="/zh/docs/about/attribution/" >}}
上游源码来源、原作者致谢、开源许可证声明与仓库对应关系。
{{< /card >}}
{{< card title="AGPLv3 开源许可" icon="fa-solid fa-code-branch" link="/zh/docs/about/license/" >}}
PostgreSQL 14–18 软件包矩阵、版本升级脚本策略与安全问题反馈。
{{< /card >}}
{{< /cards >}}
