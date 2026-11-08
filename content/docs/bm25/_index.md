---
math: true
title: "vchord_bm25 Documentation"
linkTitle: "vchord_bm25"
description: "Native Okapi BM25 ranking index and Block-WeakAnd full-text search for PostgreSQL (`vchord_bm25`)."
weight: 200
icon: fa-solid fa-magnifying-glass
type: docs
sidebar_root_for: self
aliases:
  - "/bm25/"
no_list: true
cascade:
  type: docs
  upstream_source: "bm25"
  upstream_link: "https://github.com/supervc-stack/VectorChord-bm25"
  upstream_modified: true
---

> [!IMPORTANT]
> **1.1.0** is the current PGSTY release. It keeps the native `tsvector` API and format 4 introduced in 1.0.0, so healthy 1.0.0 indexes do not need a rebuild. Examples labeled 0.3.x use the historical `bm25vector` API; read the [migration guide](/docs/bm25/reference/migration/) before changing binaries.


**`vchord_bm25`** (maintained by Pigsty at [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)) is a native PostgreSQL extension built in Rust (`pgrx`) that implements the **Okapi BM25** ranking algorithm and the **Block-WeakAnd (Block-Max WAND)** Top-K index scan access method inside PostgreSQL.

Paired with **[`pg_tokenizer`](/docs/tokenizer/)** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) for customizable multilingual tokenization and vocabulary models) or PostgreSQL's built-in `tsvector` analyzer, `vchord_bm25` brings Elasticsearch/Lucene-class lexical full-text ranking directly into your relational database—and combines seamlessly with **[`vchord`](/docs/vchord/)** and **[`pgvector`](/docs/vector/)** for hybrid semantic + lexical search.

{{< cards >}}
  {{< card link="/docs/bm25/getting-started/" title="Getting Started" icon="fa-solid fa-rocket" >}}
Understand why Okapi BM25 outperforms native `ts_rank`, install `vchord_bm25` and `pg_tokenizer` via Pigsty or Docker (Obsolete), and run your first ranked query.
{{< /card >}}
  {{< card link="/docs/bm25/usage/" title="Usage & Indexing" icon="fa-solid fa-magnifying-glass" >}}
Build and maintain `bm25` inverted indexes, run Top-K Block-WeakAnd queries, apply `WHERE` prefilters during ranking, and inspect internal index pages.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid Search" icon="fa-solid fa-code-merge" >}}
Fuse sparse BM25 lexical search with [`vchord`](/docs/vchord/) dense vector and ColBERT multi-vector retrieval using Reciprocal Rank Fusion (RRF) in SQL.
{{< /card >}}
  {{< card link="/docs/bm25/reference/" title="Reference & Benchmarks" icon="fa-solid fa-book" >}}
Consult the complete reference for SQL types, operators, functions, session GUC parameters, API version history, and BEIR benchmark evaluations.
{{< /card >}}
  {{< card link="/docs/bm25/reference/migration/" title="0.3.x to 1.0.0 Migration" icon="fa-solid fa-right-left" >}}
Follow the step-by-step migration guide from the historical `bm25vector` + `pg_tokenizer` (`0.3.x`) workflow to the native `tsvector` engine in `1.0.0` and later releases.
{{< /card >}}
  {{< card link="/docs/tokenizer/" title="pg_tokenizer Documentation" icon="fa-solid fa-language" >}}
Configure modular text analyzers, Snowball stemmers, stopwords, synonyms, HuggingFace vocabularies, Chinese Jieba, and Japanese Lindera segmentation.
{{< /card >}}
{{< /cards >}}

## Highlights

- **True Okapi BM25 Scoring**: Supports inverse document frequency (IDF), term frequency saturation (\(k_1\)), and quantized 1-byte document length normalization (\(b\) and average document length \(\text{avgdl}\))—solving fundamental relevance limitations of PostgreSQL's native `ts_rank`.
- **Block-WeakAnd Index Acceleration**: Stores compressed posting lists with per-block maximum score upper bounds using delta-bitpacking, skipping non-competitive document blocks during Top-K queries without scanning entire inverted lists.
- **Multilingual Tokenization**: Works with [`pg_tokenizer`](/docs/tokenizer/) (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`, custom corpus-trained models, Chinese `jieba`, Japanese `lindera`) through integer arrays in `v0.1`–`v0.3`; `1.0.0` indexes PostgreSQL's native `tsvector`, including the output of pg_tokenizer 1.0.0's `tokenize_to_tsvector` and `analyze_to_tsvector`.
- **Native Hybrid Search with Vchord**: Run lexical BM25 (`vchord_bm25`) and dense vector search (`vchordrq`) inside a single SQL query using Reciprocal Rank Fusion (RRF) or ColBERT MaxSim reranking.
