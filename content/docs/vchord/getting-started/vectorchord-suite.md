---
title: "Vchord Suite"
linkTitle: "Vchord Suite"
description: "Vector search, BM25 keyword ranking, and multilingual tokenization in one PostgreSQL database: what each extension does and how to install all three."
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/getting-started/vectorchord-suite.md"
aliases:
  - "/docs/getting-started/vectorchord-suite/"
  - "/vectorchord/getting-started/vectorchord-suite/"
icon: fa-solid fa-boxes-stacked
---

Search and retrieval-augmented generation need two kinds of matching. Embeddings find text that means the same thing in other words; keyword ranking finds the exact product code, error message, or name that an embedding blurs. Many systems run a vector database and a search engine next to PostgreSQL for this, and then spend their effort keeping three copies of the data in sync.

The Vchord suite does both inside PostgreSQL, so one transaction updates the rows, the vector index, and the keyword index together, and backups, replication, and access control cover all of them.

| Extension | What it adds | Release | Docs |
| --- | --- | --- | --- |
| [`vchord`](https://github.com/pgsty/vchord) | Vector indexes for pgvector columns | 1.5.0 | [vchord](/docs/vchord/) |
| [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) | BM25-ranked top-k search over `tsvector` columns | 1.3.0 | [vchord_bm25](/docs/bm25/) |
| [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) | Text analyzers and tokenizers that produce `tsvector` values, including for Chinese and Japanese | 1.3.0 | [pg_tokenizer](/docs/tokenizer/) |

Each works on its own. You need `pg_tokenizer` only when PostgreSQL's built-in `to_tsvector` does not split your language or vocabulary well.

## Install all three {#how-to-use-the-vchord-suite}

<a id="how-to-use-the-vectorchord-suite"></a>

All three support PostgreSQL 15–19 on Linux `x86_64` and `aarch64`, and all three must be preloaded.

1. Install the packages:

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord vchord_bm25 pg_tokenizer
   ```

1. Preload them, keeping any libraries already in the list, and restart PostgreSQL:

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord, vchord_bm25, pg_tokenizer';
   ```

1. Create the extensions in your database:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord CASCADE;
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
   ```
{.steps}

Release packages and source builds for each extension are described on its installation page. The `tensorchord/vchord-suite` container image contains older upstream releases with a different BM25 API.

## What to build with it {#use-cases-for-the-vchord-suite}

<a id="use-cases-for-the-vectorchord-suite"></a><a id="hybrid-search"></a><a id="ocr-free-visual-rag"></a><a id="references"></a>

- [Hybrid search](/docs/vchord/use-case/hybrid-search/) — Rank by embeddings and BM25 in one query and merge the two lists with reciprocal rank fusion.
- [ColBERT rerank](/docs/vchord/use-case/colbert-rerank/) — Retrieve with one embedding per passage, then rerank by token-level MaxSim.
- [Visual document retrieval](/docs/vchord/use-case/colqwen2-modal/) — Search PDF pages as images with ColQwen2, without OCR.
{.cards}
