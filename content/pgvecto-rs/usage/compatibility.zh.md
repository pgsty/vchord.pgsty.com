---
title: "`pgvector` 兼容性"
linkTitle: "兼容性"
description: "pgvecto.rs 对 pgvector 的原生兼容性与兼容模式配置。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/usage/compatibility.md"
aliases:
  - "/usage/compatibility/"
---

`pgvecto.rs` 在以下方面原生兼容 `pgvector`：
* `CREATE TABLE` 命令，例如 `CREATE TABLE t (val vector(3))`
* `INSERT INTO` 命令，例如 `INSERT INTO t (val) VALUES ('[0.6,0.6,0.6]')`

`pgvecto.rs` 还可以通过配置兼容 `pgvector` 的以下语法：
* 索引选项，允许通过 `USING hnsw (val vector_ip_ops)` 创建索引
* 查询选项，支持通过 `SET ivfflat.probes = 10` 设置参数

该特性称为 `pgvector` 兼容模式，可通过 `SET vectors.pgvector_compatibility = on` 启用。

## 索引选项与查询选项 {#index-options--query-options}

对于 `ivfflat` 和 `hnsw` 索引，仅支持以下选项：

* 索引选项的默认值**与 `pgvecto.rs` 原生默认值不同**，而是与 `pgvector` 保持一致。
* 查询选项的默认值则与 `pgvecto.rs` 保持一致。

`ivfflat` 的索引选项：

| 键名  | 类型    | 取值范围         | 默认值 | 说明                     |
| ----- | ------- | ---------------- | ------ | ------------------------ |
| nlist | integer | `[1, 1_000_000]` | `100`  | 聚类单元（列表）的数量。 |

`ivfflat` 的查询选项：

| 选项           | 类型    | 取值范围         | 默认值 | 说明               |
| -------------- | ------- | ---------------- | ------ | ------------------ |
| ivfflat.probes | integer | `[1, 1_000_000]` | `10`   | 扫描的列表数量。   |

> [!WARNING]
> `ivfflat.probes` 的默认值为 `10`，而非 `pgvector` 中的 `1`。


`hnsw` 的索引选项：

| 键名            | 类型    | 取值范围     | 默认值 | 说明                 |
| --------------- | ------- | ------------ | ------ | -------------------- |
| m               | integer | `[4, 128]`   | `16`   | 节点的最大出度。     |
| ef_construction | integer | `[10, 2000]` | `64`   | 构建索引时的搜索范围。 |

`hnsw` 的查询选项：

| 选项           | 类型    | 取值范围     | 默认值 | 说明               |
| -------------- | ------- | ------------ | ------ | ------------------ |
| hnsw.ef_search | integer | `[1, 65535]` | `100`  | HNSW 的搜索范围。  |

> [!WARNING]
> `hnsw.ef_search` 的默认值为 `100`，而非 `pgvector` 中的 `40`。


<a id="Examples"></a>
## 示例 {#examples}

启用 `pgvector` 兼容模式并开始向量查询非常简单：
```sql
DROP TABLE IF EXISTS t;
SET vectors.pgvector_compatibility=on;
SET hnsw.ef_search=40;
CREATE TABLE t (val vector(3));
INSERT INTO t (val) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
CREATE INDEX hnsw_cos_index ON t USING hnsw (val vector_cosine_ops);
SELECT COUNT(1) FROM (SELECT 1 FROM t ORDER BY val <-> '[0.5,0.5,0.5]' limit 100) t2;
DROP INDEX hnsw_cos_index;
```

支持创建多种类型的索引：
```sql
SET vectors.pgvector_compatibility=on;
SET hnsw.ef_search=40;
-- 使用默认选项的 [hnsw + vector_l2_ops] 索引
CREATE INDEX hnsw_l2_index ON t USING hnsw (val vector_l2_ops);
-- 指定单个 ef_construction 选项的 [hnsw + vector_cosine_ops] 索引
CREATE INDEX hnsw_cosine_index ON t USING hnsw (val vector_cosine_ops) WITH (ef_construction = 80);
-- 指定全部选项的匿名 [hnsw + vector_ip_ops] 索引
CREATE INDEX ON t USING hnsw (val vector_ip_ops) WITH (ef_construction = 80, m = 12);
SET ivfflat.probes=1;
-- 使用默认选项的 [ivfflat + vector_l2_ops] 索引
CREATE INDEX ivfflat_l2_index ON t USING ivfflat (val vector_l2_ops);
-- 指定全部选项的 [ivfflat + vector_ip_ops] 索引
CREATE INDEX ivfflat_ip_index ON t USING ivfflat (val vector_cosine_ops) WITH (nlist = 80);
-- 指定全部选项的匿名 [ivf + vector_ip_ops] 索引
CREATE INDEX ON t USING ivfflat (val vector_ip_ops) WITH (lists = 80)
```
