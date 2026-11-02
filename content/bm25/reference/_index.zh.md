---
title: "参考手册与基准测试"
description: "vchord_bm25 与 pg_tokenizer 的完整 SQL 参考手册、GUC 参数、性能基准测试与版本演进历史。"
weight: 40
icon: fa-solid fa-book
---

**`vchord_bm25`** 与 **`pg_tokenizer`** 的完整技术参考资料：

{{< cards >}}
  {{< card link="/zh/bm25/reference/sql/" title="SQL 参考手册（类型、操作符与函数）" icon="fa-solid fa-code" >}}
涵盖 bm25vector、bm25query、tsvector、<&>、to_bm25query、bm25_page_inspect 以及全部 19 个 pg_tokenizer 函数的完整参考。
{{< /card >}}
  {{< card link="/zh/bm25/reference/gucs/" title="GUC 与索引参数" icon="fa-solid fa-sliders" >}}
v0.1–v0.3 (bm25_catalog.*) 与 main 分支 (bm25.*) 的会话 GUC 参数及索引存储选项。
{{< /card >}}
  {{< card link="/zh/bm25/reference/benchmarks/" title="基准测试 (BEIR / MS MARCO)" icon="fa-solid fa-chart-bar" >}}
与 Elasticsearch、Lucene、ParadeDB 及 PostgreSQL GIN 的 QPS 吞吐量与 NDCG@10 检索精度对比。
{{< /card >}}
  {{< card link="/zh/bm25/reference/versions/" title="版本历史与 API 演进" icon="fa-solid fa-clock-rotate-left" >}}
从 v0.1.0 到 v0.3.0 再到新一代原生 tsvector 架构的变更日志与模式演进。
{{< /card >}}
{{< /cards >}}
