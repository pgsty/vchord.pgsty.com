---
title: "vchord_bm25 1.2.0: PostgreSQL 19, Planner Safety, and Parallel Build Hardening"
date: 2026-11-23
description: "vchord_bm25 1.2.0 adds PostgreSQL 15–19 support via pgrx 0.20.1, fixes planner NaN costs and scan resource cleanup, preserves old-snapshot visibility on parallel builds, and updates url to 2.5.9."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.2.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord_bm25"
aliases: [/blog/release/vchord-bm25-1.2.0/]
---

**vchord_bm25 1.2.0** brings [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) onto `pgrx 0.20.1` and Rust `1.100.0+` for PostgreSQL 15–19 on `x86_64` and `aarch64`, hardens planner cost estimation and scan error cleanup, preserves old-snapshot visibility on parallel index builds, and keeps full SQL and format-4 index compatibility with `1.0.0` and `1.1.0`. PostgreSQL 14 is no longer supported.

> [!NOTE] Superseded Draft Milestone
> The `1.2.0` tag (`https://github.com/pgsty/vchord_bm25/tree/1.2.0`) remained a draft GitHub Release and was superseded by the published [**vchord_bm25 1.3.0**](/release/vchord-bm25-1.3.0/) release, which adds batched build WAL, `shared_corpus_stats` for RLS tables, correlated-subquery prefiltering, and improved Top-K plan selection. Install [`vchord_bm25 1.3.0`](/release/vchord-bm25-1.3.0/) for production deployments and pre-built GitHub packages.

## Changes in 1.2.0 {#changes}

| Area | Change |
| :--- | :--- |
| PostgreSQL 15–19 & `pgrx 0.20.1` | Support PostgreSQL 15–19 on Linux `x86_64` and `aarch64` with `pgrx 0.20.1` and Rust `1.100.0+`. Drop PostgreSQL 14. Declare `amcanbuildparallel` on PostgreSQL 17+, and pass `SO_HINT_REL_READ_ONLY` and a static `IndexAmRoutine` on PostgreSQL 19. |
| Planner & scan safety | Replace `f64::INFINITY` with finite unusable-path costs in `amcostestimate` (preventing `NaN` costs in PostgreSQL `cost_index()`) and exclude unsupported `Index Only Scan` paths. Check query interrupts at `amgettuple` entry and reject invalid or partitioned indexes in `bm25_maintain`. |
| Memory, cleanup & stats | Fix prefilter heap-slot cleanup during error unwinding, remove dead per-batch `IndexInfo` / `ExecutorState` allocations, and restore `CurrentMemoryContext` on expression evaluation errors. Allocate scan descriptors in `es_query_cxt` and track `pg_stat_user_indexes.idx_scan` on PostgreSQL 15–19 alongside `Index Searches` (`nsearches`) on PostgreSQL 18+. |
| Parallel build visibility | Propagate broken HOT chains observed by any parallel build worker so PostgreSQL defers use of the newly built index by transactions with older snapshots. |
| Dependencies & compatibility | Update locked `url` to `2.5.9` addressing [`RUSTSEC-2026-0592`](https://rustsec.org/advisories/RUSTSEC-2026-0592.html). Preserve all `1.0.0` / `1.1.0` SQL APIs and format-4 indexes in place. |
{.wide .expand}

## Upgrade notes {#upgrade-notes}

1. **PostgreSQL 14 servers**: Upgrade PostgreSQL to 15–19 before installing `1.2.0` or later.
1. **In-place 1.x upgrade**: Install the matching library and SQL files, restart PostgreSQL, and run:

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

Existing `1.0.0` and `1.1.0` format-4 indexes keep working without `REINDEX`. Historical `0.3.x` (`bm25vector`) installations remain incompatible and must follow [Migrate from 0.x](/docs/bm25/reference/migration/#from-0x).
