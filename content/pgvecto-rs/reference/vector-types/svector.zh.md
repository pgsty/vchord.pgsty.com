---
title: "稀疏向量：`svector`"
linkTitle: "稀疏向量"
description: "与稠密向量不同，稀疏向量具有极高的维度，但仅包含少量非零值。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/vector-types/svector.md"
math: true
aliases:
  - "/reference/vector-types/svector/"
---

{{< badge text="since v0.3.0" tone="info" >}}


与稠密向量不同，稀疏向量（Sparse Vector）通常具有非常高的维度，但其中只包含极少数的非零值。

通常情况下，稀疏向量可以由以下方式生成：
- 词共现矩阵（Word co-occurrence matrices）
- 词频-逆文档频率（TF-IDF）向量或 SPLADE/BGE-M3 词法权重
- 用户-物品交互矩阵（User-item interaction matrices）
- 网络邻接矩阵（Network adjacency matrices）

在 `pgvecto.rs` 中，稀疏向量类型称为 `svector`。

以下是创建包含 `svector` 列的表并插入数据的示例：

```sql {hl_lines=["3"]}
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding svector(10) NOT NULL
);

INSERT INTO items (embedding) VALUES ('[0.1,0,0,0,0,0,0,0,0,0]'), ('[0,0,0,0,0,0,0,0,0,0.5]');
```

同样可以在 `svector` 类型上创建索引：

```sql
CREATE INDEX your_index_name ON items USING vectors (embedding svector_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[0.3,0,0,0,0,0,0,0,0,0]' LIMIT 1;
```

我们支持三种用于计算两个 `svector` 值之间距离的操作符：

- `<->`（`svector_l2_ops`）：平方欧氏距离，定义为 \(\Sigma (x_i - y_i) ^ 2\)。
- `<#>`（`svector_dot_ops`）：负点积，定义为 \(- \Sigma x_iy_i\)。
- `<=>`（`svector_cos_ops`）：余弦距离，定义为 \(1 - \frac{\Sigma x_iy_i}{\sqrt{\Sigma x_i^2 \Sigma y_i^2}}\)。

此外，还提供了 `to_svector` 函数用于构造 `svector`，它会在指定的下标位置设置对应的非零值：


$$
F(index)=\left\{
\begin{array}{rcl}
value[v]  &      & {\exists v \in \mathbb{N}: position[v] = index }\\
0         &      & {else}\\
\end{array} \right.
$$


```sql
-- to_svector(dim: INTEGER, position: ARRAY, value: ARRAY) -> svector
SELECT to_svector(5, '{0, 4}', '{0.3, 0.5}');
-- [0.3, 0, 0, 0, 0.5]
```
