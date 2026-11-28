---
title: "索引级查询默认值"
linkTitle: "索引默认值"
description: "把 probes、epsilon、ef_search 和 MaxSim 相关设置存在索引上，所有会话无需 SET 就能用上调好的值。"
weight: 70
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/fallback-parameters.md"
aliases:
  - "/docs/usage/fallback-parameters/"
  - "/vectorchord/usage/fallback-parameters/"
icon: fa-solid fa-sliders
---

`vchordrq.probes` 这类查询参数是普通的 PostgreSQL 设置，通常用 `SET` 修改。可一旦应用和数据库之间隔着事务模式的连接池或 ORM，`SET` 就很难用；两个索引需要不同的值时，它更是不对：`lists = [400, 160000]` 的索引要两个 `probes` 值，`lists = [2000]` 的只要一个。更好的做法是把调好的值存在各自的索引上。只要没人显式设置这个参数，扫描就会使用索引上的值。

## 把值存在索引上 {#usage}

在创建时，和 `options` 写在一起：

```sql
CREATE INDEX items_embedding_idx ON items USING vchordrq (embedding vector_cosine_ops)
WITH (options = $$
[build.internal]
lists = [2000]
spherical_centroids = true
$$, probes = '20', epsilon = 1.9);
```

对已有索引修改，无需重建：

```sql
ALTER INDEX items_embedding_idx SET (probes = '40');
ALTER INDEX items_embedding_idx RESET (epsilon);
```

`ALTER INDEX` 会短暂地对索引加排他锁，因此要等正在使用该索引的查询结束，并在提交前阻塞新查询。

## 哪个值生效 {#precedence}

在任何地方显式设置的值都优先于索引上的值：`postgresql.conf`、`ALTER SYSTEM`、`ALTER DATABASE`、`ALTER ROLE` 或 `SET`，即使设的值与默认值相同。只有当该设置在 `pg_settings.source` 中为 `default` 时，索引上的值才会生效：

```sql
SET vchordrq.probes = '50';   -- 本会话用 50，不管索引上是多少
RESET vchordrq.probes;        -- 恢复为索引上的值，除非别处另有设置
```

如果索引上的值没有生效，用 `SELECT name, setting, source FROM pg_settings WHERE name LIKE 'vchord%';` 检查是否有人在角色或数据库级别设置过。

## 参考 {#reference}

<a id="index-storage-parameters"></a><a id="index-storage-parameters-vchordrq"></a><a id="index-storage-parameters-vchordg"></a><a id="probes"></a><a id="epsilon"></a><a id="maxsim-refine"></a><a id="maxsim-threshold"></a><a id="ef-search"></a>

| 索引参数 | 索引类型 | 对应的设置 | 含义 |
| --- | --- | --- | --- |
| `probes` | vchordrq | `vchordrq.probes` | [要探查的列表数](/zh/docs/vchord/usage/indexing/#search-parameters)，每层一个值。 |
| `epsilon` | vchordrq | `vchordrq.epsilon` | [误差界的宽度](/zh/docs/vchord/usage/indexing/#search-parameters)。 |
| `maxsim_refine` | vchordrq | `vchordrq.maxsim_refine` | [用精确距离细化的文档数](/zh/docs/vchord/usage/multi-vector-retrieval/#search-parameters)。 |
| `maxsim_threshold` | vchordrq | `vchordrq.maxsim_threshold` | [未探查词元的距离上界](/zh/docs/vchord/usage/multi-vector-retrieval/#search-parameters)。 |
| `ef_search` | vchordg | `vchordg.ef_search` | [遍历时保留的候选数](/zh/docs/vchord/usage/graph-index/#search-parameters)。 |
{.fields meta="- -"}

其他设置，例如 `max_scan_tuples`、`max_probes`、`prefilter` 和各项 I/O 设置，只能作为 PostgreSQL 设置使用。
