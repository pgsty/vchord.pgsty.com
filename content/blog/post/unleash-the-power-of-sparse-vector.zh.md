---
title: "释放稀疏向量的强大潜能"
date: 2024-07-05
description: "结合稀疏向量、BGE-M3 与 pgvecto.rs，以纯向量搜索释放数据流水线的全部潜能"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "sparsevectors"
upstream_link: "https://blog.vectorchord.ai/unleash-the-power-of-sparse-vector"
upstream_copyright: "© 2024 Junyu Chen (TensorChord Inc.)"
math: true
aliases:
  - "/blog/unleash-the-power-of-sparse-vector/"
  - "/unleash-the-power-of-sparse-vector/"
authors: ["junyu-chen"]
images: ["/blog/covers/unleash-the-power-of-sparse-vector.png"]
---

在过去，混合搜索（hybrid search）通常结合两种搜索方式：传统的基于关键词的搜索与基于向量的相似度搜索。然而，稀疏向量（sparse vector）可以作为关键词搜索的替代方案，通过纯向量搜索释放数据流水线的全部潜能。

本文将探讨如何结合 [BGE-M3](https://github.com/FlagOpen/FlagEmbedding/tree/master/FlagEmbedding/BGE_M3) 与 [pgvecto.rs](/zh/docs/vectors/)，同时利用稀疏向量和稠密向量（dense vector）来充分发挥混合搜索的潜力。

让我们开始吧。

## 稀疏向量与稠密向量嵌入概览 {#an-overview-of-sparse-and-dense-vector-embedding}

![Sparse Vector VS Dense Vector](https://cdn.hashnode.com/res/hashnode/image/upload/v1711958357065/ef840509-b58c-4476-9f6d-9d6c698a86a7.png)

稀疏向量是仅包含少量非零值的高维向量，非常适合传统的信息检索场景。例如，一个拥有 32,000 个维度但只有 2 个非零元素的向量，就是典型的稀疏向量。


$$
S[1\times 32000]=\left[ \begin{matrix} 0 & 0 & 0.015 & 0 & 0 & 0 & 0 & \cdots & 0.543 & 0 \end{matrix} \right]
$$


稠密向量则是来自神经网络的嵌入表示。它们由文本嵌入模型生成，其中绝大部分或所有元素均为非零值。它们的维度要少得多，通常为 256 或 1536 维，远低于稀疏向量。


$$
D[1\times 256]=\left[ \begin{matrix} 0.342 & 1.774 & 0.870 & 0.001 & \cdots & 0.543 & 0.999 \end{matrix} \right]
$$


稠密向量和稀疏向量都用于表示文本片段的特征，但二者存在显著差异。稠密向量嵌入中的单个维度本身并没有明确含义，因为它过于抽象，无法直接确定其具体所指；只有将所有维度组合在一起时，它们才能共同表达输入文本的语义信息。

稀疏向量的维度等于词表大小（vocabulary size），其中每个元素代表对应词语在文本中的权重。

通常情况下，权重越高的词在文本中越重要。稀疏向量简化了对文本与词表之间关系的分析和可视化。而若要对稠密向量进行可视化，则需要借助额外的降维算法，例如：

* [主成分分析 (PCA)](https://en.wikipedia.org/wiki/Principal_component_analysis)
    
* [t-分布随机邻域嵌入 (T-SNE)](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding)
    
* [均匀流形逼近与投影 (UMAP)](https://arxiv.org/abs/1802.03426)
    

|  | 稠密向量 (Dense Vector) | 稀疏向量 (Sparse Vector) |
| --- | --- | --- |
| 维度 | 数百至数千 | 数万 |
| 元素含义 | 无独立含义 | 词语权重 |
| 可解释性 | 难 | 易 |
| 用途 | 向量距离计算 | 向量距离计算 / 可视化 |
| 语义敏感度 | 高 | 低 |

与稠密向量相比，稀疏向量在捕捉词语间关系（尤其是同义词和相关术语）方面通常表现较弱。

例如，`rocket`（火箭）和 `SPACE X` 都与太空探索相关，稠密向量更有可能发现它们之间的相似性，并为相应文本赋予更近的向量距离。

## 如何生成向量嵌入？ {#how-to-create-a-vector-embedding}

向量嵌入是输入数据在深度学习模型（即嵌入模型）中的内部表示。大多数嵌入模型（如 `text-embedding-3-small`）仅输出稠密嵌入。

[SPLADE](https://europe.naverlabs.com/research/computer-science/splade-a-sparse-bi-encoder-bert-based-model-achieves-effective-and-efficient-full-text-document-ranking/?utm_source=qdrant&utm_medium=website&utm_campaign=sparse-vectors&utm_content=article&utm_term=sparse-vectors) 和 [BGE-M3](https://arxiv.org/pdf/2402.03216.pdf) 则可以生成稀疏嵌入（有时也称为词法权重 lexical weights）。在本节中，我们将介绍如何使用 `BGE-M3` 模型来同时生成稠密向量和稀疏向量。

> [!DETAILS] 关于 BGE-M3
> `BGE-M3` 是一个多功能模型，能够同时执行嵌入模型的三种常见检索功能：稠密检索（dense retrieval）、多向量检索（multi-vector retrieval）和稀疏检索（sparse retrieval）。

```python
# pip install -U FlagEmbedding

from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
sentences = ["What is BM25?", "Definition of BM25"]

output = model.encode(sentences, return_dense=True, return_sparse=True)

# The dense embedding of the two texts above:
dense_embedding = output['dense_vecs']
# [[-0.02501617 -0.04525582 -0.01972856 ... -0.0099566   0.01677509
#   0.01292699]
# [-0.0106499  -0.04731942 -0.01477693 ... -0.0149255   0.01040097
#   0.00965083]

sparse_weight_id = output['lexical_weights']

# You can see the weight for each token:
# print(model.convert_id_to_token(sparse_weight_id))
# 
# [{'What': 0.10430284, 'is': 0.10090457, 'BM': 0.2635918, '25': 0.3382988, '?': 0.052101523}, 
# {'Definition': 0.14298248, 'of': 0.076763615, 'BM': 0.2577639, '25': 0.33806682}]
```

通过将文本输入到像 `BGE-M3` 这样的稀疏嵌入模型中，我们可以轻松获得稀疏嵌入。

```python
# pip install -U numpy

import numpy as np

# Sparse vector embedding of text
sparse_indices = [[int(token_id) for token_id in text] for text in sparse_weight_id]
# [[4865, 83, 90017, 2588, 32], [155455, 111, 90017, 2588]]
sparse_values = [[float(text[token_id]) for token_id in text] for text in sparse_weight_id]
# [[0.10430284, 0.10090457, 0.2635918, 0.3382988, 0.052101523], [0.14298248, 0.076763615, 0.2577639, 0.33806682]]

# Sparse indexes must be ascending for each pgvecto.rs
for i in range(len(sparse_weight_id)):
    sparse_values[i] = [x for _, x in sorted(zip(sparse_indices[i], sparse_values[i]))]
    sparse_indices[i] = sorted(sparse_indices[i])
```

现在我们已经同时获得了稀疏嵌入和稠密嵌入，接下来将它们插入向量数据库。

<a id="storing-vectors-in-pgvecto-rs-http-pgvecto-rs"></a>
## 在 [pgvecto.rs](/zh/docs/vectors/) 中存储向量 {#storing-vectors-in-pgvectors}

首先，需要部署一个 [`pgvecto.rs`](/zh/docs/vectors/) 实例用于向量的存储与检索。可以通过官方的 `pgvecto-rs` Docker 镜像快速启动：

```bash
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.3.0
```

安装好这一唯一必需的依赖项后，让我们创建一张表来存储向量。

[`pgvecto.rs`](/zh/docs/vectors/) 通过不同的数据类型支持稠密向量和稀疏向量：

* `vector`：用于稠密向量
    
* `svector`：用于稀疏向量
    

`BGE-M3` 模型的稠密嵌入维度为 1024，稀疏嵌入维度为 250002（与分词器词表大小一致）。

```python
print(len(model.tokenizer))
# 250002
```

在本例中，我们创建一张名为 `documents` 的表，包含四列：ID 列（`id`）、文本列（`text`）以及两个向量列（`sparse` 用于存储稀疏向量，`dense` 用于存储稠密向量）。

```python
# pip install -U psycopg

import psycopg
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

with psycopg.connect(URL) as conn:
    conn.execute("DROP TABLE IF EXISTS documents;")
    conn.execute(f"""
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY, 
            text TEXT NOT NULL,
            dense vector(1024) NOT NULL,
            sparse svector({len(model.tokenizer)}) NOT NULL);
    """
    )
```

表创建完成后，我们就可以将嵌入插入表中，并为向量列创建索引。

```python
# pip install -U pgvecto_rs

import psycopg
from pgvecto_rs.psycopg import register_vector
URL = "postgresql://postgres:mysecretpassword@localhost:5432/postgres"

with psycopg.connect(URL) as conn:
    register_vector(conn)
    for text, dense, sparse_ind, sparse_val in zip(sentences, dense_embedding, sparse_indices, sparse_values):
        conn.execute(
            "INSERT INTO documents (text, dense, sparse) VALUES (%s, %s, to_svector(%s, %s::real[]::int[], %s::real[]));",
            (text, dense, len(model.tokenizer), sparse_ind, sparse_val),
        )
    conn.execute("""
        CREATE INDEX ON documents 
        USING vectors (sparse svector_dot_ops) 
        WITH (options = \"[indexing.hnsw]\");
    """)
    conn.execute("""
        CREATE INDEX ON documents 
        USING vectors (dense vector_l2_ops) 
        WITH (options = \"[indexing.hnsw]\");
    """)
```

对于稠密向量，`vector_l2_ops` 计算的是平方欧氏距离（Squared Euclidean distance），这是最常用的距离度量方式。


$$
D_{L2} = \Sigma (x_i - y_i) ^ 2
$$


对于稀疏向量，`svector_dot_ops` 计算的是点积（dot product），这是一种更加高效的计算方法。


$$
D_{dot} = - \Sigma x_iy_i
$$


有关 [`pgvecto.rs`](/zh/docs/vectors/) 中索引类型的更多信息，请[查阅我们的文档](/zh/docs/vectors/getting-started/overview/)。

## 检索与混合结果 {#retrieving-and-mixing-results}

将向量存入数据库后，我们便可以使用 [`pgvecto.rs`](/zh/docs/vectors/) 扩展高效地查询它们。为了找出与给定输入文本最接近的向量，我们需要使用相同的模型对该文本进行编码。

这一过程与上一节介绍的步骤完全相同：

```python
def embedding(sentence: str) -> tuple[np.ndarray, list[list[int]], list[list[float]]]:
    """
    Create dense and sparse embeddings from text
    """
    output = model.encode(sentence, return_dense=True, return_sparse=True, return_colbert_vecs=False)
    dense_embedding = output['dense_vecs']
    sparse_weight_id = output['lexical_weights']
    sparse_indices = [int(token_id) for token_id in sparse_weight_id]
    sparse_values = [float(sparse_weight_id[token_id]) for token_id in sparse_weight_id]

    sparse_values = [x for _, x in sorted(zip(sparse_indices, sparse_values))]
    sparse_indices = sorted(sparse_indices)
    return dense_embedding, sparse_indices, sparse_values
```

[`pgvecto.rs`](/zh/docs/vectors/) 扩展提供了简洁的 `SELECT` 语句来分别检索稀疏向量和稠密向量，如下所示：

```python
dense_embedding, sparse_indices, sparse_values = embedding("The text you want to search...")

with psycopg.connect(URL) as conn:
    register_vector(conn)
    cur = conn.execute(
        "SELECT text FROM documents ORDER BY sparse <#> to_svector(%s, %s::real[]::int[], %s::real[]) LIMIT 50;",
        (len(model.tokenizer), sparse_indices, sparse_values),
    )
    sparse_result = cur.fetchall()
      
    cur = conn.execute(
              "SELECT text FROM documents ORDER BY dense <-> %s LIMIT 50;",
              (dense_embedding,),
          )
    dense_result = cur.fetchall()
    
# Merge sparse and dense vector search results
mix_text = set([r[0] for r in dense_result]).union([r[0] for r in sparse_result])
```

为了对合并后的结果进行重排序，您可以使用常见的融合方法，例如倒数排序融合（Reciprocal Rank Fusion, RRF）。不过，为了更好地发挥 `BGE-M3` 的优势，我们可以引入 `BGE-M3` 配套的 `Reranker`（重排序）模型。与嵌入模型不同，`Reranker` 直接接收文本对作为输入，并输出它们之间的相似度或相关性得分。

我们可以初始化一个 `Reranker` 模型，并将混合后的候选文本输入其中。通过这种方法，重排序就像按照 `Reranker` 模型评估的得分进行排序一样简单。

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)

# Obtain relevance scores （Higher scores indicate greater relevance）
scores = reranker.compute_score([["The text you want to search...", candidate] for candidate in mix_text])
# Rerank text using combined dense and sparse embeddings
reranked_text = [t for _, t in sorted(zip(scores, mix_text))]
```

恭喜！现在我们已经迈出了探索稀疏向量搜索世界的第一步。

## **总结** {#summary}

在本文中，我们使用 BGE-M3 模型生成了稀疏向量和稠密向量，并在 Postgres 数据库中完成了存储与查询。这一切都得益于 [pgvecto.rs](/zh/docs/vectors/) v0.3.0 引入的全新特性：稀疏向量类型。

敬请期待，我们将继续分享更多关于 [pgvecto.rs](/zh/docs/vectors/) 的精彩能力！

欢迎加入我们的 [**Discord 社区**](https://discord.gg/KqswhpVgdU)，与开发者及其他用户交流互动，共同推动 [**pgvecto.rs**](/zh/docs/vectors/) 的持续进化！
