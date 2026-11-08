---
title: 关于 Vchord 与 vchord.pgsty.com
linkTitle: 关于
description: 由 Pigsty 社区维护的 Vchord 发行版及文档站点的项目概览、开源许可、上游署名与商标政策。
type: docs
weight: 5
icon: fa-solid fa-circle-info
upstream_source: ""
upstream_link: ""
upstream_modified: false
aliases:
  - "/about/"
cascade:
  type: docs
  upstream_source: ""
  upstream_link: ""
  upstream_modified: false
---

**Vchord（`vchord`）** 是一款专为可扩展、高性能且磁盘友好的向量相似度搜索而设计的 PostgreSQL 扩展，是 [`pgvecto.rs`](/zh/docs/vectors/) 的下一代架构继任者。

本仓库（`pgsty/vchord.pgsty.com`）与网站（`https://vchord.pgsty.com/`）为 [`pgsty/vchord`](https://github.com/pgsty/vchord)、[`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 提供完整、快速、本地优先的文档与技术博客参考，由 [Pigsty](https://pigsty.cc/) 社区基于 [OINK 1.5.1](https://oink.pgsty.com/) 文档框架构建与维护。

> [!NOTE]
> **`pgsty/vchord`、`pgsty/vchord_bm25` 与 `pgsty/pg_tokenizer` 分别是 `tensorchord/VectorChord`、`supervc-stack/VectorChord-bm25` 与 `supervc-stack/pg_tokenizer.rs` 的社区维护分支。** 本项目与 TensorChord Inc. 不存在隶属、背书或赞助关系。详情请参阅[署名与来源](/zh/docs/about/attribution/)及[商标声明](/zh/docs/about/trademark/)。

## 文档范围 {#documentation-scope}

| 板块 | 涵盖内容 |
| :--- | :--- |
| **[`vchord` 文档](/zh/docs/vchord/)** | 安装指南、从 `pgvecto.rs` 迁移、`vchordrq` 与 `vchordg` 索引构建、MaxSim 多向量检索、范围过滤查询、PostgreSQL 参数调优、外部索引预计算、基准测试与 SQL 参考手册。 |
| **[`vchord_bm25` 文档](/zh/docs/bm25/)** | [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 的完整文档：Okapi BM25 相关性评分、Block-WeakAnd Top-K 索引扫描、预过滤检索、与 `vchord` 协同的混合检索，以及 SQL/GUC 与 BEIR 基准测试参考手册。 |
| **[`pgvector` 文档](/zh/docs/vector/)** | `pgvector` 完整文档：`vector`、`halfvec`、`bit` 与 `sparsevec` 向量类型、距离操作符、HNSW 与 IVFFlat 索引、迭代式索引扫描与量化方案。 |
| **[`pgvecto.rs` 历史归档](/zh/docs/vectors/)** | `pgvecto.rs`（`vectors` 扩展）的完整历史文档，包括安装部署、索引构建、过滤查询、开发框架集成与日常运维。 |
| **[`pg_tokenizer` 文档](/zh/docs/tokenizer/)** | [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 的完整文档：文本分析流水线、字符与词元过滤器、Snowball 词干提取、自定义语料模型、HuggingFace 模型、中文结巴（`jieba`）与日文 `lindera` 分词。 |
| **[`pg_bestmatch` 文档](/zh/docs/bestmatch/)** | `pg_bestmatch.rs` 扩展文档：在 PostgreSQL 内部生成兼容 [`pgvector`](/zh/docs/vector/) `sparsevec` 与 [`pgvecto.rs`](/zh/docs/vectors/) `svector` 的 BM25 稀疏向量。 |
| **[工程技术博客](/zh/blog/)** | 全部 37 篇工程深度解析、基准测试对比、混合检索教程以及历次版本发布公告（涵盖 `pgvecto.rs 0.2` 至 `VectorChord 1.1`）。 |
| **[VectorChord Cloud](/zh/cloud/)** | VectorChord Cloud 托管集群、连接端点、弹性扩缩容、监控指标与账单管理参考文档。 |
{.wide .expand}
