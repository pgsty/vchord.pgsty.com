---
title: "Prewarm"
linkTitle: "Prewarm"
description: "After PostgreSQL starts, tables and indexes are loaded from storage into the buffer pool only when they are accessed for the first time. As queries are executed"
weight: 100
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prewarm.md"
aliases:
  - "/docs/usage/prewarm/"
  - "/vectorchord/usage/prewarm/"
icon: fa-solid fa-fire
---

After PostgreSQL starts, tables and indexes are loaded from storage into the buffer pool only when they are accessed for the first time. As queries are executed, the frequently accessed parts of the index are naturally cached in the buffer pool. However, as initial queries are executed, the buffer pool is empty, which causes the queries to be slow.

The PostgreSQL extension `pg_prewarm` includes the `pg_prewarm` function, which can partially address this issue. After PostgreSQL starts, you simply provide the name of the index to this function, and it will load the index from storage into the buffer pool.

```sql
SELECT pg_prewarm('items_pkey');
```

However, it only works if the size of the buffer pool is much larger than the size of the index. For vector indexes, the index size is often much larger than memory size. Vector indexes are designed so that the index data is divided into two parts: a small, hot portion and a large, cold portion. Vector indexes only need the hot portion in memory to achieve reasonable performance. Therefore, a specialized prewarm function exists and it loads only the hot portion of the index into memory.

```sql [vchordrq]
SELECT vchordrq_prewarm('items_embedding_idx');
```

It works well even if the index size is much larger than memory size.

<a id="Reference"></a>
## Reference

<a id="functions"></a>
<a id="Functions"></a>
### Functions (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-prewarm"></a>
#### `vchordrq_prewarm`

- Description: This function warms the `vchordrq` index by loading index to buffer pool.
- Result: `text`
- Arguments:
    - `regclass`, the object identifier of a `vchordrq` index
- Example:
    - `SELECT vchordrq_prewarm('items_embedding_idx')`

<a id="functions"></a>
<a id="Functions"></a>
### Functions (`vchordg`)

{{< badge text="vchordg" tone="neutral" >}}

<a id="vchordg-prewarm"></a>
#### `vchordg_prewarm`

{{< badge text="since v0.5.0" tone="info" >}}

- Description: This function warms the `vchordg` index by loading index to buffer pool.
- Result: `text`
- Arguments:
    - `regclass`, the object identifier of a `vchordg` index
- Example:
    - `SELECT vchordg_prewarm('items_embedding_idx')`
