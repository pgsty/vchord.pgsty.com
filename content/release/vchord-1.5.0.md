---
title: "vchord 1.5.0: Streaming Filtered Scans, Parallel Builds, and Graph Repair"
date: 2026-11-24
description: "vchord 1.5.0 streams initial probes on filter-key RQ scans, enables parallel builds on small TOAST-backed heaps, hardens graph VACUUM bridge repair and WAL publication, and supports PostgreSQL 15–19."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.5.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.5.0/]
---

{{< release-card >}}

**vchord 1.5.0** is the published PostgreSQL 15–19 release of [`pgsty/vchord`](https://github.com/pgsty/vchord) on `x86_64` and `aarch64`, building directly on the [1.4.0](/release/vchord-1.4.0/) filter-key architecture. It streams filtered RQ scans from the initial probes, fixes relation-cache invalidation on prepared enum range queries, brings parallel builds to small TOAST-backed tables, tightens sphere recheck rules, and improves `vchordg` and `vchordrq` maintenance.

Pre-built Linux ZIP archives and Debian packages for PostgreSQL 15–19 on `x86_64` and `aarch64` (built on Ubuntu 22.04, requiring `libc6 >= 2.35`, with `.sha256` checksums for every asset) are published on the [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.5.0).

## Changes in 1.5.0 {#changes}

| Area | Change |
| :--- | :--- |
| Streaming filtered RQ scans | Ordered `vchordrq` scans with filter keys stream candidates from their initial IVF probes and expand lazily up to `vchordrq.max_probes` only when more rows are requested. Distances can decrease between expansion rounds; overfetch and sort in SQL if strict order is required. |
| Relcache & distance paths | `vchordrq` scans retain their filter-key layout across PostgreSQL relation-cache invalidation, so prepared enum range queries continue reading matching compacted blocks while another session runs `ANALYZE`. Half-precision L2 search uses FP16 differences where supported without rereading centroids during routing; cosine normalization computes squared norms once for ordinary finite vectors; scans without a sphere predicate omit sphere-bound checks from the inner loop. |
| Sphere recheck semantics | Sphere scans recheck `vchordg`, half-precision, inner-product, cosine, quantized, and split-vector candidates against the heap predicate. `vchordrq` can accept a single `f32` L2 sphere directly when final reranking matches the SQL operator's whole-vector reduction and all filter keys are exact. A `NULL` sphere ends the scan immediately. |
| Nullable vectors & prefiltering | Ordered scans on nullable vectors preserve rows selected by `IS DISTINCT FROM` and `IS NOT DISTINCT FROM`; the planner recognizes validated `NOT NULL` attributes. A runtime `NULL` ordering key streams visible heap rows and resolves HOT tuples to their HOT roots; a literal `NULL` ordering key can choose a sequential scan. `vchordrq` prefiltering evaluates eligible nonvolatile subqueries during search while keeping subplans with aggregates in the executor. |
| Graph WAL & `VACUUM` repair | `vchordg` insertion publishes an extended vector page and its incoming link in one Generic WAL record, and unchanged backlinks require only a shared identity check. `vchordg` `VACUUM` uses bounded local repair to reconnect live regions across deleted bridge vertices and reclaims deleted vertices without a full-graph reachability scan. |
| RQ `VACUUM` & parallel builds | Online `vchordrq` `VACUUM` returns each compacted list's retired pages to persistent free space immediately after publishing that list, and exclusive builds reuse retired pages across lists. Unkeyed compaction streams rows using the appendable tape's tail hint, and `VACUUM` checks the appendable tape first before compacting. CPU-bound `vchordrq` and `vchordg` builds can launch parallel workers on small TOAST-backed heaps (temporary tables and parallel-unsafe expressions/predicates build serially). Keyed RQ compaction shares its sort memory budget across the leader and launched workers. |
{.wide .expand}

## Streaming filter-key scans and relcache safety {#streaming-filtered-scans}

An RQ index with filter keys now streams results from its initial IVF probes instead of materializing all expansion rounds up front. A query such as:

```sql
SELECT id FROM items
WHERE tenant_id = 42
ORDER BY embedding <-> $1
LIMIT 10;
```

stops as soon as ten matching rows are produced from the initial lists. If fewer rows match, the scan expands lazily in subsequent rounds up to `vchordrq.max_probes`. Because a later round can discover a vector closer than one already emitted from an earlier round, callers requiring a strict total distance order should overfetch and re-sort in SQL ([Result order](/docs/vchord/usage/indexing/#result-order)).

Prepared queries with enum range filters previously could lose their filter-key metadata when a concurrent `ANALYZE` invalidated the relation cache, skipping matching rows in compacted blocks. Version `1.5.0` holds the filter-key layout across cache invalidation; existing indexes receive the fix as soon as PostgreSQL loads the new shared library.

## Sphere scans, maintenance, and parallel builds {#sphere-and-maintenance}

- **Sphere recheck**: Sphere searches remain approximate in which lists or graph regions they visit, while PostgreSQL verifies candidates against the strict radius predicate. The one fast path is a single `f32` L2 sphere on `vchordrq` when the rerank uses the same whole-vector reduction as `<->` and all filter keys are exact.
- **Graph bridge repair**: `vchordg` `VACUUM` can traverse across deleted bridge vertices to reconnect live regions that still have spare neighbor slots, without running a full-graph reachability scan. If an index already lost connectivity to a live region under an older `VACUUM`, run `REINDEX INDEX CONCURRENTLY index_name;` once after upgrading.
- **Parallel builds on TOAST-backed tables**: Tables storing large vectors out-of-line in TOAST often have a small main heap that previously discouraged parallel index workers. Both `vchordrq` and `vchordg` can now launch parallel workers for CPU-bound builds on these tables while keeping temporary tables and parallel-unsafe expressions serial.

## Upgrade notes {#upgrade-notes}

Version `1.5.0` reads `1.4.0` indexes in place and keeps the same SQL objects and on-disk formats (`1001` for unkeyed `vchordrq`, `1003` for keyed `vchordrq`).

1. **PostgreSQL 14 clusters**: Upgrade PostgreSQL to 15–19 before moving from `1.3.0` to `1.5.0`.
1. **Install and restart**: Install the `1.5.0` shared library and SQL files for your PostgreSQL major version ([Installation](/docs/vchord/getting-started/installation/)) and restart PostgreSQL.
1. **Update each database**:

   ```sql
   ALTER EXTENSION vchord UPDATE TO '1.5.0';
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

Upgrading from `1.3.0` automatically runs the `1.4.0` migration step that installs the filter-key SQL objects. Upgrading from `1.2.x` or earlier also carries the `1.3.0` requirements (schema-qualified `build.external.table`, rebuilding affected `rabitq` cosine or zero/1D indexes, and `pg_read_all_stats` for query sampling); see [Upgrade and Migration](/docs/vchord/admin/migration/#upgrade) for the full checklist.
