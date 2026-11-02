---
title: "VectorChord 0.4：凭借高级 I/O 与预过滤实现更快的 PostgreSQL 向量搜索"
date: 2025-06-05
description: "VectorChord 0.4 增强了 PostgreSQL 向量搜索能力，通过高级 I/O 和预过滤显著改善 AI 应用的延迟与吞吐量"
author: "Jinjing Zhou"
tags:
  - "release"
  - "pgvector"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-04-faster-postgresql-vector-search-with-advanced-io-and-prefiltering"
aliases:
  - "/blog/vectorchord-04-faster-postgresql-vector-search-with-advanced-io-and-prefiltering/"
  - "/vectorchord-04-faster-postgresql-vector-search-with-advanced-io-and-prefiltering/"
---

我们很高兴地宣布发布 **VectorChord 0.4**，这是一次全面增强 PostgreSQL 高性能向量搜索能力的重要更新。我们相信，此次发布进一步拓展了 PostgreSQL 向量搜索的能力边界，引入了多项关键架构改进，旨在为严苛的真实业务负载降低延迟并提升吞吐量。

如果你正在 PostgreSQL 上构建相似度搜索、RAG 流水线或其他 AI 驱动的应用，这些更新正是为你量身打造的。我们重点聚焦于两大领域：利用 PostgreSQL 不断演进的底层能力大幅提升冷查询（Cold Query）的 I/O 效率，以及深度优化带过滤条件的向量搜索。

<a id="major-improvement-1-advanced-i-o-for-disk-bound-indexes-2x-3x-lower-cold-query-latency"></a>
### 🚀 重大改进 1：面向磁盘索引的高级 I/O（冷查询延迟降低 2 到 3 倍！） {#major-improvement-1-advanced-io-for-disk-bound-indexes-2x-3x-lower-cold-query-latency}

![async i/o figure](https://cdn.hashnode.com/res/hashnode/image/upload/v1749113884459/3282ee41-625d-4b8a-9373-8b2eb8d81f1c.png)

VectorChord 自早期版本起就支持**基于磁盘的索引（Disk-Based Indexing）**。但此前的一大挑战在于 I/O 效率：受限于 **PostgreSQL 较旧的内部缓冲区操作 API**，全精度向量只能逐个读取。

VectorChord 0.4 通过**重写页面布局**并采用**现代流式 I/O（Streaming I/O）技术**解决了这一问题。我们很自豪地成为**首批（甚至可能是第一个）采用这些全新流式 I/O API 的 PostgreSQL 扩展**。这使我们能够将 I/O 与计算进行流水线化并行处理，并更高效地发起磁盘 I/O 操作。作为这项工作的一部分，我们还**向 `pgrx` 框架贡献了初步的 PostgreSQL 18 支持**，以便针对这些即将到来的异步 I/O（AIO）能力进行测试和开发，从而惠及更广泛的 PostgreSQL 社区。

我们的实现方案会自动适配你的 PostgreSQL 版本：

* **在 PostgreSQL 17（及设置 `io_method=sync` 的更新版本）上：利用 `madvise` 进行预取**。当 VectorChord 调用 PostgreSQL 的新流式 I/O API 时，PostgreSQL 在 PG17（或设置 `io_method=sync` 的 PG18）上的底层实现会在内部使用 `madvise(MADV_WILLNEED)`。这会向操作系统内核提示即将发生的数据读取需求，使磁盘数据提前被读取并缓存到内存的页缓存（Page Cache）中。当实际发生 I/O 时，PostgreSQL 可以直接从页缓存读取，而无需等待磁盘 I/O。
    
* **为异步 I/O 做好准备：PostgreSQL 18 与 `io_uring`**。展望配备基于 `io_uring` 的真正异步 I/O（AIO）的 PostgreSQL 18，VectorChord 0.4 在架构设计上已做好集成准备。这将允许数据以极低的开销和极高的效率直接预取到 PostgreSQL 的共享缓冲区（Shared Buffers）中。
    
* **在较早的 PostgreSQL 版本（PG17 之前）上：用于预取的兼容流式 I/O 接口**。对于使用旧版本 PostgreSQL 的用户，我们**在 VectorChord 内部实现了一套类似的流式 I/O 接口以保持向后兼容**。虽然它不依赖内核级 AIO 或最新的 PostgreSQL 内部 API，但该接口同样能够实现高效的缓冲区预取。这意味着使用早期 PostgreSQL 版本的用户在读取全精度向量时，也能受益于改进的 I/O 模式和更低的延迟。
    

**高级 I/O 对磁盘索引的影响：**在我们的基准测试中，这些 I/O 增强使**冷查询的延迟降低了 2 到 3 倍**。这直接改善了长尾延迟（Tail Latency），尤其是在查询需要使用驻留在磁盘上的向量进行重排序时效果更为显著。

![Streaming I/O benchmark](https://cdn.hashnode.com/res/hashnode/image/upload/v1749113962813/e201cce3-2096-40c8-b318-95a1863e9e47.png)

### 🎯 重大改进 2：通过预过滤加速带条件搜索（最高提速 3 倍！） {#major-improvement-2-pre-filtering-for-faster-filtered-searches-up-to-3x-faster}

![prefilter comparison](https://cdn.hashnode.com/res/hashnode/image/upload/v1749113999755/aaf3b1f5-8289-4a15-9545-774dd9b3b954.png)

向量搜索通常需要与元数据过滤结合使用。如何高效处理这一场景一直是我们关注的重点。我们是最早在 pgvecto.rs 中**通过引入 VBASE 风格过滤来解决 PostgreSQL 向量过滤难题**的团队之一，当时的表现在 pgvector 的基础上实现了大幅提升。

现在，在 VectorChord 0.4 中，我们**通过引入强大的预过滤（Prefiltering）支持，将性能推向了新的高度**。

* **后过滤（Post-filtering，此前的方法）**：先找出 Top-K 个向量，再进行过滤。当过滤条件选择性较高（即匹配行较少）时效率低下。
    
* **预过滤（Pre-filtering，0.4 新增）**：基于比特向量扫描结果，*首先*识别出满足元数据过滤条件的行，然后仅在这个较小的候选集上执行向量距离计算。
    

现在，我们利用高效的机制配合量化比特向量扫描，在执行向量距离计算*之前*先识别出匹配的行。由于过滤检查的开销远小于距离计算，这带来了显著的速度提升。用户可以通过 `SET vchordrq.prefilter=ON` 启用此功能。

**实际效果：**我们的基准测试表明，在适用预过滤的场景下，相比我们已经高度优化的 VBASE 后过滤方法，**搜索性能最高可提升 3 倍**。这为复杂查询带来了可观的优势。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1749114043805/f1fbd015-c96e-4a22-8c20-bb249cd5ba24.png)

### ✨ 其他值得关注的改进： {#other-notable-improvements}

* **优化残差量化（QPS 提升约 20%）**：感谢 Jianyang（RaBitQ 作者），我们改进了残差量化（Residual Quantization）。通过将 `<o, q-c>` 重构为 `<o, q> - <o, c>`，查询向量 `q` 只需量化一次，从而带来了**约 20% 的 QPS 提升**。我们现在推荐用户在 L2 距离场景下启用残差量化。
    
* **优化旋转矩阵并简化配置**：同样感谢 Jianyang，全新的快速哈达玛变换（Fast Hadamard Transform）优化了旋转矩阵，并移除了 `prewarm_dim` GUC 参数，在简化配置的同时略微加快了处理速度。
    
* **全面重写文档**：我们全面重写了官方文档，现在提供**更详尽的用户指南和 API 参考**，帮助你充分发挥 VectorChord 的潜力。欢迎访问 [https://vchord.pgsty.com/zh/docs/](/zh/docs/)。
    

<a id="get-started-with-vectorchord-0-4"></a>
### 立即体验 VectorChord 0.4！ {#get-started-with-vectorchord-04}

我们相信此次发布将显著增强 PostgreSQL 中的向量搜索能力。

* **在 GitHub 上下载 / Star：** https://github.com/tensorchord/VectorChord
    
* **加入社区：** https://discord.gg/KqswhpVgdU 我们欢迎你试用 VectorChord 0.4，在你的实际工作负载下进行基准测试，并分享你的宝贵反馈。
    

祝你向量搜索愉快！
