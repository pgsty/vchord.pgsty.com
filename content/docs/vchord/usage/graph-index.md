---
title: "vchordg Index"
linkTitle: "vchordg Index"
description: "When to use the vchordg graph index, how much memory it needs, and how to tune its build and search parameters."
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/graph-index.md"
aliases:
  - "/docs/usage/graph-index/"
  - "/vectorchord/usage/graph-index/"
icon: fa-solid fa-diagram-project
---

`vchordg` is vchord's graph index. Like pgvector's HNSW, a query walks a graph of neighboring vectors, so there are no lists to size and recall is good with the defaults. Unlike HNSW, the walk compares RaBitQ codes of 1 or 2 bits per dimension instead of full vectors, which are read only to rerank the final candidates. The part of the index every query touches is therefore a fraction of the table's size. Use it when that part fits in memory and you want low latency without tuning `lists`; use [`vchordrq`](/docs/vchord/usage/indexing/) for tables that do not fit, and for filter keys, multi-vector columns, or external builds.

## How it works {#how-it-works}

A query starts at an entry vertex and repeatedly moves to the neighbors closest to the query vector, keeping the best `ef_search` candidates it has seen. Distances along the way come from the RaBitQ codes. The candidates are then reranked with exact distances, read from the full-precision vectors, and returned in order.

Each inserted row links to at most `m` neighbors, chosen by a search with `ef_construction` candidates. Larger values give a better graph and better recall at the same `ef_search`, at the cost of a slower build and a larger index.

## Create an index {#create}

Operator classes are the same as for vchordrq: `vector_l2_ops`, `vector_ip_ops`, `vector_cosine_ops`, and their `halfvec`, `rabitq8`, and `rabitq4` versions. See the [full list](#operator-classes).

```sql
CREATE INDEX ON items USING vchordg (embedding vector_cosine_ops);

SET vchordg.ef_search = 100;
SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;
```

On PostgreSQL 17 and later the build uses parallel workers; see [PostgreSQL tuning](/docs/vchord/usage/postgresql-tuning/#parallel-index-builds).

## Size the memory {#memory}

<a id="Tuning"></a><a id="tuning"></a>

vchordg is fast while the RaBitQ codes stay in `shared_buffers` or the OS page cache. With the default `bits = 2`, a 768-dimensional vector takes 192 bytes of codes, so 10 million rows need about 1.8 GiB, plus the neighbor lists.

If that does not fit, set `bits = 1` to halve it. Recall at the same `ef_search` drops a little, which you can win back with a higher `ef_search`:

```sql
CREATE INDEX ON items USING vchordg (embedding vector_cosine_ops)
WITH (options = $$
bits = 1
$$);
```

After a restart, [`vchordg_prewarm`](/docs/vchord/usage/postgresql-tuning/#prewarm) loads the codes back into `shared_buffers`. If the graph lives on SSD rather than in memory, `vchordg.beam_search` (and `beam_construction` at build time) expands several vertices per step so their reads overlap; keep both at `1` when the graph is in memory.

## Tune recall and speed {#tune}

`vchordg.ef_search` is the one query-time knob: higher means better recall and slower queries. Start at the default `64`, [measure recall](/docs/vchord/usage/measure-recall/#vchordg) on real queries, and raise it until you reach your target. Store the value on the index so every session uses it:

```sql
ALTER INDEX items_embedding_idx SET (ef_search = 128);
```

If recall stays short even at a high `ef_search`, rebuild with larger `m` (for example `64`) and `ef_construction` (for example `128`), which helps most on high-dimensional embeddings.

## Filters {#filters}

<a id="querying-and-maintenance"></a>

`WHERE` conditions are checked after the graph search, on the rows it returns. A selective filter therefore needs a large `ef_search` to return enough rows, and a filter that matches almost nothing can make the scan walk most of the graph; `vchordg.max_scan_tuples` caps that. For tenant or category filters on large tables, vchordrq [filter keys](/docs/vchord/usage/filtering/#filter-keys) are the better fit. Distance range conditions work as on vchordrq; see [Filtering](/docs/vchord/usage/filtering/#distance-range).

## Keep the index healthy {#maintenance}

Autovacuum removes deleted rows from the graph, repairs the links around them, and reuses their space. Repair is local, so after deleting a large share of the table, [measure recall](/docs/vchord/usage/measure-recall/#vchordg) again; if it dropped, rebuild online:

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
```

## Result order {#result-order}

The scan returns rows while it is still exploring the graph, so a slightly nearer row found later can come after a farther one. A larger `ef_search` makes this rarer. When an application needs strict distance order, overfetch and sort in SQL:

```sql
SELECT * FROM (
    SELECT id, embedding <=> '[3, 1, 2]' AS distance
    FROM items
    ORDER BY embedding <=> '[3, 1, 2]'
    LIMIT 100
) AS candidates
ORDER BY distance
LIMIT 10;
```

## Reference {#reference}

### Operator classes {#operator-classes}

| Column type | L2 `<->` | Inner product `<#>` | Cosine `<=>` |
| --- | --- | --- | --- |
| `vector` | `vector_l2_ops` | `vector_ip_ops` | `vector_cosine_ops` |
| `halfvec` | `halfvec_l2_ops` | `halfvec_ip_ops` | `halfvec_cosine_ops` |
| `rabitq8` | `rabitq8_l2_ops` | `rabitq8_ip_ops` | `rabitq8_cosine_ops` |
| `rabitq4` | `rabitq4_l2_ops` | `rabitq4_ip_ops` | `rabitq4_cosine_ops` |

Each class also serves the matching [range operator](/docs/vchord/usage/filtering/#distance-range). Indexed columns can have 1 to 30,000 dimensions.

### Index options {#indexing-options}

<a id="bits"></a><a id="m"></a><a id="ef-construction"></a><a id="alpha"></a><a id="beam-construction"></a>

Set in the `options` TOML string of `CREATE INDEX`. Changing them requires a rebuild.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `bits` | integer | `2` | RaBitQ bits per dimension, `1` or `2`. `1` halves memory at some loss of recall. |
| `m` | integer | `32` | Most neighbors per vertex, up to `512`. Higher improves recall on high-dimensional data; costs build time and space. |
| `ef_construction` | integer | `64` | Candidates kept while inserting a row. Higher builds a better graph, more slowly. |
| `alpha` | float array | `[1.0, 1.2]` | Pruning thresholds for choosing neighbors, ascending, starting at `1.0`, each below `2.0`. `[1.0]` prunes like HNSW. Applies to L2 and cosine. |
| `beam_construction` | integer | `1` | Vertices expanded per step while inserting. Raise only when the graph is on SSD. |
{.fields meta="type default"}

### Search parameters {#search-parameters}

<a id="vchordg-enable-scan"></a><a id="vchordg-ef-search"></a><a id="search-parameters-vchordg-ef-search"></a><a id="vchordg-beam-search"></a><a id="vchordg-max-scan-tuples"></a>

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordg.ef_search` | integer | `64` | Candidates kept during the search. Higher improves recall and order, slows queries. Can be [stored on the index](/docs/vchord/usage/fallback-parameters/). |
| `vchordg.beam_search` | integer | `1` | Vertices expanded per step. Raise only when the graph is on SSD. |
| `vchordg.max_scan_tuples` | integer | `-1` | Stop after returning this many rows to the executor, so a filter that matches almost nothing cannot walk the whole graph. `-1` means no limit. |
| `vchordg.enable_scan` | boolean | `on` | Let the planner use vchordg indexes. Turn off to compute exact results. |
{.fields meta="type default"}

`vchordg.io_search` and `vchordg.io_rerank` choose how pages are read; see [PostgreSQL tuning](/docs/vchord/usage/postgresql-tuning/#prefetch).
