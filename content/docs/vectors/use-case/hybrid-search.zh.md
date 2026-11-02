---
title: "混合搜索"
linkTitle: "混合搜索"
description: "本节将向您展示如何使用 pgvecto.rs 实现混合搜索。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/use-case/hybrid-search.md"
aliases:
  - "/use-case/hybrid-search/"
---

本节将向您展示如何使用 `pgvecto.rs` 实现混合搜索（Hybrid Search）。

## 向量搜索与全文检索 {#vector-search-and-full-text-search}

Postgres 基于[匹配操作符 `@@`](https://www.postgresql.org/docs/current/textsearch-intro.html#TEXTSEARCH-MATCHING) 提供了[全文检索（Full Text Search）](https://www.postgresql.org/docs/current/textsearch-intro.html)功能。当 `tsvector`（文档）与 `tsquery`（查询）匹配时，它会返回 `true`。**这两种数据类型的书写先后顺序**不影响结果：

```sql
SELECT 'a fat cat sat on a mat and ate a fat rat'::tsvector @@ 'cat & rat'::tsquery;
 ?column?
----------
 t

SELECT 'cat & rat'::tsquery @@ 'a fat cat sat on a mat and ate a fat rat'::tsvector;
 ?column?
----------
 t
```

> [!TIP]
>
> 如上例所示，`tsquery` 与 `tsvector` 一样，并不仅仅是原始文本。`tsquery` 包含必须已经规范化为词位（lexeme）的搜索词项，并且可以使用 [AND、OR、NOT 以及 FOLLOWED BY 操作符](https://www.postgresql.org/docs/current/datatype-textsearch.html#DATATYPE-TSQUERY)组合多个词项。在本例中，`tsquery` `'cat & rat'` 与 `tsvector` `'a fat cat sat on a mat and ate a fat rat'` 匹配，因为文档中同时包含 `'cat'` 和 `'rat'` 两个词项。
>


借助 `pgvecto.rs`，您可以在单条查询中同时结合使用全文检索和向量搜索。在本例中，我们创建一张名为 `items` 的表，包含两个字段：`content` 和 `embedding`。其中 `content` 列的类型为 `text`，`embedding` 列的类型为 `vector(3)`。我们向表中插入四条记录：

```sql
CREATE TABLE items (
  id bigserial PRIMARY KEY,
  content text NOT NULL,
  embedding vector(3) NOT NULL -- 3 维
);

INSERT INTO items (content, embedding) VALUES
  ('a fat cat sat on a mat and ate a fat rat', '[1, 2, 3]'),
  ('a fat dog sat on a mat and ate a fat rat', '[4, 5, 6]'),
  ('a thin cat sat on a mat and ate a thin rat', '[7, 8, 9]'),
  ('a thin dog sat on a mat and ate a thin rat', '[10, 11, 12]');
```

查询该表将得到如下内容：

```
postgres=# select * from items;
 id |                  content                   |  embedding   
----+--------------------------------------------+--------------
  2 | a fat cat sat on a mat and ate a fat rat   | [1, 2, 3]
  3 | a fat dog sat on a mat and ate a fat rat   | [4, 5, 6]
  4 | a thin cat sat on a mat and ate a thin rat | [7, 8, 9]
  5 | a thin dog sat on a mat and ate a thin rat | [10, 11, 12]
(4 rows)
```

首先，我们使用全文检索来查找 `content` 中同时包含单词 `cat` 和 `rat` 的记录。`to_tsvector` 函数会将文本转换为 `tsvector`，而操作符 `@@` 则检查 `tsvector` 是否与 `tsquery` 匹配。

```sql
SELECT content, embedding
FROM items
WHERE to_tsvector('english', content) @@ 'cat & rat'::tsquery;
```

> [!TIP]
>
> `to_tsvector` 会将文本文档解析为词元（token），将词元归约为词位（lexeme），并返回一个列出所有词位及其在文档中出现位置的 `tsvector`。
>
> ```sql
> SELECT to_tsvector('english', 'a fat  cat sat on a mat - it ate a fat rats');
>                   to_tsvector
> -----------------------------------------------------
>  'ate':9 'cat':3 'fat':2,11 'mat':7 'rat':12 'sat':4
> ```
>
> 在上面的例子中可以看到，由于文本搜索配置设为了 `english`，生成的 `tsvector` 不包含停用词 `a`、`on` 或 `it`，单词 `rats` 被归约为 `rat`，标点符号 `-` 也被忽略了。
>


我们将得到以下结果：

```
                  content                   | embedding 
--------------------------------------------+-----------
 a fat cat sat on a mat and ate a fat rat   | [1, 2, 3]
 a thin cat sat on a mat and ate a thin rat | [7, 8, 9]
(2 rows)
```

接下来，我们使用向量搜索，按照每条记录的嵌入向量与查询向量之间的距离对结果进行排序：

```sql
SELECT content, embedding
FROM items
WHERE to_tsvector('english', content) @@ 'cat & rat'::tsquery
ORDER BY embedding <-> '[7, 8, 9]'::vector;
```

此时，嵌入向量为 `[7, 8, 9]` 的记录将排在第一位，而嵌入向量为 `[1, 2, 3]` 的记录排在第二位：

```
                  content                   | embedding 
--------------------------------------------+-----------
 a thin cat sat on a mat and ate a thin rat | [7, 8, 9]
 a fat cat sat on a mat and ate a fat rat   | [1, 2, 3]
(2 rows)
```

### 高级搜索：融合全文检索与向量搜索的结果 {#advanced-search-merge-the-results-of-full-text-search-and-vector-search}

您可以对全文检索结果和向量搜索结果的排名进行归一化，然后将两者融合在一起：

```sql {hl_lines=["2", "9", "20"]}
-- 查询从名为 "semantic_search" 的公用表表达式（CTE）开始。
WITH semantic_search AS (
    SELECT id, content, embedding, 
    RANK () OVER (ORDER BY embedding <-> '[7, 8, 9]') AS rank
    FROM items
    ORDER BY embedding <-> '[7, 8, 9]'::vector
    ), 
-- 定义另一个名为 "full_text_search" 的 CTE。
    full_text_search AS (
    SELECT id, content, embedding, 
    RANK () OVER (ORDER BY 
        ts_rank(to_tsvector('english', content), 
            'cat & rat'::tsquery) DESC) AS rank
    FROM items
    WHERE to_tsvector('english', content) @@ 'cat & rat'::tsquery
    ORDER BY ts_rank(
        to_tsvector('english', content), 'cat & rat'::tsquery) DESC
    )
-- 主查询从两个 CTE 中选择列并融合排名。
    SELECT 
        COALESCE(semantic_search.id, full_text_search.id) AS id,
        COALESCE(semantic_search.content, full_text_search.content) AS content,
        COALESCE(semantic_search.embedding, full_text_search.embedding) AS embedding,
        COALESCE(1.0 / (1 + semantic_search.rank), 0.0) + 
        COALESCE(1.0 / (1 + full_text_search.rank), 0.0) AS rank
    FROM semantic_search FULL OUTER JOIN full_text_search USING (id)
    ORDER BY rank DESC;
```

> [!TIP]
>
> 上述 SQL 查询对 `items` 表同时执行了语义搜索和全文检索，并根据相关性得分检索结果。以下是该查询的详细解析：
>
> - 查询以一个名为 `semantic_search` 的[公用表表达式（CTE）](https://www.postgresql.org/docs/current/queries-with.html)开始。它选择 `id`、`content`、`embedding` 列，并使用测量 `embedding` 列与向量 `'[7, 8, 9]'` 之间距离的 `<->` 操作符计算排名（rank），结果按该距离排序。
> - 定义另一个名为 `full_text_search` 的 CTE。它选择与前一个 CTE 相同的列，但结合全文检索查询使用 `ts_rank` 函数计算排名。`to_tsvector` 函数将 `content` 列转换为 `tsvector`，而 `tsquery` `'cat & rat'` 则匹配 `content` 列中同时包含 `"cat"` 和 `"rat"` 的行，结果按全文检索相关性排名排序。
> - 主查询使用 [`COALESCE`](https://www.postgresql.org/docs/current/functions-conditional.html#FUNCTIONS-COALESCE-NVL-IFNULL) 函数从两个 CTE 中选取列，以处理其中一个 CTE 可能为空值的情况。同时，它将两个 CTE 排名的倒数相加，计算出综合得分（rank）。
> - 主查询在两个 CTE 之间基于 `id` 列执行全外连接（`FULL OUTER JOIN`）。
> - 最终结果按照综合得分降序排列。
>


在这条查询中，我们先分别计算全文检索结果和向量搜索结果的排名，然后将两部分结果融合，最终得到如下输出：

```
 id |                  content                   |  embedding   |          rank          
----+--------------------------------------------+--------------+------------------------
  4 | a thin cat sat on a mat and ate a thin rat | [7, 8, 9]    | 1.00000000000000000000
  2 | a fat cat sat on a mat and ate a fat rat   | [1, 2, 3]    | 0.70000000000000000000
  3 | a fat dog sat on a mat and ate a fat rat   | [4, 5, 6]    | 0.33333333333333333333
  5 | a thin dog sat on a mat and ate a thin rat | [10, 11, 12] | 0.33333333333333333333
(4 rows)
```
