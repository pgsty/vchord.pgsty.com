---
title: "分区调优"
linkTitle: "分区调优"
description: "对于大表而言，分区阶段主导了整个索引构建的时间与内存消耗。"
weight: 140
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/partitioning-tuning.md"
math: true
aliases:
  - "/zh/docs/usage/partitioning-tuning/"
  - "/vectorchord/usage/partitioning-tuning/"
icon: fa-solid fa-table-columns
---

对于大表而言，分区阶段主导了整个索引构建的时间与内存消耗。

分区阶段的时间复杂度为 \(O(FC^{2}DL)\)，内存消耗（以字节为单位）可以近似表示为 \(4DC(F + T + 1)\)，

其中：
* \(D\) 是向量维度（如果设置了 `build.internal.kmeans_dimension`，则为该参数的值）。
* \(F\) 是 `build.internal.sampling_factor`。
* \(C\) 是 `build.internal.lists[-1]`。
* \(T\) 是 `build.internal.build_threads`。
* \(L\) 是 `build.internal.kmeans_iterations`。

本页介绍几种用于优化构建时间和内存消耗的调优技巧。

## 层次 K-means {#hierarchical-k-means}

层次 K-means（Hierarchical K-means）是一种比[劳埃德算法（Lloyd's algorithm）](https://en.wikipedia.org/wiki/Lloyd%27s_algorithm)更快的聚类算法。应用该算法后，渐近时间复杂度将降低至 \(O(FC^{1.5}DL)\)。作为折中，它会对搜索性能和召回率产生轻微的负面影响。

用法：

```toml
build.internal.kmeans_algorithm.hierarchical = {}
```

## 降低采样因子 {#reduce-sampling-factor}

降低采样因子（sampling factor）可以线性地改善构建时间和内存消耗。作为折中，它会对搜索性能和召回率产生中等程度的负面影响。

用法：

```toml
build.internal.sampling_factor = 64
```

## 降维 {#dimensionality-reduction}

降维功能使用快速约翰逊-林登施特劳斯变换（Fast Johnson–Lindenstrauss transform），将参与聚类的向量维度降低至原始维度以下，从而线性地改善构建时间和内存消耗。作为折中，它会对搜索性能和召回率产生轻微的负面影响。

用法：

```toml
build.internal.kmeans_dimension = 100
```

## 参考配置 {#reference-settings}

### LAION 100M {#laion-100m}

数据集：

* 来源：https://sisap-challenges.github.io/2024/datasets/
* 度量方式：内积（Inner Product）
* 维度：768
* 向量数量：100,000,000
* 测试向量数量：1,000

测试机器（AWS EC2 i7i.4xlarge）：

* CPU：Intel Xeon Platinum 8559C
* vCPU 数量：16
* 内存：128 GiB
* 存储：3750 GiB NVMe SSD

```sql
CREATE INDEX ON laion USING vchordrq (embedding vector_ip_ops) WITH (options = $$
build.pin = 2
build.internal.lists = [400, 160000]
build.internal.build_threads = 16
build.internal.spherical_centroids = true
build.internal.kmeans_algorithm.hierarchical = {}
build.internal.kmeans_dimension = 100
build.internal.sampling_factor = 64
$$);
```

测试结果：

* 总构建时间：18 分钟
* 峰值内存：6 GiB
* 测试用例 1
  * 参数
    * `vchordrq.probes = '40,140'`
    * `vchordrq.epsilon = 1.4`
  * QPS @ Top10：120
  * Recall @ Top10：0.949

### DEEP 1B {#deep-1b}

数据集：

* 来源：https://big-ann-benchmarks.com/neurips21.html
* 度量方式：欧氏距离（Euclidean）
* 维度：96
* 向量数量：1,000,000,000
* 测试向量数量：10,000

测试机器（AWS EC2 i7ie.6xlarge）：

* CPU：Intel Xeon Platinum 8559C
* vCPU 数量：24
* 内存：192 GiB
* 存储：7500 GiB NVMe SSD

```sql
CREATE INDEX ON deep USING vchordrq (embedding vector_l2_ops) WITH (options = $$
build.pin = 2
residual_quantization = true
build.internal.lists = [800, 640000]
build.internal.build_threads = 24
build.internal.kmeans_algorithm.hierarchical = {}
$$);
```

测试结果：

* 总构建时间：107 分钟
* 峰值内存：64 GiB
* 测试用例 1
  * 参数
    * `vchordrq.probes = '40,250'`
  * QPS @ Top10：68
  * Recall @ Top10：0.951
