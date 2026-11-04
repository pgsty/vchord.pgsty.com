---
title: "Installation"
description: "Install pg_tokenizer via Pigsty native Linux packages, Docker, Debian/ZIP archives, or cargo-pgrx."
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
---

## Linux Packages via `pig` (Recommended)

On EL 8/9/10, Debian 12/13, and Ubuntu 22.04/24.04/26.04 (PostgreSQL 14–18), you can install the native package built for your distribution and architecture from the [Pigsty repository](https://pigsty.io/ext/e/pg_tokenizer) (see the package matrix on [pgext.cloud](https://pgext.cloud/ext/pg_tokenizer)):

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
```

Native RPM/DEB packages do not embed Lindera dictionaries; supply external dictionaries compiled with Lindera 6. GitHub release `.deb`/ZIP packages enable `lindera-ipadic`. Other embedded dictionaries are optional build features.

## Docker (`vchord-suite`)

The [`tensorchord/vchord-suite`](/docs/vchord/getting-started/vectorchord-suite/) Docker image comes pre-configured with the Vchord extension suite:
- [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) — Standalone multilingual tokenizer (`pgsty/pg_tokenizer`)
- [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) — Native BM25 ranking index (`pgsty/vchord_bm25`)
- [`vchord`](https://github.com/pgsty/vchord) — Scalable, disk-friendly vector search (`pgsty/vchord`)
- [`pgvector`](/docs/vector/) — Standard PostgreSQL vector data types

```bash
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
```

Connect with `psql` and enable the extension:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## Configuration (`shared_preload_libraries` & `search_path`)

`pg_tokenizer` has no required PostgreSQL extension dependency. `vchord_bm25` is optional: its 0.3.x API consumes `INT[]` values through `bm25vector`, while its 0.4.0/main API can consume native `tsvector` values. The `pg_tokenizer` library must be loaded through `shared_preload_libraries` before PostgreSQL starts; include `tokenizer_catalog` in `search_path` if you want to call the functions without schema qualification:

```bash
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'pg_tokenizer.so';"
psql -U postgres -c "ALTER SYSTEM SET search_path TO \"\$user\", public, tokenizer_catalog;"
sudo systemctl restart postgresql.service
```

Then enable the extension in your target database:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## From Debian Package or ZIP Archive

Pre-built `.deb` and `.zip` release archives for selected PostgreSQL major versions and `x86_64`/`aarch64` architectures are available on the [`pgsty/pg_tokenizer` Releases page](https://github.com/pgsty/pg_tokenizer/releases/latest). Select a `.deb` matching the exact target Debian/Ubuntu release, PostgreSQL major version, and architecture. ZIP archives have no package-manager dependency metadata, so verify their shared-library compatibility with the target system's libc before installing; use a matching native package when one is available.

```bash
# Debian / Ubuntu
sudo apt install ./postgresql-17-pg-tokenizer_*.deb
```

## From Source (`cargo-pgrx`)

```bash
git clone https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo pgrx install --sudo --release
```

## Upgrading to 1.0.0 {#upgrade-100}

After installing the 1.0.0 library and SQL files, restart PostgreSQL to load the new preloaded library, then update each database as the extension owner or an administrator:

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '1.0.0';
```

The upgrade path is available from 0.1.0 and 0.1.1. It preserves catalog data, existing custom-model token IDs, and dependencies on the six-argument helper (including its function OID). Standard `cargo pgrx install/package` and `tools/package.sh` include the migration scripts. After the new library is loaded, committed definition changes invalidate backend-local caches; each lookup respects its SQL snapshot, and objects loaded from an older snapshot are discarded before a later statement or transaction reuses them. Lindera's dictionary-ID migration requires re-tokenization as described in the [model notes](/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model).

### Database-owner permissions {#database-owner-permissions}

Installation and upgrade grant `pg_database_owner` USAGE/CREATE on `tokenizer_catalog`, EXECUTE on its database-local functions, SELECT/INSERT/UPDATE/DELETE on catalog and model tables, and USAGE/SELECT on their sequences. Future objects created in that schema by the installing role receive the same table/sequence/function defaults; newly created custom models also explicitly grant access. The grants follow a database ownership change.

A non-superuser database owner can create/drop its own custom models, analyzers, tokenizers, stopwords, and synonyms after an administrator installs the extension. Grants do not transfer table ownership: dropping a model created by a different role still needs that object's owner or an administrator. Other application roles require explicit grants; the extension does not give PUBLIC schema access or catalog write privileges. Functions continue to execute with the caller's privileges.

The cluster-wide `add_preload_model` and `remove_preload_model` functions are restricted to the extension owner and explicitly authorized administrators. `PUBLIC` and `pg_database_owner` have no EXECUTE grant on these two functions. Changes to preload files are not transactional and take effect on restart. Broken preload entries generate WARNING messages and are skipped instead of preventing startup; repair or remove the entry before expecting that model to be preloaded.

### Compatibility changes in 1.0.0 {#compatibility-100}

- `apply_text_analyzer` is now `STABLE`, like `tokenize`: analyzer definitions are catalog data, so `IMMUTABLE` was incorrect and allowed cached plans to bypass invalidation. The upgrade refuses to run while an index, stored generated column, partition key, or extended statistics object depends on it. Replace such expressions with ordinary columns maintained by the application or a trigger, index those columns, then upgrade.
- Lindera moves from 0.42 to 6.2. The embedded IPADIC dictionary changes from the 2007-08-01 edition to the 2025-09-20 edition, so its token IDs change; external compiled dictionaries must be rebuilt with Lindera 6. User-dictionary IDs now use `1073741824 + dictionary-local ID` instead of overlapping system-dictionary IDs. Regenerate stored Lindera token arrays and rebuild their indexes.
- A matching custom-model row with a NULL source now gets a NULL embedding, including a value supplied explicitly by the INSERT; 0.1.x left the target column unchanged. Nonmatching filtered rows retain their embedding.
- Vocabulary writers that add tokens to a custom model serialize on a per-model advisory lock until commit; writers whose tokens already exist do not wait. `REPEATABLE READ` and `SERIALIZABLE` writers can receive SQLSTATE `40001` and must retry.
- `PREPARE TRANSACTION` is rejected after calling a definition-changing API. Read-only use can be prepared.
- `add_preload_model` and `remove_preload_model` are restricted to administrators, and broken preload entries are skipped with a WARNING. Before upgrading, remove preload entries for Lindera models that use external dictionaries not yet rebuilt with Lindera 6.
- The built-in `lucene_english`, `nltk_english`, and `iso_english` stopword lists are reserved: `drop_stopwords` and `create_stopwords` refuse these names. If an earlier version replaced one of them, the upgrade prints a WARNING; copy the list to a new name and reference that name instead.
- `pg_dump` now includes the definition tables; see [logical backups](#logical-backups).

### Logical backups {#logical-backups}

The five definition tables (`text_analyzer`, `tokenizer`, `model`, `stopwords`, `synonym`) are registered with `pg_extension_config_dump`, so an ordinary `pg_dump` includes their rows together with custom vocabulary tables, their identity sequences, and source-table triggers. `CREATE EXTENSION` recreates the shipped `lucene_english`, `nltk_english`, and `iso_english` stopword lists, so those three names are not dumped. They are reserved and cannot be dropped or replaced, so a restore recreates the same lists.

External Lindera dictionaries and the cluster's `pg_tokenizer/preload_models` directory are outside the database and need their own backup. A physical PostgreSQL backup includes the catalog rows and the preload directory, but not external dictionary paths.
