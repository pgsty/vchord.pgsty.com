---
title: "稀疏向量搜索"
linkTitle: "稀疏向量"
description: "过去，混合搜索结合了传统的关键词搜索与基于向量的相似度搜索。如今，稀疏向量可以替代关键词搜索，通过纯向量搜索释放数据流水线的全部潜力。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/use-case/sparse-vector.md"
math: true
aliases:
  - "/use-case/sparse-vector/"
icon: fa-solid fa-braille
---

过去，混合搜索（Hybrid Search）通常将传统的基于关键词的搜索与基于向量的相似度搜索结合在一起。然而，稀疏向量（Sparse Vector）可以作为关键词搜索的替代方案，通过纯向量搜索充分释放数据流水线的全部潜力。

> [!TIP]
> 有关基于关键词的混合搜索的更多信息，请参阅[混合搜索](/zh/docs/vectors/use-case/hybrid-search/)。


本文将探讨如何结合使用 [BGE-M3](https://huggingface.co/BAAI/bge-m3) 与 `pgvecto.rs`，同时利用稀疏向量和稠密向量发掘混合搜索的潜力。

下面让我们开始吧。

## 稀疏向量与稠密向量嵌入概览 {#an-overview-of-sparse-and-dense-vector-embedding}

稀疏向量是仅包含极少数非零值的高维向量，非常适合传统的信息检索场景。例如，一个拥有 32,000 个维度但只有 2 个非零元素的向量就是典型的稀疏向量。

$$
S[1\times 32000]=\left[
 \begin{matrix}
   0 & 0 & 0.015 & 0 & 0 & 0 & 0 & \cdots & 0.543 & 0
  \end{matrix}
  \right]
$$



稠密向量（Dense Vector）则是来自神经网络的嵌入表示。它们由文本嵌入模型生成，绝大部分或所有元素均为非零值。它们的维度通常较低，例如 256 维或 1536 维，远低于稀疏向量。

$$
D[1\times 256]=\left[
 \begin{matrix}
   0.342 & 1.774 & 0.087 & 0.321 & 0.664 & 0.870 & 0.001 & \cdots & 0.543 & 0.999
  \end{matrix}
  \right]
$$



稠密向量和稀疏向量都用于表示文本片段的特征，但两者存在显著差异。稠密向量嵌入中的单个维度本身并没有明确的字面含义，因为它过于抽象；只有将所有维度组合在一起时，它们才能表达输入文本的整体语义。

相比之下，稀疏向量的维度等于词表（Vocabulary）的大小，其中每个元素代表对应词项在该文本中的权重。

通常情况下，权重越高的词在文本中越重要。稀疏向量简化了对文本与词表之间关系的分析和可视化；而若要对稠密向量进行可视化，则需要借助额外的降维算法，例如：

- [主成分分析（PCA）](https://en.wikipedia.org/wiki/Principal_component_analysis)
- [t-分布随机邻域嵌入（t-SNE）](https://en.wikipedia.org/wiki/T-distributed_stochastic_neighbor_embedding)
- [均匀流形逼近与投影（UMAP）](https://arxiv.org/abs/1802.03426)

|              | 稠密向量（Dense Vector） | 稀疏向量（Sparse Vector） |
| ------------ | ------------------------ | ------------------------- |
| 维度规模     | 数百至数千维             | 数万至数十万维            |
| 单个元素含义 | 无单独含义               | 词项权重（Word Weight）   |
| 可解释性     | 困难                     | 容易                      |
| 常见用途     | 计算向量距离             | 计算向量距离 / 可视化分析 |
| 语义敏感度   | 高                       | 低                        |
{.wide .expand}

与稠密向量相比，稀疏向量在捕捉词与词之间的深层语义关系（尤其是同义词和相关概念）方面通常不如稠密向量有效。

例如，`rocket`（火箭）和 `SPACE X` 都与太空探索相关，稠密向量更有可能识别出它们之间的语义相似性，并为相应文本赋予更近的向量距离。

## 如何生成向量嵌入？ {#how-to-create-a-vector-embedding}

向量嵌入是输入数据在深度学习模型（即嵌入模型）中的内部表示。大多数嵌入模型（如 `text-embedding-3-small`）仅输出稠密嵌入。

而 [SPLADE](https://europe.naverlabs.com/blog/splade-a-sparse-bi-encoder-bert-based-model-achieves-effective-and-efficient-first-stage-ranking/) 和 [BGE-M3](https://arxiv.org/pdf/2402.03216.pdf) 等模型则可以生成稀疏嵌入（有时也称为词法权重 lexical weights）。在本节中，我们将介绍如何使用 `BGE-M3` 模型同时生成稠密向量和稀疏向量。

`BGE-M3` 是一个多功能模型，能够同时执行嵌入模型的三种常见检索功能：稠密检索（Dense retrieval）、多向量检索（Multi-vector retrieval）和稀疏检索（Sparse retrieval）。下面我们来学习如何用它生成稠密嵌入和稀疏嵌入。

```python
# pip install -U FlagEmbedding

from FlagEmbedding import BGEM3FlagModel

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
sentences = ["What is BM25?", "Definition of BM25"]

output = model.encode(sentences, return_dense=True, return_sparse=True)

# 上述两段文本的稠密嵌入：
dense_embedding = output['dense_vecs']
# [[-0.02501617 -0.04525582 -0.01972856 ... -0.0099566   0.01677509
#   0.01292699]
# [-0.0106499  -0.04731942 -0.01477693 ... -0.0149255   0.01040097
#   0.00965083]

sparse_weight_id = output['lexical_weights']

# 您可以查看每个 token 对应的权重：
# print(model.convert_id_to_token(sparse_weight_id))
# 
# [{'What': 0.10430284, 'is': 0.10090457, 'BM': 0.2635918, '25': 0.3382988, '?': 0.052101523}, 
# {'Definition': 0.14298248, 'of': 0.076763615, 'BM': 0.2577639, '25': 0.33806682}]
```

对于所有句子和词项，可以构建如下的“文本-词项”矩阵：

| 文本               | What | is   | BM   | 25   | ?    | Definition | of   | ...  |
| ------------------ | ---- | ---- | ---- | ---- | ---- | ---------- | ---- | ---- |
| What is BM25?      | 0.08 | 0.08 | 0.13 | 0.25 | 0.04 | 0          | 0    | ...  |
| Definition of BM25 | 0    | 0    | 0.25 | 0.33 | 0    | 0.14       | 0.06 | ...  |
{.wide .expand}


当包含整个词表时，该矩阵是高度稀疏的——大多数词只出现在少数几个句子中，只有这些位置会产生非零权重。

通过将文本输入到像 `BGE-M3` 这样的稀疏嵌入模型中，我们可以轻松获得文本的稀疏嵌入表示：

```python
# pip install -U numpy

import numpy as np

# 提取文本的稀疏向量下标与对应权重值
sparse_indices = [[int(token_id) for token_id in text] for text in sparse_weight_id]
# [[4865, 83, 90017, 2588, 32], [155455, 111, 90017, 2588]]
sparse_values = [[float(text[token_id]) for token_id in text] for text in sparse_weight_id]
# [[0.10430284, 0.10090457, 0.2635918, 0.3382988, 0.052101523], [0.14298248, 0.076763615, 0.2577639, 0.33806682]]

# 在 pgvecto.rs 中，每个稀疏向量的下标必须按升序排列
for i in range(len(sparse_weight_id)):
    sparse_values[i] = [x for _, x in sorted(zip(sparse_indices[i], sparse_values[i]))]
    sparse_indices[i] = sorted(sparse_indices[i])
```

现在我们同时拥有了稀疏嵌入和稠密嵌入，接下来可以将它们插入向量数据库了。

<a id="storing-vectors-in-pgvecto-rs"></a>
## 在 pgvecto.rs 中存储向量 {#storing-vectors-in-pgvectors}

首先，向量存储和检索需要一个运行中的 `pgvecto.rs` 实例。可以通过官方的 `pgvecto-rs` Docker 镜像快速启动：

```bash
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.3.0
```

准备好数据库环境后，让我们创建一张表来存储向量。

`pgvecto.rs` 通过不同的数据类型分别支持稠密向量和稀疏向量：

- `vector`：用于存储稠密向量
- `svector`：用于存储稀疏向量

`BGE-M3` 模型的稠密嵌入维度为 1024，而稀疏嵌入维度为 250002（与分词器词表的大小一致）。

```python
print(len(model.tokenizer))
# 250002
```

在本例中，我们创建一张名为 `documents` 的表，包含四个列：ID 列（`id`）、文本列（`text`）以及两个向量列（`sparse` 用于存储稀疏向量，`dense` 用于存储稠密向量）。

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

表创建完成后，我们可以将嵌入向量插入表中，并为两个向量列分别创建索引：

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

对于稠密向量，`vector_l2_ops` 计算平方欧氏距离，这是最常用的距离度量：

$$
D_{L2} = \Sigma (x_i - y_i) ^ 2
$$

对于稀疏向量，`svector_dot_ops` 计算负点积，这种计算方式在稀疏表示下更加高效：

$$
D_{dot} = - \Sigma x_i y_i
$$



有关 `pgvecto.rs` 中索引类型的更多信息，请[查看我们的索引文档](/zh/docs/vectors/usage/indexing/)。

## 检索与结果融合 {#retrieving-and-mixing-results}

将向量存入数据库后，我们便可以使用 `pgvecto.rs` 扩展高效地查询它们。为了找出与给定输入文本最接近的向量，我们需要使用相同的模型对查询文本进行编码。

该编码过程与上一节完全一致：

```python
def embedding(sentence: str) -> tuple[np.ndarray, list[list[int]], list[list[float]]]:
    """
    从文本生成稠密嵌入和稀疏嵌入
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

借助 `pgvecto.rs` 扩展，只需通过简单的 `SELECT` 语句即可分别检索稀疏向量和稠密向量：

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
    
# 合并稀疏向量与稠密向量的搜索结果
mix_text = set([r[0] for r in dense_result]).union([r[0] for r in sparse_result])
```

为了对合并后的结果进行重排序（Rerank），您可以使用常见的融合算法，例如倒数排名融合（Reciprocal Rank Fusion, RRF）。不过，为了充分发挥 `BGE-M3` 生态的优势，我们可以引入配套的 `Reranker`（重排序）模型。与嵌入模型不同，`Reranker` 直接以查询文本和候选文本对作为输入，并输出它们之间的相关性得分。

我们可以初始化一个 `Reranker` 模型，并将合并后的候选文本输入其中。通过这种方式，只需按 `Reranker` 模型估算的得分进行排序，即可轻松完成重排序：

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)

# 获取相关性得分（得分越高表示相关性越强）
scores = reranker.compute_score([["The text you want to search...", candidate] for candidate in mix_text])
# 对结合了稠密嵌入与稀疏嵌入检索出的候选文本进行重排序
reranked_text = [t for _, t in sorted(zip(scores, mix_text))]
```

恭喜！至此，我们已经迈出了探索稀疏向量搜索世界的第一步。
