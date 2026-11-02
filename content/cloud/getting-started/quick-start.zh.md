---
title: "快速开始"
linkTitle: "快速开始"
description: "本指南将帮助您快速上手 VectorChord Cloud。首先，您需要注册一个 VectorChord Cloud 账户。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/getting-started/quick-start.md"
---

本指南将帮助您快速上手 VectorChord Cloud。首先，您需要注册一个 VectorChord Cloud 账户。如果您还没有账户，可以在[此处](/zh/cloud/getting-started/sign-up/)免费注册。

## 创建集群 {#create-a-cluster}

> [!TIP]
> 您需要先绑定[信用卡](/zh/cloud/payment/credit-card/)，然后才能创建企业版（Enterprise）套餐集群。


![](/cloud/images/after_login_in.png)

要创建新集群，请前往 VectorChord Cloud 控制台并点击“Create Cluster”按钮。

![](/cloud/images/create_cluster.png)

您需要指定以下信息：
- 必填项：
  - **Plan**（套餐）：您希望用于该集群的套餐。有关 Cloud 付费套餐选项的详细信息，请参阅 [Cloud 套餐](/zh/cloud/pricing/price-plan/)。
  - **Cluster Name**（集群名称）：集群的唯一名称。
  - **Extension Settings**（扩展设置）：
    - **Extension**（扩展）：我们支持两种向量搜索扩展：[pgvectors](https://github.com/tensorchord/pgvecto.rs) 及其继任者 [vectorchord](https://github.com/pgsty/vchord)
      - **vectorchord**：Postgres 中可扩展、快速且磁盘友好的向量搜索扩展
      - **pgvectors**：Postgres 中可扩展、低延迟且支持混合搜索的向量搜索扩展。革新向量搜索，而非更换数据库。
      > [!WARNING]
      > `vectorchord` 仅支持配备 NVMe SSD 的服务器资源规格。

    - **Image**（镜像）：
      - 对于 VectorChord，我们提供语义化版本格式的标签，例如 `16-v0.1.0`：
        - `16` 表示 Postgres 主版本号
        - `v0.1.0` 表示 VectorChord 版本号
      - 对于 pgvecto.rs，我们提供语义化版本格式的标签，例如 `16-v0.4.0-vectors-exts`：
        - `16` 表示 Postgres 主版本号
        - `v0.4.0` 表示 pgvecto.rs 版本号
        - `vectors` 表示 pgvecto.rs schema 的安装位置，可选值为 `vectors`、`extensions`、`public`。如果您希望在 AWS RDS 上搭配使用 VectorChord Cloud，请选择 `public`。如果您打算在 Supabase 上使用 FDW，请选择 `extensions`。
        - `exts` 表示集群支持从 https://pgt.dev/ 安装扩展。
  - **Cloud Provider Settings**（云厂商设置）：
    - **Cloud Provider**（云厂商）：部署集群的云服务提供商，目前仅支持 AWS。
    - **Region**（区域）：部署集群所在的区域。
  - **Resource Settings**（资源设置）：
    - **Type**（类型）：我们提供两种资源类型：`Performance`（性能型）和 `Capacity`（容量型）。
    - **Server Resource**（服务器资源规格）：
      - **Performance**（性能型）：
        - **1C/2G**：免费套餐，1 核 CPU、2GB 内存和 3Gi 磁盘空间。
        - **2C/8G**：企业版套餐，2 核 CPU、8GB 内存和 15Gi 磁盘空间。
        - **2C/16G**：企业版套餐，2 核 CPU、16GB 内存和 15Gi 磁盘空间。
        - **4C/32G**：企业版套餐，4 核 CPU、32GB 内存和 90Gi 磁盘空间。
      - **Capacity**（容量型）：
        - **4C/32G NVMe SSD**：企业版套餐，4 核 CPU、32GB 内存和 850Gi NVMe SSD 磁盘空间。
  - **Postgres Settings**（Postgres 设置）：
    - **Database Name**（数据库名称）：用于存储向量数据的数据库名称。
    - **Enable Connection Pooler**（启用连接池，默认值：`false`）：为集群启用连接池。
    - **Enable Restore Config**（启用恢复配置，默认值：`false`）：启用恢复配置，以从其他集群创建的备份进行恢复。
    - **Optional**（可选项）：
      - **Disk Size**（磁盘大小）：Postgres PGData 磁盘大小，将覆盖默认磁盘大小。
      - **Instances**（实例数）：集群中的实例数量，默认值为 1。
      > [!WARNING]
      > 目前向量索引尚不支持流复制（Streaming Replication）。


## 集群信息 {#cluster-info}

创建集群后，系统会将您引导至集群信息页面。在这里，您可以查看集群的详细信息，例如连接字符串、集群状态以及集群的资源使用情况。

![](/cloud/images/cluster_info.png)

我们提供两种类型的连接端点，分别是 `Super User Endpoint`（超级用户端点）和 `Vector User Endpoint`（向量用户端点）。有关这两种连接方式的更多信息，请参阅[使用 psql 连接](/zh/cloud/connect/connect-with-psql/)。

![](/cloud/images/two_types_connections.png)

如果在创建集群时勾选了 `Enable Connection Pooler`，您可以点击 `Show Pooler Endpoint` 按钮获取连接池端点。

![](/cloud/images/two_types_pooler_connections.png)

## 连接到集群 {#connect-to-the-cluster}

要连接到集群，您可以使用页面提供的连接字符串，并通过 `psql` 命令行工具进行连接。有关如何连接到集群的详细说明，请参阅[使用 psql 连接 VectorChord Cloud](/zh/cloud/connect/connect-with-psql/)。连接到集群后，我们可以执行 `\dx` 命令来验证 `vectors` 扩展是否已成功安装。

```shell
$ psql 'postgres://test_user:vaBgs6CcrtMu@test-f5ys31pvbca4x6f9.us-east-1-dev.aws.vectorchord.com:5432/test?sslmode=require'
psql (15.3, server 16.5)
WARNING: psql major version 15, server major version 16.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

test=> \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description
---------+---------+------------+----------------------------------------------------------------------------------------------
 pgaudit | 16.0    | public     | provides auditing functionality
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vectors | 0.4.0   | vectors    | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
(3 rows)
```

## 创建索引 {#create-index}

在快速开始中，我们将创建一个简单的索引。如果您想创建更高级的索引，请参阅[索引参考文档](/zh/docs/usage/indexing/)。我们还提供了丰富的使用场景示例，请参阅[使用案例](/zh/docs/use-case/)。

```sql
test=> CREATE TABLE test (id integer PRIMARY KEY, embedding vector(3) NOT NULL);
CREATE TABLE
test=> INSERT INTO test SELECT i, ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 100) i;
INSERT 0 100
test=> CREATE INDEX ON test USING vectors (embedding vector_l2_ops) WITH (options = "[indexing.hnsw]");
CREATE INDEX
test=> SELECT * FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402]' LIMIT 10;
 id |              embedding
----+--------------------------------------
 53 | [0.49730784, 0.3848221, 0.28655913]
 19 | [0.54001766, 0.40314186, 0.44689152]
 62 | [0.6388231, 0.20029141, 0.34409937]
 97 | [0.5666403, 0.24310996, 0.1873124]
 30 | [0.21831545, 0.31599918, 0.21045132]
 10 | [0.5354302, 0.44377843, 0.26784408]
 48 | [0.19506525, 0.3632655, 0.24503356]
 76 | [0.283386, 0.5032842, 0.32678106]
 35 | [0.23225804, 0.051908802, 0.5431633]
 56 | [0.5288183, 0.28127462, 0.078518875]
(10 rows)
```

<a id="Monitoring"></a>
## 监控 {#monitoring}

您可以在监控指标（Metrics）页面查看集群的 CPU 使用率、内存使用量以及 PGData 磁盘总量与已用空间。您还可以查看索引信息，例如索引中的向量数量、向量维度等。有关监控的详细信息，请参阅[监控](/zh/cloud/monitoring/monitoring/)。
![](/cloud/images/monitoring.png)
