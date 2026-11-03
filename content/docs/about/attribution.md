---
title: Attribution & Provenance
linkTitle: Attribution
description: Upstream sources, copyright notices, stewardship transition, and modification records for vchord.pgsty.com.
weight: 20
icon: fa-solid fa-scroll
aliases:
  - "/about/attribution/"
---

`vchord.pgsty.com` is maintained by the [PGSTY](https://pigsty.io/) community to provide a comprehensive, searchable documentation and engineering reference for the **Vchord** extension suite (**`vchord`**, **`vchord_bm25`**, and **`pg_tokenizer`**).

## Stewardship & Maintenance Statement {#stewardship}

**TensorChord Inc.**, the original creator of `VectorChord`, `VectorChord-bm25`, and `pg_tokenizer.rs`, has wound down operations and ceased active maintenance of the upstream repositories. At the request of the original authors, the **[PGSTY](https://pigsty.io/)** community took over maintenance of all three extensions:

- **Supply-Chain & Compatibility Continuity**: PGSTY maintains the repositories, unifies all three extensions on **`pgrx 0.19.3`** (`pg14`–`pg19` Cargo features), and tests and packages the suite for **PostgreSQL** (`PG 14–18`). Pre-built RPM/DEB packages are published across [16 mainstream Linux targets](/download/), and the complete dependency and license inventory is documented in the [Software Bill of Materials (SBOM)](/docs/about/sbom/).
- **Feature Roadmap Policy**: PGSTY does not commit to developing new features; feature requests and roadmap items are evaluated on a best-effort basis as maintainer capacity allows.
- **Security Reporting**: Security vulnerabilities and critical bug reports are always welcome via [GitHub Issues](https://github.com/pgsty/vchord/issues).

## Upstream Sources {#upstream-sources}

1. **Documentation (`content/docs/`, `content/cloud/`)**
   - **VectorChord & pgvecto.rs Docs**: [`https://github.com/tensorchord/pgvecto.rs-docs`](https://github.com/tensorchord/pgvecto.rs-docs) (`https://docs.vectorchord.ai/`) — © 2023–2026 TensorChord Inc. (Apache-2.0)
   - **BM25 & Tokenizer Docs**: [`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25), [`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs), and [`https://github.com/tensorchord/pg_bestmatch.rs`](https://github.com/tensorchord/pg_bestmatch.rs) — © 2024–2026 TensorChord Inc.
   - **pgvector Docs (`content/docs/vector/`)**: Adapted from [`https://github.com/pgvector/pgvector`](https://github.com/pgvector/pgvector) — © 2021–2026 Andrew Kane (PostgreSQL License).
   - **Adaptations**: Converted to Hugo + [OINK `v1.4.0`](https://github.com/pgsty/oink), including GitHub-style callout normalization, KaTeX math delimiter standardization, internal link resolution, and bilingual Chinese/English documentation.

2. **Engineering Blog & Release Notes (`content/blog/`)**
   - **Original Publication**: [`https://blog.vectorchord.ai/`](https://blog.vectorchord.ai/)
   - **Copyright**: © 2023–2026 TensorChord Inc. and respective original authors ([Ce Gao](https://github.com/gaocegege), [Jinjing Zhou](https://github.com/VoVAllen), [Junyu Chen](https://github.com/cutecutecat), [Keming Yang](https://github.com/kemingy), [xieydd](https://github.com/xieydd), [Zoie Wang](https://hashnode.com/@zoie), and the [TensorChord Team](https://github.com/tensorchord)).
   - **Adaptations**: Archived into `content/blog/post/` and `content/blog/release/` with original publication dates, author links, per-article copyright notices, and direct `upstream_link` provenance pointers.

3. **Vchord Extension Suite (`vchord`, `vchord_bm25`, and `pg_tokenizer`)**
   - **`vchord` ([`pgsty/vchord`](https://github.com/pgsty/vchord)) Forked From**: [`https://github.com/tensorchord/VectorChord`](https://github.com/tensorchord/VectorChord)
   - **`vchord_bm25` ([`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25)) Forked From**: [`https://github.com/supervc-stack/VectorChord-bm25`](https://github.com/supervc-stack/VectorChord-bm25)
   - **`pg_tokenizer` ([`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)) Forked From**: [`https://github.com/supervc-stack/pg_tokenizer.rs`](https://github.com/supervc-stack/pg_tokenizer.rs)
   - **Predecessor Project**: [`https://github.com/tensorchord/pgvecto.rs`](https://github.com/tensorchord/pgvecto.rs)

## Page-Level Provenance {#page-level-provenance}

Every documentation page and blog post derived from upstream material declares `upstream_link` and `upstream_copyright` in its front matter (or via section `cascade`). OINK renders this provenance link and copyright attribution in the page footer alongside modification indicators.
