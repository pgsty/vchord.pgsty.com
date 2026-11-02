---
title: "Querying & Filtering"
linkTitle: "Querying & Filtering"
description: "Nearest-neighbor operators, distance calculations, aggregates, WHERE filtering with iterative index scans, and hybrid search in pgvector."
weight: 20
upstream_link: https://github.com/pgvector/pgvector#querying
math: true
---

## Distance Operators

`pgvector` supports six distance operators for ordering (`ORDER BY`) and threshold filtering:

| Operator | Metric | Supported Types | Notes |
| :---: | :--- | :--- | :--- |
| `<->` | **L2 (Euclidean) distance** | `vector`, `halfvec`, `sparsevec` | \(\sqrt{\sum (a_i - b_i)^2}\) |
| `<#>` | **Negative inner product** | `vector`, `halfvec`, `sparsevec` | Returns \(-\sum a_i b_i\) because PostgreSQL index scans only support `ASC` order |
| `<=>` | **Cosine distance** | `vector`, `halfvec`, `sparsevec` | \(1 - \frac{a \cdot b}{\|a\|\|b\|}\) (range `[0, 2]`) |
| `<+>` | **L1 (Taxicab / Manhattan) distance** | `vector`, `halfvec`, `sparsevec` | \(\sum |a_i - b_i|\) (added in `0.7.0`) |
| `<~>` | **Hamming distance** | `bit` | Number of differing bits (`XOR` popcount) |
| `<%>` | **Jaccard distance** | `bit` | \(1 - \frac{|A \cap B|}{|A \cup B|}\) |

> [!TIP] Normalized Vectors
> If your vectors are already normalized to unit length (such as OpenAI `text-embedding-3-*` or BGE embeddings), prefer inner product (`<#>`) over cosine distance (`<=>`) for the best CPU throughput.

### Nearest-Neighbor Queries

```sql
-- Top 5 nearest neighbors by L2 distance
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;

-- Top 5 nearest neighbors by cosine distance
SELECT * FROM items ORDER BY embedding <=> '[3,1,2]' LIMIT 5;

-- Top 5 nearest neighbors by maximum inner product
SELECT * FROM items ORDER BY embedding <#> '[3,1,2]' LIMIT 5;
```

---

## Calculating Distances & Similarity Scores

Retrieve the distance alongside each row:

```sql
-- L2 distance
SELECT id, embedding <-> '[3,1,2]' AS distance FROM items;

-- Actual inner product (multiply negative inner product by -1)
SELECT id, (embedding <#> '[3,1,2]') * -1 AS inner_product FROM items;

-- Cosine similarity (1 - cosine distance)
SELECT id, 1 - (embedding <=> '[3,1,2]') AS cosine_similarity FROM items;
```

### Distance Threshold Queries

Get all rows within a given distance threshold:

```sql
SELECT * FROM items WHERE embedding <-> '[3,1,2]' < 5;
```

Combine with `ORDER BY` and `LIMIT` to use an HNSW or IVFFlat index:

```sql
SELECT * FROM items
WHERE embedding <-> '[3,1,2]' < 5
ORDER BY embedding <-> '[3,1,2]'
LIMIT 5;
```

> [!NOTE] Native Range / Sphere Queries in `vchord`
> If you frequently query by distance radius, [`vchord`](/docs/vchord/) provides a dedicated `<<->>` sphere operator (`WHERE embedding <<->> sphere('[3,1,2]'::vector, 5)`) that evaluates range predicates directly inside the `vchordrq` or `vchordg` index without requiring `ORDER BY ... LIMIT`. See [Similarity Filter in `vchord`](/docs/vchord/usage/similarity-filter/).

---

## Aggregates

Compute the mean (`AVG`) or component-wise sum (`SUM`) of vectors:

```sql
SELECT AVG(embedding) FROM items;

SELECT category_id, AVG(embedding) AS centroid
FROM items
GROUP BY category_id;
```

---

## Filtering (`WHERE` Clauses) & Iterative Index Scans

Combine vector search with relational predicates:

```sql
SELECT * FROM items WHERE category_id = 123 ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

### Indexing Filter Columns

1. **Standard B-tree index** on the filter column (good when `category_id = 123` matches a very small fraction of rows):
   ```sql
   CREATE INDEX ON items (category_id);
   ```
2. **Partial vector index** (ideal when you only filter by a few known values):
   ```sql
   CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WHERE (category_id = 123);
   ```
3. **Partitioning** (ideal when filtering across a bounded set of high-volume tenants or time ranges):
   ```sql
   CREATE TABLE items (embedding vector(3), category_id int) PARTITION BY LIST(category_id);
   ```

### Iterative Index Scans (`pgvector 0.8.0+`)

By default, approximate vector index scans examine a fixed number of candidates (`hnsw.ef_search` or `ivfflat.probes`). If a `WHERE` filter rejects most of those candidates, the query may return fewer rows than `LIMIT`.

Starting in `pgvector 0.8.0`, enable **iterative index scans** so the index automatically continues scanning until enough matching rows are found (or `max_scan_tuples` / `max_probes` is reached):

```sql
-- HNSW iterative scan
SET hnsw.iterative_scan = relaxed_order;
-- Or strict_order to guarantee exact distance ordering across iterations:
-- SET hnsw.iterative_scan = strict_order;

-- IVFFlat iterative scan
SET ivfflat.iterative_scan = relaxed_order;
```

When using `relaxed_order`, results may be slightly out of order by distance; wrap the query in a CTE or subquery to re-sort the final `LIMIT` rows:

```sql
WITH relaxed_results AS MATERIALIZED (
    SELECT id, embedding <-> '[3,1,2]' AS distance
    FROM items
    WHERE category_id = 123
    ORDER BY distance
    LIMIT 5
)
SELECT * FROM relaxed_results ORDER BY distance + 0;
```

#### Controlling Iterative Scan Budgets

```sql
-- Maximum tuples HNSW will visit during an iterative scan (default: 20000)
SET hnsw.max_scan_tuples = 20000;

-- Maximum memory multiplier (multiple of work_mem) HNSW uses for visited state (default: 1)
SET hnsw.scan_mem_multiplier = 2;

-- Maximum probes IVFFlat will visit during an iterative scan
SET ivfflat.max_probes = 100;
```

---

## Hybrid Search

You can combine `pgvector` semantic similarity search with lexical full-text search using **Reciprocal Rank Fusion (RRF)**.

### Hybrid Search with PostgreSQL `tsvector`

```sql
SELECT id, content FROM (
    SELECT id, content, 1.0 / (60 + RANK() OVER (ORDER BY embedding <=> '[3,1,2]')) AS score
    FROM items
    ORDER BY embedding <=> '[3,1,2]' LIMIT 20
    UNION ALL
    SELECT id, content, 1.0 / (60 + RANK() OVER (ORDER BY ts_rank_cd(textsearch, query) DESC)) AS score
    FROM items, plainto_tsquery('english', 'hello search') query
    WHERE textsearch @@ query
    ORDER BY ts_rank_cd(textsearch, query) DESC LIMIT 20
) searches
GROUP BY id, content
ORDER BY SUM(score) DESC
LIMIT 5;
```

### Hybrid Search with `vchord_bm25` or `pg_bestmatch`

For true Okapi BM25 ranking with document-length normalization and corpus IDF:
- Pair `pgvector` (or [`vchord`](/docs/vchord/)) with [`vchord_bm25`](/docs/bm25/) and [`pg_tokenizer`](/docs/tokenizer/) — see the [Hybrid Search Guide](/docs/bm25/usage/hybrid-search/).
- Or generate BM25-weighted `sparsevec` vectors directly inside PostgreSQL using [`pg_bestmatch`](/docs/bestmatch/) and index them with `pgvector` HNSW (`sparsevec_ip_ops`).
