---
title: "预取"
linkTitle: "预取"
description: "预取（Prefetch）能够大幅加速涉及 I/O 操作的查询。它根据索引的实际需求，主动将缓冲区预读到操作系统页缓存或 PostgreSQL 的缓冲池中。"
weight: 120
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prefetch.md"
aliases:
  - "/zh/docs/usage/prefetch/"
  - "/vectorchord/usage/prefetch/"
---

{{< badge text="since v0.4.0" tone="info" >}}


预取（Prefetch）能够大幅加速涉及 I/O 操作的查询。它的工作原理是根据索引的实际访问需求，主动将缓冲区预读到操作系统页缓存（page cache）或 PostgreSQL 的缓冲池（buffer pool）中。

预取有助于将 I/O 与计算重叠执行，以及将不同的 I/O 操作相互重叠执行，从而显著减少查询执行期间等待缓冲区的时间，进而提升整体查询性能。

> [!TIP]
> 该功能默认启用。在 VectorChord `0.4.0` 及更高版本中，任何查询都能从预取机制中受益。


在 `0.4.0` 版本之前，VectorChord 使用 PostgreSQL 的同步 I/O 接口。从 `0.4.0` 版本开始，VectorChord 在较新版本的 PostgreSQL 上使用异步 I/O 接口。VectorChord 所使用的 I/O 接口可以通过 GUC 参数进行控制。

在 GUC 参数中，同步 I/O 接口被称为 `read_buffer`，异步 I/O 接口被称为 `read_stream`，而 VectorChord 的模拟异步接口被称为 `prefetch_buffer`。

对于远小于内存大小的索引，这三种预取模式之间几乎没有差异。`read_stream` 可以加速所有基于磁盘的索引，但它仅在 PostgreSQL 17 和 18 上可用。为了解决这个问题，VectorChord 提供了一个名为 `prefetch_buffer` 的模拟异步 I/O 接口，在所有 PostgreSQL 版本上均可用，作为旧版本 PostgreSQL 的回退方案。`prefetch_buffer` 的效果略逊于 `read_stream`。

| 预取模式          | 说明                                                                   | 支持的 PostgreSQL 版本            |
| ----------------- | ---------------------------------------------------------------------- | --------------------------------- |
| `read_stream`     | PostgreSQL 中的异步 I/O 接口                                           | PostgreSQL 17, 18                 |
| `prefetch_buffer` | VectorChord 的模拟异步 I/O 接口，在旧版本 PostgreSQL 上作为回退方案使用 | PostgreSQL 13, 14, 15, 16, 17, 18 |
| `read_buffer`     | PostgreSQL 中的同步 I/O 接口                                           | PostgreSQL 13, 14, 15, 16, 17, 18 |

要在 PostgreSQL 18 上通过 `read_stream` 充分发挥此功能的威力，您需要启用异步 I/O。另请参阅 [PostgreSQL 调优](/zh/docs/vchord/usage/postgresql-tuning/#asynchronous-i-o)。

<a id="Reference"></a>
## 参考 {#reference}

<a id="search-parameters"></a>
### 搜索参数（`vchordrq`） {#search-parameters-vchordrq}

{{< badge text="vchordrq" tone="neutral" >}}

<a id="vchordrq-io-search"></a>
#### `vchordrq.io_search` {#vchordrq-io-search}

{{< badge text="since v0.4.0" tone="info" >}}

- 说明：该 GUC 参数控制在向量搜索中读取位向量（bit vector）时的 I/O 预取策略，会影响基于磁盘向量的搜索性能。
- 类型：字符串（string）
- 取值范围：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18：`{"read_buffer", "prefetch_buffer", "read_stream"}`
- 默认值：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`prefetch_buffer`
    - PostgreSQL 17, 18：`read_stream`
- 注意：
    - `read_buffer` 表示优先使用 `ReadBuffer`。
    - `prefetch_buffer` 表示优先结合使用 `PrefetchBuffer` 和 `ReadBuffer`。
    - `read_stream` 表示优先使用 `read_stream`。

<a id="vchordrq-io-rerank"></a>
#### `vchordrq.io_rerank` {#vchordrq-io-rerank}

{{< badge text="since v0.4.0" tone="info" >}}

- 说明：该 GUC 参数控制在向量搜索中读取全精度向量时的 I/O 预取策略，会显著影响基于磁盘向量的搜索性能。
- 类型：字符串（string）
- 取值范围：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18：`{"read_buffer", "prefetch_buffer", "read_stream"}`
- 默认值：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`prefetch_buffer`
    - PostgreSQL 17, 18：`read_stream`
- 注意：
    - `read_buffer` 表示优先使用 `ReadBuffer`。
    - `prefetch_buffer` 表示优先结合使用 `PrefetchBuffer` 和 `ReadBuffer`。
    - `read_stream` 表示优先使用 `read_stream`。

<a id="search-parameters"></a>
### 搜索参数（`vchordg`） {#search-parameters-vchordg}

{{< badge text="vchordg" tone="neutral" >}}

<a id="vchordg-io-search"></a>
#### `vchordg.io_search` {#vchordg-io-search}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：该 GUC 参数控制在向量搜索中读取位向量（bit vector）时的 I/O 预取策略，会影响基于磁盘向量的搜索性能。
- 类型：字符串（string）
- 取值范围：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18：`{"read_buffer", "prefetch_buffer", "read_stream"}`
- 默认值：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`prefetch_buffer`
    - PostgreSQL 17, 18：`read_stream`
- 注意：
    - `read_buffer` 表示优先使用 `ReadBuffer`。
    - `prefetch_buffer` 表示优先结合使用 `PrefetchBuffer` 和 `ReadBuffer`。
    - `read_stream` 表示优先使用 `read_stream`。

<a id="vchordg-io-rerank"></a>
#### `vchordg.io_rerank` {#vchordg-io-rerank}

{{< badge text="since v0.5.0" tone="info" >}}

- 说明：该 GUC 参数控制在向量搜索中读取全精度向量时的 I/O 预取策略，会显著影响基于磁盘向量的搜索性能。
- 类型：字符串（string）
- 取值范围：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`{"read_buffer", "prefetch_buffer"}`
    - PostgreSQL 17, 18：`{"read_buffer", "prefetch_buffer", "read_stream"}`
- 默认值：取决于 PostgreSQL 版本
    - PostgreSQL 13, 14, 15, 16：`prefetch_buffer`
    - PostgreSQL 17, 18：`read_stream`
- 注意：
    - `read_buffer` 表示优先使用 `ReadBuffer`。
    - `prefetch_buffer` 表示优先结合使用 `PrefetchBuffer` 和 `ReadBuffer`。
    - `read_stream` 表示优先使用 `read_stream`。
