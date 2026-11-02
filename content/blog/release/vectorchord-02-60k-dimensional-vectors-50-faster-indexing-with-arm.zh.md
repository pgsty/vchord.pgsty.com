---
title: "VectorChord 0.2：支持 60,000 维向量，ARM 架构下索引速度提升 50%"
date: 2025-02-17
description: "VectorChord 0.2：增强 PostgreSQL 向量搜索能力，支持高达 60,000 维向量、Float16 类型以及更快的 ARM 性能"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "release"
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm"
upstream_copyright: "© 2025 Jinjing Zhou (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm/"
  - "/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm/"
---

今天，我们非常激动地向大家分享 VectorChord 0.2——这是一个凝聚了社区反馈、旨在应对 PostgreSQL 向量搜索不断演进的挑战而打造的新版本。

%[https://github.com/tensorchord/VectorChord/] 

<a id="optimized-storage-layout-supporting-up-to-60-000-dimensions"></a>
## 优化存储布局：支持高达 60,000 维向量 {#optimized-storage-layout-supporting-up-to-60000-dimensions}

在 PostgreSQL 中，基础存储单元是 8KB 的数据页（Page）。虽然这种设计对于大多数常规负载非常稳健，但它也给高维向量搜索等现代应用场景带来了限制。例如，受限于固定的页面大小，pgvector 每个向量的维度硬性上限为 2000 维，因为更大的向量无法在单个页面内建立索引。

为了解决这一问题，我们在 VectorChord 中重构了向量存储架构。通过重新设计向量的内部存储布局，我们实现了对存储分配的精细控制，允许向量在需要时跨越多个页面存储。现在，我们可以支持最高达 60,000 维的向量。

| **系统** | **向量维度上限** |
| --- | --- |
| VectorChord 0.2 | 60000 |
| VectorChord 0.1 | 1600 |
| pgvector | 2000 |

这种跨页能力不仅打破了 2000 维的壁垒（现已在 v0.2 中支持），还优化了存储效率。举例来说，一个 1200 维的向量（约占 4.8KB）在传统 PostgreSQL 存储方式下会浪费近一半的页面空间，因为每个 8KB 页面只能容纳一个这样的向量，导致存储利用率仅为约 58.5%（1200 维 × 4 字节 ÷ 8192 字节）。通过跨越页面边界紧密打包向量，VectorChord 最大限度地减少了未使用的空间，显著提高了存储密度。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739759682371/a2aef1a1-2a2c-4e3a-bb81-36dd85560fb0.png)

虽然这只是向前迈出的一小步，但我们对它为可扩展向量负载所解锁的无限可能感到兴奋。

## Float16 与 ARM 架构优化 {#float16--arm}

在 **0.2 版本**中，我们很高兴地引入了 **Float16 支持**，让用户能够灵活地在存储效率与召回精度之间取得平衡。选择 Float16 可以将向量存储需求减少 50%，仅需在召回性能上做出微小的权衡。需要说明的是，该优化仅适用于原始向量——量化后的向量仍然需要每维度 1 比特来忠实表示原始数据。此次更新让用户能够根据自身对精度和存储的具体需求做出合理选择。

我们还优先针对 ARM 架构进行了性能改进。通过使用 ARM 的**可扩展向量扩展（SVE）**指令集重写距离计算和快速扫描（Fast Scan）逻辑，VectorChord 现在能够在基于 ARM 的系统上提供出色的优化性能。这一增强确保了使用 AWS 最新 **i8g 实例**（搭载 Graviton4 处理器）等平台的用户，能够在与旧款 i4i 实例相同的成本下获得更高的吞吐量。虽然这些优化是渐进式的，但我们很高兴能帮助各团队在现代云环境中高效地实现扩展。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737032763562/de2e03f6-7657-4313-a483-0e61a0dfa4ce.png?auto=compress,format&format=webp)

如结果所示，运行在 i8g.xlarge（ARM64）上的 **VectorChord** 与价格相近的 i4i.xlarge 相比，**吞吐量提升了约 30%**。另一方面，价格**高出 50%** 的 i7ie.xlarge 相比 i8g 仅提供了约 **15% 的性能提升**——远不足以证明其高昂价格的合理性。此外，基于 ARM 的 i8g 上的**索引构建时间**也快得多，这是一个令人惊喜且深受欢迎的优势。

我们的基准测试为注重成本的用户揭示了一些重要洞察：在 AWS 的 i8g.xlarge（ARM64）上运行 VectorChord，与价格相仿的 i4i.xlarge 相比可实现**约 30% 的吞吐量提升**，充分展示了现代 ARM 架构如何在不增加成本的情况下带来可观的性能收益。相比之下，售价比 i8g 高 50% 的 i7ie.xlarge 仅带来 15% 的性能提升——对于追求成本效益的团队而言，这种权衡显然不够划算。

同样令我们感到惊喜的是，基于 ARM 的 i8g 实例在**索引构建速度上也有显著提升**。虽然这并非我们此次优化的首要目标，但它凸显了 ARM64 和 SVE 在向量工作负载领域的广阔潜力。当然，我们也深知这些结果只是庞大生态系统中的一部分，并期待与社区携手进一步完善这些基准测试。

归根结底，我们的目标是赋能用户做出数据驱动的决策。i8g 出色的性价比以及令人惊喜的索引构建速度优势，使其成为在生产环境中扩展向量搜索的极具吸引力的选择。这一切都离不开我们所依托的卓越开源生态系统。感谢社区一直以来的支持与反馈，我们将继续针对真实业务负载不断打磨 VectorChord。

## 快速开始 {#getting-started}

你可以使用 Docker 体验 VectorChord 0.2：

```bash
## Start VectorChord in postgres
docker run \
  --name vectorchord-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/vchord-postgres:pg17-v0.1.0

## Connect use psql clinet
psql -h localhost -p 5432 -U postgres
```

所有的查询语法均与 VectorChord 0.1 保持一致！

<a id="Summary"></a>
## 总结 {#summary}

VectorChord 0.2 在前代版本的基础上更进一步，实现了索引体积缩小 30%、索引构建速度提升 50%。Float16 支持将原始向量存储空间减半，而 60,000 维向量支持和 ARM64 优化等新特性则带来了更加流畅的 PostgreSQL 向量检索体验。这些更新共同帮助用户在不牺牲性能的前提下实现高效扩展。

我们热忱欢迎社区探索 VectorChord 0.2！无论你是使用 Float16 优化存储、扩展高维工作负载，还是利用 ARM 的高性价比优势，我们都将全力支持你的探索之旅。你的反馈将决定我们的下一步方向——让我们一起构建更智能的向量搜索。🚀

如果你想更进一步，欢迎体验 [VectorChord Cloud](/zh/cloud/)，我们提供省心的托管服务和免费试用，助你快速启动项目。无论你是优化存储、扩展复杂负载，还是发挥 ARM 的高能效优势，我们的云平台都能为你托管底层基础设施，让你专注于业务创新。
