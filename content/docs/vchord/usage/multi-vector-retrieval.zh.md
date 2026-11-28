---
title: "多向量检索"
linkTitle: "多向量"
description: "为 ColBERT、ColPali 类模型输出的词元或图块嵌入数组建索引，并用 @# 运算符按 MaxSim 给文档排序。"
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

每个文档只有一个嵌入时，所有细节都得塞进一个向量里，细粒度的匹配就丢了。ColBERT（文本）、ColQwen2（页面图像）这类后期交互模型改为每个词元或图块保留一个向量，并用 **MaxSim** 给文档打分：对每个查询向量，找出它在文档向量中的最佳匹配，再把这些最佳匹配加起来。

\[
\operatorname{MaxSim}(Q, D) = \sum_{i} \max_{j} \; q_i \cdot d_j
\]

vchordrq 可以直接为这样的数组建索引。`@#` 运算符返回 MaxSim 的相反数，这样和其他距离运算符一样，`ORDER BY ... LIMIT` 会把最好的文档排在前面。完整的流水线见 [ColBERT 重排](/zh/docs/vchord/use-case/colbert-rerank/)和 [ColQwen2 视觉 RAG](/zh/docs/vchord/use-case/colqwen2-modal/)。

## 建索引与查询 {#how-to-start}

把每个文档的向量存成数组，用 `*_maxsim_ops` 运算符类建索引，查询时把查询的向量也作为数组传入：

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

每个数组中的每个向量都会被单独索引，所以 `lists` 要按向量总数而不是行数来定：100 万段、每段约 100 个词元的文本就是 1 亿个向量。`halfvec`、`rabitq8`、`rabitq4` 的数组分别用 `halfvec_maxsim_ops`、`rabitq8_maxsim_ops`、`rabitq4_maxsim_ops`。把词元向量存成 [`rabitq8`](/zh/docs/vchord/usage/quantization-types/)，表的大小能降到 `vector` 的四分之一。

## 查询如何打分 {#scoring}

对每个查询向量，vchordrq 各自探查一组列表、收集最近的文档向量，再把每个文档的最佳匹配加起来。如果某个文档的向量没有在某个查询向量的结果里出现（因为它们位于没被探查的列表中），这一项就用估计值代替：该查询向量见过的最差距离，或者由 `maxsim_threshold` 给出的上界。

默认情况下，距离来自 RaBitQ 估算，不做重排。有两个设置可以用速度换精度：

- `vchordrq.probes` 决定每个查询向量读取多少个列表，与单向量相同，先调它。
- `vchordrq.maxsim_refine` 为排名靠前的文档重新计算精确距离。`0` 只用估算值；`1024` 之类的值能提高召回率，代价更高。

用 [`vchordrq_evaluate_query_recall`](/zh/docs/vchord/usage/measure-recall/) 测量召回率时要加 `exact_search => true`，默认的估算模式不支持 `@#`。

## 限制 {#limits}

MaxSim 索引只能用 vchordrq，不支持 `rerank_in_table`、过滤键和 `vchordrq.max_scan_tuples`。

## 参考 {#reference}

### 运算符类 {#operator-classes}

| 列类型 | 运算符类 | 运算符 |
| --- | --- | --- |
| `vector[]` | `vector_maxsim_ops` | `@#` |
| `halfvec[]` | `halfvec_maxsim_ops` | `@#` |
| `rabitq8[]` | `rabitq8_maxsim_ops` | `@#` |
| `rabitq4[]` | `rabitq4_maxsim_ops` | `@#` |

### 查询参数 {#search-parameters}

<a id="vchordrq-maxsim-refine"></a><a id="search-parameters-vchordrq-maxsim-refine"></a><a id="vchordrq-maxsim-threshold"></a><a id="search-parameters-vchordrq-maxsim-threshold"></a>

两者都可以[存在索引上](/zh/docs/vchord/usage/fallback-parameters/)。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordrq.maxsim_refine` | integer | `0` | 重新计算精确距离的前若干个文档数。`0` 只用 RaBitQ 估算值。 |
| `vchordrq.maxsim_threshold` | integer | `0` | 大于 `0` 时，以累计向量数达到该值的第一个叶子列表的中心距离，作为查询向量未找到的匹配的距离上界。`0` 则使用见过的最差距离。 |
{.fields meta="type default"}
