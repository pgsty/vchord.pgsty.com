---
title: "Installation"
description: "Install VectorChord-BM25 (vchord_bm25) and pg_tokenizer via Pigsty, Docker, Debian packages, or source."
weight: 20
icon: fa-solid fa-download
---

> [!IMPORTANT]
> **1.1.0** is the current PGSTY release. It keeps the native `tsvector` API and format 4 introduced in 1.0.0, so healthy 1.0.0 indexes can be upgraded in place without a rebuild. Examples labeled 0.3.x use the historical `bm25vector` API and still require the [migration guide](/docs/bm25/reference/migration/) before changing binaries.


`vchord_bm25` supports **PostgreSQL 14, 15, 16, 17, and 18** on Linux (`x86_64` and `aarch64`) and macOS.

## Method 1: Pigsty / Native OS Packages (Recommended)

[**Pigsty**](https://pgsty.com) provides pre-built native RPM and DEB packages for `vchord`, `vchord_bm25`, and `pg_tokenizer` across EL 8/9/10, Debian 12/13, and Ubuntu 22.04/24.04/26.04 for PostgreSQL 14–18. Choose the package built for the target distribution, PostgreSQL major version, and CPU architecture.

```bash
# Install via Pigsty CLI (automatically resolves PG version and OS distro)
pig ext install vchord_bm25
pig ext install pg_tokenizer
```

Or install directly via `apt` / `dnf` once the Pigsty repository is configured:

```bash
# Debian / Ubuntu (replace 17 with your PostgreSQL major version)
sudo apt-get install postgresql-17-vchord-bm25 postgresql-17-pg-tokenizer

# RHEL / Rocky / AlmaLinux (replace 17 with your PostgreSQL major version)
sudo dnf install vchord_bm25_17 pg_tokenizer_17
```

## Method 2: Docker (`tensorchord/vchord-suite`)

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for its maintained releases. These upstream instructions are retained for reference and will be updated.

The official `tensorchord/vchord-suite` Docker image bundles **PostgreSQL**, **VectorChord (`vchord`)**, **VectorChord-BM25 (`vchord_bm25`)**, and **`pg_tokenizer`** out of the box:

```bash
docker run \\
  --name vchord-suite \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  -d tensorchord/vchord-suite:pg18-latest
```

> [!NOTE]
> You can also pull from GitHub Container Registry using `ghcr.io/tensorchord/vchord-suite:pg18-latest` (or `pg17-latest`, `pg16-latest`, `pg15-latest`, `pg14-latest`).

Connect with `psql`:

```bash
psql -h localhost -p 5432 -U postgres
```

## Method 3: GitHub Release Packages (`.deb` and `.zip`)

Download release archives for your PostgreSQL major version (`14`–`18`) and CPU architecture (`amd64` / `x86_64` or `arm64` / `aarch64`) from the GitHub Releases pages of [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer). Select a `.deb` built for the exact Debian/Ubuntu release. ZIP archives have no package-manager dependency metadata and require a libc compatibility check on the target host; for supported EL systems, use the matching RPM package.

### Debian / Ubuntu (`.deb`)

```bash
# Install vchord_bm25 (example for PostgreSQL 16 on x86_64)
curl -LO https://github.com/pgsty/vchord_bm25/releases/download/1.1.0/postgresql-16-vchord-bm25_1.1.0-1_amd64.deb
sudo apt-get install ./postgresql-16-vchord-bm25_1.1.0-1_amd64.deb

# Install pg_tokenizer 1.0.0 (example for PostgreSQL 16 on x86_64)
curl -LO https://github.com/pgsty/pg_tokenizer/releases/download/v1.0.0/postgresql-16-pg-tokenizer_1.0.0-1_amd64.deb
sudo apt-get install ./postgresql-16-pg-tokenizer_1.0.0-1_amd64.deb
```

### Manual ZIP installation

If a matching native package is unavailable, install the ZIP archive manually after verifying the PostgreSQL major version, CPU architecture, and target system libc:

```bash
# 1. Locate PostgreSQL library and extension directories
pg_config --pkglibdir
# Example: /usr/pgsql-16/lib
pg_config --sharedir
# Example: /usr/pgsql-16/share

# 2. Download and extract the release archive
wget https://github.com/pgsty/pg_tokenizer/releases/download/v1.0.0/postgresql-16-pg-tokenizer_1.0.0_x86_64-linux-gnu.zip
unzip postgresql-16-pg-tokenizer_1.0.0_x86_64-linux-gnu.zip -d pg_tokenizer

# 3. Install the shared library (.so) and extension control/SQL files
sudo install -m 755 pg_tokenizer/pg_tokenizer.so "$(pg_config --pkglibdir)/"
sudo install -m 644 pg_tokenizer/pg_tokenizer--*.sql pg_tokenizer/pg_tokenizer.control "$(pg_config --sharedir)/extension/"
```

Use `install` to replace the library without truncating a file that PostgreSQL may already have loaded. Restart PostgreSQL afterward to load the installed library.

## Method 4: Build from Source {#method-4-build-from-source-cargo-pgrx}

To compile [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) from source:

```bash
# 1. Install Rust toolchain and system dependencies (clang, libclang, pkg-config, PostgreSQL dev headers)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Build and install vchord_bm25
git clone https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
PG_CONFIG=/path/to/pg_config make build
PG_CONFIG=/path/to/pg_config make install
```

> [!TIP]
> **Optional Lindera Dictionaries at Compile Time**: To embed Lindera CJK morphological dictionaries (`ipadic`, `ipadic-neologd`, `unidic`, `ko-dic`, `cc-cedict`) directly into `pg_tokenizer.so`, pass the `--features` flag when compiling `pg_tokenizer`:
> ```bash
> cargo pgrx install --release --pg-config $(which pg_config) \
>   --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

### Development & Debugging {#development--debugging-cargo-pgrx}

Use the `dev` profile for an optimized BM25 build with debug symbols:

```bash
PG_CONFIG=/path/to/pg_config PROFILE=dev make build
PG_CONFIG=/path/to/pg_config PROFILE=dev make install
```

Restart a disposable PostgreSQL instance configured to preload `vchord_bm25`, then connect with `psql`. To attach a debugger, obtain that session's backend PID:

```sql
SELECT pg_backend_pid();
```

## Configure PostgreSQL & Enable Extensions

### 1. Shared Preload Libraries (Required for 1.1.0) {#1-shared-preload-libraries-optional--recommended-for-pg_tokenizer}

1.1.0 requires `vchord_bm25` in `shared_preload_libraries`. Preserve other required libraries. `pg_tokenizer` is optional for the native `to_tsvector` workflow; if you install it for custom tokenization, add it to the same setting before PostgreSQL starts:

```ini
shared_preload_libraries = 'vchord_bm25'
# If using pg_tokenizer 1.0.0 for custom tokenization:
# shared_preload_libraries = 'vchord_bm25, pg_tokenizer'
```

Restart PostgreSQL after modifying `shared_preload_libraries`.

### 2. Create Extensions and Set `search_path`

Connect to your target database and enable the extensions:

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25;
-- pg_tokenizer is a separate extension for the historical bm25vector workflow.
```

In `v0.1.0`–`v0.3.0`, `vchord_bm25` installs its objects into the `bm25_catalog` schema and `pg_tokenizer` installs into `tokenizer_catalog`. Add both schemas to your `search_path`:

```sql
-- Per-session
SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;

-- Or persist for your database / role
ALTER DATABASE postgres SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;
```

Verify the installed version:

```sql
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vchord_bm25', 'pg_tokenizer');
```
