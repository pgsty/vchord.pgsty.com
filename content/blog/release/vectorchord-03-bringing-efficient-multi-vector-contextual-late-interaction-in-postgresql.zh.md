---
title: "VectorChord 0.3：在 PostgreSQL 中实现高效的多向量上下文晚期交互"
date: 2025-04-13
description: "VectorChord 0.3 利用 MaxSim 和 WARP 大幅提升 PostgreSQL 向量搜索能力"
author: "[Keming Yang](https://github.com/kemingy), [Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "release"
  - "multivector"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql"
upstream_copyright: "© 2025 Keming Yang, Jinjing Zhou (TensorChord Inc.)"
math: true
aliases:
  - "/blog/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql/"
  - "/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql/"
---

我们非常激动地宣布发布 **VectorChord 0.3**！这一重要里程碑直接在你的 Postgres 数据库内部显著提升了高级向量搜索技术的性能与适用性。在带来 ARM 支持与更快索引构建的 0.2 版本基础上，0.3 版本攻克了现代检索领域的最大难关之一：**具备晚期交互（Late Interaction）能力的高效多向量搜索**。

### 超越单向量：为什么多向量如此强大 {#beyond-single-vectors-why-multi-vector-rocks}

多年来，向量搜索主要将整篇文档或整个查询表示为单个稠密向量（Dense Vector）。这种方法虽然强大，但需要将复杂的信息平均或压缩为单一表示，不可避免地会导致细节语义的丢失。试想一下，如果用一句话概括一篇详尽技术文档的全部含义，你必然会丢失大量细节！

为此，以 [**ColBERT**](https://github.com/stanford-futuredata/ColBERT) 等模型为代表的**多向量表示（Multi-Vector Representations）**与**晚期交互（Late Interaction）**应运而生。这些模型不再为每个条目生成单个向量，而是生成*多个*向量——通常每个词元（Token，即单词或子词）对应一个向量。真正的魅力体现在搜索过程中：

1. **查询编码（Query Encoding）**：你的搜索查询同样被拆分为多个词元向量（记为 q1, q2, ..., qN）。
    
2. **文档编码（Document Encoding）**：同样地，文档也由其词元向量（d1, d2, ... dM）表示。
    
3. **晚期交互与 MaxSim 聚合（Late Interaction & MaxSim Aggregation）**：我们不再只做一次整体比较，而是执行细粒度匹配。其核心思想是**最大相似度（MaxSim）**运算。对于*每一个查询词元向量*（如 q\_i），我们在文档的*所有*词元向量（d1 到 dM）中找出与之具有*最高相似度*（例如余弦相似度或点积）的文档词元向量（d\_j）。对每个查询词元（q1, q2, ..., qN）重复这一过程后，将**每个查询词元所获得的最大相似度值相加**，即可计算出该文档的最终相关性得分。这一运算天然是**非对称的**，重点衡量查询中的各个部分在文档某处得到体现的程度。
    

**为什么这种方式更好？**

* **保留上下文细节**：基于 MaxSim 的晚期交互使模型能够捕捉细粒度的语义关系。它能够识别查询中的*特定重要词汇*是否与文档的*特定部分*强烈匹配，而不是依赖可能被稀释的整体平均相似度。
    
* **显著提升相关性**：通过考虑聚焦于词元级别的交互并汇总每个查询词的最佳匹配，ColBERT 等模型实现了最先进的检索质量。这种细粒度方法对于包含多个词汇、内容丰富的查询尤为强大，能够更准确地理解用户意图。在 [BEIR 基准测试](https://huggingface.co/answerdotai/ModernBERT-base#base-models)中，这转化为显著的性能提升：基于相同的 [ModernBert](https://huggingface.co/answerdotai/ModernBERT-base) 模型，ColBERT 变体取得了 51.6 的 NDCG@10 得分，而稠密单向量变体仅为 41.6。
    

我们之前的博客文章曾探讨过使用 ColBERT 进行重排序（Reranking），展示了它的强大实力：  
[**在 PostgreSQL 中利用 ColBERT Rerank 为向量搜索加速**](/zh/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)

<a id="vectorchord-0-3-bringing-efficient-maxsim-to-postgres-inspired-by-warp"></a>
### VectorChord 0.3：受 WARP 启发，将高效 MaxSim 引入 Postgres {#vectorchord-03-bringing-efficient-maxsim-to-postgres-inspired-by-warp}

VectorChord 0.3 直面**晚期交互高昂的计算成本**。受突破性的 **WARP 引擎**（[论文：WARP: An Efficient Engine for Multi-Vector Retrieval](https://arxiv.org/abs/2501.17788)，[代码：jlscheerer/xtr-warp](https://github.com/jlscheerer/xtr-warp)）启发，我们在核心 Rust 引擎中集成了高度优化的**多向量晚期交互 MaxSim 操作符与索引**。

WARP 方法的精妙之处在于一个根本性的洞察：复杂的多向量 MaxSim 计算（将 N 个查询向量与 M 个文档向量进行比较）可以巧妙地**分解为多个独立的单向量搜索过程**。WARP 不再进行庞大的 N × M 全量比较，而是针对每个查询词元向量，在已建立索引的文档向量上分别执行 N 次独立搜索，以找出各自的最佳匹配。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743730508359/1040ee64-6dd1-429c-bc6b-95184d7cf9dc.png)

VectorChord 0.3 中 MaxSim 扫描器的核心改进正是建立在这一理念之上。我们通过**复用并编排 VectorChord 现有的、高度优化的单向量搜索基础设施**来实现 MaxSim。当使用索引执行 MaxSim 查询时，VectorChord 会利用底层索引结构（**IVF 结合 RaBitQ**）执行**多次单向量搜索**——每个查询向量对应一次。随后，它会根据 MaxSim 求和规则高效地聚合结果。对于缺失值的估计，我们采用了 WARP 的方法，利用**到聚类中心（Centroid）的距离以及累积簇大小**来估计潜在候选文档的 MaxSim 得分。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743733841309/79f715b2-bbf3-4ac4-bb90-b7ffdea07f6f.png)

复用经过优化的单向量搜索组件，确保了 MaxSim 能够直接受益于现有的性能调优与稳定性。对于用户而言，更重要的是它提供了**无缝的使用体验**：你可以对单向量搜索和多向量 MaxSim 搜索使用**相同且熟悉的索引类型**（带 RaBitQ 的 IVF），而无需维护独立的系统。VectorChord 0.3 自豪地成为**首个提供这种高效分解式 MaxSim 实现的 Postgres 扩展**，让最先进的多向量检索直接在你的数据库中变得实用且高效。

### 解锁强大的应用场景 {#powerful-use-cases-unlocked}

这一全新效率为前沿技术的实际落地打开了大门：

1. **高性能 ColBERT 重排序**：对更快的初筛检索（如传统单向量搜索或关键词搜索）召回的候选集应用 ColBERT 卓越的相关性排序，而不会产生高昂的延迟代价，兼得速度与质量。
    
2. **免 OCR 文档搜索（ColPali/ColQwen）**：试想一下，直接在扫描文档、PDF 或图像中进行搜索，而*无需*经过独立且容易出错的 OCR（光学字符识别）步骤。ColPali 或 ColQwen 等模型可以直接从图像块（Image Patches）生成词元嵌入。借助 VectorChord 0.3 的高效 MaxSim，你现在可以直接在 Postgres 中对这些视觉词元嵌入执行晚期交互搜索，从而对以往纯文本方法无法处理的文档实现强大的检索能力。
    

敬请期待！我们即将发布另一篇深度文章，详细介绍 VectorChord 0.3 如何赋能革命性的免 OCR RAG 流水线。

### 性能亮点 {#performance-highlights}

我们在 **FiQA（金融观点挖掘与问答）数据集**上对 VectorChord 0.3 的全新多向量 MaxSim 能力进行了测试。该标准基准测试集包含 57,000 篇文档，累计约 1,500 万个词元。

基于 VectorChord 优化引擎驱动的 **ColBERTv2** 初步基准测试结果展现了令人瞩目的性能：

* **相关性**：我们达到了 **34.1 的 NDCG@10 得分**，优于原始 WARP 论文在同一数据集上报告的 33.6 NDCG@10。
    
* **速度**：查询执行极为高效，平均每次查询仅需 **35 毫秒**。
    

虽然这些只是我们在持续优化过程中基于单个数据集得出的初步结果，但它们充分证明了 VectorChord 0.3 的潜力。用户现在可以直接在 Postgres 数据库内部，以接近简单单向量方法的低延迟，享受多向量搜索与晚期交互带来的高级相关性检索能力。

<a id="get-started-with-vectorchord-0-3"></a>
### 快速上手 VectorChord 0.3 {#get-started-with-vectorchord-03}

**前提条件：**

* 安装了 VectorChord v0.3 的 PostgreSQL 服务器
    

你可以使用我们的 VectorChord-Suite 镜像：

```bash
docker run --rm --name vchord_db -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 \
    ghcr.io/tensorchord/vchord-postgres:pg17-v0.3.0
```

#### 步骤 1：创建多向量数据表 {#step-1-create-a-table-for-multi-vector-data}

首先，定义一张表来存储数据。关键区别在于对向量列使用数组类型（`vector[]`），以便在每行中保存多个向量。

```pgsql
-- Define a table to store items (e.g., documents), each potentially having multiple vectors.
-- Replace '128' with your actual vector dimensionality.
CREATE TABLE doc (
    id SERIAL PRIMARY KEY, -- A unique identifier for each item
    vecs vector(128)[] -- The column storing an ARRAY of 128-dimensional vectors
);
```

#### 步骤 2：插入多向量数据 {#step-2-insert-multi-vector-data}

向表中插入数据。`vecs` 列接收包含 `vector` 类型的 PostgreSQL 数组。

```pgsql
-- Insert sample data: one document with 2 vectors, another with 3.
-- Ensure vector dimensions match your table definition (128 in this example).
INSERT INTO doc (id, vecs) VALUES
    (1, array[array[0.1, 0.2, ..., 0.9]::vector, array[0.8, 0.7, ..., 0.1]::vector]),
    (2, array[array[0.5, 0.5, ..., 0.5]::vector, array[0.3, 0.4, ..., 0.7]::vector, array[0.9, 0.1, ..., 0.4]::vector]);
-- Add more data as needed...
```

#### 步骤 3：创建支持 MaxSim 的 `vchordrq` 索引 {#step-3-create-a-vchordrq-index-with-maxsim-support}

为了加速 MaxSim 搜索，使用 `vchordrq` 方法创建索引，并指定 `vector_maxsim_ops` 操作符类。这里的一个关键参数是 `build.internal.lists`。

* **计算** `n`：估算整个数据集中所有独立向量的总数。
    


$$
n=N_{doc}*\text{avg}(N_{vector\_per\_doc})
$$


* **设置** `lists`：`build.internal.lists` 的推荐范围为
    


$$
4 * \sqrt n < \text{lists} < 8 * \sqrt n
$$


在此范围内选择一个值（通常 2 的幂次方效果较好）。

```pgsql
-- Example Calculation:
-- If you have 1,000,000 documents (rows) with an average of 5 vectors each:
-- n = 1,000,000 * 5 = 5,000,000 sqrt(n) ≈ 2236 
-- Lower bound: 4 * 2236 ≈ 8944
-- Upper bound: 8 * 2236 ≈ 17888
-- A good value for 'lists' could be 16384 (power of 2).
-- Assume the K-means clusters are balanced, each will have about 305 vectors.

-- Create the index using vchordrq and vector_maxsim_ops
CREATE INDEX doc_vecs_idx ON doc USING vchordrq (vecs vector_maxsim_ops)
WITH (options = $$
build.internal.lists = [16384] -- Adjust this value based on your calculation!
$$);
```

#### 步骤 4：配置搜索参数（可选但推荐） {#step-4-configure-search-parameters-optional-but-recommended}

在查询之前，你可以调整运行时参数以平衡性能与精度：

* `vchordrq.probes`：控制搜索期间检查多少个索引列表（聚类簇）。较高的值会提高精度（召回率），但会减慢搜索速度。对于查找前 10 个结果（`LIMIT 10`），常用的起始值为 32。
    
* `vchordrq.maxsim_refine`：限制对每个候选查询词元向量使用原始精度重新计算的向量对数量（其余情况将使用比特距离）。它与 `probes` 相关，通常设为探测向量数量的 20% 即可。
    

```pgsql
-- Set runtime parameters for the current session/transaction
SET vchordrq.probes = 32; -- Adjust based on desired recall vs. speed trade-off
SET vchordrq.maxsim_refine = 2000; -- Adjust based on desired recall vs. speed trade-off
```

#### 步骤 5：执行 MaxSim 相似度搜索 {#step-5-perform-a-maxsim-similarity-search}

现在你可以使用 `@#` MaxSim 操作符进行查询了。将你的查询向量作为 `vector` 类型的 PostgreSQL 数组传入：

```pgsql
-- Find the top 10 documents most similar to the given set of query vectors
SELECT id FROM doc 
ORDER BY vecs @# ARRAY[array[0.4, 0.1, ..., 0.8]::vector, array[0.7, 0.2, ..., 0.3]::vector]
LIMIT 10;
```

恭喜！你已经成功建表、建立多向量 MaxSim 搜索索引，并使用 VectorChord 0.3 的 MaxSim 操作符执行了第一条查询！你可以尝试调整 `probes` 和 `max_maxsim_tuples` 参数，为你的具体业务场景找到速度与精度的最佳平衡点。

%[https://github.com/tensorchord/VectorChord/]
