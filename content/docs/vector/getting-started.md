---
title: "Getting Started"
linkTitle: "Getting Started"
description: "Install pgvector 0.8.7 on PostgreSQL 14–18 and run your first vector similarity queries."
weight: 10
icon: fa-solid fa-rocket
upstream_link: https://github.com/pgvector/pgvector#installation
---

## Installation {#installation}

### Pigsty / Native Linux Packages (Recommended) {#pigsty}

[Pigsty](https://pigsty.io/ext/e/vector/) provides pre-built native `pgvector` packages (`v0.8.7`) for PostgreSQL 14–18 across Debian, Ubuntu, and RHEL/Rocky/AlmaLinux (`x86_64` and `aarch64`):

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig install pgvector
```

To install the complete Vchord retrieval suite (`pgvector` + [`vchord`](/docs/vchord/) + [`vchord_bm25`](/docs/bm25/) + [`pg_tokenizer`](/docs/tokenizer/)) in one command:

```bash
pig install pgvector vchord vchord_bm25 pg_tokenizer
```

### Docker {#docker}

Run the official `pgvector` container image:

```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

### Linux (PGDG APT / YUM) {#linux-pgdg}

- **Debian / Ubuntu** (via [PostgreSQL APT Repository](https://wiki.postgresql.org/wiki/Apt)):
  ```bash
  sudo apt install postgresql-18-pgvector
  ```
- **RHEL / Rocky / AlmaLinux / Fedora** (via [PostgreSQL YUM Repository](https://yum.postgresql.org/)):
  ```bash
  sudo dnf install pgvector_18
  ```

### macOS (Homebrew) {#macos}

```bash
brew install pgvector
```

### Build from Source (Linux / macOS) {#source}

Ensure PostgreSQL development headers (`postgresql-server-dev-*` or `postgresql*-devel`), `make`, and a C compiler are installed:

```bash
cd /tmp
git clone --branch v0.8.7 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

> [!TIP] Host-Specific SIMD Optimization
> By default, `pgvector`'s `Makefile` adds `-march=native` when supported by the compiler to maximize SIMD throughput on the build host. When building a portable binary for multiple CPU generations, pass `make OPTFLAGS=""`.

---

## Enable the Extension {#enable-the-extension}

Connect to your target database and enable `vector` (once per database):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Check the installed version:

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

### Upgrading `pgvector` {#upgrading-pgvector}

After installing a newer binary package on the server, update the SQL catalog definitions in each database:

```sql
ALTER EXTENSION vector UPDATE;
```

---

## Quick Start {#quick-start}

### 1. Create a Table with a `vector` Column {#create-table}

Create a table storing 3-dimensional single-precision (`float32`) vectors:

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(3)
);
```

Or add a `vector` column to an existing table:

```sql
ALTER TABLE items ADD COLUMN embedding vector(3);
```

### 2. Insert, Upsert, Update, and Delete Vectors {#dml}

Insert vectors using the text literal format `'[x1,x2,x3]'`:

```sql
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
```

Upsert vectors with `ON CONFLICT`:

```sql
INSERT INTO items (id, embedding) VALUES (1, '[1,2,3]'), (2, '[4,5,6]')
ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;
```

Update and delete rows with standard SQL:

```sql
UPDATE items SET embedding = '[1,2,3]' WHERE id = 1;
DELETE FROM items WHERE id = 1;
```

### 3. Bulk Loading with `COPY` {#bulk-loading}

For large datasets (millions of vectors), prefer binary `COPY` over row-by-row `INSERT`:

```sql
COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);
```

### 4. Query Nearest Neighbors {#query-nearest-neighbors}

Find the 5 closest vectors by L2 (Euclidean) distance:

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

Next, read [Querying & Filtering](/docs/vector/querying/) for all six distance metrics and filtering patterns, or [HNSW & IVFFlat Indexing](/docs/vector/indexing/) to accelerate queries over large tables.
