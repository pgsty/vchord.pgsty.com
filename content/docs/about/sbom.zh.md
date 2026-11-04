---
title: 软件物料清单 (SBOM)
linkTitle: 软件物料清单 (SBOM)
description: vchord、vchord_bm25 与 pg_tokenizer 三个核心 Rust 扩展的 Workspace 内部 Crate 架构、锁定的第三方依赖、原生 C 绑定与 SPDX 开源许可证清单。
weight: 40
icon: fa-solid fa-boxes-stacked
aliases:
  - "/about/sbom/"
---

本页列出由 [PGSTY](https://pigsty.cc/) 社区维护的三个核心 Rust 扩展——**[`vchord`](https://github.com/pgsty/vchord)**、**[`vchord_bm25`](https://github.com/pgsty/vchord_bm25)** 与 **[`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer)** 的完整**软件物料清单（Software Bill of Materials, SBOM）**。下方所有依赖版本号与 SPDX 许可证标识符均直接提取自各仓库当前的 `Cargo.toml`、`Cargo.lock`，以及存在时的 `deny.toml`。pg_tokenizer 一行描述 1.0.0 源码，不代表软件包已发布。

## 核心扩展套件概览 {#summary}

| **扩展名称** | **代码仓库** | **版本** | **许可证** | **Rust / `pgrx`** | **PG 支持** | **内部 Crate** | **锁定包数** |
|:---|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **[`vchord`](/zh/docs/vchord/)** | [`pgsty/vchord`](https://github.com/pgsty/vchord) | `1.2.0` | `AGPL-3.0-only` | `2024` / `=0.19.3` | `pg14`–`pg19` | 15 | 243 |
| **[`vchord_bm25`](/zh/docs/bm25/)** | [`pgsty/vchord_bm25`](https://github.com/pgsty/vchord_bm25) | `0.4.0` | `AGPL-3.0-only` | `2024` / `=0.19.3` | `pg14`–`pg19` | 8 | 194 |
| **[`pg_tokenizer`](/zh/docs/tokenizer/)** | [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) | `1.0.0` | `Apache-2.0` | `2021` / `=0.19.3` | `pg14`–`pg18` | 1 | 405 |
{.wide .expand}

---

## 1 · `vchord` (`pgsty/vchord`) {#vchord}

**`vchord`** 编译为 C ABI 兼容的动态链接库（`cdylib`），通过 `shared_preload_libraries` 加载至 PostgreSQL 进程空间。在 PostgreSQL 扩展层，它依赖上游基础扩展 [`vector`（`pgvector`）](/zh/docs/vector/)提供标准 `vector` 与 `halfvec` 数据类型。

### 1.1 Workspace 内部 Crate 清单 (`vchord`) {#vchord-workspace}

| **Crate 名称** | **目录路径** | **许可证** | **模块职责说明** |
|:---|:---|:---:|:---|
| `vchord` | `/` | `AGPL-3.0-only` | PostgreSQL 扩展入口（`pgrx`）、SQL 数据类型（`rabitq8`、`rabitq4`、`sphere`）、GUC 参数、优化器/索引钩子与后台工作进程 |
| `vchordrq` | `crates/vchordrq` | `AGPL-3.0-only` | 磁盘友好型 RaBitQ 倒排文件索引（`USING vchordrq`）：层次化 K-means 分区构建、扫描、预过滤、重排与磁盘页面管理 |
| `vchordg` | `crates/vchordg` | `AGPL-3.0-only` | 高吞吐单层图索引（`USING vchordg`）：图构建、波束搜索（Beam Search）、邻居剪枝、并发维护与索引预热 |
| `rabitq` | `crates/rabitq` | `AGPL-3.0-only` | 1-bit、4-bit 与 8-bit RaBitQ 残差/直接量化编码、内积无偏估计器与距离下界过滤 |
| `k_means` | `crates/k_means` | `AGPL-3.0-only` | 基于 `rayon` 的并行 K-means 聚类训练（支持数据库内构建与外部构建） |
| `vector` | `crates/vector` | `AGPL-3.0-only` | 内部稠密向量、半精度（`f16`）与量化向量的内存表示及类型转换 |
| `distance` | `crates/distance` | `AGPL-3.0-only` | 欧氏距离（`<->`）、负内积（`<#>`）、余弦距离（`<=>`）与多向量 MaxSim（`@#`）距离度量抽象 |
| `simd` | `crates/simd` | `AGPL-3.0-only` | 运行时 CPU 指令集探测与多架构 SIMD 加速（`x86_64` AVX2/AVX-512/VPOPCNTDQ、`aarch64` NEON/SVE、`s390x`、`powerpc64` 与标量回退） |
| `simd_macros` | `crates/simd_macros` | `AGPL-3.0-only` | 多架构 SIMD 目标代码生成与内联分发过程宏 |
| `index` | `crates/index` | `AGPL-3.0-only` | 通用 PostgreSQL 页面/块分配器、WAL 安全缓冲区管理与 MVCC 可见性判断 |
| `index_accessor` | `crates/index_accessor` | `AGPL-3.0-only` | 面向 PostgreSQL 索引页面的零拷贝元组与量化向量访问器 |
| `always_equal` | `crates/always_equal` | `AGPL-3.0-only` | 优先队列载荷包装器（在距离比较时忽略载荷顺序） |
| `feistel` | `crates/feistel` | `AGPL-3.0-only` | 用于伪随机抽样的确定性 Feistel 置换网络 |
| `small_iter` | `crates/small_iter` | `AGPL-3.0-only` | 固定容量栈上迭代器工具 |
| `xtask` | `crates/xtask` | `AGPL-3.0-only` | 构建驱动工具：读取 `PG_CONFIG`、编译 `cdylib` 并组装 `build/` 安装目录 |
{.wide .expand}

### 1.2 直接第三方依赖清单 (`vchord`) {#vchord-dependencies}

| **Crate 名称** | **锁定版本** | **SPDX 许可证** | **作用范围** | **功能用途** | **上游仓库** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | 运行时 (`cshim`) | PostgreSQL 扩展 Rust 开发框架（支持 `pg14`–`pg19` 绑定） | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | 运行时 | PostgreSQL 服务端头文件与内核函数的底层 FFI 绑定 | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `rusqlite` | `0.41.1` | `MIT` | 运行时 (`bundled`) | 内嵌 SQLite 引擎（`libsqlite3-sys 0.39.1`），用于外部预计算聚类中心与索引导入 | [rusqlite/rusqlite](https://github.com/rusqlite/rusqlite) |
| `mimalloc` | `0.1.52` | `MIT` | 运行时 (`x86_64`/`aarch64`) | Linux 与 macOS 平台高性能内存分配器（`libmimalloc-sys 0.1.49`，启用 `local_dynamic_tls`） | [purpleprotocol/mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust) |
| `rayon` | `1.12.0` | `MIT OR Apache-2.0` | 运行时 | 数据并行工作窃取线程池，用于并行 K-means 训练与索引构建 | [rayon-rs/rayon](https://github.com/rayon-rs/rayon) |
| `crossbeam-channel` | `0.5.17` | `MIT OR Apache-2.0` | 运行时 | 多生产者多消费者并发通道，用于并行索引构建协调 | [crossbeam-rs/crossbeam](https://github.com/crossbeam-rs/crossbeam) |
| `zerocopy` | `0.8.63` | `BSD-2-Clause OR Apache-2.0 OR MIT` | 运行时 | 面向 PostgreSQL 磁盘索引页面的安全零拷贝字节转换 | [google/zerocopy](https://github.com/google/zerocopy) |
| `half` | `2.7.1` | `MIT OR Apache-2.0` | 运行时 | IEEE 754 半精度浮点数（`f16`）算术支持，用于 `halfvec` | [VoidStarKat/half-rs](https://github.com/VoidStarKat/half-rs) |
| `rand` | `0.10.3` | `MIT OR Apache-2.0` | 运行时 | K-means 初始中心采样与随机旋转矩阵生成 | [rust-random/rand](https://github.com/rust-random/rand) |
| `rand_chacha` | `0.10.0` | `MIT OR Apache-2.0` | 运行时 | 确定性 ChaCha 随机数生成器，保证正交旋转矩阵可复现 | [rust-random/rand](https://github.com/rust-random/rand) |
| `bumpalo` | `3.20.3` | `MIT OR Apache-2.0` | 运行时 | 高速 Bump Arena 内存池，用于单次扫描期间的临时内存分配 | [fitzgen/bumpalo](https://github.com/fitzgen/bumpalo) |
| `arrayvec` | `0.7.8` | `MIT OR Apache-2.0` | 运行时 | 固定容量栈上向量容器 | [bluss/arrayvec](https://github.com/bluss/arrayvec) |
| `dary_heap` | `0.3.9` | `MIT OR Apache-2.0` | 运行时 | 缓存友好的 *d*-叉优先队列，用于候选集遍历 | [hanmertens/dary_heap](https://github.com/hanmertens/dary_heap) |
| `min-max-heap` | `1.3.0` | `MIT OR Apache-2.0` | 运行时 | 双端最小-最大堆，用于 `vchordg` 有界波束搜索 | [tov/min-max-heap-rs](https://github.com/tov/min-max-heap-rs) |
| `wyhash` | `0.6.0` | `MIT OR Apache-2.0` | 运行时 | 高速非加密哈希算法，用于图遍历已访问顶点去重 | [eldruin/wyhash-rs](https://github.com/eldruin/wyhash-rs) |
| `pin-project` | `1.1.13` | `Apache-2.0 OR MIT` | 运行时 | 面向有状态索引扫描迭代器的安全 Pin 投影宏 | [taiki-e/pin-project](https://github.com/taiki-e/pin-project) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | 运行时 | 索引 `options` 参数结构化反序列化框架 | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | 运行时 | `vchordrq` 与 `vchordg` 索引构建选项的 TOML 解析器 | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | 运行时 | 索引配置参数的范围与合法性校验 | [Keats/validator](https://github.com/Keats/validator) |
| `humansize` | `2.1.3` | `MIT OR Apache-2.0` | 运行时 | 字节体积的人类可读格式化输出 | [LeopoldArkham/humansize](https://github.com/LeopoldArkham/humansize) |
| `paste` | `1.0.15` | `MIT OR Apache-2.0` | 宏 | 标识符拼接宏，用于生成多类型距离操作符绑定 | [dtolnay/paste](https://github.com/dtolnay/paste) |
| `seq-macro` | `0.3.6` | `MIT OR Apache-2.0` | 宏 | 编译期循环展开宏，用于 SIMD 内核生成 | [dtolnay/seq-macro](https://github.com/dtolnay/seq-macro) |
| `proc-macro2` / `quote` / `syn` | `1.0.107` / `1.0.47` / `3.0.9` | `MIT OR Apache-2.0` | 过程宏 | `simd_macros` 语法树解析与代码生成 | [dtolnay/syn](https://github.com/dtolnay/syn) |
| `clap` / `object` / `serde_json` / `target-tuple` | `4.6.7` / `0.40.0` / `1.0.154` / `1.0.2` | `MIT OR Apache-2.0` | 构建 (`xtask`) | 构建命令行解析、ELF/Mach-O 符号检查与 SQL 实体图生成（`pgrx-sql-entity-graph 0.19.3`） | [clap-rs/clap](https://github.com/clap-rs/clap) |
{.wide .expand}

---

## 2 · `vchord_bm25` (`pgsty/vchord_bm25`) {#vchord_bm25}

**`vchord_bm25`** 是独立编译的 Rust/pgrx 扩展（`cdylib`），在 PostgreSQL 内实现原生 Okapi BM25 相关性评分与 Block-WeakAnd（`WAND`）倒排索引扫描。它没有强制的外部扩展运行时依赖，既可直接搭配 PostgreSQL 原生 `tsvector` 使用，也可配合 [`pg_tokenizer`](/zh/docs/tokenizer/) 使用。

### 2.1 Workspace 内部 Crate 清单 (`vchord_bm25`) {#vchord_bm25-workspace}

| **Crate 名称** | **目录路径** | **许可证** | **模块职责说明** |
|:---|:---|:---:|:---|
| `vchord_bm25` | `/` | `AGPL-3.0-only` | PostgreSQL 扩展入口（`pgrx`）、`bm25` 索引访问方法、`bm25vector`/`bm25query` 类型、`<&>` 操作符、GUC 参数与规划器代价估计钩子 |
| `bm25` | `crates/bm25` | `AGPL-3.0-only` | Block-WeakAnd（`WAND`）Top-K 查询执行器、差分/位打包倒排链压缩、段构建器与外部排序 I/O |
| `score` | `crates/score` | `AGPL-3.0-only` | Okapi BM25 评分核心（`k1 = 1.2`、`b = 0.75`）与文档长度量化归一化查表 |
| `index` | `crates/index` | `AGPL-3.0-only` | PostgreSQL 关系页面管理、跳转页（Jump Pages）与 MVCC 安全缓冲区锁控制 |
| `simd` | `crates/simd` | `AGPL-3.0-only` | SIMD 位打包（Bit-packing）与向量化倒排链解码（`x86_64` AVX2/AVX-512、`aarch64` NEON 与标量回退） |
| `simd_macros` | `crates/simd_macros` | `AGPL-3.0-only` | 多架构 SIMD 分发过程宏 |
| `always_equal` | `crates/always_equal` | `AGPL-3.0-only` | Top-K 最小堆候选集比较包装器 |
| `xtask` | `crates/xtask` | `AGPL-3.0-only` | 构建驱动工具：编译扩展、校验 SQL 模式一致性并生成 `build/` 制品 |
{.wide .expand}

### 2.2 直接第三方依赖清单 (`vchord_bm25`) {#vchord_bm25-dependencies}

| **Crate 名称** | **锁定版本** | **SPDX 许可证** | **作用范围** | **功能用途** | **上游仓库** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | 运行时 | PostgreSQL 扩展 Rust 开发框架（支持 `pg14`–`pg19` 绑定） | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | 运行时 | PostgreSQL 服务端头文件与内核函数的底层 FFI 绑定 | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `blake3` | `1.8.7` | `CC0-1.0 OR Apache-2.0 OR Apache-2.0 WITH LLVM-exception` | 运行时 | 高速哈希计算，用于词项哈希与段数据完整性校验 | [BLAKE3-team/BLAKE3](https://github.com/BLAKE3-team/BLAKE3) |
| `memmap2` | `0.9.12` | `MIT OR Apache-2.0` | 运行时 | 跨平台内存映射文件 I/O，用于大规模索引构建时的外部归并排序 | [RazrFalcon/memmap2-rs](https://github.com/RazrFalcon/memmap2-rs) |
| `mimalloc` | `0.1.52` | `MIT` | 运行时 (`x86_64`/`aarch64`) | Linux 与 macOS 平台高性能内存分配器（`libmimalloc-sys 0.1.49`，启用 `local_dynamic_tls`） | [purpleprotocol/mimalloc_rust](https://github.com/purpleprotocol/mimalloc_rust) |
| `zerocopy` | `0.8.63` | `BSD-2-Clause OR Apache-2.0 OR MIT` | 运行时 (`derive`, `simd`) | 倒排链数据块与 BM25 元数据页的零拷贝序列化 | [google/zerocopy](https://github.com/google/zerocopy) |
| `getrandom` | `0.4.3` | `MIT OR Apache-2.0` | 运行时 | 操作系统熵源接口，用于生成临时排序文件名 | [rust-random/getrandom](https://github.com/rust-random/getrandom) |
| `rand` | `0.10.3` | `MIT OR Apache-2.0` | 运行时 | 随机数生成工具 | [rust-random/rand](https://github.com/rust-random/rand) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | 运行时 | `USING bm25` 索引选项反序列化框架 | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | 运行时 | 索引配置选项的 TOML 解析器 | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | 运行时 | BM25 索引选项合法性校验 | [Keats/validator](https://github.com/Keats/validator) |
| `seq-macro` | `0.3.6` | `MIT OR Apache-2.0` | 宏 | 编译期循环展开宏，用于位打包内核 | [dtolnay/seq-macro](https://github.com/dtolnay/seq-macro) |
| `proc-macro2` / `quote` / `syn` | `1.0.107` / `1.0.47` / `3.0.9` | `MIT OR Apache-2.0` | 过程宏 | `simd_macros` 语法树解析与代码生成 | [dtolnay/syn](https://github.com/dtolnay/syn) |
| `clap` / `object` / `serde_json` / `target-tuple` | `4.6.7` / `0.40.0` / `1.0.154` / `1.0.2` | `MIT OR Apache-2.0` | 构建 (`xtask`) | 构建命令行解析、符号检查与 SQL 模式一致性校验（`pgrx-sql-entity-graph 0.19.3`） | [clap-rs/clap](https://github.com/clap-rs/clap) |
{.wide .expand}

---

## 3 · `pg_tokenizer` (`pgsty/pg_tokenizer`) {#pg_tokenizer}

**`pg_tokenizer`** 是单 Crate 结构的 Rust/pgrx 扩展（`cdylib`，采用 `Apache-2.0` 许可证），在 PostgreSQL 数据库内提供多语言文本分析流水线、预分词器、词干提取、停用词/同义词过滤以及整数词元 ID（Token ID）编码。

### 3.1 直接依赖与关键原生绑定 (`pg_tokenizer`) {#pg_tokenizer-dependencies}

| **Crate 名称** | **锁定版本** | **SPDX 许可证** | **作用范围** | **功能用途** | **上游仓库** |
|:---|:---:|:---|:---:|:---|:---|
| `pgrx` | `0.19.3` | `MIT` | 运行时 | PostgreSQL 扩展 Rust 开发框架（支持 `pg14`–`pg19` 绑定） | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `pgrx-pg-sys` | `0.19.3` | `MIT` | 运行时 | PostgreSQL 服务端头文件与内核函数的底层 FFI 绑定 | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
| `tokenizers` | `0.23.2` | `Apache-2.0` | 运行时 | HuggingFace 高速分词引擎（支持 WordPiece、BPE、Unigram 模型） | [huggingface/tokenizers](https://github.com/huggingface/tokenizers) |
| `tocken` | `0.1.0` | `Apache-2.0` | 运行时 | 内置预训练词表分词器（`bert_base_uncased`、`wiki_tocken`、`gemma2b`、`llmlingua2`） | [kemingy/tocken](https://github.com/kemingy/tocken) |
| `jieba-rs` | `0.11.0` | `MIT` | 运行时 | 结巴中文分词引擎（支持精确/全模式/搜索引擎模式、HMM 新词发现与自定义词典） | [messense/jieba-rs](https://github.com/messense/jieba-rs) |
| `lindera` | `6.2.0` | `MIT` | 运行时 | 日文/中日韩形态学分析与分词框架（`lindera` 模型与预分词器） | [lindera/lindera](https://github.com/lindera/lindera) |
| `lindera-analysis` | `6.2.0` | `MIT` | 运行时 | 字符过滤器、词元过滤器及内嵌 IPADIC / UniDic / ko-dic / CC-CEDICT 词典支持 | [lindera/lindera](https://github.com/lindera/lindera) |
| `rust-stemmers` | `1.2.1` | `MIT OR BSD-3-Clause` | 运行时 | Snowball 多语言词干提取算法，支持 30 种语言（Git 标签 `v1.2.1`，提交 `61e8ea11`） | [pgsty/rust-stemmers](https://github.com/pgsty/rust-stemmers) |
| `unicode-segmentation` | `1.13.3` | `MIT OR Apache-2.0` | 运行时 | Unicode 标准附件 #29（`UAX #29`）词边界切分（`unicode` 预分词器） | [unicode-rs/unicode-segmentation](https://github.com/unicode-rs/unicode-segmentation) |
| `unicode-normalization` | `0.1.26` | `(MIT OR Apache-2.0) AND Unicode-3.0` | 运行时 | Unicode NFC / NFD / NFKC / NFKD 字符规范化过滤器 | [unicode-rs/unicode-normalization](https://github.com/unicode-rs/unicode-normalization) |
| `regex` | `1.13.1` | `MIT OR Apache-2.0` | 运行时 | 基于有限自动机的正则表达式引擎，用于正则分词与模式替换过滤 | [rust-lang/regex](https://github.com/rust-lang/regex) |
| `dashmap` | `6.2.1` | `MIT` | 运行时 | 高并发分片哈希表，用于数据库会话内词表模型与分析器缓存 | [xacrimon/dashmap](https://github.com/xacrimon/dashmap) |
| `serde` | `1.0.229` | `MIT OR Apache-2.0` | 运行时 | TOML / JSON 流水线与词表模型配置的序列化框架 | [serde-rs/serde](https://github.com/serde-rs/serde) |
| `serde_json` | `1.0.154` | `MIT OR Apache-2.0` | 运行时 | HuggingFace 分词器模型 JSON 规范解析器 | [serde-rs/json](https://github.com/serde-rs/json) |
| `toml` | `1.1.8` | `MIT OR Apache-2.0` | 运行时 | `create_tokenizer` / `create_text_analyzer` 配置块的 TOML 解析器 | [toml-rs/toml](https://github.com/toml-rs/toml) |
| `validator` | `0.21.0` | `MIT` | 运行时 | 分析器与模型配置结构体的声明式校验 | [Keats/validator](https://github.com/Keats/validator) |
| `anyhow` | `1.0.104` | `MIT OR Apache-2.0` | 运行时 | 分词流水线各阶段的上下文错误处理与传递 | [dtolnay/anyhow](https://github.com/dtolnay/anyhow) |
| `onig_sys` | `69.9.3` | `MIT` | 传递依赖 (`tokenizers`) | HuggingFace `tokenizers` 使用的 Oniguruma 正则表达式 C 库绑定 | [iwillspeak/rust-onig](https://github.com/iwillspeak/rust-onig) |
| `esaxx-rs` | `0.1.10` | `Apache-2.0` | 传递依赖 (`tokenizers`) | Unigram 词表训练使用的增强后缀数组 C++ 库绑定 | [Narsil/esaxx-rs](https://github.com/Narsil/esaxx-rs) |
| `zstd-sys` | `2.1.2+zstd.1.5.7` | `BSD-3-Clause` | 传递依赖 (`lindera`) | 形态学压缩词典使用的 Zstandard C 库绑定 | [gyscos/zstd-rs](https://github.com/gyscos/zstd-rs) |
| `pgrx-tests` | `0.19.3` | `MIT` | 开发 / 测试 | `cargo pgrx test` 集成测试框架 | [pgcentralfoundation/pgrx](https://github.com/pgcentralfoundation/pgrx) |
{.wide .expand}

---

## 4 · 许可证合规审计与 SBOM 导出验证 {#verification}

`vchord` 与 `vchord_bm25` 使用 [`cargo-deny`](https://embarkstudios.github.io/cargo-deny/)（`deny.toml`）定义依赖项许可证白名单。`pg_tokenizer` 当前没有 `deny.toml` 或 cargo-deny CI 门禁；本页清单不等同于该仓库已通过这项审计。已有白名单包括：

- `MIT`
- `Apache-2.0` 与 `Apache-2.0 WITH LLVM-exception`
- `BSD-2-Clause` 与 `BSD-3-Clause`
- `ISC`
- `Unicode-3.0` 与 `Unicode-DFS-2016`
- `CC0-1.0` 与 `Zlib`

您可以在任意扩展源码目录下直接运行以下命令，审计完整的传递依赖树或导出机器可读的 CycloneDX / SPDX JSON 格式 SBOM 文件：

```bash
# 1. 使用 cargo-deny 校验许可证白名单与安全漏洞公告
# 适用于包含 deny.toml 的仓库
cargo deny check

# 2. 查看完整锁定依赖树及其 SPDX 许可证
cargo tree --format "{p} ({l})"

# 3. 导出标准 CycloneDX 1.4 JSON 格式的软件物料清单 (SBOM)
cargo sbom --output-format cyclone_dx_json_1_4 > sbom.cdx.json
```
