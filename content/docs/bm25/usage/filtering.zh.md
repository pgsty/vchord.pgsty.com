---
math: true
title: "过滤检索与预过滤"
description: "通过后过滤、预过滤和部分索引，将 SQL WHERE 子句与 BM25 Top-K 相关性排序相结合。"
weight: 30
icon: fa-solid fa-filter
---

以下示例使用 **1.0.0 原生 `tsvector` API**，将 BM25 排序与类别、租户或时间范围等结构化条件结合。文档和查询应使用相同的文本检索配置。

## 1. 后过滤与预过滤 {#1-post-filtering-vs-pre-filtering}

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY vector <&> to_bm25query(
    to_tsvector('english', 'PostgreSQL BM25'), 'documents_bm25_idx')
LIMIT 10;
```

### 后过滤（`bm25.prefilter = false`） {#post-filtering-enable_prefilter--false}

BM25 索引提供按得分排序的候选行，PostgreSQL 再应用 `WHERE` 条件。如果首批候选中不足 10 行符合条件，扫描会扩大批次并继续，直到满足 SQL 的行数限制或数据耗尽。

`bm25.limit` 与索引的 `limit` 选项控制**首批扫描大小**，不限制结果总数。两者默认值均为 100，零值也选择 100。查询结果不再局限于首批 100 个候选中的匹配行。

### 预过滤（`bm25.prefilter = true`） {#pre-filtering-enable_prefilter--true}

预过滤在候选进入 Top-K 堆之前检查可见性和支持的查询谓词。被排除的候选不会抬高剪枝阈值。这可以减少强过滤条件下的无效排序工作，代价是在排序过程中增加回表检查。易变（volatile）谓词仍由执行器处理。

1.1.0 中，两种模式都支持按需续扫。应根据实际负载测量后选择；预过滤并不能消除所有无关倒排项的扫描。

在 1.1.0 中，`WHERE vector @@ ...` 仍由执行器过滤，并不是 BM25 原生扫描键。因此，强选择性或空的全文匹配可能仍需遍历零分尾部；如果希望该谓词驱动执行计划，可以为同一列增加 GIN 索引。

### 启用预过滤 {#enabling-pre-filtering}

```sql
-- 在当前会话覆盖索引默认值：
SET bm25.prefilter = true;

-- 或设置索引默认值：
ALTER INDEX documents_bm25_idx SET (prefilter = true);
```

显式 GUC 设置（包括 `false`）会覆盖索引选项。`RESET bm25.prefilter` 恢复配置默认值；只有 GUC 来源为内置默认值时，才使用索引选项。参阅 [GUC 优先级](/zh/docs/bm25/reference/gucs/#session-guc-parameters-main)。

### 历史 0.1–0.3 版本的行为 {#historical-013-behavior}

旧版以 `bm25_catalog.bm25_limit` 限制候选总数。后过滤时，如果 100 个候选中只有 3 行满足条件，即使表中还有其他匹配文档，也可能只返回 3 行。0.2.2 起可通过 `bm25_catalog.enable_prefilter` 启用预过滤。这些参数和候选截断行为均不适用于 1.0.0。

## 2. 面向固定子集的部分 BM25 索引 {#2-partial-bm25-indexes-for-high-selectivity-partition-keys}

对于已发布文档等固定子集，可以使用部分索引：

```sql
CREATE INDEX documents_published_bm25
ON documents
USING bm25 (vector bm25_ops)
WHERE status = 'published';
```

在 `to_bm25query` 中引用同一个索引，并使用能够推导出索引谓词的 `WHERE` 条件：

```sql
SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY vector <&> to_bm25query(
    to_tsvector('english', 'PostgreSQL BM25'), 'documents_published_bm25')
LIMIT 10;
```

部分索引拥有独立的语料统计，因此评分可能与全表索引不同。统计包含物理记录，以及合并前的 tombstone；参阅[索引维护](/zh/docs/bm25/usage/indexing/#growing-segments-and-maintenance-in-100)。

## 选择合适的过滤策略 {#choosing-the-right-filtering-strategy}

| 负载 | 建议起点 | 权衡 |
| :--- | :--- | :--- |
| 大部分行满足条件 | 后过滤 | 避免在排序循环内检查谓词；需要时继续扫描。 |
| 少量行满足条件 | 预过滤 | 避免不满足条件的行进入 Top-K 堆，但增加排序期间的回表检查。 |
| 固定租户或状态子集 | 部分索引或表分区 | 语料更小、统计独立；查询必须指向正确的索引。 |
{.wide .expand}

SQL 过滤条件不能绕过[权限与 RLS 限制](/zh/docs/bm25/reference/migration/#schema-access)。当 RLS 适用于当前角色时，1.1.0 会拒绝 BM25 评分和原生索引扫描。
