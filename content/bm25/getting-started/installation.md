---
title: "Installation"
description: "Install VectorChord-BM25 (vchord_bm25) and pg_tokenizer via Pigsty, Docker, Debian packages, or source."
weight: 20
---

`vchord_bm25` supports **PostgreSQL 14, 15, 16, 17, and 18** on Linux (`x86_64` and `aarch64`) and macOS.

## Method 1: Pigsty / Native OS Packages (Recommended)

[**Pigsty**](https://pgsty.com) provides pre-built native RPM and DEB packages for `vchord`, `vchord_bm25`, and `pg_tokenizer` across EL 8/9/10, Debian 12/13, and Ubuntu 22.04/24.04 for PostgreSQL 14–18.

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

## Method 3: GitHub Release Packages (`.deb` & RHEL `.zip`)

Download prebuilt `.deb` or RHEL 9+ `.zip` packages for your PostgreSQL major version (`14`–`18`) and CPU architecture (`amd64` / `x86_64` or `arm64` / `aarch64`) from the GitHub Releases pages of [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) (upstream [`supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)) and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) (upstream [`supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs)):

### Debian / Ubuntu (`.deb`)

```bash
# Install vchord_bm25 (example for PostgreSQL 16 on x86_64)
curl -LO https://github.com/supervc-stack/VectorChord-bm25/releases/download/0.3.0/postgresql-16-vchord-bm25_0.3.0-1_amd64.deb
sudo apt-get install ./postgresql-16-vchord-bm25_0.3.0-1_amd64.deb

# Install pg_tokenizer (example for PostgreSQL 16 on x86_64)
curl -LO https://github.com/supervc-stack/pg_tokenizer.rs/releases/download/0.1.1/postgresql-16-pg-tokenizer_0.1.1-1_amd64.deb
sudo apt-get install ./postgresql-16-pg-tokenizer_0.1.1-1_amd64.deb
```

### RHEL 9+ / Enterprise Linux (`.zip` Archive)

For RHEL 9+ systems when installing manually from the release `.zip` archive (requires `glibc >= 2.34`):

```bash
# 1. Locate PostgreSQL library and extension directories
pg_config --pkglibdir
# Example: /usr/pgsql-16/lib
pg_config --sharedir
# Example: /usr/pgsql-16/share

# 2. Download and extract the release archive
wget https://github.com/supervc-stack/pg_tokenizer.rs/releases/download/0.1.1/pg16-pg_tokenizer-0.1.1-x86_64-unknown-linux-gnu.zip
unzip pg16-pg_tokenizer-0.1.1-x86_64-unknown-linux-gnu.zip

# 3. Copy the shared library (.so) and extension control/SQL files
sudo cp ./usr/lib/postgresql/16/lib/pg_tokenizer.so $(pg_config --pkglibdir)
sudo cp ./usr/share/postgresql/16/extension/* $(pg_config --sharedir)/extension
```

## Method 4: Build from Source (`cargo-pgrx`)

To compile [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) and [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) from source:

```bash
# 1. Install Rust toolchain and system dependencies (clang, libclang, pkg-config, PostgreSQL dev headers)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Build and install vchord_bm25
git clone https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
cargo install cargo-pgrx --version $(grep -o 'pgrx = "=[^"]*' Cargo.toml | cut -d = -f 3)
cargo pgrx init --pg17=$(which pg_config)
cargo pgrx install --release --pg-config $(which pg_config)

# 3. Build and install pg_tokenizer
git clone https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo pgrx install --release --pg-config $(which pg_config)
```

> [!TIP]
> **Optional Lindera Dictionaries at Compile Time**: To embed Lindera CJK morphological dictionaries (`ipadic`, `ipadic-neologd`, `unidic`, `ko-dic`, `cc-cedict`) directly into `pg_tokenizer.so`, pass the `--features` flag when compiling `pg_tokenizer`:
> ```bash
> cargo pgrx install --release --pg-config $(which pg_config) \
>   --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

### Development & Debugging (`cargo-pgrx`)

When developing or debugging `vchord_bm25` or `pg_tokenizer` locally:

```bash
# Initialize pgrx managed PostgreSQL instances (PG 14–18)
cargo pgrx init

# Use the `dev-opt` profile to enable optimizations alongside debug symbols
RUST_BACKTRACE=1 cargo pgrx run --profile dev-opt

# Inside the interactive psql session, inspect the backend PID to attach gdb if needed:
SELECT pg_backend_pid();
```

## Configure PostgreSQL & Enable Extensions

### 1. Shared Preload Libraries (Optional / Recommended for `pg_tokenizer`)

If you use `pg_tokenizer` and want preloaded vocabulary models initialized at server startup, add `pg_tokenizer` (and `vchord` if used) to `shared_preload_libraries` in `postgresql.conf`:

```ini
shared_preload_libraries = 'vchord.so, pg_tokenizer.so'
```

Restart PostgreSQL after modifying `shared_preload_libraries`. (`vchord_bm25` itself does not require `shared_preload_libraries` and can be loaded dynamically per session via `CREATE EXTENSION`.)

### 2. Create Extensions and Set `search_path`

Connect to your target database and enable the extensions:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
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
