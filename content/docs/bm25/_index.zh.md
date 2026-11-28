---
title: "vchord_bm25 文档"
linkTitle: "vchord_bm25"
description: "为 PostgreSQL 全文检索提供 BM25 相关性排序：一种索引，无需给每个匹配行打分，就能返回 tsvector 列中最相关的行。"
weight: 200
icon: fa-solid fa-magnifying-glass
type: docs
sidebar_root_for: self
aliases:
  - "/bm25/"
no_list: true
cascade:
  type: docs
  upstream_source: "bm25"
  upstream_link: "https://github.com/supervc-stack/VectorChord-bm25"
  upstream_modified: true
---

`vchord_bm25` 是一个 PostgreSQL 扩展，通过 `tsvector` 列上的索引按 BM25 相关性给行排序。它用整张表的统计信息打分，`ORDER BY ... LIMIT k` 只需取回前几名，不必给每一个匹配行都算一遍分；这正是 GIN 索引加 `ts_rank` 做不到的。适合在 PostgreSQL 里做关键词检索和 RAG 召回，可以单独用，也可以和 [vchord](/zh/docs/vchord/) 的向量检索搭配。

{{< cards >}}
  {{< card link="/zh/docs/bm25/getting-started/overview/" title="概览与快速上手" icon="fa-solid fa-compass" >}}
为什么 PostgreSQL 里的 BM25 需要专门的索引、一次排序查询怎样执行，以及五步跑通第一条查询。
{{< /card >}}
  {{< card link="/zh/docs/bm25/getting-started/installation/" title="安装" icon="fa-solid fa-download" >}}
从 Pigsty 软件源、GitHub Release 软件包或源码安装，然后预加载并创建扩展。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/indexing/" title="建索引" icon="fa-solid fa-database" >}}
为任意语言生成 `tsvector`，建索引，选择 `k1` 和 `b`，并在数据持续变化时保持索引高效。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/querying/" title="查询" icon="fa-solid fa-ranking-star" >}}
编写排序查询、理解分数、确定扫描批次大小，并让规划器用上索引。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/filtering/" title="过滤" icon="fa-solid fa-filter" >}}
把排序和 `WHERE` 条件结合起来：预过滤、部分索引与行级安全。
{{< /card >}}
  {{< card link="/zh/docs/bm25/usage/hybrid-search/" title="混合检索" icon="fa-solid fa-code-merge" >}}
在一条 SQL 里用倒数排名融合（RRF）合并 BM25 与 vchord 向量检索的结果。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/" title="参考" icon="fa-solid fa-book" >}}
SQL 对象、参数与索引选项、升级、旧版 `bm25vector` 接口与基准测试。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/" title="pg_tokenizer" icon="fa-solid fa-language" >}}
为中文、日文、韩文、自定义分析器和模型词表生成 `tsvector`。
{{< /card >}}
{{< /cards >}}
