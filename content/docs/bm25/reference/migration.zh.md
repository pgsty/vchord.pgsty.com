---
title: "迁移到 1.0.0"
description: "vchord_bm25 1.0.0 的原生 tsvector API、安装模式、访问权限与迁移边界。"
weight: 35
icon: fa-solid fa-right-left
---

`pgsty/vchord_bm25` **1.0.0** 是 PGSTY 的首个正式版本，使用 PostgreSQL 原生 `tsvector` 和新的索引存储引擎。历史 0.3.x 软件包与套件镜像使用 `bm25vector`，两者的 API 与索引格式均不兼容。

| 接口 | 0.3.x | 1.0.0 |
| --- | --- | --- |
| 文档值 | `bm25vector`，保存整数词元 ID 与词频 | 带位置的 `tsvector` |
| 查询构造函数 | `to_bm25query(index, vector)` | `to_bm25query(vector, index)` |
| 查询字段 | `(index_oid regclass, query_vector bm25vector)` | `(vector tsvector, index regclass)` |
| 得分类型 | `real` | `double precision` |
| 模式 | 固定为 `bm25_catalog` | 安装时选择的扩展模式，可迁移 |
| 候选数上限 | `bm25_catalog.bm25_limit`，默认 100 | `bm25.limit` 或索引 `limit`，首批默认 100，按需续扫 |
| 文本分析 | `pg_tokenizer` 整数数组 | `to_tsvector`，或 pg_tokenizer 1.0.0 的 `tokenize_to_tsvector` / `analyze_to_tsvector` |
{.wide .expand}

1.0.0 使用从 Rust 动态库生成的 `vchord_bm25--1.0.0.sql`。打包时会比对检入的 SQL 与编译后的接口，遇到不一致即报错。Git 中保留的旧版安装 SQL 对应旧版动态库；把控制文件版本改成 0.3.0 并不能让新引擎兼容旧接口。

## 安装与查询 {#install-and-query}

使用 `PG_CONFIG=/path/to/pg_config make build` 与 `PG_CONFIG=/path/to/pg_config make install` 编译安装 1.0.0 源码。将 `vchord_bm25` 加入 `shared_preload_libraries` 并重启 PostgreSQL。标准文本检索无需外部分词器：

```sql
CREATE EXTENSION vchord_bm25;
CREATE TABLE documents (
    id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    passage text NOT NULL,
    vector tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
);
INSERT INTO documents (passage) VALUES
    ('PostgreSQL supports full text search.'),
    ('BM25 ranks documents by relevance.');
CREATE INDEX documents_bm25 ON documents USING bm25 (vector bm25_ops)
WITH (limit = 100);

SELECT id, vector <&> to_bm25query(to_tsvector('english', 'PostgreSQL'), 'documents_bm25') AS rank
FROM documents ORDER BY rank LIMIT 10;
```

索引通过文档位置计算词频，`strip(tsvector)` 与 `array_to_tsvector` 无法提供这些信息。文档与查询应使用相同的分析器。整数词元 ID 不等于词素，因此没有自动的 `bm25vector` 到 `tsvector` 转换。

显式执行 `SET "bm25.limit" = 100` 会覆盖索引上的首批候选数；GUC 恢复为内置默认来源时才回退到索引参数。两层默认均为 100，显式零值也使用 100。扫描会为 SQL `LIMIT`、`OFFSET` 和后置过滤自动续扫，不会因批量大小而静默截断结果。普通排序包含零分的未命中文档及 NULL；只需匹配文档时请明确添加匹配条件。`bm25.prefilter` 同样遵循设置来源优先级，显式 false 会覆盖索引参数；volatile 条件仍由执行器执行。

`postgresql.conf`、`ALTER DATABASE`、`ALTER ROLE` 或客户端启动选项中的设置也会覆盖索引参数。`RESET` 会恢复这些配置默认值；只有 GUC 来源恢复为内置默认值时，才会回退到索引参数。

## 模式访问权限 {#schema-access}

DBA 可以把扩展安装到为应用选择的模式中：

```sql
CREATE SCHEMA search;
CREATE EXTENSION vchord_bm25 WITH SCHEMA search;
GRANT USAGE ON SCHEMA search TO app_user;
ALTER ROLE app_user SET search_path = public, search;
```

这是安装到 `public` 的替代方案，不要在同一数据库执行两次安装。表的访问权限需要单独授予。PostgreSQL 默认向 `PUBLIC` 授予函数执行权限；若部署环境撤销了该默认授权，还需显式授予所需函数的权限。即使 `search` 不在 `search_path` 中，仍可通过 `search.to_bm25query(...)` 调用构造函数，迁移扩展模式后也如此。

标量评分和原生索引扫描都要求当前角色拥有被索引表的 `SELECT` 权限。对于普通的、非部分索引的单列索引，仅有被索引列的 `SELECT` 权限也可以；表达式索引和部分索引要求表级权限。即使 SQL 没有 `FROM` 子句、只对调用者提供的向量评分，也会执行权限检查。仅有视图的访问权限不代表有权读取底层语料统计。

评分使用整个索引的语料统计。当行级安全策略（RLS）适用于当前角色时，1.0.0 会拒绝标量评分和原生索引扫描，避免泄露隐藏行的统计信息。表所有者和 `BYPASSRLS` 角色的豁免遵循 PostgreSQL 规则；启用 `FORCE ROW LEVEL SECURITY` 后，普通表所有者也受此限制。设置 `row_security = off` 不能绕过检查。

## 迁移已有数据 {#move-existing-data}

从 0.3.0 执行 `ALTER EXTENSION vchord_bm25 UPDATE TO '1.0.0'` 会在修改对象前主动报错。该脚本不会重写旧索引，也不会删除依赖扩展的应用数据。

1. 保留旧数据库与旧动态库。盘点 `bm25vector` 列、索引、视图、函数和分词触发器；在旧类型仍可读取时导出原始文本与应用数据。
2. 在具有独立扩展库目录的另一套 PostgreSQL 安装或独立容器镜像中安装 1.0.0，并创建新数据库。仅换用数据目录或端口、仍共用扩展库目录，并不足以隔离新旧版本。同一套 PostgreSQL 下的数据库共享扩展动态库，不能在仍有数据库使用 0.3.x 时直接替换文件。
3. 恢复原始文本，生成 `tsvector`，重建所有 BM25 索引。复制旧索引文件或对 `bm25vector` 列执行普通 `REINDEX` 均不能完成 API 迁移。
4. 更新构造函数参数顺序、数据类型、GUC 名称与分词触发器。比较排序质量与查询结果后再切换应用。

站点继续保留 0.3.x 的 `pg_tokenizer` 整数数组工作流。对于 1.0.0，可以使用 `to_tsvector`，或 [pg_tokenizer](/zh/docs/tokenizer/) 1.0.0：`tokenizer_catalog.tokenize_to_tsvector(text, tokenizer)` 沿用同一模型，以词元 ID 作为词位；`tokenizer_catalog.analyze_to_tsvector(text, analyzer)` 使用文本分析器（例如 Jieba）的分词结果。两者均为 `STABLE`：请把结果存入 `tsvector` 列并为该列建索引，查询时使用同一个函数。词频改为来自 tsvector 中的位置，切换前请对比排序结果。

统计语义、维护门槛、手动 `bm25_maintain()`、备库重试行为，见[索引与维护](/zh/docs/bm25/usage/indexing/#growing-segments-and-maintenance-in-100)。统计包含合并前的 tombstone；活跃扫描保留其 preparation，但被淘汰的纯标量缓存条目可能在同一次执行中重新收集，`work_mem` 是软限制；标量评分为 parallel restricted。文档权重会被忽略；长文档受 [PostgreSQL tsvector 上限](https://www.postgresql.org/docs/18/textsearch-limitations.html)约束，词频受限时建议按段落切分。
