---
title: "vchordg 索引"
linkTitle: "vchordg 索引"
description: "什么时候用 vchordg 图索引、它需要多少内存，以及如何调整构建和查询参数。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/graph-index.md"
aliases:
  - "/docs/usage/graph-index/"
  - "/vectorchord/usage/graph-index/"
icon: fa-solid fa-diagram-project
---

`vchordg` 是 vchord 的图索引。和 pgvector 的 HNSW 一样，查询沿着相邻向量构成的图前进，因此不需要规划列表数，用默认参数召回率就不错。与 HNSW 不同的是，遍历时比较的是每维 1 或 2 个比特的 RaBitQ 编码，而不是完整向量，完整向量只在最后对候选重排时读取。所以每次查询都要访问的那部分索引，只占表大小的一小部分。这部分放得进内存、又想要低延迟且不想调 `lists` 时，用它；表放不进内存，或者需要过滤键、多向量列、外部构建时，用 [`vchordrq`](/zh/docs/vchord/usage/indexing/)。

## 工作原理 {#how-it-works}

查询从入口顶点出发，不断移向离查询向量更近的邻居，并保留到目前为止最好的 `ef_search` 个候选。途中的距离由 RaBitQ 编码算出。最后读取全精度向量，用精确距离对候选重排，按顺序返回。

每插入一行，都会通过一次保留 `ef_construction` 个候选的搜索，为它选出最多 `m` 个邻居。这两个值越大，图的质量越好，同样的 `ef_search` 下召回率越高，代价是构建更慢、索引更大。

## 创建索引 {#create}

运算符类与 vchordrq 相同：`vector_l2_ops`、`vector_ip_ops`、`vector_cosine_ops`，以及对应的 `halfvec`、`rabitq8`、`rabitq4` 版本，见[完整列表](#operator-classes)。

```sql
CREATE INDEX ON items USING vchordg (embedding vector_cosine_ops);

SET vchordg.ef_search = 100;
SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;
```

在 PostgreSQL 17 及以上版本，构建会使用并行工作进程，见 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/#parallel-index-builds)。

## 估算内存 {#memory}

<a id="Tuning"></a><a id="tuning"></a>

RaBitQ 编码留在 `shared_buffers` 或操作系统页缓存里时，vchordg 才快。默认 `bits = 2` 下，一条 768 维向量的编码占 192 字节，1000 万行约需 1.8 GiB，另外还有邻居列表。

放不下时，设 `bits = 1` 可以减半。同样的 `ef_search` 下召回率会略降，可以再调高 `ef_search` 补回来：

```sql
CREATE INDEX ON items USING vchordg (embedding vector_cosine_ops)
WITH (options = $$
bits = 1
$$);
```

重启后可以用 [`vchordg_prewarm`](/zh/docs/vchord/usage/postgresql-tuning/#prewarm) 把编码重新载入 `shared_buffers`。如果图放在 SSD 上而不是内存里，`vchordg.beam_search`（以及构建时的 `beam_construction`）会每步同时展开多个顶点，让它们的读取重叠起来；图在内存里时两者都保持 `1`。

## 调节召回率与速度 {#tune}

`vchordg.ef_search` 是查询时唯一的旋钮：越大召回率越高，查询越慢。从默认值 `64` 开始，用真实查询[测量召回率](/zh/docs/vchord/usage/measure-recall/#vchordg)，逐步调高直到达到目标。把结果存到索引上，所有会话都会用到：

```sql
ALTER INDEX items_embedding_idx SET (ef_search = 128);
```

如果 `ef_search` 已经很高召回率还是不够，用更大的 `m`（如 `64`）和 `ef_construction`（如 `128`）重建索引，这对高维嵌入最有帮助。

## 过滤 {#filters}

<a id="querying-and-maintenance"></a>

`WHERE` 条件在图搜索之后、对返回的行进行检查。因此选择性强的过滤需要更大的 `ef_search` 才能返回足够的行；几乎不匹配任何行的过滤可能让扫描走遍大半张图，可以用 `vchordg.max_scan_tuples` 设上限。大表上按租户或类别过滤，更适合用 vchordrq 的[过滤键](/zh/docs/vchord/usage/filtering/#filter-keys)。距离范围条件的用法与 vchordrq 相同，见[过滤](/zh/docs/vchord/usage/filtering/#distance-range)。

## 日常维护 {#maintenance}

autovacuum 会从图中移除已删除的行、修复它们周围的连接，并复用其空间。修复是局部的，所以删掉表中相当一部分数据后，要重新[测量召回率](/zh/docs/vchord/usage/measure-recall/#vchordg)；如果下降了，在线重建：

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
```

## 结果顺序 {#result-order}

扫描在探索图的同时就开始返回行，所以一个稍近、但较晚找到的行，可能排在一个稍远的行后面。`ef_search` 越大，这种情况越少。应用需要严格的距离顺序时，多取一些再在 SQL 里排序：

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

## 参考 {#reference}

### 运算符类 {#operator-classes}

| 列类型 | L2 `<->` | 内积 `<#>` | 余弦 `<=>` |
| --- | --- | --- | --- |
| `vector` | `vector_l2_ops` | `vector_ip_ops` | `vector_cosine_ops` |
| `halfvec` | `halfvec_l2_ops` | `halfvec_ip_ops` | `halfvec_cosine_ops` |
| `rabitq8` | `rabitq8_l2_ops` | `rabitq8_ip_ops` | `rabitq8_cosine_ops` |
| `rabitq4` | `rabitq4_l2_ops` | `rabitq4_ip_ops` | `rabitq4_cosine_ops` |

这些运算符类同时支持对应的[范围运算符](/zh/docs/vchord/usage/filtering/#distance-range)。被索引的列可以有 1 到 30,000 维。

### 索引选项 {#indexing-options}

<a id="bits"></a><a id="m"></a><a id="ef-construction"></a><a id="alpha"></a><a id="beam-construction"></a>

写在 `CREATE INDEX` 的 `options` TOML 字符串里，修改后需要重建索引。

| 选项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `bits` | integer | `2` | 每维的 RaBitQ 比特数，`1` 或 `2`。`1` 让内存减半，召回率略降。 |
| `m` | integer | `32` | 每个顶点最多的邻居数，最大 `512`。越大在高维数据上召回率越高，构建时间和空间也越多。 |
| `ef_construction` | integer | `64` | 插入一行时保留的候选数。越大图越好，构建越慢。 |
| `alpha` | float array | `[1.0, 1.2]` | 选择邻居时的剪枝阈值，升序，从 `1.0` 开始，每个值小于 `2.0`。`[1.0]` 与 HNSW 的剪枝方式相同。适用于 L2 和余弦距离。 |
| `beam_construction` | integer | `1` | 插入时每步展开的顶点数。只有图在 SSD 上时才调大。 |
{.fields meta="type default"}

### 查询参数 {#search-parameters}

<a id="vchordg-enable-scan"></a><a id="vchordg-ef-search"></a><a id="search-parameters-vchordg-ef-search"></a><a id="vchordg-beam-search"></a><a id="vchordg-max-scan-tuples"></a>

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordg.ef_search` | integer | `64` | 搜索时保留的候选数。越大召回率和顺序越好，查询越慢。可以[存在索引上](/zh/docs/vchord/usage/fallback-parameters/)。 |
| `vchordg.beam_search` | integer | `1` | 每步展开的顶点数。只有图在 SSD 上时才调大。 |
| `vchordg.max_scan_tuples` | integer | `-1` | 向执行器返回这么多行后停止，避免几乎不匹配的过滤走遍整张图。`-1` 表示不限。 |
| `vchordg.enable_scan` | boolean | `on` | 允许规划器使用 vchordg 索引。关闭后可得到精确结果。 |
{.fields meta="type default"}

`vchordg.io_search` 和 `vchordg.io_rerank` 决定页面的读取方式，见 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/#prefetch)。
