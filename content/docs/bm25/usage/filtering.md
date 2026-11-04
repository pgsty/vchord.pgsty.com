---
math: true
title: "Filtered Search & Prefiltering"
description: "Combine SQL WHERE clauses with BM25 Top-K ranking using post-filtering, pre-filtering, and partial indexes."
weight: 30
icon: fa-solid fa-filter
---

The examples below use the **1.0.0 native `tsvector` API**. Combine BM25 ranking with structured filters such as category, tenant, or date ranges. Use the same text search configuration for documents and queries.

## 1. Post-Filtering vs. Pre-Filtering

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY vector <&> to_bm25query(
    to_tsvector('english', 'PostgreSQL BM25'), 'documents_bm25_idx')
LIMIT 10;
```

### Post-Filtering (`bm25.prefilter = false`) {#post-filtering-enable_prefilter--false}

The BM25 index supplies ranked candidates, and PostgreSQL applies the `WHERE` predicate. If the initial batch contains fewer than 10 qualifying rows, the scan continues in growing batches until the SQL limit is satisfied or the input is exhausted.

`bm25.limit` and the index's `limit` option control the **initial batch size**, not the result count. Both default to 100; zero also selects 100. A query is no longer limited to matches found in the first 100 candidates.

### Pre-Filtering (`bm25.prefilter = true`) {#pre-filtering-enable_prefilter--true}

Pre-filtering checks visibility and supported query predicates before admitting candidates into the Top-K heap. Rejected candidates do not raise the pruning threshold. This can reduce wasted ranking work for selective filters, at the cost of heap checks during ranking. Volatile predicates remain in the executor.

Both modes support continuing scans in 1.0.0. Choose between them by measuring your workload; pre-filtering does not eliminate all work on irrelevant postings.

### Enabling Pre-Filtering

```sql
-- Override the index default for this session:
SET bm25.prefilter = true;

-- Or set the index default:
ALTER INDEX documents_bm25_idx SET (prefilter = true);
```

An explicit GUC setting, including `false`, overrides the index option. `RESET bm25.prefilter` restores the configured default; the index option applies only when the GUC source is the built-in default. See [GUC precedence](/docs/bm25/reference/gucs/#session-guc-parameters-main).

### Historical 0.1–0.3 Behavior

Older releases use `bm25_catalog.bm25_limit` as a candidate cap. With post-filtering, a batch of 100 candidates containing only 3 qualifying rows can return just 3 rows despite more qualifying documents in the table. Prefiltering is available from 0.2.2 via `bm25_catalog.enable_prefilter`. These settings and the candidate-cap behavior do not apply to 1.0.0.

## 2. Partial BM25 Indexes for High-Selectivity Partition Keys

For a fixed subset such as published documents, use a partial index:

```sql
CREATE INDEX documents_published_bm25
ON documents
USING bm25 (vector bm25_ops)
WHERE status = 'published';
```

Reference that same index in `to_bm25query` and include a `WHERE` condition that implies its predicate:

```sql
SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY vector <&> to_bm25query(
    to_tsvector('english', 'PostgreSQL BM25'), 'documents_published_bm25')
LIMIT 10;
```

A partial index has its own corpus statistics, so scores can differ from an index over the full table. Statistics include physical records and tombstones until compaction; see [maintenance](/docs/bm25/usage/indexing/#growing-segments-and-maintenance-in-100).

## Choosing the Right Filtering Strategy

| Workload | Starting Point | Tradeoff |
| :--- | :--- | :--- |
| Most rows pass the filter | Post-filtering | Avoids predicate checks inside the ranking loop; continues scanning when needed. |
| Few rows pass the filter | Pre-filtering | Keeps rejected rows out of the Top-K heap, but adds heap checks during ranking. |
| Fixed tenant or status subset | Partial index or table partitioning | Smaller corpus and independent statistics; queries must target the appropriate index. |
{.wide .expand}

SQL filters do not bypass the [permission and RLS restrictions](/docs/bm25/reference/migration/#schema-access). When RLS applies to the current role, 1.0.0 rejects BM25 scoring and native index scans.
