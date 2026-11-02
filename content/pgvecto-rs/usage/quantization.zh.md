---
title: "量化"
linkTitle: "量化"
description: "量化是一种在可接受的精度损失下降低内存消耗与计算复杂度的技术。在向量搜索场景中，主要有乘积量化和标量量化两种类型。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/usage/quantization.md"
aliases:
  - "/usage/quantization/"
---

量化（Quantization）是一种在可接受的精度损失范围内，降低内存消耗和计算复杂度的技术。在向量搜索中，主要有两种量化方式：乘积量化（Product Quantization）和标量量化（Scalar Quantization）。

## 乘积量化（Product Quantization） {#production-quantization}

乘积量化通过在数据集上训练多个子空间聚类模型，将每个高维向量映射为一组聚类中心索引列表。它常用于解决高维向量数据内存占用过高的问题。

在 `pgvecto.rs` 中，您可以通过以下方式启用乘积量化：

```sql
CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
[indexing.ivf]
quantization.product.ratio = "x16"
$$);
```

更多配置可在[索引文档](/zh/pgvecto-rs/usage/indexing/)中找到。

## 标量量化（Scalar Quantization） {#scalar-quantization}

标量量化将每个标量值映射为低比特格式（例如从 32 位浮点数映射为 8 位整数）。通常情况下，这不会对精度造成明显影响，但能有效降低内存占用并提升查询性能。`pgvecto.rs` 支持通过以下方式启用 `uint8` 标量量化：

```sql
CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = "[indexing.hnsw.quantization.scalar]");
```

<a id="Suggestions"></a>
## 选择建议 {#suggestions}

当需要使用量化时，建议始终优先尝试标量量化。它在精度与内存占用之间取得了良好的平衡。

如果内存占用仍然过高，可以尝试乘积量化。该方法能大幅降低内存占用，但可能会影响精度。由于乘积量化的效果与训练数据集高度相关，您需要尝试不同的 `ratio` 和 `sample` 参数值，以找到最适合您数据集的配置。

此外，您还可以使用主成分分析（PCA）等降维方法来降低向量维度。
