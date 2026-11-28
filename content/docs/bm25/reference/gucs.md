---
title: "Settings and Index Options"
linkTitle: "Settings"
description: "The bm25.* settings, the storage options of a bm25 index, and which one applies when both are set."
weight: 20
icon: fa-solid fa-sliders
---

Query behavior is controlled by three `bm25.*` settings, two of which also exist as per-index options; build and maintenance behavior by index options alone. [Querying](/docs/bm25/usage/querying/#how-a-query-runs) explains the scan these values tune.

## Settings {#settings}

Any user can change these with `SET`; set defaults with `ALTER ROLE ... SET`, `ALTER DATABASE ... SET`, or in `postgresql.conf`. Quote `"bm25.limit"` in `SET`, because `LIMIT` is a reserved word.

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `bm25.enable_scan` | boolean | `on` | Lets the planner use bm25 index scans. Off, PostgreSQL scores every row and sorts, with identical scores; use it as a reference when testing. |
| `bm25.limit` | integer | `100` | Rows in the first batch of an index scan, `0` to `65535`; `0` means 100. Each further batch is twice as large. A batch at least as large as `LIMIT + OFFSET` avoids a second pass; a larger one skips fewer posting blocks. See [Size the batch](/docs/bm25/usage/querying/#batch-size). |
| `bm25.prefilter` | boolean | `off` | Checks row visibility and the `WHERE` clause before a candidate enters a batch. Faster for selective filters, slower for filters most rows pass, because each competitive candidate costs a table read. See [Prefiltering](/docs/bm25/usage/filtering/#prefilter). |
{.fields meta="type default"}

## Precedence {#precedence}

`bm25.limit` and `bm25.prefilter` have index options of the same purpose, `limit` and `prefilter`. Once a setting is given any value, in `postgresql.conf`, `ALTER DATABASE`, `ALTER ROLE`, connection options, or `SET`, even its default value, it applies to every index. Only while nothing sets it does each index use its own option. `RESET` returns to whatever the configuration sets, not necessarily to the index option.

Store tuned values on the index and leave the settings unset, so each index keeps its own.

## Index options {#index-options}

Set with `CREATE INDEX ... WITH (...)` or `ALTER INDEX ... SET (...)`; remove with `ALTER INDEX ... RESET (...)`.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `options` | TOML string | `k1 = 1.2` and `b = 0.75` | BM25 parameters. `k1`, from 1.2 to 2.0, sets how quickly repeated terms stop adding to the score; `b`, from 0 to 1, sets how strongly long documents are penalized. Read at build time: after changing it, `REINDEX`. See [Choose k1 and b](/docs/bm25/usage/indexing/#scoring-parameters). |
| `limit` | integer | `100` | First batch size for this index, `0` to `65535`; `0` means 100. Used while `bm25.limit` is not set. |
| `prefilter` | boolean | `off` | Prefiltering for this index. Used while `bm25.prefilter` is not set. |
| `maintenance_min_rows` | integer | `1000` | Fewest rows the growing segment must hold before `VACUUM` merges it, from `0` to `2147483647`. |
| `maintenance_scale_factor` | real | `0.1` | From `0` to `1`. `VACUUM` merges when the growing segment reaches this fraction of the merged rows (and `maintenance_min_rows`), or when deleted rows reach this fraction of all rows. Lower values merge more often: faster queries and fresher statistics for more `VACUUM` work. |
| `shared_corpus_stats` | boolean | `off` | Lets roles under row-level security score against the statistics of the whole index. Scores then reveal how common terms are in rows those roles cannot read. See [Privileges and row-level security](/docs/bm25/usage/filtering/#access-control). Reset it before [downgrading](/docs/bm25/reference/migration/#downgrade) below 1.3.0. |
{.fields meta="type default"}

`options` takes TOML, one key per line:

```sql
CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops)
WITH (options = $$
k1 = 1.5
b = 0.6
$$, limit = 200);
```

Changing `options`, `limit`, `prefilter`, or `shared_corpus_stats` with `ALTER INDEX` takes an `ACCESS EXCLUSIVE` lock on the index, which waits for running queries that use it and blocks new ones until it commits. The two maintenance options take a `SHARE UPDATE EXCLUSIVE` lock.
