---
title: "pgvector Documentation"
linkTitle: "pgvector"
description: "Open-source vector similarity search for PostgreSQL: vector, halfvec, bit, and sparsevec data types, exact and approximate KNN search, HNSW and IVFFlat indexing."
weight: 400
icon: fa-solid fa-circle-nodes
type: docs
sidebar_root_for: self
upstream_source: pgvector
upstream_link: https://github.com/pgvector/pgvector
upstream_modified: true
aliases:
  - "/vector/"
no_list: true
cascade:
  type: docs
  upstream_source: pgvector
  upstream_modified: true
---

**`pgvector`** is the foundational open-source vector similarity search extension for PostgreSQL. It provides the core `vector`, `halfvec`, `bit`, and `sparsevec` data types, distance operators, and built-in **HNSW** and **IVFFlat** index access methods.

> [!TIP] Relationship with `vchord`
> [`vchord`](/docs/vchord/) builds directly on `pgvector`'s data types (`vector` and `halfvec`) and distance operators (`<->`, `<#>`, `<=>`). You can add [`vchord`](/docs/vchord/) (`vchordrq` or `vchordg`) indexes to existing `pgvector` tables without changing your schema or application queries.

## Key Features

- **Exact and approximate nearest-neighbor search** inside standard PostgreSQL tables with full ACID transactions, point-in-time recovery, joins, and filtering.
- **Multiple vector representations**:
  - Single-precision floating-point vectors (`vector`, up to 2,000 dimensions indexed; up to 16,000 dimensions stored)
  - Half-precision floating-point vectors (`halfvec`, up to 4,000 dimensions indexed)
  - Binary vectors (`bit`, up to 64,000 dimensions indexed)
  - Sparse vectors (`sparsevec`, up to 1,000 non-zero elements across up to 1,000,000 dimensions)
- **Six distance metrics**: L2 distance (`<->`), inner product (`<#>`), cosine distance (`<=>`), L1 distance (`<+>`), Hamming distance (`<~>`), and Jaccard distance (`<%>`).
- **Iterative index scans** (`0.8.0+`) that automatically expand HNSW or IVFFlat candidate traversal when `WHERE` filters narrow the result set.

## Documentation Sections

{{< cards >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" link="/docs/vector/getting-started/" >}}
Install `pgvector` via Pigsty, Docker, Linux packages, Homebrew, or source; enable the extension; and insert or bulk-load vectors.
{{< /card >}}
{{< card title="Querying & Filtering" icon="fa-solid fa-magnifying-glass" link="/docs/vector/querying/" >}}
Distance operators, similarity calculations, vector aggregates, `WHERE` filtering with iterative index scans, and hybrid search.
{{< /card >}}
{{< card title="HNSW & IVFFlat Indexing" icon="fa-solid fa-sitemap" link="/docs/vector/indexing/" >}}
Create and tune HNSW and IVFFlat indexes, parallel index build settings, progress monitoring, and scaling with [`vchord`](/docs/vchord/).
{{< /card >}}
{{< card title="Quantization & Sparse Vectors" icon="fa-solid fa-compress" link="/docs/vector/quantization/" >}}
Half-precision (`halfvec`), binary quantization (`bit` + re-ranking), sparse vectors (`sparsevec`), and Matryoshka sub-vector indexing.
{{< /card >}}
{{< card title="Reference, Tuning & FAQ" icon="fa-solid fa-book-open" link="/docs/vector/reference/" >}}
Complete SQL function and operator reference, GUC parameters, memory sizing, query plan debugging, and frequently asked questions.
{{< /card >}}
{{< card title="Scale with vchord" icon="fa-solid fa-layer-group" link="/docs/vchord/" >}}
Drop-in RaBitQ `vchordrq` and `vchordg` indexes on standard `pgvector` columns for 100M+ vectors without changing queries.
{{< /card >}}
{{< /cards >}}
