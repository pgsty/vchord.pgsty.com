---
title: "回退参数"
linkTitle: "回退参数"
description: "搜索参数通常通过 GUC 进行配置。VectorChord 还提供了另一种方式，允许将这些参数直接绑定到索引上，作为索引存储参数的一部分保存。"
weight: 80
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/fallback-parameters.md"
aliases:
  - "/zh/docs/usage/fallback-parameters/"
  - "/vectorchord/usage/fallback-parameters/"
icon: fa-solid fa-sliders
---

{{< badge text="since v1.1.0" tone="info" >}}


搜索参数通常通过 GUC 进行配置。VectorChord 还提供了另一种方式，允许将这些参数直接绑定到索引上，而不是绑定到会话（session）或事务（transaction）上。换句话说，您可以将它们作为索引存储参数（storage parameters）的一部分保存下来。

在构建索引时，您可以使用以下语法设置 `probes`：

```sql
CREATE INDEX items_embedding_idx ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
build.internal.lists = [1000]
$$, probes = '10');
```

现在，您无需设置 GUC 即可直接执行搜索：

```sql
--- probes = '10'
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

如果索引已经构建完成，您可以像这样修改 `probes`：

```sql
ALTER INDEX items_embedding_idx SET (probes = '100');
```

您仍然可以通过 GUC 设置搜索参数。当设置了 GUC 时，GUC 的优先级高于索引存储参数。这使您能够在不锁定索引的情况下，在当前会话或事务中临时覆盖这些设置。

```sql
SET vchordrq.probes TO '100';
--- probes = '100'
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

这种语法在以下场景中非常有用：

* 当存在多个索引且需要不同参数时。
* 当您不希望设置 GUC 时。
* 当您希望离线配置搜索参数时。

只要设置了 GUC（哪怕是在系统级别或数据库级别设置的），它都会覆盖索引上的存储参数设置。因此，为了避免难以排查的问题，我们建议仅使用一种方式来设置搜索参数：要么统一通过 GUC 设置，要么统一通过索引存储参数设置。

并非所有参数都支持此功能。有关支持此功能的全部参数，请参阅[参考](#reference)。

<a id="Reference"></a>
## 参考 {#reference}

<a id="index-storage-parameters"></a>
### 索引存储参数（`vchordrq`） {#index-storage-parameters-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

#### `probes` {#probes}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：[`vchordrq.probes`](/zh/docs/vchord/usage/indexing/#search-parameters-vchordrq-probes) 的回退值。
- 类型：整数列表（list of integers）
- 默认值：` `
- 取值范围：每项为 `1..=4294967295`；未分区索引可以使用空列表。

#### `epsilon` {#epsilon}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：[`vchordrq.epsilon`](/zh/docs/vchord/usage/indexing/#search-parameters-vchordrq-epsilon) 的回退值。
- 类型：实数（real）
- 默认值：`1.9`，拟发布的 1.3.0 保持不变。
- 取值范围：`[0.0, 4.0]`

<a id="maxsim-refine"></a>
#### `maxsim_refine` {#maxsim-refine}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：[`vchordrq.maxsim_refine`](/zh/docs/vchord/usage/multi-vector-retrieval/#search-parameters-vchordrq-maxsim-refine) 的回退值。
- 类型：整数（integer）
- 默认值：`0`
- 取值范围：`[0, 2147483647]`

<a id="maxsim-threshold"></a>
#### `maxsim_threshold` {#maxsim-threshold}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：[`vchordrq.maxsim_threshold`](/zh/docs/vchord/usage/multi-vector-retrieval/#search-parameters-vchordrq-maxsim-threshold) 的回退值。
- 类型：整数（integer）
- 默认值：`0`
- 取值范围：`[0, 2147483647]`

<a id="index-storage-parameters"></a>
### 索引存储参数（`vchordg`） {#index-storage-parameters-vchordg}

{{< badge text="vchordg" tone="neutral" >}}

<a id="ef-search"></a>
#### `ef_search` {#ef-search}

{{< badge text="since v1.1.0" tone="info" >}}

- 说明：[`vchordg.ef_search`](/zh/docs/vchord/usage/graph-index/#search-parameters-vchordg-ef-search) 的回退值。
- 类型：整数（integer）
- 默认值：`64`
- 取值范围：`[1, 65535]`
