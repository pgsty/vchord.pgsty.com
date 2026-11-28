---
title: "Building Large Indexes"
linkTitle: "Large Builds"
description: "Keep vchordrq builds on 100 million to billions of rows within time and memory budgets, and follow a build's progress."
weight: 80
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/partitioning-tuning.md"
math: true
aliases:
  - "/docs/usage/partitioning-tuning/"
  - "/vectorchord/usage/partitioning-tuning/"
  - "/docs/vchord/usage/monitoring/"
  - "/docs/usage/monitoring/"
  - "/vectorchord/usage/monitoring/"
icon: fa-solid fa-table-columns
---

On tables of tens of millions of rows and more, the k-means step of a vchordrq build takes most of the time and nearly all of the memory. Three options shrink it, and they combine: with all three, 100 million 768-dimensional vectors build in 18 minutes using 6 GiB. To move k-means off the database server entirely, see [External build](/docs/vchord/usage/external-build/).

## Where the time and memory go {#where}

k-means trains on `sampling_factor` sampled vectors per leaf list. With the standard algorithm, its working memory is about

\[
4 \cdot D \cdot C \cdot (F + T + 1) \text{ bytes}
\]

and its time grows with \(F \cdot C^2 \cdot D\), where \(C\) is the number of leaf lists (the last value of `lists`), \(D\) the dimension used for clustering, \(F\) the `sampling_factor`, and \(T\) the `build_threads`. Each option below shrinks one of these terms.

If k-means does not fit in memory, the build stops with an `out of memory` error and the server keeps running.

## Hierarchical k-means {#hierarchical-k-means}

With a two-level `lists`, hierarchical k-means clusters the coarse level first and then each coarse cluster separately. Time grows with \(C^{1.5}\) instead of \(C^2\), with little effect on recall:

```toml
[build.internal]
lists = [400, 160000]
kmeans_algorithm = { hierarchical = {} }
```

## Sample fewer vectors {#reduce-sampling-factor}

Lowering `sampling_factor` from its default of `256` reduces time and memory in proportion, at the cost of slightly less accurate centroids:

```toml
[build.internal]
sampling_factor = 64
```

## Cluster in fewer dimensions {#dimensionality-reduction}

`kmeans_dimension` clusters vectors reduced to that many dimensions and expands the centroids back to full size afterwards. For 768-dimensional embeddings, `100` cuts k-means work by nearly 8×. A value at or above the column's dimension is ignored with a warning.

```toml
[build.internal]
kmeans_dimension = 100
```

## Reference configurations {#reference-settings}

### LAION-100M {#laion-100m}

100 million 768-dimensional vectors, inner product, from [SISAP 2024](https://sisap-challenges.github.io/2024/datasets/). Built on an AWS `i7i.4xlarge` (16 vCPUs, 128 GiB RAM, local NVMe) in **18 minutes** with **6 GiB** of peak build memory. At `probes = '40,140'` and `epsilon = 1.4`, it serves 120 queries per second at 0.949 top-10 recall.

```sql
CREATE INDEX ON laion USING vchordrq (embedding vector_ip_ops)
WITH (options = $$
build.pin = 2
[build.internal]
lists = [400, 160000]
build_threads = 16
spherical_centroids = true
kmeans_algorithm = { hierarchical = {} }
kmeans_dimension = 100
sampling_factor = 64
$$);
```

### DEEP-1B {#deep-1b}

1 billion 96-dimensional vectors, L2 distance, from [BIG-ANN](https://big-ann-benchmarks.com/neurips21.html). Built on an AWS `i7ie.6xlarge` (24 vCPUs, 192 GiB RAM, local NVMe) in **107 minutes** with **64 GiB** of peak build memory. At `probes = '40,250'`, it serves 68 queries per second at 0.951 top-10 recall.

```sql
CREATE INDEX ON deep USING vchordrq (embedding vector_l2_ops)
WITH (options = $$
residual_quantization = true
build.pin = 2
[build.internal]
lists = [800, 640000]
build_threads = 24
kmeans_algorithm = { hierarchical = {} }
$$);
```

## Monitor a build {#monitoring}

<a id="phases"></a><a id="Phases"></a><a id="phases-vchordrq"></a><a id="phases-vchordg"></a><a id="catalog-statistics"></a>

Both index types report progress in PostgreSQL's [`pg_stat_progress_create_index`](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING) view:

```sql
SELECT phase, tuples_done, tuples_total,
       round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS blocks_pct
FROM pg_stat_progress_create_index;
```

A vchordrq build goes through these phases. The k-means phase reports its own percentage in the phase name; inserting rows is usually the longest.

| Phase | What happens |
| --- | --- |
| `initializing` | Options are checked. |
| `initializing index, by internal build (n %)` | k-means runs on the sample. `by default build` and `by external build` replace it when there is a single list or precomputed centroids. |
| `initializing index` | Centroids are written to the index. |
| `inserting tuples from table to index` | Every row is quantized and appended to its list; `tuples_done` and `blocks_done` advance. |
| `compacting tuples in index` | The lists are compacted. |

A vchordg build has two phases: `initializing`, then `inserting tuples from table to index`.
