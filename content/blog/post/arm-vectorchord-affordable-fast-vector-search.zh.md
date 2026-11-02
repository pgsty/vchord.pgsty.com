---
title: "ARM + VectorChord：高性价比的快速向量搜索"
date: 2025-01-21
description: "像 AWS Graviton 这样的 ARM64 服务器能显著节省成本。VectorChord 比 pgvector 便宜 26 倍，针对 ARM64 和 x86 深度优化，提供快速、高效的向量搜索体验。"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/arm-vectorchord-affordable-fast-vector-search"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/arm-vectorchord-affordable-fast-vector-search/"
  - "/arm-vectorchord-affordable-fast-vector-search/"
---

ARM64 正悄然成为高性价比云服务器的首选架构，尤其是在 AWS 上。借助 Graviton 系列（Graviton3 和 Graviton4）等基于 ARM 的处理器，你可以在不牺牲性能的前提下节省一大笔开销。这些 ARM64 实例比传统的 x86 实例实惠得多，是在云端平衡成本与性能的可靠选择。

话虽如此，由于 ARM 的架构与 x86 不同，未针对其进行优化的软件可能会因为指令模拟或缺乏优化而运行缓慢。这正是 **VectorChord** 大显身手的地方——它是一款专为可扩展、高性能且磁盘高效的向量相似度搜索而设计的 PostgreSQL 扩展。作为 [pgvecto.rs](/zh/docs/vectors/) 的继任者，VectorChord 让你**仅花 $1 就能存储多达 400,000 个向量**，带来惊人的成本节省：在相同价格下，可存储的向量数量是 Pinecone 优化存储的 **6 倍**，更是 pgvector / [pgvecto.rs](/zh/docs/vectors/) 的 **26 倍**。

通过充分利用平台特定的硬件特性（如 x86\_64 上的 AVX-512 和 ARM64 上的 SVE），VectorChord 确保了在不同系统架构下都能提供高效的向量搜索性能。无论你使用的是 ARM64 还是 x86，VectorChord 都能让系统流畅运行，是现代计算环境中可靠且通用的解决方案。简而言之，ARM64 是省钱的绝佳选择，而 VectorChord 则确保你的向量搜索既快速、高效，又经济实惠。

## **基准测试环境** {#benchmark-setup}

我们在三款 AWS EC2 实例上运行了基准测试，以评估 VectorChord 在不同硬件配置下的性能表现。以下是我们的实例选型与对比参数：

| [**实例类型**](https://docs.aws.amazon.com/ec2/latest/instancetypes/so.html) | **i4i.xlarge** | **i8g.xlarge** | **i7ie.xlarge** |
| --- | --- | --- | --- |
| 内存 | 32 GiB | 32 GiB | 32 GiB |
| vCPU | 4 | 4 | 4 |
| CPU 代数 | 第 3 代 Intel Xeon | **AWS Graviton4** | 第 5 代 Intel Xeon |
| CPU 架构 | x86\_64 | **arm64** | x86\_64 |
| 存储 | 937 GB NVME SSD | 937 GB NVME SSD | 2500 GB NVME SSD |
| 价格 | $0.1158 / 小时 | **$0.1162 / 小时** | $0.1723 / 小时 |

基于 ARM 的 **i8g.xlarge** 定价几乎与 **i4i.xlarge** 完全相同，但在 CPU 性能上带来了显著提升。而与 CPU 能力相当的 **i7ie.xlarge** 相比，**i8g.xlarge** 的价格要便宜近三分之一（后者贵约 50%），是更具性价比的选择。

## **测试结果** {#test-result}

为了展示 ARM64 机器在向量搜索领域的竞争力，我们在所有选定的机型上运行了相同的 LAION 基准测试。我们测量了不同搜索参数下的索引构建速度、查询吞吐量（QPS）以及召回率等关键指标。

该基准测试包括插入 **500 万个向量**（每个向量为 768 维）并在其上运行 1,000 次查询。下方结果重点展示了各个实例的**索引构建时间**和**查询性能**，清晰地呈现了 ARM64 与传统 x86 配置的正面对比。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737032763562/de2e03f6-7657-4313-a483-0e61a0dfa4ce.png)

如结果所示，运行在 i8g.xlarge（ARM64）上的 **VectorChord** 与价格相近的 i4i.xlarge 相比，**吞吐量提升了约 30%**。另一方面，价格**高出 50%** 的 i7ie.xlarge 相比 i8g 仅提供了小幅的 **15% 性能提升**——远不足以证明其高昂价格的合理性。此外，基于 ARM 的 i8g 上的**索引构建时间**也明显更快，这是一个令人惊喜且深受欢迎的优势。

总而言之，无论与 i4i.xlarge 还是 i7ie.xlarge 相比，基于 ARM 的 i8g.xlarge 都在性能与成本之间取得了更好的平衡。这与 **VectorChord** 为用户带来的核心价值不谋而合：**以更低的成本获得更高的性能**。无论你是希望节省开支还是最大化系统效率，ARM64 与 VectorChord 的组合都是当之无愧的赢家。
