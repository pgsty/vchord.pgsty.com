---
math: true
title: "vchord_bm25 & pg_tokenizer"
linkTitle: "BM25"
description: "Native BM25 ranking index and Block-WeakAnd full-text search for PostgreSQL (`vchord_bm25` & `pg_tokenizer`)."
weight: 15
icon: fa-solid fa-magnifying-glass
type: docs
sidebar_root_for: self
cascade:
  type: docs
  upstream_source: "bm25"
  upstream_link: "https://github.com/supervc-stack/VectorChord-bm25"
---

**`vchord_bm25`** (maintained by Pigsty at [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)) is a native PostgreSQL extension built in Rust (`pgrx`) that implements the **Okapi BM25** ranking algorithm and the **Block-WeakAnd (Block-Max WAND)** Top-K index scan access method inside PostgreSQL.

Paired with **[`pg_tokenizer`](/bm25/tokenizer/)** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) for customizable multilingual tokenization and vocabulary models) or PostgreSQL's built-in `tsvector` analyzer, `vchord_bm25` brings Elasticsearch/Lucene-class lexical full-text ranking directly into your relational database—and combines seamlessly with **[`vchord`](/docs/)** for hybrid semantic + lexical search.

{{< cards >}}
  {{< card link="/bm25/getting-started/" title="Getting Started" icon="fa-solid fa-rocket" >}}
Understand why BM25 matters, install vchord_bm25 and pg_tokenizer, and run your first ranked full-text query.
{{< /card >}}
  {{< card link="/bm25/usage/" title="Usage & Hybrid Search" icon="fa-solid fa-magnifying-glass" >}}
Build bm25 indexes, run Top-K queries, apply WHERE prefilters, and fuse BM25 with VectorChord dense vectors.
{{< /card >}}
  {{< card link="/bm25/tokenizer/" title="Tokenizers (pg_tokenizer)" icon="fa-solid fa-language" >}}
Configure text analyzers, stemmers, stopwords, synonyms, HuggingFace models, Chinese Jieba, and Japanese Lindera.
{{< /card >}}
  {{< card link="/bm25/reference/" title="Reference & Benchmarks" icon="fa-solid fa-book" >}}
Complete SQL types, operators, functions, GUC parameters, version evolution, and BEIR benchmark results.
{{< /card >}}
{{< /cards >}}

## Highlights

- **True Okapi BM25 Scoring**: Supports inverse document frequency (IDF), term frequency saturation (\(k_1\)), and quantized 1-byte document length normalization (\(b\) and average document length \(\text{avgdl}\))—solving fundamental relevance limitations of PostgreSQL's native `ts_rank`.
- **Block-WeakAnd Index Acceleration**: Stores compressed posting lists with per-block maximum score upper bounds using delta-bitpacking, skipping non-competitive document blocks during Top-K queries without scanning entire inverted lists.
- **Multilingual Tokenization**: Works with `pg_tokenizer` (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`, custom corpus-trained models, Chinese `jieba`, Japanese `lindera`) in `v0.1`–`v0.3`, and supports PostgreSQL's native `tsvector` directly in the next-generation `main` architecture.
- **Native Hybrid Search with VectorChord**: Run lexical BM25 (`vchord_bm25`) and dense vector search (`vchordrq`) inside a single SQL query using Reciprocal Rank Fusion (RRF) or ColBERT MaxSim reranking.
