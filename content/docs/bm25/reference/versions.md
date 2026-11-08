---
math: true
title: "Release History & API Evolution"
description: "Version changelog and SQL schema evolution of VectorChord-BM25 (vchord_bm25) from v0.1.0 through 1.1.0."
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!IMPORTANT]
> **1.1.0** is the current PGSTY release. It keeps the native `tsvector` API and format 4 introduced in 1.0.0, so healthy 1.0.0 indexes do not need a rebuild. Examples labeled 0.3.x use the historical `bm25vector` API; read the [migration guide](/docs/bm25/reference/migration/) before changing binaries.

`pg_tokenizer 1.0.0` is an independent tokenizer release. Use it with the historical `vchord_bm25` 0.3.x `bm25vector` workflow, or use its native `tsvector` helpers with the 1.0.0 API when custom tokenization is required. It is not a dependency of the native `vchord_bm25` path.


This page tracks the release history and SQL schema evolution of `vchord_bm25` ([`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) / [`supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)).

## Version Summary Matrix

| Version | Schema | Indexed Type | Tokenizer | Key Additions |
| :--- | :--- | :--- | :--- | :--- |
| **`1.1.0`** | Extension schema | `tsvector` | Native `to_tsvector` (or custom) | Correct WAND bounds for floating-point near ties; dense ordinal term accumulation; keeps the 1.0.0 SQL API and format 4 index storage. |
| **`1.0.0`** | Extension schema | `tsvector` | Native `to_tsvector` (or custom) | Complete storage & index engine rewrite on native `tsvector`; external sort parallel `ambuild`; index reloptions (`options`, `limit`, `prefilter`); `bm25.*` GUCs; PostgreSQL 18 support. |
| **`v0.3.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `bm25_page_inspect(regclass, int)`, `to_bm25query(regclass, int[])` overload, and PostgreSQL 18 compatibility. |
| **`v0.2.2`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `bm25_catalog.enable_prefilter` GUC for accurate filtered Top-K BM25 search with `WHERE` clauses. |
| **`v0.2.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Bug fixes for growing/sealed segment transitions and vacuum cleanup. |
| **`v0.2.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `=` and `<>` equality operators on `bm25vector` and implicit cast `CREATE CAST (int[] AS bm25vector) AS IMPLICIT`. |
| **`v0.1.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Decoupled tokenization into standalone `pg_tokenizer` extension; changed `to_bm25query(regclass, bm25vector)` signature. |
| **`v0.1.0`** | `bm25_catalog` | `bm25vector` | Built-in `unicode` | Initial release with `bm25vector`, `bm25query`, `USING bm25`, and Block-WeakAnd Top-K scan. |
{.wide .expand}

---

## Detailed Upgrade Changes

### 1.1.0: Correctness and query-path optimization {#v110-correctness-and-query-path-optimization}

- Summed WAND upper bounds in the same query order as document scoring. This closes a rare floating-point rounding case that could prune a near-tied document and silently omit it from a complete scan.
- Replaced per-sum ordinal sorting with a dense bitmap over terms present in the sealed index. Queries with many absent terms avoid bitmap work proportional to those absent terms while preserving scoring order.
- Kept the SQL API and format 4 index storage compatible with healthy 1.0.0 indexes; the `1.0.0--1.1.0` upgrade script is intentionally empty.
- Long, high-frequency multi-term queries remain workload-dependent. `WHERE ... @@ ...` is still an executor filter; a GIN index can provide a better path for highly selective or empty matches.

### `v0.3.0` (`sql/vchord_bm25--0.2.2--0.3.0.sql`)

- Added page diagnostic function:
  ```sql
  CREATE FUNCTION bm25_page_inspect(index regclass, blkno INT) RETURNS TEXT;
  ```
- Added `to_bm25query(regclass, int[])` convenience overload in late `0.3.x`.

### `v0.2.2` (`sql/vchord_bm25--0.2.1--0.2.2.sql`)

- Added prefiltering support in Block-WeakAnd (`bm25_catalog.enable_prefilter` GUC, enabled by default in `0.3.0`).
- Improved MVCC visibility checking during index scans to prevent dead/filtered tuples from polluting the Top-K threshold.

### `v0.2.0` (`sql/vchord_bm25--0.1.1--0.2.0.sql`)

- Added `=` and `<>` operators for `bm25vector`.
- Added implicit cast from `int[]` to `bm25vector` (`_vchord_bm25_cast_array_to_bm25vector`), allowing `tokenize(text, name)` output (`INT[]`) to be assigned or passed directly wherever `bm25vector` is expected.

### `v0.1.1` (`sql/vchord_bm25--0.1.0--0.1.1.sql`)

- Extracted built-in `create_tokenizer` / `tokenize` functions into the dedicated `pg_tokenizer` extension (`tokenizer_catalog`), enabling rich text analyzers, Snowball stemmers, stopwords, synonyms, HuggingFace models, `jieba`, and `lindera`.
- Simplified `to_bm25query(index_oid regclass, query_vector bm25vector)` to accept a `bm25vector` directly.

### 1.0.0: Native `tsvector` and PGSTY Fixes {#next-generation-rewrite-main-branch}

- Replaced custom `bm25vector` with PostgreSQL's native `tsvector` (`CREATE OPERATOR CLASS bm25_ops FOR TYPE tsvector USING bm25`), allowing users to index `to_tsvector(...)` columns directly with `USING bm25`.
- Added parallel index build (`bm25_parallel_build_main`) with external merge sort.
- Added configurable BM25 hyperparameters (\(k_1 \in [1.2, 2.0]\), \(b \in [0.0, 1.0]\)) via a TOML `options` string; see [Indexing](/docs/bm25/usage/indexing/).
- Scans continue for SQL `LIMIT`, `OFFSET`, and post-filtering; `bm25.limit` controls the initial batch.
- Added concurrent segment maintenance through `VACUUM` and `bm25_maintain()`, with deferred page reclamation for old snapshots.
- Hardened table/column permissions, RLS checks, schema relocation, and scan cleanup after errors or cancellation. See [migration and permissions](/docs/bm25/reference/migration/).
