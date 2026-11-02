---
math: true
title: "Querying & Scoring"
description: "Execute Top-K BM25 queries, interpret negative BM25 scores, and tune search limits."
weight: 20
---

## Basic Top-K Query Syntax

To run an index-accelerated Top-K BM25 search, use the `<&>` operator in the `ORDER BY` clause together with `to_bm25query`:

```sql
-- v0.1 – v0.3 (bm25vector + pg_tokenizer)
SELECT
    id,
    passage,
    embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL vector search', 'my_tokenizer')) AS raw_score,
    -(embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL vector search', 'my_tokenizer'))) AS bm25_score
FROM documents
ORDER BY raw_score ASC
LIMIT 10;
```

```sql
-- main branch (native tsvector)
SELECT
    id,
    passage,
    -(vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL vector search'), 'documents_bm25_idx')) AS bm25_score
FROM documents
ORDER BY vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL vector search'), 'documents_bm25_idx') ASC
LIMIT 10;
```

## Why `to_bm25query` Requires the Index Name

Unlike vector distance operators (where the distance between two vectors depends only on the two vectors themselves), the **BM25 score of a document depends on corpus-wide statistics stored inside the BM25 index**:

- Total number of documents in the corpus (\(N\))
- Average document length across the corpus (\(\text{avgdl}\))
- Document frequency of each query token (\(n(q_i)\))

Passing the index (`'documents_embedding_bm25'::regclass`) into `to_bm25query(...)` allows the standalone scoring function (`search_bm25query` / `_bm25_evaluate`) to read corpus statistics from the index even when PostgreSQL evaluates `<&>` in the `SELECT` projection list or during a brute-force sequential scan.

## Understanding Negative BM25 Scores

By design, `<&>` returns **negative** BM25 scores:

$$\text{score}_{\text{operator}}(D, Q) = -\text{BM25}(D, Q) \le 0$$

- PostgreSQL's index access method API (`amcanorderbyop`) only supports `ORDER BY <operator> ASC` for index-ordered scans.
- Because higher BM25 scores mean better relevance, returning $-\text{BM25}(D, Q)$ places the most relevant documents first when sorted in default ascending (`ASC`) order.
- Never use `ORDER BY embedding <&> to_bm25query(...) DESC`—PostgreSQL cannot use the forward `bm25` index scan for `DESC` ordering and will either fall back to a full scan or raise a scan direction error.

## Tuning `bm25_limit` vs SQL `LIMIT`

Because Block-WeakAnd maintains a bounded Top-K min-heap during the index scan to aggressively prune non-competitive posting blocks, the index scanner needs to know \(K\) (the maximum number of candidates to collect) when the scan begins.

### In `v0.1.0` – `v0.3.0`: `bm25_catalog.bm25_limit`

The GUC `bm25_catalog.bm25_limit` (default `100`, range `-1` to `65535`) controls the maximum number of Top-K documents returned by the `bm25` index scan:

```sql
-- Default is 100. Increase it if your SQL query requests LIMIT 500:
SET bm25_catalog.bm25_limit = 500;

SELECT id, passage
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('database', 'my_tokenizer'))
LIMIT 500;
```

Special values of `bm25_catalog.bm25_limit`:

| Value | Behavior |
| :--- | :--- |
| `1` – `65535` | Uses Block-WeakAnd to compute and return up to `bm25_limit` top-scoring documents (default `100`). |
| `0` | Immediately returns `0` rows. |
| `-1` | Disables Block-WeakAnd Top-K pruning and performs a full brute-force scan over all matching postings in the index. |

### In `main`: `bm25.limit` and Index `limit` Reloption

In the `main` branch, the effective limit is determined in priority order:

1. An explicitly set session GUC `bm25.limit`, including zero.
2. Otherwise, the index storage parameter `WITH (limit = ...)`.

Both defaults are zero; set a positive limit before searching. Explicit zero errors and does not fall back. `RESET "bm25.limit"` restores the index default.

```sql
SET "bm25.limit" = 100;
```

Settings from `postgresql.conf`, `ALTER DATABASE`, `ALTER ROLE`, or client startup options also override index reloptions. `RESET` restores that configured default; it falls back to the index only when the GUC source returns to the built-in default.

> [!WARNING]
> Always ensure `bm25_catalog.bm25_limit` (or `bm25.limit`) is **greater than or equal to** the `LIMIT` in your SQL query. If your SQL query specifies `LIMIT 200` while `bm25_limit` is `100`, the index scan will stop after yielding 100 rows.

## Verifying the Query Plan with `EXPLAIN`

Use `EXPLAIN (ANALYZE, BUFFERS)` to confirm that PostgreSQL is using `Index Scan using ... on documents`:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL', 'my_tokenizer'))
LIMIT 10;
```

To force a sequential scan + exact brute-force evaluation (useful for verifying recall or debugging), disable the index scan temporarily:

```sql
-- v0.1 – v0.3
SET bm25_catalog.enable_index = false;

-- main branch
SET bm25.enable_scan = false;
```
