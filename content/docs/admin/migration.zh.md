---
title: "迁移指南"
linkTitle: "迁移指南"
description: "VectorChord 的绝大多数向量数据类型均由 pgvector 原生支持，本文介绍如何从 PGVecto.rs 平滑迁移至 VectorChord。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/migration.md"
aliases:
  - "/vectorchord/admin/migration/"
---

---
outline: [2,3]
---
# VectorChord 迁移概览 {#vectorchord-migration-overview}

<a id="from-pgvecto-rs"></a>
## 从 PGVecto.rs 迁移 {#from-pgvectors}

VectorChord 的绝大多数向量类型均由 `pgvector` 提供支持。
因此，从 PGVecto.rs 迁移到 VectorChord 的过程，基本上就是[从 pgvector 迁移到 PGVecto.rs](/zh/pgvecto-rs/admin/migration/) 的逆向操作。

> [!TIP]
> 我们提供了专用的迁移镜像 [modelzai/pgvectors-vchord](https://hub.docker.com/r/modelzai/pgvectors-vchord/tags)，用于支持在 pgvecto.rs 与 VectorChord 之间进行双向迁移。


<a id="Prerequisites"></a>
### 前置条件 {#prerequisites}

假设您已经拥有包含向量数据的表，并且安装了 `PGVecto.rs` 扩展。一个简单的示例如下：

```sql
CREATE TABLE table_vector (id bigserial PRIMARY KEY, vec_f32 vectors.vector(3));
CREATE TABLE table_float16 (id bigserial PRIMARY KEY, vec_f16 vectors.vecf16(3));
CREATE TABLE table_binary (id bigserial PRIMARY KEY, vec_bits vectors.bvector(3));

```

此外，表中还插入了一些数据行，如下所示：

```sql
INSERT INTO table_vector (vec_f32) VALUES ('[0.1, 0.1, 0.1]'), ('[0.2, 0.2, 0.2]');
INSERT INTO table_float16 (vec_f16) VALUES ('[0.1, 0.1, 0.1]'), ('[-0.2, 0.2, 0.2]');
INSERT INTO table_binary (vec_bits) VALUES ('[0, 0, 0]'), ('[0, 0, 1]');
```

在大多数情况下，表上还会建有一个或多个向量索引：

```sql
CREATE INDEX index_vector ON table_vector USING vectors (vec_f32 vectors.vector_l2_ops) WITH (options = "[indexing.hnsw]");
-- CREATE INDEX index_float16 ON table_float16 USING vectors (vec_f16 vectors.vecf16_cos_ops) WITH (options = "[indexing.hnsw]");
-- CREATE INDEX index_binary ON table_binary USING vectors (vec_bits vectors.bvector_hamming_ops) WITH (options = "[indexing.hnsw]");
```

这是使用 `PGVecto.rs` 时的典型场景。如果满足以下条件，即可开始执行迁移：

- 请注意，您的 `pgvector` 和 `VectorChord` 扩展不能安装在 `vectors` 模式（schema）下。这意味着您可以在同一个数据库中同时安装 `pgvector` 和 `PGVecto.rs`。

### 迁移步骤 {#steps-to-migration}

#### 1. 安装 VectorChord {#1-install-vectorchord}

请按照[安装说明](/zh/docs/getting-started/installation/)安装 `VectorChord`，并确保 PostgreSQL 已加载该扩展。

```sql
CREATE EXTENSION vchord CASCADE;
```

> [!NOTE]
>
> 上述命令会将 `vectorchord` 和 `pgvector` 安装在 `public` 模式下。如果您选择了其他模式，请在后续迁移命令中将 `public` 替换为您实际使用的模式名。
>


> [!DETAILS]
>
> 此时，`VectorChord` 和 `PGVecto.rs` 这两个扩展已同时安装在 PostgreSQL 中，但位于不同的模式下。
> 若要验证这一点，请在 `psql` 中运行 `\dx`。您将看到已安装以下 3 个扩展：
> - 位于 `vectors` 模式下的 `vectors`（即 `PGVecto.rs`）
> - 位于 `public` 模式下的 `vector`（即 `pgvector`）
> - 位于 `public` 模式下的 `vchord`（即 `VectorChord`）
>
> ```shell
> postgres=# \dx
>                                                  List of installed extensions
>   Name   | Version |   Schema   |                                         Description                                          
> ---------+---------+------------+----------------------------------------------------------------------------------------------
>  plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
>  vchord  | 0.1.0   | public     | vchord: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
>  vector  | 0.8.0   | public     | vector data type and ivfflat and hnsw access methods
>  vectors | 0.4.0   | vectors    | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
> ```
>


#### 2. 检查现有索引 {#2-check-existing-indexes}

对于在向量列上创建的索引，请先查询其定义并将其记录在安全的地方。
在后续恢复重建索引的阶段，您将需要用到这些信息。

```sql
postgres=# \di
                       List of relations
 Schema |        Name        | Type  |  Owner   |     Table     
--------+--------------------+-------+----------+---------------
 public | index_float16      | index | postgres | table_float16
 public | index_vector       | index | postgres | table_vector
 public | table_binary_pkey  | index | postgres | table_binary
 public | table_float16_pkey | index | postgres | table_float16
 public | table_vector_pkey  | index | postgres | table_vector
```

#### 3. 迁移向量列 {#3-migrate-vector-columns}

要从 `PGVecto.rs` 的向量列进行迁移，第一步是在不同扩展之间转换列的数据类型。

以下列出了 `VectorChord` 各向量类型的转换路径：

- `vector(PGVecto.rs) -> real[] -> vector(pgvector)`
- `vecf16 -> vector(PGVecto.rs) -> real[] -> halfvec`
- `bvector -> vector(PGVecto.rs) -> text[] -> real[] -> bit`
- `svector -> text -> index++ -> text -> sparsevec`

对于稀疏向量类型 `svector`，我们需要编写一个额外的辅助函数来完成类型转换，具体请参阅[附录](#appendix-about-cast-of-sparse-vector)。

列类型迁移可通过单条命令完成，且无需消耗额外内存。
但是，您需要预先删除该向量列上的现有索引。

> [!WARNING]
> 此步骤会导致一定的停机时间，原因在于：
> - `ALTER TABLE ALTER COLUMN` 会持有较长时间的 `ACCESS EXCLUSIVE` 排他锁


```sql
-- 索引名称可在第 2 步中查得
DROP INDEX IF EXISTS index_vector;

-- 转换常规 vector 类型
ALTER TABLE table_vector ALTER COLUMN vec_f32 TYPE public.vector(3) USING vec_f32::real[]::public.vector;

-- 转换半精度 halfvec 类型
ALTER TABLE table_float16 ALTER COLUMN vec_f16 TYPE public.halfvec(3) USING vec_f16::vectors.vector::real[]::public.halfvec;

-- 转换二值 bit 类型
ALTER TABLE table_binary ALTER COLUMN vec_bits TYPE bit(3) USING array_to_string(vec_bits::vectors.vector::real[], '')::bit(3);
```

#### 4. 重建索引 {#4-recreate-index}

下一步是在转换后的 `vector` 列上使用 `VectorChord` 重新创建索引。

```sql
CREATE INDEX ON index_vector USING vchordrq (vec_f32 vector_l2_ops) WITH (options = $$
residual_quantization = true
[build.internal]
lists = [4096]
spherical_centroids = false
$$);
```

关于在 `VectorChord` 中创建索引的更多信息，请参阅[构建索引](/zh/docs/usage/indexing/)。

#### 5. 清理环境 {#5-clean-the-environment}

如果不再需要 `PGVecto.rs` 扩展，现在您可以安全地将其移除：

```
DROP extension vectors;
```

<a id="appendix-cast-of-sparse-vector"></a>
### 附录：稀疏向量的类型转换 {#appendix-about-cast-of-sparse-vector}

上文已经讨论了大多数向量类型，唯独还没有涉及稀疏向量（Sparse Vector）。它的转换比其他类型稍显复杂。假设我们有一张包含稀疏向量列的表：

```sql
CREATE TABLE table_sparse (id bigserial PRIMARY KEY, vec_sparse vectors.svector(3));
INSERT INTO table_sparse (vec_sparse) VALUES ('{0:-0.1, 1:0.1, 2:0.1}/3'), ('{0:-0.4, 1:-0.4, 2:-0.4}/3');
```

稀疏向量在 `PGVecto.rs` 和 `pgvector` 之间具有不同的文本表示格式：在 `PGVecto.rs` 中，维度下标从 `0` 开始；而在 `pgvector` 中，维度下标从 `1` 开始。

例如，一个典型的稀疏向量 `[-1, 0, 1, 0, 2]` 的文本表示分别为：
- 在 `PGVecto.rs` 中：`{0:-1, 2:1, 4:2}/5`
- 在 `pgvector` 中：`{1:-1, 3:1, 5:2}/5`

因此，我们需要创建一个辅助函数，通过处理字符串将下标整体加 1：
```sql
CREATE OR REPLACE FUNCTION migrate_sparse(input_text text) RETURNS text AS $$
DECLARE
    output_text text := '';
    cache_index_number text := '';
    number_started boolean := false;
BEGIN
    FOR i IN 1..length(input_text) LOOP
        IF substring(input_text from i for 1) = ':' THEN
            output_text := output_text || (cache_index_number::int + 1)::text || ':';
            number_started := false;
        ELSIF substring(input_text from i for 1) ~ '[,{]' THEN
            cache_index_number := '';
            number_started := true;
            output_text := output_text || substring(input_text from i for 1);
        ELSIF substring(input_text from i for 1) ~ '[0-9]' THEN
            IF number_started THEN
                cache_index_number := cache_index_number || substring(input_text from i for 1);
            ELSE
                output_text := output_text || substring(input_text from i for 1);
            END IF;
        ELSE
            output_text := output_text || substring(input_text from i for 1);
        END IF;
    END LOOP;
    RETURN output_text;
END;
$$ LANGUAGE plpgsql;
```

创建该函数后，即可顺利完成稀疏向量列的迁移：
```sql
ALTER TABLE table_sparse ALTER COLUMN vec_sparse TYPE public.sparsevec USING migrate_sparse(vec_sparse::text)::public.sparsevec;
```
