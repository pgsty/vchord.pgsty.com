---
title: "应用案例"
linkTitle: "应用案例"
description: "涵盖 BM25 + 稠密向量混合检索、ColBERT 重排序以及多模态免 OCR RAG 的端到端实战指南。"
weight: 30
icon: fa-solid fa-diagram-project
upstream_link: ""
aliases:
  - "/zh/docs/use-case/"
  - "/vectorchord/use-case/"
---

| 标题 | 描述 | 链接 | 代码 |
|-------|-------------|------|------|
| 基于 Postgres 原生 BM25 与 VectorChord 的混合检索 | 本文探讨如何在 Postgres 中结合使用 [VectorChord-bm25](https://github.com/pgsty/vchord_bm25)（关键词检索）与 [VectorChord](https://github.com/pgsty/vchord)（语义检索）来实现混合检索。 | [混合检索](/zh/docs/vchord/use-case/hybrid-search/) | [GitHub 仓库](https://github.com/xieydd/vectorchord-hybrid-search) |
| 在 PostgreSQL 中使用 ColBERT 重排序为向量检索加速 | 本文演示如何结合使用 PostgreSQL 扩展 [VectorChord](https://github.com/pgsty/vchord)、pgvector 以及 ColBERT 重排序技术。 | [ColBERT 重排序](/zh/docs/vchord/use-case/colbert-rerank/) | [GitHub 仓库](https://github.com/kemingy/vectorchord-colbert) |
| 超越纯文本：使用 Modal 与 VectorChord 在 PostgreSQL 中实现免 OCR RAG | 本文将指导您直接在熟悉的 PostgreSQL 数据库中构建一套**免 OCR 的 RAG 系统**。我们将结合 **ColQwen2** 视觉语言模型的强大能力、**VectorChord** 在 Postgres 中的高效多向量检索能力，以及 **Modal** 的可扩展 GPU 嵌入生成服务。 | [免 OCR RAG](/zh/docs/vchord/use-case/colqwen2-modal/) | [GitHub 仓库](https://github.com/xieydd/vectorchord-colqwen2) |
{.wide .expand}
