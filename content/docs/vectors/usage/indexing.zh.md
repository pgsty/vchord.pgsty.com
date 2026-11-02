---
title: "索引"
linkTitle: "索引"
description: "索引是构建高效搜索数据结构的过程。pgvecto.rs 支持三种索引算法：暴力搜索（flat）、IVF 和 HNSW。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/usage/indexing.md"
aliases:
  - "/usage/indexing/"
---

索引是构建支持高效搜索的数据结构的过程。`pgvecto.rs` 支持三种索引算法：暴力搜索（flat）、IVF 和 HNSW。默认算法为 HNSW。

要为向量构建索引，首先创建一张名为 `items` 的表，其中包含类型为 `vector(n)` 的 `embedding` 列，然后向表中填充生成的数据。

```sql
CREATE TABLE items (embedding vector(3));
INSERT INTO items (embedding) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
```

> [!TIP]
> `vector` 是适用于绝大多数场景的数据类型。`pgvecto.rs` 还支持其他特定的[向量类型](/zh/docs/vectors/reference/vector-types/)，包括：
> - [半精度向量（Half-Precision Vector）](/zh/docs/vectors/reference/vector-types/vecf16/)
> - [8 位整数向量（8-Bit Integer Vector）](/zh/docs/vectors/reference/vector-types/veci8/) {{< badge text="since v0.3.0" tone="info" >}}
> - [稀疏向量（Sparse Vector）](/zh/docs/vectors/reference/vector-types/svector/) {{< badge text="since v0.3.0" tone="info" >}}
> - [二值向量（Binary Vector）](/zh/docs/vectors/reference/vector-types/bvector/) {{< badge text="since v0.3.0" tone="info" >}}
>


您可以使用以下 SQL 为平方欧氏距离创建向量索引：

```sql
CREATE INDEX ON items USING vectors (embedding vector_l2_ops);
```

`vector_l2_ops` 操作符类用于计算平方欧氏距离。有关操作符类的完整列表，请参阅[参考文档](/zh/docs/vectors/reference/schema/#list-of-operator-classes)。

若要将索引算法从默认的 HNSW 切换为 IVF，请执行以下 SQL 命令。更多使用示例请参阅下文的[示例](#examples)。

```sql
CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
[indexing.ivf]
$$);
```

现在您可以使用以下 SQL 执行 KNN 搜索，利用向量索引加速查询：

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,2,1]' LIMIT 5;
```

> [!DETAILS]
>
> `pgvecto.rs` 采用异步方式构建索引。当您向表中插入新行时，数据会首先写入一个仅追加（append-only）文件中。后台线程会定期将新插入的行合并到现有索引中。当用户在合并完成前执行任何搜索时，系统会同时扫描该仅追加文件，以确保查询结果的准确性和一致性。
>


<a id="Examples"></a>
## 示例 {#examples}

以下是使用不同算法和参数创建索引的示例。有关所有可配置项的完整列表，请参阅[索引选项参考指南](/zh/docs/vectors/reference/indexing_options/)。

```sql
-- HNSW 算法，默认配置。

CREATE INDEX ON items USING vectors (embedding vector_l2_ops);

-- 使用 FP16 向量类型优化数据存储。

CREATE TABLE items (embedding vecf16(3));
CREATE INDEX ON items USING vectors (embedding vecf16_l2_ops)

--- 或者使用结合乘积量化（PQ）的暴力搜索（flat）。

CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
[indexing.flat]
quantization.product.ratio = "x16"
$$);

-- 或者使用结合标量量化（SQ）的索引。
CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = "[indexing.hnsw.quantization.scalar]");

--- 或者使用 IVFPQ 算法。

CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
[indexing.ivf]
quantization.product.ratio = "x16"
$$);

-- 使用更多线程在后台构建索引。

CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
optimizing.optimizing_threads = 16
$$);

-- 倾向于使用更小的 HNSW 图分段。

CREATE INDEX ON items USING vectors (embedding vector_l2_ops)
WITH (options = $$
segment.max_growing_segment_size = 200000
$$);
```

<a id="Suggestions"></a>
## 选择建议 {#suggestions}

选择合适的索引算法与参数对向量搜索性能至关重要。以下是针对不同使用场景的建议。

### 暴力搜索（flat） {#brute-force-flat}
如果您搜索的数据量较小（1,000 到 10,000 条之间）或需要完全精确的结果，[暴力搜索（flat）](/zh/docs/vectors/reference/indexing_options/#options-for-table-flat)算法是一个可行的选择。

该算法是衡量其他索引方法的基准。它以原始形式保留向量而不做压缩，避免了额外的索引开销。虽然简单直观、易于使用，但它不适合处理大规模数据集。

此外，您还可以使用量化来减少内存占用。有关所有选项的完整列表，请参阅[量化选项文档](/zh/docs/vectors/reference/indexing_options/#options-for-table-quantization)。关于量化的详细介绍也可以在[量化指南](/zh/docs/vectors/usage/quantization/)中找到。

### 倒排文件索引（IVF） {#inverted-file-index-ivf}

IVF 主要利用倒排索引的思想，将向量 `(id, vector)` 存储在各自的聚类中心下。查询向量时，它会先找到最近的若干个聚类中心，然后分别搜索这些中心下的向量。

在开始搜索之前，需要先通过 K-Means 聚类训练 `nlist` 个聚类中心，并可选择设置采样点数 `nsample`。较高的值能生成更精确的聚类结果，但需要更长的训练时间。有关更多设置，请参阅[参考指南](/zh/docs/vectors/reference/indexing_options/#options-for-table-ivf)。

### 分层可导航小世界图（HNSW） {#hierarchical-navigable-small-world-graph-hnsw}

HNSW 将[跳表（Skip List）](https://en.wikipedia.org/wiki/Skip_list)与可导航小世界（NSW）图的思想相结合，采用多层图结构：在较高层使用较长的边以实现快速跳转搜索，在较低层使用较短的边以提高搜索精度。

#### 可导航小世界（Navigable small world） {#navigable-small-world}

可导航小世界（NSW）基于这样一个前提：图中的任意节点都可以通过极少数的“跳数（hops）”从其他任何节点到达。选定入口点（无论是随机选择、启发式选择还是算法确定）后，算法会检查周围的邻居节点是否比当前节点更接近查询目标。搜索不断向最近的邻居推进，直到在当前节点的邻接列表中找不到更近的节点为止。

构建图时，参数 `m` 决定了新节点与其最近邻节点建立连接的数量。较高的 `m` 值会产生更稠密、互联程度更高的图，但也会增加内存占用并降低插入速度。在插入节点时，算法会找出最近的 `m` 个节点并与它们建立双向连接。

搜索过程从预定义的入口点开始遍历 NSW 图。算法以贪心方式移动到离查询向量更近的相邻顶点，一旦在当前顶点的邻接列表中找不到更近的邻居，搜索便停止。

NSW 搜索的一个局限在于，它总是选择通往最近节点的表面最短路径，而忽略了图的全局结构。这种“贪心搜索”方法容易陷入局部最优，这一问题通常被称为“早停（early stopping）”。

#### 跳表（Skip list） {#skip-list}

跳表使用概率方法构建：随着层级的升高，节点出现的概率逐渐降低，因此高层中的节点数量更少。搜索节点时，算法从顶层的“头节点”开始，向后移动到大于或等于目标的下一个节点；如果未找到目标节点，则下降到更低（更细粒度）的一层并重复此模式，直到定位到目标节点或其最近邻。


<a id="HNSW"></a>
#### HNSW {#hnsw}

构建这种多层图从包含整个数据集的基础层开始。沿着层级向上，每一层都提供其下一层的精简摘要，包含更少的节点，充当在图内进行大跨度跳跃的“快速通道”。

较小的 [`m`](/zh/docs/vectors/reference/indexing_options/#options-for-table-hnsw) 值更适合低维数据或对召回率要求不高的场景；较大的 `m` 值则适用于高维数据或对高召回率有严格要求的场景。

[`ef_construction`](/zh/docs/vectors/reference/indexing_options/#options-for-table-hnsw) 参数决定了添加新节点时的动态候选列表大小；增大该值可以提高召回率，但会延长索引构建时间。

HNSW 索引属于资源密集型索引，需要额外的内存，并且在处理大型数据集时需要调大 `maintenance_work_mem` 设置。如果您追求显著快于 IVF 的查询性能、高召回率以及随数据集规模良好扩展的能力，HNSW 是极佳的选择。
