---
title: "Hybrid Search (BM25 + VectorChord)"
description: "Combine sparse lexical BM25 search (vchord_bm25) and dense vector search (vchord) with Reciprocal Rank Fusion (RRF) and ColBERT reranking."
weight: 40
math: true
icon: fa-solid fa-code-merge
---

Modern retrieval pipelines combine **dense vector search** ([`vchord`](/docs/), which captures semantic similarity) with **sparse lexical BM25 search** (`vchord_bm25`, which captures exact keyword, identifier, and rare-term matches). Because both extensions run natively inside PostgreSQL, you can execute **end-to-end hybrid search in a single SQL query** with zero external orchestration.

## Schema Setup for Hybrid Search

These examples use `vchord` 1.2.0, `vchord_bm25` 1.1.0, and `pg_tokenizer` 1.0.0. [Install and preload the libraries](/docs/bm25/getting-started/installation/) first.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

SET search_path TO "$user", public, tokenizer_catalog;

-- 1. Create a BM25 tokenizer
SELECT create_tokenizer('bert', $$
model = "bert_base_uncased"
$$);

-- 2. Create a table storing both dense vectors and positioned tsvectors
CREATE TABLE chunks (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    dense_emb vector(768),
    bm25_emb tsvector,
    colbert_emb vector[]
);

CREATE FUNCTION chunks_tokenize() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    NEW.bm25_emb := tokenizer_catalog.tokenize_to_tsvector(NEW.content, 'bert');
    RETURN NEW;
END;
$$;

CREATE TRIGGER chunks_tokenize
BEFORE INSERT OR UPDATE OF content ON chunks
FOR EACH ROW EXECUTE FUNCTION chunks_tokenize();

-- 3. Create VectorChord dense index (vchordrq) and BM25 lexical index (bm25)
CREATE INDEX chunks_dense_idx ON chunks USING vchordrq (dense_emb vector_l2_ops);
CREATE INDEX chunks_bm25_idx  ON chunks USING bm25 (bm25_emb bm25_ops);
```

Store the tokenizer output in a regular column: `tokenize_to_tsvector` is `STABLE` and cannot be used in a generated column. Load document embeddings into `dense_emb` (768 dimensions) and, for reranking, `colbert_emb` (one vector per document token). The queries below use application-bound parameters: `$1` is the dense query vector, `$2` the query text, and `$3` the ColBERT query vectors.

## Method 1: Reciprocal Rank Fusion (RRF) in Pure SQL

**Reciprocal Rank Fusion (RRF)** combines rankings from multiple retrieval systems without requiring score calibration between L2/cosine distance and BM25 scores:

$$\text{RRF\_Score}(d) = \frac{w_{\text{dense}}}{k + \text{rank}_{\text{dense}}(d)} + \frac{w_{\text{bm25}}}{k + \text{rank}_{\text{bm25}}(d)}$$

where \(k\) is a smoothing constant (typically \(k = 60\)).

```sql
WITH dense_results AS (
    SELECT
        id,
        RANK() OVER (ORDER BY dense_emb <-> $1::vector) AS dense_rank
    FROM chunks
    ORDER BY dense_emb <-> $1::vector
    LIMIT 100
),
bm25_results AS (
    SELECT
        id,
        RANK() OVER (
            ORDER BY bm25_emb <&> to_bm25query(tokenize_to_tsvector('PostgreSQL BM25 hybrid search', 'bert'), 'chunks_bm25_idx')
        ) AS bm25_rank
    FROM chunks
    ORDER BY bm25_emb <&> to_bm25query(tokenize_to_tsvector('PostgreSQL BM25 hybrid search', 'bert'), 'chunks_bm25_idx')
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

## Method 2: Hybrid Retrieval + ColBERT Late-Interaction Reranking

For even higher accuracy, you can retrieve candidate documents using `vchordrq` (dense) + `vchord_bm25` (lexical) and rerank the union of candidates in PostgreSQL using VectorChord's **`@#` (`max_sim`)** multivector ColBERT operator:

```sql
WITH dense_candidates AS (
    SELECT id FROM chunks
    ORDER BY dense_emb <-> $1::vector
    LIMIT 50
),
bm25_candidates AS (
    SELECT id FROM chunks
    ORDER BY bm25_emb <&> to_bm25query(tokenize_to_tsvector($2, 'bert'), 'chunks_bm25_idx')
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
> See our engineering deep dives [**Supercharge Vector Search with ColBERT Rerank in PostgreSQL**](/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/) and [**Hybrid Search with Postgres Native BM25 and VectorChord**](/docs/vchord/use-case/hybrid-search/) for full BEIR benchmark comparisons of Dense + BM25 + ColBERT reranking inside PostgreSQL.
