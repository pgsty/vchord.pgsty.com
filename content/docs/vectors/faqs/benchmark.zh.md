---
title: "基准测试"
linkTitle: "基准测试"
description: "pgvecto.rs 从诞生之初就专注于性能。我们持续监控 pgvecto.rs 的性能表现，并与其他向量检索库进行对比。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/faqs/benchmark.md"
aliases:
  - "/faqs/benchmark/"
---

`pgvecto.rs` 从诞生之初就高度专注于性能。我们持续监控 `pgvecto.rs` 的性能表现，并与其他向量检索库进行对比测试。以下基准测试结果来自 2024 年 1 月。

测试在 Google Cloud [n2-standard-8](https://cloud.google.com/compute/docs/general-purpose-machines#n2_series)（8 vCPU，32 GB 内存）实例上进行，使用 `laion-768-5m-ip` 数据集。

<a id="pgvecto-rs-v-s-pgvector"></a>
## `pgvecto.rs` 对比 `pgvector` {#pgvecto-rs-vs-pgvector}

在使用 HNSW 索引时，`pgvecto.rs` 在保持约 97% 略高召回精度的同时，每秒响应数（RPS）可达到 `pgvector` 的 **2.5 倍**。当对召回精度要求更高时，这一性能优势还会进一步扩大。

![pgvecto.rs_vs_pgvector](/pgvecto-rs/faqs/images/2024Jan_pgvectors_compare.png)

启用 `vbase` 模式后，在不同的过滤条件选择率（filter probability）下，`pgvecto.rs` 的每秒响应数相比 `pgvector` 均可提升 **2 倍以上**。

![pgvecto.rs_vs_pgvector_filter](/pgvecto-rs/faqs/images/2024Jan_pgvectors_filter_compare.png)

![vbase](/pgvecto-rs/faqs/images/vbase.png)

## 不同量化方法的对比 {#different-quantization-methods}

`pgvecto.rs` 支持多种[量化方法](/zh/docs/vectors/usage/quantization/)以及不同低精度的[索引方式](/zh/docs/vectors/usage/indexing/)。这些方法有助于在不同数据规模下大幅降低内存占用。下图展示了 `pgvecto.rs` 在不同量化方法下的性能表现：

![pgvecto.rs_quantization](/pgvecto-rs/faqs/images/2024Jan_pgvectors_quantization.png)

<a id="shortening-embeddings-a-k-a-matryoshka-embedding-https-aniketrege-github-io-blog-2024-mrl"></a>
## 缩短嵌入向量（即 [Matryoshka Embedding](https://aniketrege.github.io/blog/2024/mrl/)） {#shortening-embeddings-aka-matryoshka-embedding}

OpenAI 的[最新嵌入模型](https://openai.com/blog/new-embedding-models-and-api-updates)支持缩短嵌入向量（Shortening Embeddings），开发者只需“直接移除序列末尾的部分数值”，即可在更短的维度下依然保留有效的文本语义表征。

> 这一特性带来了极高的使用灵活性。例如，当使用的向量数据存储仅支持最高 1024 维的嵌入向量时，开发者依然可以使用我们最强大的嵌入模型 `text-embedding-3-large`，并将 API 参数 `dimensions` 指定为 1024，从而将嵌入向量从 3072 维缩短为 1024 维，以极小的精度折衷换取更紧凑的向量体积。

以下是针对缩短后嵌入向量的性能基准测试。测试采用 [dbpedia-entities-openai3-text-embedding-3-large-3072-1M](https://huggingface.co/datasets/Qdrant/dbpedia-entities-openai3-text-embedding-3-large-3072-1M) 数据集。原始嵌入向量为 3072 维，缩短后的嵌入向量分别为 256 维和 1024 维。基准测试同样在 Google Cloud 的 `n2-standard-8`（8 vCPU，32 GB 内存）虚拟机上进行。

![](/pgvecto-rs/faqs/images/shorten-vector.png)

基准测试中的 **First Pass（初筛阶段）** 表明，仅使用缩短后的嵌入向量时，其召回精度不如完整维度的嵌入向量：256 维 HNSW 索引仅能达到约 65% 的准确率，而 1024 维 HNSW 索引约为 85%。

然而，当结合使用[自适应检索（Adaptive Retrieval）](/zh/docs/vectors/use-case/adaptive-retrieval/)时，缩短后嵌入向量的最终准确率能够超过 95%。此外，采用这种方法还能在 RPS（每秒请求数）和查询延迟方面带来显著提升。

## 二值向量 {#binary-vectors}

`pgvecto.rs` 支持[二值向量（Binary Vectors）](/zh/docs/vectors/reference/vector-types/bvector/)。`bvector` 类型专为存储效率与计算性能而优化，采用按位紧凑打包（bit-packed）的方式存储二值向量，并针对二值向量的距离计算进行了专门优化。

以下是 `bvector` 类型的性能基准测试，使用 [dbpedia-entities-openai3-text-embedding-3-large-3072-1M](https://huggingface.co/datasets/Qdrant/dbpedia-entities-openai3-text-embedding-3-large-3072-1M) 数据集，测试环境为 Google Cloud 上的 `n2-standard-8`（8 vCPU，32 GB 内存）虚拟机。

我们将 100 万条二值向量写入表中并建立索引，随后对每条查询向量运行 KNN 搜索。为 100 万条二值向量建立索引仅需约 600 MB 内存，而使用普通 `vector` 类型为相同数量的向量建立索引则需要约 18 GB 内存。

![bvector](/pgvecto-rs/faqs/images/bvector.png)

可以看到，单纯使用 `bvector` 的召回精度略低于 `vector` 类型，但如果结合采用[自适应检索（Adaptive Retrieval）](/zh/docs/vectors/use-case/adaptive-retrieval/)，其准确率同样能够超过 95%。
