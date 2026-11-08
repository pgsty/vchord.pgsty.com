---
title: "评估召回率"
linkTitle: "评估召回率"
description: "在向量搜索中，召回率（recall）是指索引返回的近似最近邻中真实最近邻所占的比例。VectorChord 提供了内置的召回率评估与查询采样工具。"
weight: 90
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/measure-recall.md"
math: true
aliases:
  - "/zh/docs/usage/measure-recall/"
  - "/vectorchord/usage/measure-recall/"
icon: fa-solid fa-bullseye
---

{{< badge text="since v0.5.0" tone="info" >}}


在向量搜索中，召回率（recall）是指索引返回的近似最近邻中真实最近邻所占的比例。例如，如果索引检索出 \(100\) 个近似最近邻，其中有 \(97\) 个属于真实最近邻，那么召回率就是 \(\frac{97}{100} = 0.97\)。

> [!TIP]
> 该功能目前处于预览阶段。


## 召回率评估 {#recall-evaluation}

{{< badge text="since v0.5.0" tone="info" >}}

召回率衡量的是搜索返回的相关结果占全部应返回真实结果的比例。在使用索引时，您通常希望了解不同参数配置所对应的召回率和 QPS。`vchordrq_evaluate_query_recall` 函数正是为评估召回率而设计的：它接收一条返回行标识符的查询语句，并返回对应的召回率。

`vchordrq_evaluate_query_recall` 函数内部依赖 [`ctid`](https://www.postgresql.org/docs/current/ddl-system-columns.html#DDL-SYSTEM-COLUMNS-CTID) 将查询结果与基准真相（ground truth）进行比对。因此，传入的 `query` 参数必须以 `SELECT ctid` 开头。

```sql
SET vchordrq.probes = '100';
SET vchordrq.epsilon = 1.0;
SELECT vchordrq_evaluate_query_recall(query => $$
  SELECT ctid FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10
$$);
```

默认情况下，该函数通过执行另一次高精度索引扫描来生成估算的基准真相，并据此评估召回率。如果您希望通过全表扫描（table scan）生成精确的基准真相来评估召回率，请将函数参数 `exact_search` 设置为 `true`。

```sql
SET vchordrq.probes = '100';
SET vchordrq.epsilon = 1.0;
SELECT vchordrq_evaluate_query_recall(query => $$
  SELECT ctid FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10
$$, exact_search => true);
```

对于 MaxSim（`@#`）查询，必须指定 `exact_search => true`；估算召回率模式会报错。使用精确搜索时，请保持顺序扫描开启。参阅[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)。

ANN 扫描使用当前设置，包括索引回退参数。未显式指定 `accu_probes` 时，估算基准扫描会探测索引各层的全部分区；无法确定唯一层数时，回退到精确搜索。函数会恢复内部修改过的所有 GUC 的值及来源，保持后续查询的回退行为。两次查询均以调用者权限执行。

## 查询采样 {#query-sampling}

{{< badge text="since v0.5.2" tone="info" >}}

为了方便评估生产或测试中的查询召回率，VectorChord 内置了查询采样方法。

```sql
SET vchordrq.query_sampling_enable = on;
SET vchordrq.query_sampling_max_records = 1000;
SET vchordrq.query_sampling_rate = 1;
```

假设您已经执行了一条示例向量搜索：`SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10`。

在查询执行并被采样后，您可以检查捕获到的查询要素，包括模式名（schema）、索引名、表名、列名、操作符以及目标向量。

```sql
SELECT * from vchordrq_sampled_queries('items_embedding_idx');
-- schema_name | index_name          | table_name | column_name | operator |    value
---------------+---------------------+------------+-------------+----------+--------------
-- public      | items_embedding_idx | items      | embedding   | <->      | [0.5,0.25,1]
```

读取已记录的查询向量需要索引所属表的所有者权限、表级 `SELECT` 权限，或 `pg_read_all_stats` 权限。两个采样函数均遵循此规则。`vchordrq_sampled_queries` 视图会隐藏调用者无权访问的索引；查询该视图还需具有视图本身的 `SELECT` 权限。

要测量已记录查询的平均召回率，您可以构造目标查询语句并调用评估函数：

```sql
SELECT AVG(recall_value) FROM (
    SELECT vchordrq_evaluate_query_recall(
            format(
                'SELECT ctid FROM %I.%I ORDER BY %I OPERATOR(%s) %L LIMIT 10',
                lq.schema_name,
                lq.table_name,
                lq.column_name,
                lq.operator,
                lq.value
            )
    ) AS recall_value
    FROM vchordrq_sampled_queries('items_embedding_idx') AS lq
) AS eval_results;
```

如果您正在使用包含主库（primary）和备库（standby）的[流复制（replication）](https://www.postgresql.org/docs/current/runtime-config-replication.html)功能，请注意：采样到的查询不会通过复制或备份进行同步。相反，每台服务器都会根据自己实际处理的查询独立维护各自的采样查询集合。

<a id="Reference"></a>
## 参考 {#reference}

`vchordg` 和多向量查询不支持查询采样。MaxSim 召回率可以通过 `vchordrq_evaluate_query_recall(..., exact_search => true)` 评估。

### 搜索参数（`vchordrq`） {#search-parameters}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-query-sampling-enable"></a>
#### `vchordrq.query_sampling_enable` {#vchordrq-query-sampling-enable}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：启用或禁用 `vchordrq` 索引扫描的查询采样。
- 类型：布尔值（boolean）
- 默认值：`off`

<a id="vchordrq-query-sampling-max-records"></a>
#### `vchordrq.query_sampling_max_records` {#vchordrq-query-sampling-max-records}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：控制每个索引最多记录的查询数量。该设置仅在 `vchordrq.query_sampling_enable` 开启时生效。
- 类型：整数（integer）
- 默认值：`0`
- 取值范围：`[0, 10000]`
- 示例：
    - `vchordrq.query_sampling_max_records = 0` 将为每个索引保留 0 条查询。
    - `vchordrq.query_sampling_max_records = 1000` 将为每个索引最多保留最近 1000 条查询。

<a id="vchordrq-query-sampling-rate"></a>
#### `vchordrq.query_sampling_rate` {#vchordrq-query-sampling-rate}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：控制记录查询的采样率。该设置仅在 `vchordrq.query_sampling_enable` 开启时生效。
- 类型：实数（real）
- 默认值：`0`
- 取值范围：`[0, 1]`
- 示例：
    - `vchordrq.query_sampling_rate = 0` 不记录任何查询。
    - `vchordrq.query_sampling_rate = 0.01` 记录约 1% 的查询。
    - `vchordrq.query_sampling_rate = 1` 记录每一条查询（仅用于测试目的）。

<a id="functions"></a>
<a id="Functions"></a>
### 函数（`vchordrq`） {#functions-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-sampled-queries"></a>
<a id="vchordrq_sampled_queries"></a>
#### `vchordrq_sampled_queries` {#vchordrq-sampled-queries-func}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：检索指定 `vchordrq` 索引已记录的查询集合。
- 返回值：`table`
    - `schema_name: text`，查询中表的模式名
    - `index_name: text`，查询中使用的索引名称
    - `table_name: text`，查询中的表名
    - `column_name: text`，参与索引扫描的列名
    - `operator: text`，查询中使用的距离[操作符](/zh/docs/vchord/usage/indexing/#operator-classes)
    - `value: text`，查询中目标向量的文本表示
- 参数：
    - `regclass`，`vchordrq` 索引的对象标识符
- 示例：
    - `SELECT vchordrq_sampled_queries('items_embedding_idx');`

<a id="vchordrq-sampled-values"></a>
#### `vchordrq_sampled_values` {#vchordrq-sampled-values}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：检索指定 `vchordrq` 索引已记录查询中的目标向量。
- 返回值：`SETOF text`，已记录查询向量的文本表示集合。
- 参数：
    - `regclass`，`vchordrq` 索引的对象标识符
- 示例：
    - `SELECT vchordrq_sampled_values('items_embedding_idx');`
- 注意：该函数仅用于调试目的。

<a id="vchordrq-evaluate-query-recall"></a>
#### `vchordrq_evaluate_query_recall` {#vchordrq-evaluate-query-recall}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：评估给定 `vchordrq` 查询的召回率。
- 返回值：`real`
- 参数：
    - `query: text`，待评估召回率的查询语句
    - `exact_search: boolean`，是否使用精确基准真相代替估算的基准真相
    - `accu_probes: text`，用于生成估算基准真相的 `vchordrq.probes`
    - `accu_epsilon: real`，用于生成估算基准真相的 `vchordrq.epsilon`（默认 `1.9`；为获得更准确的估算，应传入不低于被评估查询所用 `vchordrq.epsilon` 的值，例如 `4.0`）
- 示例：
    - `SELECT vchordrq_evaluate_query_recall(query => $$ SELECT ctid FROM t ORDER BY val <-> '[0.5, 0.25, 1.0]' LIMIT 10 $$);`
    - `SELECT vchordrq_evaluate_query_recall(query => $$ SELECT ctid FROM t ORDER BY val <-> '[0.5, 0.25, 1.0]' LIMIT 10 $$, exact_search => true);`
    - `SELECT vchordrq_evaluate_query_recall(query => $$ SELECT ctid FROM t ORDER BY val <-> '[0.5, 0.25, 1.0]' LIMIT 10 $$, accu_probes => '9999', accu_epsilon => 4.0);`

<a id="views"></a>
<a id="Views"></a>
### 视图（`vchordrq`） {#views-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-sampled-queries"></a>
#### `vchordrq_sampled_queries` {#vchordrq-sampled-queries-view}

{{< badge text="since v0.5.2" tone="info" >}}

- 说明：检索**所有** `vchordrq` 索引已记录的查询集合。
- 示例：
    - `SELECT * from vchordrq_sampled_queries;`
- 注意：该视图仅用于调试目的。
