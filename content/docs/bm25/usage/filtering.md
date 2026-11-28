---
title: "Filtering"
linkTitle: "Filtering"
description: "Combine BM25 ranking with WHERE conditions: how filters are applied, when to prefilter, partial indexes for fixed subsets, privileges, and row-level security."
weight: 30
icon: fa-solid fa-filter
---

Most searches rank within a condition: a tenant, a category, a date range. This page shows how a `WHERE` clause interacts with the batched index scan, when to switch to prefiltering, and how partial indexes and row-level security change the statistics behind a score.

## Filter with WHERE {#where}

Add the condition as usual:

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25')
LIMIT 10;
```

The filter decides which rows are returned, not how they score: scores still come from the statistics of the whole index. To score within a subset, index only that subset with a [partial index](#partial-indexes).

## Post-filtering {#post-filter}

By default the index ranks a batch of rows, PostgreSQL drops the rows that fail the `WHERE` clause, and if fewer than `LIMIT` remain, the scan ranks another batch twice as large (see [How a ranked query runs](/docs/bm25/usage/querying/#how-a-query-runs)). The result is always complete, but the cost grows as the filter gets more selective: if 1% of rows pass, `LIMIT 10` needs about 1,000 ranked rows, four batches starting from the default of 100, each walking the posting lists again.

## Prefiltering {#prefilter}

With prefiltering on ([`bm25.prefilter`](/docs/bm25/reference/gucs/#field-bm25-prefilter)), the index checks each candidate's visibility and the `WHERE` clause before the candidate can take a place in the batch. Rows that fail never occupy a slot, so the first batch is usually enough. The price is one table row read for every candidate that could enter the batch.

```sql
SET bm25.prefilter = on;
```

| The filter keeps | Start with |
| --- | --- |
| Most rows | Post-filtering, the default |
| A small fraction of rows | Prefiltering |
| A fixed subset you search often | A [partial index](#partial-indexes) on that subset |

To decide, run the query with `EXPLAIN (ANALYZE, BUFFERS)` with prefiltering off and on, keep the faster setting, and store it on the index so every session gets it:

```sql
ALTER INDEX documents_bm25 SET (prefilter = on);
```

The index setting applies only while `bm25.prefilter` is not set anywhere else; see [precedence](/docs/bm25/reference/gucs/#precedence).

Prefiltering is skipped, and the query is filtered after ranking with the same result, when:

- the table has row-level security enabled;
- the `WHERE` clause calls a volatile function;
- the query reads through a security-barrier view, locks rows with `FOR UPDATE` or `FOR SHARE`, or contains a data-modifying `WITH`;
- a subquery in the `WHERE` clause does more than plain table scans, B-tree index scans, and `count(*)`.

With a selective condition on a B-tree-indexed column, PostgreSQL may also skip the bm25 index altogether: it fetches the few matching rows, scores them, and sorts. That is often the cheapest plan; `EXPLAIN` shows which one it chose.

## Partial indexes {#partial-indexes}

A partial index covers one subset and keeps statistics for that subset only:

```sql
CREATE INDEX documents_published_bm25 ON documents
USING bm25 (terms bm25_ops)
WHERE status = 'published';

SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_published_bm25')
LIMIT 10;
```

The query's `WHERE` clause must imply the index predicate, and `to_bm25query` must name the partial index. Scores differ from those of a full-table index, because document counts and term frequencies come from the subset. For many subsets, such as one per tenant, partitioning the table gives each partition its own index; see [Limits](/docs/bm25/usage/indexing/#limits) for how to query them.

## Privileges and row-level security {#access-control}

A BM25 score reveals statistics about the whole index: how many documents there are, their average length, and how many contain each term, including rows the caller cannot read. Scoring is therefore guarded beyond what the `SELECT` itself checks.

- **Privileges.** The role that scores needs `SELECT` on the table, or column `SELECT` on the indexed column, the columns of an index expression or partial-index predicate, and `EXECUTE` on the functions they use. A grant on a view is not enough: the role querying the view needs these privileges on the table too. Otherwise scoring fails with `permission denied for table documents`.
- **Row-level security.** When a row-level security policy applies to the current role, scoring fails with `bm25 cannot expose global corpus statistics under row-level security`. The table owner (unless the table has `FORCE ROW LEVEL SECURITY`) and roles with `BYPASSRLS` are exempt. Setting `row_security = off` does not help.
- **Opting in.** The index owner can allow scoring under row-level security with [`shared_corpus_stats`](/docs/bm25/reference/gucs/#field-shared_corpus_stats):

  ```sql
  ALTER INDEX documents_bm25 SET (shared_corpus_stats = on);
  ```

  Policies still decide which rows are returned, but scores reflect how common each term is across every row, so a tenant can learn something about other tenants' vocabulary. Prefiltering stays off on tables with row-level security.

To score each tenant with its own statistics and no shared information, give each tenant a partial index or a partition.
