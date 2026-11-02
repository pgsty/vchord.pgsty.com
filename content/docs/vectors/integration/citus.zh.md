---
title: "Citus"
linkTitle: "Citus"
description: "Citus 是将 Postgres 转化为分布式数据库的 PostgreSQL 扩展。pgvecto.rs 可与 Citus 良好配合，本文介绍在分布式 PostgreSQL 实例中启用向量检索的步骤。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/integration/citus.md"
aliases:
  - "/integration/citus/"
---

`citus` 是一个将 Postgres 转化为分布式数据库的 PostgreSQL 扩展。`pgvecto.rs` 能够与 `citus` 良好协作。下面介绍如何在分布式 PostgreSQL 实例中启用向量检索。

`citus` 支持在[单节点（Single-Node）](https://docs.citusdata.com/en/latest/installation/single_node.html)和[多节点（Multi-Node）](https://docs.citusdata.com/en/latest/installation/multi_node.html)模式下运行，这两种模式均原生兼容 `pgvecto.rs`。

## 单节点 Citus {#single-node-citus}

首先，准备一个同时安装了 `pgvecto.rs` 和 `citus` 的 Dockerfile，并将它们加载到 PostgreSQL 中。

> [!DETAILS]
> 由于 `citus` 的自身限制，在 `shared_preload_libraries` 中必须将 `citus` 放在第一位。

```dockerfile
FROM tensorchord/pgvecto-rs-binary:pg16-v0.3.0-amd64 as binary

FROM postgres:16
COPY --from=binary /pgvecto-rs-binary-release.deb /tmp/vectors.deb
RUN apt-get update && apt-get install -y curl
RUN apt-get install -y /tmp/vectors.deb && rm -f /tmp/vectors.deb
RUN curl https://install.citusdata.com/community/deb.sh -o deb.sh
RUN bash deb.sh 
RUN apt-get install -y postgresql-16-citus-12.1

CMD ["postgres", "-c" ,"shared_preload_libraries=citus,vectors.so", "-c", "search_path=\"$user\", public, vectors"]
```

接着在本地构建名为 `citus-vector:16` 的 Docker 镜像并启动容器。

> [!WARNING]
> 请勿在生产环境中使用 `POSTGRES_HOST_AUTH_METHOD: "trust"`。详细的认证配置请参阅 `citus` 文档中关于[提高 Worker 安全性（Increasing Worker Security）](https://docs.citusdata.com/en/latest/admin_guide/cluster_management.html#worker-security)的说明。

```shell
docker build -t citus-vector:16 .
docker run --name citus-single -e POSTGRES_HOST_AUTH_METHOD=trust -p 5432:5432 -d citus-vector:16
```

要启用所需扩展，请使用 `psql` 连接到容器并执行以下 SQL 命令：

```sql
-- psql -h 127.0.0.1 -d postgres -U postgres -w
CREATE EXTENSION IF NOT EXISTS citus;
CREATE EXTENSION IF NOT EXISTS vectors;
```

扩展创建完成后，你可以先创建一张普通表，然后将其转换为[分布式表（distributed table）](https://docs.citusdata.com/en/latest/get_started/tutorial_multi_tenant.html#distributing-tables-and-loading-data)。

```sql
CREATE TABLE items (id bigserial, embedding vector(3), category_id bigint, PRIMARY KEY (id, category_id));
SET citus.shard_count = 4;
SELECT create_distributed_table('items', 'category_id');
```

之后的[索引构建](/zh/docs/vectors/usage/indexing/)和[向量检索](/zh/docs/vectors/usage/search/)操作与单机版完全一致。表和索引会自动分发到所有分片（Shard）/ 工作节点（Worker）上。

```sql
INSERT INTO items (embedding, category_id)
SELECT '[1, 1, 1]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000)
UNION ALL
SELECT '[1, 2, 3]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000)
UNION ALL
SELECT '[3, 2, 1]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000);
CREATE INDEX ON items USING vectors (embedding vector_cos_ops) WITH (options = "[indexing.hnsw]");
SELECT id FROM items ORDER BY embedding <=> '[1, 1, 1]' LIMIT 100;
```

## 多节点 Citus {#multi-node-citus}

你可以复用与[单节点 Citus](#single-node-citus) 相同的 Dockerfile 和镜像来部署多节点 `citus`。
在本示例中，我们将使用 Docker Compose 启动一个包含 1 个协调器节点（Coordinator）和 2 个工作节点（Worker）的集群。

> [!WARNING]
> 请勿在生产环境中使用 `POSTGRES_HOST_AUTH_METHOD: "trust"`。详细的认证配置请参阅 `citus` 文档中关于[提高 Worker 安全性（Increasing Worker Security）](https://docs.citusdata.com/en/latest/admin_guide/cluster_management.html#worker-security)的说明。

```yaml
services:
  main:
    container_name: main
    image: 'citus-vector:16'
    ports:
      - "5432:5432"
    environment:
      POSTGRES_HOST_AUTH_METHOD: "trust"
  worker1:
    container_name: worker1
    image: 'citus-vector:16'
    ports:
      - "5431:5432"
    environment:
      POSTGRES_HOST_AUTH_METHOD: "trust"
  worker2:
    container_name: worker2
    image: 'citus-vector:16'
    ports:
      - "5430:5432"
    environment:
      POSTGRES_HOST_AUTH_METHOD: "trust"
```

使用 Docker Compose 启动所有容器。每个容器对应一个 `citus` 节点，包括 1 个协调器节点（`main`）和 2 个工作节点。

```shell
docker compose up -d
```

与之前一样，需要启用相关扩展，但请确保在**所有节点**上都执行该命令：

```shell
psql -h 127.0.0.1 -d postgres -U postgres -w -c 'CREATE EXTENSION IF NOT EXISTS citus;CREATE EXTENSION IF NOT EXISTS vectors;'
psql -h 127.0.0.1 -d postgres -U postgres -w -p 5431 -c 'CREATE EXTENSION IF NOT EXISTS citus;CREATE EXTENSION IF NOT EXISTS vectors;'
psql -h 127.0.0.1 -d postgres -U postgres -w -p 5430 -c 'CREATE EXTENSION IF NOT EXISTS citus;CREATE EXTENSION IF NOT EXISTS vectors;'
```

为了让协调器知晓工作节点的信息，请使用 `psql` 连接到协调器节点，并注册这两个工作节点：

```sql
-- psql -h 127.0.0.1 -d postgres -U postgres -w
SELECT citus_set_coordinator_host('main', 5432);
SELECT * from citus_add_node('worker1', 5432);
SELECT * from citus_add_node('worker2', 5432);
```

最后，你可以按照与[单节点 Citus](#single-node-citus) 完全相同的方式执行向量查询：

```sql
CREATE TABLE items (id bigserial, embedding vector(3), category_id bigint, PRIMARY KEY (id, category_id));
SET citus.shard_count = 4;
SELECT create_distributed_table('items', 'category_id');
INSERT INTO items (embedding, category_id) 
SELECT '[1, 1, 1]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000)
UNION ALL
SELECT '[1, 2, 3]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000)
UNION ALL
SELECT '[3, 2, 1]'::vector, FLOOR(random() * 100) FROM generate_series(1, 1000);
CREATE INDEX ON items USING vectors (embedding vector_cos_ops) WITH (options = "[indexing.hnsw]");
SELECT id FROM items ORDER BY embedding <-> '[1, 1, 1]' LIMIT 100;
```

<a id="Monitor"></a>
## 监控 {#monitor}

如果你使用的是 `citus` 分布式表，协调器节点上的 `pg_vector_index_stat` 视图将为空。因为所有索引实际上都创建在工作节点上，所以我们需要将查询分发到各个工作节点来查看向量索引状态：

```sql
SELECT * from run_command_on_workers($$ SELECT (to_json(array_agg(pg_vector_index_stat .*))) FROM pg_vector_index_stat $$);
```
