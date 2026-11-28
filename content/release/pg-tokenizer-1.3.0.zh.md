---
title: "pg_tokenizer 1.3.0：主库零 SPI 缓存、原生 C TSVector 与全链路加速"
date: 2026-11-25
description: "pg_tokenizer 1.3.0 引入主库共享屏障免 SPI 缓存复查，以原生 C 实现 analyze_to_tsvector 与 tokenize_to_tsvector，优化自定义词表触发器与分析管线，面向 PostgreSQL 15–19。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
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

**pg_tokenizer 1.3.0** 是 [`pgsty/pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) 面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`）公开发布的最新版本，在 [1.2.0](/zh/release/pg-tokenizer-1.2.0/) 基础上大幅降低了主库高频读取、自定义词表写入以及 `tsvector` 转换的开销。本版本消除了主库每次调用的 SPI 缓存校验，将 `tsvector` 封装与自定义词表触发器重写为原生 `LANGUAGE c` 函数，并全面精简了文本分析与分词管线。

面向 PostgreSQL 15–19（`x86_64` 与 `aarch64`，基于 Ubuntu 24.04 构建并内置 IPADIC、要求 `glibc >= 2.39`）的 `.deb` 与 `.zip` 二进制包、PGXN 源码包（`pg_tokenizer-1.3.0.zip`）与 `SHA256SUMS` 已发布于 [GitHub Release](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0)。

## 1.3.0 变更概览 {#changes}

| 领域 | 变更 |
| :--- | :--- |
| 主库定义缓存快路径 | 在已是最新状态的主库上，重复读取通过共享失效纪元与 `FullTransactionId` 屏障直接复用已校验缓存，跳过 SPI 查询、`pg_depend` 检查以及命令 ID 标记。语句级 `BEFORE`/`AFTER` 触发器负责标记本地修改并发布已提交的定义变更；旧快照、导入快照、物理备库、主备切换以及尚未更新 SQL 的 `1.2.0` 库自动回退到基于快照的 `definition_version` 路径；无关事务的 `ROLLBACK` / `ROLLBACK TO SAVEPOINT` 保留主库已校验缓存。 |
| 原生 C `tsvector` 构建 | `analyze_to_tsvector` 与 `tokenize_to_tsvector` 改为原生 `LANGUAGE c` 函数，直接构造 PostgreSQL `TSVectorData` 变长结构，免去 SQL 包装调用、文本转义、`int4[]::text[]` 强转及 `tsvectorin` 二次解析，同时严格保持相同的词素排序、2,046 字节单词上限、256 位置上限、16,383 位置截断与 1,048,575 字节 `MAXSTRPOS` 校验。`_tokens_to_tsvector_text` 与 `_analyze_to_tsvector_text` 继续保留以兼容旧调用。 |
| 自定义词表触发器 | `custom_model_insert_trigger` 改为原生 `LANGUAGE c` 实现。写入端通过可命中唯一索引的参数化查询检查去重候选词，已有词条不再消耗新序列 ID；按模型粒度的事务级咨询锁串行化并发新词插入，两个独立触发器继续各自评估行谓词；普通分词读取调用方快照；目标列赋值遵循 PostgreSQL 类型转换与 SQL `tokenize` 函数的权限和设置。 |
| 分析与分词管线精简 | 单次调用仅读取一次 GUC 预算上限，消除中间 `Vec<&str>` 分配与冗余后置预算遍历，空/恒等分析器免去 `String` 拷贝并直接融合输出 `Vec<i32>`。轻量级过滤器中断检查节流至每 1,024 词元一次；非 ASCII `to_lowercase` 改为单遍处理（未变化的中日韩文本零分配，保留希腊语词尾 sigma）；Unicode 规范化（`nfc`/`nfd`/`nfkc`/`nfkd`）增加纯 ASCII 零分配快路径；`ngram` 批量处理增加 ASCII 快路径并复用偏移缓冲区；`pg_dict` 消除逐词临时向量与 `CString` 分配。 |
| Hugging Face 校验 | `create_huggingface_model` 导入时在词表、附加词元与后处理特殊词元之外，同步校验 `padding.pad_id <= 2147483647`。 |
| 打包与验证 | 原始 pgrx 产物、ZIP 与 Debian 包均完整包含 `1.2.0 → 1.3.0` 升级脚本；CI 在添加历史安装脚本做升级测试前，先核验安装包内迁移脚本与发布源码一致。 |
{.wide .expand}

## 二进制兼容性与最低 PostgreSQL 小版本 {#compatibility}

> [!IMPORTANT] 重启前请核对 PostgreSQL 小版本
> 链接了较新 PostgreSQL 元组头函数的 GitHub 发布二进制包，要求对应大版本至少为 **PostgreSQL 15.20、16.16、17.12、18.7 或 19.0+**。在更低小版本上，`pg_tokenizer.so` 将加载失败，且只要仍在 `shared_preload_libraries` 中，PostgreSQL 会拒绝启动。`.deb` 已将该要求写入软件包依赖；使用 `.zip` 时，替换文件前请查看 `pg_tokenizer.control` 最后一行（`unzip -p <archive>.zip pg_tokenizer.control | tail -n 1`）。请先升级 PostgreSQL 小版本，或使用本机 `pg_config` 从源码编译。

GitHub `.deb` 与 `.zip` 二进制包基于 Ubuntu 24.04 构建（要求 `glibc >= 2.39`，适用于 Ubuntu 24.04+ 与 Debian 13+）并内置 IPADIC。EL 8/9/10、Debian 12 或 Ubuntu 22.04 请安装原生 [Pigsty 软件包](/zh/docs/tokenizer/installation/#pigsty)（日文/韩文切分需外置 Lindera 7 format-v3 词典）或从源码编译。

## 升级到 1.3.0 {#upgrade-notes}

1. **安装并重启**：按[安装指南](/zh/docs/tokenizer/installation/)在主库和所有物理备库安装 `1.3.0` 动态库与 SQL 文件，然后逐节点重启 PostgreSQL。
1. **在主库更新各数据库扩展**：

   ```sql
   ALTER EXTENSION pg_tokenizer UPDATE;
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

- **从 `1.2.0` 滚动升级**：在执行 `ALTER EXTENSION pg_tokenizer UPDATE;` 之前，加载了 `1.3.0` 动态库的后端可安全通过 `definition_version` 路径继续服务 `1.2.0` SQL 数据库；执行更新后自动启用主库缓存快路径与原生 `tsvector` 函数。现有目录定义、自定义词表 ID、视图与表触发器全部原地保留，无需重算数据。
- **从 `1.1.0` 及更早版本跨版本升级**：`ALTER EXTENSION pg_tokenizer UPDATE;` 支持完整升级链 `0.1.0 → 0.1.1 → 1.0.0 → 1.1.0 → 1.2.0 → 1.3.0`。跨版本前请对照[升级说明](/zh/docs/tokenizer/installation/#upgrading)核对 [1.2.0](/zh/release/pg-tokenizer-1.2.0/)（PostgreSQL 15–19 与 Lindera 7 format v3）及 [1.1.0](/zh/release/pg-tokenizer-1.1.0/)（`READ COMMITTED` 事务与 `tokenizer_data` 模式）的额外步骤。
- **绕过触发器的维护操作**：若超级用户在禁用触发器或 `session_replication_role = replica` 状态下直接修改了 `tokenizer_catalog` 表，走快路径的主库后端不会自动感知变更。维护完成后应重新启用触发器并恢复 `session_replication_role = origin`，再对任一定义表执行一次已提交的空更新以推进屏障，具体步骤见 [Backend-Local Definition Caches](https://github.com/pgsty/pg_tokenizer/blob/v1.3.0/docs/07-limitation.md#backend-local-definition-caches)。
