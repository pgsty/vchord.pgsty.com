---
title: "SQL 与 TOML 参考"
description: "pg_tokenizer 中全部 tokenizer_catalog SQL 函数与 TOML 配置选项的完整参考手册。"
weight: 50
icon: fa-solid fa-book
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/00-reference.md"
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
{.wide .expand}

### 分词模型与预加载管理 {#tokenization-models--preloading}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_custom_model(name TEXT, config TEXT)` | `VOID` | 基于现有数据表列构建自定义词表模型。 |
| `tokenizer_catalog.create_custom_model_tokenizer_and_trigger(tokenizer_name TEXT, model_name TEXT, text_analyzer_name TEXT, table_name TEXT, source_column TEXT, target_column TEXT [, filter TEXT])` | `VOID` | 一键创建自定义词表模型与分词器，回填 `target_column`，并安装自动更新触发器。1.0.0 增加可选的第七个 `filter` 参数；省略或传入 SQL NULL 表示处理全部行，原六参签名继续可用。 |
| `tokenizer_catalog.drop_custom_model(name TEXT)` | `VOID` | 删除自定义词表模型及其关联触发器（即使源表已提前删除也能正常执行）。 |
| `tokenizer_catalog.create_huggingface_model(name TEXT, config TEXT)` | `VOID` | 导入 HuggingFace `tokenizer.json` 模型定义。 |
| `tokenizer_catalog.drop_huggingface_model(name TEXT)` | `VOID` | 删除已导入的 HuggingFace 模型。 |
| `tokenizer_catalog.create_lindera_model(name TEXT, config TEXT)` | `VOID` | 根据 TOML 配置创建 Lindera 形态学分词模型。 |
| `tokenizer_catalog.drop_lindera_model(name TEXT)` | `VOID` | 删除 Lindera 模型。 |
| `tokenizer_catalog.add_preload_model(name TEXT)` | `VOID` | 将模型加入集群预加载列表（仅管理员，不随事务回滚，重启生效）。 |
| `tokenizer_catalog.remove_preload_model(name TEXT)` | `VOID` | 将模型移出集群预加载列表（仅管理员，不随事务回滚）。 |
| `tokenizer_catalog.list_preload_models()` | `TEXT[]` | 列出当前已注册预加载的所有模型名称。 |
{.wide .expand}

### 分词器执行函数 {#tokenizer-execution}

| 函数签名 | 返回类型 | 说明 |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_tokenizer(name TEXT, config TEXT)` | `VOID` | 创建分词器（组合可选的 `text_analyzer` 与必选的 `model`）。 |
| `tokenizer_catalog.drop_tokenizer(name TEXT)` | `VOID` | 按名称删除分词器。 |
| `tokenizer_catalog.tokenize(text TEXT, tokenizer_name TEXT)` | `INT[]` | 将 `text` 分词为整数词元 ID 数组（可隐式转换为 `bm25vector`）。 |
{.wide .expand}

### 原生全文检索接口 {#native-full-text-search}

| 接口 | 返回类型 | 行为 |
| :--- | :--- | :--- |
| `tokenizer_catalog.analyze_to_tsvector(text TEXT, text_analyzer_name TEXT)` | `TSVECTOR` | 将分析器输出的字符串词元转换为带位置的原生词素。 |
| `tokenizer_catalog.tokenize_to_tsvector(text TEXT, tokenizer_name TEXT)` | `TSVECTOR` | 将模型输出的词元 ID 转为十进制词素，并按最终输出序列编号。 |
{.wide .expand}

这两个函数均为 `STABLE`，因为会读取目录中的定义。空词元会被忽略，剩余输出从位置 1 开始连续编号；位置表示最终分析器/模型输出，不是源文本偏移。应先将结果存入列，再创建 GIN/GiST 或兼容 BM25 索引，并用相同的词素表示生成查询。

---

## TOML 配置参数参考 {#toml-configuration-options}

### `text_analyzer` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `character_filters` | 表数组 / 字符串数组 | 字符级过滤转换（`to_lowercase`、`unicode_normalization = "nfc" \| "nfd" \| "nfkc" \| "nfkd"`）。 |
| `pre_tokenizer` | 表 / 字符串 | 初始分词切分器（`unicode_segmentation`、`regex = "..."` 或 `jieba`）。 |
| `token_filters` | 表数组 / 字符串数组 | 词元级过滤器（`skip_non_alphanumeric`、`stemmer`、`stopwords`、`synonym`、`pg_dict`、`ngram`）。 |
{.wide .expand}

### `tokenizer` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `text_analyzer` | 字符串 | 已创建的 `text_analyzer` 名称（或内联 `[text_analyzer]` 表）。使用独立子词模型时无需配置。 |
| `model` | 字符串 | 内置预训练模型（`llmlingua2`、`bert_base_uncased`、`wiki_tocken`、`gemma2b`）或自定义/HuggingFace/Lindera 模型名称。 |
{.wide .expand}

### `custom_model` 配置项

| 键名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `table` | 字符串 | 存放训练语料的数据表名称，支持带模式名的表名及带引号的标识符。 |
| `column` | 字符串 | 存放原始文本的 `TEXT` 列名称。 |
| `text_analyzer` | 字符串 | 用于提取词表词元的 `text_analyzer` 名称。 |
| `filter` | 字符串 | 可选的可信 SQL 布尔表达式，不包含 `WHERE` 或 `NEW.`。只有结果为 TRUE 的行参与训练和 embedding 更新；FALSE/NULL 会跳过，词表只增不减。 |
{.wide .expand}

## 并发、过滤与缓存语义 {#api-semantics}

只有新增词元的写入会在每个模型上获取事务级咨询锁，并按 `COLLATE "C"` 排序新词元；同一模型的新增词元操作会在事务内串行化。`READ COMMITTED` 下，触发器会在等待词表写入后刷新快照；`REPEATABLE READ` 或 `SERIALIZABLE` 遇到冲突时可能返回 SQLSTATE `40001`，应用应重试整个事务。过滤条件同时作用于初始词表、回填和后续写入；不匹配行的既有 embedding 与词表条目不会自动删除。

从 1.1.0 起，`tokenizer_catalog.definition_version` 中的一行事务性版本号与定义变更一同复制。主库和热备连接都在当前 SQL 快照下核对分析器、分词器、模型、停用词及同义词缓存；长连接在新提交对其快照可见时刷新，promotion 后也保持这一行为。旧的 REPEATABLE READ 快照、延迟或暂停回放的备库仍会读取旧定义。协调主备定义变更时，需要等待主库提交 LSN 回放完成并开始新快照。输出改变后，持久化向量和索引仍需显式重算或重建。

版本检查每条语句读取一行，不会逐词扫描定义表。修改定义的事务在版本行上串行化，每条修改语句增加一次 heap/WAL 更新；普通词表插入不更新版本行。写目录的函数均标记为 `PARALLEL UNSAFE`，只读分析保留 `PARALLEL SAFE`。修改定义的 API 仍不允许 `PREPARE TRANSACTION`。

## 分析资源预算 {#analysis-budgets}

| 会话参数 | 默认值 | 预算范围 |
| --- | ---: | --- |
| `pg_tokenizer.max_input_bytes` | 16,777,216 | 单次分析器输入的 UTF-8 字节数 |
| `pg_tokenizer.max_output_tokens` | 1,000,000 | 每个阶段的词元或 ID 数量 |
| `pg_tokenizer.max_output_bytes` | 67,108,864 | 词元字节与 String 描述符、ID 字节、字符输出或 ngram 偏移表 |
| `pg_tokenizer.max_piece_bytes` | 1,048,576 | 单次 regex、第三方库或 PostgreSQL 词典调用的输入字节数 |

超限返回 SQLSTATE `54000`，不会静默截断结果。检查约束扩展自己构建的中间结果、ngram 扩张及 HF 固定 padding，但不构成 backend RSS 硬上限：同时存在的缓冲区、缓存模型和库内部工作区仍占内存。任意 HF normalizer/postprocessor 可能在输出检查前分配内部内存。单次 regex 搜索或 Jieba/Lindera/HF/词典调用仍可能延迟取消；应使用可信模型配置并限制文档大小，调高预算会增加内存暴露。
