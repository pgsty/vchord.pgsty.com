---
title: Download & Install
linkTitle: Download
description: Install vchord, vchord_bm25, and pg_tokenizer using the pig package manager, historical Docker containers (Obsolete), or native RPM/DEB packages across 16 Linux distributions and PostgreSQL 14–18.
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

Pre-built native RPM and DEB packages for the Vchord extension suite (**`vchord`**, **`vchord_bm25`**, and **`pg_tokenizer`**) are published across **16 Linux OS / CPU architecture targets** (`el8`, `el9`, `el10`, `d12`, `d13`, `u22`, `u24`, `u26` × `x86_64` / `aarch64`) for **PostgreSQL 14, 15, 16, 17, and 18** (240 binary packages in total).

{{< cards >}}
{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v1.2.0" >}}
Scalable, fast, and disk-friendly vector similarity search extension built on `pgvector`, providing RaBitQ-compressed `vchordrq` (IVF) and `vchordg` (graph) indexes, multi-vector MaxSim (`@#`), and sphere search across PostgreSQL 14–18.
{{< /card >}}
{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v1.0.0" >}}
Native Okapi BM25 full-text ranking index extension powered by Block-WeakAnd block-level WAND pruning and the `<&>` operator, delivering high-throughput lexical Top-K retrieval and hybrid search across PostgreSQL 14–18.
{{< /card >}}
{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v1.0.0" >}}
Standalone in-database multilingual text analyzer and token-ID encoder supporting Unicode segmentation, Jieba (Chinese), Lindera (Japanese), Snowball stemming, HuggingFace vocabularies, and corpus-trained custom models across PostgreSQL 14–18.
{{< /card >}}
{{< /cards >}}

---

## Quick Installation {#install}

### 1 · Install with PIG Package Manager (Recommended) {#pig}

We strongly recommend installing the Vchord extension suite with [**`pig`**](https://pig.pgsty.com/) — the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` is a single static Go binary that automatically detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and resolves extension dependencies (`pgvector`) in one command.

{{< tabs >}}
{{< tab label="Global (Default)" >}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update repo cache
pig repo add pgsql -u

# 3. Install vchord, vchord_bm25, and pg_tokenizer (auto-detects active PG version, or pass -v 18)
pig install vchord vchord_bm25 pg_tokenizer
```

{{< /tab >}}
{{< tab label="Mainland China Mirror" >}}

```bash
# 1. Install the pig CLI via the mainland China mirror
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. Configure repositories using the China CDN mirror (-r china)
pig repo add pgsql -u -r china

# 3. Install vchord, vchord_bm25, and pg_tokenizer (or specify PG major version with -v 18)
pig install vchord vchord_bm25 pg_tokenizer
```

{{< /tab >}}
{{< tab label="Native APT (Debian / Ubuntu)" >}}

```bash
# Once the Pigsty APT repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo apt-get update
sudo apt-get install -y \
  postgresql-18-vchord \
  postgresql-18-vchord-bm25 \
  postgresql-18-pg-tokenizer
```

{{< /tab >}}
{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}

```bash
# Once the Pigsty YUM repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo dnf install -y \
  vchord_18 \
  vchord_bm25_18 \
  pg_tokenizer_18
```

{{< /tab >}}
{{< /tabs >}}

### 2 · Preload Shared Libraries & Enable Extensions {#enable}

All three extensions require registering their shared libraries in `shared_preload_libraries` and restarting PostgreSQL before running `CREATE EXTENSION`:

```sql
-- 1. Register shared libraries in postgresql.conf via ALTER SYSTEM
ALTER SYSTEM SET shared_preload_libraries = 'vchord.so, vchord_bm25.so, pg_tokenizer.so';
```

Restart PostgreSQL (`sudo systemctl restart postgresql-18` or `pig pg restart`), then connect to your target database and enable the extensions:

```sql
-- 2. Enable the extensions (CASCADE automatically installs pgvector for vchord)
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

### 3 · Container Images (Obsolete) {#docker}

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for its maintained releases. These upstream instructions are retained for reference and will be updated.

For local evaluation, CI pipelines, or containerized deployments, official Docker images come with PostgreSQL 18 and the extensions pre-installed and preloaded:

{{< tabs >}}
{{< tab label="Vchord Suite (All-in-One)" >}}

```bash
# Includes PostgreSQL 18 + pgvector + vchord + vchord_bm25 + pg_tokenizer
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

{{< /tab >}}
{{< tab label="vchord Only (Vector Search)" >}}

```bash
# Includes PostgreSQL 18 + pgvector + vchord v1.1.1
docker run -d \
  --name vchord-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{< /tab >}}
{{< /tabs >}}

### 4 · GitHub Releases {#releases}

| **Extension** | **Current Release** | **Documentation** | **PGEXT Catalog** | **Pigsty Docs** | **GitHub Repository & Releases** |
|:---|:---:|:---|:---|:---|:---|
| **`vchord`** | `v1.2.0` | [vchord Docs](/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pigsty.io/ext/e/vchord](https://pigsty.io/ext/e/vchord/) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v1.0.0` | [vchord_bm25 Docs](/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pigsty.io/ext/e/vchord_bm25](https://pigsty.io/ext/e/vchord_bm25/) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v1.0.0` | [pg_tokenizer Docs](/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pigsty.io/ext/e/pg_tokenizer](https://pigsty.io/ext/e/pg_tokenizer/) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{.wide .expand}

---

## 1 · `vchord` — Scalable Vector Search {#vchord}

**`vchord`** (`v1.2.0`) is the core RaBitQ-powered vector similarity search extension (`vchordrq` and `vchordg` index access methods). It depends on the `vector` ([`pgvector`](/docs/vector/)) extension.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL Extension" "blue" >}} | [`vchord`](/docs/vchord/) | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | [`vector`](/docs/vector/) | [PGEXT #1810](https://pgext.cloud/e/vchord) | {{< bg "AGPL-3.0" "License: AGPL-3.0" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `vchord_$v` | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pgvector_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-vchord` | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `postgresql-$v-pgvector` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`vchord`) {#vchord-matrix}

| **Linux** / **PG** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "vchord_14 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-15-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.2.0" "postgresql-14-vchord : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`vchord`) {#vchord-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_18` | `1.2.0` | {{< os "el8.x86_64" >}} | pigsty | 3.1 MiB | [vchord_18-1.2.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_18-1.2.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_18` | `1.2.0` | {{< os "el8.aarch64" >}} | pigsty | 2.7 MiB | [vchord_18-1.2.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_18-1.2.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_18` | `1.2.0` | {{< os "el9.x86_64" >}} | pigsty | 3.1 MiB | [vchord_18-1.2.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_18-1.2.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_18` | `1.2.0` | {{< os "el9.aarch64" >}} | pigsty | 2.9 MiB | [vchord_18-1.2.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_18-1.2.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_18` | `1.2.0` | {{< os "el10.x86_64" >}} | pigsty | 3.0 MiB | [vchord_18-1.2.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_18-1.2.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_18` | `1.2.0` | {{< os "el10.aarch64" >}} | pigsty | 2.8 MiB | [vchord_18-1.2.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_18-1.2.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "d12.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "d12.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "d13.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "d13.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u22.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u22.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u24.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u24.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u26.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-18-vchord` | `1.2.0` | {{< os "u26.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.2.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-18-vchord_1.2.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_17` | `1.2.0` | {{< os "el8.x86_64" >}} | pigsty | 3.1 MiB | [vchord_17-1.2.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_17-1.2.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_17` | `1.2.0` | {{< os "el8.aarch64" >}} | pigsty | 2.7 MiB | [vchord_17-1.2.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_17-1.2.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_17` | `1.2.0` | {{< os "el9.x86_64" >}} | pigsty | 3.1 MiB | [vchord_17-1.2.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_17-1.2.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_17` | `1.2.0` | {{< os "el9.aarch64" >}} | pigsty | 2.9 MiB | [vchord_17-1.2.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_17-1.2.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_17` | `1.2.0` | {{< os "el10.x86_64" >}} | pigsty | 3.0 MiB | [vchord_17-1.2.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_17-1.2.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_17` | `1.2.0` | {{< os "el10.aarch64" >}} | pigsty | 2.8 MiB | [vchord_17-1.2.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_17-1.2.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "d12.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "d12.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "d13.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "d13.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u22.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u22.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u24.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u24.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u26.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-17-vchord` | `1.2.0` | {{< os "u26.aarch64" >}} | pigsty | 2.9 MiB | [postgresql-17-vchord_1.2.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-17-vchord_1.2.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_16` | `1.2.0` | {{< os "el8.x86_64" >}} | pigsty | 3.1 MiB | [vchord_16-1.2.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_16-1.2.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_16` | `1.2.0` | {{< os "el8.aarch64" >}} | pigsty | 2.6 MiB | [vchord_16-1.2.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_16-1.2.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_16` | `1.2.0` | {{< os "el9.x86_64" >}} | pigsty | 3.1 MiB | [vchord_16-1.2.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_16-1.2.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_16` | `1.2.0` | {{< os "el9.aarch64" >}} | pigsty | 2.8 MiB | [vchord_16-1.2.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_16-1.2.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_16` | `1.2.0` | {{< os "el10.x86_64" >}} | pigsty | 3.0 MiB | [vchord_16-1.2.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_16-1.2.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_16` | `1.2.0` | {{< os "el10.aarch64" >}} | pigsty | 2.8 MiB | [vchord_16-1.2.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_16-1.2.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "d12.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "d12.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "d13.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "d13.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u22.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u22.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u24.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u24.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u26.x86_64" >}} | pigsty | 3.0 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-16-vchord` | `1.2.0` | {{< os "u26.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-16-vchord_1.2.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-16-vchord_1.2.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_15` | `1.2.0` | {{< os "el8.x86_64" >}} | pigsty | 3.1 MiB | [vchord_15-1.2.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_15-1.2.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_15` | `1.2.0` | {{< os "el8.aarch64" >}} | pigsty | 2.6 MiB | [vchord_15-1.2.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_15-1.2.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_15` | `1.2.0` | {{< os "el9.x86_64" >}} | pigsty | 3.1 MiB | [vchord_15-1.2.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_15-1.2.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_15` | `1.2.0` | {{< os "el9.aarch64" >}} | pigsty | 2.8 MiB | [vchord_15-1.2.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_15-1.2.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_15` | `1.2.0` | {{< os "el10.x86_64" >}} | pigsty | 3.0 MiB | [vchord_15-1.2.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_15-1.2.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_15` | `1.2.0` | {{< os "el10.aarch64" >}} | pigsty | 2.8 MiB | [vchord_15-1.2.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_15-1.2.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "d12.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "d12.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "d13.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "d13.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u22.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u22.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u24.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u24.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u26.x86_64" >}} | pigsty | 3.0 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-15-vchord` | `1.2.0` | {{< os "u26.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-15-vchord_1.2.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-15-vchord_1.2.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG14" value="pg14" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_14` | `1.2.0` | {{< os "el8.x86_64" >}} | pigsty | 3.1 MiB | [vchord_14-1.2.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_14-1.2.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_14` | `1.2.0` | {{< os "el8.aarch64" >}} | pigsty | 2.6 MiB | [vchord_14-1.2.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_14-1.2.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_14` | `1.2.0` | {{< os "el9.x86_64" >}} | pigsty | 3.1 MiB | [vchord_14-1.2.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_14-1.2.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_14` | `1.2.0` | {{< os "el9.aarch64" >}} | pigsty | 2.8 MiB | [vchord_14-1.2.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_14-1.2.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_14` | `1.2.0` | {{< os "el10.x86_64" >}} | pigsty | 3.0 MiB | [vchord_14-1.2.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_14-1.2.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_14` | `1.2.0` | {{< os "el10.aarch64" >}} | pigsty | 2.8 MiB | [vchord_14-1.2.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_14-1.2.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "d12.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "d12.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "d13.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "d13.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u22.x86_64" >}} | pigsty | 3.1 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u22.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u24.x86_64" >}} | pigsty | 3.0 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u24.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u26.x86_64" >}} | pigsty | 3.0 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-14-vchord` | `1.2.0` | {{< os "u26.aarch64" >}} | pigsty | 2.8 MiB | [postgresql-14-vchord_1.2.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-14-vchord_1.2.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## 2 · `vchord_bm25` — Native BM25 Ranking Index {#vchord_bm25}

**`vchord_bm25`** (`v1.0.0`) provides native Okapi BM25 full-text ranking indexes (`USING bm25`) and Block-WeakAnd Top-K search (`<&>`) inside PostgreSQL. Upgrading from 0.3.x requires [migration](/docs/bm25/reference/migration/).

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL Extension" "blue" >}} | [`vchord_bm25`](/docs/bm25/) | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | [PGEXT #2160](https://pgext.cloud/e/vchord_bm25) | {{< bg "AGPL-3.0" "License: AGPL-3.0" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `vchord_bm25_$v` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-vchord-bm25` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`vchord_bm25`) {#vchord_bm25-matrix}

| **Linux** / **PG** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "vchord_bm25_14 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-vchord-bm25 : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`vchord_bm25`) {#vchord_bm25-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_18` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_18-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_18-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_bm25_18` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 1014.4 KiB | [vchord_bm25_18-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_18-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_bm25_18` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_18-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_18-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_bm25_18` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 1.1 MiB | [vchord_bm25_18-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_18-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_bm25_18` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_18-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_18-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_bm25_18` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_18-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_18-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 881.2 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 774.3 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 881.1 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 774.9 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 984.5 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 920.7 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 974.9 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 907.7 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 970.4 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 905.5 KiB | [postgresql-18-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_17` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_17-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_17-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_bm25_17` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 1012.2 KiB | [vchord_bm25_17-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_17-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_bm25_17` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_17-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_17-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_bm25_17` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 1.1 MiB | [vchord_bm25_17-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_17-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_bm25_17` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_17-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_17-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_bm25_17` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_17-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_17-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 878.9 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 772.5 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 879.2 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 772.9 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 981.2 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 917.0 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 974.8 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 906.0 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 967.6 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 904.2 KiB | [postgresql-17-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_16` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_16-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_16-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_bm25_16` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 1009.7 KiB | [vchord_bm25_16-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_16-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_bm25_16` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_16-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_16-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_bm25_16` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 1.1 MiB | [vchord_bm25_16-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_16-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_bm25_16` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_16-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_16-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_bm25_16` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_16-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_16-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 879.9 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 772.4 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 880.2 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 772.1 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 984.3 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 916.1 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 972.8 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 905.6 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 968.8 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 903.5 KiB | [postgresql-16-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_15` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_15-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_15-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_bm25_15` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 1003.8 KiB | [vchord_bm25_15-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_15-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_bm25_15` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_15-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_15-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_bm25_15` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_15-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_15-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_bm25_15` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_15-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_15-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_bm25_15` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_15-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_15-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 877.1 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 770.6 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 878.2 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 770.8 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 976.9 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 914.5 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 970.6 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 902.4 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 965.3 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 900.4 KiB | [postgresql-15-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG14" value="pg14" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_14` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_14-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_14-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `vchord_bm25_14` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 1001.6 KiB | [vchord_bm25_14-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_14-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `vchord_bm25_14` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_14-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_14-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `vchord_bm25_14` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_14-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_14-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `vchord_bm25_14` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 1.1 MiB | [vchord_bm25_14-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_14-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `vchord_bm25_14` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 1.0 MiB | [vchord_bm25_14-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_14-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 873.7 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 768.3 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 873.8 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 769.1 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 976.2 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 912.7 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 966.4 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 901.3 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 962.5 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-14-vchord-bm25` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 898.0 KiB | [postgresql-14-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-14-vchord-bm25_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## 3 · `pg_tokenizer` — Multilingual Text Analyzer {#pg_tokenizer}

**`pg_tokenizer`** (`v1.0.0`) provides customizable in-database text analysis pipelines, pre-tokenizers (Unicode, Jieba, Lindera), stemmers, stopword/synonym filters, and vocabulary models.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL Extension" "blue" >}} | [`pg_tokenizer`](/docs/tokenizer/) | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | [PGEXT #2170](https://pgext.cloud/e/pg_tokenizer) | {{< bg "Apache-2.0" "License: Apache-2.0" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `pg_tokenizer_$v` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-pg-tokenizer` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`pg_tokenizer`) {#pg_tokenizer-matrix}

| **Linux** / **PG** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "pg_tokenizer_14 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.0.0" "postgresql-14-pg-tokenizer : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`pg_tokenizer`) {#pg_tokenizer-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_18` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 13.3 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_18-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_18` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 13.0 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_18-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_18` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 12.5 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_18-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_18` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_18-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_18` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_18-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_18` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_18-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_18-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 12.2 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_17` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 13.3 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_17-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_17` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 13.0 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_17-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_17` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 12.5 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_17-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_17` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_17-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_17` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_17-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_17` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_17-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_17-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 12.2 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_16` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 13.3 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_16-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_16` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 13.0 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_16-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_16` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 12.5 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_16-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_16` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_16-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_16` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_16-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_16` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_16-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_16-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 12.2 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_15` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 13.3 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_15-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_15` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 13.0 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_15-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_15` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 12.5 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_15-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_15` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_15-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_15` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_15-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_15` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_15-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_15-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG14" value="pg14" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_14` | `1.0.0` | {{< os "el8.x86_64" >}} | pigsty | 13.3 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_14-1.0.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_14` | `1.0.0` | {{< os "el8.aarch64" >}} | pigsty | 13.0 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_14-1.0.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_14` | `1.0.0` | {{< os "el9.x86_64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_14-1.0.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_14` | `1.0.0` | {{< os "el9.aarch64" >}} | pigsty | 12.4 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_14-1.0.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_14` | `1.0.0` | {{< os "el10.x86_64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_14-1.0.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_14` | `1.0.0` | {{< os "el10.aarch64" >}} | pigsty | 12.3 MiB | [pg_tokenizer_14-1.0.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_14-1.0.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "d12.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "d12.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "d13.x86_64" >}} | pigsty | 11.1 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "d13.aarch64" >}} | pigsty | 10.9 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u22.x86_64" >}} | pigsty | 12.2 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u22.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u24.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u24.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u26.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-14-pg-tokenizer` | `1.0.0` | {{< os "u26.aarch64" >}} | pigsty | 12.0 MiB | [postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-14-pg-tokenizer_1.0.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## Verification & Build Repositories {#source}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` / `apt` once configured via `pig repo add pgsql`. Every package is built transparently from open-source build specs:

| **Repository** | **Description** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | The `pig` CLI package manager for PostgreSQL and 600+ extensions |
| [pgsty/rpm](https://github.com/pgsty/rpm) | RPM build specifications for EL 8 / 9 / 10 (`x86_64` & `aarch64`) |
| [pgsty/deb](https://github.com/pgsty/deb) | DEB build specifications for Debian 12 / 13 & Ubuntu 22.04 / 24.04 / 26.04 (`x86_64` & `aarch64`) |
| [pgext.cloud](https://pgext.cloud/) | Full PostgreSQL extension catalog, availability matrix, and repository mirrors |
{.wide .expand}
