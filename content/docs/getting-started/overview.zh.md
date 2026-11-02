---
title: "概览"
linkTitle: "概览"
description: "vchord 是一款专为可扩展、高性能及高磁盘效率的向量相似性检索而设计的 PostgreSQL 扩展。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/overview.md"
aliases:
  - "/vectorchord/getting-started/overview/"
---

`vchord` 是一款专为可扩展、高性能且磁盘高效的向量相似性检索而设计的 PostgreSQL 扩展。

借助 `vchord`，您仅需 1 美元即可存储 400,000 个向量，从而显著节省成本：在同等价格下，可存储的向量数量是 Pinecone 优化型存储的 6 倍，是 pgvector/pgvecto.rs 的 26 倍[^1]。欲了解更多详情，请参阅我们的[发布博文](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)。

<a id="Features"></a>
## 核心特性 {#features}

相较于 pgvecto.rs 和 pgvector，`vchord` 带来了显著的增强：

**⚡ 性能大幅提升**：与 pgvector 的 HNSW 实现相比，经过全面优化的操作可提供最高 5 倍的查询加速、16 倍的写入吞吐量提升，以及 16 倍的索引构建提速[^1]。

[^1]: 基于 [MyScale Benchmark](https://myscale.github.io/benchmark/) 测试（768 维向量，95% 召回率）。更多详情请参阅我们的[博文](/zh/blog/post/vectorchord-store-400k-vectors-for-1-in-postgresql/)。

**💰 高性价比向量检索**：仅需 32GB 内存即可查询 1 亿条 768 维向量，在保持 Top-10 召回率达 95% 的同时实现 35ms 的 P50 延迟，助您在保障高质量检索的同时大幅降低基础设施成本。

**🔌 无缝集成**：完全兼容 pgvector 的数据类型与语法，并提供开箱即用的最优默认配置——无需手动调优参数。只需直接引入 `vchord`，即可获得性能跃升。

**🔧 加速索引构建**：支持利用 IVF 在外部（例如 GPU 上）构建索引以加快 KMeans 聚类速度，并结合 RaBitQ[^2] 压缩算法高效存储向量，同时通过自适应重排序（reranking）确保检索质量。

[^2]: Gao, Jianyang, and Cheng Long. "RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search." Proceedings of the ACM on Management of Data 2.3 (2024): 1-27.

**📏 超长向量支持**：支持存储和检索最高达 60,000[^3] 维的向量，让您轻松使用 `text-embedding-3-large` 等顶尖高维模型。

[^3]: 目前 pgvector 存在 16,000 维的[限制](https://github.com/pgvector/pgvector#vector-type)。如果您确实需要处理更高维度的向量（`16,000<dim<60,000`），可以考虑修改 [VECTOR_MAX_DIM](https://github.com/pgvector/pgvector/blob/fef635c9e5512597621e5669dce845c744170822/src/vector.h#L4) 并自行编译 pgvector。

**🌐 按需灵活扩展**：基于水平扩展架构，针对 500 万或 1 亿条 768 维向量的查询可轻松扩展至 10,000+ QPS（Top-10 召回率达 90%），且具备极具竞争力的成本优势[^4]。

[^4]: 更多详情请参阅我们的[博文](/zh/blog/post/vector-search-at-10000-qps-in-postgresql-with-vectorchord/)，其中 PostgreSQL 的水平扩展能力由 [CloudNative-PG](https://github.com/cloudnative-pg/cloudnative-pg) 提供支持。

## 快速开始 {#quick-start}

对于新用户，我们推荐使用 Docker 镜像快速上手。如果您倾向于不使用 Docker，请参阅[安装指南](/zh/docs/getting-started/installation/)了解其他安装方式。

```bash
docker run \
  --name vectorchord-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/vchord-postgres:pg18-v1.1.1
```
> 除了包含 VectorChord 扩展的基础镜像外，我们还提供了全合一镜像 `tensorchord/vchord-suite:pg18-latest`。该综合镜像包含了所有官方 TensorChord 扩展。开发者应根据[支持矩阵](https://github.com/tensorchord/VectorChord-images?tab=readme-ov-file#support-matrix)选择与所需扩展版本兼容的镜像标签。

随后，您可以使用 `psql` 命令行工具连接到数据库。默认用户名为 `postgres`，默认密码为 `mysecretpassword`。

```bash
psql -h localhost -p 5432 -U postgres
```

现在，您可以开始体验 VectorChord 了！

VectorChord 依赖于 pgvector（包括其向量数据表示形式）。由于您可以直接使用它们，您的应用程序可以毫无痛点地轻松完成迁移！

```sql
CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
```

与 pgvector 类似，您可以创建一张包含向量列的表，并向其中插入一些数据。

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));
INSERT INTO items (embedding) SELECT ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 1000);
```

借助 VectorChord，您可以创建 `vchordrq` 索引：

```SQL
CREATE INDEX ON items USING vchordrq (embedding vector_l2_ops);
```

然后使用 `SELECT ... ORDER BY ... LIMIT ...` 执行向量检索：

```SQL
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

欲了解更多用法，请阅读：

- [构建索引](/zh/docs/usage/indexing/)
- [多向量检索](/zh/docs/usage/multi-vector-retrieval/)
- [图索引](/zh/docs/usage/graph-index/)
- [量化类型](/zh/docs/usage/quantization-types/)
- [相似度过滤](/zh/docs/usage/similarity-filter/)
- [PostgreSQL 调优](/zh/docs/usage/postgresql-tuning/)
- [监控](/zh/docs/usage/monitoring/)
- [回退参数](/zh/docs/usage/fallback-parameters/)
- [评估召回率](/zh/docs/usage/measure-recall/)
- [索引预热](/zh/docs/usage/prewarm/)
- [预过滤](/zh/docs/usage/prefilter/)
- [预取优化](/zh/docs/usage/prefetch/)
- [表内重排序](/zh/docs/usage/rerank-in-table/)
- [分区调优](/zh/docs/usage/partitioning-tuning/)
- [外部构建](/zh/docs/usage/external-build/)

<a id="License"></a>
## 开源许可 {#license}

`vchord` 采用 **GNU Affero 通用公共许可证 v3.0（[`AGPL-3.0-only`](https://github.com/pgsty/vchord/blob/main/LICENSE)）** 发布。我们欢迎任何商业合作或支持咨询，如有任何问题或需求，请发送邮件至 [rh@vonng.com](mailto:rh@vonng.com)。
