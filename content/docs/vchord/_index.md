---
title: "vchord Documentation"
linkTitle: "vchord"
description: "Scalable, fast, and disk-friendly vector similarity search in PostgreSQL powered by RaBitQ quantization."
weight: 100
icon: fa-solid fa-layer-group
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/index.md
upstream_modified: true
aliases:
  - "/vchord/"
  - "/vectorchord/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

**`vchord`** (VectorChord) is a PostgreSQL extension built on [`pgvector`](/docs/vector/) for scalable, high-performance, and disk-friendly vector similarity search. Powered by **RaBitQ** 1-bit/4-bit/8-bit quantization, it delivers inverted-file (`vchordrq`) and single-layer graph (`vchordg`) index access methods, native multi-vector MaxSim (`@#`), sphere range queries (`<<->>`), and external centroid precomputation.

## Documentation Sections

{{< cards >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" link="/docs/vchord/getting-started/" >}}
Overview, quickstart tutorial, installation via Pigsty, Docker, or prebuilt packages, and migration from [`pgvecto.rs`](/docs/vectors/).
{{< /card >}}
{{< card title="Usage Guide" icon="fa-solid fa-code" link="/docs/vchord/usage/" >}}
Indexing with `vchordrq` and `vchordg`, nearest-neighbor and sphere search, filtering, prewarm, external index builds, and full SQL reference.
{{< /card >}}
{{< card title="Use Cases" icon="fa-solid fa-diagram-project" link="/docs/vchord/use-case/" >}}
Multi-vector ColBERT MaxSim (`@#`) late interaction and hybrid semantic + BM25 search with [`vchord_bm25`](/docs/bm25/) and [`pg_tokenizer`](/docs/tokenizer/).
{{< /card >}}
{{< card title="Benchmarks & TCO" icon="fa-solid fa-chart-line" link="/docs/vchord/benchmark/" >}}
Reproducible performance, recall, memory, and cost comparisons across GIST-1M, Cohere-10M, and LAION-100M.
{{< /card >}}
{{< card title="Administration" icon="fa-solid fa-sliders" link="/docs/vchord/admin/" >}}
Production parameter tuning, memory sizing, I/O concurrency, vacuuming, and version upgrades.
{{< /card >}}
{{< card title="Customer Stories" icon="fa-solid fa-earth-americas" link="/docs/vchord/customer-stories/" >}}
How the University of Oxford stores and queries 3 billion satellite embedding vectors in PostgreSQL with `vchord`.
{{< /card >}}
{{< /cards >}}

## Key Topics & Deep Dives

{{< cards >}}
{{< card title="vchordrq vs vchordg Indexing" icon="fa-solid fa-sitemap" link="/docs/vchord/usage/indexing/" >}}
Compare disk-friendly hierarchical K-Means (`vchordrq`) against low-latency single-layer graphs (`vchordg`) and configure build options.
{{< /card >}}
{{< card title="RaBitQ4 & RaBitQ8 Types" icon="fa-solid fa-compress" link="/docs/vchord/usage/quantization-types/" >}}
Compress 32-bit vectors into 4-bit (`rabitq4`) or 8-bit (`rabitq8`) quantized types with theoretical error bounds.
{{< /card >}}
{{< card title="Multi-Vector MaxSim (@#)" icon="fa-solid fa-cubes" link="/docs/vchord/usage/multi-vector-retrieval/" >}}
Index `vector[]` token embeddings with WARP dynamic pruning for ColBERTv2 and ColPali visual document retrieval.
{{< /card >}}
{{< card title="External Index Precomputation" icon="fa-solid fa-server" link="/docs/vchord/usage/external-build/" >}}
Offload K-Means centroid clustering to external CPUs or GPUs and build 100M-vector indexes in 20 minutes.
{{< /card >}}
{{< card title="Performance Tuning & Sizing" icon="fa-solid fa-gauge-high" link="/docs/vchord/usage/postgresql-tuning/" >}}
Tune `probes`, `epsilon`, `ef_search`, `io_search`, `max_scan_tuples`, and PostgreSQL shared memory for production workloads.
{{< /card >}}
{{< card title="Migrating from pgvecto.rs" icon="fa-solid fa-right-left" link="/docs/vchord/admin/migration/" >}}
Step-by-step SQL migration guide from [`pgvecto.rs`](/docs/vectors/) (`vectors` extension) or `pgvector` HNSW/IVFFlat to `vchord`.
{{< /card >}}
{{< /cards >}}
