---
title: "ColBERT Rerank"
linkTitle: "ColBERT Rerank"
description: "Retrieve candidates with a single-vector vchordrq index, then rerank them in the same SQL query by ColBERTv2 token-level MaxSim with the @# operator."
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/colbert-rerank.md"
aliases:
  - "/docs/use-case/colbert-rerank/"
  - "/vectorchord/use-case/colbert-rerank/"
icon: fa-solid fa-ranking-star
---

This tutorial builds a two-stage search over a BEIR dataset: a `vchordrq` index on one embedding per passage finds 100 candidates, and ColBERTv2 token embeddings stored in the same row rerank them by MaxSim. A single pooled vector loses the detail of individual tokens, while scoring every passage token by token is too slow for a whole corpus; reranking only the candidates gets most of the token-level accuracy at the cost of a vector search. vchord's `@#` operator computes MaxSim in SQL, so both stages run in one query.

## How it works {#how-it-works}

<img src="/docs/images/maxsim.jpeg" alt="ColBERT late interaction: query and document tokens are encoded separately, and each query token is matched to its most similar document token" width="600" />

[ColBERT](https://github.com/stanford-futuredata/ColBERT) encodes a passage into one normalized 128-dimensional vector per token, and a query into 32. The MaxSim score of a passage is the sum, over the query vectors, of each one's largest inner product with any passage vector. `embs @# query` returns that score negated, so `ORDER BY ... ASC` puts the best passage first, as with a distance.

Each row in this tutorial holds the passage, one sentence embedding for the first stage, and the ColBERT token vectors as `vector(128)[]` for the second. To index the token vectors directly instead of reranking candidates, see [Multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/) and [ColQwen2 visual search](/docs/vchord/use-case/colqwen2-modal/).

<a id="Tutorial"></a><a id="tutorial"></a>

## Prerequisites {#prerequisites}

- PostgreSQL 15–19 with vchord 1.5.0 installed and preloaded, as in the [Overview](/docs/vchord/getting-started/overview/).
- Python 3 with the encoders and the PostgreSQL driver. Encoding a corpus of tens of thousands of passages with these models needs a GPU.

  ```bash
  pip install torch sentence-transformers colbert-ai "psycopg[binary]" pgvector requests tqdm
  ```

## Build and query {#build}

1. <a id="create-schema"></a>Create the extension and the table. `emb` holds a 1536-dimensional embedding from `gte-Qwen2-1.5B-instruct`; `embs` holds the ColBERT token vectors.

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;

   CREATE TABLE corpus (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       doc_id text NOT NULL,
       text text NOT NULL,
       emb vector(1536) NOT NULL,
       embs vector(128)[] NOT NULL
   );
   ```

1. <a id="encode-tokens"></a>Start `colbert_rerank.py` with the two encoders:

   ```python
   import io
   import json
   import sys
   import zipfile

   import psycopg
   import requests
   from colbert.infra import ColBERTConfig
   from colbert.modeling.checkpoint import Checkpoint
   from pgvector.psycopg import register_vector
   from sentence_transformers import SentenceTransformer
   from tqdm import tqdm

   DB_URL = "postgresql://postgres@localhost:5432/postgres"
   DATASET = "fiqa"
   BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip"


   class SentenceEncoder:
       def __init__(self):
           self.model = SentenceTransformer(
               "Alibaba-NLP/gte-Qwen2-1.5B-instruct", trust_remote_code=True
           )

       def encode_doc(self, doc):
           return self.model.encode([doc])[0]

       def encode_query(self, query):
           return self.model.encode([query], prompt_name="query")[0]


   class TokenEncoder:
       def __init__(self):
           config = ColBERTConfig(doc_maxlen=220, query_maxlen=32)
           self.checkpoint = Checkpoint("colbert-ir/colbertv2.0", colbert_config=config, verbose=0)

       def encode_doc(self, doc):
           return self.checkpoint.docFromText([doc], keep_dims=False)[0].cpu().numpy()

       def encode_query(self, query):
           return self.checkpoint.queryFromText([query])[0].cpu().numpy()
   ```

1. <a id="insert-and-index"></a>Add loading and indexing. The script downloads the dataset from BEIR, stores both embeddings for every passage, and then builds the first-stage index. psycopg passes a list of NumPy arrays as a `vector[]`.

   ```python
   def load(conn, sentence, token):
       url = BEIR_URL.format(DATASET)
       archive = zipfile.ZipFile(io.BytesIO(requests.get(url, timeout=600).content))
       with archive.open(f"{DATASET}/corpus.jsonl") as f:
           docs = [json.loads(line) for line in f]
       with conn.cursor() as cur:
           for doc in tqdm(docs):
               text = f"{doc['title']} {doc['text']}"
               cur.execute(
                   "INSERT INTO corpus (doc_id, text, emb, embs) VALUES (%s, %s, %s, %s)",
                   (doc["_id"], text, sentence.encode_doc(text), list(token.encode_doc(text))),
               )
       lists = min(4 * int(len(docs) ** 0.5), len(docs) // 40)
       conn.execute(f"""
           CREATE INDEX corpus_emb_idx ON corpus USING vchordrq (emb vector_l2_ops)
           WITH (options = $$
           residual_quantization = true
           [build.internal]
           lists = [{lists}]
           build_threads = 8
           $$, probes = '{max(1, lists // 10)}')
       """)
   ```

   The `lists` and `probes` formulas are the ones the measured run used. For your own table, choose them as described in [vchordrq index](/docs/vchord/usage/indexing/#lists).

1. <a id="query-and-rerank"></a>Add the search. The inner query takes 100 candidates from the index; the outer query reranks them by MaxSim:

   ```python
   SEARCH_SQL = """
   SELECT doc_id, text
   FROM (
       SELECT doc_id, text, embs
       FROM corpus
       ORDER BY emb <-> %(emb)s
       LIMIT %(candidates)s
   ) AS candidates
   ORDER BY embs @# %(embs)s::vector[]
   LIMIT %(k)s
   """


   def search(conn, query, sentence, token, candidates=100, k=10):
       params = {
           "emb": sentence.encode_query(query),
           "embs": list(token.encode_query(query)),
           "candidates": candidates,
           "k": k,
       }
       return conn.execute(SEARCH_SQL, params).fetchall()


   if __name__ == "__main__":
       sentence, token = SentenceEncoder(), TokenEncoder()
       with psycopg.connect(DB_URL, autocommit=True) as conn:
           register_vector(conn)
           if sys.argv[1] == "load":
               load(conn, sentence, token)
           else:
               for doc_id, text in search(conn, sys.argv[1], sentence, token):
                   print(doc_id, text[:80])
   ```

1. Load the corpus once, then search:

   ```bash
   python colbert_rerank.py load
   python colbert_rerank.py "How do I report foreign income on my tax return?"
   ```
{.steps}

`candidates` bounds the result: a passage the first stage misses cannot be reranked into the top 10. Raise it, or `probes`, when the reranked results miss passages you expect.

<a id="Evaluation"></a>

## Results {#evaluation}

The companion repository [kemingy/vectorchord-colbert](https://github.com/kemingy/vectorchord-colbert) measured NDCG@10 with these encoders on two BEIR datasets, reranking the vector search's top 10. It scored the candidates with its own SQL function rather than `@#`, so results from this tutorial can differ.

| Dataset | Vector search | With ColBERT rerank |
| --- | --- | --- |
| FiQA | 0.23211 | **0.30330** |
| Quora | 0.31599 | **0.39340** |

## Limits {#limits}

- Token vectors make rows large: a 220-token passage stores about 110 KB of `vector(128)[]`. Declaring the column `halfvec(128)[]` halves that; `@#` is defined for `halfvec[]` as well.
- The rerank reads `embs` for every candidate, so its cost grows with `candidates` rather than with the table.

<a id="future-work"></a><a id="References"></a><a id="references"></a>
