---
title: "版本升级"
linkTitle: "版本升级"
description: "如何将 pgvecto.rs 扩展升级到新版本并更新扩展 Schema 与索引。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/upgrading.md"
aliases:
  - "/admin/upgrading/"
---

## 通用步骤 {#general-steps}

如果你将扩展更新到了新版本（假设版本号为 `a.b.c`），可以使用以下命令更新扩展的 Schema：

```sql
ALTER EXTENSION vectors UPDATE;
-- 或
ALTER EXTENSION vectors UPDATE TO 'a.b.c';
```

如果你是从 `0.1.x` 版本升级，请先阅读[从 0.1.x 升级](#upgrade-from-0-1-x)。

如果你要升级到 `0.4.0` 版本，请阅读[升级到 0.4.0](#upgrade-to-0-4-0)。

随后执行以下 SQL，它会协助完成必要的维护工作：

```sql
SELECT pgvectors_upgrade();
```

你需要重启 PostgreSQL 实例以使更改生效。

你可以通过以下命令查看所有向量索引的状态：

```sql
SELECT
        I.relname AS indexname
    FROM pg_index X JOIN
         pg_class I ON I.oid = X.indexrelid JOIN
         pg_am A ON A.oid = I.relam
    WHERE A.amname = 'vectors';
```

假设输出如下：

```text
 indexname
-------------
 t_val_idx_1
 t_val_idx_2
```

然后你可以重建所有向量索引：

```sql
REINDEX INDEX t_val_idx_1;
REINDEX INDEX t_val_idx_2;
```

## 升级到 0.4.0 {#upgrade-to-0-4-0}

如果在将 `pgvecto.rs` 升级到 0.4.0 之前已经创建了一些[索引](/zh/docs/vectors/usage/indexing/)，你可能会遇到以下错误：

```
ERROR:  index public.this_is_index depends on operator class vector_cos_ops for access method vectors
index public.this_is_index depends on operator class vector_cos_ops for access method vectors cannot drop operator class vector_cos_ops for access method vectors because other objects depend on it 

ERROR:  cannot drop operator class vector_cos_ops for access method vectors because other objects depend on it
SQL state: 2BP01
Detail: index public.that_is_also_index depends on operator class vector_cos_ops for access method vectors
index public.that_is_also_index depends on operator class vector_cos_ops for access method vectors
Hint: Use DROP ... CASCADE to drop the dependent objects too.
```

你只需先删除这些索引，然后再升级扩展并重建索引即可：

```sql
DROP INDEX this_is_index;
DROP INDEX that_is_also_index;

ALTER EXTENSION vectors UPDATE;

-- CREATE INDEX this_is_index ...
-- CREATE INDEX that_is_also_index ...
```

## 从 0.1.x 升级 {#upgrade-from-0-1-x}

你需要按照以下步骤操作，才能使 `ALTER EXTENSION vectors UPDATE` 正常工作。

假设你当前的 `pgvecto.rs` 版本为 `0.1.x`（请将 `x` 替换为实际的数字）：

```sql
CREATE SCHEMA IF NOT EXISTS vectors;
UPDATE pg_catalog.pg_extension SET extversion = '0.1.x' where extname = 'vectors';
UPDATE pg_catalog.pg_extension SET extrelocatable = true where extname = 'vectors';
ALTER EXTENSION vectors SET SCHEMA vectors;
UPDATE pg_catalog.pg_extension SET extrelocatable = false where extname = 'vectors';
ALTER EXTENSION vectors UPDATE;
```

> [!TIP]
> 从 `0.2.0` 版本开始，`pgvecto.rs` 安装在 `vectors` Schema 下，你可能需要为数据库配置 `search_path`。
