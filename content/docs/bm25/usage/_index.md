---
title: "Usage & Hybrid Search"
description: "Index management, Top-K querying, prefiltering, hybrid search with vchord, and Block-WeakAnd internals."
weight: 20
icon: fa-solid fa-code
no_list: true
---

Learn how to build, tune, and query `vchord_bm25` indexes in production:

{{< cards >}}
  {{< card link="/docs/bm25/usage/indexing/" title="Indexing & Maintenance" icon="fa-solid fa-database" >}}
Create and maintain `bm25` inverted indexes, tune segment sizes and BM25 parameters (`k1`, `b`), monitor parallel builds, and inspect index pages.
{{< /card >}}
  {{< card link="/docs/bm25/usage/querying/" title="Querying & Scoring" icon="fa-solid fa-ranking-star" >}}
Execute Top-K Block-WeakAnd queries with the `<&>` operator, understand negative BM25 relevance scores, and tune candidate limit settings.
{{< /card >}}
  {{< card link="/docs/bm25/usage/filtering/" title="Filtered Search & Prefiltering" icon="fa-solid fa-filter" >}}
Combine relational `WHERE` predicates with BM25 ranking using post-filtering, in-index pre-filtering, and partial indexes for multi-tenant workloads.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid Search (BM25 + VectorChord)" icon="fa-solid fa-code-merge" >}}
Fuse sparse BM25 lexical search with `vchord` dense vector search in a single SQL query via Reciprocal Rank Fusion (RRF) and ColBERT reranking.
{{< /card >}}
  {{< card link="/docs/bm25/usage/algorithms/" title="BM25 & Block-WeakAnd Internals" icon="fa-solid fa-microchip" >}}
Take a deep dive into the Okapi BM25 scoring formula, 1-byte fieldnorm quantization, delta-bitpacking compression, and Block-Max WAND pruning.
{{< /card >}}
{{< /cards >}}
