---
title: "vchord_bm25 Documentation"
linkTitle: "vchord_bm25"
description: "BM25 relevance ranking for PostgreSQL full-text search: an index that returns the best-matching rows of a tsvector column without scoring every match."
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

`vchord_bm25` is a PostgreSQL extension that ranks rows by BM25 relevance through an index on a `tsvector` column. It scores with statistics of the whole table and returns the top results of `ORDER BY ... LIMIT k` without scoring every matching row, which `ts_rank` with a GIN index cannot do. Use it for keyword search and retrieval for RAG inside PostgreSQL, on its own or next to vector search with [vchord](/docs/vchord/).

{{< cards >}}
  {{< card link="/docs/bm25/getting-started/overview/" title="Overview and quick start" icon="fa-solid fa-compass" >}}
Why BM25 needs its own index in PostgreSQL, how a ranked query runs, and a first query in five steps.
{{< /card >}}
  {{< card link="/docs/bm25/getting-started/installation/" title="Installation" icon="fa-solid fa-download" >}}
Install from Pigsty packages, GitHub release packages, or source, then preload and create the extension.
{{< /card >}}
  {{< card link="/docs/bm25/usage/indexing/" title="Indexing" icon="fa-solid fa-database" >}}
Produce the `tsvector` for any language, build the index, choose `k1` and `b`, and keep the index fast as rows change.
{{< /card >}}
  {{< card link="/docs/bm25/usage/querying/" title="Querying" icon="fa-solid fa-ranking-star" >}}
Write ranked queries, read the scores, size the scan batch, and make the planner use the index.
{{< /card >}}
  {{< card link="/docs/bm25/usage/filtering/" title="Filtering" icon="fa-solid fa-filter" >}}
Combine ranking with `WHERE`, prefiltering, partial indexes, and row-level security.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid search" icon="fa-solid fa-code-merge" >}}
Merge BM25 and vchord vector rankings with Reciprocal Rank Fusion in one SQL statement.
{{< /card >}}
  {{< card link="/docs/bm25/reference/" title="Reference" icon="fa-solid fa-book" >}}
SQL objects, settings and index options, upgrades, the legacy `bm25vector` API, and benchmarks.
{{< /card >}}
  {{< card link="/docs/tokenizer/" title="pg_tokenizer" icon="fa-solid fa-language" >}}
Produce `tsvector` values for Chinese, Japanese, Korean, custom analyzers, and model vocabularies.
{{< /card >}}
{{< /cards >}}
