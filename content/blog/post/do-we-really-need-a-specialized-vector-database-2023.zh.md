---
title: "我们真的需要专门的向量数据库吗？(2023)"
date: 2025-02-18
description: "注：本文最初发表于 2023 年，探讨了专用向量数据库的适用性与必要性，特别是与 Postgres 及其向量能力之间的对比。"
author: "Ce Gao"
tags:
  - "postgresql"
upstream_link: "https://blog.vectorchord.ai/do-we-really-need-a-specialized-vector-database-2023"
aliases:
  - "/blog/do-we-really-need-a-specialized-vector-database-2023/"
  - "/do-we-really-need-a-specialized-vector-database-2023/"
---

> 注：本文最初发表于 2023 年，探讨了专用向量数据库的适用性与必要性，特别是它与 Postgres 及其能力之间的关系。如需了解关于此话题的更多见解与讨论，请参阅以下链接：[Do we really need a specialized vector database? | Hacker News](https://news.ycombinator.com/item?id=37097004)。

随着大语言模型（LLM）的普及，向量数据库也成为了热门话题。只需寥寥几行简单的 Python 代码，向量数据库就能充当 LLM 廉价却高效的“外挂大脑”。但我们真的需要一个专门的向量数据库吗？

## 为什么 LLM 需要向量搜索？ {#why-does-llm-need-vector-search}

首先，让我简要介绍一下为什么 LLM 需要使用向量搜索技术。向量搜索是一个存在已久的问题：给定一个对象，在集合中找出与之最相似对象的过程就是向量搜索。文本、图像等都可以转换为向量表示，从而将文本或图像的相似性问题转化为向量相似性问题。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739843109618/85ebdec4-8579-4739-a1d6-8f51f9dfb19b.png)

在上面的例子中，我们将不同的单词转换为三维向量，因此可以在三维空间中直观地展示不同单词之间的相似度。例如，“student（学生）”与“school（学校）”之间的相似度要高于“student（学生）”与“food（食物）”之间的相似度。

回到 LLM，上下文窗口长度的限制是一个主要挑战。例如，ChatGPT 3.5 的上下文长度限制为 4k 词元（tokens）。这给 LLM 的上下文学习能力带来了显著阻碍，并对用户体验产生负面影响。然而，向量搜索为这个问题提供了一个优雅的解决方案：

* 将超出上下文长度限制的长文本切分为较短的片段（chunks），并将不同的片段转换为向量（embeddings）。
    
* 在将提示词（prompt）输入给 LLM 之前，先将提示词转换为向量（embedding）。
    
* 使用提示词向量进行搜索，找出最相似的文本片段向量。
    
* 将最相似的文本片段与提示词拼接在一起，作为给 LLM 的最终输入。
    

这就像给 LLM 配备了一个外部记忆库，允许它从记忆库中搜索最相关的信息。这种记忆能力正是向量搜索所赋予的。如果你想了解更多细节，可以阅读这两篇文章（[文章 1](https://simplicityissota.substack.com/p/what-is-an-embedding-anyways) 和 [文章 2](https://betterprogramming.pub/enhancing-chatgpt-with-infinite-external-memory-using-vector-database-and-chatgpt-retrieval-plugin-b6f4ea16ab8)），它们解释得更加透彻。

## 为什么向量数据库如此受欢迎？ {#why-is-vector-database-so-popular}

在 LLM 应用中，向量数据库已成为不可或缺的一部分，其中最重要的原因之一就是它的易用性。配合 OpenAI Embedding 模型（如 `text-embedding-ada-002`）使用时，只需大约十行代码，就能将用户的查询提示词转换为向量并完成整个向量搜索流程。

```python
def query(query, collection_name, top_k=20):

    # Creates embedding vector from user query
    embedded_query = openai.Embedding.create(
        input=query,
        model=EMBEDDING_MODEL,
    )["data"][0]['embedding']
    
    near_vector = {"vector": embedded_query}

    # Queries input schema with vectorized user query
    query_result = (
        client.query
        .get(collection_name)
        .with_near_vector(near_vector)
        .with_limit(top_k)
        .do()
    )
    
    return query_result
```

在 LLM 中，向量搜索主要扮演“召回（Recall）”的角色。简单来说，召回就是在候选集中找出最相似的对象。在 LLM 场景下，候选集是所有的文本片段，而最相似的对象就是与提示词最相关的文本片段。在 LLM 的推理过程中，向量搜索被视为实现召回的主要手段。它易于实现，并且可以利用 OpenAI Embedding 模型解决最繁琐的“文本转向量”问题；剩下的就是一个独立、纯粹的向量搜索问题，现有的向量数据库可以很好地完成，因此整个流程显得格外顺畅。

顾名思义，向量数据库是专为“向量”这种特殊数据类型设计的数据库。向量的相似度计算原本是一个复杂度为 `O(n^2)` 的问题，因为它需要将集合中的所有向量两两比较。为此，业界提出了近似最近邻（ANN）算法。通过使用 ANN 算法，向量数据库采用“空间换时间”的思想预先计算并构建向量索引，从而大幅加速相似度计算过程。这与传统数据库中的索引非常相似。

因此，向量数据库不仅性能强大，而且极易上手，看起来与 LLM 简直是天作之合！（真的如此吗？）

## 也许通用数据库会是更好的选择？ {#perhaps-a-general-purpose-database-would-be-better}

我们已经聊过了向量数据库的优势与好处，但它的局限性又是什么呢？[SingleStore 的一篇博客文章](https://www.singlestore.com/blog/why-your-vector-database-should-not-be-a-vector-database/)很好地回答了这个问题：

> 向量和向量搜索只是一种数据类型和查询处理方法，而不是一种全新的数据处理范式的根基。使用专用向量数据库（SVDB）会导致我们在使用多套专用系统的客户身上一次又一次看到（并解决）的老问题：数据冗余、过度的数据迁移、分布式组件之间的数据值不一致、专门技能带来的额外人力成本、额外的软件许可费用、有限的查询语言能力与可编程/可扩展性、有限的工具集成，以及相比真正的 DBMS 而言堪忧的数据完整性与高可用性。

我认为其中有两个问题尤为重要。第一个是**数据一致性**问题。在原型验证阶段，向量数据库非常合适，易用性高于一切。然而，向量数据库是一个独立的系统，与 OLTP 数据库、OLAP 数据湖等其他数据存储系统完全解耦。因此，数据必须在多个系统之间进行同步、流转和处理。

试想一下，如果你的业务数据已经存储在 PostgreSQL 这样的 OLTP 数据库中。为了使用独立的向量数据库执行向量搜索，你需要先从数据库中提取数据，然后调用 OpenAI Embedding 等服务将每条数据转换为向量，最后再将其同步到专用的向量数据库中。这增加了大量的系统复杂度。更严重的是，如果用户在 PostgreSQL 中删除了一条数据，但向量数据库中的对应向量未被删除，就会引发数据不一致问题。在真实的生产环境中，这类问题可能会造成非常严重的后果。

```sql
-- Update the embedding column for the documents table
UPDATE documents SET embedding = openai_embedding(content) WHERE length(embedding) = 0;

-- Create an index on the embedding column
CREATE INDEX ON documents USING ivfflat (embedding vector_l2_ops) WITH (lists = 100);

-- Query the similar embeddings
SELECT * FROM documents ORDER BY embedding <-> openai_embedding('hello world') LIMIT 5;
```

相反，如果所有操作都在通用数据库中完成，用户体验可能会比使用独立向量数据库更加简单。在通用数据库中，向量只是一种普通的数据类型，而不是一个独立的系统。这样一来，数据一致性就不再是问题了。

第二个问题是**查询语言**。向量数据库的查询语言通常是专门针对向量搜索设计的，因此在其他类型的查询上可能存在诸多限制。例如，在元数据过滤（Metadata Filtering）场景下，用户需要根据某些元数据字段进行过滤，而部分向量数据库支持的过滤操作符非常有限。

此外，它们支持的元数据类型通常也很受限，往往只包括字符串（String）、数值（Number）、字符串列表（List of Strings）和布尔值（Booleans）。这对于复杂的元数据查询非常不友好。

如果传统数据库能够支持向量数据类型，那么上述问题就迎刃而解了。首先，作为生产环境中已有的基础设施，TP 或 AP 数据库天然保障了数据一致性；其次，查询语言的问题也不复存在，因为向量数据类型只是数据库中的一种数据类型，针对向量数据的查询可以直接使用数据库的原生查询语言（如 SQL）。

## 深入剖析 {#detailed-explanation}

当然，只挑向量数据库的缺点是不公平的。支持专用向量数据库通常有以下几个主要论点：

* **易用性**：向量数据库在设计之初就充分考虑了易用性，用户可以轻松上手而无需关心底层实现细节。不过，正如前文所述，将它们与其他数据存储系统集成仍然是一个挑战。
    
* **性能**：在某些特定场景下，向量数据库相比传统数据库具有显著的性能优势。它们专为向量搜索而设计，能够在大规模高维向量数据集上实现快速、高效的相似度检索。
    
* **元数据过滤**：虽然向量数据库的元数据过滤能力有所限制，但仍能满足大多数常规业务场景的需求。不过，对于更复杂的元数据查询，可能需要采用混合方案，即将元数据存储在独立的数据库或数据湖中，并与向量数据库中的向量数据进行关联。
    

该如何看待并应对这些问题呢？在接下来的章节中，我将通过逐一回答这些问题来分享我的观点。

### 向量数据库确实易于使用 {#vector-databases-are-easy-to-use}

虽然向量数据库确实很容易上手，但这并非它们的专利。向量数据库的易用性主要源于其对特定领域的抽象，使其能够针对机器学习领域最常用的编程语言 Python 进行专门设计，并针对向量搜索场景进行优化。然而，如果传统数据库也支持向量数据类型，它们完全可以提供同等的易用性。

此外，传统数据库既可以提供 Python SDK 和其他集成工具来满足大多数场景的需求，也可以提供标准的 SQL 接口来处理更复杂的查询场景。因此，完全没有必要仅仅为了易用性而专门引入一个向量数据库。

向量数据库的另一个优势是其分布式设计，允许水平扩展以满足用户的数据量和 QPS 需求。但传统数据库同样可以通过分布式架构来满足这些需求。无论如何，是否采用分布式系统应当基于数据量和 QPS 的实际需求以及相关成本来决定。

总而言之，虽然向量数据库有其优势，但如果传统数据库支持向量数据类型，同样可以提供类似的易用性和分布式扩展能力。因此，在向量数据库与传统数据库之间做选择，应当基于应用程序的具体需求和现有资源状况。

### 向量数据库的性能更好吗？ {#vector-databases-have-better-performance}

为了探究向量数据库在 LLM 场景下的性能表现，有人进行了一项向量检索的[基础基准测试](https://www.ethanrosenthal.com/2023/04/10/nn-vs-ann/)。该基准测试包含 N 个随机初始化的 256 维向量，并测量了在不同规模 N 下查询 Top-5 最近邻所需的时间。测试采用了两种不同的方法：

* 使用 Numpy 进行**实时（real-time）**计算，执行完全精确、非预计算的最近邻计算。
    
* 使用 Hnswlib **预计算近似（approximate）**最近邻。
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739843146447/a63df75e-ff79-4038-9eed-20c32769c9a0.png)

基准测试结果显示，在 100 万向量的规模下，使用 Numpy 进行实时精确计算的延迟约为 50 毫秒。以此为基准，我们可以对比完成向量搜索之后 LLM 推理所花费的时间。例如，一个 7B 模型在 Nvidia A100（40GB）上推理生成 300 个汉字大约需要 10 秒。因此，即使算上使用 Numpy 对 100 万向量进行实时精确相似度计算的查询时间，它也仅占端到端 LLM 推理总延迟的 0.5%。由此可见，在当前的 LLM 场景中，单就延迟而言，向量数据库带来的收益很可能会被 LLM 自身的推理延迟所掩盖。那么我们还需要考虑吞吐量（Throughput）——而 LLM 的吞吐量远低于向量数据库，因此我认为吞吐量也不是该场景下的核心瓶颈。

如果极致性能并非首要矛盾，那么决定用户选择的因素会是什么？我认为是整体的易用性——包括开发使用和日常运维的便捷性、数据一致性，以及对各类数据库共性问题的成熟解决方案。传统数据库在这些方面拥有久经考验的成熟方案，而专用向量数据库仍处于发展的早期阶段。

### 元数据过滤能满足大多数业务场景吗？ {#metadata-filtering-can-still-meet-the-needs-of-most-business-scenarios}

在考虑元数据过滤时，需要注意的不仅是支持多少种操作符，数据一致性同样是一个关键因素。向量的元数据本质上就是传统数据库中的业务数据，而向量本身则是这些数据的索引表示。因此，将向量和元数据一同存储在传统数据库中是非常合理的思路。

传统数据库完全有能力支持向量数据类型，并提供与向量数据库相当的易用性和分布式能力。更重要的是，传统数据库拥有成熟的机制来保障数据一致性与完整性，例如事务管理以及数据备份与恢复。

## 传统数据库中的向量支持 {#vectors-in-traditional-databases}

既然我们将向量视为传统数据库中的一种新数据类型，那么不妨以 PostgreSQL 为例，看看如何在传统数据库中支持向量数据类型。[pgvector](https://github.com/pgvector/pgvector) 是一个支持向量数据类型的开源 PostgreSQL 插件。pgvector 默认使用精确计算，但也支持构建 IVFFlat 索引并使用 IVFFlat 算法预计算 ANN 结果，通过牺牲一定的计算精度来换取性能。

pgvector 在支持向量方面做得非常出色，并已被 [supabase](https://supabase.com/blog/openai-embeddings-postgres-vector) 等产品采用。然而，它当时支持的索引算法较为有限，仅支持最简单的 IVFFlat 算法，且未实现量化或存储优化。此外，pgvector 的索引算法对磁盘不够友好，主要是为内存使用场景设计的。因此，专为磁盘设计的向量索引算法（如 [DiskANN](https://proceedings.neurips.cc/paper_files/paper/2019/file/09853c7fb1d3f8ee67a61b6bf4a7f8e6-Paper.pdf)）在传统数据库生态中同样具有极高的价值。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739843174298/4f931dca-df4f-46f0-9a88-e6e824aa0939.jpeg)

由于 pgvector 是用 C 语言实现的，对其进行功能扩展颇具挑战。尽管已经开源两年，pgvector 当时仅有三位贡献者。虽然 pgvector 的实现并不算特别复杂，但使用 Rust 重写它无疑是一个值得考虑的方向。

使用 Rust 重写可以让代码组织更加现代化、更具可扩展性。Rust 的生态系统也非常丰富，已有诸如 [faiss-rs](https://github.com/Enet4/faiss-rs) 这样的现成绑定库。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739843199895/f6d1d545-b827-4369-9c79-fbe9cce4f4b3.png)

正因如此，[pgvecto.rs](/zh/docs/vectors/) 应运而生。[pgvecto.rs](/zh/docs/vectors/) 支持精确向量查询操作和三种距离计算操作符，并且围绕索引支持开展了大量设计与实现工作。除了 IVFFlat 之外，我们还希望支持更多索引算法，如 DiskANN、SPTAG 和 ScaNN。我们非常欢迎来自社区的贡献与反馈！

[pgvecto.rs](/zh/docs/vectors/) 提供了现代化且可扩展的代码库，具备更优的性能和并发能力。其设计与实现允许与其他机器学习库和工具无缝集成，使其成为相似度搜索场景的理想选择。

随着持续的开发演进，[pgvecto.rs](/zh/docs/vectors/) 旨在成为数据科学家和机器学习从业者的得力工具。它对多种索引算法的支持以及出色的易用性，使其成为大规模相似度搜索应用的有力候选方案。我们期待与社区携手持续推进开发与贡献。

```sql
-- call the distance function through operators

-- square Euclidean distance
SELECT array[1, 2, 3] <-> array[3, 2, 1];
-- dot product distance
SELECT array[1, 2, 3] <#> array[3, 2, 1];
-- cosine distance
SELECT array[1, 2, 3] <=> array[3, 2, 1];

-- create table
CREATE TABLE items (id bigserial PRIMARY KEY, emb numeric[]);
-- insert values
INSERT INTO items (emb) VALUES (ARRAY[1,2,3]), (ARRAY[4,5,6]);
-- query the similar embeddings
SELECT * FROM items ORDER BY emb <-> ARRAY[3,2,1] LIMIT 5;
-- query the neighbors within a certain distance
SELECT * FROM items WHERE emb <-> ARRAY[3,2,1] < 5;
```

<a id="Future"></a>
## 未来展望 {#future}

随着大语言模型（LLM）逐步走向生产环境，底层基础设施的要求变得越来越高。向量数据库的出现是对基础设施的重要补充。我们并不认为向量数据库会取代传统数据库，而是相信它们会在不同的场景中各自发挥所长。同时，向量数据库的兴起也将推动传统数据库更好地支持向量数据类型。

我们希望 [pgvecto.rs](/zh/docs/vectors/) 能够成为 Postgres 生态系统的重要组成部分，为 Postgres 提供更强大的向量支持。它基于 Rust 的实现以及对多种索引算法的支持，使其在大规模相似度搜索应用中充满潜力。我们相信，通过持续研发与社区贡献，它将成为数据科学家与机器学习从业者手中极具价值的工具。
