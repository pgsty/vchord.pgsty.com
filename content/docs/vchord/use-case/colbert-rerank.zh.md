---
title: "ColBERT 重排"
linkTitle: "ColBERT 重排"
description: "先用单向量 vchordrq 索引召回候选，再在同一条 SQL 里用 @# 运算符按 ColBERTv2 词元级 MaxSim 重排。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/colbert-rerank.md"
aliases:
  - "/docs/use-case/colbert-rerank/"
  - "/vectorchord/use-case/colbert-rerank/"
icon: fa-solid fa-ranking-star
---

本教程在一个 BEIR 数据集上搭建两阶段检索：先用建在“每段文本一条嵌入”上的 `vchordrq` 索引找出 100 个候选，再用存在同一行里的 ColBERTv2 词元向量按 MaxSim 给它们重排。把整段文本池化成一条向量会丢掉单个词元的细节，而对整个语料逐词元打分又太慢；只对候选重排，用一次向量检索的代价就能拿到大部分词元级的准确率。vchord 的 `@#` 运算符在 SQL 里计算 MaxSim，两个阶段在一条查询里完成。

## 工作原理 {#how-it-works}

<img src="/docs/images/maxsim.jpeg" alt="ColBERT 晚期交互：查询和文档的词元分别编码，每个查询词元与最相似的文档词元匹配" width="600" />

[ColBERT](https://github.com/stanford-futuredata/ColBERT) 为文本中的每个词元生成一条归一化的 128 维向量，查询固定编码成 32 条。一段文本的 MaxSim 分数是：对每条查询向量，取它与该文本所有向量内积的最大值，再把这些最大值相加。`embs @# query` 返回这个分数的相反数，所以和距离一样，`ORDER BY ... ASC` 会把最匹配的文本排在最前。

本教程的每一行存放文本、第一阶段用的一条句向量，以及第二阶段用的 ColBERT 词元向量（类型为 `vector(128)[]`）。如果想直接为词元向量建索引而不是对候选重排，见[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)和 [ColQwen2 视觉检索](/zh/docs/vchord/use-case/colqwen2-modal/)。

<a id="Tutorial"></a><a id="tutorial"></a>

## 准备工作 {#prerequisites}

- PostgreSQL 15–19，按[概览](/zh/docs/vchord/getting-started/overview/)装好并预加载 vchord 1.5.0。
- Python 3，以及编码模型和 PostgreSQL 驱动。用这两个模型为几万段文本编码需要 GPU。

  ```bash
  pip install torch sentence-transformers colbert-ai "psycopg[binary]" pgvector requests tqdm
  ```

## 搭建与查询 {#build}

1. <a id="create-schema"></a>创建扩展和表。`emb` 存放 `gte-Qwen2-1.5B-instruct` 生成的 1536 维嵌入，`embs` 存放 ColBERT 词元向量。

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;

   CREATE TABLE corpus (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       doc_id text NOT NULL,
       text text NOT NULL,
       emb vector(1536) NOT NULL,
       embs vector(128)[] NOT NULL
   );
   ```

1. <a id="encode-tokens"></a>新建 `colbert_rerank.py`，先写两个编码器：

   ```python
   import io
   import json
   import sys
   import zipfile

   import psycopg
   import requests
   from colbert.infra import ColBERTConfig
   from colbert.modeling.checkpoint import Checkpoint
   from pgvector.psycopg import register_vector
   from sentence_transformers import SentenceTransformer
   from tqdm import tqdm

   DB_URL = "postgresql://postgres@localhost:5432/postgres"
   DATASET = "fiqa"
   BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/{}.zip"


   class SentenceEncoder:
       def __init__(self):
           self.model = SentenceTransformer(
               "Alibaba-NLP/gte-Qwen2-1.5B-instruct", trust_remote_code=True
           )

       def encode_doc(self, doc):
           return self.model.encode([doc])[0]

       def encode_query(self, query):
           return self.model.encode([query], prompt_name="query")[0]


   class TokenEncoder:
       def __init__(self):
           config = ColBERTConfig(doc_maxlen=220, query_maxlen=32)
           self.checkpoint = Checkpoint("colbert-ir/colbertv2.0", colbert_config=config, verbose=0)

       def encode_doc(self, doc):
           return self.checkpoint.docFromText([doc], keep_dims=False)[0].cpu().numpy()

       def encode_query(self, query):
           return self.checkpoint.queryFromText([query])[0].cpu().numpy()
   ```

1. <a id="insert-and-index"></a>加上导入和建索引。脚本从 BEIR 下载数据集，为每段文本写入两种嵌入，然后建第一阶段的索引。psycopg 会把 NumPy 数组组成的列表当作 `vector[]` 传给数据库。

   ```python
   def load(conn, sentence, token):
       url = BEIR_URL.format(DATASET)
       archive = zipfile.ZipFile(io.BytesIO(requests.get(url, timeout=600).content))
       with archive.open(f"{DATASET}/corpus.jsonl") as f:
           docs = [json.loads(line) for line in f]
       with conn.cursor() as cur:
           for doc in tqdm(docs):
               text = f"{doc['title']} {doc['text']}"
               cur.execute(
                   "INSERT INTO corpus (doc_id, text, emb, embs) VALUES (%s, %s, %s, %s)",
                   (doc["_id"], text, sentence.encode_doc(text), list(token.encode_doc(text))),
               )
       lists = min(4 * int(len(docs) ** 0.5), len(docs) // 40)
       conn.execute(f"""
           CREATE INDEX corpus_emb_idx ON corpus USING vchordrq (emb vector_l2_ops)
           WITH (options = $$
           residual_quantization = true
           [build.internal]
           lists = [{lists}]
           build_threads = 8
           $$, probes = '{max(1, lists // 10)}')
       """)
   ```

   `lists` 和 `probes` 的公式沿用了下文测试结果所用的配置。为自己的表选取这两个值，见 [vchordrq 索引](/zh/docs/vchord/usage/indexing/#lists)。

1. <a id="query-and-rerank"></a>加上检索。内层查询从索引取 100 个候选，外层查询按 MaxSim 重排：

   ```python
   SEARCH_SQL = """
   SELECT doc_id, text
   FROM (
       SELECT doc_id, text, embs
       FROM corpus
       ORDER BY emb <-> %(emb)s
       LIMIT %(candidates)s
   ) AS candidates
   ORDER BY embs @# %(embs)s::vector[]
   LIMIT %(k)s
   """


   def search(conn, query, sentence, token, candidates=100, k=10):
       params = {
           "emb": sentence.encode_query(query),
           "embs": list(token.encode_query(query)),
           "candidates": candidates,
           "k": k,
       }
       return conn.execute(SEARCH_SQL, params).fetchall()


   if __name__ == "__main__":
       sentence, token = SentenceEncoder(), TokenEncoder()
       with psycopg.connect(DB_URL, autocommit=True) as conn:
           register_vector(conn)
           if sys.argv[1] == "load":
               load(conn, sentence, token)
           else:
               for doc_id, text in search(conn, sys.argv[1], sentence, token):
                   print(doc_id, text[:80])
   ```

1. 先导入一次语料，然后检索：

   ```bash
   python colbert_rerank.py load
   python colbert_rerank.py "How do I report foreign income on my tax return?"
   ```
{.steps}

`candidates` 决定了结果的上限：第一阶段漏掉的文本不可能被重排进前 10。重排结果里缺了你预期的文本时，调大它或 `probes`。

<a id="Evaluation"></a>

## 测试结果 {#evaluation}

配套仓库 [kemingy/vectorchord-colbert](https://github.com/kemingy/vectorchord-colbert) 用这两个编码器在两个 BEIR 数据集上测量了 NDCG@10，重排的是向量检索的前 10 条。它用自己写的 SQL 函数给候选打分，而不是 `@#`，所以本教程的结果可能有出入。

| 数据集 | 向量检索 | 加 ColBERT 重排 |
| --- | --- | --- |
| FiQA | 0.23211 | **0.30330** |
| Quora | 0.31599 | **0.39340** |

## 限制 {#limits}

- 词元向量让行变得很大：220 个词元的文本要存约 110 KB 的 `vector(128)[]`。把列声明成 `halfvec(128)[]` 可以减半，`@#` 同样支持 `halfvec[]`。
- 重排要读取每个候选的 `embs`，所以开销随 `candidates` 增长，而不随表的大小增长。

<a id="future-work"></a><a id="References"></a><a id="references"></a>
