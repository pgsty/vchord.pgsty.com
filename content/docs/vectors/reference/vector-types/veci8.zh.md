---
title: "8 位整数向量：`veci8`"
linkTitle: "8 位整数向量"
description: "Int8 是用于表示有符号整数的数据类型，使用 8 位内存存储范围在 -128 到 127 之间的整数，显著降低向量存储的内存占用。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/vector-types/veci8.md"
math: true
aliases:
  - "/reference/vector-types/veci8/"
icon: fa-solid fa-microchip
---

{{< badge text="since v0.3.0" tone="info" >}}


`Int8` 是一种用于表示有符号整数的数据类型，代表“8 位整数（integer 8-bit）”，使用 8 比特（1 字节）内存存储一个值，可表示范围为 `-128` 到 `127` 的整数。

由于向量中的每个元素仅需 8 比特（1 字节）内存，使用 `veci8` 可以大幅减少程序的整体内存占用。

以下是创建包含 `veci8` 列的表并插入数据的示例：

```sql {hl_lines=["3"]}
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding veci8(3) NOT NULL
);

INSERT INTO items (embedding) VALUES ('[1, 2, 0]'), ('[-1, 15, -2]');
```

同样可以在 `veci8` 类型上创建索引：

```sql
CREATE INDEX your_index_name ON items USING vectors (embedding veci8_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[0.3,0.2,0.1]' LIMIT 1;
```

我们支持三种用于计算两个 `veci8` 值之间距离的操作符：

- `<->`（`veci8_l2_ops`）：平方欧氏距离，定义为 \(\Sigma (x_i - y_i) ^ 2\)。
- `<#>`（`veci8_dot_ops`）：负点积，定义为 \(- \Sigma x_iy_i\)。
- `<=>`（`veci8_cos_ops`）：余弦距离，定义为 \(1 - \frac{\Sigma x_iy_i}{\sqrt{\Sigma x_i^2 \Sigma y_i^2}}\)。
