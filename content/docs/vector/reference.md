---
title: "Reference, Tuning & FAQ"
linkTitle: "Reference, Tuning & FAQ"
description: "Complete SQL function reference, GUC configuration parameters, performance tuning, monitoring, and FAQ for pgvector."
weight: 50
icon: fa-solid fa-book-open
upstream_link: https://github.com/pgvector/pgvector#reference
math: true
---

## SQL Function Reference

### Vector Functions

| Function | Return Type | Description |
| :--- | :--- | :--- |
| `l2_distance(a, b)` | `float8` | Euclidean (L2) distance between `a` and `b` (`vector`, `halfvec`, `sparsevec`) |
| `inner_product(a, b)` | `float8` | Inner (dot) product \(\sum a_i b_i\) (`vector`, `halfvec`, `sparsevec`) |
| `cosine_distance(a, b)` | `float8` | Cosine distance \(1 - \frac{a \cdot b}{\lVert a \rVert \lVert b \rVert}\) (`vector`, `halfvec`, `sparsevec`) |
| `l1_distance(a, b)` | `float8` | Manhattan (L1) distance \(\sum \lvert a_i - b_i \rvert\) (`vector`, `halfvec`, `sparsevec`) |
| `hamming_distance(a, b)` | `float8` | Hamming distance between two `bit` vectors |
| `jaccard_distance(a, b)` | `float8` | Jaccard distance between two `bit` vectors |
| `vector_dims(a)` | `integer` | Number of dimensions in `a` (`vector`, `halfvec`, `sparsevec`) |
| `vector_norm(a)` | `float8` | Euclidean norm \(\lVert a \rVert_2\) (`vector`, `halfvec`, `sparsevec`) |
| `l2_normalize(a)` | same as input | Normalize vector `a` to unit L2 length (`vector`, `halfvec`, `sparsevec`) |
| `binary_quantize(a)` | `bit` | Quantize each element of `vector` or `halfvec` to `1` (\(> 0\)) or `0` (\(\le 0\)) |
| `subvector(a, start, count)` | same as input | Extract `count` dimensions starting at 1-based index `start` (`vector`, `halfvec`) |
{.wide .expand}

### Element-Wise Arithmetic Operators

- `a + b`: Element-wise addition (`vector`, `halfvec`)
- `a - b`: Element-wise subtraction (`vector`, `halfvec`)
- `a * b`: Element-wise multiplication (`vector`, `halfvec`)
- `a || b`: Vector concatenation (`vector`, `halfvec`)

---

## GUC Parameters

| Parameter | Type / Allowed Values | Default | Description |
| :--- | :--- | :---: | :--- |
| `hnsw.ef_search` | `integer` (`1`–`1000`) | `40` | Size of the dynamic candidate list during HNSW search |
| `hnsw.iterative_scan` | `off`, `relaxed_order`, `strict_order` | `off` | Automatically scan more HNSW tuples when `WHERE` filters reduce results below `LIMIT` |
| `hnsw.max_scan_tuples` | `integer` | `20000` | Maximum tuples visited during an HNSW iterative scan |
| `hnsw.scan_mem_multiplier` | `real` | `1` | Multiple of `work_mem` used for HNSW iterative scan state |
| `ivfflat.probes` | `integer` (`1`–`lists`) | `1` | Number of inverted lists probed during an IVFFlat query |
| `ivfflat.iterative_scan` | `off`, `relaxed_order` | `off` | Automatically probe additional IVFFlat lists when `WHERE` filters reduce results below `LIMIT` |
| `ivfflat.max_probes` | `integer` | `32768` | Maximum lists probed during an IVFFlat iterative scan |
{.wide .expand}

---

## Performance Tuning & Monitoring

### 1. Check Index Size

```sql
SELECT pg_size_pretty(pg_relation_size('items_embedding_idx'));
```

### 2. Inspect Query Execution Plans

Use `EXPLAIN ANALYZE` to confirm whether an index scan is chosen and measure execution latency:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

### 3. Monitor Slow Queries with `pg_stat_statements`

```sql
SELECT
    calls,
    round((total_plan_time + total_exec_time) / calls) AS avg_time_ms,
    round((total_plan_time + total_exec_time) / 60000) AS total_time_min,
    query
FROM pg_stat_statements
ORDER BY total_plan_time + total_exec_time DESC
LIMIT 20;
```

### 4. Measure Recall

Compare approximate index results against exact sequential scan results inside a transaction:

```sql
BEGIN;
SET LOCAL enable_indexscan = off;
-- Run exact query here to collect ground-truth IDs
COMMIT;
```

---

## Frequently Asked Questions (FAQ)

### Why isn't my query using the vector index?

1. **Missing `ORDER BY ... LIMIT`**: Index scans require both an `ORDER BY <operator>` and a `LIMIT` clause.
2. **Mismatched operator class**: The query operator must match the index operator class (`<->` requires `vector_l2_ops`, `<#>` requires `vector_ip_ops`, `<=>` requires `vector_cosine_ops`).
3. **Small table cost estimation**: On small tables, PostgreSQL's planner may correctly determine that a sequential scan is cheaper than an index scan. To force index usage during testing, run `SET LOCAL enable_seqscan = off;`.

### How do I index vectors with more than 2,000 dimensions?

`pgvector` HNSW and IVFFlat indexes cap `vector` columns at 2,000 dimensions because PostgreSQL index tuples cannot exceed 8 KB page limits. You have three options:
1. **Install [`vchord`](/docs/vchord/)**: [`vchord`](/docs/vchord/)'s `vchordrq` index supports up to **60,000 dimensions** directly on `vector` and `halfvec` columns.
2. **Half-precision expression indexing**: Cast to `halfvec` (`(embedding::halfvec(3072)) halfvec_l2_ops`) to index up to **4,000 dimensions**.
3. **Binary quantization**: Use `(binary_quantize(embedding)::bit(N)) bit_hamming_ops` to index up to **64,000 dimensions**.

### Can I store vectors with different dimensions in the same column?

Yes, declare the column without a dimension modifier (`embedding vector`), though you can only create an index on rows that share the same dimension via a partial expression index:

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector);
CREATE INDEX ON items USING hnsw ((embedding::vector(3)) vector_l2_ops) WHERE (vector_dims(embedding) = 3);
```

### Do vectors contain `NULL` or `NaN` / `Infinity`?

Vectors cannot contain `NULL`, `NaN`, or `Infinity` elements. A whole column value can be `NULL`; note that `NULL` vectors are not indexed in IVFFlat and are sorted last by default unless `NULLS FIRST` is specified.
