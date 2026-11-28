---
title: "vchordrq Index"
linkTitle: "vchordrq Index"
description: "How the vchordrq IVF + RaBitQ index answers a query, how to size it for your table, and how to trade recall for speed."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/indexing.md"
aliases:
  - "/docs/usage/indexing/"
  - "/vectorchord/usage/indexing/"
  - "/docs/vchord/usage/rerank-in-table/"
  - "/docs/usage/rerank-in-table/"
  - "/vectorchord/usage/rerank-in-table/"
icon: fa-solid fa-sitemap
---

`vchordrq` is vchord's main index. It keeps memory small and builds fast by searching only a few groups of vectors per query, which makes it the default choice for large tables and for anything that does not fit in RAM. For a graph index that needs no list sizing, see [`vchordg`](/docs/vchord/usage/graph-index/).

## How it works {#how-it-works}

At build time, vchordrq clusters a sample of your vectors with k-means. Each centroid owns a **list**. Every row's vector is stored twice: as a RaBitQ code, a few bits per dimension wide, in the list of its nearest centroid, and at full precision for the final step of a query.

A query then runs in three steps:

1. **Route.** Pick the `probes` lists whose centroids are nearest to the query vector.
1. **Estimate.** Scan the RaBitQ codes in those lists. Each code gives an estimated distance with a known error bound. `epsilon` sets how wide that bound is taken to be.
1. **Rerank.** Compute exact distances for the candidates that could still be among the nearest, and return rows in exact distance order as soon as they are settled.
{.steps}

Recall is lost in two places, and each has its own knob:

- A true neighbor lives in a list that was not probed. Raise **`probes`**.
- A true neighbor's estimate was pessimistic, so it was reranked too late to make the `LIMIT`. Raise **`epsilon`**.

Both knobs are query-time settings, so you can tune them without rebuilding.

## Create an index {#create}

Pick the operator class that matches the distance operator your queries use. The [reference](#operator-classes) lists every type.

| Distance | Query operator | Operator class for `vector` |
| --- | --- | --- |
| Euclidean (L2) | `<->` | `vector_l2_ops` |
| Negative inner product | `<#>` | `vector_ip_ops` |
| Cosine | `<=>` | `vector_cosine_ops` |

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops)
WITH (options = $$
residual_quantization = true
[build.internal]
lists = [2000]
spherical_centroids = true
build_threads = 8
$$);
```

`options` is a [TOML](https://toml.io/) document. For most embedding models, which use cosine or normalized inner product, `residual_quantization` and `spherical_centroids` improve both recall and speed, so the example turns them on. Without any options, the index has a single list, which suits tables under 100,000 rows.

Queries need no changes: any `ORDER BY embedding <=> $1 LIMIT k` on the column uses the index.

```sql
SET vchordrq.probes = '20';
SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;
```

## Choose `lists` {#lists}

<a id="partitioning"></a>

More lists mean smaller lists and fewer vectors scanned per probe, at the cost of a longer k-means step at build time. Size `lists` from the row count `N` you expect the table to have:

| Rows `N` | Lists | Example |
| --- | --- | --- |
| under 100,000 | one list | `[]` (the default) |
| 100,000 to 2 million | `N / 500` | 1M rows: `[2000]` |
| 2 million to 50 million | `4√N` to `8√N` | 10M rows: `[20000]` |
| over 50 million | `8√N` to `16√N`, or two levels | 100M rows: `[160000]` or `[400, 160000]` |

A two-level `lists` builds a tree: the query first picks among 400 coarse centroids, then among the leaf lists under them. `probes` then takes one value per level, such as `'40,140'`. Above 50 million rows, also read [Partitioning tuning](/docs/vchord/usage/partitioning-tuning/) to keep the build within memory.

## Tune recall and speed {#tuning}

Tune against real queries and a recall target, not by feel:

1. Keep `epsilon` at its default of `1.9`.
1. Start `probes` near 1% of `lists`: `'20'` for `[2000]`.
1. Measure recall on a sample of real queries with [`vchordrq_evaluate_query_recall`](/docs/vchord/usage/measure-recall/).
1. Below target: raise `probes`. Comfortably above target: lower `probes`, then try lowering `epsilon` for more speed. The LAION-100M reference run uses `epsilon = 1.4`.
1. Store the result on the index so every session and connection pooler gets it:

   ```sql
   ALTER INDEX items_embedding_idx SET (probes = '20', epsilon = 1.9);
   ```

   A `SET vchordrq.probes` in a session still overrides it. See [Fallback parameters](/docs/vchord/usage/fallback-parameters/).
{.steps}

## Filter with filter keys {#filter-keys}

A `WHERE` clause works with any vchordrq index, but a selective one breaks down: if tenant 42 owns 0.1% of the table, the probed lists may hold only a handful of its rows, and `LIMIT 10` comes back short. Add the filter column to the index after the vector column. The index then checks the condition inside each list and reads more lists until it has enough rows:

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops, tenant_id)
WITH (options = $$
[build.internal]
lists = [2000]
spherical_centroids = true
$$);

SELECT id FROM items
WHERE tenant_id = 42
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

Supported key types and conditions, hashed keys, and how to cap the extra lists read are in [Filtering](/docs/vchord/usage/filtering/#filter-keys), together with prefilter and distance ranges.

## Make the index smaller {#index-size}

By default the index stores each vector twice, as a RaBitQ code and as a full-precision copy for reranking, so it takes a little more space than the vectors in the table. Two ways to shrink it:

- `rerank_in_table = true` leaves the full-precision copies out, and reranking reads the vectors from the table instead. The index shrinks to little more than the codes, but queries get slower, because reranking now reads scattered table pages, and TOAST for wide vectors, instead of the index's own pages. Multi-vector indexes do not support it.
- Store the column as `halfvec`, `rabitq8`, or `rabitq4`. This shrinks the table and the index together; see [Quantized types](/docs/vchord/usage/quantization-types/).

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops)
WITH (options = $$
rerank_in_table = true
residual_quantization = true
[build.internal]
lists = [2000]
spherical_centroids = true
$$);
```

## Build large tables faster {#build}

A build has two phases: k-means on a sample, then inserting every row into its list. Each phase has its own way to go faster:

- **k-means** uses `build_threads` threads. For tens of millions of rows and more, [Partitioning tuning](/docs/vchord/usage/partitioning-tuning/) cuts its time and memory, and an [external build](/docs/vchord/usage/external-build/) moves it to a GPU.
- **Insertion** uses PostgreSQL parallel workers on PostgreSQL 17 and later. Set `max_parallel_maintenance_workers` as described in [PostgreSQL tuning](/docs/vchord/usage/postgresql-tuning/#parallel-index-builds).
- `build.pin = 2` keeps the centroids pinned in shared memory during insertion, which speeds it up when `shared_buffers` has room.

Follow a running build in `pg_stat_progress_create_index`; [Large builds](/docs/vchord/usage/partitioning-tuning/#monitoring) explains its phases.

## Keep the index healthy {#maintenance}

New rows go into the list of their nearest centroid, and the centroids never move. Autovacuum compacts the lists and removes deleted rows, so day-to-day writes need nothing extra.

Rebuild when the data has drifted from what the centroids were trained on, for example after the table has grown several times over since the build:

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
```

## Result order {#result-order}

Rows come back sorted by exact distance in almost every case. Three things can put a row slightly out of place:

- Its RaBitQ estimate was pessimistic, so it was reranked after a slightly farther row. A higher `epsilon` makes this rarer.
- It was found in a later [filter key](/docs/vchord/usage/filtering/#filter-keys) expansion round.
- The column is `halfvec`, and the index rounds its distances to half precision.

When an application needs strict SQL order, overfetch and sort in SQL:

```sql
SELECT * FROM (
    SELECT id, embedding <=> '[3, 1, 2]' AS distance
    FROM items
    WHERE tenant_id = 42
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

Each of these classes also serves the matching [range operator](/docs/vchord/usage/filtering/#distance-range) (`<<->>`, `<<#>>`, `<<=>>`). Arrays of each type use `vector_maxsim_ops`, `halfvec_maxsim_ops`, `rabitq8_maxsim_ops`, or `rabitq4_maxsim_ops` with the `@#` operator; see [Multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/). Indexed columns can have 1 to 60,000 dimensions.

### Index options {#indexing-options}

<a id="residual-quantization"></a><a id="rerank-in-table"></a><a id="degree-of-parallelism"></a><a id="build-pin"></a><a id="default-build-options"></a><a id="internal-build-options"></a><a id="build-internal-lists"></a><a id="build-internal-spherical-centroids"></a><a id="build-internal-sampling-factor"></a><a id="build-internal-kmeans-iterations"></a><a id="build-internal-build-threads"></a><a id="build-internal-kmeans-algorithm"></a><a id="build-internal-kmeans-dimension"></a>

Set in the `options` TOML string of `CREATE INDEX ... WITH (options = $$ ... $$)`. Changing them requires a rebuild.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `residual_quantization` | boolean | `false` | Quantize each vector relative to its list's centroid. Improves recall for most datasets. Not available for `rabitq8` and `rabitq4` columns. |
| `rerank_in_table` | boolean | `false` | Leave full-precision vectors out of the index and read them from the table to rerank. Smaller index, slower queries. See [Make the index smaller](#index-size). |
| `build.pin` | integer | `-1` | Pin centroids in shared memory while inserting: `2` pins every level, `1` the upper levels, `-1` none. |
| `degree_of_parallelism` | integer | `32` | Raise it (up to `256`) when more than 32 sessions insert into the index at the same time. |
| `zone_maps` | integer | `2` | How many leading filter key columns keep per-block minimum and maximum values, so range conditions can skip blocks. |
| `build.internal.lists` | integer array | `[]` | Lists per level, ascending, up to 8 levels. See [Choose `lists`](#lists). |
| `build.internal.spherical_centroids` | boolean | `false` | Normalize centroids. Turn on for cosine and normalized inner-product embeddings. |
| `build.internal.build_threads` | integer | `1` | Threads for k-means, up to `255`. |
| `build.internal.sampling_factor` | integer | `256` | Vectors sampled per list for k-means. Lower it to cut build time and memory. |
| `build.internal.kmeans_iterations` | integer | `10` | k-means iterations. |
| `build.internal.kmeans_algorithm` | table | `lloyd` | `{ hierarchical = {} }` makes two-level `lists` build much faster. |
| `build.internal.kmeans_dimension` | integer | unset | Run k-means on vectors reduced to this many dimensions. |
| `build.external.table` | string | unset | Schema-qualified table of precomputed centroids. See [External build](/docs/vchord/usage/external-build/). |
{.fields meta="type default"}

### Search parameters {#search-parameters}

<a id="vchordrq-probes"></a><a id="search-parameters-vchordrq-probes"></a><a id="vchordrq-epsilon"></a><a id="search-parameters-vchordrq-epsilon"></a><a id="vchordrq-max-scan-tuples"></a><a id="vchordrq-enable-scan"></a>

Set per session with `SET`, per role or database with `ALTER ROLE` / `ALTER DATABASE`, or on the index itself for `probes` and `epsilon`.

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordrq.probes` | string | `''` | Lists to probe, one comma-separated value per level of `lists`, such as `'40,140'`. Empty for a single-list index. |
| `vchordrq.epsilon` | real | `1.9` | Width of the RaBitQ error bound, from `0` to `4`. Higher reranks more candidates: better recall, slower queries. |
| `vchordrq.max_probes` | integer | `-1` | Most lists a [filter key](/docs/vchord/usage/filtering/#filter-keys) scan may read once its probed lists run out. `-1` means no limit; `0` reads only `probes`. |
| `vchordrq.max_scan_tuples` | integer | `-1` | Stop the scan after this many candidates, so a query with a filter almost no row passes cannot read the whole index. `-1` means no limit. |
| `vchordrq.enable_scan` | boolean | `on` | Let the planner use vchordrq indexes. Turn off to compare with an exact scan. |
{.fields meta="type default"}

Settings for specific features are documented with them: `vchordrq.prefilter` in [Filtering](/docs/vchord/usage/filtering/#prefilter), `vchordrq.io_search` and `vchordrq.io_rerank` in [PostgreSQL tuning](/docs/vchord/usage/postgresql-tuning/#prefetch), `vchordrq.maxsim_refine` and `vchordrq.maxsim_threshold` in [Multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/), and the `vchordrq.query_sampling_*` settings in [Measure recall](/docs/vchord/usage/measure-recall/).
