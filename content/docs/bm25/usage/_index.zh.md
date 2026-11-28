---
title: "使用指南"
description: "创建并维护 bm25 索引，编写和调优排序查询，与过滤条件结合，以及与向量检索融合。"
weight: 20
icon: fa-solid fa-code
no_list: true
---

这几页沿着一张表从文本到结果的过程展开：生成 `tsvector` 并建索引，执行排序查询并确定批次大小，加上 `WHERE` 条件，最后合并关键词与向量检索的排名。

{{< cards >}}
  {{< card link="/zh/docs/bm25/usage/indexing/" title="建索引" icon="fa-solid fa-database" >}}
生成 `tsvector`、建索引、选择 `k1` 和 `b`、在持续写入下保持高效，以及安全地重建。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/querying/" title="查询" icon="fa-solid fa-ranking-star" >}}
排序查询如何执行、分数的含义、如何确定 `bm25.limit`，以及如何让索引留在执行计划里。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/filtering/" title="过滤" icon="fa-solid fa-filter" >}}
`WHERE` 与排序、针对高选择性条件的预过滤、部分索引、权限与行级安全。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/hybrid-search/" title="混合检索" icon="fa-solid fa-code-merge" >}}
一份可运行的示例，用倒数排名融合合并 BM25 与 vchord 向量检索的排名。
{{< /card >}}
{{< /cards >}}
