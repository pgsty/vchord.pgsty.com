---
title: "Kubernetes"
linkTitle: "Kubernetes"
description: "使用 CloudNative-PG 在 Kubernetes 中部署内置 VectorChord 扩展或挂载轻量级扩展镜像卷的 PostgreSQL 集群教程。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/kubernetes.md"
aliases:
  - "/vectorchord/admin/kubernetes/"
---

如果您希望在运行于 Kubernetes 上的 PostgreSQL 中使用 `vectorchord`，本教程将为您提供完整的操作指引。在本教程中，我们将使用 [CloudNative-PG](https://cloudnative-pg.io/) 在 Kubernetes 中部署 PostgreSQL 集群。

<a id="Requirements"></a>
## 环境要求 {#requirements}

| 组件名称 | 版本要求 |
|------|---------|
| [helm](https://helm.sh/) | >= 2.4.1 |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | >= 1.14 |
| [Kubernetes](https://kubernetes.io/) | >= 1.24.0 |
| [Kubernetes（使用镜像卷扩展 Image Volume Extensions）](https://kubernetes.io/) | >= 1.31.0 |

## 安装 CloudNative-PG {#install-cloudnative-pg}

我们使用 [CloudNative-PG (cnpg)](https://cloudnative-pg.io/) 在 Kubernetes 中部署 PostgreSQL 集群。您可以通过 [Helm](https://helm.sh/docs/intro/install/) 安装它：

```shell
$ sudo helm repo add cnpg https://cloudnative-pg.github.io/charts
$ sudo helm upgrade --install cnpg   --namespace cnpg-system   --create-namespace   cnpg/cloudnative-pg
$ helm list --all-namespaces
NAME                    NAMESPACE       REVISION        UPDATED                                 STATUS          CHART                         APP VERSION
cnpg                    cnpg-system     1               2024-12-30 16:37:55.9520917 +0800 CST   deployed        cloudnative-pg-0.23.0               1.25.0   
$ kubectl get pod -n cnpg-system   
NAME                                   READY   STATUS    RESTARTS   AGE
cnpg-cloudnative-pg-54f97dbcdf-jm97n   1/1     Running   0          1m
```

## 内置 `vectorchord` 的 PostgreSQL 镜像 {#postgresql-image-with-vectorchord}

在官方镜像仓库中，我们已经提供了预装 `vectorchord` 的 Docker 镜像，您可以在 [ghcr.io/tensorchord/cloudnative-vectorchord](https://github.com/tensorchord/cloudnative-vectorchord/pkgs/container/cloudnative-vectorchord) 中找到它。如果您希望构建自己的自定义镜像，可以参考以下 Dockerfile：

```dockerfile
ARG CNPG_TAG

FROM ghcr.io/cloudnative-pg/postgresql:$CNPG_TAG-bookworm

ARG CNPG_TAG
ARG VECTORCHORD_TAG
ARG TARGETARCH

# 切换为 root 用户以安装软件包
USER root
ADD https://github.com/tensorchord/VectorChord/releases/download/$VECTORCHORD_TAG/postgresql-${CNPG_TAG%.*}-vchord_${VECTORCHORD_TAG#"v"}-1_$TARGETARCH.deb /tmp/vchord.deb
RUN apt-get install -y /tmp/vchord.deb && rm -f /tmp/vchord.deb

USER postgres
```

## 创建 PostgreSQL 集群 {#create-postgresql-cluster}

我们提供了一份用于在 Kubernetes 中创建 PostgreSQL 集群的示例 YAML 文件，您可以根据实际需求进行修改。请重点注意以下配置项：
- 设置 `shared_preload_libraries` 以加载 `vchord` 共享库。
- 执行 `CREATE EXTENSION IF NOT EXISTS vchord CASCADE;` 以创建 `vchord` 扩展。

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
  name: vchord
spec:
  instances: 1
  bootstrap:
    initdb:
      database: tensorchord
      postInitApplicationSQL:
        - CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
      owner: tensorchord
      secret:
        name: tensorchord
      dataChecksums: true
      encoding: 'UTF8'
  storage:
    size: 1Gi
  imageName: ghcr.io/tensorchord/cloudnative-vectorchord:17
  postgresql:
    shared_preload_libraries: # 加载 vchord 共享库
    - "vchord"
```

您可以安装 `cnpg` 的 [kubectl 插件](https://cloudnative-pg.io/docs/1.28/kubectl-plugin)来管理您的 PostgreSQL 集群。现在，我们可以检查集群的运行状态：

```shell
$ sudo kubectl get pod
vchord-1                                                 1/1     Running     0             42s

$ kubectl cnpg status vchord
Cluster Summary
Name:                vchord
Namespace:           default
System ID:           7527554386501582867
PostgreSQL Image:    ghcr.io/tensorchord/cloudnative-vectorchord:17
Primary instance:    vchord-1
Primary start time:  2025-07-16 05:55:51 +0000 UTC (uptime 53s)
Status:              Cluster in healthy state
Instances:           1
Ready instances:     1
Current Write LSN:   0/204FB50 (Timeline: 1 - WAL File: 000000010000000000000002)

Certificates Status
Certificate Name    Expiration Date                Days Left Until Expiration
----------------    ---------------                --------------------------
vchord-ca           2025-10-14 05:50:08 +0000 UTC  90.00
vchord-replication  2025-10-14 05:50:08 +0000 UTC  90.00
vchord-server       2025-10-14 05:50:08 +0000 UTC  90.00

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
Name      Database Size  Current LSN  Replication role  Status  QoS         Manager Version  Node
----      -------------  -----------  ----------------  ------  ---         ---------------  ----
vchord-1                 0/204FB50    Primary           OK      BestEffort  1.25.0           ip-10-0-2-29.ec2.internal
```

> 注意：本文仅提供最简配置示例，未包含逻辑复制、流式复制以及备份与恢复等高级配置。我们将在后续文章中专门介绍这些内容。您也可以参考 [CloudNative-PG 官方文档](https://cloudnative-pg.io/docs/)了解更多关于 `Cluster` 资源的配置选项。

## 连接到 PostgreSQL 集群 {#connect-to-postgresql-cluster}

您可以使用 `kubectl port-forward` 转发端口并连接到 PostgreSQL 集群：

```shell
$ kubectl port-forward services/vchord-rw 5432:5432
$ psql -h 127.0.0.1 -d tensorchord -U tensorchord
tensorchord=> \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description                                         
---------+---------+------------+---------------------------------------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vchord  | 1.1.1   | public     | vchord: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
 vector  | 0.8.1   | public     | vector data type and ivfflat and hnsw access methods
(3 rows)
```

可以看到 `vchord` 扩展已成功安装。现在您无需额外安装步骤，即可直接按照[快速开始](/zh/docs/getting-started/overview/#quick-start)体验各项功能。


## 轻量级扩展镜像 {#lightweight-extension-images}

在 Kubernetes 上运行 PostgreSQL 时，扩展管理往往是最大的挑战之一。如果您想向[上述一体式镜像](#postgresql-image-with-vectorchord)中添加一个新扩展，通常必须重新构建镜像、备份 PostgreSQL 集群、应用包含新扩展的镜像，然后再恢复集群。这一繁琐流程源于 Kubernetes 中不可变容器（Immutable Containers）的设计理念。

得益于 Andrew Dunstan 和 Matheus Alcantara 的贡献，一项针对 [PostgreSQL 18 的提案](https://commitfest.postgresql.org/patch/4913/)引入了一个新的配置选项（GUC）`extension_control_path`，允许用户为扩展控制文件指定额外的搜索目录。

与此同时，在 Kubernetes 侧，[ImageVolume 特性](https://kubernetes.io/blog/2024/08/16/kubernetes-1-31-image-volume-source/)允许我们将容器镜像作为只读且不可变的卷直接挂载到运行中的 Pod 内部。这使得打包为独立 OCI 兼容容器镜像的 PostgreSQL 扩展，能够直接挂载到 CloudNativePG 集群内的指定目录中。

基于这两项特性，我们构建了轻量级的 `vectorchord` 扩展镜像 [vchord-scratch](https://github.com/tensorchord/VectorChord-images/pkgs/container/vchord-scratch)。

> [!TIP]
> 如果您希望使用[`镜像卷扩展（Image Volume Extensions）`](https://cloudnative-pg.io/docs/1.28/imagevolume_extensions/)，需要满足以下要求：
> - 使用 Kubernetes 1.31.0 或更高版本（推荐使用 1.33.0），并确保已启用 `ImageVolume` 特性门控（Feature Gate）。
> - 使用 CloudNative-PG Helm Chart 0.26.0 或更高版本。


### 使用镜像卷扩展创建 PostgreSQL 集群 {#create-postgresql-cluster-with-image-volume-extensions}

您可以使用以下示例 YAML 文件创建一个挂载 `vectorchord` 扩展镜像的 PostgreSQL 集群，并根据实际需求进行修改。请重点注意以下配置项：
- 设置 `shared_preload_libraries` 以加载 `vchord` 共享库。
- 执行 `CREATE EXTENSION IF NOT EXISTS vchord CASCADE;` 以创建 `vchord` 扩展。
- 设置 `extensions` 字段以指定 `vchord-scratch` 扩展镜像。
- 设置 `extension_control_path` 和 `dynamic_library_path`，以指定扩展控制文件和共享库文件在镜像内的路径。

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
  name: vchord 
spec:
  instances: 1 
  imageName: ghcr.io/cloudnative-pg/postgresql:18-system-bookworm
  bootstrap:
    initdb:
      database: tensorchord
      postInitApplicationSQL:
        - CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
      owner: tensorchord
      secret:
        name: tensorchord
      dataChecksums: true
      encoding: 'UTF8'
  storage:
    size: 1Gi
  postgresql:
    extensions:
      - name: vchord
        image:
          reference: ghcr.io/tensorchord/vchord-scratch:pg18-v1.1.1
        dynamic_library_path:
          - /usr/lib/postgresql/18/lib/
        extension_control_path:
          - /usr/share/postgresql/18/
    shared_preload_libraries:
    - "vchord"
```

接下来，我们可以验证扩展是否已成功安装：

```shell
$ kubectl port-forward services/vchord-rw 5432:5432
$ psql -h
$ psql -h 0.0.0.0 -U tensorchord -d tensorchord
Password for user tensorchord: 
psql (13.3 (Ubuntu 13.3-1.pgdg16.04+1), server 18.0 (Debian 18.0-1.pgdg12+3))
WARNING: psql major version 13, server major version 18.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

tensorchord=> \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description                                         
---------+---------+------------+---------------------------------------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vchord  | 1.1.1   | public     | vchord: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
 vector  | 0.8.1   | public     | vector data type and ivfflat and hnsw access methods
(3 rows)

```

> [!WARNING]
> 镜像 `ghcr.io/cloudnative-pg/postgresql:18-system-bookworm` 默认已内置了 `vchord` 所需的 `pgvector` 扩展。不过，未来的版本中该基础镜像可能会移除内置的 `pgvector`（但短期内我们尚未看到这一趋势）。
