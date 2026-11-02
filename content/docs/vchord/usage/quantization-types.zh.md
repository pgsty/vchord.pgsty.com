---
title: "量化类型"
linkTitle: "量化类型"
description: "量化不仅可以应用于索引，还可以直接应用于向量本身。为此，VectorChord 提供了用于量化向量的数据类型。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/quantization-types.md"
math: true
aliases:
  - "/zh/docs/usage/quantization-types/"
  - "/vectorchord/usage/quantization-types/"
---

{{< badge text="since v1.1.0" tone="info" >}}


量化不仅可以应用于索引，还可以直接应用于向量本身。为此，VectorChord 提供了专门用于量化向量的数据类型。

`rabitq8` 是量化向量的数据类型。在相同维度下，它的存储开销约为全精度向量（`vector`）的 \(\frac{1}{4}\)，半精度向量（`halfvec`）的 \(\frac{1}{2}\)。该类型以其所使用的量化算法命名。[^exrabitq]

[^exrabitq]: Jianyang Gao, Yutong Gou, Yuexuan Xu, Yongyi Yang, Cheng Long, Raymond Chi-Wing Wong, "Practical and Asymptotically Optimal Quantization of High-Dimensional Vectors in Euclidean Space for Approximate Nearest Neighbor Search", SIGMOD 2025, available at https://arxiv.org/abs/2409.09913.

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding rabitq8(3));
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[0,0,0]'::vector));
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[1,1,1]'::vector));
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[2,2,2]'::vector));
--- ...
SELECT id FROM items ORDER BY embedding <-> quantize_to_rabitq8('[0.9,0.9,1.1]'::vector) LIMIT 100;
```

与普通向量类型一样，也可以在 `rabitq8` 类型的列上创建索引。

```sql
CREATE INDEX ON items USING vchordrq (embedding rabitq8_l2_ops);
```

通过使用 `rabitq8`，表大小和索引大小都将缩小为使用 `vector` 类型时的 \(\frac{1}{4}\)。其代价是量化会明显折损性能与精度。因此，它适用于检索大量候选结果的场景。

此外，VectorChord 还提供了 `rabitq4` 类型。`rabitq8` 量化向量在每个维度上使用 \(8\) 比特，而 `rabitq4` 量化向量在每个维度上仅使用 \(4\) 比特。它专为在受限环境下优先追求低存储开销而非高精度的场景而设计。

<a id="Reference"></a>
## 参考 {#reference}

### 操作符类 {#operator-classes}

请参阅：

* [操作符类（`vchordrq`）](/zh/docs/vchord/usage/indexing/#operator-classes)。
* [操作符类（`vchordg`）](/zh/docs/vchord/usage/graph-index/#operator-classes)。

<a id="Types"></a>
### 数据类型 {#types}

#### `rabitq8` {#rabitq8}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用 `uint8` 进行内部存储的量化向量数据类型。基于扩展版 RaBitQ 算法。[^exrabitq]
- 文本表示：与 `vector`/`halfvec` 不同，`rabitq8` 的文本表示更为复杂。假设维度为 \(d\)，它由括在圆括号中的 \(4\) 个浮点数数组与括在方括号中的 \(d\) 个 `uint8` 整数数组拼接而成。例如 `(2.999999, 160.63234, 647, 2.8498733)[255, 205, 187]`。其内部解释无需手动处理，但您可以通过 `dequantize_to_vector(rabitq8)` / `dequantize_to_halfvec(rabitq8)` 获取它所代表的近似向量。

#### `rabitq4` {#rabitq4}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：使用 `uint4` 进行内部存储的量化向量数据类型。基于扩展版 RaBitQ 算法。[^exrabitq]
- 文本表示：与 `vector`/`halfvec` 不同，`rabitq4` 的文本表示更为复杂。假设维度为 \(d\)，它由括在圆括号中的 \(4\) 个浮点数数组与括在方括号中的 \(d\) 个 `uint4` 整数数组拼接而成。例如 `(2.999999, 9.420722, 38, 2.8498733)[15, 12, 11]`。其内部解释无需手动处理，但您可以通过 `dequantize_to_vector(rabitq4)` / `dequantize_to_halfvec(rabitq4)` 获取它所代表的近似向量。

<a id="Functions"></a>
### 函数 {#functions}

<a id="quantize-to-rabitq8-vector"></a>
#### `quantize_to_rabitq8(vector)` {#quantize-to-rabitq8-vector}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：将向量量化为 `rabitq8`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。
- 返回值：`rabitq8`，量化后的向量
- 参数：
    - `vector`，待量化的向量
- 示例：
    - `SELECT quantize_to_rabitq8('[1,1,1]'::vector)`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (vector AS rabitq8) WITH FUNCTION quantize_to_rabitq8(vector) AS ASSIGNMENT` 手动创建。

<a id="quantize-to-rabitq8-halfvec"></a>
#### `quantize_to_rabitq8(halfvec)` {#quantize-to-rabitq8-halfvec}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：将半精度向量量化为 `rabitq8`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。
- 返回值：`rabitq8`，量化后的向量
- 参数：
    - `halfvec`，待量化的向量
- 示例：
    - `SELECT quantize_to_rabitq8('[1,1,1]'::halfvec)`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (halfvec AS rabitq8) WITH FUNCTION quantize_to_rabitq8(halfvec) AS ASSIGNMENT` 手动创建。

<a id="dequantize-to-vector-rabitq8"></a>
#### `dequantize_to_vector(rabitq8)` {#dequantize-to-vector-rabitq8}

{{< badge text="since v1.1.1" tone="info" >}}

- 说明：将量化向量反量化为 `vector`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。使用此函数无法精确重建原始向量。
- 返回值：`vector`，反量化后的向量
- 参数：
    - `rabitq8`，待反量化的量化向量
- 示例：
    - `SELECT dequantize_to_vector(quantize_to_rabitq8('[1,1,1]'::vector))`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (rabitq8 AS vector) WITH FUNCTION dequantize_to_vector(rabitq8) AS ASSIGNMENT` 手动创建。

<a id="dequantize-to-halfvec-rabitq8"></a>
#### `dequantize_to_halfvec(rabitq8)` {#dequantize-to-halfvec-rabitq8}

{{< badge text="since v1.1.1" tone="info" >}}

- 说明：将量化向量反量化为 `halfvec`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。使用此函数无法精确重建原始向量。
- 返回值：`halfvec`，反量化后的向量
- 参数：
    - `rabitq8`，待反量化的量化向量
- 示例：
    - `SELECT dequantize_to_halfvec(quantize_to_rabitq8('[1,1,1]'::halfvec))`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (rabitq8 AS halfvec) WITH FUNCTION dequantize_to_halfvec(rabitq8) AS ASSIGNMENT` 手动创建。

<a id="quantize-to-rabitq4-vector"></a>
#### `quantize_to_rabitq4(vector)` {#quantize-to-rabitq4-vector}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：将向量量化为 `rabitq4`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。
- 返回值：`rabitq4`，量化后的向量
- 参数：
    - `vector`，待量化的向量
- 示例：
    - `SELECT quantize_to_rabitq4('[1,1,1]'::vector)`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (vector AS rabitq4) WITH FUNCTION quantize_to_rabitq4(vector) AS ASSIGNMENT` 手动创建。

<a id="quantize-to-rabitq4-halfvec"></a>
#### `quantize_to_rabitq4(halfvec)` {#quantize-to-rabitq4-halfvec}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：将半精度向量量化为 `rabitq4`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。
- 返回值：`rabitq4`，量化后的向量
- 参数：
    - `halfvec`，待量化的向量
- 示例：
    - `SELECT quantize_to_rabitq4('[1,1,1]'::halfvec)`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (halfvec AS rabitq4) WITH FUNCTION quantize_to_rabitq4(halfvec) AS ASSIGNMENT` 手动创建。

<a id="dequantize-to-vector-rabitq4"></a>
#### `dequantize_to_vector(rabitq4)` {#dequantize-to-vector-rabitq4}

{{< badge text="since v1.1.1" tone="info" >}}

- 说明：将量化向量反量化为 `vector`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。使用此函数无法精确重建原始向量。
- 返回值：`vector`，反量化后的向量
- 参数：
    - `rabitq4`，待反量化的量化向量
- 示例：
    - `SELECT dequantize_to_vector(quantize_to_rabitq4('[1,1,1]'::vector))`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (rabitq4 AS vector) WITH FUNCTION dequantize_to_vector(rabitq4) AS ASSIGNMENT` 手动创建。

<a id="dequantize-to-halfvec-rabitq4"></a>
#### `dequantize_to_halfvec(rabitq4)` {#dequantize-to-halfvec-rabitq4}

{{< badge text="since v1.1.1" tone="info" >}}

- 说明：将量化向量反量化为 `halfvec`。请注意，在不同的 VectorChord 版本或不同的机器上，该函数对相同输入可能会产生略有差异的结果。使用此函数无法精确重建原始向量。
- 返回值：`halfvec`，反量化后的向量
- 参数：
    - `rabitq4`，待反量化的量化向量
- 示例：
    - `SELECT dequantize_to_halfvec(quantize_to_rabitq4('[1,1,1]'::halfvec))`
- 注意：该函数没有对应的默认类型转换（`CAST`）。如有需要，您可以使用 `CREATE CAST (rabitq4 AS halfvec) WITH FUNCTION dequantize_to_halfvec(rabitq4) AS ASSIGNMENT` 手动创建。

<a id="Operators"></a>
### 操作符 {#operators}

#### `<->(rabitq8, rabitq8)` {#rabitq8-l2-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的 L2 距离。
- 返回值：`real`，两个量化向量的 L2 距离
- 参数：
    - `rabitq8`
    - `rabitq8`

#### `<#>(rabitq8, rabitq8)` {#rabitq8-ip-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的负点积距离。
- 返回值：`real`，两个量化向量的负点积距离
- 参数：
    - `rabitq8`
    - `rabitq8`

#### `<=>(rabitq8, rabitq8)` {#rabitq8-cosine-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的余弦距离。
- 返回值：`real`，两个量化向量的余弦距离
- 参数：
    - `rabitq8`
    - `rabitq8`

#### `<->(rabitq4, rabitq4)` {#rabitq4-l2-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的 L2 距离。
- 返回值：`real`，两个量化向量的 L2 距离
- 参数：
    - `rabitq4`
    - `rabitq4`

#### `<#>(rabitq4, rabitq4)` {#rabitq4-ip-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的负点积距离。
- 返回值：`real`，两个量化向量的负点积距离
- 参数：
    - `rabitq4`
    - `rabitq4`

#### `<=>(rabitq4, rabitq4)` {#rabitq4-cosine-op}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：计算两个量化向量之间的余弦距离。
- 返回值：`real`，两个量化向量的余弦距离
- 参数：
    - `rabitq4`
    - `rabitq4`
