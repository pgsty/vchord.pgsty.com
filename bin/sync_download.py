#!/usr/bin/env python3
"""Synchronize package availability matrices and download tables from pgext into content/download.{md,zh.md}."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

EXTENSIONS = ("vchord", "vchord_bm25", "pg_tokenizer")
RELEASE_VERSIONS = {"vchord": "1.5.0", "vchord_bm25": "1.3.0", "pg_tokenizer": "1.3.0"}


def table_reader_attributes(match: re.Match[str]) -> str:
    """Preserve source table attributes and add missing reader opt-ins."""
    attributes = match.group(1)
    classes = set(re.findall(r"(?:^|\s)\.([\w-]+)", attributes))
    missing = [name for name in ("wide", "expand") if name not in classes]
    return "{" + attributes.rstrip() + "".join(" ." + name for name in missing) + "}"


def parse_pgext_markdown(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")

    matrix_match = re.search(
        r"(\| \*\*Linux\*\* / \*\*PG\*\* \|.*?\n\{\.matrix(?:\s+[^{}\n]*)?\})",
        text,
        re.S,
    )
    if not matrix_match:
        raise ValueError(f"Could not find {{.matrix}} table in {path}")
    matrix_en = re.sub(r"\{(\.matrix\b[^{}\n]*)\}", table_reader_attributes, matrix_match.group(1))
    matrix_zh = matrix_en.replace(
        "| **Linux** / **PG** |", "| **系统平台 / PG 版本** |", 1
    )

    packages_match = re.search(
        r'(\{\{< tabs group="pgmajor" >\}\}.*?\{\{< /tabs >\}\})',
        text,
        re.S,
    )
    if not packages_match:
        raise ValueError(f"Could not find pgmajor tabs in {path}")

    packages_en = packages_match.group(1)
    versions = re.findall(r"^\|\s*`[^`\n]+`\s*\|\s*`([^`\n]+)`\s*\|", packages_en, re.M)
    repo_version = ", ".join(dict.fromkeys(versions)) or "—"

    # Replace internal pgext /os/<target> links with our {{< os "<target>" >}} shortcode
    packages_en = re.sub(
        r"\[([a-z0-9_.-]+)\]\(/os/\1\)",
        r'{{< os "\1" >}}',
        packages_en,
    )
    packages_en = re.sub(r"\{(\.downloads\b[^{}\n]*)\}", table_reader_attributes, packages_en)

    packages_zh = re.sub(
        r"\| \*\*Package\*\* \| \*\*Version\*\* \| \*\*OS\*\* \| \*\*ORG\*\* \| \*\*SIZE\*\* \| \*\*File URL\*\* \|",
        "| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |",
        packages_en,
        flags=re.I,
    )

    return {
        "repo_version": repo_version,
        "matrix_en": matrix_en,
        "matrix_zh": matrix_zh,
        "packages_en": packages_en,
        "packages_zh": packages_zh,
    }


def build_en(data: dict[str, dict[str, str]]) -> str:
    vc = data["vchord"]
    bm = data["vchord_bm25"]
    tk = data["pg_tokenizer"]
    return f"""---
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

{{{{< cards >}}}}
{{{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v{RELEASE_VERSIONS['vchord']}" >}}}}
Disk-friendly vector similarity search extension built on `pgvector`, providing RaBitQ-compressed `vchordrq` (IVF with filter keys) and `vchordg` (graph) indexes, multi-vector MaxSim (`@#`), and sphere search across PostgreSQL 15–19.
{{{{< /card >}}}}
{{{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v{RELEASE_VERSIONS['vchord_bm25']}" >}}}}
Native Okapi BM25 ranking index extension for `tsvector` columns powered by Block-WeakAnd pruning and the `<&>` operator, built for lexical Top-K retrieval and hybrid search across PostgreSQL 15–19.
{{{{< /card >}}}}
{{{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v{RELEASE_VERSIONS['pg_tokenizer']}" >}}}}
In-database multilingual text analyzer and token-ID encoder supporting Unicode segmentation, Jieba (Chinese), Lindera 7 (Japanese), Snowball stemming, HuggingFace vocabularies, and custom corpus models across PostgreSQL 15–19.
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## Quick Installation {{#install}}

### 1 · Install with PIG Package Manager (Recommended) {{#pig}}

Install the Vchord extension suite with [**`pig`**](https://pig.pgsty.com/), the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and installs extension dependencies (`pgvector`) automatically.

{{{{< tabs >}}}}
{{{{< tab label="Global (Default)" >}}}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update the cache
pig repo add pgsql -u

# 3. Install vchord, vchord_bm25, and pg_tokenizer (auto-detects active PG version, or pass -v 18)
pig install vchord vchord_bm25 pg_tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="Mainland China Mirror" >}}}}

```bash
# 1. Install the pig CLI via the mainland China mirror
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. Configure repositories using the China CDN mirror (-r china)
pig repo add pgsql -u -r china

# 3. Install vchord, vchord_bm25, and pg_tokenizer (or pass -v 18 for a specific PG major version)
pig install vchord vchord_bm25 pg_tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="Native APT (Debian / Ubuntu)" >}}}}

```bash
# After configuring the Pigsty APT repository, install for your PostgreSQL major version (e.g., PG 18):
sudo apt-get update
sudo apt-get install -y \\
  postgresql-18-vchord \\
  postgresql-18-vchord-bm25 \\
  postgresql-18-pg-tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}}}

```bash
# After configuring the Pigsty YUM repository, install for your PostgreSQL major version (e.g., PG 18):
sudo dnf install -y \\
  vchord_18 \\
  vchord_bm25_18 \\
  pg_tokenizer_18
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 2 · Preload Shared Libraries & Enable Extensions {{#enable}}

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

### 3 · Container Images (Historical Upstream Reference) {{#docker}}

> [!WARNING]
> **Historical Upstream Images**: PGSTY does not publish container images for `vchord 1.5.0`, `vchord_bm25 1.3.0`, or `pg_tokenizer 1.3.0`. The upstream TensorChord images below contain older versions and are listed for local reference only. Use Pigsty packages or GitHub release artifacts for current production deployments.

{{{{< tabs >}}}}
{{{{< tab label="Vchord Suite (Historical)" >}}}}

```bash
# Historical upstream image (PostgreSQL 18 + older VectorChord suite)
docker run -d \\
  --name vchord-suite \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  tensorchord/vchord-suite:pg18-latest
```

{{{{< /tab >}}}}
{{{{< tab label="vchord Only (Historical v1.1.1)" >}}}}

```bash
# Historical upstream image (PostgreSQL 18 + pgvector + VectorChord 1.1.1)
docker run -d \\
  --name vchord-postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 4 · Release & Catalog Overview {{#releases}}

| **Extension** | **Documented source release** | **Pigsty Repo Package** | **Documentation** | **PGEXT Catalog** | **GitHub Releases** |
|:---|:---:|:---:|:---|:---|:---|
| **`vchord`** | `v{RELEASE_VERSIONS['vchord']}` | `{vc['repo_version']}` | [vchord Docs](/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v{RELEASE_VERSIONS['vchord_bm25']}` | `{bm['repo_version']}` | [vchord_bm25 Docs](/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v{RELEASE_VERSIONS['pg_tokenizer']}` | `{tk['repo_version']}` | [pg_tokenizer Docs](/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{{.wide .expand}}

---

## 1 · `vchord` — Scalable Vector Search {{#vchord}}

**`vchord`** (`v{RELEASE_VERSIONS['vchord']}`) provides the `vchordrq` (RaBitQ IVF) and `vchordg` (single-layer RaBitQ graph) index access methods, `rabitq4`/`rabitq8` quantized vector types, sphere search, and `@#` MaxSim operators. It requires the `vector` ([`pgvector`](/docs/vector/)) extension.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "Latest GitHub release" "blue" >}}}} | [`vchord`](/docs/vchord/) | `{RELEASE_VERSIONS['vchord']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | [`vector`](/docs/vector/) | [GitHub Release 1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0) | {{{{< bg "AGPL-3.0" "License: AGPL-3.0-only" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `vchord_$v` | [Package versions](#vchord-packages) | [Matrix](#vchord-matrix) | `pgvector_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-vchord` | [Package versions](#vchord-packages) | [Matrix](#vchord-matrix) | `postgresql-$v-pgvector` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`vchord`) {{#vchord-matrix}}

{vc['matrix_en']}

### Package Downloads (`vchord`) {{#vchord-packages}}

{vc['packages_en']}

---

## 2 · `vchord_bm25` — Native BM25 Ranking Index {{#vchord_bm25}}

**`vchord_bm25`** (`v{RELEASE_VERSIONS['vchord_bm25']}`) provides native Okapi BM25 ranking indexes (`USING bm25`) and Block-WeakAnd Top-K scans (`<&>`) on PostgreSQL `tsvector` columns. Any `1.x` installation upgrades in place via `ALTER EXTENSION vchord_bm25 UPDATE`; upgrading from `0.3.x` requires following the [BM25 Migration Guide](/docs/bm25/reference/migration/).

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "Latest GitHub release" "blue" >}}}} | [`vchord_bm25`](/docs/bm25/) | `{RELEASE_VERSIONS['vchord_bm25']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | `-` | [GitHub Release 1.3.0](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) | {{{{< bg "AGPL-3.0" "License: AGPL-3.0-only" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `vchord_bm25_$v` | [Package versions](#vchord_bm25-packages) | [Matrix](#vchord_bm25-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-vchord-bm25` | [Package versions](#vchord_bm25-packages) | [Matrix](#vchord_bm25-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.1)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`vchord_bm25`) {{#vchord_bm25-matrix}}

{bm['matrix_en']}

### Package Downloads (`vchord_bm25`) {{#vchord_bm25-packages}}

{bm['packages_en']}

---

## 3 · `pg_tokenizer` — Multilingual Text Analyzer {{#pg_tokenizer}}

**`pg_tokenizer`** (`v{RELEASE_VERSIONS['pg_tokenizer']}`) provides customizable in-database text analyzers, pre-tokenizers (Unicode, Jieba, Lindera 7), Snowball stemmers, stopword and synonym filters, native C `tsvector` helpers, and vocabulary models. Run `ALTER EXTENSION pg_tokenizer UPDATE` on PostgreSQL 15–19; see [Upgrade](/docs/tokenizer/installation/#upgrading) when crossing earlier releases.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "Latest GitHub release" "blue" >}}}} | [`pg_tokenizer`](/docs/tokenizer/) | `{RELEASE_VERSIONS['pg_tokenizer']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | `-` | [GitHub Release v1.3.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) | {{{{< bg "Apache-2.0" "License: Apache-2.0" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `pg_tokenizer_$v` | [Package versions](#pg_tokenizer-packages) | [Matrix](#pg_tokenizer-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.0)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-pg-tokenizer` | [Package versions](#pg_tokenizer-packages) | [Matrix](#pg_tokenizer-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.20.0)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`pg_tokenizer`) {{#pg_tokenizer-matrix}}

{tk['matrix_en']}

### Package Downloads (`pg_tokenizer`) {{#pg_tokenizer-packages}}

{tk['packages_en']}

---

## Verification & Build Repositories {{#source}}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` and `apt` after running `pig repo add pgsql`. Package build specifications are maintained in open-source repositories:

| **Repository** | **Description** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | The `pig` CLI package manager for PostgreSQL and 600+ extensions |
| [pgsty/rpm](https://github.com/pgsty/rpm) | RPM build specifications for EL 8 / 9 / 10 (`x86_64` & `aarch64`) |
| [pgsty/deb](https://github.com/pgsty/deb) | DEB build specifications for Debian 12 / 13 & Ubuntu 22.04 / 24.04 / 26.04 (`x86_64` & `aarch64`) |
| [pgext.cloud](https://pgext.cloud/) | Full PostgreSQL extension catalog, availability matrix, and repository mirrors |
{{.wide .expand}}
"""


def build_zh(data: dict[str, dict[str, str]]) -> str:
    vc = data["vchord"]
    bm = data["vchord_bm25"]
    tk = data["pg_tokenizer"]
    return f"""---
title: 下载与安装
linkTitle: 下载
description: 安装 vchord、vchord_bm25 与 pg_tokenizer，按 PostgreSQL 版本和平台查找 RPM、DEB 软件包。
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

下表按 PostgreSQL 版本、操作系统和架构列出 `vchord`、`vchord_bm25` 与 `pg_tokenizer` 的 RPM 和 DEB 下载。

> [!IMPORTANT]
> **下载来源**：
> - **最新 GitHub 发行版**：[**`vchord 1.5.0`**](https://github.com/pgsty/vchord/releases/tag/1.5.0)、[**`vchord_bm25 1.3.0`**](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) 与 [**`pg_tokenizer 1.3.0`**](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) 均在 GitHub Releases 提供面向 PostgreSQL 15–19（`x86_64` / `aarch64`）的预编译 Linux ZIP 与 Debian 软件包。升级前请查阅 [`vchord 1.5.0`](/zh/release/vchord-1.5.0/)、[`vchord_bm25 1.3.0`](/zh/release/vchord-bm25-1.3.0/) 与 [`pg_tokenizer 1.3.0`](/zh/release/pg-tokenizer-1.3.0/) 发布说明。
> - **Pigsty APT / YUM 软件源**：按平台查看 [vchord](#vchord-packages)、[vchord_bm25](#vchord_bm25-packages) 和 [pg_tokenizer](#pg_tokenizer-packages) 的包版本与下载地址。

{{{{< cards >}}}}
{{{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v{RELEASE_VERSIONS['vchord']}" >}}}}
可扩展、磁盘友好型 PostgreSQL 向量相似性检索核心扩展，基于 `pgvector` 构建，提供带过滤键的 RaBitQ `vchordrq` 倒排索引、`vchordg` 单层图索引、球面检索与 MaxSim（`@#`）多向量检索，支持 PostgreSQL 15–19。
{{{{< /card >}}}}
{{{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v{RELEASE_VERSIONS['vchord_bm25']}" >}}}}
面向 PostgreSQL 原生 `tsvector` 列的 Okapi BM25 全文相关性排序扩展，采用 Block-WeakAnd 块级剪枝索引（`USING bm25`）与 `<&>` 操作符加速 Top-K 检索，支持 PostgreSQL 15–19。
{{{{< /card >}}}}
{{{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v{RELEASE_VERSIONS['pg_tokenizer']}" >}}}}
独立运行的数据库内多语言文本分析与词元 ID 编码扩展，内置结巴中文、Lindera 7 日文、Unicode 分词、Snowball 词干提取、停用词/同义词过滤以及预训练与语料训练词表模型，支持 PostgreSQL 15–19。
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## 快速安装指南 {{#install}}

### 1 · 使用 PIG 包管理器安装（推荐） {{#pig}}

推荐使用由 [PGSTY](https://pigsty.cc/) 维护的 PostgreSQL 包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 Vchord 扩展套件。`pig` 是零依赖的静态编译 Go 命令行工具，可自动识别 Linux 发行版与 CPU 架构、配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动安装 `pgvector` 等扩展依赖。

{{{{< tabs >}}}}
{{{{< tab label="中国大陆镜像（推荐）" >}}}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（启用中国大陆 CDN 镜像）并刷新缓存
pig repo add pgsql -u -r china

# 3. 安装 vchord、vchord_bm25 与 pg_tokenizer（自动匹配当前 PG 版本，或通过 -v 18 指定）
pig install vchord vchord_bm25 pg_tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="全球默认源" >}}}}

```bash
# 1. 安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库并刷新缓存
pig repo add pgsql -u

# 3. 安装 vchord、vchord_bm25 与 pg_tokenizer（可通过 -v 18 显式指定 PostgreSQL 大版本）
pig install vchord vchord_bm25 pg_tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="原生 APT 安装 (Debian / Ubuntu)" >}}}}

```bash
# 配置好 Pigsty APT 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo apt-get update
sudo apt-get install -y \\
  postgresql-18-vchord \\
  postgresql-18-vchord-bm25 \\
  postgresql-18-pg-tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="原生 DNF / YUM 安装 (EL 8 / 9 / 10)" >}}}}

```bash
# 配置好 Pigsty YUM 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo dnf install -y \\
  vchord_18 \\
  vchord_bm25_18 \\
  pg_tokenizer_18
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 2 · 配置预加载库并启用扩展 {{#enable}}

三个扩展均需先将动态库加入 `shared_preload_libraries` 并重启 PostgreSQL 服务，再在目标数据库中执行 `CREATE EXTENSION`：

```sql
-- 1. 通过 ALTER SYSTEM 将扩展动态库写入 postgresql.auto.conf
ALTER SYSTEM SET shared_preload_libraries = 'vchord.so, vchord_bm25.so, pg_tokenizer.so';
```

重启 PostgreSQL 实例（例如 `sudo systemctl restart postgresql-18` 或 `pig pg restart`），然后连接目标数据库启用扩展：

```sql
-- 2. 在目标数据库中创建扩展（CASCADE 会为 vchord 自动启用 pgvector 依赖）
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

### 3 · 容器镜像（历史上游参考） {{#docker}}

> [!WARNING]
> **历史上游镜像说明**：PGSTY 不发布包含 `vchord 1.5.0`、`vchord_bm25 1.3.0` 或 `pg_tokenizer 1.3.0` 的容器镜像。下方上游 TensorChord 镜像仅包含旧版本，仅供本地参考；当前生产部署请使用 Pigsty 软件包或 GitHub Release 构建产物。

{{{{< tabs >}}}}
{{{{< tab label="Vchord 全家桶镜像（历史版本）" >}}}}

```bash
# 历史上游镜像（PostgreSQL 18 + 旧版 VectorChord 套件）
docker run -d \\
  --name vchord-suite \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  tensorchord/vchord-suite:pg18-latest
```

{{{{< /tab >}}}}
{{{{< tab label="vchord 独立镜像（历史 v1.1.1）" >}}}}

```bash
# 历史上游镜像（PostgreSQL 18 + pgvector + VectorChord 1.1.1）
docker run -d \\
  --name vchord-postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 4 · 版本与目录总览 {{#releases}}

| **扩展名称** | **文档对应的源码版本** | **Pigsty 软件源版本** | **技术文档** | **PGEXT 扩展目录** | **GitHub 发行版** |
|:---|:---:|:---:|:---|:---|:---|
| **`vchord`** | `v{RELEASE_VERSIONS['vchord']}` | `{vc['repo_version']}` | [vchord 文档](/zh/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v{RELEASE_VERSIONS['vchord_bm25']}` | `{bm['repo_version']}` | [vchord_bm25 文档](/zh/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v{RELEASE_VERSIONS['pg_tokenizer']}` | `{tk['repo_version']}` | [pg_tokenizer 文档](/zh/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{{.wide .expand}}

---

## 1 · `vchord` —— 可扩展向量检索引擎 {{#vchord}}

**`vchord`**（`v{RELEASE_VERSIONS['vchord']}`）提供 `vchordrq`（RaBitQ 倒排索引）与 `vchordg`（单层 RaBitQ 图索引）两种索引访问方法、`rabitq4`/`rabitq8` 量化向量类型、球面检索以及 `@#` MaxSim 多向量操作符，依赖基础扩展 `vector`（[`pgvector`](/zh/docs/vector/)）。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "最新 GitHub 发行版" "blue" >}}}} | [`vchord`](/zh/docs/vchord/) | `{RELEASE_VERSIONS['vchord']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | [`vector`](/zh/docs/vector/) | [GitHub Release 1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0) | {{{{< bg "AGPL-3.0" "许可证: AGPL-3.0-only" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `vchord_$v` | [各平台版本](#vchord-packages) | [兼容矩阵](#vchord-matrix) | `pgvector_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-vchord` | [各平台版本](#vchord-packages) | [兼容矩阵](#vchord-matrix) | `postgresql-$v-pgvector` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`vchord`) {{#vchord-matrix}}

{vc['matrix_zh']}

### 软件包下载列表 (`vchord`) {{#vchord-packages}}

{vc['packages_zh']}

---

## 2 · `vchord_bm25` —— 原生 BM25 全文排序索引 {{#vchord_bm25}}

**`vchord_bm25`**（`v{RELEASE_VERSIONS['vchord_bm25']}`）面向 PostgreSQL 原生 `tsvector` 列提供 Okapi BM25 全文相关性排序索引（`USING bm25`）与 Block-WeakAnd 块级剪枝扫描（`<&>` 操作符）。任意 `1.x` 版本均可通过 `ALTER EXTENSION vchord_bm25 UPDATE` 原地升级；从历史 `0.3.x` 升级请遵循[迁移指南](/zh/docs/bm25/reference/migration/)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "最新 GitHub 发行版" "blue" >}}}} | [`vchord_bm25`](/zh/docs/bm25/) | `{RELEASE_VERSIONS['vchord_bm25']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | `-` | [GitHub Release 1.3.0](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) | {{{{< bg "AGPL-3.0" "许可证: AGPL-3.0-only" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `vchord_bm25_$v` | [各平台版本](#vchord_bm25-packages) | [兼容矩阵](#vchord_bm25-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-vchord-bm25` | [各平台版本](#vchord_bm25-packages) | [兼容矩阵](#vchord_bm25-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`vchord_bm25`) {{#vchord_bm25-matrix}}

{bm['matrix_zh']}

### 软件包下载列表 (`vchord_bm25`) {{#vchord_bm25-packages}}

{bm['packages_zh']}

---

## 3 · `pg_tokenizer` —— 多语言文本分析与分词器 {{#pg_tokenizer}}

**`pg_tokenizer`**（`v{RELEASE_VERSIONS['pg_tokenizer']}`）提供可组合的数据库内多语言文本分析流水线、预分词器（Unicode、结巴中文、Lindera 7 日文）、Snowball 词干提取、停用词/同义词过滤器、原生 C `tsvector` 生成函数与词表编码模型。在 PostgreSQL 15–19 上执行 `ALTER EXTENSION pg_tokenizer UPDATE` 即可升级；跨越更早版本请见[升级说明](/zh/docs/tokenizer/installation/#upgrading)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "最新 GitHub 发行版" "blue" >}}}} | [`pg_tokenizer`](/zh/docs/tokenizer/) | `{RELEASE_VERSIONS['pg_tokenizer']}` | {{{{< pgver "19,18,17,16,15" "g,g,g,g,g" >}}}} | `-` | [GitHub Release v1.3.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) | {{{{< bg "Apache-2.0" "许可证: Apache-2.0" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `pg_tokenizer_$v` | [各平台版本](#pg_tokenizer-packages) | [兼容矩阵](#pg_tokenizer-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.0)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-pg-tokenizer` | [各平台版本](#pg_tokenizer-packages) | [兼容矩阵](#pg_tokenizer-matrix) | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "Rust (pgrx 0.20.0)" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`pg_tokenizer`) {{#pg_tokenizer-matrix}}

{tk['matrix_zh']}

### 软件包下载列表 (`pg_tokenizer`) {{#pg_tokenizer-packages}}

{tk['packages_zh']}

---

## 签名校验与构建仓库 {{#source}}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范仓库透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{{.wide .expand}}
"""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    site = Path(os.environ.get("PGEXT_SITE_DIR") or root.parent / "pgext.cloud").expanduser()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pgext-dir",
        type=Path,
        default=site / "content" / "e",
        help="Extension page directory (default: content/e under PGEXT_SITE_DIR or the sibling pgext.cloud checkout)",
    )
    args = parser.parse_args()

    data: dict[str, dict[str, str]] = {}
    for ext in EXTENSIONS:
        md_path = args.pgext_dir / f"{ext}.md"
        if not md_path.is_file():
            raise FileNotFoundError(f"Missing pgext source file: {md_path}")
        data[ext] = parse_pgext_markdown(md_path)

    en_out = root / "content" / "download.md"
    zh_out = root / "content" / "download.zh.md"
    en_out.write_text(build_en(data), encoding="utf-8")
    zh_out.write_text(build_zh(data), encoding="utf-8")
    print(f"Synced {en_out} and {zh_out} from {args.pgext_dir}")


if __name__ == "__main__":
    main()
