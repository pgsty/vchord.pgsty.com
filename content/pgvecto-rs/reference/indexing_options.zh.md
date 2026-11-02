---
title: "索引选项"
linkTitle: "索引选项"
description: "我们使用 TOML 语法来描述索引配置。以下是配置中各个键的含义说明。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/indexing_options.md"
math: true
aliases:
  - "/reference/indexing_options/"
---

我们使用 [TOML 语法](https://toml.io/en/v1.0.0)来表达索引的配置参数。以下是配置中各个顶层键（表）的含义：

| 键名       | 类型  | 说明                     |
| ---------- | ----- | ------------------------ |
| segment    | table | 分段（Segment）相关选项。|
| optimizing | table | 后台优化相关选项。       |
| indexing   | table | 用于构建索引的算法配置。 |

## `segment` 表选项 {#options-for-table-segment}

| 键名                     | 类型    | 取值范围             | 默认值      | 说明                                     |
| ------------------------ | ------- | -------------------- | ----------- | ---------------------------------------- |
| max_growing_segment_size | integer | `[1, 4_000_000_000]` | `20_000`    | 未建立索引的增长中分段的最大向量数量。   |
| max_sealed_segment_size  | integer | `[1, 4_000_000_000]` | `1_000_000` | 已封存（建立索引）分段的最大向量数量。   |

## `optimizing` 表选项 {#options-for-table-optimizing}

| 键名               | 类型    | 取值范围             | 默认值               | 说明                       |
| ------------------ | ------- | -------------------- | -------------------- | -------------------------- |
| optimizing_threads | integer | `[1, 65535]`         | CPU 核心数的平方根   | 后台构建索引的最大线程数。 |
| sealing_secs       | integer | `[1, 60]`            | `60`                 | 见下方说明。               |
| sealing_size       | integer | `[1, 4_000_000_000]` | `1`                  | 见下方说明。               |

如果一个写入分段（write segment）中的向量数大于 `sealing_size`，且在连续 `sealing_secs` 秒内没有接收到新数据，该写入分段将被转为已封存分段（sealed segment）以构建索引。

## `indexing` 表选项 {#options-for-table-indexing}

| 键名 | 类型  | 说明                                           |
| ---- | ----- | ---------------------------------------------- |
| flat | table | 若设置此表，索引将使用暴力搜索（flat）算法。   |
| ivf  | table | 若设置此表，索引将使用 IVF 算法。              |
| hnsw | table | 若设置此表，索引将使用 HNSW 算法。             |

在上述三种索引算法中只能选择其一，默认值为 `hnsw`。

### `flat` 表选项 {#options-for-table-flat}

| 键名         | 类型  | 说明                 |
| ------------ | ----- | -------------------- |
| quantization | table | 要使用的量化算法配置。|

### `ivf` 表选项 {#options-for-table-ivf}

| 键名             | 类型    | 取值范围         | 默认值  | 说明                             |
| ---------------- | ------- | ---------------- | ------- | -------------------------------- |
| nlist            | integer | `[1, 1_000_000]` | `1000`  | 聚类单元（聚类中心）的数量。     |
| nsample          | integer | `[1, 1_000_000]` | `65536` | 用于 K-Means 聚类训练的样本数量。|
| least_iterations | integer | `[1, 1_000_000]` | `16`    | K-Means 聚类的最少迭代次数。     |
| iterations       | integer | `[1, 1_000_000]` | `500`   | K-Means 聚类的最大迭代次数。     |
| quantization     | table   |                  |         | 要使用的量化算法配置。           |

### `hnsw` 表选项 {#options-for-table-hnsw}

| 键名            | 类型    | 取值范围     | 默认值 | 说明                   |
| --------------- | ------- | ------------ | ------ | ---------------------- |
| m               | integer | `[4, 128]`   | `12`   | 节点的最大连接度数。   |
| ef_construction | integer | `[10, 2000]` | `300`  | 构建索引时的搜索范围。 |
| quantization    | table   |              |        | 要使用的量化算法配置。 |

### `quantization` 表选项 {#options-for-table-quantization}

| 键名    | 类型  | 说明                                         |
| ------- | ----- | -------------------------------------------- |
| trivial | table | 若设置此表，则不使用任何量化。               |
| scalar  | table | 若设置此表，则使用标量量化（Scalar Quantization）。 |
| product | table | 若设置此表，则使用乘积量化（Product Quantization）。|

在上述量化算法中只能选择其一，默认值为 `trivial`。

#### `product` 表选项 {#options-for-table-product}

| 键名   | 类型    | 取值范围                                  | 默认值  | 说明                     |
| ------ | ------- | ----------------------------------------- | ------- | ------------------------ |
| sample | integer | `[1, 1_000_000]`                          | `65535` | 用于量化训练的样本数量。 |
| ratio  | enum    | `"x4"`, `"x8"`, `"x16"`, `"x32"`, `"x64"` | `"x4"`  | 量化的压缩比。           |

压缩比（`ratio`）表示存储向量时节省的内存比例。例如，对于标准 32 位浮点向量 `vector`，`"x4"` 表示内存占用降至原来的 \(\frac{1}{4}\)；如果您是在半精度向量 `vecf16` 上创建索引，则 `"x4"` 表示内存占用降至原来的 \(\frac{1}{2}\)。
