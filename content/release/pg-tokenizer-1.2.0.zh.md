---
title: "pg_tokenizer 1.2.0：PostgreSQL 19、Lindera 7 与预加载加固"
date: 2026-11-23
description: "pg_tokenizer 1.2.0 升级至 pgrx 0.20.0 与 Lindera 7.0.0 支持 PostgreSQL 15–19，消除过滤器逐词分配，加固触发器异常清理与原子预加载文件，并更新 toml、regex 与 url。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
authors:
  - "vonng"
release_url: "https://github.com/pgsty/pg_tokenizer/releases/tag/v1.2.0"
upstream_source: ""
upstream_link: ""
tags:
  - "pg_tokenizer"
aliases: [/blog/release/pg-tokenizer-1.2.0/]
---

**pg_tokenizer 1.2.0** 将 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 升级至 `pgrx 0.20.0` 与 Lindera `7.0.0`，支持 `x86_64` 与 `aarch64` 上的 **PostgreSQL 15–19**（不再支持 PostgreSQL 14）。本版本同时消除了文本过滤器的逐词内存分配，加固了自定义模型触发器异常清理与预加载文件处理，并更新了核心解析与安全依赖。

> [!NOTE] 已由 1.3.0 替代的源码标签里程碑
> `v1.2.0` 源码标签（`https://github.com/pgsty/pg_tokenizer/tree/v1.2.0`）已由正式发布的 [**pg_tokenizer 1.3.0**](/zh/release/pg-tokenizer-1.3.0/) 替代；1.3.0 进一步引入主库零 SPI 定义缓存快路径、原生 C 语言 `tsvector` 构建器以及更快的自定义词表写入。获取 GitHub 预编译包与生产部署请直接使用 [`pg_tokenizer 1.3.0`](/zh/release/pg-tokenizer-1.3.0/)。

## 1.2.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| PostgreSQL 15–19 与 `pgrx 0.20.0` | 在源码构建、CI 与打包矩阵中新增 PostgreSQL 19，移除 PostgreSQL 14。CI 与发布包使用 Rust `1.100.0`（源码构建要求 Rust `1.99.1+` 及匹配的 Clang/libclang/LLVM）。修复 `tools/pgxn.py` 解析预发布版本串（如 `PostgreSQL 19rc1`、`PostgreSQL 19beta2`）的主版本识别。 |
| Lindera `7.0.0` | 升级至 Lindera `7.0.0`。外部系统词典须升级为 **format v3**。内置 IPADIC 沿用 `2025-09-20` 词典源，但构建器与切分规则变更会改变少量词条 ID；现有模型配置、用户词典 ID 段（`1073741824+`）及未登录词省略规则保持不变。 |
| 文本分析与内存优化 | `to_lowercase` 对不含大写字母的 ASCII 输入直接原地返回，转换大写 ASCII 时每 1,024 字节检查一次取消中断。Rust `1.100.0` 提供 Unicode 18.0 大小写与字母数字表（保留希腊语词尾 sigma 等上下文规则）。`stopwords`、`synonym`、`skip_non_alphanumeric` 原地复用输入向量，不再为每个词元新建结果向量。`tsvector` 构造以 16 位保存位置。 |
| 触发器与快照安全 | 自定义模型目标列类型转换失败（如 `varchar(n)` 长度超限、域 `CHECK`/`NOT NULL` 违约）时，恢复调用方 `CurrentMemoryContext` 并在 `ExecutorState::drop` 中保护进程/事务退出路径。缓存校验在读取快照前先确认存在活动快照。 |
| 原子预加载文件 | 并发调用 `add_preload_model` 与 `remove_preload_model` 每次原子发布或删除单个完整条目。启动时跳过非法名称、符号链接、特殊文件与损坏配置并记录警告。`list_preload_models()` 按排序返回名称，目录缺失时返回空数组。 |
| 解析器与安全依赖 | 升级 `toml` 至 `1.2.2`（修复畸形 TOML 栈溢出）、`regex` 至 `1.13.2`（修正共享重复前缀分支的匹配边界）、`url` 至 `2.5.9` 与 `form_urlencoded` 至 `1.2.3`（[`RUSTSEC-2026-0592`](https://rustsec.org/advisories/RUSTSEC-2026-0592.html)）。CI 增加安装 SQL 一致性、全升级链导出 C 符号与 PostgreSQL 日志健康自动化检查。 |
{.wide .expand}

## 分词输出变化 {#token-changes}

`1.2.0` 中有三处上游变更可能使相同输入产生不同的分词结果：

- **Lindera 7.0.0**：外部 format-v3 词典与内置 IPADIC 均采用 Lindera 7 构建器与切分规则。默认 IPADIC 模型对 `Google が 新しい` 的输出由 `{19678,236490}` 变为 `{19679,236490}`，`龘々` 由 `{}` 变为 `{103}`（`関西国際空港限定` 仍为 `{372982,374178}`）。
- **`regex 1.13.2`**：修正多分支共享变长前缀时的匹配边界。例如预分词正则 `id[0-9]*[0-9]|id[0-9]*-` 处理 `id42-` 时现在返回 `id42`（1.1.0 返回 `id42-`）。
- **Unicode 18.0（Rust 1.100.0）**：用 Rust `1.100.0` 构建时，`to_lowercase` 与 `skip_non_alphanumeric` 采用 Unicode 18.0（Rust `1.99.1` 为 Unicode 17.0），例如 `U+A7DD` 会转为小写 `U+0277` 并作为字母数字词元保留。

共享数据的所有节点应保持编译器与词典构建一致。若上述变化影响业务流水线，切换到新分词器前请基于原始文本重新计算已存储的词元数组与 `tsvector` 列。

## 从 1.1.0 升级 {#upgrade-notes}

1. **先升级 PostgreSQL 14**：安装 `1.2.0` 及以上版本前须先将集群升级至 PostgreSQL 15–19。
1. **准备 Lindera format-v3 词典**：若有模型使用磁盘上的外部 Lindera 系统词典，先在所有节点准备好 Lindera 7 构建的 format-v3 目录，在 PostgreSQL 停止期间替换原目录。（若仍保留 v2 目录，启动时会跳过预加载并记警告，后端加载报 SQLSTATE `22023`。）
1. **检查预加载路径**：`$PGDATA/pg_tokenizer/preload_models` 下原有的常规文件可原地沿用；若目录本身或条目为符号链接，重启前须替换为真实目录与普通文件。
1. **安装、重启并更新扩展**：在主库与全部备库安装 `1.2.0` 动态库与 SQL 文件，逐节点重启 PostgreSQL，然后在每个数据库中执行：

   ```sql
   ALTER EXTENSION pg_tokenizer UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

SQL 签名、目录定义以及 `tokenizer_data` 中的自定义词表 ID 均原地保留。详细步骤见[安装与升级](/zh/docs/tokenizer/installation/#upgrading)和[预加载模型](/zh/docs/tokenizer/models/#preload)。
