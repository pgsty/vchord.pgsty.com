---
title: "过滤"
linkTitle: "过滤"
description: "把 BM25 排序和 WHERE 条件结合起来：过滤条件如何生效、何时使用预过滤、为固定子集建部分索引、权限与行级安全。"
weight: 30
icon: fa-solid fa-filter
---

大多数检索都是在某个条件内排序：某个租户、某个分类、某段时间。本页说明 `WHERE` 子句与分批索引扫描如何配合、什么时候改用预过滤，以及部分索引和行级安全如何改变分数背后的统计信息。

## 用 WHERE 过滤 {#where}

照常写条件即可：

```sql
SELECT id, passage
FROM documents
WHERE category = 'database'
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25')
LIMIT 10;
```

过滤条件决定返回哪些行，但不影响打分：分数仍然来自整个索引的统计信息。要在子集内打分，就用[部分索引](#partial-indexes)只为该子集建索引。

## 后过滤 {#post-filter}

默认情况下，索引先排出一批行，PostgreSQL 去掉不满足 `WHERE` 的行；剩下的不足 `LIMIT` 行时，扫描再排出下一批，大小翻倍（见[排序查询如何执行](/zh/docs/bm25/usage/querying/#how-a-query-runs)）。结果总是完整的，但条件越苛刻，开销越大：如果只有 1% 的行能通过，`LIMIT 10` 大约需要排出 1,000 行，从默认的 100 行开始要排四批，每一批都要重新遍历倒排列表。

## 预过滤 {#prefilter}

开启预过滤（[`bm25.prefilter`](/zh/docs/bm25/reference/gucs/#field-bm25-prefilter)）后，索引在候选行进入批次之前，就先检查它的可见性和 `WHERE` 条件。不满足条件的行不会占用名额，通常第一批就够了。代价是：每个有可能进入批次的候选行，都要读一次表中的行。

```sql
SET bm25.prefilter = on;
```

| 条件保留的行 | 先试 |
| --- | --- |
| 大部分行 | 后过滤（默认） |
| 一小部分行 | 预过滤 |
| 经常检索的固定子集 | 为该子集建[部分索引](#partial-indexes) |

决定方法：分别关闭和开启预过滤，用 `EXPLAIN (ANALYZE, BUFFERS)` 执行查询，保留较快的设置，并把它存到索引上，让所有会话都生效：

```sql
ALTER INDEX documents_bm25 SET (prefilter = on);
```

只有在其他地方都没有设置 `bm25.prefilter` 时，索引上的设置才生效，见[优先级](/zh/docs/bm25/reference/gucs/#precedence)。

以下情况不会使用预过滤，查询改为排序后再过滤，结果相同：

- 表启用了行级安全；
- `WHERE` 子句调用了易变（volatile）函数；
- 查询经由 security barrier 视图读取、用 `FOR UPDATE` 或 `FOR SHARE` 锁行，或包含修改数据的 `WITH`；
- `WHERE` 子句中的子查询，除了普通表扫描、B-tree 索引扫描和 `count(*)` 之外还做了别的事。

如果条件落在有 B-tree 索引的列上并且选择性很高，PostgreSQL 也可能完全不用 bm25 索引：先取出少量匹配行，打分后排序。这往往就是最便宜的计划；`EXPLAIN` 会显示它选了哪一种。

## 部分索引 {#partial-indexes}

部分索引只覆盖一个子集，统计信息也只来自这个子集：

```sql
CREATE INDEX documents_published_bm25 ON documents
USING bm25 (terms bm25_ops)
WHERE status = 'published';

SELECT id, passage
FROM documents
WHERE status = 'published'
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_published_bm25')
LIMIT 10;
```

查询的 `WHERE` 子句必须能推出索引谓词，`to_bm25query` 也必须写部分索引的名字。由于文档数和词频都来自子集，分数会与全表索引不同。子集很多时（例如每个租户一个），可以按租户分区，让每个分区有自己的索引；分区表的查询方式见[限制](/zh/docs/bm25/usage/indexing/#limits)。

## 权限与行级安全 {#access-control}

BM25 分数会透露整个索引的统计信息：有多少文档、平均多长、每个词出现在多少文档里，其中也包括调用者无权读取的行。因此打分有一层额外的检查，比 `SELECT` 本身的权限检查更严格。

- **权限。** 打分的角色需要表上的 `SELECT` 权限，或者索引列、索引表达式和部分索引谓词所涉及列上的列级 `SELECT` 权限，以及其中所用函数的 `EXECUTE` 权限。只授予视图权限是不够的：通过视图查询的角色同样需要表上的这些权限，否则打分会报错 `permission denied for table documents`。
- **行级安全。** 当前角色受行级安全策略约束时，打分会报错 `bm25 cannot expose global corpus statistics under row-level security`。表的属主（表未设置 `FORCE ROW LEVEL SECURITY` 时）和拥有 `BYPASSRLS` 的角色不受此限。设置 `row_security = off` 也没有用。
- **显式开启。** 索引属主可以通过 [`shared_corpus_stats`](/zh/docs/bm25/reference/gucs/#field-shared_corpus_stats) 允许在行级安全下打分：

  ```sql
  ALTER INDEX documents_bm25 SET (shared_corpus_stats = on);
  ```

  返回哪些行仍由策略决定，但分数反映的是每个词在所有行中的常见程度，一个租户因此能推断出其他租户用词的一些信息。启用了行级安全的表不会使用预过滤。

如果要让每个租户按自己的统计信息打分、彼此不共享任何信息，就为每个租户建部分索引或分区。
