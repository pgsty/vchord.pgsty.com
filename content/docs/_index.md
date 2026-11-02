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
Scalable, disk-friendly vector similarity search built on [`pgvector`](/docs/vector/) with `vchordrq` (RaBitQ IVF), `vchordg` (RaBitQ graph), multi-vector MaxSim (`@#`), and range search.
{{< /card >}}
{{< card title="vchord_bm25" icon="fa-solid fa-magnifying-glass" link="/docs/bm25/" >}}
Native Okapi BM25 ranking index (`bm25vector`, `<&>` operator, and Block-WeakAnd WAND Top-K execution) for fast full-text and hybrid retrieval in PostgreSQL.
{{< /card >}}
{{< card title="pg_tokenizer" icon="fa-solid fa-language" link="/docs/tokenizer/" >}}
Standalone multilingual text analyzer and token-ID pipeline supporting Unicode, Regex, Jieba, Lindera, HuggingFace, LLMLingua-2, Snowball, and custom models.
{{< /card >}}
{{< card title="pgvector" icon="fa-solid fa-circle-nodes" link="/docs/vector/" >}}
Foundational open-source vector similarity search for PostgreSQL (`vector`, `halfvec`, `bit`, `sparsevec`), exact and approximate KNN search, HNSW, and IVFFlat indexes.
{{< /card >}}
{{< card title="pgvecto.rs" icon="fa-solid fa-cube" link="/docs/vectors/" >}}
Complete historical documentation archive (`v0.1`–`v0.4`) and [`vchord`](/docs/vchord/admin/migration/) migration reference for `pgvecto.rs`, the predecessor to `vchord`.
{{< /card >}}
{{< card title="pg_bestmatch" icon="fa-solid fa-ranking-star" link="/docs/bestmatch/" >}}
Lightweight BM25 sparse vector generator (`pg_bestmatch.rs`) converting text into BM25-weighted [`pgvector`](/docs/vector/) `sparsevec` or [`pgvecto.rs`](/docs/vectors/) `svector` representations.
{{< /card >}}
{{< /cards >}}

## vchord Core Guide

{{< cards >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" link="/docs/vchord/getting-started/" >}}
Architecture overview, quickstart SQL walkthrough, installation via Pigsty, Docker, or prebuilt packages, and migration from [`pgvecto.rs`](/docs/vectors/).
{{< /card >}}
{{< card title="Usage & Indexing" icon="fa-solid fa-code" link="/docs/vchord/usage/" >}}
Build `vchordrq` and `vchordg` indexes, run KNN and sphere range queries, apply `WHERE` filters, prewarm indexes, and run external centroid builds.
{{< /card >}}
{{< card title="Multi-Vector & Hybrid Search" icon="fa-solid fa-diagram-project" link="/docs/vchord/use-case/" >}}
ColBERT late-interaction MaxSim (`@#`) over `vector[]` arrays and hybrid semantic + BM25 search with [`vchord_bm25`](/docs/bm25/) and [`pg_tokenizer`](/docs/tokenizer/).
{{< /card >}}
{{< card title="Benchmarks & TCO" icon="fa-solid fa-chart-line" link="/docs/vchord/benchmark/" >}}
Reproducible recall, QPS, build speed, memory footprint, and cloud cost comparisons across GIST-1M, Cohere-10M, and LAION-100M.
{{< /card >}}
{{< card title="Administration & Tuning" icon="fa-solid fa-sliders" link="/docs/vchord/admin/" >}}
Production GUC tuning, shared memory sizing, I/O concurrency, index maintenance, vacuuming, and version upgrades.
{{< /card >}}
{{< card title="Customer Stories" icon="fa-solid fa-earth-americas" link="/docs/vchord/customer-stories/" >}}
How the University of Oxford stores and queries 3 billion satellite embedding vectors in PostgreSQL with `vchord`.
{{< /card >}}
{{< /cards >}}

## Ecosystem & Project Info

{{< cards >}}
{{< card title="About Vchord Suite" icon="fa-solid fa-circle-info" link="/docs/about/" >}}
Ecosystem architecture, extension compatibility matrix, and PGSTY community stewardship.
{{< /card >}}
{{< card title="Open-Source Attribution" icon="fa-solid fa-scale-balanced" link="/docs/about/attribution/" >}}
Upstream provenance, copyright notices, license terms, and repository mapping.
{{< /card >}}
{{< card title="AGPLv3 License" icon="fa-solid fa-code-branch" link="/docs/about/license/" >}}
PostgreSQL 14–18 packaging matrix, upgrade scripts, and security reporting.
{{< /card >}}
{{< /cards >}}
