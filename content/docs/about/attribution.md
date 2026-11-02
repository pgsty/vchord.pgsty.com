---
title: Attribution & Provenance
linkTitle: Attribution
description: Upstream sources, copyright notices, and modification records for vchord.pgsty.com.
weight: 20
icon: fa-solid fa-scroll
aliases:
  - "/about/attribution/"
---

`vchord.pgsty.com` is maintained by [PGSTY](https://pigsty.io/) to provide a comprehensive, searchable documentation and engineering reference for the **Vchord** extension suite (**`vchord`**, **`vchord_bm25`**, and **`pg_tokenizer`**).

## Upstream Sources

1. **Documentation (`content/docs/`, `content/docs/vectors/`, `content/cloud/`)**
   - **Source Repository**: [`https://github.com/tensorchord/pgvecto.rs-docs`](https://github.com/tensorchord/pgvecto.rs-docs)
   - **Original Site**: [`https://docs.vectorchord.ai/`](https://docs.vectorchord.ai/)
   - **Copyright**: © 2023–Present TensorChord Inc. and Contributors.
   - **Adaptations**: Converted from VitePress to Hugo + [OINK `v1.4.0`](https://github.com/pgsty/oink), including GitHub-style callout normalization, KaTeX math delimiter standardization, internal link resolution, and structural navigation metadata.

2. **Engineering Blog & Release Notes (`content/blog/`)**
   - **Original Publication**: [`https://blog.vectorchord.ai/`](https://blog.vectorchord.ai/)
   - **Copyright**: © 2023–Present TensorChord Inc. and respective article authors (`Keming`, `Haze`, `VoVAllen`, `Yifanwang`, `Kolkri`, `Gin`, `Scase`).
   - **Adaptations**: Archived into `content/blog/post/` and `content/blog/release/` with original publication dates, author metadata, and direct `upstream_link` provenance pointers.

3. **Vchord Extension Suite (`vchord`, `vchord_bm25`, and `pg_tokenizer`)**
   - **`vchord` ([`pgsty/vchord`](https://github.com/pgsty/vchord)) Forked From**: [`https://github.com/supervc-stack/VectorChord`](https://github.com/supervc-stack/VectorChord) (formerly [`tensorchord/VectorChord`](https://github.com/tensorchord/VectorChord))
   - **`vchord_bm25` ([`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)) Forked From**: [`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25) (formerly [`tensorchord/VectorChord-bm25`](https://github.com/tensorchord/VectorChord-bm25))
   - **`pg_tokenizer` ([`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)) Forked From**: [`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs) (formerly [`tensorchord/pg_tokenizer.rs`](https://github.com/tensorchord/pg_tokenizer.rs))
   - **Predecessor Project**: [`https://github.com/tensorchord/pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs)

## Page-Level Provenance

Every documentation page and blog post derived from upstream material declares `upstream_link` in its front matter. OINK renders this provenance link in the page footer alongside modification indicators.
