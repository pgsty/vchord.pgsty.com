---
title: "Usage Guide"
linkTitle: "Usage Guide"
description: "Step-by-step workflow for BM25 sparse vector indexing and retrieval with pg_bestmatch and pgvector or pgvecto.rs."
weight: 20
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#usage
---

This guide walks through a complete BM25 text retrieval pipeline using `pg_bestmatch` and [`pgvector`](/docs/vector/) (`sparsevec`), followed by the equivalent configuration for [`pgvecto.rs`](/docs/vectors/) (`svector`).

## 1. Enable Extensions & Set Search Path

```sql
CREATE EXTENSION IF NOT EXISTS pg_bestmatch;
CREATE EXTENSION IF NOT EXISTS vector;

SET search_path TO "$user", public, bm25_catalog;
```

## 2. Create the Documents Table & Load Data

```sql
CREATE TABLE documents (
    id bigint PRIMARY KEY,
    passage text
);

INSERT INTO documents (id, passage) VALUES
  (1, 'PostgreSQL is an advanced open-source relational database system.'),
  (2, 'VectorChord brings disk-friendly RaBitQ vector search to PostgreSQL.'),
  (3, 'BM25 is a bag-of-words ranking function used in information retrieval.');
```

## 3. Create BM25 Corpus Statistics

Call `bm25_create(table_name, column_name, statistic_name, b, k)` to register corpus statistics (`b = 0.75` and `k = 1.2` are standard defaults):

```sql
SELECT bm25_create('documents', 'passage', 'documents_passage_bm25', 0.75, 1.2);
```

What `bm25_create` does under the hood:
1. Creates materialized views and helper tables inside `bm25_catalog` to track term frequencies, document frequencies, and total document count.
2. Installs a trigger on `documents` so newly inserted or deleted rows are tracked automatically.

> [!NOTE] Refreshing Corpus Statistics After Bulk Updates
> When you load a large batch of new documents and want to recompute global IDF and average document length (`avgdl`), run:
> ```sql
> SELECT bm25_refresh('documents_passage_bm25');
> ```

## 4. Materialize Document Sparse Vectors (`pgvector`)

Add a `sparsevec` column to `documents` and populate it using `bm25_document_to_svector`:

```sql
ALTER TABLE documents ADD COLUMN embedding sparsevec(30522);

UPDATE documents
SET embedding = bm25_document_to_svector(
    'documents_passage_bm25',
    passage,
    'pgvector'
)::sparsevec;
```

## 5. Create an HNSW Sparse Vector Index

Use [`pgvector`](/docs/vector/)'s HNSW index with inner-product operator class `sparsevec_ip_ops`:

```sql
CREATE INDEX documents_embedding_bm25_idx
ON documents
USING hnsw (embedding sparsevec_ip_ops);
```

## 6. Run BM25 Queries

Convert the search query into a sparse vector with `bm25_query_to_svector` and order by `<#>` (negative inner product):

```sql
SELECT
    id,
    passage,
    (embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search', 'pgvector')::sparsevec) * -1 AS bm25_score
FROM documents
ORDER BY embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search', 'pgvector')::sparsevec
LIMIT 5;
```

---

## Using `pg_bestmatch` with `pgvecto.rs` (`svector`)

If you are using [`pgvecto.rs`](/docs/vectors/) (`v0.3.0+`) instead of `pgvector`, omit the `'pgvector'` style argument (or pass `'pgvecto.rs'`) and cast to `svector`:

```sql
CREATE EXTENSION IF NOT EXISTS vectors;

ALTER TABLE documents ADD COLUMN embedding svector(30522);

UPDATE documents
SET embedding = bm25_document_to_svector('documents_passage_bm25', passage)::svector;

CREATE INDEX documents_embedding_svector_idx
ON documents
USING vectors (embedding svector_dot_ops);

SELECT id, passage
FROM documents
ORDER BY embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search')::svector
LIMIT 5;
```
