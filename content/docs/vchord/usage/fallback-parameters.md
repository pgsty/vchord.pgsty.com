---
title: "Per-Index Search Defaults"
linkTitle: "Index Defaults"
description: "Store probes, epsilon, ef_search, and the MaxSim settings on the index itself, so every session uses the tuned values without a SET."
weight: 70
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/fallback-parameters.md"
aliases:
  - "/docs/usage/fallback-parameters/"
  - "/vectorchord/usage/fallback-parameters/"
icon: fa-solid fa-sliders
---

Search settings such as `vchordrq.probes` are ordinary PostgreSQL settings, normally changed with `SET`. That is awkward when a connection pooler in transaction mode or an ORM sits between the application and the database, and wrong when two indexes need different values: an index with `lists = [400, 160000]` needs two `probes` values, one with `lists = [2000]` only one. Store the tuned values on each index instead. A scan uses them whenever nobody has set the setting explicitly.

## Store values on an index {#usage}

At creation, next to `options`:

```sql
CREATE INDEX items_embedding_idx ON items USING vchordrq (embedding vector_cosine_ops)
WITH (options = $$
[build.internal]
lists = [2000]
spherical_centroids = true
$$, probes = '20', epsilon = 1.9);
```

On an existing index, without a rebuild:

```sql
ALTER INDEX items_embedding_idx SET (probes = '40');
ALTER INDEX items_embedding_idx RESET (epsilon);
```

`ALTER INDEX` takes an exclusive lock on the index for a moment, so it waits for queries running on it and blocks new ones until it commits.

## Which value wins {#precedence}

A value set explicitly anywhere wins over the index: in `postgresql.conf`, with `ALTER SYSTEM`, `ALTER DATABASE`, `ALTER ROLE`, or `SET`, even when it equals the default. The index's value applies only while `pg_settings.source` for the setting is `default`:

```sql
SET vchordrq.probes = '50';   -- this session uses 50, whatever the index says
RESET vchordrq.probes;        -- back to the index's value, unless set elsewhere
```

If an index's values are not taking effect, check `SELECT name, setting, source FROM pg_settings WHERE name LIKE 'vchord%';` for a setting someone set at the role or database level.

## Reference {#reference}

<a id="index-storage-parameters"></a><a id="index-storage-parameters-vchordrq"></a><a id="index-storage-parameters-vchordg"></a><a id="probes"></a><a id="epsilon"></a><a id="maxsim-refine"></a><a id="maxsim-threshold"></a><a id="ef-search"></a>

| Index parameter | Index type | Default for | Meaning |
| --- | --- | --- | --- |
| `probes` | vchordrq | `vchordrq.probes` | [Lists to probe](/docs/vchord/usage/indexing/#search-parameters), one value per level. |
| `epsilon` | vchordrq | `vchordrq.epsilon` | [Width of the error bound](/docs/vchord/usage/indexing/#search-parameters). |
| `maxsim_refine` | vchordrq | `vchordrq.maxsim_refine` | [Documents refined with exact distances](/docs/vchord/usage/multi-vector-retrieval/#search-parameters). |
| `maxsim_threshold` | vchordrq | `vchordrq.maxsim_threshold` | [Bound for unprobed tokens](/docs/vchord/usage/multi-vector-retrieval/#search-parameters). |
| `ef_search` | vchordg | `vchordg.ef_search` | [Candidates kept during the walk](/docs/vchord/usage/graph-index/#search-parameters). |
{.fields meta="- -"}

Other settings, such as `max_scan_tuples`, `max_probes`, `prefilter`, and the I/O settings, can only be set as PostgreSQL settings.
