---
title: "pg_tokenizer Documentation"
linkTitle: "pg_tokenizer"
description: "Complete guide to pg_tokenizer: installation, text analyzers, character/token filters, pretrained and custom models, multilingual tokenization, and SQL reference."
weight: 300
icon: fa-solid fa-language
type: docs
sidebar_root_for: self
aliases:
  - "/bm25/tokenizer/"
  - "/tokenizer/"
no_list: true
cascade:
  type: docs
  upstream_source: "tokenizer"
  upstream_link: "https://github.com/tensorchord/pg_tokenizer.rs"
  upstream_modified: true
---

**`pg_tokenizer`** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)) is a standalone multilingual tokenization extension for PostgreSQL built in Rust (`pgrx`). It provides customizable text analyzers, character/token filters, and vocabulary models to convert raw text into integer token ID arrays (`INT[]`) and sparse `bm25vector` embeddings for [`vchord_bm25`](/docs/bm25/).

{{< cards >}}
  {{< card link="/docs/tokenizer/installation/" title="Installation" icon="fa-solid fa-download" >}}
Install pg_tokenizer via Pigsty native Linux packages, Docker, Debian/ZIP archives, or cargo-pgrx.
{{< /card >}}
  {{< card link="/docs/tokenizer/overview/" title="Architecture & Usage" icon="fa-solid fa-sitemap" >}}
How Text Analyzers and Models combine to turn raw text into token IDs.
{{< /card >}}
  {{< card link="/docs/tokenizer/text-analyzer/" title="Text Analyzers & Filters" icon="fa-solid fa-sliders" >}}
Configure character filters, pre-tokenizers (Unicode, Regex, Jieba), stemmers (30 languages), stopwords, synonyms, and n-grams.
{{< /card >}}
  {{< card link="/docs/tokenizer/models/" title="Tokenization Models" icon="fa-solid fa-cubes" >}}
Use built-in models (llmlingua2, bert_base_uncased, wiki_tocken, gemma2b), train custom corpus models, or import HuggingFace & Lindera models.
{{< /card >}}
  {{< card link="/docs/tokenizer/multilingual/" title="Multilingual Recipes & Limitations" icon="fa-solid fa-earth-asia" >}}
Ready-to-use configurations for English, Chinese (Jieba), Japanese (Lindera), and custom domain corpora.
{{< /card >}}
  {{< card link="/docs/tokenizer/reference/" title="SQL & TOML Reference" icon="fa-solid fa-book" >}}
Complete reference for all tokenizer_catalog SQL functions and TOML configuration options.
{{< /card >}}
{{< /cards >}}
