---
title: "pg_bestmatch Documentation"
linkTitle: "pg_bestmatch"
description: "Generate Okapi BM25 sparse vectors inside PostgreSQL and run lexical similarity search over pgvector (sparsevec) or pgvecto.rs (svector)."
weight: 600
icon: fa-solid fa-ranking-star
type: docs
sidebar_root_for: self
upstream_source: bestmatch
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs
upstream_modified: true
aliases:
  - "/bestmatch/"
no_list: true
cascade:
  type: docs
  upstream_source: bestmatch
  upstream_modified: true
---

**`pg_bestmatch`** (`pg_bestmatch.rs`) is a PostgreSQL extension for servicing Okapi BM25 text queries inside PostgreSQL by converting documents and queries into **BM25-weighted sparse vectors** compatible with [`pgvector`](/docs/vector/) (`sparsevec`) and [`pgvecto.rs`](/docs/vectors/) (`svector`).

> [!IMPORTANT] Successor Recommendation: `vchord_bm25` + `pg_tokenizer`
> `pg_bestmatch.rs` was TensorChord's first-generation BM25 extension built on sparse vector dot products. For new production deployments, we recommend [`vchord_bm25`](/docs/bm25/) paired with [`pg_tokenizer`](/docs/tokenizer/), which replaces HNSW sparse-vector approximation with a native **Block-WeakAnd (WAND)** inverted index for 100% exact Top-K BM25 scoring and up to 3x higher throughput.

## Key Capabilities

- **In-Database BM25 Sparse Vector Generation**: Maintains document frequency, term frequency, and document length statistics inside `bm25_catalog` and emits BM25-weighted sparse vectors for both documents and queries.
- **Native [`pgvector`](/docs/vector/) & [`pgvecto.rs`](/docs/vectors/) Integration**: Outputs standard `sparsevec` (`pgvector 0.7.0+`) or `svector` (`pgvecto.rs`) values so you can score documents with `<#>` (negative inner product) and accelerate search with HNSW indexes.
- **Built-in Tokenization**: Ships with a built-in HuggingFace `bert-base-uncased` WordPiece vocabulary (`30,522` dimensions) and a standalone `tokenize(text)` SQL function.

## Documentation Sections

{{< cards >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" link="/docs/bestmatch/getting-started/" >}}
How `pg_bestmatch` converts BM25 scoring into sparse vector inner products, installation from packages or source, and quickstart setup.
{{< /card >}}
{{< card title="Usage Guide" icon="fa-solid fa-code" link="/docs/bestmatch/usage/" >}}
End-to-end BM25 retrieval workflow on the Stanford LoCo benchmark using [`pgvector`](/docs/vector/) `sparsevec` or [`pgvecto.rs`](/docs/vectors/) `svector`.
{{< /card >}}
{{< card title="SQL Reference & Comparison" icon="fa-solid fa-book-open" link="/docs/bestmatch/reference/" >}}
Complete reference for `bm25_create`, `bm25_refresh`, `bm25_drop`, `bm25_document_to_svector`, `bm25_query_to_svector`, and `tokenize`.
{{< /card >}}
{{< /cards >}}
