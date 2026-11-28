---
title: "Models"
linkTitle: "Models"
description: "When you need a pg_tokenizer model, and how to use the built-in LLM vocabularies, Lindera dictionaries for Japanese and Korean, Hugging Face tokenizers and custom vocabularies."
weight: 50
icon: fa-solid fa-cubes
---

A model maps text to integer token IDs from a fixed vocabulary. You need one in two cases: to segment Japanese or Korean, which takes a Lindera dictionary, and to produce IDs, whether those of an LLM's tokenizer or of a vocabulary built from your own table. For BM25 search on other languages, a [text analyzer](/docs/tokenizer/text-analyzer/) alone is enough.

## How a tokenizer uses a model {#tokenizer}

A model is used through a **tokenizer**, created with `create_tokenizer`. Its configuration names the `model` and, optionally, an analyzer to run first: either `text_analyzer`, the name of an existing analyzer, or the analyzer keys written inline. It cannot have both.

- Without an analyzer, the model receives the whole text and splits it itself. This is how the built-in, Hugging Face and Lindera models are normally used.
- With an analyzer, the model receives each word the analyzer produces, separately, and the IDs are concatenated in order. Use this to remove stopwords or stem before looking up IDs, and always with a custom model.

```sql
SELECT tokenizer_catalog.create_tokenizer('bert_words', $$
model = "bert_base_uncased"
pre_tokenizer = { regex = '(?u)\b\w\w+\b' }
character_filters = ["to_lowercase"]
token_filters = [{ stopwords = "nltk_english" }, { stemmer = "english_porter2" }]
$$);

SELECT tokenizer_catalog.tokenize('PostgreSQL is a powerful, open-source database.', 'bert_words');
```

`tokenize` returns the IDs as `int[]`. `tokenize_to_tsvector` returns them as lexemes, such as `'2695':1 '17603':2`, which vchord_bm25 can index like words; the query must then go through the same tokenizer.

What happens to a word missing from the vocabulary depends on the model. Subword models (the built-in ones except `wiki_tocken`, and most Hugging Face models) break it into pieces they know. Lindera models, custom models and `wiki_tocken` leave it out.

## Built-in models {#builtin}

<a id="1-built-in-pretrained-models"></a>

Every package includes four vocabularies. Use one when you need the same IDs as the model it comes from.

| Model | Vocabulary | Notes |
| --- | --- | --- |
| `bert_base_uncased` | [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased), WordPiece | English, lowercases its input. |
| `gemma2b` | [google/gemma-2b](https://huggingface.co/google/gemma-2b) | About 100 MB loaded. |
| `llmlingua2` | [microsoft/llmlingua-2-xlm-roberta-large-meetingbank](https://huggingface.co/microsoft/llmlingua-2-xlm-roberta-large-meetingbank), XLM-RoBERTa | Multilingual. About 200 MB loaded, [preloaded](#preload) by default. |
| `wiki_tocken` | English words from [WikiText-103](https://huggingface.co/datasets/iohadrubin/wikitext-103-raw-v1) | Lowercases, removes English stopwords and stems by itself; whole words only. |
{.wide}

```sql
SELECT tokenizer_catalog.create_tokenizer('gemma', $$
model = "gemma2b"
$$);

SELECT tokenizer_catalog.tokenize('PostgreSQL is a powerful, open-source database.', 'gemma');
```

## Japanese and Korean: Lindera {#lindera}

<a id="4-lindera-morphological-models-create_lindera_model"></a>

`create_lindera_model` creates a model from a [Lindera](https://github.com/lindera/lindera) 7 configuration: a `[segmenter]` table with the segmentation `mode` and the `dictionary`, followed by Lindera's own `[[character_filters]]` and `[[token_filters]]`, each with a `kind` and `args`. The [Japanese recipe](/docs/tokenizer/multilingual/#japanese) has a complete configuration.

```sql
SELECT tokenizer_catalog.create_lindera_model('ja_ipadic', $$
[segmenter]
mode = "normal"
dictionary = "embedded://ipadic"
$$);

SELECT tokenizer_catalog.create_tokenizer('ja_text', $$
model = "ja_ipadic"
$$);
```

The model returns the dictionary ID of each word it finds. Words that are not in the dictionary are left out, and so are the IDs of anything Lindera's token filters remove. Lindera filters that only rewrite a word's text do not change its ID.

The `dictionary` comes from one of two places:

- **Built into the library**, as `embedded://<name>`. GitHub release packages and default source builds include `embedded://ipadic`. Other dictionaries, `ipadic-neologd`, `unidic`, `ko-dic` (Korean) and `cc-cedict`, are available only in a source build with the matching [feature](/docs/tokenizer/installation/#source). Naming a dictionary the library does not contain fails with `failed to load Lindera dictionary`.
- **A directory on the database server**, given as a path or a `file://` URI. Pigsty packages include no dictionary, so they need this. The directory must be built for Lindera 7 (format v3) and installed at the same path on every node. PostgreSQL reads it as its operating-system user, so creating the model, and loading it in each new session, requires superuser or membership in `pg_read_server_files`; other roles get `permission denied to load a Lindera dictionary from a file`. A [preloaded](#preload) model is loaded by the server at startup and needs no privilege at use.

`user_dictionary` adds your own words from a CSV or compiled file, read under the same rules. Their IDs start at 1073741824, so they never collide with dictionary IDs.

## Hugging Face tokenizers {#huggingface}

<a id="3-importing-huggingface-tokenizers-create_huggingface_model"></a>

`create_huggingface_model` imports the `tokenizer.json` of any Hugging Face model, so you can produce the same IDs as an embedding model you use outside the database. In `psql`, read the file into a variable and pass it:

```sql
\set content `curl -fsSL https://huggingface.co/google-bert/bert-base-chinese/resolve/main/tokenizer.json`
SELECT tokenizer_catalog.create_huggingface_model('bert_chinese', :'content');

SELECT tokenizer_catalog.create_tokenizer('bert_chinese', $$
model = "bert_chinese"
$$);
```

Every ID in the file must fit in `int`, at most 2147483647; a model with larger IDs is rejected.

## Custom models {#custom}

<a id="2-custom-corpus-models-create_custom_model"></a><a id="custom-model-100"></a><a id="option-a-one-step-helper-create_custom_model_tokenizer_and_trigger"></a><a id="option-b-step-by-step-create_custom_model"></a>

A custom model gives every distinct word in one column of your table an integer ID. Use it when you need compact IDs for your own corpus, for example to build sparse vectors outside the database. vchord_bm25 does not need one.

`create_custom_model` runs an analyzer over the column and stores each distinct word in a vocabulary table, `tokenizer_data."model_<name>"`. It also adds a trigger, `model_<name>_trigger`, to the source table that adds new words as rows are inserted or updated. The vocabulary only grows: words from deleted or changed rows stay.

`create_custom_model_tokenizer_and_trigger` does that, creates a tokenizer for the model, fills a target column with each row's IDs, and adds a second trigger that keeps it current:

```sql
CREATE TABLE notes (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text,
    token_ids int[]
);

SELECT tokenizer_catalog.create_text_analyzer('notes_words', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ stopwords = "nltk_english" }, { stemmer = "english_porter2" }]
$$);

SELECT tokenizer_catalog.create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'notes_tok',
    model_name         => 'notes_vocab',
    text_analyzer_name => 'notes_words',
    table_name         => 'notes',
    source_column      => 'body',
    target_column      => 'token_ids'
);

INSERT INTO notes (body) VALUES ('Custom models assign IDs to words.');
SELECT token_ids FROM notes;
SELECT tokenizer_catalog.tokenize('words and models', 'notes_tok');
```

The target column receives `int[]`, converted the way an `INSERT` would convert it. To fill other columns yourself, use `create_custom_model` and a `create_tokenizer` that names the same analyzer and the model.

Things to know when you use a custom model:

- `filter`, an SQL condition on the source columns written without `WHERE`, restricts the corpus. Pass it as the seventh argument, `filter => 'tenant_id = 42'`, or in the model's configuration. Only rows for which it is true train the vocabulary and get IDs; other rows keep their target value. It does not replace row-level security.
- PostgreSQL fires `BEFORE` triggers in name order. A trigger of yours that calls `tokenize` or `tokenize_to_tsvector` on the same table must sort after `model_<name>_trigger`, or the words new in that row are not in the vocabulary yet and are left out.
- A word longer than 2,600 bytes is split into pieces of at most 2,600 bytes, each with its own ID, and a warning is raised.
- Concurrent writers wait for each other only when they add new words to the same model. Under `REPEATABLE READ` or `SERIALIZABLE`, such a conflict can fail with SQLSTATE `40001`; retry the transaction.
- `drop_custom_model` removes the vocabulary table and both triggers, but not the tokenizer.

## Preload models {#preload}

<a id="5-model-preloading-add_preload_model"></a>

Each backend loads a model the first time it uses it and keeps it for the life of the connection, which for a large model costs time on the first call and memory in every connection. A preloaded model is loaded once when the server starts and shared by all backends.

```sql
SELECT tokenizer_catalog.list_preload_models();
SELECT tokenizer_catalog.add_preload_model('ja_ipadic');
SELECT tokenizer_catalog.remove_preload_model('llmlingua2');
```

Restart PostgreSQL for a change to take effect. The list starts with `llmlingua2`, which costs about 200 MB at every server start; remove it if you do not use it.

- Preload the large models that many connections use: a Lindera model, `gemma2b`, `llmlingua2`. Custom models gain nothing, because they look words up in their vocabulary table.
- The list belongs to the server, not a database. `add_preload_model` stores the model's definition from the current database; another database uses the preloaded copy only if its definition under that name is identical.
- The list is a directory of files under `$PGDATA/pg_tokenizer/preload_models`. A change takes effect on disk at once, even if the transaction rolls back, and is not replicated: see [Replicas and backups](/docs/tokenizer/installation/#logical-backups).
- Only superusers can change it, unless granted `EXECUTE` on the two functions. Entries that fail to load are skipped with a warning in the server log.
