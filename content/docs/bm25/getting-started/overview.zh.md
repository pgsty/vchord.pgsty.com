---
title: "概览"
linkTitle: "概览"
description: "vchord_bm25 是什么、为什么排序全文检索在 PostgreSQL 里需要专门的索引、top-k 查询怎样执行，以及快速上手。"
weight: 10
icon: fa-solid fa-compass
aliases:
  - "/docs/bm25/getting-started/quick-start/"
---

`vchord_bm25` 是一个 PostgreSQL 扩展，它按 BM25 相关性给行排序，并通过索引返回 `tsvector` 列中最匹配的行。文本仍然存在你自己的表里，查询仍然是 SQL：在 `tsvector` 列上建 `USING bm25` 索引，`ORDER BY terms <&> to_bm25query(...) LIMIT 10` 就会返回最相关的十行。如果只需要找出匹配的行而不需要排序，PostgreSQL 自带的 GIN 索引就够了。

## 为什么需要 vchord_bm25 {#why}

PostgreSQL 的全文检索借助 `tsvector` 列上的 GIN 索引，能很快找出匹配的行。但要给这些行排序，会遇到两个问题：

- **`ts_rank` 孤立地给每篇文档打分。** 它不知道一个词出现在多少篇文档里，也不知道文档的平均长度。于是一个每篇都有的词和一个罕见词分量相同，长文档靠重复用词就能排到前面。BM25 用的恰恰是这些全语料统计：罕见词权重更高，同一个词重复出现时加分越来越少，并按文档长度做归一化。
- **GIN 索引回答的是 `WHERE terms @@ query`，而不是 `ORDER BY rank`。** 要拿前 10 名，PostgreSQL 得取出每一个匹配行、逐个打分、再排序。代价随匹配行数增长，宽泛的查询在大表上几乎要读遍整张表。

`vchord_bm25` 把语料统计信息存在索引里，并用 Block-WeakAnd 遍历查询词的倒排列表，整块跳过不可能进入当前前 k 名的文档。一次查询的工作量取决于它的 `LIMIT` 和查询词，而不是匹配了多少行。

## 工作原理 {#how-it-works}

1. **分析。** 把每行文本转换成 `tsvector`：可以用 PostgreSQL 的 `to_tsvector`；PostgreSQL 处理不了的语言和词表，用 [pg_tokenizer](/zh/docs/tokenizer/)。一个词位有几个位置，它的词频就是几。
1. **建索引。** `CREATE INDEX ... USING bm25` 保存压缩后的倒排列表，以及 BM25 需要的统计信息：文档数、各文档长度、每个词出现在多少篇文档里。新插入和更新的行追加到增长段，立即可查；`VACUUM` 再把它们合并进压缩段。
1. **查询。** `to_bm25query(query, 'index_name')` 指定用哪个索引的统计信息来打分。`<&>` 运算符返回 BM25 分数的相反数，所以升序排列时最佳匹配在最前面。索引扫描先排出前 100 行（由参数 `bm25.limit` 决定），只有查询要更多行时才继续排更大的批次。
{.steps}

排序结果是精确的：索引返回的分数和顺序，与对每一行计算 `<&>` 再排序完全相同。[查询](/zh/docs/bm25/usage/querying/#how-a-query-runs)一页详细解释了批次，以及它对 `LIMIT`、过滤条件和开销意味着什么。

## 什么时候选别的方案 {#alternatives}

| 需求 | 方案 |
| --- | --- |
| 找出匹配布尔条件或短语的行，不需要排序 | `tsvector` 上的 GIN 索引加 `@@` 运算符 |
| 从大表中按 BM25 取出最相关的行 | `vchord_bm25` |
| 找出与查询意思相同但措辞不同的行 | [vchord](/zh/docs/vchord/) 向量检索，或两者结合的[混合检索](/zh/docs/bm25/usage/hybrid-search/) |
| 中文、日文、韩文文本，或 BERT 这类模型词表 | 先用 [pg_tokenizer](/zh/docs/tokenizer/) 生成 `tsvector`，再用 `vchord_bm25` |

## 快速上手 {#quick-start}

vchord_bm25 1.3.0 支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19。其他安装方式见[安装](/zh/docs/bm25/getting-started/installation/)。

1. 从 Pigsty 软件源安装：

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord_bm25
   ```

1. 预加载动态库并重启 PostgreSQL。列表里已有的库要保留。跳过这一步，`CREATE EXTENSION` 会报错：`vchord_bm25 must be loaded via shared_preload_libraries.`

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord_bm25';
   ```

1. 以超级用户身份在数据库中创建扩展：

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   ```

1. 建表、建索引、执行排序查询：

   ```sql
   CREATE TABLE documents (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       passage text NOT NULL,
       terms tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
   );

   INSERT INTO documents (passage) VALUES
       ('PostgreSQL provides full text search.'),
       ('BM25 ranks documents by relevance.'),
       ('PostgreSQL supports BM25 ranking with vchord_bm25.');

   CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops);

   SELECT id, passage,
          terms <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25'), 'documents_bm25') AS score
   FROM documents
   ORDER BY score
   LIMIT 10;
   ```
{.steps}

第三行同时包含两个查询词，分数最小（负得最多），排在第一。查询必须使用和文档相同的 `to_tsvector` 配置，换一种分析方式，得到的词位索引里根本没有。分数为什么是负数、怎样只返回匹配的行，见[查询](/zh/docs/bm25/usage/querying/#scores)。

## 接下来 {#next-steps}

- **给生产表建索引**，支持任意语言，并在持续写入下保持高效：[建索引](/zh/docs/bm25/usage/indexing/)。
- **调优查询与过滤**：[查询](/zh/docs/bm25/usage/querying/)与[过滤](/zh/docs/bm25/usage/filtering/)。
- **结合向量检索**：[混合检索](/zh/docs/bm25/usage/hybrid-search/)。
- **升级，或从 0.x 的 `bm25vector` 接口迁移**：[升级与迁移](/zh/docs/bm25/reference/migration/)。

## 许可证 {#license}

vchord_bm25 以 [AGPL-3.0](https://github.com/pgsty/vchord_bm25/blob/main/LICENSE) 许可证发布，是 TensorChord [VectorChord-bm25](https://github.com/supervc-stack/VectorChord-bm25) 的分支，由 [PGSTY](https://pgsty.com) 维护。商业授权或技术支持请联系 [rh@vonng.com](mailto:rh@vonng.com)。
