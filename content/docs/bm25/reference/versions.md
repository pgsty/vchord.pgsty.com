---
math: true
title: "Release History & API Evolution"
description: "Version changelog and SQL schema evolution of VectorChord-BM25 (vchord_bm25) from v0.1.0 to v0.3.0 and main."
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!IMPORTANT]
> Current source targets **0.4.0 (unreleased)**, with native `tsvector` and a new index format. Examples labeled 0.3.x use the historical `bm25vector` API. In-place upgrades are blocked; read the [0.4.0 migration guide](/docs/bm25/reference/migration/) before changing binaries.

`pg_tokenizer 1.0.0` is an independent tokenizer release. Use it with the historical `vchord_bm25` 0.3.x `bm25vector` workflow, or use its native `tsvector` helpers with the 0.4.0/main API when custom tokenization is required. It is not a dependency of the native `vchord_bm25` path.


This page tracks the release history and SQL schema evolution of `vchord_bm25` ([`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) / [`supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)).

## Version Summary Matrix

| Version | Schema | Indexed Type | Tokenizer | Key Additions |
| :--- | :--- | :--- | :--- | :--- |
| **`0.4.0` / `main` (unreleased)** | Extension schema | `tsvector` | Native `to_tsvector` (or custom) | Complete storage & index engine rewrite on native `tsvector`; external sort parallel `ambuild`; index reloptions (`options`, `limit`, `prefilter`); `bm25.*` GUCs; PostgreSQL 18 support. |
| **`v0.3.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `bm25_page_inspect(regclass, int)`, `to_bm25query(regclass, int[])` overload, and PostgreSQL 18 compatibility. |
| **`v0.2.2`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `bm25_catalog.enable_prefilter` GUC for accurate filtered Top-K BM25 search with `WHERE` clauses. |
| **`v0.2.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Bug fixes for growing/sealed segment transitions and vacuum cleanup. |
| **`v0.2.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Added `=` and `<>` equality operators on `bm25vector` and implicit cast `CREATE CAST (int[] AS bm25vector) AS IMPLICIT`. |
| **`v0.1.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | Decoupled tokenization into standalone `pg_tokenizer` extension; changed `to_bm25query(regclass, bm25vector)` signature. |
| **`v0.1.0`** | `bm25_catalog` | `bm25vector` | Built-in `unicode` | Initial release with `bm25vector`, `bm25query`, `USING bm25`, and Block-WeakAnd Top-K scan. |
{.wide .expand}

---

## Detailed Upgrade Changes

### `v0.3.0` (`sql/vchord_bm25--0.2.2--0.3.0.sql`)

- Added page diagnostic function:
  ```sql
  CREATE FUNCTION bm25_page_inspect(index regclass, blkno INT) RETURNS TEXT;
  ```
- Added `to_bm25query(regclass, int[])` convenience overload in `main`/late `0.3.x`.

### `v0.2.2` (`sql/vchord_bm25--0.2.1--0.2.2.sql`)

- Added prefiltering support in Block-WeakAnd (`bm25_catalog.enable_prefilter` GUC, enabled by default in `0.3.0`).
- Improved MVCC visibility checking during index scans to prevent dead/filtered tuples from polluting the Top-K threshold.

### `v0.2.0` (`sql/vchord_bm25--0.1.1--0.2.0.sql`)

- Added `=` and `<>` operators for `bm25vector`.
- Added implicit cast from `int[]` to `bm25vector` (`_vchord_bm25_cast_array_to_bm25vector`), allowing `tokenize(text, name)` output (`INT[]`) to be assigned or passed directly wherever `bm25vector` is expected.

### `v0.1.1` (`sql/vchord_bm25--0.1.0--0.1.1.sql`)

- Extracted built-in `create_tokenizer` / `tokenize` functions into the dedicated `pg_tokenizer` extension (`tokenizer_catalog`), enabling rich text analyzers, Snowball stemmers, stopwords, synonyms, HuggingFace models, `jieba`, and `lindera`.
- Simplified `to_bm25query(index_oid regclass, query_vector bm25vector)` to accept a `bm25vector` directly.

### Next-Generation Rewrite (`main` Branch)

- Replaced custom `bm25vector` with PostgreSQL's native `tsvector` (`CREATE OPERATOR CLASS bm25_ops FOR TYPE tsvector USING bm25`), allowing users to index `to_tsvector(...)` columns directly with `USING bm25`.
- Added parallel index build (`bm25_parallel_build_main`) with external merge sort and constant maintenance memory consumption.
- Added configurable BM25 hyperparameters (\(k_1 \in [1.2, 2.0]\), \(b \in [0.0, 1.0]\)) via `WITH (options = $$ k1 = 1.2, b = 0.75 $$)`.
