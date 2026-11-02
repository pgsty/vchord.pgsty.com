---
title: "快速开始"
description: "使用 vchord_bm25 在 PostgreSQL 中运行你的第一条 BM25 全文排序检索查询。"
weight: 30
---

> [!IMPORTANT]
> 当前源码面向 **0.4.0（尚未发布）**，使用原生 `tsvector` 和新的索引格式。标注 0.3.x 的 `bm25vector` 示例仅适用于旧版。两者不能原地升级；请先阅读[0.4.0 迁移指南](/zh/docs/bm25/reference/migration/)。


本指南将带你一步步创建数据表、对文档进行分词、构建 `bm25` 索引，并执行 Top-K BM25 检索查询。

## 工作流 A：`bm25vector` + `pg_tokenizer`（`v0.1` – `v0.3`） {#workflow-a-bm25vector--pg_tokenizer-v01--v03}

在已发布的 `v0.1.0` 至 `v0.3.0` 版本中，`vchord_bm25` 与 `pg_tokenizer` 配合使用，将文本分词并存储到 `bm25vector` 列中。

### 1. 启用扩展并配置 `search_path` {#1-enable-extensions-and-configure-search_path}

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;
```

### 2. 创建分词器 {#2-create-a-tokenizer}

使用 `create_tokenizer` 搭配内置的 `llmlingua2`（或 `bert_base_uncased`）模型创建分词器：

```sql
SELECT create_tokenizer('my_tokenizer', $$
model = "llmlingua2"
$$);
```

> [!TIP]
> 需要领域专属词表、中文分词（`jieba`）或日文分词（`lindera`）？请参阅 [**分词器 (`pg_tokenizer`)**](/zh/docs/tokenizer/) 章节。

### 3. 创建表并写入文档 {#3-create-a-table-and-populate-documents}

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    embedding bm25vector
);

INSERT INTO documents (passage) VALUES
  ('PostgreSQL is a powerful, open-source object-relational database system. It has over 35 years of active development.'),
  ('Full-text search is a technique for searching a single computer-stored document or a collection in a full-text database.'),
  ('BM25 is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document.'),
  ('VectorChord-bm25 is a PostgreSQL extension that provides native BM25 ranking index using the Block-WeakAnd algorithm.');
```

### 4. 将文档分词为 `bm25vector` {#4-tokenize-documents-into-bm25vector}

`tokenize(text, tokenizer_name)` 返回一个由词元 ID 组成的 `INT[]` 数组，它可以隐式转换为 `bm25vector`（自动将重复的词元 ID 聚合为词频）：

```sql
UPDATE documents
SET embedding = tokenize(passage, 'my_tokenizer');

-- 查看稀疏的 bm25vector 表示形式 ({token_id:term_frequency, ...})
SELECT id, embedding FROM documents LIMIT 2;
```

### 5. 构建 `bm25` 索引 {#5-build-the-bm25-index}

```sql
CREATE INDEX documents_embedding_bm25
ON documents
USING bm25 (embedding bm25_ops);
```

### 6. 执行 Top-K BM25 查询 {#6-run-top-k-bm25-queries}

在升序 `ORDER BY` 子句中结合 `<&>` 操作符与 `to_bm25query(index_name, query_vector)` 执行检索：

```sql
SELECT
    id,
    passage,
    -(embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25 index', 'my_tokenizer'))) AS bm25_score
FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL BM25 index', 'my_tokenizer'))
LIMIT 10;
```

> [!IMPORTANT]
> **为什么 `<&>` 返回负数？**
> PostgreSQL 仅支持按**升序**（`ASC`）执行索引驱动的 `ORDER BY` 扫描。因此，`<&>` 操作符返回的是**负的** BM25 得分（例如 `-2.8415`）。数值越负代表相关性越高，从而使 `ORDER BY embedding <&> to_bm25query(...) ASC LIMIT K` 能够直接利用 Block-WeakAnd 索引扫描。如果希望展示正数得分，只需在 `SELECT` 列表中对该表达式取反（`-(embedding <&> ...)`）即可。

---

## 工作流 B：原生 `tsvector` API（`main` 分支） {#workflow-b-native-tsvector-api-main-branch}

在新一代 `main` 分支重构中，`vchord_bm25` 可直接为 PostgreSQL 原生的 **`tsvector`** 类型建立索引——对于标准语言无需安装额外的分词器扩展。

### 1. 创建扩展与数据表 {#1-create-extension-and-table}

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT NOT NULL,
    vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);

INSERT INTO documents (passage) VALUES
  ('PostgreSQL is a powerful, open-source object-relational database system.'),
  ('Full-text search is a technique for searching documents in a full-text database.'),
  ('BM25 is a bag-of-words retrieval function that ranks documents based on query terms.'),
  ('VectorChord-bm25 provides a native BM25 ranking index in PostgreSQL.');
```

### 2. 在 `tsvector` 上构建 `bm25` 索引 {#2-build-the-bm25-index-on-tsvector}

```sql
CREATE INDEX documents_bm25_idx
ON documents
USING bm25 (vector bm25_ops)
WITH (options = $$
k1 = 1.2
b = 0.75
$$, limit = 100);
```

### 3. 使用 `to_bm25query(tsvector, regclass)` 查询 {#3-query-with-to_bm25querytsvector-regclass}

```sql
SELECT
    id,
    passage,
    -(vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25 index'), 'documents_bm25_idx')) AS bm25_score
FROM documents
ORDER BY vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25 index'), 'documents_bm25_idx')
LIMIT 10;
```
