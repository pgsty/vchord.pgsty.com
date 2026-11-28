---
title: "pg_tokenizer Documentation"
linkTitle: "pg_tokenizer"
description: "pg_tokenizer turns multilingual text into tsvector lexemes for BM25 search, or into the token IDs of a vocabulary, inside PostgreSQL."
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

pg_tokenizer is a PostgreSQL extension that splits text into words, or into the token IDs of a vocabulary, with a pipeline you configure in SQL. Use it to feed [vchord_bm25](/docs/bm25/) when PostgreSQL's own `to_tsvector` does not fit your text: Chinese and Japanese, which have no spaces between words, stemming with your own stopwords and synonyms, or the vocabulary of an LLM tokenizer.

{{< cards >}}
  {{< card link="/docs/tokenizer/overview/" title="Overview" icon="fa-solid fa-compass" >}}
How the analyzer and model stages fit together, which one you need, and a quick start with BM25.
{{< /card >}}
  {{< card link="/docs/tokenizer/installation/" title="Installation" icon="fa-solid fa-download" >}}
Install from Pigsty packages, GitHub releases or source, preload the library, and upgrade in place.
{{< /card >}}
  {{< card link="/docs/tokenizer/multilingual/" title="Multilingual Recipes" icon="fa-solid fa-earth-asia" >}}
Complete SQL for BM25 search on English, other European languages, Chinese and Japanese.
{{< /card >}}
  {{< card link="/docs/tokenizer/text-analyzer/" title="Text Analyzers" icon="fa-solid fa-sliders" >}}
Choose how text is split and filtered: word boundaries or jieba, stopwords, stemming, synonyms, PostgreSQL dictionaries, n-grams.
{{< /card >}}
  {{< card link="/docs/tokenizer/models/" title="Models" icon="fa-solid fa-cubes" >}}
Token IDs from built-in LLM vocabularies, Hugging Face tokenizers, Lindera dictionaries and your own corpus.
{{< /card >}}
  {{< card link="/docs/tokenizer/reference/" title="Reference" icon="fa-solid fa-book" >}}
Every function, configuration key and setting.
{{< /card >}}
{{< /cards >}}
