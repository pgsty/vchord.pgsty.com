---
title: About VectorChord & vchord.pgsty.com
linkTitle: About
description: Project overview, licensing, upstream attribution, and trademark policy for the Pigsty-maintained VectorChord distribution and documentation site.
type: docs
sidebar_root_for: self
weight: 50
icon: fa-solid fa-circle-info
cascade:
  type: docs
---

**VectorChord (`vchord`)** is a PostgreSQL extension designed for scalable, high-performance, and disk-friendly vector similarity search, developed as the architectural successor to [`pgvecto.rs`](/pgvecto-rs/).

This repository (`pgsty/vchord.pgsty.com`) and website (`https://vchord.pgsty.com/`) provide a complete, fast, local-first documentation and technical blog reference for [`pgsty/vchord`](https://github.com/pgsty/vchord), maintained by the [Pigsty](https://pigsty.io/) community using the [OINK 1.4.0](https://oink.pgsty.com/) documentation framework.

> [!NOTE]
> **`pgsty/vchord` is a community-maintained fork of `tensorchord/VectorChord`.** It is not affiliated with, endorsed by, or sponsored by TensorChord Inc. See [Attribution](/about/attribution/) and [Trademark Policy](/about/trademark/) for details.

## Documentation Scope

| Section | Coverage |
| :--- | :--- |
| **[VectorChord Docs](/docs/)** | Installation, migration from `pgvecto.rs`, `vchordrq` and `vchordg` indexing, MaxSim multi-vector retrieval, range queries, PostgreSQL tuning, external index precomputation, benchmarks, and SQL reference. |
| **[Engineering Blog](/blog/)** | All 37 engineering deep-dives, benchmark analyses, hybrid search tutorials, and release announcements (`pgvecto.rs 0.2` through `VectorChord 1.1`). |
| **[VectorChord Cloud](/cloud/)** | Reference documentation for VectorChord Cloud clusters, connection endpoints, scaling, VPC peering, monitoring, and billing. |
| **[pgvecto.rs Archive](/pgvecto-rs/)** | Complete legacy documentation for `pgvecto.rs` (`vectors` extension), including installation, indexing, filtering, framework integrations, and administration. |
