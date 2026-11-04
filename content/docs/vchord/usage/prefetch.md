---
title: "Prefetch"
linkTitle: "Prefetch"
description: "Prefetch dramatically accelerates queries that involve I/O operations. It works by proactively reading buffers into operating system page cache or PostgreSQL's "
weight: 120
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prefetch.md"
aliases:
  - "/docs/usage/prefetch/"
  - "/vectorchord/usage/prefetch/"
icon: fa-solid fa-bolt
---

{{< badge text="since v0.4.0" tone="info" >}}


Prefetch dramatically accelerates queries that involve I/O operations. It works by proactively reading buffers into operating system page cache or PostgreSQL's buffer pool based on the actual needs of the index.

Prefetch helps overlap I/O with computation, as well as I/O with other I/O operations, significantly reducing the time spent waiting for buffers during query execution, thereby improving overall query performance.

> [!TIP]
> This feature is enabled by default. Any query can benefit from prefetching with VectorChord `0.4.0` and later versions.


Prior to version `0.4.0`, VectorChord used PostgreSQL's synchronous I/O interface. Since then, VectorChord utilizes asynchronous I/O interface on newer versions of PostgreSQL. The I/O interface used by VectorChord can be controlled via GUC parameters.

In the GUC parameters, the synchronous I/O interface is referred to as `read_buffer`, the asynchronous I/O interface as `read_stream`, and VectorChord's simulated asynchronous interface as `prefetch_buffer`.

For indexes much smaller than the memory, there is almost no difference among the three prefetch modes. `read_stream` accelerates all disk-based indexes; however, it is only available on PostgreSQL 17 and 18. To address this, VectorChord provides a simulated asynchronous I/O interface called `prefetch_buffer`, which is available on all PostgreSQL versions as a fallback for older versions. `prefetch_buffer` is less effective than `read_stream`.

| Prefetch Mode     | Description                                                                                      | Supported PostgreSQL Versions     |
| ----------------- | ------------------------------------------------------------------------------------------------ | --------------------------------- |
| `read_stream`     | Asynchronous I/O interface in PostgreSQL                                                         | PostgreSQL 17, 18                 |
| `prefetch_buffer` | VectorChord's simulated asynchronous I/O interface used as fallback on older PostgreSQL versions | PostgreSQL 13, 14, 15, 16, 17, 18 |
| `read_buffer`     | Synchronous I/O interface in PostgreSQL                                                          | PostgreSQL 13, 14, 15, 16, 17, 18 |
{.wide .expand}

To fully leverage this feature with `read_stream`, you need to enable asynchronous I/O on PostgreSQL 18. See also [PostgreSQL Tuning](/docs/vchord/usage/postgresql-tuning/#asynchronous-i-o).

<a id="Reference"></a>
## Reference

<a id="search-parameters"></a>
### Search Parameters (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-io-search"></a>
#### `vchordrq.io_search`

{{< badge text="since v0.4.0" tone="info" >}}

- Description: This GUC parameter controls the I/O prefetching strategy for reading bit vectors in vector search, which can impact search performance on disk-based vectors.
- Type: string
- Domain: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18: `{"read_buffer", "prefetch_buffer", "read_stream"}`
- Default: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `prefetch_buffer`
    - PostgreSQL 17, 18: `read_stream`
- Note:
    - `read_buffer` indicates a preference for `ReadBuffer`.
    - `prefetch_buffer` indicates a preference for both `PrefetchBuffer` and `ReadBuffer`.
    - `read_stream` indicates a preference for `read_stream`.

<a id="vchordrq-io-rerank"></a>
#### `vchordrq.io_rerank`

{{< badge text="since v0.4.0" tone="info" >}}

- Description: This GUC parameter controls the I/O prefetching strategy for reading full precision vectors in vector search, which can significantly impact search performance on disk-based vectors.
- Type: string
- Domain: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18: `{"read_buffer", "prefetch_buffer", "read_stream"}`
- Default: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `prefetch_buffer`
    - PostgreSQL 17, 18: `read_stream`
- Note:
    - `read_buffer` indicates a preference for `ReadBuffer`.
    - `prefetch_buffer` indicates a preference for both `PrefetchBuffer` and `ReadBuffer`.
    - `read_stream` indicates a preference for `read_stream`. In 1.2.0, `read_stream` reranking keeps buffer guards aligned with candidate tuples when items stop early during concurrent `VACUUM`, preventing candidate rows from being dropped or mismatched.

<a id="search-parameters"></a>
### Search Parameters (`vchordg`)

{{< badge text="vchordg" tone="neutral" >}}

<a id="vchordg-io-search"></a>
#### `vchordg.io_search`

{{< badge text="since v0.5.0" tone="info" >}}

- Description: This GUC parameter controls the I/O prefetching strategy for reading bit vectors in vector search, which can impact search performance on disk-based vectors.
- Type: string
- Domain: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18: `{"read_buffer", "prefetch_buffer", "read_stream"}`
- Default: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `prefetch_buffer`
    - PostgreSQL 17, 18: `read_stream`
- Note:
    - `read_buffer` indicates a preference for `ReadBuffer`.
    - `prefetch_buffer` indicates a preference for both `PrefetchBuffer` and `ReadBuffer`.
    - `read_stream` indicates a preference for `read_stream`.

<a id="vchordg-io-rerank"></a>
#### `vchordg.io_rerank`

{{< badge text="since v0.5.0" tone="info" >}}

- Description: This GUC parameter controls the I/O prefetching strategy for reading full precision vectors in vector search, which can significantly impact search performance on disk-based vectors.
- Type: string
- Domain: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18: `{"read_buffer", "prefetch_buffer", "read_stream"}`
- Default: Depends on PostgreSQL version
    - PostgreSQL 13, 14, 15, 16: `prefetch_buffer`
    - PostgreSQL 17, 18: `read_stream`
- Note:
    - `read_buffer` indicates a preference for `ReadBuffer`.
    - `prefetch_buffer` indicates a preference for both `PrefetchBuffer` and `ReadBuffer`.
    - `read_stream` indicates a preference for `read_stream`.
