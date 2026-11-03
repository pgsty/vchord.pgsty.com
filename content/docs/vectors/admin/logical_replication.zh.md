---
title: "逻辑复制"
linkTitle: "逻辑复制"
description: "逻辑复制是 PostgreSQL 的一项特性，支持将单个数据库对象或数据子集从一个 PostgreSQL 数据库复制到另一个 PostgreSQL 数据库。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/logical_replication.md"
aliases:
  - "/admin/logical_replication/"
icon: fa-solid fa-clone
---

逻辑复制（Logical Replication）是 PostgreSQL 的一项特性，支持将单个数据库对象或数据子集从一个 PostgreSQL 数据库复制到另一个数据库。

借助逻辑复制，你可以根据预定义的复制规则，有选择地复制特定的表、数据库甚至特定的行。与复制整个数据库集群的物理复制相比，逻辑复制提供了更高的灵活性，允许你设计自定义的复制拓扑结构，并仅复制业务所需的数据。

下面我们将演示如何使用逻辑复制将向量数据从一个 PostgreSQL 数据库复制到另一个数据库。

## 部署源端和目标端 PostgreSQL 集群 {#deploy-source-and-target-postgresql-clusters}

``` shell
$ echo 'version: "3.7"
services:
  source_db:
    image: tensorchord/pgvecto-rs:pg15-v0.2.0
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: password
    command: >
      -c wal_level=logical
      -c shared_preload_libraries=vectors.so
    networks:
      localnet:

  target_db:
    image: tensorchord/pgvecto-rs:pg15-v0.2.0
    ports:
      - "5433:5432"
    environment:
      POSTGRES_PASSWORD: password
    command: >
      -c wal_level=logical
      -c shared_preload_libraries=vectors.so
    networks:
      localnet:

networks:
  localnet:
' > docker-compose.yml

$ docker compose up -d
```

在源数据库和目标数据库中分别创建 `vectors` 扩展：

```shell
# create extension vectors
$ psql -h <source_db_ip> -U postgres -p 5432 
DROP EXTENSION IF EXISTS "vectors";
CREATE EXTENSION "vectors";

$ psql -h <target_db_ip> -U postgres -p 5432
DROP EXTENSION IF EXISTS "vectors";
CREATE EXTENSION "vectors";
```

## 配置逻辑复制 {#configure-logical-replication}

现在我们可以在源数据库和目标数据库之间配置逻辑复制。

### 准备测试数据 {#prepare-test-data}

我们需要在源数据库和目标数据库中分别创建一张名为 `test` 的表，其中包含一个类型为 `vector(10)` 的 `embedding` 列。然后在源数据库和目标数据库的 `test` 表的 `embedding` 列上分别创建索引。最后，向源数据库中插入数据。

#### 创建表 {#create-the-table}

```sql
DROP TABLE IF EXISTS test;
CREATE TABLE test (id integer PRIMARY KEY, embedding vector(10) NOT NULL);
```

#### 创建索引 {#create-the-index}

我们在源数据库和目标数据库的 `test` 表的 `embedding` 列上创建索引。这里使用 `flat`（暴力搜索）索引类型，并选择 `vector_l2_ops`（欧氏距离平方）来度量向量之间的距离。其他索引类型和距离函数请参阅[索引指南](/zh/docs/vectors/usage/indexing/)。

```sql
CREATE INDEX ON test USING vectors (embedding vector_l2_ops) WITH (options = "[indexing.flat]");
```

#### 插入数据 {#insert-data}

我们只需要向源数据库插入数据，数据随后会同步到目标数据库。

```sql
INSERT INTO test
SELECT i, ARRAY[random(), random(),random(),random(),random(),random(),random(),random(),random()]::real[] 
FROM generate_series(1, 100) i;
```

现在你可以在源数据库中搜索 `test` 表 `embedding` 列的最近邻向量：

```sql
postgres=# SELECT id FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
 id 
----
 82
 69
 80
 22
 31
 20
 85
 97
 72
(10 rows)
```

此时如果查询目标数据库，结果将为空：

```sql
SELECT id FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
 id 
----
(0 rows)
```

### 设置逻辑复制 {#set-up-logical-replication}

为了简化在两个 PostgreSQL 数据库之间配置逻辑复制的流程，我们将使用 [pg-easy-replicate](https://github.com/shayonj/pg_easy_replicate)。

我们使用 [pg-easy-replicate](https://github.com/shayonj/pg_easy_replicate) 在源数据库和目标数据库之间建立逻辑复制：

```shell
# get the network name
$ docker network ls | grep  pg
8631dd77129b   pg_regress_localnet   bridge    local

# get source and target container ip
$ docker inspect <container_id> | grep IP

$ docker run -e SOURCE_DB_URL="postgres://postgres:password@<source_db_ip>:5432/postgres"    -e TARGET_DB_URL="postgres://postgres:password@<target_db_ip>:5432/postgres"   -it --rm --network=<network> shayonj/pg_easy_replicate:latest   pg_easy_replicate config_check
/usr/bin/pg_dump
✅ Config is looking good.
```

<a id="Bootstrap"></a>
### 初始化引导（Bootstrap） {#bootstrap}

在正式设置两个数据库之间的同步之前，每次同步都需要先执行初始化引导（Bootstrap）。Bootstrap 会创建一个新的超级用户来执行后续流程所需的编排操作，同时还会创建一些内部元数据表用于记录状态。

```shell
$ docker run -e SOURCE_DB_URL="postgres://postgres:password@<source_db_ip>:5432/postgres"    -e TARGET_DB_URL="postgres://postgres:password@<target_db_ip>:5432/postgres"   -it --rm --network=pg_regress_localnet shayonj/pg_easy_replicate:latest pg_easy_replicate bootstrap --group-name database-cluster-1 --copy-schema
```

### 启动同步 {#start-sync}

Bootstrap 完成后，即可启动同步。启动同步会自动配置发布（Publication）、订阅（Subscription）并完成其他清理维护工作。

```shell
$ docker run -e SOURCE_DB_URL="postgres://postgres:password@192.168.64.2:5432/postgres"    -e TARGET_DB_URL="postgres://postgres:password@192.168.64.3:5432/postgres"   -it --rm --network=pg_regress_localnet shayonj/pg_easy_replicate:latest pg_easy_replicate start_sync --group-name database-cluster-1 
```

## 测试逻辑复制 {#test-logical-replication}

<a id="Query"></a>
### 查询验证 {#query}

现在我们可以查询目标数据库，获取 `test` 表 `embedding` 列中向量的最近邻。查询结果与源数据库完全一致：

```sql
postgres=# SELECT id FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
 id 
----
 82
 69
 80
 22
 31
 20
 85
 97
 72
(10 rows)
```

#### 更新索引 {#update-index}

如果你向源数据库继续插入新数据，数据也会实时同步到目标数据库。向源数据库插入新数据：

```sql
INSERT INTO test
SELECT i, ARRAY[random(), random(),random(),random(),random(),random(),random(),random(),random()]::real[] 
FROM generate_series(101, 200) i;
```

在源数据库中查询：

```sql
postgres=# SELECT id FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
id  
-----
  82
 130
 145
  69
  80
 200
  22
  31
 182
 (10 rows)
```

在目标数据库中查询，将返回相同的结果：

```sql
postgres=# SELECT id FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402, 0.50316447, 0.10779921, 0.80774295, 0.8879849, 0.31292745, 0.05584943, 0.8738258]' LIMIT 10;
id  
-----
  82
 130
 145
  69
  80
 200
  22
  31
 182
 (10 rows)
```
