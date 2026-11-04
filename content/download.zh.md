---
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

{{< cards >}}
{{< card title="vchord" link="#vchord" icon="fa-solid fa-layer-group" badge="v1.2.0" >}}
新一代可扩展、磁盘友好型 PostgreSQL 向量相似性检索核心扩展，基于 `pgvector` 构建，提供 RaBitQ 量化的 `vchordrq` 倒排索引、`vchordg` 高吞吐图索引与 MaxSim（`@#`）多向量检索，全面支持 PostgreSQL 14–18。
{{< /card >}}
{{< card title="vchord_bm25" link="#vchord_bm25" icon="fa-solid fa-magnifying-glass" badge="v1.0.0" >}}
PostgreSQL 原生 Okapi BM25 全文相关性排序核心扩展，采用 Block-WeakAnd 块级剪枝索引（`USING bm25`）与 `<&>` 操作符加速 Top-K 词法检索，可与 `vchord` 无缝构建混合检索，全面支持 PostgreSQL 14–18。
{{< /card >}}
{{< card title="pg_tokenizer" link="#pg_tokenizer" icon="fa-solid fa-language" badge="v1.0.0" >}}
独立运行的数据库内多语言文本分析与词元 ID 编码核心扩展，内置结巴中文、Lindera 日文、Unicode 分词、Snowball 词干提取、停用词/同义词过滤以及预训练与语料训练词表模型，全面支持 PostgreSQL 14–18。
{{< /card >}}
{{< /cards >}}

---

## 快速安装指南 {#install}

### 1 · 使用 PIG 包管理器安装（推荐） {#pig}

我们强烈推荐使用由 [PGSTY](https://pigsty.cc/) 社区维护的 PostgreSQL 专属包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 Vchord 扩展套件。`pig` 是零依赖的静态编译 Go 命令行工具，能够自动识别当前 Linux 发行版与 CPU 架构、一键配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动处理 `pgvector` 等扩展依赖关系。

{{< tabs >}}
{{< tab label="中国大陆镜像（推荐）" >}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（自动启用中国大陆 CDN 镜像）并刷新缓存
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

### 3 · Docker 容器镜像（Obsolete） {#docker}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 维护版本的 Docker 和 Kubernetes 镜像尚未发布。以下上游说明仅供参考，后续更新。

如果用于本地快速评估、CI 流水线或容器化部署，可以直接运行已预装并配置好预加载库的官方 Docker 镜像：

{{< tabs >}}
{{< tab label="Vchord 全家桶镜像 (All-in-One)" >}}

```bash
# 预装并启用 PostgreSQL 18 + pgvector + vchord + vchord_bm25 + pg_tokenizer
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

{{< /tab >}}
{{< tab label="vchord 独立镜像 (仅向量检索)" >}}

```bash
# 预装并启用 PostgreSQL 18 + pgvector + vchord v1.1.1
docker run -d \
  --name vchord-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  ghcr.io/tensorchord/vchord-postgres:pg18-v1.1.1
```

{{< /tab >}}
{{< /tabs >}}

### 4 · GitHub 发行版 {#releases}

| **扩展名称** | **当前正式版本** | **技术文档** | **PGEXT 扩展目录** | **Pigsty 扩展页** | **GitHub 仓库与发行版** |
|:---|:---:|:---|:---|:---|:---|
| **`vchord`** | `v1.2.0` | [vchord 文档](/zh/docs/vchord/) | [pgext.cloud/e/vchord](https://pgext.cloud/e/vchord) | [pigsty.cc/ext/e/vchord](https://pigsty.cc/ext/e/vchord/) | [pgsty/vchord](https://github.com/pgsty/vchord/releases) |
| **`vchord_bm25`** | `v1.0.0` | [vchord_bm25 文档](/zh/docs/bm25/) | [pgext.cloud/e/vchord_bm25](https://pgext.cloud/e/vchord_bm25) | [pigsty.cc/ext/e/vchord_bm25](https://pigsty.cc/ext/e/vchord_bm25/) | [pgsty/vchord_bm25](https://github.com/pgsty/vchord_bm25/releases) |
| **`pg_tokenizer`** | `v1.0.0` | [pg_tokenizer 文档](/zh/docs/tokenizer/) | [pgext.cloud/e/pg_tokenizer](https://pgext.cloud/e/pg_tokenizer) | [pigsty.cc/ext/e/pg_tokenizer](https://pigsty.cc/ext/e/pg_tokenizer/) | [pgsty/pg_tokenizer](https://github.com/pgsty/pg_tokenizer/releases) |
{.wide .expand}

---

## 1 · `vchord` —— 可扩展向量检索引擎 {#vchord}

**`vchord`**（`v1.2.0`）是套件的核心向量相似性检索扩展，提供 `vchordrq`（RaBitQ 倒排索引）与 `vchordg`（单层图索引）两种访问方法，依赖基础扩展 `vector`（[`pgvector`](/zh/docs/vector/)）。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL 扩展" "blue" >}} | [`vchord`](/zh/docs/vchord/) | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | [`vector`](/zh/docs/vector/) | [PGEXT #1810](https://pgext.cloud/e/vchord) | {{< bg "AGPL-3.0" "许可证: AGPL-3.0" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `vchord_$v` | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pgvector_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-vchord` | `1.2.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `postgresql-$v-pgvector` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
{.packages .wide}

### 可用性矩阵 (`vchord`) {#vchord-matrix}

| **系统平台 / PG 版本** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
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
{.matrix .wide}

### 软件包下载列表 (`vchord`) {#vchord-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 2 · `vchord_bm25` —— 原生 BM25 全文排序索引 {#vchord_bm25}

**`vchord_bm25`**（`v1.0.0`）在 PostgreSQL 内提供原生 Okapi BM25 全文相关性排序索引（`USING bm25`）与 Block-WeakAnd 块级剪枝扫描（`<&>` 操作符）。从 0.3.x 升级到 1.0.0 请参阅[迁移指南](/zh/docs/bm25/reference/migration/)。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL 扩展" "blue" >}} | [`vchord_bm25`](/zh/docs/bm25/) | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | [PGEXT #2160](https://pgext.cloud/e/vchord_bm25) | {{< bg "AGPL-3.0" "许可证: AGPL-3.0" "red" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `vchord_bm25_$v` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-vchord-bm25` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
{.packages .wide}

### 可用性矩阵 (`vchord_bm25`) {#vchord_bm25-matrix}

| **系统平台 / PG 版本** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
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
{.matrix .wide}

### 软件包下载列表 (`vchord_bm25`) {#vchord_bm25-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 3 · `pg_tokenizer` —— 多语言文本分析与分词器 {#pg_tokenizer}

**`pg_tokenizer`**（`v1.0.0`）提供可组合的数据库内多语言文本分析流水线、预分词器（Unicode、结巴中文、Lindera 日文）、词干提取、停用词/同义词过滤器与词表编码模型。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL 扩展" "blue" >}} | [`pg_tokenizer`](/zh/docs/tokenizer/) | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | [PGEXT #2170](https://pgext.cloud/e/pg_tokenizer) | {{< bg "Apache-2.0" "许可证: Apache-2.0" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `pg_tokenizer_$v` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-pg-tokenizer` | `1.0.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `-` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx) 编写" "orange" >}} |
{.packages .wide}

### 可用性矩阵 (`pg_tokenizer`) {#pg_tokenizer-matrix}

| **系统平台 / PG 版本** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
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
{.matrix .wide}

### 软件包下载列表 (`pg_tokenizer`) {#pg_tokenizer-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 签名校验与构建仓库 {#source}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（支持管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{.wide .expand}
