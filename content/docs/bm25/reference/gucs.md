---
math: true
title: "GUC & Index Parameters"
description: "Complete reference of session GUC parameters and index storage options for vchord_bm25."
weight: 20
---

> [!IMPORTANT]
> Current source targets **0.4.0 (unreleased)**, with native `tsvector` and a new index format. Examples labeled 0.3.x use the historical `bm25vector` API. In-place upgrades are blocked; read the [0.4.0 migration guide](/docs/bm25/reference/migration/) before changing binaries.


## Stable Releases (`v0.1.0` – `v0.3.0`): `bm25_catalog.*` GUCs

In versions `v0.1.0` through `v0.3.0`, all session GUC parameters use the `bm25_catalog.` prefix and can be changed per session or transaction by any user (`GucContext::Userset`):

| Parameter Name | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bm25_catalog.bm25_limit` | `integer` | `100` | `-1` .. `65535` | Maximum number of top-scoring documents to return from a `bm25` index scan. Set to `-1` to disable Block-WeakAnd pruning and perform an exhaustive brute-force scan; set to `0` to return no rows. Must be \(\ge\) your SQL `LIMIT`. |
| `bm25_catalog.enable_index` | `boolean` | `true` | `true` / `false` | Enables or disables the `bm25` index scan in the PostgreSQL query planner. Set to `false` to force a sequential scan with exact `search_bm25query` evaluation. |
| `bm25_catalog.enable_prefilter` | `boolean` | `true` | `true` / `false` | Introduced in `v0.2.2`. When `true`, filters out documents that do not satisfy the query/visibility check before inserting them into the Block-WeakAnd Top-K heap. |
| `bm25_catalog.segment_growing_max_page_size` | `integer` | `4096` | `1` .. `1000000` | Maximum size (in 8 KB pages, default `4096` = 32 MB) of the append-only growing segment before it is sealed into a compressed, delta-bitpacked read-only segment. |

### Examples (`v0.1` – `v0.3`)

```sql
-- Increase Top-K window for deep pagination (e.g., LIMIT 500)
SET bm25_catalog.bm25_limit = 500;

-- Force brute-force scan over all index postings
SET bm25_catalog.bm25_limit = -1;

-- Enable prefiltering for queries with selective WHERE clauses
SET bm25_catalog.enable_prefilter = true;

-- Disable index scan to benchmark sequential scan baseline
SET bm25_catalog.enable_index = false;
```

---

## Next-Gen `main` Branch: `bm25.*` GUCs & Index Reloptions

In the `main` branch rewrite, session GUCs use the `bm25.` prefix and work together with per-index storage parameters (`WITH (...)`):

### Session GUC Parameters (`main`)

| Parameter Name | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bm25.enable_scan` | `boolean` | `true` | `true` / `false` | Enables or disables `bm25` index scans in the planner. |
| `bm25.limit` | `integer` | `0` | `0` .. `65535` | Maximum candidates. Any explicitly set value overrides the index; explicit zero makes index scans error. `RESET` restores the index fallback. |
| `bm25.prefilter` | `boolean` | `false` | `true` / `false` | Enables pre-filtering during `bm25` index scans (overrides the index's `prefilter` storage parameter even when explicitly set to `false`). |

Settings from `postgresql.conf`, `ALTER DATABASE`, `ALTER ROLE`, or client startup options also override index reloptions. `RESET` restores that configured default; it falls back to the index only when the GUC source returns to the built-in default.

### Index Storage Parameters (`WITH (...)` in `main`)

| Storage Parameter | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `options` | `string` (TOML) | `k1 = 1.2, b = 0.75` | `k1`: `1.2..2.0`<br>`b`: `0.0..1.0` | TOML string configuring the Okapi BM25 parameters \(k_1\) and \(b\) for the index. |
| `limit` | `integer` | `0` | `0` .. `65535` | Per-index fallback search limit used when `bm25.limit` has its default source (`RESET`), not when explicitly set to zero. |
| `prefilter` | `boolean` | `false` | `true` / `false` | Per-index default prefilter setting. |
