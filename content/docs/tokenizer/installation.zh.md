---
title: "安装指南"
description: "通过 Pigsty 原生 Linux 软件包、Docker 镜像、Debian/ZIP 归档包或 cargo-pgrx 源码安装 pg_tokenizer。"
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
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
