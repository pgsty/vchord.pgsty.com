---
title: "SQL & TOML Reference"
description: "Complete reference for all tokenizer_catalog SQL functions and TOML configuration options in pg_tokenizer."
weight: 50
icon: fa-solid fa-book
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/00-reference.md"
---

## SQL Functions (`tokenizer_catalog`)

### Text Analyzer & Dictionaries

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_text_analyzer(name TEXT, config TEXT)` | `VOID` | Creates a named text analyzer pipeline from a TOML string. |
| `tokenizer_catalog.drop_text_analyzer(name TEXT)` | `VOID` | Drops a text analyzer by name. |
| `tokenizer_catalog.apply_text_analyzer(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | Splits and filters `text` using the named text analyzer for inspection/debugging. |
| `tokenizer_catalog.create_stopwords(name TEXT, config TEXT)` | `VOID` | Creates a custom stopword dictionary (one word per line). |
| `tokenizer_catalog.drop_stopwords(name TEXT)` | `VOID` | Drops a custom stopword dictionary. |
| `tokenizer_catalog.create_synonym(name TEXT, config TEXT)` | `VOID` | Creates a custom synonym dictionary (space-separated synonyms per line). |
| `tokenizer_catalog.drop_synonym(name TEXT)` | `VOID` | Drops a custom synonym dictionary. |
{.wide .expand}

### Tokenization Models & Preloading

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_custom_model(name TEXT, config TEXT)` | `VOID` | Builds a custom vocabulary model on an existing table column. |
| `tokenizer_catalog.create_custom_model_tokenizer_and_trigger(tokenizer_name TEXT, model_name TEXT, text_analyzer_name TEXT, table_name TEXT, source_column TEXT, target_column TEXT [, filter TEXT])` | `VOID` | Creates a custom model and tokenizer, backfills `target_column`, and installs triggers. Version 1.0.0 adds the optional SQL predicate; omit it or pass NULL to include all rows. The original six-argument signature remains available. |
| `tokenizer_catalog.drop_custom_model(name TEXT)` | `VOID` | Drops a custom vocabulary model and its associated triggers (succeeds even if the source table has already been dropped). |
| `tokenizer_catalog.create_huggingface_model(name TEXT, config TEXT)` | `VOID` | Imports a HuggingFace `tokenizer.json` model specification. |
| `tokenizer_catalog.drop_huggingface_model(name TEXT)` | `VOID` | Drops an imported HuggingFace model. |
| `tokenizer_catalog.create_lindera_model(name TEXT, config TEXT)` | `VOID` | Creates a Lindera morphological analyzer model from TOML config. |
| `tokenizer_catalog.drop_lindera_model(name TEXT)` | `VOID` | Drops a Lindera model. |
| `tokenizer_catalog.add_preload_model(name TEXT)` | `VOID` | Adds a model to the cluster-wide preload list (administrator only, nontransactional; restart required). |
| `tokenizer_catalog.remove_preload_model(name TEXT)` | `VOID` | Removes a model from the cluster-wide preload list (administrator only, nontransactional). |
| `tokenizer_catalog.list_preload_models()` | `TEXT[]` | Lists all models currently registered for preloading. |
{.wide .expand}

### Tokenizer Execution

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `tokenizer_catalog.create_tokenizer(name TEXT, config TEXT)` | `VOID` | Creates a tokenizer combining an optional `text_analyzer` and a `model`. |
| `tokenizer_catalog.drop_tokenizer(name TEXT)` | `VOID` | Drops a tokenizer by name. |
| `tokenizer_catalog.tokenize(text TEXT, tokenizer_name TEXT)` | `INT[]` | Tokenizes `text` into an array of integer token IDs (implicitly castable to `bm25vector`). |
{.wide .expand}

### Native full-text search {#native-full-text-search}

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `tokenizer_catalog.analyze_to_tsvector(text TEXT, text_analyzer_name TEXT)` | `TSVECTOR` | Analyzer string tokens as native lexemes, with output positions. |
| `tokenizer_catalog.tokenize_to_tsvector(text TEXT, tokenizer_name TEXT)` | `TSVECTOR` | Model IDs as decimal lexemes, with output positions. |
{.wide .expand}

These functions are `STABLE` because they read tokenizer definitions from the catalog. Store the result in a column before creating a GIN/GiST or compatible BM25 index; use the same lexeme representation for documents and queries. Positions are assigned consecutively after empty output tokens are omitted, and positions describe the final analyzer/model output rather than source-text offsets. See [positions and native limits](/docs/tokenizer/overview/#native-postgresql-full-text-search).

---

## TOML Configuration Options

### `text_analyzer` Options

| Key | Type | Description |
| :--- | :--- | :--- |
| `character_filters` | Array of Table / String | Character-level transformations (`to_lowercase`, `unicode_normalization = "nfc" \| "nfd" \| "nfkc" \| "nfkd"`). |
| `pre_tokenizer` | Table / String | Initial token splitter (`unicode_segmentation`, `regex = "..."`, or `jieba`). |
| `token_filters` | Array of Table / String | Token-level filters (`skip_non_alphanumeric`, `stemmer`, `stopwords`, `synonym`, `pg_dict`, `ngram`). |
{.wide .expand}

### `tokenizer` Options

| Key | Type | Description |
| :--- | :--- | :--- |
| `text_analyzer` | String | Name of a pre-created `text_analyzer` (or inline `[text_analyzer]` table). Omit for standalone subword models. |
| `model` | String | Built-in model (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`) or custom/HuggingFace/Lindera model name. |
{.wide .expand}

### `custom_model` Options

| Key | Type | Description |
| :--- | :--- | :--- |
| `table` | String | Source table name containing training documents; schema-qualified names and quoted identifiers are supported. |
| `column` | String | Source `TEXT` column name. |
| `text_analyzer` | String | Name of the `text_analyzer` used to extract vocabulary tokens. |
| `filter` | String | Optional trusted SQL Boolean expression over source columns, without `WHERE` or `NEW.` (1.0.0). Only `TRUE` rows are used for training and embedding updates; `FALSE` and `NULL` rows are skipped. The vocabulary is append-only. |
{.wide .expand}

## Definition caches and resource budgets {#definition-caches}

In 1.1.0, a transactional counter in `tokenizer_catalog.definition_version` is replicated with definition changes. Primary and hot-standby connections validate cached analyzers, tokenizers, models, stopwords and synonyms against their current SQL snapshot. Long-lived connections refresh after the commit is visible; promotion keeps this behavior. An old REPEATABLE READ snapshot or a lagging/paused replica still sees the old definition. Wait for the primary commit LSN to replay and begin a new snapshot when coordinating changes. Persisted vectors and indexes require explicit regeneration if output changes.

The version check reads one row per statement, rather than scanning definitions per token. Definition-changing transactions serialize on that row and add one heap/WAL update per modifying statement; vocabulary inserts do not. Catalog-writing functions are `PARALLEL UNSAFE`, while read-only analysis remains `PARALLEL SAFE`. Definition-changing API calls still reject `PREPARE TRANSACTION`.

| Session setting | Default | Budget |
| --- | ---: | --- |
| `pg_tokenizer.max_input_bytes` | 16,777,216 | Bytes in one analyzer input |
| `pg_tokenizer.max_output_tokens` | 1,000,000 | Tokens or IDs in each stage |
| `pg_tokenizer.max_output_bytes` | 67,108,864 | Token bytes plus String descriptors, ID bytes, character output or ngram offsets |
| `pg_tokenizer.max_piece_bytes` | 1,048,576 | Input to one regex or opaque library/dictionary call |

Exceeding a budget raises SQLSTATE `54000` without truncating output. These checks bound extension-owned stages, including ngram expansion and HF fixed padding, but do not impose a hard RSS limit: simultaneous buffers, cached models and library workspace add memory. Arbitrary HF normalizers/post-processors can allocate internally before output is checked. A single regex search, Jieba/Lindera/HF call or dictionary call can still delay cancellation. Use trusted model configurations and bounded documents; raising the limits increases memory exposure.
