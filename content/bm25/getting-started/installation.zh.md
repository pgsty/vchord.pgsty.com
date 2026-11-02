---
title: "安装指南"
description: "通过 Pigsty、Docker、Debian 软件包或源码编译安装 VectorChord-BM25 (vchord_bm25) 与 pg_tokenizer。"
weight: 20
---

`vchord_bm25` 支持 Linux（`x86_64` 与 `aarch64`）及 macOS 平台上的 **PostgreSQL 14、15、16、17 和 18**。

## 方式一：Pigsty / 原生操作系统软件包（推荐） {#method-1-pigsty--native-os-packages-recommended}

[**Pigsty**](https://pgsty.com) 为 EL 8/9/10、Debian 12/13 以及 Ubuntu 22.04/24.04 上的 PostgreSQL 14–18 提供了预构建的 `vchord`、`vchord_bm25` 和 `pg_tokenizer` 原生 RPM 与 DEB 软件包。

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

## 方式三：GitHub Release 软件包（`.deb` 与 RHEL `.zip`） {#method-3-github-release-deb-packages}

从 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)（上游 [`supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)）与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)（上游 [`supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs)）的 GitHub Releases 页面下载对应 PostgreSQL 主版本（`14`–`18`）和 CPU 架构（`amd64` / `x86_64` 或 `arm64` / `aarch64`）的 `.deb` 或 RHEL 9+ `.zip` 软件包：

### Debian / Ubuntu（`.deb`） {#debian--ubuntu-deb}

```bash
# 安装 vchord_bm25（以 x86_64 上的 PostgreSQL 16 为例）
curl -LO https://github.com/supervc-stack/VectorChord-bm25/releases/download/0.3.0/postgresql-16-vchord-bm25_0.3.0-1_amd64.deb
sudo apt-get install ./postgresql-16-vchord-bm25_0.3.0-1_amd64.deb

# 安装 pg_tokenizer（以 x86_64 上的 PostgreSQL 16 为例）
curl -LO https://github.com/supervc-stack/pg_tokenizer.rs/releases/download/0.1.1/postgresql-16-pg-tokenizer_0.1.1-1_amd64.deb
sudo apt-get install ./postgresql-16-pg-tokenizer_0.1.1-1_amd64.deb
```

### RHEL 9+ / Enterprise Linux（`.zip` 归档包） {#rhel-9--enterprise-linux-zip-archive}

在 RHEL 9+ 系统（要求 `glibc >= 2.34`）中手动通过 Release `.zip` 归档包安装时：

```bash
# 1. 查询 PostgreSQL 的动态库目录与扩展共享目录
pg_config --pkglibdir
# 示例输出：/usr/pgsql-16/lib
pg_config --sharedir
# 示例输出：/usr/pgsql-16/share

# 2. 下载并解压发布归档包
wget https://github.com/supervc-stack/pg_tokenizer.rs/releases/download/0.1.1/pg16-pg_tokenizer-0.1.1-x86_64-unknown-linux-gnu.zip
unzip pg16-pg_tokenizer-0.1.1-x86_64-unknown-linux-gnu.zip

# 3. 拷贝共享库 (.so) 与扩展控制/SQL 脚本文件
sudo cp ./usr/lib/postgresql/16/lib/pg_tokenizer.so $(pg_config --pkglibdir)
sudo cp ./usr/share/postgresql/16/extension/* $(pg_config --sharedir)/extension
```

## 方式四：从源码编译（`cargo-pgrx`） {#method-4-build-from-source-cargo-pgrx}

如需从源码编译 [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) 与 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)：

```bash
# 1. 安装 Rust 工具链及系统构建依赖（clang、libclang、pkg-config、PostgreSQL 开发头文件）
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. 编译并安装 vchord_bm25
git clone https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
cargo install cargo-pgrx --version $(grep -o 'pgrx = "=[^"]*' Cargo.toml | cut -d = -f 3)
cargo pgrx init --pg17=$(which pg_config)
cargo pgrx install --release --pg-config $(which pg_config)

# 3. 编译并安装 pg_tokenizer
git clone https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo pgrx install --release --pg-config $(which pg_config)
```

> [!TIP]
> **编译期启用可选的 Lindera 词典特性**：如果希望将 Lindera 中日韩形态学词典（`ipadic`、`ipadic-neologd`、`unidic`、`ko-dic`、`cc-cedict`）直接内嵌编译到 `pg_tokenizer.so` 中，请在编译 `pg_tokenizer` 时传入 `--features` 参数：
> ```bash
> cargo pgrx install --release --pg-config $(which pg_config) \
>   --features "lindera-ipadic lindera-ipadic-neologd lindera-unidic lindera-ko-dic lindera-cc-cedict"
> ```

### 本地开发与调试（`cargo-pgrx`） {#development--debugging-cargo-pgrx}

在本地开发或调试 `vchord_bm25` 与 `pg_tokenizer` 时：

```bash
# 初始化 pgrx 托管的 PostgreSQL 实例（PG 14–18）
cargo pgrx init

# 使用 dev-opt 构建配置，在开启编译优化的同时保留调试符号
RUST_BACKTRACE=1 cargo pgrx run --profile dev-opt

# 在交互式 psql 会话中查询后端进程 PID，以便挂载 gdb 调试：
SELECT pg_backend_pid();
```

## 配置 PostgreSQL 并启用扩展 {#configure-postgresql--enable-extensions}

### 1. 配置 `shared_preload_libraries`（可选，推荐用于 `pg_tokenizer`） {#1-shared-preload-libraries-optional--recommended-for-pg_tokenizer}

如果你使用 `pg_tokenizer` 并希望在数据库服务启动时预加载词表模型，请将 `pg_tokenizer`（以及同时使用的 `vchord`）添加到 `postgresql.conf` 的 `shared_preload_libraries` 中：

```ini
shared_preload_libraries = 'vchord.so, pg_tokenizer.so'
```

修改 `shared_preload_libraries` 后请重启 PostgreSQL。（`vchord_bm25` 本身不要求配置 `shared_preload_libraries`，可通过 `CREATE EXTENSION` 在会话中动态加载。）

### 2. 创建扩展并设置 `search_path` {#2-create-extensions-and-set-search_path}

连接到目标数据库并启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
CREATE EXTENSION IF NOT EXISTS vchord_bm25 CASCADE;
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
