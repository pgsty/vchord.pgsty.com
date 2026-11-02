---
math: true
title: "vchord_bm25 文档"
linkTitle: "vchord_bm25"
description: "面向 PostgreSQL 的原生 Okapi BM25 排序索引与 Block-WeakAnd 全文检索扩展（`vchord_bm25`）。"
weight: 200
icon: fa-solid fa-magnifying-glass
type: docs
sidebar_root_for: self
aliases:
  - "/bm25/"
no_list: true
cascade:
  type: docs
  upstream_source: "bm25"
  upstream_link: "https://github.com/tensorchord/VectorChord-bm25"
  upstream_modified: true
---

> [!IMPORTANT]
> 当前源码面向 **0.4.0（尚未发布）**，使用原生 `tsvector` 和新的索引格式。标注 0.3.x 的 `bm25vector` 示例仅适用于旧版。两者不能原地升级；请先阅读[0.4.0 迁移指南](/zh/docs/bm25/reference/migration/)。


**`vchord_bm25`**（由 Pigsty 在 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 维护）是一个使用 Rust（`pgrx`）构建的原生 PostgreSQL 扩展，在 PostgreSQL 内部实现了 **Okapi BM25** 相关性排序算法以及 **Block-WeakAnd（Block-Max WAND）** Top-K 索引扫描访问方法。

配合 **[`pg_tokenizer`](/zh/docs/tokenizer/)**（由 Pigsty 在 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 维护，提供可定制的多语言分词与词表模型）或 PostgreSQL 内置的 `tsvector` 分析器，`vchord_bm25` 将 Elasticsearch/Lucene 级别的词法全文检索排序能力直接带入关系型数据库，并能与 **[`vchord`](/zh/docs/vchord/)** 和 **[`pgvector`](/zh/docs/vector/)** 无缝结合，实现语义 + 词法混合检索。

{{< cards >}}
  {{< card link="/zh/docs/bm25/getting-started/" title="快速上手" icon="fa-solid fa-rocket" >}}
了解为什么需要 BM25，安装 vchord_bm25 与 pg_tokenizer，并运行你的第一条全文排序查询。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/" title="使用与索引指南" icon="fa-solid fa-magnifying-glass" >}}
构建 bm25 索引、执行 Top-K Block-WeakAnd 查询、使用 WHERE 预过滤与检查索引页。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/hybrid-search/" title="混合检索" icon="fa-solid fa-code-merge" >}}
在单条 SQL 中通过 RRF 或 ColBERT 重排序，融合稀疏 BM25 词法检索与 [`vchord`](/zh/docs/vchord/) 稠密向量检索。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/" title="参考手册与基准测试" icon="fa-solid fa-book" >}}
完整的 SQL 类型、操作符、函数、GUC 参数、版本演进历史以及 BEIR 基准测试结果。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/migration/" title="0.3.x 至 0.4.0 迁移指南" icon="fa-solid fa-right-left" >}}
从 `bm25vector` + `pg_tokenizer`（0.3.x）架构迁移至 0.4.0 原生 `tsvector` 索引格式的分步指南。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/" title="pg_tokenizer 文档" icon="fa-solid fa-language" >}}
配置文本分析器、词干提取器、停用词、同义词、HuggingFace 模型、中文结巴（Jieba）与日文 Lindera 分词。
{{< /card >}}
{{< /cards >}}

## 核心特性 {#highlights}

- **纯正的 Okapi BM25 评分**：完整支持逆文档频率（IDF）、词频饱和度控制（\(k_1\)）以及单字节量化的文档长度归一化（\(b\) 与平均文档长度 \(\text{avgdl}\)），从根本上解决了 PostgreSQL 原生 `ts_rank` 的相关性排序局限。
- **Block-WeakAnd 索引加速**：使用差分位打包（Delta-Bitpacking）存储压缩倒排链表，并在每个块中记录最大得分上界，在 Top-K 查询期间直接跳过缺乏竞争力的文档块，无需扫描整条倒排链。
- **多语言分词支持**：在 `v0.1`–`v0.3` 中可配合 [`pg_tokenizer`](/zh/docs/tokenizer/)（支持 `llmlingua2`、`bert_base_uncased`、`wiki_tocken`、`gemma2b`、自定义语料训练模型、中文 `jieba`、日文 `lindera`）使用；在新一代 `main` 架构中更可直接支持 PostgreSQL 原生 `tsvector`。
- **与 Vchord 原生混合检索**：在单条 SQL 查询中同时运行词法 BM25 检索（`vchord_bm25`）与稠密向量检索（`vchordrq`），支持倒数排序融合（RRF）或 ColBERT MaxSim 重排序。
