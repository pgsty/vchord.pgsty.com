---
title: "SQL Reference"
linkTitle: "SQL Reference"
description: "The bm25query type, the <&> operator and the BM25 score it computes, to_bm25query, bm25_maintain, and the bm25 access method."
weight: 10
math: true
icon: fa-solid fa-code
---

The objects below are created in the extension's schema, by default the current schema at `CREATE EXTENSION`, usually `public`. Functions for producing `tsvector` values with custom analyzers belong to [pg_tokenizer](/docs/tokenizer/).

## Types {#types}

| Type | Definition | Description |
| --- | --- | --- |
| `bm25query` | composite `(vector tsvector, index regclass)` | A query `tsvector` paired with the bm25 index whose statistics score it. Build it with `to_bm25query`. |
{.fields meta="type"}

## Operators {#operators}

| Operator | Returns | Description |
| --- | --- | --- |
| `tsvector <&> bm25query` | `double precision` | The negative BM25 score of the left document for the query, computed with the statistics of the index in the `bm25query`. `0` when the document contains no query term; `NULL` when the document is `NULL`. As `ORDER BY` key on an indexed column it drives a bm25 index scan, ascending only. Requires the [privileges](/docs/bm25/usage/filtering/#access-control) to read the index's table. |
{.fields meta="type"}

`<&>` is implemented by the function `_bm25_evaluate(tsvector, bm25query)`; use the operator.

### Score definition {#score}

For a document \(D\) and the set of distinct lexemes \(Q\) of the query,

\[
\text{BM25}(D, Q) = \sum_{t \in Q \cap D} \ln\!\left(\frac{N + 1}{n(t) + 0.5}\right) \cdot \frac{f(t, D)\,(k_1 + 1)}{f(t, D) + k_1\left(1 - b + b\,\dfrac{|D|}{\text{avgdl}}\right)}
\]

- \(f(t, D)\) is the number of positions of lexeme \(t\) in the document's `tsvector`. Weights set with `setweight` are ignored, and a lexeme repeated in the query counts once.
- \(|D|\) is the document length, the sum of \(f\) over all its lexemes. The index stores it in one byte: exact up to 40, rounded down to a coarser step above that.
- \(N\) is the number of non-`NULL` documents in the index and \(\text{avgdl}\) their average length; \(n(t)\) is the number of documents that contain \(t\). These counts include deleted rows until [maintenance](/docs/bm25/usage/indexing/#maintenance) removes them.
- \(k_1\) and \(b\) are the [index options](/docs/bm25/reference/gucs/#index-options) set at build time.

An index scan and `<&>` evaluated row by row produce the same scores.

## Functions {#functions}

| Function | Returns | Description |
| --- | --- | --- |
| `to_bm25query(tsvector, regclass)` | `bm25query` | Pairs a query `tsvector` with the bm25 index that scores it. For an index scan, the index must be a constant naming the index on the column being ordered. |
| `bm25_maintain(regclass)` | `boolean` | Merges the index's growing segment and removes deleted rows now, regardless of the [maintenance thresholds](/docs/bm25/reference/gucs/#index-options). Returns `true` when it wrote a merged segment, `false` when nothing changed or the previous merge still waits for older transactions. Requires ownership of the table, or `MAINTAIN` on PostgreSQL 17 and later. Fails for an invalid index or the parent index of a partitioned table. |
{.fields meta="type"}

## Access method and operator class {#access-method}

| Name | Kind | Description |
| --- | --- | --- |
| `bm25` | access method | Index type for `CREATE INDEX ... USING bm25`, handler `bm25_amhandler`. One key column; no unique indexes, index-only scans, or unlogged indexes. |
| `bm25_ops` | operator class | For `tsvector`. Not the default class, so name it: `USING bm25 (terms bm25_ops)`. Orders by `<&>`. |
{.fields meta="-"}
