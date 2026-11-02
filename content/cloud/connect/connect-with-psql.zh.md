---
title: "使用 psql 连接"
linkTitle: "使用 psql 连接"
description: "以下操作说明要求您已安装并可正常使用 psql。psql 客户端是 Postgres 的原生命令行客户端，提供交互式会话以向 Postgres 发送命令并运行即席查询。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/connect/connect-with-psql.md"
---

以下操作说明要求您已安装并可正常使用 [psql](https://www.postgresql.org/download/)。`psql` 客户端是 Postgres 的原生命令行客户端，提供交互式会话，用于向 Postgres 发送命令并运行即席查询。有关 `psql` 的更多信息，请参阅 PostgreSQL 文档中的 [psql 参考手册](https://www.postgresql.org/docs/15/app-psql.html)。

> [!WARNING]
> 集群实例运行的是标准 Postgres，这意味着任何 Postgres 应用程序或标准工具（如 `psql`）都与 VectorChord Cloud 兼容。您也可以使用各类 Postgres 客户端库和驱动程序进行连接。但请注意，部分较旧的客户端库和驱动程序（包括较旧版本的 `psql` 可执行文件）在编译时未启用 [服务器名称指示（SNI）](https://en.wikipedia.org/wiki/Server_Name_Indication) 支持，需要额外的变通方案。


使用 `psql` 连接 VectorChord Cloud 最简单的方法是使用连接端点（Connection Endpoint）。您可以从控制台仪表盘的**集群详情（Cluster Details）**页面获取连接端点。

![](/cloud/images/two_types_connections.png)

我们提供两种类型的连接端点：
- **Super User Endpoint**（超级用户端点）：该连接字符串用于以超级用户（`postgres`）身份连接到集群。您可以使用此连接字符串创建数据库、创建用户以及管理集群。
- **Vector User Endpoint**（向量用户端点）：该连接字符串用于以向量用户身份连接到集群。您可以使用此连接字符串存储和查询向量数据。

如果在创建集群时勾选了 `Enable Connection Pooler`，您可以点击 `Show Pooler Endpoint` 按钮获取连接池连接端点。

![](/cloud/images/two_types_pooler_connections.png)

在终端或命令提示符下，使用从 **Dashboard** 复制的连接端点运行 `psql` 客户端：

```shell
$ psql postgres://[user]:[password]@[hostname]/[dbname]
```

> [!WARNING]
> VectorChord Cloud 要求所有连接均使用 SSL/TLS 加密，您也可以通过在连接字符串后追加 `sslmode` 参数设置来进一步提升安全保护级别。
