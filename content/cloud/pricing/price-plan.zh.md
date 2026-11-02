---
title: "Cloud 价格方案"
linkTitle: "Cloud 价格方案"
description: "在 VectorChord Cloud 中，我们提供免费套餐，方便您在云端环境中学习和体验全托管的 VectorChord 服务。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/pricing/price-plan.md"
---

## 免费套餐 {#free-tier}

在 VectorChord Cloud 中，我们提供免费套餐（Free Tier），方便您在云端环境中学习和探索全托管的 VectorChord 服务。每位用户可以使用免费套餐创建**仅一个**集群并在其中存储向量数据。免费套餐包含以下限制：
- 共享计算资源
- 受限的 WAL（预写式日志）和 PGData 存储空间（5Gi）
- 仅支持 AWS T3 XLarge 实例类型
- 预估可容纳约 10 万条 1024 维向量，或者插入约 2.5 万条 4096 维向量。

<a id="Enterprise"></a>
## 企业版 {#enterprise}

在企业版（Enterprise）套餐中，您可以拥有独享集群，并获得以下特性：
- 独享计算资源
- 更大的 WAL 和 PGData 存储空间
- 支持更多实例类型
- 多种容量配置选项

## 服务器资源规格 {#server-resources}

### 免费套餐 {#free-tier-1}

![](/cloud/images/freetier_server_resources.png)

<a id="Enterprise"></a>
### 企业版 {#enterprise-1}

**性能型（Performance）**：针对查询性能进行优化。
![](/cloud/images/enterprise_server_resources-perf.png)

**容量型（Capacity）**：针对存储容量进行优化。
![](/cloud/images/enterprise_server_resources-capacity.png)
