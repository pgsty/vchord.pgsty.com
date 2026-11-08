---
title: "安装指南"
description: "通过 Pigsty、Docker、Debian 软件包或源码编译安装 VectorChord-BM25 (vchord_bm25) 与 pg_tokenizer。"
weight: 20
icon: fa-solid fa-download
---

> [!IMPORTANT]
> **1.1.0** 是当前 PGSTY 版本，沿用 1.0.0 引入的原生 `tsvector` API 与格式 4，健康的 1.0.0 索引可以原地升级且无需重建。标注 0.3.x 的 `bm25vector` 示例仅适用于旧版；更换动态库前请阅读[迁移指南](/zh/docs/bm25/reference/migration/)。


`vchord_bm25` 支持 Linux（`x86_64` 与 `aarch64`）及 macOS 平台上的 **PostgreSQL 14、15、16、17 和 18**。

## 方式一：Pigsty / 原生操作系统软件包（推荐） {#method-1-pigsty--native-os-packages-recommended}

[**Pigsty**](https://pgsty.com) 为 EL 8/9/10、Debian 12/13 以及 Ubuntu 22.04/24.04/26.04 上的 PostgreSQL 14–18 提供了预构建的 `vchord`、`vchord_bm25` 和 `pg_tokenizer` 原生 RPM 与 DEB 软件包。请选择与目标发行版、PostgreSQL 主版本和 CPU 架构匹配的软件包。

```bash
# 通过 Pigsty CLI 安装（自动识别 PG 版本与操作系统发行版）
pig ext install vchord_bm25
pig ext install pg_tokenizer
```

配置好 Pigsty 软件源后，也可以直接通过 `apt` 或 `dnf` 安装：

```bash
# Debian / Ubuntu（将 17 替换为你的 PostgreSQL 主版本号）
sudo apt-get install postgresql-17-vchord-bm25 postgresql-17-pg-tokenizer

# RHEL / Rocky / AlmaLinux（将 17 替换为你的 PostgreSQL 主版本号）
sudo dnf install vchord_bm25_17 pg_tokenizer_17
```

## 方式二：Docker（`tensorchord/vchord-suite`） {#method-2-docker-tensorchordvchord-suite}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 维护版本的 Docker 和 Kubernetes 镜像尚未发布。以下上游说明仅供参考，后续更新。

官方 `tensorchord/vchord-suite` Docker 镜像开箱即用地集成了 **PostgreSQL**、**VectorChord (`vchord`)**、**VectorChord-BM25 (`vchord_bm25`)** 以及 **`pg_tokenizer`**：

```bash
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
```

> [!NOTE]
> 你也可以从 GitHub Container Registry 拉取镜像：`ghcr.io/tensorchord/vchord-suite:pg18-latest`（或 `pg17-latest`、`pg16-latest`、`pg15-latest`、`pg14-latest`）。

使用 `psql` 连接数据库：

```bash
psql -h localhost -p 5432 -U postgres
```

## 方式三：GitHub Release 发行归档（`.deb` 与 `.zip`） {#method-3-github-release-deb-packages}

从 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 的 GitHub Releases 页面下载与你的 PostgreSQL 主版本（`14`–`18`）和 CPU 架构（`amd64` / `x86_64` 或 `arm64` / `aarch64`）匹配的发行归档。`.deb` 必须匹配确切的 Debian/Ubuntu 发行版；ZIP 不包含软件包管理器依赖元数据，安装前必须验证目标主机的 libc 兼容性。EL 系统有对应原生 RPM 时应优先使用 RPM：

### Debian / Ubuntu（`.deb`） {#debian--ubuntu-deb}

```bash
# 安装 vchord_bm25（以 x86_64 上的 PostgreSQL 16 为例）
curl -LO https://github.com/pgsty/vchord_bm25/releases/download/1.1.0/postgresql-16-vchord-bm25_1.1.0-1_amd64.deb
sudo apt-get install ./postgresql-16-vchord-bm25_1.1.0-1_amd64.deb

# 安装 pg_tokenizer 1.0.0（以 x86_64 上的 PostgreSQL 16 为例）
curl -LO https://github.com/pgsty/pg_tokenizer/releases/download/v1.0.0/postgresql-16-pg-tokenizer_1.0.0-1_amd64.deb
sudo apt-get install ./postgresql-16-pg-tokenizer_1.0.0-1_amd64.deb
```

### 手工安装 ZIP 归档 {#rhel-9--enterprise-linux-zip-archive}

如果没有匹配的原生软件包，可以在确认 PostgreSQL 主版本、CPU 架构和目标系统 libc 兼容后手工安装 ZIP 归档：

```bash
# 1. 查询 PostgreSQL 的动态库目录与扩展共享目录
pg_config --pkglibdir
# 示例输出：/usr/pgsql-16/lib
pg_config --sharedir
# 示例输出：/usr/pgsql-16/share

# 2. 下载并解压发布归档包
wget https://github.com/pgsty/pg_tokenizer/releases/download/v1.0.0/postgresql-16-pg-tokenizer_1.0.0_x86_64-linux-gnu.zip
unzip postgresql-16-pg-tokenizer_1.0.0_x86_64-linux-gnu.zip -d pg_tokenizer

# 3. 拷贝共享库 (.so) 与扩展控制/SQL 脚本文件
sudo cp ./pg_tokenizer/pg_tokenizer.so $(pg_config --pkglibdir)
sudo cp ./pg_tokenizer/pg_tokenizer.control ./pg_tokenizer/pg_tokenizer--*.sql $(pg_config --sharedir)/extension
```

## 方式四：从源码编译 {#method-4-build-from-source-cargo-pgrx}

如需从源码编译 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)：

```bash
# 1. 安装 Rust 工具链及系统构建依赖（clang、libclang、pkg-config、PostgreSQL 开发头文件）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. 编译并安装 vchord_bm25
git clone https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
PG_CONFIG=/path/to/pg_config make build
PG_CONFIG=/path/to/pg_config make install
```

> [!TIP]
> **编译期启用可选的 Lindera 词典特性**：如果希望将 Lindera 中日韩形态学词典（`ipadic`、`ipadic-neologd`、`unidic`、`ko-dic`、`cc-cedict`）直接内嵌编译到 `pg_tokenizer.so` 中，请在编译 `pg_tokenizer` 时传入 `--features` 参数：
> ```bash
> cargo pgrx install --release --pg-config $(which pg_config) \
>   --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

### 本地开发与调试 {#development--debugging-cargo-pgrx}

使用 `dev` 构建配置，在开启 BM25 编译优化的同时保留调试符号：

```bash
PG_CONFIG=/path/to/pg_config PROFILE=dev make build
PG_CONFIG=/path/to/pg_config PROFILE=dev make install
```

在配置预加载 `vchord_bm25` 后重启一个可丢弃的 PostgreSQL 测试实例，再通过 `psql` 连接。需要附加调试器时，可查询当前会话的后端进程 PID：

```sql
SELECT pg_backend_pid();
```

## 配置 PostgreSQL 并启用扩展 {#configure-postgresql--enable-extensions}

### 1. 配置 `shared_preload_libraries`（1.1.0 必需） {#1-shared-preload-libraries-optional--recommended-for-pg_tokenizer}

1.1.0 必须通过 `shared_preload_libraries` 预加载 `vchord_bm25`。请保留其他所需扩展；原生 `to_tsvector` 工作流不需要 `pg_tokenizer`，如果安装它来使用自定义分词，则应在 PostgreSQL 启动前将其加入同一设置：

```ini
shared_preload_libraries = 'vchord_bm25'
# 如果使用 pg_tokenizer 1.0.0 做自定义分词：
# shared_preload_libraries = 'vchord_bm25, pg_tokenizer'
```

修改 `shared_preload_libraries` 后请重启 PostgreSQL。

### 2. 创建扩展并设置 `search_path` {#2-create-extensions-and-set-search_path}

连接到目标数据库并启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vchord_bm25;
-- pg_tokenizer 是旧版 bm25vector 工作流的独立可选扩展。
```

在 `v0.1.0`–`v0.3.0` 版本中，`vchord_bm25` 会将其对象安装到 `bm25_catalog` 模式，而 `pg_tokenizer` 会安装到 `tokenizer_catalog` 模式。请将这两个模式加入你的 `search_path`：

```sql
-- 仅在当前会话生效
SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;

-- 或针对数据库 / 角色持久化保存
ALTER DATABASE postgres SET search_path TO "$user", public, bm25_catalog, tokenizer_catalog;
```

验证已安装的扩展版本：

```sql
SELECT extname, extversion FROM pg_extension WHERE extname IN ('vchord_bm25', 'pg_tokenizer');
```
