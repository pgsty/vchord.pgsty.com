---
title: "Kubernetes（CloudNativePG）"
linkTitle: "Kubernetes"
description: "用 CloudNativePG 在 Kubernetes 上运行 vchord：用发布包构建运行镜像，或在 PostgreSQL 18 及以上版本把 vchord 作为扩展镜像挂载。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/kubernetes.md"
aliases:
  - "/docs/admin/kubernetes/"
  - "/vectorchord/admin/kubernetes/"
icon: fa-solid fa-dharmachakra
---

[CloudNativePG](https://cloudnative-pg.io/)（CNPG）用容器镜像在 Kubernetes 上运行 PostgreSQL 集群，它的镜像里没有 vchord。PGSTY 不发布容器镜像，需要用 [vchord 发布页](https://github.com/pgsty/vchord/releases/tag/1.5.0)上的 `.deb` 包自己构建。可以为 PostgreSQL 15 到 19 中任一大版本构建完整的运行镜像；PostgreSQL 18 及以上也可以只构建一个很小的扩展镜像，由 CNPG 挂载进它自己的运行镜像。

<a id="requirements"></a><a id="Requirements"></a>

## 安装 Operator {#install-cloudnative-pg}

集群里已经装了 CNPG 的话跳过这一步。

```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  cnpg/cloudnative-pg
kubectl get pods -n cnpg-system
```

## 构建运行镜像 {#postgresql-image-with-vectorchord}

这个镜像基于 CNPG 的 `standard` 镜像（已自带 pgvector），装上同一 PostgreSQL 大版本、同一 CPU 架构的 vchord 包：

```dockerfile
ARG PG_MAJOR=18
FROM ghcr.io/cloudnative-pg/postgresql:${PG_MAJOR}-standard-trixie

ARG PG_MAJOR
ARG VCHORD_VERSION=1.5.0
ARG TARGETARCH
ARG DEB=postgresql-${PG_MAJOR}-vchord_${VCHORD_VERSION}-1_${TARGETARCH}.deb
ARG URL=https://github.com/pgsty/vchord/releases/download/${VCHORD_VERSION}

USER root
ADD ${URL}/${DEB} ${URL}/${DEB}.sha256 /tmp/vchord/
RUN cd /tmp/vchord && sha256sum -c ${DEB}.sha256 && \
    apt-get update && \
    apt-get install -y --no-install-recommends ./${DEB} && \
    rm -rf /tmp/vchord /var/lib/apt/lists/*
USER 26
```

按节点的 CPU 架构构建，并推送到集群能拉取的镜像仓库：

```bash
docker buildx build --platform linux/amd64 --build-arg PG_MAJOR=18 \
  -t registry.example.com/cnpg-vchord:18-1.5.0 --push .
```

## 创建集群 {#create-postgresql-cluster}

预加载 `vchord`，并在应用数据库里创建扩展：

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: vchord
spec:
  instances: 3
  imageName: registry.example.com/cnpg-vchord:18-1.5.0
  storage:
    size: 50Gi
  postgresql:
    shared_preload_libraries:
      - vchord
  bootstrap:
    initdb:
      database: app
      owner: app
      postInitApplicationSQL:
        - CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

```bash
kubectl apply -f cluster.yaml
kubectl get pods -l cnpg.io/cluster=vchord
```

`instances: 3` 表示一个主库加两个流复制副本。要把查询分摊到副本上，见[可扩展性](/zh/docs/vchord/admin/scalability/)。

## 连接与验证 {#connect-to-postgresql-cluster}

CNPG 把 `app` 用户的密码存在 `vchord-app` 这个 Secret 里。转发主库服务的端口，查看已安装的版本：

```bash
kubectl port-forward svc/vchord-rw 5432:5432 &
export PGPASSWORD=$(kubectl get secret vchord-app -o jsonpath='{.data.password}' | base64 -d)
psql -h 127.0.0.1 -U app -d app -c "SELECT extversion FROM pg_extension WHERE extname = 'vchord';"
```

```text
 extversion
------------
 1.5.0
```

## 以扩展镜像挂载 vchord {#lightweight-extension-images}

在 PostgreSQL 18 及以上版本，CNPG 可以把扩展镜像挂载成只读卷，并把它加进 `extension_control_path` 和 `dynamic_library_path`。这样运行镜像用 CNPG 官方的就行，升级 vchord 只需改一个镜像引用。前提条件：

- PostgreSQL 18 及以上，CNPG 1.27 及以上。
- Kubernetes 1.35 及以上；1.33 和 1.34 需要手动打开 `ImageVolume` 特性门控。
- containerd 2.1 及以上，或 CRI-O 1.31 及以上。

镜像里放 `lib/vchord.so` 和 `share/extension/`，这是 CNPG 默认查找的目录结构。下面的 Dockerfile 从发布页的 `.zip` 包取出这些文件：

```dockerfile
FROM --platform=$BUILDPLATFORM debian:trixie-slim AS unpack
ARG PG_MAJOR=18
ARG VCHORD_VERSION=1.5.0
ARG TARGETARCH
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl unzip
RUN case "$TARGETARCH" in amd64) arch=x86_64 ;; arm64) arch=aarch64 ;; esac && \
    zip=postgresql-${PG_MAJOR}-vchord_${VCHORD_VERSION}_${arch}-linux-gnu.zip && \
    cd /tmp && \
    curl -fsSLO https://github.com/pgsty/vchord/releases/download/${VCHORD_VERSION}/${zip} && \
    curl -fsSLO https://github.com/pgsty/vchord/releases/download/${VCHORD_VERSION}/${zip}.sha256 && \
    sha256sum -c ${zip}.sha256 && \
    unzip -q ${zip} -d /tmp/vchord && \
    mkdir -p /out/lib /out/share && \
    cp /tmp/vchord/pkglibdir/* /out/lib/ && \
    cp -r /tmp/vchord/sharedir/extension /out/share/

FROM scratch
COPY --from=unpack /out/ /
```

```bash
docker buildx build --platform linux/amd64,linux/arm64 --build-arg PG_MAJOR=18 \
  -t registry.example.com/vchord-ext:18-1.5.0 --push .
```

<a id="create-postgresql-cluster-with-image-volume-extensions"></a>

然后在集群里引用它。vchord 依赖的 pgvector 由 `standard` 运行镜像提供：

```yaml
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: vchord
spec:
  instances: 3
  imageName: ghcr.io/cloudnative-pg/postgresql:18-standard-trixie
  storage:
    size: 50Gi
  postgresql:
    shared_preload_libraries:
      - vchord
    extensions:
      - name: vchord
        image:
          reference: registry.example.com/vchord-ext:18-1.5.0
  bootstrap:
    initdb:
      database: app
      owner: app
      postInitApplicationSQL:
        - CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

## 升级与限制 {#limits}

- 升级 vchord 时，用新版本构建镜像，修改 `imageName` 或扩展镜像的 `reference`，CNPG 会逐个重启实例。之后在每个数据库里执行 `ALTER EXTENSION vchord UPDATE;`。
- 镜像要按集群的 PostgreSQL 大版本构建，为其他大版本编译的动态库加载不了。
- `minimal` 运行镜像不带 pgvector。用它的话，`CREATE EXTENSION vchord CASCADE` 会失败，除非再挂载一个 pgvector 扩展镜像，或在自己的镜像里装上 pgvector。
- 要加上 `vchord_bm25` 或 `pg_tokenizer`，在同一个运行镜像里装它们的 `.deb` 包即可，比如 [vchord_bm25 发布页](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0)上的 `postgresql-18-vchord-bm25_1.3.0-1_amd64.deb`。`pg_tokenizer` 的包要求 glibc 2.39 及以上，`trixie` 镜像满足，`bookworm` 镜像不满足。
