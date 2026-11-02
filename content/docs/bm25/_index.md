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
  upstream_link: "https://github.com/tensorchord/VectorChord-bm25"
  upstream_modified: true
---

> [!IMPORTANT]
> Current source targets **0.4.0 (unreleased)**, with native `tsvector` and a new index format. Examples labeled 0.3.x use the historical `bm25vector` API. In-place upgrades are blocked; read the [0.4.0 migration guide](/docs/bm25/reference/migration/) before changing binaries.


**`vchord_bm25`** (maintained by Pigsty at [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)) is a native PostgreSQL extension built in Rust (`pgrx`) that implements the **Okapi BM25** ranking algorithm and the **Block-WeakAnd (Block-Max WAND)** Top-K index scan access method inside PostgreSQL.

Paired with **[`pg_tokenizer`](/docs/tokenizer/)** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) for customizable multilingual tokenization and vocabulary models) or PostgreSQL's built-in `tsvector` analyzer, `vchord_bm25` brings Elasticsearch/Lucene-class lexical full-text ranking directly into your relational database—and combines seamlessly with **[`vchord`](/docs/vchord/)** and **[`pgvector`](/docs/vector/)** for hybrid semantic + lexical search.

{{< cards >}}
  {{< card link="/docs/bm25/getting-started/" title="Getting Started" icon="fa-solid fa-rocket" >}}
Understand why BM25 matters, install vchord_bm25 and pg_tokenizer, and run your first ranked full-text query.
{{< /card >}}
  {{< card link="/docs/bm25/usage/" title="Usage & Indexing" icon="fa-solid fa-magnifying-glass" >}}
Build bm25 indexes, run Top-K Block-WeakAnd queries, apply WHERE prefilters, and inspect index pages.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid Search" icon="fa-solid fa-code-merge" >}}
Fuse sparse BM25 lexical search with [`vchord`](/docs/vchord/) dense and ColBERT multi-vector search via RRF in SQL.
{{< /card >}}
  {{< card link="/docs/bm25/reference/" title="Reference & Benchmarks" icon="fa-solid fa-book" >}}
Complete SQL types, operators, functions, GUC parameters, version evolution, and BEIR benchmark results.
{{< /card >}}
  {{< card link="/docs/bm25/reference/migration/" title="0.3.x to 0.4.0 Migration" icon="fa-solid fa-right-left" >}}
Migrate from `bm25vector` + `pg_tokenizer` (0.3.x) to the native `tsvector` BM25 index format in 0.4.0.
{{< /card >}}
  {{< card link="/docs/tokenizer/" title="pg_tokenizer Documentation" icon="fa-solid fa-language" >}}
Configure text analyzers, stemmers, stopwords, synonyms, HuggingFace models, Chinese Jieba, and Japanese Lindera.
{{< /card >}}
{{< /cards >}}

## Highlights

- **True Okapi BM25 Scoring**: Supports inverse document frequency (IDF), term frequency saturation (\(k_1\)), and quantized 1-byte document length normalization (\(b\) and average document length \(\text{avgdl}\))—solving fundamental relevance limitations of PostgreSQL's native `ts_rank`.
- **Block-WeakAnd Index Acceleration**: Stores compressed posting lists with per-block maximum score upper bounds using delta-bitpacking, skipping non-competitive document blocks during Top-K queries without scanning entire inverted lists.
- **Multilingual Tokenization**: Works with [`pg_tokenizer`](/docs/tokenizer/) (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`, custom corpus-trained models, Chinese `jieba`, Japanese `lindera`) in `v0.1`–`v0.3`, and supports PostgreSQL's native `tsvector` directly in the next-generation `main` architecture.
- **Native Hybrid Search with Vchord**: Run lexical BM25 (`vchord_bm25`) and dense vector search (`vchordrq`) inside a single SQL query using Reciprocal Rank Fusion (RRF) or ColBERT MaxSim reranking.
