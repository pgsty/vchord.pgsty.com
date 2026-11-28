---
title: "升级与迁移"
linkTitle: "升级与迁移"
description: "vchord_bm25 的版本历史、1.x 内的原地升级与降级，以及从 0.x bm25vector 接口迁移。"
weight: 30
icon: fa-solid fa-right-left
aliases:
  - "/docs/bm25/reference/versions/"
---

任何 1.x 版本都可以原地升级到 1.3.0，索引保持不变。0.x 版本用的是 `bm25vector` 类型而不是 `tsvector`，无法升级：需要在新的安装中根据原始文本重建索引，见[从 0.x 迁移](#from-0x)。

## 版本历史 {#releases}

| 版本 | 日期 | 概要 | 说明 |
| --- | --- | --- | --- |
| 1.3.0 | 2026-11-24 | 新增可选的 `shared_corpus_stats`，用于启用了行级安全的表；预过滤支持相关子查询；对选择性高的 top-k 查询，规划器更常选用 bm25 索引；建索引和合并时写的 WAL 更少。 | [发布文章](/zh/release/vchord-bm25-1.3.0/) |
| 1.2.0 | 2026-11-23 | 支持 PostgreSQL 15–19，不再支持 PostgreSQL 14；修复规划与维护问题。 | [发布文章](/zh/release/vchord-bm25-1.2.0/) |
| 1.1.0 | 2026-11-08 | 修复可能漏掉分数极接近的文档的剪枝问题；打分与预过滤更快。支持 PostgreSQL 14–18。 | [发布文章](/zh/release/vchord-bm25-1.1.0/) |
| 1.0.0 | 2026-11-04 | PGSTY 的首个版本：以原生 `tsvector` 索引取代 `bm25vector`，扫描可越过 `bm25.limit` 继续，`VACUUM` 可并发合并，增加权限与行级安全检查。支持 PostgreSQL 14–18。 | [发布文章](/zh/release/vchord-bm25-1.0.0/) |
| 0.1.0–0.3.0 | 2025-02-06 至 2025-12-15 | 上游版本，使用 `bm25_catalog` 模式下的 `bm25vector` 接口。 | [上游 Releases](https://github.com/supervc-stack/VectorChord-bm25/releases) |

## 1.x 内升级 {#upgrade}

1.0.0、1.1.0 和 1.2.0 建的索引可以直接用于 1.3.0，无需 `REINDEX`。

1. 检查服务器版本。1.3.0 支持 PostgreSQL 15–19；PostgreSQL 14 需要先升级服务器。
1. 在每个节点（主库和备库）上安装 1.3.0 的文件，安装方式与之前相同（见[安装](/zh/docs/bm25/getting-started/installation/)）。
1. 逐个重启各节点上的 PostgreSQL，让它预加载新的动态库。
1. 在主库上，对每个装有该扩展的数据库执行：

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

### 降级 {#downgrade}

没有退回旧版本的 SQL 脚本，但 1.3.0 没有改动扩展的 SQL 对象，所以可以用比 1.3.0 更早的 1.x 动态库来运行。在此之前，要把所有设置过 `shared_corpus_stats` 的索引（即使设置的是 `off`）重置掉，因为旧版本的动态库不认识这个选项。用下面的查询找出这些索引：

```sql
SELECT c.oid::regclass AS index
FROM pg_class AS c
JOIN pg_am AS am ON am.oid = c.relam
WHERE am.amname = 'bm25'
  AND EXISTS (SELECT FROM unnest(c.reloptions) AS o WHERE o LIKE 'shared_corpus_stats=%');
```

对每个索引执行 `ALTER INDEX <index> RESET (shared_corpus_stats);`，然后安装旧版本的动态库并重启。

## 从 0.x 迁移 {#from-0x}

0.x 版本把文档存在 `bm25vector` 列中，由 pg_tokenizer 的 `tokenize()` 填充，并固定使用 `bm25_catalog` 模式。它的索引格式和 SQL 接口都与 1.x 不同，因此在 0.3.0 上执行 `ALTER EXTENSION vchord_bm25 UPDATE` 会在改动任何东西之前停下，并报错 `vchord_bm25 0.3.0 cannot be upgraded in place to 1.0.0`。

`bm25vector` 列是从文本派生出来的，所以迁移就是从同样的文本生成 `tsvector`，再建新的索引：

1. **在 0.x 仍然安装着的时候导出。** 导出带文本列的表，但不要带上 `bm25vector` 列，它们无法恢复到 1.x 中，例如 `COPY (SELECT id, passage FROM documents) TO ...`。同时保存分词器（`tokenizer_catalog.tokenizer`）以及用到 `bm25vector` 的视图、函数和触发器的定义。
1. **在另一套 PostgreSQL 安装中装 1.3.0**，例如另一台主机或另一个容器。一套安装只能加载一个 vchord_bm25 动态库，而 1.x 的动态库无法服务 0.x 的数据库。
1. **导入数据并生成 `tsvector`。** 想沿用之前的分词结果，就重建同一个 pg_tokenizer 分词器，并使用 `tokenizer_catalog.tokenize_to_tsvector(text, 'tokenizer')`，它会把 `tokenize()` 返回的 token ID 作为词位输出。也可以改用 `to_tsvector` 或 pg_tokenizer 的文本分析器，见[建索引](/zh/docs/bm25/usage/indexing/#tsvector)。
1. **按下表建索引，并改写查询和参数。**
1. **把应用切换到新的安装**，然后下线旧的安装。
{.steps}

| | 0.x | 1.x |
| --- | --- | --- |
| 文档列 | `bm25vector`，由 `tokenize(text, tokenizer)` 生成 | 带位置的 `tsvector` |
| 模式 | 固定为 `bm25_catalog` | 任意模式，可迁移 |
| 查询构造 | `to_bm25query('index', query_bm25vector)` | `to_bm25query(query_tsvector, 'index')`，参数顺序对调 |
| 分数类型 | `real` | `double precision` |
| `bm25_catalog.bm25_limit`（默认 `100`，`-1` 表示全部扫描） | 一次检索最多返回的行数；带过滤的查询可能返回不足 | `bm25.limit`：只是第一批的大小，结果总是完整的 |
| `bm25_catalog.enable_index`（默认 `on`） | 规划器开关 | `bm25.enable_scan` |
| `bm25_catalog.enable_prefilter`（默认 `on`） | 预过滤 | `bm25.prefilter`，默认 `off` |
| `bm25_catalog.segment_growing_max_page_size`（默认 `4096` 页） | 增长段达到该大小时封存 | 由 `VACUUM` 合并；索引选项 `maintenance_min_rows` 与 `maintenance_scale_factor` |
| `bm25_page_inspect(regclass, int)` | 调试用的页面转储 | 无 |
{.wide}

下面是一个 0.x 用法和它在 1.x 中的等价写法，使用同一个 BERT 分词器：

```sql
-- 0.x
SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;
SELECT create_tokenizer('bert', $$ model = "bert_base_uncased" $$);
ALTER TABLE documents ADD COLUMN embedding bm25vector;
UPDATE documents SET embedding = tokenize(passage, 'bert');
CREATE INDEX documents_embedding_bm25 ON documents USING bm25 (embedding bm25_ops);

SELECT id FROM documents
ORDER BY embedding <&> to_bm25query('documents_embedding_bm25', tokenize('PostgreSQL', 'bert'))
LIMIT 10;
```

```sql
-- 1.x
SELECT tokenizer_catalog.create_tokenizer('bert', $$ model = "bert_base_uncased" $$);
ALTER TABLE documents ADD COLUMN terms tsvector;
UPDATE documents SET terms = tokenizer_catalog.tokenize_to_tsvector(passage, 'bert');
CREATE INDEX documents_terms_bm25 ON documents USING bm25 (terms bm25_ops);

SELECT id FROM documents
ORDER BY terms <&> to_bm25query(tokenizer_catalog.tokenize_to_tsvector('PostgreSQL', 'bert'), 'documents_terms_bm25')
LIMIT 10;
```

新插入的行要用触发器保持 `terms` 同步，写法见[建索引](/zh/docs/bm25/usage/indexing/#tsvector)。
