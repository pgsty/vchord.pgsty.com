---
title: "vchord_bm25 1.3.0：构建 WAL 大幅精简、RLS 语料统计共享与子查询预过滤"
date: 2026-11-24
description: "vchord_bm25 1.3.0 通过跨词元批量检查点显著降低构建与重建 WAL，新增面向 RLS 的 shared_corpus_stats 选项，支持可重复相关子查询预过滤，并改进 PostgreSQL 15–19 上的 Top-K 计划选择。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord_bm25"
aliases: [/blog/release/vchord-bm25-1.3.0/]
---

{{< release-card >}}

**vchord_bm25 1.3.0** 是 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`）公开发布的最新版本，在 [1.2.0](/zh/release/vchord-bm25-1.2.0/) 基础上通过跨词元批量检查点大幅减少构建与合并 WAL，按参与进程分摊并行排序内存，改进选择性 Top-K 代价估算与增长段分页扫描，新增面向行级安全（RLS）的可选 `shared_corpus_stats` 选项，并支持可重复相关子查询的预过滤。

面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`，基于 Ubuntu 22.04 构建、要求 `libc6 >= 2.35`）的 Linux `.deb` 与 `.zip` 二进制包、符合 PGXN 规范的源码 ZIP 及全部 `.sha256` 校验文件已发布于 [GitHub Release](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0)。

## 1.3.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| 构建与重建 WAL | 索引构建与段重建改为跨词元累计并批量写入倒排检查点，在保持索引页数不变的前提下大幅减少 Generic WAL 条数与总字节数。并行构建参与者每处理 1,024 行及扫描结束时上报一次进度。 |
| 并行排序内存预算 | `CREATE INDEX` 期间由 leader 与实际启动的 worker 共同分摊映射排序内存，单个进程上限取 `maintenance_work_mem` 分摊值与 64 MiB 中的较小者；PostgreSQL 17–19 直接传入工作进程请求数。 |
| 增长段统计与分页 | 维护封闭段与增长段合并后的精确语料统计。标量 `<&>` 评分在单次执行内复用已校验的索引元数据与锁；排序扫描仅保留正分增长段候选，翻页触及零分或 `NULL` 行时再按需续读，并在后续批次跳过已耗尽的正分增长段候选。 |
| Top-K 代价估算 | `amcostestimate` 将首批准备代价与后续倒排扩批代价拆开定价，使 PostgreSQL 对选择性过滤的 Top-K 查询更准确地选用有序 BM25 索引扫描，避免过早退回 `Bitmap Scan + Sort`。 |
| RLS 与语料权限 | 新增由索引所有者控制的存储选项 `shared_corpus_stats`（默认 `off`），显式开启后允许受行级安全约束的角色使用全索引语料统计评分，PostgreSQL 仍在返回行前执行行策略。标量、索引扫描与视图路径统一校验语料权限；列级授权可覆盖简单索引表达式与部分索引谓词。 |
| 相关子查询预过滤 | `bm25.prefilter` 支持对普通堆扫描或 B-tree 扫描之上的可重复相关子查询执行预过滤（包括标量 `count(*)`）。易失子查询、未知计划节点与安全敏感过滤继续交由 PostgreSQL 执行器处理。 |
| 维护与退役页回收 | 推迟临时草稿文件创建直至确实触发段重建，空 `VACUUM` 零临时文件开销。单条原子 Generic WAL 最多从退役链移除 3 个旧页，记录完成后再更新空闲空间映射提示。 |
| 源码归档 | GitHub Release 独立附带包含 PGXN 元数据的源码 ZIP 与 `.sha256` 校验文件（发布至 PGXN 仍需配置上传凭据）。 |
{.wide .expand}

## 构建 WAL、维护与查询实测 {#performance}

根据 [1.3.0 性能验收报告](https://github.com/pgsty/vchord_bm25/blob/1.3.0/docs/performance/2026-11-24-bm25.zh-CN.md)，在 20,000 行中英文混合技术文档语料（`shared_buffers = 256MB`，热缓存）上，于 macOS `arm64`（PostgreSQL 18.7）与 Ubuntu `x86_64`（PostgreSQL 18.6，tmpfs）对比 `1.2.0` 与 `1.3.0`：

| 测试项 | macOS `arm64`（`1.2.0` → `1.3.0`） | Ubuntu `x86_64`（`1.2.0` → `1.3.0`） |
| :--- | :--- | :--- |
| 串行 `CREATE INDEX` Generic WAL 条数 | 205,319 → 3,860 | 205,320 → 3,861 |
| 串行 `CREATE INDEX` WAL 总量 | 25.99 MiB → 14.43 MiB（-44.5%） | 25.99 MiB → 14.43 MiB（-44.5%） |
| 串行 `CREATE INDEX` 耗时 | 726.1 ms → 425.8 ms | 747.6 ms → 509.4 ms |
| 追加 2,000 行后段重建耗时 | 598.0 ms → 286.5 ms | 569.9 ms → 317.2 ms |
| 退役页回收 Generic WAL 条数 | 2,771 → 927 | 2,771 → 927 |
| 相关 `count(*)` 预过滤（关闭 → 开启） | 14.49 ms → 4.25 ms（块访问 166,279 → 30,220） | 19.40 ms → 6.68 ms（块访问 166,271 → 30,219） |
{.wide .expand}

拆开首批准备与扩批代价后，10% 选择率分类过滤的 Top-10 查询在合格行靠前时自然切换为 BM25 索引扫描（延迟从 `Bitmap + Sort` 的 8.40 ms / 10.51 ms 降至 1.40 ms / 1.73 ms）。需要留意的是，规划器统计无法预知过滤条件与 BM25 排名的相关性：若合格行大量分布在低分区间，多轮扩批仍可能慢于位图扫描，建议结合 `EXPLAIN ANALYZE` 检验具体负载。

## RLS 表的 `shared_corpus_stats` 选项 {#shared-corpus-stats}

默认情况下（`shared_corpus_stats = off`），当调用者受行级安全策略约束时，`vchord_bm25` 会拒绝计算 BM25 分数，以防全局词项文档频率泄露不可见行信息。如果业务允许共享全表词频统计，可由索引所有者显式启用：

```sql
ALTER INDEX documents_terms_bm25 SET (shared_corpus_stats = on);
```

启用后，具备语料读取权限的角色即可按全索引统计打分，而 PostgreSQL 仍会在返回结果前严格应用行策略。请结合多租户隔离模型评估该权衡（参见[参数与索引选项](/zh/docs/bm25/reference/gucs/#index-options)）。

## 升级与降级说明 {#upgrade-notes}

1. **PostgreSQL 版本要求**：`1.3.0` 支持 `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19；PostgreSQL 14 实例须先升级服务器。
1. **1.x 原地升级**：按[安装指南](/zh/docs/bm25/getting-started/installation/)安装 `1.3.0` 动态库与 SQL 文件，重启 PostgreSQL，随后在每个数据库中执行：

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

`1.0.0`、`1.1.0` 与 `1.2.0` 的第 4 版索引升级后均可直接复用，无需 `REINDEX`。历史 `0.3.x`（`bm25vector`）实例需按[从 0.x 迁移](/zh/docs/bm25/reference/migration/#from-0x)导出文本并重建索引。

> [!WARNING] 回退到 1.3.0 以下版本前
> SQL 升级脚本仅支持向前升级。尽管 `1.3.0` 与 `1.2.0` 的 SQL 对象一致，但旧版动态库不识别 `shared_corpus_stats` 选项。回退动态库前，必须对每一个显式设置过该选项（包括显式设为 `off`）的索引执行 `ALTER INDEX <index> RESET (shared_corpus_stats);`。排查查询见[降级说明](/zh/docs/bm25/reference/migration/#downgrade)。
