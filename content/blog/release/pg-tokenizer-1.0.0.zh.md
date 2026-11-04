---
title: "pg_tokenizer 1.0.0：PGSTY 接手后的首个发布"
date: 2026-11-03
description: "pg_tokenizer 1.0.0 是 PGSTY 维护的首个版本，新增原生 tsvector 输出、语料过滤、安全的并发词表写入、数据库拥有者权限与事务感知的定义缓存。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
images:
  - "/blog/covers/pg-tokenizer-1.0.0.png"
tags:
  - "release"
  - "pg_tokenizer"
  - "full-text-search"
upstream_source: ""
upstream_link: ""
---

**pg_tokenizer 1.0.0** 是 PGSTY 在 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 维护的首个版本，继续采用 Apache-2.0 许可证。它将多语言文本分析器与词表模型接入 PostgreSQL 原生全文检索，让基于语料训练的自定义模型在并发写入下保持正确，并允许非超级用户的数据库拥有者管理自己的分词定义。

现有 `tokenize(text, tokenizer_name)` 接口仍返回 `INT[]`。使用历史 `vchord_bm25` 0.3.x `bm25vector` 工作流的应用可以保留原接口；使用 GIN/GiST 或 [`vchord_bm25` 1.0.0](/zh/blog/release/vchord-bm25-1.0.0/) 接口的应用可以使用新的 `tsvector` 函数。`pg_tokenizer` 不依赖 BM25 或向量检索扩展。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release**：[`pgsty/pg_tokenizer 1.0.0`](https://github.com/pgsty/pg_tokenizer/releases/tag/1.0.0) · [源码仓库](https://github.com/pgsty/pg_tokenizer)
> - **扩展目录主页**：[pgext.cloud (`pg_tokenizer`)](https://pgext.cloud/e/pg_tokenizer) · [Pigsty 扩展页面 (`pigsty.cc`)](https://pigsty.cc/ext/e/pg_tokenizer/)
> - **二进制软件包**：[RPM / DEB 软件源配置](/zh/download/) · [SBOM 与许可证清单](/zh/docs/about/sbom/)

## 1.0.0 修改概览 {#changes}

| 方面 | 修改 |
| :--- | :--- |
| 原生全文检索 | `analyze_to_tsvector` 与 `tokenize_to_tsvector` 生成带连续位置的原生词素；与 `to_tsvector` 一样，空词元和超过 2046 字节的词元会被跳过。 |
| 自定义词表 | 可选语料过滤条件同时作用于训练、回填和后续写入；支持带模式名的表名和带引号的标识符。 |
| 并发写入 | 只有向词表新增词元的写入才获取按模型划分的锁；`READ COMMITTED` 下 embedding 更新能读到刚提交的词元 ID。 |
| 权限 | `pg_database_owner` 获得目录权限；词表触发器以精确参数类型调用扩展函数；集群级预加载列表仍仅限管理员。 |
| 定义缓存 | 创建或删除定义后，提交时跨后端失效依赖对象，回滚只做本地清理；旧快照下加载的定义不会带入后续语句。 |
| 文本分析 | `ngram` 按 Unicode 字符计数，中日韩文本与 emoji 不再报错；短于 `min_gram` 的词元（含空输入）不产生 N-gram，不再报错或陷入死循环。`pg_dict` 按 `ts_lexize` 的方式调用词典，`Thesaurus` 分类词典的单词条目可以生效。 |
| 预加载与备份 | 预加载模型在缓存失效后继续保留，无效预加载条目不再阻止启动，`pg_dump` 会导出定义表。 |
| 依赖与升级 | 基于 pgrx 0.19.3 支持 PostgreSQL 14–18，升级至 Lindera 6.2.0、Jieba 0.11.0、Hugging Face tokenizers 0.23.2，Snowball 词干提取改用 [`pgsty/rust-stemmers`](https://github.com/pgsty/rust-stemmers) 1.2.1（词干结果不变）；提供从 0.1.0 和 0.1.1 的迁移路径。 |
{.wide .expand}

## 原生 `tsvector` 输出 {#native-tsvector}

两个新函数分别对应不同的词素表示：

- `analyze_to_tsvector(text, text_analyzer_name)` 直接使用分析器输出的字符串词元作为词素，适合 Jieba 以及自定义归一化、词干、停用词和同义词流水线，无需词表模型。
- `tokenize_to_tsvector(text, tokenizer_name)` 将模型词元 ID 转为十进制词素，支持内置、自定义、导入的 Hugging Face 与 Lindera 模型，不解码 ID，也不再经过 PostgreSQL 文本归一化。

安装并预加载 1.0.0 动态库后，可以将分析结果存入列，再使用原生短语查询检索：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
SET search_path = public, tokenizer_catalog;

SELECT create_text_analyzer('release_words', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = ["skip_non_alphanumeric"]
$$);

SELECT analyze_to_tsvector('Cat dog cat', 'release_words');
-- 'cat':1,3 'dog':2

CREATE TABLE release_documents (id integer PRIMARY KEY, body text, terms tsvector);
INSERT INTO release_documents VALUES
    (1, 'Cat dog cat', analyze_to_tsvector('Cat dog cat', 'release_words'));
CREATE INDEX ON release_documents USING gin (terms);
SELECT id FROM release_documents WHERE terms @@ 'cat <-> dog'::tsquery;
-- 1

SELECT create_tokenizer('release_bert', 'model = "bert_base_uncased"');
SELECT tokenize_to_tsvector('hello hello', 'release_bert');
-- '7592':1,2
```

两个函数均为 `STRICT`、`STABLE` 且可并行执行。应将结果存入列并维护，再为该列建立索引；它们不能直接用于生成列或表达式索引。示例显式填充了 `terms`，源文本变化时应用也需要同步更新。

位置从**最终输出序列**的 1 开始编号，默认权重为 D。位置不是源文本偏移：过滤器可能删除或扩展词元，模型也可能输出子词。词素中的引号、反斜杠、空白和标点会被保留。PostgreSQL 原生限制依然适用，包括每个词素最多 256 个位置、位置上限为 16,383。

文档和查询必须使用相同的词素表示。普通 `plainto_tsquery('english', ...)` 无法复现自定义分析器输出或模型 ID。本版本没有新增 `tsquery` 构造器，具体用法见[原生全文检索指南](/zh/docs/tokenizer/overview/#native-fts)。

## 自定义语料过滤与并发写入 {#custom-models}

`create_custom_model` 的 TOML 配置新增可选的 `filter`。便捷函数新增以 `filter TEXT` 为第七个参数的重载，原六参签名及依赖它的调用保持不变。省略过滤条件，或向便捷函数传入 SQL `NULL`，仍处理整张表。

沿用上文创建的分析器：

```sql
CREATE TABLE release_corpus (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text,
    published boolean DEFAULT false,
    token_ids int[]
);

SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'release_corpus_tok',
    model_name => 'release_corpus_model',
    text_analyzer_name => 'release_words',
    table_name => 'public.release_corpus',
    source_column => 'body',
    target_column => 'token_ids',
    filter => 'published IS TRUE'
);

INSERT INTO release_corpus (body, published) VALUES
    ('PostgreSQL full text search', true),
    ('Unpublished draft', false);
```

只有过滤条件为 `TRUE` 的行参与词表构建并更新 embedding，包括初始扫描、回填以及后续插入和更新；只修改过滤条件相关列的更新也会重新判断。便捷函数维护 `INT[]` 或兼容的历史 `bm25vector` 列，不会自动维护原生 `tsvector` 列。

过滤条件是基于普通源列的可信 SQL 表达式，不带 `WHERE` 或 `NEW.`；应使用不依赖目标列的确定性条件。它以调用者权限执行，不能替代行级安全策略。不匹配行保留已有 embedding，更新或删除后词表也只增不减。查询时请使用相同条件，或由应用清空被排除行的 embedding。空表达式与非法表达式即使面对空表也会被拒绝。

词表触发器先找出词表中尚不存在的词元。只有需要新增词元的行才获取按模型划分的事务级咨询锁，重新检查后按去重、排序的顺序写入；所含词元均已存在的行不会等待。这样可以避免并发批次以相反顺序插入词元造成的死锁。`READ COMMITTED` 下，embedding 触发器在等待后刷新快照，能够读到前一写入事务提交的词元 ID。`REPEATABLE READ` 或 `SERIALIZABLE` 下发生冲突时可能返回 SQLSTATE `40001`，需要重试整个事务。请缩短事务；写入多个模型或锁定业务行时保持一致顺序。

表名按 SQL 标识符解析，支持模式限定和带引号的名称。带模式的限定名优先于名称本身含点号的表。源表已被删除时，`drop_custom_model` 也能完成清理。具体规则见[自定义模型文档](/zh/docs/tokenizer/models/#custom-model-100)。

## 定义缓存、预加载与数据库拥有者权限 {#caches-and-permissions}

`create_*` 与 `drop_*` 成功后会清理当前后端的定义缓存。事务提交时向其他后端发布失效通知，它们会在下次查找前丢弃旧定义；回滚（包括子事务回滚）只清理当前后端。重建分析器或模型时，引用它们的分词器也会失效。查找遵循 SQL 快照：在旧快照下加载的定义会在后续语句或事务复用前被丢弃。并行查询同样可用。修改过定义的事务不能执行 `PREPARE TRANSACTION`。

缓存失效不会重写已经持久化的 `INT[]`、`bm25vector` 或 `tsvector` 值。主动替换定义后，应重新计算相关搜索列，并按下游要求重建索引。请通过扩展接口管理定义；直接修改目录表不会触发这些失效机制。

预加载模型在缓存失效后继续保留。非内置模型只有在当前数据库中名称与存储配置完全一致时才复用预加载对象。无法加载的预加载条目会记录 WARNING 并跳过，不会阻止 PostgreSQL 启动。

安装与升级会向 `pg_database_owner` 授予 `tokenizer_catalog` 及其函数、表、序列的访问权限。管理员安装扩展后，非超级用户数据库拥有者即可管理自己的分析器、分词器、词典和自定义模型，权限随数据库拥有者变更而转移。词表触发器以精确的 `pg_catalog.text` 参数类型调用扩展函数，在 `tokenizer_catalog` 中新建的重载无法截获这些调用。集群级的 `add_preload_model` 与 `remove_preload_model` 仍仅限管理员。其他应用角色仍需显式授权，授权也不会转移已有模型表的所有权。详见[数据库拥有者权限](/zh/docs/tokenizer/installation/#database-owner-permissions)。

普通 `pg_dump` 现在会导出分析器、分词器、模型、同义词以及用户停用词定义和自定义词表。外部 Lindera 词典和预加载目录仍需单独备份，见[逻辑备份](/zh/docs/tokenizer/installation/#logical-backups)。

## 从 0.1.x 升级 {#upgrade}

安装匹配的 1.0.0 动态库与 SQL 文件，在 `shared_preload_libraries` 中保留 `pg_tokenizer` 及其他所需库，然后重启 PostgreSQL。由扩展拥有者或管理员在每个安装了该扩展的数据库中执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '1.0.0';
SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
-- 1.0.0
```

升级脚本支持从 0.1.0 和 0.1.1 迁移，保留目录数据、已有自定义词表 ID，以及原六参便捷函数的依赖关系。复用已存储的搜索值之前，请注意以下变化：

- **`apply_text_analyzer` 改为 `STABLE`：**分析器定义属于目录数据。只要有索引、存储生成列、分区键或扩展统计对象依赖该函数，升级就会拒绝执行；请先将这些表达式改为维护的普通列。
- **Lindera 词典 ID：**依赖从 Lindera 0.42 升级到 6.2，内嵌 IPADIC 从 2007-08-01 版变为 2025-09-20 版；用户词典 ID 改为从 `1073741824` 起编号，不再与系统词典重叠。请重新生成已存储的 Lindera 词元数组和基于 ID 的向量，并重建相关索引。旧的词典配置表仍被接受，但外部编译词典必须用 Lindera 6 重新构建；升级前请移除仍指向旧词典的预加载条目。详见 [Lindera 迁移说明](/zh/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model)。
- **内置停用词表为保留名：**`drop_stopwords` 与 `create_stopwords` 拒绝 `lucene_english`、`nltk_english` 和 `iso_english`，因为 `pg_dump` 不导出这三个词表，恢复时会重建随扩展发布的内容。若旧版本中替换过其中之一，升级会给出 WARNING；请将该词表复制为新名称，并在分析器中引用新名称。
- **NULL 源列：**自定义模型中匹配行的源列为 NULL 时，embedding 现在设为 NULL；0.1.x 会保留目标列原值。

完整列表见[兼容性说明](/zh/docs/tokenizer/installation/#compatibility-100)。

## 兼容性与软件包 {#compatibility}

检查与发布工作流面向 Linux **x86_64/aarch64** 上的 PostgreSQL **14–18**，基于 `cargo-pgrx 0.19.3` 构建。代码中虽有 `pg19` Cargo feature，但 PostgreSQL 19 不在本版本的测试与打包矩阵内。

原生 RPM 与 DEB 软件包（`1.0.0-1PIGSTY` / `1.0.0-1PGSTY`）已覆盖全部 16 个受支持的 Linux 目标平台，可在[下载页面](/zh/download/)获取；原生配方不内嵌 Lindera 词典，使用 Lindera 模型时需提供用 Lindera 6 构建的词典。GitHub 发布工作流构建的软件包启用 `lindera-ipadic` 并声明共享库依赖，与原生 Pigsty 软件包相互独立。ZIP 压缩包不含包管理器依赖信息，请在目标主机上确认 libc 兼容性。完整依赖与许可证清单见 [SBOM 页面](/zh/docs/about/sbom/)。

配置与运维细节可查阅[安装与升级指南](/zh/docs/tokenizer/installation/)、[SQL 参考](/zh/docs/tokenizer/reference/)和[模型文档](/zh/docs/tokenizer/models/)。
