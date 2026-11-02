---
title: "借助 VectorChord-BM25 将搜索引擎级排序引入 PostgreSQL"
date: 2025-08-12
description: "现代应用依赖 PostgreSQL 完全符合 ACID 的事务特性、表达力丰富的 SQL 以及蓬勃发展的扩展生态。在关系型负载之外，VectorChord-BM25 将 BM25 相关性评分算法直接引入了 PostgreSQL。"
author: "[Zoie Wang](https://hashnode.com/@zoie) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/bringing-searchengine-ranking-to-postgresql-with-vectorchordbm25"
upstream_copyright: "© 2025 Zoie Wang (TensorChord Inc.)"
aliases:
  - "/blog/bringing-searchengine-ranking-to-postgresql-with-vectorchordbm25/"
  - "/bringing-searchengine-ranking-to-postgresql-with-vectorchordbm25/"
authors: ["zoie-wang"]
images: ["/blog/covers/bringing-searchengine-ranking-to-postgresql-with-vectorchordbm25.png"]
---

现代应用普遍依赖 PostgreSQL 完全符合 ACID 的事务特性、表达力丰富的 SQL 以及繁荣的扩展生态系统。虽然 PostgreSQL 在处理关系型负载方面表现得无与伦比，但许多项目同样需要在庞大的文本集合（如商品描述、客服工单、技术文档）中进行搜索，并将最相关的行优先呈现给用户。PostgreSQL 的原生工具为此提供了一定基础，但其默认的排序逻辑往往会让最理想的匹配结果被淹没在不太有用的结果之下。VectorChord‑BM25 通过将 BM25 相关性评分算法直接引入 PostgreSQL，彻底改变了这一局面。

## 什么是 PostgreSQL？ {#what-is-postgresql}

PostgreSQL 是一款开源的企业级关系型数据库管理系统（RDBMS），以高可靠性、数据完整性和标准合规性而闻名。它支持窗口函数、物化视图、JSONB 存储等高级特性，并拥有强大的扩展机制，允许开发者按需扩展新功能。点击[此处](https://www.postgresql.org/)了解更多关于 PostgreSQL 的信息。

<a id="full-text-search-with-tsvector"></a>
## 基于 `tsvector` 的全文搜索 {#full-text-search-with-tsvector}

PostgreSQL 内置了名为 `tsvector` 的基础文本搜索工具。你可以把它想象成一种特殊的列，以数据库能够快速检索的格式存储每篇文档中的重要词汇（词位，lexemes）。当你在该列上添加 GIN 或 GiST 索引后，PostgreSQL 几乎可以瞬间找到匹配某个关键词的行。你可以使用 `@@` 操作符编写搜索查询，完整细节可参阅 PostgreSQL 手册的[这一章节](https://www.postgresql.org/docs/current/datatype-textsearch.html)。

### 原生排序的不足之处 {#where-native-ranking-falls-short}

虽然 `ts_rank` 函数可以对匹配结果进行排序，但它的评分方法非常基础。仅提及一次某词汇的长篇文档，其排名可能会高于完全围绕该查询主题展开的短篇文档；而且罕见但重要的关键词也几乎没有额外的权重加成。在大规模数据集中，这往往会导致搜索结果的实际感知相关性大打折扣。

<a id="what-s-new-vectorchord-adds-bm25"></a>
## 全新突破：VectorChord 引入 BM25 {#whats-new-vectorchord-adds-bm25}

VectorChord‑BM25 是一款轻量级的 PostgreSQL 扩展，它使用行业标准的 BM25 排序公式增强了现有的文本搜索技术栈。你无需将数据导出到外部搜索引擎，而是可以把所有数据留在单一数据库内部，同时获得以下优势：

* 奖励高区分度词汇并惩罚冗长无关内容的精准排序
    
* 索引内评分（In-index scoring），显著降低查询延迟
    
* 无缝的 SQL 工作流——文档依然是表中的行，搜索依然是标准的 SQL 查询
    

## 什么是 BM25？ {#what-is-bm25}

BM25（Best Matching 25）是一种被搜索引擎和学术界广泛采用的概率检索模型。它综合评估查询词在文档中出现的频率、该词在整个语料库中的罕见程度，以及每篇文档的长度。关于该算法的详细讨论可参见其[维基百科页面](https://en.wikipedia.org/wiki/Okapi_BM25#:~:text=BM25%20is%20a%20bag%2Dof,slightly%20different%20components%20and%20parameters.)，但其核心思想非常直观：

* **词频（Term Frequency, TF）**——某个词在文档中出现的次数越多，相关性越高，但边际收益递减。
    
* **逆文档频率（Inverse Document Frequency, IDF）**——罕见词比常见词包含更多有效信息。
    
* **文档长度归一化（Document Length Normalisation）**——聚焦于查询主题的短文档不会因为篇幅短而受到不公平的惩罚。
    

VectorChord 通过全新的索引类型和操作符（`<&>`）实现了 BM25，使 PostgreSQL 能够在扫描索引的同时直接计算出相关性得分。

---

## 两个实用示例 {#two-practical-examples}

下面通过两个简明的演示，展示如何结合预训练分词器使用 VectorChord‑BM25，以及如何针对特定专业领域使用自定义模型。

<a id="example-1-quick-start-with-a-pre-trained-model"></a>
### 示例 1：使用预训练模型快速上手 {#example-1-quick-start-with-a-pre-trained-model}

```Bash
# Spin up a pre‑configured PostgreSQL instance
docker run --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg17-latest
```

```SQL
-- Inside psql
CREATE EXTENSION pg_tokenizer CASCADE;
CREATE EXTENSION vchord_bm25  CASCADE;

-- Register the LLMLingua‑2 tokenizer
SELECT create_tokenizer('llm_tok', $$ model = "llmlingua2" $$);

CREATE TABLE articles (
    id   SERIAL PRIMARY KEY,
    body TEXT,
    emb  bm25vector
);

INSERT INTO articles(body) VALUES
('PostgreSQL is a powerful open‑source database system.'),
('BM25 is a ranking function used by search engines.');

-- Tokenise each row
UPDATE articles SET emb = tokenize(body, 'llm_tok');

-- Build the BM25 index
CREATE INDEX articles_emb_bm25 ON articles USING bm25 (emb bm25_ops);

-- Query with relevance ordering
SELECT id,
       body,
       emb <&> to_bm25query('articles_emb_bm25',
                            tokenize('open source database', 'llm_tok')) AS score
FROM   articles
ORDER  BY score         -- lower (more negative) = higher relevance
LIMIT  10;
```

该查询直接返回按 BM25 排好序的行，呈现出比默认 `ts_rank` 更符合直觉的结果。

<a id="example-2-custom-model-for-domain-specific-vocabulary"></a>
### 示例 2：面向领域特定词汇表的自定义模型 {#example-2-custom-model-for-domain-specific-vocabulary}

特定领域的文本——如医疗记录、法律文书、技术日志——通常包含通用模型中缺失的专业术语。VectorChord 允许你直接在 SQL 中训练自定义分词器。

```SQL
-- 1. Create a text analyzer with Unicode segmentation, lowercasing,
--    stop‑word removal, and stemming.
SELECT create_text_analyzer('tech_analyzer', $$
pre_tokenizer = "unicode_segmentation"
[[character_filters]]
to_lowercase = {}
[[token_filters]]
stopwords = "nltk_english"
[[token_filters]]
stemmer = "english_porter2"
$$);

-- 2. Train a model on your own corpus and set up automatic embedding
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'tech_tok',
    model_name         => 'tech_model',
    text_analyzer_name => 'tech_analyzer',
    table_name         => 'tickets',
    source_column      => 'issue_text',
    target_column      => 'embedding');

-- 3. Insert support tickets; embeddings are generated via trigger
INSERT INTO tickets(issue_text)
VALUES ('Kubernetes pod fails with ExitCode 137 after OOM kill.'),
       ('Network latency spikes to 250ms during peak hours.');

-- 4. Build an index and query as before
CREATE INDEX tickets_emb_bm25 ON tickets USING bm25 (embedding bm25_ops);

SELECT issue_text,
       embedding <&> to_bm25query('tickets_emb_bm25',
                                  tokenize('OOM kill ExitCode 137', 'tech_tok')) AS score
FROM   tickets
ORDER  BY score
LIMIT  5;
```

借助量身定制的词汇表，数据库能够准确识别“OOM”和“Kubernetes”等专有缩写与术语，从而为技术支持工单场景提供更加精准的排序结果。

## 结语 {#final-thoughts}

VectorChord‑BM25 在不引入额外服务层的前提下，将搜索引擎级别的相关性排序带入了 PostgreSQL 生态系统。通过将灵活的分词器、高效的 BM25 索引以及熟悉的 SQL 相结合，它让开发者能够在保持单一数据库系统运维简洁性的同时，交付显著更优的搜索体验。如果你的应用基于 PostgreSQL 构建且需要精准的文本排序，VectorChord‑BM25 绝对值得一试。
