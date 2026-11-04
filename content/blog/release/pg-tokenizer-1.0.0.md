---
title: "pg_tokenizer 1.0.0: Native Full-Text Search and Reliable Custom Models"
date: 2026-11-03
description: "pg_tokenizer 1.0.0, the first PGSTY release, adds native tsvector output, filtered custom vocabularies, safe concurrent vocabulary writes, database-owner privileges, and transaction-aware definition caches."
author: "[Ruohang Feng](https://github.com/Vonng) · [PGSTY](https://pgsty.com)"
tags:
  - "release"
  - "pg_tokenizer"
  - "full-text-search"
upstream_source: ""
upstream_link: ""
---

**pg_tokenizer 1.0.0** is the first release maintained by PGSTY in [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) under the Apache-2.0 license. It connects the multilingual analyzers and vocabulary models to PostgreSQL's native full-text search, makes corpus-trained custom models safe under concurrent writes, and lets non-superuser database owners manage their own tokenizer definitions.

The existing `tokenize(text, tokenizer_name)` interface still returns `INT[]`. Applications using the historical `vchord_bm25` 0.3.x `bm25vector` workflow can retain that interface; applications using GIN/GiST or the `vchord_bm25` 0.4.0/main API can use the new `tsvector` functions. `pg_tokenizer` does not require either BM25 or vector-search extensions.

## Changes in 1.0.0 {#changes}

| Area | Change |
| :--- | :--- |
| Native full-text search | `analyze_to_tsvector` and `tokenize_to_tsvector` produce native lexemes with consecutive positions. Empty tokens and tokens longer than 2046 bytes are skipped, as in `to_tsvector`. |
| Custom vocabularies | Optional corpus filters apply to training, backfill, and subsequent writes. Schema-qualified tables and quoted identifiers are supported. |
| Concurrent writes | Only writers that add tokens to a vocabulary take its per-model lock; embedding updates see newly committed token IDs at `READ COMMITTED`. |
| Permissions | `pg_database_owner` receives catalog privileges; vocabulary triggers call extension functions with exact argument types; the cluster-wide preload list stays administrator-only. |
| Definition caches | Create/drop operations invalidate dependent cached objects across backends at commit, rollbacks clean up locally, and definitions loaded under an older snapshot are not carried into later statements. |
| Text analysis | `ngram` counts Unicode characters, so CJK text and emoji no longer fail, and tokens shorter than `min_gram` (including empty input) produce no n-grams instead of an error or an endless loop. `pg_dict` calls dictionaries the way `ts_lexize` does, so thesaurus dictionaries apply their single-word entries. |
| Preloading and backups | Preloaded models survive cache invalidation, broken preload entries no longer prevent startup, and `pg_dump` includes the definition tables. |
| Dependencies and upgrades | pgrx 0.19.3 for PostgreSQL 14–18, Lindera 6.2.0, Jieba 0.11.0, Hugging Face tokenizers 0.23.2, and Snowball stemmers from [`pgsty/rust-stemmers`](https://github.com/pgsty/rust-stemmers) 1.2.1 (same stemming output); migration paths from 0.1.0 and 0.1.1. |

## Native `tsvector` output {#native-tsvector}

The two new functions cover different representations:

- `analyze_to_tsvector(text, text_analyzer_name)` uses the analyzer's string tokens as lexemes. It works with Jieba and custom normalization, stemming, stopword, and synonym pipelines without a vocabulary model.
- `tokenize_to_tsvector(text, tokenizer_name)` uses model token IDs as decimal lexemes. It supports built-in, custom, imported Hugging Face, and Lindera models without decoding their IDs or applying another PostgreSQL text normalization pass.

With the 1.0.0 library installed and preloaded, this example stores analyzed text and searches it with a native phrase query:

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

Both functions are `STRICT`, `STABLE`, and parallel safe. Store and maintain the result in a column, then index that column; they cannot be used directly in generated columns or expression indexes. The example fills `terms` explicitly; applications must also refresh it when the source text changes.

Positions start at 1 in the **final output sequence**, with default weight D. They are not source-text offsets: filters can remove or expand tokens, and models can emit subwords. Quotes, backslashes, whitespace, and punctuation inside lexemes are preserved. PostgreSQL's native limits still apply, including 256 positions per lexeme and a maximum position of 16,383.

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

Vocabulary triggers first look for tokens that are not yet in the vocabulary. Only rows that add tokens take a transaction-level advisory lock per model, recheck, and insert the new tokens in deduplicated, sorted order; rows whose tokens already exist do not wait. This prevents deadlocks caused by opposite token insertion orders across concurrent batches. At `READ COMMITTED`, the embedding trigger refreshes its snapshot after waiting so it includes token IDs committed by the preceding writer. At `REPEATABLE READ` or `SERIALIZABLE`, conflicts can return SQLSTATE `40001`; retry the whole transaction. Keep transactions short and use a consistent order when writing multiple models or locking application rows.

Table names are resolved as SQL identifiers, including schema qualification and quoted names. A qualified name takes precedence over a literal table name containing a dot. `drop_custom_model` also cleans up a model whose source table has already been dropped. See the [custom-model documentation](/docs/tokenizer/models/#custom-model-100).

## Definition caches, preloading, and database-owner access {#caches-and-permissions}

Successful `create_*` and `drop_*` calls clear the current backend's definition caches. A commit publishes an invalidation to other backends, which clear stale entries before their next lookup; a rollback, including an aborted subtransaction, only clears the current backend. Rebuilding an analyzer or model also invalidates tokenizers that held references to it. Lookups respect SQL snapshots: a definition loaded under an older snapshot is discarded before a later statement or transaction can reuse it. Parallel queries are supported. A transaction that changed definitions cannot be prepared with `PREPARE TRANSACTION`.

Cache invalidation does not rewrite persisted `INT[]`, `bm25vector`, or `tsvector` values. When intentionally replacing a definition, recompute affected search columns and rebuild indexes as required by the consumer. Manage definitions through the extension's APIs; direct catalog-table edits are not covered by these invalidation hooks.

Preloaded models are kept across cache invalidation. A non-built-in preload is reused only when the current database has the same model name and exact stored configuration. Preload entries that cannot be loaded are logged as WARNING and skipped instead of preventing PostgreSQL startup.

Installation and migration grant `pg_database_owner` access to `tokenizer_catalog`, its functions, tables, and sequences. A non-superuser database owner can manage its own analyzers, tokenizers, dictionaries, and custom models after an administrator installs the extension. The privileges follow database ownership changes. Vocabulary triggers call extension functions with exact `pg_catalog.text` argument types, so an overload created in `tokenizer_catalog` cannot capture those calls. The cluster-wide `add_preload_model` and `remove_preload_model` functions remain administrator-only. Other application roles still need explicit grants, and grants do not transfer ownership of existing model tables. See [database-owner permissions](/docs/tokenizer/installation/#database-owner-permissions).

An ordinary `pg_dump` now includes the analyzer, tokenizer, model, synonym, and user stopword definitions along with custom vocabulary tables. External Lindera dictionaries and the preload directory still need their own backup; see [logical backups](/docs/tokenizer/installation/#logical-backups).

## Upgrading from 0.1.x {#upgrade}

Install the matching 1.0.0 shared library and SQL files, keep `pg_tokenizer` in `shared_preload_libraries` alongside any other required libraries, and restart PostgreSQL. Then run the following in each database containing the extension as its owner or an administrator:

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '1.0.0';
SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
-- 1.0.0
```

Upgrade paths are included from 0.1.0 and 0.1.1. They preserve catalog data, existing custom-vocabulary IDs, and dependencies on the original six-argument helper. Review these changes before reusing stored search values:

- **`apply_text_analyzer` is `STABLE`:** analyzer definitions are catalog data. The upgrade refuses to run while an index, stored generated column, partition key, or extended statistics object depends on the function; replace such expressions with maintained columns first.
- **Lindera dictionary IDs:** the dependency moves from Lindera 0.42 to 6.2, and embedded IPADIC changes from the 2007-08-01 dictionary to the 2025-09-20 dictionary. User-dictionary IDs now start at `1073741824` instead of overlapping system IDs. Regenerate stored Lindera token arrays and ID-based vectors, and rebuild consuming indexes. Legacy dictionary configuration tables remain accepted, but external compiled dictionaries must be rebuilt with Lindera 6; remove preload entries that still point at old dictionaries before upgrading. See [Lindera migration notes](/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model).
- **Built-in stopwords are reserved:** `drop_stopwords` and `create_stopwords` refuse `lucene_english`, `nltk_english`, and `iso_english`, because `pg_dump` skips them and a restore recreates the shipped lists. If an earlier version replaced one of them, the upgrade prints a WARNING; copy that list to a new name and reference it from your analyzers.
- **NULL sources:** a matching custom-model row whose source is NULL now gets a NULL embedding; 0.1.x left the target column unchanged.

See the [compatibility notes](/docs/tokenizer/installation/#compatibility-100) for the complete list.

## Compatibility and packages {#compatibility}

The check and release workflows target PostgreSQL **14–18** on Linux **x86_64/aarch64**. Build with the matching `cargo-pgrx 0.19.3`. A `pg19` Cargo feature is present, but PostgreSQL 19 is outside this release's test and package matrix.

Native RPM/DEB recipes use version **`1.0.0-1PGSTY`** and do not embed Lindera dictionaries; supply a dictionary built with Lindera 6. Packages built by the GitHub release workflow enable `lindera-ipadic`, declare their shared-library dependencies, and are distinct from the native `1PGSTY` builds. ZIP archives carry no package-manager dependency metadata, so verify libc compatibility on the target host. Check actual package availability for your distribution, PostgreSQL major version, and architecture before upgrading. The release workflow does not generate or upload SBOM artifacts; see the [SBOM page](/docs/about/sbom/) for the dependency inventory.

Read the [installation and upgrade guide](/docs/tokenizer/installation/), [SQL reference](/docs/tokenizer/reference/), and [model documentation](/docs/tokenizer/models/) for configuration and operational details.
