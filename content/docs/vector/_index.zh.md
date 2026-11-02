---
title: "pgvector 文档"
linkTitle: "pgvector"
description: "PostgreSQL 开源向量相似性检索基础扩展：涵盖 vector、halfvec、bit 与 sparsevec 数据类型，精确与近似最近邻搜索，以及 HNSW 与 IVFFlat 索引。"
weight: 400
icon: fa-solid fa-circle-nodes
type: docs
sidebar_root_for: self
upstream_source: pgvector
upstream_link: https://github.com/pgvector/pgvector
upstream_modified: true
aliases:
  - "/zh/vector/"
no_list: true
cascade:
  type: docs
  upstream_source: pgvector
  upstream_modified: true
---

**`pgvector`** 是 PostgreSQL 生态中最基础的开源向量相似性检索扩展。它提供了核心的 `vector`、`halfvec`、`bit` 与 `sparsevec` 向量数据类型、距离操作符，以及内置的 **HNSW** 和 **IVFFlat** 索引访问方法。

> [!TIP] 与 `vchord` 的关系
> [`vchord`](/zh/docs/vchord/) 直接构建在 `pgvector` 的数据类型（`vector` 与 `halfvec`）和距离操作符（`<->`、`<#>`、`<=>`）之上。无需修改现有的表结构或应用层 SQL，即可直接在现有的 `pgvector` 向量列上创建 [`vchord`](/zh/docs/vchord/)（`vchordrq` 或 `vchordg`）索引。

## 核心特性

- **精确与近似最近邻检索（KNN / ANN）**：与 PostgreSQL 完整 ACID 事务、时间点恢复（PITR）、关系连接（JOIN）及谓词过滤无缝融合。
- **多种向量数据表示**：
  - 单精度浮点向量（`vector`，索引最高支持 2,000 维，无索引存储最高支持 16,000 维）
  - 半精度浮点向量（`halfvec`，索引最高支持 4,000 维）
  - 二值位向量（`bit`，索引最高支持 64,000 维）
  - 稀疏向量（`sparsevec`，最高支持 1,000 个非零元素、总维度高达 100 万维）
- **六种距离度量**：欧氏 L2 距离（`<->`）、内积（`<#>`）、余弦距离（`<=>`）、曼哈顿 L1 距离（`<+>`）、汉明距离（`<~>`）以及杰卡德距离（`<%>`）。
- **迭代式索引扫描（Iterative Index Scans，0.8.0+）**：当带 `WHERE` 过滤条件导致候选集不足时，自动扩展 HNSW 或 IVFFlat 索引遍历范围以保证召回数量。

## 文档章节导航

{{< cards >}}
{{< card title="安装与快速上手" icon="fa-solid fa-rocket" link="/zh/docs/vector/getting-started/" >}}
通过 Pigsty、Docker、Linux 软件源、Homebrew 或源码编译安装 `pgvector`，启用扩展并执行向量写入与批量导入。
{{< /card >}}
{{< card title="查询与过滤检索" icon="fa-solid fa-magnifying-glass" link="/zh/docs/vector/querying/" >}}
距离操作符、相似度计算、向量聚合函数、带 `WHERE` 条件的迭代索引扫描以及全文/BM25 混合检索。
{{< /card >}}
{{< card title="HNSW 与 IVFFlat 索引" icon="fa-solid fa-sitemap" link="/zh/docs/vector/indexing/" >}}
HNSW 与 IVFFlat 索引构建与参数调优、并行建索引、进度监控，以及使用 [`vchord`](/zh/docs/vchord/) 突破内存瓶颈。
{{< /card >}}
{{< card title="向量量化与稀疏向量" icon="fa-solid fa-compress" link="/zh/docs/vector/quantization/" >}}
半精度（`halfvec`）、二值量化（`bit` + 精确重排）、稀疏向量（`sparsevec`）以及套娃（Matryoshka）子向量索引。
{{< /card >}}
{{< card title="参考手册、调优与 FAQ" icon="fa-solid fa-book-open" link="/zh/docs/vector/reference/" >}}
完整 SQL 函数与操作符速查表、GUC 参数、内存规划、执行计划排查与常见问题解答。
{{< /card >}}
{{< card title="使用 vchord 扩展亿级规模" icon="fa-solid fa-layer-group" link="/zh/docs/vchord/" >}}
在现有的 `pgvector` 向量列上无缝添加 `vchordrq` 与 `vchordg` RaBitQ 索引，无需修改业务查询即可扩展至亿级规模。
{{< /card >}}
{{< /cards >}}
