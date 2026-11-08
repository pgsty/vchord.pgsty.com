---
title: "VectorChord 1.0：Postgres 上开发者优先的向量搜索，索引速度比 pgvector 快 100 倍"
date: 2025-12-04
description: "两年前，当我们发布第一篇 pgvecto.rs 博客文章时，我们下了一个赌注：Postgres 是进行向量搜索的最佳场所。从那时起，我们一直在持续迭代……"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "release"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector"
release_url: "https://github.com/supervc-stack/VectorChord/releases/tag/1.0.0"
upstream_copyright: "© 2025 Jinjing Zhou (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector/"
  - "/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector/"
authors: ["jinjing-zhou"]
images: ["/blog/covers/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector.png"]
---

**GitHub 发布记录：** [VectorChord 1.0.0](https://github.com/supervc-stack/VectorChord/releases/tag/1.0.0)。

两年前，当我们发布第一篇 [pgvecto.rs](/zh/docs/vectors/) 博客文章时，我们下了一个赌注：**Postgres 是进行向量搜索的最佳场所**。从那时起，我们一直围绕这个信念持续迭代——从支持过滤向量搜索的 VBASE，到更长维度的向量支持，再到 RaBitQ 量化方案以及对磁盘友好的索引布局。

随着 VectorChord 1.0 的到来，我们再次实现了突破。在一台 16 vCPU 的机器上，我们现在可以在 20 分钟内为 1 亿（100M）个向量构建好索引；而在相同规模下，pgvector 需要超过 50 个小时。这个数字听起来很惊人，但本次发布的目的绝不仅仅是为了在基准测试幻灯片上赢下比赛，而是为了让你的**实际**开发与迭代周期变得更快。

本文将分为三个部分：

1. [为什么我们选择了更简单的 IVF + RaBitQ 索引而不是 HNSW，以及它为何能与 Postgres 配合得更好。](#1-simplicity-over-complexity-breaking-the-hnsw-is-always-better-myth)
    
2. [我们如何将索引构建时间缩短到足以让你把“重建索引”视为日常迭代的一部分，而不是一项通宵任务。](#2-making-indexing-feel-like-iteration-not-an-outage)
    
3. [我们在开发者体验方面新增了哪些特性，使 VectorChord 真正成为一款趁手的开发者工具，而不仅是一个性能演示。](#3-features-built-for-developers-not-just-for-a-benchmark-chart)
    

---

## 1\. 大道至简：打破“HNSW 总是更好”的迷思 {#1-simplicity-over-complexity-breaking-the-hnsw-is-always-better-myth}

当人们第一次和我们聊起 VectorChord 时，最常问的一个问题非常直接：

> “你们用的是 HNSW 吗？我听说 HNSW 总是比 IVF 更好。”

在纸面上，HNSW 是一个优美的算法，在许多孤立的基准测试中它确实名列前茅。但我们并不是在真空中运行向量搜索——我们是在 Postgres 内部运行它，必须面对 Postgres 自身的存储模型、VACUUM 机制、MVCC 以及运维习惯。

如果你从这个角度来看，权衡就会发生巨大的变化。

### HNSW 在 Postgres 中的现实困境 {#the-postgres-reality-of-hnsw}

HNSW 使用分层图结构。每个新向量都是一个节点，可能会跨越多个层级与其它若干个节点建立连接；每次删除操作都可能移除一个被许多其它节点所依赖的节点。

在独立的专用向量引擎中，你可以围绕这种图结构设计整个存储引擎。但在 Postgres 内部，你做不到。你必须在现有的表/索引模型中生存，与 VACUUM 协同工作，并在 MVCC 机制下保持良好表现。

这正是痛点的根源：

* **插入操作极其繁重**。向 HNSW 索引中插入单个向量，可能会跨越多个节点和层级触发连锁更新。在高写入负载下，这使得保持稳定的延迟变得十分困难。
    
* **删除操作暗藏玄机**。在实践中，删除操作通常只是将一个节点标记为死亡（dead），但仍将其留在图中，以免立即破坏图的连通性。随着越来越多节点被标记为死亡，搜索过程仍然需要遍历它们；当图中很大一部分节点处于“已死亡但仍存在”的状态时，就会引入额外的查询延迟。
    
* **VACUUM 付出了真正的代价**。你不能简单地直接丢弃那些死亡节点，因为直接移除它们会破坏邻域结构并导致图的部分区域断开连接。为了解决这个问题，pgvector 必须将死亡节点的所有邻居重新插入，以确保在没有该节点的情况下图依然保持连通。这种重新插入的工作正是维护成本高昂的原因；核心问题不仅仅是回收死元组（dead tuples），而是围绕每个被删除的节点重新布线整张图。
    

这一切并非完全无法实现，但只要你面临频繁的数据更新，它就会把你推向高昂的运维成本。

### 为什么我们转而选择 IVF + RaBitQ {#why-we-chose-ivf--rabitq-instead}

VectorChord 的核心索引是结合了简单倒排列表（Posting Lists）的 IVF + RaBitQ。向量被路由到粗粒度的聚类簇中，在每个簇内部，我们存储的是极小的量化编码，而不是 768 维的浮点数。在查询时，几乎所有工作都在这些按位打包（bit-packed）的编码上通过查表和廉价的整数运算完成。

由于索引主要扫描压缩编码，即使倒排列表扫描触及大量条目，速度依然极快。在我们的基准测试中，这使 VectorChord 明显快于比较全精度向量的朴素 IVF，并且依然快于需要遍历图并以全精度算术对邻居打分的 pgvector HNSW 索引。

有时人们会问：“那么 HNSW + 量化向量呢？”你确实可以这样做，它也能加速搜索的第一阶段（即遍历量化向量并挑选候选集）。但你仍然需要第二阶段：根据这些候选集获取全精度向量并重新打分，而这一部分并不关心你使用的是哪种索引。在典型工作负载中，第一阶段仅占总延迟的约 40%，因此即使扫描速度提升 2 倍，端到端时间也只能缩短约 20%——更何况 HNSW 无法将数据排列成紧凑、对批处理友好的快速扫描（Fast-Scan）格式，因此就连这点理论收益在实践中也很难真正兑现。

而在 IVF + RaBitQ 中，倒排列表只是压缩条目的数组。插入操作只需追加一个新编码；删除操作只需清除一个编码。没有全局图需要修复，因此频繁更新不会触发连锁反应。在运维层面上，它的表现就像一个普通索引；在我们的测试中，这种设计在保持延迟稳定的同时，能够承受约 10 倍于 pgvector HNSW 索引的更新吞吐量。有关更多性能数据（尤其是查询性能方面的数据），请参阅我们此前的博客文章[**《PostgreSQL 向量搜索：内存与磁盘方案的对比分析》**](/zh/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/)。

最重要的是，这种简洁性为我们接下来几节中的重大改进奠定了基础。如果你的索引结构本身就已经极其错综复杂，那么每一项额外优化都会增加更多活动部件。通过保持核心设计的简洁，我们为大幅改善**索引构建速度**和**开发者工作流**留出了充足的空间。

---

## 2\. 让索引构建像日常迭代，而不是一次停机事故 {#2-making-indexing-feel-like-iteration-not-an-outage}

让我们聊聊标题中的那个数字：**索引速度比 pgvector 快 100 倍**。

在 LAION 1 亿（100M）向量数据集上，纸面对比如下：

* pgvector：在 16 vCPU 上索引构建时间超过 50 小时（如果内存不足还可能失败）。
    
* VectorChord 0.1：在 GPU 上进行外部 KMeans 聚类耗时约 2 小时；在 Postgres 中使用 4 vCPU 插入耗时约 20 小时。
    
* VectorChord 1.0：KMeans 聚类与插入全部在 Postgres 内部完成，在 16 vCPU 上不到 20 分钟即可全部完成（KMeans 约 8 分钟 + 插入约 12 分钟）。
    

但对你而言，真正改变的事情其实更加直观：

* 在 pgvector 的世界里，为大型数据集建立索引是一场**跨越多日的大工程**。你必须围绕它做计划、寸步不离地盯着它，并时刻担心万一中途失败该怎么办。
    
* 在 VectorChord 1.0 的世界里，全量重建索引更像是**“午饭前启动它，喝杯咖啡回来查看结果”**。
    

我们通过同时攻克 IVF 构建的两个阶段实现了这一目标：寻找聚类中心的 KMeans 阶段，以及将每个向量分配给最近聚类中心的插入阶段。

为了做到这一点，我们从问题本质入手，而不仅仅是微调代码。首先，我们没有对 1 亿个数据点上的朴素 768 维、160,000 聚类中心 KMeans 进行微观优化，而是利用约翰逊—林登斯特劳斯引理（Johnson–Lindenstrauss Lemma）将向量投影到小得多的低维空间，直接将 KMeans 的计算量和内存占用削减了约 7 倍。其次，我们分两阶段运行层次化 KMeans（Hierarchical KMeans），每次只对较小的数据子集进行聚类，而不是同时处理 160,000 个聚类中心，这在理论上带来了 400 倍的加速。在插入阶段，我们将同样的思路向上复用一层，在聚类中心本身之上再构建一个 IVF 索引，使每个数据向量只需使用量化编码与一小部分候选聚类中心桶进行比较。这些改进共同将大部分工作从受限于 CPU 的距离数学运算中解放出来：在构建 1 亿向量索引时，主要开销变成了 Postgres 以接近 SSD 极限的速度分配和写入索引页。在我们收紧了分配路径和锁粒度、实现以大块（Chunks）方式流式写入页面之后，最终的实际效果就是：全量重建索引可以轻松控制在几分钟之内，而不再需要耗费数天时间。关于更多技术细节，我们专门撰写了一篇博客[**《我们如何在 PostgreSQL 上实现 20 分钟内完成 1 亿向量索引构建》**](/zh/blog/post/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql/)进行深入解析。

只需以下简单的 SQL 语句，即可轻松启用这些优化：

```sql
CREATE INDEX ON laion USING vchordrq (embedding vector_l2_ops) WITH (options = $$
build.pin = 2
[build.internal]
lists = [400, 160000]        -- Hierarchical KMeans
build_threads = 16
spherical_centroids = true
kmeans_algorithm.hierarchical = {}
kmeans_dimension = 100 -- Dimension Reduction
sampling_factor = 32        
$$);
```

---

## 3\. 为开发者打造的特性，而不仅是为了基准测试图表 {#3-features-built-for-developers-not-just-for-a-benchmark-chart}

VectorChord 1.0 还新增了一系列在基准测试中几乎看不出来、但在日常使用系统时至关重要的特性。它们的核心目标是帮助你理解索引的运行状态，并让你能够顺畅无阻地使用现代模型与部署架构。

<a id="built-in-monitoring-of-index-quality"></a>
### 内置的索引质量监控 {#built-in-monitoring-of-index-quality}

所有的近似最近邻（ANN）索引都会随时间推移而发生漂移。数据分布会发生变化，构建之初表现优异的索引可能会在不知不觉中退化。

VectorChord 不会让你盲目猜测，而是可以为你持续测量召回率。它会自动对真实查询向量进行采样，使用更精确的方法重新评估其近邻，并追踪索引返回“正确”答案的频率。

这把一种模糊的感觉——“最近搜索结果好像有点不太准”——转化为了你可以直观查看的图表。如果召回率保持稳定，你就知道可以推迟重建；如果呈下降趋势，你就可以在用户察觉之前提前规划重建。它还为你提供了具体的数据指标，可以接入你现有的可观测性技术栈或导入 Prometheus，让你能够在监控其它 SLO 的同一块仪表盘上随时关注召回率变化。

在实际使用中，你只需一次 SQL 调用即可评估真实查询模式的召回率，并将该数值作为监控指标导出。例如：

```sql
SELECT vchordrq_evaluate_query_recall(query => $$
  SELECT ctid FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 10
$$);
-- With sampled vector recorded from query
SELECT AVG(recall_value) FROM (
    SELECT vchordrq_evaluate_query_recall(
            format(
                'SELECT ctid FROM %I.%I ORDER BY %I OPERATOR(%s) %L LIMIT 10',
                lq.schema_name,
                lq.table_name,
                lq.column_name,
                lq.operator,
                lq.value
            )
    ) AS recall_value
    FROM vchordrq_sampled_queries('items_embedding_idx') AS lq
) AS eval_results;
```

<a id="long-vector-support-so-you-don-t-have-to-cripple-your-model"></a>
### 长向量支持，无需削足适履限制模型 {#long-vector-support-so-you-dont-have-to-cripple-your-model}

我们支持最高达 16,000 维的向量。这听起来像是一条枯燥的参数规格，但它有着非常明确的实用价值：你可以直接接入更新的模型（包括长上下文模型或多模态模型），而无需仅仅为了迁就索引就立刻对模型输出进行压缩或截断。

你可以先直接使用模型自然生成的向量表示，直观感受其性能与检索质量，然后再决定是否要应用更激进的量化或降维。索引绝不应该成为迫使你在模型选择上做出妥协的瓶颈。

<a id="multi-vector-retrieval-for-richer-rag"></a>
### 面向更丰富 RAG 场景的多向量检索 {#multi-vector-retrieval-for-richer-rag}

并非每篇文档都适合塞进单个向量里。现代检索增强生成（RAG）系统通常将一段文本表示为一组向量——例如每个词元（Token）一个向量，或每个句子一个向量——然后将这组向量与一组查询向量进行比较。这种“晚期交互（Late Interaction）”风格通常被称为多向量检索。

VectorChord 通过在向量数组上提供 MaxSim 风格的操作符，原生支持这一模式。从概念上讲，对于每个查询向量，你会寻找最匹配的文档向量，计算它们的点积，然后将这些最佳得分相加。在 VectorChord 中，这一功能通过 `vector[]` 列上的基于距离的 `@#` 操作符暴露出来：左侧是文档的向量数组，右侧是查询的向量数组。

上手方式与单向量搜索非常相似。你在每行中存储一个向量数组，并构建专用索引：

```sql
CREATE TABLE items (
  id         bigserial PRIMARY KEY,
  embeddings vector(3)[]
);

CREATE INDEX ON items
USING vchordrq (embeddings vector_maxsim_ops);
```

在查询时，传入查询向量数组并按 `@#` 得分排序即可：

```sql
SELECT *
FROM items
ORDER BY embeddings @# ARRAY[
  '[3,1,2]'::vector,
  '[2,2,2]'::vector
]
LIMIT 5;
```

在底层，VectorChord 会将其 ANN 引擎机制应用于这些向量数组，让你能够在 Postgres 中直接使用纯 SQL 获得多向量模型的强大表达能力，同时享受到与单向量 IVF 索引同等水平的高性能体验。

<a id="multi-platform-simd"></a>
### 多平台 SIMD 加速 {#multi-platform-simd}

VectorChord 内置了对 x86\_64、ARM 和 IBM 架构的 SIMD 加速支持。在运行时，我们会自动检测当前可用的最佳指令集（在支持的情况下自动启用 AVX512 等指令集）并直接加以利用，无需你手动调整编译标志或维护多份不同的二进制文件。

### 实验性的 DiskANN + RaBitQ {#experimental-diskann--rabitq}

我们还提供了一种将 DiskANN 与 2 比特 RaBitQ 相结合的实验性索引类型。在某些数据集和召回率目标下，它可以提供比 IVF + RaBitQ 更高的 QPS。其代价则是索引构建和更新速度明显更慢，且更加复杂。

```sql
CREATE INDEX ON items USING vchordg (embedding vector_l2_ops);
```

我们不建议将其作为默认选择。它是为那些拥有极其特定的工作负载、完全清楚自己在做什么，并且愿意为了在特定参数区间内换取更高 QPS 而付出更高运维成本的团队准备的。对于其他所有用户，IVF + RaBitQ 依然是推荐的主力方案。

### 提前终止扫描的相似度过滤 {#similarity-filters-that-stop-scanning-early}

有时你不仅需要最近邻，还需要“找出在此半径范围内的所有结果，最多返回 N 行”。在 SQL 中最自然的写法是在 `WHERE` 子句中加上距离条件，并配合 `ORDER BY` 和 `LIMIT`：

```sql
SELECT *
FROM items
WHERE embedding <-> '[0,0,0]' < 0.1
ORDER BY embedding <-> '[0,0,0]'
LIMIT 10;
```

这种写法虽然能返回正确结果，但当落入该半径范围内的数据点寥寥无几时，性能会非常糟糕。Postgres 仍然必须继续扫描索引，直到找齐 10 行或者穷尽整个搜索空间，因为这里的距离检查仅仅是在 ANN 扫描之后才应用的普通过滤器。

VectorChord 新增了一种“相似度过滤（Similarity Filter）”语法，允许将距离阈值直接下推到索引内部。你只需将查询向量和半径包装在 `sphere()` 值中，并使用 `<<->>` 操作符，索引就知道一旦搜索区域超出该球体范围即可立即停止扫描：

```sql
SELECT *
FROM items
WHERE embedding <<->> sphere('[0,0,0]'::vector, 0.1)
ORDER BY embedding <-> '[0,0,0]'
LIMIT 10;
```

### 预过滤与后过滤，让查询贴合你的数据模型 {#prefilter-and-postfilter-so-queries-match-your-data-model}

在真实应用中，向量搜索几乎从不孤立存在。你通常会按租户、权限、时间范围或内容类型进行过滤，然后再按向量相似度排序，有时顺序则反过来。

VectorChord 允许你在索引级别自由选择预过滤（Prefiltering）和后过滤（Postfiltering）。在低选择性（匹配结果较少）场景下，预过滤可以大幅缩减候选集，带来最高约 5 倍的 QPS 提升；而在其它情况下，你可能希望先进行向量搜索，再仅对排名前列的结果进行过滤，以获得更好的召回率。关键在于，你可以在 Postgres 中自然地表达这两种模式。

在当前会话中启用预过滤只需一条 SQL 语句：

```sql
SET vchordrq.prefilter = on;
```

<a id="text-search-with-vectorchord-bm25"></a>
### 基于 VectorChord-BM25 的文本搜索 {#text-search-with-vectorchord-bm25}

最后，我们新增了 VectorChord-BM25 扩展，将强大的全文搜索能力直接引入你的 Postgres 实例。它支持多语言和高级分词（Tokenization），旨在为众多工作负载提供堪比 ElasticSearch 级别的相关性排序能力。

我们的初衷并不是要取代所有的专用搜索引擎，而是让你能够构建将 BM25 与向量搜索并肩部署在同一个数据库中、并复用同一套运维工具的系统。对许多团队而言，仅此一项就能免去大量的部署与维护负担。

在实际使用中，你可以通过纯 SQL 直接调用它，将其与向量嵌入结合，并按统一得分进行排序。例如：

```sql
SELECT id,
       passage,
       embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL', 'bert')) AS rank
FROM documents
ORDER BY rank
LIMIT 10;
```

---

## 结语 {#closing-thoughts}

人们很容易将 VectorChord 1.0 简单概括为“在 1 亿向量上索引速度比 pgvector 快 100 倍”。这个标题确实不假，但它并不是全部的故事。

我们的目标是让 VectorChord 成为在 Postgres 上进行检索的最佳方式之一——无论是从最初的原型验证，还是扩展到十亿级规模的数据集。如果你已经在使用 pgvector，我们非常欢迎你在真实业务负载上试用 VectorChord 1.0，并告诉我们它在哪些地方帮到了你、在哪些地方还可以做得更好。最后，我们也要向 EnterpriseDB 团队在整个研发过程中提供的宝贵反馈致以诚挚的谢意。
