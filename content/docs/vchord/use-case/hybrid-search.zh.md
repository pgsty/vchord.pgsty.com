---
title: "BM25 与向量混合检索"
linkTitle: "混合检索"
description: "在同一张 PostgreSQL 表上同时执行 BM25 关键词检索和向量检索，用一条 SQL 以倒数排名融合（RRF）合并两路排名，并可选地用交叉编码器重排。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/hybrid-search.md"
math: true
aliases:
  - "/docs/use-case/hybrid-search/"
  - "/vectorchord/use-case/hybrid-search/"
icon: fa-solid fa-code-merge
---

本教程在 SciFact 语料上搭建一个检索：对同一张表同时发出 BM25 关键词查询和向量查询，再把两路排名合并。关键词检索擅长找出包含查询原词的文档，比如编号和生僻词；向量检索擅长找出换了说法、意思相同的文档；两者正好互补。[vchord_bm25](/zh/docs/bm25/) 和 vchord 建在同一张 PostgreSQL 表上，一条 SQL 就能完成两路检索和融合；更看重准确率而不是延迟时，还可以用交叉编码器对合并结果重排。

<a id="what-is-the-vectorchord"></a><a id="what-is-vectorchord-bm25"></a><a id="what-is-bm25"></a><a id="why-a-postgres-native-bm25-ranking-implementation-is-needed"></a>

## 工作原理 {#hybrid-search-explained}

<img src="/docs/images/hybrid-search-1.jpeg" alt="一条查询分别做向量检索和关键词检索，两路结果经融合或重排合成一个列表" width="600" />

每一行存放文本、`vector` 列里的嵌入，以及 `tsvector` 列里的词项。`vchordrq` 索引回答 `ORDER BY embedding <=> query LIMIT 100`，`bm25` 索引回答 `ORDER BY terms <&> query LIMIT 100`。倒数排名融合（RRF）只看文档在每一路中的名次来打分，余弦距离和 BM25 分数这两种量纲完全不用放在一起比较：

$$
\operatorname{RRF}(d) = \sum_{i} \frac{1}{k + \operatorname{rank}_i(d)}
$$

文档没出现在某一路结果里，那一路就不给分。`k = 60` 是常用取值；`k` 越大，前几名之间的分差越小。

<a id="tutorial-use-vectorchord-bm25-and-vectorchord-implement-hybrid-search"></a><a id="tutorial"></a><a id="Prerequisites"></a>

## 准备工作 {#prerequisites}

- PostgreSQL 15–19，装好 vchord 1.5.0 和 vchord_bm25 1.3.0。从 Pigsty 软件源安装：

  ```bash
  pig ext add vchord vchord_bm25
  ```

- Python 3 和下面这些包。模型在 CPU 上也能跑，但用 GPU 给语料生成嵌入会快得多。

  ```bash
  pip install "psycopg[binary]" pgvector FlagEmbedding requests
  ```

## 搭建检索 {#prepare-data}

1. 预加载两个动态库并重启 PostgreSQL。列表里已有的库要保留。

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord, vchord_bm25';
   ```

1. 创建扩展和表。`terms` 由 `content` 生成，每次插入、更新都会自动保持一致：

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;

   CREATE TABLE documents (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       content text NOT NULL,
       embedding vector(1024) NOT NULL,
       terms tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
   );
   ```

1. 导入语料。把下面的代码存为 `load.py`，执行 `python load.py`。它从 BEIR 下载 SciFact 语料，用 BGE-M3 为每篇文档生成 1024 维的归一化向量，再用 COPY 写入：

   ```python
   import io
   import json
   import zipfile

   import psycopg
   import requests
   from FlagEmbedding import BGEM3FlagModel
   from pgvector.psycopg import register_vector

   DB_URL = "postgresql://postgres@localhost:5432/postgres"
   BEIR_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"

   archive = zipfile.ZipFile(io.BytesIO(requests.get(BEIR_URL, timeout=600).content))
   with archive.open("scifact/corpus.jsonl") as f:
       texts = [f"{doc['title']} {doc['text']}" for doc in map(json.loads, f)]

   model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
   embeddings = model.encode(texts, batch_size=32, max_length=8192)["dense_vecs"]

   with psycopg.connect(DB_URL) as conn:
       register_vector(conn)
       with conn.cursor().copy(
           "COPY documents (content, embedding) FROM STDIN WITH (FORMAT BINARY)"
       ) as copy:
           copy.set_types(["text", "vector"])
           for text, embedding in zip(texts, embeddings):
               copy.write_row((text, embedding))
   ```

1. 为两列建索引。SciFact 约 5,000 篇文档，向量索引用默认的单个列表就够了；语料超过 10 万行时，按 [vchordrq 索引](/zh/docs/vchord/usage/indexing/#lists)设置 `lists` 和 `probes`。

   ```sql
   CREATE INDEX documents_embedding_idx ON documents
   USING vchordrq (embedding vector_cosine_ops);

   CREATE INDEX documents_terms_bm25 ON documents
   USING bm25 (terms bm25_ops);
   ```
{.steps}

<a id="semantic-search-with-vectorchord"></a><a id="key-word-search-with-vectorchord-bm25"></a><a id="rerank-fuse"></a><a id="rerankfuse"></a><a id="rerank-and-fuse"></a>

## 用 RRF 检索 {#rrf}

两个子查询各自按索引顺序取 100 个候选，`row_number()` 把顺序变成名次，外层查询把 RRF 分数加起来。`<&>` 返回取负的 BM25 分数，所以和距离一样，升序排列时最相关的排在最前。把下面的代码存为 `search.py`：

```python
import sys

import psycopg
from FlagEmbedding import BGEM3FlagModel
from pgvector.psycopg import register_vector

DB_URL = "postgresql://postgres@localhost:5432/postgres"

HYBRID_SQL = """
WITH semantic AS (
    SELECT id, row_number() OVER (ORDER BY distance) AS rank
    FROM (
        SELECT id, embedding <=> %(embedding)s AS distance
        FROM documents
        ORDER BY embedding <=> %(embedding)s
        LIMIT 100
    ) AS s
),
keyword AS (
    SELECT id, row_number() OVER (ORDER BY score) AS rank
    FROM (
        SELECT id, terms <&> to_bm25query(to_tsvector('english', %(query)s),
                                          'documents_terms_bm25'::regclass) AS score
        FROM documents
        ORDER BY terms <&> to_bm25query(to_tsvector('english', %(query)s),
                                        'documents_terms_bm25'::regclass)
        LIMIT 100
    ) AS k
)
SELECT id, content,
       coalesce(1.0 / (60 + semantic.rank), 0) + coalesce(1.0 / (60 + keyword.rank), 0) AS rrf
FROM semantic
FULL JOIN keyword USING (id)
JOIN documents USING (id)
ORDER BY rrf DESC
LIMIT %(limit)s
"""

model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)


def hybrid_search(conn, query, limit=10):
    embedding = model.encode([query])["dense_vecs"][0]
    params = {"embedding": embedding, "query": query, "limit": limit}
    return conn.execute(HYBRID_SQL, params).fetchall()


if __name__ == "__main__":
    with psycopg.connect(DB_URL) as conn:
        register_vector(conn)
        for doc_id, content, score in hybrid_search(conn, sys.argv[1]):
            print(f"{score:.4f}  {doc_id:>5}  {content[:80]}")
```

```bash
python search.py "Vitamin D deficiency increases the risk of multiple sclerosis"
```

想让某一路的权重更高，就在 `rrf` 表达式里给它那一项乘个系数，比如 `2 * coalesce(1.0 / (60 + keyword.rank), 0)`。

## 用交叉编码器重排 {#cross-encoder}

交叉编码器把查询和文档放在一起读，判断相关性比两种索引都准，代价是每个候选都要调用一次模型。先多取一些融合后的候选，再让它挑出前 10 条。把下面的代码加到 `search.py` 的 `if __name__` 块之前，并在该块里改为输出 `rerank(sys.argv[1], hybrid_search(conn, sys.argv[1], limit=100))` 的结果：

```python
from FlagEmbedding import FlagReranker

reranker = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=True)


def rerank(query, rows, limit=10):
    scores = reranker.compute_score([[query, content] for _, content, _ in rows], normalize=True)
    ranked = sorted(zip(rows, scores), key=lambda pair: pair[1], reverse=True)
    return [(doc_id, content, score) for (doc_id, content, _), score in ranked[:limit]]
```

## 用 pg_tokenizer 处理其他语言 {#pg-tokenizer}

`to_tsvector` 只支持 PostgreSQL 自带文本检索配置的那些语言。中文、日文或自定义的分词流程，改用 [pg_tokenizer](/zh/docs/tokenizer/) 1.3.0 生成 `tsvector`。它的 `analyze_to_tsvector` 要从目录表读取分析器定义，不能用在生成列里，所以改成普通列加触发器：

1. 安装 `pg_tokenizer`，加进 `shared_preload_libraries`，重启后创建分析器：

   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;

   SELECT tokenizer_catalog.create_text_analyzer('en_analyzer', $$
   pre_tokenizer = "unicode_segmentation"
   [[character_filters]]
   to_lowercase = {}
   [[token_filters]]
   stopwords = "nltk_english"
   [[token_filters]]
   stemmer = "english_porter2"
   $$);
   ```

   中文的话，整个配置只写 `[pre_tokenizer.jieba]` 一行即可。

1. `CREATE TABLE` 里把 `terms tsvector` 声明成普通列（去掉 `GENERATED ...`），用触发器维护它：

   ```sql
   CREATE FUNCTION documents_terms() RETURNS trigger LANGUAGE plpgsql AS $$
   BEGIN
       NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.content, 'en_analyzer');
       RETURN NEW;
   END
   $$;

   CREATE TRIGGER documents_terms BEFORE INSERT OR UPDATE OF content ON documents
   FOR EACH ROW EXECUTE FUNCTION documents_terms();
   ```

1. 查询文本也用同一个分析器处理：把 `HYBRID_SQL` 里两处 `to_tsvector('english', %(query)s)` 都换成 `tokenizer_catalog.analyze_to_tsvector(%(query)s, 'en_analyzer')`。
{.steps}

<a id="Evaluation"></a>

## BEIR 上的结果 {#evaluation}

[Hybrid Search with Postgres Native BM25 and VectorChord](/zh/blog/hybrid-search-with-postgres-native-bm25-and-vectorchord/)（2025 年 3 月）在四个 [BEIR](https://github.com/beir-cellar/beir) 数据集上测量了 NDCG@10，使用 BGE-M3 嵌入、BM25、RRF 和 `bge-reranker-v2-m3`。其中 BM25 用的是 Unicode 分词器而不是 `to_tsvector('english', ...)`，所以本教程的 BM25 结果会有些出入。

| 数据集 | 向量 | BM25 | RRF | 交叉编码器 |
| --- | --- | --- | --- | --- |
| FiQA-2018 | 0.40343 | 0.25301 | 0.37632 | **0.42706** |
| Quora | 0.88433 | 0.78687 | 0.87014 | **0.89069** |
| SCIDOCS | 0.16055 | 0.15584 | 0.17299 | **0.17942** |
| SciFact | 0.57631 | 0.68495 | 0.67855 | **0.74635** |
{.wide}

交叉编码器在每个数据集上都最好。RRF 只在 SCIDOCS 上同时超过两种单一方法，那里两者得分相近；在另外三个数据集上，它都低于较强的那一路。依赖 RRF 之前，先在自己的查询上测一测；如果某一路明显更强，就给它更高的权重。测试代码见 [xieydd/vectorchord-hybrid-search](https://github.com/xieydd/vectorchord-hybrid-search)。

<a id="future-work"></a><a id="References"></a><a id="references"></a>
