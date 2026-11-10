#!/usr/bin/env python3
"""Synchronize package availability matrices and download tables from pgext into content/download.{md,zh.md}."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EXTENSIONS = ("vchord", "vchord_bm25", "pg_tokenizer")
RELEASE_VERSIONS = {"vchord": "1.2.0", "vchord_bm25": "1.0.0", "pg_tokenizer": "1.0.0"}



def table_reader_attributes(match: re.Match[str]) -> str:
    """Preserve source table attributes and add missing reader opt-ins."""
    attributes = match.group(1)
    classes = set(re.findall(r"(?:^|\s)\.([\w-]+)", attributes))
    missing = [name for name in ("wide", "expand") if name not in classes]
    return "{" + attributes.rstrip() + "".join(" ." + name for name in missing) + "}"


def parse_pgext_markdown(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")

    version_match = re.search(r"\|\s*\*\*EXT\*\*\s*\|[^|]+\|\s*`([^`]+)`\s*\|", text)
    version = version_match.group(1) if version_match else ""
    target_version = RELEASE_VERSIONS.get(path.stem, version)
    if version and target_version and version != target_version:
        text = re.sub(
            rf"{re.escape(version)}-\d+PIGSTY",
            f"{target_version}-1PIGSTY",
            text,
        )
        text = text.replace(f"PIGSTY {version}", f"PIGSTY {target_version}")
        text = text.replace(f"`{version}`", f"`{target_version}`")
        version = target_version

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
        "version": version,
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

**vchord 1.3.0** is available from the [GitHub release](https://github.com/pgsty/vchord/releases/tag/1.3.0) as Linux ZIP and Debian packages for PostgreSQL 14–18 on x86_64/aarch64 (glibc 2.35+). The distribution-repository tables below still describe 1.2.0. See the [upgrade notes](/blog/release/vchord-1.3.0/).

{{{{< cards >}}}}
{{{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v{RELEASE_VERSIONS['vchord']}" >}}}}
Scalable, fast, and disk-friendly vector similarity search extension built on `pgvector`, providing RaBitQ-compressed `vchordrq` (IVF) and `vchordg` (graph) indexes, multi-vector MaxSim (`@#`), and sphere search across PostgreSQL 14–18.
{{{{< /card >}}}}
{{{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v{RELEASE_VERSIONS['vchord_bm25']}" >}}}}
Native Okapi BM25 full-text ranking index extension powered by Block-WeakAnd block-level WAND pruning and the `<&>` operator, delivering high-throughput lexical Top-K retrieval and hybrid search across PostgreSQL 14–18.
{{{{< /card >}}}}
{{{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v{RELEASE_VERSIONS['pg_tokenizer']}" >}}}}
Standalone in-database multilingual text analyzer and token-ID encoder supporting Unicode segmentation, Jieba (Chinese), Lindera (Japanese), Snowball stemming, HuggingFace vocabularies, and corpus-trained custom models across PostgreSQL 14–18.
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## Quick Installation {{#install}}

### 1 · Install with PIG Package Manager (Recommended) {{#pig}}

We strongly recommend installing the Vchord extension suite with [**`pig`**](https://pig.pgsty.com/) — the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` is a single static Go binary that automatically detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and resolves extension dependencies (`pgvector`) in one command.

{{{{< tabs >}}}}
{{{{< tab label="Global (Default)" >}}}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update repo cache
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

# 3. Install vchord, vchord_bm25, and pg_tokenizer (or specify PG major version with -v 18)
pig install vchord vchord_bm25 pg_tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="Native APT (Debian / Ubuntu)" >}}}}

```bash
# Once the Pigsty APT repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo apt-get update
sudo apt-get install -y \\
  postgresql-18-vchord \\
  postgresql-18-vchord-bm25 \\
  postgresql-18-pg-tokenizer
```

{{{{< /tab >}}}}
{{{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}}}

```bash
# Once the Pigsty YUM repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo dnf install -y \\
  vchord_18 \\
  vchord_bm25_18 \\
  pg_tokenizer_18
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 2 · Preload Shared Libraries & Enable Extensions {{#enable}}

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

### 3 · Container Images (Obsolete) {{#docker}}

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for its maintained releases. These upstream instructions are retained for reference and will be updated.

For local evaluation, CI pipelines, or containerized deployments, official Docker images come with PostgreSQL 18 and the extensions pre-installed and preloaded:

{{{{< tabs >}}}}
{{{{< tab label="Vchord Suite (All-in-One)" >}}}}

```bash
# Includes PostgreSQL 18 + pgvector + vchord + vchord_bm25 + pg_tokenizer
docker run -d \\
  --name vchord-suite \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  tensorchord/vchord-suite:pg18-latest
```

{{{{< /tab >}}}}
{{{{< tab label="vchord Only (Vector Search)" >}}}}

```bash
# Includes PostgreSQL 18 + pgvector + vchord v1.1.1
docker run -d \\
  --name vchord-postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 4 · GitHub Releases {{#releases}}

| **Extension** | **Current Release** | **Documentation** | **PGEXT Catalog** | **Pigsty Docs** | **GitHub Repository & Releases** |
|:---|:---:|:---|:---|:---|:---|
| **`vchord`** | `v{RELEASE_VERSIONS['vchord']}` | [vchord Docs](/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pigsty.io/ext/e/vchord](https://pigsty.io/ext/e/vchord/) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v{RELEASE_VERSIONS['vchord_bm25']}` | [vchord_bm25 Docs](/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pigsty.io/ext/e/vchord_bm25](https://pigsty.io/ext/e/vchord_bm25/) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v{RELEASE_VERSIONS['pg_tokenizer']}` | [pg_tokenizer Docs](/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pigsty.io/ext/e/pg_tokenizer](https://pigsty.io/ext/e/pg_tokenizer/) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{{.wide .expand}}

---

## 1 · `vchord` — Scalable Vector Search {{#vchord}}

**`vchord`** (`v{RELEASE_VERSIONS['vchord']}`) is the core RaBitQ-powered vector similarity search extension (`vchordrq` and `vchordg` index access methods). It depends on the `vector` ([`pgvector`](/docs/vector/)) extension.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL Extension" "blue" >}}}} | [`vchord`](/docs/vchord/) | `{RELEASE_VERSIONS['vchord']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | [`vector`](/docs/vector/) | [PGEXT #1810](https://pgext.cloud/e/vchord) | {{{{< bg "AGPL-3.0" "License: AGPL-3.0" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `vchord_$v` | `{vc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pgvector_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-vchord` | `{vc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `postgresql-$v-pgvector` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`vchord`) {{#vchord-matrix}}

{vc['matrix_en']}

### Package Downloads (`vchord`) {{#vchord-packages}}

{vc['packages_en']}

---

## 2 · `vchord_bm25` — Native BM25 Ranking Index {{#vchord_bm25}}

**`vchord_bm25`** (`v{RELEASE_VERSIONS['vchord_bm25']}`) provides native Okapi BM25 full-text ranking indexes (`USING bm25`) and Block-WeakAnd Top-K search (`<&>`) inside PostgreSQL. Upgrading from 0.3.x requires [migration](/docs/bm25/reference/migration/).

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL Extension" "blue" >}}}} | [`vchord_bm25`](/docs/bm25/) | `{RELEASE_VERSIONS['vchord_bm25']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | [PGEXT #2160](https://pgext.cloud/e/vchord_bm25) | {{{{< bg "AGPL-3.0" "License: AGPL-3.0" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `vchord_bm25_$v` | `{bm['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-vchord-bm25` | `{bm['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`vchord_bm25`) {{#vchord_bm25-matrix}}

{bm['matrix_en']}

### Package Downloads (`vchord_bm25`) {{#vchord_bm25-packages}}

{bm['packages_en']}

---

## 3 · `pg_tokenizer` — Multilingual Text Analyzer {{#pg_tokenizer}}

**`pg_tokenizer`** (`v{RELEASE_VERSIONS['pg_tokenizer']}`) provides customizable in-database text analysis pipelines, pre-tokenizers (Unicode, Jieba, Lindera), stemmers, stopword/synonym filters, and vocabulary models.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL Extension" "blue" >}}}} | [`pg_tokenizer`](/docs/tokenizer/) | `{RELEASE_VERSIONS['pg_tokenizer']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | [PGEXT #2170](https://pgext.cloud/e/pg_tokenizer) | {{{{< bg "Apache-2.0" "License: Apache-2.0" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `pg_tokenizer_$v` | `{tk['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-pg-tokenizer` | `{tk['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx)" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`pg_tokenizer`) {{#pg_tokenizer-matrix}}

{tk['matrix_en']}

### Package Downloads (`pg_tokenizer`) {{#pg_tokenizer-packages}}

{tk['packages_en']}

---

## Verification & Build Repositories {{#source}}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` / `apt` once configured via `pig repo add pgsql`. Every package is built transparently from open-source build specs:

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
description: 使用 pig 包管理器、历史 Docker 镜像（Obsolete）或原生 RPM / DEB 软件包，在 16 个 Linux 发行版平台与 PostgreSQL 14–18 上安装 vchord、vchord_bm25 与 pg_tokenizer。
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

Vchord 扩展套件（**`vchord`**、**`vchord_bm25`** 与 **`pg_tokenizer`**）已面向 **16 个 Linux 发行版与 CPU 架构目标**（`el8`、`el9`、`el10`、`d12`、`d13`、`u22`、`u24`、`u26` × `x86_64` / `aarch64`）以及 **PostgreSQL 14、15、16、17、18** 五个大版本构建并发布原生 RPM 与 DEB 软件包（共计 240 个预编译二进制包）。

**vchord 1.3.0** 已在 [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.3.0) 提供 PostgreSQL 14–18、x86_64/aarch64 的 Linux ZIP 与 Debian 包（glibc 2.35+）。下方发行版软件源表格仍对应 1.2.0。升级前请阅读[发布说明](/zh/blog/release/vchord-1.3.0/)。

{{{{< cards >}}}}
{{{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v{RELEASE_VERSIONS['vchord']}" >}}}}
新一代可扩展、磁盘友好型 PostgreSQL 向量相似性检索核心扩展，基于 `pgvector` 构建，提供 RaBitQ 量化的 `vchordrq` 倒排索引、`vchordg` 高吞吐图索引与 MaxSim（`@#`）多向量检索，全面支持 PostgreSQL 14–18。
{{{{< /card >}}}}
{{{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v{RELEASE_VERSIONS['vchord_bm25']}" >}}}}
PostgreSQL 原生 Okapi BM25 全文相关性排序核心扩展，采用 Block-WeakAnd 块级剪枝索引（`USING bm25`）与 `<&>` 操作符加速 Top-K 词法检索，可与 `vchord` 无缝构建混合检索，全面支持 PostgreSQL 14–18。
{{{{< /card >}}}}
{{{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v{RELEASE_VERSIONS['pg_tokenizer']}" >}}}}
独立运行的数据库内多语言文本分析与词元 ID 编码核心扩展，内置结巴中文、Lindera 日文、Unicode 分词、Snowball 词干提取、停用词/同义词过滤以及预训练与语料训练词表模型，全面支持 PostgreSQL 14–18。
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## 快速安装指南 {{#install}}

### 1 · 使用 PIG 包管理器安装（推荐） {{#pig}}

我们强烈推荐使用由 [PGSTY](https://pigsty.cc/) 社区维护的 PostgreSQL 专属包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 Vchord 扩展套件。`pig` 是零依赖的静态编译 Go 命令行工具，能够自动识别当前 Linux 发行版与 CPU 架构、一键配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动处理 `pgvector` 等扩展依赖关系。

{{{{< tabs >}}}}
{{{{< tab label="中国大陆镜像（推荐）" >}}}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（自动启用中国大陆 CDN 镜像）并刷新缓存
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

三个扩展均需在 `shared_preload_libraries` 中注册动态库并重启 PostgreSQL 服务后，方可在数据库内执行 `CREATE EXTENSION`：

```sql
-- 1. 通过 ALTER SYSTEM 将扩展动态库写入 postgresql.auto.conf
ALTER SYSTEM SET shared_preload_libraries = 'vchord.so, vchord_bm25.so, pg_tokenizer.so';
```

重启 PostgreSQL 实例（例如 `sudo systemctl restart postgresql-18` 或 `pig pg restart`），随后连接目标数据库启用扩展：

```sql
-- 2. 在目标数据库中创建扩展（CASCADE 会为 vchord 自动启用 pgvector 依赖）
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

### 3 · Docker 容器镜像（Obsolete） {{#docker}}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 维护版本的 Docker 和 Kubernetes 镜像尚未发布。以下上游说明仅供参考，后续更新。

如果用于本地快速评估、CI 流水线或容器化部署，可以直接运行已预装并配置好预加载库的官方 Docker 镜像：

{{{{< tabs >}}}}
{{{{< tab label="Vchord 全家桶镜像 (All-in-One)" >}}}}

```bash
# 预装并启用 PostgreSQL 18 + pgvector + vchord + vchord_bm25 + pg_tokenizer
docker run -d \\
  --name vchord-suite \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  tensorchord/vchord-suite:pg18-latest
```

{{{{< /tab >}}}}
{{{{< tab label="vchord 独立镜像 (仅向量检索)" >}}}}

```bash
# 预装并启用 PostgreSQL 18 + pgvector + vchord v1.1.1
docker run -d \\
  --name vchord-postgres \\
  -e POSTGRES_PASSWORD=postgres \\
  -p 5432:5432 \\
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 4 · GitHub 发行版 {{#releases}}

| **扩展名称** | **当前正式版本** | **技术文档** | **PGEXT 扩展目录** | **Pigsty 扩展页** | **GitHub 仓库与发行版** |
|:---|:---:|:---|:---|:---|:---|
| **`vchord`** | `v{RELEASE_VERSIONS['vchord']}` | [vchord 文档](/zh/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pigsty.cc/ext/e/vchord](https://pigsty.cc/ext/e/vchord/) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v{RELEASE_VERSIONS['vchord_bm25']}` | [vchord_bm25 文档](/zh/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pigsty.cc/ext/e/vchord_bm25](https://pigsty.cc/ext/e/vchord_bm25/) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v{RELEASE_VERSIONS['pg_tokenizer']}` | [pg_tokenizer 文档](/zh/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pigsty.cc/ext/e/pg_tokenizer](https://pigsty.cc/ext/e/pg_tokenizer/) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{{.wide .expand}}

---

## 1 · `vchord` —— 可扩展向量检索引擎 {{#vchord}}

**`vchord`**（`v{RELEASE_VERSIONS['vchord']}`）是套件的核心向量相似性检索扩展，提供 `vchordrq`（RaBitQ 倒排索引）与 `vchordg`（单层图索引）两种访问方法，依赖基础扩展 `vector`（[`pgvector`](/zh/docs/vector/)）。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL 扩展" "blue" >}}}} | [`vchord`](/zh/docs/vchord/) | `{RELEASE_VERSIONS['vchord']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | [`vector`](/zh/docs/vector/) | [PGEXT #1810](https://pgext.cloud/e/vchord) | {{{{< bg "AGPL-3.0" "许可证: AGPL-3.0" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `vchord_$v` | `{vc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pgvector_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-vchord` | `{vc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `postgresql-$v-pgvector` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`vchord`) {{#vchord-matrix}}

{vc['matrix_zh']}

### 软件包下载列表 (`vchord`) {{#vchord-packages}}

{vc['packages_zh']}

---

## 2 · `vchord_bm25` —— 原生 BM25 全文排序索引 {{#vchord_bm25}}

**`vchord_bm25`**（`v{RELEASE_VERSIONS['vchord_bm25']}`）在 PostgreSQL 内提供原生 Okapi BM25 全文相关性排序索引（`USING bm25`）与 Block-WeakAnd 块级剪枝扫描（`<&>` 操作符）。从 0.3.x 升级到 1.0.0 请参阅[迁移指南](/zh/docs/bm25/reference/migration/)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL 扩展" "blue" >}}}} | [`vchord_bm25`](/zh/docs/bm25/) | `{RELEASE_VERSIONS['vchord_bm25']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | [PGEXT #2160](https://pgext.cloud/e/vchord_bm25) | {{{{< bg "AGPL-3.0" "许可证: AGPL-3.0" "red" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `vchord_bm25_$v` | `{bm['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-vchord-bm25` | `{bm['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`vchord_bm25`) {{#vchord_bm25-matrix}}

{bm['matrix_zh']}

### 软件包下载列表 (`vchord_bm25`) {{#vchord_bm25-packages}}

{bm['packages_zh']}

---

## 3 · `pg_tokenizer` —— 多语言文本分析与分词器 {{#pg_tokenizer}}

**`pg_tokenizer`**（`v{RELEASE_VERSIONS['pg_tokenizer']}`）提供可组合的数据库内多语言文本分析流水线、预分词器（Unicode、结巴中文、Lindera 日文）、词干提取、停用词/同义词过滤器与词表编码模型。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL 扩展" "blue" >}}}} | [`pg_tokenizer`](/zh/docs/tokenizer/) | `{RELEASE_VERSIONS['pg_tokenizer']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | [PGEXT #2170](https://pgext.cloud/e/pg_tokenizer) | {{{{< bg "Apache-2.0" "许可证: Apache-2.0" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `pg_tokenizer_$v` | `{tk['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-pg-tokenizer` | `{tk['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `-` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`pg_tokenizer`) {{#pg_tokenizer-matrix}}

{tk['matrix_zh']}

### 软件包下载列表 (`pg_tokenizer`) {{#pg_tokenizer-packages}}

{tk['packages_zh']}

---

## 签名校验与构建仓库 {{#source}}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（支持管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{{.wide .expand}}
"""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pgext-dir",
        type=Path,
        default=root.parent / "pgext" / "content" / "e",
        help="Path to pgext/content/e directory",
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
