---
title: "参考"
linkTitle: "参考"
description: "pg_tokenizer 的全部函数、配置项和参数，每项只定义一次。"
weight: 60
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/00-reference.md"
icon: fa-solid fa-book
---

本页定义 pg_tokenizer 1.3.0 的每个函数、配置项和参数。什么时候用哪一个，见各篇指南：[文本分析器](/zh/docs/tokenizer/text-analyzer/)、[模型](/zh/docs/tokenizer/models/)和[多语言配方](/zh/docs/tokenizer/multilingual/)。

## 函数 {#sql-functions}

<a id="text-analyzer--dictionaries"></a><a id="tokenization-models--preloading"></a><a id="tokenizer-execution"></a><a id="native-full-text-search"></a><a id="api-semantics"></a>

所有函数都在模式 `tokenizer_catalog` 中。定义保存在当前数据库的表里。

名称已被占用时，`create_*` 函数会失败，报错形如 `Text analyzer already exists: en_text`；没有“替换”操作，只能先删除再创建。名称不存在时，`drop_*` 函数只给出警告，也不会检查是否有对象在使用该定义。这两类函数都是 `VOLATILE`、`PARALLEL UNSAFE`。

### 分析与分词 {#tokenize-functions}

这四个函数都是 `STABLE`、`STRICT`（任一参数为 `NULL` 时返回 `NULL`）和 `PARALLEL SAFE`。

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `apply_text_analyzer(text, text_analyzer_name)` | `text[]` | 运行分析器，按顺序返回切出的词。用来检查分析器。 |
| `analyze_to_tsvector(text, text_analyzer_name)` | `tsvector` | 运行分析器，把词作为词位返回，按输出顺序编号 1、2、3……，权重为 `D`。 |
| `tokenize(text, tokenizer_name)` | `int[]` | 运行分词器，按顺序返回词元 ID。 |
| `tokenize_to_tsvector(text, tokenizer_name)` | `tsvector` | 运行分词器，把 ID 作为十进制词位返回，编号方式与 `analyze_to_tsvector` 相同。 |
{.fields meta="type"}

### 文本分析器、停用词与同义词 {#text-analyzer-functions}

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `create_text_analyzer(name, config)` | `void` | 根据 TOML [配置](#text-analyzer-options)创建分析器。`pg_dict` 词典名按当前 `search_path` 解析，连同模式名一起保存。 |
| `drop_text_analyzer(name)` | `void` | 删除分析器。 |
| `create_stopwords(name, config)` | `void` | 创建停用词表：每行一个词，精确匹配。 |
| `drop_stopwords(name)` | `void` | 删除停用词表。内置的 `lucene_english`、`nltk_english` 和 `iso_english` 不能删除或替换。 |
| `create_synonym(name, config)` | `void` | 创建同义词表。每行先写要输出的形式，后面是映射到它的词，用空格分隔；同一个词在一张表里只能出现一次。 |
| `drop_synonym(name)` | `void` | 删除同义词表。 |
{.fields meta="type"}

### 分词器与模型 {#model-functions}

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `create_tokenizer(name, config)` | `void` | 根据 TOML [配置](#tokenizer-options)创建分词器。 |
| `drop_tokenizer(name)` | `void` | 删除分词器。 |
| `create_lindera_model(name, config)` | `void` | 根据 Lindera 7 的 TOML 配置创建 [Lindera](/zh/docs/tokenizer/models/#lindera) 模型。从文件读取词典需要超级用户或 `pg_read_server_files`。 |
| `drop_lindera_model(name)` | `void` | 删除 Lindera 模型。 |
| `create_huggingface_model(name, config)` | `void` | 根据 Hugging Face `tokenizer.json` 的内容创建模型。所有 ID，包括新增词元、特殊词元和 `padding.pad_id`，都不能超过 2147483647。 |
| `drop_huggingface_model(name)` | `void` | 删除 Hugging Face 模型。 |
| `create_custom_model(name, config)` | `void` | 按 TOML [配置](#custom-model-options)从表中的一列构建词表，存入 `tokenizer_data."model_<name>"`，并添加负责收录新词的触发器 `model_<name>_trigger`。 |
| `create_custom_model_tokenizer_and_trigger(tokenizer_name, model_name, text_analyzer_name, table_name, source_column, target_column [, filter])` | `void` | 执行 `create_custom_model` 和 `create_tokenizer`，把每行的 ID 填入 `target_column`，并添加保持其最新的触发器 `model_<name>_trigger_insert`。`filter` 可选，为 `NULL` 时包含所有行。 |
| `drop_custom_model(name)` | `void` | 删除自定义模型及其词表和触发器。使用它的分词器会保留。 |
{.fields meta="type"}

所有类型的模型共用同一个命名空间：名称只能由 ASCII 字母、数字和下划线组成，以字母开头，最长 20 个字符。`bert_base_uncased`、`gemma2b`、`llmlingua2` 和 `wiki_tocken` 是内置模型，名称不能复用。

### 预加载列表 {#preload-functions}

| 函数 | 返回 | 说明 |
| --- | --- | --- |
| `add_preload_model(name)` | `void` | 把一个内置模型或当前数据库中的模型加入服务器的预加载列表。下次重启时生效；即使事务回滚，文件也已写入。除非另行授权，仅限超级用户。 |
| `remove_preload_model(name)` | `void` | 从预加载列表中移除模型。规则与 `add_preload_model` 相同。 |
| `list_preload_models()` | `text[]` | 按名称排序列出预加载列表，包括加载失败的条目。 |
{.fields meta="type"}

## 配置 {#toml-configuration-options}

配置使用 [TOML](https://toml.io/) 格式。未知的键和无效的值会以 SQLSTATE `22023` 被拒绝。不带选项的阶段既可以写成字符串 `"to_lowercase"`，也可以写成表 `{ to_lowercase = {} }`。

### 文本分析器 {#text-analyzer-options}

| 键 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `character_filters` | array | `[]` | [字符过滤器](#character-filters)，按顺序作用于整段文本。 |
| `pre_tokenizer` | string or table | 无 | [预分词器](#pre-tokenizers)。没有时整段文本就是一个词。 |
| `token_filters` | array | `[]` | [词元过滤器](#token-filters)，按顺序执行。 |
{.fields meta="type default"}

### 字符过滤器 {#character-filters}

| 键 | 类型 | 说明 |
| --- | --- | --- |
| `to_lowercase` | none | 按 Unicode 规则转为小写。 |
| `unicode_normalization` | string | 应用一种 [Unicode 规范化形式](https://unicode.org/reports/tr15/)：`nfc`、`nfd`、`nfkc` 或 `nfkd`。`nfkc` 还会把全角字符和兼容字符折叠为标准形式。 |
{.fields meta="type"}

### 预分词器 {#pre-tokenizers}

| 键 | 类型 | 说明 |
| --- | --- | --- |
| `unicode_segmentation` | none | 按 Unicode 词边界（[UAX #29](https://www.unicode.org/reports/tr29/)）切分，保留含有字母或数字的片段。 |
| `regex` | string | 返回 Rust [`regex`](https://docs.rs/regex) 模式的每个不重叠匹配。 |
| `jieba` | table | 用[结巴](https://github.com/messense/jieba-rs)词典切分中文，选项见下表。 |
{.fields meta="type"}

<a id="jieba-chinese-word-segmentation"></a>

| `jieba` 键 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `mode` | string | `search` | `search` 返回最可能的切分，外加长词内部较短的词典词，适合索引和查询。`precise` 只返回最可能的切分。`full` 返回找到的所有词典词，彼此可以重叠。 |
| `enable_hmm` | boolean | `true` | 在 `precise` 和 `search` 模式下把词典中没有的字组合成词。`full` 模式忽略此项。 |
{.fields meta="type default"}

### 词元过滤器 {#token-filters}

<a id="3-token-filters-token_filters"></a>

| 键 | 类型 | 说明 |
| --- | --- | --- |
| `skip_non_alphanumeric` | none | 删除不含字母或数字的词。 |
| `stopwords` | string | 删除指定停用词表中的词：`lucene_english`、`nltk_english`、`iso_english`，或用 `create_stopwords` 创建的表。 |
| `stemmer` | string | 把每个词替换为 Snowball 词干，取值见[下文](#stemmers)。要求输入为小写。 |
| `synonym` | string | 用 `create_synonym` 创建的同义词表替换词。 |
| `pg_dict` | string | 像 `ts_lexize` 一样把每个词交给 PostgreSQL 全文检索词典处理。不认识的词原样通过，停用词被删除。 |
| `ngram` | table | 把每个词替换为它的字符 n-gram，选项见下表。 |
{.fields meta="type"}

| `ngram` 键 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `min_gram` | integer | `1` | 最短 n-gram 的字符数，取值 1 到 255，且不大于 `max_gram`。 |
| `max_gram` | integer | `2` | 最长 n-gram 的字符数，取值 1 到 255。范围越宽，能匹配的子串越多，索引也越大。 |
| `preserve_original` | boolean | `false` | 长度不在范围内的词也保留原词；否则它会被替换，短于 `min_gram` 时则被删除。 |
{.fields meta="type default"}

### 词干算法 {#stemmers}

<a id="stemmer-snowball-stemming--30-languages"></a>

`arabic`、`armenian`、`basque`、`catalan`、`danish`、`dutch`、`english_porter`、`english_porter2`、`estonian`、`finnish`、`french`、`german`、`greek`、`hindi`、`hungarian`、`indonesian`、`irish`、`italian`、`lithuanian`、`nepali`、`norwegian`、`portuguese`、`romanian`、`russian`、`serbian`、`spanish`、`swedish`、`tamil`、`turkish`、`yiddish`。英文方面，`english_porter2` 是现行的 Snowball 算法，`english_porter` 是最初的 Porter 词干算法。

### 分词器 {#tokenizer-options}

| 键 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `model` | string | 是 | 内置模型，或本数据库中的 Lindera、Hugging Face、自定义模型。 |
| `text_analyzer` | string | | 在模型之前运行的分析器。不能与下面的内联键同时使用。 |
| `character_filters` | array | | 内联分析器的字符过滤器。 |
| `pre_tokenizer` | string or table | | 内联分析器的预分词器。 |
| `token_filters` | array | | 内联分析器的词元过滤器。 |
{.fields meta="type required"}

没有分析器时，模型拿到整段文本；有分析器时，模型分别处理每个词。

### 自定义模型 {#custom-model-options}

| 键 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| `table` | string | 是 | 源表，可带模式限定，保存时会补全模式名。 |
| `column` | string | 是 | 源列。任何能转换为 `text` 的类型都可以。 |
| `text_analyzer` | string | 是 | 把该列切分成词的分析器。 |
| `filter` | string | | 针对源表列的 SQL 条件，不写 `WHERE`。只有条件为真的行参与构建词表并得到 ID。默认包含所有行。 |
{.fields meta="type required"}

### Lindera 模型 {#lindera-model-options}

配置就是 [Lindera 7](https://github.com/lindera/lindera) 的分词器配置。pg_tokenizer 自己读取下列键：

| 键 | 类型 | 说明 |
| --- | --- | --- |
| `segmenter.mode` | string | Lindera 切分模式，例如 `normal`。 |
| `segmenter.dictionary` | string | `embedded://<name>` 表示内置在动态库中的词典，或者服务器上 Lindera 7（format v3）词典目录的路径或 `file://` URI。 |
| `segmenter.user_dictionary` | string | 用户词典的路径，CSV 或编译后的格式均可。其中词的 ID 从 1073741824 开始。 |
| `character_filters` | array | Lindera 字符过滤器，每项包含 `kind` 和 `args`。 |
| `token_filters` | array | Lindera 词元过滤器，每项包含 `kind` 和 `args`。删除词的过滤器会同时删除其 ID；只改写文本的过滤器对 ID 没有影响。 |
{.fields meta="type"}

## 参数 {#analysis-budgets}

<a id="definition-caches"></a>

这些参数限制单次调用的工作量。它们都是取值 1 到 2147483647 的整数，任何用户都可以 `SET`。调用超出限制时以 SQLSTATE `54000` 失败，报错中会写明是哪个参数，例如 `pg_tokenizer exceeds max_piece_bytes (1048576)`；不会做任何截断。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `pg_tokenizer.max_input_bytes` | integer | `16777216` | 单次分析器或分词器调用的最大输入字节数。 |
| `pg_tokenizer.max_output_tokens` | integer | `1000000` | 单个阶段最多产生的词或 ID 数。 |
| `pg_tokenizer.max_output_bytes` | integer | `67108864` | 单个阶段最多产生的字节数，包括词、ID、改写后的文本和 n-gram 的簿记开销。 |
| `pg_tokenizer.max_piece_bytes` | integer | `1048576` | 单次调用结巴、正则表达式、模型或 `pg_dict` 的最大输入字节数。这类调用返回之前无法被取消，所以该参数也限定了查询能无视取消请求或 `statement_timeout` 多久。 |
{.fields meta="type default"}

面向用户的查询保持默认值即可。批量导入可信的大文档时，只在该事务内调高限制：

```sql
BEGIN;
SET LOCAL pg_tokenizer.max_piece_bytes = 16777216;
UPDATE docs SET terms = tokenizer_catalog.analyze_to_tsvector(body, 'zh_text');
COMMIT;
```

这些限制只统计 pg_tokenizer 自己的缓冲区，而不是后端进程的全部内存：已加载的模型和第三方库内部的内存都要另算。

## 目录表 {#catalog}

定义是 `tokenizer_catalog.text_analyzer`、`tokenizer`、`model`、`stopwords` 和 `synonym` 这几张表中的行，每行有 `name` 和对应的 `config`。可以查询它们来查看已有哪些定义，但修改只应通过上面的函数进行：

```sql
SELECT name FROM tokenizer_catalog.text_analyzer;
SELECT name, config FROM tokenizer_catalog.tokenizer;
```

自定义模型的词表是 `tokenizer_data."model_<name>"`，包含 `id` 和 `token` 两列。
