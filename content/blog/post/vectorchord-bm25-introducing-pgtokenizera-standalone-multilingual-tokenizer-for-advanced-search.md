---
title: "VectorChord-BM25: Introducing pg_tokenizer—A Standalone, Multilingual Tokenizer for Advanced Search"
date: 2025-04-02
description: "We're excited to announce the release of VectorChord-BM25 version 0.2, our PostgreSQL extension designed to bring advanced BM25-based full-text search…"
author: "Jinjing Zhou"
tags:
  - "vector-database"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search"
aliases:
  - "/blog/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/"
  - "/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/"
---

We're excited to announce the release of **VectorChord-BM25 version 0.2**, our PostgreSQL extension designed to bring advanced BM25-based full-text search ranking capabilities directly into your database!

VectorChord-BM25 allows you to leverage the power of the BM25 algorithm, a standard in information retrieval, without needing external search engines. This release marks a significant step forward, focusing heavily on enhancing the core text processing component: **tokenization**, unlocking greater flexibility and **significantly improved multilingual support**.

<a id="the-big-news-introducing-pg-tokenizer-rs"></a>
### The Big News: Introducing `pg_tokenizer.rs`

The cornerstone of VectorChord-BM25 0.2 is a **completely refactored and decoupled tokenizer extension:** `pg_tokenizer.rs`.

Why the change? We realized that tokenization – the process of breaking down text into meaningful units (tokens) – is incredibly complex and highly dependent on the specific language and use case. Supporting multiple languages with their unique rules, custom dictionaries, stemming, stop words, and different tokenization strategies within a single monolithic extension was becoming cumbersome.

By moving the tokenizer into its own dedicated project (`pg_tokenizer.rs`) under the permissive **Apache License**, we achieve several key benefits:

1. **Modularity & Flexibility:** Developers can now use or customize the tokenizer independently of the core BM25 ranking logic.
    
2. **Easier Contribution:** The focused nature of `pg_tokenizer.rs` makes it simpler for the community to contribute **new language support**, tokenization techniques, or custom filters.
    
3. **Faster Iteration:** We can now develop and release improvements to the tokenizer more rapidly without needing a full VectorChord-BM25 release cycle.
    
4. **Enhanced Customization:** Users gain significantly more control over how their text, **regardless of language**, is processed before ranking.
    

<a id="what-s-new-in-tokenization-thanks-to-pg-tokenizer-rs"></a>
### What's New in Tokenization (Thanks to `pg_tokenizer.rs`)

This new architecture enables several powerful features in v0.2:

* **Expanded Language Support:** Directly handle diverse linguistic needs with dedicated tokenizers like **Jieba (Chinese)** and **Lindera (Japanese)**, alongside powerful **multilingual LLM-based tokenizers** (like **Gemma2** and **LLMLingua2**) trained on vast datasets covering a wide array of languages.
    
* **Richer Tokenization Features:** You now have more granular control over the tokenization pipeline:
    
    * **Custom Stop Words:** Define your own lists of words to ignore during indexing and search.
        
    * **Custom Stemmers:** Apply stemming rules for various supported languages or even define custom ones.
        
    * **Custom Synonyms:** Define synonym lists to treat different words as equivalent (e.g., "postgres", "postgresql", "pgsql").
        
    * **Language-Specific Options:** Leverage fine-grained controls available within specific tokenizers (like Lindera or Jieba) when needed.
        

### Show Me the Code!

Let's see how easy it is to use the new tokenizer features.

**1\. Using a Pre-trained Multilingual LLM Tokenizer (LLMLingua2)**

LLM-based tokenizers are great for handling text from many different languages.

```sql
-- Enable the extensions (if not already done)
CREATE EXTENSION IF NOT EXISTS vchord_bm25;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;

-- Update search_path for the first time
ALTER SYSTEM SET search_path TO "$user", public, tokenizer_catalog, bm25_catalog;
SELECT pg_reload_conf();

-- Create a tokenizer configuration using the LLMLingua2 model
SELECT create_tokenizer('llm_tokenizer', $$
model = "llmlingua2"
$$);

-- Tokenize some English text
SELECT tokenize('PostgreSQL is a powerful, open source database.', 'llm_tokenizer');
-- Output: {2795,7134,158897,83,10,113138,4,9803,31344,63399,5} -- Example token IDs

-- Tokenize some Spanish text (LLMLingua2 handles multiple languages)
SELECT tokenize('PostgreSQL es una potente base de datos de código abierto.', 'llm_tokenizer');
-- Output: {2795,7134,158897,198,220,105889,3647,8,13084,8,55845,118754,5} -- Example token IDs

-- Integrate with a table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

INSERT INTO documents (passage) VALUES ('PostgreSQL is a powerful, open source database.');

UPDATE documents
SET embedding = tokenize(passage, 'llm_tokenizer')
WHERE id = 1; -- Or process the whole table
```

**2\. Creating a Custom Tokenizer with Filters (Example: English)**

This example defines a custom pipeline, including lowercasing, Unicode normalization, skipping non-alphanumeric tokens, using NLTK English stop words, and the Porter2 stemmer. It then automatically trains a model and sets up a trigger to tokenize text on insert/update.

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding bm25vector
);

-- Define a custom text analysis pipeline
SELECT create_text_analyzer('english_analyzer', $$
pre_tokenizer = "unicode_segmentation"  # Basic word splitting
[[character_filters]]
to_lowercase = {}                       # Lowercase everything
[[character_filters]]
unicode_normalization = "nfkd"          # Normalize Unicode
[[token_filters]]
skip_non_alphanumeric = {}              # Remove punctuation-only tokens
[[token_filters]]
stopwords = "nltk_english"              # Use built-in English stopwords
[[token_filters]]
stemmer = "english_porter2"             # Apply Porter2 stemming
$$);

-- Create tokenizer, custom model based on 'articles.content', and trigger
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'custom_english_tokenizer',
    model_name => 'article_model',
    text_analyzer_name => 'english_analyzer',
    table_name => 'articles',
    source_column => 'content',
    target_column => 'embedding'
);

-- Now, inserts automatically generate tokens
INSERT INTO articles (content) VALUES
('VectorChord-BM25 provides advanced ranking features for PostgreSQL users.');

SELECT embedding FROM articles WHERE id = 1;
-- Output: {1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1}
-- Bm25vector based on the custom model and pipeline
```

**3\. Using Jieba for Chinese Text**

```sql
CREATE TABLE chinese_docs (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

-- Define a text analyzer using the Jieba pre-tokenizer
SELECT create_text_analyzer('jieba_analyzer', $$
[pre_tokenizer.jieba]
# Optional Jieba configurations can go here
$$);

-- Create tokenizer, custom model, and trigger for Chinese text
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'chinese_tokenizer',
    model_name => 'chinese_model',
    text_analyzer_name => 'jieba_analyzer',
    table_name => 'chinese_docs',
    source_column => 'passage',
    target_column => 'embedding'
);

-- Insert Chinese text
INSERT INTO chinese_docs (passage) VALUES
('红海早过了，船在印度洋面上开驶着。'); -- Example sentence

SELECT embedding FROM chinese_docs WHERE id = 1;
-- Output: {1:1, 2:1, 3:1, 4:1, 5:1, 6:1, 7:1, 8:1, 9:1, 10:1, 11:1, 12:1}
-- Bm25vector based on Jieba segmentation
```

*(For full examples, including custom stop words and synonyms, please refer to the* `pg_tokenizer.rs` documentation.)

### Understanding the Tokenizer Configuration

The new tokenizer system revolves around two core concepts:

1. **Text Analyzer:** Defines *how* raw text is processed into a sequence of tokens. It consists of:
    
    * `character_filters`: Modify text *before* splitting (e.g., lowercasing, Unicode normalization).
        
    * `pre_tokenizer`: Splits the text into initial tokens (e.g., based on Unicode rules, Jieba, Lindera).
        
    * `token_filters`: Modify or filter tokens *after* splitting (e.g., stop word removal, stemming, synonym replacement).
        
2. **Model:** Defines the mapping from the processed tokens to the final integer token IDs used by BM25. Models can be:
    
    * `pre-trained`: Use established vocabularies and rules (like `bert-base-uncased`, `llmlingua2`). Great for general purpose and multilingual use.
        
    * `custom`: Build a vocabulary dynamically from your own data, tailored specifically to your corpus and language(s).
        

You can define these components separately or inline them when creating a tokenizer using a simple TOML configuration format passed as a string in SQL.

<a id="get-started-with-vectorchord-bm25-0-2"></a>
### Get Started with VectorChord-BM25 0.2!

This release significantly boosts the flexibility and power of VectorChord-BM25, especially for users dealing with **multiple languages** or needing fine-grained control over text processing.

* **GitHub Repository:** [https://github.com/tensorchord/VectorChord-bm25](https://github.com/tensorchord/VectorChord-bm25)
    
* **Tokenizer Documentation:** [https://vchord.pgsty.com/bm25/tokenizer/](/docs/tokenizer/)
    

We encourage you to try out version 0.2 and explore the new tokenization capabilities. Your feedback is invaluable – please report any issues or suggest features on our GitHub repository.

Upgrade your PostgreSQL full-text search today with the enhanced multilingual flexibility of VectorChord-BM25 0.2 and `pg_tokenizer.rs`!

---
