---
title: "vchord 1.4.0: Filter Keys, Adaptive Read-Ahead, and PostgreSQL 19"
date: 2026-11-23
description: "vchord 1.4.0 adds RQ filter key columns with zone maps and hashed key operator classes, adaptive I/O read-ahead, online list compaction, pgrx 0.20.1, and PostgreSQL 15–19 support."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.4.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.4.0/]
---

**vchord 1.4.0** introduces `vchordrq` filter key columns, adaptive read-ahead defaults, online list compaction, and PostgreSQL 15–19 support on `x86_64` and `aarch64` with `pgrx 0.20.1` and Rust `1.100.0+`. PostgreSQL 14 is no longer supported.

> [!NOTE] Superseded Draft Milestone
> The `1.4.0` tag (`https://github.com/pgsty/vchord/tree/1.4.0`) remained a draft GitHub Release and was superseded the next day by the published [**vchord 1.5.0**](/release/vchord-1.5.0/) release, which adds streaming filtered scans, graph `VACUUM` bridge repair, and relation-cache stability. Install [`vchord 1.5.0`](/release/vchord-1.5.0/) for production deployments and pre-built GitHub packages.

## Changes in 1.4.0 {#changes}

| Area | Change |
| :--- | :--- |
| RQ filter keys | Add multi-column filter keys on `vchordrq` indexes for equality, range, and `IS [NOT] NULL` conditions, plus separate hashed key operator classes (`uuid_hash_ops`, `int4_hash_ops`, `int8_hash_ops`). Keyed lists sort entries by key value and skip blocks via leading-key min/max `zone_maps`. Enum ranges follow PostgreSQL enum order, including domains and values inserted with `ALTER TYPE ... ADD VALUE ... BEFORE/AFTER`. `= ANY(...)` pushdown on ordered scans requires PostgreSQL 17+. |
| Filtered scan expansion | Pushed-down filter keys automatically expand beyond initial IVF `probes` until `LIMIT` is satisfied or `vchordrq.max_probes` is reached (default `-1`, unbounded; initial probes are always honored). Ordered refills sort on the original `f32` rerank distance (spilling at `work_mem` if needed) and defer heap read-ahead until rows leave the sort when reranking from the index. |
| Distance, sphere & SIMD | Center residual inner-product estimates in leaf lists on the query's projection onto the centroid. Rescale finite nonzero vectors with extreme magnitudes during cosine normalization. Route `halfvec` L2 via FP16 differences on supported CPUs with overflow fallback while keeping FP32 reranking and residual bounds. Round `vector`/`halfvec` L2 sphere radii outward before squaring so boundary candidates reach PostgreSQL's strict recheck. Single-pass quantization and multi-accumulator SIMD reductions speed up long vectors. |
| I/O & online compaction | On PostgreSQL 17+, `vchordrq.io_search` defaults to `mixed` and `vchordrq.io_rerank` defaults to `prefetch_buffer`, with upcoming table-page read-ahead ahead of table reranking. `vchordrq` list compaction runs while readers continue using existing pages, acquiring an exclusive jump-page lock only briefly to publish new tapes and absorb concurrent inserts. |
| Planner & NULL safety | Preserve old-snapshot protection whenever any parallel `vchordrq` or `vchordg` build participant encounters a broken HOT chain. Avoid index paths for explicit NULL checks on the vector or strict indexed function inputs (including `OR` branches and null-safe comparisons). With a runtime `NULL` ordering parameter, return visible heap rows subject to partial predicates and query conditions. Allow PostgreSQL to sort additional distance keys after the first. |
| Observability & tooling | Report `pg_stat_user_indexes.idx_scan` across PostgreSQL 15–19 and `Index Searches` in `EXPLAIN ANALYZE` on PostgreSQL 18+; pass read-only scan hints on PostgreSQL 19; reject invalid indexes in `vchordrq_prewarm` and `vchordg_prewarm` before reading pages. Upgrade option parsing to `toml` 1.2.2 (fixing a backend crash on malformed options) and query recording to `rusqlite` 0.43.0 (bundled SQLite 3.54.1), recovering with a fresh file if a corrupt sampling database is detected on open. |
| Platform & build | Support PostgreSQL 15–19 on Linux `x86_64` and `aarch64` (`pgrx 0.20.1`). Require Rust `1.100.0+` and matching Clang, libclang, and LLVM tools. Drop PostgreSQL 14. |
{.wide .expand}

## Filter keys on `vchordrq` {#filter-keys}

Selective `WHERE` predicates on tenant IDs, categories, or timestamps can leave a standard IVF probe short of `LIMIT` rows. Starting in `1.4.0`, you can append filter key columns after the vector column so `vchordrq` evaluates key conditions inside the index before reranking:

```sql
CREATE INDEX items_vec_tenant_idx
ON items USING vchordrq (embedding vector_cosine_ops, tenant_id, created_at)
WITH (options = $$
residual_quantization = true
[build.internal]
lists = [2000]
spherical_centroids = true
$$);

SELECT id FROM items
WHERE tenant_id = 42 AND created_at >= now() - interval '30 days'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

- **Supported types**: `int2`, `int4`, `int8`, `float4`, `float8`, `uuid`, `date`, `timestamp`, `timestamptz`, `oid`, `bool`, and PostgreSQL enums.
- **Hashed keys**: For wide equality-only keys such as UUIDs, `uuid_hash_ops`, `int4_hash_ops`, and `int8_hash_ops` store a compact hash (for example `owner uuid_hash_ops (bytes = 4)`), with PostgreSQL rechecking hash collisions.
- **Bounding expansion**: Because `vchordrq.max_probes` defaults to `-1`, a filter value with no matching rows scans every list before returning empty. Set `vchordrq.max_probes` to cap total lists visited, or to the initial leaf probe count on a single-level index when common filter values only need streaming from the initial probes. Measure recall before lowering a production cap.

In `1.4.0`, an ordered scan that can expand reranks and sorts eligible candidates before emitting the first row. [vchord 1.5.0](/release/vchord-1.5.0/) changes keyed ordered scans to stream the initial probes immediately and expand lazily on demand.

## Storage formats and upgrade notes {#upgrade-notes}

1. **Upgrade PostgreSQL 14 first**: `pgrx 0.20.1` no longer supports PostgreSQL 14. Stay on [vchord 1.3.0](/release/vchord-1.3.0/) until PostgreSQL is upgraded to 15–19.
1. **Install and update**: Install the matching library and SQL files, restart PostgreSQL, and run:

   ```sql
   ALTER EXTENSION vchord UPDATE;
   ```
{.steps}

- **On-disk formats**: Existing `1.3.0` single-column `vchordrq` indexes and newly built unkeyed `vchordrq` indexes remain format `1001`. New `vchordrq` indexes with filter key columns use format `1003`.
- **Rollback**: The `1.3.0 → 1.4.0` SQL script adds filter-key support functions and operator classes; downgrading packages alone leaves the `1.4.0` SQL catalog in place. To roll back to `1.3.0`, drop or replace keyed indexes first and restore a `1.3.0`-compatible catalog or backup.
- **Broken HOT chain fix**: The parallel build visibility fix protects transactions whose snapshots predate a build that encounters a broken HOT chain. Existing indexes do not need a blanket rebuild.
- **Approximate sphere scans**: Sphere scans (`<<->>`, `<<=>>`, `<<#>>`) remain approximate in both `vchordrq` and `vchordg` ([issue #29](https://github.com/pgsty/vchord/issues/29)). Workloads requiring every row inside a radius should verify a sequential scan with `EXPLAIN`.

See [Filtering](/docs/vchord/usage/filtering/#filter-keys), [vchordrq Index](/docs/vchord/usage/indexing/), and [Upgrade and Migration](/docs/vchord/admin/migration/) for full guidance.
