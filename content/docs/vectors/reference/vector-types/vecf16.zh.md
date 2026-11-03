---
title: "半精度向量：`vecf16`"
linkTitle: "半精度向量"
description: "vecf16 以半精度浮点数格式存储，利用 16 位浮点数，与标准 vector 相比仅占用一半的内存和带宽。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/vector-types/vecf16.md"
math: true
aliases:
  - "/reference/vector-types/vecf16/"
icon: fa-solid fa-compress
---

`vecf16` 以半精度数值格式存储，充分利用了 16 位浮点数（FP16）的优势，与标准 32 位浮点数的 `vector` 相比，仅使用一半的内存和内存带宽。

以下是创建包含 `vecf16` 列的表并插入数据的示例：

```sql {hl_lines=["3"]}
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding vecf16(3) NOT NULL
);

INSERT INTO items (embedding) VALUES ('[0.1, 0.2, 0]'), ('[0, 0.1, 0.2]');
```

同样可以在 `vecf16` 类型上创建索引：

```sql
CREATE INDEX your_index_name ON items USING vectors (embedding vecf16_l2_ops);

SELECT * FROM items ORDER BY embedding <-> '[0.3,0.2,0.1]' LIMIT 1;
```

我们支持三种用于计算两个 `vecf16` 值之间距离的操作符：

- `<->`（`vecf16_l2_ops`）：平方欧氏距离，定义为 \(\Sigma (x_i - y_i) ^ 2\)。
- `<#>`（`vecf16_dot_ops`）：负点积，定义为 \(- \Sigma x_iy_i\)。
- `<=>`（`vecf16_cos_ops`）：余弦距离，定义为 \(1 - \frac{\Sigma x_iy_i}{\sqrt{\Sigma x_i^2 \Sigma y_i^2}}\)。
