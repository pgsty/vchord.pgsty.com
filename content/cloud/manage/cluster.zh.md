---
title: "集群"
linkTitle: "集群"
description: "一个项目中可以创建一个或多个集群。集群是运行单个 Postgres 集群的一组节点集合。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/cluster.md"
---

一个项目中可以创建一个或多个集群。集群是运行单个 `Postgres` 集群的一组节点集合。

## 创建集群 {#create-a-cluster}

要创建新集群，请前往 VectorChord Cloud 控制台并点击“Create Cluster”按钮。

![](/cloud/images/after_login_in.png)

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


## 删除集群 {#delete-a-cluster}

如果您想删除集群，请前往 VectorChord Cloud 控制台并点击“Delete”按钮。

![](/cloud/images/delete_cluster.png)

> [!WARNING]
> 一旦删除该集群，Postgres 中的所有数据（包括 WAL 日志）以及集群中自动创建或按需创建的备份也将一并被删除。


## 集群监控 {#cluster-monitoring}

您可以在集群信息页面查看集群的 CPU 和内存使用情况，还可以查看索引信息，例如索引中的向量数量、向量维度等。有关监控的详细信息，请参阅[监控](/zh/cloud/monitoring/monitoring/)。

![](/cloud/images/monitoring.png)
