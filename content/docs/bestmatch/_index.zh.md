---
title: "pg_bestmatch 文档"
linkTitle: "pg_bestmatch"
description: "在 PostgreSQL 内部生成 Okapi BM25 稀疏向量，并基于 pgvector（sparsevec）或 pgvecto.rs（svector）执行高性能关键词相关性检索。"
weight: 500
icon: fa-solid fa-ranking-star
type: docs
sidebar_root_for: self
upstream_source: bestmatch
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs
upstream_modified: true
aliases:
  - "/zh/bestmatch/"
no_list: true
cascade:
  type: docs
  upstream_source: bestmatch
  upstream_modified: true
---

**`pg_bestmatch`**（`pg_bestmatch.rs`）是一个基于 Rust（`pgrx`）开发的 PostgreSQL 扩展，它通过将文档与查询文本转化为兼容 [`pgvector`](/zh/docs/vector/)（`sparsevec`）与 [`pgvecto.rs`](/zh/docs/vectors/)（`svector`）的 **BM25 加权稀疏向量**，在 PostgreSQL 内部原生实现 Okapi BM25 全文相关性排序。

> [!IMPORTANT] 演进推荐：`vchord_bm25` + `pg_tokenizer`
> `pg_bestmatch.rs` 是 TensorChord 第一代基于稀疏向量内积的 BM25 检索方案。对于新建生产环境，我们推荐使用新一代 [`vchord_bm25`](/zh/docs/bm25/) 搭配 [`pg_tokenizer`](/zh/docs/tokenizer/)——它采用专门设计的 **Block-WeakAnd（WAND）** 倒排索引替代了稀疏向量 HNSW 近似图检索，支持 100% 精确的 Top-K BM25 计分与更高吞吐量。

## 核心能力

- **数据库内原生生成 BM25 稀疏向量**：在 `bm25_catalog` 模式中维护语料库词频（TF）、逆文档频率（IDF）与平均文档长度统计信息，直接为文档与查询生成 BM25 稀疏向量。
- **无缝对接 [`pgvector`](/zh/docs/vector/) 与 [`pgvecto.rs`](/zh/docs/vectors/)**：支持直接输出标准 `sparsevec`（`pgvector 0.7.0+`）或 `svector`（`pgvecto.rs`），使用负内积操作符 `<#>` 即可计算 BM25 得分并利用 HNSW 索引加速。
- **内置分词器**：内置 HuggingFace `bert-base-uncased` WordPiece 词表（`30,522` 维），并提供独立的 `tokenize(text)` SQL 分词函数。

## 文档章节导航

{{< cards >}}
{{< card title="安装与工作原理" icon="fa-solid fa-rocket" link="/zh/docs/bestmatch/getting-started/" >}}
深入了解 `pg_bestmatch` 如何将 Okapi BM25 文本相关性排序转化为稀疏向量内积运算，并通过预编译包或源码编译方式安装启用扩展。
{{< /card >}}
{{< card title="使用指南" icon="fa-solid fa-code" link="/zh/docs/bestmatch/usage/" >}}
基于斯坦福 LoCo 基准数据集的端到端实战教程，完整演示结合 [`pgvector`](/zh/docs/vector/) `sparsevec` 与 [`pgvecto.rs`](/zh/docs/vectors/) `svector` 的 HNSW 索引检索流程。
{{< /card >}}
{{< card title="SQL 参考与方案对比" icon="fa-solid fa-book-open" link="/zh/docs/bestmatch/reference/" >}}
查阅 `bm25_create`、`bm25_refresh`、`bm25_drop`、`bm25_document_to_svector`、`bm25_query_to_svector` 与 `tokenize` 完整参考及架构对比。
{{< /card >}}
{{< /cards >}}
