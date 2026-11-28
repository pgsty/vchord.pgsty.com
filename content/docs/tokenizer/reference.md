---
title: "Reference"
linkTitle: "Reference"
description: "Every pg_tokenizer function, configuration key and setting, defined once."
weight: 60
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/00-reference.md"
icon: fa-solid fa-book
---

This page defines every function, configuration key and setting of pg_tokenizer 1.3.0. The guides explain when to use them: [Text analyzers](/docs/tokenizer/text-analyzer/), [Models](/docs/tokenizer/models/) and [Multilingual recipes](/docs/tokenizer/multilingual/).

## Functions {#sql-functions}

<a id="text-analyzer--dictionaries"></a><a id="tokenization-models--preloading"></a><a id="tokenizer-execution"></a><a id="native-full-text-search"></a><a id="api-semantics"></a>

All functions are in the schema `tokenizer_catalog`. Definitions are stored in tables of the current database.

`create_*` functions fail if the name is taken, with a message such as `Text analyzer already exists: en_text`; there is no replace, so drop and create again. `drop_*` functions only warn when the name does not exist, and do not check whether anything uses the definition. Both kinds are `VOLATILE` and `PARALLEL UNSAFE`.

### Analyze and tokenize {#tokenize-functions}

These four are `STABLE`, `STRICT` (a `NULL` argument returns `NULL`) and `PARALLEL SAFE`.

| Function | Returns | Description |
| --- | --- | --- |
| `apply_text_analyzer(text, text_analyzer_name)` | `text[]` | Runs the analyzer and returns the words in order. Use it to check an analyzer. |
| `analyze_to_tsvector(text, text_analyzer_name)` | `tsvector` | Runs the analyzer and returns the words as lexemes, numbered 1, 2, 3… in output order, with weight `D`. |
| `tokenize(text, tokenizer_name)` | `int[]` | Runs the tokenizer and returns its token IDs in order. |
| `tokenize_to_tsvector(text, tokenizer_name)` | `tsvector` | Runs the tokenizer and returns the IDs as decimal lexemes, numbered as in `analyze_to_tsvector`. |
{.fields meta="type"}

### Text analyzers, stopwords and synonyms {#text-analyzer-functions}

| Function | Returns | Description |
| --- | --- | --- |
| `create_text_analyzer(name, config)` | `void` | Creates an analyzer from a TOML [configuration](#text-analyzer-options). A `pg_dict` name is resolved with the current `search_path` and stored with its schema. |
| `drop_text_analyzer(name)` | `void` | Drops an analyzer. |
| `create_stopwords(name, config)` | `void` | Creates a stopword list: one word per line, matched exactly. |
| `drop_stopwords(name)` | `void` | Drops a stopword list. The built-in `lucene_english`, `nltk_english` and `iso_english` cannot be dropped or replaced. |
| `create_synonym(name, config)` | `void` | Creates a synonym list. Each line holds the form to output followed by the words that map to it, separated by spaces; a word may appear once per list. |
| `drop_synonym(name)` | `void` | Drops a synonym list. |
{.fields meta="type"}

### Tokenizers and models {#model-functions}

| Function | Returns | Description |
| --- | --- | --- |
| `create_tokenizer(name, config)` | `void` | Creates a tokenizer from a TOML [configuration](#tokenizer-options). |
| `drop_tokenizer(name)` | `void` | Drops a tokenizer. |
| `create_lindera_model(name, config)` | `void` | Creates a [Lindera](/docs/tokenizer/models/#lindera) model from a Lindera 7 TOML configuration. A dictionary read from a file requires superuser or `pg_read_server_files`. |
| `drop_lindera_model(name)` | `void` | Drops a Lindera model. |
| `create_huggingface_model(name, config)` | `void` | Creates a model from the contents of a Hugging Face `tokenizer.json`. Every ID, including added and special tokens and `padding.pad_id`, must be at most 2147483647. |
| `drop_huggingface_model(name)` | `void` | Drops a Hugging Face model. |
| `create_custom_model(name, config)` | `void` | Builds a vocabulary from a table column per its TOML [configuration](#custom-model-options) into `tokenizer_data."model_<name>"`, and adds the trigger `model_<name>_trigger` that adds new words. |
| `create_custom_model_tokenizer_and_trigger(tokenizer_name, model_name, text_analyzer_name, table_name, source_column, target_column [, filter])` | `void` | Runs `create_custom_model` and `create_tokenizer`, fills `target_column` with each row's IDs, and adds the trigger `model_<name>_trigger_insert` that keeps it current. `filter` is optional; `NULL` includes every row. |
| `drop_custom_model(name)` | `void` | Drops a custom model with its vocabulary table and triggers. Tokenizers that use it are kept. |
{.fields meta="type"}

Model names are shared by all model kinds: ASCII letters, digits and underscores, starting with a letter, at most 20 characters. `bert_base_uncased`, `gemma2b`, `llmlingua2` and `wiki_tocken` are the built-in models and cannot be reused.

### Preload list {#preload-functions}

| Function | Returns | Description |
| --- | --- | --- |
| `add_preload_model(name)` | `void` | Adds a built-in model, or a model of the current database, to the server's preload list. Takes effect at the next restart; the file is written even if the transaction rolls back. Superuser only unless granted. |
| `remove_preload_model(name)` | `void` | Removes a model from the preload list. Same rules as `add_preload_model`. |
| `list_preload_models()` | `text[]` | Lists the names in the preload list in sorted order, including entries that failed to load. |
{.fields meta="type"}

## Configuration {#toml-configuration-options}

Configurations are [TOML](https://toml.io/). Unknown keys and invalid values are rejected with SQLSTATE `22023`. A stage that takes no options can be written as a string, `"to_lowercase"`, or as a table, `{ to_lowercase = {} }`.

### Text analyzer {#text-analyzer-options}

| Key | Type | Default | Description |
| --- | --- | --- | --- |
| `character_filters` | array | `[]` | [Character filters](#character-filters), applied to the whole text in order. |
| `pre_tokenizer` | string or table | none | The [pre-tokenizer](#pre-tokenizers). Without one, the whole text is one word. |
| `token_filters` | array | `[]` | [Token filters](#token-filters), applied in order. |
{.fields meta="type default"}

### Character filters {#character-filters}

| Key | Type | Description |
| --- | --- | --- |
| `to_lowercase` | none | Lowercases with Unicode rules. |
| `unicode_normalization` | string | Applies a [Unicode normalization form](https://unicode.org/reports/tr15/): `nfc`, `nfd`, `nfkc` or `nfkd`. `nfkc` also folds full-width and compatibility characters. |
{.fields meta="type"}

### Pre-tokenizers {#pre-tokenizers}

| Key | Type | Description |
| --- | --- | --- |
| `unicode_segmentation` | none | Splits at Unicode word boundaries ([UAX #29](https://www.unicode.org/reports/tr29/)) and keeps pieces that contain a letter or digit. |
| `regex` | string | Returns every non-overlapping match of a Rust [`regex`](https://docs.rs/regex) pattern. |
| `jieba` | table | Splits Chinese with the [jieba](https://github.com/messense/jieba-rs) dictionary; options below. |
{.fields meta="type"}

<a id="jieba-chinese-word-segmentation"></a>

| `jieba` key | Type | Default | Description |
| --- | --- | --- | --- |
| `mode` | string | `search` | `search` returns the likely words plus the shorter dictionary words inside long ones, for indexing and queries. `precise` returns only the likely words. `full` returns every dictionary word found, overlapping. |
| `enable_hmm` | boolean | `true` | Joins characters into words missing from the dictionary in `precise` and `search` modes. `full` ignores it. |
{.fields meta="type default"}

### Token filters {#token-filters}

<a id="3-token-filters-token_filters"></a>

| Key | Type | Description |
| --- | --- | --- |
| `skip_non_alphanumeric` | none | Removes words that contain no letter or digit. |
| `stopwords` | string | Removes words in the named list: `lucene_english`, `nltk_english`, `iso_english`, or one made with `create_stopwords`. |
| `stemmer` | string | Replaces each word with its Snowball stem; values [below](#stemmers). Expects lowercase input. |
| `synonym` | string | Replaces words using a list made with `create_synonym`. |
| `pg_dict` | string | Passes each word to a PostgreSQL text search dictionary, as `ts_lexize` does. Unrecognized words pass unchanged; stopwords are removed. |
| `ngram` | table | Replaces each word with its character n-grams; options below. |
{.fields meta="type"}

| `ngram` key | Type | Default | Description |
| --- | --- | --- | --- |
| `min_gram` | integer | `1` | Shortest n-gram, in characters, from 1 to 255 and at most `max_gram`. |
| `max_gram` | integer | `2` | Longest n-gram, in characters, from 1 to 255. A wider range matches more substrings and makes the index larger. |
| `preserve_original` | boolean | `false` | Also keep a word whose length is outside the range, which would otherwise be replaced or, if shorter than `min_gram`, removed. |
{.fields meta="type default"}

### Stemmers {#stemmers}

<a id="stemmer-snowball-stemming--30-languages"></a>

`arabic`, `armenian`, `basque`, `catalan`, `danish`, `dutch`, `english_porter`, `english_porter2`, `estonian`, `finnish`, `french`, `german`, `greek`, `hindi`, `hungarian`, `indonesian`, `irish`, `italian`, `lithuanian`, `nepali`, `norwegian`, `portuguese`, `romanian`, `russian`, `serbian`, `spanish`, `swedish`, `tamil`, `turkish`, `yiddish`. For English, `english_porter2` is the current Snowball algorithm and `english_porter` the original Porter stemmer.

### Tokenizer {#tokenizer-options}

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| `model` | string | yes | A built-in model, or a Lindera, Hugging Face or custom model of this database. |
| `text_analyzer` | string | | An analyzer to run before the model. Cannot be combined with the inline keys below. |
| `character_filters` | array | | An inline analyzer's character filters. |
| `pre_tokenizer` | string or table | | An inline analyzer's pre-tokenizer. |
| `token_filters` | array | | An inline analyzer's token filters. |
{.fields meta="type required"}

Without an analyzer, the model receives the whole text. With one, it receives each word separately.

### Custom model {#custom-model-options}

| Key | Type | Required | Description |
| --- | --- | --- | --- |
| `table` | string | yes | Source table, optionally schema-qualified. Stored with its schema. |
| `column` | string | yes | Source column. Any type with a cast to `text` works. |
| `text_analyzer` | string | yes | Analyzer that splits the column into words. |
| `filter` | string | | SQL condition on source columns, without `WHERE`. Only rows where it is true train the vocabulary and get IDs. Default: every row. |
{.fields meta="type required"}

### Lindera model {#lindera-model-options}

The configuration is a [Lindera 7](https://github.com/lindera/lindera) tokenizer configuration. pg_tokenizer reads these keys itself:

| Key | Type | Description |
| --- | --- | --- |
| `segmenter.mode` | string | Lindera segmentation mode, such as `normal`. |
| `segmenter.dictionary` | string | `embedded://<name>` for a dictionary built into the library, or a path or `file://` URI of a Lindera 7 (format v3) dictionary directory on the server. |
| `segmenter.user_dictionary` | string | Path of a user dictionary, CSV or compiled. Its IDs start at 1073741824. |
| `character_filters` | array | Lindera character filters, each with `kind` and `args`. |
| `token_filters` | array | Lindera token filters, each with `kind` and `args`. Filters that remove words remove their IDs; filters that only rewrite text have no effect on the IDs. |
{.fields meta="type"}

## Settings {#analysis-budgets}

<a id="definition-caches"></a>

These limits bound the work of one call. They are integers from 1 to 2147483647 that any user can `SET`. A call that exceeds one fails with SQLSTATE `54000` and a message naming it, such as `pg_tokenizer exceeds max_piece_bytes (1048576)`; nothing is truncated.

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `pg_tokenizer.max_input_bytes` | integer | `16777216` | Largest input, in bytes, to one analyzer or tokenizer call. |
| `pg_tokenizer.max_output_tokens` | integer | `1000000` | Most words or IDs one stage may produce. |
| `pg_tokenizer.max_output_bytes` | integer | `67108864` | Most bytes one stage may produce, counting words, IDs, rewritten text and n-gram bookkeeping. |
| `pg_tokenizer.max_piece_bytes` | integer | `1048576` | Largest input, in bytes, to one call into jieba, a regular expression, a model, or `pg_dict`. Such a call cannot be cancelled until it returns, so this bounds how long a query can ignore a cancel or `statement_timeout`. |
{.fields meta="type default"}

Keep the defaults for queries from users. For a trusted batch load of large documents, raise a limit for that transaction only:

```sql
BEGIN;
SET LOCAL pg_tokenizer.max_piece_bytes = 16777216;
UPDATE docs SET terms = tokenizer_catalog.analyze_to_tsvector(body, 'zh_text');
COMMIT;
```

The limits count pg_tokenizer's own buffers, not all memory a backend uses: loaded models and memory inside third-party libraries come on top.

## Catalog tables {#catalog}

Definitions are rows in `tokenizer_catalog.text_analyzer`, `tokenizer`, `model`, `stopwords` and `synonym`, each with a `name` and its `config`. Query them to see what exists, and change them only through the functions above:

```sql
SELECT name FROM tokenizer_catalog.text_analyzer;
SELECT name, config FROM tokenizer_catalog.tokenizer;
```

A custom model's vocabulary is the table `tokenizer_data."model_<name>"`, with columns `id` and `token`.
