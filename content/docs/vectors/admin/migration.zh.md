---
title: "迁移指南"
linkTitle: "迁移指南"
description: "从 pgvector 迁移列类型与索引至历史扩展 pgvecto.rs（vectors）的操作参考。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/migration.md"
aliases:
  - "/admin/migration/"
icon: fa-solid fa-right-left
---

<a id="pgvecto-rs-migration-overview"></a>

> [!IMPORTANT] 历史扩展维护提示（推荐使用 `vchord`）
> `pgvecto.rs`（`vectors`）已停止演进并由 **[`vchord`](/zh/docs/vchord/)** 正式接替。`vchord` 直接复用 `pgvector` 的 `vector` 与 `halfvec` 列类型，无需转换表列即可直接建索引。新建项目或从 `pgvecto.rs` 升级至 `vchord`，请参阅 [`vchord` 升级与迁移指南](/zh/docs/vchord/admin/migration/)。

## 从 `pgvector` 迁移 {#from-pgvector}

<a id="Prerequisites"></a>

### 前置条件 {#prerequisites}

假设现有业务已包含一张 `pgvector` 向量表与 HNSW 索引：

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
```

请确认 `pgvector`（`vector`）未安装在 `vectors` 模式下，以便 `pgvector` 与 `pgvecto.rs`（`vectors`）在迁移期间共存。

### 迁移步骤 {#steps-to-migration}

#### 1. 安装 `pgvecto.rs` {#1-install-pgvecto-rs}

参照 [`pgvecto.rs` 安装指南](/zh/docs/vectors/getting-started/installation/)安装并预加载 `vectors` 扩展，随后创建扩展：

```sql
CREATE EXTENSION vectors;
```

运行 `\dx` 确认 `vector`（位于 `public`）与 `vectors`（位于 `vectors`）均已启用，并确保转换期间 `search_path` 中**暂不包含** `vectors`：

```sql
SHOW search_path;
-- 保持 "$user", public（转换列期间不要包含 vectors）：
SET search_path = "$user", public;
```

#### 2. 检查现有索引 {#2-check-existing-indexes}

在修改列类型前记录向量列上的索引定义：

```sql
SELECT indexdef FROM pg_indexes WHERE tablename = 'items';
```

#### 3. 迁移向量列 {#3-migrate-vector-columns}

从 `pgvector` 到 `pgvecto.rs` 的类型转换路径：

- `vector` -> `real[]` -> `vectors.vector`
- `halfvec` -> `vector` -> `real[]` -> `vectors.vector` -> `vectors.vecf16`
- `bit` -> `text[]` -> `real[]` -> `vectors.vector` -> `vectors.bvector`
- （`sparsevec` 暂不支持该转换路径。）

**方法一：新增列复制并验证后再切换**

> [!WARNING] 锁开销提示
> `ALTER TABLE ADD/DROP COLUMN` 会短暂获取 `ACCESS EXCLUSIVE` 锁，`UPDATE` 全表复制期间会持有 `ROW EXCLUSIVE` 锁并临时占用双倍存储空间。

```sql
-- 从 vector 转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vector(3);
UPDATE items SET migrate_embedding = embedding::real[]::vectors.vector;

-- 从 halfvec 转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vecf16(3);
UPDATE items SET migrate_embedding = embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- 从 bit 转换
ALTER TABLE items ADD COLUMN migrate_embedding vectors.bvector(3);
UPDATE items SET migrate_embedding = string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;

-- 校验无误后替换原列
ALTER TABLE items DROP COLUMN embedding;
ALTER TABLE items RENAME COLUMN migrate_embedding TO embedding;
```

**方法二：原地转换列类型（`ALTER COLUMN TYPE`）**

> [!WARNING] 锁开销提示
> `ALTER TABLE ... ALTER COLUMN ... TYPE` 重写表期间会持续持有 `ACCESS EXCLUSIVE` 排他锁。

```sql
DROP INDEX IF EXISTS items_embedding_idx;

-- 从 vector 转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vector(3) USING embedding::real[]::vectors.vector;

-- 从 halfvec 转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vecf16(3) USING embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- 从 bit 转换
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.bvector(3) USING string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;
```

#### 4. 重建索引 {#4-recreate-index}

对于 `vectors.vector` 列可启用 [`pgvector` 兼容模式](/zh/docs/vectors/usage/compatibility/)，或直接使用 `USING vectors` 创建索引（详见 [`pgvecto.rs` 索引指南](/zh/docs/vectors/usage/indexing/)）：

```sql
SET vectors.pgvector_compatibility = on;
CREATE INDEX items_embedding_idx ON public.items USING hnsw (embedding vector_l2_ops);
```

#### 5. 清理环境 {#5-clean-the-environment}

确认不再需要 `pgvector` 后，可卸载 `vector` 并将 `vectors` 加入全局 `search_path`：

```sql
DROP EXTENSION vector;
ALTER SYSTEM SET search_path = "$user", public, vectors;
```

### 验证迁移结果 {#verify-the-result}

```sql
SELECT embedding, pg_typeof(embedding) FROM items LIMIT 3;
```
