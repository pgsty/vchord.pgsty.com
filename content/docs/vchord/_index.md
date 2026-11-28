---
title: "vchord Documentation"
linkTitle: "vchord"
description: "Disk-friendly approximate nearest-neighbor indexes for pgvector columns in PostgreSQL."
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

`vchord` adds two approximate nearest-neighbor indexes to PostgreSQL for [pgvector](/docs/vector/) columns: `vchordrq`, which keeps memory small and scales past RAM, and `vchordg`, a graph for low-latency search. Your tables and queries stay as they are. The current release is [1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0), for PostgreSQL 15–19 on Linux `x86_64` and `aarch64`.

## Start here {#start}

- [Overview](/docs/vchord/getting-started/overview/) — Why vchord, which index to choose, and a five-minute quick start.
- [Installation](/docs/vchord/getting-started/installation/) — Pigsty packages, release archives, or a build from source.
- [vchordrq index](/docs/vchord/usage/indexing/) — How the main index works, how to size it, and how to tune it.
- [Filtering](/docs/vchord/usage/filtering/) — Nearest rows within one tenant, category, date range, or distance.
- [Upgrade and migration](/docs/vchord/admin/migration/) — Upgrade in place, or move over from pgvector and pgvecto.rs.
- [Performance tuning](/docs/vchord/usage/postgresql-tuning/) — Parallel builds, memory, prewarming, and disk reads.
{.cards}

## Go further {#more}

- [vchordg index](/docs/vchord/usage/graph-index/) — The graph index and its memory needs.
- [Multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/) — Token-level MaxSim search.
- [Quantized types](/docs/vchord/usage/quantization-types/) — Vectors at 8 or 4 bits per dimension.
- [Measure recall](/docs/vchord/usage/measure-recall/) — Tune against your own real queries.
- [Building large indexes](/docs/vchord/usage/partitioning-tuning/) — Builds for 100 million rows and up.
- [External build](/docs/vchord/usage/external-build/) — Train the centroids on a GPU.
- [Benchmarks](/docs/vchord/benchmark/) — Throughput, recall, and cost against other systems.
- [Use cases](/docs/vchord/use-case/) — Hybrid search, ColBERT reranking, and visual document retrieval.
- [Customer stories](/docs/vchord/customer-stories/) — 3.2 billion satellite embeddings on three PostgreSQL servers.
{.cards}
