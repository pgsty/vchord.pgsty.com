---
title: "在 PostgreSQL 中利用上下文检索优化 RAG"
date: 2025-05-30
description: "在 PostgreSQL 中结合向量搜索与关键词 BM25 评分实现上下文检索（Contextual Retrieval），全面提升大语言模型的生成质量。"
author: "[Keming Yang](https://github.com/kemingy) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "contextual-retrieval"
upstream_link: "https://blog.vectorchord.ai/optimize-rag-with-contextual-retrieval-in-postgresql"
upstream_copyright: "© 2025 Keming Yang (TensorChord Inc.)"
aliases:
  - "/blog/optimize-rag-with-contextual-retrieval-in-postgresql/"
  - "/optimize-rag-with-contextual-retrieval-in-postgresql/"
---

在标准的检索增强生成（RAG）方案中，一种常见做法是将长篇文档切分为更小、更易于管理的文本块（chunk）。这样做主要是为了结合句子嵌入（sentence embedding）与关键词 BM25 评分来提升检索效率，使系统能够快速定位并提取出相关的信息片段。虽然这种方法在许多场景下行之有效，但它也带来了一个显著的挑战：单个文本块很可能会丢失其原本所处的上下文语境。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1747364145166/41e0e46b-bd45-4f32-a742-9bb176253b67.png)

不妨以历史文献集合为例。如果用户询问某个特定历史事件，而检索出的文本块写着：“条约正式签署，敌对状态宣告结束。”

脱离了前后的文本，这段分块就缺失了至关重要的背景信息：签署的是*哪一份条约*、*缔约双方是谁*，以及这一重大事件发生在*何时何地*。如果仅依赖这样一个脱离上下文的片段，提供给大语言模型（LLM）的信息将是残缺甚至可能产生误导的，从而妨碍其针对该历史事件生成全面、准确的回答。

这个例子清楚地说明：虽然分块（chunking）有助于提升检索效率，但它可能会无意间剥离赋予信息片段具体含义和相关性的必要上下文。这种上下文缺失会严重影响 RAG 系统中 LLM 生成回答的质量与准确性。

为了解决这一问题，Anthropic 探索并提出了一种名为[**上下文检索（Contextual Retrieval）**](https://www.anthropic.com/news/contextual-retrieval)的方法。

简而言之，可以将它视为利用整篇文档的上下文对分块进行增强（chunk augmentation）。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1747364245704/d73b5c52-6ec5-453d-80e7-243942fbd8f4.png)

本文将带你一步步借助上下文信息来提升检索准确率。我们使用了与 Anthropic 教程中相同的[**提示词（prompt）**、数据集和评估指标](https://github.com/anthropics/anthropic-cookbook)。需要注意的是，我们在本次实验中使用了不同的嵌入模型和 LLM，因此具体数值会有所不同；但这并不反映模型本身的优劣，因为该数据集主要由代码而非自然语言构成。

我们主要使用 Gemini 模型来生成分块上下文和文本嵌入，其他模型也同样适用。嵌入质量对向量检索指标影响很大，建议参考 [MTEB 排行榜](https://huggingface.co/spaces/mteb/leaderboard)挑选最契合你业务场景的模型。在关键词分词方面，我们使用默认的 BERT 分词器，你也可以尝试[其他分词方案](/zh/docs/tokenizer/)。

重排序（rerank）并非本文的重点；如果你想深入了解重排序方法，欢迎阅读我们关于 [Cross-Encoder 重排序](/zh/blog/post/hybrid-search-with-postgres-native-bm25-and-vectorchord/)以及[词元级延迟交互重排序](/zh/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)的专题文章。顺便提一句，由于我们已经支持[多向量 MaxSim 索引](/zh/blog/release/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql/)，词元级延迟交互重排序现在可以更加高效地执行。

### 准备环境 {#prepare-the-environment}

我们在 [**VectorChord-suite**](https://github.com/tensorchord/VectorChord-images) Docker 镜像中同时提供了向量搜索和关键词搜索功能。

```bash
docker run --rm -d --name vdb -e POSTGRES_PASSWORD=postgres -p 5432:5432 ghcr.io/tensorchord/vchord-suite:pg17-20250414
```

我们将使用 [`vechord`](https://github.com/tensorchord/vechord) Python 库来减少样板代码并简化开发流程。

```bash
pip install 'vechord[gemini]'
```

### 定义 RAG 相关表结构 {#define-the-rag-related-tables}

让我们先从基础的 RAG 流程开始。

```python
from vechord.spec import (
    ForeignKey,
    Keyword,
    PrimaryKeyAutoIncrease,
    Table,
    UniqueIndex,
    Vector,
)

DenseVector = Vector[768]

class Document(Table, kw_only=True):
    uid: Optional[PrimaryKeyAutoIncrease] = None
    uuid: Annotated[str, UniqueIndex()]
    content: str

class Chunk(Table, kw_only=True):
    uid: Optional[PrimaryKeyAutoIncrease] = None
    doc_uuid: Annotated[str, ForeignKey[Document.uuid]]
    index: int
    content: str
    vector: DenseVector
    keyword: Keyword

class Query(Table, kw_only=True):
    uid: Optional[PrimaryKeyAutoIncrease] = None
    content: str
    answer: str
    doc_uuids: list[str]
    chunk_index: list[int]
    vector: DenseVector
```

上述定义已经自动包含了向量嵌入索引和关键词索引。

加载数据集的代码如下：

```python
from vechord.embedding import GeminiDenseEmbedding
from vechord.registry import VechordRegistry

emb = GeminiDenseEmbedding()
vr = VechordRegistry("anthropic", "postgresql://postgres:postgres@172.17.0.1:5432/")

vr.register([Document, Chunk, Query])

def load_data(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        docs = json.load(f)
        for doc in docs:
            vr.insert(
                Document(
                    uuid=doc["original_uuid"],
                    content=doc["content"],
                )
            )
            for chunk in doc["chunks"]:
                vr.insert(
                    Chunk(
                        doc_uuid=doc["original_uuid"],
                        index=chunk["original_index"],
                        content=chunk["content"],
                        vector=emb.vectorize_chunk(chunk["content"]),
                        keyword=Keyword(chunk["content"]),
                    )
                )

def load_query(filepath: str):
    queries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            query = json.loads(line)
            queries.append(
                Query(
                    content=query["query"],
                    answer=query["answer"],
                    doc_uuids=[x[0] for x in query["golden_chunk_uuids"]],
                    chunk_index=[x[1] for x in query["golden_chunk_uuids"]],
                    vector=emb.vectorize_query(query["query"]),
                )
            )
    vr.copy_bulk(queries)
```

<a id="Evaluation"></a>
### 评估 {#evaluation}

现在我们已经具备了基础 RAG 流程所需的全部组件。接下来定义评估指标 `Pass@k`，它表示检索出的 Top-K 文本块中包含了多少比例的标准答案（ground truth）文本块。

```python
def evaluate(topk=5, search_func=vector_search):
    print(f"TopK={topk}, search by: {search_func.__name__}")
    queries: list[Query] = vr.select_by(Query.partial_init())
    total_score = 0
    start = perf_counter()
    for query in queries:
        chunks: list[Chunk] = search_func(query, topk)
        count = 0
        for doc_uuid, chunk_index in zip(
            query.doc_uuids, query.chunk_index, strict=True
        ):
            for chunk in chunks:
                if chunk.doc_uuid == doc_uuid and chunk.index == chunk_index:
                    count += 1
                    break
        score = count / len(query.doc_uuids)
        total_score += score

    print(
        f"Pass@{topk}: {total_score / len(queries):.4f}, total queries: {len(queries)}, QPS: {len(queries) / (perf_counter() - start):.3f}"
    )
```

我们可以尝试不同的检索策略，例如向量搜索、关键词搜索、结合融合（fusion）或重排序（rerank）的混合搜索。

这些检索策略可定义如下：

```python
from vechord.rerank import CohereReranker, ReciprocalRankFusion

def vector_search(query: Query, topk: int) -> list[Chunk]:
    return vr.search_by_vector(Chunk, query.vector, topk=topk)

def keyword_search(query: Query, topk: int) -> list[Chunk]:
    return vr.search_by_keyword(Chunk, query.content, topk=topk)

def hybrid_search_fuse(query: Query, topk: int) -> list[Chunk]:
    rrf = ReciprocalRankFusion()
    return rrf.fuse([vector_search(query, topk), keyword_search(query, topk)])[:topk]

def hybrid_search_rerank(query: Query, topk: int, boost=3) -> list[Chunk]:
    ranker = CohereReranker()
    vecs = vector_search(query, topk * boost)
    keys = keyword_search(query, topk * boost)
    chunks = list({chunk.uid: chunk for chunk in vecs + keys}.values())
    indices = ranker.rerank(query.content, [chunk.content for chunk in chunks])
    return [chunks[i] for i in indices[:topk]]
```

### 上下文检索（Contextual Retrieval） {#contextual-retrieval}

LLM 使用如下提示词生成上下文信息：

```python
prompt = (
    "<document>\n{whole_document}\n</document>"
    "Here is the chunk we want to situate within the whole document \n"
    "<chunk>\n{chunk}\n</chunk>\n"
    "Please give a short succinct context to situate this chunk within "
    "the overall document for the purposes of improving search retrieval "
    "of the chunk. Answer only with the succinct context and nothing else."
)
```

上面的提示词是专为通用检索任务设计的。针对你的具体业务场景，定制更专门的提示词往往能取得更好的效果。

这一功能已经内置在 `vechord` 库中。

`GeminiAugmenter` 同样支持类似 `Claude` 的提示词缓存（prompt caching）功能，但它要求缓存内容至少达到 32768 个 token，而本实验所用的数据集未达到该长度阈值。

```python
from vechord.augment import GeminiAugmenter

class ContextualChunk(Table, kw_only=True):
    uid: Optional[PrimaryKeyAutoIncrease] = None
    doc_uuid: Annotated[str, ForeignKey[Document.uuid]]
    index: int
    content: str
    context: str
    vector: DenseVector
    keyword: Keyword

def load_contextual_chunks(filepath: str):
    augmenter = GeminiAugmenter()

    with open(filepath, "r", encoding="utf-8") as f:
        docs = json.load(f)
        for doc in docs:
            augmenter.reset(doc["content"])
            chunks = doc["chunks"]
            augments = augmenter.augment_context([chunk["content"] for chunk in chunks])
            if len(augments) != len(chunks):
                print(f"augments length not match for uuid: {doc['original_uuid']}, {len(augments)} != {len(chunks)}")
            for chunk, context in zip(chunks, augments, strict=False):
                contextual_content = f"{chunk['content']}\n\n{context}"
                vr.insert(
                    ContextualChunk(
                        doc_uuid=doc["original_uuid"],
                        index=chunk["original_index"],
                        content=chunk["content"],
                        context=context,
                        vector=emb.vectorize_chunk(contextual_content),
                        keyword=Keyword(contextual_content),
                    )
                )
```

随后，我们可以将检索策略扩展为如下形式：

```python
def vector_contextual_search(query: Query, topk: int) -> list[ContextualChunk]:
    return vr.search_by_vector(ContextualChunk, query.vector, topk=topk)

def keyword_contextual_search(query: Query, topk: int) -> list[ContextualChunk]:
    return vr.search_by_keyword(ContextualChunk, query.content, topk=topk)

def hybrid_contextual_search_fuse(query: Query, topk: int) -> list[ContextualChunk]:
    rrf = ReciprocalRankFusion()
    return rrf.fuse(
        [vector_contextual_search(query, topk), keyword_contextual_search(query, topk)]
    )[:topk]

def hybrid_contextual_search_rerank(
    query: Query, topk: int, boost=3
) -> list[ContextualChunk]:
    ranker = CohereReranker()
    vecs = vector_contextual_search(query, topk * boost)
    keys = keyword_contextual_search(query, topk * boost)
    chunks = list({chunk.uid: chunk for chunk in vecs + keys}.values())
    indices = ranker.rerank(
        query.content, [f"{chunk.content}\n{chunk.context}" for chunk in chunks]
    )
    return [chunks[i] for i in indices[:topk]]
```

<a id="Benchmark"></a>
### 基准测试结果 {#benchmark}

* `topk=5`
    

|  | Pass\_at\_5 | QPS |
| --- | --- | --- |
| 向量搜索（vector search） | 0.8071 | 289.024 |
| 关键词搜索（keyword search） | 0.7003 | 337.211 |
| 上下文向量搜索（vector contextual search） | 0.8404 | 307.253 |
| 上下文关键词搜索（keyword contextual search） | 0.8033 | 331.239 |

* `topk=10`
    

|  | Pass\_at\_10 | QPS |
| --- | --- | --- |
| 向量搜索（vector search） | 0.8574 | 254.730 |
| 关键词搜索（keyword search） | 0.7577 | 219.653 |
| 上下文向量搜索（vector contextual search） | 0.8807 | 247.819 |
| 上下文关键词搜索（keyword contextual search） | 0.8563 | 216.560 |

所有代码均可在我们的 [`vechord`](https://github.com/tensorchord/vechord/pull/30) 仓库中找到。
