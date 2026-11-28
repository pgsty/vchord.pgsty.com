---
title: "建索引"
linkTitle: "建索引"
description: "为任意语言生成 tsvector，创建 bm25 索引，选择 k1 和 b，并在表持续变化时保持索引快速、准确。"
weight: 10
icon: fa-solid fa-database
---

`bm25` 索引保存 BM25 排序所需的倒排列表和语料统计信息，建在一个 `tsvector` 列或表达式上。本页介绍如何生成这个 `tsvector`、如何建索引和调参，以及在行被插入、更新、删除时如何保持查询速度。

## 生成 tsvector {#tsvector}

索引对 `tsvector` 里的内容打分，所以相关性首先取决于文本分析。不管用哪种方法，都有两条规则：

- 文档和查询必须经过相同的分析。用另一种配置构造的查询，产生的词位索引里根本没有。
- 文档的 `tsvector` 必须带位置：一个词位有几个位置，词频就是几。`strip()`、`array_to_tsvector()` 以及不带位置的字面量都会被拒绝（见[限制](#limits)）。

**生成列** 最简单，适用于 PostgreSQL 文本检索配置能处理的语言，例如 `english` 或 `simple`。[快速上手](/zh/docs/bm25/getting-started/overview/#quick-start)用的就是生成列。

**表达式索引** 省掉单独一列的存储，但查询必须按同一个表达式排序：

```sql
CREATE INDEX documents_passage_bm25 ON documents
USING bm25 ((to_tsvector('english', passage)) bm25_ops);

SELECT id FROM documents
ORDER BY to_tsvector('english', passage)
      <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_passage_bm25')
LIMIT 10;
```

索引表达式必须是不可变的（immutable），所以要显式写出配置名。

**pg_tokenizer** 用来处理 `to_tsvector` 切分不了的文本：用 Jieba 切分中文，用 Lindera 切分日文和韩文，或者输出某个模型词表的 token ID。分析器定义保存在系统表里，因此它的函数是 `STABLE` 的，不能用在生成列或索引表达式中。改用普通列，例如由触发器填充：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;  -- 同样需要把 pg_tokenizer 加入 shared_preload_libraries

SELECT tokenizer_catalog.create_text_analyzer('zh', $$
[pre_tokenizer.jieba]
$$);

CREATE TABLE articles (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector
);

CREATE FUNCTION articles_terms() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.body, 'zh');
    RETURN NEW;
END
$$;

CREATE TRIGGER articles_terms BEFORE INSERT OR UPDATE OF body ON articles
FOR EACH ROW EXECUTE FUNCTION articles_terms();

CREATE INDEX articles_bm25 ON articles USING bm25 (terms bm25_ops);

SELECT id, body
FROM articles
ORDER BY terms <&> to_bm25query(tokenizer_catalog.analyze_to_tsvector('全文检索', 'zh'), 'articles_bm25')
LIMIT 10;
```

`analyze_to_tsvector` 把分析器切出的词作为词位输出；`tokenize_to_tsvector` 输出的是模型的 token ID。分析器、过滤器和模型的用法见 [pg_tokenizer 文档](/zh/docs/tokenizer/)。

## 创建索引 {#create}

```sql
CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops);
```

- 要写明运算符类 `bm25_ops`，它不是 `tsvector` 的默认运算符类。
- 给索引起一个会长期使用的名字。查询在 `to_bm25query` 中引用这个名字，名字决定了用哪份统计信息打分。
- 一个索引只覆盖一列。要在固定子集（例如已发布的行）内排序，建一个[部分索引](/zh/docs/bm25/usage/filtering/#partial-indexes)。
- `CREATE INDEX CONCURRENTLY` 和其他索引一样可用。

建索引时，PostgreSQL 的并行维护进程会一起扫描表，进程数受 `max_parallel_maintenance_workers`（或表的 `parallel_workers` 选项）限制。主进程和各工作进程分摊 `maintenance_work_mem` 作为排序缓冲区，每个进程最多 64 MiB，超出部分写入临时文件。构建进度可以在 `pg_stat_progress_create_index` 中查看，`phase` 依次经过 `building index: scanning table` 和 `building index: writing index structures`：

```sql
SELECT phase, tuples_done, tuples_total
FROM pg_stat_progress_create_index;
```

## 选择 k1 和 b {#scoring-parameters}

BM25 有两个参数，在建索引时确定：

- **`k1`**（默认 `1.2`，取值 1.2–2.0）决定一个词重复出现时，加分多快趋于饱和。如果重复出现确实意味着更相关（例如较长的技术文档），可以调高。
- **`b`**（默认 `0.75`，取值 0–1）决定对长文档的惩罚力度。如果文档长是因为内容多而不是啰嗦，可以调低；`0` 表示完全不做长度归一化。

默认值与 Lucene、Elasticsearch 一致，是合适的起点。只有在度量过相关性之后才去改：

1. 收集真实查询并标注相关行，度量当前索引的 NDCG@10 或召回率。
1. 用候选参数在同一列上再建一个索引。两个索引都能用，因为每条查询都会指明用哪个索引打分：

   ```sql
   CREATE INDEX CONCURRENTLY documents_bm25_k15 ON documents USING bm25 (terms bm25_ops)
   WITH (options = $$
   k1 = 1.5
   b = 0.6
   $$);
   ```

1. 针对 `documents_bm25_k15` 运行同一批查询，比较结果。
1. 留下更好的索引，删掉另一个。两者并存期间，每次写入都要维护两个索引。
{.steps}

要原地修改已有索引的参数，先设置 `options` 再重建：`ALTER INDEX documents_bm25 SET (options = $$ ... $$); REINDEX INDEX documents_bm25;`。`k1` 和 `b` 在公式中的位置见[分数定义](/zh/docs/bm25/reference/sql/#score)。

## 保持索引高效 {#maintenance}

插入和更新的行会追加到**增长段**，立即可查，分数也是精确的。但增长段没有块摘要，每次查询都要把它整个读一遍。在 `VACUUM` 把它合并进压缩段之前，查询耗时会随它一起增长。

`VACUUM`（手动执行或 autovacuum）在满足以下任一条件时合并：

- 增长段至少有 `maintenance_min_rows` 行（默认 1,000），且不少于已合并行数的 `maintenance_scale_factor` 倍（默认 0.1）。
- 已删除的行达到全部行数的 `maintenance_scale_factor`。在此之前，被删除和被替换的行仍计入统计信息（文档数、各词的文档频率和平均长度），所以大批量 `DELETE` 或整体改写之后，分数会有偏差。

合并使用与 `VACUUM` 相同的锁，读写不受影响。单独执行 `ANALYZE` 不会触发合并。两个阈值都是[索引选项](/zh/docs/bm25/reference/gucs/#index-options)；大表上调低 `maintenance_scale_factor` 可以更频繁地合并。

**只插入不更新的表**，要等插入行数达到 `autovacuum_vacuum_insert_threshold` 加上表大小的 `autovacuum_vacuum_insert_scale_factor`（默认 0.2）才会被 vacuum。大表上这会让增长段变得很大，可以为这张表调低比例：

```sql
ALTER TABLE documents SET (autovacuum_vacuum_insert_scale_factor = 0.02);
```

**立即合并**：批量导入或删除之后，可以用 [`bm25_maintain`](/zh/docs/bm25/reference/sql/#field-bm25_maintain-regclass) 无视阈值立刻合并：

```sql
SELECT bm25_maintain('documents_bm25');
```

写出了合并后的段时返回 `true`；没有变化，或者上一次合并替换下来的页还在等待更早的事务结束时，返回 `false`。调用者需要是表的属主，PostgreSQL 17 及以上也可以持有 `MAINTAIN` 权限；它与 `VACUUM` 获取相同的表锁。

**长事务** 会推迟合并后旧页的复用，在长事务结束前索引会持续膨胀。在没有开启 `hot_standby_feedback` 的热备库上，如果查询读到的页刚被主库复用，会报错 `canceling statement due to conflict with bm25 index maintenance`；重试查询，或开启 `hot_standby_feedback`。

## 重建 {#rebuild}

需要重建的场景：应用新的 `k1` 和 `b`，或者修复 `CREATE INDEX CONCURRENTLY` 失败后留下的无效索引。针对无效索引的查询会报错 `index "documents_bm25" is not valid`。

- `REINDEX INDEX documents_bm25` 保留索引的 OID。执行期间会阻塞对表的写入，以及使用该索引的查询。
- `REINDEX INDEX CONCURRENTLY documents_bm25` 不阻塞写入，但会建出一个 OID 不同的新索引。

`to_bm25query(..., 'documents_bm25')` 在语句解析时把名字转换成 OID，所以重建之后解析的语句会找到新索引。而视图、物化视图、规则以及 SQL 标准函数体（`BEGIN ATOMIC` 或 `RETURN`）存的是旧 OID，之后会报错 `the relation does not exist`。请保留它们的原始定义，并在并发重建之后用 `CREATE OR REPLACE` 重新执行；那时 `pg_get_viewdef` 输出的已经是失效的 OID。删除后重新创建索引，也是同样的情况。

## 限制 {#limits}

- **单列。** 再加一个键列会报错 `multicolumn index is not supported`。
- **必须带位置。** 不带位置的文档 `tsvector` 在插入、`CREATE INDEX` 和打分时都会报错 `tsvector must have positions`。查询用的 `tsvector` 可以不带位置。
- **PostgreSQL 的 `tsvector` 限制。** 每个词位最多保留 256 个位置，超过 16,383 的位置会被截断为 16,383，`to_tsvector` 会丢弃超过 2,046 字节的词。因此在很长的文档里词频会饱和。请按几千词的段落建索引，而不是整本书。
- **不支持 unlogged 表。** 在 `UNLOGGED` 表上执行 `CREATE INDEX`，会得到错误 `Unlogged indexes are not supported.`
- **分区表。** 在分区表上 `CREATE INDEX` 会为每个分区各建一个 bm25 索引，各有各的统计信息。请直接查询分区，并在 `to_bm25query` 中写该分区的索引名；父表上的索引不能用于打分，也不能传给 `bm25_maintain`。
