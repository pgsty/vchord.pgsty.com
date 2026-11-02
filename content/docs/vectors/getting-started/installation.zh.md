---
title: "安装"
linkTitle: "安装"
description: "安装 pgvecto.rs 的四种方式。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/getting-started/installation.md"
aliases:
  - "/getting-started/installation/"
---

> [!WARNING]
> 我们强烈建议您探索全新的 [VectorChord](https://github.com/pgsty/vchord) 实现，它提供了更高的稳定性和性能。建议用户迁移至 VectorChord，详情请参考[迁移指南](/zh/docs/vchord/admin/migration/)。


安装 `pgvecto.rs` 有四种方式。

<a id="Docker"></a>
## Docker {#docker}

<a href="https://hub.docker.com/r/tensorchord/pgvecto-rs"><img src="https://img.shields.io/docker/pulls/tensorchord/pgvecto-rs" /></a>


试用 `pgvecto.rs` 最简单的方式是直接运行开箱即用的 [Docker 镜像](https://hub.docker.com/r/tensorchord/pgvecto-rs)。

```sh
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.2.0
```

随后您可以使用 `psql` 命令行工具连接到数据库。默认用户名为 `postgres`，默认密码为 `mysecretpassword`。

```sh
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

运行以下 SQL 确保扩展已启用：

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

为了获得完整性能，请添加类似 `-v $PWD/pgdata:/var/lib/postgresql/data` 的选项，将数据卷挂载到 PostgreSQL 数据目录。

您可以参考父镜像文档 https://hub.docker.com/_/postgres/ 来配置 PostgreSQL。

## 使用 Debian 软件包安装 {#from-debian-package}

> [!TIP]
> 从 Debian 软件包安装需要依赖 `GLIBC >= 2.31`，例如：
> - `Ubuntu 20.04` 或更高版本
> - `Debian Bullseye` 或更高版本


Debian 软件包（`.deb`）适用于基于 Debian 的发行版（如 Ubuntu 等），可以通过 `dpkg` 或 `apt-get` 轻松安装。

1. 在 [Release 页面](https://github.com/tensorchord/pgvecto.rs/releases/latest)下载 `.deb` 软件包，并执行 `sudo apt install vectors-pg15-*.deb` 进行安装。

2. 修改 `shared_preload_libraries` 和 `search_path` 以包含该扩展，从而完成 PostgreSQL 配置。

```sh
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "vectors.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, vectors'
# 需要重启 PostgreSQL 集群以使配置生效。
sudo systemctl restart postgresql.service   # 适用于通过 systemd 运行的 pgvecto.rs
```

3. 连接到数据库并启用扩展。

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

## 使用 ZIP 压缩包安装 {#from-zip-package}

{{< badge text="since v0.2.1" tone="info" >}}

> [!TIP]
> 从 ZIP 压缩包安装需要依赖 `GLIBC >= 2.31`，例如：
> - `RHEL 9` 或更高版本


对于非 Debian 系且无法运行 Docker 容器的系统，请按以下步骤安装：

1. 安装前，请确保已安装必要的软件包，包括 `PostgreSQL`、`pg_config`、`unzip` 和 `wget`。

```sh
# RHEL 9 dnf 示例
# 请根据您的包管理器进行检查
sudo dnf install -y unzip wget libpq-devel
sudo dnf module install -y postgresql:15/server
sudo postgresql-setup --initdb
sudo systemctl start postgresql.service
sudo systemctl enable postgresql.service
```

2. 验证 PostgreSQL 是否已设置 `$pkglibdir` 和 `$shardir`。

```sh
pg_config --pkglibdir
# 输出类似于：
# /usr/lib/postgresql/15/lib 或
# /usr/lib64/pgsql

pg_config --sharedir
# 输出类似于：
# /usr/share/postgresql/15 或
# /usr/share/pgsql
```

3. 在 [Release 页面](https://github.com/tensorchord/pgvecto.rs/releases/latest)下载 zip 压缩包并解压到临时目录。

```sh
wget https://github.com/tensorchord/pgvecto.rs/releases/download/v0.2.1/vectors-pg15_x86_64-unknown-linux-gnu_0.2.1.zip -O vectors.zip
unzip vectors.zip -d vectors
```

4. 将扩展文件复制到 PostgreSQL 目录。

```sh
# 将动态库复制到 `$pkglibdir`
sudo cp vectors/vectors.so $(pg_config --pkglibdir)/
# 将 schema 文件复制到 `$shardir`
sudo cp vectors/vectors--* $(pg_config --sharedir)/extension/
sudo cp vectors/vectors.control $(pg_config --sharedir)/extension/
```

5. 修改 `shared_preload_libraries` 和 `search_path` 以包含该扩展，从而完成 PostgreSQL 配置。

```sh
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "vectors.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, vectors'
# 需要重启 PostgreSQL 集群以使配置生效。
sudo systemctl restart postgresql.service   # 适用于通过 systemd 运行的 pgvecto.rs
```

6. 连接到数据库并启用扩展。

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

## 从源码构建安装 {#from-source}

在从源码构建之前，您可以参考[开发指南](/zh/docs/vectors/developers/development/)配置开发环境。

1. 构建并安装扩展：

```sh
sed -e "s/@CARGO_VERSION@/0.0.0/g" ./vectors.control  # 这里的 0.0.0 是您所需的版本号
sudo cp -a ./sql/upgrade/. $(pg_config --sharedir)/extension
cargo pgrx install --sudo --release
```

2. 修改 `shared_preload_libraries` 和 `search_path` 以包含该扩展，从而完成 PostgreSQL 配置。

```sh
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "vectors.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, vectors'
# 需要重启 PostgreSQL 集群以使配置生效。
sudo systemctl restart postgresql.service   # 适用于通过 systemd 运行的 pgvecto.rs
service postgresql restart  # 适用于在 envd 中运行的 pgvecto.rs
```

3. 连接到数据库并启用扩展。

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```
