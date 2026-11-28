---
title: "性能调优"
linkTitle: "性能调优"
description: "决定 vchord 构建时间和查询延迟的 PostgreSQL 设置：并行构建、shared_buffers、重启后预热，以及从磁盘读取页面的方式。"
weight: 100
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/postgresql-tuning.md"
aliases:
  - "/docs/usage/postgresql-tuning/"
  - "/vectorchord/usage/postgresql-tuning/"
  - "/docs/vchord/usage/performance-tuning/"
  - "/vectorchord/usage/performance-tuning/"
  - "/docs/vchord/usage/prewarm/"
  - "/docs/usage/prewarm/"
  - "/docs/vchord/usage/prefetch/"
  - "/docs/usage/prefetch/"
icon: fa-solid fa-gauge-high
---

索引的召回率调好之后，剩下的速度取决于 PostgreSQL：用多少个进程来构建、查询需要的页面是否在内存里、其余的页面怎样从磁盘读取。本页按这个顺序介绍相关设置。默认值已经合理；构建太慢、重启后查询变慢，或者索引比内存大时，再来调整。

## 并行构建索引 {#parallel-index-builds}

在 PostgreSQL 17 及以上版本，`CREATE INDEX` 和 `REINDEX` 会用并行工作进程向 vchordrq 和 vchordg 索引插入行。vchordrq 的 k-means 步骤是单独的，使用自己的 [`build_threads`](/zh/docs/vchord/usage/indexing/#build)。

用 16 个进程（1 个主进程加 15 个工作进程）构建：

```sql
-- 需要重启；给其他后台工作进程留出余量。
ALTER SYSTEM SET max_worker_processes = 24;

-- 在执行 CREATE INDEX 的会话中：
SET max_parallel_workers = 15;
SET max_parallel_maintenance_workers = 15;
```

PostgreSQL 根据表的大小决定启动多少个工作进程，对刚导入数据的表可能启动得比允许的少。要固定这个数量，在表上设置：

```sql
ALTER TABLE items SET (parallel_workers = 15);
```

临时表上的构建，以及带有并行不安全表达式或 `WHERE` 谓词的索引，只用单个进程构建。

## 让索引留在内存里 {#shared-buffers}

查询读的页面都在 `shared_buffers` 里时最快。要读哪些页面取决于索引类型：

- **vchordrq**：每次查询都读聚类中心，再加上被探查列表的 RaBitQ 编码。全精度向量只为需要重排的候选读取。
- **vchordg**：遍历路径上的 RaBitQ 编码和邻居列表，以及最终候选的全精度向量。

`shared_buffers` 至少要放得下聚类中心，最好也放得下编码。专门做向量检索的服务器，可以分给它比通常的 25% 更大的内存比例。修改需要重启：

```sql
ALTER SYSTEM SET shared_buffers = '16GB';
```

### 重启后预热 {#prewarm}

<a id="usage"></a><a id="privileges"></a>

重启或故障切换之后，`shared_buffers` 是空的，最初的查询都要读磁盘。对索引执行 `pg_prewarm` 会载入所有页面，包括全精度向量，索引比内存大时反而会挤掉更有用的页面。vchord 自带的函数只载入查询需要的部分：

```sql
-- vchordrq：聚类中心和所有列表的 RaBitQ 编码
SELECT vchordrq_prewarm('items_embedding_idx');

-- vchordrq：列表放不进 shared_buffers 时，只载入聚类中心
SELECT vchordrq_prewarm('items_embedding_idx', 1);

-- vchordg：图的编码和邻居列表
SELECT vchordg_prewarm('items_graph_idx');
```

每个函数都会返回一段已载入内容的简要汇总。调用者需要拥有该表或有表的 `SELECT` 权限。

## 高效读取磁盘 {#prefetch}

<a id="prefetch-modes"></a><a id="io-and-jit"></a>

页面不在内存里时，vchord 会提前请求接下来要用的页面，让存储在 CPU 计算距离的同时工作。在 PostgreSQL 17 及以上版本，它在合适的地方使用 PostgreSQL 的 read stream，其余情况使用 `posix_fadvise` 提示。这一行为默认开启。在 NVMe 上，可以让 PostgreSQL 同时发出更多读取：

```sql
SET effective_io_concurrency = 20;
SET maintenance_io_concurrency = 20;
```

[参考](#reference)中的 `io_search` 和 `io_rerank` 决定查询各阶段的读取方式。除非在做测量，否则保持默认；索引能完全放进 `shared_buffers` 时，各模式的表现相同。

JIT 编译会增加向量查询的规划时间，却加速不了其中任何部分。为提供向量检索的数据库关闭它：

```sql
ALTER DATABASE app SET jit = off;
```

### PostgreSQL 18 的异步 I/O {#asynchronous-i-o}

<a id="worker"></a><a id="io-uring"></a><a id="sync"></a>

PostgreSQL 18 以异步方式执行 read stream，让更多读取相互重叠。`io_method` 决定具体方式，修改需要重启：

- `worker`（默认）把读取交给后台 I/O 工作进程。索引远大于内存时调高 `io_workers`。
- `io_uring` 直接向 Linux 内核提交读取，省去转交的开销。它需要为 PostgreSQL 调高打开文件数和锁定内存的上限，而且一些容器运行时的默认 seccomp 配置会禁止它；遇到这种情况就退回 `worker`。
- `sync` 关闭异步读取，只用于对比测试。

```sql
ALTER SYSTEM SET io_method = 'io_uring';
```

[Tuning AIO in PostgreSQL 18](https://vondra.me/posts/tuning-aio-in-postgresql-18/) 对其中的取舍有更深入的说明。

## 参考 {#reference}

### I/O 设置 {#io-settings}

<a id="search-parameters"></a><a id="search-parameters-vchordrq"></a><a id="search-parameters-vchordg"></a><a id="vchordrq-io-search"></a><a id="vchordrq-io-rerank"></a><a id="vchordg-io-search"></a><a id="vchordg-io-rerank"></a>

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `vchordrq.io_search` | enum | PG 17+ 为 `mixed`，15–16 为 `prefetch_buffer` | 读取列表页面的方式。`mixed` 在页面大多连续的地方用 read stream，其他地方用 `prefetch_buffer`；`io_method` 不是 `worker` 时全程用 read stream。 |
| `vchordrq.io_rerank` | enum | `prefetch_buffer` | 重排时读取向量和表页面的方式。重排的页面是分散的，所以默认不用 read stream。 |
| `vchordg.io_search` | enum | PG 17+ 为 `read_stream`，15–16 为 `prefetch_buffer` | 遍历图时读取页面的方式。 |
| `vchordg.io_rerank` | enum | PG 17+ 为 `read_stream`，15–16 为 `prefetch_buffer` | 重排时读取全精度向量的方式。 |
{.fields meta="type default"}

可选值为 `read_buffer`（不预读）、`prefetch_buffer`（`posix_fadvise` 提示），以及 PostgreSQL 17 及以上版本才有的 `read_stream` 和仅 `vchordrq.io_search` 可用的 `mixed`。

### 预热函数 {#functions}

<a id="functions-vchordrq"></a><a id="functions-vchordg"></a><a id="vchordrq-prewarm"></a><a id="vchordg-prewarm"></a><a id="vchordrq-prewarm-func"></a><a id="vchordg-prewarm-func"></a>

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `vchordrq_prewarm(index regclass, height integer DEFAULT 0)` | text | 从根部向下载入索引直到 `height` 层：`0` 包括所有列表的 RaBitQ 编码，`1` 只载入聚类中心。全精度向量永远不会载入。 |
| `vchordg_prewarm(index regclass)` | text | 载入图的 RaBitQ 编码和邻居列表。 |
{.fields meta="type"}
