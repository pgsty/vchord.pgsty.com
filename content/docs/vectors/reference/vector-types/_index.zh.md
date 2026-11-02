---
title: "向量类型"
linkTitle: "向量类型"
description: "在前面的索引和搜索章节中，我们接触了 vector 类型。本节将探讨更多向量类型及其在向量搜索领域的应用。"
weight: 40
upstream_link: https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/vector-types.md
aliases:
  - "/reference/vector-types/"
  - "/usage/vector-types/"
---

在前面的[索引](/zh/docs/vectors/usage/indexing/)和[搜索](/zh/docs/vectors/usage/search/)章节中，我们已经接触了标准的 `vector` 类型。本节将探讨更多向量数据类型及其在向量搜索领域的应用：

- [半精度向量（Half-Precision Vector）](/zh/docs/vectors/reference/vector-types/vecf16/)
- [8 位整数向量（8-Bit Integer Vector）](/zh/docs/vectors/reference/vector-types/veci8/) {{< badge text="since v0.3.0" tone="info" >}}
- [稀疏向量（Sparse Vector）](/zh/docs/vectors/reference/vector-types/svector/) {{< badge text="since v0.3.0" tone="info" >}}
- [二值向量（Binary Vector）](/zh/docs/vectors/reference/vector-types/bvector/) {{< badge text="since v0.3.0" tone="info" >}}

## 低精度索引 {#low-precision-indexing}

{{< badge text="since v0.3.0" tone="info" >}}

为了提升在 `vector` 列上的查询速度并降低内存占用，可以考虑使用表达式索引，基于 `vecf16`、`veci8` 或 `bvector` 类型创建低精度索引，而非直接对 `vector` 类型创建全精度索引：

```sql
CREATE TABLE t (val vector(3));
INSERT INTO t (val) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);

-- 在 vector 列上创建 bvector 二值向量索引
-- 注意：在构建索引时，Float32 向量会被截断为 0 或 1 的整数
CREATE INDEX lp_bin ON t USING vectors ((binarize(val)::bvector(3)) bvector_l2_ops);

-- 在 vector 列上创建 vecf16 半精度向量索引
CREATE INDEX lp_f16 ON t USING vectors ((val::vecf16(3)) vecf16_l2_ops);

-- 在 vector 列上创建 veci8 整数向量索引
-- 注意：在构建索引时，Float32 向量会被截断为 -128 到 127 之间的整数
CREATE INDEX lp_i8 ON t USING vectors ((val::veci8(3)) veci8_l2_ops);
```

## 缩短嵌入向量（Shortening Embedding） {#shortening-embedding}

{{< badge text="since v0.3.0" tone="info" >}}

部分嵌入模型（例如 OpenAI 的 `text-embedding-3-small` 和 `text-embedding-3-large`）支持[缩短嵌入向量](https://openai.com/blog/new-embedding-models-and-api-updates)，即直接移除向量序列末尾的部分数值，而不会丢失嵌入向量的核心概念表达能力。

在某些场景下，可能需要在嵌入生成并入库之后再动态调整检索维度。`pgvecto.rs` 提供了通过数组切片语法直接使用缩短后的嵌入向量进行查询和建索引的方法：

```sql
CREATE TABLE t (val vector(3));
INSERT INTO t (val) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
CREATE INDEX ON t USING vectors (val vector_l2_ops);

-- 仅使用前两个维度计算距离
SELECT * from t ORDER BY (val[:2])::vector(2) <-> '[3, 2]'::vector;
```

自 `v0.3.0` 版本起，`pgvecto.rs` 中的所有向量数据类型均支持缩短嵌入向量切片操作。

<a id="Casts"></a>
## 类型转换 {#casts}

下图展示了不同向量数据类型之间的转换关系，由箭头连接的两个类型可以相互转换（Cast）：

<iframe class="quiver-embed" src="https://q.uiver.app/?q=WzAsNyxbMywyLCJcXHRleHR7dmVjdG9yfSJdLFsyLDAsIlxcdGV4dHt2ZWNmMTZ9Il0sWzQsMCwiXFx0ZXh0e3ZlY2k4fSJdLFszLDUsIlxcdGV4dHtidmVjdG9yfSJdLFswLDIsIlxcdGV4dHtBUlJBWX0iXSxbNiwyLCJcXHRleHR7c3ZlY3Rvcn0iXSxbNywwLCJcXHRleHR7c3ZlY2YxNn0iXSxbMiwwXSxbMCwyXSxbMSwwXSxbMCwxXSxbMywwXSxbMCwzXSxbNCwwLCIiLDAseyJzdHlsZSI6eyJib2R5Ijp7Im5hbWUiOiJkb3R0ZWQifX19XSxbMCw1XSxbNSwwXSxbNiw1XSxbNSw2XSxbMCw0LCIiLDAseyJzdHlsZSI6eyJib2R5Ijp7Im5hbWUiOiJkb3R0ZWQifX19XV0=&embed" width="90%" height="440" style="border-radius: 8px; border: none;"></iframe>

其中，`ARRAY` 是 `PostgreSQL` 的原生数组类型，其余均为 `pgvecto.rs` 定义的向量类型。

以下是向量类型转换的几个示例：
```sql
-- 合法：字符串 ⇒ vector
SELECT '{1,2,3}'::vector;

-- 合法：vector ⇒ ARRAY
SELECT '{1,2,3}'::vector::real[];

-- 合法：ARRAY ⇒ vector ⇒ bvector
SELECT ARRAY[1.0 ,0 ,0]::real[]::vector::bvector;

-- 报错：无法直接将类型 vecf16 转换为 veci8
SELECT '[3, 2]'::vecf16::veci8;

-- 合法：vecf16 ⇒ vector ⇒ veci8
SELECT '[3, 2]'::vecf16::vector::veci8;
```
