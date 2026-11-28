---
title: "构建大型索引"
linkTitle: "大规模构建"
description: "让上亿到数十亿行的 vchordrq 索引构建控制在时间和内存预算之内，并跟踪构建进度。"
weight: 80
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/partitioning-tuning.md"
math: true
aliases:
  - "/docs/usage/partitioning-tuning/"
  - "/vectorchord/usage/partitioning-tuning/"
  - "/docs/vchord/usage/monitoring/"
  - "/docs/usage/monitoring/"
icon: fa-solid fa-table-columns
---

在几千万行以上的表上，vchordrq 构建的大部分时间和几乎全部内存都花在 k-means 这一步。有三个选项可以缩减它，而且可以叠加使用：三者都用上时，1 亿条 768 维向量 18 分钟建完，只用 6 GiB 内存。如果想把 k-means 完全移出数据库服务器，见[外部构建](/zh/docs/vchord/usage/external-build/)。

## 时间和内存花在哪里 {#where}

k-means 为每个叶子列表采样 `sampling_factor` 个向量来训练。使用标准算法时，它的工作内存约为

\[
4 \cdot D \cdot C \cdot (F + T + 1) \text{ 字节}
\]

耗时则随 \(F \cdot C^2 \cdot D\) 增长。其中 \(C\) 是叶子列表数（`lists` 的最后一个值），\(D\) 是聚类时使用的维度，\(F\) 是 `sampling_factor`，\(T\) 是 `build_threads`。下面每个选项各自缩小其中一项。

k-means 内存不够时，构建会以 `out of memory` 错误终止，服务器本身不受影响。

## 层次化 k-means {#hierarchical-k-means}

`lists` 分两层时，层次化 k-means 先对粗粒度层聚类，再在每个粗粒度簇内分别聚类。耗时从随 \(C^2\) 增长降为随 \(C^{1.5}\) 增长，对召回率影响很小：

```toml
[build.internal]
lists = [400, 160000]
kmeans_algorithm = { hierarchical = {} }
```

## 少采样一些向量 {#reduce-sampling-factor}

把 `sampling_factor` 从默认的 `256` 调低，时间和内存按比例减少，代价是聚类中心略不精确：

```toml
[build.internal]
sampling_factor = 64
```

## 在更低的维度上聚类 {#dimensionality-reduction}

`kmeans_dimension` 先把向量降到指定维度再聚类，之后把聚类中心还原到完整维度。对 768 维嵌入取 `100`，k-means 的工作量减少近 8 倍。取值不小于列的维度时会被忽略，并给出警告。

```toml
[build.internal]
kmeans_dimension = 100
```

## 参考配置 {#reference-settings}

### LAION-100M {#laion-100m}

来自 [SISAP 2024](https://sisap-challenges.github.io/2024/datasets/) 的 1 亿条 768 维向量，内积距离。在 AWS `i7i.4xlarge`（16 vCPU、128 GiB 内存、本地 NVMe）上 **18 分钟**建完，构建内存峰值 **6 GiB**。在 `probes = '40,140'`、`epsilon = 1.4` 下，以 0.949 的 top-10 召回率达到每秒 120 次查询。

```sql
CREATE INDEX ON laion USING vchordrq (embedding vector_ip_ops)
WITH (options = $$
build.pin = 2
[build.internal]
lists = [400, 160000]
build_threads = 16
spherical_centroids = true
kmeans_algorithm = { hierarchical = {} }
kmeans_dimension = 100
sampling_factor = 64
$$);
```

### DEEP-1B {#deep-1b}

来自 [BIG-ANN](https://big-ann-benchmarks.com/neurips21.html) 的 10 亿条 96 维向量，L2 距离。在 AWS `i7ie.6xlarge`（24 vCPU、192 GiB 内存、本地 NVMe）上 **107 分钟**建完，构建内存峰值 **64 GiB**。在 `probes = '40,250'` 下，以 0.951 的 top-10 召回率达到每秒 68 次查询。

```sql
CREATE INDEX ON deep USING vchordrq (embedding vector_l2_ops)
WITH (options = $$
residual_quantization = true
build.pin = 2
[build.internal]
lists = [800, 640000]
build_threads = 24
kmeans_algorithm = { hierarchical = {} }
$$);
```

## 监控构建进度 {#monitoring}

<a id="phases"></a><a id="Phases"></a><a id="phases-vchordrq"></a><a id="phases-vchordg"></a><a id="catalog-statistics"></a>

两种索引都会在 PostgreSQL 的 [`pg_stat_progress_create_index`](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING) 视图中报告进度：

```sql
SELECT phase, tuples_done, tuples_total,
       round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS blocks_pct
FROM pg_stat_progress_create_index;
```

vchordrq 构建依次经过下面这些阶段。k-means 阶段会在阶段名里报告自己的百分比；插入行通常是最长的阶段。

| 阶段 | 内容 |
| --- | --- |
| `initializing` | 检查选项。 |
| `initializing index, by internal build (n %)` | 在样本上运行 k-means。只有一个列表或使用预先算好的聚类中心时，分别显示为 `by default build` 和 `by external build`。 |
| `initializing index` | 把聚类中心写入索引。 |
| `inserting tuples from table to index` | 逐行量化并追加到所属列表；`tuples_done` 和 `blocks_done` 随之增长。 |
| `compacting tuples in index` | 压缩列表。 |

vchordg 构建只有两个阶段：先是 `initializing`，然后是 `inserting tuples from table to index`。
