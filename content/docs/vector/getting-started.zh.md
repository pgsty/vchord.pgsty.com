---
title: "安装与快速上手"
linkTitle: "安装与快速上手"
description: "在 PostgreSQL 14–18 上安装 pgvector 并运行第一个向量相似性查询。"
weight: 10
icon: fa-solid fa-rocket
upstream_link: https://github.com/pgvector/pgvector#installation
---

## 安装方式

### Pigsty / Linux 原生软件包（推荐）

[Pigsty](https://pigsty.io/ext/e/pgvector) 为 Debian、Ubuntu 以及 RHEL/Rocky/AlmaLinux（x86_64 与 ARM64 架构）提供了针对 PostgreSQL 14–18 预编译的原生 `pgvector`（`v0.8.2`）软件包：

```bash
pig repo add pgdg pigsty -u
pig ext install pgvector
```

如果您同时需要磁盘友好的 RaBitQ 向量索引与原生 BM25 检索能力，可以一次性安装完整的 Vchord 套件：

```bash
pig ext install pgvector vchord vchord_bm25 pg_tokenizer
```

### Docker 容器

直接启动官方 `pgvector` 容器镜像：

```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

或者使用开箱即用的 Vchord 全家桶镜像（内置 `pgvector`、[`vchord`](/zh/docs/vchord/)、[`vchord_bm25`](/zh/docs/bm25/) 与 [`pg_tokenizer`](/zh/docs/tokenizer/)）：

```bash
docker run -d \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  tensorchord/vchord-suite:pg18-latest
```

### Linux 官方软件源（PGDG APT / YUM）

- **Debian / Ubuntu**（通过 [PostgreSQL APT 仓库](https://wiki.postgresql.org/wiki/Apt)）：
  ```bash
  sudo apt install postgresql-18-pgvector
  ```
- **RHEL / Rocky / AlmaLinux / Fedora**（通过 [PostgreSQL YUM 仓库](https://yum.postgresql.org/)）：
  ```bash
  sudo dnf install pgvector_18
  ```

### macOS（Homebrew）

```bash
brew install pgvector
```

### 从源码编译安装（Linux / macOS）

请确保系统已安装 PostgreSQL 开发头文件（`postgresql-server-dev-*` 或 `postgresql*-devel`）、`make` 及 C 编译器：

```bash
cd /tmp
git clone --branch v0.8.2 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

> [!TIP] CPU 原生指令集优化
> 默认情况下，`pgvector` 的 `Makefile` 会在编译器支持时自动启用 `-march=native` 以最大化当前机器的 SIMD 吞吐性能。如果您需要构建跨不同代际 CPU 通用的可移植二进制包，请使用 `make OPTFLAGS=""`。

---

## 启用扩展

连接到目标数据库并启用 `vector` 扩展（需要在每个使用向量功能的数据库中执行一次）：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

查看当前安装的扩展版本：

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

### 升级 `pgvector`

在服务器上更新二进制包后，在数据库中执行以下命令升级 SQL 目录对象定义：

```sql
ALTER EXTENSION vector UPDATE;
```

---

## 快速上手

### 1. 创建包含向量列的表

创建一个包含 3 维单精度浮点（`float32`）向量的表：

```sql
CREATE TABLE items (
    id bigserial PRIMARY KEY,
    embedding vector(3)
);
```

也可以向已有表中添加向量列：

```sql
ALTER TABLE items ADD COLUMN embedding vector(3);
```

### 2. 插入、更新与删除向量

使用文本字面量格式 `'[x1,x2,x3]'` 插入向量：

```sql
INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');
```

使用 `ON CONFLICT` 执行 Upsert（插入或更新）：

```sql
INSERT INTO items (id, embedding) VALUES (1, '[1,2,3]'), (2, '[4,5,6]')
ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding;
```

使用标准 SQL 更新或删除记录：

```sql
UPDATE items SET embedding = '[1,2,3]' WHERE id = 1;
DELETE FROM items WHERE id = 1;
```

### 3. 使用 `COPY` 批量导入

对于百万级以上的大规模数据集，强烈建议使用二进制 `COPY` 替代逐行 `INSERT`：

```sql
COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);
```

### 4. 查询最近邻向量

按欧氏距离（L2）检索距离 `'[3,1,2]'` 最近的 5 条记录：

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

接下来请阅读[查询与过滤检索](/zh/docs/vector/querying/)了解所有距离度量与过滤查询模式，或参阅[HNSW 与 IVFFlat 索引](/zh/docs/vector/indexing/)了解如何加速大规模表上的近似检索。
