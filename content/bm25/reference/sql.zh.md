---
math: true
title: "SQL 参考手册"
description: "vchord_bm25 与 pg_tokenizer 的完整 SQL 数据类型、操作符、类型转换、索引访问方法与函数参考。"
weight: 10
---

## `vchord_bm25` 数据类型 {#vchord_bm25-data-types}

| 数据类型 | 所属模式 | 适用版本 | 文本表示形式 / 内部结构 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `bm25vector` | `bm25_catalog` | `v0.1.0` – `v0.3.0` | `{token_id:freq, ...}`（例如 `{1:1, 2:2, 15:1}`） | 将 32 位无符号词元 ID 映射为 32 位词频的稀疏向量。存储策略为 `STORAGE = EXTERNAL`。 |
| `bm25query` | `bm25_catalog` | `v0.1.0` – `v0.3.0` | `(index_oid regclass, query_vector bm25vector)` | 将目标 `bm25` 索引 OID 与查询 `bm25vector` 配对的复合类型。 |
| `bm25query` | `public` / 扩展模式 | `main` | `(vector tsvector, index regclass)` | 将查询 `tsvector` 与目标 `bm25` 索引 OID 配对的复合类型。 |

### `bm25vector` 字面量语法（`v0.1` – `v0.3`） {#bm25vector-literal-syntax-v01--v03}

```sql
-- 空 bm25vector
SELECT '{}'::bm25vector;

-- 显式指定 token_id:frequency 键值对
SELECT '{1:1, 2:3, 10:2}'::bm25vector;

-- 从 int[] 隐式转换（自动将重复的词元 ID 聚合为词频计数）
SELECT ARRAY[1, 2, 2, 2, 10, 10]::bm25vector;
-- 输出：{1:1, 2:3, 10:2}
```

---

## `vchord_bm25` 操作符 {#vchord_bm25-operators}

| 操作符 | 左操作数 | 右操作数 | 返回类型 | 适用版本 | 说明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `<&>` | `bm25vector` | `bm25query` | `real` (`f32`) | `v0.1.0` – `v0.3.0` | 计算**负值** BM25 相关性得分（$-\text{BM25}(D, Q)$）。支持使用 `bm25_ops` 执行索引加速的 `ORDER BY ... ASC` 扫描。 |
| `<&>` | `tsvector` | `bm25query` | `float8` (`f64`) | `main` | 在原生 `tsvector` 上计算**负值** BM25 相关性得分。支持使用 `bm25_ops` 执行索引加速的 `ORDER BY ... ASC` 扫描。 |
| `=` | `bm25vector` | `bm25vector` | `bool` | `v0.2.0` – `v0.3.0` | 比较两个 `bm25vector` 值是否完全相等。 |
| `<>` | `bm25vector` | `bm25vector` | `bool` | `v0.2.0` – `v0.3.0` | 比较两个 `bm25vector` 值是否不相等。 |

---

## `vchord_bm25` 函数 {#vchord_bm25-functions}

| 函数签名 | 返回类型 | 适用版本 | 说明 |
| :--- | :--- | :--- | :--- |
| `to_bm25query(index_oid regclass, query_vector bm25vector)` | `bm25query` | `v0.1.1` – `v0.3.0` | 根据 `bm25` 索引名称/OID 与查询 `bm25vector`（或经由隐式转换的 `INT[]`）构造 `bm25query`。 |
| `to_bm25query(index_oid regclass, query_vector int[])` | `bm25query` | `v0.3.0+` | 直接接受 `INT[]` 词元 ID 数组的显式重载函数。 |
| `to_bm25query(vector tsvector, index regclass)` | `bm25query` | `main` | 根据原生 `tsvector` 与目标 `bm25` 索引名称/OID 构造 `bm25query`。 |
| `search_bm25query(target_vector bm25vector, query bm25query)` | `real` | `v0.1.0` – `v0.3.0` | `bm25vector <&> bm25query` 操作符的底层实现函数。 |
| `_bm25_evaluate(left tsvector, right bm25query)` | `float8` | `main` | `tsvector <&> bm25query` 操作符的底层实现函数。 |
| `bm25_page_inspect(index regclass, blkno int)` | `text` | `v0.3.0` | 返回 `bm25` 索引第 `blkno` 号数据块的可读诊断元数据。 |

---

## `vchord_bm25` 访问方法与操作符类 {#vchord_bm25-access-method--operator-class}

| 对象类型 | 名称 | 目标类型 | 排序操作符 |
| :--- | :--- | :--- | :--- |
| 访问方法 (Access Method) | `bm25` | 索引 (Index) | 处理器 `_bm25_amhandler` |
| 操作符族 (Operator Family) | `bm25_ops` | `USING bm25` | `OPERATOR 1 pg_catalog.<&> FOR ORDER BY float_ops` |
| 操作符类 (Operator Class) | `bm25_ops` | `bm25vector`（`v0.1`–`v0.3`）/ `tsvector`（`main`） | `USING bm25` 的默认操作符类 |

---

## `pg_tokenizer` 函数（`tokenizer_catalog`） {#pg_tokenizer-functions-tokenizer_catalog}

所有 `pg_tokenizer` 函数均位于 `tokenizer_catalog` 模式中：

### 分词器管理与执行 {#tokenizer-management--execution}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `create_tokenizer(name TEXT, config TEXT)` | `void` | 根据 TOML 配置字符串创建一个命名分词器。 |
| `drop_tokenizer(name TEXT)` | `void` | 删除已有的分词器。 |
| `tokenize(text TEXT, tokenizer_name TEXT)` | `INT[]` | 使用 `tokenizer_name` 对 `text` 进行分词，返回整数词元 ID 数组（可隐式转换为 `bm25vector`）。 |

### 文本分析器管理 {#text-analyzer-management}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `create_text_analyzer(name TEXT, config TEXT)` | `void` | 创建可复用的命名文本分析器流水线（包含 `character_filters`、`pre_tokenizer`、`token_filters`）。 |
| `drop_text_analyzer(name TEXT)` | `void` | 删除指定的命名文本分析器。 |
| `apply_text_analyzer(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | 对 `text` 运行指定的文本分析器，返回归一化后的字符串词元数组（常用于调试分词效果）。 |

### 模型管理 {#model-management}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `create_custom_model(name TEXT, config TEXT)` | `void` | 使用指定的文本分析器，在现有表列上训练自定义词表模型。 |
| `drop_custom_model(name TEXT)` | `void` | 删除自定义模型及其底层词表数据表。 |
| `create_custom_model_tokenizer_and_trigger(tokenizer_name TEXT, model_name TEXT, text_analyzer_name TEXT, table_name TEXT, source_column TEXT, target_column TEXT)` | `void` | 一步创建自定义模型与分词器，回填 `table_name` 表中的 `target_column` 列，并绑定自动 `BEFORE INSERT OR UPDATE` 触发器。 |
| `create_huggingface_model(name TEXT, config TEXT)` | `void` | 从 HuggingFace `tokenizer.json` 字符串导入模型。 |
| `drop_huggingface_model(name TEXT)` | `void` | 删除已导入的 HuggingFace 模型。 |
| `create_lindera_model(name TEXT, config TEXT)` | `void` | 根据 TOML 配置创建 Lindera 形态学分析模型（如 `ipadic`）。 |
| `drop_lindera_model(name TEXT)` | `void` | 删除 Lindera 模型。 |

### 词典与预加载管理 {#dictionary--preload-management}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `create_stopwords(name TEXT, config TEXT)` | `void` | 创建自定义停用词典（每行一个停用词）。 |
| `drop_stopwords(name TEXT)` | `void` | 删除自定义停用词典。 |
| `create_synonym(name TEXT, config TEXT)` | `void` | 创建自定义同义词典（每行以空格分隔一组同义词，统一映射到该行第一个词）。 |
| `drop_synonym(name TEXT)` | `void` | 删除自定义同义词典。 |
| `add_preload_model(name TEXT)` | `void` | 注册在 PostgreSQL 服务启动（`shared_preload_libraries`）时预加载的模型。 |
| `remove_preload_model(name TEXT)` | `void` | 从启动预加载列表中移除指定模型。 |
| `list_preload_models()` | `TEXT[]` | 返回当前已注册为启动预加载的所有模型名称列表。 |

### 内部触发器与辅助函数（`tokenizer_catalog`） {#internal-trigger--helper-functions-tokenizer_catalog}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `apply_text_analyzer_for_custom_model(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | 调用 `text_analyzer_name` 分词，并在写入自定义模型词表前自动过滤掉长度超过 `2600` 字节（PostgreSQL B-tree `UNIQUE` 索引键最大长度限制）的超长词元。 |
| `custom_model_insert_trigger()` | `trigger` | `AFTER INSERT OR UPDATE` 触发器函数，从源文本列提取词元并将新出现的词元自动追加写入 `tokenizer_catalog."model_<name>"` 词表。 |
| `custom_model_tokenizer_set_target_column_trigger()` | `trigger` | 由 `create_custom_model_tokenizer_and_trigger` 安装的 `BEFORE INSERT OR UPDATE` 触发器函数，自动执行 `NEW.<target_column> = tokenize(NEW.<source_column>, tokenizer_name)`。 |

---

## `pg_tokenizer` 元数据表（`tokenizer_catalog`） {#pg_tokenizer-catalog-tables-tokenizer_catalog}

| 表名 | 列定义 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.tokenizer` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | 存储已注册的分词器名称及其序列化后的 JSON/TOML 配置。 |
| `tokenizer_catalog.text_analyzer` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | 存储独立命名且可复用的文本分析器定义。 |
| `tokenizer_catalog.model` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | 存储已注册的自定义模型、HuggingFace 模型与 Lindera 模型定义。 |
| `tokenizer_catalog.stopwords` | `name TEXT NOT NULL PRIMARY KEY`, `config TEXT NOT NULL` | 存储内置（`lucene_english`、`nltk_english`、`iso_english`）及自定义停用词典。 |
| `tokenizer_catalog.synonym` | `name TEXT NOT NULL PRIMARY KEY`, `config TEXT NOT NULL` | 存储自定义同义词典。 |
| `tokenizer_catalog."model_<name>"` | `id SERIAL PRIMARY KEY`, `token TEXT NOT NULL UNIQUE` | 为每个自定义模型 `<name>` 自动创建的底层词表数据表，将唯一归一化词元映射为从 1 开始的自增整数 ID。 |

---

## `pg_tokenizer` TOML 配置参数参考 {#pg_tokenizer-toml-configuration-reference}

### 分词器配置项（`create_tokenizer`） {#tokenizer-options-create_tokenizer}

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `text_analyzer` | `string`（可选） | 预先创建的命名 `text_analyzer` 名称。若省略，可在支持文本分析器的模型中直接内联定义 `character_filters`、`pre_tokenizer` 和 `token_filters`。 |
| `model` | `string`（必填） | 内置模型（`llmlingua2`、`bert_base_uncased`、`wiki_tocken`、`gemma2b`）或用户创建的模型（`custom`、`huggingface`、`lindera`）名称。 |

### 文本分析器配置项（`create_text_analyzer`） {#text-analyzer-options-create_text_analyzer}

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `character_filters` | `array` / `table` | 在分词前对整段字符串依次应用的字符过滤器列表：`to_lowercase`、`unicode_normalization`（`nfc`、`nfd`、`nfkc`、`nfkd`）。 |
| `pre_tokenizer` | `string` / `table` | 将字符串切分为初始词元的单个预分词器：`unicode_segmentation`、`regex`（Rust 正则表达式）或 `jieba`（`mode = "full" \| "precise" \| "search"`，`enable_hmm = true \| false`）。 |
| `token_filters` | `array` | 按顺序执行的词元过滤器列表：`skip_non_alphanumeric`、`stemmer`（支持 30 种 Snowball 词干提取器）、`stopwords`（内置 `lucene_english`、`nltk_english`、`iso_english` 或自定义停用词典）、`synonym`、`pg_dict`（除 `Thesaurus` 外的任意 `pg_ts_dict` 词典）、`ngram`（`min_gram`、`max_gram` 范围 `1..=255`，`preserve_original`）。 |

### 自定义模型配置项（`create_custom_model`） {#custom-model-options-create_custom_model}

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `table` | `string`（必填） | 包含源文本语料的目标表名称。 |
| `column` | `string`（必填） | `table` 表中用于构建词表的源 `TEXT` 列名称。 |
| `text_analyzer` | `string`（必填） | 用于将 `column` 列切分为词表词元的 `text_analyzer` 名称。 |
