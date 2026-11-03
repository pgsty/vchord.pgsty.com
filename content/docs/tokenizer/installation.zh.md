---
title: "安装指南"
description: "通过 Pigsty 原生 Linux 软件包、Docker 镜像、Debian/ZIP 归档包或 cargo-pgrx 源码安装 pg_tokenizer。"
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
---

## 通过 `pig` 安装原生 Linux 软件包（推荐） {#linux-packages-via-pig}

在 EL 8/9/10、Debian 12/13 与 Ubuntu 22.04/24.04/26.04（支持 PostgreSQL 14–18）上，可以从 [Pigsty 软件仓库](https://pigsty.cc/ext/e/pg_tokenizer)安装与目标发行版、CPU 架构匹配的原生软件包（完整包可用性矩阵见 [pgext.cloud](https://pgext.cloud/ext/pg_tokenizer)）：

```bash
curl -fsSL https://repo.pigsty.cc/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
```

## 使用 Docker（`vchord-suite`） {#docker}

[`tensorchord/vchord-suite`](/zh/docs/vchord/getting-started/vectorchord-suite/) Docker 镜像已预装完整的 Vchord 检索扩展套件：
- [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) —— 独立多语言分词器（`pgsty/pg_tokenizer`）
- [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) —— 原生 BM25 排序索引（`pgsty/vchord_bm25`）
- [`vchord`](https://github.com/pgsty/vchord) —— 可扩展、磁盘友好的向量相似性检索（`pgsty/vchord`）
- [`pgvector`](/zh/docs/vector/) —— 标准 PostgreSQL 向量数据类型

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

`pg_tokenizer` 没有必需的 PostgreSQL 扩展依赖。`vchord_bm25` 是可选组件：其 0.3.x 接口通过 `bm25vector` 消费 `INT[]`，0.4.0/main 接口可以直接消费原生 `tsvector`。`pg_tokenizer` 动态库必须在 PostgreSQL 启动前通过 `shared_preload_libraries` 预加载；如果希望省略模式限定调用函数，再将 `tokenizer_catalog` 加入 `search_path`：

```bash
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'pg_tokenizer.so';"
psql -U postgres -c "ALTER SYSTEM SET search_path TO \"\$user\", public, tokenizer_catalog;"
sudo systemctl restart postgresql.service
```

随后在目标数据库中创建扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## 从 Debian 软件包或 ZIP 归档包安装 {#from-debian-package-or-zip-archive}

[`pgsty/pg_tokenizer` Releases 页面](https://github.com/pgsty/pg_tokenizer/releases/latest)提供面向部分 PostgreSQL 主版本及 `x86_64`/`aarch64` 架构的 `.deb` 与 `.zip` 发行归档。`.deb` 必须匹配目标 Debian/Ubuntu 发行版、PostgreSQL 主版本和架构；ZIP 不包含软件包管理器依赖元数据，安装前必须自行验证共享库与目标系统 libc 的兼容性，目标平台有原生包时应优先使用原生包。

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

## 升级到 0.2.0 {#upgrade-020}

安装 0.2.0 动态库和 SQL 脚本后，先重启 PostgreSQL 以加载预加载库，再由扩展拥有者或管理员对各数据库执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '0.2.0';
```

0.1.0、0.1.1 与 0.1.2 均有升级路径。迁移会保留目录数据、已有自定义词表 ID 以及原六参函数的依赖关系。0.2.0 新增事务结束时的会话级对象缓存失效、原生 `tsvector` 辅助函数，以及删除空输出词元后连续编号的位置语义。如果分析器或模型重建影响了已存储的 `tsvector` 或词元 ID 列，应重新计算这些搜索值。标准 `cargo pgrx install/package` 与 `tools/package.sh` 均会包含升级脚本。Lindera 字典版本变化引起的 ID 迁移仍须按照[模型说明](/zh/docs/tokenizer/models/)重新分词。

### 数据库拥有者权限 {#database-owner-permissions}

安装与升级向 `pg_database_owner` 授予 `tokenizer_catalog` 的 USAGE/CREATE、函数的 EXECUTE，目录表与模型表的 SELECT/INSERT/UPDATE/DELETE，以及序列的 USAGE/SELECT。安装角色以后在该模式中创建的表、序列和函数也有相同默认授权；新建自定义模型还会显式授权。授权随数据库拥有者变更而生效。

管理员安装扩展后，非超级用户的数据库拥有者可以创建、删除自己创建的模型、分析器、分词器、停用词及同义词。授权不转移对象所有权：删除其他角色创建的模型仍需原对象拥有者或管理员。其他应用角色需要显式授权；扩展不会向 PUBLIC 开放模式访问或目录写权限，函数继续以调用者权限执行。
