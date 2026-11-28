---
title: "pg_tokenizer 文档"
linkTitle: "pg_tokenizer"
description: "pg_tokenizer 在 PostgreSQL 内把多语言文本转换成用于 BM25 检索的 tsvector 词位，或某个词表的词元 ID。"
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

pg_tokenizer 是一个 PostgreSQL 扩展，用 SQL 配置的流水线把文本切分成词，或者转换成某个词表的词元 ID。当 PostgreSQL 自带的 `to_tsvector` 处理不好你的文本时，用它为 [vchord_bm25](/zh/docs/bm25/) 提供输入：词与词之间没有空格的中文和日文，需要自定义停用词和同义词的词干提取，或者要与某个大模型分词器的词表保持一致。

{{< cards >}}
  {{< card link="/zh/docs/tokenizer/overview/" title="概览" icon="fa-solid fa-compass" >}}
分析器与模型两个阶段如何配合、你需要哪一个，以及 BM25 快速上手。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/installation/" title="安装" icon="fa-solid fa-download" >}}
通过 Pigsty 软件包、GitHub 发布包或源码安装，预加载动态库，原地升级。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/multilingual/" title="多语言配方" icon="fa-solid fa-earth-asia" >}}
为英文、其他欧洲语言、中文和日文搭建 BM25 检索的完整 SQL。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/text-analyzer/" title="文本分析器" icon="fa-solid fa-sliders" >}}
选择文本的切分与过滤方式：词边界或结巴分词、停用词、词干提取、同义词、PostgreSQL 词典、n-gram。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/models/" title="模型" icon="fa-solid fa-cubes" >}}
从内置大模型词表、Hugging Face 分词器、Lindera 词典和你自己的语料生成词元 ID。
{{< /card >}}
  {{< card link="/zh/docs/tokenizer/reference/" title="参考" icon="fa-solid fa-book" >}}
全部函数、配置项和参数。
{{< /card >}}
{{< /cards >}}
