---
title: "Kubernetes (CloudNativePG)"
linkTitle: "Kubernetes"
description: "Run vchord on Kubernetes with CloudNativePG: build an operand image from the release packages, or mount vchord as an extension image on PostgreSQL 18 and later."
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/kubernetes.md"
aliases:
  - "/docs/admin/kubernetes/"
  - "/vectorchord/admin/kubernetes/"
icon: fa-solid fa-dharmachakra
---

[CloudNativePG](https://cloudnative-pg.io/) (CNPG) runs PostgreSQL clusters on Kubernetes from container images, and its images do not include vchord. PGSTY does not publish a container image, so you build one from the `.deb` packages on the [vchord release page](https://github.com/pgsty/vchord/releases/tag/1.5.0). Build a full operand image for any PostgreSQL major from 15 to 19; on PostgreSQL 18 and later you can instead build a small extension image that CNPG mounts into its own operand image.

<a id="requirements"></a><a id="Requirements"></a>

## Install the operator {#install-cloudnative-pg}

Skip this step if CNPG already runs in your cluster.

```bash
helm repo add cnpg https://cloudnative-pg.github.io/charts
helm upgrade --install cnpg \
  --namespace cnpg-system \
  --create-namespace \
  cnpg/cloudnative-pg
kubectl get pods -n cnpg-system
```

## Build an operand image {#postgresql-image-with-vectorchord}

This image extends CNPG's `standard` image, which already contains pgvector, with the vchord package for the same PostgreSQL major and CPU architecture:

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

Build it for the architecture of your nodes and push it to a registry the cluster can pull from:

```bash
docker buildx build --platform linux/amd64 --build-arg PG_MAJOR=18 \
  -t registry.example.com/cnpg-vchord:18-1.5.0 --push .
```

## Create the cluster {#create-postgresql-cluster}

Preload `vchord` and create the extension in the application database:

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

`instances: 3` is one primary and two streaming replicas. To spread queries across the replicas, see [Scalability](/docs/vchord/admin/scalability/).

## Connect and verify {#connect-to-postgresql-cluster}

CNPG stores the `app` user's password in the `vchord-app` secret. Forward the primary's service and check the installed version:

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

## Mount vchord as an extension image {#lightweight-extension-images}

On PostgreSQL 18 and later, CNPG can mount an extension image as a read-only volume and add it to `extension_control_path` and `dynamic_library_path`, so you keep CNPG's own operand image and upgrade vchord by changing one image reference. This needs:

- PostgreSQL 18 or later and CNPG 1.27 or later.
- Kubernetes 1.35 or later, or 1.33 and 1.34 with the `ImageVolume` feature gate turned on.
- containerd 2.1 or later, or CRI-O 1.31 or later.

The image holds `lib/vchord.so` and `share/extension/`, the layout CNPG looks for by default. This Dockerfile fills it from the release `.zip` package:

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

Then reference it from the cluster. The `standard` operand image provides pgvector, which vchord requires:

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

## Upgrade and limits {#limits}

- To upgrade vchord, build an image with the new version and change `imageName` or the extension image `reference`. CNPG restarts the instances one at a time. Then run `ALTER EXTENSION vchord UPDATE;` in each database.
- Build for the PostgreSQL major of the cluster. A library built for another major does not load.
- A `minimal` operand image has no pgvector. With it, `CREATE EXTENSION vchord CASCADE` fails until you also mount a pgvector extension image or install pgvector in your own image.
- To add `vchord_bm25` or `pg_tokenizer`, install their `.deb` packages in the same operand image, for example `postgresql-18-vchord-bm25_1.3.0-1_amd64.deb` from the [vchord_bm25 release page](https://github.com/pgsty/vchord_bm25/releases/tag/1.3.0). The `pg_tokenizer` packages need glibc 2.39 or later, which `trixie` images have and `bookworm` images do not.
