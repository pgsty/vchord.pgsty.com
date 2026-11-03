---
title: "概览"
linkTitle: "概览"
description: "pgvecto.rs 简介。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/getting-started/overview.md"
math: true
aliases:
  - "/getting-started/overview/"
icon: fa-solid fa-compass
---

> [!WARNING]
> 我们强烈建议您探索全新的 [VectorChord](https://github.com/pgsty/vchord) 实现，它提供了更高的稳定性和性能。建议用户迁移至 VectorChord，详情请参考[迁移指南](/zh/docs/vchord/admin/migration/)。


`pgvecto.rs` 简介。

<a id="what-is-pgvecto-rs"></a>
## 什么是 `pgvecto.rs` {#what-is-pgvectors}

`pgvecto.rs` 是一个提供向量相似度搜索功能的 Postgres 扩展。它使用 Rust 编写，基于 [pgrx](https://github.com/tcdi/pgrx) 构建。目前处于测试（Beta）阶段，诚邀您在生产环境中试用并向我们提供反馈。更多信息请参阅[📝我们的发布博客](/zh/blog/release/pgvectors-02-unifying-relational-queries-and-vector-search-in-postgresql/)。

## 与 pgvector 的对比 {#comparison-with-pgvector}

查看 [pgvecto.rs vs pgvector](/zh/docs/vectors/faqs/comparison-pgvector/) 了解更多详情。

| 特性 | pgvecto.rs | pgvector |
| --- | --- | --- |
| 过滤（Filtering） | 引入 VBASE 方法，将向量搜索与关系查询统一（例如：单向量 TopK + 过滤 + 连接）。 | 应用过滤条件时，返回结果可能不完整。例如，原本希望限制返回 10 条结果，加上过滤后可能最终只得到 5 条结果。 |
| 向量维度 | 最高支持 65535 维。 | 最高支持 2000 维。 |
| SIMD | 在运行时动态分派 SIMD 指令，根据具体机器的硬件能力最大化性能。 | 在 0.7.0 版本中为 Linux x86-64 增加了距离函数的 CPU 动态分派。 |
| 数据类型 | 引入额外的数据类型：二值向量（binary vector）、FP16（16 位浮点数）和 INT8（8 位整数）。 | \- |
| 索引机制 | 独立于 PostgreSQL 管理索引的存储和内存 | 依赖 PostgreSQL 的原生存储引擎 |
| WAL 支持 | 为数据提供预写式日志（WAL）支持，索引的 WAL 支持正在开发中。 | 为索引和数据均提供预写式日志（WAL）支持。 |
{.wide .expand}

## 快速开始 {#quick-start}

对于新用户，我们建议使用 [Docker 镜像](https://hub.docker.com/r/tensorchord/pgvecto-rs)快速上手。

```sh
docker run \
  --name pgvecto-rs-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/pgvecto-rs:pg16-v0.2.0
```

随后您可以使用 `psql` 命令行工具连接到数据库。默认用户名为 `postgres`，默认密码为 `mysecretpassword`。

```sh
psql postgresql://postgres:mysecretpassword@localhost:5432/postgres
```

运行以下 SQL 确保扩展已启用：

```sql
DROP EXTENSION IF EXISTS vectors;
CREATE EXTENSION vectors;
```

`pgvecto.rs` 引入了新的数据类型 `vector(n)` 来表示 n 维向量，括号内的 `n` 代表向量的维度。

您可以使用以下 SQL 创建一张表：

```sql
-- 创建包含向量列的表

CREATE TABLE items (
  id bigserial PRIMARY KEY,
  embedding vector(3) NOT NULL -- 3 维
);
```

> [!DETAILS]
>
> 仅当 \(1 \leq n \leq 65535\) 时，`vector(n)` 才是有效的数据类型。受限于 PostgreSQL 的机制，您有可能在 `vector(3)` 类型的列中存入 \(5\) 维的值，而且不带维度的 `vector` 也是合法的数据类型。但您仍然不能向向量中放入 \(0\) 个标量或超过 \(65535\) 个标量。如果您在列定义中使用不带维度的 `vector`，或者列中存在与声明维度不匹配的值，您将无法在该列上创建索引。
>


接下来，您可以按如下方式向表中插入向量数据：

```sql
-- 插入值

INSERT INTO items (embedding)
VALUES ('[1,2,3]'), ('[4,5,6]');

-- 或者将数组类型转换为向量后插入

INSERT INTO items (embedding)
VALUES (ARRAY[1, 2, 3]::real[]), (ARRAY[4, 5, 6]::real[]);
```

我们支持三种用于计算两个向量之间距离的操作符：

- `<->`：平方欧氏距离（Squared Euclidean distance），定义为 \(\Sigma (x_i - y_i) ^ 2\)。
- `<#>`：负点积（Negative dot product），定义为 \(- \Sigma x_iy_i\)。
- `<=>`：余弦距离（Cosine distance），定义为 \(1 - \frac{\Sigma x_iy_i}{\sqrt{\Sigma x_i^2 \Sigma y_i^2}}\)。

```sql
-- 通过操作符调用距离函数

-- 平方欧氏距离
SELECT '[1, 2, 3]'::vector <-> '[3, 2, 1]'::vector;
-- 负点积
SELECT '[1, 2, 3]'::vector <#> '[3, 2, 1]'::vector;
-- 余弦距离
SELECT '[1, 2, 3]'::vector <=> '[3, 2, 1]'::vector;
```

您可以像这样简单地搜索相似向量：

```sql
-- 查询相似的嵌入向量
SELECT * FROM items ORDER BY embedding <-> '[3,2,1]' LIMIT 5;
```

### 简单的问答（Question-Answering）应用 {#a-simple-question-answering-application}

请查看[问答应用](/zh/docs/vectors/use-case/question-answering/)教程。

### 半精度浮点数 {#half-precision-floating-point}

`vecf16` 类型除了标量元素类型外，其余与 `vector` 完全一致。它存储 16 位浮点数。如果您希望减少内存占用以获得更好的性能，可以尝试将 `vector` 类型替换为 `vecf16` 类型。

关于 `vecf16` 的更多用法，请参考[向量类型](/zh/docs/vectors/reference/vector-types/vecf16/)。

### 稀疏向量 {#sparse-vector}

`svector` 类型是稀疏向量类型。它以稀疏格式存储向量，非常适合包含大量零元素的向量。

关于 `svector` 的更多用法，请参考[向量类型](/zh/docs/vectors/reference/vector-types/svector/)。

### 二值向量 {#binary-vector}

`bvector` 类型是二值向量类型，本质上是定长位串（bit string）。除了上述 3 种距离外，我们还支持 `jaccard` 距离 `<~>`，其定义为 \(1 - \frac{|X\cap Y|}{|X\cup Y|}\)。而汉明距离（`hamming` distance）与平方欧氏距离等价，您可以使用 `<->` 操作符来计算。此外，我们还提供了 `binarize` 函数，用于从 `vector` 构造 `bvector`（将正数元素设为 1，其余设为 0）。

关于 `bvector` 的更多用法，请参考[向量类型](/zh/docs/vectors/reference/vector-types/bvector/)。

## 路线图 🗂️ {#roadmap}

请查看[路线图（ROADMAP）](/zh/docs/vectors/community/roadmap/)。

## 参与贡献 😊 {#contribute}

我们欢迎来自开源社区、个人及合作伙伴的各种形式的贡献。

- 加入我们的 [Discord 社区](https://discord.gg/KqswhpVgdU)！
- 如需从源码构建，请阅读我们的[贡献指南](/zh/docs/vectors/community/contributing/)和[开发教程](/zh/docs/vectors/developers/development/)。

### 与我们交流 {#talk-with-us}

💬 有兴趣与我们聊聊您在构建或管理 AI/ML 应用方面的经验吗？

[**预约交流时间！**](https://calendly.com/cegao/tensorchord-interview)
