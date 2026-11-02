---
title: "工作流"
linkTitle: "工作流"
description: "工作流（Workflow）是一项允许您使用预定义函数完成特定任务的功能，例如使用 ExternalBuildIndex 工作流在外部构建索引。"
weight: 100
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/workflow.md"
---

<a id="Overview"></a>
## 概览 {#overview}

工作流（Workflow）是一项允许您使用预定义函数完成特定任务的功能。例如，您可以使用 [`ExternalBuildIndex`](#ExternalBuildIndex) 工作流在集群外部为您的 Postgres 集群构建索引。使用工作流具有以下优势：
- **开箱即用（Out Of Box）**：无需编写任何代码即可使用预定义函数完成特定任务。
- **加速任务执行（Accelerate Tasks）**：可以使用比 PostgreSQL 集群更高资源配置的服务器来加速任务处理。
- **保障集群稳定性（Cluster Stability）**：工作流在独立的服务器上执行，不会影响 PostgreSQL 集群自身的稳定性。
- **低成本（Low Cost）**：对于短期任务，您无需像维护数据库那样持续为高配资源付费。

## 支持的工作流 {#supported-workflows}

目前支持的工作流如下：
- [ExternalBuildIndex](#ExternalBuildIndex)

<a id="externalbuildindex"></a>
### ExternalBuildIndex {#ExternalBuildIndex}

`ExternalBuildIndex` 工作流用于在集群外部为您的 Postgres 集群构建 `vchord` 索引，详细原理可参阅[外部构建索引](/zh/docs/usage/external-build/)。

![](/cloud/images/create_workflow.png)

在控制台中，您可以点击 `Create Workflow` 按钮创建一个新工作流。

![](/cloud/images/external-build-index.png)

您需要指定以下信息：
- **Workflow Name**（工作流名称）：工作流的唯一名称。
- **Option**（选项）：`ExternalBuildIndex` 工作流的参数选项
    - **Table**（表名）：向量所在的表名
    - **Column**（列名）：向量列名称
    - **Dimension**（维度）：向量的维度
    - **Lists**（聚类中心数）：KMeans 的列表数量（n list）
    - **DistanceMetric**（距离度量）：向量的距离度量方式
        - **DistanceMetricCosine**：余弦距离（Cosine distance）
        - **DistanceMetricL2**：欧氏距离（Euclidean distance）
        - **DistanceMetricDot**：点积距离（Dot product distance）

提交工作流后，工作流将进入 `Running` 状态。在运行过程中工作流不可操作，整个运行过程可能需要几分钟时间。运行完成后，工作流状态将变为 `Succeeded`。您可以在控制台中列出所有工作流。

![](/cloud/images/workflow-list.png)

您可以在工作流详情页面查看每个步骤的执行详情。

![](/cloud/images/after-submit-external-build-index.png)

当工作流处于 `Succeeded` 状态时，您可以验证索引是否已就绪可用。

![](/cloud/images/external-build-index-succeeded.png)

```shell
$ psql 'postgres://vectorchord_user:C8bTXXFi2vxA@vectorchord-oews3hvirnsq3vi7.us-east-1-dev.aws.vectorchord.com:5432/vectorchord?sslmode=require'
psql (15.3, server 16.5)
WARNING: psql major version 15, server major version 16.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.
vectorchord=# EXPLAIN ANALYZE SELECT * FROM sift ORDER BY embedding <-> '[12,47,14,25,2,3,4,7,14,122,90,7,0,0,6,14,0,24,122,22,2,4,6,0,0,10,93,10,6,6,0,0,122,31,9,23,19,9,8,56,122,100,29,19,3,0,0,25,3,9,43,59,76,32,0,0,8,6,10,7,24,58,1,1,81,23,32,68,14,19,10,23,122,13,2,1,4,9,86,122,3,0,0,8,122,95,68,30,9,2,0,2,26,50,44,13,0,0,0,3,12,82,18,7,6,0,0,0,2,20,112,122,6,5,1,0,3,69,122,43,15,1,0,0,0,27,29,21]' LIMIT 5;
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
 Limit  (cost=0.00..1.85 rows=5 width=532) (actual time=0.644..0.683 rows=5 loops=1)
   ->  Index Scan using sift_embedding_idx on sift  (cost=0.00..73962.25 rows=200012 width=532) (actual time=0.643..0.681 rows=5 loops=1)
         Order By: (embedding <-> '[12,47,14,25,2,3,4,7,14,122,90,7,0,0,6,14,0,24,122,22,2,4,6,0,0,10,93,10,6,6,0,0,122,31,9,23,19,9,8,56,122,100,29,19,3,0,0,25,3,9,43,59,76,32,0,0,8,6,10,7,24,58,1,1,81,23,32,68,14,19,10,23,122,13,2,1,4,9,86,122,3,0,0,8,122,95,68,30,9,2,0,2,26,50,44,13,0,0,0,3,12,82,18,7,6,0,0,0,2,20,112,122,6,5,1,0,3,69,122,43,15,1,0,0,0,27,29,21]'::vector)
 Planning Time: 0.069 ms
 Execution Time: 0.710 ms
(5 rows)
```
