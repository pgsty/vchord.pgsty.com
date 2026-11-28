---
title: "模型"
linkTitle: "模型"
description: "什么时候需要 pg_tokenizer 模型，以及如何使用内置大模型词表、用于日文和韩文的 Lindera 词典、Hugging Face 分词器和自定义词表。"
weight: 50
icon: fa-solid fa-cubes
---

模型把文本映射为固定词表中的整数词元 ID。只有两种情况需要它：切分日文或韩文，这需要 Lindera 词典；以及需要 ID 的时候，无论是某个大模型分词器的 ID，还是从你自己的表构建的词表 ID。对其他语言做 BM25 检索，只用[文本分析器](/zh/docs/tokenizer/text-analyzer/)就够了。

## 分词器如何使用模型 {#tokenizer}

模型要通过用 `create_tokenizer` 创建的**分词器**（tokenizer）来使用。分词器的配置指定 `model`，还可以指定一个先运行的分析器：要么用 `text_analyzer` 引用已有分析器的名称，要么直接内联写出分析器的各个键，二者不能同时使用。

- 没有分析器时，模型拿到整段文本，自己负责切分。内置模型、Hugging Face 模型和 Lindera 模型通常这样用。
- 有分析器时，模型分别处理分析器产生的每个词，再按顺序拼接得到的 ID。适合在查 ID 之前先去停用词或做词干提取；自定义模型则总是要配分析器。

```sql
SELECT tokenizer_catalog.create_tokenizer('bert_words', $$
model = "bert_base_uncased"
pre_tokenizer = { regex = '(?u)\b\w\w+\b' }
character_filters = ["to_lowercase"]
token_filters = [{ stopwords = "nltk_english" }, { stemmer = "english_porter2" }]
$$);

SELECT tokenizer_catalog.tokenize('PostgreSQL is a powerful, open-source database.', 'bert_words');
```

`tokenize` 以 `int[]` 返回 ID。`tokenize_to_tsvector` 则把 ID 作为词位返回，形如 `'2695':1 '17603':2`，vchord_bm25 可以像索引普通词一样索引它们；这时查询也必须经过同一个分词器。

词表里没有的词如何处理，取决于模型。子词模型（除 `wiki_tocken` 外的内置模型，以及大多数 Hugging Face 模型）会把它拆成已知的片段。Lindera 模型、自定义模型和 `wiki_tocken` 则直接丢弃它。

## 内置模型 {#builtin}

<a id="1-built-in-pretrained-models"></a>

所有安装包都带有四个词表。需要与某个模型完全相同的 ID 时，就用对应的内置模型。

| 模型 | 词表 | 说明 |
| --- | --- | --- |
| `bert_base_uncased` | [google-bert/bert-base-uncased](https://huggingface.co/google-bert/bert-base-uncased)，WordPiece | 英文，会把输入转成小写。 |
| `gemma2b` | [google/gemma-2b](https://huggingface.co/google/gemma-2b) | 加载后约占 100 MB。 |
| `llmlingua2` | [microsoft/llmlingua-2-xlm-roberta-large-meetingbank](https://huggingface.co/microsoft/llmlingua-2-xlm-roberta-large-meetingbank)，XLM-RoBERTa | 多语言。加载后约占 200 MB，默认[预加载](#preload)。 |
| `wiki_tocken` | 来自 [WikiText-103](https://huggingface.co/datasets/iohadrubin/wikitext-103-raw-v1) 的英文词 | 自带转小写、去英文停用词和词干提取，只输出整词。 |
{.wide}

```sql
SELECT tokenizer_catalog.create_tokenizer('gemma', $$
model = "gemma2b"
$$);

SELECT tokenizer_catalog.tokenize('PostgreSQL is a powerful, open-source database.', 'gemma');
```

## 日文与韩文：Lindera {#lindera}

<a id="4-lindera-morphological-models-create_lindera_model"></a>

`create_lindera_model` 根据 [Lindera](https://github.com/lindera/lindera) 7 的配置创建模型：一个 `[segmenter]` 表指定切分模式 `mode` 和词典 `dictionary`，后面跟着 Lindera 自己的 `[[character_filters]]` 和 `[[token_filters]]`，每项都有 `kind` 和 `args`。完整配置见[日文配方](/zh/docs/tokenizer/multilingual/#japanese)。

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

模型为找到的每个词返回它在词典中的 ID。词典里没有的词会被丢弃，被 Lindera 词元过滤器删掉的词也不会产生 ID。只改写词面文本的 Lindera 过滤器不会改变 ID。

`dictionary` 有两种来源：

- **内置在动态库中**，写作 `embedded://<name>`。GitHub 发布包和默认的源码构建内置了 `embedded://ipadic`。其他词典，即 `ipadic-neologd`、`unidic`、`ko-dic`（韩文）和 `cc-cedict`，只有在源码构建时启用对应[特性](/zh/docs/tokenizer/installation/#source)才可用。指定动态库中没有的词典会报 `failed to load Lindera dictionary`。
- **数据库服务器上的目录**，写成路径或 `file://` URI。Pigsty 软件包不含任何词典，只能用这种方式。目录必须是为 Lindera 7 构建的（format v3），并且安装在每个节点的相同路径下。PostgreSQL 以其操作系统用户的身份读取它，所以创建模型以及每个新会话加载模型时，都需要超级用户或 `pg_read_server_files` 成员身份；其他角色会收到 `permission denied to load a Lindera dictionary from a file`。[预加载](#preload)的模型由服务器在启动时加载，使用时不需要这项权限。

`user_dictionary` 从 CSV 或编译后的文件中加入自定义词，读取规则相同。这些词的 ID 从 1073741824 开始，不会与词典 ID 冲突。

## Hugging Face 分词器 {#huggingface}

<a id="3-importing-huggingface-tokenizers-create_huggingface_model"></a>

`create_huggingface_model` 可以导入任意 Hugging Face 模型的 `tokenizer.json`，从而在数据库里得到与外部嵌入模型相同的 ID。在 `psql` 中把文件读入变量再传入：

```sql
\set content `curl -fsSL https://huggingface.co/google-bert/bert-base-chinese/resolve/main/tokenizer.json`
SELECT tokenizer_catalog.create_huggingface_model('bert_chinese', :'content');

SELECT tokenizer_catalog.create_tokenizer('bert_chinese', $$
model = "bert_chinese"
$$);
```

文件中的每个 ID 都必须能放进 `int`，即不超过 2147483647；ID 更大的模型会被拒绝。

## 自定义模型 {#custom}

<a id="2-custom-corpus-models-create_custom_model"></a><a id="custom-model-100"></a><a id="option-a-one-step-helper-create_custom_model_tokenizer_and_trigger"></a><a id="option-b-step-by-step-create_custom_model"></a>

自定义模型为表中某一列出现的每个不同的词分配一个整数 ID。当你需要为自己的语料生成紧凑的 ID 时使用它，例如在数据库外构建稀疏向量。vchord_bm25 不需要它。

`create_custom_model` 用一个分析器处理该列，把每个不同的词存进词表 `tokenizer_data."model_<name>"`。它还会在源表上加一个触发器 `model_<name>_trigger`，在插入或更新行时把新出现的词加入词表。词表只增不减：被删除或修改的行里的词仍然保留。

`create_custom_model_tokenizer_and_trigger` 在此基础上还会为模型创建分词器，把每行的 ID 填进目标列，并再加一个触发器保持它最新：

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

目标列接收的是 `int[]`，按 `INSERT` 的规则做类型转换。如果要自己填充其他列，就用 `create_custom_model`，再用 `create_tokenizer` 创建一个引用同一分析器和该模型的分词器。

使用自定义模型时需要注意：

- `filter` 是一个针对源表列的 SQL 条件，不写 `WHERE`，用来限定语料范围。可以作为第七个参数传入，如 `filter => 'tenant_id = 42'`，也可以写在模型配置中。只有条件为真的行参与构建词表并得到 ID，其他行的目标列保持不变。它不能替代行级安全策略。
- PostgreSQL 按名称顺序触发 `BEFORE` 触发器。如果你自己的触发器在同一张表上调用 `tokenize` 或 `tokenize_to_tsvector`，它的名称必须排在 `model_<name>_trigger` 之后，否则这一行里新出现的词还不在词表中，会被丢弃。
- 超过 2,600 字节的词会被切成不超过 2,600 字节的若干片段，每段各有一个 ID，同时给出警告。
- 并发写入只有在向同一个模型添加新词时才会互相等待。在 `REPEATABLE READ` 或 `SERIALIZABLE` 下，这种冲突可能以 SQLSTATE `40001` 失败，需要重试事务。
- `drop_custom_model` 会删除词表和两个触发器，但不删除分词器。

## 预加载模型 {#preload}

<a id="5-model-preloading-add_preload_model"></a>

每个后端在第一次用到模型时加载它，并在连接存续期间一直保留。对于大模型，这意味着首次调用变慢，而且每个连接都占一份内存。预加载的模型在服务器启动时加载一次，所有后端共享。

```sql
SELECT tokenizer_catalog.list_preload_models();
SELECT tokenizer_catalog.add_preload_model('ja_ipadic');
SELECT tokenizer_catalog.remove_preload_model('llmlingua2');
```

修改后需要重启 PostgreSQL 才能生效。列表初始包含 `llmlingua2`，每次服务器启动约占 200 MB；不用的话就把它移除。

- 预加载被许多连接使用的大模型：Lindera 模型、`gemma2b`、`llmlingua2`。自定义模型预加载没有收益，因为它们是在词表里查词。
- 列表属于服务器而不是某个数据库。`add_preload_model` 保存的是当前数据库中该模型的定义；其他数据库只有在同名模型的定义完全相同时，才会使用预加载的副本。
- 列表是 `$PGDATA/pg_tokenizer/preload_models` 下的一组文件。修改会立即写入磁盘，即使事务回滚也不会撤销，并且不会复制到备库，见[副本与备份](/zh/docs/tokenizer/installation/#logical-backups)。
- 只有超级用户能修改它，除非被授予这两个函数的 `EXECUTE` 权限。加载失败的条目会被跳过，并在服务器日志中留下警告。
