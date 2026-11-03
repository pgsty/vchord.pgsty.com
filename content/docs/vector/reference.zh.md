---
title: "参考手册、调优与 FAQ"
linkTitle: "参考手册、调优与 FAQ"
description: "pgvector 的完整 SQL 函数参考、GUC 配置参数、性能调优、监控方法与常见问题解答。"
weight: 50
icon: fa-solid fa-book-open
upstream_link: https://github.com/pgvector/pgvector#reference
math: true
---

## SQL 函数与操作符速查表

### 向量函数

| 函数 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `l2_distance(a, b)` | `float8` | 计算 `a` 与 `b` 之间的欧氏（L2）距离（支持 `vector`, `halfvec`, `sparsevec`） |
| `inner_product(a, b)` | `float8` | 计算内积 \(\sum a_i b_i\)（支持 `vector`, `halfvec`, `sparsevec`） |
| `cosine_distance(a, b)` | `float8` | 计算余弦距离 \(1 - \frac{a \cdot b}{\lVert a \rVert \lVert b \rVert}\)（支持 `vector`, `halfvec`, `sparsevec`） |
| `l1_distance(a, b)` | `float8` | 计算曼哈顿（L1）距离 \(\sum \lvert a_i - b_i \rvert\)（支持 `vector`, `halfvec`, `sparsevec`） |
| `hamming_distance(a, b)` | `float8` | 计算两个 `bit` 位向量之间的汉明距离 |
| `jaccard_distance(a, b)` | `float8` | 计算两个 `bit` 位向量之间的杰卡德距离 |
| `vector_dims(a)` | `integer` | 返回向量的维度数（支持 `vector`, `halfvec`, `sparsevec`） |
| `vector_norm(a)` | `float8` | 返回向量的欧氏范数 \(\lVert a \rVert_2\)（支持 `vector`, `halfvec`, `sparsevec`） |
| `l2_normalize(a)` | 与输入相同 | 将向量归一化为单位 L2 长度（支持 `vector`, `halfvec`, `sparsevec`） |
| `binary_quantize(a)` | `bit` | 将 `vector` 或 `halfvec` 的每个元素二值化为 `1`（\(> 0\)）或 `0`（\(\le 0\)） |
| `subvector(a, start, count)` | 与输入相同 | 从 1 起始下标 `start` 处截取长度为 `count` 的子向量（支持 `vector`, `halfvec`） |
{.wide .expand}

### 逐元素算术操作符

- `a + b`：逐元素加法（`vector`, `halfvec`）
- `a - b`：逐元素减法（`vector`, `halfvec`）
- `a * b`：逐元素乘法（`vector`, `halfvec`）
- `a || b`：向量拼接（`vector`, `halfvec`）

---

## GUC 配置参数

| 参数名称 | 类型 / 允许取值 | 默认值 | 说明 |
| :--- | :--- | :---: | :--- |
| `hnsw.ef_search` | `integer`（`1`–`1000`） | `40` | HNSW 查询时的动态候选列表大小 |
| `hnsw.iterative_scan` | `off`, `relaxed_order`, `strict_order` | `off` | 当 `WHERE` 条件过滤导致结果少于 `LIMIT` 时，自动继续扫描 HNSW 索引 |
| `hnsw.max_scan_tuples` | `integer` | `20000` | HNSW 迭代扫描期间最多访问的元组数量 |
| `hnsw.scan_mem_multiplier` | `real` | `1` | HNSW 迭代扫描维护访问状态可使用的 `work_mem` 倍数 |
| `ivfflat.probes` | `integer`（`1`–`lists`） | `1` | IVFFlat 查询时探测的倒排列表数量 |
| `ivfflat.iterative_scan` | `off`, `relaxed_order` | `off` | 当 `WHERE` 条件过滤导致结果少于 `LIMIT` 时，自动探测更多 IVFFlat 分桶 |
| `ivfflat.max_probes` | `integer` | `32768` | IVFFlat 迭代扫描期间最多探测的倒排列表数量 |
{.wide .expand}

---

## 性能调优与监控

### 1. 查看索引体积

```sql
SELECT pg_size_pretty(pg_relation_size('items_embedding_idx'));
```

### 2. 检查查询执行计划

使用 `EXPLAIN ANALYZE` 确认查询是否命中向量索引并查看缓冲区命中与耗时：

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

### 3. 使用 `pg_stat_statements` 监控慢查询

```sql
SELECT
    calls,
    round((total_plan_time + total_exec_time) / calls) AS avg_time_ms,
    round((total_plan_time + total_exec_time) / 60000) AS total_time_min,
    query
FROM pg_stat_statements
ORDER BY total_plan_time + total_exec_time DESC
LIMIT 20;
```

### 4. 评估近似检索召回率（Recall）

在事务内临时关闭索引扫描，获取精确最近邻基准（Ground Truth）并与近似结果对比：

```sql
BEGIN;
SET LOCAL enable_indexscan = off;
-- 在此执行精确查询以获取基准 ID 列表
COMMIT;
```

---

## 常见问题解答（FAQ）

### 为什么我的查询没有走向量索引？

1. **缺少 `ORDER BY ... LIMIT`**：向量索引扫描要求查询同时包含 `ORDER BY <距离操作符>` 与 `LIMIT` 子句。
2. **操作符与索引操作符类不匹配**：查询操作符必须与创建索引时的操作符类一致（`<->` 对应 `vector_l2_ops`，`<#>` 对应 `vector_ip_ops`，`<=>` 对应 `vector_cosine_ops`）。
3. **小表成本估算**：当表行数较少时，PostgreSQL 优化器认为全表顺序扫描比走索引更快。在测试环境中可通过 `SET LOCAL enable_seqscan = off;` 强制走索引验证。

### 如何对超过 2,000 维的向量建立索引？

受限于 PostgreSQL 8 KB 页面元组大小，内置的 HNSW 与 IVFFlat 索引对 `vector` 类型的维度上限为 2,000 维。您有三种解决方案：
1. **安装 [`vchord`](/zh/docs/vchord/)**：[`vchord`](/zh/docs/vchord/) 的 `vchordrq` 索引直接在 `vector` 与 `halfvec` 列上支持高达 **60,000 维**的超长向量。
2. **使用 `halfvec` 半精度表达式索引**：通过 `(embedding::halfvec(3072)) halfvec_l2_ops` 最高支持 **4,000 维**。
3. **使用二值量化表达式索引**：通过 `(binary_quantize(embedding)::bit(N)) bit_hamming_ops` 最高支持 **64,000 维**。

### 可以在同一列中存储不同维度的向量吗？

可以，定义列时不指定维度即可（`embedding vector`）。如果需要建索引，可以针对特定维度的行创建部分表达式索引：

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector);
CREATE INDEX ON items USING hnsw ((embedding::vector(3)) vector_l2_ops) WHERE (vector_dims(embedding) = 3);
```

### 向量中可以包含 `NULL`、`NaN` 或 `Infinity` 吗？

向量内部的元素不能为 `NULL`、`NaN` 或 `Infinity`。整列的值可以为 `NULL`；请注意 IVFFlat 不会对 `NULL` 值建索引。
