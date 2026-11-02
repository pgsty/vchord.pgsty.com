---
title: "相似度过滤"
linkTitle: "相似度过滤"
description: "通常我们使用 ORDER BY 和 LIMIT 子句执行向量搜索。在某些场景下，您可能希望使用 WHERE 子句过滤掉距离查询向量较远的向量。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/similarity-filter.md"
math: true
aliases:
  - "/zh/docs/usage/similarity-filter/"
  - "/vectorchord/usage/similarity-filter/"
  - "/docs/vchord/usage/range-query/"
  - "/vectorchord/usage/range-query/"
---

通常，我们会使用 `ORDER BY` 和 `LIMIT` 子句来执行向量搜索。但在某些情况下，您可能希望使用 `WHERE` 子句过滤掉距离查询向量太远的向量。很自然地，您可能会写出如下 SQL：

```sql
EXPLAIN (COSTS FALSE) 
SELECT * FROM items WHERE embedding <-> '[0, 0, 0]' < 0.1 ORDER BY embedding <-> '[0, 0, 0]' LIMIT 10;
                                  QUERY PLAN                                   
-------------------------------------------------------------------------------
 Limit
   ->  Index Scan using items_embedding_idx on items
         Order By: (embedding <-> '[0,0,0]'::vector)
         Filter: ((embedding <-> '[0,0,0]'::vector) < '0.1'::double precision)
```

返回的结果虽然符合预期，但这种写法的性能却很差。这是因为如果落在距离阈值内的向量少于 \(10\) 个，PostgreSQL 会强制索引继续搜索以凑够 \(10\) 条结果，从而遍历耗尽整个搜索空间。

为了避免这种情况，您可以使用特定语法将过滤条件直接下推（push down）到向量索引中，使索引一旦发现搜索区域超出指定距离便立即停止搜索。我们将这种可以下推到索引中的基于距离的过滤条件称为**相似度过滤（similarity filter）**。

```sql
EXPLAIN (COSTS FALSE) 
SELECT * FROM items WHERE embedding <<->> sphere('[0, 0, 0]'::vector, 0.1) ORDER BY embedding <-> '[0, 0, 0]' LIMIT 10;
                               QUERY PLAN                               
------------------------------------------------------------------------
 Limit
   ->  Index Scan using items_embedding_idx on items
         Index Cond: (embedding <<->> '("[0,0,0]",0.1)'::sphere_vector)
         Order By: (embedding <-> '[0,0,0]'::vector)
```

当且仅当两个向量之间的 L2 距离小于 `0.1` 时，`embedding <<->> sphere('[0, 0, 0]'::vector, 0.1)` 的求值结果为 `true`。对于负内积请使用 `<<#>>` 操作符，对于余弦距离请使用 `<<=>>` 操作符。

此外，如果您只指定 `WHERE` 子句而不使用 `ORDER BY`，索引依然能够被有效利用。

```sql
EXPLAIN (COSTS FALSE) 
SELECT * FROM items WHERE embedding <<->> sphere('[0, 0, 0]'::vector, 0.1);
                            QUERY PLAN                            
------------------------------------------------------------------
 Index Scan using items_embedding_idx on items
   Index Cond: (embedding <<->> '("[0,0,0]",0.1)'::sphere_vector)
```

<a id="Reference"></a>
## 参考 {#reference}

### 操作符类 {#operator-classes}

请参阅：

* [操作符类（`vchordrq`）](/zh/docs/vchord/usage/indexing/#operator-classes)。
* [操作符类（`vchordg`）](/zh/docs/vchord/usage/graph-index/#operator-classes)。

<a id="Types"></a>
### 数据类型 {#types}

<a id="sphere-vector"></a>
#### `sphere_vector` {#sphere-vector}

- 说明：球体（Sphere）。
- 定义：`(center vector, radius REAL)`。

<a id="sphere-halfvec"></a>
#### `sphere_halfvec` {#sphere-halfvec}

- 说明：球体（Sphere）。
- 定义：`(center halfvec, radius REAL)`。

<a id="sphere-rabitq8"></a>
#### `sphere_rabitq8` {#sphere-rabitq8}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：球体（Sphere）。
- 定义：`(center rabitq8, radius REAL)`。

<a id="sphere-rabitq4"></a>
#### `sphere_rabitq4` {#sphere-rabitq4}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：球体（Sphere）。
- 定义：`(center rabitq4, radius REAL)`。

<a id="Functions"></a>
### 函数 {#functions}

<a id="sphere-vector-real"></a>
#### `sphere(vector, real)` {#sphere-vector-real}

- 说明：通过球心和半径创建一个球体。
- 定义：`SELECT ROW($1, $2)`。
- 返回值：`sphere_vector`
- 参数：
    - `vector`，球体的球心
    - `real`，球体的半径
- 示例：
    - `SELECT sphere('[0,0,0]'::vector, 1.0)`

<a id="sphere-halfvec-real"></a>
#### `sphere(halfvec, real)` {#sphere-halfvec-real}

- 说明：通过球心和半径创建一个球体。
- 定义：`SELECT ROW($1, $2)`。
- 返回值：`sphere_halfvec`
- 参数：
    - `halfvec`，球体的球心
    - `real`，球体的半径
- 示例：
    - `SELECT sphere('[0,0,0]'::halfvec, 1.0)`

<a id="sphere-rabitq8-real"></a>
#### `sphere(rabitq8, real)` {#sphere-rabitq8-real}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：通过球心和半径创建一个球体。
- 定义：`SELECT ROW($1, $2)`。
- 返回值：`sphere_rabitq8`
- 参数：
    - `rabitq8`，球体的球心
    - `real`，球体的半径
- 示例：
    - `SELECT sphere(quantize_to_rabitq8('[0,0,0]'::vector), 1.0)`

<a id="sphere-rabitq4-real"></a>
#### `sphere(rabitq4, real)` {#sphere-rabitq4-real}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：通过球心和半径创建一个球体。
- 定义：`SELECT ROW($1, $2)`。
- 返回值：`sphere_rabitq4`
- 参数：
    - `rabitq4`，球体的球心
    - `real`，球体的半径
- 示例：
    - `SELECT sphere(quantize_to_rabitq4('[0,0,0]'::vector), 1.0)`

<a id="Operators"></a>
### 操作符 {#operators}

<a id="vector-sphere-vector"></a>
#### `<<->>(vector, sphere_vector)`

- 说明：使用 L2 度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `vector`，待检测的向量
    - `sphere_vector`，球体

<a id="vector-sphere-vector"></a>
#### `<<#>>(vector, sphere_vector)`

- 说明：使用负点积度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `vector`，待检测的向量
    - `sphere_vector`，球体

<a id="vector-sphere-vector"></a>
#### `<<=>>(vector, sphere_vector)`

- 说明：使用余弦度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `vector`，待检测的向量
    - `sphere_vector`，球体

<a id="halfvec-sphere-halfvec"></a>
#### `<<->>(halfvec, sphere_halfvec)`

- 说明：使用 L2 度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `halfvec`，待检测的向量
    - `sphere_halfvec`，球体

<a id="halfvec-sphere-halfvec"></a>
#### `<<#>>(halfvec, sphere_halfvec)`

- 说明：使用负点积度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `halfvec`，待检测的向量
    - `sphere_halfvec`，球体

<a id="halfvec-sphere-halfvec"></a>
#### `<<=>>(halfvec, sphere_halfvec)`

- 说明：使用余弦度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `halfvec`，待检测的向量
    - `sphere_halfvec`，球体

<a id="rabitq8-sphere-rabitq8"></a>
#### `<<->>(rabitq8, sphere_rabitq8)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用 L2 度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq8`，待检测的向量
    - `sphere_rabitq8`，球体

<a id="rabitq8-sphere-rabitq8"></a>
#### `<<#>>(rabitq8, sphere_rabitq8)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用负点积度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq8`，待检测的向量
    - `sphere_rabitq8`，球体

<a id="rabitq8-sphere-rabitq8"></a>
#### `<<=>>(rabitq8, sphere_rabitq8)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用余弦度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq8`，待检测的向量
    - `sphere_rabitq8`，球体

<a id="rabitq4-sphere-rabitq4"></a>
#### `<<->>(rabitq4, sphere_rabitq4)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用 L2 度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq4`，待检测的向量
    - `sphere_rabitq4`，球体

<a id="rabitq4-sphere-rabitq4"></a>
#### `<<#>>(rabitq4, sphere_rabitq4)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用负点积度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq4`，待检测的向量
    - `sphere_rabitq4`，球体

<a id="rabitq4-sphere-rabitq4"></a>
#### `<<=>>(rabitq4, sphere_rabitq4)`

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用余弦度量检测向量是否位于球体内部。
- 返回值：布尔值（boolean）
- 参数：
    - `rabitq4`，待检测的向量
    - `sphere_rabitq4`，球体
