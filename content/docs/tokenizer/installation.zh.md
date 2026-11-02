---
title: "安装指南"
description: "通过 Pigsty 原生 Linux 软件包、Docker 镜像、Debian/ZIP 归档包或 cargo-pgrx 源码安装 pg_tokenizer。"
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/tensorchord/pg_tokenizer.rs/blob/main/docs/01-installation.md"
---

## 通过 `pig` 安装原生 Linux 软件包（推荐） {#linux-packages-via-pig}

在 EL 8/9/10、Debian 12/13 与 Ubuntu 22.04/24.04（支持 PostgreSQL 14–18）上，可以直接从 [Pigsty 软件仓库](https://pigsty.cc/ext/e/pg_tokenizer)安装预构建的原生软件包（完整包可用性矩阵见 [pgext.cloud](https://pgext.cloud/ext/pg_tokenizer)）：

```bash
curl -fsSL https://repo.pigsty.cc/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
```

## 使用 Docker（`vchord-suite`） {#docker}

[`tensorchord/vchord-suite`](/zh/docs/getting-started/vectorchord-suite/) Docker 镜像已预装完整的 Vchord 检索扩展套件：
- [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) —— 独立多语言分词器（`pgsty/pg_tokenizer`）
- [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) —— 原生 BM25 排序索引（`pgsty/vchord_bm25`）
- [`vchord`](https://github.com/pgsty/vchord) —— 可扩展、磁盘友好的向量相似性检索（`pgsty/vchord`）
- [`pgvector`](https://github.com/pgvector/pgvector) —— 标准 PostgreSQL 向量数据类型

```bash
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
```

使用 `psql` 连接数据库并启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## 参数配置（`shared_preload_libraries` 与 `search_path`） {#configuration}

通过原生软件包或归档包安装时，请将 `pg_tokenizer.so` 加入 `shared_preload_libraries`（预加载词表模型所必需），并将 `tokenizer_catalog` 加入 `search_path`：

```bash
psql -U postgres -c 'ALTER SYSTEM SET shared_preload_libraries = "pg_tokenizer.so"'
psql -U postgres -c 'ALTER SYSTEM SET search_path TO "$user", public, tokenizer_catalog'
sudo systemctl restart postgresql.service
```

随后在目标数据库中创建扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## 从 Debian 软件包或 ZIP 归档包安装 {#from-debian-package-or-zip-archive}

预编译的 `.deb` 与 `.zip` 发行包（要求 `GLIBC >= 2.35`，支持 `x86_64` 与 `aarch64`）可在 [`pgsty/pg_tokenizer` Releases 页面](https://github.com/pgsty/pg_tokenizer/releases/latest)下载：

```bash
# Debian / Ubuntu
sudo apt install ./postgresql-17-pg-tokenizer_*.deb
```

## 从源码编译安装（`cargo-pgrx`） {#from-source}

```bash
git clone https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo pgrx install --sudo --release
```

## 升级到 0.1.2（未发布） {#upgrade-012}

以下为 0.1.2 源码中的变更，尚未发布。安装匹配的动态库和 SQL 脚本后，先重启 PostgreSQL 以加载新的预加载库，再由扩展拥有者或管理员对各数据库执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '0.1.2';
```

0.1.0 与 0.1.1 均有升级路径。升级替换触发器及便捷函数定义，并授予目录权限，不重建自定义词表、不改变已有词元 ID，保留原六参函数的依赖关系。标准 `cargo pgrx install/package` 与 `tools/package.sh` 均会包含升级脚本。Lindera 字典版本变化引起的 ID 迁移仍须按照[模型说明](/zh/docs/tokenizer/models/)重新分词。

### 数据库拥有者权限 {#database-owner-permissions}

安装与升级向 `pg_database_owner` 授予 `tokenizer_catalog` 的 USAGE/CREATE、函数的 EXECUTE，目录表与模型表的 SELECT/INSERT/UPDATE/DELETE，以及序列的 USAGE/SELECT。安装角色以后在该模式中创建的表、序列和函数也有相同默认授权；新建自定义模型还会显式授权。授权随数据库拥有者变更而生效。

管理员安装扩展后，非超级用户的数据库拥有者可以创建、删除自己创建的模型、分析器、分词器、停用词及同义词。授权不转移对象所有权：删除其他角色创建的模型仍需原对象拥有者或管理员。其他应用角色需要显式授权；扩展不会向 PUBLIC 开放模式访问或目录写权限，函数继续以调用者权限执行。
