---
title: "Indexing"
linkTitle: "Indexing"
description: "VectorChord's index type vchordrq divides vectors into lists and searches only a subset of lists closest to the query vector. It provides fast build time and lo"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/indexing.md"
math: true
aliases:
  - "/docs/usage/indexing/"
  - "/vectorchord/usage/indexing/"
icon: fa-solid fa-sitemap
---

VectorChord's index type `vchordrq` divides vectors into lists and searches only a subset of lists closest to the query vector. It provides fast build time and low memory consumption, while delivering [significantly better performance](/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/#ivf-vs-hnsw) than both `hnsw` and `ivfflat`.

Let's start by creating a table named `items` with an `embedding` column of type `vector(n)`, and then populate it with sample data.

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
```

To create a `vchordrq` index, you can use the following SQL.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);
```

After the index is built, you can perform a vector search using it to retrieve the \(10\) nearest neighbors to a vector.

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

You can also add filters to vector search queries as needed.

```sql
SELECT * FROM items WHERE id % 7 <> 0 ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

<a id="Tuning"></a>
## Tuning

When there are less than \(100,000\) rows in the table, you usually don't need to set the index options.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

However, as the number of rows grows, partitioning becomes necessary and can be configured using index options. `options` are specified using a [TOML: Tom's Obvious Minimal Language](https://toml.io/) string. You can refer to [#Index Options](#indexing-options) for more information.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
[build.internal]
lists = [1000]
$$);

SET vchordrq.probes TO '10';
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

The parameter `lists` should be tuned based on the number of rows. The following table provides guidelines for choosing an appropriate value. When querying, choose `vchordrq.probes` accordingly.

| Number of Rows \(N\)                     | Recommended Number of Partitions \(L\) | Example `lists` |
| -------------------------------------- | ------------------------------------ | --------------- |
| \(N \in [0, 10^5)\)                      | N/A                                  | `[]`            |
| \(N \in [10^5, 2 \times 10^6)\)          | \(L = \frac{N}{500}\)                  | `[2000]`        |
| \(N \in [2 \times 10^6, 5 \times 10^7)\) | \(L \in [4 \sqrt{N}, 8 \sqrt{N}]\)     | `[10000]`       |
| \(N \in [5 \times 10^7, \infty)\)        | \(L \in [8 \sqrt{N}, 16\sqrt{N}]\)     | `[80000]`       |
{.wide .expand}

The process of building an index involves two steps: partitioning the vector space first, and then inserting rows into the index. The first step, partitioning the vector space, can be sped up using multiple threads.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
[build.internal]
lists = [1000]
build_threads = 8
$$);

SET vchordrq.probes TO '10';
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

The second step, inserting rows, can be parallelized using multiple processes. Refer to [PostgreSQL Tuning](/docs/vchord/usage/postgresql-tuning/).

For most datasets using cosine similarity, enabling `residual_quantization` and `build.internal.spherical_centroids` improves both QPS and recall.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops) WITH (options = $$
residual_quantization = true
[build.internal]
lists = [1000]
spherical_centroids = true
build_threads = 8
$$);

SET vchordrq.probes TO '10';
SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 10;
```

To improve the build speed, you may opt to use more shared memory to accelerate the process by setting `build.pin` to `2`.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
residual_quantization = true
build.pin = 2
[build.internal]
lists = [1000]
spherical_centroids = true
build_threads = 8
$$);
```

For large tables, time and memory overhead are dominated by the partitioning phase. See [Partitioning Tuning](/docs/vchord/usage/partitioning-tuning/) for further tuning.

You can also refer to [External Build](/docs/vchord/usage/external-build/) to offload the partitioning phase to other machines.

<a id="Reference"></a>
## Reference

### Operator Classes (`vchordrq`) {#operator-classes}

{{< badge text="vchordrq" tone="neutral" >}}

The following table lists all available operator classes supported by `vchordrq`.

| Operator Class       | Description                                                     | Operator 1                | Operator 2               |
| -------------------- | --------------------------------------------------------------- | ------------------------- | ------------------------ |
| `vector_l2_ops`      | index works for `vector` type and Euclidean distance            | `<->(vector,vector)`      | `<<->>(vector,vector)`   |
| `vector_ip_ops`      | index works for `vector` type and negative inner product        | `<#>(vector,vector)`      | `<<#>>(vector,vector)`   |
| `vector_cosine_ops`  | index works for `vector` type and cosine distance               | `<=>(vector,vector)`      | `<<=>>(vector,vector)`   |
| `halfvec_l2_ops`     | index works for `halfvec` type and Euclidean distance           | `<->(halfvec,halfvec)`    | `<<->>(halfvec,halfvec)` |
| `halfvec_ip_ops`     | index works for `halfvec` type and negative inner product       | `<#>(halfvec,halfvec)`    | `<<#>>(halfvec,halfvec)` |
| `halfvec_cosine_ops` | index works for `halfvec` type and cosine distance              | `<=>(halfvec,halfvec)`    | `<<=>>(halfvec,halfvec)` |
| `rabitq8_l2_ops`     | index works for `rabitq8` type and Euclidean distance           | `<->(rabitq8,rabitq8)`    | `<<->>(rabitq8,rabitq8)` |
| `rabitq8_ip_ops`     | index works for `rabitq8` type and negative inner product       | `<#>(rabitq8,rabitq8)`    | `<<#>>(rabitq8,rabitq8)` |
| `rabitq8_cosine_ops` | index works for `rabitq8` type and cosine distance              | `<=>(rabitq8,rabitq8)`    | `<<=>>(rabitq8,rabitq8)` |
| `rabitq4_l2_ops`     | index works for `rabitq4` type and Euclidean distance           | `<->(rabitq4,rabitq4)`    | `<<->>(rabitq4,rabitq4)` |
| `rabitq4_ip_ops`     | index works for `rabitq4` type and negative inner product       | `<#>(rabitq4,rabitq4)`    | `<<#>>(rabitq4,rabitq4)` |
| `rabitq4_cosine_ops` | index works for `rabitq4` type and cosine distance              | `<=>(rabitq4,rabitq4)`    | `<<=>>(rabitq4,rabitq4)` |
| `vector_maxsim_ops`  | index works for `vector[]` type and scalable vector-similarity  | `@#(vector[],vector[])`   | N/A                      |
| `halfvec_maxsim_ops` | index works for `halfvec[]` type and scalable vector-similarity | `@#(halfvec[],halfvec[])` | N/A                      |
| `rabitq8_maxsim_ops` | index works for `rabitq8[]` type and scalable vector-similarity | `@#(rabitq8[],rabitq8[])` | N/A                      |
| `rabitq4_maxsim_ops` | index works for `rabitq4[]` type and scalable vector-similarity | `@#(rabitq4[],rabitq4[])` | N/A                      |
{.wide .expand}

`<->`, `<#>` and `<=>` are operators defined by pgvector.

| Name  | Description                |
| ----- | -------------------------- |
| `<->` | Euclidean distance |
| `<#>` | negative dot product       |
| `<=>` | cosine distance            |

`<<->>`, `<<#>>`, `<<=>>` are operators defined by VectorChord. For more information about `<<->>`, `<<#>>`, `<<=>>`, refer to [Similarity Filter](/docs/vchord/usage/similarity-filter/).

`@#` is an operator defined by VectorChord. For more information about `@#`, refer to [Multi-Vector Retrieval](/docs/vchord/usage/multi-vector-retrieval/).

`rabitq8`, `rabitq4` are types defined by VectorChord. For more information about `rabitq8`, `rabitq4`, refer to [Quantization Types](/docs/vchord/usage/quantization-types/).

The operator classes for `MaxSim` are available since version `0.3.0`. The operator classes for `rabitq8` and `rabitq4` are available since version `1.1.0`.

> [!NOTE]
> With `halfvec_cosine_ops`, the index normalizes vectors in half precision. Two rows whose cosine distances differ by about 0.0001 or less can therefore be returned in the opposite order of their `<=>` values, with `rerank_in_table` as well. If strict order matters, re-sort the candidates as shown in [Graph Index: Result order](/docs/vchord/usage/graph-index/#result-order). This is tracked in [pgsty/vchord#17](https://github.com/pgsty/vchord/issues/17).

### Indexing Options (`vchordrq`) {#indexing-options}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="residual-quantization"></a>
#### `residual_quantization`

- Description: This option determines whether residual quantization is used. If you are not familiar with residual quantization, you can read this [blog](https://drscotthawley.github.io/blog/posts/2023-06-12-RVQ.html) for more information. In short, residual quantization is a technique that improves the accuracy of vector search by quantizing the residuals of the vectors.
- Type: boolean
- Default: `false`
- Example:
    - `residual_quantization = false` means that residual quantization is not used.
    - `residual_quantization = true` means that residual quantization is used.
- Note: This option is not supported for `rabitq8` and `rabitq4`.

<a id="degree-of-parallelism"></a>
#### `degree_of_parallelism`

{{< badge text="since v1.0.0" tone="info" >}}

- Description: This option is a hint that specifies the degree of parallelism. In most cases, you do not need to change it. If you are using a CPU with more than `32` threads and wish to utilize more threads for PostgreSQL, you may set it to the number of threads for better performance.
- Type: integer
- Default: `32`
- Domain: `[1, 256]`
- Example:
    - `degree_of_parallelism = 32` hints to the index that `32` or less processes may access on the index concurrently.
    - `degree_of_parallelism = 64` hints to the index that `64` or less processes may access on the index concurrently.

<a id="build-pin"></a>
#### `build.pin`

{{< badge text="since v0.2.1" tone="info" >}}

- Description: This option determines whether shared memory is used for indexing. For large tables, you can choose to enable this option to speed up the build process.
- Type: union of integer and boolean
- Default:
    - `-1` {{< badge text="since v1.0.0" tone="info" >}}
    - `false` {{< badge text="until v0.5.3" tone="info" >}}
- Domain:
    - `{-1, 0, 1, 2, false, true}` {{< badge text="since v1.0.0" tone="info" >}}
    - `{false, true}` {{< badge text="until v0.5.3" tone="info" >}}
- Example:
    - `build.pin = 2` means the hot portion of the index is cached in memory. 
    - `build.pin = 1` means a subset of the hot portion of the index is cached in memory, consuming less memory.
    - `build.pin = 0` means that this feature is enabled but nothing is actually cached. This option is for debugging purposes only.
    - `build.pin = -1` means that this feature is disabled.
    - `build.pin = false` is the legacy form of `build.pin = -1`.
    - `build.pin = true` is the legacy form of `build.pin = 1`.

### Default Build Options

{{< badge text="since v0.5.3" tone="info" >}}

This is the default value of index building. The index will not be partitioned. In terms of semantics, `build.default = {}` is similar to `build.internal.lists = []`.

<a id="internal-build-options"></a>
### Internal Build Options (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

Internal training samples only rows visible to its MVCC snapshot. In 1.2.0, the initial sample buffer is sized from the estimated table row count and grows as needed, up to `max(lists) × sampling_factor` vectors. For multi-vector columns, one row can contribute several vectors.

When there are more lists than sampled vectors, the required centroid allocations must fit in `maintenance_work_mem`; otherwise the build reports an error before allocating them. Reduce `lists` or increase `maintenance_work_mem` for that case. This setting is not a hard limit on the total memory of a build with enough samples; use `sampling_factor` and `kmeans_dimension` to control that working set.

<a id="build-internal-lists"></a>
#### `build.internal.lists`

- Description: This option determines the hierarchical structure of the vector space partitioning.
- Type: list of integers
- Default:
    - `[]` {{< badge text="since v0.3.0" tone="info" >}}
    - `[1000]` {{< badge text="until v0.2.2: implicit behavior is not ideal" tone="info" >}}
- Example:
    - `build.internal.lists = []` means that the vector space is not partitioned.
    - `build.internal.lists = [4096]` means the vector space is divided into \(4096\) cells.
    - `build.internal.lists = [4096, 262144]` means the vector space is divided into \(4096\) cells, and those cells are further divided into \(262144\) smaller cells.
- Note: The index partitions the vector space into multiple Voronoi cells based on centroids, iteratively creating a hierarchical space partition tree. Each leaf node in this tree represents a region with an associated list storing vectors in that region. During insertion, vectors are placed in lists corresponding to their appropriate leaf nodes. For queries, the index optimizes search by excluding lists whose leaf nodes are distant from the query vector, effectively pruning the search space. If the length of `lists` is \(1\), the `lists` option should be no less than \(4\sqrt{N}\), where \(N\) is the number of vectors in the table.

<a id="build-internal-spherical-centroids"></a>
#### `build.internal.spherical_centroids`

- Description: This option determines whether to perform spherical K-means -- the centroids are L2 normalized after each iteration, you can refer to option `spherical` in [here](https://github.com/facebookresearch/faiss/wiki/Faiss-building-blocks:-clustering,-PCA,-quantization#additional-options).
- Type: boolean
- Default: `false`
- Example:
    - `build.internal.spherical_centroids = false` means that spherical k-means is not performed.
    - `build.internal.spherical_centroids = true` means that spherical k-means is performed.
- Note: Set this to `true` if your model generates embeddings that use cosine similarity as the metric.

<a id="build-internal-sampling-factor"></a>
#### `build.internal.sampling_factor`

{{< badge text="since v0.2.0" tone="info" >}}

- Description: This option determines the number of vectors the K-means algorithm samples per cluster. The higher this value, the slower the build, the greater the memory consumption in building, and the better search performance.
- Type: integer
- Domain: `[0, 1024]`
- Default: `256`
- Example:
    - `build.internal.sampling_factor = 256` means that the K-means algorithm samples \(256 C\) vectors, where \(C\) is the maximum value in `build.internal.lists`.
    - `build.internal.sampling_factor = 32` means that the K-means algorithm samples \(32 C\) vectors, where \(C\) is the maximum value in `build.internal.lists`. This reduces K-means' time and memory usage to approximately \(\frac{1}{8}\) of what it would be with the default value of `256`.

<a id="build-internal-kmeans-iterations"></a>
#### `build.internal.kmeans_iterations`

{{< badge text="since v0.2.2" tone="info" >}}

- Description: This option determines the number of iterations for K-means algorithm. The higher this value, the slower the build.
- Type: integer
- Domain: `[0, 1024]`
- Default: `10`
- Example:
    - `build.internal.kmeans_iterations = 10` means that the K-means algorithm performs \(10\) iterations.
    - `build.internal.kmeans_iterations = 100` means that the K-means algorithm performs \(100\) iterations.

<a id="build-internal-build-threads"></a>
#### `build.internal.build_threads`

- Description: This option determines the number of threads used by K-means algorithm. The higher this value, the faster the build, and greater load on the server in building.
- Type: integer
- Domain: `[1, 255]`
- Default: `1`
- Example:
    - `build.internal.build_threads = 1` means that the K-means algorithm uses \(1\) thread.
    - `build.internal.build_threads = 4` means that the K-means algorithm uses \(4\) threads.

<a id="build-internal-kmeans-algorithm"></a>
#### `build.internal.kmeans_algorithm`

{{< badge text="since v1.0.0" tone="info" >}}

- Description: This option determines the K-means algorithm to be used.
- Type: object
- Example:
    - `build.internal.kmeans_algorithm.lloyd = {}`. This uses Lloyd's algorithm. This is the default value.
    - `build.internal.kmeans_algorithm.hierarchical = {}`. This uses hierarchical clustering. Compared to Lloyd's algorithm, this approach is much faster, but it may cause a loss of accuracy.

<a id="build-internal-kmeans-dimension"></a>
#### `build.internal.kmeans_dimension`

{{< badge text="since v1.0.0" tone="info" >}}

- Description: This option determines the dimension to use for K-means input and output. This feature employs dimensionality reduction and expansion via resampling, effectively reducing K-means' time and memory consumption, but it may cause a loss of accuracy.
- Type: union of integer and null
- Default: null
- Example:
    - If this option is not set, this feature is disabled.
    - `build.internal.kmeans_dimension = 100` means that K-means will process vectors with \(100\) dimensions. For original vectors of \(900\) dimensions, this reduces K-means' time and memory usage to approximately \(\frac{1}{9}\) of what it would be without this feature.

### Search Parameters (`vchordrq`) {#search-parameters}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-enable-scan"></a>
#### `vchordrq.enable_scan`

{{< badge text="since v0.5.0" tone="info" >}}

- Description: Enables or disables the query planner's use of `vchordrq` index scan. It's for testing purposes.
- Type: boolean
- Default: `on`
- Example:
    - `vchordrq.enable_scan = off` disables the query planner's use of `vchordrq` index scan.
    - `vchordrq.enable_scan = on` enables the query planner's use of `vchordrq` index scan.

<a id="vchordrq-probes"></a>
#### `vchordrq.probes` {#search-parameters-vchordrq-probes}

- Description: This GUC parameter `vchordrq.probes` controls how the vector space assists in query pruning. The more probes, the more accurate the search, but also the slower it is.
- Type: list of integers
- Default:
    - ` ` {{< badge text="since v0.3.0" tone="info" >}}
    - `10` {{< badge text="until v0.2.2: the default value was 10 before `lists` defaulted to empty" tone="info" >}}
    - This parameter supports [fallback](/docs/vchord/usage/fallback-parameters/).
- Example:
    - `SET vchordrq.probes = 1` means that only one probe is used.
    - `SET vchordrq.probes = 10` means that ten probes are used.
- Note: The default value is an empty list. The length of this option must match the length of `lists`.
    - Each entry must be an unsigned decimal integer in `1..=4294967295`. Whitespace is allowed around values, and one trailing comma is accepted (`10,` or `10, `). Leading or intermediate empty entries (`,5`, `1,,2`), repeated trailing commas, zero, overflow, invalid characters, and missing commas (`1 0`) are rejected when the setting or index option is assigned. The same rules apply to the index's `probes` fallback option.
    - If `lists = []`, then probes must be ` `.
    - If `lists = [11, 22]`, then probes can be `2,4` or `4,8`. It must not be incorrectly shaped, for example, ` `, `3`, `7,8,9`, `5,5,5,5`.
    - In 1.2.0, the query planner (`amcostestimate`) accounts for `LIMIT`, filter selectivity, and the `probes` budget, and disables `vchordrq` index paths whose `probes` level count does not match the index's `lists` depth (raising an error at execution time only if a mismatched index scan is forced).

<a id="vchordrq-epsilon"></a>
#### `vchordrq.epsilon` {#search-parameters-vchordrq-epsilon}

- Description: Even after pruning, the number of retrieved vectors remains substantial. The index employs the RaBitQ algorithm to quantize vectors into bit vectors, which require just \(\frac{1}{32}\) the memory of single-precision floating-point vectors. Most computations are integer-based, leading to faster processing. Unlike conventional quantization algorithms, RaBitQ estimates not only distances but also their lower bounds. The index computes the lower bound for each vector and dynamically adjusts the number of vectors needing recalculated distances, based on the query count, thus balancing performance and accuracy. The GUC parameter `vchordrq.epsilon` controls the conservativeness of the lower bounds of distances. The higher the value, the higher the accuracy, but the worse the performance. The default value tends to favor higher accuracy than needed for most use cases, so you can try lowering this parameter to achieve better performance.
- Type: real
- Default:
    - `1.9`
    - This parameter supports [fallback](/docs/vchord/usage/fallback-parameters/).
- Domain: `[0.0, 4.0]`
- Example:
    - `SET vchordrq.epsilon = 0.1` indicates you are using a very optimistic lower bound estimation. You set it this way because your dataset is not sensitive to the lower bound estimation, for the precision you need.
    - `SET vchordrq.epsilon = 4.0` indicates you are using a very pessimistic lower bound estimation. You set it this way because your dataset is not very sensitive to the lower bound estimation, for the precision you need.

<a id="vchordrq-prewarm-dim"></a>
#### `vchordrq.prewarm_dim`

{{< badge text="removed in v0.4.0" tone="danger" >}}

- Description: The `vchordrq.prewarm_dim` GUC parameter is used to precompute the RaBitQ projection matrix for the specified dimensions. This can help to reduce the latency of the first query after the PostgreSQL cluster is started.
- Type: list of integers
- Default: `64,128,256,384,512,768,1024,1536`
- Example:
    - `ALTER SYSTEM SET vchordrq.prewarm_dim = '64,128'` means that the projection matrix will be precomputed for dimensions 64 and 128.
- Note:
    - This setting requires a database restart to take effect.
    - Since `v0.4.0`, a new algorithm made this option obsolete.

<a id="vchordrq-max-scan-tuples"></a>
#### `vchordrq.max_scan_tuples`

{{< badge text="since v0.2.0" tone="info" >}}

- Description: The GUC parameter `vchordrq.max_scan_tuples` controls the maximum number of tuples that can be scanned in a vector search. In most cases, you do not need to set this parameter, because the `LIMIT` clause serves a similar purpose. However, when a `WHERE` clause is present, the `LIMIT` clause applies after filtering, while this GUC parameter applies before filtering. This parameter is intended to prevent performance degradation when the filtering selectivity is very low.
- Type: integer
- Default: `-1`
- Domain: `[-1, 2147483647]`
- Example:
  - `SET vchordrq.max_scan_tuples = 999` indicates the index scan returns at most \(999\) tuples.
  - `SET vchordrq.max_scan_tuples = -1` indicates no limit on the number of tuples.
- Note: This parameter has no effect when set to `-1`.
