---
title: "测量召回率"
linkTitle: "测量召回率"
description: "测量查询返回了多少真正的最近邻，可以针对单个查询，也可以针对真实流量的样本，以便按目标调整 probes、epsilon 和 ef_search。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/measure-recall.md"
aliases:
  - "/docs/usage/measure-recall/"
  - "/vectorchord/usage/measure-recall/"
icon: fa-solid fa-bullseye
---

召回率是索引扫描返回的结果中真正最近邻所占的比例：一个 `LIMIT 10` 查询如果返回了精确扫描结果中的 9 行，召回率就是 0.9。调参要以它为准，因为 vchord 中每个提速的设置都会牺牲一部分召回率。请在自己的数据和查询上测量；在其他数据集上得到的基准数字没法预测它。

## 测量单个查询 {#recall-evaluation}

`vchordrq_evaluate_query_recall` 先通过索引执行查询，再执行一次得到真实答案，返回两者共有的行所占比例。查询只能选择 `ctid`：

```sql
SET vchordrq.probes = '20';

SELECT vchordrq_evaluate_query_recall(query => $$
    SELECT ctid FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10
$$);
```

走索引的那一次使用当前会话的设置，或者[存在索引上的设置](/zh/docs/vchord/usage/fallback-parameters/)，所以可以改一下 `vchordrq.probes` 或 `vchordrq.epsilon` 再测一次。

<a id="estimated-ground-truth"></a><a id="exact-ground-truth"></a>

默认情况下，真实答案来自第二次探查所有列表的 vchordrq 扫描，比读整张表快得多，结果也非常接近精确值。如果要测试高于 `1.9` 的 `epsilon`，把至少同样大的值传给 `accu_epsilon`。想要顺序扫描得到的精确答案，传 `exact_search => true`；多向量（`@#`）查询必须这样做。

```sql
SELECT vchordrq_evaluate_query_recall(
    query => $$ SELECT ctid FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10 $$,
    exact_search => true
);
```

## 测量真实流量 {#query-sampling}

<a id="sampling-security"></a>

单个查询说明不了多少问题。要针对应用实际发出的查询调参，可以让 vchordrq 记录一部分查询，再对这批样本求平均召回率。记录功能默认关闭，只有超级用户能打开：

```sql
ALTER SYSTEM SET vchordrq.query_sampling_enable = on;
ALTER SYSTEM SET vchordrq.query_sampling_max_records = 1000;  -- 每个索引保留的条数
ALTER SYSTEM SET vchordrq.query_sampling_rate = 0.01;         -- 被记录的扫描比例
SELECT pg_reload_conf();
```

积累一段流量后，计算某个索引已记录查询的平均召回率：

```sql
SELECT avg(vchordrq_evaluate_query_recall(
    format('SELECT ctid FROM %I.%I ORDER BY %I OPERATOR(%s) %L LIMIT 10',
           q.schema_name, q.table_name, q.column_name, q.operator, q.value),
    exact_search => true))
FROM vchordrq_sampled_queries('items_embedding_idx') AS q;
```

- 读取样本需要超级用户或 `pg_read_all_stats` 角色成员身份，因为样本中包含其他用户的查询向量，不受行级安全策略约束。
- 样本保存在执行查询的那台服务器上、数据库之外：不会复制，不会被备份，也不会因回滚而删除。如果查询发往备库，就到备库上读取样本。
- 只记录单向量的 vchordrq 扫描。

## 测量 vchordg {#vchordg}

`vchordrq_evaluate_query_recall` 在计算真实答案时只关闭 vchordrq 索引，对 vchordg 查询来说等于拿图索引和自己比。请改为与顺序扫描对比：

```sql
BEGIN;
CREATE TEMP TABLE ann ON COMMIT DROP AS
    SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;

SET LOCAL vchordg.enable_scan = off;
SET LOCAL vchordrq.enable_scan = off;

SELECT count(*) / 10.0 AS recall
FROM ann
WHERE id IN (SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10);
COMMIT;
```

## 参考 {#reference}

### 函数 {#functions}

<a id="functions-vchordrq"></a><a id="vchordrq-evaluate-query-recall"></a>

```sql
vchordrq_evaluate_query_recall(
    query        text,                 -- SELECT ctid ... ORDER BY ... LIMIT k
    exact_search boolean DEFAULT false,-- true：用顺序扫描得到真实答案
    accu_probes  text    DEFAULT NULL, -- 计算真实答案时的 probes；NULL 表示探查所有列表
    accu_epsilon real    DEFAULT 1.9   -- 计算真实答案时的 epsilon
) RETURNS real
```

<a id="vchordrq-sampled-queries-func"></a><a id="vchordrq-sampled-values"></a><a id="views"></a><a id="Views"></a><a id="views-vchordrq"></a><a id="vchordrq-sampled-queries-view"></a><a id="vchordrq_sampled_queries"></a><a id="vchordrq-sampled-queries"></a>

`vchordrq_sampled_queries(index regclass)` 返回某个索引已记录的查询，列为 `schema_name`、`index_name`、`table_name`、`column_name`、`operator` 和 `value`（文本形式的查询向量）。同名视图 `vchordrq_sampled_queries` 列出数据库中所有 vchordrq 索引的记录。`vchordrq_sampled_values(index regclass)` 只返回向量。

### 设置 {#search-parameters}

<a id="vchordrq-query-sampling-enable"></a><a id="vchordrq-query-sampling-max-records"></a><a id="vchordrq-query-sampling-rate"></a>

只有超级用户能修改。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordrq.query_sampling_enable` | boolean | `off` | 记录一部分 vchordrq 查询。 |
| `vchordrq.query_sampling_max_records` | integer | `0` | 每个索引保留的最近查询条数，最大 `10000`。 |
| `vchordrq.query_sampling_rate` | real | `0` | 被记录的扫描比例，`0` 到 `1`。 |
{.fields meta="type default"}
