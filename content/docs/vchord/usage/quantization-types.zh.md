---
title: "量化类型"
linkTitle: "量化类型"
description: "用 rabitq8 和 rabitq4 列类型以每维 8 或 4 比特存储向量，并了解它在精度上的代价。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/quantization-types.md"
aliases:
  - "/docs/usage/quantization-types/"
  - "/vectorchord/usage/quantization-types/"
icon: fa-solid fa-compress
---

vchord 的索引内部已经压缩了向量，但表里仍然存着每个向量的完整大小。到了几亿行，这一列就占了数据库的大头。pgvector 的 `halfvec` 能把它减半，vchord 的 `rabitq8` 和 `rabitq4` 类型更进一步：基于[扩展 RaBitQ](https://arxiv.org/abs/2409.09913)，每个向量存成每维一个 8 比特或 4 比特的编码，外加四个缩放值：

| 类型 | 一条 768 维向量的大致大小 | 相对 `vector` |
| --- | --- | --- |
| `vector` | 3,072 字节 | 1 |
| `halfvec` | 1,536 字节 | 1/2 |
| `rabitq8` | 784 字节 | 约 1/4 |
| `rabitq4` | 400 字节 | 约 1/8 |

代价是量化向量之间的距离都是估算值，在索引里和在 SQL 里都一样。用 `rabitq8` 检索候选时，召回率损失通常不到 1%；`rabitq4` 损失更多。如果最终排序需要精确距离，就把原始向量保存在别处，用它们对排名靠前的候选重新排序。

## 使用方法 {#basic-usage}

插入时量化向量，查询向量也用同样的方式量化：

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding rabitq8(3));

INSERT INTO items (embedding) VALUES
    (quantize_to_rabitq8('[0, 0, 0]'::vector)),
    (quantize_to_rabitq8('[1, 1, 1]'::vector)),
    (quantize_to_rabitq8('[2, 2, 2]'::vector));

CREATE INDEX ON items USING vchordrq (embedding rabitq8_l2_ops);

SELECT id FROM items
ORDER BY embedding <-> quantize_to_rabitq8('[0.9, 0.9, 1.1]'::vector)
LIMIT 10;
```

这两种类型可以用于 vchordrq 和 vchordg，可以组成数组做[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)，也支持[距离范围](/zh/docs/vchord/usage/filtering/#distance-range)。按距离选用对应的 `rabitq8_*` 或 `rabitq4_*` 运算符类。

如果想让应用或 ORM 直接插入普通的向量字面量，注册一次赋值转换即可：

```sql
CREATE CAST (vector AS rabitq8) WITH FUNCTION quantize_to_rabitq8(vector) AS ASSIGNMENT;
```

## 限制 {#limits}

<a id="input-validation"></a>

- 这两种类型上的索引不能用 `residual_quantization`。
- `rabitq8(n)` 中声明的维度在插入时还不检查（[#31](https://github.com/pgsty/vchord/issues/31)），不过列上的索引会拒绝维度不符的行。在此之前，请在应用中检查维度。
- 用 `dequantize_to_vector` 或 `dequantize_to_halfvec` 转换回去，得到的是原始向量的近似值，并受 pgvector 的维度上限约束：`vector` 最多 16,000 维，`halfvec` 最多 4,000 维。

## 参考 {#reference}

<a id="operator-classes"></a><a id="types"></a><a id="rabitq8"></a><a id="rabitq4"></a><a id="operators"></a><a id="rabitq8-l2-op"></a><a id="rabitq8-ip-op"></a><a id="rabitq8-cosine-op"></a><a id="rabitq4-l2-op"></a><a id="rabitq4-ip-op"></a><a id="rabitq4-cosine-op"></a>

两种类型最多 65,535 维；vchordrq 最多能索引 60,000 维，vchordg 最多 30,000 维。它们支持 `<->`、`<#>`、`<=>`，返回估算距离，运算符类见 [vchordrq](/zh/docs/vchord/usage/indexing/#operator-classes) 和 [vchordg](/zh/docs/vchord/usage/graph-index/#operator-classes)。文本形式如 `(2.99, 160.6, 647, 2.85)[255, 205, 187]`，先是四个缩放值，然后每维一个编码；请用下面的函数生成，而不要手写。

### 函数 {#functions}

<a id="Functions"></a><a id="quantize-to-rabitq8-vector"></a><a id="quantize-to-rabitq8-halfvec"></a><a id="dequantize-to-vector-rabitq8"></a><a id="dequantize-to-halfvec-rabitq8"></a><a id="quantize-to-rabitq4-vector"></a><a id="quantize-to-rabitq4-halfvec"></a><a id="dequantize-to-vector-rabitq4"></a><a id="dequantize-to-halfvec-rabitq4"></a>

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `quantize_to_rabitq8(vector \| halfvec)` | `rabitq8` | 量化为每维 8 比特。 |
| `quantize_to_rabitq4(vector \| halfvec)` | `rabitq4` | 量化为每维 4 比特。 |
| `dequantize_to_vector(rabitq8 \| rabitq4)` | `vector` | 近似还原原始向量。 |
| `dequantize_to_halfvec(rabitq8 \| rabitq4)` | `halfvec` | 以半精度近似还原原始向量。 |
{.fields meta="type"}
