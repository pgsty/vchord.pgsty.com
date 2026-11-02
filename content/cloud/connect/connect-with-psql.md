---
title: "Connecting with psql"
linkTitle: "Connecting with psql"
description: "The following instructions require a working installation of psql. The psql client is the native command-line client for Postgres. It provides an interactive se"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/connect/connect-with-psql.md"
---

The following instructions require a working installation of [psql](https://www.postgresql.org/download/). The psql client is the native command-line client for Postgres. It provides an interactive session for sending commands to Postgres and running ad-hoc queries. For more information about psql, refer to the [psql reference](https://www.postgresql.org/docs/15/app-psql.html), in the PostgreSQL Documentation.

> [!WARNING]
> Cluster instance runs Postgres, which means that any Postgres application or standard utility such as psql is compatible with VectorChord Cloud. You can also use Postgres client libraries and drivers to connect. However, please be aware that some older client libraries and drivers, including older psql executables, are built without [Server Name Indication (SNI)](https://en.wikipedia.org/wiki/Server_Name_Indication) support and require a workaround.


The easiest way to connect to VectorChord Cloud using psql is to use a connection endpoint. You can obtain a connection endpoint from the **cluster details** on the dashboard. 

![](/cloud/images/two_types_connections.png)

We provide two types of connection endpoints:
- Super User Endpoint: This connection string is used to connect to the cluster as a superuser(postgres). You can use this connection string to create databases, users, and manage the cluster.
- Vector User Endpoint: This connection string is used to connect to the cluster as a vector user. You can use this connection string to store and query vector data.

If `Enable Connection Pooler` is selected when create cluster, you can get the pooler connection endpoint via clicking the `Show Pooler Endpoint` button.

![](/cloud/images/two_types_pooler_connections.png)

From your terminal or command prompt, run the psql client with the connection endpoint copied from the **Dashboard**.

```shell
$ psql postgres://[user]:[password]@[hostname]/[dbname]
```

> [!WARNING]
> VectorChord Cloud requires that all connections use SSL/TLS encryption, but you can increase the level of protection by appending an sslmode parameter setting to your connection string.
