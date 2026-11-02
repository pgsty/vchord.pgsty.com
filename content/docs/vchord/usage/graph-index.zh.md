---
title: "图索引"
linkTitle: "图索引"
description: "VectorChord 的 vchordg 索引类型是一种基于磁盘的图索引，具有低内存占用的特点。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/graph-index.md"
math: true
aliases:
  - "/zh/docs/usage/graph-index/"
  - "/vectorchord/usage/graph-index/"
---

{{< badge text="since v0.5.0" tone="info" >}}


VectorChord 的索引类型 `vchordg` 是一种基于磁盘的图索引，具有低内存占用的特点。

我们首先创建一个名为 `items` 的表，其中包含一个类型为 `vector(n)` 的 `embedding` 列，然后向其中填充示例数据。

要创建 `vchordg` 索引，可以使用以下 SQL 语句：

```sql
CREATE INDEX ON items USING vchordg (embedding vector_l2_ops);
```

> [!TIP]
> 该功能目前处于预览阶段。


<a id="Tuning"></a>
## 调优 {#tuning}

在构建索引时，通常需要对两个选项进行调优：`m` 和 `ef_construction`。`m` 是每个顶点的最大邻居数，`ef_construction` 是插入期间包含最近邻的动态列表大小。

在搜索时，需要对 `ef_search` 进行调优。`ef_search` 是搜索期间包含最近邻的动态列表大小。

```sql
CREATE INDEX ON items USING vchordg (embedding vector_l2_ops) WITH (options = $$
m = 64
ef_construction = 128
$$);

SET vchordg.ef_search TO '128';
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10;
```

作为一种基于磁盘的索引，`vchordg` 通常只需要将量化后的向量保存在缓冲池（buffer pool）中即可维持良好性能。默认情况下，`vchordg` 会将一个 \(D\) 维向量量化为 \(2D\) 比特。设行数为 \(N\)，则该索引所需的总内存为 \(2DN\) 比特。如果您的内存非常有限且正在使用超高维向量，可以考虑将向量量化为 \(D\) 比特，此时索引所需的总内存为 \(DN\) 比特。

```sql
CREATE INDEX ON items USING vchordg (embedding vector_l2_ops) WITH (options = $$
bits = 1
m = 64
ef_construction = 128
$$);
```

索引构建可以通过使用多进程来加速。详情请参阅 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/)。

<a id="Reference"></a>
## 参考 {#reference}

### 操作符类（`vchordg`） {#operator-classes}

{{< badge text="vchordg" tone="neutral" >}}

下表列出了 `vchordg` 支持的所有可用操作符类。

| 操作符类             | 说明                                  | 操作符 1               | 操作符 2                 |
| -------------------- | ------------------------------------- | ---------------------- | ------------------------ |
| `vector_l2_ops`      | 适用于 `vector` 类型与欧氏距离        | `<->(vector,vector)`   | `<<->>(vector,vector)`   |
| `vector_ip_ops`      | 适用于 `vector` 类型与负内积          | `<#>(vector,vector)`   | `<<#>>(vector,vector)`   |
| `vector_cosine_ops`  | 适用于 `vector` 类型与余弦距离        | `<=>(vector,vector)`   | `<<=>>(vector,vector)`   |
| `halfvec_l2_ops`     | 适用于 `halfvec` 类型与欧氏距离       | `<->(halfvec,halfvec)` | `<<->>(halfvec,halfvec)` |
| `halfvec_ip_ops`     | 适用于 `halfvec` 类型与负内积         | `<#>(halfvec,halfvec)` | `<<#>>(halfvec,halfvec)` |
| `halfvec_cosine_ops` | 适用于 `halfvec` 类型与余弦距离       | `<=>(halfvec,halfvec)` | `<<=>>(halfvec,halfvec)` |
| `rabitq8_l2_ops`     | 适用于 `rabitq8` 类型与欧氏距离       | `<->(rabitq8,rabitq8)` | `<<->>(rabitq8,rabitq8)` |
| `rabitq8_ip_ops`     | 适用于 `rabitq8` 类型与负内积         | `<#>(rabitq8,rabitq8)` | `<<#>>(rabitq8,rabitq8)` |
| `rabitq8_cosine_ops` | 适用于 `rabitq8` 类型与余弦距离       | `<=>(rabitq8,rabitq8)` | `<<=>>(rabitq8,rabitq8)` |
| `rabitq4_l2_ops`     | 适用于 `rabitq4` 类型与欧氏距离       | `<->(rabitq4,rabitq4)` | `<<->>(rabitq4,rabitq4)` |
| `rabitq4_ip_ops`     | 适用于 `rabitq4` 类型与负内积         | `<#>(rabitq4,rabitq4)` | `<<#>>(rabitq4,rabitq4)` |
| `rabitq4_cosine_ops` | 适用于 `rabitq4` 类型与余弦距离       | `<=>(rabitq4,rabitq4)` | `<<=>>(rabitq4,rabitq4)` |

`<<->>`、`<<#>>`、`<<=>>` 是由 VectorChord 定义的操作符。有关 `<<->>`、`<<#>>`、`<<=>>` 的更多信息，请参阅[相似度过滤](/zh/docs/vchord/usage/similarity-filter/)。

`rabitq8`、`rabitq4` 是由 VectorChord 定义的数据类型。有关 `rabitq8`、`rabitq4` 的更多信息，请参阅[量化类型](/zh/docs/vchord/usage/quantization-types/)。

前 6 个操作符类自 `0.5.0` 版本起可用，后 6 个操作符类自 `1.1.0` 版本起可用。

<a id="indexing-options"></a>
### 索引选项（`vchordg`） {#indexing-options}

{{< badge text="vchordg" tone="neutral" >}}

#### `bits` {#bits}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：RaBitQ 量化后比特数与维度的比值。`bits = 2` 可提供更好的召回率和 QPS，而 `bits = 1` 则消耗更少的内存。
- 类型：整数（integer）
- 默认值：`2`
- 示例：
    - `bits = 2` 表示将 \(D\) 维向量量化为 \(2D\) 比特。
    - `bits = 1` 表示将 \(D\) 维向量量化为 \(D\) 比特。

#### `m` {#m}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：每个顶点的最大邻居数。`m` 越大，性能越好，但存储需求也越高。`m` 对应于 HNSW 中的 \(m_0\) 和 DiskANN 中的 \(m\)。
- 类型：整数（integer）
- 默认值：`32`
- 示例：
    - `m = 32` 表示每个顶点最多有 \(32\) 个邻居。
    - `m = 64` 表示每个顶点最多有 \(64\) 个邻居。

<a id="ef-construction"></a>
#### `ef_construction` {#ef-construction}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：插入期间包含最近邻的动态列表大小。`ef_construction` 越大，搜索性能越好，但插入速度越慢。`ef_construction` 对应于 HNSW 中的 \(\text{ef}_\text{construction}\) 和 DiskANN 中的 \(\text{ef}_C\)。
- 类型：整数（integer）
- 默认值：`64`
- 示例：
    - `ef_construction = 64` 表示在插入期间包含最近邻的动态列表大小为 \(64\)。
    - `ef_construction = 128` 表示在插入期间包含最近邻的动态列表大小为 \(128\)。

#### `alpha` {#alpha}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：剪枝期间所选用的 `alpha` 值。`alpha` 对应于 DiskANN 中的 \(\alpha\)。该选项必须包含 1–8 个升序排列的值，其中第一个元素为 `1.0`，最后一个元素小于 `2.0`，不允许空列表。
- 类型：浮点数列表（list of floats）
- 默认值：`[1.0, 1.2]`
- 示例：
    - `alpha = [1.0, 1.2]` 等价于在 DiskANN 中设置 `alpha = 1.2`。
    - `alpha = [1.0]` 等价于 HNSW 中的默认剪枝策略。
- 注意：当距离度量为负内积时，此选项无效。

<a id="beam-construction"></a>
#### `beam_construction` {#beam-construction}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：插入期间使用的束宽（beam width）。束宽是指一次同时访问的顶点数量。由于从 SSD 随机读取少量扇区的时间与读取单个扇区几乎相同，较大的束宽可以有效减少对 SSD 的往返访问次数，从而获得更好的性能。但由于它会增加计算量，因此对于完全放入内存的索引而言反而不利。
- 类型：整数（integer）
- 默认值：`1`
- 示例：
    - `beam_construction = 8` 表示索引在插入期间一次同时访问 8 个顶点。
    - `beam_construction = 1` 表示索引在插入期间一次访问 1 个顶点。

<a id="search-parameters"></a>
### 搜索参数（`vchordg`） {#search-parameters}

{{< badge text="vchordg" tone="neutral" >}}

<a id="vchordg-enable-scan"></a>
#### `vchordg.enable_scan` {#vchordg-enable-scan}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：启用或禁用查询规划器对 `vchordg` 索引扫描的使用。该参数仅用于测试目的。
- 类型：布尔值（boolean）
- 默认值：`on`
- 示例：
    - `vchordg.enable_scan = off` 禁用查询规划器使用 `vchordg` 索引扫描。
    - `vchordg.enable_scan = on` 启用查询规划器使用 `vchordg` 索引扫描。

<a id="vchordg-ef-search"></a>
#### `vchordg.ef_search` {#search-parameters-vchordg-ef-search}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：搜索期间包含最近邻的动态列表大小。`vchordg.ef_search` 越大，召回率越好，但 QPS 越低。`vchordg.ef_search` 对应于 HNSW 和 DiskANN 中的 \(\text{ef}\)。
- 类型：整数（integer）
- 默认值：
    - `64`
    - 该参数支持[回退参数（fallback）](/zh/docs/vchord/usage/fallback-parameters/)。
- 取值范围：`[1, 65535]`
- 示例：
    - `SET vchordg.ef_search = 64` 表示在搜索期间包含最近邻的动态列表大小为 \(64\)。
    - `SET vchordg.ef_search = 128` 表示在搜索期间包含最近邻的动态列表大小为 \(128\)。

<a id="vchordg-beam-search"></a>
#### `vchordg.beam_search` {#vchordg-beam-search}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：搜索期间使用的束宽（beam width）。束宽是指一次同时访问的顶点数量。由于从 SSD 随机读取少量扇区的时间与读取单个扇区几乎相同，较大的束宽可以有效减少对 SSD 的往返访问次数，从而获得更好的性能。但由于它会增加计算量，因此对于完全放入内存的索引而言反而不利。
- 类型：整数（integer）
- 默认值：`1`
- 取值范围：`[1, 65535]`
- 示例：
    - `SET vchordg.beam_search = 8` 表示索引在搜索期间一次同时访问 8 个顶点。
    - `SET vchordg.beam_search = 1` 表示索引在搜索期间一次访问 1 个顶点。

<a id="vchordg-max-scan-tuples"></a>
#### `vchordg.max_scan_tuples` {#vchordg-max-scan-tuples}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：GUC 参数 `vchordg.max_scan_tuples` 控制在一次向量搜索中最多可以扫描的元组数量。在大多数情况下，您不需要设置此参数，因为 `LIMIT` 子句起到了类似的作用。然而，当存在 `WHERE` 子句时，`LIMIT` 子句在过滤之后生效，而此 GUC 参数在过滤之前生效。该参数旨在防止过滤选择率极低时出现性能下降。
- 类型：整数（integer）
- 默认值：`-1`
- 取值范围：`[-1, 2147483647]`
- 示例：
  - `SET vchordg.max_scan_tuples = 999` 表示索引扫描最多返回 \(999\) 个元组。
  - `SET vchordg.max_scan_tuples = -1` 表示对元组数量没有限制。
- 注意：当设置为 `-1` 时，此参数不起作用。
