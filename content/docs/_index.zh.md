---
title: "Vchord 文档中心"
linkTitle: "文档"
description: "vchord、vchord_bm25 与 pg_tokenizer 的文档：在 PostgreSQL 内部实现向量检索、BM25 排序和分词。"
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

三个由 [PGSTY](https://pgsty.com) 维护的 PostgreSQL 扩展，共同覆盖数据库内的检索：向量检索、BM25 关键词排序，以及为它提供输入的分词。三者都可以单独使用，[Vchord 套件](/zh/docs/vchord/getting-started/vectorchord-suite/)介绍了它们如何配合。

## 扩展 {#extension-suite}

- [vchord](/zh/docs/vchord/) — pgvector 向量列的向量索引，数据超出内存也能扩展。版本 1.5.0。
- [vchord_bm25](/zh/docs/bm25/) — 对全文检索列做 BM25 排序检索。版本 1.3.0。
- [pg_tokenizer](/zh/docs/tokenizer/) — 为 BM25 提供分词，支持中文、日文等语言。版本 1.3.0。
{.cards}

## 相关项目 {#related}

<a id="vchord-core-guide"></a><a id="ecosystem"></a>

- [pgvector](/zh/docs/vector/) — vchord 所依赖的向量类型和运算符。
- [pgvecto.rs](/zh/docs/vectors/) — vchord 的前身，已停止开发。
- [pg_bestmatch](/zh/docs/bestmatch/) — vchord_bm25 的前身，已停止开发。
{.cards}

## 关于 {#about}

- [关于本站](/zh/docs/about/) — 谁在维护这些扩展和这份文档。
- [致谢与来源](/zh/docs/about/attribution/) — 本项目来自哪些上游项目和作者。
- [许可证](/zh/docs/about/license/) — 代码采用 AGPL-3.0 与 Apache-2.0，文档采用 CC BY 4.0。
{.cards}
