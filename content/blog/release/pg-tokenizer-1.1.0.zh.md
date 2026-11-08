---
title: "pg_tokenizer 1.1.0：缓存一致性与分析资源限制"
date: 2026-11-08
description: "pg_tokenizer 1.1.0 新增通过 WAL 复制的定义缓存失效机制，修复两阶段事务缓存清理，分离运行时词表权限，并提供可配置的文本分析资源预算。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com/zh/)"
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

**pg_tokenizer 1.1.0** 改进了定义缓存一致性、文本分析正确性与配置权限。支持 PostgreSQL 14–18，保留现有的 `INT[]` 分词接口与原生 `tsvector` 接口。

> [!NOTE] 发布范围
> 本版本以**新机器全新安装**为验收范围。升级兼容、按模式设置的默认权限迁移、跨升级旧快照以及构建前置检查失败后遗留的 staging manifest，不在本轮发布验收范围内。已有升级脚本继续保留，需单独评估。

> [!NOTE] 扩展主页与发布链接
> - **GitHub Release**：[pg_tokenizer v1.1.0](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.1.0) · [完整变更](https://github.com/pgsty/pg_tokenizer/compare/v1.0.0...v1.1.0)
> - **文档**：[安装指南](/zh/docs/tokenizer/installation/) · [SQL 参考](/zh/docs/tokenizer/reference/) · [模型](/zh/docs/tokenizer/models/)
> - **源码**：[仓库](https://github.com/pgsty/pg_tokenizer) · [版本化发布说明](https://github.com/pgsty/pg_tokenizer/blob/v1.1.0/docs/release-notes/1.1.0.md)

GitHub Release 按草稿准备；草稿正式发布后，下载附件才会向公众开放。

## 定义缓存与两阶段事务 {#definition-caches}

定义缓存现在通过具有事务语义的目录版本号进行校验，版本号随 WAL 复制。分析器、分词器、模型、停用词与同义词查询使用同一个 SQL 快照读取版本号与定义。备库回放到相应提交、且查询取得合适快照后即可观察到变化；提升为主库后继续保持这一行为。

执行 `PREPARE TRANSACTION` 时，原连接现在会清空派生对象缓存与校验状态。这修复了一条具体故障路径：直接修改目录并将配置 X 加载进会话缓存，另一连接回滚该预备事务，随后另一个事务以相同版本号提交配置 Y。原连接现在能够重新加载 Y。回归测试确认，替换后的正则配置对 `Hello World` 返回 `{"H","W"}`，不会继续使用旧配置返回 `{"hello","world"}`。

只读事务仍可 prepare，定义变更 API 仍拒绝 PREPARE，普通事务提交保留正常缓存复用路径。直接修改目录会绕过 API 配置校验，仍属于管理员操作。

## 其他修改 {#changes}

| 方面 | 修改 |
| :--- | :--- |
| 运行时模式 | 词表及其序列位于 `tokenizer_data`，数据库拥有者无需取得 `tokenizer_catalog` 的 CREATE 权限。 |
| 并行查询 | 写目录的函数标记为 `PARALLEL UNSAFE`，只读分析保留 `PARALLEL SAFE`。 |
| PostgreSQL 词典 | 新建 `pg_dict` 定义保存带模式名的词典名称，后续调用者的 search_path 不会将它指向其他词典。 |
| Lindera 权限 | 加载词典文件需要超级用户或 `pg_read_server_files` 权限；配置匹配、已经加载或预加载的模型仍可复用。 |
| 自定义词表 | 长词元按 UTF-8 字符边界拆分；触发器输出遵循目标列的赋值语义。 |
| 原生全文检索 | 在转换为 `tsvector` 前聚合重复词素。 |
| Jieba | `full` 与 `precise` 使用对应的正确算法，默认 `search` 模式不变。 |
| 打包安装 | 修正共享库安装示例，提供兼容 PGXN 的源码归档，并验证实际 DEB 与 ZIP 制品。 |
{.wide .expand}

## 分析资源预算 {#analysis-budgets}

以下参数可在会话中设置，输入或输出超限时返回 SQLSTATE `54000`：

| 参数 | 默认值 |
| :--- | ---: |
| `pg_tokenizer.max_input_bytes` | 16 MiB |
| `pg_tokenizer.max_output_tokens` | 1,000,000 |
| `pg_tokenizer.max_output_bytes` | 64 MiB |
| `pg_tokenizer.max_piece_bytes` | 1 MiB |
{.wide .expand}

这些预算不构成第三方库内部的硬内存上限，也不保证取消延迟上限。应加载可信的模型配置，并在应用层限制文档大小。[Issue #13](https://github.com/pgsty/pg_tokenizer/issues/13) 继续跟踪这一限制；详细口径见[资源预算参考](/zh/docs/tokenizer/reference/#analysis-budgets)。

## 安装与软件包 {#installation}

GitHub DEB 与 ZIP 软件包覆盖 PostgreSQL 14–18，提供 x86_64/amd64 与 aarch64/arm64 两种架构，在 **Ubuntu 24.04** 上构建并内嵌 IPADIC。其他发行版应使用匹配的原生包或从源码构建。Pigsty 原生 RPM/DEB 包不内嵌 Lindera 词典，需要提供用 Lindera 6 编译的词典。

GitHub Release 同时提供源码包 `pg_tokenizer-1.1.0.zip`、对应的 SHA-256 文件，以及覆盖二进制包与源码包的 `SHA256SUMS`。准备该源码包不代表已经发布到 PGXN。

安装匹配文件后，将 `pg_tokenizer.so` 加入 `shared_preload_libraries`，保留已有条目并重启 PostgreSQL，然后执行：

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

结果为 `{hello,world}`。使用 pg_tokenizer 无需安装 `vchord` 或 `vchord_bm25`。包选择与服务器配置步骤见[安装指南](/zh/docs/tokenizer/installation/)。

若复用旧版本生成的持久化结果，需要注意：1.0.0 及更早版本的 Jieba `full` 与 `precise` 模式被互换。使用过这两种模式时，应重新生成结果并重建相关索引。

## 验证 {#validation}

创建 Draft Release 前，标签对应提交必须通过 PostgreSQL 14–18 与两种 Linux 架构的 Check 工作流。每个发布构建会安装生成的 DEB，核对安装内容与 ZIP 一致，并针对包内共享库运行 SQLLogicTest、集成、预加载及物理备库测试。

两阶段事务回归还在 macOS arm64 / PostgreSQL 18.6 上验证了修复前后差异：同一测试在未修复基线上失败、修复后通过，覆盖版本号复用和正常的 `COMMIT PREPARED`。
