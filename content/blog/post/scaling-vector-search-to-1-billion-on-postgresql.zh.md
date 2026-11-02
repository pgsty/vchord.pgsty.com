---
title: "在 PostgreSQL 上将向量搜索扩展至 10 亿规模"
date: 2026-01-15
description: "单机 2 小时内完成极速索引构建"
author: "Junyu Chen"
tags:
  - "vector-database"
upstream_link: "https://blog.vectorchord.ai/scaling-vector-search-to-1-billion-on-postgresql"
aliases:
  - "/blog/scaling-vector-search-to-1-billion-on-postgresql/"
  - "/scaling-vector-search-to-1-billion-on-postgresql/"
---

对于希望自行部署十亿级规模向量搜索的团队而言，真正的挑战往往不在于原始性能，而在于实用性。许多专为十亿级规模、低延迟向量搜索而设计的解决方案都伴随着诸多现实约束，需要在各种权衡中做出妥协，从而影响了落地的难易程度。

现有的大多数方案通常属于以下几类之一：

* **运维复杂**：依赖多节点分布式系统，长期管理、运维和维护的难度较高。
    
* **构建耗时过长**：需要漫长的索引构建时间，导致重建索引成本高昂，且极易影响生产环境负载。
    
* **内存开销巨大**：单机往往需要高达 1 TB 的内存，高昂的硬件成本让大多数团队望而却步。
    

这些权衡在现有的公开基准测试中清晰可见。例如，[ScyllaDB](https://www.scylladb.com/2025/12/01/scylladb-vector-search-1b-benchmark/) 报告在 DEEP-1B 数据集上实现了高达 98% 的召回率和 12.3 ms 的 P99 延迟，但这一结果依赖于多台大型实例。而在相同数据集和规模下，[YugabyteDB](https://www.yugabyte.com/blog/benchmarking-1-billion-vectors-in-yugabytedb/) 报告的长尾延迟明显更高，P99 达到了 0.319 秒。

|  | 延迟 / 召回率 | 硬件配置 | 构建时间 |
| --- | --- | --- | --- |
| ScyllaDB | 13ms / 98% | 3×`AWS r7i.48xlarge` + 3×`AWS i4i.16xlarge` | 24.4 小时 |
| YugabyteDB | 319 ms / 96% | 未报告 | 未报告 |
| VectorChord | 40 ms / 95% | `AWS i7ie.6xlarge` | 1.8 小时 |

在单节点部署方面，[Scalable Vector Search (SVS)](https://intel.github.io/ScalableVectorSearch/benchs/static/previous/large_scale_benchs.html#search-with-reduced-memory-footprint) 此前的研究表明，使用 [HNSWlib](https://github.com/nmslib/hnswlib) 为 DEEP-1B 构建索引通常需要 800 GiB 内存；尽管 SVS 或 [FAISS-IVFPQs](https://github.com/facebookresearch/faiss) 可以将其降低至约 300 GiB，但这依然是一笔可观的硬件开销。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1768291667540/ec225f8e-015a-4832-9aef-c5227a545a67.png)

这使得希望坚持自托管的团队很难实现平滑扩展。从 100 万向量扩展到 10 亿向量，往往需要重新思考架构：要么改变硬件假设，要么重构业务工作流。

借助 [VectorChord 1.0.0](/zh/blog/release/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector/)，规模扩展变得前所未有地简单。得益于全新的[层次化 K-means（Hierarchical K-means）及其他优化](/zh/blog/post/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql/)，构建 10 亿向量索引与构建 100 万向量索引的流程完全一致。这也是我们实际使用它的方式：只需迁移到一台配置稍高一点的机器，例如从 AWS i7i.xlarge 升级到 i7i.4xlarge。

## DEEP-1B 基准测试 {#the-deep-1b-benchmark}

为了验证 VectorChord 在十亿级向量规模下的能力，我们采用了来自 [BIGANN](https://big-ann-benchmarks.com/neurips21.html) 的 [Yandex DEEP-1B](https://research.yandex.com/datasets/biganns) 数据集。DEEP-1B 是大规模向量搜索领域广泛采用的基准数据集，包含由自然图像训练的深度学习模型生成的 **10 亿条 96 维向量嵌入（embeddings）**。

由于其庞大的规模，DEEP-1B 被广泛用作评估大规模向量搜索系统的基准数据集。其广泛的普及度使得测试结果易于复现和对比，尤其是在评估十亿级向量规模下的索引构建性能、查询延迟和资源效率时。

面对如此庞大的数据集，构建 VectorChord 索引需要：

* **存储**：约 **900 GB** 的高性能 SSD
    
* **内存（**[**shared\_buffers**](https://www.postgresql.org/docs/current/runtime-config-resource.html#GUC-SHARED-BUFFERS)**）**：不低于 **60 GB**，由 PostgreSQL 管理
    
* **内存（额外开销）**：索引构建期间至少需要 **60 GB 额外**内存
    

基于上述要求，`AWS i7i.4xlarge` 是该规模下构建索引的最低配置。我们的测试在一台 `AWS i7ie.6xlarge` 上运行，这反映了实际生产部署中的常见做法——通过配置更多内存来减少磁盘访问并保持稳定的查询延迟。

| 实例类型 | `AWS i7i.4xlarge` | `AWS i7ie.6xlarge` |
| --- | --- | --- |
| 物理处理器 | Intel Xeon Scalable (Emerald Rapids) | Intel Xeon Scalable (Emerald Rapids) |
| vCPU 数量 | 16 | 24 |
| 内存 (GiB) | 128 | 192 |
| 磁盘空间 (GiB) | 3750 GB NVMe SSD | 2×7500 GB NVMe SSD |
| 价格 | **$1088** / 月 | **$2246** / 月 |

所有实验均在 PostgreSQL 17 上使用 VectorChord 1.0.0 运行。下方 SQL 是我们用于构建索引的完整命令：

```pgsql
CREATE INDEX ON deep USING vchordrq (embedding vector_l2_ops) WITH (options = $$
build.pin = 2
residual_quantization = true
[build.internal]
build_threads = 24
lists = [800, 640000]
kmeans_algorithm.hierarchical = {}
$$);
```

构建配置中各个选项的作用如下：

* [`build.pin`](/zh/docs/usage/indexing/#build-pin)：启用构建期内存固定（pinning），将索引的热点部分缓存在共享内存中，从而加速大规模数据集上的索引构建。
    
* [`residual_quantization`](/zh/docs/usage/indexing/#residual-quantization)：在 DEEP-1B 上，我们发现启用**残差量化（residual quantization）**能够提升查询性能，因此在本基准测试中保持开启。
    
* [`build.internal.build_threads`](/zh/docs/usage/indexing/#build-internal-build-threads)：在 K-means 构建阶段使用 24 个线程，充分跑满实例上的可用 CPU 资源。
    
* [`build.internal.lists`](/zh/docs/usage/indexing/#build-internal-lists)：根据我们的经验，应根据数据行数选择合适的聚类列表大小。在大规模场景下，使用**双层列表（two-level list）**效果显著，能同时提升索引构建效率与查询性能。
    
* [`build.internal.kmeans_algorithm.hierarchical`](/zh/docs/usage/indexing/#build-internal-kmeans-algorithm)：启用 VectorChord 1.0 引入的**层次化 K-means（Hierarchical K-means）**路径，大幅加快大规模索引的构建速度。
    

## 测试结果 {#our-results}

在单台 AWS i7ie.6xlarge 机器上使用 **24 个 CPU 核心**时，索引构建仅耗时 **6,408 秒（约 1.8 小时）**即告完成，证明十亿级规模的索引构建完全可以在切实可行的维护窗口内完成。

下图展示了在缓存预热（warm cache）状态下，使用单搜索线程在 Deep1B 数据集上评估 Top-10 和 Top-100 查询时的查询吞吐量（QPS）与召回率（Recall）关系。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1767855767038/b2a769c9-0d5d-48d6-ab2f-791d6bac7e29.png)

对于 Top-10 查询，吞吐量从约 0.91 召回率下的超过 117 QPS，变化至约 0.95 召回率下的约 69 QPS。Top-100 查询也遵循相同的规律，随着召回率的提高，吞吐量相应下降。

下表列出了每个数据点对应的具体搜索参数（固定 `epsilon = 1.9`，改变探测聚类数 `probes`）。综合图表数据可以看出，即使在 10 亿向量规模下，VectorChord 依然能在单机上提供稳定且可调优的查询性能。

| [probes](/zh/docs/usage/indexing/#vchordrq-probes) / [epsilon](/zh/docs/usage/indexing/#vchordrq-epsilon) | Recall@Top 10 | QPS | P99 延迟 / ms |
| --- | --- | --- | --- |
| 40,120 / 1.9 | 0.9132 | 117.45 | 12.33 |
| 40,160 / 1.9 | 0.9305 | 97.32 | 14.61 |
| 40,250 / 1.9 | 0.9511 | 68.87 | 20.53 |

| [probes](/zh/docs/usage/indexing/#vchordrq-probes) / [epsilon](/zh/docs/usage/indexing/#vchordrq-epsilon) | Recall@Top 100 | QPS | P99 延迟 / ms |
| --- | --- | --- | --- |
| 40,180 / 1.9 | 0.9051 | 66.12 | 22.60 |
| 40,270 / 1.9 | 0.9318 | 49.55 | 30.40 |
| 40,390 / 1.9 | 0.9509 | 37.53 | 39.70 |

这些结果表明，即便在十亿级规模下，单机上的向量查询性能依然可以做到实用且可预测。

## **总结** {#summary}

VectorChord 1.0.0 证明了实时向量搜索可以从 100 万向量平滑扩展至 10 亿向量，而无需强迫用户改变架构、工作流或使用方式。无论您是在构建以图搜图、AI 驱动的应用，还是 RAG 流水线，VectorChord 都旨在成为运行在您自己机器上的可靠向量引擎，随数据增长而自然扩展。

准备好扩展规模了吗？您可以立即开始使用，也可以通过 [GitHub](https://github.com/tensorchord/VectorChord) 或 [Discord](https://discord.gg/KqswhpVgdU) 联系我们，了解更多信息并获取社区支持。
