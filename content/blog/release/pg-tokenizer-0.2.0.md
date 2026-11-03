---
title: "pg_tokenizer 0.2.0: Native Full-Text Search and Reliable Custom Models"
date: 2026-11-03
description: "pg_tokenizer 0.2.0 adds native tsvector output, filtered custom vocabularies, concurrent-write fixes, database-owner privileges, and transaction-aware cache invalidation."
author: "[Ruohang Feng](https://github.com/Vonng) · [PGSTY](https://pgsty.com)"
tags:
  - "release"
  - "pg_tokenizer"
  - "full-text-search"
upstream_source: ""
upstream_link: ""
---

**pg_tokenizer 0.2.0** connects its multilingual analyzers and vocabulary models to PostgreSQL's native full-text search. It also fixes custom-model concurrency, database-owner access, and stale definitions across database sessions. PGSTY maintains this release in [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) under the Apache-2.0 license.

The existing `tokenize(text, tokenizer_name)` interface still returns `INT[]`. Applications using the historical `vchord_bm25` 0.3.x `bm25vector` workflow can retain that interface; applications using GIN/GiST or the `vchord_bm25` 0.4.0/main API can use the new `tsvector` functions. `pg_tokenizer` does not require either BM25 or vector-search extensions.

## Changes in 0.2.0 {#changes}

| Area | Change |
| :--- | :--- |
| Native full-text search | `analyze_to_tsvector` and `tokenize_to_tsvector` produce native lexemes with positions. Empty output tokens are omitted before numbering. |
| Custom vocabularies | Optional corpus filters apply to training, backfill, and subsequent writes. Schema-qualified tables and quoted identifiers are supported. |
| Concurrent writes | Writers to one vocabulary serialize for the transaction; embedding updates see newly committed token IDs after waiting at `READ COMMITTED`. |
| Permissions | `pg_database_owner` receives catalog privileges, allowing non-superuser database owners to manage their tokenizer objects after installation. |
| Definition caches | Create/drop operations invalidate dependent cached objects across backends; transaction and subtransaction rollback cleanup is automatic. |
| Dependencies and upgrades | pgrx 0.19.3, Lindera 6.2.0, Jieba 0.11.0, and Hugging Face tokenizers 0.23.2; migration paths from 0.1.0, 0.1.1, and the 0.1.2 development snapshot. |

## Native `tsvector` output {#native-tsvector}

The two new functions cover different representations:

- `analyze_to_tsvector(text, text_analyzer_name)` uses the analyzer's string tokens as lexemes. It works with Jieba and custom normalization, stemming, stopword, and synonym pipelines without a vocabulary model.
- `tokenize_to_tsvector(text, tokenizer_name)` uses model token IDs as decimal lexemes. It supports built-in, custom, imported Hugging Face, and Lindera models without decoding their IDs or applying another PostgreSQL text normalization pass.

With the 0.2.0 library installed and preloaded, this example stores analyzed text and searches it with a native phrase query:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
SET search_path = public, tokenizer_catalog;

SELECT create_text_analyzer('release_words', $$
character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"
token_filters = ["skip_non_alphanumeric"]
$$);

SELECT analyze_to_tsvector('Cat dog cat', 'release_words');
-- 'cat':1,3 'dog':2

CREATE TABLE release_documents (id integer PRIMARY KEY, body text, terms tsvector);
INSERT INTO release_documents VALUES
    (1, 'Cat dog cat', analyze_to_tsvector('Cat dog cat', 'release_words'));
CREATE INDEX ON release_documents USING gin (terms);
SELECT id FROM release_documents WHERE terms @@ 'cat <-> dog'::tsquery;
-- 1

SELECT create_tokenizer('release_bert', 'model = "bert_base_uncased"');
SELECT tokenize_to_tsvector('hello hello', 'release_bert');
-- '7592':1,2
```

Both functions are `STRICT` and `STABLE`. Store and maintain the result in a column, then index that column. They cannot be used directly as immutable expressions for generated columns or expression indexes. The example fills `terms` explicitly; applications must also refresh it when the source text changes.

Positions start at 1 in the **final non-empty output sequence**, with default weight D. They are not source-text offsets: filters can remove or expand tokens, and models can emit subwords. Quotes, backslashes, whitespace, and punctuation inside lexemes are preserved. PostgreSQL's native limits still apply, including 256 positions per lexeme and a maximum position of 16,383.

Documents and queries must use the same lexeme representation. An ordinary `plainto_tsquery('english', ...)` does not reproduce custom analyzer output or model IDs. This release does not add a `tsquery` builder. See the [native full-text search guide](/docs/tokenizer/overview/#native-postgresql-full-text-search).

## Filtered custom models and concurrent writes {#custom-models}

The `create_custom_model` TOML configuration accepts an optional `filter`. The convenience helper has a seven-argument overload with `filter TEXT` as its last argument; its original six-argument signature and dependent callers are preserved. Omitting the filter, or passing SQL `NULL` to the helper, processes the whole table.

Using the analyzer created above:

```sql
CREATE TABLE release_corpus (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text,
    published boolean DEFAULT false,
    token_ids int[]
);

SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'release_corpus_tok',
    model_name => 'release_corpus_model',
    text_analyzer_name => 'release_words',
    table_name => 'public.release_corpus',
    source_column => 'body',
    target_column => 'token_ids',
    filter => 'published IS TRUE'
);

INSERT INTO release_corpus (body, published) VALUES
    ('PostgreSQL full text search', true),
    ('Unpublished draft', false);
```

Only rows for which the predicate is `TRUE` contribute to the vocabulary and receive embedding updates. This applies to the initial scan, backfill, and future inserts or updates, including updates that change only a predicate column. The helper fills an `INT[]` or compatible historical `bm25vector` column; it does not automatically maintain a native `tsvector` column.

Filters are trusted SQL expressions over ordinary source columns, without `WHERE` or `NEW.`; use deterministic predicates independent of the target column. They run with the caller's privileges and do not replace row-level security. Nonmatching rows retain existing embeddings, and vocabularies remain append-only after updates or deletes. Query with the same predicate, or clear excluded embeddings in the application. Empty and invalid predicates are rejected even for empty source tables.

Vocabulary writes now use a transaction-level advisory lock per model and insert new tokens in deduplicated, sorted order. This fixes deadlocks caused by opposite token insertion orders across concurrent batches. At `READ COMMITTED`, the embedding trigger refreshes its snapshot after waiting so it includes token IDs committed by the preceding writer. At `REPEATABLE READ` or `SERIALIZABLE`, conflicts can return SQLSTATE `40001`; retry the whole transaction. Keep transactions short and use a consistent order when writing multiple models or locking application rows.

Table names are resolved as SQL identifiers, including schema qualification and quoted names. A qualified name takes precedence over a literal table name containing a dot. See the [custom-model documentation](/docs/tokenizer/models/#custom-model-behavior-in-020).

## Definition caches and database-owner access {#caches-and-permissions}

Successful `create_*` and `drop_*` calls clear the current backend's definition caches. Transaction completion publishes an invalidation to other backends, which clear stale entries before their next lookup. Rebuilding an analyzer or model also invalidates tokenizers that held references to it. Rollbacks, including aborted subtransactions, clear cached objects from the reverted work. The previous workaround of dropping phantom objects or reconnecting after a rollback is no longer required.

Cache invalidation does not rewrite persisted `INT[]`, `bm25vector`, or `tsvector` values. When intentionally replacing a definition, recompute affected search columns and rebuild indexes as required by the consumer. Manage definitions through the extension's APIs; direct catalog-table edits are not covered by these invalidation hooks.

Installation and migration grant `pg_database_owner` access to `tokenizer_catalog`, its functions, tables, and sequences. A non-superuser database owner can manage its own analyzers, tokenizers, dictionaries, and custom models after an administrator installs the extension. The privileges follow database ownership changes. Other application roles still need explicit grants, and grants do not transfer ownership of existing model tables. See [database-owner permissions](/docs/tokenizer/installation/#database-owner-permissions).

## Upgrading to 0.2.0 {#upgrade}

Install the matching 0.2.0 shared library and SQL files, keep `pg_tokenizer` in `shared_preload_libraries` alongside any other required libraries, and restart PostgreSQL. Then run the following in each database containing the extension as its owner or an administrator:

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '0.2.0';
SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
-- 0.2.0
```

Upgrade paths are included for 0.1.0, 0.1.1, and the 0.1.2 development snapshot. They preserve catalog data, existing custom-vocabulary IDs, and dependencies on the original six-argument helper. The 0.1.2 SQL files remain an intermediate step in the migration chain; the release version is **0.2.0**.

Two changes need particular attention when stored search values are reused:

- **Lindera dictionary IDs:** the dependency moves from Lindera 0.42 to 6.2, and embedded IPADIC changes from the 2007-08-01 dictionary to the 2025-09-20 dictionary. Regenerate stored Lindera token arrays and ID-based vectors, and rebuild consuming indexes before using them with new query tokens. Legacy dictionary configuration tables remain accepted, but external compiled dictionaries must be rebuilt with Lindera 6. Embedded dictionaries remain optional build features. See [Lindera migration notes](/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model).
- **Empty-token positions:** vectors created by the 0.1.2 development snapshot may contain position gaps where a pipeline emitted empty tokens. Recompute these values when phrase positions matter; 0.2.0 numbers the remaining output consecutively.

## Compatibility, packages, and validation {#compatibility}

The check and release workflows target PostgreSQL **14–18** on Linux **x86_64/aarch64**. Build with the matching `cargo-pgrx 0.19.3`. A `pg19` Cargo feature is present, but PostgreSQL 19 is outside this release's configured test and package matrix.

Native RPM/DEB recipes use version **`0.2.0-1PGSTY`**. Local package validation covered PostgreSQL 18 on EL9/aarch64 and Ubuntu 24.04/arm64, including debug packages. Completion and publication of the full 16-platform matrix are separate from this source tag. Check actual package availability before upgrading, and match the distribution, PostgreSQL major version, and architecture.

The existing manual GitHub workflow builds Ubuntu 24.04 `.deb` packages with revision `-1` and Linux ZIP archives; these are distinct from the native `1PGSTY` package builds. ZIP archives carry no package-manager dependency metadata, so verify libc compatibility on the target host. This release workflow does not yet generate or upload SBOM artifacts.

Local acceptance passed Rust formatting, Clippy, unit tests, release build and SQL generation, **16 SQLLogicTest suites**, and **11 integration tests** covering concurrency, cache invalidation, permissions, and upgrades. The companion English and Chinese tokenizer documentation has been updated for 0.2.0.

Read the [installation and upgrade guide](/docs/tokenizer/installation/), [SQL reference](/docs/tokenizer/reference/), and [model documentation](/docs/tokenizer/models/) for configuration and operational details.
