---
title: Attribution & Provenance
linkTitle: Attribution
description: Upstream sources, copyright notices, and modification records for vchord.pgsty.com.
weight: 20
icon: fa-solid fa-scroll
---

`vchord.pgsty.com` is maintained by the [Pigsty](https://pigsty.io/) community to provide a comprehensive, searchable, and archival documentation and engineering reference for **VectorChord (`pgsty/vchord`)** and **`pgvecto.rs`**.

## Upstream Sources

1. **VectorChord, Cloud, and `pgvecto.rs` Documentation**
   - **Source Repository**: [`https://github.com/tensorchord/pgvecto.rs-docs`](https://github.com/tensorchord/pgvecto.rs-docs)
   - **Original Site**: [`https://docs.vectorchord.ai/`](https://docs.vectorchord.ai/)
   - **Copyright**: © 2023–Present TensorChord Inc. and Contributors.
   - **Adaptations**: Converted from VitePress to Hugo + [OINK `v1.4.0`](https://github.com/pgsty/oink), including GitHub-style callout normalization, KaTeX math delimiter standardization, internal link resolution, and structural navigation metadata.

2. **VectorChord Engineering Blog & Release Notes**
   - **Original Publication**: [`https://blog.vectorchord.ai/`](https://blog.vectorchord.ai/)
   - **Copyright**: © 2023–Present TensorChord Inc. and respective article authors (`Keming`, `Haze`, `VoVAllen`, `Yifanwang`, `Kolkri`, `Gin`, `Scase`).
   - **Adaptations**: Archived into `content/blog/post/` and `content/blog/release/` with original publication dates, author metadata, and direct `upstream_link` provenance pointers.

3. **VectorChord Source Code (`pgsty/vchord`)**
   - **Forked From**: [`https://github.com/tensorchord/VectorChord`](https://github.com/tensorchord/VectorChord)
   - **Companion Projects**:
     - [`tensorchord/VectorChord-bm25`](https://github.com/tensorchord/VectorChord-bm25)
     - [`tensorchord/pg_tokenizer.rs`](https://github.com/tensorchord/pg_tokenizer.rs)
     - [`tensorchord/pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs)

## Page-Level Provenance

Every documentation page and blog post derived from upstream material declares `upstream_link` in its front matter. OINK renders this provenance link in the page footer alongside modification indicators.
