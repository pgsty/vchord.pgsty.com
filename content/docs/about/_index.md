---
title: About Vchord & vchord.pgsty.com
linkTitle: About
description: Project overview, licensing, upstream attribution, and trademark policy for the Pigsty-maintained Vchord distribution and documentation site.
type: docs
weight: 5
icon: fa-solid fa-circle-info
upstream_source: ""
upstream_link: ""
upstream_modified: false
aliases:
  - "/about/"
cascade:
  type: docs
  upstream_source: ""
  upstream_link: ""
  upstream_modified: false
---

**Vchord (`vchord`)** is a PostgreSQL extension designed for scalable, high-performance, and disk-friendly vector similarity search, developed as the architectural successor to [`pgvecto.rs`](/docs/vectors/).

This repository (`pgsty/vchord.pgsty.com`) and website (`https://vchord.pgsty.com/`) provide a complete, fast, local-first documentation and technical blog reference for [`pgsty/vchord`](https://github.com/pgsty/vchord), [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25), and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer), maintained by the [Pigsty](https://pigsty.io/) community using the [OINK 1.5.0](https://oink.pgsty.com/) documentation framework.

> [!NOTE]
> **`pgsty/vchord`, `pgsty/vchord_bm25`, and `pgsty/pg_tokenizer` are community-maintained forks of `tensorchord/VectorChord`, `supervc-stack/VectorChord-bm25`, and `supervc-stack/pg_tokenizer.rs`.** They are not affiliated with, endorsed by, or sponsored by TensorChord Inc. See [Attribution](/docs/about/attribution/) and [Trademark Policy](/docs/about/trademark/) for details.

## Documentation Scope

| Section | Coverage |
| :--- | :--- |
| **[`vchord` Docs](/docs/vchord/)** | Installation, migration from `pgvecto.rs`, `vchordrq` and `vchordg` indexing, MaxSim multi-vector retrieval, range queries, PostgreSQL tuning, external index precomputation, benchmarks, and SQL reference. |
| **[`vchord_bm25` Docs](/docs/bm25/)** | Complete documentation for [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25): Okapi BM25 scoring, Block-WeakAnd Top-K index scans, prefiltering, hybrid search with `vchord`, and SQL/GUC/BEIR benchmark reference. |
| **[`pgvector` Docs](/docs/vector/)** | Complete documentation for `pgvector`: `vector`, `halfvec`, `bit`, and `sparsevec` types, distance operators, HNSW and IVFFlat indexing, iterative index scans, and quantization. |
| **[`pgvecto.rs` Archive](/docs/vectors/)** | Complete legacy documentation for `pgvecto.rs` (`vectors` extension), including installation, indexing, filtering, framework integrations, and administration. |
| **[`pg_tokenizer` Docs](/docs/tokenizer/)** | Complete documentation for [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer): text analyzer pipelines, character/token filters, Snowball stemmers, custom corpus models, HuggingFace models, Chinese `jieba`, and Japanese `lindera`. |
| **[`pg_bestmatch` Docs](/docs/bestmatch/)** | Documentation for `pg_bestmatch.rs`: generating Okapi BM25 sparse vectors inside PostgreSQL for [`pgvector`](/docs/vector/) `sparsevec` and [`pgvecto.rs`](/docs/vectors/) `svector`. |
| **[Engineering Blog](/blog/)** | All 37 engineering deep-dives, benchmark analyses, hybrid search tutorials, and release announcements (`pgvecto.rs 0.2` through `VectorChord 1.1`). |
| **[VectorChord Cloud](/cloud/)** | Reference documentation for VectorChord Cloud clusters, connection endpoints, scaling, VPC peering, monitoring, and billing. |
{.wide .expand}
