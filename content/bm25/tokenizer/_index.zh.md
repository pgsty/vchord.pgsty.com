---
title: "分词器 (pg_tokenizer)"
description: "pg_tokenizer 完整指南：文本分析器、字符/词元过滤器、预训练与自定义词表模型，以及多语言分词。"
weight: 30
icon: fa-solid fa-language
cascade:
  type: docs
  upstream_source: "tokenizer"
  upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs"
---

**`pg_tokenizer`**（由 Pigsty 在 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 维护）是 [`vchord_bm25` (`pgsty/vchord_bm25`)](https://github.com/pgsty/vchord_bm25) 的配套 PostgreSQL 分词扩展，提供全文分析器与词表模型，可将原始文本转换为整数词元 ID 数组（`INT[]`）及稀疏 `bm25vector` 向量。

{{< cards >}}
  {{< card link="/zh/bm25/tokenizer/overview/" title="分词器架构与基本用法" icon="fa-solid fa-sitemap" >}}
了解文本分析器（Text Analyzer）与词表模型（Model）如何协同工作，将原始文本转化为词元 ID。
{{< /card >}}
  {{< card link="/zh/bm25/tokenizer/text-analyzer/" title="文本分析器与过滤器" icon="fa-solid fa-sliders" >}}
配置字符过滤器、预分词器（Unicode、正则、结巴 Jieba）、词干提取器（支持 30 种语言）、停用词、同义词与 N-gram。
{{< /card >}}
  {{< card link="/zh/bm25/tokenizer/models/" title="分词词表模型" icon="fa-solid fa-cubes" >}}
使用内置预训练模型（llmlingua2、bert_base_uncased、wiki_tocken、gemma2b）、训练自定义语料模型，或导入 HuggingFace 与 Lindera 模型。
{{< /card >}}
  {{< card link="/zh/bm25/tokenizer/multilingual/" title="多语言分词配方与限制" icon="fa-solid fa-earth-asia" >}}
面向英文、中文（Jieba）、日文（Lindera）及特定领域自定义语料库的开箱即用配置方案。
{{< /card >}}
{{< /cards >}}
