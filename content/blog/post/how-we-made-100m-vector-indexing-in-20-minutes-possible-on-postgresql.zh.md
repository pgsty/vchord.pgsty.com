---
title: "我们如何在 PostgreSQL 上实现 20 分钟构建 1 亿向量索引"
date: 2025-12-03
description: "在过去几个月里，我们收到了来自用户和合作伙伴的一致反馈：尽管我们致力于提供可扩展、高性能的 pgvector 替代方案，但在十亿级规模下，索引构建时间和内存占用仍然是核心痛点……"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorsearch"
upstream_link: "https://blog.vectorchord.ai/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql/"
  - "/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql/"
authors: ["junyu-chen"]
images: ["/blog/covers/how-we-made-100m-vector-indexing-in-20-minutes-possible-on-postgresql.png"]
---

## 1\. 引言 {#1-introduction}

在过去几个月里，我们收到了来自用户和合作伙伴的一致反馈：尽管我们提供可扩展、高性能 pgvector 替代方案的目标广受好评，但在十亿级规模下，索引构建时间和内存占用仍然是大家关注的主要痛点。

现在，VectorChord 可以在一台仅配备 12 GB 内存的 16 vCPU 机器上，在 20 分钟内为 1 亿个 768 维向量构建索引。相比之下，使用 pgvector 为相同规模的数据构建索引，在 16 核实例上需要大约 200 GB 内存和约 40 小时。而且当内存不足时，pgvector 往往会频繁触发页面交换（page swapping），导致构建速度进一步恶化。

简而言之，内存占用和构建时间已成为大规模部署向量检索的关键障碍。通过一系列有针对性的优化，我们将构建时间缩短至 **20 分钟**，内存占用降低了 **7 倍**，而精度损失微乎其微。

借助这些改进，我们现在可以使用内存小得多、价格低廉得多的机器（且无需 GPU），**依然能够承载 1 亿个 768 维向量**：

|  | 实例规格 | 价格 | 已用内存 / 总内存 |
| --- | --- | --- | --- |
| 优化前最低配置 | Amazon i7i.8xlarge | 🟨 $2174 / 月 | 135 GB / 256 GB |
| 推荐快速建索引配置 | Amazon i7i.4xlarge | ✅ $**1087** / 月 | 12 GB / 128 GB |
| 最低配置 | Amazon i7i.xlarge + 建索引时使用 GPU | ✅ $**272** / 月 + GPU 成本 | 6 GB / 32 GB |
{.wide .expand}

在接下来的章节中，我们将介绍如何优化各个阶段，使索引构建更快、更省内存。各项优化按阶段划分如下，每项优化分别针对一个阶段：

| 优化手段 | 目标阶段 | 优化效果 |
| --- | --- | --- |
| [层次化 K-means](#hierarchical-k-means) ➕ [降维](#dimensionality-reduction) | 1️⃣ 初始化（Initialization） | 🚀 30 分钟 (GPU) → 8 分钟 (CPU) 🧾 135 → 23 GB |
| [减少锁竞争](#4-reducing-contention) | 2️⃣ 插入（Insertion） | 🚀 420 分钟 → 9 分钟 |
| [并行化压缩](#5-parallelize-compaction) | 3️⃣ 压缩（Compaction） | 🚀 8 分钟 → 1 分钟 |
{.wide .expand}

## 2\. 背景 {#2-background}

VectorChord 中使用的索引类型 **vchordrq** 在逻辑上是一棵高度为 \\(n+1\\) 的树。树的前 \\(n\\) 层是不可变的，纯粹作为检索时的路由结构；第 \\((n+1)\\) 层则存储所有实际数据。

如果 \\(n=1\\)，索引是一个扁平的、无分区的结构；如果 \\(n=2\\)，它就是一个倒排文件（IVF）索引；如果 \\(n=3\\)，则会多出一层路由结构。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1764057309344/ab2bc34f-0185-4513-bdf6-ff82c91db0c4.webp)

索引构建过程可以分为 3 个阶段：**初始化（Initialization）**、**插入（Insertion）** 和 **压缩（Compaction）**。

* **初始化阶段（Initialization Phase）**  
    在此阶段，树的前 \\(n\\) 层被写入索引。首先，索引对表中的向量进行采样；然后，通过对样本进行聚类、对聚类中心再聚类，以此类推构建 \\(n\\) 层树结构；最后将这棵树写入索引。
    
* **插入阶段（Insertion Phase）**  
    索引将表中的向量插入到树的最底层。
    
* **压缩阶段（Compaction Phase）**
    
    索引将所有已插入的向量从非紧凑布局（non-compact layout）转换为紧凑布局（compact layout）。
    

## 3\. 让聚类更快、更省内存 {#3-making-clustering-faster-and-more-memory-efficient}

过去，虽然我们可以在小规格实例上为 1 亿向量构建索引，但通常需要借助 GPU 来加速聚类计算。

初始化阶段的主要瓶颈在于聚类，它既耗时又消耗大量内存。事实上，正是聚类决定了构建索引的最低内存需求。如果我们能在 CPU 上以既快速又省内存的方式实现聚类，那么在没有大内存和 GPU 的小规格实例上构建索引就变得切实可行了。

设 \\(n\\) 为向量数量，\\(c\\) 为聚类中心（质心）数量，\\(d\\) 为向量维度，\\(l\\) 为迭代次数。K-means 的时间复杂度为 \\(O(ncdl)\\)，空间复杂度为 \\(O(nd + cd)\\)。设 \\(f\\) 为采样系数，即 \\(n=fc\\)。此时 K-means 的时间复杂度为 \\(O(fc^2dl)\\)，空间复杂度为 \\(O(fcd)\\)。

在接下来的小节中，我们将解释如何降低算法复杂度，并减小 \\(d\\) 和 \\(f\\) 以获得更好的性能。

### 层次化 K-means {#hierarchical-k-means}

受限于时间复杂度，无论应用何种工程优化，标准 K-means 都无法突破线性加速的上限。即使在 GPU 上，这一过程也需要 30 分钟。因此我们必须从算法层面降低时间复杂度。

一个直观的思路是将样本划分为多个互不相交的子集，在每个子集上分别运行 K-means，然后再合并各个子集生成的聚类中心。为了平衡子集的大小与子集的数量，我们选择 \\(\sqrt{c}\\) 作为子集数量。为了生成这 \\(\sqrt{c}\\) 个子集，我们先执行一次小规模的 K-means，然后利用得到的 \\(\sqrt{c}\\) 个质心将 \\(n\\) 个向量分配到 \\(\sqrt{c}\\) 个互不相交的子集中。

假设各子集大小均匀，这一步的时间复杂度为 \\(O(f\sqrt{c}\sqrt{c}dl) \times \sqrt{c} = O(fc^{1.5}dl)\\)。如果 `f = 64` 且 `c = 160,000`，该算法的理论速度将提升约 400 倍。

这里还有一个小问题：每个子集应该分配多少个质心？如果忽略质心数量必须为整数的约束，答案是 \\(\frac{n}{|s|}c\\)。考虑到整数约束后，这个问题就类似于比例代表制中的席位分配问题，其中[圣拉古法（Sainte-Laguë method）](https://en.wikipedia.org/wiki/Sainte-Lagu%C3%AB_method)是一种能够最小化平均席位与选票比例偏差的算法。其工作原理如下：

> 在统计完所有选票后，依次为每个政党计算商数。商数的计算公式为 \\(\frac{V}{s_i+0.5}\\)，其中 \\(V\\) 是该政党获得的总票数，\\(s_i\\) 是目前为止已分配给该政党的席位数（所有政党初始值均为 \\(0\\)）。得数最高的政党获得下一个席位，随后重新计算其商数，重复此过程直至所有席位分配完毕。

现在，在 CPU 上进行聚类已经切实可行了。然而，这一算法本身并没有降低内存占用。

### 降维 {#dimensionality-reduction}

现在让我们回过头来看 K-means 样本所占用的 140 GB 内存。在一台 128 GB 内存的机器上，这必然会导致内存溢出（OOM）。考察空间复杂度 \\(O(fcd)\\)，我们有两种降低内存占用的途径：减小 \\(f\\)，以及减小 \\(d\\)。

我们先来减小 \\(d\\)。虽然听起来有些不可思议，但我们确实可以先对向量进行降维，再执行聚类，而且不会损害最终的精度。[Christos 的研究成果](https://arxiv.org/abs/1011.4632)表明，在低维投影上运行 K-means 依然能够保持良好的聚类精度。

> [Johnson–Lindenstrauss 引理](https://en.wikipedia.org/wiki/Johnson%E2%80%93Lindenstrauss_lemma)指出，高维空间中的一组点可以嵌入到维度低得多的空间中，且点与点之间的距离基本保持不变。在该引理的经典证明中，这种嵌入是通过随机正交投影实现的。

根据该定理，\\(n\\) 个向量可以降维到 \\(O(\lg n)\\) 维。具体而言，我们只需要构造一个随机高斯矩阵，通过矩阵乘法将高维向量降维为低维向量，然后在低维空间上执行 K-means。

由于我们的目标是降低内存占用，因此在采样阶段我们就直接应用 Johnson-Lindenstrauss 变换。最终我们会得到低维空间下的质心。我们并不尝试进行逆变换；相反，我们会再次对表进行采样，在经过 Johnson-Lindenstrauss 变换后的低维空间中找到最近的聚类簇，从而恢复出高维空间下的质心。

将维度从 768 降至 100 后，实例的常驻内存集大小（RSS）降至 23 GB，使我们能够在 i4i.xlarge 实例上完成索引构建。此外，理论上这也会让聚类速度提升 7 倍。结合层次化 K-means 与降维技术后，初始化阶段的耗时降至 24 分钟。

减小 \\(f\\) 则非常简单。它对应配置项 `build.internal.sampling_factor`，因此我们只需修改配置即可。将 \\(f\\) 设为 \\(64\\) 后，实例的常驻内存集大小进一步降至 6 GB，聚类速度也大约提升了 2 倍。

<a id="Sampling"></a>
### 采样 {#sampling}

为了执行聚类，我们需要从表中对向量进行采样。我们此前采用的方法是[水塘抽样（reservoir sampling）](https://en.wikipedia.org/wiki/Reservoir_sampling)，它虽然可靠但速度较慢。之前之所以使用该方法，是因为如果不进行全表扫描，我们无法预知表中的总行数；然而水塘抽样本身仍然需要执行全表扫描。

为了避免全表扫描，我们利用了 PostgreSQL 表访问方法（Table Access Method）的采样接口。该接口接收一个函数，该函数在给定最大块号（block number）时生成一个块号迭代器，随后接口会返回这些数据块中元组（tuple）的迭代器。为了生成这样一个随机块号迭代器，我们可以先生成一个有序序列，再对其执行 [Fisher–Yates 洗牌算法](https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle)，但这会消耗可观的内存。事实上，我们有一种更巧妙的方法：在密码学中，[伪随机置换（pseudorandom permutation）](https://en.wikipedia.org/wiki/Pseudorandom_permutation)是一种在统计上无法与真正随机置换区分开来的函数。

[Feistel 网络（Feistel network）](https://en.wikipedia.org/wiki/Feistel_cipher)可以用作伪随机置换。其定义为 \\(L_{i + 1} = R_{i}, R_{i + 1} = L_{i} \oplus F(R_i, K_i)\\)，其中 \\(F\\) 是哈希函数，\\(K_i\\) 是随机种子。该函数的输入为 \\((L_0, R_0)\\)，输出为 \\((L_n, R_n)\\)。因此它是一个从 \\([0, 2^n) \times [0, 2^n)\\) 到 \\([0, 2^n) \times [0, 2^n)\\) 的映射。巧妙之处在于，由于 \\(R_{i} = L_{i + 1}, L_{i} = R_{i + 1} \oplus F(L_{i + 1}, K_i)\\)，该函数是可逆的。可逆函数必然是双射（bijective）的，而 \\([0, 2^n) \times [0, 2^n)\\) 等价于 \\([0, 4^n)\\)，因此它构成了 \\([0, 4^n)\\) 上的一个置换。现在，只需过滤掉该置换中所有大于最大块号的元素，我们就得到了所需的惰性求值随机置换（lazy random permutation）。

基于该接口和这一置换函数，我们实现了块级采样（block sampling），从而只需访问被采样命中的向量数据块。

综合以上所有优化，初始化阶段现在的总耗时仅需 8 分钟。

## 4\. 减少锁竞争 {#4-reducing-contention}

在早期的实验中，如果在 Amazon i7i.16xlarge（64 vCPU）实例上使用 \\(n=2\\) 为 `LAION-100m` 数据集构建索引，插入阶段大约需要 420 分钟，且完全受限于计算瓶颈（computation-bound）。

从 0.1 版本开始，VectorChord 允许将 \\(n\\) 设置为不大于 \\(8\\) 的正整数。在我们看来，这对于十亿级规模的数据是必不可少的。不过在当时，我们并不清楚它具体能带来多大的加速效果。

在规格更小的 i7i.4xlarge（16 vCPU）实例上尝试 \\(n=3\\) 后，我们观察到插入阶段仅需 40–60 分钟即可完成。此时 CPU 利用率保持在 40% 左右，IO 吞吐量在 300 MB/s 到 800 MB/s 之间波动，这表明其中存在巨大的优化空间。

### 减少链表竞争 {#reducing-linked-list-contention}

插入阶段耗时 40–60 分钟。令人惊讶的是，我们的测试显示使用 8 个工作进程（worker）耗时 40 分钟，而使用 16 个工作进程反而耗时 55 分钟。这表明工作进程在插入过程中存在潜在的锁竞争。

在具体实现中，索引除了树结构之外，还维护了一个单链表用于存储全精度向量，而树中仅存储量化后的向量。这使得树节点体积小得多，从而能将整棵树放入内存中。

将 \\(n\\) 从 \\(2\\) 改为 \\(3\\) 后，插入阶段的计算量大幅减少，导致向该链表插入向量的操作变得更加频繁。并行工作进程在向同一个链表插入数据时产生了严重竞争，因此增加工作进程反而拖慢了插入速度，导致性能表现难以预测。

为了解决这个问题，我们将单个链表替换为 \\(1+k\\) 个链表。第一个链表存储树的前 \\(n\\) 层所用的全精度向量，其余 \\(k\\) 个链表存储最底层节点的向量。在构建索引期间，第 \\(i\\) 个工作进程将向量插入到第 \\((i\ \text{mod}\ k)\\) 个链表中。我们将默认值设为 \\(k=32\\)，这足以应对大多数场景。

完成这一改动后，CPU 利用率稳定在 54% 左右，插入阶段耗时缩短至约 30 分钟。

### 减少页面扩展锁竞争 {#reducing-page-extension-lock-contention}

此时的 CPU 利用率仍然暗示还有进一步优化的潜力。但瓶颈究竟在哪里？我们首先使用 `htop` 检查了 PostgreSQL 的工作进程状态。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1764296302226/4ac9364b-09d9-4a13-81b7-dc2252b800b6.png)

许多进程的标题显示为 `waiting`，表明 PostgreSQL 内部存在严重的锁竞争。通过在源码中搜索，我们追踪到设置 `waiting` 状态的代码位于 [lock.c](https://github.com/postgres/postgres/blob/REL_18_0/src/backend/storage/lmgr/lock.c#L1943)。为了测量进程脱离 CPU（off-CPU）的时间，我们使用了 [BCC](https://github.com/iovisor/bcc) 工具集中的 `offcputime`。随后，借助 Brendan Gregg 的 [FlameGraph](https://github.com/brendangregg/FlameGraph) 中的 `stackcollapse.pl` 和 `flamegraph.pl`，我们生成了进程 off-CPU 时间的火焰图。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1764294200682/6c64c880-2083-4c73-bf1e-65a10b61c77e.png)

结果令人意外：罪魁祸首竟然是 `LockRelationForExtension`，它在扩展索引文件时负责获取索引的扩展锁。

> [!TIP]
> 图中显示的 `ockRelationForExtension` 实际上应为 `LockRelationForExtension`。这可能是 `flamegraph.pl` 脚本的某种未知行为导致首字母被截断。

为什么获取这个锁会成为瓶颈？检索 PostgreSQL 邮件列表后，我们找到了这篇[讨论](https://postgr.es/m/20221029025420.eplyow6k7tgu6he3@awork3.anarazel.de)。

简而言之，PostgreSQL 会对每个索引加锁，以防止该索引被并发扩展，但这个锁的粒度过于粗放。感谢 Andres Freund 提交的补丁，它缩小了临界区（critical section）并修复了这一问题，但该优化需要使用 PostgreSQL 16 引入的新 API。

由于 VectorChord 支持 PostgreSQL 13 至 18，我们在早期开发中使用了旧版 API，不幸因此错过了这项优化。

切换到新 API 后，插入阶段的耗时缩短到了 22 分钟。

### 批量页面扩展 {#bulk-page-extensions}

然而，新一轮的性能剖析显示，瓶颈依然停留在同一区域。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1764294272317/208f1bcb-ee51-46a0-98b4-9e18257e48a2.png)

既然锁的临界区已经缩小，我们就需要加快页面扩展本身的速度来缓解瓶颈。在文件系统中，使用 `fallocate` 扩展文件非常快。如果使用 `fallocate` 来扩展索引，扩展单个页面的平均耗时就会大幅缩短。那么问题来了：我们能否使用 `fallocate` 来扩展索引？

答案是肯定的。如果单次扩展索引的页面数超过 8 页，PostgreSQL 会自动从 `pwrite` 切换到 `fallocate`。通过每次一次性申请 16 个页面，我们显著提升了页面扩展的速度。

完成这一改动后，插入阶段耗时骤降至 9 分钟，CPU 利用率稳定在 90%，写入吞吐量保持在 1.8 GB/s 左右。`iostat` 报告的 IO 利用率达到 0.75–0.85，表明我们终于充分利用了硬件资源。

这里仍然存在进一步调优的空间，但就目前而言，插入阶段已不再有任何明显的瓶颈。

## 5\. 并行化压缩 {#5-parallelize-compaction}

在树的最底层，量化向量以两种布局形式存在：

* 非紧凑布局（面向插入）：每个量化向量独立存储为一个元组，因此可以直接追加数据，而无需修改现有元组。
    
* 紧凑布局（面向检索）：每 32 个量化向量打包存储为一个元组。该布局针对 SIMD 指令集进行了优化，能够大幅提升检索速度。
    

所有向量在最初插入时都采用非紧凑布局，并在最后一个阶段统一转换为紧凑布局。值得注意的是，此前这一阶段是串行执行的，在索引构建过程中大约耗时 8 分钟。

由于前两个阶段的速度已经大幅提升，优化压缩阶段变得愈发重要。因此我们将这一阶段并行化：假设有 \\(k\\) 个工作进程，树的第 \\(n\\) 层有 \\(m\\) 个节点，那么第 \\(i\\) 个节点的子节点将由第 \\((i\ \text{mod}\ k)\\) 个工作进程负责压缩。得益于并行化，压缩阶段现在的耗时不到 1 分钟。

你可能会注意到，为了维持检索性能，高效索引在日常运行中也需要定期执行这种压缩操作。PostgreSQL 提供了 `VACUUM` 机制来承担此类维护任务，因此该压缩阶段也会在 `VACUUM` 过程中定期对索引执行。遗憾的是，我们无法在 `VACUUM` 中将其并行化：PostgreSQL 不允许索引使用嵌套并行（nested parallelism）。如果 `VACUUM` 本身是并行执行的，索引就无法再次启动并行工作进程。

## 6\. 总结 {#6-conclusion}

在此之前，使用 VectorChord `0.5.3` 在 Amazon i7i.4xlarge 实例上为 `LAION-100M` 数据集构建索引是不可行的，因为会发生内存溢出（OOM）错误。[将聚类卸载到 GPU](/zh/docs/vchord/usage/external-build/) 使得索引构建成为可能，在查询 Top 10 结果时，可在 **120** QPS 下达到 **95.6%** 的召回率（recall），但需要在 GPU 上耗时 **30 分钟**，并在 i7i.4xlarge 上耗时 **420 分钟**。

凭借 VectorChord `1.0.0` 引入的一系列优化，现在完全可以在单台 i7i.4xlarge 实例上用仅仅 **18 分钟**完成整个索引构建，并在相同 QPS 下达到 **94.9%** 的召回率。

```pgsql
CREATE INDEX ON laion USING vchordrq (embedding vector_ip_ops) WITH (options = $$
build.pin = 2
[build.internal]
lists = [400, 160000]
build_threads = 16
spherical_centroids = true
kmeans_algorithm.hierarchical = {}
kmeans_dimension = 100
sampling_factor = 64
$$);
```

我们的目标是让 VectorChord 成为 PostgreSQL 上最优秀的检索方案之一，无论你是在构建第一个原型，还是在应对十亿级规模的数据集。如果你已经在使用 pgvector，我们非常欢迎你在真实工作负载上试用 VectorChord 1.0，并告诉我们它在哪些地方帮到了你，又在哪些地方还可以做得更好。
