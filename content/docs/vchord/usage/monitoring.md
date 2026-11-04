---
title: "Monitoring"
linkTitle: "Monitoring"
description: "You can monitor the progress of building a PostgreSQL index by querying the pgstatprogresscreateindex view."
weight: 70
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/monitoring.md"
aliases:
  - "/docs/usage/monitoring/"
  - "/vectorchord/usage/monitoring/"
icon: fa-solid fa-heart-pulse
---

You can monitor the progress of building a PostgreSQL index by querying the [`pg_stat_progress_create_index`](https://www.postgresql.org/docs/current/progress-reporting.html#CREATE-INDEX-PROGRESS-REPORTING) view.

```SQL
SELECT command, phase, round(100.0 * blocks_done / nullif(blocks_total, 0), 1) AS "%" FROM pg_stat_progress_create_index;
```

<a id="Reference"></a>
## Reference

<a id="phases"></a>
<a id="Phases"></a>
### Phases (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

There are 5 steps in the index construction process of `vchordrq`. The phase name of each step are as follows:

| Step | Message                                 | Description                                                                                                            | Waiting time |
| ---- | --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1    | `initializing`                          | Start building index                                                                                                   | Short        |
| 2    | `initializing index, by default build`  | This step is only for default build                                                                                    | Short        |
| 2    | `initializing index, by internal build` | This step is only for internal build. It involves table sampling and performing partitioning to obtain centroids | Long         |
| 2    | `initializing index, by external build` | This step is only for external build. It loads centroids from a specified table                                        | Short        |
| 3    | `initializing index`                    | Initialize the data structure and storage of the index                                                                 | Short        |
| 4    | `inserting tuples from table to index`  | Assign all vectors to their corresponding lists                                                                        | Long         |
| 5    | `compacting tuples in index`            | Optimize the structure of the vector index to enhance performance                                                      | Medium       |
{.wide .expand}

The 4th step, `inserting tuples from table to index`, takes up the majority of the time during index construction. The `tuples_done`, `blocks_done` and `blocks_total` columns indicate the progress of this step.

<a id="phases"></a>
<a id="Phases"></a>
### Phases (`vchordg`)

{{< badge text="vchordg" tone="neutral" >}}

There are 2 steps in the index construction process of `vchordg`. The phase name of each step are as follows:

| Step | Message                                | Description                       | Waiting time |
| ---- | -------------------------------------- | --------------------------------- | ------------ |
| 1    | `initializing`                         | Start building index              | Short        |
| 2    | `inserting tuples from table to index` | Insert all vectors into the graph | Long         |
{.wide .expand}

The 2nd step, `inserting tuples from table to index`, takes up the majority of the time during index construction. The `tuples_done`, `blocks_done` and `blocks_total` columns indicate the progress of this step.

### Catalog Statistics & Maintenance

In `vchord` 1.2.0:

- `CREATE INDEX`, `REINDEX`, and `VACUUM` on both `vchordrq` and `vchordg` indexes report actual heap/index tuple counts and index page counts back to PostgreSQL, keeping `pg_class.reltuples` and `pg_class.relpages` accurate instead of resetting them to `0`.
- Running `ANALYZE` alone no longer triggers index cleanup or compaction in `amvacuumcleanup`; physical index maintenance runs only during `VACUUM`.
