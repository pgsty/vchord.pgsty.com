---
title: "Text Analyzers & Filters"
description: "Complete configuration reference for character filters, pre-tokenizers, and token filters in pg_tokenizer."
weight: 20
icon: fa-solid fa-sliders
---

A **Text Analyzer** processes raw text through three sequential stages:

1. **Character Filters (`character_filters`)** — Zero or more character-level transformations on the full text string.
2. **Pre-tokenizer (`pre_tokenizer`)** — Exactly one splitter that breaks the string into initial tokens.
3. **Token Filters (`token_filters`)** — Zero or more token-level transformations, expansions, or filters.

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
> You can test any text analyzer directly using `SELECT apply_text_analyzer('Sample text here', 'analyzer1');` to inspect the resulting `TEXT[]` array before wiring it to a model.

---

## 1. Character Filters (`character_filters`)

### `to_lowercase`

Converts all characters in the input text to lowercase.

```toml
character_filters = ["to_lowercase"]
# or table syntax:
[[character_filters]]
to_lowercase = {}
```

### `unicode_normalization`

Applies Unicode Normalization Forms ([UAX #15](https://www.unicode.org/reports/tr15/)) to standardize composed/decomposed characters, accents, and full-width/half-width variants.

Supported modes:
- `"nfc"` — Normalization Form C (Canonical Decomposition followed by Canonical Composition)
- `"nfd"` — Normalization Form D (Canonical Decomposition)
- `"nfkc"` — Normalization Form KC (Compatibility Decomposition followed by Canonical Composition)
- `"nfkd"` — Normalization Form KD (Compatibility Decomposition)

```toml
[[character_filters]]
unicode_normalization = "nfkd"
```

---

## 2. Pre-Tokenizers (`pre_tokenizer`)

A text analyzer may specify **at most one** `pre_tokenizer`.

### `unicode_segmentation`

Splits text on Unicode word boundaries according to the [Unicode Standard Annex #29 (UAX #29)](https://www.unicode.org/reports/tr29/) specification (via the Rust `unicode-segmentation` crate). Ideal for space-delimited and Western languages.

```toml
pre_tokenizer = "unicode_segmentation"
# or:
[pre_tokenizer.unicode_segmentation]
```

### `regex`

Extracts tokens matching a custom regular expression (powered by the Rust [`regex`](https://docs.rs/regex) crate):

```toml
[pre_tokenizer]
regex = '''\\w+'''
```

### `jieba` (Chinese Word Segmentation)

Segments Chinese text into words using the [`jieba-rs`](https://docs.rs/jieba-rs) dictionary and Hidden Markov Model (HMM):

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `mode` | `string` | `"search"` | `"full"` (`jieba.cut_all`, every dictionary match), `"precise"` (standard `jieba.cut`), or `"search"` (`jieba.cut_for_search` finer-grained segmentation for search recall). |
| `enable_hmm` | `bool` | `true` | Enables HMM recognition for out-of-vocabulary words in `"precise"` and `"search"`; `"full"` ignores it. |
{.wide .expand}

Versions through 1.0.0 swapped `full` and `precise`. After upgrading to 1.0.1, regenerate persisted output produced with either mode and rebuild dependent indexes. The default `search` mode is unchanged.

```toml
[pre_tokenizer.jieba]
mode = "search"
enable_hmm = true
```

---

## 3. Token Filters (`token_filters`)

Token filters run in the exact order listed in your TOML array.

### `skip_non_alphanumeric`

Drops any token that contains no alphanumeric characters (such as standalone punctuation marks `,`, `.`, `!` left behind by word segmentation).

```toml
[[token_filters]]
skip_non_alphanumeric = {}
# or in array shorthand:
token_filters = ["skip_non_alphanumeric"]
```

### `stemmer` (Snowball Stemming — 30 Languages)

Reduces inflected words to their root stem using the [Snowball stemming algorithms](https://snowballstem.org/).

```toml
[[token_filters]]
stemmer = "english_porter2"
```

Supported `stemmer` values:

| Language | `stemmer` Value | Language | `stemmer` Value |
| :--- | :--- | :--- | :--- |
| Arabic | `arabic` | Lithuanian | `lithuanian` |
| Armenian | `armenian` | Nepali | `nepali` |
| Basque | `basque` | Norwegian | `norwegian` |
| Catalan | `catalan` | Portuguese | `portuguese` |
| Danish | `danish` | Romanian | `romanian` |
| Dutch | `dutch` | Russian | `russian` |
| English (Porter) | `english_porter` | Serbian | `serbian` |
| **English (Porter2)** | **`english_porter2`** | Spanish | `spanish` |
| Esperanto | `esperanto` | Swedish | `swedish` |
| Estonian | `estonian` | Tamil | `tamil` |
| Finnish | `finnish` | Turkish | `turkish` |
| French | `french` | Yiddish | `yiddish` |
| German | `german` | | |
| Greek | `greek` | | |
| Hindi | `hindi` | | |
| Hungarian | `hungarian` | | |
| Indonesian | `indonesian` | | |
| Irish | `irish` | | |
| Italian | `italian` | | |
{.wide .expand}

### `stopwords`

Removes common stopwords that carry little lexical signal.

- **Built-in dictionaries**:
  - `"lucene_english"` — Apache Lucene standard English stopword list
  - `"nltk_english"` — NLTK standard English stopword list
  - `"iso_english"` — Stopwords ISO English stopword list
- **Custom stopword dictionary**: Create your own with `create_stopwords(name, text)` (one word per line) and reference it by name. The built-in names are reserved: since 1.0.0 they cannot be dropped or replaced, so a logical restore always recreates the same lists.

```sql
-- Create a custom stopword dictionary (one word per line)
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
-- Output: {cat}
```

### `synonym`

Normalizes synonymous terms to a single canonical token. Create a synonym dictionary with `create_synonym(name, text)` where each line contains space-separated synonyms (all words on a line are replaced by the **first** word on that line):

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
-- Output: {postgres,and,postgres,have,many,index}
```

### `pg_dict` (PostgreSQL Full-Text Dictionaries)

Delegates token filtering to any existing [PostgreSQL Full-Text Search Dictionary](https://www.postgresql.org/docs/current/textsearch-dictionaries.html) (`pg_ts_dict`, including `Simple`, `Ispell`, `Snowball`, `Synonym`, and `Thesaurus` dictionaries). Each token is looked up on its own, as `ts_lexize` does, so a `Thesaurus` dictionary applies only its single-word entries, not phrases that span several tokens:

```toml
[[token_filters]]
pg_dict = "english_stem"
```

Since 1.0.1, creation resolves the name and stores its schema-qualified form. Later calls use that name independently of the session search_path and resolve its OID once per batch, so DROP/CREATE and ALTER no longer require reconnecting. Renaming/moving the dictionary requires updating the analyzer. Upgrade qualifies a legacy name only when exactly one dictionary has that name across all schemas. Missing or ambiguous names stop the upgrade, including a custom dictionary sharing a builtin name; explicitly choose the custom schema or `pg_catalog` first. Legacy definitions loaded before the SQL upgrade follow the same rule. Changes to external dictionary files still follow PostgreSQL's normal reload rules.

### `ngram`

Splits each token into character n-grams (useful for substring, prefix, CJK without dictionaries, or code/identifier search):

| Parameter | Type | Default | Range | Description |
| :--- | :--- | :--- | :--- | :--- |
| `min_gram` | `int` | `1` | `1..=255` (`<= max_gram`) | Minimum character length of generated n-grams. |
| `max_gram` | `int` | `2` | `1..=255` (`>= min_gram`) | Maximum character length of generated n-grams. |
| `preserve_original` | `bool` | `false` | `true` / `false` | Whether to also emit the original unsplit token if its length falls outside `[min_gram, max_gram]`. |
{.wide .expand}

```toml
[[token_filters]]
ngram = { min_gram = 2, max_gram = 3, preserve_original = true }
```

Lengths count Unicode characters, not bytes, so CJK text and emoji split cleanly. A token shorter than `min_gram` produces no n-grams unless `preserve_original` is set.
