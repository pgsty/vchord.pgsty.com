---
math: true
title: "GUC & Index Parameters"
description: "Complete reference of session GUC parameters and index storage options for vchord_bm25."
weight: 20
icon: fa-solid fa-sliders
---

> [!IMPORTANT]
> **1.0.0** is the first PGSTY release, with native `tsvector` and a new index format. Examples labeled 0.3.x use the historical `bm25vector` API. In-place upgrades are blocked; read the [1.0.0 migration guide](/docs/bm25/reference/migration/) before changing binaries.


## Historical Releases (`v0.1.0` – `v0.3.0`): `bm25_catalog.*` GUCs {#stable-releases-v010--v030-bm25_catalog-gucs}

In versions `v0.1.0` through `v0.3.0`, all session GUC parameters use the `bm25_catalog.` prefix and can be changed per session or transaction by any user (`GucContext::Userset`):

| Parameter Name | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bm25_catalog.bm25_limit` | `integer` | `100` | `-1` .. `65535` | Maximum number of top-scoring documents to return from a `bm25` index scan. Set to `-1` to disable Block-WeakAnd pruning and perform an exhaustive brute-force scan; set to `0` to return no rows. Must be \(\ge\) your SQL `LIMIT`. |
| `bm25_catalog.enable_index` | `boolean` | `true` | `true` / `false` | Enables or disables the `bm25` index scan in the PostgreSQL query planner. Set to `false` to force a sequential scan with exact `search_bm25query` evaluation. |
| `bm25_catalog.enable_prefilter` | `boolean` | `true` | `true` / `false` | Introduced in `v0.2.2`. When `true`, filters out documents that do not satisfy the query/visibility check before inserting them into the Block-WeakAnd Top-K heap. |
| `bm25_catalog.segment_growing_max_page_size` | `integer` | `4096` | `1` .. `1000000` | Maximum size (in 8 KB pages, default `4096` = 32 MB) of the append-only growing segment before it is sealed into a compressed, delta-bitpacked read-only segment. |
{.wide .expand}

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

## 1.0.0: `bm25.*` GUCs & Index Reloptions {#next-gen-main-branch-bm25-gucs--index-reloptions}

In 1.0.0, session GUCs use the `bm25.` prefix and work together with per-index storage parameters (`WITH (...)`):

### Session GUC Parameters (1.0.0) {#session-guc-parameters-main}

| Parameter Name | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bm25.enable_scan` | `boolean` | `true` | `true` / `false` | Enables or disables `bm25` index scans in the planner. |
| `bm25.limit` | `integer` | `100` | `0` .. `65535` | Initial scan batch size; zero selects 100. Explicit settings override the index. Scans continue as needed for SQL `LIMIT`, `OFFSET` and post-filtering. |
| `bm25.prefilter` | `boolean` | `false` | `true` / `false` | Enables pre-filtering during `bm25` index scans (overrides the index's `prefilter` storage parameter even when explicitly set to `false`). |
{.wide .expand}

Settings from `postgresql.conf`, `ALTER DATABASE`, `ALTER ROLE`, or client startup options also override index reloptions. `RESET` restores that configured default; it falls back to the index only when the GUC source returns to the built-in default.

### Index Storage Parameters (`WITH (...)` in 1.0.0) {#index-storage-parameters-with--in-main}

| Storage Parameter | Type | Default | Valid Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `options` | `string` (TOML) | `k1 = 1.2`<br>`b = 0.75` | `k1`: `1.2..2.0`<br>`b`: `0.0..1.0` | TOML string configuring the Okapi BM25 parameters \(k_1\) and \(b\) for the index. |
| `limit` | `integer` | `100` | `0` .. `65535` | Initial batch size used when `bm25.limit` has its built-in default source. Zero selects 100; this does not cap the SQL result count. |
| `prefilter` | `boolean` | `false` | `true` / `false` | Per-index default prefilter setting. |
| `maintenance_min_rows` | `integer` | `1000` | `0` .. `2147483647` | Minimum growing records before an automatic merge. The actual threshold is the greater of this value and `maintenance_scale_factor` × sealed records. |
| `maintenance_scale_factor` | `real` | `0.1` | `0` .. `1` | Growing/sealed or tombstone/total fraction that triggers merging during VACUUM. Old snapshots can delay reclamation and the next merge. |
{.wide .expand}
