---
title: "Multilingual Recipes"
linkTitle: "Recipes"
description: "Complete SQL to set up BM25 search with pg_tokenizer and vchord_bm25 for English, other European languages, Chinese and Japanese."
weight: 30
icon: fa-solid fa-earth-asia
---

Each recipe sets up BM25 search for one language from start to finish: it creates the analyzer or tokenizer, a table whose `tsvector` column a trigger keeps current, a vchord_bm25 index, and a ranked query. Run it in a database where pg_tokenizer and vchord_bm25 are [installed and preloaded](/docs/tokenizer/installation/#enable), then replace the sample table with your own.

All recipes share the same shape, for two reasons explained in [Limits](/docs/tokenizer/overview/#limits):

- The `tsvector` column is filled by a trigger, because the pg_tokenizer functions are `STABLE` and PostgreSQL does not allow them in a generated column.
- The query text goes through the same analyzer or tokenizer as the documents, so both sides produce the same lexemes.

`<&>` returns the negated BM25 score, so `ORDER BY ... LIMIT` returns the best matches first. Function calls are schema-qualified so the recipes work whatever the `search_path`.

## English {#english}

<a id="recipe-1-english-with-stemming--stopwords-wiki_tocken"></a><a id="recipe-2-english-custom-corpus-model-with-trigger"></a>

The analyzer lowercases the text, splits it at Unicode word boundaries (which also drops punctuation), removes the NLTK English stopwords, and reduces each word to its Porter2 stem, so that "ranking", "ranked" and "ranks" match each other.

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
CREATE EXTENSION IF NOT EXISTS vchord_bm25;

SELECT tokenizer_catalog.create_text_analyzer('en_text', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [
    { stopwords = "nltk_english" },
    { stemmer = "english_porter2" },
]
$$);

CREATE TABLE en_docs (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector
);

CREATE FUNCTION en_docs_terms() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.body, 'en_text');
    RETURN NEW;
END;
$$;

CREATE TRIGGER en_docs_terms BEFORE INSERT OR UPDATE OF body ON en_docs
FOR EACH ROW EXECUTE FUNCTION en_docs_terms();

INSERT INTO en_docs (body) VALUES
    ('PostgreSQL is an open-source object-relational database system.'),
    ('BM25 ranks documents by how often the query terms appear in them.'),
    ('vchord_bm25 adds a BM25 index to PostgreSQL.'),
    ('pg_tokenizer splits text into words before they are indexed.');

CREATE INDEX en_docs_bm25 ON en_docs USING bm25 (terms bm25_ops);

SELECT id, body
FROM en_docs
ORDER BY terms <&> to_bm25query(
    tokenizer_catalog.analyze_to_tsvector('ranking documents in PostgreSQL', 'en_text'),
    'en_docs_bm25')
LIMIT 10;
```

To index an existing table instead, add the `terms` column and the trigger, fill the column once with `UPDATE en_docs SET terms = tokenizer_catalog.analyze_to_tsvector(body, 'en_text');`, then create the index.

## Other languages with spaces {#european}

For French, German, Spanish, Russian and the other languages that separate words with spaces, change only the analyzer in the English recipe. Two choices:

- A Snowball **stemmer** with your own stopword list. pg_tokenizer has [30 stemmers](/docs/tokenizer/reference/#stemmers) but ships English stopword lists only; create others with `create_stopwords`.
- One **`pg_dict`** filter naming a PostgreSQL Snowball dictionary such as `french_stem` or `german_stem`, the dictionary `to_tsvector` uses for that language. It lowercases, removes the language's stopwords and stems in one step.

```sql
SELECT tokenizer_catalog.create_text_analyzer('de_text', $$
pre_tokenizer = "unicode_segmentation"
token_filters = [{ pg_dict = "german_stem" }]
$$);

SELECT tokenizer_catalog.apply_text_analyzer(
    'Aus so krummen Holze, als woraus der Mensch gemacht ist, kann nichts ganz Gerades gezimmert werden.',
    'de_text');
```

```text
{krumm,holz,woraus,mensch,gemacht,ganz,gerad,gezimmert}
```

`SELECT dictname FROM pg_ts_dict WHERE dictname LIKE '%\_stem';` lists the Snowball dictionaries your PostgreSQL has.

## Chinese {#chinese}

<a id="recipe-2-chinese-full-text-search-jieba--custom-model"></a><a id="recipe-3-chinese-full-text-search-jieba"></a>

Chinese has no spaces between words, so the analyzer uses the jieba dictionary to find them. NFKC normalization turns full-width letters and digits into ASCII, lowercasing makes English words inside Chinese text match regardless of case, and `skip_non_alphanumeric` drops the punctuation and spaces that jieba returns as tokens. jieba's default `search` mode also emits the shorter words inside a long one, so a query for 数据 finds 数据库.

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
CREATE EXTENSION IF NOT EXISTS vchord_bm25;

SELECT tokenizer_catalog.create_text_analyzer('zh_text', $$
character_filters = [{ unicode_normalization = "nfkc" }, "to_lowercase"]
pre_tokenizer = { jieba = { mode = "search" } }
token_filters = ["skip_non_alphanumeric"]
$$);

CREATE TABLE zh_docs (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector
);

CREATE FUNCTION zh_docs_terms() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.body, 'zh_text');
    RETURN NEW;
END;
$$;

CREATE TRIGGER zh_docs_terms BEFORE INSERT OR UPDATE OF body ON zh_docs
FOR EACH ROW EXECUTE FUNCTION zh_docs_terms();

INSERT INTO zh_docs (body) VALUES
    ('PostgreSQL 是一个开源的关系型数据库管理系统。'),
    ('全文检索需要先把句子切分成词语，再建立倒排索引。'),
    ('结巴分词根据词典和隐马尔可夫模型切分中文句子。'),
    ('vchord_bm25 在 PostgreSQL 中按 BM25 分数对文档排序。');

CREATE INDEX zh_docs_bm25 ON zh_docs USING bm25 (terms bm25_ops);

SELECT id, body
FROM zh_docs
ORDER BY terms <&> to_bm25query(
    tokenizer_catalog.analyze_to_tsvector('中文分词与全文检索', 'zh_text'),
    'zh_docs_bm25')
LIMIT 10;
```

pg_tokenizer has no Chinese stopword list. To drop common words such as 的 and 了, create one with `create_stopwords` and add `{ stopwords = "<name>" }` to `token_filters`.

## Japanese {#japanese}

<a id="recipe-3-japanese-full-text-search-lindera-ipadic"></a><a id="recipe-4-japanese-full-text-search-lindera-ipadic"></a>

Japanese has no spaces either, and finding its words needs a morphological dictionary. The recipe creates a [Lindera](/docs/tokenizer/models/#lindera) model with the IPADIC dictionary and a tokenizer that uses it, and stores the dictionary IDs of the words as lexemes. Before segmenting, the model folds full-width and half-width forms (NFKC) and expands repetition marks such as 々; afterwards it drops particles, auxiliary verbs and symbols by their part of speech.

The recipe uses the IPADIC dictionary built into the GitHub release packages and source builds. Pigsty packages do not include it: replace `embedded://ipadic` with the path of an IPADIC directory built for Lindera 7, and run the recipe as a superuser or a member of `pg_read_server_files`. Every session that loads such a model needs that privilege, including the application role whose inserts fire the trigger, unless the model is [preloaded](/docs/tokenizer/models/#preload).

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
CREATE EXTENSION IF NOT EXISTS vchord_bm25;

SELECT tokenizer_catalog.create_lindera_model('ja_ipadic', $$
[segmenter]
mode = "normal"
dictionary = "embedded://ipadic"

[[character_filters]]
kind = "unicode_normalize"
  [character_filters.args]
  kind = "nfkc"

[[character_filters]]
kind = "japanese_iteration_mark"
  [character_filters.args]
  normalize_kanji = true
  normalize_kana = true

[[token_filters]]
kind = "japanese_stop_tags"
  [token_filters.args]
  tags = [
    "接続詞", "助詞", "助詞,格助詞", "助詞,格助詞,一般", "助詞,格助詞,引用",
    "助詞,格助詞,連語", "助詞,係助詞", "助詞,副助詞", "助詞,間投助詞",
    "助詞,並立助詞", "助詞,終助詞", "助詞,副助詞／並立助詞／終助詞",
    "助詞,連体化", "助詞,副詞化", "助詞,特殊", "助動詞", "記号",
    "記号,一般", "記号,読点", "記号,句点", "記号,空白", "記号,括弧閉",
    "その他,間投", "フィラー", "非言語音",
  ]
$$);

SELECT tokenizer_catalog.create_tokenizer('ja_text', $$
model = "ja_ipadic"
$$);

CREATE TABLE ja_docs (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector
);

CREATE FUNCTION ja_docs_terms() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.terms := tokenizer_catalog.tokenize_to_tsvector(NEW.body, 'ja_text');
    RETURN NEW;
END;
$$;

CREATE TRIGGER ja_docs_terms BEFORE INSERT OR UPDATE OF body ON ja_docs
FOR EACH ROW EXECUTE FUNCTION ja_docs_terms();

INSERT INTO ja_docs (body) VALUES
    ('PostgreSQL はオープンソースのリレーショナルデータベースです。'),
    ('全文検索では文章を単語に分割してから索引を作ります。'),
    ('日本語の文章には単語の間に空白がありません。'),
    ('vchord_bm25 は PostgreSQL に BM25 のランキングを追加します。');

CREATE INDEX ja_docs_bm25 ON ja_docs USING bm25 (terms bm25_ops);

SELECT id, body
FROM ja_docs
ORDER BY terms <&> to_bm25query(
    tokenizer_catalog.tokenize_to_tsvector('日本語の全文検索', 'ja_text'),
    'ja_docs_bm25')
LIMIT 10;
```

Each backend loads the dictionary the first time it tokenizes. To load it once at server start instead, [preload the model](/docs/tokenizer/models/#preload). Words that are not in the dictionary are left out, and that includes most words in Latin letters, such as PostgreSQL. For Korean, build pg_tokenizer with the `lindera-ko-dic` feature and use `embedded://ko-dic` with Korean part-of-speech tags.
