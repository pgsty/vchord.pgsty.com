---
title: "External Build"
linkTitle: "External Build"
description: "Run the k-means step of a vchordrq build outside PostgreSQL, for example on a GPU, and build the index from the centroids it produces."
weight: 90
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/external-build.md"
aliases:
  - "/docs/usage/external-build/"
  - "/vectorchord/usage/external-build/"
  - "/docs/vchord/usage/external-index-precomputation/"
  - "/vectorchord/usage/external-index-precomputation/"
icon: fa-solid fa-server
---

The k-means step is the slowest and most memory-hungry part of building a large vchordrq index. An external build moves it out of the database: you train the centroids wherever you like, for example on a GPU with [Faiss](https://github.com/facebookresearch/faiss), write them to a table, and `CREATE INDEX` only assigns rows to them. Use it when the database server lacks the memory or CPU for k-means, or when you rebuild often and want to reuse centroids. Before reaching for it, try the in-database options in [Building large indexes](/docs/vchord/usage/partitioning-tuning/).

## Workflow {#workflow}

1. Sample vectors from the table. A few dozen per leaf list is enough, such as 64 × 160,000 for `lists = [400, 160000]`:

   ```sql
   CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
   SELECT embedding FROM public.items TABLESAMPLE SYSTEM_ROWS(10240000);
   ```

1. Train the centroids and turn them into rows `(id, parent, vector)`. The function below does both with Faiss; pass `gpu=True` to `Kmeans` to train on a GPU, and `spherical=True` for cosine or normalized inner-product embeddings.

   ```python
   import numpy as np
   from faiss import Kmeans


   def centroid_rows(samples, lists, spherical=False):
       """Rows (id, parent, vector) for build.external.table.

       `lists` is the index's `lists`, such as [400, 160000]. Each level is trained
       on the centroids of the level below, and each centroid's parent is its
       nearest centroid one level up.
       """
       samples = np.ascontiguousarray(samples, dtype=np.float32)
       levels, data = [], samples
       for k in reversed(lists):
           kmeans = Kmeans(samples.shape[1], k, niter=10, seed=42, spherical=spherical)
           kmeans.train(data)
           data = kmeans.centroids
           levels.append(data)
       levels.append(data.mean(axis=0, keepdims=True))  # the root
       levels.reverse()

       rows, upper, upper_ids, next_id = [], None, None, 0
       for level in levels:
           ids = np.arange(next_id, next_id + len(level))
           next_id += len(level)
           if upper is None:
               parents = [None] * len(level)
           else:
               # squared L2 distance to every centroid one level up, without a 3-D array
               d = (upper * upper).sum(axis=1) - 2 * level @ upper.T
               parents = upper_ids[d.argmin(axis=1)].tolist()
           rows += [(int(i), p, v.tolist()) for i, p, v in zip(ids, parents, level)]
           upper, upper_ids = level, ids
       return rows
   ```

1. Load the rows into a table with exactly these three columns, for example with `COPY`. A vector literal is the list written as text, such as `[0.1, 0.2, 0.3]`.

   ```sql
   CREATE TABLE public.items_centroids (
       id integer NOT NULL UNIQUE,
       parent integer,
       vector vector NOT NULL
   );
   ```

1. Build the index from it. The table name must include its schema:

   ```sql
   CREATE INDEX ON public.items USING vchordrq (embedding vector_cosine_ops)
   WITH (options = $$
   residual_quantization = true
   [build.external]
   table = 'public.items_centroids'
   $$);
   ```

   Query it as usual, with `vchordrq.probes` giving one value per level of the tree, here two.
{.steps}

## Rules for the centroid table {#format}

<a id="Format"></a><a id="schema-qualification"></a><a id="partitioning"></a><a id="Partitioning"></a>

`CREATE INDEX` and every later rebuild check the table and stop with an error if a rule is broken:

- **Columns**: `id integer NOT NULL` and unique, `parent integer` (`NULL` only for the root), and `vector vector NOT NULL` with the same dimension as the indexed column. Use `vector` even when the indexed column is `halfvec`.
- **Shape**: one root, every node reachable from it, every leaf at the same depth, and 2 to 9 levels counting the root, which matches 1 to 8 levels of `lists`.
- **Single level**: you may leave out the root and give at least two centroids with `parent = NULL`; vchordrq adds the root itself.
- **Name**: `table` must be written as `schema.table`. The build runs with a restricted `search_path`, so an unqualified name is rejected.

The index reads the table at every build, including `REINDEX`, `VACUUM FULL`, `CLUSTER`, `TRUNCATE`, and restoring a dump, so keep it as long as the index exists.
