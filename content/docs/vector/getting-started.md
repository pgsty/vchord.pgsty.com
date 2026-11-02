---
title: "Getting Started"
linkTitle: "Getting Started"
description: "Install pgvector on PostgreSQL 14–18 and run your first vector similarity queries."
weight: 10
upstream_link: https://github.com/pgvector/pgvector#installation
---

## Installation

### Pigsty / Native Linux Packages (Recommended)

[Pigsty](https://pigsty.io/ext/e/pgvector) provides prebuilt native `pgvector` packages (`v0.8.2`) for PostgreSQL 14–18 across Debian, Ubuntu, and RHEL/Rocky/AlmaLinux (x86_64 and ARM64):

```bash
pig repo add pgdg pigsty -u
pig ext install pgvector
```

If you also want disk-friendly RaBitQ vector indexes and BM25 ranking, install the full Vchord suite together:

```bash
pig ext install pgvector vchord vchord_bm25 pg_tokenizer
```

### Docker

Run the official `pgvector` container image:

```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

Or use the all-in-one Vchord Suite image, which bundles `pgvector`, [`vchord`](/docs/vchord/), [`vchord_bm25`](/docs/bm25/), and [`pg_tokenizer`](/docs/tokenizer/):

```bash
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

### Linux (PGDG APT / YUM)

- **Debian / Ubuntu** (via [PostgreSQL APT Repository](https://wiki.postgresql.org/wiki/Apt)):
  ```bash
  sudo apt install postgresql-18-pgvector
  ```
- **RHEL / Rocky / AlmaLinux / Fedora** (via [PostgreSQL YUM Repository](https://yum.postgresql.org/)):
  ```bash
  sudo dnf install pgvector_18
  ```

### macOS (Homebrew)

```bash
brew install pgvector
```

### Build from Source (Linux / macOS)

Ensure PostgreSQL development headers (`postgresql-server-dev-*` or `postgresql*-devel`), `make`, and a C compiler are installed:

```bash
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

> [!TIP] Host-Specific SIMD Optimization
> To compile with `-march=native` for maximum SIMD performance on the current machine, pass `OPTFLAGS=""` only if needed for portability; by default `pgvector`'s `Makefile` adds `-march=native` when supported by the compiler. If building a portable binary for multiple CPU generations, run `make OPTFLAGS=""`.

---

## Enable the Extension

Connect to your target database and enable `vector` (this must be done once per database where you want to use it):

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Check the installed version:

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

### Upgrading `pgvector`

After installing a newer binary package on the server, upgrade the SQL catalog definitions inside each database:

```sql
ALTER EXTENSION vector UPDATE;
```

---

## Quick Start

### 1. Create a Table with a `vector` Column

Create a table storing 3-dimensional single-precision (`float32`) vectors:

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(3)
);
```

You can also add a `vector` column to an existing table:

```sql
ALTER TABLE items ADD COLUMN embedding vector(3);
```

### 2. Insert, Upsert, Update, and Delete Vectors

Insert vectors using the string literal format `'[x1,x2,x3]'`:

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

### 3. Bulk Loading with `COPY`

For large datasets (millions of vectors), always prefer `COPY` over row-by-row `INSERT`:

```sql
COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);
```

### 4. Query Nearest Neighbors

Find the 5 closest vectors by L2 (Euclidean) distance:

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

Next, read [Querying & Filtering](/docs/vector/querying/) for all distance metrics and filtering patterns, or [HNSW & IVFFlat Indexing](/docs/vector/indexing/) to accelerate queries over large tables.
