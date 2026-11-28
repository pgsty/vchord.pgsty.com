---
title: "Installation"
linkTitle: "Installation"
description: "Install pg_tokenizer from Pigsty packages, GitHub release packages or source, preload it, create the extension, and upgrade in place."
weight: 20
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
icon: fa-solid fa-download
---

pg_tokenizer 1.3.0 runs on PostgreSQL 15–19 on Linux `x86_64` and `aarch64` and depends on no other extension. For BM25 ranking, also install [vchord_bm25](/docs/bm25/). Pick one way to install the files, then [enable the extension](#enable) the same way for all of them.

<a id="supported-versions"></a>

| Method | Use it when | Japanese IPADIC dictionary |
| --- | --- | --- |
| [Pigsty packages](#pigsty) | You run EL 8/9/10, Debian 12/13, or Ubuntu 22.04/24.04. | Not included; supply [an external dictionary](/docs/tokenizer/models/#lindera) |
| [Debian and Ubuntu packages](#debian) | You run Ubuntu 24.04+ or Debian 13+ with PostgreSQL from PGDG. | Built in |
| [ZIP archives](#zip) | Another Linux with glibc 2.39 or later. | Built in |
| [Source](#source) | Older or other distributions, or you want other built-in Lindera dictionaries. | Built in by default |

## Pigsty packages {#pigsty}

<a id="linux-packages-via-pig"></a>

[`pig`](https://pigsty.io/ext/e/pg_tokenizer) adds the PostgreSQL and Pigsty repositories and installs the package for the PostgreSQL it finds:

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
pig ext add vchord_bm25    # for BM25 ranking
```

With several PostgreSQL majors installed, name one: `pig ext add pg_tokenizer -v 18`. The [PGEXT catalog](https://pgext.cloud/ext/pg_tokenizer) lists every package.

These packages leave out the Lindera dictionaries to stay small. Everything except Japanese and Korean segmentation works as is; for those, point the Lindera model at a dictionary directory on the server, as described in [Models](/docs/tokenizer/models/#lindera).

## Debian and Ubuntu packages {#debian}

<a id="from-debian-package-or-zip-archive"></a>

Each [GitHub release](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) has a `.deb` per PostgreSQL major and architecture (`amd64`, `arm64`). They are built on Ubuntu 24.04, so they need glibc 2.39 or later: Ubuntu 24.04+ or Debian 13+. On older systems, use Pigsty packages or build from source.

```bash
V=1.3.0; PG=18; ARCH=amd64
F=postgresql-${PG}-pg-tokenizer_${V}-1_${ARCH}.deb
wget https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/${F} \
     https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/SHA256SUMS
sha256sum --ignore-missing -c SHA256SUMS
sudo apt install ./${F}
```

> [!IMPORTANT]
> A release binary can require a recent PostgreSQL minor release: at least 15.20, 16.16, 17.12 or 18.7 on those majors. On an older server the library does not load, and PostgreSQL does not start while it is in `shared_preload_libraries`. The `.deb` declares the requirement as a package dependency; for a ZIP, read the last line of `pg_tokenizer.control`. Update the server first, or build from source against it.

## ZIP archives {#zip}

The same release has a `.zip` per PostgreSQL major and architecture (`x86_64`, `aarch64`) with the same glibc requirement. It holds the library, the control file and the SQL scripts in one directory:

```bash
V=1.3.0; PG=18; ARCH=x86_64
F=postgresql-${PG}-pg-tokenizer_${V}_${ARCH}-linux-gnu.zip
curl -fsSLO https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/${F}
unzip ${F} -d pg_tokenizer
tail -n 1 pg_tokenizer/pg_tokenizer.control    # minimum PostgreSQL version
sudo install -m 755 pg_tokenizer/pg_tokenizer.so "$(pg_config --pkglibdir)/"
sudo install -m 644 pg_tokenizer/pg_tokenizer--*.sql pg_tokenizer/pg_tokenizer.control \
     "$(pg_config --sharedir)/extension/"
```

Use `install` rather than `cp`: it replaces the library file instead of overwriting it, so a running server keeps using the old copy until you restart it.

## Build from source {#source}

<a id="from-source"></a>

You need PostgreSQL 15–19 development files (`pg_config`), Rust 1.99.1 or later, Python 3.11+, GNU Make, and Clang with libclang and LLVM tools of a matching version.

```bash
git clone --branch v1.3.0 --depth 1 https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo install cargo-pgrx --version 0.20.0 --locked
PG_CONFIG=/path/to/pg_config make build
sudo make PG_CONFIG=/path/to/pg_config install
```

The build embeds the Japanese IPADIC dictionary. To embed others, list them in `FEATURES`, for example `make build FEATURES="lindera-ipadic lindera-ko-dic"`; the choices are `lindera-ipadic`, `lindera-ipadic-neologd`, `lindera-unidic`, `lindera-ko-dic` (Korean) and `lindera-cc-cedict`. If several LLVM versions are installed, point `CLANG_PATH` and `LIBCLANG_PATH` at one; if your Clang loads a default configuration file, set `CLANG_NO_DEFAULT_CONFIG=1`.

## Enable the extension {#enable}

<a id="configuration"></a>

1. Add `pg_tokenizer` to `shared_preload_libraries`, keeping any libraries already there, and restart PostgreSQL. The order of the list does not matter. Without this step, `CREATE EXTENSION` stops with `pg_tokenizer must be loaded via shared_preload_libraries.`

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'pg_tokenizer, vchord_bm25';
   ```

1. Create the extension in each database that needs it:

   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
   ```

   This creates two schemas: `tokenizer_catalog`, which holds the functions and the tables of definitions, and `tokenizer_data`, which holds the vocabularies of custom models.

1. Optionally, put `tokenizer_catalog` on the database's search path so you can call the functions without the schema prefix. The examples in these docs use the prefix and work either way.

   ```sql
   ALTER DATABASE app SET search_path = "$user", public, tokenizer_catalog;
   ```

1. Check the version:

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

Next, follow the [quick start](/docs/tokenizer/overview/#quick-start) or pick a [recipe](/docs/tokenizer/multilingual/).

## Roles and privileges {#database-owner-permissions}

The database owner can create and drop definitions without being a superuser: the extension grants the `pg_database_owner` role what it needs. Other roles need grants:

- To analyze or tokenize text, including through a trigger that fires on its inserts, a role needs read access to the definitions. Without it, the call fails with `permission denied for schema tokenizer_catalog`.

  ```sql
  GRANT USAGE ON SCHEMA tokenizer_catalog TO app;
  GRANT SELECT ON ALL TABLES IN SCHEMA tokenizer_catalog TO app;
  ```

- To insert into a table with a [custom model](/docs/tokenizer/models/#custom), a role also needs `USAGE` on the schema `tokenizer_data` and `SELECT` and `INSERT` on the model's vocabulary table.
- The preload list applies to the whole server, so only superusers can change it with `add_preload_model` and `remove_preload_model`, unless you `GRANT EXECUTE` on those functions.
- Loading a Lindera dictionary from a file on the server requires superuser or membership in `pg_read_server_files`; see [Models](/docs/tokenizer/models/#lindera).

## Upgrade {#upgrading}

<a id="upgrade-120"></a><a id="upgrade-110"></a><a id="compatibility-100"></a>

From 1.2.0, install the new files on the primary and every replica, restart PostgreSQL on each node, and run this in each database on the primary:

```sql
ALTER EXTENSION pg_tokenizer UPDATE;
```

Definitions, custom vocabularies and their IDs, and the triggers on your tables are kept, and no stored values need recomputing. Until you run the update, the new library keeps working with the 1.2.0 SQL definitions.

`ALTER EXTENSION pg_tokenizer UPDATE` walks the whole chain from any earlier release. Starting further back, also do the steps for every release you pass:

| Upgrading from | Before or after the update |
| --- | --- |
| 1.1.0 | Move PostgreSQL 14 clusters to 15 or later first. If a model uses an external Lindera dictionary, replace it on every node, while PostgreSQL is stopped, with one built by Lindera 7 (format v3). Lindera 7, a regular-expression fix and newer Unicode tables can change the tokens for some text: compare document and query tokens before and after, and recompute stored values where they differ. |
| 1.0.0 | Run the update under `READ COMMITTED`: `BEGIN ISOLATION LEVEL READ COMMITTED; ALTER EXTENSION pg_tokenizer UPDATE; COMMIT;`. First schema-qualify `pg_dict` names that exist in more than one schema, and make sure no unrelated schema named `tokenizer_data` exists; if custom models belong to several roles, run the update as a superuser. Vocabulary tables move from `tokenizer_catalog` to `tokenizer_data`; update SQL that reads them directly. Jieba's `full` and `precise` modes were swapped before; recompute values made with either. |
| 0.1.x | Drop expression indexes, generated columns, partition keys and statistics that use `apply_text_analyzer` first; it is no longer `IMMUTABLE`. Recompute stored Lindera token IDs. The names `lucene_english`, `nltk_english` and `iso_english` are reserved for the built-in stopword lists. |
{.wide}

The release notes for [1.3.0](/release/pg-tokenizer-1.3.0/), [1.2.0](/release/pg-tokenizer-1.2.0/), [1.1.0](/release/pg-tokenizer-1.1.0/) and [1.0.0](/release/pg-tokenizer-1.0.0/) list every change. Indexes that still store `bm25vector` values from vchord_bm25 0.x need the [BM25 migration](/docs/bm25/reference/migration/).

## Replicas and backups {#logical-backups}

Definitions and custom vocabularies are ordinary tables: they replicate to standbys and `pg_dump` includes them. Two things live outside the database and need handling on every node:

- The preload list in `$PGDATA/pg_tokenizer/preload_models`. Each server reads its own copy at startup. A standby starts with the copy it was cloned with; copy later changes to each node yourself, and back the directory up separately.
- External Lindera dictionary directories. Install the same build at the same path on every node.

Install the same pg_tokenizer version on all nodes, so that a query analyzed on a standby produces the same tokens as the documents written on the primary.
