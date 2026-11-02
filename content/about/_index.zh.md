---
title: 关于 Vchord 与 vchord.pgsty.com
linkTitle: 关于
description: 由 PGSTY 维护的 Vchord 扩展家族及文档站点的项目概览、开源许可、上游署名与商标政策。
type: docs
sidebar_root_for: self
weight: 50
icon: fa-solid fa-circle-info
cascade:
  type: docs
---

**Vchord** 是面向 PostgreSQL 的可扩展向量检索与 BM25 全文检索扩展家族，由 **[`vchord`](https://github.com/pgsty/vchord)**、**[`vchord_bm25`](https://github.com/pgsty/vchord_bm25)** 与 **[`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)** 三个扩展组成。

本仓库（`pgsty/vchord.pgsty.com`）与网站（`https://vchord.pgsty.com/`）为 [`pgsty/vchord`](https://github.com/pgsty/vchord)、[`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 提供完整、快速、本地优先的文档与技术博客参考，由 [PGSTY](https://pigsty.cc/) 基于 [OINK 1.4.0](https://oink.pgsty.com/) 文档框架构建与维护。

> [!NOTE]
> **`pgsty/vchord`、`pgsty/vchord_bm25` 与 `pgsty/pg_tokenizer` 分别是 `tensorchord/VectorChord`、`tensorchord/VectorChord-bm25` 与 `tensorchord/pg_tokenizer.rs` 的 PGSTY 维护分支。** 详情请参阅[署名与来源](/zh/about/attribution/)及[商标声明](/zh/about/trademark/)。

## 文档范围 {#documentation-scope}

| 板块 | 涵盖内容 |
| :--- | :--- |
| **[`vchord` 文档](/zh/docs/)** | 安装指南、从 `pgvecto.rs` 迁移、`vchordrq` 与 `vchordg` 索引构建、MaxSim 多向量检索、范围过滤查询、PostgreSQL 参数调优、外部索引预计算、基准测试与 SQL 参考手册。 |
| **[`vchord_bm25` 与 `pg_tokenizer`](/zh/bm25/)** | [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)（`vchord_bm25`）与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)（`pg_tokenizer`）的完整文档：Okapi BM25 相关性评分、Block-WeakAnd Top-K 索引扫描、预过滤检索、与 `vchord` 协同的混合检索、多语言文本分析器（`jieba`、`lindera`、Snowball、HuggingFace）以及 SQL/GUC 参考手册。 |
| **[工程技术博客](/zh/blog/)** | 全部 37 篇工程深度解析、基准测试对比、混合检索教程以及历次版本发布公告。 |
