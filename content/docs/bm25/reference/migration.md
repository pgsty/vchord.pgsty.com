---
title: "Migrating to 1.0.0"
description: "The native tsvector API, installation schema, permissions, and migration boundary for vchord_bm25 1.0.0."
weight: 35
icon: fa-solid fa-right-left
---

`pgsty/vchord_bm25` **1.0.0** is the first PGSTY release. It uses PostgreSQL's native `tsvector` and a new index storage engine. Historical 0.3.x packages and suite images use `bm25vector`; the two APIs and index formats are incompatible.

| Interface | 0.3.x | 1.0.0 |
| --- | --- | --- |
| Document value | `bm25vector`, integer token IDs and frequencies | `tsvector` with positions |
| Query constructor | `to_bm25query(index, vector)` | `to_bm25query(vector, index)` |
| Query fields | `(index_oid regclass, query_vector bm25vector)` | `(vector tsvector, index regclass)` |
| Score | `real` | `double precision` |
| Schema | Fixed `bm25_catalog` | Selected extension schema, relocatable |
| Candidate limit | `bm25_catalog.bm25_limit`, default 100 | `bm25.limit` or index `limit`; initial batch defaults to 100, results continue as needed |
| Tokenization | `pg_tokenizer` integer arrays | `to_tsvector`, or pg_tokenizer 1.0.0 `tokenize_to_tsvector` / `analyze_to_tsvector` |
{.wide .expand}

1.0.0 ships `vchord_bm25--1.0.0.sql`, generated from the Rust library. Packaging compares the checked-in schema with the compiled API and rejects mismatches. The old install SQL remains available in Git for old binaries; changing the control version to 0.3.0 does not make the current engine compatible with it.

## Install and query

Build the 1.0.0 source using `PG_CONFIG=/path/to/pg_config make build` and `PG_CONFIG=/path/to/pg_config make install`. Add `vchord_bm25` to `shared_preload_libraries` and restart PostgreSQL. Standard text search needs no external tokenizer:

```sql
CREATE EXTENSION vchord_bm25;
CREATE TABLE documents (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    passage text NOT NULL,
    vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);
INSERT INTO documents (passage) VALUES
    ('PostgreSQL supports full text search.'),
    ('BM25 ranks documents by relevance.');
CREATE INDEX documents_bm25 ON documents USING bm25 (vector bm25_ops)
WITH (limit = 100);

SELECT id, vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL'), 'documents_bm25') AS rank
FROM documents ORDER BY rank LIMIT 10;
```

The index needs document positions to recover term frequencies. `strip(tsvector)` and `array_to_tsvector` cannot supply them. Use the same analyzer for documents and queries. An integer token ID is not a lexeme; no automatic `bm25vector`-to-`tsvector` cast is provided.

An explicit `SET "bm25.limit" = 100` overrides the index's initial batch size; built-in defaults fall back to the index setting. Both defaults are 100, and explicit zero selects 100. Scans automatically continue for SQL `LIMIT`, `OFFSET`, and post-filtering; the batch setting never silently truncates results. Ordinary ordering includes zero-score nonmatches and NULLs. Use an explicit match predicate if those rows are unwanted. `bm25.prefilter` follows the same source-based precedence, including explicit false; volatile predicates stay in the executor.

Settings from `postgresql.conf`, `ALTER DATABASE`, `ALTER ROLE`, or client startup options also override index reloptions. `RESET` restores that configured default; it falls back to the index only when the GUC source returns to the built-in default.

## Schema access

A DBA can install into a schema chosen for the application:

```sql
CREATE SCHEMA search;
CREATE EXTENSION vchord_bm25 WITH SCHEMA search;
GRANT USAGE ON SCHEMA search TO app_user;
ALTER ROLE app_user SET search_path = public, search;
```

This is an alternative to installing into `public`; do not run both installations in one database. Grant table access separately. Function execution is granted to `PUBLIC` by PostgreSQL's default privileges; if your deployment revokes it, grant the required functions explicitly. Schema-qualified calls to `search.to_bm25query(...)` work without adding `search` to `search_path`, including after relocating the extension.

Both scalar scoring and native index scans require `SELECT` on the indexed table. An ordinary, non-partial single-column index also accepts `SELECT` on that column; expression and partial indexes require table-level access. Checks use the current role, including when scoring a supplied vector without reading rows in SQL. A view grant alone does not grant access to the underlying corpus.

Scores use global corpus statistics. When row-level security applies to the current role, 1.0.0 rejects both scoring and native scans to avoid exposing statistics about hidden rows. Owner and `BYPASSRLS` exemptions follow PostgreSQL rules; an ordinary owner is restricted under `FORCE ROW LEVEL SECURITY`. `row_security = off` does not bypass this restriction.

## Move existing data

`ALTER EXTENSION vchord_bm25 UPDATE TO '1.0.0'` from 0.3.0 deliberately raises an error before changing objects. It neither rewrites old indexes nor drops dependent application data.

1. Keep the old database and old binary available. Inventory `bm25vector` columns, indexes, views, functions, and tokenizer triggers; export source text and application data while the old datatype can still be read.
2. Install 1.0.0 into a separate PostgreSQL installation with its own library directory, or a separate container image, and create a new database. A separate data directory or port using the same library directory is not sufficient. Databases in the same installation share the extension library, so replacing the binary while any database still uses 0.3.x is unsafe.
3. Restore the source text, generate `tsvector` values, and rebuild all BM25 indexes. A binary copy of an old index or an ordinary `REINDEX` on a `bm25vector` column cannot migrate the API.
4. Update the constructor argument order, types, GUC names, and tokenizer triggers. Compare ranking quality and query results before switching the application.

The `pg_tokenizer` integer-array workflow remains documented for 0.3.x. For 1.0.0, use `to_tsvector` or [pg_tokenizer](/docs/tokenizer/) 1.0.0: `tokenizer_catalog.tokenize_to_tsvector(text, tokenizer)` keeps the same model with token IDs as lexemes, and `tokenizer_catalog.analyze_to_tsvector(text, analyzer)` uses a text analyzer's tokens (for example Jieba). Both are `STABLE`; store the result in a `tsvector` column, index that column, and build queries with the same function. Term frequencies now come from tsvector positions, so compare rankings before switching.

Statistics, maintenance thresholds, manual `bm25_maintain()`, and standby retry behavior are described in [Indexing & Maintenance](/docs/bm25/usage/indexing/#growing-segments-and-maintenance-in-100). Statistics include tombstones until compaction; active scans retain their preparation, but evicted scalar-only cache entries can be recollected during the execution. `work_mem` is a soft limit; scalar scoring is parallel restricted. Document weights are ignored, and long documents are subject to [PostgreSQL tsvector limits](https://www.postgresql.org/docs/18/textsearch-limitations.html); split long documents into chunks when these limits affect term frequencies.
