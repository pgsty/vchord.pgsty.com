---
title: "vchord_bm25 1.2.0：PostgreSQL 19 支持、规划器修复与并行构建加固"
date: 2026-11-23
description: "vchord_bm25 1.2.0 升级至 pgrx 0.20.1 支持 PostgreSQL 15–19，修复规划器 NaN 代价与扫描清理缺陷，保留并行建索引的旧快照可见性保护，并更新 url 至 2.5.9。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.2.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord_bm25"
aliases: [/blog/release/vchord-bm25-1.2.0/]
---

**vchord_bm25 1.2.0** 将 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 升级至 `pgrx 0.20.1` 与 Rust `1.100.0+`，支持 `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19，修复规划器代价估算与扫描异常清理缺陷，补全并行索引构建的旧快照可见性保护，并完全兼容 `1.0.0` / `1.1.0` 的 SQL 接口与第 4 版索引格式。自本版本起不再支持 PostgreSQL 14。

> [!NOTE] 已由 1.3.0 替代的草稿里程碑
> `1.2.0` 标签（`https://github.com/pgsty/vchord_bm25/tree/1.2.0`）在 GitHub 上保持为草稿发布，已由正式发布的 [**vchord_bm25 1.3.0**](/zh/release/vchord-bm25-1.3.0/) 替代；1.3.0 进一步加入批量构建 WAL 优化、面向行级安全的 `shared_corpus_stats`、相关子查询预过滤与选择性 Top-K 计划选择改进。生产部署与预编译包下载请直接使用 [`vchord_bm25 1.3.0`](/zh/release/vchord-bm25-1.3.0/)。

## 1.2.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| PostgreSQL 15–19 与 `pgrx 0.20.1` | 升级至 `pgrx 0.20.1` 与 Rust `1.100.0+`，支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19 并移除 PostgreSQL 14。在 PostgreSQL 17+ 声明 `amcanbuildparallel`；在 PostgreSQL 19 传递 `SO_HINT_REL_READ_ONLY` 并返回静态 `IndexAmRoutine`。 |
| 规划器与扫描安全 | `amcostestimate` 改用有限的不可用路径代价（避免 `f64::INFINITY` 在 PostgreSQL `cost_index()` 中产生 `NaN`），并排除不支持的 `Index Only Scan` 路径。在 `amgettuple` 入口检查查询取消中断；`bm25_maintain` 拒绝无效索引与分区父索引。 |
| 内存清理与统计上报 | 修复预过滤路径在异常展开时的堆槽清理，移除每批次冗余的 `IndexInfo` / `ExecutorState` 分配，并在表达式求值报错时恢复 `CurrentMemoryContext`。扫描描述符改在 `es_query_cxt` 中分配；在 PostgreSQL 15–19 上报 `pg_stat_user_indexes.idx_scan`，在 PostgreSQL 18+ 同时上报 `Index Searches`（`nsearches`）。 |
| 并行构建可见性 | 任意并行构建 worker 遇到断裂 HOT 链时正确向上传播，使快照早于该次构建的并发事务延迟使用新建索引。 |
| 依赖与兼容性 | 锁文件升级 `url` 至 `2.5.9` 以修复安全公告 [`RUSTSEC-2026-0592`](https://rustsec.org/advisories/RUSTSEC-2026-0592.html)。与 `1.0.0` / `1.1.0` 保持 SQL 接口和第 4 版索引磁盘格式原地兼容。 |
{.wide .expand}

## 升级说明 {#upgrade-notes}

1. **PostgreSQL 14 实例**：安装 `1.2.0` 及以上版本前须先将 PostgreSQL 升级至 15–19。
1. **1.x 原地升级**：安装对应版本的动态库与 SQL 文件，重启 PostgreSQL，随后在每个数据库中执行：

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

存量 `1.0.0` 与 `1.1.0` 的第 4 版索引无需 `REINDEX` 即可继续使用。历史 `0.3.x`（`bm25vector`）实例仍需按[从 0.x 迁移](/zh/docs/bm25/reference/migration/#from-0x)重构数据和索引。
