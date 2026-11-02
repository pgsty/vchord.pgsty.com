---
title: "查询与过滤检索"
linkTitle: "查询与过滤检索"
description: "pgvector 的最近邻操作符、距离与相似度计算、向量聚合、带 WHERE 条件的迭代式索引扫描与混合检索。"
weight: 20
upstream_link: https://github.com/pgvector/pgvector#querying
math: true
---

## 距离操作符

`pgvector` 提供六种距离操作符，可用于排序（`ORDER BY`）与阈值过滤：

| 操作符 | 距离度量 | 支持的数据类型 | 说明 |
| :---: | :--- | :--- | :--- |
| `<->` | **欧氏距离（L2）** | `vector`, `halfvec`, `sparsevec` | \(\sqrt{\sum (a_i - b_i)^2}\) |
| `<#>` | **负内积（Negative Inner Product）** | `vector`, `halfvec`, `sparsevec` | 返回 \(-\sum a_i b_i\)（因为 PostgreSQL 索引扫描仅支持升序 `ASC` 排序） |
| `<=>` | **余弦距离（Cosine Distance）** | `vector`, `halfvec`, `sparsevec` | \(1 - \frac{a \cdot b}{\|a\|\|b\|}\)（取值范围 `[0, 2]`） |
| `<+>` | **曼哈顿距离（L1）** | `vector`, `halfvec`, `sparsevec` | \(\sum |a_i - b_i|\)（自 `0.7.0` 起引入） |
| `<~>` | **汉明距离（Hamming Distance）** | `bit` | 两个位向量中不同比特位的数量（`XOR` 置位计数） |
| `<%>` | **杰卡德距离（Jaccard Distance）** | `bit` | \(1 - \frac{|A \cap B|}{|A \cup B|}\) |

> [!TIP] 归一化向量建议
> 如果您的嵌入向量已经归一化为单位长度（例如 OpenAI `text-embedding-3-*` 或 BGE 模型输出），建议优先使用内积（`<#>`）而非余弦距离（`<=>`），以获得更高的 CPU 计算吞吐量。

### 最近邻检索示例

```sql
-- 按 L2 欧氏距离查询最近的 5 条记录
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

-- 按余弦距离查询最近的 5 条记录
SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 5;

-- 按最大内积查询最相似的 5 条记录
SELECT * FROM items ORDER BY embedding <#> '[3,1,2]' LIMIT 5;
```

---

## 计算距离与相似度得分

在查询结果中同时返回距离或相似度数值：

```sql
-- 返回 L2 欧氏距离
SELECT id, embedding <-> '[3,1,2]' AS distance FROM items;

-- 返回真实内积（将负内积乘以 -1）
SELECT id, (embedding <#> '[3,1,2]') * -1 AS inner_product FROM items;

-- 返回余弦相似度（1 - 余弦距离）
SELECT id, 1 - (embedding <=> '[3,1,2]') AS cosine_similarity FROM items;
```

### 距离阈值过滤查询

检索距离在指定半径内的所有记录：

```sql
SELECT * FROM items WHERE embedding <-> '[3,1,2]' < 5;
```

结合 `ORDER BY` 与 `LIMIT` 可直接利用 HNSW 或 IVFFlat 索引：

```sql
SELECT * FROM items
WHERE embedding <-> '[3,1,2]' < 5
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;
```

> [!NOTE] `vchord` 的原生球面范围查询
> 如果您的业务需要频繁按距离半径做范围过滤，[`vchord`](/zh/docs/vchord/) 提供了专用的 `<<->>` 球面操作符（`WHERE embedding <<->> sphere('[3,1,2]'::vector, 5)`），可直接在 `vchordrq` 或 `vchordg` 索引内部完成半径剪枝，而无需强制携带 `ORDER BY ... LIMIT`。详见 [`vchord` 相似度范围过滤](/zh/docs/vchord/usage/similarity-filter/)。

---

## 向量聚合函数

计算一组向量的均值中心（`AVG`）或逐元素累加和（`SUM`）：

```sql
SELECT AVG(embedding) FROM items;

SELECT category_id, AVG(embedding) AS centroid
FROM items
GROUP BY category_id;
```

---

## 条件过滤（`WHERE`）与迭代式索引扫描

将向量相似性检索与结构化关系谓词结合：

```sql
SELECT * FROM items WHERE category_id = 123 ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

### 为过滤列建立索引

1. **在过滤列上创建标准 B-tree 索引**（适用于 `category_id = 123` 选择率极高、仅匹配极少行数的场景）：
   ```sql
   CREATE INDEX ON items (category_id);
   ```
2. **创建部分向量索引（Partial Index）**（适用于仅按少数固定类别过滤的场景）：
   ```sql
   CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WHERE (category_id = 123);
   ```
3. **表分区（Partitioning）**（适用于按租户或时间范围高频过滤的大表）：
   ```sql
   CREATE TABLE items (embedding vector(3), category_id int) PARTITION BY LIST(category_id);
   ```

### 迭代式索引扫描（Iterative Index Scans，`pgvector 0.8.0+`）

默认情况下，近似向量索引扫描只会访问固定数量的候选集（`hnsw.ef_search` 或 `ivfflat.probes`）。如果 `WHERE` 过滤条件过滤掉了绝大部分候选行，最终返回的行数可能会少于 `LIMIT`。

自 `pgvector 0.8.0` 起，您可以开启**迭代式索引扫描（Iterative Index Scans）**，让索引在候选结果不足时自动继续向后搜索，直到凑齐 `LIMIT` 条记录（或达到 `max_scan_tuples` / `max_probes` 上限）：

```sql
-- 开启 HNSW 宽松顺序迭代扫描
SET hnsw.iterative_scan = relaxed_order;
-- 或使用 strict_order 严格保证跨迭代结果的精确距离顺序：
-- SET hnsw.iterative_scan = strict_order;

-- 开启 IVFFlat 宽松顺序迭代扫描
SET ivfflat.iterative_scan = relaxed_order;
```

使用 `relaxed_order` 时，返回结果的距离顺序可能存在轻微乱序，可通过外层 CTE 对最终的 `LIMIT` 条结果重排序：

```sql
WITH relaxed_results AS MATERIALIZED (
    SELECT id, embedding <-> '[3,1,2]' AS distance
    FROM items
    WHERE category_id = 123
    ORDER BY distance
    LIMIT 5
)
SELECT * FROM relaxed_results ORDER BY distance + 0;
```

#### 控制迭代扫描开销上限

```sql
-- HNSW 迭代扫描最多访问的元组数（默认：20000）
SET hnsw.max_scan_tuples = 20000;

-- HNSW 记录已访问节点状态允许使用的 work_mem 倍数（默认：1）
SET hnsw.scan_mem_multiplier = 2;

-- IVFFlat 迭代扫描最多探测的倒排列表数
SET ivfflat.max_probes = 100;
```

---

## 混合检索（Hybrid Search）

您可以使用 **倒数排序融合（Reciprocal Rank Fusion, RRF）** 将 `pgvector` 语义检索与关键词全文检索结合。

### 结合 PostgreSQL 内置 `tsvector`

```sql
SELECT id, content FROM (
    SELECT id, content, 1.0 / (60 + RANK() OVER (ORDER BY embedding <=> '[3,1,2]')) AS score
    FROM items
    ORDER BY embedding <=> '[3,1,2]' LIMIT 20
    UNION ALL
    SELECT id, content, 1.0 / (60 + RANK() OVER (ORDER BY ts_rank_cd(textsearch, query) DESC)) AS score
    FROM items, plainto_tsquery('english', 'hello search') query
    WHERE textsearch @@ query
    ORDER BY ts_rank_cd(textsearch, query) DESC LIMIT 20
) searches
GROUP BY id, content
ORDER BY SUM(score) DESC
LIMIT 5;
```

### 结合 `vchord_bm25` 或 `pg_bestmatch`

如果您需要具备文档长度归一化与全局语料库 IDF 权重的标准 Okapi BM25 排序：
- 将 `pgvector`（或 [`vchord`](/zh/docs/vchord/)）与 [`vchord_bm25`](/zh/docs/bm25/) 及 [`pg_tokenizer`](/zh/docs/tokenizer/) 搭配使用——详见[混合检索指南](/zh/docs/bm25/usage/hybrid-search/)。
- 或使用 [`pg_bestmatch`](/zh/docs/bestmatch/) 在数据库内直接生成带 BM25 权重的 `sparsevec` 稀疏向量，并通过 `pgvector` 的 HNSW（`sparsevec_ip_ops`）索引加速检索。
