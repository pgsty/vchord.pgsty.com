---
title: "文本分析器"
linkTitle: "文本分析器"
description: "为某种语言选择 pg_tokenizer 切分和规范化文本的方式，检查输出结果，以及替换正在使用的分析器。"
weight: 40
icon: fa-solid fa-sliders
---

文本分析器决定什么算一个词，是整条流水线中需要针对语言和检索习惯来调整的部分。本页说明每个阶段怎么选、怎么检查输出，以及怎样替换一个已有存储数据依赖的分析器。每个配置项都只在[参考](/zh/docs/tokenizer/reference/#text-analyzer-options)中定义一次。

## 分析器如何运行 {#how-it-works}

分析器分三个阶段，依次执行：

1. **字符过滤器**（character filters）逐个改写整段文本：`to_lowercase` 和 `unicode_normalization`。
1. **预分词器**（pre-tokenizer）把文本切成词，最多一个。没有预分词器时，整段文本就是一个词。
1. **词元过滤器**（token filters）按列出的顺序执行，每个都处理上一个的输出。它们可以删除词（`skip_non_alphanumeric`、`stopwords`）、改写词（`stemmer`、`synonym`、`pg_dict`）或扩展词（`ngram`）。
{.steps}

顺序很重要，因为过滤器都是精确匹配。转小写要放在停用词和同义词之前，否则 "The" 不会被包含 "the" 的停用词表去掉；停用词要放在词干提取之前，因为停用词表里存的是未经词干化的原词。

配置使用 [TOML](https://toml.io/) 格式。不带选项的阶段既可以写成字符串，也可以写成表，所以下面两个分析器完全相同：

```sql
SELECT tokenizer_catalog.create_text_analyzer('en_short', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ stopwords = "nltk_english" }, { stemmer = "english_porter2" }]
$$);

SELECT tokenizer_catalog.create_text_analyzer('en_long', $$
pre_tokenizer = "unicode_segmentation"

[[character_filters]]
to_lowercase = {}

[[token_filters]]
stopwords = "nltk_english"

[[token_filters]]
stemmer = "english_porter2"
$$);
```

按 TOML 语法，`pre_tokenizer` 这类顶层键必须写在第一个 `[[table]]` 标题之前。创建分析器时，未知的键或无效的值都会被拒绝。

## 检查分析器的输出 {#test}

`apply_text_analyzer` 按顺序返回切出的词，`analyze_to_tsvector` 显示实际会存储的词位和位置：

```sql
SELECT tokenizer_catalog.apply_text_analyzer('The Quick brown foxes', 'en_short');
SELECT tokenizer_catalog.analyze_to_tsvector('The Quick brown foxes', 'en_short');
```

```text
{quick,brown,fox}
'brown':2 'fox':3 'quick':1
```

在存储任何数据之前，先拿几篇真实的文档和查询跑一遍：以后再改，就得重新计算所有已存储的值。

## 选择预分词器 {#pre-tokenizer}

| 文本 | 预分词器 | 说明 |
| --- | --- | --- |
| 英文及其他以空格分词的语言 | `unicode_segmentation` | 按 Unicode 词边界（[UAX #29](https://www.unicode.org/reports/tr29/)）切分，丢弃不含字母或数字的片段。 |
| 中文 | `jieba` | 借助词典找出词语。标点和空格也会作为词返回，所以要加上 `skip_non_alphanumeric`。 |
| 日文、韩文 | 不用 | 改用 [Lindera 模型](/zh/docs/tokenizer/models/#lindera)，不用分析器。 |
| 编码、标识符、日志字段 | `regex` | 模式的每个不重叠匹配都是一个词，例如 `regex = '[A-Za-z0-9_]+'`。 |

结巴有三种模式。默认的 `search` 适合检索索引：它返回最可能的切分，同时还返回长词内部的词典词，因此查询短词也能匹配到包含它的长词。`precise` 只返回最可能的切分，`full` 返回找到的所有词典词，彼此可以重叠。以“我来到北京清华大学”为例：

| 模式 | 切分结果 |
| --- | --- |
| `precise` | 我, 来到, 北京, 清华大学 |
| `search` | 我, 来到, 北京, 清华, 华大, 大学, 清华大学 |
| `full` | 我, 来, 来到, 到, 北, 北京, 京, 清, 清华, 清华大学, 华, 华大, 大, 大学, 学 |

`enable_hmm` 默认开启，它让 `precise` 和 `search` 模式能把词典里没有的字组合成词，比如人名。

## 过滤词 {#token-filters}

### 停用词 {#stopwords}

`stopwords` 删除出现在停用词表中的每个词。内置三张英文表：`lucene_english`、`nltk_english` 和 `iso_english`。其他语言或特定领域的停用词，可以自己建表，每行一个词；匹配是精确的，区分大小写。

```sql
SELECT tokenizer_catalog.create_stopwords('my_stopwords', $$
it
is
an
$$);

SELECT tokenizer_catalog.create_text_analyzer('with_stopwords', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ stopwords = "my_stopwords" }]
$$);

SELECT tokenizer_catalog.apply_text_analyzer('It is an apple.', 'with_stopwords');
```

```text
{apple}
```

### 词干提取 {#stemmer}

`stemmer` 把每个词还原为 Snowball 词干，于是 "connected"、"connecting" 和 "connection" 都变成 "connect"。共有 [30 种算法](/zh/docs/tokenizer/reference/#stemmers)，英文用 `english_porter2`。词干提取器要求输入为小写。

### 同义词 {#synonym}

`synonym` 把词替换成指定的形式。同义词表每行以这个形式开头，后面跟着要映射到它的词；同一个词在一张表里只能出现一次。

```sql
SELECT tokenizer_catalog.create_synonym('db_terms', $$
postgres pgsql postgresql
index indices indexes
$$);

SELECT tokenizer_catalog.create_text_analyzer('with_synonyms', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ synonym = "db_terms" }]
$$);

SELECT tokenizer_catalog.apply_text_analyzer('PostgreSQL indexes', 'with_synonyms');
```

```text
{postgres,index}
```

`synonym` 要放在 `stemmer` 之前，这样同义词表里写的就是人们实际使用的词形。

### PostgreSQL 词典 {#pg_dict}

`pg_dict` 像 `ts_lexize` 一样，把每个词交给一个 PostgreSQL [全文检索词典](https://www.postgresql.org/docs/current/textsearch-dictionaries.html)处理：可以是 `german_stem` 这样的 Snowball 词典，Ispell、同义词和同义词库（thesaurus）词典，或者 `unaccent` 这类由扩展提供的词典。词典不认识的词原样通过，被词典判定为停用词的词会被删除。同义词库词典每次只看到一个词，所以只有单词条目生效。

创建分析器时，词典名按当前会话的 `search_path` 解析，并连同模式名一起保存。之后对词典本身的修改无需重连即可生效，但如果把词典改名或移到其他模式，就要重建分析器。

### N-gram {#ngram}

`ngram` 把每个词替换成长度从 `min_gram` 到 `max_gram` 个字符的所有子串，让查询能匹配词的一部分，比如标识符片段或产品编号。长度按字符计，不按字节计。短于 `min_gram` 的词不产生任何输出，除非用 `preserve_original = true` 保留原词。

```sql
SELECT tokenizer_catalog.create_text_analyzer('trigrams', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ ngram = { min_gram = 3, max_gram = 3 } }]
$$);
```

N-gram 会成倍增加每篇文档的词位数，索引也随之变大，范围要尽量窄。

### 标点 {#skip_non_alphanumeric}

`skip_non_alphanumeric` 删除不含任何字母或数字的词。`unicode_segmentation` 本身已经会这样做，所以只有在 `jieba`、`regex` 之后或没有预分词器时才需要它。

## 修改正在使用的分析器 {#change}

定义无法原地修改，基于它存储的值也不会自动重新计算。要修改一个已有存储数据依赖的分析器，用新名称创建新版本，再切换过去：

1. 创建新的分析器，例如 `en_text_v2`。
1. 加一列，填充数据并建索引：

   ```sql
   ALTER TABLE en_docs ADD COLUMN terms_v2 tsvector;
   UPDATE en_docs SET terms_v2 = tokenizer_catalog.analyze_to_tsvector(body, 'en_text_v2');
   CREATE INDEX en_docs_bm25_v2 ON en_docs USING bm25 (terms_v2 bm25_ops);
   ```

1. 让触发器和查询改用新的分析器、新列和新索引。
1. 删除旧列，再用 `drop_text_analyzer('en_text')` 删除旧分析器。
{.steps}

表不大时，也可以在一个事务里以同一名称删除并重建分析器，再对原有列执行 `UPDATE`。在 `UPDATE` 完成之前，用新定义分析的查询会与用旧定义分析的文档相比较。

删除分析器时不会检查谁在使用它。引用它的分词器、自定义模型或触发器下次使用时会报 `TextAnalyzer not found: <name>`。
