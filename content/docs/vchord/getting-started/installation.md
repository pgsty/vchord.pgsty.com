---
title: "Installation"
linkTitle: "Installation"
description: "VectorChord is tested on the following operating system:"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/installation.md"
aliases:
  - "/docs/getting-started/installation/"
  - "/vectorchord/getting-started/installation/"
icon: fa-solid fa-download
---

`vchord` 1.2.0 is formally released for PostgreSQL 14–18. Pre-built native RPM and DEB packages are published for EL 8/9/10, Debian 12/13, and Ubuntu 22.04/24.04/26.04 on Linux `x86_64` and `aarch64` (see the [Download page](/download/) and [PGEXT release matrix](https://pgext.cloud/ext/vchord)). The source tree is also tested on macOS, Windows, Alpine Linux, and additional architectures in CI.

The current release is installed from the `pgsty/vchord` repository or the Pigsty package repository. PostgreSQL 19 builds are development validation only and are not part of the release support matrix.

* Ubuntu (x86_64, aarch64)
* MacOS (x86_64, aarch64)
* Windows (x86_64)
* Alpine Linux (x86_64, aarch64) [^1]
* Debian (powerpc64le, s390x, riscv64) [^2]

[^1]: CI coverage includes PostgreSQL 15–17 on Alpine Linux 3.22.
[^2]: CI coverage includes PostgreSQL 14–18 on `powerpc64le`, and selected PostgreSQL 15/17 jobs on `s390x` and `riscv64` with QEMU user-space emulation. These are source/CI targets; native binary packages target `x86_64` and `aarch64`.

Please report a bug if you encounter issues on any of the above operating systems, or submit a feature request for additional platform support.

<a id="Docker"></a>
## Docker

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for its maintained releases. These upstream instructions are retained for reference and will be updated.

### VectorChord Image

<a href="https://hub.docker.com/r/tensorchord/vchord-postgres"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-postgres" /></a>

The easiest way to try VectorChord is to run it from a ready-to use [Docker image](https://hub.docker.com/r/tensorchord/vchord-postgres).

1. Launch a VectorChord container in Docker.

```sh
docker run \
  --name vchord-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/vchord-postgres:pg18-v1.1.1
```

2. Connect to the database using the `psql` command line tool. The default username is `postgres`.

```sh
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

> [!TIP]
>
> To achieve full performance, please mount the volume to PostgreSQL data directory by adding the option like:
>
> * `-v $PWD/pgdata:/var/lib/postgresql/18/docker`, on PostgreSQL 18
> * `-v $PWD/pgdata:/var/lib/postgresql/data`, on PostgreSQL 14, 15, 16 and 17
>
> You can configure PostgreSQL by the reference of the parent image in https://hub.docker.com/_/postgres/.
>


### VectorChord Suite Image

<a href="https://hub.docker.com/r/tensorchord/vchord-suite"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-suite"/></a>

In addition to the base image with the VectorChord extension, we provide an all-in-one image, `tensorchord/vchord-suite:pg18-latest`. This comprehensive image includes all official TensorChord extensions. Developers should select an image tag that is compatible with their extension's version, as indicated in [the support matrix](https://github.com/tensorchord/VectorChord-images?tab=readme-ov-file#support-matrix).

1. Launch a VectorChord container in Docker.

```sh
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
  # If you want to use ghcr image, you can change the image to `ghcr.io/tensorchord/vchord-suite:pg18-latest`.
  # if you want to use the specific version, you can use the tag `pg17-20250815`, supported version can be found in the support matrix.
```

Other sections may align with the above.

### VectorChord Scratch Image

<a href="https://hub.docker.com/r/tensorchord/vchord-scratch"><img src="https://img.shields.io/docker/pulls/tensorchord/vchord-scratch" /></a>

We provide a scratch image that contains only the files of VectorChord. You can install VectorChord in any image using Docker's `COPY`, like

```dockerfile
FROM tensorchord/vchord-scratch:pg18-v1.1.1 AS vchord_scratch
FROM postgres:18-bookworm
RUN apt-get update && apt-get install -y postgresql-18-pgvector
COPY --from=vchord_scratch / /
CMD ["postgres", "-c" ,"shared_preload_libraries=vchord,vector"]
```

This image can also be used as a CloudNativePG image volume extension. See also

* [Image Volume Extensions](https://cloudnative-pg.io/docs/1.28/imagevolume_extensions/)
* [Kubernetes](/docs/vchord/admin/kubernetes/)

<a id="Source"></a>
## Source

> [!TIP]
>
> Build requirements:
>
> * any port of `make`
> * `clang >= 16` with `libclang`
> * `rust >= 1.93` with `cargo`
>
> It's recommended to use Rustup for installing Rust on most platforms, while on Alpine Linux, using the system package manager is advised.
>
> You can set the environment variable `CC` to specify the desired C compiler for the build system. If you do not set this variable, the build system automatically searches for clang and gcc. To compile all C code with clang, set `CC` to the path of clang. To compile all C code with gcc, set `CC` to the path of gcc; note that in this case, there is a requirement `gcc >= 14`.
>
> Rust version requirement is not a long-term guarantee; we will raise the required Rust version with each new release.
>
> These build requirements apply only to x86_64 and aarch64. For all other architectures, including powerpc64le, s390x and riscv64, nightly Rust and latest Clang are required.
>


If you have not installed PostgreSQL yet, please install PostgreSQL. If you have not installed pgvector yet, you could install pgvector before the 3rd step.

1. Download the source code, build and install it with `make`.

```sh
curl -fsSL https://github.com/pgsty/vchord/archive/refs/tags/1.2.0.tar.gz | tar -xz
cd vchord-1.2.0
PG_CONFIG=/path/to/pg_config make build
PG_CONFIG=/path/to/pg_config make install # or `sudo make install`
```

2. Configure your PostgreSQL by modifying the `shared_preload_libraries` to include the extension. And then restart the PostgreSQL cluster.

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="Tuning"></a>
### Tuning

VectorChord performs runtime CPU dispatch for SIMD code. If you want the compiler to optimize the whole program for a particular CPU, you could instruct it to generate code for that CPU.

```sh
RUSTFLAGS="-Ctarget-cpu=icelake" make build
```

To see all valid CPU options and the default CPU for your target triple, run:

```sh
rustc --print target-cpus
```

To generate code for the host machine, run:

```sh
RUSTFLAGS="-Ctarget-cpu=native" make build
```

Please note that binaries generated with a specific `target-cpu` are not compatible with other CPUs.

You can also do it by using Cargo's configuration.

```sh
cd vchord-1.2.0
mkdir -p .cargo
touch .cargo/config.toml
echo 'build.rustflags = ["-Ctarget-cpu=icelake"]' >> ./cargo/config.toml
```

<a id="Debian"></a>
## Debian

If you have not installed PostgreSQL yet, please install PostgreSQL following https://www.postgresql.org/download/linux/debian/. If you have not installed pgvector yet, you could install pgvector by `apt install postgresql-16-pgvector` before the 3rd step. Replace `16` with your PostgreSQL major version.

> [!TIP] Current release
> The current PGSTY release is `vchord` 1.2.0. The example below uses PostgreSQL 16; replace `16` and `amd64` with the PostgreSQL major version and architecture of the package you downloaded.


1. Download Debian packages in [the release page](https://github.com/pgsty/vchord/releases), and install them by `apt`.

```sh
wget https://github.com/pgsty/vchord/releases/download/1.2.0/postgresql-16-vchord_1.2.0-1_amd64.deb
sudo apt install ./postgresql-16-vchord_1.2.0-1_amd64.deb
```

2. Configure your PostgreSQL by modifying the `shared_preload_libraries` to include the extension. And then restart the PostgreSQL cluster.

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
sudo systemctl restart postgresql.service
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="Ubuntu"></a>
## Ubuntu

If you have not installed PostgreSQL yet, please install PostgreSQL following https://www.postgresql.org/download/linux/ubuntu/. If you have not installed pgvector yet, you could install pgvector by `apt install postgresql-16-pgvector` before the 3rd step. Replace `16` with your PostgreSQL major version.

> [!TIP] Current release
> The current PGSTY release is `vchord` 1.2.0. The example below uses PostgreSQL 16; replace `16` and `amd64` with the PostgreSQL major version and architecture of the package you downloaded.


1. Download Debian packages in [the release page](https://github.com/pgsty/vchord/releases), and install them by `apt`.

```sh
wget https://github.com/pgsty/vchord/releases/download/1.2.0/postgresql-16-vchord_1.2.0-1_amd64.deb
sudo apt install ./postgresql-16-vchord_1.2.0-1_amd64.deb
```

2. Configure your PostgreSQL by modifying the `shared_preload_libraries` to include the extension. And then restart the PostgreSQL cluster.

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
sudo systemctl restart postgresql.service
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

<a id="PGXN"></a>
## PGXN

> [!TIP]
>
> See [Source](#source) for build requirements.
>


If you have not installed PostgreSQL yet, please install PostgreSQL. If you have not installed pgvector yet, you could install pgvector by `pgrxclient install vector` before the 3rd step.

1. Install VectorChord from [PostgreSQL Extension Network](https://pgxn.org/dist/vchord) with:

```sh
pgxnclient install vchord # or `pgxnclient install vchord --sudo`
```

2. Configure your PostgreSQL by modifying the `shared_preload_libraries` to include the extension. And then restart the PostgreSQL cluster.

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

> [!TIP]
>
> PGXN is a historical distribution path for the upstream VectorChord project. For the PGSTY 1.2.0 release, use the Pigsty or GitHub release packages above.
>


## Prebuilt binaries

{{< badge text="deprecated" tone="danger" >}}

> [!WARNING]
>
> Prebuilt binaries may not match the PostgreSQL in ABI on your machine, which could cause silent errors. We strongly recommend that you build from source in this case.
>


If you have not installed PostgreSQL yet, please install PostgreSQL. If you have not installed pgvector yet, you could install pgvector before the 3rd step.

1. Download prebuilt binaries in [the release page](https://github.com/pgsty/vchord/releases), and repackage it referring to your distribution's documentation. Then install it by system package manager. We do not recommend doing this, but if you wish, you can also manually copy the files to the system directory.

```sh
cp -r ./pkglibdir/. $(pg_config --pkglibdir)
cp -r ./sharedir/. $(pg_config --sharedir)
```

2. Configure your PostgreSQL by modifying the `shared_preload_libraries` to include the extension. And then restart the PostgreSQL cluster.

```sh
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'vchord'"
```

3. Run the following SQL to ensure the extension is enabled.

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

## Upgrading to 1.2.0

To upgrade from `1.1.1` (or any earlier release from `0.2.0` onward), install the 1.2.0 library and extension SQL files for your PostgreSQL major version, then restart PostgreSQL to load the new preloaded library. Direct upgrade paths from `0.2.0` through `1.1.1` are included, along with compatibility symbols so extensions registered before `1.0.0` can complete `ALTER EXTENSION` cleanly. Run this in each database using `vchord`:

```sql
ALTER EXTENSION vchord UPDATE TO '1.2.0';
SELECT extversion FROM pg_extension WHERE extname = 'vchord';
```
