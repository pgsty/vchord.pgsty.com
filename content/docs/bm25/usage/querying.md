---
title: "Querying"
linkTitle: "Querying"
description: "Write ranked BM25 queries, read their scores, understand how an index scan runs in batches, size bm25.limit, and keep the index in the plan."
weight: 20
icon: fa-solid fa-ranking-star
aliases:
  - "/docs/bm25/usage/algorithms/"
---

A ranked query names the index whose statistics define the score, orders by the `<&>` operator, and limits the result. This page explains how such a query runs, so you can predict its cost, size its batches, and make PostgreSQL plan it the way you expect.

## Write a ranked query {#query}

```sql
SELECT id, passage
FROM documents
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25')
LIMIT 10;
```

PostgreSQL uses the bm25 index for this query when:

- `ORDER BY` is the indexed column or expression `<&>` a `to_bm25query(...)`, ascending, and it is the only sort key.
- The second argument of `to_bm25query` is a constant naming that same index. A parameter, a `to_regclass()` lookup, or a `bm25query` parameter cannot be matched to an index at plan time; PostgreSQL then scores every row and sorts.
- The query has a `LIMIT`, so that ranking only the top rows pays off.

The index name is part of the query because a BM25 score depends on statistics of the whole corpus: the number of documents, their average length, and how many contain each query term. Those statistics live in the index. The same `<&>` expression in a `SELECT` list or `WHERE` clause computes the same score for any row, from the same statistics.

## Scores {#scores}

`<&>` returns the BM25 score negated, as `double precision`, because PostgreSQL index scans return rows in ascending order. The most relevant row has the most negative score. To show positive scores, negate the expression in the select list: `-(terms <&> to_bm25query(...)) AS score`.

A row matches when it contains any of the query terms; rows with more of them, and with rarer ones, score higher. Rows that contain none score `0` and come after all matches, and rows whose `tsvector` is `NULL` come last. When `LIMIT` exceeds the number of matches, those rows fill the rest of the result. To return only matching rows, filter in an outer query, which keeps the index scan inside:

```sql
SELECT id, -score AS relevance
FROM (
    SELECT id, terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25') AS score
    FROM documents
    ORDER BY score
    LIMIT 10
) AS ranked
WHERE score < 0;
```

To require every query term, add `WHERE terms @@ plainto_tsquery('english', 'full text search')`. It is an ordinary filter, handled as described in [Filtering](/docs/bm25/usage/filtering/).

Each distinct term in the query counts once, and weights set with `setweight` are ignored. The [score definition](/docs/bm25/reference/sql/#score) gives the formula.

## How a ranked query runs {#how-a-query-runs}

1. **Prepare.** The scan reads the index statistics and every row of the growing segment, the rows not yet merged by `VACUUM`. Scores then reflect every indexed row, merged or not.
1. **Rank a batch.** Block-WeakAnd walks the posting lists of the query terms. Each list is stored in blocks of 128 documents, and each block records the highest score any of its documents can contribute. A block that cannot beat the current k-th best score is skipped without decoding its documents. The batch size k is [`bm25.limit`](/docs/bm25/reference/gucs/#field-bm25-limit), 100 by default.
1. **Continue if needed.** PostgreSQL consumes the batch. If it needs more rows, because `LIMIT` plus `OFFSET` is larger than the batch or because the `WHERE` clause or row visibility removed rows, the scan ranks the next batch, twice as large, starting after the last row returned. Each new batch walks the posting lists again.
{.steps}

This explains the cost of a query:

- A small k raises the score threshold early, so more blocks are skipped. Queries with a small `LIMIT` are the cheap ones.
- Rare terms have short posting lists. A query made only of very common terms reads more.
- A large growing segment slows every query, because step 1 reads all of it. [Indexing](/docs/bm25/usage/indexing/#maintenance) explains how to keep it small.
- Results are complete. The scan keeps going until the query has its rows or every row has been returned, whatever `bm25.limit` is.

## Size the batch {#batch-size}

`bm25.limit` trades the cost of the first batch against the chance of needing a second one:

- The default of 100 suits queries with `LIMIT` up to 100 and few rows removed by filters. They finish in one batch.
- For larger pages or deep `OFFSET`, set it to at least `LIMIT + OFFSET`.
- When a `WHERE` clause keeps only a fraction of rows, either raise it to about `LIMIT` divided by that fraction, or turn on [prefiltering](/docs/bm25/usage/filtering/#prefilter).
- A larger batch skips fewer blocks, so do not set it far above what queries consume.

To tune it:

1. Run a typical query with `EXPLAIN (ANALYZE, BUFFERS)` and note the execution time and shared buffers.
1. Try other values in the session. The name must be quoted, because `LIMIT` is a reserved word:

   ```sql
   SET "bm25.limit" = 200;
   ```

1. Store the best value on the index, so every session gets it:

   ```sql
   ALTER INDEX documents_bm25 SET (limit = 200);
   ```

   The index value applies only while `bm25.limit` is not set anywhere else; see [precedence](/docs/bm25/reference/gucs/#precedence).
{.steps}

## Prepared statements {#prepared-statements}

Keep the index name a literal and pass only the search text as a parameter. The planner can then match the query to the index even in a generic plan:

```sql
PREPARE search_docs(text) AS
SELECT id FROM documents
ORDER BY terms <&> to_bm25query(to_tsvector('english', $1), 'documents_bm25')
LIMIT 10;

EXECUTE search_docs('full text search');
```

## Check the plan {#explain}

`EXPLAIN` shows `Index Scan using documents_bm25 on documents` with an `Order By` line for the `<&>` expression. A `Sort` above a `Seq Scan` or `Bitmap Heap Scan` means PostgreSQL is scoring rows one by one. Check the rules in [Write a ranked query](#query) first. If they hold, PostgreSQL chose another plan because it estimated that plan to be cheaper, for example a B-tree index on a selective filter followed by a sort; compare both with `EXPLAIN ANALYZE`.

[`SET bm25.enable_scan = off`](/docs/bm25/reference/gucs/#field-bm25-enable_scan) makes PostgreSQL score every row and sort. The scores are identical, which makes it a reference for testing.

## Result order {#result-order}

Rows come back in exact BM25 score order; unlike vector search, nothing is approximated. Rows with equal scores come back in the index's internal order, which can change after a merge or rebuild. Adding a second sort key such as `id` to `ORDER BY` stops PostgreSQL from using the index. For a stable order, overfetch and sort again in an outer query:

```sql
SELECT id, score
FROM (
    SELECT id, terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25') AS score
    FROM documents
    ORDER BY score
    LIMIT 20
) AS ranked
ORDER BY score, id
LIMIT 10;
```
