---
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

{{< cards >}}
{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v1.5.0" >}}
可扩展、磁盘友好型 PostgreSQL 向量相似性检索核心扩展，基于 `pgvector` 构建，提供带过滤键的 RaBitQ `vchordrq` 倒排索引、`vchordg` 单层图索引、球面检索与 MaxSim（`@#`）多向量检索，支持 PostgreSQL 15–19。
{{< /card >}}
{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v1.3.0" >}}
面向 PostgreSQL 原生 `tsvector` 列的 Okapi BM25 全文相关性排序扩展，采用 Block-WeakAnd 块级剪枝索引（`USING bm25`）与 `<&>` 操作符加速 Top-K 检索，支持 PostgreSQL 15–19。
{{< /card >}}
{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v1.3.0" >}}
独立运行的数据库内多语言文本分析与词元 ID 编码扩展，内置结巴中文、Lindera 7 日文、Unicode 分词、Snowball 词干提取、停用词/同义词过滤以及预训练与语料训练词表模型，支持 PostgreSQL 15–19。
{{< /card >}}
{{< /cards >}}

---

## 快速安装指南 {#install}

### 1 · 使用 PIG 包管理器安装（推荐） {#pig}

推荐使用由 [PGSTY](https://pigsty.cc/) 维护的 PostgreSQL 包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 Vchord 扩展套件。`pig` 是零依赖的静态编译 Go 命令行工具，可自动识别 Linux 发行版与 CPU 架构、配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动安装 `pgvector` 等扩展依赖。

{{< tabs >}}
{{< tab label="中国大陆镜像（推荐）" >}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（启用中国大陆 CDN 镜像）并刷新缓存
pig repo add pgsql -u -r china

# 3. 安装 vchord、vchord_bm25 与 pg_tokenizer（自动匹配当前 PG 版本，或通过 -v 18 指定）
pig install vchord vchord_bm25 pg_tokenizer
```

{{< /tab >}}
{{< tab label="全球默认源" >}}

```bash
# 1. 安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库并刷新缓存
pig repo add pgsql -u

# 3. 安装 vchord、vchord_bm25 与 pg_tokenizer（可通过 -v 18 显式指定 PostgreSQL 大版本）
pig install vchord vchord_bm25 pg_tokenizer
```

{{< /tab >}}
{{< tab label="原生 APT 安装 (Debian / Ubuntu)" >}}

```bash
# 配置好 Pigsty APT 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo apt-get update
sudo apt-get install -y \
  postgresql-18-vchord \
  postgresql-18-vchord-bm25 \
  postgresql-18-pg-tokenizer
```

{{< /tab >}}
{{< tab label="原生 DNF / YUM 安装 (EL 8 / 9 / 10)" >}}

```bash
# 配置好 Pigsty YUM 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo dnf install -y \
  vchord_18 \
  vchord_bm25_18 \
  pg_tokenizer_18
```

{{< /tab >}}
{{< /tabs >}}

### 2 · 配置预加载库并启用扩展 {#enable}

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

### 3 · 容器镜像（历史上游参考） {#docker}

> [!WARNING]
> **历史上游镜像说明**：PGSTY 不发布包含 `vchord 1.5.0`、`vchord_bm25 1.3.0` 或 `pg_tokenizer 1.3.0` 的容器镜像。下方上游 TensorChord 镜像仅包含旧版本，仅供本地参考；当前生产部署请使用 Pigsty 软件包或 GitHub Release 构建产物。

{{< tabs >}}
{{< tab label="Vchord 全家桶镜像（历史版本）" >}}

```bash
# 历史上游镜像（PostgreSQL 18 + 旧版 VectorChord 套件）
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

{{< /tab >}}
{{< tab label="vchord 独立镜像（历史 v1.1.1）" >}}

```bash
# 历史上游镜像（PostgreSQL 18 + pgvector + VectorChord 1.1.1）
docker run -d \
  --name vchord-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{< /tab >}}
{{< /tabs >}}

### 4 · 版本与目录总览 {#releases}

| **扩展名称** | **文档对应的源码版本** | **Pigsty 软件源版本** | **技术文档** | **PGEXT 扩展目录** | **GitHub 发行版** |
|:---|:---:|:---:|:---|:---|:---|
| **`vchord`** | `v1.5.0` | `1.5.0, 1.3.0` | [vchord 文档](/zh/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v1.3.0` | `1.3.0` | [vchord_bm25 文档](/zh/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v1.3.0` | `1.3.0` | [pg_tokenizer 文档](/zh/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{.wide .expand}

---

## 1 · `vchord` —— 可扩展向量检索引擎 {#vchord}

**`vchord`**（`v1.5.0`）提供 `vchordrq`（RaBitQ 倒排索引）与 `vchordg`（单层 RaBitQ 图索引）两种索引访问方法、`rabitq4`/`rabitq8` 量化向量类型、球面检索以及 `@#` MaxSim 多向量操作符，依赖基础扩展 `vector`（[`pgvector`](/zh/docs/vector/)）。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "最新 GitHub 发行版" "blue" >}} | [`vchord`](/zh/docs/vchord/) | `1.5.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | [`vector`](/zh/docs/vector/) | [GitHub Release 1.5.0](https://github.com/pgsty/vchord/releases/tag/1.5.0) | {{< bg "AGPL-3.0" "许可证: AGPL-3.0-only" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `vchord_$v` | [各平台版本](#vchord-packages) | [兼容矩阵](#vchord-matrix) | `pgvector_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-vchord` | [各平台版本](#vchord-packages) | [兼容矩阵](#vchord-matrix) | `postgresql-$v-pgvector` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}} |
{.packages .wide .expand}

### 可用性矩阵 (`vchord`) {#vchord-matrix}

| **系统平台 / PG 版本** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
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

### 软件包下载列表 (`vchord`) {#vchord-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 2 · `vchord_bm25` —— 原生 BM25 全文排序索引 {#vchord_bm25}

**`vchord_bm25`**（`v1.3.0`）面向 PostgreSQL 原生 `tsvector` 列提供 Okapi BM25 全文相关性排序索引（`USING bm25`）与 Block-WeakAnd 块级剪枝扫描（`<&>` 操作符）。任意 `1.x` 版本均可通过 `ALTER EXTENSION vchord_bm25 UPDATE` 原地升级；从历史 `0.3.x` 升级请遵循[迁移指南](/zh/docs/bm25/reference/migration/)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "最新 GitHub 发行版" "blue" >}} | [`vchord_bm25`](/zh/docs/bm25/) | `1.3.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | `-` | [GitHub Release 1.3.0](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) | {{< bg "AGPL-3.0" "许可证: AGPL-3.0-only" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `vchord_bm25_$v` | [各平台版本](#vchord_bm25-packages) | [兼容矩阵](#vchord_bm25-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-vchord-bm25` | [各平台版本](#vchord_bm25-packages) | [兼容矩阵](#vchord_bm25-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.1)" "orange" >}} |
{.packages .wide .expand}

### 可用性矩阵 (`vchord_bm25`) {#vchord_bm25-matrix}

| **系统平台 / PG 版本** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
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

### 软件包下载列表 (`vchord_bm25`) {#vchord_bm25-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 3 · `pg_tokenizer` —— 多语言文本分析与分词器 {#pg_tokenizer}

**`pg_tokenizer`**（`v1.3.0`）提供可组合的数据库内多语言文本分析流水线、预分词器（Unicode、结巴中文、Lindera 7 日文）、Snowball 词干提取、停用词/同义词过滤器、原生 C `tsvector` 生成函数与词表编码模型。在 PostgreSQL 15–19 上执行 `ALTER EXTENSION pg_tokenizer UPDATE` 即可升级；跨越更早版本请见[升级说明](/zh/docs/tokenizer/installation/#upgrading)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **发布渠道** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "最新 GitHub 发行版" "blue" >}} | [`pg_tokenizer`](/zh/docs/tokenizer/) | `1.3.0` | {{< pgver "19,18,17,16,15" "g,g,g,g,g" >}} | `-` | [GitHub Release v1.3.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0) | {{< bg "Apache-2.0" "许可证: Apache-2.0" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `pg_tokenizer_$v` | [各平台版本](#pg_tokenizer-packages) | [兼容矩阵](#pg_tokenizer-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.0)" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-pg-tokenizer` | [各平台版本](#pg_tokenizer-packages) | [兼容矩阵](#pg_tokenizer-matrix) | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "Rust (pgrx 0.20.0)" "orange" >}} |
{.packages .wide .expand}

### 可用性矩阵 (`pg_tokenizer`) {#pg_tokenizer-matrix}

| **系统平台 / PG 版本** |                  **PG19**                   |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |
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

### 软件包下载列表 (`pg_tokenizer`) {#pg_tokenizer-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG19" value="pg19" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 签名校验与构建仓库 {#source}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范仓库透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{.wide .expand}
