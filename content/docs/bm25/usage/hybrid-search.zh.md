---
title: "混合检索 (BM25 + VectorChord)"
description: "结合稀疏词法 BM25 检索 (vchord_bm25) 与稠密向量检索 (vchord)，通过倒数排序融合 (RRF) 与 ColBERT 重排序提升检索精度。"
weight: 40
math: true
---

现代检索增强生成（RAG）与搜索流水线通常将**稠密向量检索**（[`vchord`](/zh/docs/)，擅长捕捉语义相似性）与**稀疏词法 BM25 检索**（`vchord_bm25`，擅长捕捉精确关键词、标识符与罕见词匹配）结合使用。由于这两个扩展均原生运行在 PostgreSQL 内部，你可以在**单条 SQL 查询中端到端执行混合检索**，无需任何外部编排服务。

## 混合检索表结构准备 {#schema-setup-for-hybrid-search}

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;

-- 1. 创建 BM25 分词器
SELECT create_tokenizer('bert', $$
model = "bert_base_uncased"
$$);

-- 2. 创建同时存储稠密向量与稀疏 bm25vector 的数据表
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    dense_emb vector(768),
    bm25_emb bm25vector
);

-- 3. 创建 VectorChord 稠密向量索引 (vchordrq) 与 BM25 词法索引 (bm25)
CREATE INDEX chunks_dense_idx ON chunks USING vchordrq (dense_emb vector_l2_ops);
CREATE INDEX chunks_bm25_idx  ON chunks USING bm25 (bm25_emb bm25_ops);
```

## 方式一：纯 SQL 实现倒数排序融合（RRF） {#method-1-reciprocal-rank-fusion-rrf-in-pure-sql}

**倒数排序融合（Reciprocal Rank Fusion，RRF）** 能够直接融合来自多个检索系统的排名结果，而无需在 L2/余弦距离与 BM25 得分之间做复杂的分数归一化校准：

$$\text{RRF\_Score}(d) = \frac{w_{\text{dense}}}{k + \text{rank}_{\text{dense}}(d)} + \frac{w_{\text{bm25}}}{k + \text{rank}_{\text{bm25}}(d)}$$

其中 \(k\) 为平滑常数（通常取 \(k = 60\)）。

```sql
WITH dense_results AS (
    SELECT
        id,
        RANK() OVER (ORDER BY dense_emb <-> '[0.012, -0.034, ...]'::vector) AS dense_rank
    FROM chunks
    ORDER BY dense_emb <-> '[0.012, -0.034, ...]'::vector
    LIMIT 100
),
bm25_results AS (
    SELECT
        id,
        RANK() OVER (
            ORDER BY bm25_emb <&> to_bm25query('chunks_bm25_idx', tokenize('PostgreSQL BM25 hybrid search', 'bert'))
        ) AS bm25_rank
    FROM chunks
    ORDER BY bm25_emb <&> to_bm25query('chunks_bm25_idx', tokenize('PostgreSQL BM25 hybrid search', 'bert'))
    LIMIT 100
),
fused AS (
    SELECT
        COALESCE(d.id, b.id) AS id,
        d.dense_rank,
        b.bm25_rank,
        COALESCE(1.0 / (60 + d.dense_rank), 0.0) +
        COALESCE(1.0 / (60 + b.bm25_rank), 0.0) AS rrf_score
    FROM dense_results d
    FULL OUTER JOIN bm25_results b ON d.id = b.id
    ORDER BY rrf_score DESC
    LIMIT 10
)
SELECT
    c.id,
    c.content,
    f.dense_rank,
    f.bm25_rank,
    round(f.rrf_score::numeric, 6) AS rrf_score
FROM fused f
JOIN chunks c ON c.id = f.id
ORDER BY f.rrf_score DESC;
```

## 方式二：混合召回 + ColBERT 晚期交互重排序 {#method-2-hybrid-retrieval--colbert-late-interaction-reranking}

如果追求更高的检索精度，可以先使用 `vchordrq`（稠密检索）+ `vchord_bm25`（词法检索）召回候选文档并集，再在 PostgreSQL 内使用 VectorChord 的 **`@#` (`max_sim`)** 多向量 ColBERT 操作符进行精细重排序：

```sql
WITH dense_candidates AS (
    SELECT id FROM chunks
    ORDER BY dense_emb <-> $1::vector
    LIMIT 50
),
bm25_candidates AS (
    SELECT id FROM chunks
    ORDER BY bm25_emb <&> to_bm25query('chunks_bm25_idx', tokenize($2, 'bert'))
    LIMIT 50
),
candidate_ids AS (
    SELECT id FROM dense_candidates
    UNION
    SELECT id FROM bm25_candidates
)
SELECT
    c.id,
    c.content,
    -(c.colbert_emb @# $3::vector[]) AS colbert_maxsim_score
FROM candidate_ids u
JOIN chunks c ON c.id = u.id
ORDER BY c.colbert_emb @# $3::vector[] ASC
LIMIT 10;
```

> [!TIP]
> 请参阅我们的工程深度解析博客 [**在 PostgreSQL 中使用 ColBERT 重排序为向量检索加速**](/zh/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/) 以及 [**使用 Postgres 原生 BM25 与 VectorChord 实现混合检索**](/zh/docs/vchord/use-case/hybrid-search/)，了解在 PostgreSQL 内部执行“稠密向量 + BM25 + ColBERT 重排序”的完整 BEIR 基准测试对比。
