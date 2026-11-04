---
title: "分词词表模型"
description: "预训练模型（llmlingua2、bert_base_uncased、wiki_tocken、gemma2b）、自定义语料训练模型、HuggingFace 分词器与 Lindera 模型。"
weight: 30
icon: fa-solid fa-brain
---

在 `pg_tokenizer` 中，**模型（Model）** 负责将字符串词元（或原始文本）映射为整数词元 ID（`INT[]`）。你可以直接选用四个内置预训练模型、在 PostgreSQL 表上训练自定义词表模型、导入任意 HuggingFace `tokenizer.json`，或者使用 Lindera 形态学分析模型。

## 1. 内置预训练模型 {#1-built-in-pretrained-models}

| 模型名称 | 来源 / 架构 | 是否需要 `text_analyzer`？ | 内存占用 | 适用场景 |
| :--- | :--- | :--- | :--- | :--- |
| **`llmlingua2`** | [`microsoft/llmlingua-2-xlm-roberta-large-meetingbank`](https://huggingface.co/microsoft/llmlingua-2-xlm-roberta-large-meetingbank)（XLM-RoBERTa 多语言子词模型） | 否（禁止） | ~200 MB（默认预加载） | 开箱即用的多语言通用文本分词，无需训练自定义词表。 |
| **`bert_base_uncased`** | [`google-bert/bert-base-uncased`](https://huggingface.co/google-bert/bert-base-uncased)（WordPiece，30,522 词表） | 否（禁止） | ~15 MB | 通用英文文本；启动极快且词表紧凑。 |
| **`wiki_tocken`** | [`Snowolf/wiki-tocken`](https://huggingface.co/Snowolf/wiki-tocken)（内置英文维基百科词元词典） | **是（必需）** | ~30 MB | 配合自定义词干提取器、停用词与同义词使用的英文全文检索。 |
| **`gemma2b`** | [`google/gemma-2b`](https://huggingface.co/google/gemma-2b)（SentencePiece BPE，256k 词表） | 否（禁止） | ~100 MB | 代码、技术标识符以及多语言大语言模型工作负载。 |
{.wide .expand}

### 示例：使用 `bert_base_uncased` 或 `llmlingua2` {#example-using-bert_base_uncased-or-llmlingua2}

```sql
SELECT create_tokenizer('bert_tok', $$
model = "bert_base_uncased"
$$);

SELECT tokenize('VectorChord-BM25 brings Block-WeakAnd to PostgreSQL.', 'bert_tok');
```

---

## 2. 自定义语料库模型（`create_custom_model`） {#2-custom-corpus-models-create_custom_model}

为了获得最高的 BM25 相关性精度与最小的内存占用，你可以直接基于自己的业务表列构建**自定义词表模型**。不同于大语言模型子词分词器（会将罕见的领域专有名词切碎为多个子词元），自定义模型会为 `text_analyzer` 产出的每个唯一归一化词元分配独立的 1:1 整数 ID，且在内存中仅占用几兆字节。

### 方式 A：一步到位辅助函数（`create_custom_model_tokenizer_and_trigger`） {#option-a-one-step-helper-create_custom_model_tokenizer_and_trigger}

该便捷函数会一步完成创建自定义模型、创建分词器、为所有存量行回填目标 `bm25vector` 列，并安装一个 `BEFORE INSERT OR UPDATE` 触发器——当数据行发生变化时，自动学习新词元并更新 `bm25vector` 列：

```sql
-- 1. 定义文本分析流水线
SELECT create_text_analyzer('my_analyzer', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = [
    "skip_non_alphanumeric",
    { stopwords = "nltk_english" },
    { stemmer = "english_porter2" },
]
$$);

-- 2. 创建模型与分词器、回填向量并挂载触发器
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name     => 'my_tokenizer',
    model_name         => 'my_model',
    text_analyzer_name => 'my_analyzer',
    table_name         => 'documents',
    source_column      => 'passage',
    target_column      => 'embedding'
);
```

### 方式 B：分步创建（不使用触发器的 `create_custom_model`） {#option-b-step-by-step-create_custom_model}

如果你不希望挂载自动触发器（或者希望自行控制何时计算并回填 `embedding` 列）：

```sql
-- 1. 基于现有表列构建自定义词表模型
SELECT create_custom_model('my_model', $$
table = "documents"
column = "passage"
text_analyzer = "my_analyzer"
$$);

-- 2. 创建引用该分析器与自定义模型的分词器
SELECT create_tokenizer('my_tokenizer', $$
text_analyzer = "my_analyzer"
model = "my_model"
$$);

-- 3. 手动回填或刷新词频向量列
UPDATE documents SET embedding = tokenize(passage, 'my_tokenizer');
```

---

## 3. 导入 HuggingFace 分词器（`create_huggingface_model`） {#3-importing-huggingface-tokenizers-create_huggingface_model}

你可以使用 `create_huggingface_model` 将任意 HuggingFace [`tokenizers`](https://github.com/huggingface/tokenizers) 的 JSON 配置文件（`tokenizer.json`）导入 PostgreSQL。

在 `psql` 中，可以使用 `\set` 直接从 HuggingFace Hub 下载 `tokenizer.json` 到变量中并传给 `create_huggingface_model`：

```sql
\set content `wget -q -O - https://huggingface.co/google-bert/bert-base-uncased/resolve/main/tokenizer.json`
SELECT create_huggingface_model('bert_import', :'content');

SELECT create_tokenizer('bert_import_tok', $$
model = "bert_import"
$$);
```

也可以直接将 `tokenizer.json` 文件的完整内容作为美元符号引用的字符串传入：

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

## 4. Lindera 形态学分词模型（`create_lindera_model`） {#4-lindera-morphological-models-create_lindera_model}

对于日文、韩文、中文等需要形态学词典分析的东亚语言，`pg_tokenizer` 集成了 [`lindera`](https://github.com/lindera/lindera)。

使用 Lindera 6.2 构建时，原生词典配置为 `[segmenter]` 下的 `dictionary = "embedded://ipadic"`。目录表与预加载文件中已有的 `[segmenter.dictionary] kind = "ipadic"` 配置仍然兼容，旧格式的词典及用户词典 `path` 表也继续支持。外部编译词典需要使用 Lindera 6 重新构建。

> [!IMPORTANT]
> Lindera 6.2 内嵌的 IPADIC 从 Lindera 0.42 使用的 2007-08-01 版升级到 2025-09-20 版，词元 ID 会变化。使用升级后的分词器查询前，请重新生成已存储的 Lindera 词元数组，并重建使用这些数组的索引。未知词仍然会被过滤。

> [!NOTE]
> 如果你从源码编译 `pg_tokenizer`，请在编译时通过 `--features` 启用所需的 Lindera 词典特性：
> ```bash
> cargo pgrx install --release --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

以下完整示例展示了基于 `ipadic` 词典配置日文叠字符（Iteration Mark）规范化、NFKC Unicode 规范化、字符映射、复合词合并、数词归一化、日文停用词性（Stop-tags）过滤、片假名词干提取以及变音符号移除：

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

## 5. 模型预加载（`add_preload_model`） {#5-model-preloading-add_preload_model}

大型模型（如约 200 MB 的 `llmlingua2`、约 100 MB 的 `gemma2b`、`japanese_ipadic`）在每个新建的 PostgreSQL 后端进程首次查询时，需要数秒钟时间和可观的内存来加载。通过在 `shared_preload_libraries` 启动阶段预加载模型，PostgreSQL 只需在 postmaster 主进程中加载一次模型，即可通过写时复制（Copy-on-Write）内存在所有后端连接之间共享（`llmlingua2` 默认已加入预加载列表）：

```sql
-- 将模型加入预加载列表（持久化保存在 $PGDATA/pg_tokenizer/preload_models）
SELECT add_preload_model('my_model');

-- 查看当前已配置的预加载模型列表（默认为 {llmlingua2}）
SELECT list_preload_models();

-- 从预加载列表中移除模型（例如不使用 llmlingua2 时可释放约 200 MB 内存）
SELECT remove_preload_model('llmlingua2');
```

调用 `add_preload_model(...)` 后（请确保已在 `postgresql.conf` 中设置 `shared_preload_libraries = 'pg_tokenizer.so'`），重启 PostgreSQL 即可使预加载对所有后端连接生效。

## 1.0.0 自定义模型行为 {#custom-model-100}

词表触发器先计算缺失词元，仅需要新增词元的行获取按模型划分的事务级咨询锁，然后重新检查并排序写入；仅包含已提交词元的行不获取这把锁。新增词元的写入在整个事务内串行执行，覆盖多行批次与多条语句，避免相反词元顺序导致的唯一索引死锁。普通分词读取及不同模型的写入仍可并发。请缩短事务；写入多个模型或锁定业务行时，仍需保持一致顺序并处理普通死锁、序列化失败重试。

生成 embedding 的触发器会在词表触发器完成后刷新 SPI 快照，因此在 `READ COMMITTED` 下可以读取等待期间由其他事务提交的词元 ID。在 `REPEATABLE READ` 或 `SERIALIZABLE` 下，冲突的写事务可能收到 SQLSTATE `40001`，需要重试整个事务。升级保留已有词表 ID；新模型的 ID 属于内部映射，不保证与独立创建的其他模型相同。

### 按条件选择语料 {#corpus-filter}

```sql
SELECT create_custom_model('tenant_a', $$
table = 'public.documents'
column = 'passage'
text_analyzer = 'text_analyzer1'
filter = "tenant_id = 42 AND published IS TRUE"
$$);

-- 或通过便捷函数同时创建模型、分词器和 embedding 触发器。
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'tenant_b_tok', model_name => 'tenant_b',
    text_analyzer_name => 'text_analyzer1', table_name => 'public.documents',
    source_column => 'passage', target_column => 'embedding',
    filter => 'tenant_id = 43 AND published IS TRUE'
);
```

`filter` 是使用源表列名的 SQL 布尔表达式，不带 `WHERE` 或 `NEW.`，按调用者权限求值。仅 TRUE 匹配，FALSE 和 NULL 均跳过；空表达式或非法表达式即使面对空表也会报错。条件应由普通源列确定，不应依赖 embedding 目标列；不支持 `ctid` 等系统列及非确定性条件。应传入可信表达式，必要时为函数加上模式限定。该功能用于选择语料，不能替代行级安全策略。

过滤条件同时作用于初始词表扫描、embedding 回填和后续插入/更新。配置过滤条件后，触发器监听所有 UPDATE，因此只修改租户字段也会重新判断。匹配行的源文本变为 NULL 时，embedding 同步设为 NULL。

不匹配行保持原值，包括已有 embedding；行退出语料范围后，不会删除其原 embedding 或词表条目。查询时应使用相同过滤条件，或由应用清空排除行的 embedding。词表只增不减，UPDATE/DELETE 不会裁剪词表。省略 `filter` 或向便捷函数传入 SQL NULL，仍处理整张表。原六参调用与旧模型配置兼容，并支持带模式的表名及含特殊字符的列名。

带模式的表名优先按限定名解析；如需选择名称本身含点号的表，请使用 SQL 双引号，例如 `'"corpus.docs"'`。

### 目录缓存失效

为提高分词速度，每个 PostgreSQL 后端都会缓存分析器、分词器、模型、停用词典和同义词典定义。创建、删除或重建这些对象时会立即清理当前后端，并在事务提交时发布跨后端失效通知，回滚仅清理本地缓存；其他后端在下次查找前会丢弃旧定义，回滚也不会在当前后端留下不存在的对象。依赖被重建的分析器或模型的分词器会一并失效。

缓存失效不会自动改写已经存储在 `INT[]`、`bm25vector` 或 `tsvector` 列中的值。如果有意使用同名定义替换分析器或模型，应重新计算持久化的搜索列，并在词素或词元 ID 表示发生变化时重建索引。


缓存失效会保留继承的预加载对象。非内置模型只有在当前数据库中名称与存储配置完全一致时才能复用预加载，不能代替缺失或不同的本库定义。预加载列表由管理员管理，失败条目记录 WARNING 后跳过；文件修改不随 SQL 事务回滚。

自 1.0.0 起，Lindera 用户词典 ID 从 `1073741824` 起编号，不再与系统词典 ID 重叠。使用用户词典时需重新生成已存储的 ID 并重建索引。原生 RPM/DEB 需外部词典，GitHub Release 包内嵌 IPADIC。

查询遵循 SQL 快照。观察到失效通知后，在旧快照下加载的对象会在后续语句和事务边界清理；并行 worker 沿用 leader 的快照。修改定义的事务不能执行 `PREPARE TRANSACTION`。匹配行的 NULL 源列会将显式提供的 embedding 也设为 NULL；不匹配行仍保留原值。
