---
title: "搜索选项"
linkTitle: "搜索选项"
description: "搜索选项通过 PostgreSQL GUC 参数进行配置。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/search_options.md"
aliases:
  - "/reference/search_options/"
---

搜索选项通过 [PostgreSQL GUC 参数](https://www.postgresql.org/docs/current/config-setting.html)进行指定。

## `ivf` 选项 {#options-for-ivf}

以下选项仅对 IVF 算法生效。详情请参阅[索引指南](/zh/pgvecto-rs/usage/indexing/#inverted-file-index-ivf)。

| 选项               | 类型    | 取值范围         | 默认值 | 说明             |
| ------------------ | ------- | ---------------- | ------ | ---------------- |
| vectors.ivf_nprobe | integer | `[1, 1_000_000]` | `10`   | 扫描的列表数量。 |

## `hnsw` 选项 {#options-for-hnsw}

以下选项仅对 HNSW 算法生效。详情请参阅[索引指南](/zh/pgvecto-rs/usage/indexing/#hierarchical-navigable-small-world-graph-hnsw)。

| 选项                   | 类型    | 取值范围     | 默认值 | 说明              |
| ---------------------- | ------- | ------------ | ------ | ----------------- |
| vectors.hnsw_ef_search | integer | `[1, 65535]` | `100`  | HNSW 的搜索范围。 |

## 其他选项 {#other-options}

与搜索模式及规划器相关的查询选项：

| 选项                           | 类型    | 取值范围           | 默认值    | 说明                                                                                              |
| ------------------------------ | ------- | ------------------ | --------- | ------------------------------------------------------------------------------------------------- |
| vectors.search_mode            | enum    | `"basic", "vbase"` | `"vbase"` | 搜索模式，详情请参阅[搜索指南](/zh/pgvecto-rs/usage/search/#search-modes)。                       |
| vectors.pgvector_compatibility | boolean |                    | `off`     | 启用或禁用 `pgvector` 兼容模式，详情请参阅 [pgvector 兼容性](/zh/pgvecto-rs/usage/compatibility/)。 |
| vectors.enable_index           | boolean |                    | `on`      | 启用或禁用查询规划器对向量索引的使用。                                                            |
