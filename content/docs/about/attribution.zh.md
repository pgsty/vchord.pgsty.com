---
title: 署名与上游来源
linkTitle: 署名与来源
description: vchord.pgsty.com 的上游内容来源、版权声明、社区接手维护说明与适配修改记录。
weight: 20
icon: fa-solid fa-scroll
aliases:
  - "/about/attribution/"
---

`vchord.pgsty.com` 由 [PGSTY](https://pigsty.cc/) 社区维护，旨在为 **Vchord** 扩展家族（**`vchord`**、**`vchord_bm25`** 与 **`pg_tokenizer`**）提供全面、可检索的文档与工程技术参考。

## 社区接手与维护声明 {#stewardship}

`VectorChord`、`VectorChord-bm25` 与 `pg_tokenizer.rs` 的原开发公司 **TensorChord Inc.** 已清算并停止对上游仓库的日常维护。应原作者请求，**[PGSTY](https://pigsty.cc/)** 社区正式接手维护这三个扩展：

- **供应链持续性与版本适配**：PGSTY 社区持续维护代码仓库，已将三个扩展统一升级至 **`pgrx 0.19.3`** 基线（支持 `pg14`–`pg19` 特性），并针对 **PostgreSQL**（`PG 14–18`）测试与打包扩展套件。主流 [16 个 Linux 发行版与架构目标](/zh/download/)均提供预构建原生 RPM/DEB 软件包，完整的依赖项与开源许可证盘点详见[软件物料清单 (SBOM)](/zh/docs/about/sbom/)。
- **功能演进路线图**：我们不承诺任何新功能的开发，新功能需求与演进路线图将视维护团队的精力余量来响应。
- **安全问题反馈**：如果您发现任何安全问题或严重缺陷，非常欢迎通过 [GitHub Issues](https://github.com/pgsty/vchord/issues) 提交给我们。

## 上游来源 {#upstream-sources}

1. **文档内容（`content/docs/`、`content/cloud/`）**
   - **VectorChord 与 pgvecto.rs 文档**：[`https://github.com/tensorchord/pgvecto.rs-docs`](https://github.com/tensorchord/pgvecto.rs-docs)（`https://docs.vectorchord.ai/`）—— © 2023–2026 TensorChord Inc.（Apache-2.0）
   - **BM25 与分词器文档**：[`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)、[`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs) 与 [`https://github.com/tensorchord/pg_bestmatch.rs`](https://github.com/tensorchord/pg_bestmatch.rs) —— © 2024–2026 TensorChord Inc.
   - **pgvector 文档（`content/docs/vector/`）**：整理自 [`https://github.com/pgvector/pgvector`](https://github.com/pgvector/pgvector) —— © 2021–2026 Andrew Kane（PostgreSQL 许可证）。
   - **适配说明**：迁移并统一整理至 Hugo + [OINK `v1.4.0`](https://github.com/pgsty/oink)，包含 GitHub 风格提示框规范化、KaTeX 数学公式分隔符标准化、站内链接解析修正、结构化导航元数据补齐以及完整中文化翻译。

2. **工程技术博客与发布说明（`content/blog/`）**
   - **原始发布站点**：[`https://blog.vectorchord.ai/`](https://blog.vectorchord.ai/)
   - **版权声明**：© 2023–2026 TensorChord Inc. 及各篇文章原作者（[Ce Gao](https://github.com/gaocegege)、[Jinjing Zhou](https://github.com/VoVAllen)、[Junyu Chen](https://github.com/cutecutecat)、[Keming Yang](https://github.com/kemingy)、[xieydd](https://github.com/xieydd)、[Zoie Wang](https://hashnode.com/@zoie) 以及 [TensorChord 团队](https://github.com/tensorchord)）。
   - **适配说明**：归档整理至 `content/blog/post/` 与 `content/blog/release/`，保留原始发布日期、原作者主页链接、单篇版权声明与直接指向原文的 `upstream_link` 溯源链接，并提供完整中文译文。

3. **Vchord 扩展家族（`vchord`、`vchord_bm25` 与 `pg_tokenizer`）**
   - **`vchord`（[`pgsty/vchord`](https://github.com/pgsty/vchord)）Fork 自**：[`https://github.com/tensorchord/VectorChord`](https://github.com/tensorchord/VectorChord)
   - **`vchord_bm25`（[`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)）Fork 自**：[`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)
   - **`pg_tokenizer`（[`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)）Fork 自**：[`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs)
   - **前代项目**：[`https://github.com/tensorchord/pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs)

## 页面级溯源 {#page-level-provenance}

每一篇源自上游材料的文档页面与博客文章均在 Front Matter（或章节 `cascade`）中声明了 `upstream_link` 与 `upstream_copyright`。OINK 会在页面底部自动渲染上游原文链接、原作者/上游版权归属及修改状态标识。
