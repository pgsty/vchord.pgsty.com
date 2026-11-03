---
title: "Quick Start"
description: "Run your first BM25 ranked full-text search query in PostgreSQL with vchord_bm25."
weight: 30
icon: fa-solid fa-bolt
---

> [!IMPORTANT]
> Current source targets **0.4.0 (unreleased)**, with native `tsvector` and a new index format. Examples labeled 0.3.x use the historical `bm25vector` API. In-place upgrades are blocked; read the [0.4.0 migration guide](/docs/bm25/reference/migration/) before changing binaries.


This guide walks through creating a table, tokenizing documents, building a `bm25` index, and executing Top-K BM25 queries.

## Workflow A: `bm25vector` + `pg_tokenizer 0.2.0` (`v0.1` – `v0.3`)

In released `vchord_bm25` versions `v0.1.0` through `v0.3.0`, `pg_tokenizer 0.2.0` can tokenize text into an `INT[]` column that is implicitly cast to the historical `bm25vector` type. The helper and `tokenize()` API remain available for this workflow.

### 1. Enable Extensions and Configure `search_path`

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;
```

### 2. Create a Tokenizer

Use `create_tokenizer` with the built-in `llmlingua2` (or `bert_base_uncased`) model:

```sql
SELECT create_tokenizer('my_tokenizer', $$
model = "llmlingua2"
$$);
```

> [!TIP]
> Need domain-specific vocabulary, Chinese (`jieba`), or Japanese (`lindera`)? See the [**Tokenizers (`pg_tokenizer`)**](/docs/tokenizer/) section.

### 3. Create a Table and Populate Documents

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    embedding bm25vector
);

INSERT INTO documents (passage) VALUES
  ('PostgreSQL is a powerful, open-source object-relational database system. It has over 35 years of active development.'),
  ('Full-text search is a technique for searching a single computer-stored document or a collection in a full-text database.'),
  ('BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document.'),
  ('VectorChord-bm25 is a PostgreSQL extension that provides native BM25 ranking index using the Block-WeakAnd algorithm.');
```

### 4. Tokenize Documents into `bm25vector`

`tokenize(text, tokenizer_name)` returns an `INT[]` array of token IDs, which implicitly casts to `bm25vector` (aggregating duplicate token IDs into term frequencies):

```sql
UPDATE documents
SET embedding = tokenize(passage, 'my_tokenizer');

-- Inspect the sparse bm25vector representation ({token_id:term_frequency, ...})
SELECT id, embedding FROM documents LIMIT 2;
```

### 5. Build the `bm25` Index

```sql
CREATE INDEX documents_embedding_bm25
ON documents
USING bm25 (embedding bm25_ops);
```

### 6. Run Top-K BM25 Queries

Use the `<&>` operator with `to_bm25query(index_name, query_vector)` in an ascending `ORDER BY` clause:

```sql
SELECT
    id,
    passage,
    -(embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25 index', 'my_tokenizer'))) AS bm25_score
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25 index', 'my_tokenizer'))
LIMIT 10;
```

> [!IMPORTANT]
> **Why is `<&>` negative?**
> PostgreSQL only supports index-driven `ORDER BY` scans in **ascending** (`ASC`) order. Therefore, `<&>` returns the **negative** BM25 score (e.g., `-2.8415`). More negative values represent higher relevance, allowing `ORDER BY embedding <&> to_bm25query(...) ASC LIMIT K` to use the Block-WeakAnd index scan directly. Negate the expression (`-(embedding <&> ...)`) in `SELECT` if you want positive scores displayed.

---

## Workflow B: Native `tsvector` API (`main` Branch)

In the next-generation `main` branch rewrite, `vchord_bm25` indexes PostgreSQL's native **`tsvector`** type directly—no external tokenizer extension is required for standard languages. Install `pg_tokenizer 0.2.0` when you need its custom analyzer, model, or multilingual pipeline and use `analyze_to_tsvector` or `tokenize_to_tsvector` to produce the indexed value.

### 1. Create Extension and Table

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);

INSERT INTO documents (passage) VALUES
  ('PostgreSQL is a powerful, open-source object-relational database system.'),
  ('Full-text search is a technique for searching documents in a full-text database.'),
  ('BM25 is a bag-of-words retrieval function that ranks documents based on query terms.'),
  ('VectorChord-bm25 provides a native BM25 ranking index in PostgreSQL.');
```

### 2. Build the `bm25` Index on `tsvector`

```sql
CREATE INDEX documents_bm25_idx
ON documents
USING bm25 (vector bm25_ops)
WITH (options = $$
k1 = 1.2
b = 0.75
$$, limit = 100);
```

### 3. Query with `to_bm25query(tsvector, regclass)`

```sql
SELECT
    id,
    passage,
    -(vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25 index'), 'documents_bm25_idx')) AS bm25_score
FROM documents
ORDER BY vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25 index'), 'documents_bm25_idx')
LIMIT 10;
```
