---
title: "Text Analyzers"
linkTitle: "Text Analyzers"
description: "Choose how pg_tokenizer splits and normalizes text for a language, test the result, and change an analyzer that is already in use."
weight: 40
icon: fa-solid fa-sliders
---

A text analyzer decides what counts as a word, and is the part of the pipeline you adapt to a language and to how people search. This page explains how to choose each stage, check what it produces, and replace an analyzer that stored data already depends on. Every key is defined once in the [reference](/docs/tokenizer/reference/#text-analyzer-options).

## How an analyzer runs {#how-it-works}

An analyzer has three stages, applied in this order:

1. **Character filters** rewrite the whole text, one after another: `to_lowercase` and `unicode_normalization`.
1. **A pre-tokenizer** splits the text into words. There is at most one. Without one, the whole text is a single word.
1. **Token filters** run in the order listed, each on the output of the previous one. They remove words (`skip_non_alphanumeric`, `stopwords`), rewrite them (`stemmer`, `synonym`, `pg_dict`) or expand them (`ngram`).
{.steps}

Order matters because filters match exactly. Lowercase before stopwords and synonyms, or "The" survives a list that contains "the"; remove stopwords before stemming, because the lists hold unstemmed words.

The configuration is [TOML](https://toml.io/). A stage without options can be written as a string or as a table, so these two analyzers are the same:

```sql
SELECT tokenizer_catalog.create_text_analyzer('en_short', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ stopwords = "nltk_english" }, { stemmer = "english_porter2" }]
$$);

SELECT tokenizer_catalog.create_text_analyzer('en_long', $$
pre_tokenizer = "unicode_segmentation"

[[character_filters]]
to_lowercase = {}

[[token_filters]]
stopwords = "nltk_english"

[[token_filters]]
stemmer = "english_porter2"
$$);
```

In TOML, top-level keys such as `pre_tokenizer` must come before the first `[[table]]` header. An unknown key or an invalid value is rejected when you create the analyzer.

## Check what an analyzer produces {#test}

`apply_text_analyzer` returns the words in order, and `analyze_to_tsvector` shows the lexemes and positions that will be stored:

```sql
SELECT tokenizer_catalog.apply_text_analyzer('The Quick brown foxes', 'en_short');
SELECT tokenizer_catalog.analyze_to_tsvector('The Quick brown foxes', 'en_short');
```

```text
{quick,brown,fox}
'brown':2 'fox':3 'quick':1
```

Run a few real documents and queries through it before you store anything: changing it later means recomputing every stored value.

## Choose a pre-tokenizer {#pre-tokenizer}

| Text | Pre-tokenizer | Notes |
| --- | --- | --- |
| English and other languages with spaces | `unicode_segmentation` | Splits at Unicode word boundaries ([UAX #29](https://www.unicode.org/reports/tr29/)) and drops pieces with no letter or digit. |
| Chinese | `jieba` | Finds words with a dictionary. Returns punctuation and spaces as words too, so add `skip_non_alphanumeric`. |
| Japanese, Korean | none | Use a [Lindera model](/docs/tokenizer/models/#lindera) instead of an analyzer. |
| Codes, identifiers, log fields | `regex` | Every non-overlapping match of the pattern becomes a word, for example `regex = '[A-Za-z0-9_]+'`. |

jieba has three modes. `search`, the default, suits search indexes: it returns the most likely words and also the dictionary words inside long ones, so a query for a short word matches documents containing a longer word that includes it. `precise` returns only the most likely words, and `full` returns every dictionary word it finds, overlapping. For 我来到北京清华大学:

| Mode | Words |
| --- | --- |
| `precise` | 我, 来到, 北京, 清华大学 |
| `search` | 我, 来到, 北京, 清华, 华大, 大学, 清华大学 |
| `full` | 我, 来, 来到, 到, 北, 北京, 京, 清, 清华, 清华大学, 华, 华大, 大, 大学, 学 |

`enable_hmm`, on by default, lets `precise` and `search` join characters into words that are not in the dictionary, such as names.

## Filter words {#token-filters}

### Stopwords {#stopwords}

`stopwords` removes every word that appears in a list. Three English lists are built in: `lucene_english`, `nltk_english` and `iso_english`. For other languages or your own domain, create a list with one word per line; matching is exact and case-sensitive.

```sql
SELECT tokenizer_catalog.create_stopwords('my_stopwords', $$
it
is
an
$$);

SELECT tokenizer_catalog.create_text_analyzer('with_stopwords', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ stopwords = "my_stopwords" }]
$$);

SELECT tokenizer_catalog.apply_text_analyzer('It is an apple.', 'with_stopwords');
```

```text
{apple}
```

### Stemming {#stemmer}

`stemmer` reduces each word to its Snowball stem, so that "connected", "connecting" and "connection" become "connect". There are [30 algorithms](/docs/tokenizer/reference/#stemmers); for English use `english_porter2`. Stemmers expect lowercase input.

### Synonyms {#synonym}

`synonym` replaces words with a chosen form. Each line of a synonym list starts with that form and continues with the words that map to it; a word may appear only once in a list.

```sql
SELECT tokenizer_catalog.create_synonym('db_terms', $$
postgres pgsql postgresql
index indices indexes
$$);

SELECT tokenizer_catalog.create_text_analyzer('with_synonyms', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ synonym = "db_terms" }]
$$);

SELECT tokenizer_catalog.apply_text_analyzer('PostgreSQL indexes', 'with_synonyms');
```

```text
{postgres,index}
```

Put `synonym` before `stemmer`, so the list holds the words as people write them.

### PostgreSQL dictionaries {#pg_dict}

`pg_dict` passes each word to a PostgreSQL [text search dictionary](https://www.postgresql.org/docs/current/textsearch-dictionaries.html), as `ts_lexize` does: Snowball dictionaries such as `german_stem`, Ispell, synonym and thesaurus dictionaries, or one from an extension such as `unaccent`. A word the dictionary does not recognize passes through unchanged, and a word it reports as a stopword is removed. A thesaurus sees one word at a time, so only its single-word entries apply.

The name is looked up with the creating session's `search_path` when you create the analyzer, and stored with its schema. Later changes to the dictionary take effect without reconnecting, but renaming it or moving it to another schema means recreating the analyzer.

### N-grams {#ngram}

`ngram` replaces each word with all of its substrings from `min_gram` to `max_gram` characters long, which lets a query match part of a word, such as an identifier fragment or a product code. Lengths count characters, not bytes. A word shorter than `min_gram` produces nothing unless `preserve_original = true` keeps it.

```sql
SELECT tokenizer_catalog.create_text_analyzer('trigrams', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [{ ngram = { min_gram = 3, max_gram = 3 } }]
$$);
```

N-grams multiply the number of lexemes per document, and with them the index size; keep the range narrow.

### Punctuation {#skip_non_alphanumeric}

`skip_non_alphanumeric` removes words that contain no letter or digit. `unicode_segmentation` already does this, so you need the filter after `jieba`, `regex`, or no pre-tokenizer.

## Change an analyzer in use {#change}

A definition cannot be altered, and nothing recomputes the values stored from it. To change an analyzer that stored data depends on, create the new version under a new name and switch over:

1. Create the new analyzer, for example `en_text_v2`.
1. Add a column, fill it, and index it:

   ```sql
   ALTER TABLE en_docs ADD COLUMN terms_v2 tsvector;
   UPDATE en_docs SET terms_v2 = tokenizer_catalog.analyze_to_tsvector(body, 'en_text_v2');
   CREATE INDEX en_docs_bm25_v2 ON en_docs USING bm25 (terms_v2 bm25_ops);
   ```

1. Point the trigger and the queries at the new analyzer, column and index.
1. Drop the old column, then the old analyzer with `drop_text_analyzer('en_text')`.
{.steps}

On a small table you can instead drop and recreate the analyzer under the same name in one transaction, then run the `UPDATE` on the existing column. Until the `UPDATE` finishes, queries analyzed by the new definition run against documents analyzed by the old one.

Dropping an analyzer does not check what uses it. A tokenizer, custom model or trigger that names it fails at its next use with `TextAnalyzer not found: <name>`.
