---
title: "参考手册与基准测试"
description: "vchord_bm25 与 pg_tokenizer 的完整 SQL 参考手册、GUC 参数、性能基准测试与版本演进历史。"
weight: 40
icon: fa-solid fa-book
no_list: true
---

**`vchord_bm25`** 与 **`pg_tokenizer`** 的完整技术参考资料：

{{< cards >}}
  {{< card link="/zh/docs/bm25/reference/sql/" title="SQL 参考手册（类型、操作符与函数）" icon="fa-solid fa-code" >}}
涵盖 `bm25vector`、`bm25query`、`tsvector`、`<&>`、`to_bm25query`、`bm25_page_inspect` 以及 `pg_tokenizer` SQL 函数的完整参考。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/gucs/" title="GUC 与索引参数" icon="fa-solid fa-sliders" >}}
完整列出 `v0.1`–`v0.3`（`bm25_catalog.*`）与当前 `1.1.0`（`bm25.*`）的会话级 GUC 运行时参数、优先级覆盖规则及索引存储选项。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/benchmarks/" title="基准测试 (BEIR / MS MARCO)" icon="fa-solid fa-chart-bar" >}}
展示 `vchord_bm25` 与 Elasticsearch、Lucene、ParadeDB 及 PostgreSQL 原生 GIN 索引的 QPS 吞吐量与 NDCG@10 检索精度对比。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/versions/" title="版本历史与 API 演进" icon="fa-solid fa-clock-rotate-left" >}}
梳理从 `v0.1.0` 到 `v0.3.0`，再到 `1.0.0` 原生 `tsvector` 架构与当前 `1.1.0` 的版本变更日志、SQL 模式演进和兼容性边界。
{{< /card >}}
{{< /cards >}}
