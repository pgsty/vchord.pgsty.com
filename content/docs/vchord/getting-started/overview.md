---
title: "Overview"
linkTitle: "Overview"
description: "What vchord is, the problem it solves for pgvector users, how its two index types differ, and a five-minute quick start."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/overview.md"
aliases:
  - "/docs/getting-started/overview/"
  - "/vectorchord/getting-started/overview/"
icon: fa-solid fa-compass
---

`vchord` is a PostgreSQL extension that adds two approximate nearest-neighbor (ANN) indexes for [pgvector](/docs/vector/) columns. Your tables, vector types, and queries stay as they are: you create a `vchordrq` or `vchordg` index instead of `hnsw` or `ivfflat`, and the same `ORDER BY embedding <-> $1 LIMIT 10` query uses it.

## Why vchord {#why}

pgvector's HNSW index is fast while the whole graph sits in memory. Each index entry holds a full copy of its vector, so the index is at least as large as the vectors themselves, and every step through the graph is a random page read. At tens of millions of vectors the index outgrows RAM, builds take hours, and latency follows the disk.

`vchordrq`, the main vchord index, is designed for that size:

- **Less memory.** Vectors are grouped into lists around centroids (IVF), and each vector is also stored as a [RaBitQ](https://arxiv.org/abs/2405.12497) code a few bits per dimension wide. A query keeps only the centroids hot and reads the lists it needs sequentially.
- **Faster builds.** Clustering runs on a sample with many threads, or [on a GPU outside the database](/docs/vchord/usage/external-build/). On a 16-vCPU machine, 100 million 768-dimensional vectors index in 18 minutes with 6 GiB of build memory ([configuration](/docs/vchord/usage/partitioning-tuning/#laion-100m)).
- **Exact distances at the end.** The compact codes only shortlist candidates. vchord reranks the shortlist with the same exact `<->`, `<#>`, or `<=>` distance that SQL computes before it returns a row.

A 4-vCPU, 32 GB server answers queries over 100 million 768-dimensional vectors at 0.95 top-10 recall ([benchmark](/docs/vchord/benchmark/performance/#laion-100m-on-i4ixlarge)).

## Choose an index {#choose-an-index}

| | `vchordrq` | `vchordg` |
| --- | --- | --- |
| Structure | IVF lists of RaBitQ codes, exact rerank | Graph over RaBitQ codes, exact rerank |
| Good fit | Tables larger than memory, fast builds, filtering by tenant or category | Index fits in memory, low latency without choosing list counts |
| You tune | `lists` at build; `probes` and `epsilon` at query | `m` and `ef_construction` at build; `ef_search` at query |
| Only here | [Filter keys](/docs/vchord/usage/filtering/#filter-keys), [multi-vector MaxSim](/docs/vchord/usage/multi-vector-retrieval/), [external builds](/docs/vchord/usage/external-build/) | |
| Dimensions | up to 60,000 | up to 30,000 |
{.wide}

If you are unsure, start with `vchordrq`: it supports every feature and keeps working when the data outgrows RAM. Both indexes accept pgvector's `vector` and `halfvec` and vchord's compressed [`rabitq8` and `rabitq4`](/docs/vchord/usage/quantization-types/) types.

## Quick start {#quick-start}

vchord 1.5.0 runs on PostgreSQL 15–19 on Linux `x86_64` and `aarch64`, and needs pgvector. Other ways to install are on the [installation page](/docs/vchord/getting-started/installation/).

1. Install the packages from the Pigsty repository:

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord
   ```

1. Preload the library and restart PostgreSQL. Without this step, `CREATE EXTENSION` stops with `vchord must be loaded via shared_preload_libraries`. Keep any libraries already in the list.

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord';
   ```

1. Create the extension in your database. `CASCADE` also creates pgvector's `vector` extension.

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   ```

1. Index a table and query it:

   ```sql
   CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

   INSERT INTO items (embedding)
   SELECT ARRAY[random(), random(), random()]::real[]
   FROM generate_series(1, 1000);

   CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);

   SELECT id FROM items ORDER BY embedding <-> '[3, 1, 2]' LIMIT 5;
   ```
{.steps}

This index has a single list, which is right for small tables. For a real table, choose `lists` from its row count as described in [vchordrq index](/docs/vchord/usage/indexing/#lists).

## Where to go next {#next-steps}

- **Index a production table**: [vchordrq index](/docs/vchord/usage/indexing/), then [measure recall](/docs/vchord/usage/measure-recall/) to tune it.
- **Filter results** by tenant, category, or distance: [Filtering](/docs/vchord/usage/filtering/).
- **Move from pgvector or pgvecto.rs**: [Migration](/docs/vchord/admin/migration/).
- **Add keyword search**: the [Vchord suite](/docs/vchord/getting-started/vectorchord-suite/) combines vchord with BM25 ranking in the same database.

## License {#license}

vchord is licensed under [AGPL-3.0](https://github.com/pgsty/vchord/blob/main/LICENSE). It is a fork of TensorChord's VectorChord, maintained by [PGSTY](https://pgsty.com). For commercial licensing or support, contact [rh@vonng.com](mailto:rh@vonng.com).
