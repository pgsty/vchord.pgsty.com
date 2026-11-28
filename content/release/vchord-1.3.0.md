---
title: "vchord 1.3.0: Recovery and Operational Hardening"
date: 2026-11-10
description: "vchord 1.3.0 hardens WAL page publication, graph maintenance, query-sampling permissions, RaBitQ cosine semantics, and scan execution for PostgreSQL 14–18."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/vchord/releases/tag/1.3.0"
upstream_source: ""
upstream_link: ""
tags:
  - "vchord"
aliases: [/blog/release/vchord-1.3.0/]
---

{{< release-card >}}

**vchord 1.3.0** continues the PGSTY-maintained release line for PostgreSQL 14–18. It retains `vchordrq.epsilon = 1.9` as the default search setting and hardens crash recovery, graph maintenance, query-sampling privileges, quantization edge cases, and scan execution.

Pre-built Linux ZIP archives and Debian packages for PostgreSQL 14–18 on `x86_64` and `aarch64` (built on Ubuntu 22.04; DEB control declares `libc6 >= 2.35`, with SHA-256 checksums for every artifact) are attached to the [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.3.0).

Install the matching shared library and SQL files, restart PostgreSQL, and run `ALTER EXTENSION vchord UPDATE TO '1.3.0';` in each database where `vchord` is installed. In-place catalog upgrades from `0.2.0` through `1.2.0` are supported; review the [upgrade notes](#upgrade-notes) before upgrading.

## Changes in 1.3.0 {#changes}

| Area | Change |
| :--- | :--- |
| WAL page publication | New `vchordrq` vector pages and `vchordg` vertex pages publish page initialization and their incoming link in a single Generic WAL record before free-space hints expose the page. Unaligned vertex-pointer writes on aligned `vchordg` pages are fixed. On-disk page formats remain compatible. |
| Graph maintenance & inserts | `vchordg` performs bounded local `VACUUM` bridge repair, skips index rewrites when `VACUUM` finds no changes, prevents concurrent inserts from linking through vertices freed by `VACUUM`, and aborts exhausted backlink retries with SQLSTATE `40001`. |
| Query sampling & recorder | Query sampling remains `off` by default. Reading `vchordrq_sampled_queries` and calling sampling functions now require superuser or `pg_read_all_stats`; table ownership and `SELECT` are insufficient. Ordinary committed index and database drops clean up recorder files after commit, while `ROLLBACK` and `SAVEPOINT` rollback keep existing samples. |
| External build options | `build.external.table` must use a schema-qualified `schema.table` name. Existing unqualified indexes remain queryable, and operations that rebuild or replace the index (`REINDEX`, `TRUNCATE`, `VACUUM FULL`, `CLUSTER`, type rewrites, dump restore) fail with SQLSTATE `22023` and a hint until updated. |
| RaBitQ cosine & validation | `rabitq4` and `rabitq8` cosine distance (`<=>` and `<<=>>`) computes `1 - cos`; zero-norm and non-finite vectors return `NaN` and are skipped by cosine indexes. Zero and 1-dimensional vectors produce finite quantization factors. `dequantize_to_*` rejects dimensions `> 16000` (`54000`) and `f16` overflow (`22003`). `rabitq4(n)` and `rabitq8(n)` text and `COPY` input preserve `1.2.0` behavior (typmod `n` is validated by indexes, not plain table input) for `pg_dump` compatibility. |
| `halfvec` & scan execution | `halfvec` ANN routing uses exact residual bounds with ARM FP16/FHM acceleration. `vchordg.io_search` and `vchordg.io_rerank` now control vertex traversal and vector reranking respectively (fixing swapped GUC dispatch). `vchordrq` prefiltering evaluates predicates once per candidate and disables prefiltering when volatile expressions or `SubPlan`s are present. |
| Planner, sampling & platform | Index scans check for query cancellation outside list locks without sleeping under locks; hook-started scans allocate in the query memory context; `NULL` sphere keys enforce heap recheck and malformed spheres raise errors; unusable vector index paths receive `disable_cost`; K-means block sampling uses a `u64` Feistel domain for tables above 8 TiB; `mimalloc` is enabled only on Linux so `vchord` and `vchord_bm25` coexist on macOS. |
{.wide .expand}

## Recovery, graph maintenance, and sampling lifecycle {#recovery-and-operations}

- **Atomic page publication**: Initializing a new `vchordrq` vector page or `vchordg` vertex page and writing its incoming link now share one Generic WAL record before PostgreSQL's Free Space Map (FSM) can advertise the page to concurrent writers. Crash recovery and physical standby replay never observe an uninitialized linked page, without adding per-page WAL flushes.
- **Bounded `vchordg` `VACUUM` repair**: `vchordg` repairs sparse deleted bridges within bounded memory and traversal limits. Clustered or heavy delete workloads can still reduce graph connectivity; measure recall after large deletes and run `REINDEX INDEX CONCURRENTLY` when recall drops. Table `autovacuum` remains required.
- **Recorder security and transaction boundaries**: Sampled query vectors are local diagnostic artifacts stored outside MVCC rollback, not an audit log. Access to `vchordrq_sampled_queries` and `vchordrq.query_sampling_*` is restricted to superusers and members of `pg_read_all_stats` (`vchordrq_prewarm` and `vchordg_prewarm` keep their table owner / `SELECT` checks). Post-commit cleanup removes sample files after ordinary committed `DROP INDEX` or `DROP DATABASE`; `PREPARE TRANSACTION` retains samples, `COMMIT PREPARED` or a post-commit crash can leave unreachable files, `DROP INDEX CONCURRENTLY` can delete samples at an internal commit even if later canceled, and `REINDEX CONCURRENTLY` starts a new sample identity.

## Upgrade notes {#upgrade-notes}

1. **Audit external-build index options before maintenance or restore**: Check whether any `vchordrq` index stores an unqualified `build.external.table` name:

   ```sql
   SELECT c.oid::regclass AS index_name, o.option_value
   FROM pg_class AS c
   JOIN pg_am AS am ON am.oid = c.relam
   CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
   WHERE am.amname = 'vchordrq'
     AND o.option_name = 'options'
     AND o.option_value LIKE '%external%';
   ```

   Inspect both dotted (`build.external.table`) and `[build.external]` TOML forms. Update unqualified names while keeping all other options intact:

   ```sql
   ALTER INDEX my_index SET (options = $$
   [build.external]
   table = 'public.centroids'
   $$);
   ```

2. **Rebuild affected legacy quantized or cosine indexes**: `ALTER EXTENSION vchord UPDATE TO '1.3.0'` updates SQL catalog definitions without rewriting existing index pages. Run `REINDEX INDEX CONCURRENTLY` on:
   - Existing `rabitq4` / `rabitq8` cosine indexes (`rabitq*_cosine_ops`), or cosine indexes containing zero-norm or non-finite vectors.
   - `rabitq4` / `rabitq8` indexes built in `1.2.0` or earlier that contain zero vectors or 1-dimensional vectors.

3. **Review monitoring roles**: Grant `pg_read_all_stats` to monitoring roles that read `vchordrq_sampled_queries` or run `vchordrq_evaluate_query_recall` against sampled queries.

See the [External Build Guide](/docs/vchord/usage/external-build/), [Recall Evaluation & Query Sampling](/docs/vchord/usage/measure-recall/#query-sampling), [Graph Index Maintenance](/docs/vchord/usage/graph-index/#maintenance), and [Quantization Types](/docs/vchord/usage/quantization-types/) for complete operational details.
