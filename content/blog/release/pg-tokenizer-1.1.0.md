---
title: "pg_tokenizer 1.1.0: Consistent Caches and Analysis Limits"
date: 2026-11-08
description: "pg_tokenizer 1.1.0 adds WAL-replicated definition invalidation, fixes prepared-transaction cache cleanup, separates runtime vocabulary privileges, and introduces configurable analysis budgets."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
tags:
  - "release"
  - "pg_tokenizer"
  - "full-text-search"
release_url: "https://github.com/pgsty/pg_tokenizer/releases/tag/v1.1.0"
upstream_source: ""
upstream_link: ""
---

**pg_tokenizer 1.1.0** improves definition-cache consistency, text-analysis correctness, and configuration privileges. It supports PostgreSQL 14–18 and retains the existing `INT[]` tokenization and native `tsvector` interfaces.

> [!NOTE] Release scope
> This release is accepted for **fresh installations**. Upgrade compatibility, per-schema default-privilege migration, snapshots spanning an upgrade, and staging manifests left by failed build preflight are outside this release's acceptance scope. Existing upgrade scripts remain available for separate evaluation.

> [!NOTE] Extension & Release Links
> - **GitHub Release**: [pg_tokenizer v1.1.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.1.0) · [Full changelog](https://github.com/pgsty/pg_tokenizer/compare/v1.0.0...v1.1.0)
> - **Documentation**: [Installation](/docs/tokenizer/installation/) · [SQL reference](/docs/tokenizer/reference/) · [Models](/docs/tokenizer/models/)
> - **Source**: [Repository](https://github.com/pgsty/pg_tokenizer) · [Versioned release notes](https://github.com/pgsty/pg_tokenizer/blob/v1.1.0/docs/release-notes/1.1.0.md)

The GitHub release is prepared as a draft. Its download assets become publicly available when the draft is published.

## Definition caches and prepared transactions {#definition-caches}

Definition caches now validate against a transactional catalog version replicated through WAL. Analyzer, tokenizer, model, stopword, and synonym lookups read the version and definitions under the same SQL snapshot. A standby observes committed changes after replay reaches them and its query takes a suitable snapshot; promotion preserves this behavior.

The preparing backend now clears derived objects and validation state at `PREPARE TRANSACTION`. This fixes a specific failure sequence: direct catalog DML loads configuration X into a session's cache, another connection rolls back the prepared transaction, and a later transaction commits configuration Y with the same version number. The original connection now loads Y. The regression verifies that `Hello World` returns `{"H","W"}` for the replacement regex configuration instead of retaining `{"hello","world"}`.

Read-only transactions can still be prepared. Definition-changing APIs continue to reject PREPARE. Ordinary transaction commits retain the normal cache-reuse path, and direct catalog DML remains an administrative operation because it bypasses API configuration validation.

## Other changes {#changes}

| Area | Change |
| :--- | :--- |
| Runtime schema | Vocabulary tables and their sequences live in `tokenizer_data`; database owners do not need CREATE on `tokenizer_catalog`. |
| Parallel queries | Catalog-writing functions are `PARALLEL UNSAFE`; read-only analysis remains `PARALLEL SAFE`. |
| PostgreSQL dictionaries | New `pg_dict` definitions store schema-qualified names, so later callers' search paths cannot select a different dictionary. |
| Lindera privileges | Loading dictionary files requires superuser or `pg_read_server_files` privileges. Matching models already loaded or preloaded remain reusable. |
| Custom vocabularies | Long tokens split at UTF-8 boundaries; trigger output follows the target column's assignment semantics. |
| Native full-text search | Repeated lexemes are aggregated before conversion to `tsvector`. |
| Jieba | `full` and `precise` select the intended algorithms; the default `search` mode is unchanged. |
| Packaging | Safe shared-library installation examples, a PGXN-compatible source archive, and tests of the actual DEB and ZIP contents. |

## Analysis budgets {#analysis-budgets}

The following session-settable limits reject oversized input or output with SQLSTATE `54000`:

| Setting | Default |
| :--- | ---: |
| `pg_tokenizer.max_input_bytes` | 16 MiB |
| `pg_tokenizer.max_output_tokens` | 1,000,000 |
| `pg_tokenizer.max_output_bytes` | 64 MiB |
| `pg_tokenizer.max_piece_bytes` | 1 MiB |

These budgets do not impose a hard memory limit or a bounded cancellation latency inside third-party libraries. Load trusted model configurations and bound documents in the application. [Issue #13](https://github.com/pgsty/pg_tokenizer/issues/13) remains open for this limitation; see the [resource-budget reference](/docs/tokenizer/reference/#definition-caches).

## Installation and packages {#installation}

GitHub DEB and ZIP packages target PostgreSQL 14–18 on x86_64/amd64 and aarch64/arm64 and are built on **Ubuntu 24.04** with embedded IPADIC. Use a matching native package or a source build on other distributions. Native Pigsty RPM/DEB packages do not embed Lindera dictionaries; supply a dictionary compiled with Lindera 6.

The GitHub release also includes `pg_tokenizer-1.1.0.zip`, its SHA-256 file, and `SHA256SUMS` covering the binary packages and source ZIP. PGXN publication is separate from preparing this source archive.

Install the matching files, add `pg_tokenizer.so` to `shared_preload_libraries` while preserving existing entries, and restart PostgreSQL. Then run:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
SET search_path TO "$user", public, tokenizer_catalog;

SELECT create_text_analyzer(
    'words',
    'character_filters = ["to_lowercase"]
pre_tokenizer = "unicode_segmentation"'
);
SELECT apply_text_analyzer('Hello World', 'words');
```

The result is `{hello,world}`. Neither `vchord` nor `vchord_bm25` is required. Follow the [installation guide](/docs/tokenizer/installation/) for package selection and server configuration.

If reusing persisted output from older versions, note that Jieba's `full` and `precise` modes were swapped in 1.0.0 and earlier. Regenerate output produced with either mode and rebuild dependent indexes.

## Validation {#validation}

Draft creation is gated on a successful Check run for the tagged commit across PostgreSQL 14–18 and both Linux architectures. Each release build installs its DEB, compares the installed files with its ZIP, and runs SQLLogicTest, integration, preload, and physical-standby tests against the packaged library.

The prepared-transaction regression was also verified on macOS arm64/PostgreSQL 18.6: the same test fails against the unpatched baseline and passes after the fix, including version reuse and normal `COMMIT PREPARED`.
