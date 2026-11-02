---
title: "VectorChord 外部聚类中心构建的优势与操作步骤"
date: 2024-12-10
description: "利用外部计算资源与层次化 K-means 在 VectorChord 中进行外部聚类中心构建，显著提升大规模向量搜索的索引效率"
author: "[Keming Yang](https://github.com/kemingy) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorsearch"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/benefits-and-steps-of-external-centroids-building-in-vectorchord"
upstream_copyright: "© 2024 Keming Yang (TensorChord Inc.)"
math: true
aliases:
  - "/blog/benefits-and-steps-of-external-centroids-building-in-vectorchord/"
  - "/benefits-and-steps-of-external-centroids-building-in-vectorchord/"
---

聚类（Clustering）是向量搜索中的重要组成部分，而 K-means 算法依然是目前应用最广泛的技术之一。然而，它的简洁性也伴随着一个显著的缺点：密集的计算资源消耗使其在处理大规模数据集时往往力不从心。本文将探讨这一挑战产生的原因，并介绍如何利用外部构建（External Builds）来克服它，同时分享我们在实现这一方案过程中的技术洞察。

### 为什么需要外部构建 {#why-we-need-it}

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711948118/a8ca38d3-580f-4f20-90b9-03c826289a7c.png)

VectorChord 使用 IVF + RaBitQ 来执行向量搜索。IVF 聚类簇的质量会直接影响搜索精度和速度。K-means 通常需要迭代数十轮才能收敛，而在每一轮中，所有采样的向量都需要被分配到距离最近的聚类簇中。这是计算最密集的环节，不过好消息是，这一过程非常容易并行化。

然而，承载向量搜索服务的数据库实例通常没有富余的计算资源来执行这种大规模并行计算；如果强行在数据库实例上运行，会严重影响线上向量搜索服务的稳定性。在这种情况下，利用外部计算实例来加速索引构建阶段便成为了顺理成章的选择。

### 外部 K-means 聚类 {#external-k-means}

源向量数据的总大小可能是实例内存的数倍。为了避免内存溢出（OOM），我们可以在聚类之前先对向量进行采样。聚类簇数量（\(n_{cluster}\)）的推荐选择范围为：


$$
4 * \sqrt{n_{vec}} \le n_{cluster} \le 8 * \sqrt{n_{vec}}
$$


通常，我们最多只需要采样 `256 * n_cluster` 个向量。如果数据无法全部装入内存，可以通过水塘抽样（Reservoir Sampling）来完成采样。

如果你有现成可用的 GPU 环境，它的运行速度可以比 CPU 实例快上数十倍甚至数百倍。否则，你可能会发现一半甚至大部分时间都花在了启动实例、传输数据和采样上，而不是真正的计算上。

下面的聚类实验是在一台运行 `faiss-gpu (max_iter=25)` 的 `H100 SXM5` 实例（成本为 $3.29 / 小时）与一台运行 `faiss-cpu (max_iter=25)` 的 `i4i.8xlarge` 实例（成本为 $2.746 / 小时）上进行的对比。算下来，使用 CPU 实例进行聚类的总成本大约是 GPU 实例的 **60** 倍。

| **数据集** | **Cohere** (1024 × 10m) | **MS MARCO** (768 × 100m) |
| --- | --- | --- |
| `n_cluster` | 16384 | 65536 |
| GPU K-means 耗时 | 80s | 960s |
| CPU K-means 耗时 | 5850s | 68420s |

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711341914/feb175a8-7c40-446e-91ac-ebb5c2ef9fb0.png)

> [!TIP]
> 敬请期待我们即将推出的云端外部索引构建支持。

显而易见，更大的 `n_cluster` 会导致计算时间呈指数级增长。此外，当 `n_cluster` 很大时，普通的 K-means 也很难維持各个聚类簇之间的相对平衡。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711427796/555454cf-f0d7-472f-b3cc-dc5f563c52c9.png)

克服这一问题的好方法是采用层次化 K-means（Hierarchical K-means）。通常 2 层结构就已经足够。我们可以构建一个 `n_cluster = [40, 100]` 的层次化 K-means，而不是直接构建 `n_cluster = 4000` 的扁平 K-means。这种方式将繁重的计算转化为了 I/O 和轻量级计算，当你希望使用 CPU 实例处理大规模数据集时，这是一个非常理想的选择。

<a id="Steps"></a>
### 操作步骤 {#steps}

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711098280/7498c023-1b42-4cbc-b8b8-b247eb97baaf.png)

假设向量数据已经存储在 VectorChord 中，我们需要执行以下步骤：

1. 导出向量并将其上传至 S3
    
2. 启动外部计算实例来运行 K-means 聚类
    
3. 将生成的聚类中心（Centroids）插回 VectorChord
    
4. 使用外部聚类中心表构建索引
    

我们提供了一些脚本，方便你快速上手：

[外部构建文档](/zh/docs/usage/external-build/)

你可以克隆代码仓库并亲自尝试：

```bash
gh repo clone tensorchord/VectorChord
cd VectorChord/scripts
# export embeddings to a h5 file
python dump.py -n [table name] -c [column name] -d [dim] -o export.hdf5
# upload to s3
aws s3api put-object --bucket external-centroids --key export.hdf5 --body export.hdf5
# download in the CPU/GPU worker
aws s3api get-object --bucket external-centroids --key export.hdf5 export.hdf5
# run K-means with CPU
python train.py -i export.hdf5 -o centroid.npy -lists [lists]
# or with GPU
python train.py -i export.hdf5 -o centroid.npy -lists [lists] -g
# insert to the centroids table & build the index
python index.py -n [table name] -i export.hdf5 -c centroid.npy -d [dim]
```

<a id="Summary"></a>
### 总结 {#summary}

综上所述，在 VectorChord 中利用外部聚类中心构建，为处理向量搜索中的大规模数据集提供了显著优势。通过利用外部资源执行计算密集型的 K-means 聚类，我们不仅能够提升搜索过程的效率与精度，还能有效缓解向量搜索数据库实例的资源压力，并在使用 GPU 环境时大幅缩短处理时间。结合层次化 K-means 可以进一步平衡计算与 I/O 操作，使得使用 CPU 实例处理超大规模数据集也同样切实可行。
