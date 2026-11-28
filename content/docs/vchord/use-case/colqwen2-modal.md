---
title: "Visual Document Search with ColQwen2 and Modal"
linkTitle: "ColQwen2 & Modal"
description: "Search document pages by their images without OCR: embed pages with ColQwen2 on Modal GPUs, index the patch vectors with vchordrq, and rank pages with MaxSim."
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/colqwen2-modal.md"
aliases:
  - "/docs/use-case/colqwen2-modal/"
  - "/vectorchord/use-case/colqwen2-modal/"
icon: fa-solid fa-file-image
---

This tutorial builds a search over the page images of the ViDoRe benchmark that takes a text question and returns the pages that answer it, without running OCR. OCR pipelines lose what text extraction cannot capture, such as tables, charts, and layout; ColQwen2 instead embeds each rendered page as a set of 128-dimensional vectors, one per image patch, that a query's token vectors are matched against. vchord indexes those vector arrays with `vector_maxsim_ops` and ranks pages by MaxSim with the `@#` operator, and [Modal](https://modal.com/) supplies the GPUs that compute the embeddings.

<a id="what-is-colqwen2-the-power-of-visual-understanding"></a>

## How it works {#how-does-vectorchord-enable-colqwen2-in-postgres}

[ColPali](https://arxiv.org/abs/2407.01449) encodes a page image with a vision language model and keeps one vector per image patch; [ColQwen2](https://huggingface.co/vidore/colqwen2-v1.0) does the same with Qwen2-VL-2B. A text query becomes one vector per token. A page's score is MaxSim: for each query vector, its largest inner product with any of the page's vectors, summed over the query.

Scoring every page that way is too slow for a large collection. A `vchordrq` index with `vector_maxsim_ops` stores every patch vector of every page in its lists. A query probes the lists for each of its vectors, adds up per-page scores from the vectors it finds, and estimates the contribution of query vectors that found nothing on a page, a technique taken from [WARP](https://arxiv.org/abs/2501.17788). `vchordrq.maxsim_refine` and `vchordrq.maxsim_threshold` make that estimate tighter at the cost of more work; [Multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/) defines them.

<a id="tutorial-building-your-ocr-free-rag-system"></a><a id="Prerequisites"></a>

## Prerequisites {#prerequisites}

- PostgreSQL 15–19 with vchord 1.5.0 installed and preloaded, as in the [Overview](/docs/vchord/getting-started/overview/).
- A [Modal](https://modal.com/) account. The embedding step runs on one H100.
- The companion repository and the Python packages for the embedding and loading steps:

  ```bash
  git clone https://github.com/xieydd/vectorchord-colqwen2
  cd vectorchord-colqwen2/modal
  pip install modal fastapi msgspec datasets numpy "psycopg[binary]" pgvector
  python3 -m modal setup
  ```

## Build the index {#build}

1. <a id="step-1-load-the-data-using-modal-volumes"></a>Download the ViDoRe benchmark into a Modal volume. `dataset.py` saves every dataset in the [ViDoRe collection](https://huggingface.co/collections/vidore/vidore-benchmark-667173f98e70a1c0fa4db00d) to the `colpali-dataset` volume, keeping one row per page image:

   ```bash
   modal run dataset.py::download_dataset
   ```

1. <a id="step-2-process-data--generate-embeddings-with-modal--colqwen2"></a><a id="step-2-generate-embeddings"></a>Embed the pages and their questions. `embedding.py` runs `vidore/colqwen2-v1.0` on a Modal GPU, writes a checkpoint to the `colpali-embedding-checkpoint` volume after each batch so an interrupted run resumes, and stores one saved dataset per ViDoRe dataset with each page's patch vectors and its question's token vectors. Copy the result to your machine:

   ```bash
   modal run embedding.py::embed_dataset
   modal volume get colpali-embedding-checkpoint / embeddings
   ```

1. <a id="step-3-create-index-in-vectorchord-using-vechord-sdk"></a>Create the table. Each row is one page with the question that ViDoRe pairs with it:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;

   CREATE TABLE pages (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       dataset text NOT NULL,
       dataset_id int NOT NULL,
       query text,
       image_embedding vector(128)[] NOT NULL,
       query_embedding vector(128)[] NOT NULL
   );
   ```

1. Load the embeddings. Save this as `load.py` and run `python load.py embeddings`:

   ```python
   import sys
   from pathlib import Path

   import numpy as np
   import psycopg
   from datasets import load_from_disk
   from pgvector.psycopg import register_vector

   DB_URL = "postgresql://postgres@localhost:5432/postgres"


   def vectors(buffer, shape):
       return list(np.frombuffer(buffer, dtype=np.float32).reshape(shape))


   with psycopg.connect(DB_URL) as conn:
       register_vector(conn)
       with conn.cursor() as cur:
           for info in sorted(Path(sys.argv[1]).rglob("dataset_info.json")):
               path = info.parent
               dataset = f"{path.parent.name}/{path.name}"
               for item in load_from_disk(str(path)):
                   cur.execute(
                       "INSERT INTO pages (dataset, dataset_id, query, image_embedding, query_embedding)"
                       " VALUES (%s, %s, %s, %s, %s)",
                       (
                           dataset,
                           item["id"],
                           item["query"],
                           vectors(item["image_embedding"], item["image_embedding_shape"]),
                           vectors(item["query_embedding"], item["query_embedding_shape"]),
                       ),
                   )
   ```

1. Build the MaxSim index. It stores every patch vector separately, so size `lists` from the total number of patch vectors, not the number of pages; see [vchordrq index](/docs/vchord/usage/indexing/#lists). The companion repository uses 2,500 lists:

   ```sql
   CREATE INDEX pages_image_embedding_idx ON pages
   USING vchordrq (image_embedding vector_maxsim_ops)
   WITH (options = $$
   [build.internal]
   lists = [2500]
   spherical_centroids = true
   build_threads = 8
   $$);
   ```
{.steps}

## Search {#search}

A search orders pages by `@#` against the query's token vectors. The settings are those of the companion repository's evaluation:

```sql
SET vchordrq.probes = '16';
SET vchordrq.epsilon = 1.0;
SET vchordrq.maxsim_refine = 10;
SET vchordrq.maxsim_threshold = 2000;

SELECT p.dataset, p.dataset_id
FROM pages AS p
ORDER BY p.image_embedding @# (SELECT query_embedding FROM pages WHERE id = 1)
LIMIT 10;
```

In an application, encode the question with the same ColQwen2 model and pass its token vectors as a `vector[]` parameter in place of the subquery.

<a id="step-4-evaluation-does-it-work"></a><a id="step-4-evaluation---does-it-work"></a><a id="step-4-evaluation"></a>

## Evaluate {#evaluate}

ViDoRe pairs each question with one page, so a question is answered when its own row comes back. This query measures NDCG@10 and recall@10 over 100 questions from [`vidore/arxivqa_test_subsampled`](https://huggingface.co/datasets/vidore/arxivqa_test_subsampled), scientific figures and charts. Run it with `\timing on` to compare settings:

```sql
WITH questions AS MATERIALIZED (
    SELECT id, query_embedding
    FROM pages
    WHERE dataset = 'vidore/arxivqa_test_subsampled'
    ORDER BY id
    LIMIT 100
),
ranks AS (
    SELECT array_position(
        ARRAY(
            SELECT p.id
            FROM pages AS p
            ORDER BY p.image_embedding @# q.query_embedding
            LIMIT 10
        ),
        q.id
    ) AS rank
    FROM questions AS q
)
SELECT round(avg(coalesce(1 / log(2, rank + 1), 0)), 4) AS ndcg_at_10,
       round(avg((rank IS NOT NULL)::int), 4) AS recall_at_10
FROM ranks;
```

## Results {#results}

[Beyond Text: Unlock OCR-Free RAG in PostgreSQL with Modal & VectorChord](/blog/beyond-text-unlock-ocr-free-rag-in-postgresql-with-modal-and-vectorchord/) (April 2025) ran this evaluation with and without vchord's MaxSim pruning:

| | NDCG@10 | Recall@10 | Time for 100 questions |
| --- | --- | --- | --- |
| Without pruning | 0.8615 | 0.92 | 810 s |
| With pruning | 0.8353 | 0.90 | 41 s |

Pruning made the evaluation about 20 times faster for a drop of 0.026 in NDCG@10 and 0.02 in recall@10. The post notes that the timings come from a slow local setup, so compare the ratio rather than the absolute times.

<a id="conclusion-visual-rag-made-simpler-in-postgres"></a><a id="References"></a><a id="references"></a>
