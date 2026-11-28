---
title: "Migration"
linkTitle: "Migration"
description: "Historical guide for migrating columns and indexes from pgvector to legacy pgvecto.rs (vectors)."
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/migration.md"
aliases:
  - "/admin/migration/"
icon: fa-solid fa-right-left
---

<a id="pgvecto-rs-migration-overview"></a>

> [!IMPORTANT] Legacy Extension Notice (`pgvecto.rs` -> `vchord`)
> `pgvecto.rs` (`vectors`) is deprecated and succeeded by **[`vchord`](/docs/vchord/)**, which indexes `pgvector`'s `vector` and `halfvec` columns directly without rewriting table types. For new deployments or upgrades from `pgvecto.rs` to `vchord`, follow the [`vchord` Migration Guide](/docs/vchord/admin/migration/).

## From `pgvector` {#from-pgvector}

<a id="Prerequisites"></a>

### Prerequisites {#prerequisites}

Suppose you have an existing `pgvector` table and HNSW index:

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
CREATE INDEX ON items USING hnsw (embedding vector_l2_ops);
```

Ensure `pgvector` (`vector`) is **not** installed inside the `vectors` schema so `pgvector` and `pgvecto.rs` (`vectors`) can coexist during migration.

### Migration Steps {#steps-to-migration}

#### 1. Install `pgvecto.rs` {#1-install-pgvecto-rs}

Follow the [`pgvecto.rs` installation guide](/docs/vectors/getting-started/installation/), preload `vectors`, and create the extension:

```sql
CREATE EXTENSION vectors;
```

Verify with `\dx` that `vector` (`public`) and `vectors` (`vectors`) are both installed, and ensure `vectors` is **not** yet in your `search_path`:

```sql
SHOW search_path;
-- Keep "$user", public (do not include vectors during column casts):
SET search_path = "$user", public;
```

#### 2. Check Existing Indexes {#2-check-existing-indexes}

Record existing index definitions on your vector columns before modifying column types:

```sql
SELECT indexdef FROM pg_indexes WHERE tablename = 'items';
```

#### 3. Migrate Vector Columns {#3-migrate-vector-columns}

Supported conversion paths from `pgvector` to `pgvecto.rs`:

- `vector` -> `real[]` -> `vectors.vector`
- `halfvec` -> `vector` -> `real[]` -> `vectors.vector` -> `vectors.vecf16`
- `bit` -> `text[]` -> `real[]` -> `vectors.vector` -> `vectors.bvector`
- (`sparsevec` is not supported by this cast path.)

**Method 1: Side-by-side column copy (validates before dropping)**

> [!WARNING] Locking Notice
> `ALTER TABLE ADD/DROP COLUMN` acquires a brief `ACCESS EXCLUSIVE` lock, and `UPDATE` holds a `ROW EXCLUSIVE` lock while duplicating storage temporarily.

```sql
-- From vector
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vector(3);
UPDATE items SET migrate_embedding = embedding::real[]::vectors.vector;

-- From halfvec
ALTER TABLE items ADD COLUMN migrate_embedding vectors.vecf16(3);
UPDATE items SET migrate_embedding = embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- From bit
ALTER TABLE items ADD COLUMN migrate_embedding vectors.bvector(3);
UPDATE items SET migrate_embedding = string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;

-- Swap columns after verification
ALTER TABLE items DROP COLUMN embedding;
ALTER TABLE items RENAME COLUMN migrate_embedding TO embedding;
```

**Method 2: In-place `ALTER COLUMN TYPE`**

> [!WARNING] Locking Notice
> `ALTER TABLE ... ALTER COLUMN ... TYPE` holds an `ACCESS EXCLUSIVE` lock for the full table rewrite.

```sql
DROP INDEX IF EXISTS items_embedding_idx;

-- From vector
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vector(3) USING embedding::real[]::vectors.vector;

-- From halfvec
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.vecf16(3) USING embedding::vector::real[]::vectors.vector::vectors.vecf16;

-- From bit
ALTER TABLE items ALTER COLUMN embedding TYPE vectors.bvector(3) USING string_to_array(embedding::text, NULL)::real[]::vectors.vector::vectors.bvector;
```

#### 4. Recreate Indexes {#4-recreate-index}

Enable [`pgvector` compatibility mode](/docs/vectors/usage/compatibility/) for `vectors.vector` columns or use `USING vectors` directly (see [`pgvecto.rs` Indexing](/docs/vectors/usage/indexing/)):

```sql
SET vectors.pgvector_compatibility = on;
CREATE INDEX items_embedding_idx ON public.items USING hnsw (embedding vector_l2_ops);
```

#### 5. Clean the Environment {#5-clean-the-environment}

If `pgvector` is no longer needed, drop it and add `vectors` to `search_path`:

```sql
DROP EXTENSION vector;
ALTER SYSTEM SET search_path = "$user", public, vectors;
```

### Verify the Result {#verify-the-result}

```sql
SELECT embedding, pg_typeof(embedding) FROM items LIMIT 3;
```
