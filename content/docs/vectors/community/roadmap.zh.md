---
title: "路线图"
linkTitle: "路线图"
description: "pgvecto.rs 的中期与长期发展规划，包括稀疏向量支持、流式工作负载优化、单机大容量向量存储及物理复制支持。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/community/roadmap.md"
aliases:
  - "/community/roadmap/"
---

> [!WARNING]
> 我们强烈建议你了解并选用我们全新的 [VectorChord](https://github.com/pgsty/vchord) 实现，它提供了更高的稳定性和性能。建议现有用户迁移至 VectorChord，具体步骤请参阅[迁移指南](/zh/docs/vchord/admin/migration/)。

## 中期规划 {#midterm-plan}

### 稀疏向量支持 {#sparse-vector-support}

稀疏向量在 RAG 和文本检索等任务中表现出了优异的性能，并且能够与稠密向量互补以提升检索效果。因此，我们计划支持稀疏向量索引。

### 更好地支持流式工作负载 {#better-support-for-streaming-workloads}

作为数据库，支持向量数据的灵活插入和删除至关重要。然而，当前主流的 HNSW 算法对删除操作的支持并不理想，通常需要重建索引。因此，我们计划参考 DiskANN 论文并支持 Vamana 算法。Vamana 算法是一种基于图的增量索引算法，无需重建索引即可良好地支持向量的动态删除与插入。

### 单机支持更大规模向量 {#more-vectors-on-a-single-machine}

在相同硬件资源下支持更多向量，对于帮助用户降低成本具有重要意义。目前我们已经支持用户以 `fp16` 格式存储向量，在几乎不损失精度的前提下仅需一半的内存和存储空间。我们还计划支持更多向量格式（如 `fp8` 和 `int8`），以进一步降低存储和内存消耗。同时，我们也在积极探索基于 SSD 的向量索引算法（如 DiskANN）。

### 物理复制与流复制支持 {#physical-and-streaming-replication}

`pgvecto.rs` 目前是一个独立于 PostgreSQL 的外部存储系统，自行管理索引内存和磁盘存储，因此无法开箱即用地支持物理复制。我们计划实现自定义的 WAL 资源管理器（Resource Manager），以满足物理复制的要求，使用户在 PG 中使用复制更加便捷。

## 长期规划 {#longterm-plan}

### 在 PostgreSQL 内支持十亿级（1B）向量 {#1b-vectors-inside-postgresql}

我们的终极目标是在 PostgreSQL 中支持 10 亿（1 Billion）规模的向量检索。要实现这一目标仍需克服诸多挑战，可能需要借助表访问方法（Table Access Method）实现自定义的向量存储方案，或者结合 Citus 等分布式分片扩展。目前我们在该领域的探索尚处于早期阶段，非常欢迎感兴趣的开发者与我们探讨交流。

## 与我们交流 {#talk-with-us}

想要参与进来？欢迎随时参与讨论和代码贡献！

- 在 [💬 Discord](https://discord.gg/KqswhpVgdU) 上与我们交流
- 查看带有 [`good first issue 💖`](https://github.com/tensorchord/pgvecto.rs/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue+%E2%9D%A4%EF%B8%8F%22) 标签的新手友好型 Issue！
- 更多详情请参阅[贡献指南](/zh/docs/vectors/community/contributing/)

以上规划项并非 MVP 的必需功能，而是我们长期路线图的一部分。如果你对其中任何方向感兴趣，欢迎随时加入！

更多规划将在未来持续补充。
