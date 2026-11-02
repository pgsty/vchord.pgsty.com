---
title: "监控指标"
linkTitle: "监控指标"
description: "VectorChord Cloud 提供多张图表，用于监控系统和数据库指标。您可以从 VectorChord Cloud 控制台的集群详情页进入 Metrics 仪表盘。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/monitoring/monitoring.md"
---

VectorChord Cloud 提供多张图表，用于监控系统和数据库指标。您可以从 VectorChord Cloud 控制台的集群详情页进入 **Metrics** 仪表盘。可观测的指标包括：
- [存储使用量](#storage-usage)
- [内存（RAM）](#ram)
- [CPU](#cpu)
- [向量索引](#vector)

## 存储使用量 {#storage-usage}

该图表展示了 Postgres 实例的存储总量与已用空间。
![](/cloud/images/storage-usage.png)

<a id="RAM"></a>
## 内存（RAM） {#ram}

该图表展示了 Postgres 实例的平均内存使用量，单位为 MB。

![](/cloud/images/memory_usage.png)

<a id="CPU"></a>
## CPU {#cpu}

该图表展示了过去 5 分钟内 Postgres 实例的平均 CPU 使用率百分比。

![](/cloud/images/cpu_utilization.png)

<a id="Vector"></a>
## 向量索引 {#vector}

该图表展示了向量索引的详细信息，包含以下指标：
- **Index Name**（索引名称）：索引的名称。
- **Index Dimension**（索引维度）：索引中向量的维度。
- **Index Vector Count**（索引向量数量）：索引中的向量条数。
- **Index Options**（索引选项）：有关索引选项的详细信息，请参阅[索引选项](/zh/docs/usage/indexing/#indexing-options)。
- **Indexing**（构建状态）：如果为 `True`，则表示该索引正在对数据进行索引构建。

![](/cloud/images/indexes.png)
