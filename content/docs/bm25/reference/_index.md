---
title: "Reference & Benchmarks"
description: "Complete SQL reference, GUC parameters, benchmarks, and version history for vchord_bm25 and pg_tokenizer."
weight: 40
icon: fa-solid fa-book
no_list: true
---

Complete technical reference for **`vchord_bm25`** and **`pg_tokenizer`**:

{{< cards >}}
  {{< card link="/docs/bm25/reference/sql/" title="SQL Reference (Types, Operators, Functions)" icon="fa-solid fa-code" >}}
Complete reference for `bm25vector`, `bm25query`, `tsvector`, `<&>`, `to_bm25query`, `bm25_page_inspect`, and `pg_tokenizer` SQL functions.
{{< /card >}}
  {{< card link="/docs/bm25/reference/gucs/" title="GUC & Index Parameters" icon="fa-solid fa-sliders" >}}
Detailed guide to session GUCs, precedence rules, and index storage reloptions across `v0.1`–`v0.3` (`bm25_catalog.*`) and the current `1.1.0` API (`bm25.*`).
{{< /card >}}
  {{< card link="/docs/bm25/reference/benchmarks/" title="Benchmarks (BEIR / MS MARCO)" icon="fa-solid fa-chart-bar" >}}
Reproducible QPS throughput and NDCG@10 accuracy comparisons against Elasticsearch, Lucene, ParadeDB, and native PostgreSQL GIN indexes.
{{< /card >}}
  {{< card link="/docs/bm25/reference/versions/" title="Release History & API Evolution" icon="fa-solid fa-clock-rotate-left" >}}
Comprehensive changelog and SQL schema evolution from `v0.1.0` through `v0.3.0` to the native `tsvector` engine in `1.0.0` and the current `1.1.0` release.
{{< /card >}}
{{< /cards >}}
