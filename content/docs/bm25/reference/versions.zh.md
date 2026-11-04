---
math: true
title: "版本历史与 API 演进"
description: "VectorChord-BM25 (vchord_bm25) 从 v0.1.0 到 1.0.0 的版本变更日志与 SQL 模式演进。"
weight: 40
icon: fa-solid fa-clock-rotate-left
---

> [!IMPORTANT]
> **1.0.0** 是 PGSTY 的首个正式版本，使用原生 `tsvector` 和新的索引格式。标注 0.3.x 的 `bm25vector` 示例仅适用于旧版。两者不能原地升级；请先阅读[1.0.0 迁移指南](/zh/docs/bm25/reference/migration/)。

`pg_tokenizer 1.0.0` 是独立发布的分词扩展。它可以与历史 `vchord_bm25 0.3.x` 的 `bm25vector` 工作流配合使用；如果需要自定义分词，也可以在 1.0.0 接口中使用它提供的原生 `tsvector` 辅助函数。原生 `vchord_bm25` 路径不依赖 `pg_tokenizer`。


本页记录 `vchord_bm25`（[`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) / [`supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)）的版本发布历史与 SQL 模式演进。

## 版本演进总览矩阵 {#version-summary-matrix}

| 版本 | 所属模式 | 索引列类型 | 分词方案 | 核心新增特性 |
| :--- | :--- | :--- | :--- | :--- |
| **`1.0.0`** | 扩展所在模式 | `tsvector` | 原生 `to_tsvector`（或自定义） | 基于原生 `tsvector` 完全重写存储与索引引擎；支持外部排序并行构建（`ambuild`）；引入索引级存储参数（`options`、`limit`、`prefilter`）；引入 `bm25.*` GUC 参数；支持 PostgreSQL 18。 |
| **`v0.3.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | 新增 `bm25_page_inspect(regclass, int)` 函数、`to_bm25query(regclass, int[])` 重载，以及 PostgreSQL 18 兼容性支持。 |
| **`v0.2.2`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | 新增 `bm25_catalog.enable_prefilter` GUC 参数，支持带 `WHERE` 子句的精确过滤 Top-K BM25 检索。 |
| **`v0.2.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | 修复增长段（Growing）向封闭段（Sealed）转换以及 VACUUM 清理过程中的若干缺陷。 |
| **`v0.2.0`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | 为 `bm25vector` 新增 `=` 与 `<>` 相等性操作符，以及隐式类型转换 `CREATE CAST (int[] AS bm25vector) AS IMPLICIT`。 |
| **`v0.1.1`** | `bm25_catalog` | `bm25vector` | `pg_tokenizer` | 将分词能力解耦为独立的 `pg_tokenizer` 扩展；调整 `to_bm25query(regclass, bm25vector)` 函数签名。 |
| **`v0.1.0`** | `bm25_catalog` | `bm25vector` | 内置 `unicode` | 首个发布版本，提供 `bm25vector`、`bm25query`、`USING bm25` 及 Block-WeakAnd Top-K 扫描。 |
{.wide .expand}

---

## 各版本升级变更详解 {#detailed-upgrade-changes}

### `v0.3.0`（`sql/vchord_bm25--0.2.2--0.3.0.sql`） {#v030-sqlvchord_bm25--022--030sql}

- 新增页面诊断函数：
  ```sql
  CREATE FUNCTION bm25_page_inspect(index regclass, blkno INT) RETURNS TEXT;
  ```
- 在 `0.3.x` 后期版本中新增了直接接受 `int[]` 的便捷重载 `to_bm25query(regclass, int[])`。

### `v0.2.2`（`sql/vchord_bm25--0.2.1--0.2.2.sql`） {#v022-sqlvchord_bm25--021--022sql}

- 在 Block-WeakAnd 中新增预过滤支持（`bm25_catalog.enable_prefilter` GUC 参数，在 `0.3.0` 中默认启用）。
- 改进索引扫描期间的 MVCC 可见性检查，防止死元组（Dead Tuples）或被过滤元组污染 Top-K 剪枝阈值。

### `v0.2.0`（`sql/vchord_bm25--0.1.1--0.2.0.sql`） {#v020-sqlvchord_bm25--011--020sql}

- 为 `bm25vector` 新增 `=` 与 `<>` 操作符。
- 新增从 `int[]` 到 `bm25vector` 的隐式类型转换（`_vchord_bm25_cast_array_to_bm25vector`），允许将 `tokenize(text, name)` 的输出（`INT[]`）直接赋值给 `bm25vector` 列或传入任何接受 `bm25vector` 的位置。

### `v0.1.1`（`sql/vchord_bm25--0.1.0--0.1.1.sql`） {#v011-sqlvchord_bm25--010--011sql}

- 将原本内置的 `create_tokenizer` / `tokenize` 函数抽离为独立的 `pg_tokenizer` 扩展（`tokenizer_catalog`），从而支持丰富的文本分析器、Snowball 词干提取、停用词、同义词、HuggingFace 模型、`jieba` 中文分词与 `lindera` 日文分词。
- 简化 `to_bm25query(index_oid regclass, query_vector bm25vector)` 签名，直接接受 `bm25vector` 参数。

### 1.0.0：原生 `tsvector` 与 PGSTY 修复 {#next-generation-rewrite-main-branch}

- 用 PostgreSQL 原生 `tsvector` 替代自定义 `bm25vector` 类型（`CREATE OPERATOR CLASS bm25_ops FOR TYPE tsvector USING bm25`），允许用户直接使用 `USING bm25` 为 `to_tsvector(...)` 列建立索引。
- 新增基于外部归并排序（External Merge Sort）的并行索引构建（`bm25_parallel_build_main`）。
- 支持通过 TOML `options` 字符串配置索引级 BM25 超参数（\(k_1 \in [1.2, 2.0]\)，\(b \in [0.0, 1.0]\)）。
- SQL `LIMIT`、`OFFSET` 和后过滤均支持按需续扫；`bm25.limit` 控制首批大小。
- 通过 `VACUUM` 和 `bm25_maintain()` 支持并发段维护，旧快照结束后再回收旧页。
- 完善表/列权限、RLS 检查、模式迁移，以及报错或取消后的扫描资源清理。参阅[迁移与权限](/zh/docs/bm25/reference/migration/)。
