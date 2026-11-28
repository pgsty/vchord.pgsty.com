---
title: "Multi-Vector Retrieval"
linkTitle: "Multi-Vector"
description: "Index arrays of token or patch embeddings from ColBERT- and ColPali-style models and rank documents by MaxSim with the @# operator."
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/multi-vector-retrieval.md"
math: true
aliases:
  - "/docs/usage/multi-vector-retrieval/"
  - "/vectorchord/usage/multi-vector-retrieval/"
  - "/docs/vchord/usage/indexing-with-maxsim-operators/"
  - "/vectorchord/usage/indexing-with-maxsim-operators/"
icon: fa-solid fa-cubes
---

A single embedding per document has to squeeze every detail into one vector, and fine-grained matches get lost. Late-interaction models such as ColBERT for text and ColQwen2 for page images keep one vector per token or image patch instead, and score a document by **MaxSim**: for each query vector, take its best match among the document's vectors, then add those up.

\[
\operatorname{MaxSim}(Q, D) = \sum_{i} \max_{j} \; q_i \cdot d_j
\]

vchordrq indexes such arrays directly. The `@#` operator returns the negative MaxSim, so that `ORDER BY ... LIMIT` puts the best documents first, like the other distance operators. For complete pipelines, see [ColBERT rerank](/docs/vchord/use-case/colbert-rerank/) and [ColQwen2 visual RAG](/docs/vchord/use-case/colqwen2-modal/).

## Index and query {#how-to-start}

Store each document's vectors as an array, index it with a `*_maxsim_ops` class, and pass the query's vectors as an array:

```sql
CREATE TABLE docs (id bigserial PRIMARY KEY, embeddings vector(3)[]);

INSERT INTO docs (embeddings)
SELECT ARRAY[
    ARRAY[random(), random(), random()]::vector,
    ARRAY[random(), random(), random()]::vector,
    ARRAY[random(), random(), random()]::vector
]
FROM generate_series(1, 1000);

CREATE INDEX ON docs USING vchordrq (embeddings vector_maxsim_ops);

SELECT id FROM docs
ORDER BY embeddings @# ARRAY['[3, 1, 2]'::vector, '[2, 2, 2]'::vector]
LIMIT 5;
```

Every vector in every array is indexed on its own, so size `lists` from the total number of vectors, not rows: 1 million passages of about 100 tokens are 100 million vectors. Arrays of `halfvec`, `rabitq8`, and `rabitq4` use `halfvec_maxsim_ops`, `rabitq8_maxsim_ops`, and `rabitq4_maxsim_ops`. Storing token vectors as [`rabitq8`](/docs/vchord/usage/quantization-types/) cuts the table to a quarter of its `vector` size.

## How a query is scored {#scoring}

For each query vector, vchordrq probes its own lists and collects the nearest document vectors, then adds up each document's best matches. A document whose vectors were not found for some query vector, because they sat in lists that were not probed, gets an estimate for that term: the worst distance seen for that query vector, or a bound from `maxsim_threshold`.

By default, the distances come from RaBitQ estimates without reranking. Two settings trade speed for accuracy:

- `vchordrq.probes` decides how many lists each query vector reads, as for single vectors. Raise it first.
- `vchordrq.maxsim_refine` recomputes exact distances for the top documents. `0` keeps estimates only; values such as `1024` improve recall at a higher cost.

Measure recall with [`vchordrq_evaluate_query_recall`](/docs/vchord/usage/measure-recall/) and `exact_search => true`; the default estimated mode does not support `@#`.

## Limits {#limits}

MaxSim indexes are vchordrq only, and do not support `rerank_in_table`, filter keys, or `vchordrq.max_scan_tuples`.

## Reference {#reference}

### Operator classes {#operator-classes}

| Column type | Operator class | Operator |
| --- | --- | --- |
| `vector[]` | `vector_maxsim_ops` | `@#` |
| `halfvec[]` | `halfvec_maxsim_ops` | `@#` |
| `rabitq8[]` | `rabitq8_maxsim_ops` | `@#` |
| `rabitq4[]` | `rabitq4_maxsim_ops` | `@#` |

### Search parameters {#search-parameters}

<a id="vchordrq-maxsim-refine"></a><a id="search-parameters-vchordrq-maxsim-refine"></a><a id="vchordrq-maxsim-threshold"></a><a id="search-parameters-vchordrq-maxsim-threshold"></a>

Both can also be [stored on the index](/docs/vchord/usage/fallback-parameters/).

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordrq.maxsim_refine` | integer | `0` | Number of top documents whose distances are recomputed exactly. `0` uses RaBitQ estimates only. |
| `vchordrq.maxsim_threshold` | integer | `0` | When above `0`, bound the distance of a query vector's unfound matches by the centroid of the first leaf list at which this many vectors have been counted. `0` uses the worst distance seen instead. |
{.fields meta="type default"}
