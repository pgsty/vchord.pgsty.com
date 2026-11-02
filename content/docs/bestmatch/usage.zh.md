---
title: "使用指南"
linkTitle: "使用指南"
description: "结合 pg_bestmatch 与 pgvector（sparsevec）或 pgvecto.rs（svector）构建 BM25 稀疏向量索引并执行全文检索的完整步骤。"
weight: 20
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#usage
---

本指南演示如何将 `pg_bestmatch` 与 [`pgvector`](/zh/docs/vector/)（`sparsevec`）搭配完成端到端的 BM25 文本检索流程，并附带基于 [`pgvecto.rs`](/zh/docs/vectors/)（`svector`）的等效用法。

## 1. 启用扩展并设置 `search_path`

```sql
CREATE EXTENSION IF NOT EXISTS pg_bestmatch;
CREATE EXTENSION IF NOT EXISTS vector;

SET search_path TO "$user", public, bm25_catalog;
```

## 2. 创建文档表并写入测试数据

```sql
CREATE TABLE documents (
    id bigint PRIMARY KEY,
    passage text
);

INSERT INTO documents (id, passage) VALUES
  (1, 'PostgreSQL is an advanced open-source relational database system.'),
  (2, 'VectorChord brings disk-friendly RaBitQ vector search to PostgreSQL.'),
  (3, 'BM25 is a bag-of-words ranking function used in information retrieval.');
```

## 3. 创建 BM25 语料库统计集

调用 `bm25_create(table_name, column_name, statistic_name, b, k)` 为目标表与文本列创建 BM25 统计信息（`b = 0.75`、`k = 1.2` 为默认推荐参数）：

```sql
SELECT bm25_create('documents', 'passage', 'documents_passage_bm25', 0.75, 1.2);
```

`bm25_create` 会在后台执行以下操作：
1. 在 `bm25_catalog` 模式下创建统计表与物化视图，统计全局词频、文档频率及文档总数。
2. 在 `documents` 表上注册触发器，自动追踪后续新增或删除的记录。

> [!NOTE] 批量更新后刷新统计集
> 当向表中大批量写入新文档后，如果希望重新计算全局逆文档频率（IDF）与平均文档长度（`avgdl`），请执行：
> ```sql
> SELECT bm25_refresh('documents_passage_bm25');
> ```

## 4. 生成文档稀疏向量列（配合 `pgvector`）

为 `documents` 表添加 `sparsevec(30522)` 列，并调用 `bm25_document_to_svector` 生成文档向量：

```sql
ALTER TABLE documents ADD COLUMN embedding sparsevec(30522);

UPDATE documents
SET embedding = bm25_document_to_svector(
    'documents_passage_bm25',
    passage,
    'pgvector'
)::sparsevec;
```

## 5. 创建 HNSW 稀疏向量索引

使用 [`pgvector`](/zh/docs/vector/) 的 HNSW 索引与内积操作符类 `sparsevec_ip_ops`：

```sql
CREATE INDEX documents_embedding_bm25_idx
ON documents
USING hnsw (embedding sparsevec_ip_ops);
```

## 6. 执行 BM25 检索查询

使用 `bm25_query_to_svector` 将查询词转化为稀疏向量，并按 `<#>`（负内积）升序排序：

```sql
SELECT
    id,
    passage,
    (embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search', 'pgvector')::sparsevec) * -1 AS bm25_score
FROM documents
ORDER BY embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search', 'pgvector')::sparsevec
LIMIT 5;
```

---

## 配合 `pgvecto.rs`（`svector`）使用

如果您使用的是 [`pgvecto.rs`](/zh/docs/vectors/)（`v0.3.0+`），可省略 `'pgvector'` 参数（或显式传入 `'pgvecto.rs'`）并将返回值转换为 `svector`：

```sql
CREATE EXTENSION IF NOT EXISTS vectors;

ALTER TABLE documents ADD COLUMN embedding svector(30522);

UPDATE documents
SET embedding = bm25_document_to_svector('documents_passage_bm25', passage)::svector;

CREATE INDEX documents_embedding_svector_idx
ON documents
USING vectors (embedding svector_dot_ops);

SELECT id, passage
FROM documents
ORDER BY embedding <#> bm25_query_to_svector('documents_passage_bm25', 'PostgreSQL vector search')::svector
LIMIT 5;
```
