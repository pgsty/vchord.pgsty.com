---
title: "索引构建"
linkTitle: "索引构建"
description: "VectorChord 的 vchordrq 索引类型会将向量划分为多个列表，并仅搜索距离查询向量最近的一部分列表。它兼具极快的构建速度与低内存占用，同时性能显著优于 hnsw 和 ivfflat。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/indexing.md"
math: true
aliases:
  - "/zh/docs/usage/indexing/"
  - "/vectorchord/usage/indexing/"
icon: fa-solid fa-sitemap
---

VectorChord 的索引类型 `vchordrq` 会将向量划分为多个列表（list），并仅搜索距离查询向量最近的一部分列表。它兼具极快的构建速度与低内存占用，同时在性能上[显著优于](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/#ivf-vs-hnsw) `hnsw` 和 `ivfflat`。

我们首先创建一个名为 `items` 的表，其中包含一个类型为 `vector(n)` 的 `embedding` 列，然后向其中填充示例数据。

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
```

要创建 `vchordrq` 索引，可以使用以下 SQL 语句：

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);
```

索引构建完成后，您就可以使用它执行向量搜索，检索距离目标向量最近的 \(10\) 个近邻。

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

您还可以根据需要为向量搜索查询添加过滤条件。

```sql
SELECT * FROM items WHERE id % 7 <> 0 ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

<a id="Tuning"></a>
## 调优 {#tuning}

当表中的行数少于 \(100,000\) 时，通常不需要设置索引选项。

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

然而，随着行数的增长，对向量空间进行分区变得十分必要，这可以通过索引选项进行配置。`options` 使用 [TOML（Tom's Obvious Minimal Language）](https://toml.io/) 格式的字符串指定。更多信息请参阅 [#索引选项](#indexing-options)。

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
[build.internal]
lists = [1000]
$$);

SET vchordrq.probes TO '10';
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

参数 `lists` 应根据表中的行数进行调优。下表提供了选择合适取值的指导建议。在执行查询时，请相应地选择 `vchordrq.probes`。

| 行数 \(N\)                               | 推荐分区数 \(L\)                         | `lists` 示例 |
| -------------------------------------- | ------------------------------------ | ------------ |
| \(N \in [0, 10^5)\)                      | N/A                                  | `[]`         |
| \(N \in [10^5, 2 \times 10^6)\)          | \(L = \frac{N}{500}\)                  | `[2000]`     |
| \(N \in [2 \times 10^6, 5 \times 10^7)\) | \(L \in [4 \sqrt{N}, 8 \sqrt{N}]\)     | `[10000]`    |
| \(N \in [5 \times 10^7, \infty)\)        | \(L \in [8 \sqrt{N}, 16\sqrt{N}]\)     | `[80000]`    |
{.wide .expand}

构建索引的过程包含两个步骤：首先对向量空间进行分区，然后将行插入到索引中。第一步（划分向量空间）可以使用多线程进行加速。

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
[build.internal]
lists = [1000]
build_threads = 8
$$);

SET vchordrq.probes TO '10';
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

第二步（插入数据行）可以使用多进程并行执行。详情请参阅 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/)。

对于大多数使用余弦相似度的数据集，启用 `residual_quantization` 和 `build.internal.spherical_centroids` 可以同时提升 QPS 和召回率（recall）。

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

为了提高构建速度，您可以选择将 `build.pin` 设置为 `2`，通过使用更多共享内存来加速构建过程。

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

对于大表而言，时间和内存开销主要由分区阶段主导。有关进一步的调优方法，请参阅[分区调优](/zh/docs/vchord/usage/partitioning-tuning/)。

您也可以参考[外部构建](/zh/docs/vchord/usage/external-build/)，将分区阶段卸载到其他机器上执行。

<a id="Reference"></a>
## 参考 {#reference}

### 操作符类（`vchordrq`） {#operator-classes}

{{< badge text="vchordrq" tone="neutral" >}}

下表列出了 `vchordrq` 支持的所有可用操作符类（Operator Classes）。

| 操作符类             | 说明                                           | 操作符 1                  | 操作符 2                 |
| -------------------- | ---------------------------------------------- | ------------------------- | ------------------------ |
| `vector_l2_ops`      | 适用于 `vector` 类型与欧氏距离                 | `<->(vector,vector)`      | `<<->>(vector,vector)`   |
| `vector_ip_ops`      | 适用于 `vector` 类型与负内积                   | `<#>(vector,vector)`      | `<<#>>(vector,vector)`   |
| `vector_cosine_ops`  | 适用于 `vector` 类型与余弦距离                 | `<=>(vector,vector)`      | `<<=>>(vector,vector)`   |
| `halfvec_l2_ops`     | 适用于 `halfvec` 类型与欧氏距离                | `<->(halfvec,halfvec)`    | `<<->>(halfvec,halfvec)` |
| `halfvec_ip_ops`     | 适用于 `halfvec` 类型与负内积                  | `<#>(halfvec,halfvec)`    | `<<#>>(halfvec,halfvec)` |
| `halfvec_cosine_ops` | 适用于 `halfvec` 类型与余弦距离                | `<=>(halfvec,halfvec)`    | `<<=>>(halfvec,halfvec)` |
| `rabitq8_l2_ops`     | 适用于 `rabitq8` 类型与欧氏距离                | `<->(rabitq8,rabitq8)`    | `<<->>(rabitq8,rabitq8)` |
| `rabitq8_ip_ops`     | 适用于 `rabitq8` 类型与负内积                  | `<#>(rabitq8,rabitq8)`    | `<<#>>(rabitq8,rabitq8)` |
| `rabitq8_cosine_ops` | 适用于 `rabitq8` 类型与余弦距离                | `<=>(rabitq8,rabitq8)`    | `<<=>>(rabitq8,rabitq8)` |
| `rabitq4_l2_ops`     | 适用于 `rabitq4` 类型与欧氏距离                | `<->(rabitq4,rabitq4)`    | `<<->>(rabitq4,rabitq4)` |
| `rabitq4_ip_ops`     | 适用于 `rabitq4` 类型与负内积                  | `<#>(rabitq4,rabitq4)`    | `<<#>>(rabitq4,rabitq4)` |
| `rabitq4_cosine_ops` | 适用于 `rabitq4` 类型与余弦距离                | `<=>(rabitq4,rabitq4)`    | `<<=>>(rabitq4,rabitq4)` |
| `vector_maxsim_ops`  | 适用于 `vector[]` 类型与可扩展的多向量相似度   | `@#(vector[],vector[])`   | N/A                      |
| `halfvec_maxsim_ops` | 适用于 `halfvec[]` 类型与可扩展的多向量相似度  | `@#(halfvec[],halfvec[])` | N/A                      |
| `rabitq8_maxsim_ops` | 适用于 `rabitq8[]` 类型与可扩展的多向量相似度  | `@#(rabitq8[],rabitq8[])` | N/A                      |
| `rabitq4_maxsim_ops` | 适用于 `rabitq4[]` 类型与可扩展的多向量相似度  | `@#(rabitq4[],rabitq4[])` | N/A                      |
{.wide .expand}

`<->`、`<#>` 和 `<=>` 是由 pgvector 定义的操作符。

| 名称  | 说明           |
| ----- | -------------- |
| `<->` | 欧氏距离 |
| `<#>` | 负点积         |
| `<=>` | 余弦距离       |

`<<->>`、`<<#>>`、`<<=>>` 是由 VectorChord 定义的操作符。有关 `<<->>`、`<<#>>`、`<<=>>` 的更多信息，请参阅[相似度过滤](/zh/docs/vchord/usage/similarity-filter/)。

`@#` 是由 VectorChord 定义的操作符。有关 `@#` 的更多信息，请参阅[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)。

`rabitq8`、`rabitq4` 是由 VectorChord 定义的数据类型。有关 `rabitq8`、`rabitq4` 的更多信息，请参阅[量化类型](/zh/docs/vchord/usage/quantization-types/)。

`MaxSim` 相关的操作符类自 `0.3.0` 版本起可用。`rabitq8` 和 `rabitq4` 相关的操作符类自 `1.1.0` 版本起可用。

> [!NOTE]
> 使用 `halfvec_cosine_ops` 时，索引以半精度对向量做归一化。因此余弦距离相差约 0.0001 以内的两行，返回顺序可能与 `<=>` 的值相反；启用 `rerank_in_table` 也是如此。需要严格顺序时，请按[图索引：结果顺序](/zh/docs/vchord/usage/graph-index/#result-order)中的方法对候选结果重新排序。背景见 [pgsty/vchord#17](https://github.com/pgsty/vchord/issues/17)。

### 索引选项（`vchordrq`） {#indexing-options}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="residual-quantization"></a>
#### `residual_quantization` {#residual-quantization}

- 说明：该选项决定是否使用残差量化（Residual Quantization）。如果您不熟悉残差量化，可以阅读这篇[博客](https://drscotthawley.github.io/blog/posts/2023-06-12-RVQ.html)了解更多信息。简而言之，残差量化是一种通过对向量的残差进行量化来提高向量搜索精度的技术。
- 类型：布尔值（boolean）
- 默认值：`false`
- 示例：
    - `residual_quantization = false` 表示不使用残差量化。
    - `residual_quantization = true` 表示使用残差量化。
- 注意：该选项不支持 `rabitq8` 和 `rabitq4`。

<a id="degree-of-parallelism"></a>
#### `degree_of_parallelism` {#degree-of-parallelism}

{{< badge text="since v1.0.0" tone="info" >}}

- 说明：该选项是一个指定并行度的提示值。在大多数情况下，您无需更改它。如果您使用的 CPU 拥有超过 `32` 个线程，并且希望在 PostgreSQL 中利用更多线程，可以将其设置为线程数量以获得更好的性能。
- 类型：整数（integer）
- 默认值：`32`
- 取值范围：`[1, 256]`
- 示例：
    - `degree_of_parallelism = 32` 提示索引最多可能有 `32` 个进程并发访问该索引。
    - `degree_of_parallelism = 64` 提示索引最多可能有 `64` 个进程并发访问该索引。

<a id="build-pin"></a>
#### `build.pin` {#build-pin}

{{< badge text="since v0.2.1" tone="info" >}}

- 说明：该选项决定构建索引时是否使用共享内存。对于大表，您可以选择启用此选项以加速构建过程。
- 类型：整数与布尔值的联合类型（union of integer and boolean）
- 默认值：
    - `-1` {{< badge text="since v1.0.0" tone="info" >}}
    - `false` {{< badge text="until v0.5.3" tone="info" >}}
- 取值范围：
    - `{-1, 0, 1, 2, false, true}` {{< badge text="since v1.0.0" tone="info" >}}
    - `{false, true}` {{< badge text="until v0.5.3" tone="info" >}}
- 示例：
    - `build.pin = 2` 表示将索引的热数据部分全部缓存在内存中。
    - `build.pin = 1` 表示将索引热数据部分的一个子集缓存在内存中，消耗较少内存。
    - `build.pin = 0` 表示启用该功能但实际上不缓存任何内容。此选项仅用于调试目的。
    - `build.pin = -1` 表示禁用该功能。
    - `build.pin = false` 是 `build.pin = -1` 的旧版写法。
    - `build.pin = true` 是 `build.pin = 1` 的旧版写法。

### 默认构建选项 {#default-build-options}

{{< badge text="since v0.5.3" tone="info" >}}

这是索引构建的默认设置。索引将不会进行分区。从语义上讲，`build.default = {}` 类似于 `build.internal.lists = []`。

<a id="internal-build-options"></a>
### 内部构建选项（`vchordrq`） {#internal-build-options}

{{< badge text="vchordrq" tone="neutral" >}}

内部训练只采样其 MVCC 快照可见的行。1.2.0 根据估算的表行数预分配采样缓冲区，并按实际需要扩容，最多采集 `max(lists) × sampling_factor` 个向量。对于多向量列，一行可以贡献多个向量。

当分区数超过样本向量数时，所需的质心内存分配必须能放入 `maintenance_work_mem`，否则构建会在分配前报错。此时可减少 `lists` 或提高 `maintenance_work_mem`。该参数不是样本充足时整个构建过程的内存硬上限；这类构建应通过 `sampling_factor` 和 `kmeans_dimension` 控制工作集大小。

<a id="build-internal-lists"></a>
#### `build.internal.lists` {#build-internal-lists}

- 说明：该选项决定向量空间分区的层次结构。
- 类型：整数列表（list of integers）
- 默认值：
    - `[]` {{< badge text="since v0.3.0" tone="info" >}}
    - `[1000]` {{< badge text="until v0.2.2: implicit behavior is not ideal" tone="info" >}}
- 示例：
    - `build.internal.lists = []` 表示不对向量空间进行分区。
    - `build.internal.lists = [4096]` 表示将向量空间划分为 \(4096\) 个单元（cell）。
    - `build.internal.lists = [4096, 262144]` 表示将向量空间划分为 \(4096\) 个单元，并进一步将这些单元细分为 \(262144\) 个更小的单元。
- 注意：索引会基于质心（centroid）将向量空间划分为多个 Voronoi 单元，通过迭代构建出一棵层次化的空间分区树。树中的每个叶子节点代表一个区域，并关联一个存储该区域内向量的列表。在插入时，向量会被放入其对应叶子节点的列表中。在查询时，索引通过排除叶子节点距离查询向量较远的列表来优化搜索，从而有效剪枝搜索空间。如果 `lists` 的长度为 \(1\)，则 `lists` 选项的值不应小于 \(4\sqrt{N}\)，其中 \(N\) 是表中的向量数量。

<a id="build-internal-spherical-centroids"></a>
#### `build.internal.spherical_centroids` {#build-internal-spherical-centroids}

- 说明：该选项决定是否执行球面 K-means（spherical K-means）——即在每次迭代后对质心进行 L2 归一化，您可以参考[此处](https://github.com/facebookresearch/faiss/wiki/Faiss-building-blocks:-clustering,-PCA,-quantization#additional-options)的 `spherical` 选项。
- 类型：布尔值（boolean）
- 默认值：`false`
- 示例：
    - `build.internal.spherical_centroids = false` 表示不执行球面 K-means。
    - `build.internal.spherical_centroids = true` 表示执行球面 K-means。
- 注意：如果您的模型生成的嵌入向量使用余弦相似度作为度量标准，请将此项设置为 `true`。

<a id="build-internal-sampling-factor"></a>
#### `build.internal.sampling_factor` {#build-internal-sampling-factor}

{{< badge text="since v0.2.0" tone="info" >}}

- 说明：该选项决定 K-means 算法为每个聚类采样的向量数量。该值越高，构建速度越慢，构建时的内存消耗越大，但搜索性能越好。
- 类型：整数（integer）
- 取值范围：`[0, 1024]`
- 默认值：`256`
- 示例：
    - `build.internal.sampling_factor = 256` 表示 K-means 算法采样 \(256 C\) 个向量，其中 \(C\) 是 `build.internal.lists` 中的最大值。
    - `build.internal.sampling_factor = 32` 表示 K-means 算法采样 \(32 C\) 个向量，其中 \(C\) 是 `build.internal.lists` 中的最大值。这会将 K-means 的时间和内存开销降低至默认值 `256` 时的约 \(\frac{1}{8}\)。

<a id="build-internal-kmeans-iterations"></a>
#### `build.internal.kmeans_iterations` {#build-internal-kmeans-iterations}

{{< badge text="since v0.2.2" tone="info" >}}

- 说明：该选项决定 K-means 算法的迭代次数。该值越高，构建速度越慢。
- 类型：整数（integer）
- 取值范围：`[0, 1024]`
- 默认值：`10`
- 示例：
    - `build.internal.kmeans_iterations = 10` 表示 K-means 算法执行 \(10\) 次迭代。
    - `build.internal.kmeans_iterations = 100` 表示 K-means 算法执行 \(100\) 次迭代。

<a id="build-internal-build-threads"></a>
#### `build.internal.build_threads` {#build-internal-build-threads}

- 说明：该选项决定 K-means 算法使用的线程数。该值越高，构建速度越快，同时构建期间服务器的负载也越高。
- 类型：整数（integer）
- 取值范围：`[1, 255]`
- 默认值：`1`
- 示例：
    - `build.internal.build_threads = 1` 表示 K-means 算法使用 \(1\) 个线程。
    - `build.internal.build_threads = 4` 表示 K-means 算法使用 \(4\) 个线程。

<a id="build-internal-kmeans-algorithm"></a>
#### `build.internal.kmeans_algorithm` {#build-internal-kmeans-algorithm}

{{< badge text="since v1.0.0" tone="info" >}}

- 说明：该选项决定所使用的 K-means 算法。
- 类型：对象（object）
- 示例：
    - `build.internal.kmeans_algorithm.lloyd = {}`：使用劳埃德算法（Lloyd's algorithm）。这是默认值。
    - `build.internal.kmeans_algorithm.hierarchical = {}`：使用层次聚类（hierarchical clustering）。与劳埃德算法相比，这种方法速度要快得多，但可能会导致一定的精度损失。

<a id="build-internal-kmeans-dimension"></a>
#### `build.internal.kmeans_dimension` {#build-internal-kmeans-dimension}

{{< badge text="since v1.0.0" tone="info" >}}

- 说明：该选项决定用于 K-means 输入和输出的维度。该特性通过重采样实现降维与升维，从而有效降低 K-means 的时间和内存消耗，但可能会导致一定的精度损失。
- 类型：整数与空值的联合类型（union of integer and null）
- 默认值：null
- 示例：
    - 如果未设置此选项，则禁用该特性。
    - `build.internal.kmeans_dimension = 100` 表示 K-means 将处理 \(100\) 维的向量。对于原始维度为 \(900\) 的向量，这会将 K-means 的时间和内存开销降低至未启用该特性时的约 \(\frac{1}{9}\)。

### 搜索参数（`vchordrq`） {#search-parameters}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-enable-scan"></a>
#### `vchordrq.enable_scan` {#vchordrq-enable-scan}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：启用或禁用查询规划器对 `vchordrq` 索引扫描的使用。该参数仅用于测试目的。
- 类型：布尔值（boolean）
- 默认值：`on`
- 示例：
    - `vchordrq.enable_scan = off` 禁用查询规划器使用 `vchordrq` 索引扫描。
    - `vchordrq.enable_scan = on` 启用查询规划器使用 `vchordrq` 索引扫描。

<a id="vchordrq-probes"></a>
#### `vchordrq.probes` {#search-parameters-vchordrq-probes}

- 说明：GUC 参数 `vchordrq.probes` 控制如何利用向量空间分区来辅助查询剪枝。探测数（probes）越多，搜索结果越精确，但速度也越慢。
- 类型：整数列表（list of integers）
- 默认值：
    - ` ` {{< badge text="since v0.3.0" tone="info" >}}
    - `10` {{< badge text="until v0.2.2: the default value was 10 before `lists` defaulted to empty" tone="info" >}}
    - 该参数支持[回退参数（fallback）](/zh/docs/vchord/usage/fallback-parameters/)。
- 示例：
    - `SET vchordrq.probes = 1` 表示仅使用 1 个探测分区。
    - `SET vchordrq.probes = 10` 表示使用 10 个探测分区。
- 注意：默认值为空列表。该选项的长度必须与 `lists` 的长度相匹配。
    - 每项必须是 `1..=4294967295` 范围内的无符号十进制整数，允许数值两侧有空白，也接受单个尾逗号（`10,` 或 `10, `）。前导或中间空项（`,5`、`1,,2`）、多个尾逗号、零值、溢出值、非法字符和缺少逗号（`1 0`）会在设置参数或索引选项时直接拒绝。索引的 `probes` 回退参数也遵循相同规则。
    - 如果 `lists = []`，则 probes 必须为 ` `。
    - 如果 `lists = [11, 22]`，则 probes 可以是 `2,4` 或 `4,8`。其形状不能不匹配，例如不能是 ` `、`3`、`7,8,9` 或 `5,5,5,5`。
    - 在 1.2.0 中，查询规划器（`amcostestimate`）会结合 `LIMIT`、过滤选择率与 `probes` 预算估算代价，并自动禁用 `probes` 层级数与索引 `lists` 深度不匹配的 `vchordrq` 索引路径（仅在被强制执行不匹配的索引扫描时于执行期报错）。

<a id="vchordrq-epsilon"></a>
#### `vchordrq.epsilon` {#search-parameters-vchordrq-epsilon}

- 说明：即使经过剪枝，检索出的候选向量数量依然可观。索引采用 RaBitQ 算法将向量量化为位向量（bit vector），其内存占用仅为单精度浮点向量的 \(\frac{1}{32}\)。由于大部分计算基于整数完成，处理速度得以大幅提升。与传统量化算法不同，RaBitQ 不仅估算距离，还会估算距离的下界（lower bound）。索引会计算每个向量的距离下界，并根据查询需求动态调整需要重新计算精确距离的向量数量，从而在性能与精度之间取得平衡。GUC 参数 `vchordrq.epsilon` 控制距离下界估算的保守程度。该值越高，精度越高，但性能越差。对于大多数应用场景而言，默认值倾向于提供高于实际所需的精度，因此您可以尝试调低此参数以获得更好的性能。
- 类型：实数（real）
- 默认值：
    - `1.9`，拟发布的 1.3.0 保持不变。
    - 显式调高至 `2.5` 等值可以改善召回率、减少距离乱序，代价是需要精排更多向量。调高前应测量实际负载的召回率与延迟。已有的显式会话设置和索引参数继续生效。
    - 该参数支持[回退参数（fallback）](/zh/docs/vchord/usage/fallback-parameters/)。
- 取值范围：`[0.0, 4.0]`
- 示例：
    - `SET vchordrq.epsilon = 0.1` 表示您正在使用非常乐观的下界估算。这样设置是因为在您所需的精度下，您的数据集对下界估算不敏感。
    - `SET vchordrq.epsilon = 4.0` 表示您正在使用非常悲观的下界估算。这样设置是因为在您所需的精度下，您的数据集对下界估算较为敏感。

<a id="vchordrq-prewarm-dim"></a>
#### `vchordrq.prewarm_dim` {#vchordrq-prewarm-dim}

{{< badge text="removed in v0.4.0" tone="danger" >}}

- 说明：GUC 参数 `vchordrq.prewarm_dim` 用于为指定维度预计算 RaBitQ 投影矩阵。这有助于降低 PostgreSQL 集群启动后首次查询的延迟。
- 类型：整数列表（list of integers）
- 默认值：`64,128,256,384,512,768,1024,1536`
- 示例：
    - `ALTER SYSTEM SET vchordrq.prewarm_dim = '64,128'` 表示将为维度 64 和 128 预计算投影矩阵。
- 注意：
    - 此设置需要重启数据库才能生效。
    - 自 `v0.4.0` 起，新算法已使该选项不再需要。

<a id="vchordrq-max-scan-tuples"></a>
#### `vchordrq.max_scan_tuples` {#vchordrq-max-scan-tuples}

{{< badge text="since v0.2.0" tone="info" >}}

- 说明：GUC 参数 `vchordrq.max_scan_tuples` 控制在一次向量搜索中最多可以扫描的元组（tuple）数量。在大多数情况下，您不需要设置此参数，因为 `LIMIT` 子句起到了类似的作用。然而，当存在 `WHERE` 子句时，`LIMIT` 子句在过滤之后生效，而此 GUC 参数在过滤之前生效。该参数旨在防止过滤选择率极低时出现性能下降。
- 类型：整数（integer）
- 默认值：`-1`
- 取值范围：`[-1, 2147483647]`
- 示例：
  - `SET vchordrq.max_scan_tuples = 999` 表示索引扫描最多返回 \(999\) 个元组。
  - `SET vchordrq.max_scan_tuples = -1` 表示对元组数量没有限制。
- 注意：当设置为 `-1` 时，此参数不起作用。
