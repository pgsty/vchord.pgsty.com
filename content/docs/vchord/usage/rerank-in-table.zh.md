---
title: "表内重排序"
linkTitle: "表内重排序"
description: "PostgreSQL 索引会存储行标识符以及被索引列的值。启用 rerank_in_table 可避免在索引中重复存储原始向量，从而节省磁盘空间。"
weight: 130
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/rerank-in-table.md"
aliases:
  - "/zh/docs/usage/rerank-in-table/"
  - "/vectorchord/usage/rerank-in-table/"
---

{{< badge text="since v0.2.1" tone="info" >}}


PostgreSQL 索引会存储行标识符（row identifier）以及被索引列的值。通常情况下，被索引的列具有简单的数据类型，例如整数或长度有限的短字符串。

然而，如果被索引的列是向量类型，那么表和索引都会存储向量，这意味着您需要为这些向量支付双倍的存储成本。如果您希望降低这部分开销，可以在构建索引时启用 `rerank_in_table`。启用后，索引将采用一种巧妙的方式：它自身不再存储原始向量，而是在需要时直接从表中读取它们。

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
rerank_in_table = true
residual_quantization = true
$$);
```

启用该选项会导致[查询性能下降](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/)，并且在启用 `rerank_in_table` 时，[预取（prefetch）](/zh/docs/vchord/usage/prefetch/)功能将无法生效。

这是一种以时间换空间的折中方案，通常不推荐使用，仅适用于需要解决磁盘存储空间极度紧张的特定场景。

<a id="Reference"></a>
## 参考 {#reference}

`vchordg` 不支持此功能。

<a id="indexing-options"></a>
### 索引选项（`vchordrq`） {#indexing-options}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="rerank-in-table"></a>
#### `rerank_in_table` {#rerank-in-table}

{{< badge text="since v0.2.1" tone="info" >}}

- 说明：该选项决定是否从表中读取向量进行重排序。如果启用，索引所需的存储空间将减少，但查询延迟会显著增加。仅当磁盘空间极其有限时才应启用此选项。
- 类型：布尔值（boolean）
- 默认值：`false`
- 示例：
    - `rerank_in_table = false` 表示向量同时存储在索引和表中，搜索时从索引中读取向量。
    - `rerank_in_table = true` 表示向量仅存储在表中，搜索时从表中读取向量。
