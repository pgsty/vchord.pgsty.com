---
title: "Vchord Documentation"
linkTitle: "Documentation"
description: "Unified documentation hub for the PostgreSQL vector search, BM25 ranking, and tokenization extension suite: vchord, vchord_bm25, pg_tokenizer, pgvector, pgvecto.rs, and pg_bestmatch."
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://docs.vectorchord.ai/
upstream_modified: true
aliases:
  - "/cloud/"
  - "/cloud/pricing/price-plan/"
  - "/cloud/manage/apikey/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

## Extension Suite

{{< cards >}}
{{< card title="vchord" icon="fa-solid fa-layer-group" link="/docs/vchord/" >}}
Core disk-friendly PostgreSQL vector search extension powered by RaBitQ quantization, featuring `vchordrq` IVF indexes, `vchordg` graph indexes, and MaxSim (`@#`).
{{< /card >}}
{{< card title="vchord_bm25" icon="fa-solid fa-magnifying-glass" link="/docs/bm25/" >}}
Core native Okapi BM25 full-text ranking extension for PostgreSQL using Block-WeakAnd Top-K index pruning, designed to pair with `vchord` for hybrid search.
{{< /card >}}
{{< card title="pg_tokenizer" icon="fa-solid fa-language" link="/docs/tokenizer/" >}}
Core in-database multilingual text analyzer and tokenization pipeline supporting Jieba, Lindera, Snowball stemmers, LLM vocabularies, and custom corpus models.
{{< /card >}}
{{< card title="pgvecto.rs" icon="fa-solid fa-cube" badge="Deprecated" link="/docs/vectors/" >}}
Predecessor reference manual: complete historical documentation (`v0.1`–`v0.4`), configuration reference, and step-by-step migration guide to [`vchord`](/docs/vchord/admin/migration/).
{{< /card >}}
{{< card title="pg_bestmatch" icon="fa-solid fa-ranking-star" badge="Deprecated" link="/docs/bestmatch/" >}}
Predecessor reference manual: early in-database BM25 sparse-vector extension (`pg_bestmatch.rs`), now succeeded by [`vchord_bm25`](/docs/bm25/) and [`pg_tokenizer`](/docs/tokenizer/) in SQL.
{{< /card >}}
{{< card title="pgvector" icon="fa-solid fa-circle-nodes" badge="Upstream" link="/docs/vector/" >}}
Required upstream foundational extension providing standard `vector`, `halfvec`, `bit`, and `sparsevec` types, distance operators, and HNSW / IVFFlat indexes.
{{< /card >}}
{{< /cards >}}

## vchord Core Guide

{{< cards >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" link="/docs/vchord/getting-started/" >}}
Architecture overview, quickstart SQL walkthrough, installation via Pigsty packages, Docker (Obsolete), or source, and step-by-step migration from [`pgvecto.rs`](/docs/vectors/).
{{< /card >}}
{{< card title="Usage & Indexing" icon="fa-solid fa-code" link="/docs/vchord/usage/" >}}
Build `vchordrq` and `vchordg` indexes, run KNN and sphere range queries, apply `WHERE` prefilters, prewarm indexes, and run external centroid builds.
{{< /card >}}
{{< card title="Multi-Vector & Hybrid Search" icon="fa-solid fa-diagram-project" link="/docs/vchord/use-case/" >}}
ColBERT late-interaction MaxSim (`@#`) over `vector[]` arrays and hybrid semantic + BM25 search with [`vchord_bm25`](/docs/bm25/) and [`pg_tokenizer`](/docs/tokenizer/).
{{< /card >}}
{{< card title="Benchmarks & TCO" icon="fa-solid fa-chart-line" link="/docs/vchord/benchmark/" >}}
Reproducible recall, QPS throughput, index build speed, memory footprint, and cloud cost comparisons across GIST-1M, Cohere-10M, and LAION-100M.
{{< /card >}}
{{< card title="Administration & Tuning" icon="fa-solid fa-sliders" link="/docs/vchord/admin/" >}}
Production GUC parameter tuning, shared memory sizing, I/O concurrency settings, index maintenance, routine vacuuming, and version upgrades.
{{< /card >}}
{{< card title="Customer Stories" icon="fa-solid fa-earth-americas" link="/docs/vchord/customer-stories/" >}}
Discover how the University of Oxford and Earth Genome store and query 3 billion satellite embedding vectors on a single PostgreSQL node with `vchord`.
{{< /card >}}
{{< /cards >}}

## Ecosystem & Project Info

{{< cards >}}
{{< card title="About Vchord Suite" icon="fa-solid fa-circle-info" link="/docs/about/" >}}
Explore the overall Vchord suite architecture, functional comparison across all six extensions, and PGSTY community stewardship and maintenance policy.
{{< /card >}}
{{< card title="Open-Source Attribution" icon="fa-solid fa-scale-balanced" link="/docs/about/attribution/" >}}
Complete upstream source provenance, original TensorChord author credits, open-source license notices, and repository mapping across the suite.
{{< /card >}}
{{< card title="AGPLv3 License" icon="fa-solid fa-code-branch" link="/docs/about/license/" >}}
Full GNU AGPLv3 open-source license terms, PostgreSQL 14–18 Linux package matrix, extension upgrade script policy, and security vulnerability reporting.
{{< /card >}}
{{< /cards >}}
