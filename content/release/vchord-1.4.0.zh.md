---
title: "vchord 1.4.0：过滤键索引、自适应预读与 PostgreSQL 19 支持"
date: 2026-11-23
description: "vchord 1.4.0 新增带分区极值与哈希键的 RQ 过滤键索引、自适应 I/O 预读、在线列表压缩，升级至 pgrx 0.20.1 并支持 PostgreSQL 15–19。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.4.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.4.0/]
---

**vchord 1.4.0** 引入 `vchordrq` 多列过滤键索引、自适应 I/O 预读默认值与在线列表压缩，升级至 `pgrx 0.20.1` 与 Rust `1.100.0+`，并面向 `x86_64` 与 `aarch64` 支持 PostgreSQL 15–19。自本版本起不再支持 PostgreSQL 14。

> [!NOTE] 已由 1.5.0 替代的草稿里程碑
> `1.4.0` 标签（`https://github.com/pgsty/vchord/tree/1.4.0`）在 GitHub 上保持为草稿发布，已于次日由正式发布的 [**vchord 1.5.0**](/zh/release/vchord-1.5.0/) 替代；1.5.0 在 1.4.0 基础上进一步加入了流式过滤检索、图索引 `VACUUM` 跨桥修复与关系缓存稳定性修复。生产部署与预编译包下载请直接使用 [`vchord 1.5.0`](/zh/release/vchord-1.5.0/)。

## 1.4.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| RQ 过滤键索引 | 为 `vchordrq` 增加多列过滤键支持，下推等值、范围与 `IS [NOT] NULL` 条件，并提供独立哈希键运算符类（`uuid_hash_ops`、`int4_hash_ops`、`int8_hash_ops`）。带键列表按键值排序，并通过前导键的块级最小/最大值 `zone_maps` 跳过整块。枚举范围遵循 PostgreSQL 枚举排序（含域类型及 `ALTER TYPE ... ADD VALUE ... BEFORE/AFTER` 新增的枚举值）。有序扫描中的 `= ANY(...)` 下推需要 PostgreSQL 17+。 |
| 过滤扩容扫描 | 带下推过滤键的扫描在初始 IVF `probes` 列表候选不足时自动向外扩容，总探测列表数受 `vchordrq.max_probes` 控制（默认 `-1` 不限，始终保留初始探测数）。有序补扫按原始 `f32` 重排距离排序（超出 `work_mem` 时可落盘），从索引重排时推迟堆表预读直至行离开排序缓冲区。 |
| 距离、球面与 SIMD | 叶子列表的残差内积估算改以查询向量在质心上的投影为中心；余弦归一化对极端量级的有限非零向量先缩放再归一化；`halfvec` L2 路由在支持的硬件上使用 FP16 差值（带溢出回退），最终重排与残差下界维持 FP32；`vector`/`halfvec` L2 球面半径平方前向外舍入，避免边界候选在 PostgreSQL 严格复核前被漏掉；单遍量化与多累加器 SIMD 归约加速高维向量计算。 |
| I/O 与在线压缩 | 在 PostgreSQL 17+ 上，`vchordrq.io_search` 默认改为 `mixed`，`vchordrq.io_rerank` 默认改为 `prefetch_buffer`，并在回表重排前对后续候选提前发起堆页预读。`vchordrq` 列表压缩不再阻塞并发读者访问旧页，仅在发布新带并合入并发插入时短暂加排他锁保护 jump 页。 |
| 规划器与 NULL 安全 | 并行构建 `vchordrq` 或 `vchordg` 遇到断裂 HOT 链时正确保留 PostgreSQL 的旧快照可见性保护。对显式向量 `NULL` 判定或严格索引函数入参的 `NULL` 测试（含 `OR` 分支与空值安全比较）交由其他执行路径处理；执行期排序参数为 `NULL` 时返回满足部分索引谓词与查询条件的可见堆行；支持 PostgreSQL 对第一排序键之后的额外距离键排序。 |
| 可观测性与依赖 | 在 PostgreSQL 15–19 上上报 `pg_stat_user_indexes.idx_scan`，在 PostgreSQL 18+ 的 `EXPLAIN ANALYZE` 中上报 `Index Searches`；在 PostgreSQL 19 传递只读扫描提示；`vchordrq_prewarm` 与 `vchordg_prewarm` 读页前先拒绝无效索引。索引选项解析升级至 `toml` 1.2.2（修复畸形选项引发后端崩溃），查询采样记录器升级至 `rusqlite` 0.43.0（内置 SQLite 3.54.1），打开采样库检测到损坏时可在下次请求自动新建恢复。 |
| 平台与构建 | 新增 PostgreSQL 19 测试与 Linux 打包矩阵（`x86_64` 与 `aarch64`，`pgrx 0.20.1`），要求 Rust `1.100.0+` 及版本匹配的 Clang/libclang/LLVM 工具链；移除 PostgreSQL 14 支持。 |
{.wide .expand}

## `vchordrq` 过滤键 {#filter-keys}

按租户、类目或时间等高选择性字段过滤时，常规 IVF 探测列表里的合格行往往凑不齐 `LIMIT`。自 `1.4.0` 起，可以将过滤键列附在向量列之后，由 `vchordrq` 在索引扫描重排前直接筛选：

```sql
CREATE INDEX items_vec_tenant_idx
ON items USING vchordrq (embedding vector_cosine_ops, tenant_id, created_at)
WITH (options = $$
residual_quantization = true
[build.internal]
lists = [2000]
spherical_centroids = true
$$);

SELECT id FROM items
WHERE tenant_id = 42 AND created_at >= now() - interval '30 days'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

- **支持的类型**：`int2`、`int4`、`int8`、`float4`、`float8`、`uuid`、`date`、`timestamp`、`timestamptz`、`oid`、`bool` 及任意 PostgreSQL 枚举类型。
- **哈希键**：仅做等值过滤的宽键（如 UUID）可选用 `uuid_hash_ops`、`int4_hash_ops` 或 `int8_hash_ops` 存储紧凑哈希值（如 `owner uuid_hash_ops (bytes = 4)`），发生哈希碰撞时由 PostgreSQL 回表复核。
- **限制扩容开销**：`vchordrq.max_probes` 默认为 `-1`；遇到零匹配过滤值时，扫描会读完所有列表才返回空集。按需设置 `vchordrq.max_probes` 控制最大探测列表数；对单层索引上的常见过滤值和小 `LIMIT`，可将其设为初始探测数。下调生产上限前应先实测召回率。

在 `1.4.0` 中，可扩容的有序扫描会在返回首行前先重排并排序合格候选；[vchord 1.5.0](/zh/release/vchord-1.5.0/) 进一步改为先流式返回初始探测结果，不足时再按需扩容。

## 存储格式与升级说明 {#upgrade-notes}

1. **先升级 PostgreSQL 14**：`pgrx 0.20.1` 不再支持 PostgreSQL 14。PostgreSQL 14 用户应停留在 [vchord 1.3.0](/zh/release/vchord-1.3.0/)，待升级至 PostgreSQL 15–19 后再升级扩展。
1. **安装并更新目录**：安装对应 PostgreSQL 主版本的动态库与 SQL 文件，重启 PostgreSQL，然后在每个数据库中执行：

   ```sql
   ALTER EXTENSION vchord UPDATE;
   ```
{.steps}

- **索引磁盘格式**：存量 `1.3.0` 单列 `vchordrq` 索引与新建无过滤键索引继续使用格式 `1001`；带过滤键的 `vchordrq` 索引使用格式 `1003`。
- **回退注意**：`1.3.0 → 1.4.0` 升级脚本新增了过滤键函数与运算符类，仅降级软件包不会回退 SQL 目录。若需回退至 `1.3.0`，须先在 `1.4.0` 下删除或替换所有带键索引，再恢复与 `1.3.0` 兼容的目录或备份。
- **断裂 HOT 链保护**：并行构建修复用于保护快照早于受影响构建的并发事务；旧事务结束后新索引即可正常使用，存量索引无需全面重建。
- **球面检索近似语义**：`vchordrq` 与 `vchordg` 的球面检索（`<<->>`、`<<=>>`、`<<#>>`）仍属近似搜索（参见 [issue #29](https://github.com/pgsty/vchord/issues/29)）。必须找齐半径内全部行时，请通过 `EXPLAIN` 确认走顺序扫描。

详细用法见[条件过滤](/zh/docs/vchord/usage/filtering/#filter-keys)、[vchordrq 索引](/zh/docs/vchord/usage/indexing/)与[升级与迁移](/zh/docs/vchord/admin/migration/)。
