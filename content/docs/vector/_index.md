---
title: "pgvector Documentation"
linkTitle: "pgvector"
description: "Open-source vector similarity search for PostgreSQL: vector, halfvec, bit, and sparsevec data types, exact and approximate KNN search, HNSW and IVFFlat indexing."
weight: 600
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
Install `pgvector` via Pigsty packages, Docker, Linux repositories, Homebrew, or source; enable the extension; and insert or bulk-load vector data.
{{< /card >}}
{{< card title="Querying & Filtering" icon="fa-solid fa-magnifying-glass" link="/docs/vector/querying/" >}}
Use the six distance operators, convert distances to similarity scores, compute aggregates, and run `WHERE` filters with iterative index scans.
{{< /card >}}
{{< card title="HNSW & IVFFlat Indexing" icon="fa-solid fa-sitemap" link="/docs/vector/indexing/" >}}
Create and tune HNSW and IVFFlat indexes, configure parallel build memory, monitor build progress, and scale beyond RAM limits with [`vchord`](/docs/vchord/).
{{< /card >}}
{{< card title="Quantization & Sparse Vectors" icon="fa-solid fa-compress" link="/docs/vector/quantization/" >}}
Reduce memory footprint using half-precision (`halfvec`), binary quantization (`bit` with re-ranking), sparse vectors (`sparsevec`), and Matryoshka indexing.
{{< /card >}}
{{< card title="Reference, Tuning & FAQ" icon="fa-solid fa-book-open" link="/docs/vector/reference/" >}}
Consult the complete SQL type, operator, and function reference, GUC runtime parameters, memory sizing guide, and query plan troubleshooting FAQ.
{{< /card >}}
{{< card title="Scale with vchord" icon="fa-solid fa-layer-group" link="/docs/vchord/" >}}
Add drop-in RaBitQ `vchordrq` and `vchordg` indexes directly onto existing `pgvector` columns to scale to 100M+ vectors without changing SQL queries.
{{< /card >}}
{{< /cards >}}
