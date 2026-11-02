---
title: "多语言分词配方与限制"
description: "面向英文、中文（结巴 Jieba）、日文（Lindera）的完整生产级分词配置方案及已知使用限制。"
weight: 40
---

本页提供可直接用于生产环境的英文、中文和日文全文 BM25 检索分词配置配方，并列出在实际运维中需要注意的关键限制事项。

## 配方一：带词干提取与停用词过滤的英文检索（`wiki_tocken`） {#recipe-1-english-with-stemming--stopwords-wiki_tocken}

将 Unicode 词边界切分、NLTK 停用词过滤、Porter2 词干提取与内置维基百科词表（`wiki_tocken`）结合使用：

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

## 配方二：带自动触发器的英文自定义语料库模型 {#recipe-2-english-custom-corpus-model-with-trigger}

源自上游 [`pg_tokenizer` 示例文档](https://github.com/pgsty/pg_tokenizer/blob/main/docs/03-examples.md)，该工作流直接基于 `documents` 表构建特定领域的英文词表，并通过触发器自动同步更新词频向量：

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

## 配方三：中文全文检索（`jieba` + 自定义模型） {#recipe-2-chinese-full-text-search-jieba--custom-model}

处理中文文本时，推荐将 `jieba` 预分词器（`mode = "search"`，`enable_hmm = true`）与基于业务表训练的自定义语料词表模型结合使用（以下示例采用钱钟书《围城》选段作为测试语料）：

```sql
CREATE TABLE zh_docs (
    id SERIAL PRIMARY KEY,
    passage TEXT,
    embedding bm25vector
);

-- 1. 创建启用 NFKD 规范化与结巴搜索引擎模式的中文文本分析器
SELECT create_text_analyzer('text_analyzer1', $$
[character_filters.to_lowercase]
[character_filters.unicode_normalization]
kind = "nfkd"
[pre_tokenizer.jieba]
mode = "search"
enable_hmm = true
[[token_filters.skip_non_alphanumeric]]
$$);

-- 2. 创建自定义词表模型、分词器，并绑定自动更新触发器
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'tokenizer1',
    model_name         => 'model1',
    text_analyzer_name => 'text_analyzer1',
    table_name         => 'zh_docs',
    source_column      => 'passage',
    target_column      => 'embedding'
);

-- 3. 写入中文语料（触发器会自动分词并填充 embedding 列）
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

-- 4. 创建 BM25 索引并执行检索
CREATE INDEX zh_docs_passage_bm25 ON zh_docs USING bm25 (embedding bm25_ops);

SELECT id, passage,
       embedding <&> to_bm25query('zh_docs_passage_bm25', tokenize('苏小姐 法国', 'tokenizer1')) AS rank
FROM zh_docs
ORDER BY rank
LIMIT 10;
```

## 配方四：日文全文检索（`lindera` IPADIC） {#recipe-3-japanese-full-text-search-lindera-ipadic}

从 Lindera 0.42 升级到 6.2 时，IPADIC 词元 ID 会变化，需要重新生成已存储的词元数组并重建相关索引。下方的词典配置仍然兼容，详见 [Lindera 升级说明](/zh/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model)。

处理日文文本时，可创建基于 Lindera IPADIC 的形态学分词模型，并配置叠字符规范化、NFKC 规范化、日文停用词性（Stop-tags）过滤以及片假名词干提取（以下示例采用夏目漱石《吾輩は猫である》选段作为测试语料）：

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

## 运维注意事项与已知限制 {#operational-notes--known-limitations}

1. **对象名称命名规范**：所有分词器、文本分析器、模型、停用词典和同义词典的名称只能包含字母、数字和下划线（`[A-Za-z0-9_]`），且不能以数字开头。
2. **事务回滚与会话级内存对象缓存**：每个 PostgreSQL 后端连接都会在进程内存（`DashMap`）中缓存 `tokenizer`、`text_analyzer`、`model`、`stopwords` 和 `synonym` 对象。由于该内存对象池未挂载到 PostgreSQL 事务回滚回调机制上，当事务执行 `ROLLBACK` 时，磁盘上的 `tokenizer_catalog` 元数据表会回滚，但当前连接的内存缓存中仍会残留刚才创建的对象。在 `ROLLBACK` 之后，请显式调用对应的 `drop_*` 函数（或重新建立数据库连接）以清理内存缓存：
   ```sql
   BEGIN;
   SELECT create_text_analyzer('text_analyzer1', $$
   pre_tokenizer = "unicode_segmentation"
   $$);
   ROLLBACK;

   -- 清理当前会话内存中残留的缓存项（或者重新建立数据库连接）
   SELECT drop_text_analyzer('text_analyzer1');

   -- 现在可以正常重新创建同名对象
   SELECT create_text_analyzer('text_analyzer1', $$
   pre_tokenizer = "unicode_segmentation"
   $$);
   ```
3. **只读从库上的模型预加载**：`add_preload_model` 会将预加载模型列表写入主节点本地的 `$PGDATA/pg_tokenizer` 目录。由于 PostgreSQL 关系表以外的文件系统文件不会通过 WAL 日志复制到从库，如果你在只读从库上也需要预加载模型，请在从库上独立执行一次 `add_preload_model`。
4. **内置大语言模型分词器的内存开销**：`llmlingua2`（~200 MB）、`gemma2b`（~100 MB）和 `lindera` 等模型会占用较多内存。在生产环境中，请务必使用 `add_preload_model` 让模型在 postmaster 主进程中仅加载一次，避免在每个连接中重复占用内存；或者优先选用仅占用几兆字节内存的自定义语料模型（`create_custom_model`）。
