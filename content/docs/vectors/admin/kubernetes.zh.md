---
title: "Kubernetes"
linkTitle: "Kubernetes"
description: "如果你想在运行于 Kubernetes 上的 PostgreSQL 中使用 pgvecto.rs，本教程将演示如何使用 CloudNative-PG 在 Kubernetes 中部署集群。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/admin/kubernetes.md"
aliases:
  - "/admin/kubernetes/"
---

如果你想在运行于 Kubernetes 上的 PostgreSQL 中使用 `pgvecto.rs`，可以参考本教程。在本教程中，我们将使用 [CloudNative-PG](https://cloudnative-pg.io/) 在 Kubernetes 中部署 PostgreSQL 集群。

<a id="Requirements"></a>
## 环境要求 {#requirements}

| 组件名称 | 版本要求 |
|------|---------|
| [helm](https://helm.sh/) | >= 2.4.1 |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | >= 1.14 |
| [Kubernetes](https://kubernetes.io/) | >= 1.24.0 |

## 安装 CloudNative-PG {#install-cloudnative-pg}

我们使用 [CloudNative-PG (cnpg)](https://cloudnative-pg.io/) 在 Kubernetes 中部署 PostgreSQL 集群。你可以通过 [Helm](https://helm.sh/docs/intro/install/) 安装它：

```shell
$ sudo helm repo add cnpg https://cloudnative-pg.github.io/charts
$ sudo helm upgrade --install cnpg   --namespace cnpg-system   --create-namespace   cnpg/cloudnative-pg
$ helm list --all-namespaces
NAME                    NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                         APP VERSION
cnpg                    cnpg-system     1               2024-01-02 08:17:11.661297545 +0000 UTC deployed        cloudnative-pg-0.20.0         1.22.0     
$ kubectl get pod -n cnpg-system   
NAME                                   READY   STATUS    RESTARTS   AGE
cnpg-cloudnative-pg-67ff4f5f66-94m8d   1/1     Running   0          1m
```

<a id="build-postgresql-image-with-pgvecto-rs"></a>
## 构建包含 `pgvecto.rs` 的 PostgreSQL 镜像 {#build-postgresql-image-with-pgvecto-rs}

我们以官方的 [CloudNative-PG Docker 镜像](https://github.com/cloudnative-pg/postgres-containers)作为基础镜像，并在其中安装 `pgvecto.rs`。你可以在 [Releases 页面](https://github.com/tensorchord/pgvecto.rs/releases)查看可用的 `pgvecto.rs` 版本。

```dockerfile
# syntax=docker/dockerfile-upstream:master
ARG CNPG_TAG

FROM ghcr.io/cloudnative-pg/postgresql:$CNPG_TAG

ARG CNPG_TAG
ARG PGVECTORS_TAG
ARG TARGETARCH

# drop to root to install packages
USER root

# install pgvecto.rs
ADD https://github.com/tensorchord/pgvecto.rs/releases/download/$PGVECTORS_TAG/vectors-pg${CNPG_TAG%.*}_${PGVECTORS_TAG#"v"}_$TARGETARCH.deb ./pgvectors.deb
RUN apt install ./pgvectors.deb

USER postgres
```

```shell
$ docker build -t <your-postgresql-image-repo>:15 --build-arg CNPG_TAG=15 --build-arg PGVECTORS_TAG=v0.1.13   --build-arg TARGETARCH=amd64 .
```

> 注意：PostgreSQL Docker 镜像的 Tag 必须以 `CNPG_TAG`（PostgreSQL 主版本号）开头，以便 CloudNative-PG 识别 Postgres 版本。

## 创建 PostgreSQL 集群 {#create-postgresql-cluster}

下面提供一个用于在 Kubernetes 中创建 PostgreSQL 集群的示例 YAML 文件，你可以根据实际需求进行修改。请注意以下两点：
- 配置 `shared_preload_libraries` 以加载 `pgvecto.rs` 共享库（也可以在 `postInitApplicationSQL` 中配置 `ALTER SYSTEM SET shared_preload_libraries = "vectors.so";` 来加载共享库）。
- 执行 `CREATE EXTENSION IF NOT EXISTS "vectors";` 以创建 `vectors` 扩展。

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tensorchord
type: kubernetes.io/basic-auth
data:
  password: dGVuc29yY2hvcmQ= # tensorchord 
  username: dGVuc29yY2hvcmQ= # tensorchord
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: pgvectors 
spec:
  instances: 1 
  bootstrap:
    initdb:
      database: tensorchord
      postInitApplicationSQL:
        - CREATE EXTENSION IF NOT EXISTS "vectors";
      owner: tensorchord
      secret:
        name: tensorchord
      dataChecksums: true
      encoding: 'UTF8'
  storage:
    size: 1Gi
  imageName: <your-postgresql-image-repo>:<pg-tag>
  postgresql:
    shared_preload_libraries: # load pgvecto.rs shared library
    - "vectors.so"
```

你可以安装 `cnpg` 的 [kubectl 插件](https://cloudnative-pg.io/docs/1.28/kubectl-plugin)来管理 PostgreSQL 集群。现在我们可以查看集群状态：

```shell
$ sudo kubectl get pod
pgvectors-1                                                1/1     Running   0             3m54s

$ kubectl cnpg status pgvectors
Cluster Summary
Name:                pgvectors
Namespace:           default
System ID:           7323107530735296538
PostgreSQL Image:    docker.io/xieydd/pgvectors:15
Primary instance:    pgvectors-1
Primary start time:  2024-01-12 07:17:34 +0000 UTC (uptime 17m33s)
Status:              Cluster in healthy state 
Instances:           1
Ready instances:     1
Current Write LSN:   0/4000000 (Timeline: 1 - WAL File: 000000010000000000000003)

Certificates Status
Certificate Name       Expiration Date                Days Left Until Expiration
----------------       ---------------                --------------------------
pgvectors-ca           2024-04-11 07:12:00 +0000 UTC  89.98
pgvectors-replication  2024-04-11 07:12:00 +0000 UTC  89.98
pgvectors-server       2024-04-11 07:12:00 +0000 UTC  89.98

Continuous Backup status
Not configured

Physical backups
No running physical backups found

Streaming Replication status
Not configured

Unmanaged Replication Slot Status
No unmanaged replication slots found

Managed roles status
No roles managed

Tablespaces status
No managed tablespaces

Instances status
Name         Database Size  Current LSN  Replication role  Status  QoS         Manager Version  Node
----         -------------  -----------  ----------------  ------  ---         ---------------  ----
pgvectors-1  29 MB          0/4000000    Primary           OK      BestEffort  1.22.0           kind-control-plane
```

> 注意：本文仅提供最小化配置示例，不包含逻辑复制、流式复制、备份与恢复等高级配置。更多 `Cluster` 配置项请参阅 [CloudNative-PG 官方文档](https://cloudnative-pg.io/docs/)。

## 连接 PostgreSQL 集群 {#connect-to-postgresql-cluster}

你可以使用 `kubectl port-forward` 转发端口并连接到 PostgreSQL 集群：

```shell
$ kubectl port-forward services/pgvectors-rw 5432:5432
$ psql -h 127.0.0.1 -d tensorchord -U tensorchord
tensorchord=> \dx
Name   | Version |   Schema   |                                         Description                                          
---------+---------+------------+----------------------------------------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vectors | 0.1.13  | public     | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
```

至此，`vectors` 扩展已安装成功。你可以跳过安装步骤，直接体验[快速开始](/zh/docs/vectors/getting-started/overview/)。
