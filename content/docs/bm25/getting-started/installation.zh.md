---
title: "安装"
linkTitle: "安装"
description: "从 Pigsty 软件包、GitHub Release 软件包或源码安装 vchord_bm25，然后预加载并创建扩展。"
weight: 20
icon: fa-solid fa-download
---

vchord_bm25 1.3.0 支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19。任选一种方式安装文件，之后的[启用扩展](#enable)步骤都一样。

| 方式 | 适用场景 |
| --- | --- |
| [Pigsty 软件包](#pigsty) | 运行 EL 8/9/10、Debian 12/13 或 Ubuntu 22.04/24.04，希望软件源一并配好。 |
| [Debian/Ubuntu 软件包](#debian) | PostgreSQL 来自 PGDG（`apt.postgresql.org`），想直接用 GitHub 上的发布文件。 |
| [ZIP 归档](#zip) | 其他基于 glibc 的 Linux，或自定义的 PostgreSQL 目录布局。 |
| [源码编译](#source) | 其他平台，或 PostgreSQL 的编译选项与预编译包不一致。 |

## Pigsty 软件包 {#pigsty}

[`pig`](https://pigsty.io/ext/e/vchord_bm25/) 会添加 PostgreSQL 与 Pigsty 软件源，并为它找到的 PostgreSQL 安装对应的包：

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add vchord_bm25
```

装了多个 PostgreSQL 大版本时，指定一个：`pig ext add vchord_bm25 -v 18`。要处理中文、日文或韩文，用同样的方式再装上 `pg_tokenizer`。[下载页](/zh/download/)和 [PGEXT 目录](https://pgext.cloud/ext/vchord_bm25)列出了各个软件包及其版本。

## Debian/Ubuntu 软件包 {#debian}

每个 [GitHub Release](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0) 都为每个 PostgreSQL 大版本和架构（`amd64`、`arm64`）提供一个 `.deb`。这些包在 Ubuntu 22.04 上构建，要求 `libc6 >= 2.35`，并依赖 PGDG 的服务端包 `postgresql-<大版本>`。

```bash
V=1.3.0; PG=18; ARCH=amd64
F=postgresql-${PG}-vchord-bm25_${V}-1_${ARCH}.deb
wget https://github.com/pgsty/vchord_bm25/releases/download/${V}/${F}{,.sha256}
sha256sum -c ${F}.sha256
sudo apt install ./${F}
```

## ZIP 归档 {#zip}

同一个 Release 还为每个 PostgreSQL 大版本和架构（`x86_64`、`aarch64`）提供 `.zip`。共享库在 `pkglibdir/` 下，控制文件和 SQL 文件在 `sharedir/extension/` 下，复制到 `pg_config` 报告的目录即可：

```bash
V=1.3.0; PG=18; ARCH=x86_64
curl -fsSLO https://github.com/pgsty/vchord_bm25/releases/download/${V}/postgresql-${PG}-vchord-bm25_${V}_${ARCH}-linux-gnu.zip
unzip postgresql-${PG}-vchord-bm25_${V}_${ARCH}-linux-gnu.zip -d vchord_bm25
sudo install -m 755 vchord_bm25/pkglibdir/vchord_bm25.so "$(pg_config --pkglibdir)/"
sudo install -m 644 vchord_bm25/sharedir/extension/* "$(pg_config --sharedir)/extension/"
```

`install` 会写出一个新文件，而不是原地覆盖旧文件，这样已加载该库的服务器进程不会因此崩溃。归档基于 glibc 2.35 上的 PGDG PostgreSQL 构建；编译选项不同的 PostgreSQL 可能需要[从源码编译](#source)。

## 从源码编译 {#source}

需要 PostgreSQL 15–19 的开发文件（`pg_config`）、GNU Make、Rust 1.100.0 或更高版本，以及版本匹配的 Clang、libclang 与 LLVM 工具，平台为 `x86_64` 或 `aarch64`。

```bash
git clone --branch 1.3.0 --depth 1 https://github.com/pgsty/vchord_bm25.git
cd vchord_bm25
PG_CONFIG=/path/to/pg_config make build
sudo make PG_CONFIG=/path/to/pg_config install
```

装有多个 LLVM 版本时，用 `CLANG_PATH` 和 `LIBCLANG_PATH` 指定其中一个。如果 Clang 会加载默认配置文件（例如 Homebrew 的 Clang），设置 `CLANG_NO_DEFAULT_CONFIG=1`。

## 启用扩展 {#enable}

1. 把 `vchord_bm25` 加入 `shared_preload_libraries`（保留列表里已有的库），然后重启 PostgreSQL。跳过这一步，`CREATE EXTENSION` 会报错：`vchord_bm25 must be loaded via shared_preload_libraries.`

   同一个实例里还有 vchord 和 pg_tokenizer 时，三个都要列上：

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord,vchord_bm25,pg_tokenizer';
   ```

1. 以超级用户身份，在每个需要它的数据库中创建扩展：

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   ```

   对象会建在当前模式下，通常是 `public`；用 `WITH SCHEMA` 可以换一个模式。如果这个模式不在查询角色的 `search_path` 中，运算符、运算符类和函数都要写全限定名：`OPERATOR(search.<&>)`、`search.bm25_ops`、`search.to_bm25query(...)`。

1. 确认版本：

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'vchord_bm25';
   ```
{.steps}

vchord_bm25 会创建名为 `bm25` 的索引访问方法。另一个扩展如果也有同名的访问方法（例如 ParadeDB 的 `pg_search`），就不能装在同一个数据库里：后执行的 `CREATE EXTENSION` 会报错 `access method "bm25" already exists`。

接下来，跟着[快速上手](/zh/docs/bm25/getting-started/overview/#quick-start)走一遍，或者直接看[建索引](/zh/docs/bm25/usage/indexing/)。

## 升级 {#upgrade}

安装新版本文件，重启 PostgreSQL，然后在每个数据库中执行 `ALTER EXTENSION vchord_bm25 UPDATE;`。1.0.0 及之后版本建的索引无需重建即可继续使用。从 PostgreSQL 14 升级、降级，或从 0.x 的 `bm25vector` 接口迁移，见[升级与迁移](/zh/docs/bm25/reference/migration/)。

## Docker {#docker}

PGSTY 不发布容器镜像。`tensorchord/vchord-suite` 镜像里是 0.x 的 `bm25vector` 接口，不是本文档描述的接口。要在容器里运行当前版本，请在自己的镜像中安装 `.deb` 包。
