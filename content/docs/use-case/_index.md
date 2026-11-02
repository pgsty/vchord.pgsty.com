---
title: "Use Cases"
linkTitle: "Use Cases"
description: "End-to-end recipes for hybrid BM25 + dense search, ColBERT reranking, and multimodal OCR-free RAG."
weight: 30
icon: fa-solid fa-diagram-project
upstream_link: ""
aliases:
  - "/vectorchord/use-case/"
---

| Title | Description | Link | Code |
|-------|-------------|------|------|
| Hybrid search with Postgres Native BM25 and VectorChord | This article explores how to implement Hybrid Search in Postgres using [VectorChord-bm25](https://github.com/pgsty/vchord_bm25) for keyword-based retrieval and [VectorChord](https://github.com/pgsty/vchord) for semantic search. | [Hybrid Search](/docs/use-case/hybrid-search/) | [Github Repo](https://github.com/xieydd/vectorchord-hybrid-search) |
| Supercharge vector search with ColBERT rerank in PostgreSQL | This blog will demonstrate using the PostgreSQL extension [VectorChord](https://github.com/pgsty/vchord) and pgvector with ColBERT rerank. | [ColBERT Rerank](/docs/use-case/colbert-rerank/) | [Github Repo](https://github.com/kemingy/vectorchord-colbert) |
| Beyond Text: Unlock OCR-Free RAG in PostgreSQL with Modal & VectorChord | This post is your guide to building exactly that: an **OCR-free RAG system** directly within your familiar PostgreSQL database. We'll leverage the power of the **ColQwen2** Vision Language Model, the efficiency of **VectorChord** for multi-vector search in Postgres, and the scalability of **Modal** for GPU-powered embedding generation. | [OCR-Free RAG](/docs/use-case/colqwen2-modal/) | [Github Repo](https://github.com/xieydd/vectorchord-colqwen2) |
