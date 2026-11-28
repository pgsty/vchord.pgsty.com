---
title: "Vchord 套件"
linkTitle: "Vchord 套件"
description: "在同一个 PostgreSQL 数据库中实现向量检索、BM25 关键词排序和多语言分词：每个扩展做什么，以及如何一次装好三个。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/vectorchord-suite.md"
aliases:
  - "/docs/getting-started/vectorchord-suite/"
  - "/vectorchord/getting-started/vectorchord-suite/"
icon: fa-solid fa-boxes-stacked
---

搜索和检索增强生成（RAG）需要两种匹配。嵌入向量能找到换了说法、意思相同的文本；关键词排序能找到被嵌入模糊掉的精确商品编号、报错信息或人名。很多系统为此在 PostgreSQL 旁边再跑一个向量数据库和一个搜索引擎，然后把精力花在让三份数据保持同步上。

Vchord 套件在 PostgreSQL 内部同时完成这两件事：一个事务就能一起更新数据行、向量索引和关键词索引，备份、复制和权限控制也一并覆盖。

| 扩展 | 提供的能力 | 版本 | 文档 |
| --- | --- | --- | --- |
| [`vchord`](https://github.com/pgsty/vchord) | pgvector 向量列的向量索引 | 1.5.0 | [vchord](/zh/docs/vchord/) |
| [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) | 基于 `tsvector` 列的 BM25 排序 top-k 检索 | 1.3.0 | [vchord_bm25](/zh/docs/bm25/) |
| [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) | 生成 `tsvector` 的文本分析器与分词器，支持中文、日文等 | 1.3.0 | [pg_tokenizer](/zh/docs/tokenizer/) |

三个扩展都可以单独使用。只有当 PostgreSQL 内置的 `to_tsvector` 切分不好你的语言或词表时，才需要 `pg_tokenizer`。

## 一次装好三个 {#how-to-use-the-vchord-suite}

<a id="how-to-use-the-vectorchord-suite"></a>

三个扩展都支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19，也都需要预加载。

1. 安装软件包：

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord vchord_bm25 pg_tokenizer
   ```

1. 预加载它们（保留列表中已有的库），然后重启 PostgreSQL：

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord, vchord_bm25, pg_tokenizer';
   ```

1. 在数据库中创建扩展：

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
   ```
{.steps}

各扩展的发布包和源码构建方式见各自的安装页面。`tensorchord/vchord-suite` 容器镜像中是较旧的上游版本，BM25 接口也不同。

## 可以用它做什么 {#use-cases-for-the-vchord-suite}

<a id="use-cases-for-the-vectorchord-suite"></a><a id="hybrid-search"></a><a id="ocr-free-visual-rag"></a><a id="references"></a>

- [混合检索](/zh/docs/vchord/use-case/hybrid-search/) — 在一个查询里分别按嵌入和 BM25 排序，再用倒数排名融合合并两份结果。
- [ColBERT 重排](/zh/docs/vchord/use-case/colbert-rerank/) — 先用段落级嵌入召回，再按词元级 MaxSim 重排。
- [视觉文档检索](/zh/docs/vchord/use-case/colqwen2-modal/) — 用 ColQwen2 把 PDF 页面当作图像检索，无需 OCR。
{.cards}
