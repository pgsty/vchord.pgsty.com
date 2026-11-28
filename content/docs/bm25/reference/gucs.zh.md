---
title: "参数与索引选项"
linkTitle: "参数"
description: "bm25.* 参数、bm25 索引的存储选项，以及两者同时设置时以谁为准。"
weight: 20
icon: fa-solid fa-sliders
---

查询行为由三个 `bm25.*` 参数控制，其中两个也可以按索引设置；构建与维护行为只由索引选项控制。这些值调节的是哪种扫描，见[查询](/zh/docs/bm25/usage/querying/#how-a-query-runs)。

## 参数 {#settings}

任何用户都可以用 `SET` 修改这些参数；默认值可以用 `ALTER ROLE ... SET`、`ALTER DATABASE ... SET` 或 `postgresql.conf` 设置。在 `SET` 中要给 `"bm25.limit"` 加引号，因为 `LIMIT` 是保留字。

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `bm25.enable_scan` | boolean | `on` | 允许规划器使用 bm25 索引扫描。关闭后，PostgreSQL 给每一行打分再排序，分数完全相同；可在测试时作为参照。 |
| `bm25.limit` | integer | `100` | 索引扫描第一批的行数，取值 `0` 到 `65535`；`0` 表示 100。之后每一批翻倍。批次不小于 `LIMIT + OFFSET` 时不需要第二轮；批次越大，能跳过的倒排块越少。见[确定批次大小](/zh/docs/bm25/usage/querying/#batch-size)。 |
| `bm25.prefilter` | boolean | `off` | 候选行进入批次之前，先检查行可见性和 `WHERE` 子句。条件选择性高时更快；大部分行都能通过时更慢，因为每个有竞争力的候选都要读一次表。见[预过滤](/zh/docs/bm25/usage/filtering/#prefilter)。 |
{.fields meta="type default"}

## 优先级 {#precedence}

`bm25.limit` 和 `bm25.prefilter` 都有作用相同的索引选项：`limit` 和 `prefilter`。参数一旦在任何地方被赋值，无论是 `postgresql.conf`、`ALTER DATABASE`、`ALTER ROLE`、连接参数还是 `SET`，哪怕赋的就是默认值，它都会作用于所有索引。只有在哪里都没有设置它时，各索引才使用自己的选项。`RESET` 恢复的是配置中设定的值，不一定回到索引选项。

把调好的值存在索引上，并保持参数未设置，每个索引就能各用各的。

## 索引选项 {#index-options}

用 `CREATE INDEX ... WITH (...)` 或 `ALTER INDEX ... SET (...)` 设置，用 `ALTER INDEX ... RESET (...)` 移除。

| 选项 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `options` | TOML 字符串 | `k1 = 1.2` 与 `b = 0.75` | BM25 参数。`k1` 取值 1.2 到 2.0，决定重复出现的词加分多快饱和；`b` 取值 0 到 1，决定对长文档的惩罚力度。只在建索引时读取：修改后要 `REINDEX`。见[选择 k1 和 b](/zh/docs/bm25/usage/indexing/#scoring-parameters)。 |
| `limit` | integer | `100` | 本索引第一批的大小，取值 `0` 到 `65535`；`0` 表示 100。在 `bm25.limit` 未设置时生效。 |
| `prefilter` | boolean | `off` | 本索引是否预过滤。在 `bm25.prefilter` 未设置时生效。 |
| `maintenance_min_rows` | integer | `1000` | `VACUUM` 合并增长段前，增长段至少要有的行数，取值 `0` 到 `2147483647`。 |
| `maintenance_scale_factor` | real | `0.1` | 取值 `0` 到 `1`。增长段达到已合并行数的这一比例（且满足 `maintenance_min_rows`），或已删除的行达到全部行数的这一比例时，`VACUUM` 执行合并。值越小合并越频繁：查询更快、统计信息更新鲜，代价是 `VACUUM` 的工作量更大。 |
| `shared_corpus_stats` | boolean | `off` | 允许受行级安全约束的角色基于整个索引的统计信息打分。这样一来，分数会透露各个词在这些角色无权读取的行中有多常见。见[权限与行级安全](/zh/docs/bm25/usage/filtering/#access-control)。[降级](/zh/docs/bm25/reference/migration/#downgrade)到 1.3.0 之前的版本前要先重置。 |
{.fields meta="type default"}

`options` 的值是 TOML，每行一个键：

```sql
CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops)
WITH (options = $$
k1 = 1.5
b = 0.6
$$, limit = 200);
```

用 `ALTER INDEX` 修改 `options`、`limit`、`prefilter` 或 `shared_corpus_stats` 会在索引上加 `ACCESS EXCLUSIVE` 锁：它要等使用该索引的查询结束，并在提交前阻塞新的查询。两个维护选项只加 `SHARE UPDATE EXCLUSIVE` 锁。
