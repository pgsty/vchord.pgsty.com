---
title: "推出 Vechord：以 Pythonic 的方式将 PostgreSQL 打造成你的搜索引擎"
date: 2025-04-23
description: "借助支持无缝向量与关键词搜索的 Python 库 Vechord，将 PostgreSQL 打造成强大的搜索引擎"
author: "Keming"
tags:
  - "vectorsearch"
upstream_link: "https://blog.vectorchord.ai/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way"
aliases:
  - "/blog/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way/"
  - "/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way/"
---

今天，我们非常激动地宣布发布 [**Vechord**](https://github.com/tensorchord/vechord)——一个全新的 Python 库，旨在大幅简化直接在 PostgreSQL 数据库之上构建稳健搜索基础设施的流程。

在人工智能与大语言模型（LLM）飞速发展的今天，检索增强生成（RAG）和语义搜索已成为不可或缺的核心组件。然而，搭建所需的向量搜索基础设施往往意味着学习全新的数据库技术、管理复杂的系统集成，或是与繁琐的框架搏斗。这不仅增加了研发摩擦，还会拖慢开发进度，对于已经熟悉 PostgreSQL 的团队而言尤为如此。

## **挑战：混合搜索的复杂性** {#the-challenge-hybrid-search-complexity}

构建搜索能力通常意味着：

1. **选型与运维专用数据库**：评估、部署和维护专用的向量数据库（如 Pinecone、Weaviate、Milvus 等）以及全文检索框架（如 ElasticSearch、Solr 等）会带来额外的运维开销。
    
2. **复杂的数据处理**：需要管理源数据与向量表征之间的同步。
    
3. **陡峭的学习曲线**：需要理解那些面向广泛 LLM 任务的庞大框架中的各种 API 与抽象概念。
    

## **Vechord：构建于 PostgreSQL 之上的简洁、Pythonic 解决方案** {#vechord-the-simple-pythonic-solution-built-on-top-of-postgresql}

Vechord 通过充分发挥 PostgreSQL 的强大能力与可扩展性，并结合强大的 [**VectorChord**](https://github.com/tensorchord/VectorChord/) 和 [**VectorChord-bm25**](https://github.com/tensorchord/VectorChord-bm25) 扩展，正面解决了这些挑战。我们的核心设计理念是**简洁与专注**。

Vechord 提供了一套干净、Pythonic 的接口，助你轻松完成：

* **初始化（Initialize）**：使用 Python 结构体和类型注解轻松配置表结构（Schema）。
    
* **数据写入（Ingest Data）**：配合转换工具，轻松导入文档、PDF 或任何其他类型的数据。
    
* **执行混合搜索（Perform Hybrid Search）**：通过友好的 API 高效执行向量相似度搜索与关键词搜索，并对检索结果进行重排序（rerank）。
    
* **指标评估（Evaluate Metrics）**：无论是对比标准答案（ground truth）还是使用基于 LLM 的评分，都能无缝评估检索指标。
    
* **化繁为简（Makes Simple Tasks Simple）**：提供类 ORM 的接口，方便地对 PostgreSQL 数据库执行查询、插入和删除操作。
    

## **Vechord 有何不同？** {#how-is-vechord-different}

1. **高度专注于 PostgreSQL 向量 + 关键词搜索**：Vechord *专门*致力于让 PostgreSQL + VectorChord 套件的组合在搜索场景下简单易用。如果你的首要目标是在现有的 PostgreSQL 生态中实现高效的向量搜索与关键词搜索，Vechord 提供了一条更精简、更直接的路径。
    
2. **定位为库，而非庞大平台**：Vechord 被设计为一个*库（Library）*——一个可以集成到你应用代码中的专注构建块。它为你提供基于 PostgreSQL 的核心存储与混合搜索能力，而将更宏观的应用架构与工作流设计完全交还给你。
    
3. **复用现有基础设施**：Vechord 的核心前提是赋能已经在使用 PostgreSQL 的团队。如果你的数据规模和业务需求能够通过 VectorChord 套件得到良好满足，就无需再引入和维护一套独立的专用向量数据库或文档数据库，从而大幅降低运维复杂度和成本。
    
4. **把简洁当作核心特性**：Vechord 优先追求极简的 API 表面积以及特定任务下的易用性，旨在让你以最少的样板代码和心智负担在 Postgres 上实现混合搜索。
    

## 快速上手 Vechord {#get-started-with-vechord}

* 定义表结构（Schema）
    

```python
from typing import Annotated, Optional
from vechord.spec import Table, Vector, PrimaryKeyAutoIncrease, ForeignKey, Keyword

# use 768 dimension vector
DenseVector = Vector[768]

class Document(Table, kw_only=True):
    uid: Optional[PrimaryKeyAutoIncrease] = None  # auto-increase id, no need to set
    link: str = ""
    text: str

class Chunk(Table, kw_only=True)
    uid: Optional[PrimaryKeyAutoIncrease] = None
    doc_id: Annotated[int, ForeignKey[Document.uid]]  # reference to `Document.uid` on DELETE CASCADE
    vec: DenseVector  # this comes with a default vector index
    keyword: Keyword  # this comes with a default tokenizer and text index
    text: str
```

* 使用 Python 装饰器注入数据
    

```python
import httpx
from vechord.registry import VechordRegistry
from vechord.extract import SimpleExtractor
from vechord.embedding import GeminiDenseEmbedding

vr = VechordRegistry(namespace="test", url="postgresql://postgres:postgres@127.0.0.1:5432/")
# ensure the table and index are created if not exists
vr.register([Document, Chunk])
extractor = SimpleExtractor()
emb = GeminiDenseEmbedding()

@vr.inject(output=Document)  # dump to the `Document` table
# function parameters are free to define since `inject(input=...)` is not set
def add_document(url: str) -> Document:  # the return type is `Document`
    with httpx.Client() as client:
        resp = client.get(url)
        text = extractor.extract_html(resp.text)
        return Document(link=url, text=text)

@vr.inject(input=Document, output=Chunk)  # load from the `Document` table and dump to the `Chunk` table
# function parameters are the attributes of the `Document` table, only defined attributes
# will be loaded from the `Document` table
def add_chunk(uid: int, text: str) -> list[Chunk]:  # the return type is `list[Chunk]`
    chunks = text.split("\n")
    return [Chunk(doc_id=uid, vec=emb.vectorize_chunk(t), keyword=Keyword(t), text=t) for t in chunks]

if __name__ == "__main__":
    add_document("https://paulgraham.com/best.html")  # add arguments as usual
    add_chunk()  # omit the arguments since the `input` is will be loaded from the `Document` table
    vr.insert(Document(text="hello world"))  # insert manually
    print(vr.select_by(Document.partial_init()))  # select all the columns from table `Document`
```

* 在单个事务中运行多个步骤以保证数据一致性
    

```python
pipeline = vr.create_pipeline([add_document, add_chunk])
pipeline.run("https://paulgraham.com/best.html")  # only accept the arguments for the first function
```

* 按向量和关键词进行检索，并使用交叉编码器（Cross-Encoder）模型重排序
    

```python
from vechord.rerank import CohereReranker

reranker = CohereReranker()
text = vr.search_by_vector(Chunk, emb.vectorize_query("startup"))
vec = vr.search_by_keyword(Chunk, "startup")
chunks = list({chunk.uid: chunk for chunk in text_retrieves + vec_retrievse}.values())
indices = reranker.rerank(query, [chunk.text for chunk in chunks])
print([chunks[i] for i in indices[:topk]])
```

## **加入社区！** {#join-the-community}

Vechord 是开源且由社区驱动的项目。我们相信它为那些希望获得强大搜索能力、却不想引入不必要复杂度的开发者填补了一个关键空白。

* **在 GitHub 上查看源码**：[https://github.com/tensorchord/vechord](https://github.com/tensorchord/vechord)
    
* **阅读文档**：[https://tensorchord.github.io/vechord/](https://tensorchord.github.io/vechord/)
    
* **在 Discord 上与我们交流**：[https://discord.gg/KqswhpVgdU](https://discord.gg/KqswhpVgdU)
    

%[https://github.com/tensorchord/vechord]
