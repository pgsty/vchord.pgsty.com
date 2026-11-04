---
title: "预热"
linkTitle: "预热"
description: "PostgreSQL 启动后，表和索引只有在首次被访问时才会从存储加载到缓冲池中。使用专用预热函数可以将索引的热数据部分提前加载到内存中。"
weight: 100
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prewarm.md"
aliases:
  - "/zh/docs/usage/prewarm/"
  - "/vectorchord/usage/prewarm/"
icon: fa-solid fa-fire
---

PostgreSQL 启动后，表和索引只有在首次被访问时才会从存储加载到缓冲池（buffer pool）中。随着查询的不断执行，索引中被频繁访问的部分会自然地缓存在缓冲池里。然而，在执行最初的几批查询时，由于缓冲池为空，查询速度往往较慢。

PostgreSQL 扩展 `pg_prewarm` 提供了 `pg_prewarm` 函数，可以在一定程度上解决这一问题。在 PostgreSQL 启动后，您只需向该函数传入索引名称，它就会将索引从存储加载到缓冲池中。

```sql
SELECT pg_prewarm('items_pkey');
```

不过，这种方法只有在缓冲池远大于索引大小时才有效。对于向量索引而言，索引大小往往远超内存容量。向量索引在设计上将索引数据分为两部分：体量较小的热数据部分（hot portion）和体量庞大的冷数据部分（cold portion）。向量索引只需要将热数据部分保留在内存中即可获得理想的性能。因此，VectorChord 提供了专用的预热函数，仅将索引的热数据部分加载到内存中。

```sql [vchordrq]
SELECT vchordrq_prewarm('items_embedding_idx');
```

即使索引大小远大于内存容量，该函数依然能够很好地发挥作用。

`vchordrq_prewarm` 与 `vchordg_prewarm` 均要求索引所属表的所有者权限或表级 `SELECT` 权限。仅具有 `pg_read_all_stats` 权限不能执行预热。

<a id="Reference"></a>
## 参考 {#reference}

<a id="functions"></a>
<a id="Functions"></a>
### 函数（`vchordrq`） {#functions-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-prewarm"></a>
#### `vchordrq_prewarm` {#vchordrq-prewarm-func}

- 说明：该函数通过将 `vchordrq` 索引的热数据加载到缓冲池中来预热索引。
- 返回值：`text`
- 参数：
    - `regclass`，`vchordrq` 索引的对象标识符
- 示例：
    - `SELECT vchordrq_prewarm('items_embedding_idx')`

<a id="functions"></a>
<a id="Functions"></a>
### 函数（`vchordg`） {#functions-vchordg}

{{< badge text="vchordg" tone="neutral" >}}

<a id="vchordg-prewarm"></a>
#### `vchordg_prewarm` {#vchordg-prewarm-func}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：该函数通过将 `vchordg` 索引的热数据加载到缓冲池中来预热索引。
- 返回值：`text`
- 参数：
    - `regclass`，`vchordg` 索引的对象标识符
- 示例：
    - `SELECT vchordg_prewarm('items_embedding_idx')`
