---
title: "vchord_bm25 1.1.0: Correctness Fixes for WAND Search"
date: 2026-11-08
description: "vchord_bm25 1.1.0 fixes rare floating-point pruning that could omit near-tied documents, reduces absent-term bookkeeping, and keeps the 1.0.0 SQL API and index format."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-bm25-1.0.0.png"
tags:
  - "release"
  - "vchord_bm25"
  - "bm25"
  - "full-text-search"
upstream_source: ""
upstream_link: ""
---

**vchord_bm25 1.1.0** is a correctness and query-path release for the PGSTY-maintained [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) extension. It fixes a rare floating-point rounding case in Block-WeakAnd (WAND) pruning that could silently omit a near-tied document from a complete scan, while keeping the native PostgreSQL `tsvector` API and format 4 index storage introduced in 1.0.0.

> [!NOTE] Extension & Release Links
> - **GitHub Release**: [`pgsty/vchord_bm25 1.1.0`](https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0) · [Source Repository](https://github.com/pgsty/vchord_bm25)
> - **Documentation**: [Version history](/docs/bm25/reference/versions/) · [Installation](/docs/bm25/getting-started/installation/)
> - **PGXN**: [Distribution page](https://pgxn.org/dist/vchord_bm25/)

## Correct WAND pruning near equal scores {#correct-wand-pruning}

WAND upper bounds now add term contributions in the same query order used by document scoring. Before this fix, a different cursor order could round a bound slightly below the corresponding score. A document whose score was within a few floating-point units of the current batch threshold could then be pruned and disappear from a complete scan.

The fix covers the pivot bound, block bounds, tight bounds, prefilter path, growing-segment continuation, and paginated scans. Equal scores keep the stable internal index order. The regression suite exercises the near-tie case with prefiltering enabled and disabled, `LIMIT`, pagination, deletes, growing records, and absent query terms.

## Less bookkeeping for absent terms {#absent-term-bookkeeping}

The per-document sum uses a dense ordinal bitmap sized to the sealed cursors that actually contribute to the query. A query with many terms that are absent from the index no longer creates bitmap state proportional to every missing term, while the scoring order remains unchanged. Boundary coverage includes empty sets and bitmap sizes around 64 and 128 entries, together with a 129-term absent-word SQL regression.

This optimization keeps long-query cost workload-dependent. High-frequency queries with many terms can still spend more CPU in bound calculation than short queries; measure representative workloads and tune the initial `bm25.limit` when needed.

## Upgrade from 1.0.0 {#upgrade-from-100}

The SQL API and format 4 index storage are unchanged. A healthy 1.0.0 index does not need `REINDEX`; install the 1.1.0 library and SQL files, restart PostgreSQL when changing `shared_preload_libraries`, and run:

```sql
ALTER EXTENSION vchord_bm25 UPDATE TO '1.1.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
-- 1.1.0
```

The `1.0.0--1.1.0` upgrade script is intentionally empty because the fix is in the library code. The 0.3.x `bm25vector` API and index format remain incompatible with 1.1.0; use the [migration guide](/docs/bm25/reference/migration/) for that boundary.

## Filtering and zero-score rows {#filtering-and-zero-score-rows}

`bm25.limit` and the index `limit` option control the initial WAND batch size, not a hard result cap. SQL `LIMIT`, `OFFSET`, and executor-side `WHERE` filters can request more candidates, so scans continue as needed. `WHERE vector @@ ...` remains an executor filter; a GIN index can provide a better path for highly selective or empty full-text matches. Nonmatching documents have zero scores and `NULL` rows sort last in ascending score order.

The release was validated with the PG18.6 acceptance harness, SQLLogicTest coverage, Rust tests, Clippy, and a generated PGXN source archive. The GitHub workflow continues to build the supported PostgreSQL 14–18 Linux and macOS package matrix.
