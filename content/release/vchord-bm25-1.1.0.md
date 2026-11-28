---
title: "vchord_bm25 1.1.0: Correctness Fixes and WAND Hardening"
date: 2026-11-08
description: "vchord_bm25 1.1.0 fixes floating-point WAND bound rounding near tied scores, reduces absent-term bookkeeping, hardens recycling and tsvector validation, and preserves 1.0.0 SQL and format-4 compatibility."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-bm25-1.0.0.png"
tags:
  - "vchord_bm25"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0"
upstream_source: ""
upstream_link: ""
aliases: [/blog/release/vchord-bm25-1.1.0/]
---

{{< release-card >}}

**vchord_bm25 1.1.0** is a correctness, search-efficiency, and maintenance-hardening release for [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) across PostgreSQL 14–18. It fixes a rare floating-point rounding case in Block-WeakAnd (WAND) pruning that could omit a near-tied document from a complete scan, streamlines per-document scoring and prefiltering, hardens segment recycling and catalog validation, and preserves full SQL and format-4 index compatibility with `1.0.0`.

> [!NOTE] Extension & Release Links
> - **GitHub Release**: [`pgsty/vchord_bm25 1.1.0`](https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0) · [Source Repository](https://github.com/pgsty/vchord_bm25)
> - **Documentation**: [Version History](/docs/bm25/reference/migration/#releases) · [Installation](/docs/bm25/getting-started/installation/) · [Migration Guide](/docs/bm25/reference/migration/)
> - **Packages & SBOM**: [Download Matrix](/download/) · [PGEXT (`vchord_bm25`)](https://pgext.cloud/e/vchord_bm25) · [SBOM & Licenses](/docs/about/sbom/)

## Changes in 1.1.0 {#changes}

| Area | Change |
| :--- | :--- |
| WAND bound summation | WAND upper bounds sum term contributions in the exact query ordinal order used by document scoring, preventing floating-point rounding differences from pruning near-tied documents. |
| Absent-term & per-doc cost | Document scoring uses a dense ordinal bitmap sized to sealed cursors that appear in the index, avoids per-document heap allocations and hashing, orders score ties by internal index position, prefilters only candidates that can enter the current batch, and stops scanning the zero-score tail once the batch is full. |
| Prefilter & planner safety | `bm25.prefilter` skips quals containing `SubPlan`s (leaving them to the PostgreSQL executor), and `amcostestimate` trusts only the extension's own `to_bm25query` function. |
| Storage, cache & recycling | Page recycling is atomic and publishes swept free pages under the page lock; invalid or unready indexes are rejected with SQLSTATE `55000` before reading pages; `tsvector` word entries and item pointers validate bounds before slicing; scan statistics and recent queries stay resident in the `work_mem`-bounded cache; `ambuild` reports real tuple/page counts and parallel worker counts. |
| Platform coexistence | `mimalloc` is enabled only on Linux `x86_64`/`aarch64` so `vchord_bm25` and `vchord` can be loaded together in `shared_preload_libraries` on macOS. |
{.wide .expand}

## Correct WAND pruning near equal scores {#correct-wand-pruning}

WAND upper bounds now add term contributions in the same query order used by document scoring. Previously, summing terms in cursor order could round an upper bound a few ULPs below the actual document score, causing a document near the current batch threshold to be pruned during a full scan.

The fix covers the pivot bound, block bounds, tight bounds, prefilter path, growing-segment continuation, and paginated scans. Equal scores keep their deterministic internal index order. Regression tests cover near-tie queries with prefiltering enabled and disabled, `LIMIT`, pagination, deleted rows, growing-segment rows, and absent query terms.

## Lower absent-term and tail-scan overhead {#absent-term-bookkeeping}

Per-document scoring uses a dense ordinal bitmap sized only to the sealed cursors present in the index rather than allocating state proportional to absent query terms. In addition, candidate evaluation eliminates per-document allocations, skips prefilter predicate evaluation when a candidate's bound cannot enter the current top-K batch, and stops scanning zero-score rows as soon as the requested batch is satisfied.

High-frequency queries with many matching terms still evaluate more posting lists than short queries; measure representative workloads and tune the initial `"bm25.limit"` batch size when needed.

## Upgrade from 1.0.0 {#upgrade-from-100}

The SQL API and format-4 index layout are unchanged from `1.0.0`. Healthy `1.0.0` indexes do not require `REINDEX`. Install the `1.1.0` shared library and SQL files, restart PostgreSQL so the updated `vchord_bm25.so` is loaded, and run:

```sql
ALTER EXTENSION vchord_bm25 UPDATE TO '1.1.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
-- 1.1.0
```

The `1.0.0--1.1.0` upgrade script is intentionally empty because all changes reside in the shared library. Note that `REINDEX CONCURRENTLY` creates a new index OID, so cached prepared plans or stored `bm25query` values referencing an explicit OID should resolve the index by name (`'my_idx'::regclass`). Legacy `0.3.x` (`bm25vector`) installations remain incompatible and must follow the [BM25 Migration Guide](/docs/bm25/reference/migration/).

## Filtering and zero-score rows {#filtering-and-zero-score-rows}

`"bm25.limit"` and the index `limit` storage option set the initial WAND batch size rather than a hard result cap. SQL `LIMIT`, `OFFSET`, and executor `WHERE` filters request additional batches automatically. `WHERE doc @@ ...` predicates run in the PostgreSQL executor; add a standard `GIN` index when a query requires selective boolean full-text matching without BM25 ranking. Non-matching documents score `+0.0`, and `NULL` rows sort last in ascending order.
