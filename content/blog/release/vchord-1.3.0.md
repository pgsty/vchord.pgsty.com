---
title: "vchord 1.3.0: Recovery and Operational Hardening"
date: 2026-11-09
description: "vchord 1.3.0 hardens index-page publication and diagnostic-data access while keeping approximate search tradeoffs explicit."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
upstream_source: ""
upstream_link: ""
tags:
  - "release"
  - "vchord"
  - "vector-database"
---

**vchord 1.3.0** continues the PGSTY-maintained release line for PostgreSQL 14–18. It keeps the `vchordrq.epsilon` default at `1.9` and focuses this release on recovery ordering, diagnostic-data permissions, and upgrade-safe operational behavior.

## Changes

| Area | Change |
| :--- | :--- |
| WAL publication | New `vchordrq` vector pages and `vchordg` vertex pages are published together with their incoming link in one Generic WAL record before free-space hints can expose the page. This does not add a per-page WAL flush or change the on-disk format. |
| Graph maintenance | `vchordg` keeps bounded local `VACUUM` repair. Arbitrary delete patterns can still reduce ANN recall; use recall checks and `REINDEX INDEX CONCURRENTLY` when a rebuild is appropriate. Full maintenance-page reclamation remains deferred. |
| Query sampling | Sampling remains disabled by default. Reading samples requires superuser or `pg_read_all_stats`; table ownership and `SELECT` are insufficient. Prewarm keeps its existing table privilege checks. Samples are local diagnostic data, outside PostgreSQL transaction rollback and not an audit log. |
| Recorder cleanup | Ordinary committed index and database drops trigger best-effort cleanup after commit. Rollback and SAVEPOINT rollback preserve samples. `PREPARE TRANSACTION` keeps them; `COMMIT PREPARED` or a crash after commit can leave unreachable diagnostics. `DROP INDEX CONCURRENTLY` can remove samples at an internal commit even if later cancelled. Concurrent reindexing starts a new sample identity. |
| External builds | `build.external.table` must be written as `schema.table`. Existing unqualified indexes remain queryable, but their option must be updated before operations that rebuild or replace the index, including `REINDEX`, `TRUNCATE`, `VACUUM FULL`, `CLUSTER`, relevant type changes, and dump restore. |
| RaBitQ typmods | Text and binary input keep the 1.2.0 behavior until the complete typmod design lands: `rabitq4(n)` and `rabitq8(n)` do not enforce `n` on input. This preserves `pg_dump` and logical-input compatibility for rows already accepted by `INSERT`; vchord indexes still validate dimensions. |
| Distance and numeric edge cases | RaBitQ cosine distance now uses `1 - cosine`; zero or non-finite directions are undefined and are skipped by cosine indexes. `halfvec` overflow and invalid dequantization now raise errors. Existing cosine indexes containing affected legacy vectors need a rebuild. |
| Insert conflicts | Exhausted `vchordg` backlink retries abort the transaction with `40001`; retry the transaction at the application level. |

## Upgrade notes

Before upgrading, check external-build options before maintenance or restore operations:

```sql
SELECT c.oid::regclass AS index_name, o.option_value
FROM pg_class AS c
JOIN pg_am AS am ON am.oid = c.relam
CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
WHERE am.amname = 'vchordrq'
  AND o.option_name = 'options'
  AND o.option_value LIKE '%external%';
```

Review both dotted and `[build.external]` TOML forms. Update any unqualified value, preserving other settings in `options`, for example:

```sql
ALTER INDEX my_index SET (options = $$
[build.external]
table = 'public.centroids'
$$);
```

Rebuild old cosine indexes when their data contains zero-norm or otherwise invalid directions. A catalog upgrade does not rewrite index pages. Review access to `vchordrq_sampled_queries` and the sampling functions: these functions intentionally expose query vectors only to statistics administrators.

See the [external-build guide](/docs/vchord/usage/external-build/), [query-sampling guide](/docs/vchord/usage/measure-recall/#query-sampling), [graph maintenance guide](/docs/vchord/usage/graph-index/#maintenance), and [quantization types](/docs/vchord/usage/quantization-types/) for the operational details.
