---
title: "Multilingual Recipes & Limitations"
description: "Complete tokenization configurations for English, Chinese (Jieba), Japanese (Lindera), and known limitations."
weight: 40
icon: fa-solid fa-language
---

This page provides production-ready tokenization recipes for English, Chinese, and Japanese full-text BM25 search, followed by important operational limitations to keep in mind.

## Recipe 1: English with Stemming & Stopwords (`wiki_tocken`)

Combines Unicode word segmentation, NLTK stopwords removal, and Porter2 stemming with the built-in Wikipedia vocabulary (`wiki_tocken`):

```sql
SELECT create_tokenizer('eng_wiki', $$
model = "wiki_tocken"

[text_analyzer.character_filters.to_lowercase]
[text_analyzer.pre_tokenizer.unicode_segmentation]
[[text_analyzer.token_filters.skip_non_alphanumeric]]
[[text_analyzer.token_filters.stopwords]]
words = "nltk_english"
[[text_analyzer.token_filters.stemmer]]
kind = "english_porter2"
$$);

SELECT tokenize('PostgreSQL databases are running analytical and vector workloads.', 'eng_wiki');
```

## Recipe 2: English Custom Corpus Model with Trigger

From the upstream [`pg_tokenizer` examples](https://github.com/pgsty/pg_tokenizer/blob/main/docs/03-examples.md), this workflow builds a domain-specific English vocabulary from your `documents` table and keeps embeddings updated automatically via trigger:

```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

SELECT create_text_analyzer('text_analyzer1', $$
pre_tokenizer = "unicode_segmentation"
[[character_filters]]
to_lowercase = {}
[[character_filters]]
unicode_normalization = "nfkd"
[[token_filters]]
skip_non_alphanumeric = {}
[[token_filters]]
stopwords = "nltk_english"
[[token_filters]]
stemmer = "english_porter2"
$$);

SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'tokenizer1',
    model_name => 'model1',
    text_analyzer_name => 'text_analyzer1',
    table_name => 'documents',
    source_column => 'passage',
    target_column => 'embedding'
);

INSERT INTO documents (passage) VALUES
('PostgreSQL is a powerful, open-source object-relational database system. It has over 15 years of active development and a proven architecture that has earned it a strong reputation for reliability, feature robustness, and performance.'),
('Full-text search is a technique for searching a computer-stored document or a collection in a full-text database. Full-text search is distinguished from searches based on metadata or on parts of the original texts represented in databases (such as titles, abstracts, selected sections, or bibliographical references).'),
('BM25 is a ranking function used by search engines to estimate the relevance of documents to a given search query. It is based on the probabilistic retrieval framework developed in the 1970s and 1980s by Stephen E. Robertson, Karen Spärck Jones, and others.'),
('PostgreSQL supports advanced data types and performance optimization features, only available in the expensive commercial databases, such as Oracle and SQL Server. It is known for its resilience, integrity, and correctness.'),
('The BM25 algorithm computes a score for each document in a collection based on the query terms appearing in the document, regardless of their proximity within the document. It is a bag-of-words retrieval function that ranks a set of documents based on the query terms appearing in each document.'),
('PostgreSQL has a wide range of extensions and tools that make it suitable for various use cases, from small single-machine applications to large internet-facing applications with many concurrent users.'),
('Full-text search in PostgreSQL allows users to perform complex queries on text data, including phrase searching, ranking of results, and support for multiple languages through configurations and dictionaries.'),
('VectorChord-BM25 is a postgresql extension designed for bm25 ranking algorithm. Block-WeakAnd algorithm is implemented in it to accelerate the ranking process.'),
('pg_tokenizer is a postgresql extension designed for full-text search. It provides a set of functions to preprocess text data and generate tokens for indexing and searching.'),
('Look for organizations which use PostgreSQL for mission-critical or scaled applications. Look for organizations that have used PostgreSQL for a significant length of time.');

CREATE INDEX documents_passage_bm25 ON documents USING bm25 (embedding bm25_ops);

SELECT id, passage, embedding <&> to_bm25query('documents_passage_bm25', tokenize('PostgreSQL BM25', 'tokenizer1')) AS rank
FROM documents
ORDER BY rank
LIMIT 10;
```

## Recipe 3: Chinese Full-Text Search (`jieba` + Custom Model)

For Chinese text, combine the `jieba` pre-tokenizer (`mode = "search"`, `enable_hmm = true`) with a custom corpus model trained on your table (demonstrated below using passages from Qian Zhongshu's *Fortress Besieged* / 《围城》):

```sql
CREATE TABLE zh_docs (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

-- 1. Create Chinese text analyzer with NFKD normalization and Jieba search mode
SELECT create_text_analyzer('text_analyzer1', $$
[character_filters.to_lowercase]
[character_filters.unicode_normalization]
kind = "nfkd"
[pre_tokenizer.jieba]
mode = "search"
enable_hmm = true
[[token_filters.skip_non_alphanumeric]]
$$);

-- 2. Create custom vocabulary model, tokenizer, and auto-update trigger
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'tokenizer1',
    model_name         => 'model1',
    text_analyzer_name => 'text_analyzer1',
    table_name         => 'zh_docs',
    source_column      => 'passage',
    target_column      => 'embedding'
);

-- 3. Insert Chinese corpus (trigger automatically populates embedding)
INSERT INTO zh_docs (passage) VALUES
('红海早过了，船在印度洋面上开驶着，但是太阳依然不饶人地迟落早起，侵占去大部分的夜。'),
('夜仿佛纸浸了油，变成半透明体；它给太阳拥抱住了，分不出身来，也许是给太阳陶醉了，所以夕照霞隐褪后的夜色也带着酡红。'),
('到红消醉醒，船舱里的睡人也一身腻汗地醒来，洗了澡赶到甲板上吹海风，又是一天开始。'),
('这是七月下旬，合中国旧历的三伏，一年最热的时候。在中国热得更比常年利害，事后大家都说是兵戈之象，因为这就是民国二十六年【一九三七年】。'),
('这条法国邮船白康蒂号（VicomtedeBragelonne）正开向中国来。早晨八点多钟，冲洗过的三等舱甲板湿意未干，但已坐立满了人，法国人、德国流亡出来的犹太人、印度人、安南人，不用说还有中国人。'),
('海风里早含着燥热，胖人身体给风吹干了，蒙上一层汗结的盐霜，仿佛刚在巴勒斯坦的死海里洗过澡。'),
('毕竟是清晨，人的兴致还不没给太阳晒萎，烘懒，说话做事都很起劲。那几个新派到安南或中国租界当警察的法国人，正围了那年轻善撒娇的犹太女人在调情。'),
('俾斯麦曾说过，法国公使大使的特点，就是一句外国话不会讲；这几位警察并不懂德文，居然传情达意，引得犹太女人格格地笑，比他们的外交官强多了。'),
('这女人的漂亮丈夫，在旁顾而乐之，因为几天来，香烟、啤酒、柠檬水全靠这几个警察孝敬。船上买东西用法国钱，这犹太人只有一点儿沿着那位丹麦王子汉姆烈德（Hamlet）路线逃出来的德国马克。'),
('当时德国跟日本虽在谈恋爱，尚未结婚，到中国来的犹太人还是德国公民，有他们本国的保护。这船上的犹太人有过路到香港的，有到上海居留的，聚在一起在讨论生计，声音活像小洋磁盆里托的石子。'),
('几个年轻的安南人比手画脚，像猴子跳电线一样迅捷地交换着法语，华侨在旁羡慕地听着。这船上都是回家乡的中国人，像报纸上的标题，电影的字幕，标语，籍贯姓名年纪一张表上那几格，他们老早填满了，此番回来，不过把这些公式平滑无波地重演一次。'),
('只有鼻梁上架着一副黑眼镜的苏小姐，心算着她离国这几年，家里有什么变化，她父亲是否老了，她母亲新添了什么病痛，她弟弟结婚了没有。'),
('苏小姐在里昂研究法国文学，做了一篇《中国十八世纪的法国文学里的中国》的论文，刚得了博士。'),
('方鸿渐也到甲板上来了，在苏小姐身旁走过，向她脱帽招呼。苏小姐一壁应着，一壁想他真算厚脸皮，昨天向自己借了照相机，今天见了面，提都不提。');

-- 4. Create BM25 index and search
CREATE INDEX zh_docs_passage_bm25 ON zh_docs USING bm25 (embedding bm25_ops);

SELECT id, passage,
       embedding <&> to_bm25query('zh_docs_passage_bm25', tokenize('苏小姐 法国', 'tokenizer1')) AS rank
FROM zh_docs
ORDER BY rank
LIMIT 10;
```

## Recipe 4: Japanese Full-Text Search (`lindera` IPADIC)

When upgrading from Lindera 0.42 to 6.2, regenerate stored token arrays and rebuild their indexes because the IPADIC token IDs change. The dictionary configuration below remains supported; see the [Lindera migration notes](/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model).

For Japanese text, create a Lindera IPADIC morphological model with iteration mark normalization, NFKC normalization, Japanese stop-tag filtering, and Katakana stemming (demonstrated below using passages from Natsume Sōseki's *I Am a Cat* / 《吾輩は猫である》):

```sql
CREATE TABLE jp_docs (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

INSERT INTO jp_docs (passage) VALUES
('吾輩は猫である。名前はまだ無い。'),
('どこで生れたかとんと見当がつかぬ。何でも薄暗いじめじめした所でニャーニャー泣いていた事だけは記憶している。'),
('吾輩はここで始めて人間というものを見た。しかもあとで聞くとそれは書生という人間中で一番獰悪な種族であったそうだ。'),
('この書生というのは時々我々を捕えて煮て食うという話である。しかしその当時は何という考もなかったから別段恐しいとも思わなかった。'),
('ただ彼の掌に載せられてスーと持ち上げられた時何だかフワフワした感じがあったばかりである。'),
('掌の上で少し落ちついて書生の顔を見たのがいわゆる人間というものの見始であろう。この時妙なものだと思った感じが今でも残っている。'),
('第一毛をもって装飾されべきはずの顔がつるつるしてまるで薬缶だ。その後猫にもだいぶ逢ったがこんな片輪には一度も出会わした事がない。'),
('のみならず顔の真中があまりに突起している。そうしてその穴の中から時々ぷうぷうと煙を吹く。どうも咽せぽくて実に弱った。'),
('これが人間の飲む煙草というものである事はようやくこの頃知った。'),
('この書生の掌の裏でしばらくはよい心持に坐っておったが、しばらくすると非常な速力で運転し始めた。'),
('書生が動くのか自分だけが動くのか分らないが無暗に眼が廻る。胸が悪くなる。到底助からないと思っていると、どさりと音がして眼から火が出た。'),
('それまでは記憶しているがあとは何の事やらいくら考え出そうとしても分らない。'),
('ふと気が付いて見ると書生はいない。たくさんおった兄弟が一疋も見えぬ。肝心の母親さえ姿を隠してしまった。'),
('その上今までの所とは違って無暗に明るい。眼を明いていられぬくらいだ。果てな何でも容子がおかしいと、のそのそ這い出して見ると非常に痛い。'),
('吾輩は藁の上から急に笹原の中へ棄てられたのである。');

SELECT create_lindera_model('lindera_ipadic', $$
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
    "接続詞", "助詞", "助詞,格助詞", "助詞,格助詞,一般", "助詞,格助詞,引用",
    "助詞,格助詞,連語", "助詞,係助詞", "助詞,副助詞", "助詞,間投助詞",
    "助詞,並立助詞", "助詞,終助詞", "助詞,副助詞／並立助詞／終助詞",
    "助詞,連体化", "助詞,副詞化", "助詞,特殊", "助動詞", "記号",
    "記号,一般", "記号,読点", "記号,句点", "記号,空白", "記号,括弧閉",
    "その他,間投", "フィラー", "非言語音"
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

SELECT create_tokenizer('tokenizer1', $$
model = "lindera_ipadic"
$$);

UPDATE jp_docs SET embedding = tokenize(passage, 'tokenizer1');

CREATE INDEX jp_docs_passage_bm25 ON jp_docs USING bm25 (embedding bm25_ops);

SELECT id, passage,
       embedding <&> to_bm25query('jp_docs_passage_bm25', tokenize('人間 吾輩', 'tokenizer1')) AS rank
FROM jp_docs
ORDER BY rank
LIMIT 10;
```

## Operational Notes & Known Limitations

1. **Object Name Validation**: All names for tokenizers, text analyzers, models, stopword dictionaries, and synonym dictionaries must contain only alphanumeric characters and underscores (`[A-Za-z0-9_]`), and must not start with a digit.
2. **Transaction boundaries & object cache**: Each PostgreSQL backend caches `tokenizer`, `text_analyzer`, `model`, `stopwords`, and `synonym` objects in backend memory (`DashMap`). In 0.2.0, create/drop/rebuild operations clear the current backend and publish cache invalidation at transaction commit or abort. Other backends discard stale definitions before their next lookup, and a rollback does not leave a created object in the cache. Replacing an analyzer or model also invalidates dependent tokenizers. Persisted `INT[]`, `bm25vector`, and `tsvector` values are not rewritten automatically; recompute them after an intentional definition replacement.
3. **Preload Models Across Replicas**: `add_preload_model` writes the preload model list to the local `$PGDATA/pg_tokenizer` directory on the primary node. Because filesystem files outside PostgreSQL relations are not replicated via WAL, you should run `add_preload_model` on read replicas independently if you preload models there.
4. **Memory Consumption of Built-in LLM Models**: Models like `llmlingua2` (~200 MB), `gemma2b` (~100 MB), and `lindera` consume significant memory. Always use `add_preload_model` in production so the model is loaded once in the postmaster process rather than duplicated per connection, or prefer a custom corpus model (`create_custom_model`) which uses only a few megabytes.
