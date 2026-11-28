---
title: "Performance Tuning"
linkTitle: "Performance Tuning"
description: "PostgreSQL settings that decide vchord build time and query latency: parallel builds, shared_buffers, prewarming after a restart, and how pages are read from disk."
weight: 100
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/postgresql-tuning.md"
aliases:
  - "/docs/usage/postgresql-tuning/"
  - "/vectorchord/usage/postgresql-tuning/"
  - "/docs/vchord/usage/performance-tuning/"
  - "/vectorchord/usage/performance-tuning/"
  - "/docs/vchord/usage/prewarm/"
  - "/docs/usage/prewarm/"
  - "/vectorchord/usage/prewarm/"
  - "/docs/vchord/usage/prefetch/"
  - "/docs/usage/prefetch/"
  - "/vectorchord/usage/prefetch/"
icon: fa-solid fa-gauge-high
---

Once an index has the recall you want, the rest of its speed comes from PostgreSQL: how many processes build it, whether the pages queries need are in memory, and how the rest is read from disk. This page covers those settings in that order. The defaults are reasonable; change them when a build is too slow, or when queries are slow right after a restart or on an index larger than memory.

## Parallel index builds {#parallel-index-builds}

On PostgreSQL 17 and later, `CREATE INDEX` and `REINDEX` insert rows into vchordrq and vchordg indexes with parallel workers. vchordrq's k-means step is separate and uses its own [`build_threads`](/docs/vchord/usage/indexing/#build).

For a build with 16 processes, the leader and 15 workers:

```sql
-- Needs a restart; leave room for other background workers.
ALTER SYSTEM SET max_worker_processes = 24;

-- In the session that runs CREATE INDEX:
SET max_parallel_workers = 15;
SET max_parallel_maintenance_workers = 15;
```

PostgreSQL decides how many workers to start from the table's size, and may start fewer than allowed on a table that was just loaded. To fix the number, set it on the table:

```sql
ALTER TABLE items SET (parallel_workers = 15);
```

Builds on temporary tables, and indexes with parallel-unsafe expressions or `WHERE` predicates, run in a single process.

## Keep the index in memory {#shared-buffers}

A query is fastest when the pages it reads are in `shared_buffers`. What it reads depends on the index:

- **vchordrq**: the centroids on every query, plus the RaBitQ codes of the lists it probes. Full-precision vectors are read only for the candidates it reranks.
- **vchordg**: the RaBitQ codes and neighbor lists along its walk, plus full-precision vectors for the final candidates.

Size `shared_buffers` so that at least the centroids, and ideally the codes, fit. A server dedicated to vector search can give it a larger share of RAM than the usual 25%. Changing it needs a restart:

```sql
ALTER SYSTEM SET shared_buffers = '16GB';
```

### Prewarm after a restart {#prewarm}

<a id="usage"></a><a id="privileges"></a>

After a restart or failover, `shared_buffers` is empty and the first queries read from disk. `pg_prewarm` on the index would load every page, including the full-precision vectors, which may push out more useful pages when the index is larger than memory. vchord's own functions load only what queries need:

```sql
-- vchordrq: centroids and the RaBitQ codes of every list
SELECT vchordrq_prewarm('items_embedding_idx');

-- vchordrq: centroids only, when the lists do not fit in shared_buffers
SELECT vchordrq_prewarm('items_embedding_idx', 1);

-- vchordg: the graph's codes and neighbor lists
SELECT vchordg_prewarm('items_graph_idx');
```

Each returns a short summary of what it loaded. The caller needs `SELECT` on the table or must own it.

## Read from disk efficiently {#prefetch}

<a id="prefetch-modes"></a><a id="io-and-jit"></a>

When pages are not in memory, vchord asks for the pages it will need next before it needs them, so that storage works while the CPU computes distances. It uses PostgreSQL's read streams where they help, on PostgreSQL 17 and later, and `posix_fadvise` hints otherwise. This is on by default. On NVMe, let PostgreSQL keep more reads in flight:

```sql
SET effective_io_concurrency = 20;
SET maintenance_io_concurrency = 20;
```

The `io_search` and `io_rerank` settings in the [reference](#reference) choose how each phase of a query reads. Keep their defaults unless you are measuring; on an index that fits in `shared_buffers`, all modes perform the same.

JIT compilation adds planning time to vector queries and speeds up nothing in them. Turn it off for databases that serve vector search:

```sql
ALTER DATABASE app SET jit = off;
```

### Asynchronous I/O on PostgreSQL 18 {#asynchronous-i-o}

<a id="worker"></a><a id="io-uring"></a><a id="sync"></a>

PostgreSQL 18 performs read streams asynchronously, which lets more reads overlap. `io_method` chooses how, and needs a restart:

- `worker` (the default) hands reads to background I/O workers. Raise `io_workers` for indexes much larger than memory.
- `io_uring` submits reads directly to the Linux kernel and avoids the hand-off. It needs higher open-file and locked-memory limits for PostgreSQL, and some container runtimes block it in their default seccomp profile; fall back to `worker` there.
- `sync` turns asynchronous reads off; use it only to compare.

```sql
ALTER SYSTEM SET io_method = 'io_uring';
```

[Tuning AIO in PostgreSQL 18](https://vondra.me/posts/tuning-aio-in-postgresql-18/) explains the trade-offs in more depth.

## Reference {#reference}

### I/O settings {#io-settings}

<a id="search-parameters"></a><a id="search-parameters-vchordrq"></a><a id="search-parameters-vchordg"></a><a id="vchordrq-io-search"></a><a id="vchordrq-io-rerank"></a><a id="vchordg-io-search"></a><a id="vchordg-io-rerank"></a>

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordrq.io_search` | enum | `mixed` on PG 17+, `prefetch_buffer` on 15–16 | How list pages are read. `mixed` uses a read stream where pages mostly follow one another and `prefetch_buffer` elsewhere, or a read stream throughout when `io_method` is not `worker`. |
| `vchordrq.io_rerank` | enum | `prefetch_buffer` | How vectors and table pages are read for reranking. Reranked pages are scattered, which is why the default is not a read stream. |
| `vchordg.io_search` | enum | `read_stream` on PG 17+, `prefetch_buffer` on 15–16 | How graph pages are read during the walk. |
| `vchordg.io_rerank` | enum | `read_stream` on PG 17+, `prefetch_buffer` on 15–16 | How full-precision vectors are read for reranking. |
{.fields meta="type default"}

The values are `read_buffer` (no read-ahead), `prefetch_buffer` (`posix_fadvise` hints), and, on PostgreSQL 17 and later, `read_stream` and, for `vchordrq.io_search` only, `mixed`.

### Prewarm functions {#functions}

<a id="functions-vchordrq"></a><a id="functions-vchordg"></a><a id="vchordrq-prewarm"></a><a id="vchordg-prewarm"></a><a id="vchordrq-prewarm-func"></a><a id="vchordg-prewarm-func"></a>

| Function | Returns | Description |
| --- | --- | --- |
| `vchordrq_prewarm(index regclass, height integer DEFAULT 0)` | text | Load the index from the root down to `height`: `0` includes the RaBitQ codes of every list, `1` loads the centroids only. Full-precision vectors are never loaded. |
| `vchordg_prewarm(index regclass)` | text | Load the graph's RaBitQ codes and neighbor lists. |
{.fields meta="type"}
