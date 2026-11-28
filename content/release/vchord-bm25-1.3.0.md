---
title: "vchord_bm25 1.3.0: Lower Build WAL, RLS Corpus Sharing, and Subquery Prefiltering"
date: 2026-11-24
description: "vchord_bm25 1.3.0 batches posting WAL during builds and rebuilds, adds opt-in shared_corpus_stats for RLS tables, prefilters repeatable correlated subqueries, and improves selective Top-K plan choice on PostgreSQL 15–19."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord_bm25"
aliases: [/blog/release/vchord-bm25-1.3.0/]
---

{{< release-card >}}

**vchord_bm25 1.3.0** is the published PostgreSQL 15–19 release of [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) on `x86_64` and `aarch64`, building on [1.2.0](/release/vchord-bm25-1.2.0/). It batches posting checkpoints to cut build and maintenance WAL, shares parallel sort memory across workers, refines Top-K cost estimation and growing-segment scans, adds opt-in `shared_corpus_stats` for tables under Row-Level Security (RLS), and prefilters repeatable correlated subqueries.

Pre-built Linux `.deb` and `.zip` packages for PostgreSQL 15–19 (`x86_64` and `aarch64`, built on Ubuntu 22.04, requiring `libc6 >= 2.35`), a PGXN-formatted source ZIP, and `.sha256` checksum files are published on the [GitHub Release](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0).

## Changes in 1.3.0 {#changes}

| Area | Change |
| :--- | :--- |
| Build & rebuild WAL | Batch posting checkpoints across terms during index builds and segment rebuilds instead of flushing per term, reducing Generic WAL records and total WAL bytes while keeping identical index page counts. Parallel build participants report progress every 1,024 rows and at scan completion. |
| Parallel sort budget | Share the mapping sort budget across the leader and launched workers during `CREATE INDEX`, capping each participant at the smaller of its `maintenance_work_mem` share and 64 MiB. PostgreSQL 17–19 supply the worker count directly. |
| Growing stats & pagination | Keep exact combined corpus statistics across sealed and growing segments. Scalar `<&>` scoring reuses validated index metadata and locks within an execution. Ranked scans retain only positive growing candidates and stream zero-score and `NULL` rows as pagination reaches them, skipping exhausted positive growing candidates on later batches. |
| Top-K cost estimation | Price first-batch preparation separately from repeated posting scans in `amcostestimate`, letting PostgreSQL choose ordered BM25 index scans for selective Top-K queries instead of falling back to `Bitmap Scan + Sort`. |
| RLS & corpus privileges | Add index-owner storage option `shared_corpus_stats` (default `off`) to allow scoring against whole-index corpus statistics on RLS-protected tables while PostgreSQL still enforces row policies before returning rows. Unify corpus privilege checks across scalar, index, and view paths; allow column grants to cover simple index expressions and partial predicates. |
| Subquery prefiltering | `bm25.prefilter` can evaluate repeatable correlated subqueries over plain heap or B-tree scans, including scalar `count(*)`. Volatile subqueries, unknown plan nodes, and security-sensitive filters stay in the PostgreSQL executor. |
| Maintenance & recycling | Delay maintenance scratch-file creation until a segment rebuild is actually needed, so no-op `VACUUM` creates zero temporary files. Unlink up to three retired pages from their chain in a single atomic Generic WAL record and publish Free Space Map hints after the record completes. |
| Source packaging | Attach a PGXN-compatible source ZIP and `.sha256` checksum to the GitHub Release independently of PGXN upload credentials. |
{.wide .expand}

## Build WAL, maintenance, and query performance {#performance}

In the [1.3.0 performance report](https://github.com/pgsty/vchord_bm25/blob/1.3.0/docs/performance/2026-11-24-bm25.zh-CN.md) comparing `1.3.0` against `1.2.0` on a 20,000-row mixed Chinese/English technical corpus (256 MiB `shared_buffers`, warm cache) across macOS `arm64` (PostgreSQL 18.7) and Ubuntu `x86_64` (PostgreSQL 18.6, tmpfs):

| Workload | macOS `arm64` (`1.2.0` → `1.3.0`) | Ubuntu `x86_64` (`1.2.0` → `1.3.0`) |
| :--- | :--- | :--- |
| Serial `CREATE INDEX` Generic WAL records | 205,319 → 3,860 | 205,320 → 3,861 |
| Serial `CREATE INDEX` total WAL | 25.99 MiB → 14.43 MiB (-44.5%) | 25.99 MiB → 14.43 MiB (-44.5%) |
| Serial `CREATE INDEX` elapsed time | 726.1 ms → 425.8 ms | 747.6 ms → 509.4 ms |
| Segment rebuild (+2,000 rows) time | 598.0 ms → 286.5 ms | 569.9 ms → 317.2 ms |
| Retired-page recycling Generic WAL records | 2,771 → 927 | 2,771 → 927 |
| Correlated `count(*)` prefilter (`off` → `on`) | 14.49 ms → 4.25 ms (166,279 → 30,220 buffer accesses) | 19.40 ms → 6.68 ms (166,271 → 30,219 buffer accesses) |
{.wide .expand}

Separating first-batch setup from expansion cost also switched selective filtered Top-10 queries (10% category filter) from `Bitmap + Sort` (8.40 ms macOS / 10.51 ms Ubuntu) to ordered BM25 scans (1.40 ms / 1.73 ms) when high-scoring rows appeared early. Because planner statistics cannot predict how filtered rows correlate with BM25 rank, workloads where matching rows sit deep in the ranking can still expand across multiple batches and run slower than a bitmap scan; verify with `EXPLAIN ANALYZE`.

## Opt-in `shared_corpus_stats` under RLS {#shared-corpus-stats}

By default (`shared_corpus_stats = off`), `vchord_bm25` rejects BM25 scoring when RLS policies apply to the caller so global term document frequencies cannot leak information about hidden rows. When an index owner explicitly opts in:

```sql
ALTER INDEX documents_terms_bm25 SET (shared_corpus_stats = on);
```

roles that already hold corpus read privileges can score against whole-index statistics, while PostgreSQL continues applying row-level policies before returning any rows. Only enable this when revealing global term frequency across tenants is acceptable for your threat model ([Settings and Index Options](/docs/bm25/reference/gucs/#index-options)).

## Upgrade and downgrade notes {#upgrade-notes}

1. **PostgreSQL version**: `1.3.0` supports PostgreSQL 15–19 on `x86_64` and `aarch64`. PostgreSQL 14 installations must upgrade the server first.
1. **In-place 1.x upgrade**: Install the `1.3.0` shared library and SQL files ([Installation](/docs/bm25/getting-started/installation/)), restart PostgreSQL, and run:

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

Versions `1.0.0`, `1.1.0`, and `1.2.0` keep their format-4 indexes during the upgrade with no `REINDEX`. Legacy `0.3.x` (`bm25vector`) installations require data export and index rebuilding ([Migrate from 0.x](/docs/bm25/reference/migration/#from-0x)).

> [!WARNING] Reverting below 1.3.0
> The SQL upgrade path is forward-only. Although `1.3.0` keeps the same SQL objects as `1.2.0`, earlier libraries do not recognize the `shared_corpus_stats` reloption. Before reverting the shared library, run `ALTER INDEX <index> RESET (shared_corpus_stats);` on every index where the option was explicitly set, including explicit `off` values. See [Downgrade](/docs/bm25/reference/migration/#downgrade) for the inspection query.
