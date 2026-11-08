---
title: "vchord_bm25 1.0.0: First Release Under PGSTY"
date: 2026-11-03
description: "vchord_bm25 1.0.0, the first PGSTY release, replaces custom bm25vector columns with native PostgreSQL tsvector indexing, adds continuing WAND scans, concurrent ShareUpdateExclusiveLock maintenance, and corpus-level ACL/RLS checks."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-bm25-1.0.0.png"
tags:
  - "release"
  - "vchord_bm25"
  - "bm25"
  - "full-text-search"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/untagged-e766a17dbd8365cfa7be"
upstream_source: ""
upstream_link: ""
---

**vchord_bm25 1.0.0** is the first release maintained by PGSTY in [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) under the AGPL-3.0 license. It replaces the custom `bm25vector` data type and fixed `bm25_catalog` schema from 0.3.x with native PostgreSQL `tsvector` indexing, reworks the Block-WeakAnd (WAND) scan and storage engine for continuing scans and concurrent `VACUUM`, and enforces table privileges and Row-Level Security (RLS) across both indexed scans and scalar scoring.

> [!NOTE] Extension & Release Links
> - **GitHub Release draft**: [`pgsty/vchord_bm25 1.0.0`](https://github.com/pgsty/vchord_bm25/releases/tag/untagged-e766a17dbd8365cfa7be) · [Source Repository](https://github.com/pgsty/vchord_bm25)
> - **Extension Catalog**: [pgext.cloud (`vchord_bm25`)](https://pgext.cloud/e/vchord_bm25) · [Pigsty Extension Page (`pigsty.io`)](https://pigsty.io/ext/e/vchord_bm25/)
> - **Binary Packages**: [RPM / DEB Repository Setup](/download/) · [SBOM & License Inventory](/docs/about/sbom/)

The 1.0.0 GitHub entry remains a draft and requires repository access. For the published release, see [vchord_bm25 1.1.0](/blog/release/vchord-bm25-1.1.0/).

## Changes in 1.0.0 {#changes}

| Area | Change |
| :--- | :--- |
| Native `tsvector` API | Indexes standard PostgreSQL `tsvector` columns with `USING bm25 (... bm25_ops)`. `to_bm25query(tsvector, regclass)` builds queries, and `<&>` returns negative `double precision` BM25 scores (`+0.0` for zero scores). |
| Relocatable schema | Extension objects install into the target schema (`public` by default) and support `ALTER EXTENSION vchord_bm25 SET SCHEMA`. The fixed `bm25_catalog` schema is no longer required. |
| Continuing WAND scans | `bm25.limit` and the index `limit` reloption (`0..=65535`, default `100`, `0` selects `100`) set the initial WAND top-K batch size rather than a hard result cap; scans continue through matching, zero-score, and `NULL` rows as needed. |
| Shared statistics cache | Prepared corpus statistics and growing-segment scores are cached per `(index, query)` within `work_mem` and shared between indexed scans and scalar `<&>` evaluations (`PARALLEL RESTRICTED`). `NULL` rows are excluded from document count, and WAND upper bounds adjust for `avgdl` drift. |
| Concurrent maintenance | Format 4 storage uses generation stamps, a growing segment, and one crash-resumable retired generation. `VACUUM` and `bm25_maintain(regclass)` merge growing tuples under `ShareUpdateExclusiveLock` using PostgreSQL's `GlobalVis` horizon without taking `AccessExclusiveLock` or allocating an XID. `ANALYZE` is a no-op. |
| Standby replay | `VACUUM` tombstones only already-pruned heap TIDs, raising no false standby conflicts; only page recycling raises SQLSTATE `40001` (`serialization_failure`) if an older standby query is still reading a retired generation. |
| Corpus permissions & RLS | Both indexed scans and scalar `<&>` check current-role table `SELECT` (or column `SELECT` for simple single-column non-partial indexes) and reject queries when RLS policies apply (`0A000`), preventing corpus-statistic leaks. Scalar scoring locks the heap before the index. |
| Build & platform support | Upgraded to `pgrx 0.19.3` for PostgreSQL 14–18 on Linux x86_64 and aarch64, with runtime SIMD dispatch (`AVX512` / `AVX2` / `NEON`) and responsive query cancellation outside page locks. |
{.wide .expand}

## Native `tsvector` indexing and relocatable schema {#native-tsvector}

In `vchord_bm25 1.0.0`, documents are stored as standard PostgreSQL `tsvector` values with lexeme positions (`1..=16383`, up to 256 positions per lexeme). Each position entry counts as one occurrence of that lexeme when computing term frequency (`tf`) and document length (`dl`); lexemes without positions are ignored by BM25 scoring.

Because `vchord_bm25` operates directly on `tsvector`, you can populate indexed columns with PostgreSQL's built-in `to_tsvector(regconfig, text)` or with [`pg_tokenizer 1.0.0`](/blog/release/pg-tokenizer-1.0.0/) (`analyze_to_tsvector` for string lexemes or `tokenize_to_tsvector` for model token IDs):

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

CREATE TABLE documents (
    id integer PRIMARY KEY,
    passage text NOT NULL,
    doc tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);

INSERT INTO documents (id, passage) VALUES
    (1, 'PostgreSQL full-text search with Block-WeakAnd BM25 ranking'),
    (2, 'Hybrid retrieval combining VectorChord and vchord_bm25 in PostgreSQL'),
    (3, 'Concurrent VACUUM maintenance for growing BM25 segments');

CREATE INDEX documents_doc_bm25_idx
    ON documents USING bm25 (doc bm25_ops)
    WITH (
        options = $$
        k1 = 1.2
        b = 0.75
        $$,
        limit = 100
    );

SELECT id, doc <&> to_bm25query(to_tsvector('english', 'postgresql bm25'), 'documents_doc_bm25_idx') AS score
FROM documents
ORDER BY score
LIMIT 2;
```

Key API changes in `1.0.0`:

- **Query constructor order**: `to_bm25query(vector tsvector, index regclass)` takes the query `tsvector` first and the index `regclass` second. Both arguments are `STRICT`, so a `NULL` query vector or index returns `NULL`.
- **Negative BM25 scores**: `<&>` returns negative `double precision` (`float8`) scores so standard ascending `ORDER BY` scans return the best matches first. Zero scores are normalized to `+0.0`.
- **Relocatable extension objects**: All types, functions, operators, and the `bm25` access method live in the extension's target schema (`public` by default) and can be moved with `ALTER EXTENSION vchord_bm25 SET SCHEMA <schema>;`.

See the [BM25 indexing](/docs/bm25/usage/indexing/) and [BM25 querying](/docs/bm25/usage/querying/) guides for complete examples, including multilingual tokenization with `pg_tokenizer`.

## Continuing WAND scans, batch sizing, and shared statistics {#scans-and-caching}

In 0.3.x, `bm25_catalog.bm25_limit` acted as a hard cap on how many candidates a BM25 index scan could yield. When a query combined `ORDER BY ... <&> ...` with a selective `WHERE` filter, post-filtering could discard most of the top candidates and return fewer rows than requested by `LIMIT`.

In `1.0.0`, `bm25.limit` (and the per-index `limit` storage option) sets the **initial WAND top-K batch size**:

- **Continuing execution**: If the executor still needs rows after consuming the initial WAND batch (for example, because a `WHERE` filter rejected earlier rows or the query requests a larger `LIMIT` / `OFFSET`), the scan continues through the remaining matching documents, zero-score documents, and `NULL` rows.
- **Range and precedence**: Both `bm25.limit` and the index `limit` reloption accept `0..=65535` (default `100`); an explicit `0` selects the default batch size of `100`. Any non-built-in GUC setting (`SET`, session, user, database, or `postgresql.conf`) overrides the index's storage option, including explicit `0` or `false` (`bm25.enable_scan` / `bm25.prefilter`). Double-quote `"bm25.limit"` in `SET` / `SHOW` / `RESET` statements because `limit` is a SQL keyword.
- **Shared statistics and growing-segment cache**: Corpus statistics (`N`, `avgdl`, and per-term `df`) along with growing-segment scores are cached per `(index, query)` in backend memory bounded by `work_mem` (with oldest-first eviction) and shared within an executor run between the index scan and scalar `<&>` evaluation in `SELECT` lists or `WHERE` clauses. Physical statistics include non-`NULL` records (including tombstones until compaction removes them, while result generation skips tombstones immediately). Because the cache lives in backend state, `<&>` is marked `PARALLEL RESTRICTED`.
- **Bounds under concurrent writes**: When unsealed growing-segment rows shift the live average document length (`avgdl`) relative to the sealed segment, WAND upper bounds adjust accordingly so candidates are not pruned early.
- **Planner and cancellation**: `amcostestimate` accepts single-key `ORDER BY` queries, recognizes `to_bm25query(..., const regclass)` in generic/prepared plans, and charges conservative index startup costs using PostgreSQL's standard cost parameters. Search loops copy block jump metadata and release page locks before invoking filter predicates, checking for query cancellation between blocks so statement timeouts and `pg_cancel_backend` take effect immediately.

## Concurrent maintenance, `VACUUM`, and standby replay {#maintenance-and-vacuum}

Inserts and updates append through a tail hint into a **growing segment** and are searchable immediately without rewriting compressed posting lists on every transaction. `vchord_bm25 1.0.0` introduces on-disk format **4** so segment merging and page recycling work alongside concurrent readers and writers, parallel `VACUUM`, crash recovery, and physical replication standbys:

- **Automatic and manual merge thresholds**: Each BM25 index exposes `maintenance_min_rows` (default `1000`, range `0..=2147483647`) and `maintenance_scale_factor` (default `0.1`, range `0.0..=1.0`). `VACUUM` merges the growing segment and compacts deleted tuples when growing records reach `max(maintenance_min_rows, maintenance_scale_factor × sealed_records)` or when tombstones reach `maintenance_scale_factor × total_records`. Calling `SELECT bm25_maintain('documents_doc_bm25_idx'::regclass);` bypasses the size thresholds and returns `true` when it publishes a merged segment (or `false` when there is no work or an older retired generation is still awaiting reclamation; requires table ownership or, on PostgreSQL 17+, `MAINTAIN` privilege).
- **No `AccessExclusiveLock` or XID assignment**: Both `VACUUM` and `bm25_maintain(regclass)` run under the heap's `ShareUpdateExclusiveLock` and use PostgreSQL's `GlobalVis` horizon to retire superseded pages. Maintenance never takes `AccessExclusiveLock` on the index and never allocates a transaction ID, so it runs safely inside parallel `VACUUM`. Running `ANALYZE` alone returns immediately without rebuilding the index.
- **Crash-resumable retired generation**: When a merge finishes while older snapshots may still be scanning the previous sealed generation, the index retains one retired generation until all older snapshots advance. If another merge is requested before that retired generation can be recycled, the merge is deferred cleanly without blocking readers or writers.
- **Physical standby conflict resolution**: Because `VACUUM` only tombstones heap TIDs that have already been pruned on the heap, replaying the earlier heap prune record on a physical standby already resolves snapshot conflicts (matching PostgreSQL's `nbtree` behavior). Standby queries are only canceled with SQLSTATE `40001` (`serialization_failure`) if page recycling reclaims a retired index generation that a long-running standby query is still reading.

## Corpus permissions and Row-Level Security (RLS) {#permissions-and-rls}

BM25 scores depend on corpus-wide statistics (`N`, `avgdl`, and term document frequencies `df`) stored inside the index. Evaluating `<&>` without checking privileges on the underlying table would allow an unprivileged role—or a role restricted by Row-Level Security—to probe global term frequencies across rows they cannot read.

`vchord_bm25 1.0.0` enforces privilege and RLS checks on both indexed scans and standalone scalar `<&>` evaluations:

1. **Table and column `SELECT` checks**: Before reading index statistics, `vchord_bm25` verifies that the current role holds `SELECT` on the indexed table (or column-level `SELECT` on the indexed column for an ordinary non-partial single-column index; expression and partial indexes require table-level `SELECT`). Checks use the current role even when scoring a supplied vector without reading table rows in SQL, and a view grant alone does not grant access to the underlying corpus.
2. **Row-Level Security enforcement**: When row-level security applies to the current role on the indexed table, `vchord_bm25` rejects both scalar scoring and native scans with SQLSTATE `0A000` (`feature_not_supported`) to avoid exposing statistics about hidden rows. Owner and `BYPASSRLS` exemptions follow PostgreSQL rules (an ordinary owner is restricted under `FORCE ROW LEVEL SECURITY`), and `row_security = off` does not bypass this restriction.
3. **Lock ordering**: Scalar `<&>` evaluations lock the heap relation before locking the BM25 index relation, matching PostgreSQL's standard table-then-index lock order.

## Migrating from 0.3.x and packages {#migration-and-packages}

Because `vchord_bm25 1.0.0` changes the document data type, catalog schema, query constructor order, and on-disk index format, the `0.3.0 -> 1.0.0` upgrade script intentionally aborts `ALTER EXTENSION vchord_bm25 UPDATE` with an error message before modifying any database objects.

| Feature | `vchord_bm25 0.3.x` | `vchord_bm25 1.0.0` |
| :--- | :--- | :--- |
| Extension schema | Fixed `bm25_catalog` (`relocatable = false`) | Target schema (`public` by default, `relocatable = true`) |
| Document column type | `bm25_catalog.bm25vector` (`token_id:freq` array) | Native PostgreSQL `pg_catalog.tsvector` (with lexeme positions) |
| Query constructor | `to_bm25query(regclass, bm25vector)` | `to_bm25query(tsvector, regclass)` |
| Score return type | `real` (`float4`) | `double precision` (`float8`, `+0.0` for zero scores) |
| GUCs | `bm25_catalog.bm25_limit`, `bm25_catalog.enable_index` | `"bm25.limit"`, `bm25.enable_scan`, `bm25.prefilter` |
| Maintenance helper | `REINDEX` required to seal growing segments on demand | `bm25_maintain(regclass)` + automatic `VACUUM` thresholds |
{.wide .expand}

To migrate an existing 0.3.x deployment, retain the source text columns, install the `1.0.0` packages in a separate PostgreSQL installation or container image with its own library directory, populate native `tsvector` columns, and build new `USING bm25 (doc bm25_ops)` indexes. Step-by-step instructions are in the [BM25 Migration Guide](/docs/bm25/reference/migration/).

Native RPM and DEB packages (`1.0.0-1PIGSTY` / `1.0.0-1PGSTY`) for PostgreSQL **14–18** across 16 Linux distributions on `x86_64` and `aarch64` are available on the [Download page](/download/). See the [BM25 SQL Reference](/docs/bm25/reference/sql/), [GUC Reference](/docs/bm25/reference/gucs/), and [SBOM page](/docs/about/sbom/) for complete operational details.
