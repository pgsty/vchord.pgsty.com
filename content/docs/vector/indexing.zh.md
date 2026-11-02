---
title: "HNSW 与 IVFFlat 索引"
linkTitle: "HNSW 与 IVFFlat 索引"
description: "在 pgvector 中创建、调优与维护 HNSW 和 IVFFlat 近似最近邻索引，并与 vchord 进行对比。"
weight: 30
upstream_link: https://github.com/pgvector/pgvector#indexing
math: true
---

默认情况下，`pgvector` 执行精确最近邻搜索（全表顺序扫描），具有 100% 的召回率。当表数据量增长至数万行以上时，可以通过创建近似最近邻（ANN）索引，以极小的召回率折中换取几个数量级的查询加速。

`pgvector` 内置了两种索引访问方法：
- **HNSW**（Hierarchical Navigable Small World，分层可导航小世界图）：多层近邻图结构。查询速度与召回率表现显著优于 IVFFlat，且无需预先训练步骤；代价是索引构建时间更长、内存占用更高。
- **IVFFlat**（Inverted File with Flat Vectors，倒排文件索引）：基于 K-means 聚类将向量划分到不同倒排列表。建索引速度更快、体积更小，但必须在表中已有数据的前提下创建，且相同延迟下的召回率低于 HNSW。

> [!IMPORTANT] 突破 HNSW 与 IVFFlat 的规模瓶颈
> 当数据集规模超过可用内存（例如千万级至十亿级向量），或者 HNSW 建索引耗时过长时，建议在 `pgvector` 基础上安装 [`vchord`](/zh/docs/vchord/)。[`vchord`](/zh/docs/vchord/) 提供的 `vchordrq` 与 `vchordg` 索引直接作用于 `pgvector` 的 `vector` 和 `halfvec` 列，通过 RaBitQ 量化压缩实现最高 **100 倍建索引加速**，并支持高效的磁盘/SSD 检索。

---

## HNSW 索引

HNSW 索引构建了一个多层导航图。与 IVFFlat 不同，HNSW 没有聚类训练阶段，因此可以在空表上预先创建索引。

### 创建 HNSW 索引

根据查询语句中使用的距离操作符，选择对应的操作符类（Operator Class）：

```sql
-- L2 欧氏距离 (<->)
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);

-- 内积 (<#>)
CREATE INDEX ON items USING hnsw (embedding vector_ip_ops);

-- 余弦距离 (<=>)
CREATE INDEX ON items USING hnsw (embedding vector_cosine_ops);

-- L1 曼哈顿距离 (<+>)
CREATE INDEX ON items USING hnsw (embedding vector_l1_ops);

-- 位向量汉明距离 (<~>)
CREATE INDEX ON items USING hnsw (embedding bit_hamming_ops);

-- 位向量杰卡德距离 (<%>)
CREATE INDEX ON items USING hnsw (embedding bit_jaccard_ops);
```

HNSW 索引支持的最大维度上限：
- `vector`：最高 **2,000** 维
- `halfvec`：最高 **4,000** 维
- `bit`：最高 **64,000** 维
- `sparsevec`：最高 **1,000** 个非零元素

### HNSW 构建参数

- `m`（默认 `16`，范围 `2`–`100`）：每个节点在每层图中的最大双向连接数。提高 `m` 可改善高内在维度数据集上的召回率，但会增加索引体积与构建耗时。
- `ef_construction`（默认 `64`，范围 `4`–`1000`）：建图时的动态候选列表大小，必须满足 \(\ge 2 \times m\)。

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops)
WITH (m = 16, ef_construction = 64);
```

### HNSW 查询参数

通过 `hnsw.ef_search`（默认 `40`，范围 `1`–`1000`）控制查询时的动态候选集大小。增大该值可提升召回率：

```sql
SET hnsw.ef_search = 100;

-- 或通过 SET LOCAL 仅对当前事务生效：
BEGIN;
SET LOCAL hnsw.ef_search = 100;
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
COMMIT;
```

### 加速 HNSW 索引构建

当 HNSW 图结构超出 `maintenance_work_mem` 容量时，建索引速度会急剧下降。在大表上创建 HNSW 索引前，请调大 `maintenance_work_mem` 与并行维护工作进程数：

```sql
SET maintenance_work_mem = '8GB';
SET max_parallel_maintenance_workers = 7; -- 加上 leader 共 8 个并行进程
```

> [!NOTE]
> 建议始终在完成 `COPY` 初始数据批量导入**之后**再创建 HNSW 索引。在生产环境中，请使用 `CREATE INDEX CONCURRENTLY` 以避免阻塞在线写入。

---

## IVFFlat 索引

IVFFlat 索引利用 K-means 聚类将向量空间划分为 `lists` 个倒排分桶，查询时仅扫描距离查询向量最近的 `ivfflat.probes` 个分桶。

> [!WARNING] 务必在导入数据后再创建 IVFFlat 索引
> 由于 IVFFlat 在 `CREATE INDEX` 期间计算 K-means 聚类中心，您**必须**在表中已有代表性数据之后再创建该索引。

### 创建 IVFFlat 索引

根据表的总行数设置 `lists` 参数：
- 100 万行以内：`rows / 1000`
- 超过 100 万行：`sqrt(rows)`

```sql
-- L2 欧氏距离 (<->)
CREATE INDEX ON items USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- 内积 (<#>)
CREATE INDEX ON items USING ivfflat (embedding vector_ip_ops) WITH (lists = 100);

-- 余弦距离 (<=>)
CREATE INDEX ON items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- 位向量汉明距离 (<~>)
CREATE INDEX ON items USING ivfflat (embedding bit_hamming_ops) WITH (lists = 100);
```

IVFFlat 索引支持的最大维度上限：
- `vector`：最高 **2,000** 维
- `halfvec`：最高 **4,000** 维
- `bit`：最高 **64,000** 维

### IVFFlat 查询参数

通过 `ivfflat.probes`（默认 `1`）设置每次查询探测的倒排列表数量，推荐初始值为 `sqrt(lists)`：

```sql
BEGIN;
SET LOCAL ivfflat.probes = 10;
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
COMMIT;
```

---

## 索引构建进度监控与维护

### 监控建索引进度

在 `CREATE INDEX` 执行期间查询 `pg_stat_progress_create_index`：

```sql
SELECT
    phase,
    round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "%"
FROM pg_stat_progress_create_index;
```

- **HNSW 阶段**：`initializing` \(\rightarrow\) `loading tuples`
- **IVFFlat 阶段**：`initializing` \(\rightarrow\) `performing k-means` \(\rightarrow\) `assigning tuples` \(\rightarrow\) `loading tuples`

### HNSW 索引的 VACUUM 维护

在大批量删除数据后，直接对 HNSW 索引执行 `VACUUM` 可能会因为修复图边连接而耗时较长。此时可先并发重建索引，再执行 `VACUUM`：

```sql
REINDEX INDEX CONCURRENTLY items_embedding_idx;
VACUUM items;
```
