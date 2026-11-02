---
title: "搜索"
linkTitle: "搜索"
description: "获取与目标向量最近的 5 个邻居"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/usage/search.md"
aliases:
  - "/usage/search/"
---

获取与目标向量最近的 5 个邻居：
```sql
SET vectors.hnsw_ef_search = 64;
SELECT * FROM items ORDER BY embedding <-> '[3,2,1]' LIMIT 5;
```

<a id="Operators"></a>
## 操作符 {#operators}

以下操作符用于表示不同的距离度量：

| 名称  | 说明                       |
| ----  | -------------------------- |
| <->   | 平方欧氏距离（Squared Euclidean distance） |
| <#>   | 负点积（Negative dot product）             |
| <=>   | 余弦距离（Cosine distance）                |

有关它们的数学定义，请参阅[概览](/zh/docs/vectors/getting-started/overview/#quick-start)。

<a id="Filter"></a>
## 过滤查询 {#filter}

在指定类别下，获取与目标向量最近的 10 个邻居：
```sql
SELECT 1 FROM items WHERE category_id = 1 ORDER BY embedding <#> '[0.5,0.5,0.5]' limit 10
```

## 查询选项 {#query-options}

在当前会话中将 `ivf` 扫描列表数设置为 1：
```sql
SET vectors.ivf_nprobe=1;
```

在当前事务中将 `hnsw` 搜索范围设置为 40：
```sql
SET LOCAL vectors.hnsw_ef_search=40;
```

有关所有可配置项，请参阅[搜索选项](/zh/docs/vectors/reference/search_options/)。

## 搜索模式 {#search-modes}

支持两种搜索模式：`vbase` 和 `basic`。

### `vbase` {#vbase}

作为默认搜索模式，`vbase` 适用于绝大多数场景。

关于其工作原理，请参阅论文 [VBASE: Unifying Online Vector Similarity Search and Relational Queries via Relaxed Monotonicity](https://www.usenix.org/conference/osdi23/presentation/zhang-qianxi)。

### `basic` {#basic}

`basic` 模式在行为上与 `faiss` 等向量算法库保持一致。如果您希望将结果与这些库对齐，该模式会很有帮助。

启用 `basic` 模式时，必须遵守以下限制：
* 在执行更新操作后、进行搜索前，必须先执行 [VACUUM](https://www.postgresql.org/docs/current/sql-vacuum.html)。
* 搜索时不能带有过滤条件（Filter）。
