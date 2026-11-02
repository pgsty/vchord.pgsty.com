---
title: "常见问答"
linkTitle: "常见问答"
description: "在大多数情况下，找不到向量类型或操作符类是由于缺少 Schema 搜索路径（search_path）或权限不足导致的。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/faqs/general.md"
aliases:
  - "/faqs/general/"
---

> [!WARNING]
> 我们强烈建议你了解并选用我们全新的 [VectorChord](https://github.com/pgsty/vchord) 实现，它提供了更高的稳定性和性能。建议现有用户迁移至 VectorChord，具体步骤请参阅[迁移指南](/zh/docs/admin/migration/)。

## 找不到向量类型或操作符类 {#the-vector-type-or-operator-class-is-not-found}

在大多数情况下，这是由于缺少 Schema 搜索路径（`search_path`）或权限不足导致的。

请按照以下检查清单逐一排查：

1. 在 `psql` 中运行 `\dx` 或执行 `SELECT * FROM pg_extension;`，检查扩展是否已安装：

```bash
postgres=# \dx
                                                    List of installed extensions
  Name   |    Version    |   Schema   |                                         Description                                          
---------+---------------+------------+----------------------------------------------------------------------------------------------
 vectors | 0.3.0         | vectors    | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
```

如果未安装，请执行 `CREATE EXTENSION vectors;` 进行安装。

2. 运行 `SHOW search_path;`，检查其中是否包含 `vectors`：

```bash
postgres=# SHOW search_path;
       search_path        
--------------------------
 "$user", public, vectors
```

如果不包含，请执行 `SET search_path="$user", public, vectors;` 进行设置。

3. 如果 `pgvecto.rs` 是由其他超级用户安装的：

请在 `psql` 中运行 `\dn` 或执行 `SELECT nspname FROM pg_catalog.pg_namespace;`，检查 `vectors` Schema 是否存在且当前用户是否有权访问：

```bash
postgres=# SELECT current_user;
 current_user 
--------------
 tensorchord

postgres=# \dn
       List of schemas
  Name   |       Owner       
---------+-------------------
 public  | pg_database_owner
 vectors | postgres
```

如果当前用户无权访问，请以超级用户身份登录并将 Schema 权限授予当前用户（`current_user`）：

`GRANT ALL ON SCHEMA vectors to tensorchord;`
