---
title: "HNSW & IVFFlat Indexing"
linkTitle: "HNSW & IVFFlat Indexing"
description: "Build, tune, and maintain HNSW and IVFFlat approximate nearest-neighbor indexes in pgvector, and compare with vchord."
weight: 30
icon: fa-solid fa-sitemap
upstream_link: https://github.com/pgvector/pgvector#indexing
math: true
---

By default, `pgvector` performs exact nearest-neighbor search (sequential scan), which delivers 100% recall. When your dataset grows beyond tens of thousands of rows, add an approximate nearest-neighbor (ANN) index to trade a small amount of recall for orders-of-magnitude higher query speed.

`pgvector` includes two built-in index access methods:
- **HNSW** (Hierarchical Navigable Small World): Multi-layer proximity graph. Higher recall-speed trade-off and no training step required, at the cost of slower build times and higher memory usage.
- **IVFFlat** (Inverted File with Flat Vectors): K-means clustering over vectors. Faster index builds and smaller index footprint, but requires data to exist before index creation and delivers lower recall per probe than HNSW.

> [!IMPORTANT] Scaling Beyond HNSW & IVFFlat
> When datasets exceed available RAM (e.g., 10M–1B+ vectors) or HNSW index build times become a bottleneck, install [`vchord`](/docs/vchord/) alongside `pgvector`. [`vchord`](/docs/vchord/)'s `vchordrq` and `vchordg` index access methods work directly on `pgvector`'s `vector` and `halfvec` columns, compressing vectors with RaBitQ to build up to **100x faster** and run efficiently from disk/SSD.

---

## HNSW Indexes

An HNSW index constructs a multilayer navigation graph. Unlike IVFFlat, it has no training phase, so you can create an HNSW index on an empty table before loading data.

### Creating an HNSW Index

Create an index matching the distance operator used in your queries:

```sql
-- L2 distance (<->)
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

-- Inner product (<#>)
CREATE INDEX ON items USING hnsw (embedding vector_ip_ops);

-- Cosine distance (<=>)
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- L1 distance (<+>)
CREATE INDEX ON items USING hnsw (embedding vector_l1_ops);

-- Hamming distance (<~>) on bit columns
CREATE INDEX ON items USING hnsw (embedding bit_hamming_ops);

-- Jaccard distance (<%>) on bit columns
CREATE INDEX ON items USING hnsw (embedding bit_jaccard_ops);
```

Supported dimensionality limits for HNSW:
- `vector`: up to **2,000** dimensions
- `halfvec`: up to **4,000** dimensions
- `bit`: up to **64,000** dimensions
- `sparsevec`: up to **1,000** non-zero elements

### HNSW Build Parameters

- `m` (default `16`, range `2`–`100`): Maximum number of bidirectional links per node per layer. Higher `m` improves recall on high-intrinsic-dimensionality datasets at the cost of larger index size and longer build times.
- `ef_construction` (default `64`, range `4`–`1000`): Size of the dynamic candidate list during graph construction. Must be \(\ge 2 \times m\).

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);
```

### HNSW Query Options

Specify the size of the dynamic candidate list during search (`hnsw.ef_search`, default `40`, range `1`–`1000`). Higher values increase recall at the cost of latency:

```sql
SET hnsw.ef_search = 100;

-- Or scope to a single transaction:
BEGIN;
SET LOCAL hnsw.ef_search = 100;
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
COMMIT;
```

### Accelerating HNSW Index Builds

HNSW construction speed drops sharply once the graph no longer fits into `maintenance_work_mem`. Before building an HNSW index on a large table, increase `maintenance_work_mem` and `max_parallel_maintenance_workers`:

```sql
SET maintenance_work_mem = '8GB';
SET max_parallel_maintenance_workers = 7; -- plus leader = 8 total workers
```

> [!NOTE]
> Always create HNSW indexes **after** bulk-loading initial data with `COPY` for significantly faster ingestion. In production, use `CREATE INDEX CONCURRENTLY` to avoid blocking writes.

---

## IVFFlat Indexes

An IVFFlat index partitions vectors into `lists` Voronoi cells using k-means clustering, and at query time inspects the closest `ivfflat.probes` lists.

> [!WARNING] Create IVFFlat After Loading Data
> Because IVFFlat computes k-means centroids during `CREATE INDEX`, you **must** load representative data into the table before creating the index.

### Creating an IVFFlat Index

Choose `lists` based on table size:
- Up to 1 million rows: `rows / 1000`
- Over 1 million rows: `sqrt(rows)`

```sql
-- L2 distance (<->)
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Inner product (<#>)
CREATE INDEX ON items USING ivfflat (embedding vector_ip_ops) WITH (lists = 100);

-- Cosine distance (<=>)
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Hamming distance (<~>) on bit columns
CREATE INDEX ON items USING ivfflat (embedding bit_hamming_ops) WITH (lists = 100);
```

Supported dimensionality limits for IVFFlat:
- `vector`: up to **2,000** dimensions
- `halfvec`: up to **4,000** dimensions
- `bit`: up to **64,000** dimensions

### IVFFlat Query Options

Set the number of lists probed per query (`ivfflat.probes`, default `1`). A good starting point is `sqrt(lists)`:

```sql
BEGIN;
SET LOCAL ivfflat.probes = 10;
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
COMMIT;
```

---

## Index Build Progress & Maintenance

### Monitoring Index Build Progress

Query `pg_stat_progress_create_index` while `CREATE INDEX` is running:

```sql
SELECT
    phase,
    round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "%"
FROM pg_stat_progress_create_index;
```

- **HNSW phases**: `initializing` \(\rightarrow\) `loading tuples`
- **IVFFlat phases**: `initializing` \(\rightarrow\) `performing k-means` \(\rightarrow\) `assigning tuples` \(\rightarrow\) `loading tuples`

### Vacuuming HNSW Indexes

Vacuuming an HNSW index after heavy deletes can be slow because graph links must be repaired. To speed up `DELETE` + `VACUUM` cycles on HNSW tables, rebuild the index concurrently first:

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
VACUUM items;
```
