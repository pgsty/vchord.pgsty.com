---
title: "Getting Started"
description: "Overview, installation, and quick start guide for vchord_bm25 and pg_tokenizer."
weight: 10
icon: fa-solid fa-rocket
no_list: true
---

Get started with **`vchord_bm25`** in PostgreSQL:

{{< cards >}}
  {{< card link="/docs/bm25/getting-started/overview/" title="Overview" icon="fa-solid fa-compass" >}}
Understand why Okapi BM25 and Block-WeakAnd index pruning significantly outperform native PostgreSQL `ts_rank` and GIN indexes for Top-K search.
{{< /card >}}
  {{< card link="/docs/bm25/getting-started/installation/" title="Installation" icon="fa-solid fa-download" >}}
Install and preload `vchord_bm25` and `pg_tokenizer` via Pigsty native Linux packages, Docker containers, Debian/ZIP archives, or source builds.
{{< /card >}}
  {{< card link="/docs/bm25/getting-started/quick-start/" title="Quick Start" icon="fa-solid fa-bolt" >}}
Walk through a complete hands-on SQL tutorial to tokenize text, build a `bm25` inverted index, and run Top-K ranked full-text queries in minutes.
{{< /card >}}
{{< /cards >}}
