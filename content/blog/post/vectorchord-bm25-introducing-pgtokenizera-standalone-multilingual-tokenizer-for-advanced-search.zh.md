---
title: "VectorChord-BM25：推出独立的多语言高级搜索分词器 pg_tokenizer"
date: 2025-04-02
description: "我们很高兴宣布发布 VectorChord-BM25 0.2 版本，这款 PostgreSQL 扩展旨在将先进的基于 BM25 的全文检索排序能力直接带入数据库……"
author: "Jinjing Zhou"
tags:
  - "vector-database"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search"
aliases:
  - "/blog/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/"
  - "/vectorchord-bm25-introducing-pgtokenizera-standalone-multilingual-tokenizer-for-advanced-search/"
---

我们很高兴地宣布发布 **VectorChord-BM25 0.2 版本**！这款 PostgreSQL 扩展旨在将先进的基于 BM25 的全文检索排序能力直接引入您的数据库中。

借助 VectorChord-BM25，您无需依赖外部搜索引擎，即可直接利用信息检索领域的标准算法——BM25 的强大能力。本次发布迈出了重要一步，重点强化了核心文本处理组件：**分词（tokenization）**，从而带来了更高的灵活性以及**显著提升的多语言支持能力**。

<a id="the-big-news-introducing-pg-tokenizer-rs"></a>
### 重磅消息：推出 `pg_tokenizer.rs` {#the-big-news-introducing-pg_tokenizerrs}

VectorChord-BM25 0.2 的核心基石是一个**完全重构并解耦的独立分词器扩展：**`pg_tokenizer.rs`。

为什么要做出这一改变？我们意识到，分词（即将文本切分为有意义的最小单元 token 的过程）极其复杂，且高度依赖于具体的语言和业务场景。在单一庞大的扩展中同时支持多种语言的独特规则、自定义词典、词干提取（stemming）、停用词（stop words）以及不同的分词策略，正变得越来越笨重。

通过将分词器拆分到遵循宽松 **Apache 许可证**的独立项目（`pg_tokenizer.rs`）中，我们实现了以下几项核心优势：

1. **模块化与灵活性**：开发者现在可以独立于核心 BM25 排序逻辑来使用或定制分词器。
    
2. **更易于社区贡献**：`pg_tokenizer.rs` 职责更加聚焦，使社区能够更轻松地贡献**新语言支持**、分词技术或自定义过滤器。
    
3. **更快的迭代速度**：我们现在可以更快速地开发和发布分词器改进，而无需等待完整的 VectorChord-BM25 发布周期。
    
4. **更强大的定制能力**：**无论处理何种语言**，用户都能对排序前的文本处理流程获得更精细的控制权。
    

<a id="what-s-new-in-tokenization-thanks-to-pg-tokenizer-rs"></a>
### 分词功能有哪些新特性（得益于 `pg_tokenizer.rs`） {#whats-new-in-tokenization-thanks-to-pg_tokenizerrs}

这一全新架构在 v0.2 中解锁了多项强大特性：

* **更广泛的语言支持**：通过专用分词器（如针对**中文的 Jieba** 和针对**日文的 Lindera**），以及在海量多语言数据集上训练的强大**多语言大模型分词器**（如 **Gemma2** 和 **LLMLingua2**），直接满足多样化的语言处理需求。
    
* **更丰富的分词特性**：现在您可以对分词流水线进行更细粒度的控制：
    
    * **自定义停用词（Custom Stop Words）**：定义您自己的停用词列表，在索引和搜索期间忽略这些词。
        
    * **自定义词干提取器（Custom Stemmers）**：应用多种受支持语言的词干提取规则，甚至定义自定义规则。
        
    * **自定义同义词（Custom Synonyms）**：定义同义词列表，将不同的词视为等价词（例如 `"postgres"`、`"postgresql"`、`"pgsql"`）。
        
    * **语言专属选项（Language-Specific Options）**：在需要时利用特定分词器（如 Lindera 或 Jieba）内部提供的细粒度控制选项。
        

### 代码示例！ {#show-me-the-code}

下面来看看使用全新的分词器特性有多么简单。

**1\. 使用预训练的多语言 LLM 分词器（LLMLingua2）**

基于大语言模型（LLM）的分词器非常适合处理包含多种不同语言的文本。

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

**2\. 创建带过滤器的自定义分词器（示例：英文）**

本示例定义了一条自定义流水线，包括转小写、Unicode 规范化、跳过非字母数字词元、使用 NLTK 英文停用词表以及 Porter2 词干提取器。随后，它会自动训练模型并设置触发器，以便在插入或更新时自动对文本进行分词。

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

**3\. 使用 Jieba 处理中文文本**

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

*（有关包括自定义停用词和同义词在内的完整示例，请参阅 `pg_tokenizer.rs` 文档。）*

### 深入理解分词器配置 {#understanding-the-tokenizer-configuration}

全新的分词器系统围绕两个核心概念构建：

1. **文本分析器（Text Analyzer）**：定义*如何*将原始文本处理为词元序列。它由以下部分组成：
    
    * `character_filters`（字符过滤器）：在切分*之前*修改文本（例如转小写、Unicode 规范化）。
        
    * `pre_tokenizer`（预分词器）：将文本切分为初始词元（例如基于 Unicode 规则、Jieba、Lindera）。
        
    * `token_filters`（词元过滤器）：在切分*之后*修改或过滤词元（例如移除停用词、词干提取、同义词替换）。
        
2. **模型（Model）**：定义从处理后的词元到 BM25 最终使用的整数词元 ID 的映射关系。模型可以分为：
    
    * `pre-trained`（预训练模型）：使用现成的词表和规则（如 `bert-base-uncased`、`llmlingua2`），非常适合通用场景及多语言使用。
        
    * `custom`（自定义模型）：根据您自己的数据动态构建词表，专门针对您的语料库和语言量身定制。
        

您可以在 SQL 中以字符串形式传入简洁的 TOML 配置格式，将这些组件分开定义，也可以在创建分词器时直接内联定义。

<a id="get-started-with-vectorchord-bm25-0-2"></a>
### 立即上手 VectorChord-BM25 0.2！ {#get-started-with-vectorchord-bm25-02}

本次发布大幅提升了 VectorChord-BM25 的灵活性与功能深度，特别是对于需要处理**多语言**或对文本处理有细粒度控制需求的用户。

* **GitHub 仓库**：[https://github.com/tensorchord/VectorChord-bm25](https://github.com/tensorchord/VectorChord-bm25)
    
* **分词器文档**：[https://vchord.pgsty.com/bm25/tokenizer/](/zh/docs/tokenizer/)
    

我们诚邀您试用 0.2 版本并探索全新的分词能力。您的反馈至关重要——欢迎在我们的 GitHub 仓库中报告任何问题或提出功能建议。

立即使用 VectorChord-BM25 0.2 与 `pg_tokenizer.rs`，以强大的多语言灵活性升级您的 PostgreSQL 全文检索体验！

---
