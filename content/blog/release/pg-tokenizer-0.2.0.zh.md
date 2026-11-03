---
title: "pg_tokenizer 0.2.0：原生全文检索与自定义模型可靠性改进"
date: 2026-11-03
description: "pg_tokenizer 0.2.0 新增原生 tsvector 输出、语料过滤与事务缓存失效，修复并发词表写入和数据库拥有者权限问题。"
author: "[冯若航](https://github.com/Vonng) · [PGSTY](https://pgsty.com)"
tags:
  - "release"
  - "pg_tokenizer"
  - "full-text-search"
upstream_source: ""
upstream_link: ""
---

**pg_tokenizer 0.2.0** 将多语言文本分析器与词表模型接入 PostgreSQL 原生全文检索，同时修复自定义模型并发写入、数据库拥有者权限，以及跨会话定义缓存过期的问题。本版本由 PGSTY 在 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 维护，采用 Apache-2.0 许可证。

原有的 `tokenize(text, tokenizer_name)` 接口仍返回 `INT[]`。使用历史 `vchord_bm25 0.3.x` 的 `bm25vector` 工作流可以继续使用该接口；使用 GIN/GiST 或 `vchord_bm25 0.4.0/main` 接口时，可以改用新增的 `tsvector` 函数。`pg_tokenizer` 本身不依赖 BM25 或向量检索扩展。

## 0.2.0 修改概览 {#changes}

| 领域 | 修改 |
| :--- | :--- |
| 原生全文检索 | 新增 `analyze_to_tsvector` 与 `tokenize_to_tsvector`，输出带位置的原生词素；删除空输出词元后再连续编号。 |
| 自定义词表 | 支持可选语料过滤，覆盖训练、存量回填与后续写入；支持带模式的表名及带引号的标识符。 |
| 并发写入 | 同一词表的写入在事务内串行化；`READ COMMITTED` 下等待结束后的 embedding 更新能看到新提交的词元 ID。 |
| 权限 | 向 `pg_database_owner` 授予目录权限，非超级用户数据库拥有者可在扩展安装后管理自己的分词对象。 |
| 定义缓存 | 创建、删除对象后跨后端失效，并清理依赖缓存；事务及子事务回滚自动清理缓存。 |
| 依赖与升级 | 升级至 pgrx 0.19.3、Lindera 6.2.0、Jieba 0.11.0、Hugging Face tokenizers 0.23.2；提供从 0.1.0、0.1.1 和 0.1.2 开发快照的迁移路径。 |

## 原生 `tsvector` 输出 {#native-tsvector}

两个新函数分别处理不同的词素表示：

- `analyze_to_tsvector(text, text_analyzer_name)` 直接使用分析器输出的字符串词元作为词素。适用于 Jieba，以及自定义规范化、词干、停用词和同义词流水线，无需词表模型。
- `tokenize_to_tsvector(text, tokenizer_name)` 将模型词元 ID 转为十进制词素。适用于内置、自定义、导入的 Hugging Face 和 Lindera 模型，不会解码 ID，也不会再次执行 PostgreSQL 文本归一化。

安装并预加载 0.2.0 动态库后，可以将分析结果存入列，再使用原生短语查询检索：

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

两个函数均为 `STRICT`、`STABLE`。应先将结果存入普通列并维护其更新，再为该列建立索引；不能直接用作要求不可变表达式的生成列或表达式索引。示例显式填充了 `terms`，后续修改源文本时，应用也需要同步更新该列。

位置从 1 开始，按**最终非空输出序列**连续编号，默认权重为 D。位置不是源文本偏移：过滤器可能删除或展开词元，模型可能输出子词。词素中的引号、反斜杠、空白和标点会被保留。PostgreSQL 原生限制仍然适用，包括每个词素最多保存 256 个位置，以及最大位置 16,383。

文档和查询必须使用相同的词素表示。普通 `plainto_tsquery('english', ...)` 无法复现自定义分析器输出或模型 ID。本版本没有新增 `tsquery` 构造器，具体用法见[原生全文检索指南](/zh/docs/tokenizer/overview/#native-fts)。

## 自定义语料过滤与并发写入 {#custom-models}

`create_custom_model` 的 TOML 配置新增可选的 `filter`；便捷函数新增七参重载，最后一个参数为 `filter TEXT`，原六参签名及依赖它的调用者继续保留。省略过滤条件，或向便捷函数传入 SQL `NULL`，仍然处理整张表。

使用前面创建的分析器：

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

只有谓词结果为 `TRUE` 的行参与词表训练与 embedding 更新。该规则覆盖初始扫描、存量回填和后续插入或更新，也包括只修改过滤条件列的更新。便捷函数填充 `INT[]` 或兼容的历史 `bm25vector` 列，不会自动维护原生 `tsvector` 列。

过滤条件是基于普通源列的可信 SQL 表达式，不包含 `WHERE` 或 `NEW.`；应使用不依赖目标列的确定性谓词。表达式以调用者权限执行，不能代替行级安全策略。不匹配行保留已有 embedding，词表在更新、删除后仍然只增不减。查询时应使用相同谓词，或由应用清空被排除行的 embedding。即使源表为空，空白或无效谓词也会被拒绝。

词表写入现在会去重、排序新词元，并按模型获取事务级咨询锁，修复并发批次以相反词元顺序插入时产生的死锁。在 `READ COMMITTED` 下，embedding 触发器会在等待后刷新快照，从而包含前一个写入事务新提交的词元 ID。在 `REPEATABLE READ` 或 `SERIALIZABLE` 下，冲突可能返回 SQLSTATE `40001`，应用需要重试整个事务。写入多个模型或锁定业务行时，仍应保持一致顺序并缩短事务。

表名按 SQL 标识符解析，支持模式限定和带引号的名称。带模式的限定名优先于名称本身含点号的表，具体规则见[自定义模型文档](/zh/docs/tokenizer/models/#custom-model-020)。

## 定义缓存与数据库拥有者权限 {#caches-and-permissions}

成功执行 `create_*` 或 `drop_*` 后，当前后端的定义缓存会立即清理。事务结束时发布跨后端失效通知，其他后端在下次查找前丢弃旧缓存。重建分析器或模型，也会使持有旧引用的分词器缓存失效。事务回滚及子事务回滚会清理已撤销操作留下的缓存对象，无需再手动删除“幽灵对象”或通过重连恢复。

缓存失效不会自动重写已持久化的 `INT[]`、`bm25vector` 或 `tsvector`。主动替换定义时，应重算受影响的搜索列，并按使用方要求重建索引。请通过扩展 API 管理定义；直接修改目录表不在这些失效钩子的覆盖范围内。

安装与升级会向 `pg_database_owner` 授予 `tokenizer_catalog` 及其函数、表、序列的访问权限。管理员安装扩展后，非超级用户数据库拥有者即可管理自己的分析器、分词器、词典和自定义模型；权限随数据库拥有者变更而生效。其他应用角色仍需显式授权，这些授权也不会转移已有模型表的所有权，详见[数据库拥有者权限](/zh/docs/tokenizer/installation/#database-owner-permissions)。

## 升级到 0.2.0 {#upgrade}

安装匹配的 0.2.0 动态库与 SQL 文件，在 `shared_preload_libraries` 中保留 `pg_tokenizer` 及其他所需库，然后重启 PostgreSQL。由扩展拥有者或管理员在每个已安装该扩展的数据库中执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '0.2.0';
SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
-- 0.2.0
```

升级脚本支持从 0.1.0、0.1.1 及 0.1.2 开发快照迁移，保留目录数据、已有自定义词表 ID，以及原六参便捷函数的依赖关系。0.1.2 SQL 文件继续作为迁移链中的中间步骤，正式版本号为 **0.2.0**。

复用已有搜索数据时，需要特别处理两项变化：

- **Lindera 词典 ID：**依赖从 Lindera 0.42 升级到 6.2，内嵌 IPADIC 从 2007-08-01 版变为 2025-09-20 版。将旧数据与新查询词元配合使用前，必须重新生成已存储的 Lindera 词元数组及基于 ID 的向量，并重建使用它们的索引。旧词典配置表仍可使用，但外部编译词典必须使用 Lindera 6 重建；内嵌词典仍是可选编译特性。详见 [Lindera 升级说明](/zh/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model)。
- **空词元的位置：**如果 0.1.2 开发快照中的流水线曾输出空词元，已存储的向量可能带有位置间隙。依赖短语位置时应重新计算这些值；0.2.0 会对剩余输出连续编号。

## 兼容性、软件包与验收 {#compatibility}

检查与发布工作流面向 Linux **x86_64/aarch64** 上的 PostgreSQL **14–18**。源码构建需要匹配的 `cargo-pgrx 0.19.3`。虽然 Cargo 中已有 `pg19` 特性，PostgreSQL 19 尚未纳入本版本配置的测试与打包矩阵。

原生 RPM/DEB 配方使用 **`0.2.0-1PGSTY`** 版本。本地包验收覆盖了 PostgreSQL 18 的 EL9/aarch64 与 Ubuntu 24.04/arm64，包含调试包。完整 16 平台构建及入库发布是独立于源码 tag 的后续工作；升级前请确认实际包可用性，并匹配发行版、PostgreSQL 主版本和 CPU 架构。

现有手动 GitHub 工作流生成 Ubuntu 24.04 上修订号为 `-1` 的 `.deb` 及 Linux ZIP 归档，与原生 `1PGSTY` 包分别构建。ZIP 不包含软件包管理器依赖元数据，安装前需确认目标系统 libc 兼容性。该发布工作流尚未生成或上传 SBOM 制品。

本地验收已通过 Rust 格式检查、Clippy、单元测试、release 构建与 SQL 生成，以及 **16 组 SQLLogicTest** 和 **11 项集成测试**，覆盖并发、缓存失效、权限与升级场景。配套的中英文分词器文档已同步到 0.2.0。

配置与运维细节可查阅[安装与升级指南](/zh/docs/tokenizer/installation/)、[SQL 参考](/zh/docs/tokenizer/reference/)和[模型文档](/zh/docs/tokenizer/models/)。
