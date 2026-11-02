---
title: "云端对象层级结构概览"
linkTitle: "概览"
description: "管理您的 VectorChord Cloud 项目需要了解其对象层级结构。下图展示了云端各对象之间的关系，下文对每个对象进行了详细说明。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/overview.md"
---

管理您的 VectorChord Cloud 项目需要了解其对象层级结构。下图展示了云端各对象之间的关系，下文对每个对象进行了详细说明。
![](/cloud/images/cloud_object_hierarchy.png)

## VectorChord Cloud 账户 {#vectorchord-cloud-account}

这是您用于注册 VectorChord Cloud 的账户。目前支持使用 GitHub 账户注册。

<a id="Projects"></a>
## 项目 {#projects}

项目（Project）是层级结构中的顶层对象。它是该项目下所有集群和计费信息的容器。有关更多信息，请参阅[项目](/zh/cloud/manage/project/)。

<a id="Clusters"></a>
## 集群 {#clusters}

一个项目可以包含一个或多个集群（Cluster）。集群是运行单个 `Postgres` 集群的一组节点集合。有关更多信息，请参阅[集群](/zh/cloud/manage/cluster/)。

## 计算实例 {#compute-instances}

一个集群可以包含一个或多个计算实例（Compute Instance）。计算实例是运行 `Postgres` 实例的虚拟机。

<a id="Databases"></a>
## 数据库 {#databases}

每个集群包含两个默认数据库：`postgres` 以及您在创建集群时命名的数据库。集群就绪后，您可以使用 [psql](/zh/cloud/connect/connect-with-psql/) 在集群中创建更多数据库。
