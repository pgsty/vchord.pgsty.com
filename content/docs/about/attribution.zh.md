---
title: 署名与上游来源
linkTitle: 署名与来源
description: vchord.pgsty.com 的上游内容来源、版权声明与适配修改记录。
weight: 20
icon: fa-solid fa-scroll
aliases:
  - "/about/attribution/"
---

`vchord.pgsty.com` 由 [PGSTY](https://pigsty.cc/) 维护，旨在为 **Vchord** 扩展家族（**`vchord`**、**`vchord_bm25`** 与 **`pg_tokenizer`**）提供全面、可检索的文档与工程技术参考。

## 上游来源 {#upstream-sources}

1. **文档内容（`content/docs/`、`content/docs/vectors/`、`content/cloud/`）**
   - **源码仓库**：[`https://github.com/tensorchord/pgvecto.rs-docs`](https://github.com/tensorchord/pgvecto.rs-docs)
   - **原始站点**：[`https://docs.vectorchord.ai/`](https://docs.vectorchord.ai/)
   - **版权声明**：© 2023–至今 TensorChord Inc. 及贡献者。
   - **适配说明**：由 VitePress 迁移至 Hugo + [OINK `v1.4.0`](https://github.com/pgsty/oink)，包含 GitHub 风格提示框规范化、KaTeX 数学公式分隔符标准化、站内链接解析修正、结构化导航元数据补齐以及完整中文化翻译。

2. **工程技术博客与发布说明（`content/blog/`）**
   - **原始发布站点**：[`https://blog.vectorchord.ai/`](https://blog.vectorchord.ai/)
   - **版权声明**：© 2023–至今 TensorChord Inc. 及各篇文章作者（`Keming`、`Haze`、`VoVAllen`、`Yifanwang`、`Kolkri`、`Gin`、`Scase`）。
   - **适配说明**：归档整理至 `content/blog/post/` 与 `content/blog/release/`，保留原始发布日期、作者元数据与直接指向原文的 `upstream_link` 溯源链接，并提供完整中文译文。

3. **Vchord 扩展家族（`vchord`、`vchord_bm25` 与 `pg_tokenizer`）**
   - **`vchord`（[`pgsty/vchord`](https://github.com/pgsty/vchord)）派生自**：[`https://github.com/supervc-stack/VectorChord`](https://github.com/supervc-stack/VectorChord)（原 [`tensorchord/VectorChord`](https://github.com/tensorchord/VectorChord)）
   - **`vchord_bm25`（[`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)）派生自**：[`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)（原 [`tensorchord/VectorChord-bm25`](https://github.com/tensorchord/VectorChord-bm25)）
   - **`pg_tokenizer`（[`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)）派生自**：[`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs)（原 [`tensorchord/pg_tokenizer.rs`](https://github.com/tensorchord/pg_tokenizer.rs)）
   - **前代项目**：[`https://github.com/tensorchord/pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs)

## 页面级溯源 {#page-level-provenance}

每一篇源自上游材料的文档页面与博客文章均在 Front Matter 中声明了 `upstream_link`。OINK 会在页面底部自动渲染该上游溯源链接及修改状态标识。
