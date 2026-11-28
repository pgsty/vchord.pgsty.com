---
title: "混合检索"
linkTitle: "混合检索"
description: "一份可直接运行的 SQL 示例：用倒数排名融合（RRF）把 vchord_bm25 关键词排序与 vchord 向量检索结合起来。"
weight: 40
icon: fa-solid fa-code-merge
---

关键词检索能精确命中人名、产品编号、罕见词这类向量会模糊掉的词；向量检索能找到措辞不同但意思相同的段落。本示例在同一张表上、用一条 SQL 同时跑这两种检索，并用倒数排名融合（Reciprocal Rank Fusion，RRF）合并结果。RRF 只看每一行在各个列表中的名次，BM25 分数和向量距离不必换算到同一个尺度。

## 前提条件 {#prerequisites}

需要 [vchord](/zh/docs/vchord/getting-started/installation/) 1.5.0（含 pgvector）和 vchord_bm25，两者都要预加载。保留列表里已有的库，然后重启 PostgreSQL：

```sql
ALTER SYSTEM SET shared_preload_libraries = 'vchord,vchord_bm25';
```

然后以超级用户身份，在数据库中执行：

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25;
```

## 把文本、词项和向量存在一起 {#schema}

```sql
CREATE TABLE chunks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector GENERATED ALWAYS AS (to_tsvector('english', body)) STORED,
    embedding vector(3) NOT NULL
);

INSERT INTO chunks (body, embedding) VALUES
    ('PostgreSQL ranks text search results with BM25.',       '[0.9, 0.1, 0.1]'),
    ('vchord indexes embeddings for nearest-neighbor search.', '[0.1, 0.9, 0.2]'),
    ('Hybrid search merges keyword and vector rankings.',      '[0.6, 0.6, 0.3]'),
    ('A GIN index answers boolean full-text matches.',         '[0.8, 0.2, 0.0]');

CREATE INDEX chunks_terms_bm25 ON chunks USING bm25 (terms bm25_ops);
CREATE INDEX chunks_embedding_rq ON chunks USING vchordrq (embedding vector_cosine_ops);
```

三维向量只是用来代替嵌入模型的输出。真实的表里，向量列的维度与模型一致，文档和查询由同一个模型生成向量，vchordrq 索引按[vchordrq 索引](/zh/docs/vchord/usage/indexing/)中的方法根据行数配置。

## 融合排序结果 {#rrf}

```sql
WITH keyword AS (
    SELECT id, row_number() OVER (ORDER BY score) AS rank
    FROM (
        SELECT id, terms <&> to_bm25query(to_tsvector('english', 'vector search ranking'), 'chunks_terms_bm25') AS score
        FROM chunks
        ORDER BY score
        LIMIT 50
    ) AS hits
    WHERE score < 0
),
semantic AS (
    SELECT id, row_number() OVER (ORDER BY distance) AS rank
    FROM (
        SELECT id, embedding <=> '[0.5, 0.7, 0.2]' AS distance
        FROM chunks
        ORDER BY distance
        LIMIT 50
    ) AS hits
)
SELECT c.id, c.body,
       k.rank AS keyword_rank,
       s.rank AS semantic_rank,
       coalesce(1.0 / (60 + k.rank), 0) + coalesce(1.0 / (60 + s.rank), 0) AS rrf
FROM keyword AS k
FULL JOIN semantic AS s USING (id)
JOIN chunks AS c USING (id)
ORDER BY rrf DESC, c.id
LIMIT 10;
```

- 两个分支都是普通的按索引排序的查询，一个走 bm25 索引，一个走 vchordrq 索引，各自最多返回 50 个候选。
- `WHERE score < 0` 去掉一个查询词都不包含的行，这些行不参与关键词排名。
- 每一行的融合分数，是它在各个列表中 `1 / (60 + 名次)` 之和。常数 60 来自 RRF 的原始论文，作用是不让前几名的差距过大。
- `FULL JOIN` 保留只被其中一个分支找到的行。

## 调整融合方式 {#tuning}

- **候选深度。** 列表取得更深（例如 100 而不是 50），能找回只在一侧排名靠前的行，代价是两次索引扫描都更贵。让 `bm25.limit` 不小于关键词分支的深度，关键词分支就能[一批完成](/zh/docs/bm25/usage/querying/#batch-size)；默认值 100 足以覆盖 50。
- **权重。** 给某个分支的项乘一个系数，表示更信任它，例如 `0.7 * coalesce(1.0 / (60 + s.rank), 0)`。
- **过滤。** 把相同的条件（例如租户）同时放进两个分支。关键词一侧见[过滤](/zh/docs/bm25/usage/filtering/)，向量一侧见[vchordrq 索引](/zh/docs/vchord/usage/indexing/)。
- **度量。** RRF 并不总是优于两者中较好的那一个：在[已发布的 BEIR 测试](/zh/docs/bm25/reference/benchmarks/#hybrid)中，它在 FiQA 上低于单独的向量检索，在 SCIDOCS 上则高于两者。确定权重之前，先在自己的查询上比较 NDCG@10。想要更高的准确度，可以用 cross-encoder 对融合后的候选重排，见 vchord 的[混合检索案例](/zh/docs/vchord/use-case/hybrid-search/)。

## 在应用中执行 {#parameters}

把查询文本换成 `$1`，把查询向量换成 `$2::vector`，两个索引名都保持为字面量；索引名一旦参数化，PostgreSQL 就无法使用 bm25 索引（见[预备语句](/zh/docs/bm25/usage/querying/#prepared-statements)）。
