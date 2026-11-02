---
title: "推出 PGVecto.rs Cloud：PostgreSQL 可扩展向量搜索现已上云"
date: 2024-08-02
description: "我们激动地宣布推出 PGVecto.rs Cloud——将可扩展向量搜索的强大能力带入你的 PostgreSQL 数据库，现已作为全托管云服务正式上线……"
author: "[Ce Gao](https://github.com/gaocegege) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vector-database"
upstream_link: "https://blog.vectorchord.ai/introducing-pgvectors-cloud-scalable-vector-search-in-postgresql-now-in-the-cloud"
upstream_copyright: "© 2024 Ce Gao (TensorChord Inc.)"
aliases:
  - "/blog/introducing-pgvectors-cloud-scalable-vector-search-in-postgresql-now-in-the-cloud/"
  - "/introducing-pgvectors-cloud-scalable-vector-search-in-postgresql-now-in-the-cloud/"
---

我们非常激动地宣布推出 [PGVecto.rs](/zh/docs/vectors/) Cloud——将可扩展向量搜索的强大能力带入你的 PostgreSQL 数据库，现已作为全托管云服务正式上线。

[PGVecto.rs](/zh/docs/vectors/) 是一款开创性的 Postgres 扩展，支持高性能向量搜索，赋能开发者在现有 Postgres 基础设施之上构建先进的相似度检索应用。借助 [PGVecto.rs](/zh/docs/vectors/) Cloud，你现在无需自行承担管理扩展的运维开销，即可直接释放这项变革性技术的全部潜力。

![](https://framerusercontent.com/images/HgBD4Sp9X3rig7dK1MYFxXSKh7I.png?scale-down-to=2048)

通过与现有 Postgres 基础设施无缝集成，[PGVecto.rs](/zh/docs/vectors/) Cloud 助你构建前沿应用，轻松实现：

1. **革新搜索体验**：借助可扩展、高性能的向量搜索能力，充分释放数据潜能，帮助用户找到最相关、最相似的结果。
    
2. **增强过滤能力**：支持应用任意过滤条件并与其他表进行关联（JOIN），同时兼顾高召回率与低延迟——这是相比其他专用向量数据库的独特优势。
    
3. **支持超长向量维度**：[PGVecto.rs](/zh/docs/vectors/) Cloud 支持高达 65,535 维的向量长度，能够从容应对最新机器学习模型不断增长的输出维度需求。
    
4. **优化二值向量搜索**：利用自适应检索（adaptive retrieval）技术，[PGVecto.rs](/zh/docs/vectors/) Cloud 在保持高精度的同时，可将内存占用大幅降低多达 30 倍。
    
5. **无缝结合全文与向量搜索**：将 Postgres 内置的全文检索功能与 [PGVecto.rs](/zh/docs/vectors/) Cloud 相结合，在单条查询中同时检索文本和向量数据，解锁前所未有的灵活性与表现力。
    
6. **畅享卓越性能**：速度比其他基于 Postgres 的解决方案快 4 倍，[PGVecto.rs](/zh/docs/vectors/) Cloud 提供闪电般的响应速度，确保你的应用始终保持极速体验。
    
7. **拥抱完整 SQL 支持**：[PGVecto.rs](/zh/docs/vectors/) Cloud 提供完整的 SQL 支持，可与你现有的工作流无缝集成，让你不受限制、无需额外配置地自由使用 JOIN、过滤及其他 SQL 特性。
    

<a id="Pricing"></a>
## 价格方案 {#pricing}

[PGVecto.rs](/zh/docs/vectors/) Cloud 提供灵活的定价方案，以满足不同企业和开发者的多样化需求。无论你是刚刚开启向量搜索之旅，还是在运行大规模生产系统，我们都有契合你需求的方案。欢迎访问我们的[价格页面了解更多详情](/zh/cloud/pricing/price-plan/)。

如果你需要企业级支持或咨询服务，请通过 [pgvecto-rs-sales@tensorchord.ai](mailto:pgvecto-rs-sales@tensorchord.ai) 与我们联系。我们的团队随时准备协助你挑选最合适的方案，并提供必要的指导，确保你在 [PGVecto.rs](/zh/docs/vectors/) Cloud 上取得成功。
