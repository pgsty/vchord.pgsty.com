---
title: About Vchord & vchord.pgsty.com
linkTitle: About
description: Project overview, licensing, upstream attribution, and trademark policy for the PGSTY-maintained Vchord extension suite and documentation site.
type: docs
sidebar_root_for: self
weight: 50
icon: fa-solid fa-circle-info
cascade:
  type: docs
---

**Vchord** is a PostgreSQL extension suite for scalable vector similarity search and BM25 full-text search, consisting of **[`vchord`](https://github.com/pgsty/vchord)**, **[`vchord_bm25`](https://github.com/pgsty/vchord_bm25)**, and **[`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)**.

This repository (`pgsty/vchord.pgsty.com`) and website (`https://vchord.pgsty.com/`) provide a complete, fast, local-first documentation and technical blog reference for [`pgsty/vchord`](https://github.com/pgsty/vchord), [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25), and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer), maintained by [PGSTY](https://pigsty.io/) using the [OINK 1.4.0](https://oink.pgsty.com/) documentation framework.

> [!NOTE]
> **`pgsty/vchord`, `pgsty/vchord_bm25`, and `pgsty/pg_tokenizer` are PGSTY-maintained forks of `tensorchord/VectorChord`, `tensorchord/VectorChord-bm25`, and `tensorchord/pg_tokenizer.rs`.** See [Attribution](/about/attribution/) and [Trademark Policy](/about/trademark/) for details.

## Documentation Scope

| Section | Coverage |
| :--- | :--- |
| **[`vchord` Docs](/docs/)** | Installation, migration from `pgvecto.rs`, `vchordrq` and `vchordg` indexing, MaxSim multi-vector retrieval, range queries, PostgreSQL tuning, external index precomputation, benchmarks, and SQL reference. |
| **[`vchord_bm25` & `pg_tokenizer`](/bm25/)** | Complete documentation for [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) (`vchord_bm25`) and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) (`pg_tokenizer`): Okapi BM25 scoring, Block-WeakAnd Top-K index scans, prefiltering, hybrid search with `vchord`, multilingual text analyzers (`jieba`, `lindera`, Snowball, HuggingFace), and SQL/GUC reference. |
| **[Engineering Blog](/blog/)** | All 37 engineering deep-dives, benchmark analyses, hybrid search tutorials, and release announcements. |
