---
title: "vchordrq 索引"
linkTitle: "vchordrq 索引"
description: "vchordrq（IVF + RaBitQ）索引如何回答一次查询、如何按表的规模配置，以及如何在召回率与速度之间取舍。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/indexing.md"
aliases:
  - "/docs/usage/indexing/"
  - "/vectorchord/usage/indexing/"
  - "/docs/vchord/usage/rerank-in-table/"
  - "/docs/usage/rerank-in-table/"
icon: fa-solid fa-sitemap
---

`vchordrq` 是 vchord 的主力索引。每次查询只搜索少数几组向量，因此内存占用小、构建快，是大表和装不进内存的数据的默认选择。如果想要一个不用规划列表数的图索引，请看 [`vchordg`](/zh/docs/vchord/usage/graph-index/)。

## 工作原理 {#how-it-works}

构建时，vchordrq 对一部分样本向量做 k-means 聚类，每个聚类中心对应一个**列表**（list）。每行的向量在索引里存两份：一份是每维只占几个比特的 RaBitQ 编码，放在离它最近的中心所属的列表里；另一份是全精度向量，供查询最后一步使用。

一次查询分三步：

1. **路由。** 选出离查询向量最近的 `probes` 个列表。
1. **估算。** 扫描这些列表中的 RaBitQ 编码。每个编码给出一个估算距离和一个已知的误差界，`epsilon` 决定误差界取多宽。
1. **重排。** 对仍有可能进入最近邻的候选计算精确距离，一旦某行的位置确定，就按精确距离顺序返回。
{.steps}

召回率在两个地方损失，各有一个参数对应：

- 真正的近邻落在没被探查的列表里：调大 **`probes`**。
- 真正的近邻估算距离偏大，重排得太晚，没赶上 `LIMIT`：调大 **`epsilon`**。

两个参数都在查询时生效，调参不需要重建索引。

## 创建索引 {#create}

按查询用的距离运算符选择对应的运算符类。完整列表见[参考](#operator-classes)。

| 距离 | 查询运算符 | `vector` 列的运算符类 |
| --- | --- | --- |
| 欧氏距离（L2） | `<->` | `vector_l2_ops` |
| 负内积 | `<#>` | `vector_ip_ops` |
| 余弦距离 | `<=>` | `vector_cosine_ops` |

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

`options` 是一段 [TOML](https://toml.io/)。大多数嵌入模型用余弦距离或归一化内积，对它们来说，`residual_quantization` 和 `spherical_centroids` 能同时提升召回率和速度，所以示例里都打开了。不写任何选项时，索引只有一个列表，适合 10 万行以下的表。

查询不用改：该列上的 `ORDER BY embedding <=> $1 LIMIT k` 都会走索引。

```sql
SET vchordrq.probes = '20';
SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;
```

## 选择 `lists` {#lists}

<a id="partitioning"></a>

列表越多，每个列表越小，每次探查扫描的向量越少，代价是构建时 k-means 更慢。按表预计会达到的行数 `N` 来定：

| 行数 `N` | 列表数 | 示例 |
| --- | --- | --- |
| 10 万以下 | 一个列表 | `[]`（默认） |
| 10 万到 200 万 | `N / 500` | 100 万行：`[2000]` |
| 200 万到 5000 万 | `4√N` 到 `8√N` | 1000 万行：`[20000]` |
| 5000 万以上 | `8√N` 到 `16√N`，或分两层 | 1 亿行：`[160000]` 或 `[400, 160000]` |

两层的 `lists` 会建出一棵树：查询先在 400 个粗粒度中心里挑，再在它们下面的叶子列表里挑。此时 `probes` 每层给一个值，例如 `'40,140'`。超过 5000 万行时，还请阅读[分区调优](/zh/docs/vchord/usage/partitioning-tuning/)，把构建控制在内存范围内。

## 调节召回率与速度 {#tuning}

用真实查询和明确的召回率目标来调，不要凭感觉：

1. `epsilon` 保持默认值 `1.9`。
1. `probes` 先取 `lists` 的 1% 左右：`[2000]` 对应 `'20'`。
1. 用 [`vchordrq_evaluate_query_recall`](/zh/docs/vchord/usage/measure-recall/) 在一批真实查询上测召回率。
1. 低于目标就调大 `probes`。明显高于目标时，先调小 `probes`，再试着调小 `epsilon` 换取速度。LAION-1 亿的参考配置用的是 `epsilon = 1.4`。
1. 把结果存到索引上，所有会话和连接池都会用到它：

   ```sql
   ALTER INDEX items_embedding_idx SET (probes = '20', epsilon = 1.9);
   ```

   会话里的 `SET vchordrq.probes` 仍然优先。详见[回退参数](/zh/docs/vchord/usage/fallback-parameters/)。
{.steps}

## 用过滤键过滤 {#filter-keys}

任何 vchordrq 索引都能配合 `WHERE` 使用，但过滤条件很严格时就不够了：如果 42 号租户只占全表的 0.1%，被探查的列表里可能只有寥寥几行属于它，`LIMIT 10` 就凑不满。把过滤列加进索引，排在向量列后面，索引就会在每个列表内部检查条件，并继续读取更多列表，直到凑够行数：

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

支持的键类型和条件、哈希键，以及如何限制额外读取的列表数，见[过滤](/zh/docs/vchord/usage/filtering/#filter-keys)，那里还介绍了预过滤和距离范围。

## 缩小索引 {#index-size}

默认情况下，索引把每个向量存两份：RaBitQ 编码和供重排用的全精度副本，所以索引比表里的向量本身还要稍大一些。有两种办法缩小它：

- `rerank_in_table = true` 不存全精度副本，重排时改从表中读取向量。索引缩小到只比编码大一点，但查询会变慢，因为重排要读取分散的表页面（宽向量还要读 TOAST），而不是索引自己的页面。多向量索引不支持这个选项。
- 把列存成 `halfvec`、`rabitq8` 或 `rabitq4`，表和索引一起缩小，见[量化类型](/zh/docs/vchord/usage/quantization-types/)。

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

## 加快大表构建 {#build}

构建分两个阶段：先在样本上做 k-means，再把每一行插入它所属的列表。两个阶段各有提速办法：

- **k-means** 使用 `build_threads` 个线程。几千万行以上时，[分区调优](/zh/docs/vchord/usage/partitioning-tuning/)能减少它的时间和内存，[外部构建](/zh/docs/vchord/usage/external-build/)能把它放到 GPU 上。
- **插入**在 PostgreSQL 17 及以上版本使用并行工作进程。按 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/#parallel-index-builds)设置 `max_parallel_maintenance_workers`。
- `build.pin = 2` 在插入期间把聚类中心固定在共享内存中，`shared_buffers` 有余量时能加快插入。

构建进度可以在 `pg_stat_progress_create_index` 里查看，各阶段的含义见[大规模构建](/zh/docs/vchord/usage/partitioning-tuning/#monitoring)。

## 日常维护 {#maintenance}

新行写入离它最近的中心所属的列表，聚类中心本身不再变化。autovacuum 会压缩列表、清理已删除的行，日常写入不需要额外操作。

当数据与训练聚类中心时相比已经明显变化，比如表的规模比建索引时翻了几倍，就重建索引：

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
```

## 结果顺序 {#result-order}

返回的行几乎总是按精确距离排好序的。只有三种情况会让某行稍微错位：

- 它的 RaBitQ 估算偏大，因而排在一个稍远的行之后才重排。调大 `epsilon` 能减少这种情况。
- 它是在后面一轮[过滤键](/zh/docs/vchord/usage/filtering/#filter-keys)扩展中找到的。
- 列类型是 `halfvec`，索引按半精度舍入距离。

应用需要严格的 SQL 顺序时，多取一些，再在 SQL 里排序：

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

## 参考 {#reference}

### 运算符类 {#operator-classes}

| 列类型 | L2 `<->` | 内积 `<#>` | 余弦 `<=>` |
| --- | --- | --- | --- |
| `vector` | `vector_l2_ops` | `vector_ip_ops` | `vector_cosine_ops` |
| `halfvec` | `halfvec_l2_ops` | `halfvec_ip_ops` | `halfvec_cosine_ops` |
| `rabitq8` | `rabitq8_l2_ops` | `rabitq8_ip_ops` | `rabitq8_cosine_ops` |
| `rabitq4` | `rabitq4_l2_ops` | `rabitq4_ip_ops` | `rabitq4_cosine_ops` |

这些运算符类同时支持对应的[范围运算符](/zh/docs/vchord/usage/filtering/#distance-range)（`<<->>`、`<<#>>`、`<<=>>`）。各类型的数组用 `vector_maxsim_ops`、`halfvec_maxsim_ops`、`rabitq8_maxsim_ops` 或 `rabitq4_maxsim_ops`，配合 `@#` 运算符，见[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)。被索引的列可以有 1 到 60,000 维。

### 索引选项 {#indexing-options}

<a id="residual-quantization"></a><a id="rerank-in-table"></a><a id="degree-of-parallelism"></a><a id="build-pin"></a><a id="default-build-options"></a><a id="internal-build-options"></a><a id="build-internal-lists"></a><a id="build-internal-spherical-centroids"></a><a id="build-internal-sampling-factor"></a><a id="build-internal-kmeans-iterations"></a><a id="build-internal-build-threads"></a><a id="build-internal-kmeans-algorithm"></a><a id="build-internal-kmeans-dimension"></a>

写在 `CREATE INDEX ... WITH (options = $$ ... $$)` 的 TOML 字符串里，修改后需要重建索引。

| 选项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `residual_quantization` | boolean | `false` | 相对所属列表的中心对向量做量化，多数数据集上能提升召回率。`rabitq8` 和 `rabitq4` 列不可用。 |
| `rerank_in_table` | boolean | `false` | 索引里不存全精度向量，重排时从表中读取。索引更小，查询更慢。见[缩小索引](#index-size)。 |
| `build.pin` | integer | `-1` | 插入期间把聚类中心固定在共享内存中：`2` 固定所有层，`1` 固定上层，`-1` 不固定。 |
| `degree_of_parallelism` | integer | `32` | 同时向索引插入的会话超过 32 个时调大，最大 `256`。 |
| `zone_maps` | integer | `2` | 前几个过滤键列在每个数据块上记录最小值和最大值，让范围条件可以跳过整块。 |
| `build.internal.lists` | integer array | `[]` | 每层的列表数，升序，最多 8 层。见[选择 `lists`](#lists)。 |
| `build.internal.spherical_centroids` | boolean | `false` | 对聚类中心做归一化。余弦距离和归一化内积的嵌入应打开。 |
| `build.internal.build_threads` | integer | `1` | k-means 使用的线程数，最大 `255`。 |
| `build.internal.sampling_factor` | integer | `256` | k-means 为每个列表采样的向量数。调小可减少构建时间和内存。 |
| `build.internal.kmeans_iterations` | integer | `10` | k-means 迭代次数。 |
| `build.internal.kmeans_algorithm` | table | `lloyd` | 设为 `{ hierarchical = {} }` 可大幅加快两层 `lists` 的构建。 |
| `build.internal.kmeans_dimension` | integer | 未设置 | 先把向量降到这个维度再做 k-means。 |
| `build.external.table` | string | 未设置 | 存放预先算好的聚类中心的表，须带模式名。见[外部构建](/zh/docs/vchord/usage/external-build/)。 |
{.fields meta="type default"}

### 查询参数 {#search-parameters}

<a id="vchordrq-probes"></a><a id="search-parameters-vchordrq-probes"></a><a id="vchordrq-epsilon"></a><a id="search-parameters-vchordrq-epsilon"></a><a id="vchordrq-max-scan-tuples"></a><a id="vchordrq-enable-scan"></a>

可以在会话中用 `SET` 设置，用 `ALTER ROLE` / `ALTER DATABASE` 按角色或数据库设置；`probes` 和 `epsilon` 还可以直接存在索引上。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordrq.probes` | string | `''` | 要探查的列表数，`lists` 每层一个值，用逗号分隔，如 `'40,140'`。单列表索引留空。 |
| `vchordrq.epsilon` | real | `1.9` | RaBitQ 误差界的宽度，取值 `0` 到 `4`。越大重排的候选越多：召回率更高，查询更慢。 |
| `vchordrq.max_probes` | integer | `-1` | [过滤键](/zh/docs/vchord/usage/filtering/#filter-keys)扫描在已探查列表用完后最多再读多少个列表。`-1` 表示不限，`0` 表示只读 `probes` 个。 |
| `vchordrq.max_scan_tuples` | integer | `-1` | 扫描到这么多个候选就停止，避免几乎没有行能通过的过滤条件读完整个索引。`-1` 表示不限。 |
| `vchordrq.enable_scan` | boolean | `on` | 允许规划器使用 vchordrq 索引。关闭后可与精确扫描对比。 |
{.fields meta="type default"}

特定功能的参数随功能一起介绍：`vchordrq.prefilter` 见[过滤](/zh/docs/vchord/usage/filtering/#prefilter)，`vchordrq.io_search` 和 `vchordrq.io_rerank` 见 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/#prefetch)，`vchordrq.maxsim_refine` 和 `vchordrq.maxsim_threshold` 见[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)，`vchordrq.query_sampling_*` 见[召回率评估](/zh/docs/vchord/usage/measure-recall/)。
