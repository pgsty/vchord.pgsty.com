---
title: "多向量检索"
linkTitle: "多向量检索"
description: "多向量检索（Multi-Vector Retrieval）是检索增强生成（RAG）系统中的一项高级技术，通过为每个文档使用多个向量来增强文档检索能力。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/multi-vector-retrieval.md"
math: true
aliases:
  - "/zh/docs/usage/multi-vector-retrieval/"
  - "/vectorchord/usage/multi-vector-retrieval/"
  - "/docs/vchord/usage/indexing-with-maxsim-operators/"
  - "/vectorchord/usage/indexing-with-maxsim-operators/"
icon: fa-solid fa-cubes
---

{{< badge text="since v0.3.0" tone="info" >}}


多向量检索（Multi-Vector Retrieval）是检索增强生成（RAG）系统中使用的一项高级技术，通过为每个文档关联多个向量来增强文档检索效果。

与单向量检索不同，使用 `MaxSim` 操作符的多向量检索能够捕捉细粒度的语义关系。

关于如何构建端到端的多向量检索应用，请参阅[我们的博客](/zh/blog/post/beyond-text-unlock-ocr-free-rag-in-postgresql-with-modal-and-vectorchord/)了解更多细节。

## 快速上手 {#how-to-start}

晚期交互（Late interaction）模型会将文档和查询分别嵌入为向量数组，并通过名为 `MaxSim` 的操作符计算相似度。`MaxSim` 操作符的定义为 \(\sum_i \max_j q_i \cdot d_j\)，即对于查询向量数组中的每个向量，在文档向量数组中找到最接近的向量，计算它们的点积，最后将所有结果求和。

在 VectorChord 中，该操作符的符号为 `@#`。左操作数是文档向量数组，右操作数是查询向量数组。原始的 `MaxSim` 操作符基于相似度，而 VectorChord 中的操作符则基于距离：VectorChord 的实现通过对相似度得分取反，将其解释为一种距离度量。

要为向量数组构建索引，首先创建一个名为 `items` 的表，其中包含一个类型为 `vector(n)[]` 的 `embeddings` 列，然后向表中填充生成的数据。

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embeddings vector(3)[]);

INSERT INTO items (embeddings) 
SELECT
    ARRAY[
        ARRAY[random(), random(), random()]::vector,
        ARRAY[random(), random(), random()]::vector,
        ARRAY[random(), random(), random()]::vector
    ]
FROM generate_series(1, 1000);
```

与其他向量操作符一样，使用 `MaxSim` 操作符的查询也可以通过索引进行加速。

```sql
CREATE INDEX ON items USING vchordrq (embeddings vector_maxsim_ops);
```

随后，您便可以使用该索引执行向量搜索。

```sql
SELECT * FROM items
ORDER BY embeddings @# 
    ARRAY[
        '[3,1,2]'::vector,
        '[2,2,2]'::vector
    ] LIMIT 5;
```

<a id="Reference"></a>
## 参考 {#reference}

`vchordg` 不支持此功能。

### 操作符类 {#operator-classes}

请参阅：

* [操作符类（`vchordrq`）](/zh/docs/vchord/usage/indexing/#operator-classes)。

<a id="search-parameters"></a>
### 搜索参数（`vchordrq`） {#search-parameters}

{{< badge text="vchordrq" tone="neutral" >}}

`MaxSim` 操作符的索引机制与其他向量操作符类似。当在向量数组列上构建索引时，数组中的每个向量都会被单独插入到索引数据结构中。在查询期间，索引会对查询数组中的每个向量分别执行一次独立的向量搜索。默认情况下，索引不会对结果进行重排序（rerank），而是使用 RaBitQ 的估算距离代替实际距离。随后，索引会将所有独立向量搜索的结果进行合并，以生成最终输出。

MaxSim 索引还使用了以下几个额外参数：

<a id="vchordrq-maxsim-refine"></a>
#### `vchordrq.maxsim_refine` {#search-parameters-vchordrq-maxsim-refine}

{{< badge text="since v0.3.0" tone="info" >}}

- 说明：GUC 参数 `vchordrq.maxsim_refine` 会让索引对结果进行重排序，用实际距离替换 RaBitQ 的估算距离，直到前 k 个（top-k）最近向量的距离全部重新计算完毕。
- 类型：整数（integer）
- 取值范围：`[0, 2147483647]`
- 默认值：
    - `0`
    - 该参数支持[回退参数（fallback）](/zh/docs/vchord/usage/fallback-parameters/)。
- 示例：
    - `SET vchordrq.maxsim_refine = 0` 表示索引始终使用 RaBitQ 的估算距离。
    - `SET vchordrq.maxsim_refine = 1024` 表示索引会对结果进行重排序，用实际距离替换 RaBitQ 的估算距离，直到前 1024 个最近向量的距离全部重新计算完毕。

<a id="vchordrq-maxsim-threshold"></a>
#### `vchordrq.maxsim_threshold` {#search-parameters-vchordrq-maxsim-threshold}

{{< badge text="since v0.3.0" tone="info" >}}

- 说明：GUC 参数 `vchordrq.maxsim_threshold` 启用对缺失值更激进的估算策略。启用该设置后，索引会在最底层列表中找到累积大小达到或超过 `vchordrq.maxsim_threshold` 的第一个聚类（cluster），并使用其与查询向量的距离来估算缺失值。
- 类型：整数（integer）
- 取值范围：`[0, 2147483647]`
- 默认值：
    - `0`
    - 该参数支持[回退参数（fallback）](/zh/docs/vchord/usage/fallback-parameters/)。
- 示例：
    - `SET vchordrq.maxsim_threshold = 0` 表示不启用更激进的估算策略。
    - `SET vchordrq.maxsim_threshold = 1024` 表示索引会在最底层列表中找到累积大小达到或超过 `1024` 的第一个聚类，并使用其与查询向量的距离来估算缺失值。
