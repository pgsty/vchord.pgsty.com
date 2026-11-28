---
title: "Measure Recall"
linkTitle: "Measure Recall"
description: "Measure how many of the true nearest neighbors your queries return, on single queries or on a sample of real traffic, so you can tune probes, epsilon, and ef_search against a target."
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/measure-recall.md"
aliases:
  - "/docs/usage/measure-recall/"
  - "/vectorchord/usage/measure-recall/"
icon: fa-solid fa-bullseye
---

Recall is the share of the true nearest neighbors that an index scan returns: if a `LIMIT 10` query returns 9 of the 10 rows an exact scan would, its recall is 0.9. It is the number to tune against, because every speed setting in vchord trades some of it away. Measure it on your own data and queries; benchmarks on other datasets do not predict it well.

## Measure one query {#recall-evaluation}

`vchordrq_evaluate_query_recall` runs a query through the index, runs it again to get the true answer, and returns the share of rows they have in common. The query must select only `ctid`:

```sql
SET vchordrq.probes = '20';

SELECT vchordrq_evaluate_query_recall(query => $$
    SELECT ctid FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10
$$);
```

The index pass uses your current settings, or those [stored on the index](/docs/vchord/usage/fallback-parameters/), so you can change `vchordrq.probes` or `vchordrq.epsilon` and run it again.

<a id="estimated-ground-truth"></a><a id="exact-ground-truth"></a>

By default, the true answer comes from a second vchordrq scan that probes every list, which is much faster than reading the whole table and very close to exact. If you test an `epsilon` above `1.9`, pass at least that value as `accu_epsilon`. For an exact answer from a sequential scan, pass `exact_search => true`; multi-vector (`@#`) queries require it.

```sql
SELECT vchordrq_evaluate_query_recall(
    query => $$ SELECT ctid FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10 $$,
    exact_search => true
);
```

## Measure real traffic {#query-sampling}

<a id="sampling-security"></a>

One query says little. To tune for the queries your application actually sends, let vchordrq record a sample of them, then average the recall over the sample. Recording is off by default, and only a superuser can turn it on:

```sql
ALTER SYSTEM SET vchordrq.query_sampling_enable = on;
ALTER SYSTEM SET vchordrq.query_sampling_max_records = 1000;  -- kept per index
ALTER SYSTEM SET vchordrq.query_sampling_rate = 0.01;         -- share of scans recorded
SELECT pg_reload_conf();
```

After some traffic, compute the average recall of the recorded queries for one index:

```sql
SELECT avg(vchordrq_evaluate_query_recall(
    format('SELECT ctid FROM %I.%I ORDER BY %I OPERATOR(%s) %L LIMIT 10',
           q.schema_name, q.table_name, q.column_name, q.operator, q.value),
    exact_search => true))
FROM vchordrq_sampled_queries('items_embedding_idx') AS q;
```

- Reading samples requires superuser or membership in `pg_read_all_stats`, because they contain other users' query vectors, regardless of row-level security.
- Samples are kept on the server that ran the query, outside the database: they are not replicated, not backed up, and not removed by a rollback. If queries go to a standby, read the samples there.
- Only single-vector vchordrq scans are recorded.

## Measure vchordg {#vchordg}

`vchordrq_evaluate_query_recall` turns off only vchordrq indexes for its true answer, so on a vchordg query it would compare the graph with itself. Compare against a sequential scan instead:

```sql
BEGIN;
CREATE TEMP TABLE ann ON COMMIT DROP AS
    SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10;

SET LOCAL vchordg.enable_scan = off;
SET LOCAL vchordrq.enable_scan = off;

SELECT count(*) / 10.0 AS recall
FROM ann
WHERE id IN (SELECT id FROM items ORDER BY embedding <=> '[3, 1, 2]' LIMIT 10);
COMMIT;
```

## Reference {#reference}

### Function {#functions}

<a id="functions-vchordrq"></a><a id="vchordrq-evaluate-query-recall"></a>

```sql
vchordrq_evaluate_query_recall(
    query        text,                 -- SELECT ctid ... ORDER BY ... LIMIT k
    exact_search boolean DEFAULT false,-- true: true answer from a sequential scan
    accu_probes  text    DEFAULT NULL, -- probes for the true answer; NULL probes every list
    accu_epsilon real    DEFAULT 1.9   -- epsilon for the true answer
) RETURNS real
```

<a id="vchordrq-sampled-queries-func"></a><a id="vchordrq-sampled-values"></a><a id="views"></a><a id="Views"></a><a id="views-vchordrq"></a><a id="vchordrq-sampled-queries-view"></a><a id="vchordrq_sampled_queries"></a><a id="vchordrq-sampled-queries"></a>

`vchordrq_sampled_queries(index regclass)` returns the recorded queries of one index as `schema_name`, `index_name`, `table_name`, `column_name`, `operator`, and `value` (the query vector as text). The view `vchordrq_sampled_queries` lists them for every vchordrq index in the database. `vchordrq_sampled_values(index regclass)` returns only the vectors.

### Settings {#search-parameters}

<a id="vchordrq-query-sampling-enable"></a><a id="vchordrq-query-sampling-max-records"></a><a id="vchordrq-query-sampling-rate"></a>

Only a superuser can change these.

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordrq.query_sampling_enable` | boolean | `off` | Record a sample of vchordrq queries. |
| `vchordrq.query_sampling_max_records` | integer | `0` | Most recent queries kept per index, up to `10000`. |
| `vchordrq.query_sampling_rate` | real | `0` | Share of scans recorded, from `0` to `1`. |
{.fields meta="type default"}
