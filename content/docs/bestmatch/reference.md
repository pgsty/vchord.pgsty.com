---
title: "SQL Reference & Comparison"
linkTitle: "SQL Reference"
description: "Complete SQL function reference for pg_bestmatch (bm25_catalog) and architectural comparison with vchord_bm25."
weight: 30
icon: fa-solid fa-book
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#references
math: true
---

## SQL Function Reference (`bm25_catalog`)

All `pg_bestmatch` functions reside in the `bm25_catalog` schema.

### `bm25_create`

Creates BM25 corpus statistics for a specified table and text column.

```sql
bm25_create(
    table_name     regclass,
    column_name    text,
    statistic_name text,
    b              real DEFAULT 0.75,
    k              real DEFAULT 1.2
) RETURNS void
```

- `table_name`: Target table containing the text documents.
- `column_name`: Name of the `text` column to analyze.
- `statistic_name`: Unique identifier for this BM25 statistic set (must be a valid SQL identifier).
- `b`: BM25 document-length normalization factor (default `0.75`).
- `k`: BM25 term-frequency saturation parameter \(k_1\) (default `1.2`).

---

### `bm25_refresh`

Refreshes the materialized corpus statistics for `statistic_name` after document insertions, updates, or deletions.

```sql
bm25_refresh(
    statistic_name text
) RETURNS void
```

---

### `bm25_drop`

Drops all internal tables, materialized views, and triggers associated with `statistic_name`.

```sql
bm25_drop(
    statistic_name text
) RETURNS void
```

---

### `bm25_document_to_svector`

Converts a document string into a BM25 term-frequency sparse vector representation (`text`) formatted for either [`pgvecto.rs`](/docs/vectors/) (`svector`) or [`pgvector`](/docs/vector/) (`sparsevec`).

```sql
bm25_document_to_svector(
    statistic_name text,
    passage        text,
    style          text DEFAULT 'pgvecto.rs'
) RETURNS text
```

- `statistic_name`: Name of the registered statistic set.
- `passage`: Input document text.
- `style`: Output format — `'pgvector'` (1-based indices) or `'pgvecto.rs'` (0-based indices).

---

### `bm25_query_to_svector`

Converts a search query string into an IDF-weighted sparse vector representation (`text`).

```sql
bm25_query_to_svector(
    statistic_name text,
    query          text,
    style          text DEFAULT 'pgvecto.rs'
) RETURNS text
```

---

### `tokenize`

Tokenizes an input string into an array of WordPiece subword tokens using the built-in `bert-base-uncased` vocabulary.

```sql
tokenize(
    input text
) RETURNS text[]
```

---

## Comparison: `pg_bestmatch` vs `vchord_bm25`

Both `pg_bestmatch` and [`vchord_bm25`](/docs/bm25/) were created by the TensorChord team to bring Okapi BM25 ranking into PostgreSQL, but they use fundamentally different architectures:

| Dimension | `pg_bestmatch` (`pg_bestmatch.rs`) | [`vchord_bm25`](/docs/bm25/) + [`pg_tokenizer`](/docs/tokenizer/) |
| :--- | :--- | :--- |
| **Core Mechanism** | Projects BM25 TF/IDF weights into sparse vectors (`sparsevec` / `svector`) | Native inverted index with **Block-WeakAnd (WAND)** Top-K pruning |
| **Index Type** | Relies on [`pgvector`](/docs/vector/) or [`pgvecto.rs`](/docs/vectors/) HNSW sparse index | Dedicated `USING bm25 (vec bm25_ops)` index access method |
| **Search Accuracy** | Approximate (HNSW graph traversal over sparse vectors) | **100% Exact** Top-K BM25 scoring |
| **Tokenization** | Fixed `bert-base-uncased` WordPiece (`30,522` dims) | Pluggable [`pg_tokenizer`](/docs/tokenizer/) (Unicode, Jieba, Lindera, HuggingFace, Snowball, custom corpus-trained models) |
| **Recommended Use** | Lightweight experiments when you already only have `pgvector` HNSW | **Production full-text and hybrid search** |
{.wide .expand}
