---
title: "向量量化与稀疏向量"
linkTitle: "向量量化与稀疏向量"
description: "pgvector 中的半精度向量（halfvec）、二值量化（bit）、稀疏向量（sparsevec）与套娃（Matryoshka）子向量索引。"
weight: 40
upstream_link: https://github.com/pgvector/pgvector#half-precision-vectors
math: true
---

`pgvector` 支持四种向量数据类型，方便您在内存占用、维度上限与检索召回率之间灵活权衡：

| 数据类型 | 元素精度 | 索引最大维度上限 | 存储空间占用 |
| :--- | :--- | :---: | :--- |
| `vector(n)` | 32 位浮点（`float32`） | 2,000 维 | \(4n + 8\) 字节 |
| `halfvec(n)` | 16 位半精度浮点（`float16`） | 4,000 维 | \(2n + 8\) 字节 |
| `bit(n)` | 1 位二值比特（`0` / `1`） | 64,000 维 | \(\lceil n / 8 \rceil + 8\) 字节 |
| `sparsevec(n)` | 非零 `下标:float32` 键值对 | 最多 1,000 个非零元素（总维度可达 100 万） | \(8 \times \text{nnz} + 16\) 字节 |

> [!TIP] `vchord` 中的 RaBitQ 量化
> 除了 `pgvector` 内置的量化类型外，[`vchord`](/zh/docs/vchord/) 还提供 `rabitq8`（8-bit）与 `rabitq4`（4-bit）专用量化向量类型，并在 `vchordrq` 索引中支持高达 **60,000 维**的超长向量。详见 [`vchord` 量化类型](/zh/docs/vchord/usage/quantization-types/)。

---

## 半精度浮点向量（`halfvec`）

使用 `halfvec` 类型（自 `pgvector 0.7.0` 起引入）存储 16 位半精度浮点向量，相比 `vector` 可将表与索引体积直接缩减 50%：

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding halfvec(3)
);

CREATE INDEX ON items USING hnsw (embedding halfvec_l2_ops);
```

### 半精度表达式索引（标量量化）

如果您希望在表中保留完整的 32 位 `vector` 精度（或者需要为 2,001 至 4,000 维的向量建索引，例如 3,072 维的 OpenAI `text-embedding-3-large`），可以通过表达式索引将 `vector` 转换为 `halfvec`：

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(3072)
);

CREATE INDEX ON items USING hnsw ((embedding::halfvec(3072)) halfvec_l2_ops);

-- 查询时使用与索引一致的转换表达式
SELECT * FROM items
ORDER BY embedding::halfvec(3072) <-> '[1,2,3,...]'
LIMIT 5;
```

---

## 二值向量（`bit`）与二值量化

结合 PostgreSQL 内置的 `bit(n)` 类型与 `pgvector` 的汉明距离（`<~>`）及杰卡德距离（`<%>`）操作符，可存储并索引高达 **64,000 位**的二值向量：

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding bit(3)
);

INSERT INTO items (embedding) VALUES ('000'), ('111');

-- 按汉明距离检索最近邻
SELECT * FROM items ORDER BY embedding <~> '101' LIMIT 5;

-- 创建 HNSW 索引
CREATE INDEX ON items USING hnsw (embedding bit_hamming_ops);
```

### 二值量化索引 + 全精度重排序（Re-Ranking）

使用 `binary_quantize(vector)` 函数在表达式索引中将每个维度压缩为 1 比特（大于 `0` 为 `1`，否则为 `0`），并在子查询召回候选集后使用原始 `vector` 列执行精确重排：

```sql
CREATE INDEX ON items USING hnsw ((binary_quantize(embedding)::bit(3)) bit_hamming_ops);

SELECT * FROM (
    SELECT * FROM items
    ORDER BY binary_quantize(embedding)::bit(3) <~> binary_quantize('[1,-2,3]')
    LIMIT 20
) AS candidates
ORDER BY embedding <=> '[1,-2,3]'
LIMIT 5;
```

---

## 稀疏向量（`sparsevec`）

使用 `sparsevec`（自 `pgvector 0.7.0` 起引入）存储绝大部分维度为零的稀疏向量（例如 SPLADE、BGE-M3 稀疏输出，或由 [`pg_bestmatch`](/zh/docs/bestmatch/) 生成的 BM25 词频权重向量）。

### 稀疏向量字面量格式

语法格式为 `'{下标1:值1,下标2:值2}/总维度'`，其中下标**从 1 开始计数**：

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding sparsevec(5)
);

INSERT INTO items (embedding) VALUES ('{1:1,3:2,5:3}/5'), ('{1:4,3:5,5:6}/5');

-- 检索最近邻
SELECT * FROM items ORDER BY embedding <-> '{1:3,3:1,5:2}/5' LIMIT 5;

-- 创建 HNSW 索引（支持最多 1,000 个非零元素）
CREATE INDEX ON items USING hnsw (embedding sparsevec_l2_ops);
```

---

## 套娃（Matryoshka）子向量索引（`subvector`）

对于支持套娃表示学习（Matryoshka Representation Learning, MRL）的嵌入模型，可以使用 `subvector(vector, start, count)` 仅对前 \(M\) 个维度建立轻量级索引，再利用完整向量执行精确重排：

```sql
CREATE INDEX ON items USING hnsw ((subvector(embedding, 1, 512)::vector(512)) vector_cosine_ops);

SELECT * FROM (
    SELECT * FROM items
    ORDER BY subvector(embedding, 1, 512)::vector(512) <=> subvector('[1,2,3,...]'::vector, 1, 512)
    LIMIT 20
) AS candidates
ORDER BY embedding <=> '[1,2,3,...]'
LIMIT 5;
```
