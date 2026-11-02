---
title: "LlamaIndex"
linkTitle: "LlamaIndex"
description: "LlamaIndex 是一个简单、灵活的数据框架，用于将自定义数据源连接到大语言模型（LLM）。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/integration/llama-index.md"
aliases:
  - "/integration/llama-index/"
---

LlamaIndex 是一个简单、灵活的数据框架，用于将自定义数据源连接到大语言模型（LLM）。

`pgvecto.rs` 提供了 LlamaIndex 集成，支持检索最相似的向量。

## 安装依赖 {#install-dependencies}

使用 LlamaIndex 集成需要安装以下依赖：

```sh
pip install llama-index "pgvecto_rs[sdk]"
```

你可以在 Docker 容器中启动带有 `pgvecto.rs` 扩展的 Postgres 实例：

```sh
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.2.0
```

然后可以使用 `psql` 命令行工具连接到数据库。默认用户名为 `postgres`，默认密码为 `mysecretpassword`。

```sh
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

执行以下 SQL 以确保扩展已启用：

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

## 创建数据库并加载文档 {#create-the-database-and-load-documents}

首先，创建数据库连接客户端。这里同样以 Markdown 文件 [getting-started/overview.md](/zh/docs/vectors/getting-started/overview/) 为例。

```python
import logging
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from pgvecto_rs.sdk import PGVectoRs

URL = "postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}".format(
    port=os.getenv("DB_PORT", "5432"),
    host=os.getenv("DB_HOST", "localhost"),
    username=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS", "mysecretpassword"),
    db_name=os.getenv("DB_NAME", "postgres"),
)

client = PGVectoRs(
    db_url=URL,
    collection_name="example",
    dimension=1536,  # Using OpenAI’s text-embedding-ada-002
)
```

接着配置 OpenAI API 密钥，并将文档加载到数据库中。

```python
import os

os.environ["OPENAI_API_KEY"] = "sk-..."

from llama_index import SimpleDirectoryReader, VectorStoreIndex
from llama_index.vector_stores import PGVectoRsStore

# load documents
documents = SimpleDirectoryReader("./src/getting-started/overview.md").load_data()

# initialize without metadata filter
from llama_index.storage.storage_context import StorageContext

vector_store = PGVectoRsStore(client=client)
storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)
```

### 查询索引 {#query-index}

最后，我们可以检索最相似的文档片段。

```python
# set Logging to DEBUG for more detailed outputs
query_engine = index.as_query_engine()
response = query_engine.query("What did the author do growing up?")
```
