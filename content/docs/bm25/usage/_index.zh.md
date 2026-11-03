---
title: "使用指南与混合检索"
description: "索引管理、Top-K 查询、预过滤、与 vchord 的混合检索以及 Block-WeakAnd 内部原理。"
weight: 20
icon: fa-solid fa-code
no_list: true
---

了解如何在生产环境中构建、调优和查询 `vchord_bm25` 索引：

{{< cards >}}
  {{< card link="/zh/docs/bm25/usage/indexing/" title="索引构建与维护" icon="fa-solid fa-database" >}}
创建并维护 `bm25` 倒排索引、调优段大小与 BM25 超参数（`k1`、`b`）、监控并行索引构建进度并检查底层索引存储页面。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/querying/" title="查询与相关性评分" icon="fa-solid fa-ranking-star" >}}
使用 `<&>` 操作符运行 Top-K Block-WeakAnd 检索查询、理解负值 BM25 相关性得分设计，并合理配置候选集上限参数。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/filtering/" title="过滤检索与预过滤" icon="fa-solid fa-filter" >}}
对比后过滤、预过滤与部分索引策略，将业务 `WHERE` 谓词过滤条件与 BM25 全文相关性排序在生产环境中无缝结合。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/hybrid-search/" title="混合检索 (BM25 + VectorChord)" icon="fa-solid fa-code-merge" >}}
在单条 SQL 查询中通过倒数排序融合（RRF）或 ColBERT 多向量重排序，融合稀疏 BM25 词法检索与 `vchord` 稠密向量检索。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/algorithms/" title="BM25 与 Block-WeakAnd 内部原理" icon="fa-solid fa-microchip" >}}
深入解析 Okapi BM25 评分公式、单字节文档长度（Fieldnorm）量化、差分位打包编码与 Block-Max WAND 剪枝算法实现。
{{< /card >}}
{{< /cards >}}
