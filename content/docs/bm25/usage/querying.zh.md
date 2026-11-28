---
title: "查询"
linkTitle: "查询"
description: "编写 BM25 排序查询，理解分数含义，了解索引扫描如何分批执行，确定 bm25.limit，并让查询计划用上索引。"
weight: 20
icon: fa-solid fa-ranking-star
aliases:
  - "/docs/bm25/usage/algorithms/"
---

一条排序查询要指明用哪个索引的统计信息打分，按 `<&>` 运算符排序，并限制返回行数。本页解释这样的查询如何执行，帮助你预估开销、确定批次大小，并让 PostgreSQL 按预期生成执行计划。

## 编写排序查询 {#query}

```sql
SELECT id, passage
FROM documents
ORDER BY terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25')
LIMIT 10;
```

满足以下条件时，PostgreSQL 会用 bm25 索引执行这条查询：

- `ORDER BY` 是被索引的列或表达式 `<&>` 一个 `to_bm25query(...)`，升序，并且是唯一的排序键。
- `to_bm25query` 的第二个参数是常量，指向同一个索引。参数、`to_regclass()` 查找或 `bm25query` 类型的参数，在规划时都无法对应到索引；这时 PostgreSQL 会给每一行打分再排序。
- 查询带 `LIMIT`，只排前几名才划算。

查询里要写索引名，是因为 BM25 分数依赖整个语料的统计信息：文档数、平均长度，以及每个查询词出现在多少篇文档里。这些统计信息存在索引里。同样的 `<&>` 表达式出现在 `SELECT` 列表或 `WHERE` 子句中时，对任意一行都会基于同一份统计信息算出相同的分数。

## 分数 {#scores}

PostgreSQL 的索引扫描按升序返回行，所以 `<&>` 返回的是 BM25 分数的相反数，类型为 `double precision`。最相关的行分数最小（负得最多）。要显示正分，在选择列表里取反：`-(terms <&> to_bm25query(...)) AS score`。

只要包含任一查询词，这一行就算匹配；包含的查询词越多、越罕见，分数越高。一个查询词都不包含的行分数为 `0`，排在所有匹配行之后；`tsvector` 为 `NULL` 的行排在最后。`LIMIT` 大于匹配行数时，剩下的位置会由这些行填满。只想返回匹配的行，就在外层查询里过滤，内层仍然走索引扫描：

```sql
SELECT id, -score AS relevance
FROM (
    SELECT id, terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25') AS score
    FROM documents
    ORDER BY score
    LIMIT 10
) AS ranked
WHERE score < 0;
```

如果要求包含全部查询词，加上 `WHERE terms @@ plainto_tsquery('english', 'full text search')`。它只是一个普通的过滤条件，处理方式见[过滤](/zh/docs/bm25/usage/filtering/)。

查询中重复的词只计一次，`setweight` 设置的权重会被忽略。公式见[分数定义](/zh/docs/bm25/reference/sql/#score)。

## 排序查询如何执行 {#how-a-query-runs}

1. **准备。** 扫描读取索引的统计信息，以及增长段中的每一行，也就是 `VACUUM` 尚未合并的行。这样分数反映的是全部已索引的行，无论合并与否。
1. **排出一批。** Block-WeakAnd 遍历查询词的倒排列表。每个列表按 128 篇文档一块存储，每块记录了块内文档可能贡献的最高分。如果一块不可能超过当前第 k 名的分数，就不解码其中的文档，直接跳过。批次大小 k 由 [`bm25.limit`](/zh/docs/bm25/reference/gucs/#field-bm25-limit) 决定，默认为 100。
1. **按需继续。** PostgreSQL 消费这一批结果。如果还需要更多行（`LIMIT` 加 `OFFSET` 超过批次大小，或者 `WHERE` 子句、行可见性去掉了一部分），扫描就从上次返回的最后一行之后，排出下一批，大小翻倍。每一批都要重新遍历倒排列表。
{.steps}

由此可以推出一条查询的开销：

- k 越小，分数门槛越早抬高，跳过的块越多。`LIMIT` 小的查询最便宜。
- 罕见词的倒排列表短。全是高频词的查询要读得更多。
- 增长段很大时，每条查询都会变慢，因为第 1 步要把它整个读一遍。如何让它保持精简，见[建索引](/zh/docs/bm25/usage/indexing/#maintenance)。
- 结果是完整的。无论 `bm25.limit` 设成多少，扫描都会一直进行，直到查询拿够行数，或所有行都已返回。

## 确定批次大小 {#batch-size}

`bm25.limit` 在第一批的开销和需要第二批的可能性之间权衡：

- 默认值 100 适合 `LIMIT` 不超过 100、过滤掉的行也不多的查询，一批就能完成。
- 分页较大或 `OFFSET` 较深时，至少设为 `LIMIT + OFFSET`。
- 如果 `WHERE` 子句只保留一小部分行，要么把它调到约为 `LIMIT` 除以该比例，要么开启[预过滤](/zh/docs/bm25/usage/filtering/#prefilter)。
- 批次越大，跳过的块越少，所以不要设得远超查询实际用到的行数。

调优步骤：

1. 用 `EXPLAIN (ANALYZE, BUFFERS)` 执行一条典型查询，记下执行时间和共享缓冲区访问量。
1. 在会话中尝试其他取值。参数名必须加引号，因为 `LIMIT` 是保留字：

   ```sql
   SET "bm25.limit" = 200;
   ```

1. 把最佳值保存到索引上，让所有会话都生效：

   ```sql
   ALTER INDEX documents_bm25 SET (limit = 200);
   ```

   只有在其他地方都没有设置 `bm25.limit` 时，索引上的值才生效，见[优先级](/zh/docs/bm25/reference/gucs/#precedence)。
{.steps}

## 预备语句 {#prepared-statements}

索引名保持为字面量，只把检索文本作为参数传入。这样即使是通用计划（generic plan），规划器也能把查询对应到索引：

```sql
PREPARE search_docs(text) AS
SELECT id FROM documents
ORDER BY terms <&> to_bm25query(to_tsvector('english', $1), 'documents_bm25')
LIMIT 10;

EXECUTE search_docs('full text search');
```

## 检查执行计划 {#explain}

`EXPLAIN` 中会出现 `Index Scan using documents_bm25 on documents`，并带有一行针对 `<&>` 表达式的 `Order By`。如果看到 `Seq Scan` 或 `Bitmap Heap Scan` 上面套着 `Sort`，说明 PostgreSQL 在逐行打分。先对照[编写排序查询](#query)中的条件检查。如果条件都满足，那就是 PostgreSQL 估算另一个计划更便宜，例如先用 B-tree 索引按选择性高的条件取行，再排序；用 `EXPLAIN ANALYZE` 比较两者。

[`SET bm25.enable_scan = off`](/zh/docs/bm25/reference/gucs/#field-bm25-enable_scan) 让 PostgreSQL 给每一行打分再排序。分数完全一样，可以作为测试时的参照。

## 结果顺序 {#result-order}

行严格按 BM25 分数返回；与向量检索不同，这里没有任何近似。分数相同的行按索引内部顺序返回，这个顺序在合并或重建之后可能变化。在 `ORDER BY` 中加上第二个排序键（例如 `id`）会让 PostgreSQL 无法使用索引。需要稳定顺序时，多取一些，再在外层查询中重新排序：

```sql
SELECT id, score
FROM (
    SELECT id, terms <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_bm25') AS score
    FROM documents
    ORDER BY score
    LIMIT 20
) AS ranked
ORDER BY score, id
LIMIT 10;
```
