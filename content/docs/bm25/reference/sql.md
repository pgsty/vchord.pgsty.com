---
math: true
title: "SQL Reference"
description: "Complete SQL data types, operators, casts, index access methods, and functions for vchord_bm25 and pg_tokenizer."
weight: 10
---

## `vchord_bm25` Data Types

| Data Type | Schema | Versions | Text Representation / Structure | Description |
| :--- | :--- | :--- | :--- | :--- |
| `bm25vector` | `bm25_catalog` | `v0.1.0` – `v0.3.0` | `{token_id:freq, ...}` (e.g., `{1:1, 2:2, 15:1}`) | Sparse vector mapping 32-bit unsigned token IDs to 32-bit term frequencies. Stored with `STORAGE = EXTERNAL`. |
| `bm25query` | `bm25_catalog` | `v0.1.0` – `v0.3.0` | `(index_oid regclass, query_vector bm25vector)` | Composite type pairing a target `bm25` index OID with a query `bm25vector`. |
| `bm25query` | `public` / ext schema | `main` | `(vector tsvector, index regclass)` | Composite type pairing a query `tsvector` with a target `bm25` index OID. |

### `bm25vector` Literal Syntax (`v0.1` – `v0.3`)

```sql
-- Empty bm25vector
SELECT '{}'::bm25vector;

-- Explicit token_id:frequency pairs
SELECT '{1:1, 2:3, 10:2}'::bm25vector;

-- Implicit cast from int[] (automatically aggregates duplicate token IDs into counts)
SELECT ARRAY[1, 2, 2, 2, 10, 10]::bm25vector;
-- Output: {1:1, 2:3, 10:2}
```

---

## `vchord_bm25` Operators

| Operator | Left Arg | Right Arg | Return Type | Versions | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `<&>` | `bm25vector` | `bm25query` | `real` (`f32`) | `v0.1.0` – `v0.3.0` | Computes the **negative** BM25 relevance score ($-\text{BM25}(D, Q)$). Supports index-accelerated `ORDER BY ... ASC` scans using `bm25_ops`. |
| `<&>` | `tsvector` | `bm25query` | `float8` (`f64`) | `main` | Computes the **negative** BM25 relevance score on native `tsvector`. Supports index-accelerated `ORDER BY ... ASC` scans using `bm25_ops`. |
| `=` | `bm25vector` | `bm25vector` | `bool` | `v0.2.0` – `v0.3.0` | Exact equality comparison between two `bm25vector` values. |
| `<>` | `bm25vector` | `bm25vector` | `bool` | `v0.2.0` – `v0.3.0` | Inequality comparison between two `bm25vector` values. |

---

## `vchord_bm25` Functions

| Function Signature | Return Type | Versions | Description |
| :--- | :--- | :--- | :--- |
| `to_bm25query(index_oid regclass, query_vector bm25vector)` | `bm25query` | `v0.1.1` – `v0.3.0` | Constructs a `bm25query` from a `bm25` index name/OID and a query `bm25vector` (or `INT[]` via implicit cast). |
| `to_bm25query(index_oid regclass, query_vector int[])` | `bm25query` | `v0.3.0+` | Explicit overload accepting an `INT[]` token ID array directly. |
| `to_bm25query(vector tsvector, index regclass)` | `bm25query` | `main` | Constructs a `bm25query` from a native `tsvector` and target `bm25` index name/OID. |
| `search_bm25query(target_vector bm25vector, query bm25query)` | `real` | `v0.1.0` – `v0.3.0` | Underlying implementation function for `bm25vector <&> bm25query`. |
| `_bm25_evaluate(left tsvector, right bm25query)` | `float8` | `main` | Underlying implementation function for `tsvector <&> bm25query`. |
| `bm25_page_inspect(index regclass, blkno int)` | `text` | `v0.3.0` | Returns human-readable diagnostic metadata for block `blkno` of a `bm25` index. |

---

## `vchord_bm25` Access Method & Operator Class

| Object | Name | Target Type | Ordering Operator |
| :--- | :--- | :--- | :--- |
| Access Method | `bm25` | Index | Handler `_bm25_amhandler` |
| Operator Family | `bm25_ops` | `USING bm25` | `OPERATOR 1 pg_catalog.<&> FOR ORDER BY float_ops` |
| Operator Class | `bm25_ops` | `bm25vector` (`v0.1`–`v0.3`) / `tsvector` (`main`) | Default operator class for `USING bm25` |

---

## `pg_tokenizer` Functions (`tokenizer_catalog`)

All `pg_tokenizer` functions reside in the `tokenizer_catalog` schema:

### Tokenizer Management & Execution

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `create_tokenizer(name TEXT, config TEXT)` | `void` | Creates a named tokenizer from a TOML configuration string. |
| `drop_tokenizer(name TEXT)` | `void` | Drops an existing tokenizer. |
| `tokenize(text TEXT, tokenizer_name TEXT)` | `INT[]` | Tokenizes `text` using `tokenizer_name` and returns an array of integer token IDs (implicitly castable to `bm25vector`). |

### Text Analyzer Management

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `create_text_analyzer(name TEXT, config TEXT)` | `void` | Creates a reusable named text analyzer pipeline (`character_filters`, `pre_tokenizer`, `token_filters`). |
| `drop_text_analyzer(name TEXT)` | `void` | Drops a named text analyzer. |
| `apply_text_analyzer(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | Runs a text analyzer on `text` and returns the array of normalized string tokens (useful for debugging). |

### Model Management

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `create_custom_model(name TEXT, config TEXT)` | `void` | Trains a custom vocabulary model on an existing table column using a text analyzer. |
| `drop_custom_model(name TEXT)` | `void` | Drops a custom model and its backing vocabulary table. |
| `create_custom_model_tokenizer_and_trigger(tokenizer_name TEXT, model_name TEXT, text_analyzer_name TEXT, table_name TEXT, source_column TEXT, target_column TEXT)` | `void` | Creates a custom model, creates a tokenizer, populates `target_column` on `table_name`, and attaches an automatic `BEFORE INSERT OR UPDATE` trigger. |
| `create_huggingface_model(name TEXT, config TEXT)` | `void` | Imports a model from a HuggingFace `tokenizer.json` string. |
| `drop_huggingface_model(name TEXT)` | `void` | Drops an imported HuggingFace model. |
| `create_lindera_model(name TEXT, config TEXT)` | `void` | Creates a Lindera morphological analysis model (e.g., `ipadic`) from a TOML config. |
| `drop_lindera_model(name TEXT)` | `void` | Drops a Lindera model. |

### Dictionary & Preload Management

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `create_stopwords(name TEXT, config TEXT)` | `void` | Creates a custom stopword dictionary (one word per line). |
| `drop_stopwords(name TEXT)` | `void` | Drops a custom stopword dictionary. |
| `create_synonym(name TEXT, config TEXT)` | `void` | Creates a custom synonym dictionary (space-separated synonyms per line, mapped to the first word). |
| `drop_synonym(name TEXT)` | `void` | Drops a custom synonym dictionary. |
| `add_preload_model(name TEXT)` | `void` | Registers a model to be preloaded at PostgreSQL server startup (`shared_preload_libraries`). |
| `remove_preload_model(name TEXT)` | `void` | Removes a model from the startup preload list. |
| `list_preload_models()` | `TEXT[]` | Returns the list of models currently registered for preloading. |

### Internal Trigger & Helper Functions (`tokenizer_catalog`)

| Function Signature | Return Type | Description |
| :--- | :--- | :--- |
| `apply_text_analyzer_for_custom_model(text TEXT, text_analyzer_name TEXT)` | `TEXT[]` | Applies `text_analyzer_name` and filters out tokens exceeding `2600` bytes (PostgreSQL B-tree `UNIQUE` index maximum key size) before inserting into a custom model vocabulary table. |
| `custom_model_insert_trigger()` | `trigger` | `AFTER INSERT OR UPDATE` trigger function that extracts new tokens from the source text column and inserts unseen tokens into `tokenizer_catalog."model_<name>"`. |
| `custom_model_tokenizer_set_target_column_trigger()` | `trigger` | `BEFORE INSERT OR UPDATE` trigger function installed by `create_custom_model_tokenizer_and_trigger` that automatically populates `NEW.<target_column> = tokenize(NEW.<source_column>, tokenizer_name)`. |

---

## `pg_tokenizer` Catalog Tables (`tokenizer_catalog`)

| Table Name | Columns | Description |
| :--- | :--- | :--- |
| `tokenizer_catalog.tokenizer` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | Stores registered tokenizer names and their serialized JSON/TOML configuration. |
| `tokenizer_catalog.text_analyzer` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | Stores standalone reusable text analyzer definitions. |
| `tokenizer_catalog.model` | `name TEXT NOT NULL UNIQUE`, `config TEXT NOT NULL` | Stores registered custom, HuggingFace, and Lindera model definitions. |
| `tokenizer_catalog.stopwords` | `name TEXT NOT NULL PRIMARY KEY`, `config TEXT NOT NULL` | Stores built-in (`lucene_english`, `nltk_english`, `iso_english`) and custom stopword dictionaries. |
| `tokenizer_catalog.synonym` | `name TEXT NOT NULL PRIMARY KEY`, `config TEXT NOT NULL` | Stores custom synonym dictionaries. |
| `tokenizer_catalog."model_<name>"` | `id SERIAL PRIMARY KEY`, `token TEXT NOT NULL UNIQUE` | Backing vocabulary table created for each custom model `<name>`, mapping unique normalized tokens to 1-based integer IDs. |

---

## `pg_tokenizer` TOML Configuration Reference

### Tokenizer Options (`create_tokenizer`)

| Option | Type | Description |
| :--- | :--- | :--- |
| `text_analyzer` | `string` (optional) | Name of a pre-created `text_analyzer`. If omitted, inline `character_filters`, `pre_tokenizer`, and `token_filters` may be defined directly (when supported by `model`). |
| `model` | `string` (required) | Name of a built-in model (`llmlingua2`, `bert_base_uncased`, `wiki_tocken`, `gemma2b`) or a user-created model (`custom`, `huggingface`, or `lindera`). |

### Text Analyzer Options (`create_text_analyzer`)

| Option | Type | Description |
| :--- | :--- | :--- |
| `character_filters` | `array` / `table` | List of character filters applied to the full string before splitting: `to_lowercase`, `unicode_normalization` (`nfc`, `nfd`, `nfkc`, `nfkd`). |
| `pre_tokenizer` | `string` / `table` | Single pre-tokenizer that splits the string into initial tokens: `unicode_segmentation`, `regex` (Rust regex string), or `jieba` (`mode = "full" \| "precise" \| "search"`, `enable_hmm = true \| false`). |
| `token_filters` | `array` | Ordered list of token filters: `skip_non_alphanumeric`, `stemmer` (30 Snowball stemmers), `stopwords` (`lucene_english`, `nltk_english`, `iso_english`, or custom), `synonym`, `pg_dict` (any `pg_ts_dict` except `Thesaurus`), `ngram` (`min_gram`, `max_gram` in `1..=255`, `preserve_original`). |

### Custom Model Options (`create_custom_model`)

| Option | Type | Description |
| :--- | :--- | :--- |
| `table` | `string` (required) | Target table name containing the source text corpus. |
| `column` | `string` (required) | Source `TEXT` column name on `table` used to build the vocabulary. |
| `text_analyzer` | `string` (required) | Name of the `text_analyzer` used to tokenize `column` into vocabulary terms. |
