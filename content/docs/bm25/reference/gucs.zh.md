---
math: true
title: "GUC 与索引参数"
description: "vchord_bm25 会话级 GUC 参数与索引存储选项的完整参考手册。"
weight: 20
icon: fa-solid fa-sliders
---

> [!IMPORTANT]
> **1.0.0** 是 PGSTY 的首个正式版本，使用原生 `tsvector` 和新的索引格式。标注 0.3.x 的 `bm25vector` 示例仅适用于旧版。两者不能原地升级；请先阅读[1.0.0 迁移指南](/zh/docs/bm25/reference/migration/)。


## 历史版本（`v0.1.0` – `v0.3.0`）：`bm25_catalog.*` GUC 参数 {#stable-releases-v010--v030-bm25_catalog-gucs}

在 `v0.1.0` 至 `v0.3.0` 版本中，所有会话级 GUC 参数均使用 `bm25_catalog.` 前缀，任何普通用户均可在会话或事务级别修改（`GucContext::Userset`）：

| 参数名称 | 类型 | 默认值 | 有效范围 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `bm25_catalog.bm25_limit` | `integer` | `100` | `-1` .. `65535` | 单次 `bm25` 索引扫描返回的高分文档最大数量。设为 `-1` 时禁用 Block-WeakAnd 剪枝并执行全量暴力扫描；设为 `0` 时直接返回空结果。必须 \(\ge\) SQL 查询中的 `LIMIT` 值。 |
| `bm25_catalog.enable_index` | `boolean` | `true` | `true` / `false` | 在 PostgreSQL 查询规划器中启用或禁用 `bm25` 索引扫描。设为 `false` 可强制执行顺序扫描并调用 `search_bm25query` 精确求值。 |
| `bm25_catalog.enable_prefilter` | `boolean` | `true` | `true` / `false` | 自 `v0.2.2` 引入。设为 `true` 时，会在将候选文档推入 Block-WeakAnd Top-K 最小堆之前，先行过滤掉不满足查询过滤条件或 MVCC 可见性检查的文档。 |
| `bm25_catalog.segment_growing_max_page_size` | `integer` | `4096` | `1` .. `1000000` | 仅追加的增长段（Growing Segment）在被封存为差分位打包压缩的只读封闭段（Sealed Segment）之前的最大尺寸（以 8 KB 页面为单位，默认值 `4096` 即 32 MB）。 |
{.wide .expand}

### 配置示例（`v0.1` – `v0.3`） {#examples-v01--v03}

```sql
-- 为深度分页（例如 LIMIT 500）调大 Top-K 候选窗口
SET bm25_catalog.bm25_limit = 500;

-- 强制对索引中的所有倒排项执行全量暴力扫描
SET bm25_catalog.bm25_limit = -1;

-- 为包含高选择性 WHERE 子句的查询启用预过滤
SET bm25_catalog.enable_prefilter = true;

-- 禁用索引扫描，用于对比顺序扫描基线性能
SET bm25_catalog.enable_index = false;
```

---

## 1.0.0：`bm25.*` GUC 参数与索引存储参数 {#next-gen-main-branch-bm25-gucs--index-reloptions}

在 1.0.0 中，会话级 GUC 参数改用 `bm25.` 前缀，并与每个索引独立的存储参数（`WITH (...)`）配合工作：

### 会话级 GUC 参数（1.0.0） {#session-guc-parameters-main}

| 参数名称 | 类型 | 默认值 | 有效范围 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `bm25.enable_scan` | `boolean` | `true` | `true` / `false` | 在查询规划器中启用或禁用 `bm25` 索引扫描。 |
| `bm25.limit` | `integer` | `100` | `0` .. `65535` | 首批扫描大小；零值自动选择 100。显式设置覆盖索引参数。扫描会按 SQL `LIMIT`、`OFFSET` 和后置过滤的需要继续取候选。 |
| `bm25.prefilter` | `boolean` | `false` | `true` / `false` | 在 `bm25` 索引扫描期间启用预过滤（显式设置时覆盖索引自身的 `prefilter` 存储参数，包括 `false`）。 |
{.wide .expand}

`postgresql.conf`、`ALTER DATABASE`、`ALTER ROLE` 或客户端启动选项中的设置也会覆盖索引参数。`RESET` 会恢复这些配置默认值；只有 GUC 来源恢复为内置默认值时，才会回退到索引参数。

### 索引存储参数（1.0.0 中的 `WITH (...)`） {#index-storage-parameters-with--in-main}

| 存储参数 | 类型 | 默认值 | 有效范围 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `options` | `string` (TOML) | `k1 = 1.2`<br>`b = 0.75` | `k1`: `1.2..2.0`<br>`b`: `0.0..1.0` | 用于配置该索引 Okapi BM25 超参数 \(k_1\) 与 \(b\) 的 TOML 字符串。 |
| `limit` | `integer` | `100` | `0` .. `65535` | 当 `bm25.limit` 来源为内置默认值时使用的首批大小。零值选择 100，不限制 SQL 返回行数。 |
| `prefilter` | `boolean` | `false` | `true` / `false` | 索引级的默认预过滤设置。 |
| `maintenance_min_rows` | `integer` | `1000` | `0` .. `2147483647` | 自动合并的最小增长记录数。实际门槛取该值与 `maintenance_scale_factor` × 封闭段记录数中的较大值。 |
| `maintenance_scale_factor` | `real` | `0.1` | `0` .. `1` | VACUUM 合并的增长段/封闭段记录比，或 tombstone/总记录比门槛。旧快照可能延迟回收和下一次合并。 |
{.wide .expand}
