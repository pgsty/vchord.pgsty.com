---
title: "vchord_bm25 1.0.0：PGSTY 接手后的首个发布"
date: 2026-11-03
description: "vchord_bm25 1.0.0 是 PGSTY 维护的首个版本，以 PostgreSQL 原生 tsvector 替代自定义 bm25vector，支持可续扫的 WAND 检索、ShareUpdateExclusiveLock 并发维护以及语料级权限与 RLS 校验。"
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
release_url: "https://github.com/pgsty/vchord_bm25/releases/tag/untagged-e766a17dbd8365cfa7be"
upstream_source: ""
upstream_link: ""
---

**vchord_bm25 1.0.0** 是 PGSTY 在 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 维护的首个正式版本，采用 AGPL-3.0 许可证发布。它使用 PostgreSQL 原生 `tsvector` 索引替代 0.3.x 的自定义 `bm25vector` 类型与固定 `bm25_catalog` 模式，重新设计了支持按需续扫与并发 `VACUUM` 维护的 Block-WeakAnd（WAND）存储引擎，并在索引扫描与标量评分两条路径上加入了表/列权限检查与行级安全策略（RLS）防护。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release 草稿**：[`pgsty/vchord_bm25 1.0.0`](https://github.com/pgsty/vchord_bm25/releases/tag/untagged-e766a17dbd8365cfa7be) · [源码仓库](https://github.com/pgsty/vchord_bm25)
> - **扩展目录主页**：[pgext.cloud (`vchord_bm25`)](https://pgext.cloud/e/vchord_bm25) · [Pigsty 扩展页面 (`pigsty.cc`)](https://pigsty.cc/ext/e/vchord_bm25/)
> - **二进制软件包**：[RPM / DEB 软件源配置](/zh/download/) · [SBOM 与许可证清单](/zh/docs/about/sbom/)

1.0.0 的 GitHub 条目仍为草稿，需要相应仓库访问权限。已公开发布的版本见 [vchord_bm25 1.1.0](/zh/blog/release/vchord-bm25-1.1.0/)。

## 1.0.0 修改概览 {#changes}

| 方面 | 修改 |
| :--- | :--- |
| 原生 `tsvector` 接口 | 直接使用 `USING bm25 (... bm25_ops)` 为标准 PostgreSQL `tsvector` 列建立索引；`to_bm25query(tsvector, regclass)` 构造查询，`<&>` 返回负值 `double precision` BM25 分数（零分统一为 `+0.0`）。 |
| 可迁移模式 | 扩展对象直接安装在目标模式（默认 `public`），支持 `ALTER EXTENSION vchord_bm25 SET SCHEMA`，不再依赖固定的 `bm25_catalog` 模式。 |
| 可续扫的 WAND 检索 | `bm25.limit` 与索引 `limit` 选项（`0..=65535`，默认 `100`，显式设为 `0` 时同样取 `100`）作为初始 WAND top-K 批次大小而非硬性结果上限；扫描按需继续遍历后续匹配行、零分行与 `NULL` 行。 |
| 共享统计信息缓存 | 预处理的语料统计信息与增长段（growing）评分按 `(index, query)` 在 `work_mem` 预算内缓存，并在同一次执行的索引扫描与标量 `<&>` 计算之间共享（标记为 `PARALLEL RESTRICTED`）；文档总数排除 `NULL` 行，WAND 上界随 `avgdl` 漂移自动调整。 |
| 并发维护与 `VACUUM` | 第 4 版磁盘格式引入代际标记（generation stamp）、增长段与可崩溃恢复的待回收代际。`VACUUM` 与 `bm25_maintain(regclass)` 在基表 `ShareUpdateExclusiveLock` 下结合 `GlobalVis` 回收视界合并增长段，无需获取索引 `AccessExclusiveLock` 或分配事务 ID（XID）；单独执行 `ANALYZE` 不触发重建。 |
| 物理备库回放 | `VACUUM` 仅对基表上已完成修剪（pruned）的 TID 写入墓碑，备库回放堆页修剪记录时已解决快照冲突；仅当页面回收复用旧代际且备库仍有旧查询在读该代际时返回 SQLSTATE `40001`（`serialization_failure`）。 |
| 语料权限与 RLS | 索引扫描与标量 `<&>` 均检查当前角色的表级 `SELECT` 权限（普通单列非部分索引支持列级 `SELECT`），并在行级安全策略（RLS）生效时拒绝评分（`0A000`），防止通过全局语料统计信息产生侧信道泄漏；标量评分按“先锁基表、再锁索引”的顺序加锁。 |
| 构建与平台支持 | 升级至 `pgrx 0.19.3`，支持 Linux x86_64 与 aarch64 上的 PostgreSQL 14–18，支持运行时 SIMD 分发（`AVX512` / `AVX2` / `NEON`），并在页面锁外执行过滤谓词与中断检查。 |
{.wide .expand}

## 原生 `tsvector` 索引与可迁移模式 {#native-tsvector}

在 `vchord_bm25 1.0.0` 中，文档直接存储为带词素位置（`1..=16383`，每个词素最多 256 个位置）的标准 PostgreSQL `tsvector`。计算词频（`tf`）和文档长度（`dl`）时，词素的每个位置条目计作一次出现；不带位置信息的词素不参与 BM25 计分。

由于直接作用于原生 `tsvector`，可以使用 PostgreSQL 内置的 `to_tsvector(regconfig, text)` 生成文档列，也可以搭配 [`pg_tokenizer 1.0.0`](/zh/blog/release/pg-tokenizer-1.0.0/)（用 `analyze_to_tsvector` 生成字符串词素，或用 `tokenize_to_tsvector` 生成模型词元 ID 词素）：

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;

CREATE TABLE documents (
    id integer PRIMARY KEY,
    passage text NOT NULL,
    doc tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);

INSERT INTO documents (id, passage) VALUES
    (1, 'PostgreSQL full-text search with Block-WeakAnd BM25 ranking'),
    (2, 'Hybrid retrieval combining VectorChord and vchord_bm25 in PostgreSQL'),
    (3, 'Concurrent VACUUM maintenance for growing BM25 segments');

CREATE INDEX documents_doc_bm25_idx
    ON documents USING bm25 (doc bm25_ops)
    WITH (
        options = $$
        k1 = 1.2
        b = 0.75
        $$,
        limit = 100
    );

SELECT id, doc <&> to_bm25query(to_tsvector('english', 'postgresql bm25'), 'documents_doc_bm25_idx') AS score
FROM documents
ORDER BY score
LIMIT 2;
```

`1.0.0` 接口的几个主要变化：

- **查询构造器参数顺序**：`to_bm25query(vector tsvector, index regclass)` 第一个参数为查询 `tsvector`，第二个参数为目标索引 `regclass`。该函数为 `STRICT`，任一参数为 `NULL` 时返回 `NULL`。
- **负数 BM25 分数**：`<&>` 返回取反后的 `double precision`（`float8`）BM25 分数，标准升序 `ORDER BY` 即可按相关性从高到低返回结果；零分统一返回 `+0.0`。
- **支持模式迁移**：所有类型、函数、操作符与 `bm25` 访问方法均安装在扩展所在模式（默认 `public`），支持通过 `ALTER EXTENSION vchord_bm25 SET SCHEMA <schema>;` 迁移。

包含 `pg_tokenizer` 多语言分词在内的完整示例，请参阅 [BM25 索引指南](/zh/docs/bm25/usage/indexing/)与 [BM25 查询指南](/zh/docs/bm25/usage/querying/)。

## 可续扫的 WAND 检索、批次大小与共享统计缓存 {#scans-and-caching}

在 0.3.x 中，`bm25_catalog.bm25_limit` 是单次索引扫描返回候选行的硬上限。当查询同时包含 `ORDER BY ... <&> ...` 与高选择率的 `WHERE` 过滤条件时，后置过滤可能筛掉大部分前排候选，导致最终返回行数少于 `LIMIT`。

在 `1.0.0` 中，`bm25.limit`（以及索引级 `limit` 存储参数）定义为 **WAND 初始 top-K 批次大小**：

- **按需续扫**：当初始 WAND 批次消费完而执行器仍需更多行时（例如前排候选被 `WHERE` 条件过滤，或查询请求了更大的 `LIMIT` / `OFFSET`），扫描会自动继续向下遍历剩余匹配文档、零分文档与 `NULL` 行。
- **取值范围与优先级**：`bm25.limit` 与索引 `limit` 选项均支持 `0..=65535`（默认 `100`）；显式传入 `0` 时同样使用默认批次大小 `100`。任何非默认值来源的 GUC 设置（会话 `SET`、用户/数据库级设置或 `postgresql.conf`）均优先于索引上的存储选项，包括显式设为 `0` 或 `false`（`bm25.enable_scan` / `bm25.prefilter`）。由于 `limit` 是 SQL 保留关键字，在 `SET` / `SHOW` / `RESET` 中请使用双引号包裹 `"bm25.limit"`。
- **共享统计信息与增长段缓存**：语料统计信息（`N`、`avgdl` 与词项 `df`）及增长段评分按 `(index, query)` 缓存在受 `work_mem` 限制的后端内存中（按最旧优先淘汰），并在同一次执行的索引扫描与 `SELECT` 列表 / `WHERE` 子句中的标量 `<&>` 计算之间共享。统计计数包含所有非 `NULL` 物理记录（含合并前的墓碑，返回结果时立即跳过墓碑）。由于依赖后端缓存状态，`<&>` 标记为 `PARALLEL RESTRICTED`。
- **并发写入下的上界修正**：当尚未合并的增长段新行改变了实时平均文档长度（`avgdl`）时，WAND 词项上界会按比例调整，防止候选文档被提前剪枝。
- **优化器代价与快速取消**：`amcostestimate` 仅对单键 `ORDER BY` 启用索引排序路径，支持在通用执行计划（generic plan）中识别 `to_bm25query(..., const regclass)`。搜索循环在调用过滤谓词前先拷贝块跳转元数据并释放页面锁，在块间响应中断信号，使 `statement_timeout` 与 `pg_cancel_backend` 能立即生效。

## 并发维护、`VACUUM` 与物理备库回放 {#maintenance-and-vacuum}

新插入与更新的行通过尾页提示追加写入**增长段（growing segment）**，立即可被搜索，无需在每次前台写入时重写压缩倒排链。`vchord_bm25 1.0.0` 引入第 **4** 版磁盘格式，使段合并与空间回收能够与并发读写、并行 `VACUUM`、崩溃恢复及物理流复制备库协同工作：

- **自动与手动合并门槛**：每个 BM25 索引支持 `maintenance_min_rows`（默认 `1000`，范围 `0..=2147483647`）和 `maintenance_scale_factor`（默认 `0.1`，范围 `0.0..=1.0`）两个存储参数。当增长段记录数达到 `max(maintenance_min_rows, maintenance_scale_factor × 封闭段记录数)`，或墓碑数达到 `maintenance_scale_factor × 总记录数` 时，`VACUUM` 会自动合并增长段并清理墓碑。调用 `SELECT bm25_maintain('documents_doc_bm25_idx'::regclass);` 会绕过门槛直接请求维护（发布了合并新段时返回 `true`，无变化或上一待回收代际尚未回收时返回 `false`；要求表所有者权限或 PostgreSQL 17+ 的 `MAINTAIN` 权限）。
- **无需索引 `AccessExclusiveLock` 或分配事务 ID**：`VACUUM` 与 `bm25_maintain(regclass)` 仅持有基表的 `ShareUpdateExclusiveLock`，并利用 PostgreSQL 的 `GlobalVis` 回收视界判断旧页面是否可安全复用，不会在索引上获取 `AccessExclusiveLock`，也不会分配事务 ID（XID），可安全运行在并行 `VACUUM` 中。单独执行 `ANALYZE` 会直接返回，不触发索引重建。
- **可崩溃恢复的待回收代际（retired generation）**：发布合并新段时若仍有旧快照正在扫描上一代封闭段，索引会保留一个待回收代际，待后续维护确认旧快照全部结束后再回收旧页；在待回收代际回收完毕前若再次请求合并，维护会推迟而不会阻塞读写。
- **物理备库冲突处理**：由于 `VACUUM` 仅对基表上已完成修剪（heap prune）的 TID 写入墓碑，物理备库在回放先前的基表修剪 WAL 记录时已处理完快照冲突（与 PostgreSQL 原生 `nbtree` 一致）。仅当页面回收复用旧代际页面、而备库上仍有长查询正在读取该代际时，备库查询才会收到 SQLSTATE `40001`（`serialization_failure`）。

## 语料访问权限与行级安全策略（RLS） {#permissions-and-rls}

BM25 分数依赖存储在索引中的全局语料统计信息（总文档数 `N`、平均文档长度 `avgdl` 以及词项文档频率 `df`）。如果标量 `<&>` 或索引扫描不校验基表权限，无权限角色或受行级安全策略（RLS）限制的角色就可能通过分数推算隐藏行的词频分布。

`vchord_bm25 1.0.0` 在索引扫描和独立标量 `<&>` 计算两条路径上统一检查权限：

1. **表级与列级 `SELECT` 权限检查**：读取索引统计信息前，`vchord_bm25` 会验证当前角色是否拥有被索引表的 `SELECT` 权限（对于普通单列、非部分索引，拥有被索引列的列级 `SELECT` 权限亦可；表达式索引与部分索引要求表级 `SELECT` 权限）。即使 SQL 不含 `FROM` 子句、仅对传入向量计算标量得分，也会执行该检查；仅拥有视图权限并不赋予底层语料访问权。
2. **行级安全策略（RLS）限制**：当行级安全策略适用于当前角色时，`vchord_bm25` 会以 SQLSTATE `0A000`（`feature_not_supported`）拒绝标量评分和原生索引扫描，防止跨受限行泄漏语料统计信息。表所有者和 `BYPASSRLS` 角色的豁免遵循 PostgreSQL 规则（启用 `FORCE ROW LEVEL SECURITY` 后普通表所有者同样受限）；设置 `row_security = off` 不能绕过该检查。
3. **加锁顺序**：标量 `<&>` 评分在锁定 BM25 索引前先锁定基表，遵循 PostgreSQL“先基表、后索引”的加锁顺序。

## 从 0.3.x 迁移与软件包获取 {#migration-and-packages}

由于 `vchord_bm25 1.0.0` 更换了文档数据类型、扩展模式、查询构造函数参数顺序以及磁盘索引格式，`0.3.0 -> 1.0.0` 升级脚本在修改任何数据库对象前会主动报错终止 `ALTER EXTENSION vchord_bm25 UPDATE`，不会破坏现有数据。

| 特性 | `vchord_bm25 0.3.x` | `vchord_bm25 1.0.0` |
| :--- | :--- | :--- |
| 扩展模式 | 固定 `bm25_catalog`（`relocatable = false`） | 安装至目标模式（默认 `public`，`relocatable = true`） |
| 文档列类型 | `bm25_catalog.bm25vector`（`token_id:freq` 数组） | PostgreSQL 原生 `pg_catalog.tsvector`（带词素位置） |
| 查询构造函数 | `to_bm25query(regclass, bm25vector)` | `to_bm25query(tsvector, regclass)` |
| 分数返回类型 | `real`（`float4`） | `double precision`（`float8`，零分统一为 `+0.0`） |
| GUC 参数 | `bm25_catalog.bm25_limit`、`bm25_catalog.enable_index` | `"bm25.limit"`、`bm25.enable_scan`、`bm25.prefilter` |
| 段维护方式 | 需执行 `REINDEX` 才能手动合并增长段 | `bm25_maintain(regclass)` + `VACUUM` 自动合并门槛 |
{.wide .expand}

从 0.3.x 迁移时，请保留原始文本列，在具有独立扩展库目录的新 PostgreSQL 安装或容器环境中安装 `1.0.0` 软件包，生成原生 `tsvector` 列并重建 `USING bm25 (doc bm25_ops)` 索引。详细步骤请参阅 [BM25 迁移指南](/zh/docs/bm25/reference/migration/)。

面向 PostgreSQL **14–18**、覆盖 16 个 Linux 发行版（`x86_64` 与 `aarch64`）的原生 RPM 与 DEB 软件包（`1.0.0-1PIGSTY` / `1.0.0-1PGSTY`）已发布在[下载页面](/zh/download/)。更多配置细节请参阅 [BM25 SQL 参考](/zh/docs/bm25/reference/sql/)、[GUC 参数参考](/zh/docs/bm25/reference/gucs/)与 [SBOM 页面](/zh/docs/about/sbom/)。
