---
title: "Tokenizers (pg_tokenizer)"
description: "Complete guide to pg_tokenizer: text analyzers, character/token filters, pretrained and custom models, and multilingual tokenization."
weight: 30
icon: fa-solid fa-language
cascade:
  type: docs
  upstream_source: "tokenizer"
  upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs"
---

**`pg_tokenizer`** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)) is the companion PostgreSQL extension for [`vchord_bm25` (`pgsty/vchord_bm25`)](https://github.com/pgsty/vchord_bm25) that provides full-text analyzers and vocabulary models to convert raw text into integer token ID arrays (`INT[]`) and sparse `bm25vector` embeddings.

{{< cards >}}
  {{< card link="/bm25/tokenizer/overview/" title="Tokenizer Architecture & Usage" icon="fa-solid fa-sitemap" >}}
How Text Analyzers and Models combine to turn raw text into token IDs.
{{< /card >}}
  {{< card link="/bm25/tokenizer/text-analyzer/" title="Text Analyzers & Filters" icon="fa-solid fa-sliders" >}}
Configure character filters, pre-tokenizers (Unicode, Regex, Jieba), stemmers (30 languages), stopwords, synonyms, and n-grams.
{{< /card >}}
  {{< card link="/bm25/tokenizer/models/" title="Tokenization Models" icon="fa-solid fa-cubes" >}}
Use built-in models (llmlingua2, bert_base_uncased, wiki_tocken, gemma2b), train custom corpus models, or import HuggingFace & Lindera models.
{{< /card >}}
  {{< card link="/bm25/tokenizer/multilingual/" title="Multilingual Recipes & Limitations" icon="fa-solid fa-earth-asia" >}}
Ready-to-use configurations for English, Chinese (Jieba), Japanese (Lindera), and custom domain corpora.
{{< /card >}}
{{< /cards >}}
