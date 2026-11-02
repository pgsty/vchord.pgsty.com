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
创建 bm25 索引、调优段大小与 BM25 参数（k1、b）、监控并行构建进度并检查索引页。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/querying/" title="查询与相关性评分" icon="fa-solid fa-ranking-star" >}}
运行 Top-K Block-WeakAnd 查询、理解负值 BM25 得分并调优 bm25_limit。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/filtering/" title="过滤检索与预过滤" icon="fa-solid fa-filter" >}}
通过后过滤、预过滤和部分索引，将 WHERE 过滤条件与 BM25 排序无缝结合。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/hybrid-search/" title="混合检索 (BM25 + VectorChord)" icon="fa-solid fa-code-merge" >}}
通过倒数排序融合（RRF）和 ColBERT 重排序，融合稀疏 BM25 词法检索与 VectorChord 稠密向量检索。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/algorithms/" title="BM25 与 Block-WeakAnd 内部原理" icon="fa-solid fa-microchip" >}}
深入解析 Okapi BM25 公式、单字节 Fieldnorm 量化、差分位打包与 Block-Max WAND 算法。
{{< /card >}}
{{< /cards >}}
