---
title: "Installation"
linkTitle: "Installation"
description: "Install vchord_bm25 from Pigsty packages, GitHub release packages, or source, then preload it and create the extension."
weight: 20
icon: fa-solid fa-download
---

vchord_bm25 1.3.0 runs on PostgreSQL 15–19 on Linux `x86_64` and `aarch64`. Pick one way to install the files, then [enable the extension](#enable) the same way for all of them.

| Method | Use it when |
| --- | --- |
| [Pigsty packages](#pigsty) | You run EL 8/9/10, Debian 12/13, or Ubuntu 22.04/24.04 and want the PostgreSQL repository set up for you. |
| [Debian and Ubuntu packages](#debian) | You install PostgreSQL from PGDG (`apt.postgresql.org`) and prefer release files from GitHub. |
| [ZIP archives](#zip) | Another glibc-based Linux, or a custom PostgreSQL layout. |
| [Source](#source) | Another platform, or a PostgreSQL built with options the packages do not match. |

## Pigsty packages {#pigsty}

[`pig`](https://pigsty.io/ext/e/vchord_bm25/) adds the PostgreSQL and Pigsty repositories and installs the package for the PostgreSQL it finds:

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add vchord_bm25
```

With several PostgreSQL majors installed, name one: `pig ext add vchord_bm25 -v 18`. For Chinese, Japanese, or Korean text, also install `pg_tokenizer` the same way. The [download page](/download/) and the [PGEXT catalog](https://pgext.cloud/ext/vchord_bm25) list the packages and their versions.

## Debian and Ubuntu packages {#debian}

Each [GitHub release](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) has a `.deb` per PostgreSQL major and architecture (`amd64`, `arm64`). They are built on Ubuntu 22.04, need `libc6 >= 2.35`, and depend on the PGDG server package `postgresql-<major>`.

```bash
V=1.3.0; PG=18; ARCH=amd64
F=postgresql-${PG}-vchord-bm25_${V}-1_${ARCH}.deb
wget https://github.com/pgsty/vchord_bm25/releases/download/${V}/${F}{,.sha256}
sha256sum -c ${F}.sha256
sudo apt install ./${F}
```

## ZIP archives {#zip}

The same release has a `.zip` per PostgreSQL major and architecture (`x86_64`, `aarch64`). Each holds the shared library under `pkglibdir/` and the control and SQL files under `sharedir/extension/`. Copy them into the directories your `pg_config` reports:

```bash
V=1.3.0; PG=18; ARCH=x86_64
curl -fsSLO https://github.com/pgsty/vchord_bm25/releases/download/${V}/postgresql-${PG}-vchord-bm25_${V}_${ARCH}-linux-gnu.zip
unzip postgresql-${PG}-vchord-bm25_${V}_${ARCH}-linux-gnu.zip -d vchord_bm25
sudo install -m 755 vchord_bm25/pkglibdir/vchord_bm25.so "$(pg_config --pkglibdir)/"
sudo install -m 644 vchord_bm25/sharedir/extension/* "$(pg_config --sharedir)/extension/"
```

`install` writes a new file instead of overwriting the old one in place, which keeps a running server that has the library loaded from crashing. The archives are built against PGDG PostgreSQL on glibc 2.35; a PostgreSQL built with different options may need a [source build](#source).

## Build from source {#source}

You need PostgreSQL 15–19 development files (`pg_config`), GNU Make, Rust 1.100.0 or later, and Clang with libclang and LLVM tools of a matching version, on `x86_64` or `aarch64`.

```bash
git clone --branch 1.3.0 --depth 1 https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
PG_CONFIG=/path/to/pg_config make build
sudo make PG_CONFIG=/path/to/pg_config install
```

If several LLVM versions are installed, point `CLANG_PATH` and `LIBCLANG_PATH` at one. If your Clang loads a default configuration file, as Homebrew's does, set `CLANG_NO_DEFAULT_CONFIG=1`.

## Enable the extension {#enable}

1. Add `vchord_bm25` to `shared_preload_libraries`, keeping any libraries already there, and restart PostgreSQL. Without this, `CREATE EXTENSION` stops with `vchord_bm25 must be loaded via shared_preload_libraries.` With vchord and pg_tokenizer in the same server, list all three:

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord,vchord_bm25,pg_tokenizer';
   ```

1. Create the extension, as a superuser, in each database that needs it:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   ```

   The objects go into the current schema, usually `public`; `WITH SCHEMA` picks another. If that schema is not on the `search_path` of the roles that query, they must qualify the operator, the operator class, and the function: `OPERATOR(search.<&>)`, `search.bm25_ops`, `search.to_bm25query(...)`.

1. Check the version:

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

vchord_bm25 creates an index access method named `bm25`. Another extension with an access method of that name, such as ParadeDB's `pg_search`, cannot be installed in the same database: the second `CREATE EXTENSION` fails with `access method "bm25" already exists`.

Next, follow the [quick start](/docs/bm25/getting-started/overview/#quick-start) or go straight to [Indexing](/docs/bm25/usage/indexing/).

## Upgrade {#upgrade}

Install the new files, restart PostgreSQL, and run `ALTER EXTENSION vchord_bm25 UPDATE;` in each database. Indexes built by 1.0.0 or later keep working without a rebuild. Moving from PostgreSQL 14, downgrading, or migrating from the 0.x `bm25vector` API is covered in [Upgrade and migration](/docs/bm25/reference/migration/).

## Docker {#docker}

PGSTY does not publish container images. The `tensorchord/vchord-suite` images contain the 0.x `bm25vector` API, not the API documented here. To run the current release in a container, install the `.deb` package in your own image.
