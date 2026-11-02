---
title: "Usage & Hybrid Search"
description: "Index management, Top-K querying, prefiltering, hybrid search with vchord, and Block-WeakAnd internals."
weight: 20
icon: fa-solid fa-code
---

Learn how to build, tune, and query `vchord_bm25` indexes in production:

{{< cards >}}
  {{< card link="/docs/bm25/usage/indexing/" title="Indexing & Maintenance" icon="fa-solid fa-database" >}}
Create bm25 indexes, tune segment sizes and BM25 parameters (k1, b), monitor parallel builds, and inspect pages.
{{< /card >}}
  {{< card link="/docs/bm25/usage/querying/" title="Querying & Scoring" icon="fa-solid fa-ranking-star" >}}
Run Top-K Block-WeakAnd queries, understand negative BM25 scores, and tune bm25_limit.
{{< /card >}}
  {{< card link="/docs/bm25/usage/filtering/" title="Filtered Search & Prefiltering" icon="fa-solid fa-filter" >}}
Combine WHERE predicates with BM25 ranking using post-filtering, pre-filtering, and partial indexes.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid Search (BM25 + VectorChord)" icon="fa-solid fa-code-merge" >}}
Fuse sparse BM25 lexical search with VectorChord dense vector search via Reciprocal Rank Fusion (RRF) and ColBERT.
{{< /card >}}
  {{< card link="/docs/bm25/usage/algorithms/" title="BM25 & Block-WeakAnd Internals" icon="fa-solid fa-microchip" >}}
Deep dive into the Okapi BM25 formula, 1-byte fieldnorm quantization, delta-bitpacking, and Block-Max WAND.
{{< /card >}}
{{< /cards >}}
