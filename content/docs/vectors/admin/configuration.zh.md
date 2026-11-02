---
title: "配置"
linkTitle: "配置"
description: "默认情况下无法捕获所有 pgvecto.rs 日志。pgvecto.rs 会启动后台工作进程进行索引构建并将日志输出到标准错误，需要开启 logging_collector 来捕获日志。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/configuration.md"
aliases:
  - "/admin/configuration/"
---

<a id="Logging"></a>
## 日志配置 {#logging}

默认情况下，你无法捕获 `pgvecto.rs` 的全部日志。`pgvecto.rs` 会启动一个后台工作进程（Background Worker）来构建索引，并将日志输出到标准错误（stderr）。若要捕获这些日志，你需要将 `logging_collector` 设置为 `on`。更多详情可参阅 [PostgreSQL 关于日志收集器的官方文档](https://www.postgresql.org/docs/current/runtime-config-logging.html#GUC-LOGGING-COLLECTOR)。

你可以通过以下命令将 `logging_collector` 设置为 `on`：

```sh
psql -U postgres -c 'ALTER SYSTEM SET logging_collector = on;'
# 需要重启 PostgreSQL 集群以使配置生效。
sudo systemctl restart postgresql.service   # 适用于通过 systemd 运行的 pgvecto.rs
docker restart pgvecto-rs-demo  # 适用于在 Docker 中运行的 pgvecto.rs
```

## 索引配置 {#index-configuration}

{{< badge text="自 v0.3.0 起" tone="info" >}}

对于每个索引，都有若干可动态调整的配置项。与创建时的静态选项（options）不同，这些配置项支持在索引创建后进行实时修改。你可以通过 `alter_vector_index` 函数来修改这些配置项。

```sql
-- alter_vector_index(dim: OID, key: TEXT, value: TEXT)
SELECT alter_vector_index('index_name'::regclass::oid, 'configuration_name', 'value');
```

目前支持的所有配置项如下：

### 后端优化线程数 {#threads-for-backend-optimizing}

默认情况下，每个向量索引在后端仅由一个线程执行优化。如果你有多个空闲 CPU 核心并希望充分利用它们，可以增加优化线程的数量。

将 `key` 参数设置为 `optimizing.threads`，并将 `value` 参数设置为期望的线程数：

```sql
-- alter_vector_index(dim: OID, key = 'optimizing.threads', value: TEXT as INT[1-65535])
SELECT alter_vector_index('table_col_idx'::regclass::oid, 'optimizing.threads', '4');
```
