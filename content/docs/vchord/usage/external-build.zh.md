---
title: "外部构建"
linkTitle: "外部构建"
description: "除了使用分区调优中的方法外，您还可以选择在其他机器或 GPU 上离线运行分区阶段，以缩短索引构建时间并降低内存消耗。"
weight: 150
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/external-build.md"
aliases:
  - "/zh/docs/usage/external-build/"
  - "/vectorchord/usage/external-build/"
  - "/docs/vchord/usage/external-index-precomputation/"
  - "/vectorchord/usage/external-index-precomputation/"
icon: fa-solid fa-server
---

除了使用[分区调优](/zh/docs/vchord/usage/partitioning-tuning/)中的方法（以牺牲一定 QPS 和召回率为代价来缩短构建时间并降低内存消耗）之外，您还可以选择在其他机器或 GPU 上离线运行分区阶段。由于 `vchordg` 没有分区阶段，因此该特性不支持 `vchordg`。

假设表名为 `t`，待建索引的列名为 `val`。

```sql
CREATE TABLE t (val vector(3));
```

具体而言，您需要先对待建索引的列进行采样。

```sql
CREATE EXTENSION IF NOT EXISTS tsm_system_rows;
SELECT val FROM t TABLESAMPLE SYSTEM_ROWS(1000);
```

基于这些样本，您可以将向量空间划分为多个 Voronoi 单元（Voronoi cells）。完成划分后，创建一张表并将分区质心插入其中。

```sql
CREATE TABLE public.t_build (id INTEGER NOT NULL UNIQUE, parent INTEGER, vector vector NOT NULL);
INSERT INTO public.t_build (id, parent, vector) VALUES (0, NULL, '[0.1, 0.2, 0.3]');
INSERT INTO public.t_build (id, parent, vector) VALUES (1, 0, '[0.1, 0.2, 0.3]');
INSERT INTO public.t_build (id, parent, vector) VALUES (2, 0, '[0.4, 0.5, 0.6]');
INSERT INTO public.t_build (id, parent, vector) VALUES (3, 0, '[0.7, 0.8, 0.9]');
```

随后可以使用以下语法创建索引：

```sql
CREATE INDEX ON t USING vchordrq (val vector_l2_ops) WITH (options = $$
build.external.table = 'public.t_build'
$$);
```

1.3.0 要求 `build.external.table` 使用 `schema.table` 格式，例如 `public.t_build`。索引构建使用受限的 `search_path`，未限定 schema 的名称会被拒绝，不会自动假定为 `public`。如果现有索引的配置保存了未限定名称，请在 `REINDEX` 前将其 `options` 更新为限定名称；现有查询不受影响。标识符沿用不带引号的语法，并转换为小写。

<a id="Format"></a>
## 表结构格式 {#format}

存储分区信息的表必须严格遵循以下表结构（Schema）：

- 第一列必须为 `id`，类型为 `integer`，不可为 null（`NOT NULL`），且必须唯一（`UNIQUE`）。
- 第二列必须为 `parent`，类型为 `integer`，允许为 null（根节点为 `NULL`）。
- 第三列必须为 `vector`，类型为 `vector`，不可为 null（`NOT NULL`）。目前尚不支持 `halfvec` 或其他类型。

在逻辑上，这些数据构成一棵树：根节点的 `parent` 为 `NULL`，其他节点的 `parent` 必须指向已有的 `id`。所有节点必须从根可达，所有叶子深度相同；包含根在内的树高为 2–9 层。循环、不可达节点或超出高度限制都会报错。质心维度必须与索引列一致。

也支持不显式提供根节点的单层分区：至少提供两个质心，并将所有 `parent` 设为 `NULL`，构建时会自动生成根节点。

如果上述任何属性未得到满足，系统都会报错。

<a id="Partitioning"></a>
## 分区示例 {#partitioning}

为了帮助您快速上手，下面给出一个使用 [faiss](https://github.com/facebookresearch/faiss) 执行向量空间分区的最小代码示例。

```python
from typing import List
from faiss import Kmeans
import numpy

def partition(
    samples: numpy.ndarray, lists: List[int]
) -> List[numpy.ndarray]:
    dim = samples.shape[1]
    results = []
    for i in range(len(lists) + 1):
        kmeans = Kmeans(
            dim,
            lists[len(lists) - 1 - i] if len(lists) - 1 - i >= 0 else 1,
            gpu=False,
            verbose=True,
            niter=10,
            seed=42,
            spherical=False,
        )
        kmeans.train(samples)
        results.append(kmeans.centroids)
        samples = kmeans.centroids
    return results
```

这段代码会计算出不同层级上所有 Voronoi 单元的生成元（质心）。树中的父子关系可通过计算最短距离来确定，此处省略具体细节。您可以使用任何能够生成多级 Voronoi 单元的算法，例如球面 K-means（spherical K-means）、平衡 K-means（balanced K-means）或 GPU K-means。
