---
title: "用 ColQwen2 与 Modal 做文档图像检索"
linkTitle: "ColQwen2 与 Modal"
description: "不做 OCR，直接按页面图像检索文档：在 Modal GPU 上用 ColQwen2 生成页面嵌入，用 vchordrq 为图块向量建索引，再按 MaxSim 给页面排序。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/use-case/colqwen2-modal.md"
aliases:
  - "/docs/use-case/colqwen2-modal/"
  - "/vectorchord/use-case/colqwen2-modal/"
icon: fa-solid fa-file-image
---

本教程在 ViDoRe 基准的页面图像上搭建一个检索：输入一个文字问题，返回能回答它的页面，全程不做 OCR。OCR 流程会丢掉文字提取抓不住的东西，比如表格、图表和版式；ColQwen2 则把每张渲染好的页面编码成一组 128 维向量，每个图像块一条，查询的词元向量直接与它们匹配。vchord 用 `vector_maxsim_ops` 为这些向量数组建索引，用 `@#` 运算符按 MaxSim 给页面排序；计算嵌入用的 GPU 由 [Modal](https://modal.com/) 提供。

<a id="what-is-colqwen2-the-power-of-visual-understanding"></a>

## 工作原理 {#how-does-vectorchord-enable-colqwen2-in-postgres}

[ColPali](https://arxiv.org/abs/2407.01449) 用视觉语言模型编码页面图像，每个图像块保留一条向量；[ColQwen2](https://huggingface.co/vidore/colqwen2-v1.0) 做法相同，模型换成了 Qwen2-VL-2B。文字查询则每个词元一条向量。页面得分是 MaxSim：对每条查询向量，取它与该页所有向量内积的最大值，再把这些最大值相加。

集合一大，逐页这样打分就太慢了。用 `vector_maxsim_ops` 建的 `vchordrq` 索引把每个页面的每条图块向量都放进列表。查询时，每条查询向量各自探查列表，把找到的向量按页面累加得分；某条查询向量在某页上一条都没找到时，就估算它对该页的贡献，这个做法借鉴自 [WARP](https://arxiv.org/abs/2501.17788)。`vchordrq.maxsim_refine` 和 `vchordrq.maxsim_threshold` 以更多计算换取更准的估算，定义见[多向量检索](/zh/docs/vchord/usage/multi-vector-retrieval/)。

<a id="tutorial-building-your-ocr-free-rag-system"></a><a id="Prerequisites"></a>

## 准备工作 {#prerequisites}

- PostgreSQL 15–19，按[概览](/zh/docs/vchord/getting-started/overview/)装好并预加载 vchord 1.5.0。
- 一个 [Modal](https://modal.com/) 账号。生成嵌入那一步用一块 H100。
- 配套仓库，以及生成嵌入和导入数据所需的 Python 包：

  ```bash
  git clone https://github.com/xieydd/vectorchord-colqwen2
  cd vectorchord-colqwen2/modal
  pip install modal fastapi msgspec datasets numpy "psycopg[binary]" pgvector
  python3 -m modal setup
  ```

## 建立索引 {#build}

1. <a id="step-1-load-the-data-using-modal-volumes"></a>把 ViDoRe 基准下载到 Modal 卷里。`dataset.py` 把 [ViDoRe 集合](https://huggingface.co/collections/vidore/vidore-benchmark-667173f98e70a1c0fa4db00d)中的每个数据集存进 `colpali-dataset` 卷，每张页面图像只保留一行：

   ```bash
   modal run dataset.py::download_dataset
   ```

1. <a id="step-2-process-data--generate-embeddings-with-modal--colqwen2"></a><a id="step-2-generate-embeddings"></a>为页面和问题生成嵌入。`embedding.py` 在 Modal GPU 上运行 `vidore/colqwen2-v1.0`，每处理完一批就往 `colpali-embedding-checkpoint` 卷写一次检查点，中断后可以接着跑；最后为每个 ViDoRe 数据集保存一份数据，内含每页的图块向量和对应问题的词元向量。把结果拷到本机：

   ```bash
   modal run embedding.py::embed_dataset
   modal volume get colpali-embedding-checkpoint / embeddings
   ```

1. <a id="step-3-create-index-in-vectorchord-using-vechord-sdk"></a>建表。每行是一张页面，以及 ViDoRe 为它配的问题：

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;

   CREATE TABLE pages (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       dataset text NOT NULL,
       dataset_id int NOT NULL,
       query text,
       image_embedding vector(128)[] NOT NULL,
       query_embedding vector(128)[] NOT NULL
   );
   ```

1. 导入嵌入。把下面的代码存为 `load.py`，执行 `python load.py embeddings`：

   ```python
   import sys
   from pathlib import Path

   import numpy as np
   import psycopg
   from datasets import load_from_disk
   from pgvector.psycopg import register_vector

   DB_URL = "postgresql://postgres@localhost:5432/postgres"


   def vectors(buffer, shape):
       return list(np.frombuffer(buffer, dtype=np.float32).reshape(shape))


   with psycopg.connect(DB_URL) as conn:
       register_vector(conn)
       with conn.cursor() as cur:
           for info in sorted(Path(sys.argv[1]).rglob("dataset_info.json")):
               path = info.parent
               dataset = f"{path.parent.name}/{path.name}"
               for item in load_from_disk(str(path)):
                   cur.execute(
                       "INSERT INTO pages (dataset, dataset_id, query, image_embedding, query_embedding)"
                       " VALUES (%s, %s, %s, %s, %s)",
                       (
                           dataset,
                           item["id"],
                           item["query"],
                           vectors(item["image_embedding"], item["image_embedding_shape"]),
                           vectors(item["query_embedding"], item["query_embedding_shape"]),
                       ),
                   )
   ```

1. 建 MaxSim 索引。索引会把每条图块向量单独存放，所以 `lists` 要按图块向量的总数而不是页面数来定，见 [vchordrq 索引](/zh/docs/vchord/usage/indexing/#lists)。配套仓库用的是 2,500 个列表：

   ```sql
   CREATE INDEX pages_image_embedding_idx ON pages
   USING vchordrq (image_embedding vector_maxsim_ops)
   WITH (options = $$
   [build.internal]
   lists = [2500]
   spherical_centroids = true
   build_threads = 8
   $$);
   ```
{.steps}

## 检索 {#search}

检索就是按 `@#` 与查询词元向量的结果给页面排序。下面的参数取自配套仓库的评测：

```sql
SET vchordrq.probes = '16';
SET vchordrq.epsilon = 1.0;
SET vchordrq.maxsim_refine = 10;
SET vchordrq.maxsim_threshold = 2000;

SELECT p.dataset, p.dataset_id
FROM pages AS p
ORDER BY p.image_embedding @# (SELECT query_embedding FROM pages WHERE id = 1)
LIMIT 10;
```

在应用里，用同一个 ColQwen2 模型编码问题，把得到的词元向量作为 `vector[]` 参数传入，替换掉这里的子查询。

<a id="step-4-evaluation-does-it-work"></a><a id="step-4-evaluation---does-it-work"></a><a id="step-4-evaluation"></a>

## 评测 {#evaluate}

ViDoRe 中每个问题对应一张页面，所以返回结果里出现问题自己那一行，就算答对。下面的查询在 [`vidore/arxivqa_test_subsampled`](https://huggingface.co/datasets/vidore/arxivqa_test_subsampled)（科学论文中的图和图表）的 100 个问题上计算 NDCG@10 和 recall@10。打开 `\timing on` 运行，就能比较不同参数的耗时：

```sql
WITH questions AS MATERIALIZED (
    SELECT id, query_embedding
    FROM pages
    WHERE dataset = 'vidore/arxivqa_test_subsampled'
    ORDER BY id
    LIMIT 100
),
ranks AS (
    SELECT array_position(
        ARRAY(
            SELECT p.id
            FROM pages AS p
            ORDER BY p.image_embedding @# q.query_embedding
            LIMIT 10
        ),
        q.id
    ) AS rank
    FROM questions AS q
)
SELECT round(avg(coalesce(1 / log(2, rank + 1), 0)), 4) AS ndcg_at_10,
       round(avg((rank IS NOT NULL)::int), 4) AS recall_at_10
FROM ranks;
```

## 测试结果 {#results}

[Beyond Text: Unlock OCR-Free RAG in PostgreSQL with Modal & VectorChord](/zh/blog/beyond-text-unlock-ocr-free-rag-in-postgresql-with-modal-and-vectorchord/)（2025 年 4 月）在开启和关闭 vchord 的 MaxSim 剪枝两种情况下跑了这项评测：

| | NDCG@10 | Recall@10 | 100 个问题的耗时 |
| --- | --- | --- | --- |
| 不剪枝 | 0.8615 | 0.92 | 810 秒 |
| 剪枝 | 0.8353 | 0.90 | 41 秒 |

剪枝让评测快了约 20 倍，NDCG@10 降低 0.026，recall@10 降低 0.02。文章说明这些耗时来自一套较慢的本地环境，所以看比例，不要看绝对时间。

<a id="conclusion-visual-rag-made-simpler-in-postgres"></a><a id="References"></a><a id="references"></a>
