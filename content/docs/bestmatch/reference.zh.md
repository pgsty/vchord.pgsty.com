---
title: "SQL 参考与方案对比"
linkTitle: "SQL 参考"
description: "pg_bestmatch（bm25_catalog）的完整 SQL 函数参考手册，以及与 vchord_bm25 的架构对比。"
weight: 30
math: true
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#references
---

## SQL 函数参考（`bm25_catalog`）

`pg_bestmatch` 的所有 SQL 函数均位于 `bm25_catalog` 模式下。

### `bm25_create`

为指定的表与文本列创建 BM25 语料库统计信息。

```sql
bm25_create(
    table_name     regclass,
    column_name    text,
    statistic_name text,
    b              real DEFAULT 0.75,
    k              real DEFAULT 1.2
) RETURNS void
```

- `table_name`：包含文档数据的目标表名。
- `column_name`：待分析的 `text` 文本列名。
- `statistic_name`：该 BM25 统计集的唯一标识名称（需为合法的 SQL 标识符）。
- `b`：BM25 文档长度归一化系数（默认 `0.75`）。
- `k`：BM25 词频饱和度参数 \(k_1\)（默认 `1.2`）。

---

### `bm25_refresh`

在文档发生增删改后，刷新 `statistic_name` 对应的物化语料库统计数据。

```sql
bm25_refresh(
    statistic_name text
) RETURNS void
```

---

### `bm25_drop`

删除与 `statistic_name` 关联的所有内部统计表、物化视图与触发器。

```sql
bm25_drop(
    statistic_name text
) RETURNS void
```

---

### `bm25_document_to_svector`

将文档字符串转化为兼容 [`pgvecto.rs`](/zh/docs/vectors/)（`svector`）或 [`pgvector`](/zh/docs/vector/)（`sparsevec`）的 BM25 词频权重稀疏向量字面量（`text`）。

```sql
bm25_document_to_svector(
    statistic_name text,
    passage        text,
    style          text DEFAULT 'pgvecto.rs'
) RETURNS text
```

- `statistic_name`：已注册的统计集名称。
- `passage`：输入文档文本。
- `style`：输出格式——`'pgvector'`（下标从 1 开始）或 `'pgvecto.rs'`（下标从 0 开始）。

---

### `bm25_query_to_svector`

将检索查询字符串转化为带 IDF 权重的稀疏向量字面量（`text`）。

```sql
bm25_query_to_svector(
    statistic_name text,
    query          text,
    style          text DEFAULT 'pgvecto.rs'
) RETURNS text
```

---

### `tokenize`

使用内置的 `bert-base-uncased` WordPiece 词表，将输入字符串切分为子词词元数组（`text[]`）。

```sql
tokenize(
    input text
) RETURNS text[]
```

---

## 方案对比：`pg_bestmatch` vs `vchord_bm25`

`pg_bestmatch` 与 [`vchord_bm25`](/zh/docs/bm25/) 均由 TensorChord 团队开发，旨在将 Okapi BM25 排序引入 PostgreSQL，但两者采用了截然不同的底层架构：

| 对比维度 | `pg_bestmatch`（`pg_bestmatch.rs`） | [`vchord_bm25`](/zh/docs/bm25/) + [`pg_tokenizer`](/zh/docs/tokenizer/) |
| :--- | :--- | :--- |
| **核心机制** | 将 BM25 的 TF/IDF 权重映射为稀疏向量（`sparsevec` / `svector`） | 原生倒排索引 + **Block-WeakAnd（WAND）** 块级剪枝扫描 |
| **索引类型** | 复用 [`pgvector`](/zh/docs/vector/) 或 [`pgvecto.rs`](/zh/docs/vectors/) 的 HNSW 稀疏向量索引 | 专用 `USING bm25 (vec bm25_ops)` 索引访问方法 |
| **检索精度** | 近似检索（基于稀疏向量 HNSW 图遍历） | **100% 精确** Top-K BM25 计分 |
| **分词能力** | 固定内置 `bert-base-uncased` 词表（`30,522` 维） | 可插拔 [`pg_tokenizer`](/zh/docs/tokenizer/)（支持 Unicode、Jieba、Lindera、HuggingFace、Snowball 及自定义语料词表） |
| **适用场景** | 仅安装了 `pgvector` 环境下的轻量级实验与基准对比 | **生产级全文检索与多路混合检索首选** |
