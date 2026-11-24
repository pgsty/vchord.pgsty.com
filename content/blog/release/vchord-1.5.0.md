---
title: "vchord 1.5.0 for PostgreSQL 15–19"
date: 2026-11-24
description: "Streaming filtered searches, parallel vector builds and graph repair after deletes."
authors: ["vonng"]
release_url: "https://github.com/pgsty/vchord/releases/tag/1.5.0"
upstream_source: ""
upstream_link: ""
tags: ["release", "vchord"]
---

Download the Linux ZIP or DEB for your PostgreSQL major and architecture. The GitHub release covers PostgreSQL 15–19 on x86_64 and aarch64. [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.5.0)

An RQ index with filter keys now streams candidates from the initial IVF lists. A query such as `WHERE tenant_id = 42 ORDER BY embedding <-> $1 LIMIT 10` can stop as soon as ten rows are available. When more rows are needed, the scan expands up to `vchordrq.max_probes`. A later round can return a closer row. Applications that need a total order can overfetch and sort their result.

### Sphere search

A sphere search remains approximate in the rows it visits. PostgreSQL checks candidates against the strict radius. An RQ scan can accept an interior hit directly for a single f32 L2 sphere when the rerank uses the SQL operator’s whole-vector reduction and the filter keys are exact. Graph, half-precision, inner-product and cosine sphere searches use the heap predicate.

### Building and maintaining indexes

Parallel builds can use workers on TOAST-backed tables whose main heap is small. Keyed RQ compaction divides its sort memory among the leader and workers actually launched. Online RQ VACUUM returns retired pages after publishing each list. Graph insertion records an extended vector page and its incoming link together in WAL. Graph VACUUM can follow a deleted bridge to a live region with spare neighbor slots.

## Upgrade

Install the matching library and SQL files, restart PostgreSQL, and run the command in every database using vchord. Existing 1.4.0 indexes open in place. Upgrades from 1.3.0 also install the filter-key SQL objects. If an older graph VACUUM already disconnected a live region, rebuild that index with `REINDEX INDEX CONCURRENTLY index_name;`.

```sql
ALTER EXTENSION vchord UPDATE TO '1.5.0';
```
