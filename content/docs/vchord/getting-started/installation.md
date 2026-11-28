---
title: "Installation"
linkTitle: "Installation"
description: "Install vchord from Pigsty packages, GitHub release packages, or source, then preload it and create the extension."
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/installation.md"
aliases:
  - "/docs/getting-started/installation/"
  - "/vectorchord/getting-started/installation/"
icon: fa-solid fa-download
---

vchord 1.5.0 runs on PostgreSQL 15–19 on Linux `x86_64` and `aarch64`, and needs [pgvector](/docs/vector/) installed. Pick one way to install the files, then [enable the extension](#enable) the same way for all of them.

| Method | Use it when |
| --- | --- |
| [Pigsty packages](#pigsty) | You run EL 8/9/10, Debian 12/13, or Ubuntu 22.04/24.04. Handles pgvector and the PostgreSQL repository for you. |
| [Debian and Ubuntu packages](#debian) | You install PostgreSQL from PGDG (`apt.postgresql.org`) and prefer release files from GitHub. |
| [ZIP archives](#prebuilt-binaries) | Another glibc-based Linux, or a custom PostgreSQL layout. |
| [Source](#source) | Another platform, or you want to build for your own CPU. |

## Pigsty packages {#pigsty}

[`pig`](https://pigsty.io/ext/e/vchord/) adds the PostgreSQL and Pigsty repositories and installs vchord with pgvector for the PostgreSQL it finds:

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add vchord
```

With several PostgreSQL majors installed, name one: `pig ext add vchord -v 18`. The [download page](/download/) and the [PGEXT catalog](https://pgext.cloud/ext/vchord) list every package.

## Debian and Ubuntu packages {#debian}

<a id="Debian"></a><a id="Ubuntu"></a>

Each [GitHub release](https://github.com/pgsty/vchord/releases/tag/1.5.0) has a `.deb` per PostgreSQL major and architecture (`amd64`, `arm64`), built on Ubuntu 22.04, so they need `libc6 >= 2.35`.

1. Install PostgreSQL and pgvector from PGDG, replacing `18` with your major version:

   ```bash
   sudo apt install -y postgresql-18 postgresql-18-pgvector
   ```

1. Download, verify, and install the matching package:

   ```bash
   V=1.5.0; PG=18; ARCH=amd64
   F=postgresql-${PG}-vchord_${V}-1_${ARCH}.deb
   wget https://github.com/pgsty/vchord/releases/download/${V}/${F}{,.sha256}
   sha256sum -c ${F}.sha256
   sudo apt install ./${F}
   ```
{.steps}

## ZIP archives {#prebuilt-binaries}

The same release has a `.zip` per PostgreSQL major and architecture (`x86_64`, `aarch64`). Each holds the shared library under `pkglibdir/` and the control and SQL files under `sharedir/extension/`. Copy them into the directories your `pg_config` reports:

```bash
V=1.5.0; PG=18; ARCH=x86_64
curl -fsSLO https://github.com/pgsty/vchord/releases/download/${V}/postgresql-${PG}-vchord_${V}_${ARCH}-linux-gnu.zip
unzip postgresql-${PG}-vchord_${V}_${ARCH}-linux-gnu.zip -d vchord
sudo install -m 755 vchord/pkglibdir/vchord.so "$(pg_config --pkglibdir)/"
sudo install -m 644 vchord/sharedir/extension/* "$(pg_config --sharedir)/extension/"
```

The archives are built against PGDG PostgreSQL on glibc 2.35. A PostgreSQL built with different options may need a [source build](#source) instead.

## Build from source {#source}

You need PostgreSQL 15–19 development files (`pg_config`), pgvector, GNU Make, Rust 1.100.0 or later, and Clang with libclang and LLVM tools of a matching version, on `x86_64` or `aarch64`.

```bash
git clone --branch 1.5.0 --depth 1 https://github.com/pgsty/vchord.git
cd vchord
PG_CONFIG=/path/to/pg_config make build
sudo PG_CONFIG=/path/to/pg_config make install
```

If several LLVM versions are installed, point `CLANG_PATH` and `LIBCLANG_PATH` at one. If your Clang loads a default configuration file, as Homebrew's does, set `CLANG_NO_DEFAULT_CONFIG=1`.

<a id="Tuning"></a>

vchord picks SIMD kernels for the CPU at run time, so a default build is already fast on any machine. To also compile the rest of the code for your CPU, add `RUSTFLAGS="-C target-cpu=native"` to `make build`; the result crashes with `SIGILL` on older CPUs, so build it on the machine that runs it.

## Enable the extension {#enable}

1. Add `vchord` to `shared_preload_libraries`, keeping any libraries already there, and restart PostgreSQL. Without this, `CREATE EXTENSION` stops with `vchord must be loaded via shared_preload_libraries`.

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord';
   ```

1. Create the extension in each database that needs it. `CASCADE` also creates pgvector's `vector` extension.

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   ```

1. Check the version:

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

Next, follow the [quick start](/docs/vchord/getting-started/overview/#quick-start) or go straight to the [vchordrq index](/docs/vchord/usage/indexing/).

## Upgrade {#upgrade}

<a id="upgrading-to-130"></a><a id="upgrading-to-120"></a>

Install the new files, restart PostgreSQL, and run `ALTER EXTENSION vchord UPDATE;` in each database. Upgrading from 1.3.0 or earlier, or from PostgreSQL 14, needs a few more steps, described in [Upgrade and migration](/docs/vchord/admin/migration/).

## Docker {#docker}

<a id="docker-postgres"></a><a id="docker-suite"></a><a id="docker-scratch"></a><a id="PGXN"></a><a id="pgxn"></a>

PGSTY does not publish container images. The `tensorchord/vchord-*` images on GHCR contain older upstream releases. To run the current release in a container, install the `.deb` package in your own image, as shown for [Kubernetes](/docs/vchord/admin/kubernetes/).
