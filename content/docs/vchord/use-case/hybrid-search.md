---
title: "Hybrid Search with BM25 and Vectors"
linkTitle: "Hybrid Search"
description: "Search one PostgreSQL table with a BM25 keyword query and a vector query, merge the two rankings with Reciprocal Rank Fusion in one SQL statement, and optionally rerank with a cross-encoder."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/hybrid-search.md"
math: true
aliases:
  - "/docs/use-case/hybrid-search/"
  - "/vectorchord/use-case/hybrid-search/"
icon: fa-solid fa-code-merge
---

This tutorial builds a search over the SciFact corpus that runs a BM25 keyword query and a vector query against the same table and merges the two rankings. Keyword search finds documents containing the query's exact terms, such as identifiers and rare words; vector search finds documents that say the same thing in other words; each catches what the other misses. Because [vchord_bm25](/docs/bm25/) and vchord index the same PostgreSQL table, one SQL statement runs both searches and fuses the results, and a cross-encoder can rerank the merged list when accuracy matters more than latency.

<a id="what-is-the-vectorchord"></a><a id="what-is-vectorchord-bm25"></a><a id="what-is-bm25"></a><a id="why-a-postgres-native-bm25-ranking-implementation-is-needed"></a>

## How it works {#hybrid-search-explained}

<img src="/docs/images/hybrid-search-1.jpeg" alt="A query runs as a vector search and a keyword search, and the two result lists are fused or reranked into one" width="600" />

Each row stores the text, its embedding in a `vector` column, and its terms in a `tsvector` column. A `vchordrq` index answers `ORDER BY embedding <=> query LIMIT 100`, and a `bm25` index answers `ORDER BY terms <&> query LIMIT 100`. Reciprocal Rank Fusion (RRF) then scores each document by its rank in each list, so the two scales, cosine distance and BM25 score, never need to be compared:

$$
\operatorname{RRF}(d) = \sum_{i} \frac{1}{k + \operatorname{rank}_i(d)}
$$

A document missing from one list gets nothing from it. `k = 60` is the customary constant; a larger `k` flattens the difference between the top ranks.

<a id="tutorial-use-vectorchord-bm25-and-vectorchord-implement-hybrid-search"></a><a id="tutorial"></a><a id="Prerequisites"></a>

## Prerequisites {#prerequisites}

- PostgreSQL 15–19 with vchord 1.5.0 and vchord_bm25 1.3.0. From the Pigsty repository:

  ```bash
  pig ext add vchord vchord_bm25
  ```

- Python 3 and these packages. The models run on CPU, but a GPU makes embedding the corpus much faster.

  ```bash
  pip install "psycopg[binary]" pgvector FlagEmbedding requests
  ```

## Build the search {#prepare-data}

1. Preload both libraries and restart PostgreSQL. Keep any libraries already in the list.

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord, vchord_bm25';
   ```

1. Create the extensions and the table. `terms` is generated from `content`, so it stays in step with every insert and update:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;

   CREATE TABLE documents (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       content text NOT NULL,
       embedding vector(1024) NOT NULL,
       terms tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
   );
   ```

1. Load the corpus. Save this as `load.py` and run `python load.py`. It downloads the SciFact corpus from BEIR, embeds each document with BGE-M3, whose 1024-dimensional vectors are normalized, and copies the rows in:

   ```python
   import io
   import json
   import zipfile

   import psycopg
   import requests
   from FlagEmbedding import BGEM3FlagModel
   from pgvector.psycopg import register_vector

   DB_URL = "postgresql://postgres@localhost:5432/postgres"
   BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"

   archive = zipfile.ZipFile(io.BytesIO(requests.get(BEIR_URL, timeout=600).content))
   with archive.open("scifact/corpus.jsonl") as f:
       texts = [f"{doc['title']} {doc['text']}" for doc in map(json.loads, f)]

   model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
   embeddings = model.encode(texts, batch_size=32, max_length=8192)["dense_vecs"]

   with psycopg.connect(DB_URL) as conn:
       register_vector(conn)
       with conn.cursor().copy(
           "COPY documents (content, embedding) FROM STDIN WITH (FORMAT BINARY)"
       ) as copy:
           copy.set_types(["text", "vector"])
           for text, embedding in zip(texts, embeddings):
               copy.write_row((text, embedding))
   ```

1. Index both columns. SciFact has about 5,000 documents, so the vector index needs only its default single list; for a corpus over 100,000 rows, set `lists` and `probes` as described in [vchordrq index](/docs/vchord/usage/indexing/#lists).

   ```sql
   CREATE INDEX documents_embedding_idx ON documents
   USING vchordrq (embedding vector_cosine_ops);

   CREATE INDEX documents_terms_bm25 ON documents
   USING bm25 (terms bm25_ops);
   ```
{.steps}

<a id="semantic-search-with-vectorchord"></a><a id="key-word-search-with-vectorchord-bm25"></a><a id="rerank-fuse"></a><a id="rerankfuse"></a><a id="rerank-and-fuse"></a>

## Search with RRF {#rrf}

Each subquery takes 100 candidates from its index in index order, `row_number()` turns that order into ranks, and the outer query adds up the RRF scores. `<&>` returns the BM25 score negated, so ascending order puts the best match first, the same as a distance. Save this as `search.py`:

```python
import sys

import psycopg
from FlagEmbedding import BGEM3FlagModel
from pgvector.psycopg import register_vector

DB_URL = "postgresql://postgres@localhost:5432/postgres"

HYBRID_SQL = """
WITH semantic AS (
    SELECT id, row_number() OVER (ORDER BY distance) AS rank
    FROM (
        SELECT id, embedding <=> %(embedding)s AS distance
        FROM documents
        ORDER BY embedding <=> %(embedding)s
        LIMIT 100
    ) AS s
),
keyword AS (
    SELECT id, row_number() OVER (ORDER BY score) AS rank
    FROM (
        SELECT id, terms <&> to_bm25query(to_tsvector('english', %(query)s),
                                          'documents_terms_bm25'::regclass) AS score
        FROM documents
        ORDER BY terms <&> to_bm25query(to_tsvector('english', %(query)s),
                                        'documents_terms_bm25'::regclass)
        LIMIT 100
    ) AS k
)
SELECT id, content,
       coalesce(1.0 / (60 + semantic.rank), 0) + coalesce(1.0 / (60 + keyword.rank), 0) AS rrf
FROM semantic
FULL JOIN keyword USING (id)
JOIN documents USING (id)
ORDER BY rrf DESC
LIMIT %(limit)s
"""

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)


def hybrid_search(conn, query, limit=10):
    embedding = model.encode([query])["dense_vecs"][0]
    params = {"embedding": embedding, "query": query, "limit": limit}
    return conn.execute(HYBRID_SQL, params).fetchall()


if __name__ == "__main__":
    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        for doc_id, content, score in hybrid_search(conn, sys.argv[1]):
            print(f"{score:.4f}  {doc_id:>5}  {content[:80]}")
```

```bash
python search.py "Vitamin D deficiency increases the risk of multiple sclerosis"
```

To weight one side more, multiply its term in the `rrf` expression, for example `2 * coalesce(1.0 / (60 + keyword.rank), 0)`.

## Rerank with a cross-encoder {#cross-encoder}

A cross-encoder reads the query and a document together, so it judges relevance better than either index, but it costs one model call per candidate. Fetch more fused candidates and let it choose the top 10. Add this to `search.py` above the `if __name__` block, and in that block print `rerank(sys.argv[1], hybrid_search(conn, sys.argv[1], limit=100))` instead:

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)


def rerank(query, rows, limit=10):
    scores = reranker.compute_score([[query, content] for _, content, _ in rows], normalize=True)
    ranked = sorted(zip(rows, scores), key=lambda pair: pair[1], reverse=True)
    return [(doc_id, content, score) for (doc_id, content, _), score in ranked[:limit]]
```

## Other languages with pg_tokenizer {#pg-tokenizer}

`to_tsvector` covers the languages PostgreSQL ships text search configurations for. For Chinese, Japanese, or a custom pipeline, produce the `tsvector` with [pg_tokenizer](/docs/tokenizer/) 1.3.0 instead. Its `analyze_to_tsvector` reads the analyzer from a catalog table, so it cannot be used in a generated column; fill a plain column with a trigger:

1. Install `pg_tokenizer`, add it to `shared_preload_libraries`, restart, and create an analyzer:

   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;

   SELECT tokenizer_catalog.create_text_analyzer('en_analyzer', $$
   pre_tokenizer = "unicode_segmentation"
   [[character_filters]]
   to_lowercase = {}
   [[token_filters]]
   stopwords = "nltk_english"
   [[token_filters]]
   stemmer = "english_porter2"
   $$);
   ```

   For Chinese, use `[pre_tokenizer.jieba]` as the whole configuration.

1. Declare `terms tsvector` without `GENERATED ...` in `CREATE TABLE`, and keep it filled with a trigger:

   ```sql
   CREATE FUNCTION documents_terms() RETURNS trigger LANGUAGE plpgsql AS $$
   BEGIN
       NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.content, 'en_analyzer');
       RETURN NEW;
   END
   $$;

   CREATE TRIGGER documents_terms BEFORE INSERT OR UPDATE OF content ON documents
   FOR EACH ROW EXECUTE FUNCTION documents_terms();
   ```

1. Analyze the query text with the same analyzer. In `HYBRID_SQL`, replace both `to_tsvector('english', %(query)s)` with `tokenizer_catalog.analyze_to_tsvector(%(query)s, 'en_analyzer')`.
{.steps}

<a id="Evaluation"></a>

## Results on BEIR {#evaluation}

[Hybrid Search with Postgres Native BM25 and VectorChord](/blog/hybrid-search-with-postgres-native-bm25-and-vectorchord/) (March 2025) measured NDCG@10 on four [BEIR](https://github.com/beir-cellar/beir) datasets with BGE-M3 embeddings, BM25, RRF, and `bge-reranker-v2-m3`. Its BM25 used a Unicode word tokenizer instead of `to_tsvector('english', ...)`, so BM25 numbers from this tutorial will differ somewhat.

| Dataset | Vector | BM25 | RRF | Cross-encoder |
| --- | --- | --- | --- | --- |
| FiQA-2018 | 0.40343 | 0.25301 | 0.37632 | **0.42706** |
| Quora | 0.88433 | 0.78687 | 0.87014 | **0.89069** |
| SCIDOCS | 0.16055 | 0.15584 | 0.17299 | **0.17942** |
| SciFact | 0.57631 | 0.68495 | 0.67855 | **0.74635** |
{.wide}

The cross-encoder is best on every dataset. RRF beats both single methods only on SCIDOCS, where they score alike; on the other three it falls below the stronger method. Measure RRF on your own queries before relying on it, and weight the stronger side if one is clearly better. The benchmark code is in [xieydd/vectorchord-hybrid-search](https://github.com/xieydd/vectorchord-hybrid-search).

<a id="future-work"></a><a id="References"></a><a id="references"></a>
