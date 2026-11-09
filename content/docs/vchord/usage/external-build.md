---
title: "External Build"
linkTitle: "External Build"
description: "In addition to using the methods in Partitioning Tuning to achieve shorter build time and lower memory consumption at the cost of QPS and recall, you can also c"
weight: 150
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/external-build.md"
aliases:
  - "/docs/usage/external-build/"
  - "/vectorchord/usage/external-build/"
  - "/docs/vchord/usage/external-index-precomputation/"
  - "/vectorchord/usage/external-index-precomputation/"
icon: fa-solid fa-server
---

In addition to using the methods in [Partitioning Tuning](/docs/vchord/usage/partitioning-tuning/) to achieve shorter build time and lower memory consumption at the cost of QPS and recall, you can also choose to run the partitioning phase offline on other machines or on GPUs. This feature is not supported by `vchordg`, since it does not have a partitioning phase.

Assume the table is `t` and the column to be indexed is `val`.

```sql
CREATE TABLE t (val vector(3));
```

Specifically, you need to sample the column for which the index will be built.

```sql
CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
SELECT val FROM t TABLESAMPLE SYSTEM_ROWS(1000);
```

Based on these samples, you can partition the vector space into Voronoi cells. After that, you will create a table and insert your partitions.

```sql
CREATE TABLE public.t_build (id INTEGER NOT NULL UNIQUE, parent INTEGER, vector vector NOT NULL);
INSERT INTO public.t_build (id, parent, vector) VALUES (0, NULL, '[0.1, 0.2, 0.3]');
INSERT INTO public.t_build (id, parent, vector) VALUES (1, 0, '[0.1, 0.2, 0.3]');
INSERT INTO public.t_build (id, parent, vector) VALUES (2, 0, '[0.4, 0.5, 0.6]');
INSERT INTO public.t_build (id, parent, vector) VALUES (3, 0, '[0.7, 0.8, 0.9]');
```

The index can be created using the following syntax.

```sql
CREATE INDEX ON t USING vchordrq (val vector_l2_ops) WITH (options = $$
build.external.table = 'public.t_build'
$$);
```

In 1.3.0, `build.external.table` must use `schema.table`, for example `public.t_build`. Index builds use a restricted `search_path`; unqualified names are rejected instead of assuming `public`. Existing queries remain usable until an operation needs to rebuild or replace the index. This includes `REINDEX` (with or without `CONCURRENTLY`), `TRUNCATE`, `VACUUM FULL`, `CLUSTER`, column-type changes that rebuild indexes, and restoring the index from a dump. Update a legacy index before rebuilding it, preserving any other settings in its `options`:

```sql
ALTER INDEX my_index SET (options = $$
[build.external]
table = 'public.t_build'
$$);
```

Use this query to find external-build options that need review before upgrading:

```sql
SELECT c.oid::regclass AS index_name, o.option_value
FROM pg_class AS c
JOIN pg_am AS am ON am.oid = c.relam
CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
WHERE am.amname = 'vchordrq'
  AND o.option_name = 'options'
  AND o.option_value LIKE '%external%';
```

Review the returned TOML options, including both `build.external.table = ...` and `[build.external]` forms. Each external table must name both a schema and a table. Identifiers use the existing unquoted syntax and are folded to lowercase.

<a id="Format"></a>
## Format

The table that stores the partition information must strictly follow the following schema:

- The first column must be `id`. Its type is `integer`. It must not be null. It must be unique.
- The second column must be `parent`. Its type is `integer`; the root has a NULL parent.
- The third column must be `vector`. Its type is `vector`. It must not be null. `halfvec` or other types are not supported yet.

Logically, this forms a tree: the root has `parent = NULL`, and every other parent must reference an existing `id`. All nodes must be reachable from the root, and all leaves must have the same depth. The tree must have 2–9 levels including the root. Cycles, unreachable nodes, and excessive height raise errors. Centroid dimensions must match the indexed column.

A flat partition can omit the explicit root: supply at least two centroids with all `parent` values set to `NULL`, and the build generates the root automatically.

If any of the above properties are not satisfied, an error will be reported.

<a id="Partitioning"></a>
## Partitioning

To get started, here is a minimal code example for performing partitioning using [faiss](https://github.com/facebookresearch/faiss).

```python
from typing import List
from faiss import Kmeans
import numpy

def partition(
    samples: numpy.ndarray, lists: List[int]
) -> List[numpy.ndarray]:
    dim = samples.shape[1]
    results = []
    for i in range(len(lists) + 1):
        kmeans = Kmeans(
            dim,
            lists[len(lists) - 1 - i] if len(lists) - 1 - i >= 0 else 1,
            gpu=False,
            verbose=True,
            niter=10,
            seed=42,
            spherical=False,
        )
        kmeans.train(samples)
        results.append(kmeans.centroids)
        samples = kmeans.centroids
    return results
```

This computes the generators of all Voronoi cells across different levels. The parent-child relationships in the tree are determined by computing the shortest distances, but the details are omitted here. Any algorithm capable of generating multi-level Voronoi cells can be used, such as spherical K-means, balanced K-means or GPU K-means.
