---
title: "VectorChord-BM25: Revolutionize PostgreSQL Search with BM25 Ranking — 3x Faster Than ElasticSearch"
date: 2025-02-24
description: "VectorChord-BM25 enhances PostgreSQL search with BM25 ranking, 3x faster than ElasticSearch. Supports BERT, Tocken, and Unicode tokenizers"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch"
upstream_copyright: "© 2025 Jinjing Zhou (TensorChord Inc.)"
math: true
aliases:
  - "/blog/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/"
  - "/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/"
---

We’re excited to share something special with you: **VectorChord-BM25**, a new extension designed to make PostgreSQL’s full-text search even better. Whether you’re building a small app or managing a large-scale system, this tool brings advanced BM25 scoring and ranking right into PostgreSQL, making your searches smarter and faster.

<a id="what-s-new"></a>
### **What’s New?**

* **BM25 Scoring & Ranking**: Get more precise and relevant search results with BM25, helping you find what matters most.
    
* **Optimized Indexing**: Thanks to the Block WeakAnd algorithm, searches are quicker and more efficient, even with large datasets.
    
* **Enhanced Tokenization**: Improved stemming and stop word handling mean better accuracy and smoother performance.
    

We built VectorChord-BM25 to be simple, powerful, and fully integrated with PostgreSQL—because we believe great tools should make your life easier, not more complicated. We hope you’ll give it a try and let us know what you think.

%[https://github.com/tensorchord/VectorChord-BM25] 

<a id="BM25"></a>
## BM25

Before we get to the exciting news, let’s take a quick look at **BM25**, the algorithm that powers modern search engines. BM25 is a probabilistic ranking function that determines how relevant a document is to a search query.

The BM25 formula might look a bit intimidating at first, but let’s break it down step by step to make it easy to understand. Here’s it:


$$
\text{score}(Q, D) = \sum_{q \in Q} \text{IDF}(q) \cdot \frac{f(q, D) \, (k_1 + 1)}{f(q, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
$$


**Term Frequency (TF)**: The term f(q,D) represents how often the query term *q* appears in document *D*. The more a term appears in a document, the higher its relevance score. For example, if "AI" appears 5 times in Document A and 2 times in Document B, Document A gets a higher score for this term.

**Inverse Document Frequency (IDF)**: The term IDF(q) measures how rare or common the term *q* is across all documents. Rare terms (e.g., "NVIDIA") are given more weight than common terms (e.g., "revenue"). This ensures that unique terms have a greater impact on the relevance score.

**Document Length Normalization**: The term ∣*D*∣ represents the length of document *D*, while avgdl is the average length of all documents in the collection. This part of the formula adjusts the score to account for document length, ensuring shorter documents aren’t unfairly penalized. For instance, a concise report won’t be overshadowed by a lengthy one that only briefly mentions the query term.

**Tuning Parameters**: The parameters *k*1 and *b* allow the formula to be fine-tuned. *k*1 controls the extent to which term frequency impacts the score, while *b* balances the effect of document length normalization. These parameters can be adjusted to optimize results for specific datasets.

Consider searching a database of financial reports for "Tesla stock performance." A report that mentions "Tesla" ten times will score higher than one that mentions it only twice. However, the term "stock" might appear in many reports, so it’s given less weight than "Tesla," which is more specific. Furthermore, a short, concise report about Tesla’s stock performance won’t be overshadowed by a lengthy report that only briefly mentions Tesla.

## Existing Solution in Postgres

Now that we’ve covered the basics, let’s take a look at the existing solutions for full-text search in PostgreSQL.

PostgreSQL provides built-in support for full-text search through the combination of the `tsvector` data type and GIN (Generalized Inverted Index) indexes. Here’s how it works: text is first converted into a `tsvector`, which tokenizes the content into lexemes—standardized word forms that make searching more efficient. A GIN index is then created on the `tsvector` column, significantly speeding up query performance and enabling fast retrieval of relevant documents, even when dealing with large text fields. This integration of text processing and advanced indexing makes PostgreSQL a powerful and scalable solution for applications that require efficient full-text search.

```sql
-- Create a table with a text column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    content_vector tsvector
);

-- Insert sample data with tsvector conversion
INSERT INTO documents (content, content_vector) VALUES
('PostgreSQL is a powerful, open-source database system.', to_tsvector(...)),
('Full-text search in PostgreSQL is efficient and scalable.', to_tsvector(...)),
('BM25 is a ranking function used by search engines.', to_tsvector(...));

-- Create a GIN index on the tsvector column
CREATE INDEX idx_content_vector ON documents USING GIN (content_vector);

-- Query using tsvector, rank results with ts_rank, and leverage the GIN index
SELECT id, content, ts_rank(content_vector, to_tsquery('english', 'PostgreSQL & search')) AS rank
FROM documents
WHERE content_vector @@ to_tsquery('english', 'PostgreSQL & search')
ORDER BY rank DESC;
```

However, PostgreSQL has a limitation: it lacks modern relevance scoring mechanisms like BM25. Instead, it returns all matching documents and relies on `ts_rank` to re-rank them, which can be inefficient. This makes it challenging for users to quickly identify the most important results, especially when dealing with large datasets.

Another solution is ParadeDB, which pushes full-text search queries down to Tantivy for results. It supports BM25 scoring and complex query patterns like negative terms, aiming to be a complete replacement for ElasticSearch. However, it uses its own unique syntax for filtering and querying and delegates filtering operations to Tantivy instead of relying on Postgres directly. Its implementation requires several hooks into Postgres' query planning and storage, potentially leading to compatibility issues.

In contrast, VectorChord-BM25 takes a different approach. It focuses exclusively on bringing BM25 ranking to PostgreSQL in a lightweight and native way. We implemented the BM25 ranking algorithm and the Block WeakAnd technique from scratch, building it as a custom operator and index (similar to `pgvector`) to accelerate queries. Designed to be intuitive and efficient, VectorChord-BM25 **provides a seamless API for enhanced full-text search and ranking, all while staying fully integrated with PostgreSQL’s ecosystem**.

## VectorChord-BM25

Our implementation introduces a novel approach by developing the BM25 index and search algorithm from the ground up, while seamlessly integrating with PostgreSQL’s existing development interfaces to ensure maximum compatibility.

Inspired by the PISA engine, Tantivy, and Lucene, we incorporated the BlockMax WeakAnd algorithm to facilitate efficient score-based filtering and ranking. Furthermore, we employ bitpacking for ID compression to enhance overall efficiency and re-implemented a user data-based tokenizer to more closely align with ElasticSearch’s performance.

The table below compares the **Top1000 Queries Per Second (QPS)**—a metric that measures how many queries a system can process per second while retrieving the top 1000 results for each query—between our implementation and ElasticSearch across various datasets from [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks):

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740189817247/5a81c020-1aa2-452d-8e8d-b9653c5b3489.png)

On average, our implementation achieves **3 times higher QPS** compared to ElasticSearch across the tested datasets, showcasing its efficiency and scalability. However, speed alone isn’t sufficient—we also prioritize accuracy. To ensure relevance, we evaluated **NDCG@10 (Normalized Discounted Cumulative Gain at 10)**, a key metric for assessing ranking quality.

> [!TIP]
> **NDCG@10** (Normalized Discounted Cumulative Gain at rank 10) is a metric that assesses the relevance of documents within the top 10 positions of a ranked list. It emphasizes not only the relevance of each document but also its position, ensuring higher-ranked relevant documents contribute more to the overall score.

The table below compares the NDCG@10 scores between VectorChord-BM25 and ElasticSearch across various datasets:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190423528/10f75122-34fc-4fa2-bb66-3e26e09516ec.png)

We have dedicated substantial effort to align VectorChord-BM25 with ElasticSearch’s behavior, ensuring a fair and precise comparison. As demonstrated in the table, our implementation achieves NDCG@10 scores that are comparable across most datasets, with certain cases even surpassing ElasticSearch (e.g., trec-covid and scifact).

We’ll share the technical details of our alignment efforts in a later section, including how we addressed tokenization, scoring, and other critical components to achieve these results. Before that, let’s explore how to use VectorChord-BM25 in PostgreSQL.

## Quick start

To get started with VectorChord-BM25, we’ve put together a detailed guide in our [GitHub README](https://github.com/tensorchord/VectorChord-bm25/) that walks you through the installation and configuration process. Below, you’ll find a complete example showing how to use VectorChord-BM25 for BM25 full-text search in Postgres. Each SQL snippet comes with a clear explanation of what it does and why it’s useful.

The extension consists of three main components:

* **Tokenizer**: Converts text into a bm25vector, which is similar to a sparse vector that stores vocabulary IDs and their frequencies.
    
* **bm25vector**: Represents the tokenized text in a format suitable for BM25 scoring.
    
* **bm25vector Index**: Speeds up the search and ranking process, making it more efficient.
    

If you’d like to tokenize some text, you can use the `tokenize` function. It takes two arguments: the text you want to tokenize and the name of the tokenizer.

```sql
-- tokenize text with bert tokenizer
SELECT tokenize('A quick brown fox jumps over the lazy dog.', 'Bert');
-- Output: {2474:1, 2829:1, 3899:1, 4248:1, 4419:1, 5376:1, 5831:1}
-- The output is a bm25vector, 2474:1 means the word with id 2474 appears once in the text.
```

One unique aspect of the BM25 score is that it relies on a global document frequency. This means the score of a word in a document is influenced by how frequently that word appears across all documents in the set. To calculate the BM25 score between a bm25vector and a query, you’ll first need a document set. Once that’s in place, you can use the `<&>` operator to perform the calculation.

Here is an example step by step. First, create a table and insert some documents:

```sql
-- Setup the document table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

INSERT INTO documents (passage) VALUES
('PostgreSQL is a powerful, open-source object-relational database system. It has over 15 years of active development.'),
('Full-text search is a technique for searching in plain-text documents or textual database fields. PostgreSQL supports this with tsvector.'),
...
('Effective search ranking algorithms, such as BM25, improve search results by understanding relevance.');
```

Then tokenize it

```sql
UPDATE documents SET embedding = tokenize(passage, 'Bert');
```

Create the index on the bm25vector column so that we can collect the global document frequency.

```sql
CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);
```

Now we can compute the BM25 score between the query and the vectors. It’s worth noting that the BM25 score is negative—this is by design. A higher (less negative) score indicates a more relevant document. We intentionally made the score negative so that you can use the default `ORDER BY` clause to easily retrieve the most relevant documents first.

```sql
SELECT id, passage, embedding <&> to_bm25query('documents_embedding_bm25', 'PostgreSQL', 'Bert') AS rank
FROM documents
ORDER BY rank
LIMIT 10;
```

### Other Tokenizers

In addition to BERT, VectorChord-BM25 also supports `Tocken` and `Unicode` Tokenizers. `Tocken` is a Unicode tokenizer pre-trained on the `wiki-103-raw` dataset with a minimum frequency (`min_freq`) of 10. Since it’s a pre-trained tokenizer, you can use it similarly to BERT.

```sql
SELECT tokenize('A quick brown fox jumps over the lazy dog.', 'Tocken');
```

`Unicode` is a tokenizer that builds a vocabulary list from your data, similar to the standard behavior in Elasticsearch and other full-text search engines. To enable this, you need to create a specific one for your data using `create_unicode_tokenizer_and_trigger(vocab_list_name, table_name, source_text_column, tokenized_vec_column)`.

```sql
CREATE TABLE documents (id SERIAL, text TEXT, embedding bm25vector);
SELECT create_unicode_tokenizer_and_trigger('test_token', 'documents', 'text', 'embedding');

INSERT INTO documents (text) VALUES ('PostgreSQL is a powerful, open-source object-relational database system.');
CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);
SELECT id, text, embedding <&> to_bm25query('documents_embedding_bm25', 'PostgreSQL', 'test_token') AS rank
    FROM documents
    ORDER BY rank
    LIMIT 10;
```

Please check out the [tokenizer documentation](/docs/tokenizer/) if you want to know more about it.

## Faster than ElasticSearch (Really?)

![math Memes & GIFs - Imgflip](https://i.imgflip.com/6b4xz9.jpg)

To ensure our new plugin provides meaningful and relevant results—not just faster performance—we rigorously evaluated VectorChord-BM25 using [bm25-benchmarks](https://github.com/xhluca/bm25-benchmarks). We leveraged the widely recognized BEIR benchmark for information retrieval, focusing on two key metrics: **QPS (Queries Per Second)** to measure speed and **NDCG@10 (Normalized Discounted Cumulative Gain at 10)** to assess relevance and ranking accuracy.

In our initial version, we were thrilled to see our system achieve **3-5 times higher QPS** compared to ElasticSearch. However, we also noticed that on certain datasets, our NDCG@10 scores were significantly lower than ElasticSearch’s. After a thorough analysis, we realized these gaps weren’t caused by our indexing implementation but rather by differences in tokenization approaches.

To address this, we invested considerable effort to align our tokenization process with ElasticSearch’s, ensuring a more accurate and fair comparison.

### Issue 1: Stopword List

> [!TIP]
> A **stopword** is a common word filtered out during text processing because it adds little meaning—for example, words like "the," "is," and "at."

ElasticSearch defaults to using Lucene’s Standard Tokenizer, which relies on a relatively short stopword list. In contrast, our initial implementation utilized NLTK’s much more comprehensive stopword list. As a result, ElasticSearch’s searches include certain stopwords, leading to longer inverted index lists that require additional scanning time—ultimately impacting performance.

### Issue 2: Stemming

> [!TIP]
> A **stemmer** reduces words to their base form, "running" and "ran" both become "run."

We initially used the **snowball stemmer** from the rust-stemmer library to handle word variations, but we observed discrepancies compared to ElasticSearch’s implementation. Upon investigation, we discovered that the rust-stemmer’s version of snowball was outdated. Following the guidelines from the official snowball repository, we regenerated the files using the latest version.

When we aligned both the **stopword list** and **stemmer** between our system and ElasticSearch, our performance advantage decreased from **300% to 40%**. Even so, on three datasets—nq, fever, and climate-fever—a noticeable performance gap persisted. A deeper comparison revealed a subtle but critical detail: in the bm25-benchmark, ElasticSearch preprocesses data differently from other frameworks, which contributed to the remaining discrepancy.

### Issue 3: Data Preprocessing

In the BEIR dataset, each document includes both a title and a text field. While most frameworks concatenate these fields into a single string for indexing, ElasticSearch accepts JSON input and indexes the title and text separately. During querying, ElasticSearch performs a multi\_match operation, searching both fields independently and combining their scores (using the higher score plus 0.5 times the lower score). This approach yields significantly better NDCG@10 results but requires searching two separate indexes, which can substantially impact performance.

To ensure a fair comparison, we re-ran our ElasticSearch tests by concatenating the title and text fields. With this adjustment, VectorChord-BM25 was able to match ElasticSearch’s results. Interestingly, ElasticSearch’s **QPS (geometric mean)** increased from **135 to 341** when using concatenated fields, making it **25% faster** than VectorChord-BM25’s **271.91 QPS** in Top10 query tests. However, in Top1000 tests, VectorChord-BM25 achieved a QPS of **112** compared to ElasticSearch’s **49**—making our implementation **2.26 times faster**.

This experience highlights the challenges of conducting fair performance comparisons between different BM25 full-text search implementations. The **tokenizer** is an exceptionally complex and influential component, and ElasticSearch’s intricate default settings add another layer of complexity to the evaluation process.

<a id="Future"></a>
## Future

We’re still in the early stages of this project, and we’ve already pinpointed several areas for performance optimization. Tokenization is an inherently complex process—even for English, we face numerous decisions and trade-offs. Our next step is to **fully decouple the tokenization process**, transforming it into an independent and extensible extension. This will enable us to support multiple languages, allow users to customize tokenization for better results, and even incorporate advanced features like synonym handling.

Our ultimate goal is to empower users to perform **high-quality, relevance-based full-text searches** on PostgreSQL with ease. Combined with [**VectorChord**](https://github.com/tensorchord/VectorChord/), we aim to deliver a **first-class data infrastructure for RAG (Retrieval-Augmented Generation)**. After all, choosing PostgreSQL is always a solid decision!

If you have any questions about vector search or full-text search in PostgreSQL, feel free to reach out to us! You can connect with us at:

* Discord: [https://discord.gg/KqswhpVgdU](https://discord.gg/KqswhpVgdU)
    
* Email: [vectorchord-inquery@tensorchord.ai](mailto:vectorchord-inquery@tensorchord.ai)
    

%[https://github.com/tensorchord/VectorChord-bm25] 

## More Benchmarks

In addition to the Top1000 benchmarks, we have also conducted extensive evaluations for Top10 results. These benchmarks provide further insights into the performance of our implementation across different datasets. If you’re interested in exploring these results in detail, feel free to refer to the data provided here.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190947932/67305460-724d-4dc5-aa7f-606a6ceb13cb.png)

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1740190965658/ca72272a-49af-43f8-87b7-16d14b383e8a.png)
