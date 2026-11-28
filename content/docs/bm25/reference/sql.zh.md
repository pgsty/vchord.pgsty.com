---
title: "SQL 参考"
linkTitle: "SQL 参考"
description: "bm25query 类型、<&> 运算符及其计算的 BM25 分数、to_bm25query、bm25_maintain，以及 bm25 访问方法。"
weight: 10
math: true
icon: fa-solid fa-code
---

以下对象创建在扩展所在的模式中，默认是执行 `CREATE EXTENSION` 时的当前模式，通常为 `public`。用自定义分析器生成 `tsvector` 的函数属于 [pg_tokenizer](/zh/docs/tokenizer/)。

## 类型 {#types}

| 类型 | 定义 | 说明 |
| --- | --- | --- |
| `bm25query` | 复合类型 `(vector tsvector, index regclass)` | 查询 `tsvector` 与为它打分的 bm25 索引组成的一对。用 `to_bm25query` 构造。 |
{.fields meta="type"}

## 运算符 {#operators}

| 运算符 | 返回值 | 说明 |
| --- | --- | --- |
| `tsvector <&> bm25query` | `double precision` | 左侧文档相对于查询的 BM25 分数的相反数，使用 `bm25query` 中那个索引的统计信息计算。文档不含任何查询词时为 `0`；文档为 `NULL` 时为 `NULL`。在被索引列上作为 `ORDER BY` 键时驱动 bm25 索引扫描，只支持升序。需要读取索引所在表的[权限](/zh/docs/bm25/usage/filtering/#access-control)。 |
{.fields meta="type"}

`<&>` 由函数 `_bm25_evaluate(tsvector, bm25query)` 实现；请直接使用运算符。

### 分数定义 {#score}

对于文档 \(D\) 和查询中不重复的词位集合 \(Q\)：

\[
\text{BM25}(D, Q) = \sum_{t \in Q \cap D} \ln\!\left(\frac{N + 1}{n(t) + 0.5}\right) \cdot \frac{f(t, D)\,(k_1 + 1)}{f(t, D) + k_1\left(1 - b + b\,\dfrac{|D|}{\text{avgdl}}\right)}
\]

- \(f(t, D)\) 是词位 \(t\) 在文档 `tsvector` 中的位置个数。`setweight` 设置的权重会被忽略，查询中重复的词位只计一次。
- \(|D|\) 是文档长度，即所有词位的 \(f\) 之和。索引用一个字节存储它：40 以内精确，超过 40 则向下取到更粗的档位。
- \(N\) 是索引中非 `NULL` 文档的数量，\(\text{avgdl}\) 是它们的平均长度；\(n(t)\) 是包含 \(t\) 的文档数。在[维护](/zh/docs/bm25/usage/indexing/#maintenance)清理之前，这些计数包含已删除的行。
- \(k_1\) 和 \(b\) 是建索引时设置的[索引选项](/zh/docs/bm25/reference/gucs/#index-options)。

索引扫描与逐行计算 `<&>` 得到的分数完全相同。

## 函数 {#functions}

| 函数 | 返回值 | 说明 |
| --- | --- | --- |
| `to_bm25query(tsvector, regclass)` | `bm25query` | 把查询 `tsvector` 与为它打分的 bm25 索引组合起来。要走索引扫描，索引参数必须是常量，并且指向排序列上的那个索引。 |
| `bm25_maintain(regclass)` | `boolean` | 立即合并索引的增长段并清理已删除的行，不受[维护阈值](/zh/docs/bm25/reference/gucs/#index-options)限制。写出了合并后的段时返回 `true`；没有变化，或上一次合并仍在等待更早的事务结束时，返回 `false`。需要是表的属主，PostgreSQL 17 及以上也可以持有 `MAINTAIN` 权限。对无效索引或分区表的父索引调用会报错。 |
{.fields meta="type"}

## 访问方法与运算符类 {#access-method}

| 名称 | 类别 | 说明 |
| --- | --- | --- |
| `bm25` | 访问方法 | `CREATE INDEX ... USING bm25` 的索引类型，处理函数为 `bm25_amhandler`。只支持一个键列；不支持唯一索引、仅索引扫描和 unlogged 索引。 |
| `bm25_ops` | 运算符类 | 用于 `tsvector`。不是默认运算符类，必须写明：`USING bm25 (terms bm25_ops)`。按 `<&>` 排序。 |
{.fields meta="-"}
