---
title: "Installation"
description: "Install pg_tokenizer via Pigsty native Linux packages, Docker, Debian/ZIP archives, or cargo-pgrx."
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/tensorchord/pg_tokenizer.rs/blob/main/docs/01-installation.md"
---

## Linux Packages via `pig` (Recommended)

On EL 8/9/10, Debian 12/13, and Ubuntu 22.04/24.04 (PostgreSQL 14–18), you can install pre-built native packages from the [Pigsty repository](https://pigsty.io/ext/e/pg_tokenizer) (see package matrix on [pgext.cloud](https://pgext.cloud/ext/pg_tokenizer)):

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
```

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

When installing via native packages or archives, add `pg_tokenizer.so` to `shared_preload_libraries` (required for model preloading) and include `tokenizer_catalog` in `search_path`:

```bash
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "pg_tokenizer.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, tokenizer_catalog'
sudo systemctl restart postgresql.service
```

Then enable the extension in your target database:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## From Debian Package or ZIP Archive

Pre-built `.deb` and `.zip` release archives (`GLIBC >= 2.35`, `x86_64` and `aarch64`) are available on the [`pgsty/pg_tokenizer` Releases page](https://github.com/pgsty/pg_tokenizer/releases/latest):

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

## Upgrading to 0.1.2

The 0.1.2 source changes are not yet a published release. After installing the matching library and SQL files, restart PostgreSQL to load the new preloaded library, then update each database as the extension owner/administrator:

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '0.1.2';
```

Both 0.1.0 and 0.1.1 have upgrade paths. The upgrade replaces trigger/helper definitions and grants catalog access without rebuilding custom vocabularies or changing existing token IDs. Six-argument helper dependencies remain valid. Standard `cargo pgrx install/package` and `tools/package.sh` include the migration scripts. Lindera's separate dictionary-ID migration still requires re-tokenization as described in the [model notes](/docs/tokenizer/models/).

### Database-owner permissions

Installation and upgrade grant `pg_database_owner` USAGE/CREATE on `tokenizer_catalog`, EXECUTE on its functions, SELECT/INSERT/UPDATE/DELETE on catalog and model tables, and USAGE/SELECT on their sequences. Future objects created in that schema by the installing role receive the same table/sequence/function defaults; newly created custom models also explicitly grant access. The grants follow a database ownership change.

A non-superuser database owner can create/drop its own custom models, analyzers, tokenizers, stopwords, and synonyms after an administrator installs the extension. Grants do not transfer table ownership: dropping a model created by a different role still needs that object's owner or an administrator. Other application roles require explicit grants; the extension does not give PUBLIC schema access or catalog write privileges. Functions continue to execute with the caller's privileges.
