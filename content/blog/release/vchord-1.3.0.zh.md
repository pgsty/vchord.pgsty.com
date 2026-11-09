---
title: "vchord 1.3.0：恢复安全与运维加固"
date: 2026-11-09
description: "vchord 1.3.0 加固索引页发布和诊断数据访问，同时明确近似搜索的取舍。"
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

**vchord 1.3.0** 延续 PGSTY 对 PostgreSQL 14–18 的维护版本线。`vchordrq.epsilon` 默认值保持 `1.9`；本版本重点处理恢复顺序、诊断数据权限和升级后的运维行为。

## 变更

| 领域 | 变更 |
| :--- | :--- |
| WAL 发布 | 新的 `vchordrq` 向量页和 `vchordg` 顶点页会与指向它的入口链接写入同一条 Generic WAL 记录，然后才可能被空闲空间提示暴露。不会为每页增加 WAL flush，也不改变磁盘格式。 |
| 图索引维护 | `vchordg` 保留有界的局部 `VACUUM` 修复。任意删除模式仍可能降低 ANN 召回率；需要重建时请测量召回并使用 `REINDEX INDEX CONCURRENTLY`。完整的维护页回收仍延期。 |
| 查询采样 | 采样默认关闭。读取采样需要超级用户或 `pg_read_all_stats`；表所有者和 `SELECT` 权限不足以授权。预热继续使用原有的表权限检查。采样是本机诊断数据，不随 PostgreSQL 事务回滚，也不是审计日志。 |
| Recorder 清理 | 普通事务提交后，索引和数据库删除会尽力清理样本。回滚和 SAVEPOINT 回滚会保留样本。`PREPARE TRANSACTION` 会保留样本；`COMMIT PREPARED` 或提交后崩溃可能留下不可达诊断数据。`DROP INDEX CONCURRENTLY` 即使后来取消，也可能已经在内部提交时清理样本。并发重建会开始新的采样身份。 |
| 外部构建 | `build.external.table` 必须写成 `schema.table`。已有未限定索引仍可查询，但在 `REINDEX`、`TRUNCATE`、`VACUUM FULL`、`CLUSTER`、相关类型变更和转储恢复等会重建或替换索引的操作前，必须先更新配置。 |
| RaBitQ 类型修饰符 | 在完整 typmod 设计实现前，文本和二进制输入保持 1.2.0 行为：`rabitq4(n)` 和 `rabitq8(n)` 的输入不强制检查 `n`。这样可以保证 `INSERT` 已接受的数据可通过 `pg_dump` 和逻辑输入恢复；vchord 索引仍会校验维度。 |
| 距离与数值边界 | RaBitQ 余弦距离改为 `1 - cosine`；零方向或非有限方向没有定义，余弦索引会跳过它们。`halfvec` 溢出和无效反量化现在报错。包含相关旧向量的余弦索引需要重建。 |
| 插入冲突 | `vchordg` backlink 重试耗尽后以 `40001` 中止事务，应用应重试整个事务。 |

## 升级说明

升级前检查外部构建配置：

```sql
SELECT c.oid::regclass AS index_name, o.option_value
FROM pg_class AS c
JOIN pg_am AS am ON am.oid = c.relam
CROSS JOIN LATERAL pg_options_to_table(c.reloptions) AS o
WHERE am.amname = 'vchordrq'
  AND o.option_name = 'options'
  AND o.option_value LIKE '%external%';
```

请检查点分键和 `[build.external]` 两种 TOML 写法。将未限定的值更新为限定名称，并保留 `options` 中的其他设置，例如：

```sql
ALTER INDEX my_index SET (options = $$
[build.external]
table = 'public.centroids'
$$);
```

如果旧余弦索引包含零范数或其他无效方向的向量，请重建索引。目录升级不会重写索引页。请检查 `vchordrq_sampled_queries` 和采样函数的访问权限：这些接口有意只向统计管理员暴露查询向量。

详细运维说明见[外部构建](/zh/docs/vchord/usage/external-build/)、[查询采样](/zh/docs/vchord/usage/measure-recall/#query-sampling)、[图索引维护](/zh/docs/vchord/usage/graph-index/#maintenance)和[量化类型](/zh/docs/vchord/usage/quantization-types/)文档。
