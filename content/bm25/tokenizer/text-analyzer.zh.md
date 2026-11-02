---
title: "文本分析器与过滤器"
description: "pg_tokenizer 中字符过滤器、预分词器与词元过滤器的完整配置参考手册。"
weight: 20
---

**文本分析器（Text Analyzer）** 通过三个顺序阶段处理原始文本：

1. **字符过滤器（`character_filters`）** —— 对完整输入字符串执行零个或多个字符级转换。
2. **预分词器（`pre_tokenizer`）** —— 使用唯一的一个切分器将字符串切分为初始词元。
3. **词元过滤器（`token_filters`）** —— 对切分出的词元执行零个或多个转换、扩展或过滤操作。

```sql
SELECT create_text_analyzer('analyzer1', $$
character_filters = [
    "to_lowercase",
    { unicode_normalization = "nfkd" },
]
pre_tokenizer = "unicode_segmentation"
token_filters = [
    "skip_non_alphanumeric",
    { stopwords = "nltk_english" },
    { stemmer = "english_porter2" },
]
$$);
```

> [!TIP]
> 在将文本分析器绑定到模型之前，你可以直接运行 `SELECT apply_text_analyzer('Sample text here', 'analyzer1');` 来测试并查看其输出的 `TEXT[]` 词元数组。

---

## 1. 字符过滤器（`character_filters`） {#1-character-filters-character_filters}

### `to_lowercase` {#to_lowercase}

将输入文本中的所有字符转换为小写。

```toml
character_filters = ["to_lowercase"]
# 或使用表语法：
[character_filters.to_lowercase]
```

### `unicode_normalization` {#unicode_normalization}

应用 Unicode 规范化形式（[UAX #15](https://www.unicode.org/reports/tr15/)），将组合/分解字符、重音符号以及全角/半角变体标准化。

支持的模式包括：
- `"nfc"` —— 规范化形式 C（标准分解后再执行标准组合）
- `"nfd"` —— 规范化形式 D（标准分解）
- `"nfkc"` —— 规范化形式 KC（兼容性分解后再执行标准组合）
- `"nfkd"` —— 规范化形式 KD（兼容性分解）

```toml
[[character_filters]]
unicode_normalization = "nfkd"
```

---

## 2. 预分词器（`pre_tokenizer`） {#2-pre-tokenizers-pre_tokenizer}

每个文本分析器**最多只能指定一个** `pre_tokenizer`。

### `unicode_segmentation` {#unicode_segmentation}

按照 [Unicode 标准附件 #29 (UAX #29)](https://www.unicode.org/reports/tr29/) 规范（底层基于 Rust `unicode-segmentation` 库）在 Unicode 词边界处切分文本。非常适合以空格分隔的西方语言。

```toml
pre_tokenizer = "unicode_segmentation"
# 或：
[pre_tokenizer.unicode_segmentation]
```

### `regex` {#regex}

提取匹配自定义正则表达式的词元（底层基于 Rust [`regex`](https://docs.rs/regex) 库）：

```toml
[pre_tokenizer]
regex = '''\w+'''
```

### `jieba`（中文结巴分词） {#jieba-chinese-word-segmentation}

使用 [`jieba-rs`](https://docs.rs/jieba-rs) 词典与隐马尔可夫模型（HMM）将中文文本切分为词语：

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `mode` | `string` | `"search"` | `"full"`（调用标准 `jieba.cut` 分词）、`"precise"`（调用 `jieba.cut_all` 扫描句中所有可成词的词语）或 `"search"`（搜索引擎模式，调用 `jieba.cut_for_search` 对长词再次切分以提高检索召回率）。 |
| `enable_hmm` | `bool` | `true` | 是否启用 HMM 新词发现能力（仅在 `"full"` 和 `"search"` 模式下生效）。 |

```toml
[pre_tokenizer.jieba]
mode = "search"
enable_hmm = true
```

---

## 3. 词元过滤器（`token_filters`） {#3-token-filters-token_filters}

词元过滤器会严格按照 TOML 数组中声明的顺序依次执行。

### `skip_non_alphanumeric` {#skip_non_alphanumeric}

丢弃不包含任何字母或数字字符的词元（例如分词后残留的独立标点符号 `,`、`.`、`!` 等）。

```toml
[[token_filters]]
skip_non_alphanumeric = {}
# 或使用数组简写形式：
token_filters = ["skip_non_alphanumeric"]
```

### `stemmer`（Snowball 词干提取 —— 支持 30 种语言） {#stemmer-snowball-stemming--30-languages}

使用 [Snowball 词干提取算法](https://snowballstem.org/)将屈折变化的单词还原为其词干形式。

```toml
[[token_filters]]
stemmer = "english_porter2"
```

支持的 `stemmer` 取值如下：

| 语言 | `stemmer` 取值 | 语言 | `stemmer` 取值 |
| :--- | :--- | :--- | :--- |
| 阿拉伯语 (Arabic) | `arabic` | 立陶宛语 (Lithuanian) | `lithuanian` |
| 亚美尼亚语 (Armenian) | `armenian` | 尼泊尔语 (Nepali) | `nepali` |
| 巴斯克语 (Basque) | `basque` | 挪威语 (Norwegian) | `norwegian` |
| 加泰罗尼亚语 (Catalan) | `catalan` | 葡萄牙语 (Portuguese) | `portuguese` |
| 丹麦语 (Danish) | `danish` | 罗马尼亚语 (Romanian) | `romanian` |
| 荷兰语 (Dutch) | `dutch` | 俄语 (Russian) | `russian` |
| 英语 (English Porter) | `english_porter` | 塞尔维亚语 (Serbian) | `serbian` |
| **英语 (English Porter2)** | **`english_porter2`** | 西班牙语 (Spanish) | `spanish` |
| 世界语 (Esperanto) | `esperanto` | 瑞典语 (Swedish) | `swedish` |
| 爱沙尼亚语 (Estonian) | `estonian` | 泰米尔语 (Tamil) | `tamil` |
| 芬兰语 (Finnish) | `finnish` | 土耳其语 (Turkish) | `turkish` |
| 法语 (French) | `french` | 意第绪语 (Yiddish) | `yiddish` |
| 德语 (German) | `german` | | |
| 希腊语 (Greek) | `greek` | | |
| 印地语 (Hindi) | `hindi` | | |
| 匈牙利语 (Hungarian) | `hungarian` | | |
| 印度尼西亚语 (Indonesian) | `indonesian` | | |
| 爱尔兰语 (Irish) | `irish` | | |
| 意大利语 (Italian) | `italian` | | |

### `stopwords`（停用词过滤） {#stopwords}

移除几乎不携带有效语义信号的常见停用词。

- **内置停用词典**：
  - `"lucene_english"` —— Apache Lucene 标准英文停用词表
  - `"nltk_english"` —— NLTK 标准英文停用词表
  - `"iso_english"` —— Stopwords ISO 英文停用词表
- **自定义停用词典**：通过 `create_stopwords(name, text)` 创建（每行一个词），随后按名称引用。

```sql
-- 创建自定义停用词表（每行一个词）
SELECT create_stopwords('my_stopwords', $$
it
is
a
an
the
$$);

SELECT create_text_analyzer('text_analyzer1', $$
pre_tokenizer = "unicode_segmentation"
[[token_filters]]
stopwords = "my_stopwords"
$$);

SELECT apply_text_analyzer('it is a cat', 'text_analyzer1');
-- 输出：{cat}
```

### `synonym`（同义词归一） {#synonym}

将同义词组归一化为同一个标准词元。使用 `create_synonym(name, text)` 创建同义词典，其中每行包含以空格分隔的一组同义词（同一行中的所有词都会被替换为该行的**第一个**词）：

```sql
SELECT create_synonym('my_synonym', $$
postgres pgsql postgresql
index indices
$$);

SELECT create_text_analyzer('text_analyzer2', $$
pre_tokenizer = "unicode_segmentation"
[[token_filters]]
synonym = "my_synonym"
$$);

SELECT apply_text_analyzer('pgsql and postgresql have many indices', 'text_analyzer2');
-- 输出：{postgres,and,postgres,have,many,index}
```

### `pg_dict`（PostgreSQL 全文检索词典） {#pg_dict-postgresql-full-text-dictionaries}

将词元过滤委托给任意已有的 [PostgreSQL 全文检索词典](https://www.postgresql.org/docs/current/textsearch-dictionaries.html)（`pg_ts_dict`，支持 `Simple`、`Ispell`、`Snowball` 和 `Synonym` 词典；注意不支持 `Thesaurus` 分类词典，因为后者作用于多词短语而非单个词元）：

```toml
[[token_filters]]
pg_dict = "english_stem"
```

### `ngram` {#ngram}

将每个词元切分为字符级 N-gram（适用于子串匹配、前缀匹配、无词典 CJK 检索，或代码/标识符检索）：

| 参数 | 类型 | 默认值 | 取值范围 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `min_gram` | `int` | `1` | `1..=255` (`<= max_gram`) | 生成 N-gram 的最小字符长度。 |
| `max_gram` | `int` | `2` | `1..=255` (`>= min_gram`) | 生成 N-gram 的最大字符长度。 |
| `preserve_original` | `bool` | `false` | `true` / `false` | 当原始词元长度不在 `[min_gram, max_gram]` 范围内时，是否同时保留未切分的原始词元。 |

```toml
[[token_filters.ngram]]
min_gram = 2
max_gram = 3
preserve_original = true
```
