---
title: "vchord_bm25 1.1.0：WAND 剪枝正确性修复与检索加固"
date: 2026-11-08
description: "vchord_bm25 1.1.0 修复近同分场景下 WAND 上界浮点舍入漏行问题，降低缺失词项开销，加固页面回收与 tsvector 边界校验，并保持与 1.0.0 的 SQL 及格式兼容。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-bm25-1.0.0.png"
tags:
  - "vchord_bm25"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0"
upstream_source: ""
upstream_link: ""
aliases: [/blog/release/vchord-bm25-1.1.0/]
---

{{< release-card >}}

**vchord_bm25 1.1.0** 是面向 PostgreSQL 14–18 的 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 正确性修复、查询优化与维护加固版本。本版本修复了 Block-WeakAnd（WAND）剪枝中因浮点加法顺序不同而在近同分阈值处漏掉候选行的边界缺陷，降低了缺失查询词与零分尾扫描开销，加固了段页面回收与 `tsvector` 数据校验，并完全兼容 `1.0.0` 的原生 `tsvector` SQL 接口与第 4 版索引格式。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release**：[`pgsty/vchord_bm25 1.1.0`](https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0) · [源码仓库](https://github.com/pgsty/vchord_bm25)
> - **技术文档**：[版本历史](/zh/docs/bm25/reference/migration/#releases) · [安装指南](/zh/docs/bm25/getting-started/installation/) · [迁移指南](/zh/docs/bm25/reference/migration/)
> - **软件包与 SBOM**：[下载矩阵](/zh/download/) · [PGEXT (`vchord_bm25`)](https://pgext.cloud/e/vchord_bm25) · [SBOM 与许可证](/zh/docs/about/sbom/)

## 1.1.0 修改概览 {#changes}

| 领域 | 修改 |
| :--- | :--- |
| WAND 上界累加顺序 | WAND 上界严格按照文档评分所使用的查询词序累加词项贡献，消除因浮点舍入误差导致近同分文档被提前剪枝的问题。 |
| 缺失词项与单文档开销 | 文档求和改用仅覆盖封闭段命中游标的稠密 ordinal bitmap，消除逐文档堆分配与哈希计算；同分文档按内部索引位置稳定排序与剪枝；仅对有望进入当前批次的候选执行预过滤，并在批次填满后立即终止零分尾扫描。 |
| 预过滤与优化器安全 | `bm25.prefilter` 自动跳过包含 `SubPlan` 的过滤表达式（交由 PostgreSQL 执行器求值）；`amcostestimate` 仅采信本扩展定义的 `to_bm25query` 函数。 |
| 存储、缓存与回收加固 | 段页面回收原子化并在页锁保护下发布空闲页；读取索引页前先拒绝无效或未就绪索引（SQLSTATE `55000`）；切片前严格校验 `tsvector` 布局与偏移边界；保持扫描统计与近期查询驻留在受 `work_mem` 限制的缓存中；`ambuild` 上报真实行数/页数与并行工作进程数。 |
| 跨平台共存 | 仅在 Linux `x86_64`/`aarch64` 上启用 `mimalloc`，使 `vchord_bm25` 与 `vchord` 可在 macOS 的 `shared_preload_libraries` 中同时加载。 |
{.wide .expand}

## 修复近同分场景下的 WAND 剪枝 {#correct-wand-pruning}

WAND 上界现在按与文档实际评分一致的查询词序累加。此前按游标顺序求和时，浮点舍入可能令上界比真实得分低几个 ULP，使分数紧邻当前批次阈值的文档在完整扫描中被误剪枝。

该修复覆盖 pivot 上界、普通块上界、紧上界、预过滤路径、增长段续扫及分页扫描。同分结果保持稳定的内部索引位置顺序。回归套件覆盖开启/关闭预过滤、`LIMIT`、分页、删除行、增长段记录及缺失查询词的近同分场景。

## 降低缺失词项与零分尾扫描开销 {#absent-term-bookkeeping}

单文档求和改用按封闭段实际命中游标定长的稠密 ordinal bitmap，包含大量未命中词项的长查询不再分配与缺失词数成正比的状态。同时，扫描消除了逐文档内存分配，在候选上界不足以进入当前 Top-K 批次时跳过预过滤求值，并在当前批次已满后停止遍历零分尾行。

包含大量高频命中词的长查询仍需遍历更多倒排链；建议基于代表性业务负载评估延迟，并按需调整初始 `"bm25.limit"` 批次大小。

## 从 1.0.0 升级 {#upgrade-from-100}

SQL API 与第 4 版索引磁盘格式与 `1.0.0` 完全一致，健康的 `1.0.0` 索引无需 `REINDEX`。安装 `1.1.0` 动态库与 SQL 文件并重启 PostgreSQL 以加载新版 `vchord_bm25.so`，随后执行：

```sql
ALTER EXTENSION vchord_bm25 UPDATE TO '1.1.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
-- 1.1.0
```

由于全部修复均位于共享库代码中，`1.0.0--1.1.0` 升级脚本有意为空。请注意：`REINDEX CONCURRENTLY` 会生成新的索引 OID，若应用缓存了预处理计划或持久化了带旧 OID 的 `bm25query`，请在查询时通过索引名（`'my_idx'::regclass`）动态解析。历史 `0.3.x`（`bm25vector`）实例仍需遵循 [BM25 迁移指南](/zh/docs/bm25/reference/migration/)完成迁移。

## 过滤与零分记录 {#filtering-and-zero-score-rows}

`"bm25.limit"` 与索引级 `limit` 存储选项仅控制初始 WAND 批次大小，而非硬性返回上限；SQL `LIMIT`、`OFFSET` 与执行器 `WHERE` 过滤会按需自动续扫。`WHERE doc @@ ...` 全文布尔匹配仍由 PostgreSQL 执行器求值；若存在高选择率或无需排序的纯布尔匹配查询，建议配合标准 `GIN` 索引。未命中文档得分为 `+0.0`，`NULL` 行在升序排序中排在末尾。
