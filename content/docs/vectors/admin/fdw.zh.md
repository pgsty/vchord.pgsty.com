---
title: "外部数据包装器 (FDW)"
linkTitle: "外部数据包装器 (FDW)"
description: "外部数据包装器（FDW）是 PostgreSQL 的一项扩展，允许你像查询本地表一样访问和查询存储在远程数据库中的数据。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/fdw.md"
aliases:
  - "/admin/fdw/"
---

[外部数据包装器（Foreign Data Wrapper，简称 FDW）](https://wiki.postgresql.org/wiki/Foreign_data_wrappers)是 PostgreSQL 中的一项扩展，允许你像操作本地表一样访问和查询存储在远程数据库中的数据。FDW 提供了一种与不同数据源集成和交互的标准方式。

借助 FDW 扩展，你可以在本地 PostgreSQL 数据库中定义外部表（Foreign Table），用于映射远程数据库中的表结构。这些外部表充当远程数据的代理或包装器，使你能够像操作普通 PostgreSQL 表一样对它们执行 `SELECT`、`INSERT`、`UPDATE` 和 `DELETE` 操作。

在本教程中，我们将使用内置外部数据包装器的 [`postgres_fdw`](https://www.postgresql.org/docs/current/postgres-fdw.html) 模块。该包装器可用于访问存储在外部 PostgreSQL 服务器中的数据。本文将介绍如何使用 `postgres_fdw` 访问已安装 [`pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs) 扩展的远程 PostgreSQL 集群中的向量索引数据。

## 部署本地和远程 PostgreSQL 集群 {#deploy-local-and-foreign-postgresql-clusters}

在本教程中，我们将使用 Docker Compose 部署两个 PostgreSQL 集群。

``` shell
$ echo 'version: "3.7"
services:
  local_db:
    image: tensorchord/pgvecto-rs:pg15-v0.2.0
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: password
    command: >
      -c shared_preload_libraries=vectors.so
    networks:
      localnet:

  foreign_db:
    image: tensorchord/pgvecto-rs:pg15-v0.2.0
    ports:
      - "5433:5432"
    environment:
      POSTGRES_PASSWORD: password
    command: >
      -c shared_preload_libraries=vectors.so
    networks:
      localnet:

networks:
  localnet:
' > docker-compose.yml

$ docker compose up -d
```

```shell
# create extension postgres_fdw in local db
$ psql -h <local_db_ip> -U postgres -p 5432 
DROP EXTENSION IF EXISTS postgres_fdw;
CREATE EXTENSION postgres_fdw;

# create extension vectors in foreign db
$ psql -h <foreign_db_ip> -U postgres -p 5432
DROP EXTENSION IF EXISTS "vectors";
CREATE EXTENSION "vectors";
```

## 远程数据库操作 {#foreign-database-operations}

首先，我们需要在远程数据库（`foreign_db`）中创建一张 `test` 表并在其上构建向量索引。`test` 表包含两列：`id` 和 `embedding`。其中 `embedding` 列是类型为 `vector(10)` 的向量列，`id` 列是 `test` 表的主键。

### 创建表 {#create-a-table}

```sql
DROP TABLE IF EXISTS test;
CREATE TABLE test (id integer PRIMARY KEY, embedding vector(10) NOT NULL);
INSERT INTO test SELECT i, ARRAY[random(),random(),random(),random(),random(),random(),random(),random(),random(),random()]::real[] FROM generate_series(1, 100) i;
```

### 创建用户 {#create-a-user}

在远程数据库中创建一个名为 `fdw_user` 的用户，并将 `test` 表上的 `SELECT`、`INSERT`、`UPDATE`、`DELETE` 权限授予 `fdw_user`：

```sql
CREATE USER fdw_user WITH ENCRYPTED PASSWORD 'secret';
GRANT SELECT,INSERT,UPDATE,DELETE ON TABLE test TO fdw_user;
```

### 创建索引 {#create-the-index}

在 `test` 表的 `embedding` 列上创建向量索引。这里使用 `flat`（暴力搜索）索引类型，并选择 `vector_l2_ops`（欧氏距离平方）来度量向量距离。其他索引类型和距离函数请参阅[索引指南](/zh/docs/vectors/usage/indexing/)。

```sql
CREATE INDEX ON test USING vectors (embedding vector_l2_ops) WITH (options = "[indexing.flat]");
```

## 本地数据库操作 {#local-database-operations}

在本地数据库中，我们需要创建一张本地表 `local` 和一个外部服务器 `foreign_server`。`local` 表包含两列：`id` 和 `name`，其中 `id` 是主键。`foreign_server` 用于连接访问远程数据库。

### 创建本地表 {#create-local-table}

```sql
DROP TABLE IF EXISTS local;
CREATE TABLE local (id integer PRIMARY KEY, name VARCHAR(50) NOT NULL);
INSERT INTO local (id, name) VALUES (1, 'terry'), (2, 'jason'), (3, 'curry');
```

### 创建本地用户 {#create-local-user}

使用超级用户在本地 PostgreSQL 数据库中执行以下语句，创建一个名为 `local_user` 的普通用户：

```sql
CREATE USER local_user WITH ENCRYPTED PASSWORD 'secret';
```

### 创建外部服务器 {#create-the-foreign-server}

使用 `CREATE SERVER` 语句创建外部服务器时，需要指定远程数据库的主机地址、端口和数据库名称：

```sql
CREATE SERVER foreign_server
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (host '<foreign_db_ip>', port '5432', dbname 'postgres');
```

### 创建用户映射 {#create-the-user-mapping}

使用 `CREATE USER MAPPING` 语句创建本地用户与远程用户之间的映射关系，需提供远程用户的用户名和密码：

```sql
CREATE USER MAPPING FOR local_user
    SERVER foreign_server
    OPTIONS (user 'fdw_user', password 'secret');
```

### 创建外部表 {#creat-the-foreign-table}

使用 `CREATE FOREIGN TABLE` 语句创建远程表的映射表。需要注意，每一列的数据类型必须与远程表的实际类型匹配，并且建议保持列名一致；否则，你需要为每个列单独使用 `column_name` 参数指定远程表中的列名。

```sql
CREATE FOREIGN TABLE foreign_test (id integer, embedding vector(10) NOT NULL)
    SERVER foreign_server
    OPTIONS (schema_name 'public', table_name 'test');
```

<a id="Authorization"></a>
### 权限授予 {#authorization}

为 `local_user` 授予所需权限：
- 授予 `local_user` 使用 `postgres_fdw` 的权限。
- 授予 `local_user` 使用外部服务器 `foreign_server` 的权限。
- 授予 `local_user` 访问 `public` Schema 下所有表的权限。

```sql
GRANT USAGE ON FOREIGN DATA WRAPPER postgres_fdw TO local_user;
GRANT USAGE ON FOREIGN SERVER foreign_server TO local_user;
GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO local_user;
```

<a id="Query"></a>
## 查询测试 {#query}

现在我们可以在本地数据库中通过连接查询（JOIN）访问外部表：

```shell
$ psql -h <local_db_ip> -U local_user -p 5432 -d postgres
```

```sql
SELECT l.id, l.name FROM local l LEFT JOIN foreign_test f on l.id = f.id ORDER BY f.embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
 id | name  
----+-------
  2 | jason
  3 | curry
  1 | terry


EXPLAIN SELECT l.id, l.name FROM local l LEFT JOIN foreign_test f on l.id = f.id ORDER BY f.embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
 Limit  (cost=209.63..209.65 rows=10 width=126)
   ->  Sort  (cost=209.63..213.04 rows=1365 width=126)
         Sort Key: ((f.embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]'::vector))
         ->  Hash Right Join  (cost=122.15..180.13 rows=1365 width=126)
               Hash Cond: (f.id = l.id)
               ->  Foreign Scan on foreign_test f  (cost=100.00..150.95 rows=1365 width=36)
               ->  Hash  (cost=15.40..15.40 rows=540 width=122)
                     ->  Seq Scan on local l  (cost=0.00..15.40 rows=540 width=122)
```
