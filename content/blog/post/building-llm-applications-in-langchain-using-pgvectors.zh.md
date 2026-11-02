---
title: "使用 pgvecto.rs 在 LangChain 中构建大语言模型应用"
date: 2024-03-08
description: "利用 pgvecto.rs 的强大能力，为你在 LangChain 中构建的大语言模型（LLM）应用全面加速"
author: "[Ce Gao](https://github.com/gaocegege) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "ai"
upstream_link: "https://blog.vectorchord.ai/building-llm-applications-in-langchain-using-pgvectors"
upstream_copyright: "© 2024 Ce Gao (TensorChord Inc.)"
aliases:
  - "/blog/building-llm-applications-in-langchain-using-pgvectors/"
  - "/building-llm-applications-in-langchain-using-pgvectors/"
authors: ["ce-gao"]
images: ["/blog/covers/building-llm-applications-in-langchain-using-pgvectors.png"]
---

**LangChain** 是一个用于开发由语言模型驱动的应用程序的框架。它使应用程序能够：

* **具备上下文感知能力**：将语言模型连接到各种上下文来源（提示词指令、少样本示例、作为回答依据的业务内容等）。
    
* **进行推理**：依靠语言模型进行推理（例如如何根据提供的上下文作答、应当采取什么行动等）。
    

[pgvecto.rs](/zh/docs/vectors/) 是 Postgres 中的一款向量搜索扩展。在本篇博客中，我们将向你展示如何使用 LangChain 和 pgvecto.rs 构建 LLM 应用程序。

## **安装依赖** {#install-dependencies}

使用 LangChain 集成需要安装以下[依赖项](/zh/docs/vectors/integration/langchain/#install-dependencies)：

```bash
pip install langchain langchain-openai pgvecto-rs
```

你可以在 Docker 容器中启动安装了 [`pgvecto.rs`](/zh/docs/vectors/) 扩展的 [Postgres](/zh/docs/vectors/integration/langchain/#install-dependencies) 实例：

```bash
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.2.0
```

然后，你可以使用 `psql` 命令行工具[连接](/zh/docs/vectors/integration/langchain/#install-dependencies)到数据库。默认用户名为 `postgres`，默认密码为 `mysecretpassword`。

```bash
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

运行以下 [SQL](/zh/docs/vectors/integration/langchain/#install-dependencies) 以确保扩展已启用：

```bash
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

## **创建数据库并加载文档** {#create-the-database-and-load-documents}

下面我们将展示如何在 LangChain 中使用 `pgvecto.rs` 检索最相似的向量。

首先，你需要创建文本加载器（TextLoader）和文本切分器（CharacterTextSplitter），将文本切分为多个片段（Chunks）。这里我们以 Markdown 文件 [**pgvecto-rs/getting-started/overview.md**](/zh/docs/vectors/getting-started/overview/) 为例：

```python
## Loading Environment Variables
from dotenv import load_dotenv

load_dotenv()

from langchain.docstore.document import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores.pgvecto_rs import PGVecto_rs
from langchain_openai import OpenAIEmbeddings


loader = TextLoader("./src/getting-started/overview.md")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()
```

接着，我们创建 `PGVecto_rs` 实例并将文档加载到数据库中：

```python
## PGVecto.rs needs the connection string to the database.
## We will load it from the environment variables.
import os

PORT = os.getenv("DB_PORT", 5432)
HOST = os.getenv("DB_HOST", "localhost")
USER = os.getenv("DB_USER", "postgres")
PASS = os.getenv("DB_PASS", "mysecretpassword")
DB_NAME = os.getenv("DB_NAME", "postgres")

# Run tests with shell:
URL = "postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}".format(
    port=PORT,
    host=HOST,
    username=USER,
    password=PASS,
    db_name=DB_NAME,
)

# The pgvectors Module will try to create a table with the name of the collection.
# So, make sure that the collection name is unique and the user has the permission to create a table.

COLLECTION_NAME = "state_of_the_union_test"

db = PGVecto_rs.from_documents(
    embedding=embeddings,
    documents=docs,
    collection_name=COLLECTION_NAME,
    db_url=URL,
)
```

## **查询索引** {#query-index}

最后，我们可以在 LangChain 中检索最相似的文本片段：

```python
query = "What is pgvecto.rs"
docs_with_score = db.similarity_search_with_score(query)

for doc, score in docs_with_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)
```

输出结果如下：

```plaintext
Created a chunk of size 1181, which is longer than the specified 1000
--------------------------------------------------------------------------------
Score:  0.25059962
# Overview

An introduction to the pgvecto.rs.

## What is pgvecto.rs

pgvecto.rs is a Postgres extension that provides vector similarity search functions. It is written in Rust and based on [pgrx](https://github.com/tcdi/pgrx). It is currently in the beta status, we invite you to try it out in production and provide us with feedback. Read more at [📝our launch blog](https://modelz.ai/blog/pgvecto-rs).

## Why use pgvecto.rs
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Score:  0.29536954
- 💃 **Easy to use**: pgvecto.rs is a Postgres extension, which means that you can use it directly within your existing database. This makes it easy to integrate into your existing workflows and applications.
- 🔗 **Async indexing**: pgvecto.rs's index is asynchronously constructed by the background threads and does not block insertions and always ready for new queries.
- 🥅 **Filtering**: pgvecto.rs supports filtering. You can set conditions when searching or retrieving points. This is the missing feature of other postgres extensions.
- 🧮 **Quantization**: pgvecto.rs supports scalar quantization and product qutization up to 64x.
- 🦀 **Rewrite in Rust**: Rust's strict compile-time checks ensure memory safety, reducing the risk of bugs and security issues commonly associated with C extensions.

## Comparison with pgvector
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Score:  0.35845917
More details at [📝`pgvecto.rs` vs. pgvector](/faqs/comparison-pgvector.md).

## Quick start

For new users, we recommend using the [Docker image](https://hub.docker.com/r/tensorchord/pgvecto-rs) to get started quickly.
...
```

## **从现有数据库初始化** {#initialize-from-an-existing-database}

在上面的示例中，我们从零创建了一个向量存储。但在很多时候，我们希望直接使用已有的向量存储。为此，我们可以直接对其进行初始化：

```python
db = PGVecto_rs(
    embedding=embeddings,
    collection_name=COLLECTION_NAME,
    # OpenAI embedding has 1536 dimensions.
    dimension=1536,
    db_url=URL,
)
```

随后，我们可以向存储中添加新向量并执行查询：

```python
db.add_documents([Document(page_content="foo")])
docs_with_score = db.similarity_search_with_score("foo")
print(docs_with_score[0])
```

输出结果为：

```python
(Document(page_content='foo'), 0.0)
```
