---
math: true
title: "Indexing & Maintenance"
description: "Create, configure, maintain, and inspect bm25 indexes in PostgreSQL."
weight: 10
icon: fa-solid fa-database
---

`vchord_bm25` provides the `bm25` index access method and the explicit `bm25_ops` operator class. The SQL handler is `bm25_amhandler` in 1.0.0 and `_bm25_amhandler` in 0.3.x.

## Creating a `bm25` Index

### Historical Releases (`v0.1` – `v0.3`, `bm25vector`) {#stable-releases-v01--v03-bm25vector}

```sql
CREATE INDEX documents_embedding_bm25
ON documents
USING bm25 (embedding bm25_ops);
```

### 1.0.0 (`tsvector`) {#next-gen-main-branch-tsvector}

In 1.0.0, `bm25_ops` operates on `tsvector` and supports index-level storage parameters (`options`, `limit`, and `prefilter`):

```sql
CREATE INDEX documents_vector_bm25
ON documents
USING bm25 (vector bm25_ops)
WITH (
    options = $$
    k1 = 1.2
    b = 0.75
    $$,
    limit = 100,
    prefilter = false
);
```

| Storage Parameter (`WITH (...)`) | Type | Default | Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `options` (`k1`) | `float` (in TOML) | `1.2` | `1.2` – `2.0` | Term frequency saturation parameter \(k_1\). Higher values increase the weight of repeated occurrences of a term within a document. |
| `options` (`b`) | `float` (in TOML) | `0.75` | `0.0` – `1.0` | Document length normalization parameter \(b\). `0.0` disables length normalization; `1.0` fully normalizes by document length relative to \(\text{avgdl}\). |
| `limit` | `int` | `100` | `0` – `65535` | Initial scan batch size; zero selects 100. Scans continue as needed for complete SQL results. |
| `prefilter` | `bool` | `false` | `true` / `false` | Default prefilter behavior stored on the index (can be overridden per session via `bm25.prefilter`). |
{.wide .expand}

You can dynamically update `limit` or `prefilter` on an existing index with `ALTER INDEX`:

```sql
ALTER INDEX documents_vector_bm25 SET (limit = 200, prefilter = true);
ALTER INDEX documents_vector_bm25 RESET (limit, prefilter);
```

## Automatic Tokenization Triggers (`v0.1` – `v0.3`)

When using `pg_tokenizer 1.0.0` with the historical `bm25vector` API, you can keep a tokenized column automatically synchronized on `INSERT` and `UPDATE`:

### Using a Custom Model Trigger (One-Step Helper)

`create_custom_model_tokenizer_and_trigger` creates a custom model, a tokenizer, backfills existing rows, and attaches an automatic `BEFORE INSERT OR UPDATE` trigger:

The helper accepts an optional seventh `filter` argument. It limits vocabulary training and embedding updates to rows whose trusted source-column predicate evaluates to `TRUE`; omit it or pass SQL `NULL` to retain whole-table behavior. See the [pg_tokenizer model notes](/docs/tokenizer/models/#filtering-a-corpus).

```sql
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'my_tokenizer',
    model_name     => 'my_model',
    text_analyzer_name => 'my_analyzer',
    table_name     => 'documents',
    source_column  => 'passage',
    target_column  => 'embedding'
);
```

### Using a Standard PL/pgSQL Trigger with Pretrained Models

If you use a pretrained model (such as `llmlingua2` or `bert_base_uncased`), create a standard trigger function:

```sql
CREATE OR REPLACE FUNCTION documents_tokenize_trigger()
RETURNS trigger AS $$
BEGIN
    NEW.embedding := tokenize(NEW.passage, 'my_tokenizer');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_documents_tokenize
BEFORE INSERT OR UPDATE OF passage ON documents
FOR EACH ROW
EXECUTE FUNCTION documents_tokenize_trigger();
```

## Growing segments and maintenance in 1.0.0

In 1.0.0, inserts append through a tail hint and are searchable immediately. Scans and scalar scoring share cached statistics within an executor execution. `work_mem` is a soft limit: active native scans and the eight most recently used queries retain their statistics above it; other entries are evicted in LRU order. Recollected entries can see corpus changes during the same statement. Terms share two immutable length-normalization tables per preparation, but growing-document scores still require memory proportional to the growing segment. Counts include physical non-NULL records, including tombstones until compaction removes them. Result generation skips tombstones immediately. WAND stays enabled with upper bounds adjusted for average-length drift. Scalar scoring is parallel restricted. These physical statistics are not an MVCC snapshot of the corpus.

`VACUUM`, including parallel VACUUM, can merge while readers and writers continue. `ANALYZE` alone does not rebuild. Maintenance uses the heap's normal `ShareUpdateExclusiveLock` and short page locks. Publication records a retirement horizon; a later pass recycles old pages only after older snapshots are gone. Cancelled or crashed output is reclaimed and the free-space map repaired on a later pass. Recycling advances the graveyard head and marks the retired page deleted in the same WAL record, so stale free-space hints cannot enable reuse before unlinking. Inserts wait for the tail page without holding jump, revalidate the generation, and acquire the tail lock conditionally; they retain jump while appending one document, including any relation extension.

Automatic merging requires growing records to reach `max(maintenance_min_rows, maintenance_scale_factor × sealed records)`, or tombstones to reach `maintenance_scale_factor × total records`. Defaults are 1000 rows and 0.1. Unchanged indexes are not rewritten. Set these reloptions with `ALTER INDEX`.

```sql
ALTER INDEX documents_vector_bm25 SET (maintenance_min_rows = 1000, maintenance_scale_factor = 0.1);
VACUUM documents;
SELECT bm25_maintain('documents_vector_bm25');
```

`bm25_maintain(regclass)` bypasses the thresholds and returns true when it publishes a merged segment. False means no work or an older generation still prevents another merge. It requires table ownership or, on PostgreSQL 17+, `MAINTAIN` privilege. It does not find dead heap tuples; use `VACUUM` for that. It holds the table's `ShareUpdateExclusiveLock` while maintenance runs.

There is one retirement slot. Long snapshots can postpone reclamation and the next merge, so growing-segment size has no hard bound. In an idle database the transaction horizon may also stop advancing. Tune table-level `autovacuum_vacuum_insert_threshold` and `autovacuum_vacuum_insert_scale_factor` for insert-heavy workloads. Freed pages are reused, not necessarily truncated; no fixed file-size multiplier is guaranteed. Standby readers receive SQLSTATE `40001` when they meet recycled pages or growing pages appended after a newer segment was published. Retry these queries. `hot_standby_feedback` prevents recycling conflicts at the cost of delaying reclamation; it does not prevent the newer-growing-page conflict. Tombstones never cancel standby queries: PostgreSQL resolves those conflicts when it replays the heap pruning that precedes them.


There is one sealed segment, and every merge rewrites it together with the growing records. Every non-ANALYZE VACUUM still scans the whole index and sealed document chain before its no-op decision; skipping only on a zero deletion count would miss insert-driven merges and crash/FSM repair. A large append or page I/O can still delay publication. Temporary build/merge files are outside PostgreSQL's `temp_file_limit` and `log_temp_files` accounting. VACUUM reports estimated index counts; CREATE INDEX, REINDEX and ANALYZE update catalog statistics.

`bm25query` stores a `regclass` OID. Plain `REINDEX` preserves it, but `REINDEX ... CONCURRENTLY` replaces it. Views, materialized views, rules and SQL-standard function bodies keep their old OID constants. Save the original DDL before reindexing, then recreate those definitions against the new qualified name; `CREATE OR REPLACE VIEW` and `CREATE OR REPLACE FUNCTION` work for ordinary views and functions. `pg_get_viewdef()` after reindexing may contain the dangling numeric OID and cannot recover the original binding. Text-body functions and prepared statements are reanalyzed.

An explicit `to_bm25query(query_vector, pg_catalog.to_regclass('public.documents_vector_bm25'))` resolves the qualified name at execution time and survives concurrent reindexing. It uses scalar sorting, retains the same SELECT/RLS checks, and creates no stored dependency on the index. Rename/drop can change its target; a missing name returns NULL. Existing OID-based definitions are not automatically repaired. Format-4 healthy indexes need no rebuild for the recycling/locking fixes; an already-reused graveyard page is rejected and requires REINDEX.


The `bm25_catalog.segment_growing_max_page_size` setting below belongs to 0.3.x and is not part of the 1.0.0 API.

## Segment Architecture: Growing vs. Sealed Segments (`v0.1` – `v0.3`)

Internally, `vchord_bm25` organizes index tuples into two segment states:

1. **Growing Segment**: Newly inserted tuples (`INSERT` / `UPDATE`) are appended to the growing segment for fast write throughput without re-compressing entire posting lists.
2. **Sealed Segment**: When the growing segment exceeds `bm25_catalog.segment_growing_max_page_size` pages (default `4096` pages, ~32 MB), it is sealed into an immutable, read-only segment with delta-bitpacked 128-document blocks, precomputed block-max upper bounds, and term document frequency statistics.

```sql
-- Adjust the growing segment seal threshold (in 8 KB pages, range 1..1000000)
SET bm25_catalog.segment_growing_max_page_size = 4096;
```

## Parallel Index Build & Progress Monitoring

Index creation supports PostgreSQL parallel maintenance workers and reports live build progress via `pg_stat_progress_create_index` across three phases:

1. `initializing`
2. `scanning table`
3. `writing index structures`

```sql
-- Speed up large index builds with parallel workers
SET max_parallel_maintenance_workers = 8;
SET maintenance_work_mem = '2GB';

-- Monitor build progress from another session
SELECT
    pid,
    phase,
    tuples_total,
    tuples_done,
    round(100.0 * tuples_done / nullif(tuples_total, 0), 2) AS pct_done
FROM pg_stat_progress_create_index;
```

## Inspecting Index Pages (`v0.3.0`)

Version `0.3.0` provides `bm25_page_inspect(index regclass, blkno int)` to inspect the internal metadata and page headers of a `bm25` index:

```sql
-- Inspect the metapage (block 0) of a bm25 index
SELECT bm25_page_inspect('documents_embedding_bm25', 0);
```

## Index Constraints & Limitations

- **Single-Column Only**: A `bm25` index can only be created on a single `bm25vector` (or `tsvector`) column. Multicolumn `bm25` indexes are not supported.
- **No Unlogged Tables**: `UNLOGGED` tables are not supported by the `bm25` access method (`ambuildempty` raises `Unlogged indexes are not supported`).
- **Forward Scan Direction Only**: `bm25` index scans only support forward (`ASC`) scan direction on `<&>`.
