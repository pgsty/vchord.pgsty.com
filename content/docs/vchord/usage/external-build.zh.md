---
title: "外部构建"
linkTitle: "外部构建"
description: "在 PostgreSQL 之外（例如在 GPU 上）运行 vchordrq 构建中的 k-means 步骤，再用得到的聚类中心构建索引。"
weight: 90
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/external-build.md"
aliases:
  - "/docs/usage/external-build/"
  - "/vectorchord/usage/external-build/"
  - "/docs/vchord/usage/external-index-precomputation/"
  - "/vectorchord/usage/external-index-precomputation/"
icon: fa-solid fa-server
---

构建大型 vchordrq 索引时，k-means 是最慢、最耗内存的一步。外部构建把这一步移出数据库：你在任何地方训练聚类中心（例如用 [Faiss](https://github.com/facebookresearch/faiss) 在 GPU 上），把结果写进一张表，`CREATE INDEX` 只负责把行分配给这些中心。数据库服务器的内存或 CPU 不足以跑 k-means，或者需要经常重建、想复用聚类中心时，就用它。在此之前，先试试[构建大型索引](/zh/docs/vchord/usage/partitioning-tuning/)里的库内选项。

## 流程 {#workflow}

1. 从表中采样向量。每个叶子列表几十个就够了，例如 `lists = [400, 160000]` 取 64 × 160,000 个：

   ```sql
   CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
   SELECT embedding FROM public.items TABLESAMPLE SYSTEM_ROWS(10240000);
   ```

1. 训练聚类中心，并转换成 `(id, parent, vector)` 形式的行。下面的函数用 Faiss 完成这两件事；给 `Kmeans` 传入 `gpu=True` 即可在 GPU 上训练，余弦距离或归一化内积的嵌入传 `spherical=True`。

   ```python
   import numpy as np
   from faiss import Kmeans


   def centroid_rows(samples, lists, spherical=False):
       """Rows (id, parent, vector) for build.external.table.

       `lists` is the index's `lists`, such as [400, 160000]. Each level is trained
       on the centroids of the level below, and each centroid's parent is its
       nearest centroid one level up.
       """
       samples = np.ascontiguousarray(samples, dtype=np.float32)
       levels, data = [], samples
       for k in reversed(lists):
           kmeans = Kmeans(samples.shape[1], k, niter=10, seed=42, spherical=spherical)
           kmeans.train(data)
           data = kmeans.centroids
           levels.append(data)
       levels.append(data.mean(axis=0, keepdims=True))  # the root
       levels.reverse()

       rows, upper, upper_ids, next_id = [], None, None, 0
       for level in levels:
           ids = np.arange(next_id, next_id + len(level))
           next_id += len(level)
           if upper is None:
               parents = [None] * len(level)
           else:
               # squared L2 distance to every centroid one level up, without a 3-D array
               d = (upper * upper).sum(axis=1) - 2 * level @ upper.T
               parents = upper_ids[d.argmin(axis=1)].tolist()
           rows += [(int(i), p, v.tolist()) for i, p, v in zip(ids, parents, level)]
           upper, upper_ids = level, ids
       return rows
   ```

1. 把这些行导入一张恰好有下面三列的表，例如用 `COPY`。向量字面量就是把列表写成文本，如 `[0.1, 0.2, 0.3]`。

   ```sql
   CREATE TABLE public.items_centroids (
       id integer NOT NULL UNIQUE,
       parent integer,
       vector vector NOT NULL
   );
   ```

1. 用这张表构建索引，表名必须带模式名：

   ```sql
   CREATE INDEX ON public.items USING vchordrq (embedding vector_cosine_ops)
   WITH (options = $$
   residual_quantization = true
   [build.external]
   table = 'public.items_centroids'
   $$);
   ```

   查询方式不变，`vchordrq.probes` 按树的层数给值，这里是两个。
{.steps}

## 聚类中心表的规则 {#format}

<a id="Format"></a><a id="schema-qualification"></a><a id="partitioning"></a><a id="Partitioning"></a>

`CREATE INDEX` 以及之后的每次重建都会检查这张表，违反规则就报错终止：

- **列**：`id integer NOT NULL` 且唯一；`parent integer`（只有根节点为 `NULL`）；`vector vector NOT NULL`，维度与被索引列相同。即使被索引的列是 `halfvec`，这里也用 `vector`。
- **形状**：只有一个根，所有节点都能从根到达，所有叶子深度相同，算上根共 2 到 9 层，对应 1 到 8 层的 `lists`。
- **单层**：可以省略根节点，给出至少两个 `parent = NULL` 的聚类中心，vchordrq 会自己补上根。
- **表名**：`table` 必须写成 `schema.table`。构建在受限的 `search_path` 下运行，不带模式名会被拒绝。

每次构建都会读取这张表，包括 `REINDEX`、`VACUUM FULL`、`CLUSTER`、`TRUNCATE` 和恢复备份，所以只要索引还在，就要保留它。
