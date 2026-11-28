---
title: "Earth Genome：PostgreSQL 中的 32 亿条向量"
linkTitle: "Earth Genome"
description: "Earth Genome 的 Earth Index 如何用 PostgreSQL、PostGIS 和 vchord 在三台服务器上存放 32 亿条卫星图像嵌入：每月约 12,000 美元，带过滤条件的 top-500 检索中位延迟 761 毫秒。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/customer-stories/earthgenome.md"
aliases:
  - "/docs/customer-stories/earthgenome/"
  - "/vectorchord/customer-stories/earthgenome/"
icon: fa-solid fa-earth-americas
---

Earth Genome 的 [Earth Index](https://www.earthgenome.org/earth-index) 让整个地球陆地表面都可以“以图搜地”：用户点选一个已知地点，比如一条非法跑道或一处采石场，就能找出外观相似的其他地方。它把 32 亿条图像嵌入存在 PostgreSQL 里，用 vchord 做向量检索，并在同一条查询里用 PostGIS 做地理过滤，整套系统跑在三台服务器上。本页整理自 [3 Billion Vectors in PostgreSQL to Protect the Earth](/zh/blog/3-billion-vectors-in-postgresql-to-protect-the-earth/)（2025 年 4 月），介绍其负载、选择 PostgreSQL 的原因，以及硬件、成本和延迟。

<a id="what-is-earth-index-doing-turning-pixels-into-planetary-insights"></a>

## 负载 {#workload}

Earth Index 把陆地表面切成 32 亿块互相重叠、每块约 10 公顷的图块。一个面向对地观测的视觉 Transformer 在 Harmonized Landsat Sentinel-2、Sentinel-1 雷达等卫星影像上以自监督对比学习训练，把每个图块变成一条 384 维嵌入，体积不到原始影像的万分之一。检索时找出嵌入与示例相近的图块，通常还会限定在某个区域内。

<a id="real-world-impact-earth-index-in-action-for-environmental-protection"></a>

记者、研究人员、原住民社区和环保组织用它在肉眼看不过来的大范围内寻找环境破坏。它曾和 Mongabay 一起找出亚马孙雨林里隐蔽的贩毒飞机跑道；自由欧洲电台用它在巴尔干地区找到 1,300 多处采石场，其中约一半没有有效许可。它还可以找出侵入红树林的养虾场和靠近水道的畜禽养殖场。

<a id="the-infrastructure-challenge-searching-billions-of-vectors-affordably"></a><a id="why-postgresql-rocks-for-planetary-scale-vectors"></a><a id="why-earth-index-chose-vectorchord-for-performance-and-affordability"></a>

## 为什么选择 PostgreSQL 和 vchord {#why}

几乎每次检索都要把向量相似度和地理条件结合起来：在某个行政区内、在某条河附近。这些地理数据本来就在 PostGIS 里，向量索引也放进同一个 PostgreSQL 数据库，就是一条查询，而不是两套需要同步的系统。剩下的问题是成本，因为 Earth Genome 是非营利组织。其 CTO Hutch Ingold 解释了其他方案为何行不通：标准 pgvector 在这个规模下达不到性能要求；Qdrant 托管版太贵，在自家 Kubernetes 上自建 Qdrant 集群又显得不够成熟；Google Vertex AI Vector Search 对这份数据的标价是每月 237,000 美元。

vchord 的索引从 NVMe SSD 读取列表，不需要把 32 亿条向量构成的图全部放进内存，硬件因此控制在三台服务器。

<a id="earth-index-technical-architecture-and-setup"></a>

## 架构与结果 {#architecture}

<img src="/docs/images/vector-search-with-geo.png" alt="Earth Index 架构：一张 PostgreSQL 表分区分布在三个节点上，每个节点都装有 PostGIS 和 vchord" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

| | Earth Index |
| --- | --- |
| 服务器 | 3 台 AWS `i8g.16xlarge`：Graviton4（`aarch64`），每台 64 vCPU、512 GB 内存、15 TB NVMe SSD |
| 成本 | 每月约 12,000 美元，而 Vertex AI Vector Search 的报价是每月 237,000 美元 |
| 表 | `globe24`，按 `partkey` 分区分布在三个节点上：图块 ID、`geometry(Point, 4326)`，以及存为 `halfvec(384)` 的嵌入 |
| 延迟 | 在 32 亿行上做一次典型的 top-500 检索，中位延迟 761 毫秒 |

典型的检索语句是这样的形状，把 vchord 的排序、PostGIS 过滤和分区裁剪结合在一起：

```sql
SELECT id
FROM globe24
WHERE partkey IN (...)
  AND ST_Within(geom, $1)
ORDER BY embedding <=> $2
LIMIT 500;
```

这套设计里有两点适用于任何大规模部署：用 `halfvec` 存嵌入，体积是 `vector` 的一半；分区让查询直接跳过 `partkey` 条件排除的所有分区。

<a id="enabling-environmental-action-at-scale"></a>

## 了解更多 {#learn-more}

- [Earth Index](https://www.earthgenome.org/earth-index) 及其[候补名单](https://app.earthindex.ai/waitlist/)。
- 按其他列过滤向量检索，见 [vchordrq 索引](/zh/docs/vchord/usage/indexing/#filter-keys)。
