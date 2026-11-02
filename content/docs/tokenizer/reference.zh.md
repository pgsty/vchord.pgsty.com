---
title: "SQL 与 TOML 参考"
description: "pg_tokenizer 中全部 tokenizer_catalog SQL 函数与 TOML 配置选项的完整参考手册。"
weight: 50
icon: fa-solid fa-book
upstream_link: "https://github.com/tensorchord/pg_tokenizer.rs/blob/main/docs/00-reference.md"
---

## SQL 函数参考（`tokenizer_catalog`） {#sql-functions}

### 文本分析器与词典管理 {#text-analyzer--dictionaries}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_text_analyzer(name TEXT, config TEXT)` | `VOID` | 根据 TOML 配置字符串创建命名文本分析器流水线。 |
| `tokenizer_catalog.drop_text_analyzer(name TEXT)` | `VOID` | 按名称删除文本分析器。 |
| `tokenizer_catalog.apply_text_analyzer(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | 使用指定文本分析器切分并过滤 `text`，返回词元数组以供调试预览。 |
| `tokenizer_catalog.create_stopwords(name TEXT, config TEXT)` | `VOID` | 创建自定义停用词词典（每行一个停用词）。 |
| `tokenizer_catalog.drop_stopwords(name TEXT)` | `VOID` | 删除自定义停用词词典。 |
| `tokenizer_catalog.create_synonym(name TEXT, config TEXT)` | `VOID` | 创建自定义同义词词典（每行一组以空格分隔的同义词，统一映射为首词）。 |
| `tokenizer_catalog.drop_synonym(name TEXT)` | `VOID` | 删除自定义同义词词典。 |

### 分词模型与预加载管理 {#tokenization-models--preloading}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_custom_model(name TEXT, config TEXT)` | `VOID` | 基于现有数据表列构建自定义词表模型。 |
| `tokenizer_catalog.create_custom_model_tokenizer_and_trigger(tokenizer_name TEXT, model_name TEXT, text_analyzer_name TEXT, table_name TEXT, source_column TEXT, target_column TEXT)` | `VOID` | 一键创建自定义词表模型与分词器，回填 `target_column`，并在 `source_column` 上安装自动更新触发器。 |
| `tokenizer_catalog.drop_custom_model(name TEXT)` | `VOID` | 删除自定义词表模型。 |
| `tokenizer_catalog.create_huggingface_model(name TEXT, config TEXT)` | `VOID` | 导入 HuggingFace `tokenizer.json` 模型定义。 |
| `tokenizer_catalog.drop_huggingface_model(name TEXT)` | `VOID` | 删除已导入的 HuggingFace 模型。 |
| `tokenizer_catalog.create_lindera_model(name TEXT, config TEXT)` | `VOID` | 根据 TOML 配置创建 Lindera 形态学分词模型。 |
| `tokenizer_catalog.drop_lindera_model(name TEXT)` | `VOID` | 删除 Lindera 模型。 |
| `tokenizer_catalog.add_preload_model(name TEXT)` | `VOID` | 将模型加入共享内存预加载列表（重启 PostgreSQL 后生效）。 |
| `tokenizer_catalog.remove_preload_model(name TEXT)` | `VOID` | 将模型移出预加载列表。 |
| `tokenizer_catalog.list_preload_models()` | `TEXT[]` | 列出当前已注册预加载的所有模型名称。 |

### 分词器执行函数 {#tokenizer-execution}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_tokenizer(name TEXT, config TEXT)` | `VOID` | 创建分词器（组合可选的 `text_analyzer` 与必选的 `model`）。 |
| `tokenizer_catalog.drop_tokenizer(name TEXT)` | `VOID` | 按名称删除分词器。 |
| `tokenizer_catalog.tokenize(text TEXT, tokenizer_name TEXT)` | `INT[]` | 将 `text` 分词为整数词元 ID 数组（可隐式转换为 `bm25vector`）。 |

---

## TOML 配置参数参考 {#toml-configuration-options}

### `text_analyzer` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `character_filters` | 表数组 / 字符串数组 | 字符级过滤转换（`to_lowercase`、`unicode_normalization = "nfc" \| "nfd" \| "nfkc" \| "nfkd"`）。 |
| `pre_tokenizer` | 表 / 字符串 | 初始分词切分器（`unicode_segmentation`、`regex = "..."` 或 `jieba`）。 |
| `token_filters` | 表数组 / 字符串数组 | 词元级过滤器（`skip_non_alphanumeric`、`stemmer`、`stopwords`、`synonym`、`pg_dict`、`ngram`）。 |

### `tokenizer` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `text_analyzer` | 字符串 | 已创建的 `text_analyzer` 名称（或内联 `[text_analyzer]` 表）。使用独立子词模型时无需配置。 |
| `model` | 字符串 | 内置预训练模型（`llmlingua2`、`bert_base_uncased`、`wiki_tocken`、`gemma2b`）或自定义/HuggingFace/Lindera 模型名称。 |

### `custom_model` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `table` | 字符串 | 存放训练语料的数据表名称。 |
| `column` | 字符串 | 存放原始文本的 `TEXT` 列名称。 |
| `text_analyzer` | 字符串 | 用于提取词表词元的 `text_analyzer` 名称。 |

## 0.1.2 新增接口（未发布） {#api-012}

| 接口 | 返回类型 | 行为 |
| :--- | :--- | :--- |
| `tokenizer_catalog.analyze_to_tsvector(text TEXT, text_analyzer_name TEXT)` | `TSVECTOR` | 将分析器输出的字符串词元转换为带位置的原生词素。 |
| `tokenizer_catalog.tokenize_to_tsvector(text TEXT, tokenizer_name TEXT)` | `TSVECTOR` | 将模型输出的词元 ID 转为十进制词素，保留输出位置。 |

两个函数均为 `STABLE`；先存入列，再为该列创建 GIN/GiST 索引。文档与查询必须采用相同的词素表示，详见[原生全文检索](/zh/docs/tokenizer/overview/#native-fts)。

`create_custom_model` 的 TOML 配置新增可选字符串 `filter`，内容为源表列上的 SQL 布尔表达式，不包含 `WHERE` 或 `NEW.`。`create_custom_model_tokenizer_and_trigger` 新增七参重载，最后一参为 `filter TEXT`；原六参调用继续可用，省略过滤条件或传入 SQL NULL 表示选取全部行。`table` 支持带模式名的表名。详见[过滤与并发语义](/zh/docs/tokenizer/models/#custom-model-012)。
