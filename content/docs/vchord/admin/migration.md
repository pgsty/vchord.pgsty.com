---
title: "Upgrade and Migration"
linkTitle: "Upgrade & Migration"
description: "Upgrade vchord in place, move pgvector HNSW or IVFFlat indexes to vchord without rewriting tables, or migrate from pgvecto.rs."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/migration.md"
aliases:
  - "/docs/admin/migration/"
  - "/vectorchord/admin/migration/"
icon: fa-solid fa-right-left
---

<a id="vectorchord-migration-overview"></a>

This page covers three moves: [upgrading vchord](#upgrade) to a newer release, [replacing pgvector indexes](#from-pgvector) with vchord indexes, and [migrating from pgvecto.rs](#from-pgvectors), which used its own vector types.

## Upgrade vchord {#upgrade}

<a id="upgrading-vchord-to-130"></a>

vchord ships upgrade scripts from every earlier release, and 1.5.0 reads existing indexes in place.

1. Install the 1.5.0 files for your PostgreSQL major, as described in [Installation](/docs/vchord/getting-started/installation/).
1. Restart PostgreSQL so it loads the new library.
1. Update the extension in every database that has it:

   ```sql
   ALTER EXTENSION vchord UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

Depending on where you start, also do the following.

**From PostgreSQL 14.** vchord 1.4.0 and later do not support PostgreSQL 14. Stay on vchord 1.3.0 until PostgreSQL is upgraded to 15 or later, then upgrade vchord.

**From 1.3.0 or earlier.** The update passes through 1.4.0, which adds the SQL objects for [filter keys](/docs/vchord/usage/filtering/#filter-keys). A package downgrade does not undo that, so take a backup before upgrading if you may need to roll back.

**From 1.2.x or earlier.** Releases since 1.3.0 changed three things you may have to act on:

- `build.external.table` must name a schema-qualified table, such as `'public.t_build'`. Existing indexes keep serving queries, but any rebuild (`REINDEX`, `VACUUM FULL`, `CLUSTER`, `TRUNCATE`, a restore) fails until the option is fixed. Find affected indexes and rewrite their options, keeping the rest of each TOML string:

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

- Cosine distance on `rabitq8` and `rabitq4`, and the encoding of zero and one-dimensional vectors, were fixed. Rebuild `rabitq8` and `rabitq4` cosine indexes, and indexes holding such vectors, with `REINDEX INDEX CONCURRENTLY`.
- Reading [sampled queries](/docs/vchord/usage/measure-recall/#query-sampling) requires superuser or membership in `pg_read_all_stats`, because samples can contain other users' query vectors. Grant the role to whoever tunes recall.

**Graph indexes that lost recall.** A `VACUUM` before 1.5.0 could cut a region of a `vchordg` graph off from the rest. If recall dropped after large deletes, rebuild the index once with `REINDEX INDEX CONCURRENTLY`.

## From pgvector {#from-pgvector}

vchord indexes pgvector's own `vector` and `halfvec` columns with the same `<->`, `<#>`, and `<=>` operators, so moving from an `hnsw` or `ivfflat` index changes no table and no query. Build the new index next to the old one, compare, and drop the old one:

1. [Install vchord](/docs/vchord/getting-started/installation/) and create the extension.
1. Build a vchordrq index without blocking writes. Choose `lists` from the row count as described in [Choose `lists`](/docs/vchord/usage/indexing/#lists):

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

1. [Measure recall](/docs/vchord/usage/measure-recall/) at the `probes` you set, and check with `EXPLAIN` which index your queries use. While both indexes exist, the planner chooses between them by estimated cost.
1. Drop the old index:

   ```sql
   DROP INDEX CONCURRENTLY items_embedding_hnsw;
   ```
{.steps}

Session settings do not carry over: `hnsw.ef_search` and `ivfflat.probes` have no effect on vchord. Use `vchordrq.probes` and `vchordrq.epsilon`, or store them on the index as above.

## From pgvecto.rs {#from-pgvectors}

<a id="from-pgvecto-rs"></a><a id="prerequisites"></a><a id="Prerequisites"></a><a id="steps-to-migration"></a>

[pgvecto.rs](/docs/vectors/) stored vectors in its own types in the `vectors` schema. Migrating converts each column to the matching pgvector type and rebuilds its index with vchord. Converting a column rewrites the table under an `ACCESS EXCLUSIVE` lock, so plan a maintenance window for large tables.

| pgvecto.rs type | pgvector type | Conversion |
| --- | --- | --- |
| `vectors.vector(n)` | `vector(n)` | `col::real[]::public.vector` |
| `vectors.vecf16(n)` | `halfvec(n)` | `col::vectors.vector::real[]::public.halfvec` |
| `vectors.bvector(n)` | `bit(n)` | `array_to_string(col::vectors.vector::real[], '')::bit(n)` |
| `vectors.svector(n)` | `sparsevec(n)` | shift indexes by one, see [below](#appendix-about-cast-of-sparse-vector) |

1. <a id="1-install-vectorchord"></a>Install vchord and pgvector into a schema other than `vectors`, usually `public`, so both extensions can exist during the conversion. Add `vchord` to `shared_preload_libraries` next to `vectors`, restart, and run `CREATE EXTENSION vchord CASCADE;`.
1. <a id="2-check-existing-indexes"></a>Save the definitions of the pgvecto.rs indexes:

   ```sql
   SELECT indexrelid::regclass, pg_get_indexdef(indexrelid)
   FROM pg_index i
   JOIN pg_class c ON c.oid = i.indexrelid
   JOIN pg_am am ON am.oid = c.relam
   WHERE am.amname = 'vectors';
   ```

1. <a id="3-migrate-vector-columns"></a>Drop those indexes and convert each column:

   ```sql
   DROP INDEX index_vector;

   ALTER TABLE table_vector
       ALTER COLUMN vec TYPE public.vector(3)
       USING vec::real[]::public.vector;
   ```

1. <a id="4-recreate-index"></a>Create vchord indexes on the converted columns, as described in [vchordrq index](/docs/vchord/usage/indexing/).
1. <a id="5-clean-the-environment"></a>When nothing uses the `vectors` types any more, run `DROP EXTENSION vectors;` and remove `vectors` from `shared_preload_libraries`.
{.steps}

### Converting sparse vectors {#appendix-about-cast-of-sparse-vector}

<a id="appendix-cast-of-sparse-vector"></a>

pgvecto.rs numbers sparse vector dimensions from 0 (`{0:-1, 2:1}/5`); pgvector's `sparsevec` numbers them from 1 (`{1:-1, 3:1}/5`). This function shifts every index by one during the conversion:

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

vchord does not index `sparsevec`; use pgvector's HNSW index for sparse columns, or [vchord_bm25](/docs/bm25/) for keyword search.
