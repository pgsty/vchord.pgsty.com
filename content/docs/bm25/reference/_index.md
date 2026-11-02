---
title: "Reference & Benchmarks"
description: "Complete SQL reference, GUC parameters, benchmarks, and version history for vchord_bm25 and pg_tokenizer."
weight: 40
icon: fa-solid fa-book
---

Complete technical reference for **`vchord_bm25`** and **`pg_tokenizer`**:

{{< cards >}}
  {{< card link="/docs/bm25/reference/sql/" title="SQL Reference (Types, Operators, Functions)" icon="fa-solid fa-code" >}}
Complete reference for bm25vector, bm25query, tsvector, <&>, to_bm25query, bm25_page_inspect, and all 19 pg_tokenizer functions.
{{< /card >}}
  {{< card link="/docs/bm25/reference/gucs/" title="GUC & Index Parameters" icon="fa-solid fa-sliders" >}}
Session GUCs and index storage parameters across v0.1–v0.3 (bm25_catalog.*) and main (bm25.*).
{{< /card >}}
  {{< card link="/docs/bm25/reference/benchmarks/" title="Benchmarks (BEIR / MS MARCO)" icon="fa-solid fa-chart-bar" >}}
QPS and NDCG@10 accuracy comparisons against Elasticsearch, Lucene, ParadeDB, and PostgreSQL GIN.
{{< /card >}}
  {{< card link="/docs/bm25/reference/versions/" title="Release History & API Evolution" icon="fa-solid fa-clock-rotate-left" >}}
Changelog and schema evolution from v0.1.0 through v0.3.0 to the next-generation native tsvector architecture.
{{< /card >}}
{{< /cards >}}
