---
title: "多语言配方"
linkTitle: "配方"
description: "用 pg_tokenizer 与 vchord_bm25 为英文、其他欧洲语言、中文和日文搭建 BM25 检索的完整 SQL。"
weight: 30
icon: fa-solid fa-earth-asia
---

每个配方从头到尾为一种语言搭好 BM25 检索：创建分析器或分词器，建一张由触发器维护 `tsvector` 列的表，建 vchord_bm25 索引，再执行一次排序查询。在已经[安装并预加载](/zh/docs/tokenizer/installation/#enable) pg_tokenizer 和 vchord_bm25 的数据库里运行，再把示例表换成你自己的表即可。

所有配方的结构都一样，原因见[限制](/zh/docs/tokenizer/overview/#limits)：

- `tsvector` 列由触发器填充，因为 pg_tokenizer 的函数是 `STABLE` 的，PostgreSQL 不允许把它们用在生成列里。
- 查询文本与文档经过同一个分析器或分词器，两边才会得到相同的词位。

`<&>` 返回的是 BM25 分数的相反数，所以 `ORDER BY ... LIMIT` 先返回最匹配的行。函数调用都带了模式前缀，无论 `search_path` 如何设置，配方都能运行。

## 英文 {#english}

<a id="recipe-1-english-with-stemming--stopwords-wiki_tocken"></a><a id="recipe-2-english-custom-corpus-model-with-trigger"></a>

分析器先把文本转成小写，按 Unicode 词边界切分（标点也随之去掉），删除 NLTK 英文停用词，再把每个词还原为 Porter2 词干，这样 "ranking"、"ranked" 和 "ranks" 可以互相匹配。

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

如果要给已有的表建索引：加上 `terms` 列和触发器，执行一次 `UPDATE en_docs SET terms = tokenizer_catalog.analyze_to_tsvector(body, 'en_text');` 填充该列，再创建索引。

## 其他以空格分词的语言 {#european}

法语、德语、西班牙语、俄语等用空格分隔单词的语言，只需替换英文配方中的分析器。有两种做法：

- 用 Snowball **词干提取器**（`stemmer`）加上你自己的停用词表。pg_tokenizer 提供 [30 种词干算法](/zh/docs/tokenizer/reference/#stemmers)，但只自带英文停用词表，其他语言的停用词表用 `create_stopwords` 创建。
- 用一个 **`pg_dict`** 过滤器，指定 PostgreSQL 的 Snowball 词典，例如 `french_stem` 或 `german_stem`，也就是 `to_tsvector` 处理该语言时所用的词典。它一步完成转小写、去除该语言的停用词和词干提取。

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

执行 `SELECT dictname FROM pg_ts_dict WHERE dictname LIKE '%\_stem';` 可以列出当前 PostgreSQL 提供的 Snowball 词典。

## 中文 {#chinese}

<a id="recipe-2-chinese-full-text-search-jieba--custom-model"></a><a id="recipe-3-chinese-full-text-search-jieba"></a>

中文词与词之间没有空格，所以分析器用结巴词典来切词。NFKC 规范化把全角字母和数字转成 ASCII，转小写让中文里夹杂的英文单词不分大小写都能匹配，`skip_non_alphanumeric` 去掉结巴当作词返回的标点和空格。结巴默认的 `search` 模式还会输出长词内部的短词，所以查询“数据”也能命中“数据库”。

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

pg_tokenizer 没有自带中文停用词表。如果想去掉“的”“了”这类高频词，用 `create_stopwords` 建一张停用词表，再在 `token_filters` 中加上 `{ stopwords = "<表名>" }`。

## 日文 {#japanese}

<a id="recipe-3-japanese-full-text-search-lindera-ipadic"></a><a id="recipe-4-japanese-full-text-search-lindera-ipadic"></a>

日文同样没有空格，找出其中的词需要形态学词典。这个配方用 IPADIC 词典创建一个 [Lindera](/zh/docs/tokenizer/models/#lindera) 模型，再创建一个使用它的分词器，把词在词典中的 ID 作为词位存储。切分之前，模型先做 NFKC 规范化，统一全角和半角形式，并展开“々”这类重复符号；切分之后，按词性删掉助词、助动词和符号。

配方使用 GitHub 发布包和源码构建中内置的 IPADIC 词典。Pigsty 软件包不含这个词典：请把 `embedded://ipadic` 换成为 Lindera 7 构建的 IPADIC 目录路径，并以超级用户或 `pg_read_server_files` 成员的身份运行配方。凡是加载这种模型的会话都需要该权限，包括插入数据时触发了触发器的应用角色，除非模型已经[预加载](/zh/docs/tokenizer/models/#preload)。

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

每个后端第一次分词时才加载词典。想在服务器启动时一次性加载，请[预加载这个模型](/zh/docs/tokenizer/models/#preload)。词典里没有的词会被丢弃，其中包括大多数拉丁字母写成的词，比如 PostgreSQL。韩文需要用 `lindera-ko-dic` 特性构建 pg_tokenizer，改用 `embedded://ko-dic`，并换成韩文的词性标签。
