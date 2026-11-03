---
title: "使用 VectorChord 在 PostgreSQL 中实现 10,000 QPS 的向量搜索"
date: 2025-02-27
description: "作为 pgvecto.rs 的继任者，VectorChord 是一款专为向量搜索打造的 PostgreSQL 扩展，可轻松扩展至 10,000 QPS。"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorsearch"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vector-search-at-10000-qps-in-postgresql-with-vectorchord"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/vector-search-at-10000-qps-in-postgresql-with-vectorchord/"
  - "/vector-search-at-10000-qps-in-postgresql-with-vectorchord/"
authors: ["junyu-chen"]
images: ["/blog/covers/vector-search-at-10000-qps-in-postgresql-with-vectorchord.png"]
---

VectorChord 是一款专为可扩展、高性能且磁盘友好的向量相似度搜索而设计的 PostgreSQL 扩展，也是 [pgvecto.rs](/zh/docs/vectors/) 的继任者。在我们之前的[博客文章](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)中，我们展示了仅需每月 $250 的成本，VectorChord 就能在 1 亿规模的向量数据集上以 0.95 的精度实现 131 QPS——展现了大规模向量搜索中令人印象深刻的高性价比。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733194599461/eb1cf21d-4eb0-4427-8b39-bbb96d125182.png?auto=compress,format&format=webp)

在此基础上，本文将聚焦于极致性能，探讨如何借助 VectorChord **在 PostgreSQL 中实现 10,000 QPS**。我们将为您详细介绍 PostgreSQL 可靠的关系型底座如何与先进的向量索引相结合，以提供快速、可扩展的搜索能力；同时提供一套生产级部署方案与详尽的架构指南，帮助您在高负载下从容应对大规模向量计算。

<a id="Background"></a>
## 背景 {#background}

高每秒查询率（QPS）的向量搜索对于推荐引擎、图像识别和自然语言处理等实时应用至关重要。这类应用要求快速、高效的搜索以即时返回结果，这对于保持用户参与度和业务运营效率至关重要。通过利用 PostgreSQL 进行向量搜索，您不仅可以受益于其成熟稳健的关系型能力和先进的索引机制，还能避免维护独立专用向量数据库所带来的额外开销。这种统一的架构简化了系统集成、降低了整体复杂度，同时依然能够满足现代应用的高性能需求。

在实验中，我们在包含 500 万和 1 亿向量的 LAION 数据集上评估了性能，并将目标精度设定为 90% 以贴近真实业务场景。我们还探索了通过多副本扩展系统以提升 QPS 的方案，展示了 PostgreSQL 如何在保持高性能的同时有效承载严苛的向量搜索负载。

## **架构** {#architecture}

在多节点集群上使用 VectorChord 比在单机上更具挑战性。与其他分布式服务类似，可靠的分布式向量搜索通常需要满足以下要求：

* **易用性（Usability）**：声明式的配置管理
    
* **弹性（Elasticity）**：根据 QPS 需求自动扩缩容节点
    
* **负载均衡（Load Balancing）**：将请求高效分发至不同的只读副本实例
    
* **高可用性（High Availability）**：维护数据库的多个副本，并在发生故障时自动从副本恢复
    
* **持久性（Durability）**：安全、持久的存储，确保数据完整性并防止故障时发生数据丢失
    

为此，我们在 AWS EKS 上结合 OpenTofu 和 CloudNativePG 部署 VectorChord 服务，以管理提供上述能力的基础设施。以下是构建示例集群所用的核心模块：

* [OpenTofu](https://opentofu.org/)：Terraform 的开源替代方案，用于在 AWS EKS 上实现基础设施即代码（IaC）
    
* [CloudNativePG](https://cloudnative-pg.io/)：采用主从（primary/standby）架构管理高可用 PostgreSQL 数据库集群的完整生命周期
    
* [PGBouncer](https://www.pgbouncer.org/)：轻量级 PostgreSQL 连接池，由 CloudNativePG 的 [Pooler](https://cloudnative-pg.io/documentation/1.25/connection_pooling/) 模块提供
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740621480659/d68f7e47-0dc6-48bc-939d-d87f00be6861.png)

与 [DiskANN](https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf) 类似，VectorChord 可以充分利用磁盘资源，在内存不足时依然保持极具竞争力的性能。此外，VectorChord 还可以将索引缓存在内存中，以获得更高的查询性能。

> [!TIP]
> 有关 VectorChord 技术细节的更多信息，请参阅我们之前的[文章](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/#vectorchords-solution-disk-friendly-ivfrabitq)。

为了冲击 QPS 上限，我们假设内存能够完全容纳整个数据集，并以此为标准选择 AWS 机型。

下表列出了针对不同规模数据集能够将数据完全缓存在内存中的合适机型：

| **数据集** | **维度 / 规模** | **机型 / 内存** |
| --- | --- | --- |
| LAION-5m | 768 / 5,000,000 | r7i.xlarge / 32GB |
| LAION-100m | 768 / 100,000,000 | r7i.16xlarge / 512GB |
{.wide .expand}

## **测试结果** {#results}

正如[我们的文档](/zh/docs/vchord/usage/indexing/)所述，VectorChord 接收两个关键参数：`nprob` 和 `epsilon`。其中，`nprob` 定义了查询期间需要扫描的候选向量聚类数量，而 `epsilon` 则作为决定是否对结果进行重排序的阈值。这两个参数对 **QPS** 和 **召回率（recall）** 都有着关键影响，允许用户在搜索速度与准确度之间进行精细权衡。

* 较低的 `nprob` 会带来更高的 QPS 和更低的召回率。
    
* 较低的 `epsilon` 会带来更高**但更不稳定**的 QPS 以及更低的召回率。
    

如果固定这两个参数，每次实验的精度将保持一致，但实际 QPS 仍会随底层硬件的 CPU 和 I/O 性能而变化。为了确保精度保持在 0.9 以上，我们根据此前在较小数据集上进行的实验配置了参数：

| **数据集** | **nprob / epsilon** | **召回率 (recall)** |
| --- | --- | --- |
| LAION-5m | 20 / 1.0 | 0.9324 |
| LAION-100m | 20 / 1.0 | 0.9042 |
{.wide .expand}

我们在同一个可用区内部署了一台 **r7i.4xlarge** 实例作为客户端，向 VectorChord 集群发起查询。测试使用了 **16 到 128** 个并发工作线程，以模拟真实场景中数据库通常承受的并发水平。这一设置使我们能够评估 VectorChord 在不同负载和并发条件下的表现。

> [!TIP]
> `r7i.4xlarge` 拥有 16 个 vCPU，当并发请求达到 128 时，能够有效减少客户端侧的 CPU 争用。

遵循常见的 PgBouncer 最佳实践，我们采用了两类实例：一个主实例（primary）用于数据写入，多个副本实例（replica）用于处理只读工作负载。PgBouncer 充当负载均衡器，将查询高效地分发至各个后端实例。在基准测试期间，我们将查询端点指向 `read-only (ro)` 连接池，而 `read-write (rw)` 主实例在测试期间保持空闲。这种设置确保了读密集型工作负载下的最优资源利用率和可扩展性。

对于 **500 万规模数据集**，我们将实例数量从 **5 台扩展到 15 台**以达到 **10,000 QPS**。相比之下，对于 **1 亿规模数据集**，仅需 **2 台实例**即可达到该性能标准。下图展示了这些实验的结果，体现了 VectorChord 在不同数据集规模下的可扩展性与高效率。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740537380494/5e9a1e66-1cc6-4dc7-b26d-a68c83891289.png)

## **成本** {#cost}

综上所述，如果您需要在上述数据集上实现 10,000 QPS，所需的最低硬件成本如下：

| **数据集** | **达到 10000+ QPS 的最低硬件配置** | **vCPU 数量** | **预估月度成本** |
| --- | --- | --- | --- |
| LAION-5m | r7i.xlarge × 7 | 4 × 7 = 28 vcpu | $0.2646 × 7 × 720 = $1334 |
| LAION-100m | r7i.16xlarge × 2 | 64 × 2 = 128 vcpu | $4.2336 × 2 × 720 = $6096 |
{.wide .expand}

> [!TIP]
> 主实例的成本未包含在上述计算中，因为它可以与其他 PostgreSQL 连接池共享和复用，从而进一步优化资源分配并降低总体开支。

通过这项实验，无论是在公有云还是私有数据中心，您都可以据此设计和扩展自己的集群，以达到理想的 VectorChord 搜索性能水平。即使在将性能置于首位的场景下，VectorChord 依然具备极具竞争力的价格，是满足高性能向量搜索需求的高性价比解决方案。

## **总结** {#summary}

无论您是在高性价比 VPS 上起步的初创团队，还是为追求极致性能而扩展大型集群的企业，VectorChord 都能为您打开无限可能。虽然本文聚焦于 10,000 QPS，但这远非 VectorChord 所能达到的上限。

凭借强大的索引算法，VectorChord 不仅通过高效利用内存和高速 SSD 超越了 pgvector 等标准 PostgreSQL 解决方案，更在处理海量数据和应对高 QPS 需求方面超越了专用向量数据库。在相同成本下，它不仅提供了更卓越的性能，还消除了维护独立向量搜索系统的复杂性。

如果您希望探索大规模向量搜索解决方案，欢迎加入我们的 [Discord 社区](https://discord.gg/KqswhpVgdU)或通过 [support@tensorchord.ai](mailto:support@tensorchord.ai) 联系我们。让我们一起释放数据的全部潜能！

%[https://github.com/tensorchord/VectorChord]
