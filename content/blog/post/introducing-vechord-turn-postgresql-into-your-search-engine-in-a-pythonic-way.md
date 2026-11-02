---
title: "Introducing Vechord: Turn PostgreSQL into your search engine in a Pythonic way."
date: 2025-04-23
description: "Turn PostgreSQL into a powerful search engine with Vechord, a Python library for seamless vector and keyword search"
author: "[Keming Yang](https://github.com/kemingy) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorsearch"
upstream_link: "https://blog.vectorchord.ai/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way"
upstream_copyright: "© 2025 Keming Yang (TensorChord Inc.)"
aliases:
  - "/blog/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way/"
  - "/introducing-vechord-turn-postgresql-into-your-search-engine-in-a-pythonic-way/"
---

Today, we're thrilled to announce the release of [**Vechord**](https://github.com/tensorchord/vechord), a new Python library designed to dramatically simplify building robust search infrastructure directly on top of the PostgreSQL database.

In the rapidly evolving world of AI and large language models (LLMs), Retrieval-Augmented Generation (RAG) and semantic search have become crucial components. However, setting up the necessary vector search infrastructure often involves learning new database technologies, managing complex integrations, or wrestling with intricate frameworks. This adds friction and slows down development, especially for teams already comfortable with PostgreSQL.

## **The Challenge: Hybrid Search Complexity**

Building search capabilities often means:

1. **Choosing & Managing a Vector Database:** Evaluating, deploying, and maintaining specialized vector databases (Pinecone, Weaviate, Milvus, etc.) and text search frameworks (ElasticSearch, Solr, etc.) adds operational overhead.
    
2. **Complex Data Handling:** Managing the synchronization between the source data and the vector representations.
    
3. **Steep Learning Curves:** Understanding the APIs and abstractions of comprehensive frameworks for a wide range of LLM tasks.
    

## **Vechord: The Simple, Pythonic Solution Built on Top of PostgreSQL**

Vechord tackles these challenges head-on by leveraging the power and extensibility of PostgreSQL, enhanced with the powerful [**VectorChord**](https://github.com/tensorchord/VectorChord/) and [**VectorChord-bm25**](https://github.com/tensorchord/VectorChord-bm25) extensions. Our core philosophy is **simplicity and focus**.

Vechord provides a clean, Pythonic interface to:

* **Initialize:** Easily configure the table schema with Python struct and annotations.
    
* **Ingest Data:** Effortlessly add documents, PDFs, or any other type of data with transformation tools.
    
* **Perform Hybrid Search:** Efficiently execute the vector similarity search and keyword search, and rerank the retrieval results with the user-friendly API.
    
* **Evaluate Metrics**: Evaluate metrics seamlessly, either against ground truth or with LLM-based scoring.
    
* **Makes Simple Tasks Simple**: offer an ORM-like interface to select, insert, and delete records from the PostgreSQL database.
    

## **How is Vechord Different?**

1. **Laser Focus on PostgreSQL Vector + Keyword Search:** Vechord concentrates *specifically* on making the PostgreSQL + VectorChord-suite combination easy to use for search. If your primary goal is streamlined vector search and keyword search within your existing PostgreSQL ecosystem, Vechord offers a leaner, more direct path.
    
2. **Library, Not a Full Platform:** Vechord is designed as a *library* – a focused building block that you can integrate into your application code. It gives you the core storage and hybrid search capability on PostgreSQL, leaving the broader application architecture and workflow design entirely up to you.
    
3. **Leveraging Existing Infrastructure:** The core premise of Vechord is to empower teams already using PostgreSQL. You don't need to introduce and manage a separate, dedicated vector database or document database if your scale and requirements are well-served by the VectorChord suite. This reduces operational complexity and cost.
    
4. **Simplicity as a Feature:** Vechord prioritizes a minimal API surface and ease of use for its specific task. Vechord aims to get you performing hybrid search on Postgres with minimal boilerplate and cognitive load.
    

## Get Started with Vechord

* Define the table schema
    

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

* Inject the data with a Python decorator
    

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

* Run several steps in a transaction to guarantee data consistency
    

```python
pipeline = vr.create_pipeline([add_document, add_chunk])
pipeline.run("https://paulgraham.com/best.html")  # only accept the arguments for the first function
```

* Search by the vector and keyword, rerank with the cross-encoder model
    

```python
from vechord.rerank import CohereReranker

reranker = CohereReranker()
text = vr.search_by_vector(Chunk, emb.vectorize_query("startup"))
vec = vr.search_by_keyword(Chunk, "startup")
chunks = list({chunk.uid: chunk for chunk in text_retrieves + vec_retrievse}.values())
indices = reranker.rerank(query, [chunk.text for chunk in chunks])
print([chunks[i] for i in indices[:topk]])
```

## **Join the Community!**

Vechord is open-source and community-driven. We believe it fills a vital gap for developers wanting powerful search capabilities without unnecessary complexity.

* **Check out the code on GitHub:** [https://github.com/tensorchord/vechord](https://github.com/tensorchord/vechord)
    
* **Read the documentation:** [https://tensorchord.github.io/vechord/](https://tensorchord.github.io/vechord/)
    
* **Communicate with us on Discord**: [https://discord.gg/KqswhpVgdU](https://discord.gg/KqswhpVgdU)
    

%[https://github.com/tensorchord/vechord]
