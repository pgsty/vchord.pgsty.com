---
title: Software Bill of Materials (SBOM)
linkTitle: SBOM
description: Rust workspace architecture, internal crates, locked third-party dependencies, native C bindings, and SPDX license inventory for vchord, vchord_bm25, and pg_tokenizer.
weight: 40
icon: fa-solid fa-boxes-stacked
aliases:
  - "/about/sbom/"
---

This page provides the **Software Bill of Materials (SBOM)** for the three core Rust extensions maintained by the [PGSTY](https://pigsty.io/) community: **[`vchord`](https://github.com/pgsty/vchord)**, **[`vchord_bm25`](https://github.com/pgsty/vchord_bm25)**, and **[`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)**. All dependency versions and SPDX license identifiers below are extracted directly from each repository's `Cargo.toml`, `Cargo.lock`, and `deny.toml` manifests.

## Extension Suite Summary {#summary}

| **Extension** | **Repository** | **Version** | **License** | **Rust / `pgrx`** | **PG Support** | **Workspace Crates** | **Locked Packages** |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **[`vchord`](/docs/vchord/)** | [`pgsty/vchord`](https://github.com/pgsty/vchord) | `1.2.0` | `AGPL-3.0-only` | `2024` / `=0.19.3` | `pg14`–`pg19` | 15 | 243 |
| **[`vchord_bm25`](/docs/bm25/)** | [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) | `0.4.0` | `AGPL-3.0-only` | `2024` / `=0.19.3` | `pg14`–`pg19` | 8 | 194 |
| **[`pg_tokenizer`](/docs/tokenizer/)** | [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) | `0.2.0` | `Apache-2.0` | `2021` / `=0.19.3` | `pg14`–`pg19` | 1 | 366 |
{.wide .expand}

---

## 1 · `vchord` (`pgsty/vchord`) {#vchord}

**`vchord`** is compiled as a C-compatible dynamic library (`cdylib`) loaded into PostgreSQL via `shared_preload_libraries`. At the PostgreSQL extension level, it requires the upstream [`vector` (`/docs/vector/`)](/docs/vector/) extension for base `vector` and `halfvec` data types.

### 1.1 Internal Workspace Crates (`vchord`) {#vchord-workspace}

| **Crate** | **Path** | **License** | **Role in `vchord`** |
|:---|:---|:---:|:---|
| `vchord` | `/` | `AGPL-3.0-only` | PostgreSQL extension entrypoint (`pgrx`), SQL datatypes (`rabitq8`, `rabitq4`, `sphere`), GUCs, planner/index hooks, and background workers |
| `vchordrq` | `crates/vchordrq` | `AGPL-3.0-only` | Disk-friendly RaBitQ Inverted File (`USING vchordrq`) index build, hierarchical K-means partitioning, scan, prefiltering, reranking, and tape storage |
| `vchordg` | `crates/vchordg` | `AGPL-3.0-only` | High-QPS single-layer graph (`USING vchordg`) index build, beam search, neighborhood pruning, maintenance, and prewarming |
| `rabitq` | `crates/rabitq` | `AGPL-3.0-only` | 1-bit, 4-bit, and 8-bit RaBitQ residual/direct quantization, dot-product estimators, and lower-bound distance filters |
| `k_means` | `crates/k_means` | `AGPL-3.0-only` | Parallel K-means clustering (`rayon`) for in-database and external centroid training |
| `vector` | `crates/vector` | `AGPL-3.0-only` | Internal dense, half-precision (`f16`), and quantized vector representations and conversions |
| `distance` | `crates/distance` | `AGPL-3.0-only` | L2 (`<->`), negative inner product (`<#>`), cosine (`<=>`), and multi-vector MaxSim (`@#`) distance traits |
| `simd` | `crates/simd` | `AGPL-3.0-only` | Runtime CPU feature detection and SIMD intrinsics (`x86_64` AVX2/AVX-512/VPOPCNTDQ, `aarch64` NEON/SVE, `s390x`, `powerpc64`, scalar fallback) |
| `simd_macros` | `crates/simd_macros` | `AGPL-3.0-only` | Procedural macros for multi-architecture SIMD target dispatch |
| `index` | `crates/index` | `AGPL-3.0-only` | Generic PostgreSQL page/block allocator, WAL-safe buffer manager, and MVCC visibility helpers |
| `index_accessor` | `crates/index_accessor` | `AGPL-3.0-only` | Zero-copy tuple and quantized vector accessors over PostgreSQL index pages |
| `always_equal` | `crates/always_equal` | `AGPL-3.0-only` | Priority-queue payload wrapper that ignores payload ordering during distance comparisons |
| `feistel` | `crates/feistel` | `AGPL-3.0-only` | Deterministic Feistel network permutation used for pseudo-random sampling |
| `small_iter` | `crates/small_iter` | `AGPL-3.0-only` | Fixed-capacity stack iterator utilities |
| `xtask` | `crates/xtask` | `AGPL-3.0-only` | Build-time driver that inspects `PG_CONFIG`, compiles the `cdylib`, and packages `build/` artifacts |
{.wide .expand}

### 1.2 Direct Third-Party Dependencies (`vchord`) {#vchord-dependencies}

| **Crate** | **Locked Version** | **SPDX License** | **Scope** | **Purpose** | **Upstream Repository** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | Runtime (`cshim`) | Rust framework for PostgreSQL extensions (`pg14`–`pg19` bindings) | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | Runtime | Raw FFI bindings to PostgreSQL server headers and internals | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `rusqlite` | `0.41.1` | `MIT` | Runtime (`bundled`) | Embedded SQLite engine (`libsqlite3-sys 0.39.1`) used for external centroid/index import | [rusqlite/rusqlite](https://github.com/rusqlite/rusqlite) |
| `mimalloc` | `0.1.52` | `MIT` | Runtime (`x86_64`/`aarch64`) | High-performance allocator (`libmimalloc-sys 0.1.49`, `local_dynamic_tls`) on Linux & macOS | [purpleprotocol/mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust) |
| `rayon` | `1.12.0` | `MIT OR Apache-2.0` | Runtime | Data-parallel work-stealing thread pool for K-means and parallel index builds | [rayon-rs/rayon](https://github.com/rayon-rs/rayon) |
| `crossbeam-channel` | `0.5.17` | `MIT OR Apache-2.0` | Runtime | Multi-producer multi-consumer channels for parallel build coordination | [crossbeam-rs/crossbeam](https://github.com/crossbeam-rs/crossbeam) |
| `zerocopy` | `0.8.63` | `BSD-2-Clause OR Apache-2.0 OR MIT` | Runtime | Safe zero-copy byte reinterpretation for on-disk PostgreSQL index pages | [google/zerocopy](https://github.com/google/zerocopy) |
| `half` | `2.7.1` | `MIT OR Apache-2.0` | Runtime | IEEE 754 half-precision (`f16`) floating-point implementation for `halfvec` | [VoidStarKat/half-rs](https://github.com/VoidStarKat/half-rs) |
| `rand` | `0.10.3` | `MIT OR Apache-2.0` | Runtime | Random number generation for K-means seeding and random rotations | [rust-random/rand](https://github.com/rust-random/rand) |
| `rand_chacha` | `0.10.0` | `MIT OR Apache-2.0` | Runtime | Deterministic ChaCha CSPRNG for reproducible orthogonal matrix generation | [rust-random/rand](https://github.com/rust-random/rand) |
| `bumpalo` | `3.20.3` | `MIT OR Apache-2.0` | Runtime | Fast bump arena allocator for per-scan temporary allocations | [fitzgen/bumpalo](https://github.com/fitzgen/bumpalo) |
| `arrayvec` | `0.7.8` | `MIT OR Apache-2.0` | Runtime | Stack-allocated vectors with fixed capacity | [bluss/arrayvec](https://github.com/bluss/arrayvec) |
| `dary_heap` | `0.3.9` | `MIT OR Apache-2.0` | Runtime | Cache-friendly *d*-ary priority queue for candidate traversal | [hanmertens/dary_heap](https://github.com/hanmertens/dary_heap) |
| `min-max-heap` | `1.3.0` | `MIT OR Apache-2.0` | Runtime | Double-ended priority queue for bounded beam search in `vchordg` | [tov/min-max-heap-rs](https://github.com/tov/min-max-heap-rs) |
| `wyhash` | `0.6.0` | `MIT OR Apache-2.0` | Runtime | Fast non-cryptographic hashing for visited-vertex deduplication | [eldruin/wyhash-rs](https://github.com/eldruin/wyhash-rs) |
| `pin-project` | `1.1.13` | `Apache-2.0 OR MIT` | Runtime | Safe pinned struct projections for stateful index scan coroutines | [taiki-e/pin-project](https://github.com/taiki-e/pin-project) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | Runtime | Serialization framework for index reloptions (`options = $$...$$`) | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | Runtime | TOML parser for `vchordrq` and `vchordg` index build options | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | Runtime | Declarative range and structural validation for index options | [Keats/validator](https://github.com/Keats/validator) |
| `humansize` | `2.1.3` | `MIT OR Apache-2.0` | Runtime | Human-readable byte formatting for diagnostics | [LeopoldArkham/humansize](https://github.com/LeopoldArkham/humansize) |
| `paste` | `1.0.15` | `MIT OR Apache-2.0` | Macro | Identifier concatenation macro for operator boilerplate generation | [dtolnay/paste](https://github.com/dtolnay/paste) |
| `seq-macro` | `0.3.6` | `MIT OR Apache-2.0` | Macro | Compile-time loop unrolling for SIMD kernels | [dtolnay/seq-macro](https://github.com/dtolnay/seq-macro) |
| `proc-macro2` / `quote` / `syn` | `1.0.107` / `1.0.47` / `3.0.9` | `MIT OR Apache-2.0` | Proc-macro | Syntax parsing and token generation for `simd_macros` | [dtolnay/syn](https://github.com/dtolnay/syn) |
| `clap` / `object` / `serde_json` / `target-tuple` | `4.6.7` / `0.40.0` / `1.0.154` / `1.0.2` | `MIT OR Apache-2.0` | Build (`xtask`) | Build CLI parsing, ELF/Mach-O symbol inspection, and SQL entity graph generation (`pgrx-sql-entity-graph 0.19.3`) | [clap-rs/clap](https://github.com/clap-rs/clap) |
{.wide .expand}

---

## 2 · `vchord_bm25` (`pgsty/vchord_bm25`) {#vchord_bm25}

**`vchord_bm25`** is a standalone Rust/pgrx extension (`cdylib`) implementing native Okapi BM25 ranking and Block-WeakAnd (`WAND`) inverted indexes inside PostgreSQL. It has no hard runtime extension dependencies and pairs with either PostgreSQL native `tsvector` or [`pg_tokenizer`](/docs/tokenizer/).

### 2.1 Internal Workspace Crates (`vchord_bm25`) {#vchord_bm25-workspace}

| **Crate** | **Path** | **License** | **Role in `vchord_bm25`** |
|:---|:---|:---:|:---|
| `vchord_bm25` | `/` | `AGPL-3.0-only` | PostgreSQL extension entrypoint (`pgrx`), `bm25` index access method, `bm25vector`/`bm25query` types, `<&>` operator, GUCs, and planner cost hooks |
| `bm25` | `crates/bm25` | `AGPL-3.0-only` | Block-WeakAnd (`WAND`) top-K query evaluator, delta/bit-packed posting list compression, segment builder, and external sort I/O |
| `score` | `crates/score` | `AGPL-3.0-only` | Okapi BM25 scoring kernel (`k1 = 1.2`, `b = 0.75`) and quantized document-length normalization tables |
| `index` | `crates/index` | `AGPL-3.0-only` | PostgreSQL relation page management, jump pages, and MVCC-safe buffer locking |
| `simd` | `crates/simd` | `AGPL-3.0-only` | SIMD bit-packing and vectorized posting-list decoding (`x86_64` AVX2/AVX-512, `aarch64` NEON, scalar fallback) |
| `simd_macros` | `crates/simd_macros` | `AGPL-3.0-only` | Procedural macros for multi-architecture SIMD dispatch |
| `always_equal` | `crates/always_equal` | `AGPL-3.0-only` | Tie-breaking wrapper for top-K min-heap candidate evaluation |
| `xtask` | `crates/xtask` | `AGPL-3.0-only` | Build-time driver that compiles the extension, verifies SQL schema parity, and assembles `build/` |
{.wide .expand}

### 2.2 Direct Third-Party Dependencies (`vchord_bm25`) {#vchord_bm25-dependencies}

| **Crate** | **Locked Version** | **SPDX License** | **Scope** | **Purpose** | **Upstream Repository** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | Runtime | Rust framework for PostgreSQL extensions (`pg14`–`pg19` bindings) | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | Runtime | Raw FFI bindings to PostgreSQL server headers and internals | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `blake3` | `1.8.7` | `CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception` | Runtime | Cryptographic/fast hashing for vocabulary terms and segment integrity | [BLAKE3-team/BLAKE3](https://github.com/BLAKE3-team/BLAKE3) |
| `memmap2` | `0.9.12` | `MIT OR Apache-2.0` | Runtime | Cross-platform memory-mapped file I/O during external segment sorting | [RazrFalcon/memmap2-rs](https://github.com/RazrFalcon/memmap2-rs) |
| `mimalloc` | `0.1.52` | `MIT` | Runtime (`x86_64`/`aarch64`) | High-performance allocator (`libmimalloc-sys 0.1.49`, `local_dynamic_tls`) on Linux & macOS | [purpleprotocol/mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust) |
| `zerocopy` | `0.8.63` | `BSD-2-Clause OR Apache-2.0 OR MIT` | Runtime (`derive`, `simd`) | Zero-copy serialization of posting-list blocks and BM25 metadata pages | [google/zerocopy](https://github.com/google/zerocopy) |
| `getrandom` | `0.4.3` | `MIT OR Apache-2.0` | Runtime | Operating-system entropy source for temporary file naming | [rust-random/getrandom](https://github.com/rust-random/getrandom) |
| `rand` | `0.10.3` | `MIT OR Apache-2.0` | Runtime | Random number generation utilities | [rust-random/rand](https://github.com/rust-random/rand) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | Runtime | Serialization framework for `USING bm25` index reloptions | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | Runtime | TOML parser for index configuration options | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | Runtime | Validation rules for BM25 index reloptions | [Keats/validator](https://github.com/Keats/validator) |
| `seq-macro` | `0.3.6` | `MIT OR Apache-2.0` | Macro | Compile-time loop unrolling for bit-packing kernels | [dtolnay/seq-macro](https://github.com/dtolnay/seq-macro) |
| `proc-macro2` / `quote` / `syn` | `1.0.107` / `1.0.47` / `3.0.9` | `MIT OR Apache-2.0` | Proc-macro | Syntax parsing and token generation for `simd_macros` | [dtolnay/syn](https://github.com/dtolnay/syn) |
| `clap` / `object` / `serde_json` / `target-tuple` | `4.6.7` / `0.40.0` / `1.0.154` / `1.0.2` | `MIT OR Apache-2.0` | Build (`xtask`) | Build CLI parsing, symbol verification, and SQL schema parity check (`pgrx-sql-entity-graph 0.19.3`) | [clap-rs/clap](https://github.com/clap-rs/clap) |
{.wide .expand}

---

## 3 · `pg_tokenizer` (`pgsty/pg_tokenizer`) {#pg_tokenizer}

**`pg_tokenizer`** is a single-crate Rust/pgrx extension (`cdylib`, licensed under `Apache-2.0`) providing in-database multilingual text analysis, pre-tokenization, stemming, stopword/synonym filtering, and integer token-ID encoding.

### 3.1 Direct & Native Transitive Dependencies (`pg_tokenizer`) {#pg_tokenizer-dependencies}

| **Crate** | **Locked Version** | **SPDX License** | **Scope** | **Purpose** | **Upstream Repository** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | Runtime | Rust framework for PostgreSQL extensions (`pg14`–`pg19` bindings) | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | Runtime | Raw FFI bindings to PostgreSQL server headers and internals | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `tokenizers` | `0.23.2` | `Apache-2.0` | Runtime | HuggingFace fast tokenization pipeline (WordPiece, BPE, Unigram) | [huggingface/tokenizers](https://github.com/huggingface/tokenizers) |
| `tocken` | `0.1.0` | `Apache-2.0` | Runtime | Pre-built LLM/embedding vocabulary tokenizer (`bert_base_uncased`, `wiki_tocken`, `gemma2b`, `llmlingua2`) | [kemingy/tocken](https://github.com/kemingy/tocken) |
| `jieba-rs` | `0.11.0` | `MIT` | Runtime | Chinese word segmentation (`jieba` pre-tokenizer with HMM and user dictionaries) | [messense/jieba-rs](https://github.com/messense/jieba-rs) |
| `lindera` | `6.2.0` | `MIT` | Runtime | Japanese/CJK morphological analyzer framework (`lindera` model & pre-tokenizer) | [lindera/lindera](https://github.com/lindera/lindera) |
| `lindera-analysis` | `6.2.0` | `MIT` | Runtime | Character filters, token filters, and embedded IPADIC / UniDic / ko-dic / CC-CEDICT dictionary support | [lindera/lindera](https://github.com/lindera/lindera) |
| `rust-stemmers` | `1.2.0` | `MIT OR BSD-3-Clause` | Runtime | Snowball stemming algorithms for 20+ languages (fork commit `51696378`) | [tensorchord/rust-stemmers](https://github.com/tensorchord/rust-stemmers) |
| `unicode-segmentation` | `1.13.3` | `MIT OR Apache-2.0` | Runtime | Unicode Standard Annex #29 (`UAX #29`) word boundary segmentation (`unicode` pre-tokenizer) | [unicode-rs/unicode-segmentation](https://github.com/unicode-rs/unicode-segmentation) |
| `unicode-normalization` | `0.1.26` | `(MIT OR Apache-2.0) AND Unicode-3.0` | Runtime | Unicode NFC / NFD / NFKC / NFKD character normalization filters | [unicode-rs/unicode-normalization](https://github.com/unicode-rs/unicode-normalization) |
| `regex` | `1.13.1` | `MIT OR Apache-2.0` | Runtime | Finite-automata regular expression engine for regex pre-tokenizers and pattern filters | [rust-lang/regex](https://github.com/rust-lang/regex) |
| `dashmap` | `6.2.1` | `MIT` | Runtime | Concurrent sharded hash map for in-memory model and analyzer caching | [xacrimon/dashmap](https://github.com/xacrimon/dashmap) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | Runtime | Serialization framework for TOML/JSON pipeline and model configurations | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `serde_json` | `1.0.154` | `MIT OR Apache-2.0` | Runtime | JSON parser for HuggingFace tokenizer specifications | [serde-rs/json](https://github.com/serde-rs/json) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | Runtime | TOML parser for `create_tokenizer` / `create_text_analyzer` configuration blocks | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | Runtime | Declarative validation for analyzer and model configuration structs | [Keats/validator](https://github.com/Keats/validator) |
| `anyhow` | `1.0.104` | `MIT OR Apache-2.0` | Runtime | Contextual error reporting across tokenizer stages | [dtolnay/anyhow](https://github.com/dtolnay/anyhow) |
| `onig_sys` | `69.9.3` | `MIT` | Transitive (`tokenizers`) | Oniguruma regular expression C library bindings used by HuggingFace `tokenizers` | [iwillspeak/rust-onig](https://github.com/iwillspeak/rust-onig) |
| `esaxx-rs` | `0.1.10` | `Apache-2.0` | Transitive (`tokenizers`) | Enhanced suffix array C++ library used by Unigram vocabulary training | [Narsil/esaxx-rs](https://github.com/Narsil/esaxx-rs) |
| `zstd-sys` | `2.1.2+zstd.1.5.7` | `BSD-3-Clause` | Transitive (`lindera`) | Zstandard compression C bindings used for compressed morphological dictionaries | [gyscos/zstd-rs](https://github.com/gyscos/zstd-rs) |
| `pgrx-tests` | `0.19.3` | `MIT` | Dev / Test | PostgreSQL test harness for `cargo pgrx test` | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
{.wide .expand}

---

## 4 · License Compliance & SBOM Verification {#verification}

All three extension repositories enforce dependency license policies via [`cargo-deny`](https://embarkstudios.github.io/cargo-deny/) (`deny.toml`). Every third-party dependency in the resolved `Cargo.lock` graph is restricted to permissive, OSI-approved licenses:

- `MIT`
- `Apache-2.0` and `Apache-2.0 WITH LLVM-exception`
- `BSD-2-Clause` and `BSD-3-Clause`
- `ISC`
- `Unicode-3.0` and `Unicode-DFS-2016`
- `CC0-1.0` and `Zlib`

You can inspect the full transitive dependency tree or generate machine-readable CycloneDX / SPDX SBOM documents directly from any extension checkout:

```bash
# 1. Verify license compliance and security advisories with cargo-deny
cargo deny check

# 2. Inspect the full resolved dependency graph and licenses
cargo tree --format "{p} ({l})"

# 3. Export a machine-readable CycloneDX or SPDX JSON SBOM (via cargo-sbom or syft)
cargo sbom --output-format cyclone_dx_json_1_4 > sbom.cdx.json
```
