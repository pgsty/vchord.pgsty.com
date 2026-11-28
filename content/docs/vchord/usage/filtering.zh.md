---
title: "过滤"
linkTitle: "过滤"
description: "把向量检索与 WHERE 条件结合：什么时候普通过滤就够了，什么时候用过滤键或预过滤，以及如何按距离限定结果。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prefilter.md"
aliases:
  - "/docs/vchord/usage/prefilter/"
  - "/docs/vchord/usage/similarity-filter/"
  - "/docs/usage/prefilter/"
  - "/docs/usage/similarity-filter/"
  - "/docs/vchord/usage/range-query/"
icon: fa-solid fa-filter
---

实际的查询大多是"离查询向量最近、*同时*满足某个条件的行"：某个租户的文档、有货的商品、上周的图片、距离小于某个阈值的结果。vchord 提供四种施加条件的方式，该用哪种取决于条件会留下多少行：

| 你的条件 | 用法 |
| --- | --- |
| 留下大部分行，如 `NOT deleted` | 普通的 [`WHERE`](#where) |
| 只留下少量行，条件列是租户、类别、日期这类字段 | [过滤键](#filter-keys) |
| 只留下少量行，但条件做不成键：表达式、子查询、文本匹配 | [预过滤](#prefilter) |
| 与查询向量的最大距离 | [距离范围](#distance-range) |

## 普通的 `WHERE` {#where}

<a id="post-filter"></a>

任何 `WHERE` 子句都能配合 vchord 索引使用。索引按距离由近到远产出行，PostgreSQL 丢掉不匹配的，直到凑满 `LIMIT`：

```sql
SELECT id FROM items
WHERE NOT deleted
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

大部分行都匹配时，这样做开销很小。匹配的行很少时，会有两种问题。vchordrq 只读取离查询最近的 `probes` 个列表，如果其中匹配的行不足 10 条，查询返回的就不足 10 条。vchordg 会一直遍历图直到找够，这可能意味着走遍大半张图。下面两节就是为 vchordrq 解决这个问题的。

## 过滤键 {#filter-keys}

过滤键是 vchordrq 索引中与每个向量存放在一起的列。有了它，索引在重排之前就自己检查条件；被探查的列表里匹配的行用完后，它会继续读取更多列表，每轮数量翻倍，直到凑满 `LIMIT`。

把键列加在向量列后面：

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops, tenant_id, created_at)
WITH (options = $$
[build.internal]
lists = [2000]
spherical_centroids = true
$$);

SELECT id FROM items
WHERE tenant_id = 42 AND created_at >= now() - interval '30 days'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

在 `EXPLAIN` 里，键上的条件显示为 `Index Cond`，与 `Order By` 并列。没有按向量 `ORDER BY` 的查询不会仅凭键来使用这个索引，那是 B-tree 的活。

- **类型与条件。** 键可以是 `int2`、`int4`、`int8`、`float4`、`float8`、`uuid`、`date`、`timestamp`、`timestamptz`、`oid`、`bool` 或任意枚举类型。索引能利用 `=`、`<`、`<=`、`>`、`>=`、`BETWEEN` 和 `= ANY(...)`。在 PostgreSQL 15 和 16 上，`= ANY(...)` 在扫描之后而非扫描之中检查。
- **键的顺序。** 选择性最强的键放在最前面。前 `zone_maps` 个键（默认 2 个）还会在每个数据块上记录最小值和最大值，范围条件可以借此跳过整块。
- **哈希键。** 对于只做 `=` 比较的宽键（如 `uuid`），`uuid_hash_ops`、`int8_hash_ops`、`int4_hash_ops` 只存一个短哈希而不存原值：`(embedding vector_cosine_ops, owner uuid_hash_ops (bytes = 4))`。哈希冲突的行由 PostgreSQL 重新检查。
- **限制工作量。** 默认 `vchordrq.max_probes = -1` 时，一个匹配不到任何行的值会让扫描读完所有列表，才能返回空结果。设置 `vchordrq.max_probes` 可以限制读取的列表数，设为 `0` 则只读 `probes` 个。
- **顺序。** 后面几轮找到的行可能比已返回的行更近。需要严格的距离顺序时，多取一些再在 SQL 中排序，见[结果顺序](/zh/docs/vchord/usage/indexing/#result-order)。

多向量（`@#`）索引和 vchordg 不支持过滤键。

## 预过滤 {#prefilter}

<a id="when-to-enable"></a><a id="execution-semantics"></a>

条件做不成过滤键时，`vchordrq.prefilter` 让 vchordrq 在重排每个候选之前检查条件，而不是之后。重排要做一次全精度距离计算和一次页面读取；在 1% 的选择率下，几乎全部这类工作都花在了最终会被过滤掉的行上。

```sql
SET vchordrq.prefilter = on;

SELECT id FROM items
WHERE metadata @> '{"lang": "de"}'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

条件既有选择性、计算又便宜时再打开。在 LAION-5M 上，1% 选择率时吞吐提升约 200%，10% 时约 5%：

![LAION-5M 上预过滤带来的 QPS 提升](/docs/images/prefilter.png)

大部分行都能通过的条件得不到好处，而开销大的条件（如正则表达式）可能得不偿失。`random()` 这类易变函数始终在扫描之后求值。

预过滤不改变读取哪些列表，所以不能像过滤键那样解决结果不足的问题。它只适用于 vchordrq。

## 距离范围 {#distance-range}

<a id="operator-classes"></a><a id="types"></a><a id="functions"></a><a id="operators"></a>

只想要与查询向量距离在某个范围内的行时，用 `sphere(center, radius)` 和范围运算符表达阈值，而不是在 `WHERE` 里比较距离：

```sql
SELECT id FROM items
WHERE embedding <<=>> sphere('[3, 1, 2]'::vector, 0.2)
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

这样索引在确定不会再有行落在半径内时就能停下，而不是继续产出随后被 PostgreSQL 丢弃的行。在 `EXPLAIN` 中这个条件显示为 `Index Cond`。不带 `ORDER BY` 和 `LIMIT` 也可以使用，用来取出半径内的所有行。

| 运算符 | 匹配条件 | 中心点类型 |
| --- | --- | --- |
| `<<->>` | `<->`（L2 距离）< 半径 | `sphere(vector \| halfvec \| rabitq8 \| rabitq4, real)` |
| `<<#>>` | `<#>`（负内积）< 半径 | 同上 |
| `<<=>>` | `<=>`（余弦距离）< 半径 | 同上 |

vchordrq 和 vchordg 都支持这些运算符，使用与 `ORDER BY` 相同的运算符类。搜索仍然是近似的，可能漏掉匹配的行，比如位于未被探查的列表中，或者位于图遍历没走到的区域。需要半径内的全部行时，不走索引执行查询（`SET vchordrq.enable_scan = off` 或 `vchordg.enable_scan = off`），并用 `EXPLAIN` 确认 PostgreSQL 在扫描表。

## 参考 {#reference}

<a id="search-parameters"></a><a id="vchordrq-prefilter"></a>

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordrq.prefilter` | boolean | `off` | 在重排每个候选之前检查 `WHERE` 条件。 |
| `vchordrq.max_probes` | integer | `-1` | 过滤键扫描在已探查列表用完后最多读取的列表数。`-1` 表示不限，`0` 表示只读 `probes` 个。 |
| `vchordrq.max_scan_tuples` | integer | `-1` | 无论过滤条件如何，产出这么多个候选后停止。`-1` 表示不限。 |
| `vchordg.max_scan_tuples` | integer | `-1` | vchordg 的同名参数。 |
{.fields meta="type default"}

每种键类型都有默认运算符类，所以不必显式指定；`uuid_hash_ops`、`int4_hash_ops`、`int8_hash_ops` 是对应的哈希版本。`zone_maps` 选项与其他 [vchordrq 索引选项](/zh/docs/vchord/usage/indexing/#indexing-options)列在一起。`sphere()` 返回复合类型 `sphere_vector`、`sphere_halfvec`、`sphere_rabitq8`、`sphere_rabitq4`。
