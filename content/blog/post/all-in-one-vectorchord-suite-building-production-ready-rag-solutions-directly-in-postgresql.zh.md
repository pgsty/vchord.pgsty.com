---
title: "一站式 VectorChord 套件：直接在 PostgreSQL 中构建生产就绪的 RAG 解决方案"
date: 2025-04-29
description: "利用 VectorChord 套件的向量搜索、BM25 排序和灵活分词扩展，直接在 PostgreSQL 中构建生产就绪的 RAG 解决方案"
author: "xieydd"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/all-in-one-vectorchord-suite-building-production-ready-rag-solutions-directly-in-postgresql"
aliases:
  - "/blog/all-in-one-vectorchord-suite-building-production-ready-rag-solutions-directly-in-postgresql/"
  - "/all-in-one-vectorchord-suite-building-production-ready-rag-solutions-directly-in-postgresql/"
---

检索增强生成（Retrieval-Augmented Generation, RAG）正在彻底改变我们与海量数据集及语言模型的交互方式。通过在生成回答之前先检索相关信息，RAG 系统能够提供更准确、更具上下文感知能力且实时更新的答案。然而，构建稳健、可扩展且高效的 RAG 流水线依然面临诸多挑战，在生产环境中更是如此。

许多解决方案采用了复杂的架构，分别为向量搜索、关键词搜索和主数据存储使用不同的数据库。这通常会导致数据同步难题、更高的基础设施复杂度以及高昂的运维成本。

如果可以直接在你信赖的 PostgreSQL 数据库内部构建一套强大且生产就绪的 RAG 系统，会怎样呢？

为此，我们推出了 **VectorChord 套件（VectorChord Suite）**——这是一组旨在将高性能向量搜索、原生 BM25 排序以及灵活的分词能力直接引入 Postgres 的 PostgreSQL 扩展集合。下面让我们一起探索它的各个组件，看看它们如何赋能下一代 RAG 解决方案。

## 什么是 VectorChord 套件？ {#what-is-the-vectorchord-suite}

该套件由三个协同工作的核心 PostgreSQL 扩展组成：

1. [**VectorChord：**](https://github.com/tensorchord/VectorChord)核心向量搜索引擎。专为在 PostgreSQL 内部实现可扩展、高性能且磁盘高效的向量相似度搜索而设计。
    
2. [**VectorChord-bm25：**](https://github.com/tensorchord/VectorChord-bm25)该扩展利用高效的 Block-WeakAnd 算法，直接在 PostgreSQL 内部实现了成熟的 BM25 排序算法。BM25 是基于关键词频率和文档特征进行相关性排序的行业标准。
    
3. [**pg\_tokenizer.rs：**](https://github.com/tensorchord/pg_tokenizer.rs)提供高效全文搜索所必需的文本分词（Tokenization）能力，支持对全文搜索的文本处理方式进行细粒度控制。
    

通过组合这些扩展，你可以完全在 PostgreSQL 内部解锁构建高级 RAG 系统的强大能力。

## 如何使用 VectorChord 套件 {#how-to-use-the-vectorchord-suite}

你可以使用 `tensorchord/vchord-suite` 镜像来运行 TensorChord 提供的多个扩展。该镜像基于官方 Postgres 镜像构建，包含以下扩展：

```powershell
docker run   \           
  --name vchord-suite  \
  -e POSTGRES_PASSWORD=postgres  \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg17-latest
  # If you want to use ghcr image, you can change the image to `ghcr.io/tensorchord/vchord-suite:pg17-latest`.
  # if you want to use the specific version, you can use the tag `pg17-20250414`, supported version can be found in the support matrix.
```

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
\dx
pg_tokenizer | 0.1.0   | tokenizer_catalog | pg_tokenizer
vchord       | 0.3.0   | public            | vchord: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
vchord_bm25  | 0.2.0   | bm25_catalog      | vchord_bm25: A postgresql extension for bm25 ranking algorithm
vector       | 0.8.0   | public            | vector data type and ivfflat and hnsw access methods
```

## VectorChord 套件的应用场景 {#use-cases-for-the-vectorchord-suite}

### 场景 1：结合原生 BM25 与 VectorChord 的强大混合搜索 {#use-case-1-powerful-hybrid-search-with-native-bm25-and-vectorchord}

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1744643437495/b57592c9-e1c2-4940-ae59-751ff93e37a3.jpeg)

在 RAG 时代，高效的检索至关重要。无论是单纯的关键词搜索还是单纯的向量搜索，都并非十全十美：

* **关键词搜索（如 BM25）**：擅长精准匹配，能够找出包含精确关键词的文档，非常适合结构化查询和特定术语搜索。但它在处理同义词、改写表达以及理解深层*含义*或语义意图方面表现欠佳。（利用 `VectorChord-bm25` 和 `pg_tokenizer`）。
    
* **向量搜索**：擅长捕捉深层语义和概念之间的关联，即使文档中没有出现完全一致的关键词，也能找到相关信息。但在面对要求精确匹配特定术语的查询时，有时会缺乏精准度。（利用 `VectorChord`）。
    

**解决方案：混合搜索（Hybrid Search）**。通过在 Postgres 内部结合这两种方法的优势，VectorChord 套件弥合了这一差距。你可以运行一条同时利用以下两者的查询：

* 使用 `VectorChord-bm25`（由 `pg_tokenizer` 驱动）保证关键词精准匹配。
    
* 使用 `VectorChord` 实现深层语义理解。
    

两者的检索结果可以进行智能融合（例如使用倒数排序融合 RRF 或基于模型的重排序 Rerank），从而生成比任何单一方法都更准确、上下文更相关且更具语义感知能力的最终排序。这将为你的 RAG 应用带来显著更优的检索表现。

<a id="use-case-2-beyond-text-ocr-free-rag-with-colqwen2-vectorchord"></a>
### 场景 2：超越纯文本——基于 ColQwen2 与 VectorChord 的免 OCR RAG {#use-case-2-beyond-text---ocr-free-rag-with-colqwen2--vectorchord}

为 PDF 或扫描图像等文档构建 RAG 系统，通常涉及繁琐的预处理流水线。传统方法高度依赖光学字符识别（OCR）和版面分析来提取文本。这一过程往往存在以下问题：

* **速度慢**：OCR 的计算开销可能非常高昂。
    
* **容易出错**：OCR 的准确率受文档质量影响很大。
    
* **信息有损**：在提取纯文本的过程中，表格、图表、格式以及相对位置等关键视觉上下文信息往往会丢失。
    

**解决方案：免 OCR、具备视觉感知能力的 RAG**。如果可以直接根据文档的*外观版式*及其*内容*进行查询，而无需显式执行 OCR，会怎样呢？

现在，通过结合以下两项技术即可实现这一目标：

1. **多模态视觉语言模型（VLM）**：像 ColQwen2 这样的模型可以直接处理图像（文档页面），并生成*同时*捕捉文本内容和视觉版面信息的向量嵌入。
    
2. **VectorChord 的多向量能力**：VectorChord 可以在 Postgres 内部高效地为每篇文档存储和搜索*多个*向量——允许你存储代表不同维度特征（如文本内容、视觉布局）的嵌入向量。
    

借助这套方案，你可以直接在 PostgreSQL 中使用引用视觉元素的提示词（例如“查找包含对比销售数据的柱状图的文档”）或结合文本与视觉线索的查询来检索文档数据库。这不仅简化了你的 RAG 技术栈，通过保留视觉上下文提升了检索准确率，还彻底消除了传统 OCR 流水线带来的性能瓶颈。

## 为什么要在 PostgreSQL 中构建 RAG？ {#why-build-rag-in-postgresql}

在 Postgres 内部使用 VectorChord 套件具有诸多显著优势：

* **数据统一**：将源数据、文本、元数据和向量嵌入全部保存在同一个地方。
    
* **降低复杂度**：无需再维护独立的向量数据库和数据同步流水线。
    
* **复用现有基础设施**：充分利用你现有的 Postgres 专业知识、工具链和运维实践。
    
* **事务完整性**：受益于 PostgreSQL 强大的 ACID 事务保障。
    
* **丰富的生态系统**：无缝使用 Postgres 生态系统中极其丰富的工具与功能特性。
    

<a id="Conclusion"></a>
## 总结 {#conclusion}

VectorChord 套件将 PostgreSQL 打造成了一个强大且生产就绪的高级 RAG 解决方案构建平台。通过集成高性能向量搜索（`VectorChord`）、成熟的关键词排序（`VectorChord-bm25`）以及灵活的文本处理（`pg_tokenizer`），你可以直接在数据库内部实现混合搜索和免 OCR 多模态检索等前沿技术。立即在 PostgreSQL 中使用 VectorChord，简化系统架构、提升检索精度，充分释放 RAG 的全部潜力。

## 往期博客文章 {#previous-blog-post}

在此前的博客中，我们分享过一些实际应用案例，其中的所有镜像现在都可以直接替换为 VectorChord Suite 镜像：

* [在 PostgreSQL 中利用 ColBERT Rerank 为向量搜索加速](/zh/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)
    
* [使用 Postgres 原生 BM25 与 VectorChord 实现混合搜索](/zh/blog/post/hybrid-search-with-postgres-native-bm25-and-vectorchord/)
    
* [超越文本：使用 Modal 与 VectorChord 在 PostgreSQL 中解锁免 OCR 的 RAG](/zh/blog/post/beyond-text-unlock-ocr-free-rag-in-postgresql-with-modal-and-vectorchord/)
    

<a id="References"></a>
## 参考资料 {#references}

* [https://vchord.pgsty.com/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)
    
* [https://vchord.pgsty.com/zh/blog/post/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/](/zh/blog/post/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/)
    
* [https://vchord.pgsty.com/zh/blog/post/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/](/zh/blog/post/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/)
