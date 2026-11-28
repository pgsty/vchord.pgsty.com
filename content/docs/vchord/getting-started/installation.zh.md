---
title: "安装"
linkTitle: "安装"
description: "通过 Pigsty 软件包、GitHub 发布包或源码安装 vchord，然后预加载并创建扩展。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/installation.md"
aliases:
  - "/docs/getting-started/installation/"
  - "/vectorchord/getting-started/installation/"
icon: fa-solid fa-download
---

vchord 1.5.0 支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19，需要先装好 [pgvector](/zh/docs/vector/)。从下面选一种方式安装文件，之后的[启用步骤](#enable)都一样。

| 方式 | 适用场景 |
| --- | --- |
| [Pigsty 软件包](#pigsty) | EL 8/9/10、Debian 12/13、Ubuntu 22.04/24.04。pgvector 和 PostgreSQL 软件源都会一并处理好。 |
| [Debian / Ubuntu 软件包](#debian) | PostgreSQL 从 PGDG（`apt.postgresql.org`）安装，并且想用 GitHub 上的发布文件。 |
| [ZIP 压缩包](#prebuilt-binaries) | 其他基于 glibc 的 Linux，或自定义的 PostgreSQL 目录布局。 |
| [源码](#source) | 其他平台，或者想针对自己的 CPU 编译。 |

## Pigsty 软件包 {#pigsty}

[`pig`](https://pigsty.io/ext/e/vchord/) 会添加 PostgreSQL 与 Pigsty 软件源，并为它找到的 PostgreSQL 安装 vchord 和 pgvector：

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add vchord
```

装了多个 PostgreSQL 大版本时，指定其中一个：`pig ext add vchord -v 18`。全部软件包见[下载页](/zh/download/)和 [PGEXT 目录](https://pgext.cloud/ext/vchord)。

## Debian / Ubuntu 软件包 {#debian}

<a id="Debian"></a><a id="Ubuntu"></a>

每个 [GitHub 发布版本](https://github.com/pgsty/vchord/releases/tag/1.5.0)都为每个 PostgreSQL 大版本和架构（`amd64`、`arm64`）提供一个 `.deb`。它们在 Ubuntu 22.04 上构建，需要 `libc6 >= 2.35`。

1. 从 PGDG 安装 PostgreSQL 和 pgvector，把 `18` 换成你的大版本：

   ```bash
   sudo apt install -y postgresql-18 postgresql-18-pgvector
   ```

1. 下载、校验并安装对应的软件包：

   ```bash
   V=1.5.0; PG=18; ARCH=amd64
   F=postgresql-${PG}-vchord_${V}-1_${ARCH}.deb
   wget https://github.com/pgsty/vchord/releases/download/${V}/${F}{,.sha256}
   sha256sum -c ${F}.sha256
   sudo apt install ./${F}
   ```
{.steps}

## ZIP 压缩包 {#prebuilt-binaries}

同一个发布版本还为每个 PostgreSQL 大版本和架构（`x86_64`、`aarch64`）提供 `.zip`，里面 `pkglibdir/` 放动态库，`sharedir/extension/` 放控制文件和 SQL 文件。把它们复制到 `pg_config` 给出的目录：

```bash
V=1.5.0; PG=18; ARCH=x86_64
curl -fsSLO https://github.com/pgsty/vchord/releases/download/${V}/postgresql-${PG}-vchord_${V}_${ARCH}-linux-gnu.zip
unzip postgresql-${PG}-vchord_${V}_${ARCH}-linux-gnu.zip -d vchord
sudo install -m 755 vchord/pkglibdir/vchord.so "$(pg_config --pkglibdir)/"
sudo install -m 644 vchord/sharedir/extension/* "$(pg_config --sharedir)/extension/"
```

压缩包针对 glibc 2.35 上的 PGDG PostgreSQL 构建。如果你的 PostgreSQL 用了不同的编译选项，可能需要改用[源码构建](#source)。

## 从源码构建 {#source}

需要 PostgreSQL 15–19 的开发文件（`pg_config`）、pgvector、GNU Make、Rust 1.100.0 及以上，以及版本相互匹配的 Clang、libclang 和 LLVM 工具，平台为 `x86_64` 或 `aarch64`。

```bash
git clone --branch 1.5.0 --depth 1 https://github.com/pgsty/vchord.git
cd vchord
PG_CONFIG=/path/to/pg_config make build
sudo PG_CONFIG=/path/to/pg_config make install
```

装了多个 LLVM 版本时，用 `CLANG_PATH` 和 `LIBCLANG_PATH` 指定其中一个。如果你的 Clang 会加载默认配置文件（例如 Homebrew 的 Clang），设置 `CLANG_NO_DEFAULT_CONFIG=1`。

<a id="Tuning"></a>

vchord 在运行时按 CPU 选择 SIMD 内核，默认构建在任何机器上都已经够快。如果想把其余代码也针对本机 CPU 编译，在 `make build` 前加上 `RUSTFLAGS="-C target-cpu=native"`；这样构建的二进制在较老的 CPU 上会因 `SIGILL` 崩溃，所以要在运行它的机器上构建。

## 启用扩展 {#enable}

1. 把 `vchord` 加入 `shared_preload_libraries`（保留列表里已有的库），然后重启 PostgreSQL。不做这一步，`CREATE EXTENSION` 会报错 `vchord must be loaded via shared_preload_libraries`。

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord';
   ```

1. 在需要的每个数据库中创建扩展。`CASCADE` 会一并创建 pgvector 的 `vector` 扩展。

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   ```

1. 确认版本：

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'vchord';
   ```
{.steps}

接下来可以跟着[快速上手](/zh/docs/vchord/getting-started/overview/#quick-start)走一遍，或者直接看 [vchordrq 索引](/zh/docs/vchord/usage/indexing/)。

## 升级 {#upgrade}

<a id="upgrading-to-130"></a><a id="upgrading-to-120"></a>

安装新版本文件，重启 PostgreSQL，然后在每个数据库中执行 `ALTER EXTENSION vchord UPDATE;`。从 1.3.0 及更早版本升级，或者还在用 PostgreSQL 14，需要额外几步，见[升级与迁移](/zh/docs/vchord/admin/migration/)。

## Docker {#docker}

<a id="docker-postgres"></a><a id="docker-suite"></a><a id="docker-scratch"></a><a id="PGXN"></a><a id="pgxn"></a>

PGSTY 不发布容器镜像。GHCR 上的 `tensorchord/vchord-*` 镜像是较旧的上游版本。要在容器中运行当前版本，在自己的镜像里安装 `.deb` 软件包即可，做法见 [Kubernetes](/zh/docs/vchord/admin/kubernetes/)。
