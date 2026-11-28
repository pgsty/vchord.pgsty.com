---
title: "Upgrade and Migration"
linkTitle: "Upgrade and Migration"
description: "vchord_bm25 releases, in-place upgrades and downgrades within 1.x, and migrating from the 0.x bm25vector API."
weight: 30
icon: fa-solid fa-right-left
aliases:
  - "/docs/bm25/reference/versions/"
---

Any 1.x installation upgrades to 1.3.0 in place, keeping its indexes. Installations of the 0.x releases, which used a `bm25vector` type instead of `tsvector`, cannot be upgraded: their indexes are rebuilt from the source text in a new installation, as described in [Migrate from 0.x](#from-0x).

## Releases {#releases}

| Version | Date | Summary | Notes |
| --- | --- | --- | --- |
| 1.3.0 | 2026-11-24 | Opt-in `shared_corpus_stats` for tables with row-level security; prefiltering through correlated subqueries; the planner picks the bm25 index for selective top-k queries more often; less WAL during builds and merges. | [Release post](/release/vchord-bm25-1.3.0/) |
| 1.2.0 | 2026-11-23 | PostgreSQL 15–19, dropping PostgreSQL 14; planner and maintenance fixes. | [Release post](/release/vchord-bm25-1.2.0/) |
| 1.1.0 | 2026-11-08 | Fixes pruning that could omit near-tied documents; faster scoring and prefiltering. PostgreSQL 14–18. | [Release post](/release/vchord-bm25-1.1.0/) |
| 1.0.0 | 2026-11-04 | First PGSTY release: native `tsvector` indexing replaces `bm25vector`, scans continue past `bm25.limit`, `VACUUM` merges concurrently, privilege and row-level security checks. PostgreSQL 14–18. | [Release post](/release/vchord-bm25-1.0.0/) |
| 0.1.0–0.3.0 | 2025-02-06 to 2025-12-15 | Upstream releases with the `bm25vector` API in the `bm25_catalog` schema. | [Upstream releases](https://github.com/supervc-stack/VectorChord-bm25/releases) |

## Upgrade within 1.x {#upgrade}

Indexes built by 1.0.0, 1.1.0, and 1.2.0 work with 1.3.0 unchanged; no `REINDEX` is needed.

1. Check the server version. 1.3.0 supports PostgreSQL 15–19; a PostgreSQL 14 server must be upgraded first.
1. Install the 1.3.0 files on every node, primary and standbys, using the same method as before ([Installation](/docs/bm25/getting-started/installation/)).
1. Restart PostgreSQL on each node, so it preloads the new library.
1. In each database that has the extension, on the primary:

   ```sql
   ALTER EXTENSION vchord_bm25 UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

### Downgrade {#downgrade}

There is no SQL script to go back to an earlier version, but 1.3.0 did not change the extension's SQL objects, so you can run a 1.x library older than 1.3.0 against it. Before you do, reset `shared_corpus_stats` on every index where it was set, even to `off`, because older libraries do not know the option. To find those indexes:

```sql
SELECT c.oid::regclass AS index
FROM pg_class AS c
JOIN pg_am AS am ON am.oid = c.relam
WHERE am.amname = 'bm25'
  AND EXISTS (SELECT FROM unnest(c.reloptions) AS o WHERE o LIKE 'shared_corpus_stats=%');
```

Run `ALTER INDEX <index> RESET (shared_corpus_stats);` for each, then install the older library and restart.

## Migrate from 0.x {#from-0x}

The 0.x releases stored documents in a `bm25vector` column filled from pg_tokenizer's `tokenize()`, in a fixed `bm25_catalog` schema. Their index format and SQL API differ from 1.x, so `ALTER EXTENSION vchord_bm25 UPDATE` on 0.3.0 stops before changing anything, with `vchord_bm25 0.3.0 cannot be upgraded in place to 1.0.0`.

A `bm25vector` column is derived from text, so migrating means producing `tsvector` values from the same text and building new indexes:

1. **Export while 0.x is installed.** Export the tables with the text columns, leaving out the `bm25vector` columns, which cannot be restored into 1.x, for example `COPY (SELECT id, passage FROM documents) TO ...`. Save the definitions of the tokenizers (`tokenizer_catalog.tokenizer`), views, functions, and triggers that use `bm25vector`.
1. **Install 1.3.0 in a separate PostgreSQL installation**, such as another host or container. One installation loads a single vchord_bm25 library, and the 1.x library cannot serve 0.x databases.
1. **Load the data and produce `tsvector` values.** To keep the same tokens as before, recreate the pg_tokenizer tokenizer and use `tokenizer_catalog.tokenize_to_tsvector(text, 'tokenizer')`, which emits the token IDs that `tokenize()` returned as lexemes. Alternatively, switch to `to_tsvector` or a pg_tokenizer text analyzer, as in [Indexing](/docs/bm25/usage/indexing/#tsvector).
1. **Build the indexes and rewrite queries and settings** using the table below.
1. **Switch the application** to the new installation, then retire the old one.
{.steps}

| | 0.x | 1.x |
| --- | --- | --- |
| Document column | `bm25vector`, from `tokenize(text, tokenizer)` | `tsvector` with positions |
| Schema | `bm25_catalog`, fixed | Any schema, relocatable |
| Query constructor | `to_bm25query('index', query_bm25vector)` | `to_bm25query(query_tsvector, 'index')`; the arguments are swapped |
| Score type | `real` | `double precision` |
| `bm25_catalog.bm25_limit` (default `100`, `-1` scans all) | Most rows a search returns; filtered queries could come back short | `bm25.limit`: size of the first batch only; results are always complete |
| `bm25_catalog.enable_index` (default `on`) | Planner switch | `bm25.enable_scan` |
| `bm25_catalog.enable_prefilter` (default `on`) | Prefiltering | `bm25.prefilter`, default `off` |
| `bm25_catalog.segment_growing_max_page_size` (default `4096` pages) | Growing segment sealed at this size | Merged by `VACUUM`; index options `maintenance_min_rows` and `maintenance_scale_factor` |
| `bm25_page_inspect(regclass, int)` | Page dump for debugging | None |
{.wide}

A 0.x workflow and its 1.x equivalent, with the same BERT tokenizer:

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

Keep `terms` current for new rows with a trigger, as shown in [Indexing](/docs/bm25/usage/indexing/#tsvector).
