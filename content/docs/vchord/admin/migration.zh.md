---
title: "升级与迁移"
linkTitle: "升级与迁移"
description: "原地升级 vchord，不改表就把 pgvector 的 HNSW / IVFFlat 索引换成 vchord，或从 pgvecto.rs 迁移过来。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/migration.md"
aliases:
  - "/docs/admin/migration/"
  - "/vectorchord/admin/migration/"
icon: fa-solid fa-right-left
---

<a id="vectorchord-migration-overview"></a>

本页介绍三种情况：把 vchord [升级](#upgrade)到新版本，把 [pgvector 索引替换](#from-pgvector)成 vchord 索引，以及从使用自有向量类型的 [pgvecto.rs 迁移](#from-pgvectors)。

## 升级 vchord {#upgrade}

<a id="upgrading-vchord-to-130"></a>

vchord 自带从以往每个版本出发的升级脚本，1.5.0 可以直接读取已有索引。

1. 按[安装](/zh/docs/vchord/getting-started/installation/)一节，为你的 PostgreSQL 大版本装好 1.5.0 的文件。
1. 重启 PostgreSQL，加载新的动态库。
1. 在每个装有 vchord 的数据库中更新扩展：

   ```sql
   ALTER EXTENSION vchord UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

根据起点不同，还需要做下面这些事。

**从 PostgreSQL 14 出发。** vchord 1.4.0 及以后的版本不再支持 PostgreSQL 14。先停留在 vchord 1.3.0，把 PostgreSQL 升级到 15 或更高版本后，再升级 vchord。

**从 1.3.0 及更早版本出发。** 升级会经过 1.4.0，后者为[过滤键](/zh/docs/vchord/usage/filtering/#filter-keys)添加了 SQL 对象。降级软件包并不会撤销这些对象，如果可能需要回退，升级前先做好备份。

**从 1.2.x 及更早版本出发。** 1.3.0 以来有三处改动可能需要你处理：

- `build.external.table` 必须写成带模式名的表名，例如 `'public.t_build'`。已有索引仍能正常查询，但任何重建操作（`REINDEX`、`VACUUM FULL`、`CLUSTER`、`TRUNCATE`、恢复备份）都会失败，直到改好这个选项。找出受影响的索引并改写选项，TOML 中的其他内容保持不变：

  ```sql
  SELECT c.oid::regclass AS index_name, o.option_value
  FROM pg_class AS c
  JOIN pg_am AS am ON am.oid = c.relam
  CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
  WHERE am.amname = 'vchordrq'
    AND o.option_name = 'options'
    AND o.option_value LIKE '%external%';

  ALTER INDEX public.t_val_idx SET (options = $$
  [build.external]
  table = 'public.t_build'
  $$);
  ```

- `rabitq8`、`rabitq4` 的余弦距离，以及零向量和一维向量的编码都已修正。用 `REINDEX INDEX CONCURRENTLY` 重建 `rabitq8`、`rabitq4` 上的余弦索引，以及包含这类向量的索引。
- 读取[采样查询](/zh/docs/vchord/usage/measure-recall/#query-sampling)需要超级用户或 `pg_read_all_stats` 角色成员身份，因为采样里可能有其他用户的查询向量。把这个角色授予负责调召回率的人。

**召回率下降的图索引。** 1.5.0 之前的 `VACUUM` 可能把 `vchordg` 图的某个区域与其余部分断开。如果大批删除后召回率下降，用 `REINDEX INDEX CONCURRENTLY` 重建一次该索引。

## 从 pgvector 迁移 {#from-pgvector}

vchord 直接索引 pgvector 自己的 `vector` 和 `halfvec` 列，运算符同样是 `<->`、`<#>`、`<=>`，所以从 `hnsw` 或 `ivfflat` 索引切换过来，表和查询都不用改。在旧索引旁边建新索引，对比之后删掉旧的：

1. [安装 vchord](/zh/docs/vchord/getting-started/installation/) 并创建扩展。
1. 在不阻塞写入的情况下建 vchordrq 索引。`lists` 按行数选，见[选择 `lists`](/zh/docs/vchord/usage/indexing/#lists)：

   ```sql
   CREATE INDEX CONCURRENTLY items_embedding_rq
   ON items USING vchordrq (embedding vector_cosine_ops)
   WITH (options = $$
   residual_quantization = true
   [build.internal]
   lists = [4096]
   spherical_centroids = true
   build_threads = 8
   $$, probes = '40');
   ```

1. 在设定的 `probes` 下[测量召回率](/zh/docs/vchord/usage/measure-recall/)，并用 `EXPLAIN` 确认查询走的是哪个索引。两个索引同时存在时，规划器按估算代价二选一。
1. 删除旧索引：

   ```sql
   DROP INDEX CONCURRENTLY items_embedding_hnsw;
   ```
{.steps}

会话参数不会沿用：`hnsw.ef_search` 和 `ivfflat.probes` 对 vchord 不起作用。请改用 `vchordrq.probes` 和 `vchordrq.epsilon`，或者像上面那样直接存在索引上。

## 从 pgvecto.rs 迁移 {#from-pgvectors}

<a id="from-pgvecto-rs"></a><a id="prerequisites"></a><a id="Prerequisites"></a><a id="steps-to-migration"></a>

[pgvecto.rs](/zh/docs/vectors/) 把向量存成 `vectors` 模式下的自有类型。迁移就是把每一列转换成对应的 pgvector 类型，再用 vchord 重建索引。转换列类型会在 `ACCESS EXCLUSIVE` 锁下重写整张表，大表要安排维护窗口。

| pgvecto.rs 类型 | pgvector 类型 | 转换表达式 |
| --- | --- | --- |
| `vectors.vector(n)` | `vector(n)` | `col::real[]::public.vector` |
| `vectors.vecf16(n)` | `halfvec(n)` | `col::vectors.vector::real[]::public.halfvec` |
| `vectors.bvector(n)` | `bit(n)` | `array_to_string(col::vectors.vector::real[], '')::bit(n)` |
| `vectors.svector(n)` | `sparsevec(n)` | 下标整体加一，见[下文](#appendix-about-cast-of-sparse-vector) |

1. <a id="1-install-vectorchord"></a>把 vchord 和 pgvector 装到 `vectors` 以外的模式（通常是 `public`），这样转换期间两个扩展可以共存。把 `vchord` 加到 `shared_preload_libraries` 中 `vectors` 的旁边，重启后执行 `CREATE EXTENSION vchord CASCADE;`。
1. <a id="2-check-existing-indexes"></a>保存 pgvecto.rs 索引的定义：

   ```sql
   SELECT indexrelid::regclass, pg_get_indexdef(indexrelid)
   FROM pg_index i
   JOIN pg_class c ON c.oid = i.indexrelid
   JOIN pg_am am ON am.oid = c.relam
   WHERE am.amname = 'vectors';
   ```

1. <a id="3-migrate-vector-columns"></a>删除这些索引，逐列转换类型：

   ```sql
   DROP INDEX index_vector;

   ALTER TABLE table_vector
       ALTER COLUMN vec TYPE public.vector(3)
       USING vec::real[]::public.vector;
   ```

1. <a id="4-recreate-index"></a>在转换后的列上创建 vchord 索引，见 [vchordrq 索引](/zh/docs/vchord/usage/indexing/)。
1. <a id="5-clean-the-environment"></a>确认没有任何列再使用 `vectors` 类型后，执行 `DROP EXTENSION vectors;`，并把 `vectors` 从 `shared_preload_libraries` 中移除。
{.steps}

### 转换稀疏向量 {#appendix-about-cast-of-sparse-vector}

<a id="appendix-cast-of-sparse-vector"></a>

pgvecto.rs 的稀疏向量下标从 0 开始（`{0:-1, 2:1}/5`），pgvector 的 `sparsevec` 从 1 开始（`{1:-1, 3:1}/5`）。下面的函数在转换时把每个下标加一：

```sql
CREATE OR REPLACE FUNCTION migrate_sparse(input_text text) RETURNS text AS $$
DECLARE
    output_text text := '';
    cache_index_number text := '';
    number_started boolean := false;
    ch text;
BEGIN
    FOR i IN 1..length(input_text) LOOP
        ch := substring(input_text FROM i FOR 1);
        IF ch = ':' THEN
            output_text := output_text || (cache_index_number::int + 1)::text || ':';
            number_started := false;
        ELSIF ch ~ '[,{]' THEN
            cache_index_number := '';
            number_started := true;
            output_text := output_text || ch;
        ELSIF ch ~ '[0-9]' AND number_started THEN
            cache_index_number := cache_index_number || ch;
        ELSE
            output_text := output_text || ch;
        END IF;
    END LOOP;
    RETURN output_text;
END;
$$ LANGUAGE plpgsql IMMUTABLE STRICT;

ALTER TABLE table_sparse
    ALTER COLUMN vec TYPE public.sparsevec
    USING migrate_sparse(vec::text)::public.sparsevec;
```

vchord 不索引 `sparsevec`。稀疏向量列请用 pgvector 的 HNSW 索引，关键词检索请用 [vchord_bm25](/zh/docs/bm25/)。
