---
title: "监控"
linkTitle: "监控"
description: "我们提供了 pg_vector_index_stat 视图来监控索引构建进度。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/usage/monitoring.md"
aliases:
  - "/usage/monitoring/"
icon: fa-solid fa-heart-pulse
---

我们提供了 `pg_vector_index_stat` 视图来监控索引的构建进度。

| 列名         | 类型   | 说明                                                                               |
| ------------ | ------ | ---------------------------------------------------------------------------------- |
| tablerelid   | oid    | 表的 OID。                                                                         |
| indexrelid   | oid    | 索引的 OID。                                                                       |
| tablename    | name   | 表名。                                                                             |
| indexname    | name   | 索引名。                                                                           |
| idx_status   | text   | 取值为 `NORMAL` 或 `UPGRADE`，表示该索引处于正常状态还是需要升级。                 |
| idx_indexing | bool   | 当 `idx_status` 为 `NORMAL` 时非空。表示后台线程是否正在构建索引。                 |
| idx_tuples   | int8   | 当 `idx_status` 为 `NORMAL` 时非空。索引中的元组总数。                             |
| idx_sealed   | int8[] | 当 `idx_status` 为 `NORMAL` 时非空。每个已封存分段（sealed segment）中的元组数量。  |
| idx_growing  | int8[] | 当 `idx_status` 为 `NORMAL` 时非空。每个增长中分段（growing segment）中的元组数量。 |
| idx_write    | int8   | 当 `idx_status` 为 `NORMAL` 时非空。写缓冲区（write buffer）中的元组数量。         |
| idx_size     | int8   | 当 `idx_status` 为 `NORMAL` 时非空。所有分段占用的总字节大小。                     |
| idx_options  | text   | 当 `idx_status` 为 `NORMAL` 时非空。索引的配置信息。                               |
{.wide .expand}

> [!DETAILS] `idx_options` 详情
> `idx_options` 是一个包含向量（vector）、分段（segment）、优化（optimizing）和索引（indexing）选项的 JSON 字符串。示例如下：
>
> ```json
> {
>     "vector": {
>         "dimensions": 256,
>         "distance": "L2",
>         "kind": "F32"
>     },
>     "segment": {
>         "max_growing_segment_size": 20000,
>         "max_sealed_segment_size": 1000000
>     },
>     "optimizing": {
>         "sealing_secs": 60,
>         "sealing_size": 1,
>         "delete_threshold": 0.2,
>         "optimizing_threads": 2
>     },
>     "indexing": {
>         "hnsw": {
>             "m": 12,
>             "ef_construction": 300,
>             "quantization": {
>                 "trivial": {}
>             }
>         }
>     }
> }
> ```
>


如果不再有新的插入操作，并且您希望等待所有索引构建完成，可以每隔 60 秒检查一次 `idx_indexing` 字段，直到其变为 `false`（注：原文写作 `true`，实际 `idx_indexing = false` 表示后台索引构建已完成）。
