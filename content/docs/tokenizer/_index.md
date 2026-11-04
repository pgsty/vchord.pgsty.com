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
  upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs"
  upstream_modified: true
---

**`pg_tokenizer` 1.0.0** (maintained by Pigsty at [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)) is a standalone multilingual tokenization extension for PostgreSQL built in Rust (`pgrx`). It provides customizable text analyzers, character/token filters, and vocabulary models that produce integer token ID arrays (`INT[]`) for the historical `bm25vector` workflow and native PostgreSQL `tsvector` values for GIN/GiST or compatible BM25 indexes.

{{< cards >}}
  {{< card link="/docs/tokenizer/installation/" title="Installation" icon="fa-solid fa-download" >}}
Install and preload `pg_tokenizer` via Pigsty native Linux packages, Docker (Obsolete) containers, Debian/ZIP release archives, or `cargo-pgrx` source builds.
{{< /card >}}
  {{< card link="/docs/tokenizer/overview/" title="Architecture & Usage" icon="fa-solid fa-sitemap" >}}
Understand how two-stage Text Analyzers and Vocabulary Models work together to transform raw text into integer token IDs or native `tsvector` values.
{{< /card >}}
  {{< card link="/docs/tokenizer/text-analyzer/" title="Text Analyzers & Filters" icon="fa-solid fa-sliders" >}}
Chain declarative character filters, pre-tokenizers (Unicode, Regex, Jieba), Snowball stemmers (30 languages), stopwords, synonyms, and n-gram filters.
{{< /card >}}
  {{< card link="/docs/tokenizer/models/" title="Tokenization Models" icon="fa-solid fa-cubes" >}}
Use built-in pretrained models (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`), train custom corpus models, or import HuggingFace models.
{{< /card >}}
  {{< card link="/docs/tokenizer/multilingual/" title="Multilingual Recipes & Limitations" icon="fa-solid fa-earth-asia" >}}
Ready-to-use SQL configurations and operational guidelines for English, Chinese (`jieba`), Japanese (`lindera`), and custom domain-specific corpora.
{{< /card >}}
  {{< card link="/docs/tokenizer/reference/" title="SQL & TOML Reference" icon="fa-solid fa-book" >}}
Consult the complete reference for all `tokenizer_catalog` SQL functions, trigger helpers, built-in model specs, and TOML configuration parameters.
{{< /card >}}
{{< /cards >}}
