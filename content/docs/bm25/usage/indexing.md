---
math: true
title: "Indexing & Maintenance"
description: "Create, configure, maintain, and inspect bm25 indexes in PostgreSQL."
weight: 10
icon: fa-solid fa-database
---

`vchord_bm25` provides the `bm25` index access method and the explicit `bm25_ops` operator class. The SQL handler is `bm25_amhandler` in 0.4.0 and `_bm25_amhandler` in 0.3.x.

## Creating a `bm25` Index

### Stable Releases (`v0.1` – `v0.3`, `bm25vector`)

```sql
CREATE INDEX documents_embedding_bm25
ON documents
USING bm25 (embedding bm25_ops);
```

### Next-Gen `main` Branch (`tsvector`)

In the `main` branch, `bm25_ops` operates on `tsvector` and supports index-level storage parameters (`options`, `limit`, and `prefilter`):

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
| `limit` | `int` | `0` | `0` – `65535` | Default Top-K search limit stored on the index (used when session GUC `bm25.limit` has its default source, after `RESET`). |
| `prefilter` | `bool` | `false` | `true` / `false` | Default prefilter behavior stored on the index (can be overridden per session via `bm25.prefilter`). |
{.wide .expand}

You can dynamically update `limit` or `prefilter` on an existing index with `ALTER INDEX`:

```sql
ALTER INDEX documents_vector_bm25 SET (limit = 200, prefilter = true);
ALTER INDEX documents_vector_bm25 RESET (limit, prefilter);
```

## Automatic Tokenization Triggers (`v0.1` – `v0.3`)

When using `pg_tokenizer 0.2.0` with the historical `bm25vector` API, you can keep a tokenized column automatically synchronized on `INSERT` and `UPDATE`:

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
