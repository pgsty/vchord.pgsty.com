---
title: "Rerank in Table"
linkTitle: "Rerank in Table"
description: "PostgreSQL indexes store row identifiers and the values of the indexed columns. Typically, indexed columns have simple data types, for example, integers or stri"
weight: 130
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/rerank-in-table.md"
aliases:
  - "/vectorchord/usage/rerank-in-table/"
---

{{< badge text="since v0.2.1" tone="info" >}}


PostgreSQL indexes store row identifiers and the values of the indexed columns. Typically, indexed columns have simple data types, for example, integers or strings with short length limits.

However, if the indexed column is of a vector type, both the table and the index store vectors, which means you pay twice the storage cost for the vectors. If you would like to reduce this cost, you can enable `rerank_in_table` when building the index. The index will then use a tricky approach where it does not store the vectors itself but reads them from the table when needed.

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
rerank_in_table = true
residual_quantization = true
$$);
```

Enabling this option results in [degraded query performance](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/) and [prefetch](/docs/usage/prefetch/) does not work when `rerank_in_table` is enabled.

It's a trade-off of time for space, which is generally not recommended, so it's intended only to address the specific issue of excessively high storage usage.

<a id="Reference"></a>
## Reference

This feature is not supported by `vchordg`.

<a id="indexing-options"></a>
### Indexing Options (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

<a id="rerank-in-table"></a>
#### `rerank_in_table`

{{< badge text="since v0.2.1" tone="info" >}}

- Description: This option determines whether the vectors are fetched from the table. If so, the index will require less storage, but the query latency will increase significantly. It should only be enabled when disk space is extremely limited.
- Type: boolean
- Default: `false`
- Example:
    - `rerank_in_table = false` means that vectors are stored in both the index and the table, and fetched from the index in search.
    - `rerank_in_table = true` means that vectors are stored in the table only, and fetched from the table in search.
