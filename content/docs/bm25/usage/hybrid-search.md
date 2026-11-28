---
title: "Hybrid Search"
linkTitle: "Hybrid Search"
description: "A runnable SQL recipe that combines vchord_bm25 keyword ranking with vchord vector search through Reciprocal Rank Fusion."
weight: 40
icon: fa-solid fa-code-merge
---

Keyword search finds exact terms that embeddings blur, such as names, product codes, and rare words; vector search finds passages that say the same thing in other words. This recipe runs both on one table in one SQL statement and merges them with Reciprocal Rank Fusion (RRF), which uses only each row's rank in each list, so BM25 scores and vector distances never have to be put on one scale.

## Prerequisites {#prerequisites}

You need [vchord](/docs/vchord/getting-started/installation/) 1.5.0 with pgvector and vchord_bm25, both preloaded. Keep any libraries already in the list, and restart PostgreSQL:

```sql
ALTER SYSTEM SET shared_preload_libraries = 'vchord,vchord_bm25';
```

Then, as a superuser, in your database:

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25;
```

## Store text, terms, and embeddings together {#schema}

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

The three-dimensional vectors stand in for your embedding model's output. In a real table the column has the model's dimension, documents and queries are embedded by the same model, and the vchordrq index is sized for the row count as described in [vchordrq index](/docs/vchord/usage/indexing/).

## Fuse the rankings {#rrf}

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

- Each branch is an ordinary index-ordered query, one on the bm25 index and one on the vchordrq index, and each returns at most 50 candidates.
- `WHERE score < 0` drops rows that contain none of the query terms, so they get no keyword rank.
- Each row's fused score is the sum of `1 / (60 + rank)` over the lists it appears in. The constant 60 comes from the original RRF paper and keeps the top few ranks from dominating.
- `FULL JOIN` keeps rows that only one branch found.

## Tune the fusion {#tuning}

- **Candidate depth.** Deeper lists, such as 100 instead of 50, find rows that rank well on one side only, at the cost of both index scans. Keep `bm25.limit` at least as large as the keyword depth so the keyword branch finishes in [one batch](/docs/bm25/usage/querying/#batch-size); the default of 100 covers 50.
- **Weights.** Multiply a branch's term to trust it more, for example `0.7 * coalesce(1.0 / (60 + s.rank), 0)`.
- **Filters.** Put the same condition, such as a tenant, in both branches. [Filtering](/docs/bm25/usage/filtering/) covers the keyword side and [vchordrq index](/docs/vchord/usage/indexing/) the vector side.
- **Measure.** RRF does not always beat the better single method: in the [published BEIR runs](/docs/bm25/reference/benchmarks/#hybrid) it scored below vector search alone on FiQA and above both methods on SCIDOCS. Compare NDCG@10 on your own queries before choosing weights. For more accuracy, rerank the fused candidates with a cross-encoder, as in vchord's [hybrid search use case](/docs/vchord/use-case/hybrid-search/).

## Run it from an application {#parameters}

Replace the query text with `$1` and the query vector with `$2::vector`, and keep both index names as literals; with a parameterized index name, PostgreSQL cannot use the bm25 index ([Prepared statements](/docs/bm25/usage/querying/#prepared-statements)).
