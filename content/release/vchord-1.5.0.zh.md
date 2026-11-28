---
title: "vchord 1.5.0：流式过滤检索、并行构建与图索引维护修复"
date: 2026-11-24
description: "vchord 1.5.0 让带过滤键的 RQ 扫描从初始探测流式返回并按需扩容，支持小主堆 TOAST 表并行建索引，加固图索引 VACUUM 桥接修复与 WAL 发布，面向 PostgreSQL 15–19。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.5.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.5.0/]
---

{{< release-card >}}

**vchord 1.5.0** 是 [`pgsty/vchord`](https://github.com/pgsty/vchord) 面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`）公开发布的最新版本，在 [1.4.0](/zh/release/vchord-1.4.0/) 过滤键架构之上增加了流式过滤扫描、预备查询关系缓存保护、小主堆 TOAST 表并行构建、球面复核加固以及 `vchordg` / `vchordrq` 维护改进。

面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`）的 Linux ZIP 与 Debian 软件包（基于 Ubuntu 22.04 构建，要求 `libc6 >= 2.35`，所有产物均附 `.sha256` 校验文件）已发布于 [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.5.0)。

## 1.5.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| 流式过滤键检索 | 带过滤键的 `vchordrq` 有序扫描先从初始 IVF 探测列表流式输出候选，仅在调用方需要更多行时才按需扩容至 `vchordrq.max_probes`。跨扩容轮次的距离可能减小；需要严格全局距离排序时，可在 SQL 中多取并重排。 |
| 关系缓存与距离路径 | `vchordrq` 扫描在 PostgreSQL 关系缓存失效期间持续保有过滤键布局，预备枚举范围查询在并发 `ANALYZE` 期间仍能正确读取已压缩块中的匹配行。半精度 L2 搜索在支持的 CPU 上使用 FP16 差值且路由阶段不再重读质心；余弦归一化对常规有限向量仅计算一次模长平方；不含球面条件的扫描不再在热循环中检查球面边界。 |
| 球面复核语义 | `vchordg` 以及半精度、内积、余弦、量化与拆分向量球面检索均通过堆表谓词复核候选；`vchordrq` 仅在单球面 `f32` L2 最终重排与 SQL 运算符使用相同整向量归约且所有过滤键均为精确键时直接接纳半径内候选。`NULL` 球面参数立即结束扫描。 |
| 可空向量与预过滤 | 可空向量列上的有序扫描保留 `IS DISTINCT FROM` 与 `IS NOT DISTINCT FROM` 选中的行，规划器识别已校验的非空属性。执行期排序键为 `NULL` 时流式返回可见堆行并将 HOT 元组解析到 HOT 根；字面量 `NULL` 排序键可选用顺序扫描。`vchordrq` 预过滤在搜索阶段求值符合条件的非易失子查询，带聚合的子计划保留在执行器中执行。 |
| 图索引 WAL 与 `VACUUM` | `vchordg` 插入将新向量页及其入口链接写入同一条 Generic WAL 记录，未变更的反向链接仅需共享身份校验。图 `VACUUM` 通过有界局部修复跨越已删除的桥接顶点重连活区域，并在不做全图可达性扫描的情况下回收已删除顶点。 |
| RQ `VACUUM` 与并行构建 | 在线 `vchordrq` `VACUUM` 每发布一个压缩列表即把退役页归还给持久化空闲空间，独占构建跨列表复用退役页；无键列表压缩流式处理并利用追加带尾指针提示，`VACUUM` 判断是否需要压缩时先检查追加带。CPU 密集型 `vchordrq` 与 `vchordg` 构建在小主堆 TOAST 表上可启用并行 worker（临时表及非并行安全表达式/谓词保持串行）；带键 RQ 压缩按实际启动的 leader 与 worker 分摊排序内存预算。 |
{.wide .expand}

## 流式过滤键扫描与关系缓存安全 {#streaming-filtered-scans}

带过滤键的 RQ 索引现在会直接从初始 IVF 探测列表流式输出候选，而不是先拉齐全部扩容轮次。执行如下查询时：

```sql
SELECT id FROM items
WHERE tenant_id = 42
ORDER BY embedding <-> $1
LIMIT 10;
```

只要初始探测列表凑够 10 条合格记录就能立即结束；候选不足时再逐轮扩容，直到满足 `LIMIT` 或触及 `vchordrq.max_probes`。由于后续扩容轮次可能找到距离更近的行，业务如果需要严格的距离全序，应在 SQL 层适当多取结果后重新排序（见[结果顺序](/zh/docs/vchord/usage/indexing/#result-order)）。

对于带枚举范围过滤的预备查询，此前并发 `ANALYZE` 触发关系缓存刷新时，扫描可能丢失过滤键布局并跳过已压缩块中的匹配行。`1.5.0` 在扫描生命周期内持有过滤键布局，重启加载新版动态库后存量索引即自动生效。

## 球面检索、维护与并行构建 {#sphere-and-maintenance}

- **球面复核**：球面检索在访问哪些列表或图区域上仍具近似性，候选由 PostgreSQL 严格半径谓词复核。唯一的免回表快路径是 `vchordrq` 的单球面 `f32` L2 检索，前提是最终重排与 `<->` 使用相同的整向量归约且所有过滤键均为精确键。
- **图索引跨桥修复**：`vchordg` `VACUUM` 遇到尚有邻居空位的活顶点时，可沿已删除的桥接顶点寻路重连另一侧活区域，无需全图遍历。若历史版本的 `VACUUM` 已经切断过某个活区域，升级后请对受影响的图索引执行一次 `REINDEX INDEX CONCURRENTLY index_name;`。
- **TOAST 表并行构建**：大维度向量存储在 TOAST 表时，主堆本身往往很小，此前容易回退到串行构建。`1.5.0` 允许此类 CPU 密集型的 `vchordrq` 与 `vchordg` 构建正常启用并行 worker，临时表和并行不安全的索引表达式/谓词仍串行执行。

## 升级说明 {#upgrade-notes}

`1.5.0` 可原地读取 `1.4.0` 索引，SQL 对象与磁盘格式保持不变（无键 `vchordrq` 为 `1001`，带键 `vchordrq` 为 `1003`）。

1. **PostgreSQL 14 集群**：自 `1.4.0` 起不再支持 PostgreSQL 14，从 `1.3.0` 升级前须先将 PostgreSQL 升级至 15–19。
1. **安装并重启**：按[安装指南](/zh/docs/vchord/getting-started/installation/)安装对应 PostgreSQL 主版本的 `1.5.0` 动态库与 SQL 文件，然后重启 PostgreSQL。
1. **更新各数据库扩展**：

   ```sql
   ALTER EXTENSION vchord UPDATE TO '1.5.0';
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

从 `1.3.0` 升级时会自动途经 `1.4.0` 升级脚本并安装过滤键 SQL 对象。从 `1.2.x` 及更早版本跨越升级的注意事项（`build.external.table` 模式限定、受影响的 `rabitq` 余弦或零/一维向量索引重建、查询采样所需的 `pg_read_all_stats` 权限）请参阅[升级与迁移](/zh/docs/vchord/admin/migration/#upgrade)。
