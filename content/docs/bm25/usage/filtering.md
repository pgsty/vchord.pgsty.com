---
math: true
title: "Filtered Search & Prefiltering"
description: "Combine SQL WHERE clauses with BM25 Top-K ranking using post-filtering, pre-filtering, and partial indexes."
weight: 30
icon: fa-solid fa-filter
---

Real-world applications frequently combine full-text BM25 ranking with structured relational filters (such as `category_id = 5`, `tenant_id = 'acme'`, or date ranges). `vchord_bm25` supports three strategies for filtered BM25 search.

## 1. Post-Filtering vs. Pre-Filtering

When you execute a query with a `WHERE` clause and `ORDER BY embedding <&> to_bm25query(...) LIMIT K`:

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25', 'my_tokenizer'))
LIMIT 10;
```

There are two ways `vchord_bm25` can evaluate the `WHERE` predicate:

### Post-Filtering (`enable_prefilter = false`)

1. The `bm25` index runs Block-WeakAnd over the entire corpus and returns the global Top-`bm25_limit` candidates (e.g., Top 100).
2. PostgreSQL fetches those 100 heap tuples and applies `WHERE category = 'database'`.
3. **Caveat**: If only 3 of the global Top-100 documents have `category = 'database'`, the query returns only 3 rows even if hundreds of other `'database'` documents exist with slightly lower BM25 scores!

### Pre-Filtering (`enable_prefilter = true`)

When pre-filtering is enabled, `vchord_bm25` checks heap visibility and evaluates filter acceptability **before** pushing candidate documents into the Block-WeakAnd Top-K heap:

1. Non-matching documents never enter the Top-K heap and never raise the Block-WeakAnd pruning threshold \(\theta\).
2. The index scan continues until it finds \(K\) documents that both **match the `WHERE` filter** and have the **highest BM25 scores** among all matching rows.

### Enabling Pre-Filtering

In **`v0.2.2` – `v0.3.0`**:

```sql
-- Enabled by default in v0.3.0; can be toggled per session:
SET bm25_catalog.enable_prefilter = true;
```

In **`main` branch**:

```sql
-- Enable per session:
SET bm25.prefilter = true;

-- Or enable by default on the index:
ALTER INDEX documents_bm25_idx SET (prefilter = true);
```

## 2. Partial BM25 Indexes for High-Selectivity Partition Keys

If you frequently filter by a small set of known partition keys (for example, `status = 'published'` or specific `tenant_id` values), you can create **partial `bm25` indexes**:

```sql
CREATE INDEX documents_published_bm25
ON documents
USING bm25 (embedding bm25_ops)
WHERE status = 'published';
```

When querying a partial index, reference the partial index's name in `to_bm25query` and include the matching `WHERE` condition:

```sql
SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY embedding <&> to_bm25query('documents_published_bm25', tokenize('PostgreSQL BM25', 'my_tokenizer'))
LIMIT 10;
```

## Choosing the Right Filtering Strategy

| Filter Selectivity | Recommended Strategy | Why |
| :--- | :--- | :--- |
| **High selectivity (50%–100% rows match)** | Post-filtering (`enable_prefilter = false`) with slightly higher `bm25_limit` | Avoids heap fetches during the inner WAND loop; global Top-100 easily contains 10+ matching rows. |
| **Medium selectivity (5%–50% rows match)** | Pre-filtering (`enable_prefilter = true` / `bm25.prefilter = true`) | Guarantees exact Top-K recall over filtered rows without scanning irrelevant postings. |
| **Fixed tenant / status subset** | Partial `bm25` index (`CREATE INDEX ... WHERE ...`) or table partitioning | Smaller index size, dedicated corpus IDF statistics, and zero wasted checks on other partitions. |
{.wide .expand}
