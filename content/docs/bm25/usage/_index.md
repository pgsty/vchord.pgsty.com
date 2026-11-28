---
title: "Usage"
description: "Build and maintain bm25 indexes, write and tune ranked queries, combine them with filters, and fuse them with vector search."
weight: 20
icon: fa-solid fa-code
no_list: true
---

These pages follow a table from text to results: produce the `tsvector` and build the index, run ranked queries and size their batches, add `WHERE` conditions, and merge keyword and vector rankings.

{{< cards >}}
  {{< card link="/docs/bm25/usage/indexing/" title="Indexing" icon="fa-solid fa-database" >}}
Produce the `tsvector`, build the index, choose `k1` and `b`, keep it fast under writes, and rebuild it safely.
{{< /card >}}
  {{< card link="/docs/bm25/usage/querying/" title="Querying" icon="fa-solid fa-ranking-star" >}}
How a ranked query runs, what the scores mean, how to size `bm25.limit`, and how to keep the index in the plan.
{{< /card >}}
  {{< card link="/docs/bm25/usage/filtering/" title="Filtering" icon="fa-solid fa-filter" >}}
`WHERE` with ranking, prefiltering for selective conditions, partial indexes, privileges, and row-level security.
{{< /card >}}
  {{< card link="/docs/bm25/usage/hybrid-search/" title="Hybrid search" icon="fa-solid fa-code-merge" >}}
A runnable recipe that fuses BM25 and vchord vector rankings with Reciprocal Rank Fusion.
{{< /card >}}
{{< /cards >}}
