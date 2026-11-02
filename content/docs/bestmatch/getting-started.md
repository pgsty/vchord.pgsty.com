---
title: "Getting Started"
linkTitle: "Getting Started"
description: "How pg_bestmatch converts BM25 scoring into sparse vector inner products, and how to install and enable the extension."
weight: 10
math: true
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#how-does-it-work
---

## How Does `pg_bestmatch` Work?

Given a document \(D\) and a query \(Q\) tokenized into vocabulary terms \(q_1, q_2, \dots, q_n\), the **Okapi BM25** relevance score is:

$$
\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
$$

Notice that this sum is the **inner product (dot product)** of two sparse vectors over the vocabulary space \(V\) (dimension \(|V| = 30{,}522\) for `bert-base-uncased`):

1. **Document Sparse Vector** \(\vec{v}_D\): For each unique token \(t \in D\), store the normalized term-frequency weight:
   $$
   v_D[t] = \frac{f(t, D) \cdot (k_1 + 1)}{f(t, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
   $$
2. **Query Sparse Vector** \(\vec{v}_Q\): For each token \(q_i \in Q\), store its inverse document frequency weight \(\text{IDF}(q_i)\).

When you compute the inner product \(\vec{v}_D \cdot \vec{v}_Q\) using [`pgvector`](/docs/vector/) or [`pgvecto.rs`](/docs/vectors/)'s `<#>` operator, PostgreSQL returns \(-\text{BM25}(D, Q)\) so that `ORDER BY embedding <#> query_vec ASC` returns the highest-scoring documents first!

---

## Installation

### Prerequisites

Install either [`pgvector`](/docs/vector/) (`v0.7.0+` for `sparsevec` support) or [`pgvecto.rs`](/docs/vectors/) (`v0.3.0+` for `svector` support) first.

### Install from Release Packages (Debian / Ubuntu)

Download the prebuilt `.deb` package matching your PostgreSQL major version from [GitHub Releases](https://github.com/tensorchord/pg_bestmatch.rs/releases):

```bash
# Example for PostgreSQL 16 on x86_64
wget https://github.com/tensorchord/pg_bestmatch.rs/releases/download/v0.0.1/pg-bestmatch-pg16_0.0.1_amd64.deb
sudo dpkg -i pg-bestmatch-pg16_0.0.1_amd64.deb
```

### Build from Source (`cargo pgrx`)

Ensure Rust and `cargo-pgrx` (`0.12.0-alpha.1` or compatible) are installed:

```bash
git clone https://github.com/tensorchord/pg_bestmatch.rs.git
cd pg_bestmatch.rs
cargo pgrx install --release
```

---

## Enable the Extension

Connect to PostgreSQL, create the extension, and add `bm25_catalog` to your `search_path`:

```sql
CREATE EXTENSION IF NOT EXISTS pg_bestmatch;
CREATE EXTENSION IF NOT EXISTS vector; -- or vectors for pgvecto.rs

SET search_path TO "$user", public, bm25_catalog;
```

Test tokenization with a single SQL query:

```sql
SELECT tokenize('PostgreSQL BM25 full-text search with pg_bestmatch');
--                 tokenize
-- -----------------------------------------
--  {postgresql,bm,##25,full,-,text,search,with,pg,_,best,##mat,##ch}
```

Continue to the [Usage Guide](/docs/bestmatch/usage/) for a complete end-to-end indexing and query workflow.
