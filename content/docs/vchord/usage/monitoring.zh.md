---
title: "监控"
linkTitle: "监控"
description: "您可以通过查询 pg_stat_progress_create_index 视图来监控 PostgreSQL 索引的构建进度。"
weight: 70
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/monitoring.md"
aliases:
  - "/zh/docs/usage/monitoring/"
  - "/vectorchord/usage/monitoring/"
icon: fa-solid fa-heart-pulse
---

您可以通过查询 [`pg_stat_progress_create_index`](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING) 视图来监控 PostgreSQL 索引的构建进度。

```SQL
SELECT command, phase, round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "%" FROM pg_stat_progress_create_index;
```

<a id="Reference"></a>
## 参考 {#reference}

<a id="phases"></a>
<a id="Phases"></a>
### 构建阶段（`vchordrq`） {#phases-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

`vchordrq` 的索引构建过程包含 5 个步骤，每个步骤的阶段名称（phase）如下：

| 步骤 | 阶段消息                                | 说明                                                   | 耗时 |
| ---- | --------------------------------------- | ------------------------------------------------------ | ---- |
| 1    | `initializing`                          | 开始构建索引                                           | 短   |
| 2    | `initializing index, by default build`  | 该步骤仅用于默认构建（default build）                  | 短   |
| 2    | `initializing index, by internal build` | 该步骤仅用于内部构建：对表进行采样并执行分区以获取质心 | 长   |
| 2    | `initializing index, by external build` | 该步骤仅用于外部构建：从指定表中加载质心               | 短   |
| 3    | `initializing index`                    | 初始化索引的数据结构与存储空间                         | 短   |
| 4    | `inserting tuples from table to index`  | 将所有向量分配并插入到各自对应的列表中                 | 长   |
| 5    | `compacting tuples in index`            | 紧缩优化向量索引结构以提升查询性能                     | 中等 |
{.wide .expand}

第 4 步 `inserting tuples from table to index` 占据了索引构建过程中的大部分时间。`tuples_done`、`blocks_done` 和 `blocks_total` 列可用于指示该步骤的当前进度。

<a id="phases"></a>
<a id="Phases"></a>
### 构建阶段（`vchordg`） {#phases-vchordg}

{{< badge text="vchordg" tone="neutral" >}}

`vchordg` 的索引构建过程包含 2 个步骤，每个步骤的阶段名称（phase）如下：

| 步骤 | 阶段消息                               | 说明                     | 耗时 |
| ---- | -------------------------------------- | ------------------------ | ---- |
| 1    | `initializing`                         | 开始构建索引             | 短   |
| 2    | `inserting tuples from table to index` | 将所有向量插入到图结构中 | 长   |
{.wide .expand}

第 2 步 `inserting tuples from table to index` 占据了索引构建过程中的大部分时间。`tuples_done`、`blocks_done` 和 `blocks_total` 列可用于指示该步骤的当前进度。

### 系统目录统计信息与维护 {#catalog-statistics--maintenance}

在 `vchord` 1.2.0 中：

- 在 `vchordrq` 和 `vchordg` 索引上执行 `CREATE INDEX`、`REINDEX` 与 `VACUUM` 时，会向 PostgreSQL 报告真实的元组数与索引页数，保持 `pg_class.reltuples` 与 `pg_class.relpages` 准确，而不再将其重置为 `0`。
- 单独执行 `ANALYZE` 不再触发 `amvacuumcleanup` 中的索引清理或紧缩；物理索引维护仅在 `VACUUM` 期间运行。
