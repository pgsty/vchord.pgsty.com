---
math: true
title: "过滤检索与预过滤"
description: "通过后过滤、预过滤和部分索引，将 SQL WHERE 子句与 BM25 Top-K 相关性排序相结合。"
weight: 30
---

在实际业务场景中，全文 BM25 排序通常需要与结构化关系过滤条件（例如 `category_id = 5`、`tenant_id = 'acme'` 或时间范围）结合使用。`vchord_bm25` 支持三种带过滤条件的 BM25 检索策略。

## 1. 后过滤（Post-Filtering）与预过滤（Pre-Filtering） {#1-post-filtering-vs-pre-filtering}

当你执行一条同时包含 `WHERE` 子句和 `ORDER BY embedding <&> to_bm25query(...) LIMIT K` 的查询时：

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25', 'my_tokenizer'))
LIMIT 10;
```

`vchord_bm25` 可以通过以下两种方式评估 `WHERE` 谓词：

### 后过滤（`enable_prefilter = false`） {#post-filtering-enable_prefilter--false}

1. `bm25` 索引在整个语料库上运行 Block-WeakAnd，返回全局前 `bm25_limit` 名候选文档（例如全局 Top 100）。
2. PostgreSQL 回表取出这 100 条堆表元组，并应用 `WHERE category = 'database'` 过滤条件。
3. **注意事项**：如果全局 Top-100 文档中只有 3 篇满足 `category = 'database'`，那么即使表里还有数百篇 BM25 得分略低的 `'database'` 类别文档，查询也只会返回 3 行！

### 预过滤（`enable_prefilter = true`） {#pre-filtering-enable_prefilter--true}

启用预过滤后，`vchord_bm25` 会在将候选文档推入 Block-WeakAnd Top-K 堆**之前**，先行检查堆表可见性并评估过滤条件是否满足：

1. 不满足过滤条件的文档绝不会进入 Top-K 堆，也不会抬高 Block-WeakAnd 的剪枝阈值 \(\theta\)。
2. 索引扫描会持续推进，直到找齐 \(K\) 篇**既满足 `WHERE` 过滤条件**、又在所有匹配行中**拥有最高 BM25 得分**的文档。

### 启用预过滤 {#enabling-pre-filtering}

在 **`v0.2.2` – `v0.3.0`** 中：

```sql
-- 在 v0.3.0 中默认启用；可在会话级动态切换：
SET bm25_catalog.enable_prefilter = true;
```

在 **`main` 分支**中：

```sql
-- 在当前会话中启用：
SET bm25.prefilter = true;

-- 或在索引级别默认启用：
ALTER INDEX documents_bm25_idx SET (prefilter = true);
```

## 2. 面向高选择性分区键的部分 BM25 索引（Partial Index） {#2-partial-bm25-indexes-for-high-selectivity-partition-keys}

如果你经常按固定的一组分区键（例如 `status = 'published'` 或特定 `tenant_id`）进行过滤，可以创建**部分 `bm25` 索引（Partial Index）**：

```sql
CREATE INDEX documents_published_bm25
ON documents
USING bm25 (embedding bm25_ops)
WHERE status = 'published';
```

查询部分索引时，请在 `to_bm25query` 中指定该部分索引的名称，并在 SQL 中附上匹配的 `WHERE` 条件：

```sql
SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY embedding <&> to_bm25query('documents_published_bm25', tokenize('PostgreSQL BM25', 'my_tokenizer'))
LIMIT 10;
```

## 选择合适的过滤策略 {#choosing-the-right-filtering-strategy}

| 过滤条件选择率 | 推荐策略 | 原因说明 |
| :--- | :--- | :--- |
| **高匹配率（50%–100% 的行匹配）** | 后过滤（`enable_prefilter = false`）并适当调大 `bm25_limit` | 避免在 WAND 内层循环中频繁回表读取堆页；全局 Top-100 中即可轻松包含 10 条以上匹配行。 |
| **中等匹配率（5%–50% 的行匹配）** | 预过滤（`enable_prefilter = true` / `bm25.prefilter = true`） | 确保在过滤后的子集上实现精确的 Top-K 召回，同时不扫描无关倒排项。 |
| **固定租户 / 状态子集** | 部分 `bm25` 索引（`CREATE INDEX ... WHERE ...`）或表分区 | 索引体积更小，拥有针对该子集独立的 IDF 统计信息，且对其他分区零无效检查开销。 |
