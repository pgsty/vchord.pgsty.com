---
title: "Tokenization Models"
description: "Pretrained models (llmlingua2, bert_base_uncased, wiki_tocken, gemma2b), custom corpus-trained models, HuggingFace tokenizers, and Lindera models."
weight: 30
---

In `pg_tokenizer`, a **Model** maps string tokens (or raw text) to integer token IDs (`INT[]`). You can choose from four built-in pretrained models, train a custom vocabulary model directly on your PostgreSQL table, import any HuggingFace `tokenizer.json`, or use a Lindera morphological model.

## 1. Built-in Pretrained Models

| Model Name | Source / Architecture | Requires `text_analyzer`? | Memory Footprint | Best For |
| :--- | :--- | :--- | :--- | :--- |
| **`llmlingua2`** | [`microsoft/llmlingua-2-xlm-roberta-large-meetingbank`](https://huggingface.co/microsoft/llmlingua-2-xlm-roberta-large-meetingbank) (XLM-RoBERTa multilingual subword) | No (forbidden) | ~200 MB (default preloaded) | Multilingual general text out of the box without training a custom vocabulary. |
| **`bert_base_uncased`** | [`google-bert/bert-base-uncased`](https://huggingface.co/google-bert/bert-base-uncased) (WordPiece, 30,522 vocab) | No (forbidden) | ~15 MB | General English text; fast startup and compact vocabulary. |
| **`wiki_tocken`** | [`Snowolf/wiki-tocken`](https://huggingface.co/Snowolf/wiki-tocken) (Built-in English Wikipedia token dictionary) | **Yes (required)** | ~30 MB | English full-text search combined with custom stemmers, stopwords, and synonyms. |
| **`gemma2b`** | [`google/gemma-2b`](https://huggingface.co/google/gemma-2b) (SentencePiece BPE, 256k vocab) | No (forbidden) | ~100 MB | Code, technical identifiers, and multilingual LLM workloads. |

### Example: Using `bert_base_uncased` or `llmlingua2`

```sql
SELECT create_tokenizer('bert_tok', $$
model = "bert_base_uncased"
$$);

SELECT tokenize('VectorChord-BM25 brings Block-WeakAnd to PostgreSQL.', 'bert_tok');
```

---

## 2. Custom Corpus Models (`create_custom_model`)

For maximum BM25 accuracy and minimal memory footprint, you can build a **custom vocabulary model** directly from your own table column. Unlike subword LLM tokenizers (which split rare domain words into multiple sub-tokens), a custom model assigns a dedicated 1:1 integer ID to every unique normalized token produced by your `text_analyzer`—and weighs only a few megabytes in memory.

### Option A: One-Step Helper (`create_custom_model_tokenizer_and_trigger`)

This convenience function creates the custom model, creates the tokenizer, populates the target `bm25vector` column for all existing rows, and installs a `BEFORE INSERT OR UPDATE` trigger that automatically learns new vocabulary tokens and updates the `bm25vector` column when rows change:

```sql
-- 1. Define how text should be analyzed
SELECT create_text_analyzer('my_analyzer', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [
    "skip_non_alphanumeric",
    { stopwords = "nltk_english" },
    { stemmer = "english_porter2" },
]
$$);

-- 2. Create model, tokenizer, backfill embeddings, and attach trigger
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'my_tokenizer',
    model_name         => 'my_model',
    text_analyzer_name => 'my_analyzer',
    table_name         => 'documents',
    source_column      => 'passage',
    target_column      => 'embedding'
);
```

### Option B: Step-by-Step (`create_custom_model` Without Trigger)

If you prefer not to attach an automatic trigger (or want to control when `embedding` is populated):

```sql
-- 1. Build the custom model from the existing table column
SELECT create_custom_model('my_model', $$
table = "documents"
column = "passage"
text_analyzer = "my_analyzer"
$$);

-- 2. Create the tokenizer referencing the analyzer and custom model
SELECT create_tokenizer('my_tokenizer', $$
text_analyzer = "my_analyzer"
model = "my_model"
$$);

-- 3. Populate or refresh embeddings manually
UPDATE documents SET embedding = tokenize(passage, 'my_tokenizer');
```

---

## 3. Importing HuggingFace Tokenizers (`create_huggingface_model`)

You can import any HuggingFace [`tokenizers`](https://github.com/huggingface/tokenizers) JSON specification (`tokenizer.json`) into PostgreSQL using `create_huggingface_model`.

In `psql`, you can fetch `tokenizer.json` directly from HuggingFace Hub into a variable using `\set` and pass it to `create_huggingface_model`:

```sql
\set content `wget -q -O - https://huggingface.co/google-bert/bert-base-uncased/resolve/main/tokenizer.json`
SELECT create_huggingface_model('bert_import', :'content');

SELECT create_tokenizer('bert_import_tok', $$
model = "bert_import"
$$);
```

Or pass the contents of a `tokenizer.json` file directly as a dollar-quoted string:

```sql
SELECT create_huggingface_model('bge_m3_model', $$
{
  "version": "1.0",
  ...
}
$$);

SELECT create_tokenizer('bge_m3_tok', $$
model = "bge_m3_model"
$$);
```

---

## 4. Lindera Morphological Models (`create_lindera_model`)

For East Asian languages such as Japanese, Korean, and Chinese that benefit from morphological dictionary analysis, `pg_tokenizer` integrates [`lindera`](https://github.com/lindera/lindera).

> [!NOTE]
> If you build `pg_tokenizer` from source, enable the desired Lindera dictionary features at compile time:
> ```bash
> cargo pgrx install --release --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

Example configuration using `ipadic` with iteration mark normalization, NFKC Unicode normalization, character mapping, compound word merging, number normalization, Japanese part-of-speech stop-tags, Katakana stemming, and diacritical mark removal:

```sql
SELECT create_lindera_model('japanese_ipadic', $$
[segmenter]
mode = "normal"
  [segmenter.dictionary]
  kind = "ipadic"

[[character_filters]]
kind = "japanese_iteration_mark"
  [character_filters.args]
  normalize_kanji = true
  normalize_kana = true

[[character_filters]]
kind = "unicode_normalize"
  [character_filters.args]
  kind = "nfkc"

[[character_filters]]
kind = "mapping"
  [character_filters.args.mapping]
  "リンデラ" = "Lindera"

[[token_filters]]
kind = "japanese_compound_word"
  [token_filters.args]
  kind = "ipadic"
  tags = [
    "名詞,数",
    "名詞,接尾,助数詞",
  ]
  new_tag = "名詞,数"

[[token_filters]]
kind = "japanese_number"
  [token_filters.args]
  tags = ["名詞,数"]

[[token_filters]]
kind = "japanese_stop_tags"
  [token_filters.args]
  tags = [
    "接続詞",
    "助詞",
    "助詞,格助詞",
    "助詞,格助詞,一般",
    "助詞,格助詞,引用",
    "助詞,格助詞,連語",
    "助詞,係助詞",
    "助詞,副助詞",
    "助詞,間投助詞",
    "助詞,並立助詞",
    "助詞,終助詞",
    "助詞,副助詞／並立助詞／終助詞",
    "助詞,連体化",
    "助詞,副詞化",
    "助詞,特殊",
    "助動詞",
    "記号",
    "記号,一般",
    "記号,読点",
    "記号,句点",
    "記号,空白",
    "記号,括弧閉",
    "その他,間投",
    "フィラー",
    "非言語音",
  ]

[[token_filters]]
kind = "japanese_katakana_stem"
  [token_filters.args]
  min = 3

[[token_filters]]
kind = "remove_diacritical_mark"
  [token_filters.args]
  japanese = false
$$);

SELECT create_tokenizer('jp_tok', $$
model = "japanese_ipadic"
$$);
```

---

## 5. Model Preloading (`add_preload_model`)

Large models (`llmlingua2` at ~200 MB, `gemma2b` at ~100 MB, `japanese_ipadic`) take several seconds and significant RAM to load on first query in each new PostgreSQL backend process. By preloading models during `shared_preload_libraries` startup, PostgreSQL loads the model once in the postmaster process and shares it across all backend connections via copy-on-write memory (`llmlingua2` is preloaded by default):

```sql
-- Add a model to the preload list (persisted in $PGDATA/pg_tokenizer/preload_models)
SELECT add_preload_model('my_model');

-- List currently configured preload models (default: {llmlingua2})
SELECT list_preload_models();

-- Remove a model from the preload list (e.g., to save ~200 MB if llmlingua2 is unused)
SELECT remove_preload_model('llmlingua2');
```

Restart PostgreSQL after calling `add_preload_model(...)` (with `shared_preload_libraries = 'pg_tokenizer.so'` set in `postgresql.conf`) for preloading to take effect across all backends.
