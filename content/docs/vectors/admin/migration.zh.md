---
title: "迁移指南"
linkTitle: "迁移指南"
description: "从 pgvector 迁移到 PGVecto.rs 的完整步骤与注意事项。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/migration.md"
aliases:
  - "/admin/migration/"
icon: fa-solid fa-right-left
---

# PGVecto.rs 迁移概览 {#pgvecto-rs-migration-overview}

## 从 pgvector 迁移 {#from-pgvector}

<a id="Prerequisites"></a>
### 前置条件 {#prerequisites}

从 `pgvector` 迁移到 `PGVecto.rs` 时，你通常已经有一张包含 `vector` 类型列的表。例如：

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
```

并且表中已经插入了一些数据行：

```sql
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
```

在大多数情况下，表上还会有一个或多个向量索引：

```sql
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
```

这是使用 `pgvector` 时的典型场景。如果满足以下条件，即可开始迁移：

- 请确认你的 `pgvector` 扩展并未安装在 `vectors` Schema 中。这意味着你可以在同一个数据库中同时安装 `pgvector` 和 `PGVecto.rs`。

### 迁移步骤 {#steps-to-migration}

<a id="1-install-pgvecto-rs"></a>
#### 1. 安装 PGVecto.rs {#1-install-pgvecto-rs}

请按照[安装指南](/zh/docs/vectors/getting-started/installation/)安装 `PGVecto.rs`，并确保 PostgreSQL 已加载该扩展。

```sql
CREATE EXTENSION vectors;
```

此时，`pgvector` 和 `PGVecto.rs` 两个扩展已同时安装在 PostgreSQL 中。

要验证安装结果，请在 `psql` 中运行 `\dx`。你会看到代表 `pgvector` 的 `vector` 扩展，以及代表 `PGVecto.rs` 的 `vectors` 扩展。

```shell
postgres=# \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description                                          
---------+---------+------------+----------------------------------------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vector  | 0.7.2   | public     | vector data type and ivfflat and hnsw access methods
 vectors | 0.3.0   | vectors    | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
```

请注意，这两个扩展中存在一些同名的类型和符号，这可能会在迁移过程中引起混淆。为了区分二者，请先确认当前的 `search_path` 中**不包含** `PGVecto.rs` 的 `vectors` Schema：

```sql
SHOW search_path;
-- 如果显示为：`"$user", public` -> 正常
-- 如果显示为：`"$user", public, vectors` -> 请通过以下命令移除 `vectors`：
SET search_path = "$user, public";
```

#### 2. 检查现有索引 {#2-check-existing-indexes}

对于在向量列上创建的索引，请先查询其定义并记录下来，以便在后续阶段重建索引。

```sql
postgres=# SELECT indexdef FROM pg_indexes WHERE tablename = 'items';
                                       indexdef                                        
---------------------------------------------------------------------------------------
 CREATE UNIQUE INDEX items_pkey ON public.items USING btree (id)
 CREATE INDEX items_embedding_idx ON public.items USING hnsw (embedding vector_l2_ops)
(2 rows)
```

#### 3. 迁移向量列 {#3-migrate-vector-columns}

要迁移 `pgvector` 的向量列，第一步是创建一个对应类型的 `PGVecto.rs` 向量列，第二步是将原列中的向量数据复制到新列中。

以下是 `pgvector` 各向量类型的转换路径：

- `vector(pgvector) -> real[] -> vector(PGVecto.rs)`
- `halfvec -> vector(pgvector) -> real[] -> vector(PGVecto.rs) -> vecf16`
- `bit -> text[] -> real[] -> vector(PGVecto.rs) -> bvector`

目前暂不支持迁移以下向量类型：
- `sparsevec`

**方法一：先验证再替换**

使用此方法，你可以在迁移过程中检查向量数据的正确性，而且无需担心原向量列上已创建的索引（在删除原列时索引会自动删除）。
但这种方法需要额外的存储空间来同时保存迁移前后的向量数据。

> [!WARNING]
> 此步骤会导致一定的停机时间，原因包括：
> - `ALTER TABLE ADD COLUMN` 会获取短暂的 `ACCESS EXCLUSIVE` 锁
> - `UPDATE` 会持有较长时间的 `ROW EXCLUSIVE` 锁
> - `ALTER TABLE DROP COLUMN` 会获取短暂的 `ACCESS EXCLUSIVE` 锁

```sql
-- 从 vector 类型转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vector(3);
UPDATE items SET migrate_embedding = embedding::real[]::vectors.vector;

-- 从 halfvec 类型转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vecf16(3);
UPDATE items SET migrate_embedding = embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- 从 bit 类型转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.bvector(3);
UPDATE items SET migrate_embedding = string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;
```

数据复制完成后，你可以通过 `SELECT` 检查数据，然后用新列替换旧列：

```sql
ALTER TABLE items DROP COLUMN embedding;
ALTER TABLE items RENAME COLUMN migrate_embedding TO embedding;
```

**方法二：原地转换（无需额外存储空间）**

使用此方法，可以在一条命令内完成列类型转换，无需占用额外的列存储空间。
但你需要提前手动删除该向量列上的索引。

> [!WARNING]
> 此步骤会导致一定的停机时间，原因包括：
> - `ALTER TABLE ALTER COLUMN` 会持有较长时间的 `ACCESS EXCLUSIVE` 锁

```sql
-- 索引名称来自第 2 步的查询结果
DROP INDEX IF EXISTS items_embedding_idx;

-- 从 vector 类型转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vector(3) USING embedding::real[]::vectors.vector;

-- 从 halfvec 类型转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vecf16(3) USING embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- 从 bit 类型转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.bvector(3) USING string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;
```

#### 4. 重建索引 {#4-recreate-index}

要为 `PGVecto.rs` 的 `vector` 列重建索引，可以开启[兼容模式](/zh/docs/vectors/usage/compatibility/)并直接执行之前的索引创建语句：

```sql
SET vectors.pgvector_compatibility=on;
-- 执行第 2 步中记录的命令
CREATE INDEX items_embedding_idx ON public.items USING hnsw (embedding vector_l2_ops);
```

对于其他向量类型（如 `halfvec`、`sparsevec` 和 `bit`），请参考[索引指南](/zh/docs/vectors/usage/indexing/)重新创建索引。目前 `pgvector_compatibility` 兼容模式暂不支持这些类型。

#### 5. 清理环境 {#5-clean-the-environment}

如果不再需要 `pgvector` 扩展，现在可以安全地将其卸载：

```
DROP extension vector;
```

卸载 `pgvector` 扩展后，建议重新设置 `search_path`，以确保可以在全局直接访问 `PGVecto.rs` 中的符号：

```sql
SET search_path = "$user, public, vectors";
-- 或在全局级别设置
ALTER SYSTEM SET search_path = "$user, public, vectors";
```

### 验证结果 {#verify-the-result}

迁移任务执行完毕后，你可以通过 `SELECT` 语句验证新列的数据与类型：

```sql
SELECT embedding, pg_typeof("embedding") from items limit 3;

-- embedding |   pg_typeof    
-------------+----------------
-- [1, 2, 3] | vectors.vector
-- [4, 5, 6] | vectors.vector
```
