---
title: "vchord 1.2.0: First Release Under PGSTY"
date: 2026-11-04
description: "vchord 1.2.0, the first PGSTY release, fixes multi-vector MaxSim under partial probes, sphere filters on vchordg, VACUUM vertex visibility and catalog statistics, external centroid tree validation, quantization edge cases, and prewarm/sampling privilege checks."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-1.2.0.png"
tags:
  - "release"
  - "vchord"
  - "vectorchord"
  - "vector-database"
upstream_source: ""
upstream_link: ""
---

**vchord 1.2.0** is the first release maintained by PGSTY in [`pgsty/vchord`](https://github.com/pgsty/vchord) under the AGPL-3.0 license. It supports direct in-place upgrades from `vchord 0.2.0` through `1.1.1` (`ALTER EXTENSION vchord UPDATE TO '1.2.0'` without reindexing), fixing query-correctness bugs in `vchordrq` and `vchordg`, `VACUUM` vertex visibility and catalog statistics, internal and external index-build checks, quantization edge cases, and privilege checks for prewarming and query sampling.

> [!NOTE] Extension & Release Links
> - **GitHub Release**: [`pgsty/vchord 1.2.0`](https://github.com/pgsty/vchord/releases/tag/1.2.0) · [Source Repository](https://github.com/pgsty/vchord)
> - **Extension Catalog**: [pgext.cloud (`vchord`)](https://pgext.cloud/e/vchord) · [Pigsty Extension Page (`pigsty.io`)](https://pigsty.io/ext/e/vchord/)
> - **Binary Packages**: [RPM / DEB Repository Setup](/download/) · [SBOM & License Inventory](/docs/about/sbom/)

## Changes in 1.2.0 {#changes}

| Area | Change |
| :--- | :--- |
| Multi-vector MaxSim (`@#`) | Under partial `vchordrq.probes` with `maxsim_refine = 0` and `maxsim_threshold = 0`, documents absent from a query token's candidate set now receive the worst distance in that candidate set instead of `-Infinity`, preventing missing candidates from being falsely ranked first. |
| Sphere filters & constructors | `vchordg` sphere operators (`<<->>`, `<<=>>`, `<<#>>`) compare radii in the operator's distance units rather than squared distance and set `xs_recheck = true`. All six `sphere(center, real)` constructors bind return types at extension creation time rather than via caller `search_path`. |
| `read_stream` reranking | On PostgreSQL 17/18, `vchordrq.io_rerank = 'read_stream'` keeps heap buffer guards aligned with candidate index items when concurrent `VACUUM` shortens a page's visible item batch. |
| `VACUUM` & catalog stats | `vchordg` excludes deleted vertices after `VACUUM` while keeping a deleted entry point traversable; `CREATE INDEX`, `REINDEX`, and `VACUUM` on `vchordrq` and `vchordg` report actual tuple and page counts instead of resetting `reltuples` to `0`; `ANALYZE` alone no longer triggers index cleanup. |
| Planner & parallel builds | `vchordg` honors partial index `WHERE` predicates and adds `disable_cost` for non-vector scans (such as `SELECT COUNT(*)`); `vchordrq` cost estimation accounts for `LIMIT`, filter selectivity, and `probes` depth; table options like `parallel_workers` no longer block parallel index builds. |
| Internal & external builds | Internal k-means sampling reads only MVCC-visible rows and checks `maintenance_work_mem` when `lists > samples`; external centroid builds validate tree depth (`2..=9`), reject cycles and unreachable nodes, and synthesize a root when `>= 2` top-level centroids have `parent IS NULL`. |
| Quantization types | `rabitq4` and `rabitq8` enforce `1..=65535` dimensions and code ranges (`0..=15` / `0..=255`); `quantize_to_rabitq*` rejects non-finite overflow while input functions accept legacy `NaN`/`Inf` metadata for `pg_restore`; `halfvec` distances accumulate in `f32`; quantized L2 clamps negative rounding residuals to `0` before `sqrt`. |
| Recall & privileges | `vchordrq_evaluate_query_recall` requires `exact_search => true` for `@#`, derives multi-level default `accu_probes`, and restores `vchordrq.*` GUCs; `vchordrq_prewarm`, `vchordg_prewarm`, and query sampling enforce table ownership or `SELECT` privileges. |
| Build & platform support | Upgraded to `pgrx 0.19.3` for PostgreSQL 14–18 on Linux x86_64 and aarch64, with full in-place upgrade scripts from `0.2.0` through `1.1.1`. |
{.wide .expand}

## Multi-vector MaxSim (`@#`), sphere filters, and `read_stream` reranking {#query-correctness}

- **MaxSim (`@#`) missing-value estimates under partial probes**: VectorChord's `@#` operator negates MaxSim similarity so smaller (more negative) values rank first in ascending `ORDER BY`. Under partial probes, a candidate document can appear in the probed lists for some query vectors while being absent from others. Previously, when both `vchordrq.maxsim_refine = 0` and `vchordrq.maxsim_threshold = 0`, missing query-token hits defaulted to `-Infinity` (`f32::NEG_INFINITY`), which falsely ranked unprobed candidates first. In `1.2.0`, when neither refinement nor a threshold supplies an estimate, missing hits use the worst distance observed in that query token's candidate set.
- **`vchordg` sphere similarity filters (`<<->>`, `<<=>>`, `<<#>>`)**: Internally, `vchordg` tracks squared L2 and cosine distances during graph traversal. Previously, sphere range scans compared the user-supplied radius directly against the internal squared distance and returned index tuples without requesting a heap recheck. `vchordg` now converts the radius into the operator's distance units before pruning and sets `xs_recheck = true` on returned items so PostgreSQL rechecks the exact sphere predicate on the heap tuple.
- **`search_path`-safe `sphere(...)` constructors**: The six `sphere(vector, real)`, `sphere(halfvec, real)`, `sphere(rabitq8, real)`, and multi-vector array constructors are now defined as SQL-language `ROW($1, $2)::sphere_*` expressions whose composite return types are bound at `CREATE EXTENSION` / `ALTER EXTENSION` time. Calling `sphere(...)` works regardless of the caller's `search_path`.
- **PostgreSQL 17/18 `read_stream` reranking**: When `vchordrq.io_rerank = 'read_stream'` is active on PostgreSQL 17 or 18 and concurrent `VACUUM` removes heap tuples between index scan and heap fetch, the `read_stream` batch consumer keeps its buffer pin guards aligned with the remaining candidate tuples rather than advancing out of sync.

## Index maintenance, `VACUUM`, and planner cost estimation {#maintenance-and-planner}

- **`vchordg` `VACUUM` visibility and entry-point reachability**: After `VACUUM` marks deleted heap TIDs in a `vchordg` index, graph searches exclude deleted vertices from returned results while still traversing through the graph's entry point if that entry point was deleted, keeping surviving vertices reachable without a `REINDEX`.
- **`vchordg` partial indexes and `COUNT(*)` protection**: `vchordg` now supports partial index predicates (`CREATE INDEX ... USING vchordg (...) WHERE ...`) and adds PostgreSQL's `disable_cost` penalty whenever a scan has no vector ordering or filter clauses, preventing the planner from choosing a graph index for plain `SELECT COUNT(*)` queries.
- **Accurate `reltuples` / `relpages` statistics and `ANALYZE` no-op**: Previously, `ambuild` and `amvacuumcleanup` returned zeroed `IndexBuildResult` / `IndexVacuumInfo` counters, which caused `CREATE INDEX`, `REINDEX`, and `VACUUM` to overwrite `pg_class.reltuples` with `0`. Both `vchordrq` and `vchordg` now report actual indexed tuple and page counts. When `ANALYZE` runs (`analyze_only = true`), `amvacuumcleanup` returns immediately without running index compaction or page cleanup.
- **Parallel index build planning**: Setting table storage options such as `ALTER TABLE items SET (parallel_workers = 4)` previously caused `amoptions` validation to reject the table's reloptions when planning parallel index builds. Both `vchordrq` and `vchordg` now validate only index-level reloptions so parallel worker planning proceeds normally.
- **`vchordrq` cost model**: `amcostestimate` for `vchordrq` now incorporates the query's `LIMIT`, filter selectivity, and the effective `probes` budget when estimating filtered vector scans, and adds `disable_cost` when a multi-level `vchordrq.probes` setting does not match the number of levels in the index's `lists` hierarchy.

## Internal and external index build validation {#index-builds}

- **MVCC-visible k-means sampling and memory checks**: Internal k-means clustering checks `HeapTupleSatisfiesVisibility` before sampling a heap tuple so dead or uncommitted tuples do not skew centroids. The initial sampling buffer is sized from the estimated live row count (capped at `max(lists) * sampling_factor`), and centroid buffer allocations are checked against `maintenance_work_mem` even when `lists` exceeds the number of sampled rows.
- **External centroid tree validation**: When building a `vchordrq` index from an external centroid table (`[build.external]`), `vchord` validates the `id` / `parent` hierarchy before partitioning vectors:
  1. The tree depth must be between `2` and `9` levels (including the root), matching the `1..=8` `lists` levels supported by `vchordrq`.
  2. Cyclic `parent` chains and disconnected nodes are rejected with a descriptive error.
  3. If two or more top-level centroids have `parent IS NULL`, `vchordrq` automatically synthesizes a root node above them so flat or multi-root centroid tables do not need a manual dummy root row.
- **Strict `probes` and `alpha` validation**: Both `SET vchordrq.probes` and the per-index `probes` storage option validate every comma-separated integer (`1..=4294967295`, permitting surrounding whitespace and at most one trailing comma) and reject invalid strings immediately. For `vchordg`, the `alpha` build option must contain `1..=8` non-decreasing floats in `[1.0, 2.0)` whose first element is `1.0`.

## Quantization types (`rabitq4`, `rabitq8`, and `halfvec`) {#quantization-types}

- **Dimensions and code ranges**: `rabitq4` and `rabitq8` enforce `1..=65535` dimensions (`typmod` validation and input parsing) and verify that every quantized code lies in `0..=15` (`rabitq4`) or `0..=255` (`rabitq8`), rejecting trailing tokens or malformed brackets.
- **Overflow rejection with `pg_dump` / `pg_restore` compatibility**: `quantize_to_rabitq4` and `quantize_to_rabitq8` reject input vectors whose norm or dot product overflows `f32` (`NaN` / `Infinity`), and produce finite metadata for zero or constant vectors. At the same time, the `rabitq4` and `rabitq8` text and binary input functions still accept legacy `NaN` / `Inf` metadata fields so existing backups created under `1.1.x` restore without error.
- **`f32` accumulation for `halfvec` and clamped L2 roots**: `halfvec` distance operators (`<->`, `<=>`, `<#>`) now accumulate in `f32` rather than `f16` so large or high-dimensional `halfvec` values do not overflow to `Infinity`. Quantized L2 distance functions clamp tiny negative floating-point rounding residuals to `0.0` before calling `sqrt`, eliminating spurious `NaN` results on near-identical vectors.

## Recall evaluation and prewarm privileges {#recall-and-security}

- **`vchordrq_evaluate_query_recall` improvements**:
  - Multi-vector MaxSim (`@#`) queries now require `exact_search => true` (attempting approximate ground-truth probing with `@#` raises an error explaining why `exact_search => true` is required).
  - When `accu_probes` is omitted, `vchordrq_evaluate_query_recall` generates a `65535` entry for each level of a multi-level `lists` index (for example, `'65535,65535'` on a 2-level index) instead of a single `'65535'` value that would fail level-count validation.
  - Temporary changes to `vchordrq.probes`, `vchordrq.epsilon`, and `vchordrq.enable_scan` inside `vchordrq_evaluate_query_recall` are restored to their prior values and GUC sources (`RESET` when previously unset) even if the query errors out.
- **Prewarm and query-sampling privilege checks**:
  - `vchordrq_prewarm(regclass, integer)` and `vchordg_prewarm(regclass)` verify that the calling role owns the underlying table or holds table-level `SELECT` privilege before warming index pages into shared buffers.
  - Enabling or configuring query sampling (`vchordrq.query_sampling_*`) checks that the role owns the table, holds table-level `SELECT`, or is a member of `pg_read_all_stats`. Similarly, reading `vchordrq_sampled_queries` filters out recorded queries from indexes whose underlying tables the current role is not allowed to read.

## Known issues {#known-issues}

Package QA for `1.2.0` found two cases where results can come back out of distance order. Both are tracked in [pgsty/vchord#17](https://github.com/pgsty/vchord/issues/17) for a later release. Recall is not affected.

- `vchordg` can return `ORDER BY ... LIMIT` rows out of distance order, because it keeps searching while it returns rows. A larger `vchordg.ef_search` makes this rarer but does not rule it out.
- On `halfvec` columns, rows whose distances differ by about 0.0001 or less can be swapped. This affects `vchordrq` with `halfvec_cosine_ops` and `vchordg` with any `halfvec` operator class.

When strict order matters, re-sort the candidates in an outer query; see [Graph Index: Result order](/docs/vchord/usage/graph-index/#result-order). The [GitHub release](https://github.com/pgsty/vchord/releases/tag/1.2.0) lists the other known issues.

## Upgrading to 1.2.0 and packages {#upgrade-and-packages}

`vchord 1.2.0` is binary- and on-disk-compatible with indexes created in `0.2.0` through `1.1.1`. Install the `1.2.0` package for your PostgreSQL version, restart PostgreSQL so the updated `vchord.so` is loaded via `shared_preload_libraries`, and run:

```sql
ALTER EXTENSION vchord UPDATE TO '1.2.0';
SELECT vchord_version();
-- 1.2.0
```

Direct upgrade scripts are shipped for every historical version from `0.2.0` through `1.1.1`, and the shared library retains C entry-point compatibility wrappers (`_vchord_0_3_*` and `_vchord_0_4_*`) so databases still running pre-`1.0.0` SQL catalog definitions can execute `ALTER EXTENSION vchord UPDATE TO '1.2.0'` without error.

Native RPM and DEB packages (`1.2.0-1PIGSTY` / `1.2.0-1PGSTY`) for PostgreSQL **14–18** across 16 Linux distributions on `x86_64` and `aarch64` are available on the [Download page](/download/). See the [Upgrade & Migration Guide](/docs/vchord/admin/migration/), [Indexing Guide](/docs/vchord/usage/indexing/), [Quantization Types Guide](/docs/vchord/usage/quantization-types/), and [SBOM page](/docs/about/sbom/) for complete details.
