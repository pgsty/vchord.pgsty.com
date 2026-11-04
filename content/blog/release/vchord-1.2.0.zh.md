---
title: "vchord 1.2.0：PGSTY 接手后的首个发布"
date: 2026-11-04
description: "vchord 1.2.0 是 PGSTY 维护的首个版本，修复了部分探测下的多向量 MaxSim、vchordg 球面过滤、VACUUM 顶点可见性与统计信息维护、外部质心树校验、量化类型边界检查以及预热与采样权限控制。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
images:
  - "/blog/covers/vchord-1.2.0.png"
tags:
  - "release"
  - "vchord"
  - "vectorchord"
  - "vector-database"
upstream_source: ""
upstream_link: ""
---

**vchord 1.2.0** 是 PGSTY 在 [`pgsty/vchord`](https://github.com/pgsty/vchord) 维护的首个正式版本，采用 AGPL-3.0 许可证发布。它支持从 `vchord 0.2.0` 至 `1.1.1` 直接原地升级（`ALTER EXTENSION vchord UPDATE TO '1.2.0'`，无需重建现有索引），修复了 `vchordrq` 与 `vchordg` 的多处查询正确性问题，改进了 `VACUUM` 顶点可见性、统计信息上报、内外索引构建与量化类型校验，并补齐了缓存预热与查询采样的权限检查。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release**：[`pgsty/vchord 1.2.0`](https://github.com/pgsty/vchord/releases/tag/1.2.0) · [源码仓库](https://github.com/pgsty/vchord)
> - **扩展目录主页**：[pgext.cloud (`vchord`)](https://pgext.cloud/e/vchord) · [Pigsty 扩展页面 (`pigsty.cc`)](https://pigsty.cc/ext/e/vchord/)
> - **二进制软件包**：[RPM / DEB 软件源配置](/zh/download/) · [SBOM 与许可证清单](/zh/docs/about/sbom/)

## 1.2.0 修改概览 {#changes}

| 方面 | 修改 |
| :--- | :--- |
| 多向量 MaxSim（`@#`） | 只探测部分分区且 `maxsim_refine = 0`、`maxsim_threshold = 0` 时，未出现在某个查询词元候选集中的文档改用该候选集中的最差距离填补缺失值，不再因取 `-Infinity` 而错误排在最前面。 |
| 球面过滤与构造器 | `vchordg` 球面范围操作符（`<<->>`、`<<=>>`、`<<#>>`）改为按操作符距离单位而非内部平方距离比较半径，并设置 `xs_recheck = true`；全部 6 个 `sphere(center, real)` 构造器在扩展创建时绑定复合返回类型，不再受调用者 `search_path` 影响。 |
| `read_stream` 重排序 | 在 PostgreSQL 17/18 上启用 `vchordrq.io_rerank = 'read_stream'` 时，若并发 `VACUUM` 使基表页面可见项减少，缓冲区守卫（buffer guard）仍与剩余候选项保持严格对齐。 |
| `VACUUM` 与统计信息 | `vchordg` 在 `VACUUM` 后排除已删除顶点，同时在入口顶点被删除时仍允许借道遍历以保证剩余顶点可达；`vchordrq` 与 `vchordg` 在 `CREATE INDEX`、`REINDEX` 和 `VACUUM` 后上报真实行数与页数，不再将 `pg_class.reltuples` 重置为 `0`；单独执行 `ANALYZE` 不再触发索引清理。 |
| 优化器与并行建索引 | `vchordg` 支持部分索引 `WHERE` 谓词，并在无向量排序/过滤条件（如 `SELECT COUNT(*)`）时施加 `disable_cost`；`vchordrq` 代价估算纳入 `LIMIT`、过滤选择率与 `probes` 预算；表级 `parallel_workers` 等存储选项不再阻碍并行构建索引。 |
| 内外索引构建校验 | 内部 k-means 采样仅读取 MVCC 可见元组，并在 `lists > samples` 时校验 `maintenance_work_mem` 预算；外部质心树构建校验树深度（`2..=9` 层）、拒绝环路与不可达节点，且当存在 `>= 2` 个 `parent IS NULL` 顶层质心时自动合成根节点。 |
| 量化数据类型 | `rabitq4` 与 `rabitq8` 严格限制 `1..=65535` 维度与编码范围（`0..=15` / `0..=255`）；`quantize_to_rabitq*` 拒绝非有限值溢出，而输入函数仍接受历史备份中的 `NaN`/`Inf` 元数据以保证 `pg_restore` 兼容；`halfvec` 距离按 `f32` 累加；量化 L2 距离在 `sqrt` 前将微小的负舍入残差截断为 `0`。 |
| 召回率评估与权限加固 | `vchordrq_evaluate_query_recall` 对 `@#` 查询要求 `exact_search => true`，按多级索引层数自动生成默认 `accu_probes`，并在评估后精确还原 `vchordrq.*` GUC；`vchordrq_prewarm`、`vchordg_prewarm` 与查询采样强制检查表拥有者或表级 `SELECT` 权限。 |
| 构建与平台支持 | 升级至 `pgrx 0.19.3`，支持 Linux x86_64 与 aarch64 上的 PostgreSQL 14–18，并提供从 `0.2.0` 至 `1.1.1` 的完整升级脚本与兼容符号。 |
{.wide .expand}

## 多向量 MaxSim（`@#`）、球面过滤与 `read_stream` 重排序 {#query-correctness}

- **部分探测下的多向量 MaxSim（`@#`）缺失值估算**：在多向量延迟交互检索（`@#`）中，VectorChord 将相似度取反作为距离（越小越靠前）。只探测部分 IVF 分区时，一篇候选文档可能出现在部分查询词元的候选集中，而未出现在另一些查询词元的候选集中。此前当 `vchordrq.maxsim_refine = 0` 且 `vchordrq.maxsim_threshold = 0` 时，缺失项会默认取 `-Infinity`（`f32::NEG_INFINITY`），反而使未被完整探测到的文档在升序 `ORDER BY` 中错误排到最前面。`1.2.0` 在精排和阈值都未提供估算值时，改用该查询词元已探测候选集中的最差距离填补缺失值。
- **`vchordg` 球面范围过滤（`<<->>`、`<<=>>`、`<<#>>`）**：`vchordg` 图遍历在内部使用平方距离计算 L2 与余弦距离。此前球面范围扫描直接将用户传入的半径与内部平方距离比较，且未要求回表复核（recheck）。`1.2.0` 会先将半径换算为对应操作符的距离单位再做剪枝，并对返回项设置 `xs_recheck = true`，由 PostgreSQL 执行器在基表元组上复核球面谓词。
- **不受 `search_path` 影响的 `sphere(...)` 构造器**：6 个 `sphere(vector, real)`、`sphere(halfvec, real)`、`sphere(rabitq8, real)` 及其多向量数组构造器改为在 `CREATE EXTENSION` / `ALTER EXTENSION` 时静态绑定复合返回类型（`SELECT ROW($1, $2)::sphere_*`），不再受调用者当前 `search_path` 影响。
- **PostgreSQL 17/18 `read_stream` 重排序对齐**：在 PostgreSQL 17 或 18 上设置 `vchordrq.io_rerank = 'read_stream'` 时，若并发 `VACUUM` 在索引扫描与回表精排之间清理了基表页面上的部分元组，`read_stream` 批次消费器会使缓冲区引脚守卫（buffer pin guard）与剩余候选元组保持同步，避免错位。

## 索引维护、`VACUUM` 与优化器代价估算 {#maintenance-and-planner}

- **`vchordg` 的 `VACUUM` 可见性与入口顶点可达性**：`VACUUM` 在 `vchordg` 索引中标记已删除的基表 TID 后，图搜索会在返回结果时过滤掉已删除顶点；即便图的入口顶点（entry point）本身已被删除，搜索仍允许借道遍历其邻接边，无需 `REINDEX` 即可保证其余存活顶点可达。
- **`vchordg` 部分索引与 `COUNT(*)` 保护**：`vchordg` 现支持部分索引谓词（`CREATE INDEX ... USING vchordg (...) WHERE ...`），并在扫描不包含任何向量排序或过滤条件时附加 `disable_cost` 惩罚代价，防止优化器为普通 `SELECT COUNT(*)` 选择图索引扫描。
- **准确的 `reltuples` / `relpages` 统计信息与 `ANALYZE` 行为**：此前 `ambuild` 与 `amvacuumcleanup` 返回全零的统计计数，导致执行 `CREATE INDEX`、`REINDEX` 或 `VACUUM` 后 `pg_class.reltuples` 被清零。现在 `vchordrq` 与 `vchordg` 均会统计并上报真实的索引元组数与页面数；单独执行 `ANALYZE`（`analyze_only = true`）时 `amvacuumcleanup` 会直接返回，不再无谓触发索引清理与压缩。
- **并行索引构建规划**：此前当基表配置了 `ALTER TABLE items SET (parallel_workers = 4)` 等表级存储选项时，`amoptions` 校验会误拒表级选项，导致并行建索引无法启动并行工作进程。修复后，`vchordrq` 与 `vchordg` 仅校验索引自身的存储参数，并行建索引可正常按表级或系统级参数规划工作进程。
- **`vchordrq` 代价模型**：`vchordrq` 的 `amcostestimate` 在估算带过滤条件的向量扫描时纳入了 `LIMIT`、过滤选择率以及当前生效的 `probes` 探测预算；当多级 `vchordrq.probes` 的层数与索引 `lists` 层级数不匹配时，优化器会自动附加 `disable_cost` 禁用该索引路径。

## 内部与外部索引构建校验 {#index-builds}

- **MVCC 可见行采样与内存上限检查**：`vchordrq` 内部 k-means 聚类在采样基表元组前会先通过 `HeapTupleSatisfiesVisibility` 检查可见性，避免死元组或未提交元组污染质心；初始采样缓冲区根据估算存活行数分配（上限为 `max(lists) * sampling_factor`），且当 `lists` 大于实际采样行数时仍会检查质心分配是否超出 `maintenance_work_mem`。
- **外部质心树结构校验**：通过外部质心表（`[build.external]`）构建 `vchordrq` 索引时，会在划分向量前先校验 `id` / `parent` 层次结构：
  1. 质心树深度必须介于 `2` 到 `9` 层之间（含根节点），对应 `vchordrq` 支持的 `1..=8` 层 `lists`。
  2. 包含循环父子引用（cycle）或不可达孤立节点的质心表会被直接拒绝并报错。
  3. 当存在 2 个及以上 `parent IS NULL` 的顶层质心时，`vchordrq` 会自动在它们上方合成一个虚拟根节点，无需手动插入虚拟根行。
- **`probes` 与 `alpha` 参数校验**：`SET vchordrq.probes` 与索引级 `probes` 存储参数会校验每个逗号分隔整数（范围 `1..=4294967295`，允许前后空白与单个尾逗号），遇到非法输入时立即报错。`vchordg` 的 `alpha` 构建参数要求包含 `1..=8` 个落在 `[1.0, 2.0)` 区间内的非递减浮点数，且首个元素必须为 `1.0`。

## 量化与半精度类型（`rabitq4`、`rabitq8` 与 `halfvec`） {#quantization-types}

- **维度与编码范围校验**：`rabitq4` 与 `rabitq8` 在 `typmod` 与文本/二进制输入解析时限制维度为 `1..=65535`，并校验每个量化编码落在 `0..=15`（`rabitq4`）或 `0..=255`（`rabitq8`）范围内，拒绝多余尾随字符或非法括号。
- **溢出拦截与 `pg_dump` / `pg_restore` 兼容**：`quantize_to_rabitq4` 与 `quantize_to_rabitq8` 会在输入向量范数或内积超出 `f32` 表示范围（产生 `NaN` / `Infinity`）时报错拒绝，并为全零向量或常数向量生成有限的元数据。与此同时，`rabitq4` 与 `rabitq8` 的文本和二进制输入函数仍允许读入旧版本备份中已存在的 `NaN` / `Inf` 元数据字段，保证 `1.1.x` 生成的逻辑备份能够恢复。
- **`halfvec` 的 `f32` 累加与量化 L2 开方保护**：`halfvec` 的距离操作符（`<->`、`<=>`、`<#>`）改为使用 `f32` 而非 `f16` 累加中间结果，避免高维或大幅值半精度向量中途溢出为 `Infinity`；量化 L2 距离估算在调用 `sqrt` 前会将浮点舍入产生的微小负数截断为 `0.0`，避免近似相等向量距离计算出现 `NaN`。

## 召回率评估与预热/采样权限加固 {#recall-and-security}

- **`vchordrq_evaluate_query_recall` 增强**：
  - 对多向量 MaxSim（`@#`）查询评估召回率时强制要求 `exact_search => true`（若使用近似基准搜索会直接给出明确报错）。
  - 省略 `accu_probes` 参数时，函数会根据目标索引的 `lists` 层级数自动生成对应层数的 `'65535'`（例如双层索引自动生成 `'65535,65535'`），不再因固定传入单层 `'65535'` 而触发层数不匹配错误。
  - 函数内部临时修改的 `vchordrq.probes`、`vchordrq.epsilon` 与 `vchordrq.enable_scan` 在评估结束或异常退出时均会恢复到调用前的值与 GUC 来源（先前未设置时执行 `RESET`）。
- **缓存预热与查询采样的权限检查**：
  - `vchordrq_prewarm(regclass, integer)` 与 `vchordg_prewarm(regclass)` 在将索引页加载至共享缓冲区前，会验证调用角色是否为基表拥有者或持有基表的表级 `SELECT` 权限。
  - 开启或配置查询采样（`vchordrq.query_sampling_*`）要求调用角色为表拥有者、持有表级 `SELECT` 权限或属于 `pg_read_all_stats` 角色；查询 `vchordrq_sampled_queries` 时也会自动过滤掉当前角色无权读取的索引记录。

## 已知问题 {#known-issues}

`1.2.0` 的软件包验收发现两种结果顺序与距离不一致的情况，已记录于 [pgsty/vchord#17](https://github.com/pgsty/vchord/issues/17)，计划在后续版本处理。召回率不受影响。

- `vchordg` 在返回结果的同时仍在继续搜索，`ORDER BY ... LIMIT` 的结果可能不按距离排序。调大 `vchordg.ef_search` 能减少这种情况，但不能完全避免。
- 对于 `halfvec` 列，距离相差约 0.0001 以内的两行可能顺序颠倒。涉及 `vchordrq` 的 `halfvec_cosine_ops`，以及 `vchordg` 的所有 `halfvec` 操作符类。

需要严格顺序时，请在外层查询中对候选结果重新排序，参见[图索引：结果顺序](/zh/docs/vchord/usage/graph-index/#result-order)。其他已知问题见 [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.2.0)。

## 升级至 1.2.0 与软件包获取 {#upgrade-and-packages}

`vchord 1.2.0` 与 `0.2.0` 至 `1.1.1` 创建的磁盘索引完全兼容。安装对应 PostgreSQL 版本的 `1.2.0` 软件包后，重启 PostgreSQL 以通过 `shared_preload_libraries` 加载新版动态库，随后在数据库中执行：

```sql
ALTER EXTENSION vchord UPDATE TO '1.2.0';
SELECT vchord_version();
-- 1.2.0
```

安装包内置了从 `0.2.0` 到 `1.1.1` 所有历史版本的直达升级脚本，并在动态库中保留了 `_vchord_0_3_*` 与 `_vchord_0_4_*` C 符号兼容包装，使仍停留在 `1.0.0` 之前目录定义的数据库也能直接执行 `ALTER EXTENSION vchord UPDATE TO '1.2.0'` 完成升级。

面向 PostgreSQL **14–18**、覆盖 16 个 Linux 发行版（`x86_64` 与 `aarch64`）的原生 RPM 与 DEB 软件包（`1.2.0-1PIGSTY` / `1.2.0-1PGSTY`）已发布在[下载页面](/zh/download/)。更多细节请参阅[升级与迁移指南](/zh/docs/vchord/admin/migration/)、[索引指南](/zh/docs/vchord/usage/indexing/)、[量化类型指南](/zh/docs/vchord/usage/quantization-types/)与 [SBOM 页面](/zh/docs/about/sbom/)。
