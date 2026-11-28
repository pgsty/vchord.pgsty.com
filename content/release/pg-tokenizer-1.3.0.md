---
title: "pg_tokenizer 1.3.0: Fast-Path Caches, Native C TSVector, and Pipeline Speedups"
date: 2026-11-25
description: "pg_tokenizer 1.3.0 cuts repeated primary-read overhead with a lock-free cache barrier, rewrites analyze_to_tsvector and tokenize_to_tsvector in native C, optimizes custom vocabulary triggers and pipeline stages, and supports PostgreSQL 15–19."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0"
upstream_source: ""
upstream_link: ""
tags:
  - "pg_tokenizer"
aliases: [/blog/release/pg-tokenizer-1.3.0/]
---

{{< release-card >}}

**pg_tokenizer 1.3.0** is the published PostgreSQL 15–19 release of [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) on `x86_64` and `aarch64`, building on [1.2.0](/release/pg-tokenizer-1.2.0/). It eliminates per-statement SPI lookups on primary reads, replaces the SQL `tsvector` wrappers and PL/pgSQL custom-model trigger with native `LANGUAGE c` implementations, streamlines every stage of the analysis and tokenization pipeline, and tightens Hugging Face import validation.

Pre-built `.deb` and `.zip` packages for PostgreSQL 15–19 (`x86_64` and `aarch64`, built on Ubuntu 24.04 with embedded IPADIC, requiring `glibc >= 2.39`), the PGXN source archive (`pg_tokenizer-1.3.0.zip`), and `SHA256SUMS` are published on the [GitHub Release](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0).

## Changes in 1.3.0 {#changes}

| Area | Change |
| :--- | :--- |
| Primary definition caches | On an up-to-date primary, repeated reads reuse validated backend caches through a shared invalidation epoch and `FullTransactionId` barrier without SPI queries, `pg_depend` lookups, or marking the command ID used. `BEFORE` and `AFTER STATEMENT` triggers mark local mutations and publish committed definition changes. Older/imported snapshots, physical standbys, promotion, and databases still running `1.2.0` SQL automatically fall back to the snapshot-visible `definition_version` path. Unrelated `ROLLBACK` / `ROLLBACK TO SAVEPOINT` statements preserve validated primary caches. |
| Native `LANGUAGE c` `tsvector` | `analyze_to_tsvector` and `tokenize_to_tsvector` are now native `LANGUAGE c` functions that construct PostgreSQL `TSVectorData` varlenas directly, bypassing SQL wrapper overhead, text escaping, `int4[]::text[]` casts, and `tsvectorin` reparsing while preserving identical lexeme sorting, the 2,046-byte lexeme limit, 256-position cap, 16,383 position clamp, and 1,048,575-byte `MAXSTRPOS` checks. `_tokens_to_tsvector_text` and `_analyze_to_tsvector_text` remain exported for backward compatibility. |
| Custom vocabulary triggers | `custom_model_insert_trigger` is rewritten in `LANGUAGE c`. Writers check distinct candidate terms via parameterized queries that use the vocabulary's unique index, so known terms consume no new sequence IDs. Per-model transaction advisory locks serialize concurrent new-term insertion while both triggers evaluate their own row predicates. Ordinary tokenization reads the caller's snapshot, and target assignments honor PostgreSQL casts and SQL `tokenize` privileges/settings. |
| Streamlined pipeline | Read GUC budget limits once per call, eliminate intermediate `Vec<&str>` allocations and redundant post-stage budget passes, avoid `String` copies on empty/identity analyzers, and fuse `Vec<i32>` output directly. Throttle lightweight filter interrupt checks to every 1,024 tokens; make non-ASCII `to_lowercase` single-pass (zero-allocation for unchanged CJK while preserving Greek final sigma); add an ASCII zero-allocation fast path to Unicode normalization (`nfc`/`nfd`/`nfkc`/`nfkd`); optimize `ngram` batches (ASCII fast path + reusable offset scratch); remove per-token temporary vectors and `CString` allocations in `pg_dict`. |
| Hugging Face validation | `create_huggingface_model` validates `padding.pad_id <= 2147483647` at import time in addition to vocabulary, added tokens, and post-processor special tokens. |
| Packaging & verification | Raw pgrx output, ZIP archives, and Debian packages all include the `1.2.0 → 1.3.0` upgrade script. CI verifies installed migrations against release sources before running full-chain upgrade tests. |
{.wide .expand}

## Binary compatibility and minimum PostgreSQL minor versions {#compatibility}

> [!IMPORTANT] Check your PostgreSQL minor version before restarting
> GitHub release binaries linked against newer PostgreSQL tuple-header functions require at least **PostgreSQL 15.20, 16.16, 17.12, 18.7, or 19.0+** on their respective branches. On an older minor release, `pg_tokenizer.so` fails to load and PostgreSQL refuses to start while it is in `shared_preload_libraries`. The `.deb` declares this requirement as a package dependency; for a `.zip`, inspect the last line of `pg_tokenizer.control` (`unzip -p <archive>.zip pg_tokenizer.control | tail -n 1`) before installing. Upgrade PostgreSQL's minor release first, or build from source against the local `pg_config`.

GitHub `.deb` and `.zip` binaries are compiled on Ubuntu 24.04 (`glibc >= 2.39`, targeting Ubuntu 24.04+ and Debian 13+) with embedded IPADIC. On EL 8/9/10, Debian 12, or Ubuntu 22.04, install native [Pigsty packages](/docs/tokenizer/installation/#pigsty) (with external Lindera 7 format-v3 dictionaries if Japanese/Korean segmentation is needed) or build from source.

## Upgrading to 1.3.0 {#upgrade-notes}

1. **Install and restart**: Install the `1.3.0` shared library and SQL files on the primary and all physical standbys ([Installation](/docs/tokenizer/installation/)), then restart PostgreSQL on each node.
1. **Update each database on the primary**:

   ```sql
   ALTER EXTENSION pg_tokenizer UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

- **Rolling `1.2.0 → 1.3.0` compatibility**: Backends running the `1.3.0` library against un-upgraded `1.2.0` SQL continue working safely on the `definition_version` path until `ALTER EXTENSION pg_tokenizer UPDATE;` enables the primary cache fast path and native `tsvector` functions. Catalog definitions, custom vocabulary IDs, views, and table triggers are preserved in place with no recomputation needed.
- **Upgrading from `1.1.0` or earlier**: `ALTER EXTENSION pg_tokenizer UPDATE;` walks the full chain `0.1.0 → 0.1.1 → 1.0.0 → 1.1.0 → 1.2.0 → 1.3.0`. Review the [1.2.0](/release/pg-tokenizer-1.2.0/) (PostgreSQL 15–19 and Lindera 7 format v3) and [1.1.0](/release/pg-tokenizer-1.1.0/) (`READ COMMITTED` transaction and `tokenizer_data` schema) steps in [Upgrade](/docs/tokenizer/installation/#upgrading).
- **Trigger-bypass maintenance**: If a superuser modifies `tokenizer_catalog` tables with triggers disabled or under `session_replication_role = replica`, primary backends on the fast path will not observe the change until a trigger advances the barrier. Re-enable triggers, restore `session_replication_role = origin`, and run a committed no-op update on one definition table as documented in [Backend-Local Definition Caches](https://github.com/pgsty/pg_tokenizer/blob/v1.3.0/docs/07-limitation.md#backend-local-definition-caches).
