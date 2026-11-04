---
title: "安装指南"
linkTitle: "安装指南"
description: "VectorChord 已在多种操作系统与架构上完成测试，支持通过 Docker、源码、Debian/Ubuntu 包及 PGXN 安装。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/installation.md"
aliases:
  - "/zh/docs/getting-started/installation/"
  - "/vectorchord/getting-started/installation/"
icon: fa-solid fa-download
---

`vchord` 1.2.0 已正式发布，支持 PostgreSQL 14–18。Pigsty 已发布适用于 EL 8/9/10、Debian 12/13、Ubuntu 22.04/24.04/26.04 的 Linux 原生 RPM/DEB 软件包，覆盖 `x86_64` 和 `aarch64`（详见[下载页面](/zh/download/)与 [PGEXT 发布矩阵](https://pgext.cloud/ext/vchord)）。源码还在 CI 中测试了 macOS、Windows、Alpine Linux 及其他架构。

当前版本可从 `pgsty/vchord` 仓库或 Pigsty 软件包仓库安装。PostgreSQL 19 构建仅用于开发验证，不属于正式发布支持矩阵。

* Ubuntu (x86_64, aarch64)
* macOS (x86_64, aarch64)
* Windows (x86_64)
* Alpine Linux (x86_64, aarch64) [^1]
* Debian (powerpc64le, s390x, riscv64) [^2]

[^1]: CI 在 Alpine Linux 3.22 上覆盖 PostgreSQL 15–17。
[^2]: CI 通过 QEMU 用户态模拟器在 `powerpc64le` 上覆盖 PostgreSQL 14–18，并在 `s390x` 与 `riscv64` 上覆盖部分 PostgreSQL 15/17 作业。这些是源码/CI 目标；预构建原生二进制软件包面向 `x86_64` 与 `aarch64`。

如果您在上述任何操作系统上遇到问题，请提交 Bug 报告；如果您需要更多平台支持，欢迎提交功能请求。

<a id="Docker"></a>
## Docker {#docker}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 维护版本的 Docker 和 Kubernetes 镜像尚未发布。以下上游说明仅供参考，后续更新。

### VectorChord 镜像 {#vectorchord-image}

<a href="https://hub.docker.com/r/tensorchord/vchord-postgres"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-postgres" /></a>

体验 VectorChord 最简便的方式是直接运行开箱即用的 [Docker 镜像](https://hub.docker.com/r/tensorchord/vchord-postgres)。

1. 在 Docker 中启动 VectorChord 容器。

```sh
docker run \
  --name vchord-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/vchord-postgres:pg18-v1.1.1
```

2. 使用 `psql` 命令行工具连接到数据库。默认用户名为 `postgres`。

```sh
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

> [!TIP]
>
> 为了充分发挥性能，请通过添加如下参数将数据卷挂载到 PostgreSQL 数据目录：
>
> * 在 PostgreSQL 18 上：`-v $PWD/pgdata:/var/lib/postgresql/18/docker`
> * 在 PostgreSQL 14、15、16 和 17 上：`-v $PWD/pgdata:/var/lib/postgresql/data`
>
> 您可以参考基础父镜像的说明文档（https://hub.docker.com/_/postgres/）来配置 PostgreSQL。
>


### VectorChord Suite 镜像 {#vectorchord-suite-image}

<a href="https://hub.docker.com/r/tensorchord/vchord-suite"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-suite"/></a>

除了仅包含 VectorChord 扩展的基础镜像外，我们还提供了全合一镜像 `tensorchord/vchord-suite:pg18-latest`。该综合镜像包含了所有官方 TensorChord 扩展。开发者应根据[支持矩阵](https://github.com/tensorchord/VectorChord-images?tab=readme-ov-file#support-matrix)选择与所需扩展版本兼容的镜像标签。

1. 在 Docker 中启动 VectorChord 容器。

```sh
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
  # 如果您希望使用 ghcr 镜像，可以将镜像名改为 `ghcr.io/tensorchord/vchord-suite:pg18-latest`。
  # 如果您希望使用特定版本，可以使用如 `pg17-20250815` 的标签，受支持的版本可在支持矩阵中查看。
```

其余步骤与上文一致。

### VectorChord Scratch 镜像 {#vectorchord-scratch-image}

<a href="https://hub.docker.com/r/tensorchord/vchord-scratch"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-scratch" /></a>

我们提供了一个仅包含 VectorChord 相关文件的 scratch 镜像。您可以使用 Docker 的 `COPY` 指令将 VectorChord 安装到任何镜像中，例如：

```dockerfile
FROM tensorchord/vchord-scratch:pg18-v1.1.1 AS vchord_scratch
FROM postgres:18-bookworm
RUN apt-get update && apt-get install -y postgresql-18-pgvector
COPY --from=vchord_scratch / /
CMD ["postgres", "-c" ,"shared_preload_libraries=vchord,vector"]
```

该镜像同样可以作为 CloudNativePG 的镜像卷扩展（Image Volume Extension）使用。另请参阅：

* [Image Volume Extensions](https://cloudnative-pg.io/docs/1.28/imagevolume_extensions/)
* [Kubernetes](/zh/docs/vchord/admin/kubernetes/)

<a id="Source"></a>
## 源码编译 {#source}

> [!TIP]
>
> 编译环境要求：
>
> * 任意版本的 `make`
> * `clang >= 16` 及 `libclang`
> * `rust >= 1.93` 及 `cargo`
>
> 在大多数平台上推荐使用 Rustup 安装 Rust，而在 Alpine Linux 上则建议使用系统包管理器安装。
>
> 您可以设置环境变量 `CC` 来为构建系统指定所需的 C 编译器。如果不设置该变量，构建系统会自动搜索 clang 和 gcc。若要使用 clang 编译所有 C 代码，请将 `CC` 设置为 clang 的路径；若要使用 gcc 编译所有 C 代码，请将 `CC` 设置为 gcc 的路径（注意：此时要求 `gcc >= 14`）。
>
> Rust 版本要求并非长期不变的承诺；我们会在每次发布新版本时上调所需的最低 Rust 版本。
>
> 上述编译要求仅适用于 x86_64 和 aarch64 架构。对于包括 powerpc64le、s390x 和 riscv64 在内的所有其他架构，均需要使用 nightly 版本的 Rust 以及最新版本的 Clang。
>


如果您尚未安装 PostgreSQL，请先安装 PostgreSQL。如果您尚未安装 pgvector，可以在执行第 3 步之前安装 pgvector。

1. 下载源码，并使用 `make` 进行编译和安装。

```sh
curl -fsSL https://github.com/pgsty/vchord/archive/refs/tags/1.2.0.tar.gz | tar -xz
cd vchord-1.2.0
PG_CONFIG=/path/to/pg_config make build
PG_CONFIG=/path/to/pg_config make install # 或者 `sudo make install`
```

2. 修改 `shared_preload_libraries` 以加载该扩展来配置 PostgreSQL，然后重启 PostgreSQL 集群。

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="Tuning"></a>
### 编译调优 {#tuning}

VectorChord 会针对 SIMD 代码执行运行时 CPU 指令集分发（runtime CPU dispatch）。如果您希望编译器针对特定 CPU 对整个程序进行优化，可以指示编译器为该特定 CPU 生成代码。

```sh
RUSTFLAGS="-Ctarget-cpu=icelake" make build
```

若要查看当前目标平台（target triple）支持的所有有效 CPU 选项及默认 CPU，请运行：

```sh
rustc --print target-cpus
```

若要针对当前宿主机生成优化代码，请运行：

```sh
RUSTFLAGS="-Ctarget-cpu=native" make build
```

请注意，指定特定 `target-cpu` 生成的二进制文件与其他型号的 CPU 不兼容。

您也可以通过 Cargo 配置文件来完成此设置：

```sh
cd vchord-1.2.0
mkdir -p .cargo
touch .cargo/config.toml
echo 'build.rustflags = ["-Ctarget-cpu=icelake"]' >> ./cargo/config.toml
```

<a id="Debian"></a>
## Debian {#debian}

如果您尚未安装 PostgreSQL，请参照 https://www.postgresql.org/download/linux/debian/ 进行安装。如果您尚未安装 pgvector，可以在执行第 3 步之前通过 `apt install postgresql-16-pgvector` 进行安装；请将 `16` 替换为您的 PostgreSQL 主版本。

> [!TIP] 关于发布链接的说明
> 当前 PGSTY 发布版本为 `vchord` 1.2.0。下面以 PostgreSQL 16 为例；请将 `16` 和 `amd64` 替换为您下载的软件包对应的 PostgreSQL 主版本和架构。


1. 在[发布页面](https://github.com/pgsty/vchord/releases)下载 Debian 软件包，并通过 `apt` 进行安装。

```sh
wget https://github.com/pgsty/vchord/releases/download/1.2.0/postgresql-16-vchord_1.2.0-1_amd64.deb
sudo apt install ./postgresql-16-vchord_1.2.0-1_amd64.deb
```

2. 修改 `shared_preload_libraries` 以加载该扩展来配置 PostgreSQL，然后重启 PostgreSQL 集群。

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
sudo systemctl restart postgresql.service
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="Ubuntu"></a>
## Ubuntu {#ubuntu}

如果您尚未安装 PostgreSQL，请参照 https://www.postgresql.org/download/linux/ubuntu/ 进行安装。如果您尚未安装 pgvector，可以在执行第 3 步之前通过 `apt install postgresql-16-pgvector` 进行安装；请将 `16` 替换为您的 PostgreSQL 主版本。

> [!TIP] 关于发布链接的说明
> 当前 PGSTY 发布版本为 `vchord` 1.2.0。下面以 PostgreSQL 16 为例；请将 `16` 和 `amd64` 替换为您下载的软件包对应的 PostgreSQL 主版本和架构。


1. 在[发布页面](https://github.com/pgsty/vchord/releases)下载 Debian 软件包，并通过 `apt` 进行安装。

```sh
wget https://github.com/pgsty/vchord/releases/download/1.2.0/postgresql-16-vchord_1.2.0-1_amd64.deb
sudo apt install ./postgresql-16-vchord_1.2.0-1_amd64.deb
```

2. 修改 `shared_preload_libraries` 以加载该扩展来配置 PostgreSQL，然后重启 PostgreSQL 集群。

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
sudo systemctl restart postgresql.service
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="PGXN"></a>
## PGXN {#pgxn}

> [!TIP]
>
> 编译环境要求请参阅[源码编译](#source)。
>


如果您尚未安装 PostgreSQL，请先安装 PostgreSQL。如果您尚未安装 pgvector，可以在执行第 3 步之前通过 `pgrxclient install vector` 进行安装。

1. 使用以下命令从 [PostgreSQL Extension Network (PGXN)](https://pgxn.org/dist/vchord) 安装 VectorChord：

```sh
pgxnclient install vchord # 或者 `pgxnclient install vchord --sudo`
```

2. 修改 `shared_preload_libraries` 以加载该扩展来配置 PostgreSQL，然后重启 PostgreSQL 集群。

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

> [!TIP]
>
> PGXN 是上游 VectorChord 项目的历史分发渠道。对于 PGSTY 1.2.0，请使用上面的 Pigsty 或 GitHub 发布软件包。
>


## 预编译二进制文件 {#prebuilt-binaries}

{{< badge text="deprecated" tone="danger" >}}

> [!WARNING]
>
> 预编译二进制文件可能与您机器上安装的 PostgreSQL 存在 ABI 不兼容，这可能会导致静默错误。在此情况下，我们强烈建议您从源码进行编译。
>


如果您尚未安装 PostgreSQL，请先安装 PostgreSQL。如果您尚未安装 pgvector，可以在执行第 3 步之前安装 pgvector。

1. 在[发布页面](https://github.com/pgsty/vchord/releases)下载预编译二进制文件，并参考您所用发行版的文档重新打包，然后通过系统包管理器进行安装。虽然我们不建议这样做，但如果您需要，也可以直接将文件手动复制到系统目录中：

```sh
cp -r ./pkglibdir/. $(pg_config --pkglibdir)
cp -r ./sharedir/. $(pg_config --sharedir)
```

2. 修改 `shared_preload_libraries` 以加载该扩展来配置 PostgreSQL，然后重启 PostgreSQL 集群。

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. 执行以下 SQL 语句以确保扩展已启用。

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

## 升级到 1.2.0 {#upgrading-to-120}

从 `1.1.1`（或 `0.2.0` 及之后的任意旧版本）升级时，先安装与 PostgreSQL 主版本匹配的 1.2.0 动态库和扩展 SQL 文件，再重启 PostgreSQL 以加载新的预加载库。1.2.0 包含从 `0.2.0` 至 `1.1.1` 的直接升级路径，并保留旧版 SQL 包装函数的兼容符号，确保 `1.0.0` 之前注册的扩展也能顺利完成 `ALTER EXTENSION`。在每个使用 `vchord` 的数据库中执行：

```sql
ALTER EXTENSION vchord UPDATE TO '1.2.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord';
```
