---
title: "VectorChord-BM25：用 BM25 排序彻底革新 PostgreSQL 搜索——速度比 ElasticSearch 快 3 倍"
date: 2025-02-24
description: "VectorChord-BM25 通过 BM25 排序增强 PostgreSQL 搜索能力，速度比 ElasticSearch 快 3 倍，支持 BERT、Tocken 和 Unicode 分词器"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch"
upstream_copyright: "© 2025 Jinjing Zhou (TensorChord Inc.)"
math: true
aliases:
  - "/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/"
  - "/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/"
---

我们非常高兴与大家分享一款重磅新作：**VectorChord-BM25**，这是一款旨在让 PostgreSQL 全文检索更上一层楼的全新扩展。无论您是在构建小型应用还是管理大规模系统，这款工具都能将先进的 BM25 评分与排序能力直接引入 PostgreSQL，让您的搜索更智能、更迅速。

<a id="what-s-new"></a>
### **有哪些新特性？** {#whats-new}

* **BM25 评分与排序**：借助 BM25 获得更精准、更相关的搜索结果，助您快速定位最重要的信息。
    
* **优化的索引结构**：得益于 Block WeakAnd 算法，即便面对大规模数据集，搜索也能更加快速高效。
    
* **增强的分词能力**：改进的词干提取与停用词处理机制，带来更高的准确度与更流畅的性能表现。
    

我们将 VectorChord-BM25 打造得简洁、强大且与 PostgreSQL 深度集成——因为我们坚信，优秀的工具应当让您的工作更轻松，而不是更复杂。欢迎您试用并向我们反馈您的想法。

%[https://github.com/tensorchord/VectorChord-BM25] 

<a id="BM25"></a>
## BM25 {#bm25}

在深入介绍这项激动人心的成果之前，让我们先快速了解一下驱动现代搜索引擎的核心算法——**BM25**。BM25 是一种概率排序函数，用于衡量文档与搜索查询之间的相关性。

BM25 公式乍看之下可能有些复杂，但让我们逐步拆解，使其易于理解。公式如下：


$$
\text{score}(Q, D) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \, (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
$$


**词频（Term Frequency, TF）**：项 \(f(q, D)\) 表示查询词 *q* 在文档 *D* 中出现的频率。一个词在文档中出现的次数越多，其相关性得分就越高。例如，如果“AI”在文档 A 中出现 5 次，在文档 B 中出现 2 次，那么文档 A 在该词上的得分更高。

**逆文档频率（Inverse Document Frequency, IDF）**：项 \(\text{IDF}(q)\) 衡量查询词 *q* 在所有文档中的罕见或常见程度。罕见词（例如“NVIDIA”）会比常见词（例如“revenue”）获得更高的权重。这确保了具有区分度的独特词汇对相关性得分产生更大的影响。

**文档长度归一化（Document Length Normalization）**：项 \(|D|\) 表示文档 *D* 的长度，而 \(\text{avgdl}\) 是整个文档集合中所有文档的平均长度。公式的这一部分会根据文档长度调整得分，确保较短的文档不会受到不公平的惩罚。例如，一篇简明扼要的报告不会被另一篇仅仅顺带提及查询词的长篇大论所掩盖。

**调优参数（Tuning Parameters）**：参数 *k*1 和 *b* 允许对公式进行微调。*k*1 控制词频对得分的影响程度，而 *b* 则平衡文档长度归一化的作用强度。可以根据特定数据集调整这些参数以优化检索效果。

设想在一个财务报告数据库中搜索“Tesla stock performance（特斯拉股票表现）”。一份提及“Tesla”十次的报告得分会高于仅提及两次的报告。然而，“stock（股票）”一词可能出现在许多报告中，因此它所获得的权重会低于更具指向性的“Tesla”。此外，一份专门探讨特斯拉股票表现的简短报告，也不会被一份只是略微提及特斯拉的冗长报告所淹没。

## Postgres 中的现有方案 {#existing-solution-in-postgres}

了解了基础知识后，让我们来看看 PostgreSQL 中现有的全文检索解决方案。

PostgreSQL 通过结合 `tsvector` 数据类型和 GIN（通用倒排索引，Generalized Inverted Index）索引，提供了内置的全文检索支持。其工作原理如下：首先将文本转换为 `tsvector`，将内容分词为词位（lexemes，即标准化的词形，有助于提高搜索效率）；随后在 `tsvector` 列上创建 GIN 索引，从而显著加快查询速度，即使面对大文本字段也能快速检索出相关文档。这种文本处理与高级索引的结合，使 PostgreSQL 成为需要高效全文检索的应用的强大且可扩展的解决方案。

```sql
-- Create a table with a text column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    content_vector tsvector
);

-- Insert sample data with tsvector conversion
INSERT INTO documents (content, content_vector) VALUES
('PostgreSQL is a powerful, open-source database system.', to_tsvector(...)),
('Full-text search in PostgreSQL is efficient and scalable.', to_tsvector(...)),
('BM25 is a ranking function used by search engines.', to_tsvector(...));

-- Create a GIN index on the tsvector column
CREATE INDEX idx_content_vector ON documents USING GIN (content_vector);

-- Query using tsvector, rank results with ts_rank, and leverage the GIN index
SELECT id, content, ts_rank(content_vector, to_tsquery('english', 'PostgreSQL & search')) AS rank
FROM documents
WHERE content_vector @@ to_tsquery('english', 'PostgreSQL & search')
ORDER BY rank DESC;
```

然而，PostgreSQL 原生方案存在一个局限：它缺乏像 BM25 这样的现代相关性评分机制。相反，它会先返回所有匹配的文档，然后再依赖 `ts_rank` 对它们进行重排序，这在数据量大时往往效率低下。这使得用户很难快速找出最重要的结果，尤其是在处理大规模数据集时。

另一种解决方案是 ParadeDB，它将全文检索查询下推给 Tantivy 以获取结果。它支持 BM25 评分以及排除词（negative terms）等复杂查询模式，旨在成为 ElasticSearch 的完全替代品。然而，它使用自己独特的语法进行过滤和查询，并将过滤操作委托给 Tantivy 而不是直接依赖 Postgres。其实现需要深入挂载 Postgres 的查询规划与存储钩子（hooks），这可能会引发潜在的兼容性问题。

相比之下，VectorChord-BM25 采取了截然不同的路径。它专注于以轻量级、原生的方式将 BM25 排序引入 PostgreSQL。我们从零实现了 BM25 排序算法和 Block WeakAnd 技术，将其构建为自定义操作符和索引（类似于 `pgvector`）来加速查询。VectorChord-BM25 的设计直观而高效，**在完全融入 PostgreSQL 生态系统的同时，提供了一套无缝的 API 来增强全文检索与排序能力**。

## VectorChord-BM25 {#vectorchord-bm25}

我们的实现引入了一种全新的方法：从零开发 BM25 索引和搜索算法，同时与 PostgreSQL 现有的扩展开发接口无缝集成，以确保最大程度的兼容性。

受 PISA 引擎、Tantivy 和 Lucene 的启发，我们引入了 BlockMax WeakAnd 算法，以支持高效的基于得分的剪枝过滤与排序。此外，我们还采用位打包（bitpacking）技术进行 ID 压缩以提升整体效率，并重新实现了基于用户数据的分词器，使其性能与行为更紧密地对齐 ElasticSearch。

下表对比了我们的实现与 ElasticSearch 在来自 [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks) 的多个数据集上的 **Top1000 每秒查询数（QPS）**（即系统在每次查询检索前 1000 条结果时每秒能处理的查询数量）：

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740189817247/5a81c020-1aa2-452d-8e8d-b9653c5b3489.png)

在测试的数据集上，我们的实现平均达到了 ElasticSearch **3 倍的 QPS**，充分展示了其高效率与可扩展性。然而，光有速度还不够——我们同样高度重视准确度。为了确保检索相关性，我们评估了衡量排序质量的核心指标——**NDCG@10（Normalized Discounted Cumulative Gain at 10，前 10 位归一化折损累计增益）**。

> [!TIP]
> **NDCG@10** 是评估排序列表前 10 个位置中文档相关性的指标。它不仅考量每篇文档自身的相关度，还兼顾其所处的排序位置，确保排名越靠前的相关文档对总得分的贡献越大。

下表对比了 VectorChord-BM25 与 ElasticSearch 在各个数据集上的 NDCG@10 得分：

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190423528/10f75122-34fc-4fa2-bb66-3e26e09516ec.png)

我们投入了大量精力使 VectorChord-BM25 的行为与 ElasticSearch 保持对齐，以确保对比的公平性与准确性。如表所示，我们的实现在大多数数据集上都取得了与 ElasticSearch 相当的 NDCG@10 得分，在部分数据集（如 trec-covid 和 scifact）上甚至超越了 ElasticSearch。

我们将在后文分享对齐工作的技术细节，包括我们如何处理分词、评分及其他关键组件以达成这些结果。在此之前，让我们先看看如何在 PostgreSQL 中使用 VectorChord-BM25。

## 快速上手 {#quick-start}

为了帮助您快速上手 VectorChord-BM25，我们在 [GitHub README](https://github.com/tensorchord/VectorChord-bm25/) 中准备了一份详尽的指南，引导您完成安装与配置过程。下面提供了一个完整的示例，展示如何在 Postgres 中使用 VectorChord-BM25 进行 BM25 全文检索。每段 SQL 代码都附有清晰的说明，解释其作用及用途。

该扩展主要由三个核心组件构成：

* **分词器（Tokenizer）**：将文本转换为 `bm25vector`（类似于存储词表 ID 及其词频的稀疏向量）。
    
* **bm25vector**：以适合计算 BM25 得分的格式表示分词后的文本。
    
* **bm25vector 索引**：加速搜索与排序过程，使其更加高效。
    

如果您想对一段文本进行分词，可以使用 `tokenize` 函数。它接收两个参数：待分词的文本以及分词器的名称。

```sql
-- tokenize text with bert tokenizer
SELECT tokenize('A quick brown fox jumps over the lazy dog.', 'Bert');
-- Output: {2474:1, 2829:1, 3899:1, 4248:1, 4419:1, 5376:1, 5831:1}
-- The output is a bm25vector, 2474:1 means the word with id 2474 appears once in the text.
```

BM25 评分的一个独特之处在于它依赖全局文档频率（global document frequency）。这意味着一个词在某篇文档中的得分，会受到该词在整个文档集合中出现频率的影响。因此，要计算 `bm25vector` 与查询之间的 BM25 得分，首先需要构建一个文档集合。准备就绪后，即可使用 `<&>` 操作符执行计算。

下面是一个分步示例。首先，创建一张表并插入一些文档：

```sql
-- Setup the document table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

INSERT INTO documents (passage) VALUES
('PostgreSQL is a powerful, open-source object-relational database system. It has over 15 years of active development.'),
('Full-text search is a technique for searching in plain-text documents or textual database fields. PostgreSQL supports this with tsvector.'),
...
('Effective search ranking algorithms, such as BM25, improve search results by understanding relevance.');
```

然后对其进行分词：

```sql
UPDATE documents SET embedding = tokenize(passage, 'Bert');
```

在 `bm25vector` 列上创建索引，以便收集全局文档频率统计信息：

```sql
CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);
```

现在我们可以计算查询与向量之间的 BM25 得分了。值得注意的是，返回的 BM25 得分是负数——这是特意设计的。得分越高（即负得越少）代表文档越相关。我们之所以故意将得分设为负数，是为了让您可以直接使用默认的 `ORDER BY`（升序）子句，轻松将最相关的文档排在最前面。

```sql
SELECT id, passage, embedding <&> to_bm25query('documents_embedding_bm25', 'PostgreSQL', 'Bert') AS rank
FROM documents
ORDER BY rank
LIMIT 10;
```

### 其他分词器 {#other-tokenizers}

除了 BERT 之外，VectorChord-BM25 还支持 `Tocken` 和 `Unicode` 分词器。`Tocken` 是一个在 `wiki-103-raw` 数据集上以最小词频（`min_freq`）为 10 预训练的 Unicode 分词器。由于它是预训练分词器，其使用方式与 BERT 类似：

```sql
SELECT tokenize('A quick brown fox jumps over the lazy dog.', 'Tocken');
```

`Unicode` 则是一个根据您的业务数据构建词表的分词器，其行为类似于 Elasticsearch 和其他全文检索引擎中的标准分词器。要启用它，您需要使用 `create_unicode_tokenizer_and_trigger(vocab_list_name, table_name, source_text_column, tokenized_vec_column)` 为您的数据专门创建一个分词器：

```sql
CREATE TABLE documents (id SERIAL, text TEXT, embedding bm25vector);
SELECT create_unicode_tokenizer_and_trigger('test_token', 'documents', 'text', 'embedding');

INSERT INTO documents (text) VALUES ('PostgreSQL is a powerful, open-source object-relational database system.');
CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);
SELECT id, text, embedding <&> to_bm25query('documents_embedding_bm25', 'PostgreSQL', 'test_token') AS rank
    FROM documents
    ORDER BY rank
    LIMIT 10;
```

如果您想了解更多相关信息，请查阅[分词器文档](/zh/docs/tokenizer/)。

## 比 ElasticSearch 更快（真的吗？） {#faster-than-elasticsearch-really}

![math Memes & GIFs - Imgflip](https://i.imgflip.com/6b4xz9.jpg)

为了确保我们的新插件不仅速度快，更能提供有意义、高相关性的检索结果，我们使用 [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks) 对 VectorChord-BM25 进行了严格的评估。我们采用了信息检索领域广泛认可的 BEIR 基准测试，重点关注两个核心指标：衡量速度的 **QPS（每秒查询数）** 与评估相关性及排序准确度的 **NDCG@10**。

在最初的版本中，我们欣喜地看到系统的 **QPS 比 ElasticSearch 高出 3 到 5 倍**。然而，我们也注意到在某些数据集上，我们的 NDCG@10 得分明显低于 ElasticSearch。经过深入分析，我们发现造成这些差距的原因并非索引实现本身，而是分词处理方式上的差异。

为了解决这一问题，我们投入了大量精力将分词流程与 ElasticSearch 对齐，以确保对比更加准确、公平。

### 问题 1：停用词表 {#issue-1-stopword-list}

> [!TIP]
> **停用词（stopword）** 是指在文本处理过程中被过滤掉的常见词，因为它们几乎不携带实质语义——例如英语中的“the”、“is”和“at”。

ElasticSearch 默认使用 Lucene 的 Standard Tokenizer，它依赖一个相对较短的停用词表。相比之下，我们的初始实现使用了 NLTK 中包含词汇多得多的停用词表。因此，ElasticSearch 的搜索会包含某些停用词，导致倒排列表更长、需要花费更多扫描时间——进而影响了查询性能。

### 问题 2：词干提取 {#issue-2-stemming}

> [!TIP]
> **词干提取器（stemmer）** 会将词语还原为其词根形式，例如“running”和“ran”都会被还原为“run”。

起初我们使用 `rust-stemmer` 库中的 **Snowball 词干提取器**来处理词形变化，但观察到了与 ElasticSearch 实现不一致的地方。经过排查，我们发现 `rust-stemmer` 中打包的 Snowball 版本已经过时。遵循官方 Snowball 仓库的指南，我们使用最新版本重新生成了词干提取代码文件。

当我们将系统的**停用词表**和**词干提取器**都与 ElasticSearch 对齐后，我们的性能优势从 **300% 缩小到了 40%**。即便如此，在 nq、fever 和 climate-fever 这三个数据集上，仍然存在明显的质量差距。更深入的对比揭示了一个微妙但关键的细节：在 bm25-benchmark 中，ElasticSearch 对数据的预处理方式与其他框架不同，这正是造成剩余差异的原因。

### 问题 3：数据预处理 {#issue-3-data-preprocessing}

在 BEIR 数据集中，每篇文档都包含 `title`（标题）和 `text`（正文）两个字段。虽然大多数框架会将这两个字段拼接成一个字符串进行索引，但 ElasticSearch 接收 JSON 输入，并对 `title` 和 `text` 分别建立索引。在查询期间，ElasticSearch 执行 `multi_match` 操作，独立搜索这两个字段并合并它们的得分（采用较高得分加上 0.5 倍较低得分的策略）。这种方法能显著提升 NDCG@10 结果，但需要搜索两个独立的索引，从而对性能产生较大影响。

为了确保公平对比，我们将 `title` 和 `text` 字段拼接后重新运行了 ElasticSearch 测试。经过这一调整，VectorChord-BM25 的检索质量与 ElasticSearch 完全持平。有趣的是，在使用拼接字段后，ElasticSearch 的 **QPS（几何平均值）** 从 **135 提升到了 341**，在 Top10 查询测试中比 VectorChord-BM25 的 **271.91 QPS** 快了 **25%**。然而，在 Top1000 测试中，VectorChord-BM25 达到了 **112 QPS**，而 ElasticSearch 为 **49 QPS**——我们的实现**快了 2.26 倍**。

这一经历凸显了在不同 BM25 全文检索实现之间进行公平性能对比的难度。**分词器**是一个极其复杂且影响深远的组件，而 ElasticSearch 错综复杂的默认设置更是为评估过程增加了另一层复杂性。

<a id="Future"></a>
## 未来规划 {#future}

目前该项目仍处于早期阶段，我们已经明确了多个可进一步优化性能的方向。分词本身是一个天然复杂的过程——即便是处理英文，我们也面临着诸多权衡与决策。我们的下一步计划是**将分词过程彻底解耦**，将其转化为一个独立且可扩展的扩展。这将使我们能够支持更多语言，允许用户自定义分词流程以获得更好的效果，甚至引入同义词处理等高级特性。

我们的最终目标是让用户能够在 PostgreSQL 上轻松执行**高质量、基于相关性的全文检索**。结合 [**VectorChord**](https://github.com/tensorchord/VectorChord/)，我们致力于为 **RAG（检索增强生成）提供一流的数据基础设施**。毕竟，选择 PostgreSQL 永远是一个稳健的决定！

如果您对 PostgreSQL 中的向量搜索或全文检索有任何疑问，欢迎随时联系我们：

* Discord：[https://discord.gg/KqswhpVgdU](https://discord.gg/KqswhpVgdU)
    
* 邮箱：[vectorchord-inquery@tensorchord.ai](mailto:vectorchord-inquery@tensorchord.ai)
    

%[https://github.com/tensorchord/VectorChord-bm25] 

## 更多基准测试 {#more-benchmarks}

除了 Top1000 基准测试外，我们还针对 Top10 结果进行了广泛评估。这些基准测试进一步展示了我们的实现在不同数据集上的性能表现。如果您有兴趣深入了解这些结果，欢迎参考下方提供的数据图表。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190947932/67305460-724d-4dc5-aa7f-606a6ceb13cb.png)

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190965658/ca72272a-49af-43f8-87b7-16d14b383e8a.png)
