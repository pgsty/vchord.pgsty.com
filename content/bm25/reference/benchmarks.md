---
title: "Benchmarks"
description: "QPS throughput and NDCG@10 retrieval accuracy benchmarks for VectorChord-BM25 against Elasticsearch, Lucene, ParadeDB, and PostgreSQL GIN."
weight: 30
---

## Throughput Benchmark (QPS vs. Elasticsearch, Lucene, ParadeDB, PG GIN)

VectorChord-BM25's **Block-WeakAnd** implementation with 128-document delta-bitpacked blocks and 1-byte fieldnorm quantization delivers up to **3x higher QPS** than Tantivy-based PostgreSQL extensions (`ParadeDB / pg_search`) and an order of magnitude higher QPS than native PostgreSQL `GIN` indexes on Top-10 ranked queries:

![VectorChord-BM25 RPS Benchmark](/docs/images/es-vchord-bm25-rps.png)

![VectorChord-BM25 NDCG@10 Benchmark](/docs/images/es-vchord-bm25-ndcg10.png)

### Why `vchord_bm25` Achieves High QPS

1. **Zero Cross-Engine Serialization**: Unlike foreign-data-wrapper or external Tantivy/Lucene bridges, `vchord_bm25` stores its segments directly inside PostgreSQL buffer pages (`PostgresRelation`), avoiding tuple marshaling overhead.
2. **Aggressive Block-Max Pruning**: On multi-term queries, Block-WeakAnd skips over 80%–95% of 128-document posting blocks without decompressing them once the Top-10 threshold stabilizes.
3. **256-Entry Precomputed BM25 Lookup Table**: Quantizing document length into a 1-byte `fieldnorm` replaces expensive per-document floating-point math with a single array lookup.

---

## Retrieval Accuracy Benchmark (`NDCG@10` on BEIR & LoTTE)

The table below (from our [BEIR / LoTTE Hybrid Search & ColBERT Reranking evaluation](/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)) compares retrieval accuracy (`NDCG@10`) across:

- **PostgreSQL `vchord` Dense Vector Search** (`Vector`)
- **PostgreSQL `vchord_bm25` Lexical Search** (`BM25`)
- **Hybrid Search (`vchord` + `vchord_bm25` with ColBERT Rerank)**

| Dataset | Domain | Vector (`vchord`) | BM25 (`vchord_bm25`) | Hybrid + ColBERT Rerank |
| :--- | :--- | :---: | :---: | :---: |
| **scifact** | Scientific Fact-Checking | 0.676 | 0.665 | **0.751** |
| **nfcorpus** | Bio-Medical IR | 0.340 | 0.325 | **0.370** |
| **fiqa** | Financial QA | 0.405 | 0.236 | **0.415** |
| **trec-covid** | Biomedical COVID-19 | 0.728 | 0.656 | **0.838** |
| **LoTTE-lifestyle (search)** | Lifestyle QA | 0.735 | 0.635 | **0.779** |
| **LoTTE-lifestyle (forum)** | Lifestyle Forum | 0.662 | 0.506 | **0.701** |
| **LoTTE-recreation (search)** | Recreation QA | 0.642 | 0.564 | **0.708** |
| **LoTTE-technology (search)** | Technology QA | 0.562 | 0.483 | **0.647** |
| **LoTTE-writing (search)** | Writing QA | 0.726 | 0.674 | **0.793** |

> [!TIP]
> Combining **`vchord_bm25`** with **`vchord`** consistently outperforms either dense vector search or lexical BM25 alone across every evaluated dataset. See [Hybrid Search (BM25 + VectorChord)](/bm25/usage/hybrid-search/) for SQL query templates.
