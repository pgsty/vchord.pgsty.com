---
title: "vchord 1.3.0：恢复安全与运维加固"
date: 2026-11-10
description: "vchord 1.3.0 面向 PostgreSQL 14–18 加固 WAL 索引页原子发布、图索引维护、查询采样权限、RaBitQ 余弦语义与扫描执行。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.3.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.3.0/]
---

{{< release-card >}}

**vchord 1.3.0** 延续 PGSTY 面向 PostgreSQL 14–18 的维护发布线。本版本将 `vchordrq.epsilon` 默认值保持为 `1.9`，重点加固崩溃恢复顺序、图索引维护、查询采样诊断权限、量化边界行为与扫描执行路径。

面向 PostgreSQL 14–18（`x86_64` 与 `aarch64`）的 Linux ZIP 压缩包与 Debian 软件包（基于 Ubuntu 22.04 构建，DEB 包声明 `libc6 >= 2.35`，全部产物均附 SHA-256 校验文件）已发布于 [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.3.0)。

安装对应 PostgreSQL 大版本的共享库与 SQL 文件并重启 PostgreSQL，随后在每个安装了该扩展的数据库中执行 `ALTER EXTENSION vchord UPDATE TO '1.3.0';`。已验证从 `0.2.0` 至 `1.2.0` 的就地升级路径；升级前请先阅读下方[升级说明](#upgrade-notes)。

## 1.3.0 修改概览 {#changes}

| 领域 | 修改 |
| :--- | :--- |
| WAL 页面原子发布 | 新分配的 `vchordrq` 向量页与 `vchordg` 顶点页在被空闲空间映射（FSM）暴露前，会将页面初始化与入口链接写入同一条 Generic WAL 记录；修复对齐 `vchordg` 页上的非对齐顶点指针写入。磁盘页面格式保持兼容。 |
| 图索引维护与并发写入 | `vchordg` 执行有界的局部 `VACUUM` 桥接修复，无变更时跳过 `VACUUM` 页面重写，禁止并发插入通过已被 `VACUUM` 释放的顶点建立链接，并在反向链接重试耗尽时以 SQLSTATE `40001` 中止事务。 |
| 查询采样与 Recorder | 查询采样默认保持 `off`。读取 `vchordrq_sampled_queries` 及调用采样函数现要求超级用户或 `pg_read_all_stats` 权限（表所有者或 `SELECT` 权限不再放行）。普通已提交的删除索引/数据库操作在提交后清理采样文件，`ROLLBACK` 与 `SAVEPOINT` 回滚保留现有样本。 |
| 外部构建表名限定 | `build.external.table` 必须写成带模式的 `schema.table`。存量未限定索引仍可正常查询，但在执行 `REINDEX`、`TRUNCATE`、`VACUUM FULL`、`CLUSTER`、相关类型改写或恢复转储等会重建/替换索引的操作前必须先更新配置（否则返回 SQLSTATE `22023` 并给出修复提示）。 |
| RaBitQ 余弦与边界校验 | `rabitq4` 与 `rabitq8` 余弦距离（`<=>` 与 `<<=>>`）统一计算 `1 - cos`，零范数或非有限向量返回 `NaN` 并在余弦索引中自动跳过；零向量与一维向量生成有限量化因子；`dequantize_to_*` 拒绝超过 `16000` 维（`54000`）与 `f16` 溢出（`22003`）；`rabitq4(n)` / `rabitq8(n)` 文本与 `COPY` 输入保持 `1.2.0` 行为以兼容 `pg_dump`，维度约束仍由索引校验。 |
| `halfvec` 与扫描执行 | `halfvec` 近邻路由引入精确残差下界与 ARM FP16/FHM 硬件加速；修正 `vchordg.io_search` 与 `vchordg.io_rerank` 先前互换的顶点搜索与向量精排 I/O 策略分发；`vchordrq` 预过滤对每条候选仅求值一次谓词，遇到易变表达式或 `SubPlan` 时自动回退为后过滤。 |
| 优化器、大表采样与平台 | 索引扫描在列表锁外检查取消中断且不在持锁期间执行代价休眠；钩子启动的扫描在查询内存上下文中分配资源；`NULL` 球面键强制回表复核且非法球面参数直接报错；不可用的向量索引路径附加 `disable_cost`；K-means 堆块采样改用 `u64` Feistel 域以支持超过 8 TiB 的大表；仅在 Linux 启用 `mimalloc`，使 `vchord` 与 `vchord_bm25` 可在 macOS 上同时预加载。 |
{.wide .expand}

## 恢复安全、图索引维护与采样生命周期 {#recovery-and-operations}

- **原子索引页发布**：初始化新的 `vchordrq` 向量页或 `vchordg` 顶点页并写入其入口链接现合并为单条 Generic WAL 记录，完成后才更新 FSM 空闲空间提示。崩溃恢复与物理备库回放不会读到已链接但未初始化的页面，且无需为每页增加额外 WAL 刷盘。
- **有界的 `vchordg` `VACUUM` 修复**：`vchordg` 在受控内存与跳数预算内修复稀疏删除桥接节点。大范围或聚簇删除仍可能削弱图连通性；批量删除后请评估召回率，必要时执行 `REINDEX INDEX CONCURRENTLY` 重建，并保持基表 `autovacuum` 开启。
- **Recorder 权限与事务边界**：查询采样用于本机召回诊断，不参与 PostgreSQL 事务回滚，也不应作为审计日志使用。访问 `vchordrq_sampled_queries` 与 `vchordrq.query_sampling_*` 仅限超级用户或 `pg_read_all_stats` 成员（`vchordrq_prewarm` 与 `vchordg_prewarm` 保留原有的表所有者或 `SELECT` 权限检查）。普通已提交的 `DROP INDEX` / `DROP DATABASE` 会在提交后尽力清理样本文件；`PREPARE TRANSACTION` 保留样本，`COMMIT PREPARED` 或提交后崩溃可能遗留不可达诊断文件，`DROP INDEX CONCURRENTLY` 即使中途取消也可能已在内部提交阶段移除样本，`REINDEX CONCURRENTLY` 则会启用新的采样标识。

## 升级说明 {#upgrade-notes}

1. **在维护或恢复前检查外部构建索引配置**：排查是否存在未加模式前缀的 `build.external.table` 选项：

   ```sql
   SELECT c.oid::regclass AS index_name, o.option_value
   FROM pg_class AS c
   JOIN pg_am AS am ON am.oid = c.relam
   CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
   WHERE am.amname = 'vchordrq'
     AND o.option_name = 'options'
     AND o.option_value LIKE '%external%';
   ```

   请同时检查点分键（`build.external.table`）与 `[build.external]` 两种 TOML 写法，保留其余选项并将表名改为 `schema.table`：

   ```sql
   ALTER INDEX my_index SET (options = $$
   [build.external]
   table = 'public.centroids'
   $$);
   ```

2. **按需重建受影响的历史余弦或量化索引**：`ALTER EXTENSION vchord UPDATE TO '1.3.0'` 仅更新目录定义，不会重写既有索引页。对以下存量索引请执行 `REINDEX INDEX CONCURRENTLY`：
   - 既有 `rabitq4` / `rabitq8` 余弦索引（`rabitq*_cosine_ops`），或包含零范数、非有限向量的余弦索引；
   - 由 `1.2.0` 及更早版本构建、且包含零向量或一维向量的 `rabitq4` / `rabitq8` 索引。

3. **核对监控角色权限**：若监控或召回评估角色需要读取 `vchordrq_sampled_queries`，请为其授予 `pg_read_all_stats`。

完整运维细节请参阅[外部索引构建](/zh/docs/vchord/usage/external-build/)、[召回率评估与查询采样](/zh/docs/vchord/usage/measure-recall/#query-sampling)、[图索引维护](/zh/docs/vchord/usage/graph-index/#maintenance)与[量化类型指南](/zh/docs/vchord/usage/quantization-types/)。
