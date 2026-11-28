---
title: "pg_tokenizer 1.2.0: PostgreSQL 19, Lindera 7, and Preload Hardening"
date: 2026-11-23
description: "pg_tokenizer 1.2.0 upgrades to pgrx 0.20.0 and Lindera 7.0.0 for PostgreSQL 15–19, eliminates per-token filter allocations, hardens trigger cleanup and atomic preload files, and updates toml, regex, and url."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/pg_tokenizer/releases/tag/v1.2.0"
upstream_source: ""
upstream_link: ""
tags:
  - "pg_tokenizer"
aliases: [/blog/release/pg-tokenizer-1.2.0/]
---

**pg_tokenizer 1.2.0** upgrades [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) to `pgrx 0.20.0` and Lindera `7.0.0`, supporting **PostgreSQL 15–19** on `x86_64` and `aarch64` (dropping PostgreSQL 14). It also reduces per-token allocations across text filters, hardens trigger exception cleanup and preload file handling, and updates core parsing and security dependencies.

> [!NOTE] Superseded Tagged Milestone
> The `v1.2.0` source tag (`https://github.com/pgsty/pg_tokenizer/tree/v1.2.0`) was superseded by the published [**pg_tokenizer 1.3.0**](/release/pg-tokenizer-1.3.0/) release, which adds a zero-SPI primary cache fast path, native `LANGUAGE c` `tsvector` builders, and faster custom vocabulary writes. Install [`pg_tokenizer 1.3.0`](/release/pg-tokenizer-1.3.0/) for pre-built GitHub packages and production deployments.

## Changes in 1.2.0 {#changes}

| Area | Change |
| :--- | :--- |
| PostgreSQL 15–19 & `pgrx 0.20.0` | Add PostgreSQL 19 across source builds, CI, and packaging; drop PostgreSQL 14. CI and release builds use Rust `1.100.0` (source builds require Rust `1.99.1+` and matching Clang/libclang/LLVM tools). Fix `tools/pgxn.py` major-version detection for pre-release strings such as `PostgreSQL 19rc1` and `PostgreSQL 19beta2`. |
| Lindera `7.0.0` | Upgrade Lindera to `7.0.0`. External system dictionaries now require **format v3**. Embedded IPADIC keeps the `2025-09-20` source while builder and segmentation changes alter some word IDs; existing model configs, user dictionary IDs (`1073741824+`), and omission of unknown tokens remain preserved. |
| Text analysis & allocations | `to_lowercase` leaves all-lowercase ASCII input in place and checks cancellation every 1,024 bytes when converting uppercase ASCII. Rust `1.100.0` supplies Unicode 18.0 tables for lowercasing and alphanumeric checks (preserving contextual rules like Greek final sigma). `stopwords`, `synonym`, and `skip_non_alphanumeric` reuse the input vector in place instead of allocating a vector per token. `tsvector` construction stores 16-bit positions. |
| Trigger & snapshot safety | Restore the caller's `CurrentMemoryContext` and guard process/transaction exit paths in `ExecutorState::drop` when custom-model target-column coercion fails (e.g. `varchar(n)` length or domain `CHECK`/`NOT NULL` errors). Cache validation verifies an active snapshot exists before accessing it. |
| Atomic preload files | Concurrent `add_preload_model` and `remove_preload_model` publish or unlink one complete entry at a time. Startup skips invalid names, symlinks, special files, and damaged configurations with a warning. `list_preload_models()` returns sorted names and an empty array when the directory does not exist. |
| Parser & security deps | Update `toml` to `1.2.2` (fixes a stack overflow on invalid TOML), `regex` to `1.13.2` (corrects match boundaries of alternatives sharing a repeated prefix), and `url` `2.5.9` / `form_urlencoded` `1.2.3` ([`RUSTSEC-2026-0592`](https://rustsec.org/advisories/RUSTSEC-2026-0592.html)). Add automated CI checks for install SQL parity, exported C symbols across the full upgrade chain, and PostgreSQL server log health. |
{.wide .expand}

## Tokenization output changes {#token-changes}

Three upstream changes in `1.2.0` can alter tokens produced from the same input text:

- **Lindera 7.0.0**: Both external format-v3 dictionaries and embedded IPADIC use the Lindera 7 builder and segmentation rules. For the default IPADIC model, `Google が 新しい` changes from `{19678,236490}` to `{19679,236490}` and `龘々` changes from `{}` to `{103}` (`関西国際空港限定` remains `{372982,374178}`).
- **`regex 1.13.2`**: Fixes match boundaries when regex alternatives share a variable-length prefix. For example, `id[0-9]*[0-9]|id[0-9]*-` on `id42-` now matches `id42` (previously `id42-`).
- **Unicode 18.0 (Rust 1.100.0)**: Lowercasing and `skip_non_alphanumeric` follow Unicode 18.0 when built with Rust `1.100.0` (vs. Unicode 17.0 on Rust `1.99.1`), for example lowercasing `U+A7DD` to `U+0277` and retaining it as alphanumeric.

Use the same compiler and dictionary build on all nodes that share data. If any of these changes affect your pipeline, recompute stored token arrays and `tsvector` columns from the source text before serving queries with the new version.

## Upgrading from 1.1.0 {#upgrade-notes}

1. **Upgrade PostgreSQL 14 first**: Move clusters to PostgreSQL 15–19 before installing `1.2.0` or later.
1. **Stage Lindera format-v3 dictionaries**: If any model loads an external Lindera system dictionary from disk, stage a format-v3 directory compiled with Lindera 7 on every node and swap it into the configured path while PostgreSQL is stopped. (If left on v2, startup skips preloading with a warning and backend loads fail with SQLSTATE `22023`.)
1. **Check preload paths**: Valid regular preload files under `$PGDATA/pg_tokenizer/preload_models` continue working in place. Replace any symlinked preload directories or entries with real directories and regular files before restarting.
1. **Install, restart, and update**: Install the `1.2.0` shared library and SQL files on primary and replicas, restart PostgreSQL on each node, and run:

   ```sql
   ALTER EXTENSION pg_tokenizer UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

SQL signatures, catalog definitions, and custom vocabulary IDs in `tokenizer_data` are preserved in place. See [Installation & Upgrade](/docs/tokenizer/installation/#upgrading) and [Preload models](/docs/tokenizer/models/#preload) for full details.
