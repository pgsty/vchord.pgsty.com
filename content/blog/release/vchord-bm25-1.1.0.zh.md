---
title: "vchord_bm25 1.1.0：修复 WAND 检索正确性问题"
date: 2026-11-08
description: "vchord_bm25 1.1.0 修复罕见浮点舍入导致近同分文档被剪枝漏行的问题，减少不存在词项的求和开销，并保持 1.0.0 的 SQL API 与索引格式兼容。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-bm25-1.0.0.png"
tags:
  - "release"
  - "vchord_bm25"
  - "bm25"
  - "full-text-search"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0"
upstream_source: ""
upstream_link: ""
---

**vchord_bm25 1.1.0** 是 PGSTY 维护的 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 正确性与查询路径优化版本。本版本修复了 Block-WeakAnd（WAND）剪枝中罕见的浮点舍入问题：近同分文档可能在完整扫描中被静默漏掉。同时继续保持 1.0.0 引入的 PostgreSQL 原生 `tsvector` SQL API 与第 4 版索引存储格式。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release**：[`pgsty/vchord_bm25 1.1.0`](https://github.com/pgsty/vchord_bm25/releases/tag/1.1.0) · [源码仓库](https://github.com/pgsty/vchord_bm25)
> - **文档**：[版本历史](/zh/docs/bm25/reference/versions/) · [安装指南](/zh/docs/bm25/getting-started/installation/)
> - **PGXN**：[扩展分发页](https://pgxn.org/dist/vchord_bm25/)

## 修复近同分场景下的 WAND 剪枝 {#correct-wand-pruning}

现在，WAND 上界按照与文档评分相同的查询词序累加。此前如果游标顺序不同，浮点加法可能使上界比实际分数低几个 ULP；当文档分数与当前批次阈值极其接近时，该文档可能被提前剪枝，并从完整扫描结果中消失。

修复覆盖 pivot 上界、普通 block 上界、tight 上界、prefilter 路径、growing 段续扫以及分页扫描。同分结果继续使用稳定的内部索引位置排序。回归测试覆盖开启和关闭 prefilter、`LIMIT`、分页、删除记录、growing 记录以及不存在词项的近同分场景。

## 减少不存在词项带来的求和开销 {#absent-term-bookkeeping}

每个文档的求和现在使用稠密 ordinal bitmap，大小只取决于封闭索引中实际参与查询的游标数量。查询包含大量索引中不存在的词时，不再创建与缺失词数量成正比的 bitmap 状态，同时保持原有评分顺序不变。测试覆盖空集合、64 和 128 附近的 bitmap 边界，以及包含 129 个不存在词的 SQL 回归用例。

该优化并不改变长查询的工作负载依赖特征。高频多词查询在上界计算上仍可能比短查询消耗更多 CPU；请使用代表性查询进行测量，并按需要调整初始 `bm25.limit`。

## 从 1.0.0 升级 {#upgrade-from-100}

SQL API 与第 4 版索引存储格式保持不变。健康的 1.0.0 索引无需 `REINDEX`；安装 1.1.0 动态库与 SQL 文件，如果修改了 `shared_preload_libraries` 请重启 PostgreSQL，然后执行：

```sql
ALTER EXTENSION vchord_bm25 UPDATE TO '1.1.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
-- 1.1.0
```

由于修复位于动态库代码中，`1.0.0--1.1.0` 升级脚本有意为空。0.3.x 的 `bm25vector` API 与索引格式仍然不能与 1.1.0 兼容；跨越这一边界请阅读[迁移指南](/zh/docs/bm25/reference/migration/)。

## 过滤与零分记录 {#filtering-and-zero-score-rows}

`bm25.limit` 与索引 `limit` 选项控制初始 WAND 批次大小，而不是硬性结果上限。SQL `LIMIT`、`OFFSET` 和执行器侧的 `WHERE` 过滤可能需要更多候选，扫描会按需继续。`WHERE vector @@ ...` 仍由执行器负责过滤；对于选择性很高或几乎为空的全文匹配，可以使用 GIN 索引改善过滤路径。不匹配文档的分数为零，`NULL` 行在升序分数排序中排在最后。

本版本已通过 PostgreSQL 18.6 acceptance、SQLLogicTest、Rust 测试、Clippy 以及 PGXN 源码归档检查。GitHub workflow 继续覆盖 PostgreSQL 14–18 的 Linux 与 macOS 软件包矩阵。
