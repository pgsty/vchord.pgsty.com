---
title: "VectorChord 1.1：原生 4/8 比特向量类型与每索引查询默认值"
date: 2026-02-14
description: "VectorChord 1.1 引入 RaBitQ8 与 RaBitQ4，带来高效存储并改善多索引查询体验"
author: "Junyu Chen"
tags:
  - "release"
  - "vector-database"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-11-native-48-bit-vector-types-and-per-index-query-defaults"
aliases:
  - "/blog/vectorchord-11-native-48-bit-vector-types-and-per-index-query-defaults/"
  - "/vectorchord-11-native-48-bit-vector-types-and-per-index-query-defaults/"
---

值此马年新春开启之际，我们非常高兴地宣布发布 VectorChord 1.1。

[VectorChord 1.0](/zh/blog/release/vectorchord-10-developer-first-vector-search-on-postgres-100x-faster-indexing-than-pgvector/) 是 Postgres 原生向量搜索的一个重要里程碑：它让大规模索引构建变得足够快，感觉就像日常迭代而非停机维护。在 1.1 版本中，我们在此基础上更进一步，推出了 RaBitQ8：这是一种全新的向量类型，相比 float32 可节省 4 倍存储空间并提供更快的搜索速度，同时召回率损失不到 1%。配合 RaBitQ4 以及更具可组合性的查询控制能力，VectorChord 1.1 已准备好应对你最严苛的生产工作负载。

本次发布重点解决我们在社区反馈中观察到的两大痛点：

* **容量瓶颈**。当向量索引规模变得极其庞大时，扩展性不仅关乎吞吐量，还直接受限于 SSD 存储占用和缓冲区缓存（Buffer Cache）压力。
    
* **运维开销**。随着索引数量的增长，为每条查询手动设置搜索参数（如 `nprobe`）会让应用逻辑变得繁琐杂乱。在分区表等场景下，这个问题尤为棘手，因为不同的索引往往需要各自独立的配置。依赖全局会话变量（GUC）使得独立调优这些索引变得不可能。
    

VectorChord 1.1 同时解决了这两个问题。我们引入了 `rabitq8` 和 `rabitq4` 原生量化向量类型，其体积分别仅为标准 float32 的 1/4 和 1/8。这些类型可将总索引大小缩减至原来的 1/4 到 1/7，大幅降低存储开销。同时，我们还新增了每索引查询默认值（Per-Index Query Defaults），让跨多索引查询能够依赖各自独立的配置，而不再受制于脆弱的全局 PostgreSQL GUC。

## RaBitQ8 与 RaBitQ4：提升存储效率的低比特向量类型 {#rabitq8--rabitq4-low-bit-vector-type-for-storage-efficiency}

向量数据占用空间是在 Postgres 上进行大规模搜索的隐形瓶颈。将高维向量存储为标准 float32（每维度 4 字节）会消耗海量的 SSD 空间和内存。随着存储占用的增长，它会加剧**缓冲区缓存压力**，迫使查询频繁从磁盘读取数据，进而导致 P99 延迟飙升。

VectorChord 1.1 通过引入基于扩展 RaBitQ（[论文](https://arxiv.org/abs/2409.09913)）构建的两种全新量化数据类型 `rabitq8` 和 `rabitq4` 解决了这一问题。通过使用 8 比特和 4 比特表示替代 32 比特浮点数，这两种类型将单向量存储空间分别缩减至 1/4 和 1/8，同时将精度损失控制在极低水平。

使用这些类型的方式与使用 `vector` 几乎完全相同。唯一的区别是在执行 `INSERT` 和 `SELECT` 时，使用 `quantize_to_rabitq8` 或 `quantize_to_rabitq4` 对值进行量化。

```pgsql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding rabitq8(3));
CREATE INDEX ON items USING vchordrq (embedding rabitq8_l2_ops);
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[0,0,0]'));
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[1,1,1]'));
INSERT INTO items (embedding) VALUES (quantize_to_rabitq8('[2,2,2]'));
--- ...
SELECT id FROM items ORDER BY embedding <-> quantize_to_rabitq8('[1,2,3]') LIMIT 100;
```

在包含 1 亿个 768 维向量的 LAION 数据集上，典型的 `vector`（float32）索引约占 **400GB**。使用 `halfvec`（float16）类型可将其缩减至约 **171GB**。在相同的索引选项下，切换为 `rabitq8` 可进一步将其缩减至约 **95GB**，而 `rabitq4` 则可缩减至约 **58GB**，相比基线实现了 **4 到 7 倍**的存储空间缩减。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1770862442344/781ef6d4-aa1e-4281-b306-7de000051672.png)

接下来的问题是召回率与吞吐量的权衡。`rabitq8` 在大幅缩减索引体积的同时，保持了与基线（`float32` 向量）基本持平的召回率和 QPS。`rabitq4` 则是一个更为激进的选项：它以较大的召回率损失换取了极致的最小索引体积，最适合将存储空间作为首要限制因素的部署场景。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1771052144440/61043c76-0e82-441a-bd3e-c0eeea17747c.png)

## 每索引查询默认值：可组合的多索引查询 {#per-index-query-defaults-composable-multi-index-queries}

在 VectorChord 中，`vchordrq.probes` GUC 控制查询时搜索多少向量空间，直接决定了吞吐量与召回率之间的权衡。对于层次化的 `vchordrq` 索引，`vchordrq.probes` 的层级长度必须与构建时使用的 `build.internal.lists` 配置保持一致。典型配置如下表所示：

|  | `build.internal.lists` | `vchordrq.probes` |
| --- | --- | --- |
| 无分区 | `[]` | `''` |
| 1 层分区 | `[2000]` | `'40'` |
| 2 层分区 | `[800, 640000]` | `'40,200'` |

对于单表、单索引上的简单向量搜索，在运行查询前设置一次 GUC 是一个很自然的选择：

```pgsql
SET vchordrq.probes = '40';
```

然而，当一条查询涉及多个向量索引时，情况就不同了。使用不同 `build.internal.lists` 配置构建的索引，在逻辑上应当使用不同的 `probes` 设置。更糟糕的是，当列表层级数量不同时，没有任何一个单一的全局 `probes` 值能够同时匹配两个索引，导致全局设置天然无法支持此类查询。

```pgsql
CREATE INDEX idx_1 ON table_1 USING vchordrq (emb vector_cosine_ops);

CREATE INDEX idx_2 ON table_2 USING vchordrq (emb vector_cosine_ops) WITH (options = $$
[build.internal]
lists = [2000]
$$);

-- Bad: matches idx_2 configuration but not idx_1
SET vchordrq.probes = '40';
-- Bad: matches idx_1 configuration but not idx_2
SET vchordrq.probes = '';

-- Error: single global probes cannot satisfy both index configurations
SELECT 'table_1' AS src, id FROM table_1 ORDER BY emb <=> '[1,2,3]' LIMIT 5 
UNION ALL
SELECT 'table_2' AS src, id FROM table_2 ORDER BY emb <=> '[4,5,6]' LIMIT 5;
```

为了解决这一问题，VectorChord 1.1 遵循 PostgreSQL 的索引级配置模型，将每索引查询默认值（Per-Index Query Defaults）作为索引选项引入。现在，不必再强迫每条查询共享单一的全局配置，每个索引都可以定义自己的默认值，当未显式设置全局配置时，这些默认值就会自动生效。

你可以在创建索引时设置每索引默认值，也可以随时在线修改它们，而无需重建索引。

```pgsql
CREATE INDEX idx_1 ON table_1 USING vchordrq (emb vector_cosine_ops) WITH (options = $$
[build.internal]
lists = []
$$, probes = '');

CREATE INDEX idx_2 ON table_2 USING vchordrq (emb vector_cosine_ops) WITH (options = $$
[build.internal]
lists = [2000]
$$, probes = '20');

-- Modify per-index probes default online
ALTER INDEX idx_2 SET (probes = '40');

-- Success: the statement runs correctly with per-index defaults
SELECT 'table_1' AS src, id FROM table_1 ORDER BY emb <=> '[1,2,3]' LIMIT 5 
UNION ALL
SELECT 'table_2' AS src, id FROM table_2 ORDER BY emb <=> '[4,5,6]' LIMIT 5;
```

除了 `vchordrq.probes` 之外，其他查询期参数也可以在创建索引时指定每索引默认值，从而让多索引查询能够依赖各自独立的、特定于索引的设置。有关可配置参数的完整列表，请参阅[回退参数（Fallback Parameters）](/zh/docs/usage/fallback-parameters/)。

<a id="Summary"></a>
## 总结 {#summary}

VectorChord 1.1 让大规模部署的运维变得更加轻松。`rabitq8` 和 `rabitq4` 大幅缩减了存储体积，在保持熟悉的 SQL 使用模式的同时，显著降低了存储与内存压力。每索引回退查询默认值则使得在单条语句中执行跨多索引的向量查询成为可能，尤其是当这些索引采用不同选项构建时。

无论你是在真实工作负载中遇到了存储与内存瓶颈，还是正在运行涉及多个向量索引的复杂查询，我们都诚挚邀请你升级到 VectorChord 1.1，在你的业务负载中亲自体验并分享反馈。

* **在 GitHub 上下载 / Star：** [https://github.com/tensorchord/VectorChord](https://github.com/tensorchord/VectorChord)
    
* **加入社区：** [https://discord.gg/KqswhpVgdU](https://discord.gg/KqswhpVgdU)
