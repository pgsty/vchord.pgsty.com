---
title: "pg_tokenizer 文档"
linkTitle: "pg_tokenizer"
description: "pg_tokenizer 完整指南：安装部署、文本分析器、字符/词元过滤器、预训练与自定义词表模型、多语言分词以及 SQL 参考手册。"
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

**`pg_tokenizer` 0.2.0**（由 Pigsty 在 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 维护）是一个使用 Rust（`pgrx`）构建的独立 PostgreSQL 多语言分词扩展。它提供可定制的文本分析器、字符与词元过滤器以及词表模型：既能为历史 `bm25vector` 工作流生成整数词元 ID 数组（`INT[]`），也能生成供 GIN/GiST 或兼容 BM25 索引使用的 PostgreSQL 原生 `tsvector`。

{{< cards >}}
  {{< card link="/zh/docs/tokenizer/installation/" title="安装指南" icon="fa-solid fa-download" >}}
通过 Pigsty 原生 Linux 软件包、Docker 容器镜像、Debian/ZIP 预编译归档包或 `cargo-pgrx` 源码编译方式安装并启用 `pg_tokenizer`。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/overview/" title="架构与基本用法" icon="fa-solid fa-sitemap" >}}
深入了解文本分析器（Text Analyzer）与词表模型（Model）如何协同工作，将原始文本转化为词元 ID 数组或原生 `tsvector`。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/text-analyzer/" title="文本分析器与过滤器" icon="fa-solid fa-sliders" >}}
灵活配置字符过滤器、预分词器（Unicode、正则、结巴 Jieba）、Snowball 词干提取（支持 30 种语言）、停用词、同义词与 N-gram。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/models/" title="分词词表模型" icon="fa-solid fa-cubes" >}}
使用内置预训练模型（`llmlingua2`、`bert_base_uncased`、`wiki_tocken`、`gemma2b`）、训练自定义语料模型，或导入 HuggingFace 模型。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/multilingual/" title="多语言分词配方与限制" icon="fa-solid fa-earth-asia" >}}
提供面向英文、中文（结巴 Jieba）、日文（Lindera IPADIC/UniDic）及特定领域自定义语料库的开箱即用分词配置与升级注意事项。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/reference/" title="SQL 与 TOML 参考" icon="fa-solid fa-book" >}}
查阅完整的 `tokenizer_catalog` SQL 函数签名、触发器辅助函数、内置词表规格以及分析器与分词器 TOML 配置参数参考手册。
{{< /card >}}
{{< /cards >}}
