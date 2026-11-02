---
title: "PostgreSQL 调优"
linkTitle: "PostgreSQL 调优"
description: "索引构建可以并行化执行。由于并行化会增加服务器负载，PostgreSQL 默认未启用它。请参考本文配置并行构建、I/O 与共享缓冲区。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/postgresql-tuning.md"
aliases:
  - "/zh/docs/usage/postgresql-tuning/"
  - "/vectorchord/usage/postgresql-tuning/"
  - "/docs/vchord/usage/performance-tuning/"
  - "/vectorchord/usage/performance-tuning/"
---

索引构建可以并行化执行。由于并行化会增加服务器负载，PostgreSQL 默认并未启用。如需启用并行构建，请参考以下 SQL 配置：

```sql
-- 设置数据库集群可支持的最大后台进程数。
-- 建议将其设置为至少等于您期望的并行度加上 8。
-- 例如，如果您希望使用 16 个线程进行并行处理，请将该值至少设置为 24。
-- 根据您的实际工作负载，将该值设置得更高可能会更有帮助。
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET max_worker_processes = 24;

-- 设置数据库集群可用于并行操作的最大工作进程数。
-- 建议将其设置为您期望的并行度减 1。
-- 例如，如果您希望使用 16 个线程进行并行处理，请将该值设置为 15。
SET max_parallel_workers = 15;

-- 设置单个维护命令（如 CREATE INDEX）可启动的最大并行工作进程数。
-- 建议将其设置为您期望的并行度减 1。
-- 例如，如果您希望使用 16 个线程进行并行处理，请将该值设置为 15。
SET max_parallel_maintenance_workers = 15;
```

并行工作进程的数量还取决于表本身的配置。默认情况下，该值由 PostgreSQL 自动计算决定。如果 PostgreSQL 判定不启用并行，那么并行索引构建就不会生效。您可以通过调整表的 `parallel_workers` 存储参数来覆盖 PostgreSQL 的默认行为，强制启用并行索引构建。

```sql
ALTER TABLE items set (parallel_workers = 15);
```

您还需要调整以下几个设置以提升 I/O 性能：

```sql
-- 设置 PostgreSQL 预期可同时执行的并发磁盘 I/O 操作数。
-- 使用 SSD 存储时，建议将其设置为 20。
SET effective_io_concurrency = 20;
SET maintenance_io_concurrency = 20;
```

我们观察到在某些情况下，工作异常的 JIT（即时编译）可能会对性能产生负面影响。如果您并不依赖它，可以选择将其禁用。

```sql
SET jit = off;
```

最后，您需要设置 PostgreSQL 共享缓冲区（shared buffers）的大小。

```sql
-- 设置数据库服务器用于共享内存缓冲区的内存量。
-- 根据您的工作负载，通常建议将该值设置为总内存的 25%~40%。
-- 对于向量数据库工作负载，将该值设置为总内存的 80% 往往更有优势。
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET shared_buffers = '16GB';
```

## 异步 I/O {#asynchronous-i-o}

PostgreSQL 17 首次引入了流式 I/O（streaming I/O）API。在此基础上，PostgreSQL 18 引入了异步 I/O（Asynchronous I/O）。借助异步 I/O，PostgreSQL 可以同时发起多个读取操作，并在等待结果返回的同时继续处理其他任务。这能够显著提升需要从磁盘读取大量数据的查询性能。PostgreSQL 提供了多种异步 I/O 方式，您可以根据需要进行调整。

本节内容仅适用于 PostgreSQL 18。

<a id="io-uring"></a>
### `io_uring` {#io_uring}

`io_uring` 方式使用 Linux 内核的 `io_uring` 接口，能够减少上下文切换的开销。该接口在 Linux 内核 5.1 及更高版本中可用。您可以通过 GUC 参数 `io_method` 启用此方式。

```sql
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET io_method = 'io_uring';
```

由于 `io_uring` 会使用额外的文件描述符和锁定内存（locked memory），PostgreSQL 可能会触及系统的 `RLIMIT_NOFILE` 和 `RLIMIT_MEMLOCK` 限制。您可能需要在操作系统层面调高这些限制。另请参阅：

* [limits.conf (PAM)](https://www.man7.org/linux/man-pages/man5/limits.conf.5.html)
* [Process Properties (systemd)](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Process%20Properties)
* [Set ulimits in container (Docker)](https://docs.docker.com/reference/cli/docker/container/run/#ulimit)

出于安全考虑，容器运行时、云服务商或系统管理员可能会禁用 `io_uring`。如果遇到此类情况，请向您的服务提供商咨询详情。另请参阅：

* [Consider removing io_uring syscalls in from RuntimeDefault (containerd)](https://github.com/containerd/containerd/issues/9048)

通常推荐使用 `io_uring`，但实际性能表现仍取决于您的具体工作负载。另请参阅：

* [Tuning AIO in PostgreSQL 18 (Tomas Vondra)](https://vondra.me/posts/tuning-aio-in-postgresql-18/)
* [Benchmarking Postgres 17 vs 18 (planetscale)](https://planetscale.com/blog/benchmarking-postgres-17-vs-18)

本小节仅适用于 Linux 系统。

### `worker` {#worker}

这是 PostgreSQL 18 中的默认设置。PostgreSQL 通过将 I/O 请求发送到专门的进程池来避免阻塞后端进程。您可以通过 GUC 参数 `io_method` 显式启用此方式。

```sql
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET io_method = 'worker';

-- 选择要使用的 I/O 工作进程数量。
-- 建议将其设置为您的并行度与参数上限值之间的较小者。
-- 例如，如果您的并行度为 16，请将该值设置为 16。
-- 该参数的最大值为 32，因此不能设置超过 32 的值。
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET io_workers = 16;
```

### `sync` {#sync}

`sync` 方式的工作机制与 PostgreSQL 17 相同：读取操作是同步且阻塞的，并使用 `posix_fadvise` 向操作系统提供即将发生的读取提示。通常只有在调试时才会使用此方式。您可以通过 GUC 参数 `io_method` 启用此方式。

```sql
-- 注意：此设置需要重启数据库才能生效。
ALTER SYSTEM SET io_method = 'sync';
```
