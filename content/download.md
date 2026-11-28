---
title: Download & Install
linkTitle: Download
description: Install vchord, vchord_bm25 and pg_tokenizer and find RPM and DEB packages for your PostgreSQL version and platform.
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

The download tables list RPM and DEB packages for `vchord`, `vchord_bm25` and `pg_tokenizer` by PostgreSQL version, operating system and architecture.

> [!IMPORTANT]
> **Download sources**:
> - **Latest GitHub releases**: [**`vchord 1.5.0`**](https://github.com/pgsty/vchord/releases/tag/1.5.0), [**`vchord_bm25 1.3.0`**](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0), and [**`pg_tokenizer 1.3.0`**](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) provide pre-built Linux ZIP and Debian packages for PostgreSQL 15–19 (`x86_64` / `aarch64`). Review the [`vchord 1.5.0`](/release/vchord-1.5.0/), [`vchord_bm25 1.3.0`](/release/vchord-bm25-1.3.0/), and [`pg_tokenizer 1.3.0`](/release/pg-tokenizer-1.3.0/) release notes before upgrading.
> - **Pigsty APT / YUM** publishes package versions and file URLs by platform for [vchord](#vchord-packages), [vchord_bm25](#vchord_bm25-packages) and [pg_tokenizer](#pg_tokenizer-packages).

{{< cards >}}
{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v1.5.0" >}}
Disk-friendly vector similarity search extension built on `pgvector`, providing RaBitQ-compressed `vchordrq` (IVF with filter keys) and `vchordg` (graph) indexes, multi-vector MaxSim (`@#`), and sphere search across PostgreSQL 15–19.
{{< /card >}}
{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v1.3.0" >}}
Native Okapi BM25 ranking index extension for `tsvector` columns powered by Block-WeakAnd pruning and the `<&>` operator, built for lexical Top-K retrieval and hybrid search across PostgreSQL 15–19.
{{< /card >}}
{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v1.3.0" >}}
In-database multilingual text analyzer and token-ID encoder supporting Unicode segmentation, Jieba (Chinese), Lindera 7 (Japanese), Snowball stemming, HuggingFace vocabularies, and custom corpus models across PostgreSQL 15–19.
{{< /card >}}
{{< /cards >}}

---

## Quick Installation {#install}

### 1 · Install with PIG Package Manager (Recommended) {#pig}

Install the Vchord extension suite with [**`pig`**](https://pig.pgsty.com/), the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and installs extension dependencies (`pgvector`) automatically.

{{< tabs >}}
{{< tab label="Global (Default)" >}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update the cache
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

# 3. Install vchord, vchord_bm25, and pg_tokenizer (or pass -v 18 for a specific PG major version)
pig install vchord vchord_bm25 pg_tokenizer
```

{{< /tab >}}
{{< tab label="Native APT (Debian / Ubuntu)" >}}

```bash
# After configuring the Pigsty APT repository, install for your PostgreSQL major version (e.g., PG 18):
sudo apt-get update
sudo apt-get install -y \
  postgresql-18-vchord \
  postgresql-18-vchord-bm25 \
  postgresql-18-pg-tokenizer
```

{{< /tab >}}
{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}

```bash
# After configuring the Pigsty YUM repository, install for your PostgreSQL major version (e.g., PG 18):
sudo dnf install -y \
  vchord_18 \
  vchord_bm25_18 \
  pg_tokenizer_18
```

{{< /tab >}}
{{< /tabs >}}

### 2 · Preload Shared Libraries & Enable Extensions {#enable}

Add the shared libraries to `shared_preload_libraries` and restart PostgreSQL before running `CREATE EXTENSION`:

```sql
-- 1. Register shared libraries in postgresql.auto.conf
ALTER SYSTEM SET shared_preload_libraries = 'vchord.so, vchord_bm25.so, pg_tokenizer.so';
```

Restart PostgreSQL (`sudo systemctl restart postgresql-18` or `pig pg restart`), then connect to your target database and create the extensions:

```sql
-- 2. Enable the extensions (CASCADE installs pgvector for vchord)
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

### 3 · Container Images (Historical Upstream Reference) {#docker}

> [!WARNING]
> **Historical Upstream Images**: PGSTY does not publish container images for `vchord 1.5.0`, `vchord_bm25 1.3.0`, or `pg_tokenizer 1.3.0`. The upstream TensorChord images below contain older versions and are listed for local reference only. Use Pigsty packages or GitHub release artifacts for current production deployments.

{{< tabs >}}
{{< tab label="Vchord Suite (Historical)" >}}

```bash
# Historical upstream image (PostgreSQL 18 + older VectorChord suite)
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

{{< /tab >}}
{{< tab label="vchord Only (Historical v1.1.1)" >}}

```bash
# Historical upstream image (PostgreSQL 18 + pgvector + VectorChord 1.1.1)
docker run -d \
  --name vchord-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{< /tab >}}
{{< /tabs >}}

### 4 · Release & Catalog Overview {#releases}

| **Extension** | **Documented source release** | **Pigsty Repo Package** | **Documentation** | **PGEXT Catalog** | **GitHub Releases** |
|:---|:---:|:---:|:---|:---|:---|
| **`vchord`** | `v1.5.0` | `1.5.0, 1.3.0` | [vchord Docs](/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v1.3.0` | `1.3.0` | [vchord_bm25 Docs](/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v1.3.0` | `1.3.0` | [pg_tokenizer Docs](/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{.wide .expand}

---

## 1 · `vchord` — Scalable Vector Search {#vchord}

**`vchord`** (`v1.5.0`) provides the `vchordrq` (RaBitQ IVF) and `vchordg` (single-layer RaBitQ graph) index access methods, `rabitq4`/`rabitq8` quantized vector types, sphere search, and `@#` MaxSim operators. It requires the `vector` ([`pgvector`](/docs/vector/)) extension.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "Latest GitHub release" "blue" >}} | [`vchord`](/docs/vchord/) | `1.5.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | [`vector`](/docs/vector/) | [GitHub Release 1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0) | {{< bg "AGPL-3.0" "License: AGPL-3.0-only" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `vchord_$v` | [Package versions](#vchord-packages) | [Matrix](#vchord-matrix) | `pgvector_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-vchord` | [Package versions](#vchord-packages) | [Matrix](#vchord-matrix) | `postgresql-$v-pgvector` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`vchord`) {#vchord-matrix}

| **Linux** / **PG** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "N/A" "vchord_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "N/A" "vchord_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "vchord_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "vchord_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "vchord_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "vchord_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "vchord_15 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-19-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-18-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-17-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-16-vchord : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.5.0" "postgresql-15-vchord : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`vchord`) {#vchord-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_19` | `1.5.0` | {{< os "el9.x86_64" >}} | pigsty | 3.5 MiB | [vchord_19-1.5.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_19-1.5.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_19` | `1.5.0` | {{< os "el9.aarch64" >}} | pigsty | 3.2 MiB | [vchord_19-1.5.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_19-1.5.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_19` | `1.5.0` | {{< os "el10.x86_64" >}} | pigsty | 3.6 MiB | [vchord_19-1.5.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_19-1.5.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_19` | `1.5.0` | {{< os "el10.aarch64" >}} | pigsty | 3.2 MiB | [vchord_19-1.5.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_19-1.5.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "d12.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "d12.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "d13.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "d13.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u22.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u22.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u24.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~noble_amd64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u24.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~noble_arm64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u26.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-19-vchord` | `1.5.0` | {{< os "u26.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-19-vchord_1.5.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-19-vchord_1.5.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_18` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 3.4 MiB | [vchord_18-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_18-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_18` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 3.0 MiB | [vchord_18-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_18-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_18` | `1.5.0` | {{< os "el9.x86_64" >}} | pigsty | 3.5 MiB | [vchord_18-1.5.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_18-1.5.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_18` | `1.5.0` | {{< os "el9.aarch64" >}} | pigsty | 3.2 MiB | [vchord_18-1.5.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_18-1.5.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_18` | `1.5.0` | {{< os "el10.x86_64" >}} | pigsty | 3.5 MiB | [vchord_18-1.5.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_18-1.5.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_18` | `1.5.0` | {{< os "el10.aarch64" >}} | pigsty | 3.2 MiB | [vchord_18-1.5.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_18-1.5.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "d12.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "d12.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "d13.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "d13.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u22.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u22.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u24.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~noble_amd64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u24.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~noble_arm64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u26.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-18-vchord` | `1.5.0` | {{< os "u26.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-18-vchord_1.5.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-18-vchord_1.5.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_17` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 3.4 MiB | [vchord_17-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_17-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_17` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 3.0 MiB | [vchord_17-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_17-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_17` | `1.5.0` | {{< os "el9.x86_64" >}} | pigsty | 3.5 MiB | [vchord_17-1.5.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_17-1.5.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_17` | `1.5.0` | {{< os "el9.aarch64" >}} | pigsty | 3.2 MiB | [vchord_17-1.5.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_17-1.5.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_17` | `1.5.0` | {{< os "el10.x86_64" >}} | pigsty | 3.5 MiB | [vchord_17-1.5.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_17-1.5.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_17` | `1.5.0` | {{< os "el10.aarch64" >}} | pigsty | 3.2 MiB | [vchord_17-1.5.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_17-1.5.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "d12.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "d12.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "d13.x86_64" >}} | pigsty | 2.6 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "d13.aarch64" >}} | pigsty | 2.1 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u22.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u22.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u24.x86_64" >}} | pigsty | 2.9 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~noble_amd64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u24.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~noble_arm64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u26.x86_64" >}} | pigsty | 2.8 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-17-vchord` | `1.5.0` | {{< os "u26.aarch64" >}} | pigsty | 2.5 MiB | [postgresql-17-vchord_1.5.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-17-vchord_1.5.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_16` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 3.3 MiB | [vchord_16-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_16-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_16` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 2.9 MiB | [vchord_16-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_16-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_16` | `1.5.0` | {{< os "el9.x86_64" >}} | pigsty | 3.3 MiB | [vchord_16-1.5.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_16-1.5.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_16` | `1.5.0` | {{< os "el9.aarch64" >}} | pigsty | 3.0 MiB | [vchord_16-1.5.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_16-1.5.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_16` | `1.5.0` | {{< os "el10.x86_64" >}} | pigsty | 3.3 MiB | [vchord_16-1.5.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_16-1.5.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_16` | `1.5.0` | {{< os "el10.aarch64" >}} | pigsty | 3.0 MiB | [vchord_16-1.5.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_16-1.5.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "d12.x86_64" >}} | pigsty | 2.5 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "d12.aarch64" >}} | pigsty | 2.0 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "d13.x86_64" >}} | pigsty | 2.5 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "d13.aarch64" >}} | pigsty | 2.0 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u22.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u22.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u24.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~noble_amd64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u24.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~noble_arm64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u26.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-16-vchord` | `1.5.0` | {{< os "u26.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-16-vchord_1.5.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-16-vchord_1.5.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_15` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 3.3 MiB | [vchord_15-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_15-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_15` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 2.9 MiB | [vchord_15-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_15-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_15` | `1.5.0` | {{< os "el9.x86_64" >}} | pigsty | 3.3 MiB | [vchord_15-1.5.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_15-1.5.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_15` | `1.5.0` | {{< os "el9.aarch64" >}} | pigsty | 3.0 MiB | [vchord_15-1.5.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_15-1.5.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_15` | `1.5.0` | {{< os "el10.x86_64" >}} | pigsty | 3.3 MiB | [vchord_15-1.5.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_15-1.5.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_15` | `1.5.0` | {{< os "el10.aarch64" >}} | pigsty | 3.0 MiB | [vchord_15-1.5.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_15-1.5.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "d12.x86_64" >}} | pigsty | 2.5 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "d12.aarch64" >}} | pigsty | 2.0 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "d13.x86_64" >}} | pigsty | 2.5 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "d13.aarch64" >}} | pigsty | 2.0 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u22.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u22.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u24.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~noble_amd64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u24.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~noble_arm64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u26.x86_64" >}} | pigsty | 2.7 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-15-vchord` | `1.5.0` | {{< os "u26.aarch64" >}} | pigsty | 2.4 MiB | [postgresql-15-vchord_1.5.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord/postgresql-15-vchord_1.5.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## 2 · `vchord_bm25` — Native BM25 Ranking Index {#vchord_bm25}

**`vchord_bm25`** (`v1.3.0`) provides native Okapi BM25 ranking indexes (`USING bm25`) and Block-WeakAnd Top-K scans (`<&>`) on PostgreSQL `tsvector` columns. Any `1.x` installation upgrades in place via `ALTER EXTENSION vchord_bm25 UPDATE`; upgrading from `0.3.x` requires following the [BM25 Migration Guide](/docs/bm25/reference/migration/).

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "Latest GitHub release" "blue" >}} | [`vchord_bm25`](/docs/bm25/) | `1.3.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | `-` | [GitHub Release 1.3.0](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) | {{< bg "AGPL-3.0" "License: AGPL-3.0-only" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `vchord_bm25_$v` | [Package versions](#vchord_bm25-packages) | [Matrix](#vchord_bm25-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-vchord-bm25` | [Package versions](#vchord_bm25-packages) | [Matrix](#vchord_bm25-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`vchord_bm25`) {#vchord_bm25-matrix}

| **Linux** / **PG** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "N/A" "vchord_bm25_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "N/A" "vchord_bm25_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "vchord_bm25_15 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-vchord-bm25 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-vchord-bm25 : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`vchord_bm25`) {#vchord_bm25-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_19` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_19-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_19-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_bm25_19` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_19-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_19-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_bm25_19` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_19-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_19-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_bm25_19` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_19-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_19-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 1.4 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-19-vchord-bm25` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-19-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-19-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_18` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_18-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_bm25_18` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_18-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_bm25_18` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_18-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_bm25_18` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_18-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_bm25_18` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_18-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_bm25_18` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_18-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_18-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 1.4 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-18-vchord-bm25` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-18-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-18-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_17` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_17-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_bm25_17` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_17-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_bm25_17` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_17-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_bm25_17` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_17-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_bm25_17` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_17-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_bm25_17` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_17-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_17-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-17-vchord-bm25` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-17-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-17-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_16` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_16-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_bm25_16` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_16-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_bm25_16` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_16-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_bm25_16` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_16-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_bm25_16` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_16-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_bm25_16` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_16-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_16-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-16-vchord-bm25` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-16-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-16-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `vchord_bm25_15` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/vchord_bm25_15-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `vchord_bm25_15` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/vchord_bm25_15-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `vchord_bm25_15` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 2.0 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/vchord_bm25_15-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `vchord_bm25_15` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/vchord_bm25_15-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `vchord_bm25_15` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 1.9 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/vchord_bm25_15-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `vchord_bm25_15` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 1.8 MiB | [vchord_bm25_15-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/vchord_bm25_15-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 1.4 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 1.1 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 1.5 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-15-vchord-bm25` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 1.3 MiB | [postgresql-15-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/v/vchord-bm25/postgresql-15-vchord-bm25_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## 3 · `pg_tokenizer` — Multilingual Text Analyzer {#pg_tokenizer}

**`pg_tokenizer`** (`v1.3.0`) provides customizable in-database text analyzers, pre-tokenizers (Unicode, Jieba, Lindera 7), Snowball stemmers, stopword and synonym filters, native C `tsvector` helpers, and vocabulary models. Run `ALTER EXTENSION pg_tokenizer UPDATE` on PostgreSQL 15–19; see [Upgrade](/docs/tokenizer/installation/#upgrading) when crossing earlier releases.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "Latest GitHub release" "blue" >}} | [`pg_tokenizer`](/docs/tokenizer/) | `1.3.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | `-` | [GitHub Release v1.3.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) | {{< bg "Apache-2.0" "License: Apache-2.0" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `pg_tokenizer_$v` | [Package versions](#pg_tokenizer-packages) | [Matrix](#pg_tokenizer-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.0)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-pg-tokenizer` | [Package versions](#pg_tokenizer-packages) | [Matrix](#pg_tokenizer-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.20.0)" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`pg_tokenizer`) {#pg_tokenizer-matrix}

| **Linux** / **PG** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "N/A" "pg_tokenizer_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "N/A" "pg_tokenizer_19 : N/A 0" "gray" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_19 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "pg_tokenizer_15 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-19-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-18-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-17-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-16-pg-tokenizer : AVAIL 1" "green" >}} | {{< bg "PIGSTY 1.3.0" "postgresql-15-pg-tokenizer : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`pg_tokenizer`) {#pg_tokenizer-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_19` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_19-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_19-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_19` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_19-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_19-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_19` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 16.7 MiB | [pg_tokenizer_19-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_19-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_19` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 16.4 MiB | [pg_tokenizer_19-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_19-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 11.8 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 11.8 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-19-pg-tokenizer` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-19-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-19-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_18` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_18-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_18` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_18-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_18` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_18-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_18` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_18-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_18` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 16.7 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_18-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_18` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 16.4 MiB | [pg_tokenizer_18-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_18-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 11.8 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 13.2 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-18-pg-tokenizer` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-18-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-18-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_17` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_17-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_17` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_17-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_17` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_17-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_17` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_17-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_17` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 16.7 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_17-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_17` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 16.4 MiB | [pg_tokenizer_17-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_17-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-17-pg-tokenizer` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-17-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-17-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_16` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_16-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_16` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_16-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_16` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_16-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_16` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_16-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_16` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 16.7 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_16-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_16` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 16.4 MiB | [pg_tokenizer_16-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_16-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-16-pg-tokenizer` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-16-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-16-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_tokenizer_15` | `1.3.0` | {{< os "el8.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_tokenizer_15-1.3.0-1PGSTY.el8.x86_64.rpm) |
| `pg_tokenizer_15` | `1.3.0` | {{< os "el8.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_tokenizer_15-1.3.0-1PGSTY.el8.aarch64.rpm) |
| `pg_tokenizer_15` | `1.3.0` | {{< os "el9.x86_64" >}} | pigsty | 16.8 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_tokenizer_15-1.3.0-1PGSTY.el9.x86_64.rpm) |
| `pg_tokenizer_15` | `1.3.0` | {{< os "el9.aarch64" >}} | pigsty | 16.6 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_tokenizer_15-1.3.0-1PGSTY.el9.aarch64.rpm) |
| `pg_tokenizer_15` | `1.3.0` | {{< os "el10.x86_64" >}} | pigsty | 16.7 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_tokenizer_15-1.3.0-1PGSTY.el10.x86_64.rpm) |
| `pg_tokenizer_15` | `1.3.0` | {{< os "el10.aarch64" >}} | pigsty | 16.4 MiB | [pg_tokenizer_15-1.3.0-1PGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_tokenizer_15-1.3.0-1PGSTY.el10.aarch64.rpm) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "d12.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~bookworm_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "d12.aarch64" >}} | pigsty | 11.7 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~bookworm_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "d13.x86_64" >}} | pigsty | 12.1 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~trixie_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "d13.aarch64" >}} | pigsty | 11.8 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~trixie_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u22.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~jammy_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u22.aarch64" >}} | pigsty | 12.9 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~jammy_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u24.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~noble_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u24.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~noble_arm64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u26.x86_64" >}} | pigsty | 13.1 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~resolute_amd64.deb) |
| `postgresql-15-pg-tokenizer` | `1.3.0` | {{< os "u26.aarch64" >}} | pigsty | 12.8 MiB | [postgresql-15-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-tokenizer/postgresql-15-pg-tokenizer_1.3.0-1PGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## Verification & Build Repositories {#source}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` and `apt` after running `pig repo add pgsql`. Package build specifications are maintained in open-source repositories:

| **Repository** | **Description** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | The `pig` CLI package manager for PostgreSQL and 600+ extensions |
| [pgsty/rpm](https://github.com/pgsty/rpm) | RPM build specifications for EL 8 / 9 / 10 (`x86_64` & `aarch64`) |
| [pgsty/deb](https://github.com/pgsty/deb) | DEB build specifications for Debian 12 / 13 & Ubuntu 22.04 / 24.04 / 26.04 (`x86_64` & `aarch64`) |
| [pgext.cloud](https://pgext.cloud/) | Full PostgreSQL extension catalog, availability matrix, and repository mirrors |
{.wide .expand}
