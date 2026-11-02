---
title: "在 PostgreSQL 中使用 ColBERT 重排序为向量搜索赋能"
date: 2025-01-23
description: "通过本篇详尽教程，学习如何结合 PostgreSQL 与 VectorChord 使用 ColBERT 重排序来提升向量搜索准确度"
author: "[Keming Yang](https://github.com/kemingy) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "colbert"
upstream_link: "https://blog.vectorchord.ai/supercharge-vector-search-with-colbert-rerank-in-postgresql"
upstream_copyright: "© 2025 Keming Yang (TensorChord Inc.)"
aliases:
  - "/blog/supercharge-vector-search-with-colbert-rerank-in-postgresql/"
  - "/supercharge-vector-search-with-colbert-rerank-in-postgresql/"
---

传统的向量搜索方法通常采用句子级嵌入（sentence embeddings）来定位相似内容。然而，通过对词元嵌入（token embeddings）进行池化来生成句子嵌入，可能会牺牲词元级别所蕴含的细粒度细节。[ColBERT](https://github.com/stanford-futuredata/ColBERT) 通过将文本表示为词元级多向量（multi-vectors）而非单个聚合向量，克服了这一局限。这种方法利用词元级的上下文后期交互（contextual late interaction），使 ColBERT 相比仅依赖句子嵌入的方法能够保留更微妙的语义信息，并提高搜索准确度。

![ColBERT 结构（引自原论文）](https://cdn.hashnode.com/res/hashnode/image/upload/v1736414634494/e50e0b90-74da-49d9-813d-5c5ec00317ee.jpeg)

如上图所示，ColBERT 将每个文档/查询编码为一组词元向量列表，并在查询时计算最大相似度（MaxSim）。

词元级后期交互需要更多的计算资源和存储空间。这使得在大规模数据集上直接使用 ColBERT 搜索极具挑战性，尤其是在对低延迟有较高要求的场景下。

一种可行的解决方案是将句子级向量搜索与词元级后期交互重排序（rerank）相结合，从而兼顾近似向量搜索的高效率与多向量相似度搜索的高质量。

多向量方法不仅局限于纯文本检索任务，还可以应用于视觉文档理解。在多模态检索模型中，诸如 [ColPali](https://huggingface.co/vidore/colpali-v1.3) 和 [ColQwen](https://huggingface.co/vidore/colqwen2-v1.0-merged) 等前沿模型直接将文档图像编码为多向量，展现出比传统“OCR 转文本”方法更强大的性能。

本文将演示如何结合 PostgreSQL 扩展 [VectorChord](https://github.com/tensorchord/VectorChord/) 和 pgvector 来实现 ColBERT 重排序。

<a id="Tutorial"></a>
## 教程 {#tutorial}

假设我们已经准备好了文档数据，首先创建一个表来存储这些文档：

```python
import psycopg
from pgvector.psycopg import register_vector

class PgClient:
    def __init__(self, url: str, dataset: str, sentence_emb_dim: int, token_emb_dim: int):
        self.dataset = dataset
        self.sentence_emb_dim = sentence_emb_dim
        self.token_emb_dim = token_emb_dim
        self.conn = psycopg.connect(url, autocommit=True)
        with self.conn.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vchord CASCADE;")
        register_vector(self.conn)

    def create(self):
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {self.dataset}_corpus "
                "(id INT BY DEFAULT AS IDENTITY PRIMARY KEY, text TEXT, "
                f"emb vector({self.sentence_emb_dim}), embs vector({self.token_emb_dim})[]);"
            )
```

这里我们创建了一张同时包含句子级嵌入和词元级嵌入数组的表。

市面上有许多嵌入 API 和[开源模型](https://huggingface.co/spaces/mteb/leaderboard)，您可以根据具体业务场景选择合适的模型。

对于词元级嵌入：

```python
from colbert.infra import ColBERTConfig
from colbert.modeling.checkpoint import Checkpoint

class TokenEncoder:
    def __init__(self):
        self.config = ColBERTConfig(doc_maxlen=220, query_maxlen=32)
        self.checkpoint = Checkpoint(
            "colbert-ir/colbertv2.0", colbert_config=self.config, verbose=0
        )

    def encode_doc(self, doc: str):
        return self.checkpoint.docFromText([doc], keep_dims=False)[0].numpy()

    def encode_query(self, query: str):
        return self.checkpoint.queryFromText([query])[0].numpy()
```

ColBERT 模型默认生成 128 维的向量。

插入数据：

```python
class PgClient:
    ...
    def insert(self, documents: list[str]):
        with self.conn.cursor() as cursor:
            for doc in tqdm(documents):
                sentence_emb = sentence_encoder.encode_doc(doc)
                token_embs = [emb for emb in token_encoder.encode(doc)]
                cursor.execute(
                    f"INSERT INTO {self.dataset}_corpus (text, emb, embs) VALUES (%s, %s, %s)"
                    (doc, sentence_emb, token_embs)
                )
```

在向量搜索部分，我们可以使用 VectorChord 构建高性能的 RaBitQ 索引：

```python
class PgClient:
    ...
    def index(self, num_doc: int, workers: int):
        n_cluster = 1 << math.ceil(math.log2(num_doc ** 0.5 * 4))
        config = f"""
        residual_quantization = true
        [build.internal]
        lists = [{n_cluster}]
        build_threads = {workers}
        spherical_centroids = false
        """
        with self.conn.cursor() as cursor:
            cursor.execute(f"SET max_parallel_maintenance_workers TO {workers}")
            cursor.execute(f"SET max_parallel_workers TO {workers}")
            cursor.execute(
                f"CREATE INDEX {self.dataset}_rabitq ON {self.dataset}_corpus USING "
                f"vchordrq (emb vector_l2_ops) WITH (options = $${config}$$)"
            )
```

为了加快索引构建过程，我们可以利用外部质心构建功能。详情请参阅《[VectorChord 外部质心构建的优势与步骤](/zh/blog/post/benefits-and-steps-of-external-centroids-building-in-vectorchord/)》。

现在，我们可以在 PostgreSQL 中执行查询：

```python
class PgClient:
    ...
    def query(self, doc: str, topk: int):
        sentence_emb = sentence_encoder.encode_query(doc)
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"SELECT id, text FROM {self.dataset}_corpus ORDER BY emb <-> %s LIMIT {topk}"
            )
            res = cursor.fetchall()
        return res
```

为了支持 `MaxSim` 重排序，我们需要创建一个 SQL 函数：

```python
class PgClient:
    def __init__(self, url: str, dataset: str, sentence_emb_dim: int, token_emb_dim: int):
        ...
        self.conn.execute("""
            CREATE OR REPLACE FUNCTION max_sim(document vector[], query vector[]) RETURNS double precision AS $$
            WITH queries AS (
                SELECT row_number() OVER () AS query_number, * FROM (SELECT unnest(query) AS query)
            ),
            documents AS (
                SELECT unnest(document) AS document
            ),
            similarities AS (
                SELECT query_number, document <=> query AS similarity FROM queries CROSS JOIN documents
            ),
            max_similarities AS (
                SELECT MAX(similarity) AS max_similarity FROM similarities GROUP BY query_number
            )
            SELECT SUM(max_similarity) FROM max_similarities
            $$ LANGUAGE SQL
        """)
```

接下来，我们就可以对向量搜索召回的候选文档进行重排序了：

```python
class PgClient:
    def rerank(self, query: str, ids: list[int], topk: int):
        token_embs = [emb for emb in token_encoder.encode_query(query)]
        with self.conn.cursor() as cursor:
            cursor.execute(
                f"SELECT id, text FROM {self.dataset}_corpus WHERE id = ANY(%s) ORDER BY "
                f"max_sim(embs, %s) DESC LIMIT {topk}"
                (ids, token_embs)
            )
            res = cursor.fetchall()
        return res
```

<a id="Evaluation"></a>
## 评估 {#evaluation}

我们在多个 [BEIR](https://github.com/beir-cellar/beir) 数据集上测试了该方法，结果如下：

| 数据集 | 搜索 NDCG@10 | 重排序 NDCG@10 |
| --- | --- | --- |
| fiqa | 0.23211 | 0.3033 |
| quora | 0.31599 | 0.3934 |

结果表明，ColBERT 重排序能够显著提升向量搜索的结果质量。

所有相关的基准测试代码均可在[此处](https://github.com/kemingy/vectorchord-colbert)找到。

## 未来计划 {#future-work}

将向量搜索、全文检索与 ColBERT 重排序相结合，可以进一步提升检索效果。我们目前也在开发 [PostgreSQL BM25 扩展](https://github.com/tensorchord/VectorChord-bm25)，敬请期待。

<a id="References"></a>
### 参考资料 {#references}

* [https://www.answer.ai/posts/colbert-pooling.html](https://www.answer.ai/posts/colbert-pooling.html)
    
* [https://github.com/stanford-futuredata/ColBERT](https://github.com/stanford-futuredata/ColBERT)
    
* [https://github.com/tensorchord/vectorChord/](https://github.com/tensorchord/vectorChord/)
    
* [https://github.com/tensorchord/VectorChord-bm25](https://github.com/tensorchord/VectorChord-bm25)
    
* [https://huggingface.co/blog/manu/colpali](https://huggingface.co/blog/manu/colpali)
