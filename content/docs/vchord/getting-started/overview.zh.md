---
title: "概览"
linkTitle: "概览"
description: "vchord 是什么、为 pgvector 用户解决什么问题、两种索引怎么选，以及五分钟上手。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/overview.md"
aliases:
  - "/docs/getting-started/overview/"
  - "/vectorchord/getting-started/overview/"
icon: fa-solid fa-compass
---

`vchord` 是一个 PostgreSQL 扩展，为 [pgvector](/zh/docs/vector/) 的向量列提供两种近似最近邻（ANN）索引。表结构、向量类型和查询语句都不用改：把 `hnsw` 或 `ivfflat` 换成 `vchordrq` 或 `vchordg` 索引，原来的 `ORDER BY embedding <-> $1 LIMIT 10` 就会走新索引。

## 为什么需要 vchord {#why}

pgvector 的 HNSW 索引在整张图都放得进内存时很快。但它的每个索引条目都存着一份完整向量，索引至少和向量本身一样大，而且在图上每走一步都是一次随机页读取。向量到了几千万条，索引就装不进内存了：构建要花上几个小时，查询延迟取决于磁盘。

vchord 的主力索引 `vchordrq` 就是为这个规模设计的：

- **内存占用小。** 向量按聚类中心分成若干列表（IVF），每个向量还会存成每维只占几个比特的 [RaBitQ](https://arxiv.org/abs/2405.12497) 编码。查询时只需要聚类中心常驻内存，需要的列表从磁盘顺序读取。
- **构建快。** 聚类只在样本上做，可以多线程并行，也可以[放到数据库外的 GPU 上](/zh/docs/vchord/usage/external-build/)。在一台 16 vCPU 的机器上，1 亿条 768 维向量 18 分钟建完索引，构建内存 6 GiB（[配置](/zh/docs/vchord/usage/partitioning-tuning/#laion-100m)）。
- **最终用精确距离。** 压缩编码只负责筛出候选，返回之前，vchord 会用与 SQL 相同的 `<->`、`<#>` 或 `<=>` 精确距离对候选重新排序。

在一台 4 vCPU、32 GB 内存的服务器上，1 亿条 768 维向量可以在 top-10 召回率 0.95 下提供查询服务（[基准测试](/zh/docs/vchord/benchmark/performance/#laion-100m-on-i4ixlarge)）。

## 选择索引 {#choose-an-index}

| | `vchordrq` | `vchordg` |
| --- | --- | --- |
| 结构 | RaBitQ 编码组成的 IVF 列表，精确重排 | 基于 RaBitQ 编码的图，精确重排 |
| 适合 | 表比内存大、需要快速构建、按租户或类别过滤 | 索引放得进内存，想要低延迟又不想选列表数 |
| 需要调的参数 | 构建时 `lists`；查询时 `probes` 和 `epsilon` | 构建时 `m`、`ef_construction`；查询时 `ef_search` |
| 独有功能 | [过滤键](/zh/docs/vchord/usage/filtering/#filter-keys)、[多向量 MaxSim](/zh/docs/vchord/usage/multi-vector-retrieval/)、[外部构建](/zh/docs/vchord/usage/external-build/) | |
| 最大维度 | 60,000 | 30,000 |
{.wide}

拿不准就先用 `vchordrq`：它支持全部功能，数据超出内存后也照样能用。两种索引都支持 pgvector 的 `vector`、`halfvec`，以及 vchord 自带的压缩类型 [`rabitq8` 和 `rabitq4`](/zh/docs/vchord/usage/quantization-types/)。

## 快速上手 {#quick-start}

vchord 1.5.0 支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19，依赖 pgvector。其他安装方式见[安装](/zh/docs/vchord/getting-started/installation/)。

1. 从 Pigsty 软件源安装：

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord
   ```

1. 预加载动态库并重启 PostgreSQL。跳过这一步，`CREATE EXTENSION` 会报错 `vchord must be loaded via shared_preload_libraries`。列表里已有的库要保留。

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord';
   ```

1. 在数据库中创建扩展。`CASCADE` 会一并创建 pgvector 的 `vector` 扩展。

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   ```

1. 建表、建索引、查询：

   ```sql
   CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));

   INSERT INTO items (embedding)
   SELECT ARRAY[random(), random(), random()]::real[]
   FROM generate_series(1, 1000);

   CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);

   SELECT id FROM items ORDER BY embedding <-> '[3, 1, 2]' LIMIT 5;
   ```
{.steps}

这个索引只有一个列表，适合小表。正式的表要按行数选 `lists`，见 [vchordrq 索引](/zh/docs/vchord/usage/indexing/#lists)。

## 接下来 {#next-steps}

- **给生产表建索引**：[vchordrq 索引](/zh/docs/vchord/usage/indexing/)，再用[召回率评估](/zh/docs/vchord/usage/measure-recall/)调参。
- **过滤结果**（按租户、类别或距离）：[过滤](/zh/docs/vchord/usage/filtering/)。
- **从 pgvector 或 pgvecto.rs 迁移**：[迁移](/zh/docs/vchord/admin/migration/)。
- **加上关键词检索**：[Vchord 套件](/zh/docs/vchord/getting-started/vectorchord-suite/)在同一个数据库里把 vchord 和 BM25 排序组合起来。

## 许可证 {#license}

vchord 以 [AGPL-3.0](https://github.com/pgsty/vchord/blob/main/LICENSE) 许可证发布，是 TensorChord VectorChord 的分支，由 [PGSTY](https://pgsty.com) 维护。商业授权或技术支持请联系 [rh@vonng.com](mailto:rh@vonng.com)。
