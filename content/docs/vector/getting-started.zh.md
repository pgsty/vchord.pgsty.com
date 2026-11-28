---
title: "安装与快速上手"
linkTitle: "安装与快速上手"
description: "在 PostgreSQL 14–18 上安装 pgvector 0.8.7 并运行第一个向量相似性查询。"
weight: 10
icon: fa-solid fa-rocket
upstream_link: https://github.com/pgvector/pgvector#installation
---

## 安装方式 {#installation}

### Pigsty / Linux 原生软件包（推荐） {#pigsty}

[Pigsty](https://pigsty.io/ext/e/vector/) 为 Debian、Ubuntu 以及 RHEL/Rocky/AlmaLinux（`x86_64` 与 `aarch64` 架构）提供针对 PostgreSQL 14–18 预编译的原生 `pgvector`（`v0.8.7`）软件包：

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig install pgvector
```

如需同时安装磁盘友好的 RaBitQ 向量索引与原生 BM25 检索能力，可一次性安装完整的 Vchord 检索套件：

```bash
pig install pgvector vchord vchord_bm25 pg_tokenizer
```

### Docker 容器 {#docker}

直接启动官方 `pgvector` 容器镜像：

```bash
docker run -d \
  --name pgvector-demo \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  pgvector/pgvector:pg18
```

### Linux 官方软件源（PGDG APT / YUM） {#linux-pgdg}

- **Debian / Ubuntu**（通过 [PostgreSQL APT 仓库](https://wiki.postgresql.org/wiki/Apt)）：
  ```bash
  sudo apt install postgresql-18-pgvector
  ```
- **RHEL / Rocky / AlmaLinux / Fedora**（通过 [PostgreSQL YUM 仓库](https://yum.postgresql.org/)）：
  ```bash
  sudo dnf install pgvector_18
  ```

### macOS（Homebrew） {#macos}

```bash
brew install pgvector
```

### 从源码编译安装（Linux / macOS） {#source}

请确保系统已安装 PostgreSQL 开发头文件（`postgresql-server-dev-*` 或 `postgresql*-devel`）、`make` 及 C 编译器：

```bash
cd /tmp
git clone --branch v0.8.7 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

> [!TIP] CPU 原生指令集优化
> 默认情况下，`pgvector` 的 `Makefile` 会在编译器支持时自动附加 `-march=native` 以充分发挥本机 SIMD 吞吐性能。如需构建跨不同代次 CPU 通用的可移植二进制文件，请执行 `make OPTFLAGS=""`。

---

## 启用扩展 {#enable-the-extension}

连接到目标数据库并启用 `vector` 扩展（需在每个使用向量功能的数据库中执行一次）：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

查看当前安装的扩展版本：

```sql
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

### 升级 `pgvector` {#upgrading-pgvector}

在服务器上更新二进制软件包后，在各数据库中执行以下命令升级 SQL 目录对象定义：

```sql
ALTER EXTENSION vector UPDATE;
```

---

## 快速上手 {#quick-start}

### 1. 创建包含向量列的表 {#create-table}

创建一张包含 3 维单精度浮点（`float32`）向量的表：

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

### 2. 插入、更新与删除向量 {#dml}

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

### 3. 使用 `COPY` 批量导入 {#bulk-loading}

对于百万级以上的大规模数据集，建议使用二进制 `COPY` 替代逐行 `INSERT`：

```sql
COPY items (embedding) FROM STDIN WITH (FORMAT BINARY);
```

### 4. 查询最近邻向量 {#query-nearest-neighbors}

按欧氏距离（L2）检索距离 `'[3,1,2]'` 最近的 5 条记录：

```sql
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

接下来请阅读[查询与过滤检索](/zh/docs/vector/querying/)了解全部六种距离度量与过滤查询模式，或参阅[HNSW 与 IVFFlat 索引](/zh/docs/vector/indexing/)了解如何加速大规模表上的近似检索。
