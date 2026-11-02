---
title: "性能与精度基准测试"
description: "VectorChord-BM25 与 Elasticsearch、Lucene、ParadeDB 及 PostgreSQL GIN 的 QPS 吞吐量与 NDCG@10 检索精度对比基准测试。"
weight: 30
---

## 吞吐量基准测试（QPS 对比 Elasticsearch、Lucene、ParadeDB、PG GIN） {#throughput-benchmark-qps-vs-elasticsearch-lucene-paradedb-pg-gin}

凭借结合 128 文档差分位打包块与单字节 Fieldnorm 量化的 **Block-WeakAnd** 算法实现，VectorChord-BM25 在 Top-10 排序查询上的 QPS 吞吐量最高可达基于 Tantivy 的 PostgreSQL 扩展（`ParadeDB / pg_search`）的 **3 倍**，并比 PostgreSQL 原生 `GIN` 索引高出一个数量级：

![VectorChord-BM25 RPS 基准测试](/docs/images/es-vchord-bm25-rps.png)

![VectorChord-BM25 NDCG@10 基准测试](/docs/images/es-vchord-bm25-ndcg10.png)

### 为什么 `vchord_bm25` 能实现极高的 QPS {#why-vchord_bm25-achieves-high-qps}

1. **零跨引擎序列化开销**：不同于外部数据包装器（FDW）或外挂 Tantivy/Lucene 桥接方案，`vchord_bm25` 将段数据直接存储在 PostgreSQL 缓冲池页面（`PostgresRelation`）中，彻底消除了跨引擎元组编组（Marshaling）开销。
2. **激进的块级上界剪枝（Block-Max Pruning）**：在多词查询场景下，一旦 Top-10 阈值趋于稳定，Block-WeakAnd 即可直接跳过 80%–95% 以上的 128 文档倒排块，无需对其进行解压。
3. **256 项预计算 BM25 查找表**：将文档长度量化为单字节 `fieldnorm`，使原本昂贵的逐文档浮点运算简化为单次数组查表。

---

## 检索精度基准测试（BEIR 与 LoTTE 上的 `NDCG@10`） {#retrieval-accuracy-benchmark-ndcg10-on-beir--lotte}

下表（摘自我们的 [BEIR / LoTTE 混合检索与 ColBERT 重排序评测报告](/zh/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)）对比了以下三种方案的检索精度（`NDCG@10`）：

- **PostgreSQL `vchord` 稠密向量检索**（`Vector`）
- **PostgreSQL `vchord_bm25` 词法检索**（`BM25`）
- **混合检索（`vchord` + `vchord_bm25` 配合 ColBERT 重排序）**

| 数据集 | 领域 | 稠密向量 (`vchord`) | 词法 BM25 (`vchord_bm25`) | 混合检索 + ColBERT 重排序 |
| :--- | :--- | :---: | :---: | :---: |
| **scifact** | 科学事实核查 | 0.676 | 0.665 | **0.751** |
| **nfcorpus** | 生物医学信息检索 | 0.340 | 0.325 | **0.370** |
| **fiqa** | 金融问答 | 0.405 | 0.236 | **0.415** |
| **trec-covid** | 生物医学 COVID-19 | 0.728 | 0.656 | **0.838** |
| **LoTTE-lifestyle (search)** | 生活方式问答（搜索） | 0.735 | 0.635 | **0.779** |
| **LoTTE-lifestyle (forum)** | 生活方式论坛 | 0.662 | 0.506 | **0.701** |
| **LoTTE-recreation (search)** | 休闲娱乐问答 | 0.642 | 0.564 | **0.708** |
| **LoTTE-technology (search)** | 技术问答 | 0.562 | 0.483 | **0.647** |
| **LoTTE-writing (search)** | 写作问答 | 0.726 | 0.674 | **0.793** |

> [!TIP]
> 在所有评测数据集上，将 **`vchord_bm25`** 与 **`vchord`** 结合使用均稳定超越单独使用稠密向量检索或单独使用词法 BM25 检索。如需获取开箱即用的 SQL 查询模板，请参阅[混合检索 (BM25 + VectorChord)](/zh/docs/bm25/usage/hybrid-search/)。
