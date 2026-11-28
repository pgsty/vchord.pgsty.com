---
title: 关于 Vchord 与 vchord.pgsty.com
linkTitle: 关于
description: vchord、vchord_bm25 与 pg_tokenizer 由谁维护、来自哪里、采用什么许可证。
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

本站为 [PGSTY](https://pgsty.com) 维护的三个 PostgreSQL 扩展提供文档：用于向量检索的 [vchord](/zh/docs/vchord/)、用于 BM25 排序的 [vchord_bm25](/zh/docs/bm25/)，以及用于分词的 [pg_tokenizer](/zh/docs/tokenizer/)。本站还保留了 vchord 所依赖的 [pgvector](/zh/docs/vector/) 的参考文档，以及已退役的前身 [pgvecto.rs](/zh/docs/vectors/) 和 [pg_bestmatch](/zh/docs/bestmatch/) 的文档。发布说明和技术文章见[博客](/zh/blog/)。

这三个扩展分别是 TensorChord 的 VectorChord、VectorChord-bm25 和 pg_tokenizer.rs 的分支。TensorChord 停止维护后，PGSTY 应原作者之邀接手维护。这些分支与 TensorChord Inc. 没有隶属、背书或赞助关系。

- [致谢与来源](/zh/docs/about/attribution/) — 上游项目与作者，以及对其材料的改编方式。
- [许可证](/zh/docs/about/license/) — vchord 与 vchord_bm25 采用 AGPL-3.0，pg_tokenizer 采用 Apache-2.0，本文档采用 CC BY 4.0。
- [商标](/zh/docs/about/trademark/) — 名称的使用方式。
- [软件物料清单](/zh/docs/about/sbom/) — 依赖及其许可证。
{.cards}

缺陷和安全问题请在 [GitHub](https://github.com/pgsty/vchord/issues) 上报告。
