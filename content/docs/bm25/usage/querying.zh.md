---
math: true
title: "查询与相关性评分"
description: "执行 Top-K BM25 查询、理解负值 BM25 得分并调优检索上限参数。"
weight: 20
icon: fa-solid fa-ranking-star
---

## 基础 Top-K 查询语法 {#basic-top-k-query-syntax}

要运行经索引加速的 Top-K BM25 检索，请在 `ORDER BY` 子句中将 `<&>` 操作符与 `to_bm25query` 结合使用：

```sql
-- v0.1 – v0.3 (bm25vector + pg_tokenizer)
SELECT
    id,
    passage,
    embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL vector search', 'my_tokenizer')) AS raw_score,
    -(embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL vector search', 'my_tokenizer'))) AS bm25_score
FROM documents
ORDER BY raw_score ASC
LIMIT 10;
```

```sql
-- main 分支（原生 tsvector）
SELECT
    id,
    passage,
    -(vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL vector search'), 'documents_bm25_idx')) AS bm25_score
FROM documents
ORDER BY vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL vector search'), 'documents_bm25_idx') ASC
LIMIT 10;
```

## 为什么 `to_bm25query` 需要传入索引名称 {#why-to_bm25query-requires-the-index-name}

与向量距离操作符不同（两个向量之间的距离仅取决于这两个向量本身），**一篇文档的 BM25 得分依赖于存储在 BM25 索引中的全语料库统计信息**：

- 语料库中的文档总数（\(N\)）
- 全语料库的平均文档长度（\(\text{avgdl}\)）
- 每个查询词元在语料库中的文档频率（\(n(q_i)\)）

将索引（`'documents_embedding_bm25'::regclass`）传入 `to_bm25query(...)`，使得独立评分函数（`search_bm25query` / `_bm25_evaluate`）即使在 PostgreSQL 于 `SELECT` 投影列表中求值 `<&>` 或执行暴力顺序扫描（Sequential Scan）时，也能从索引中读取语料库统计信息。

## 理解负值 BM25 得分 {#understanding-negative-bm25-scores}

根据设计，`<&>` 返回的是**负值** BM25 得分：

$$\text{score}_{\text{operator}}(D, Q) = -\text{BM25}(D, Q) \le 0$$

- PostgreSQL 的索引访问方法 API（`amcanorderbyop`）仅支持对 `ORDER BY <operator> ASC` 执行按索引排序的扫描。
- 由于 BM25 得分越高代表相关性越强，返回 $-\text{BM25}(D, Q)$ 可以在默认的升序（`ASC`）排列下，将最相关的文档排在最前面。
- **切勿**使用 `ORDER BY embedding <&> to_bm25query(...) DESC`——PostgreSQL 无法对 `DESC` 排序使用正向 `bm25` 索引扫描，会导致回退到全表扫描或抛出扫描方向错误。

## 调优 `bm25_limit` 与 SQL `LIMIT` {#tuning-bm25_limit-vs-sql-limit}

由于 Block-WeakAnd 在索引扫描期间会维护一个有界 Top-K 最小堆，以激进地剪枝缺乏竞争力的倒排块，因此索引扫描器在扫描开始时就需要知道 \(K\)（即最多需要收集多少个候选文档）。

### 在 `v0.1.0` – `v0.3.0` 中：`bm25_catalog.bm25_limit` {#in-v010--v030-bm25_catalogbm25_limit}

GUC 参数 `bm25_catalog.bm25_limit`（默认值为 `100`，取值范围 `-1` 至 `65535`）控制单次 `bm25` 索引扫描最多返回的 Top-K 文档数量：

```sql
-- 默认值为 100。如果你的 SQL 查询请求 LIMIT 500，请先调大该参数：
SET bm25_catalog.bm25_limit = 500;

SELECT id, passage
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('database', 'my_tokenizer'))
LIMIT 500;
```

`bm25_catalog.bm25_limit` 的特殊取值说明：

| 取值 | 行为说明 |
| :--- | :--- |
| `1` – `65535` | 使用 Block-WeakAnd 计算并返回最多 `bm25_limit` 条高分文档（默认 `100`）。 |
| `0` | 立即返回 `0` 行。 |
| `-1` | 禁用 Block-WeakAnd Top-K 剪枝，对索引中所有匹配的倒排项执行全量暴力扫描。 |
{.wide .expand}

### 在 `main` 分支中：`bm25.limit` 与索引 `limit` 存储参数 {#in-main-bm25limit-and-index-limit-reloption}

在 `main` 分支中，实际生效的检索上限按以下优先级顺序决定：

1. 显式设置的会话 GUC 参数 `bm25.limit`，包括零值。
2. 否则使用索引存储参数 `WITH (limit = ...)`。

两层默认值均为零，因此检索前必须设置正值。显式零值会报错，不触发回退。执行 `RESET "bm25.limit"` 可恢复索引默认值。

```sql
SET "bm25.limit" = 100;
```

`postgresql.conf`、`ALTER DATABASE`、`ALTER ROLE` 或客户端启动选项中的设置也会覆盖索引参数。`RESET` 会恢复这些配置默认值；只有 GUC 来源恢复为内置默认值时，才会回退到索引参数。

> [!WARNING]
> 请始终确保 `bm25_catalog.bm25_limit`（或 `bm25.limit`）**大于或等于** SQL 查询中的 `LIMIT` 值。如果 SQL 查询指定了 `LIMIT 200`，而 `bm25_limit` 仍为 `100`，则索引扫描在产出 100 行后就会停止。

## 使用 `EXPLAIN` 验证查询计划 {#verifying-the-query-plan-with-explain}

使用 `EXPLAIN (ANALYZE, BUFFERS)` 确认 PostgreSQL 正在使用 `Index Scan using ... on documents`：

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL', 'my_tokenizer'))
LIMIT 10;
```

如需强制执行顺序扫描 + 精确暴力求值（常用于验证召回率或调试），可以临时禁用索引扫描：

```sql
-- v0.1 – v0.3
SET bm25_catalog.enable_index = false;

-- main 分支
SET bm25.enable_scan = false;
```
