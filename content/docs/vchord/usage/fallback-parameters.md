---
title: "Fallback Parameters"
linkTitle: "Fallback Parameters"
description: "Search parameters are typically configured via GUCs. VectorChord also offers an alternative method, allowing these parameters to be attached directly to an inde"
weight: 80
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/fallback-parameters.md"
aliases:
  - "/docs/usage/fallback-parameters/"
  - "/vectorchord/usage/fallback-parameters/"
icon: fa-solid fa-sliders
---

{{< badge text="since v1.1.0" tone="info" >}}


Search parameters are typically configured via GUCs. VectorChord also offers an alternative method, allowing these parameters to be attached directly to an index instead of a session or transaction. In other words, you can store them as part of the index's storage parameters.

You could set `probes` at index building using the following syntax.

```sql
CREATE INDEX items_embedding_idx ON items USING vchordrq (embedding vector_l2_ops) WITH (options = $$
build.internal.lists = [1000]
$$, probes = '10');
```

You can now perform searches without setting GUCs:

```sql
--- probes = '10'
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

If the index is already built, you can set `probes` like this:

```sql
ALTER INDEX items_embedding_idx SET (probes = '100');
```

You can still set GUCs for search parameters. When you do so, the GUCs take precedence over the index storage parameters. This allows you to temporarily override these settings for the current session or transaction without locking the index.

```sql
SET vchordrq.probes TO '100';
--- probes = '100'
SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;
```

This syntax is useful in the following situations:

* When there are multiple indexes.
* When you prefer not to set GUCs.
* When you want to configure search parameters offline.

As long as GUCs are set, even at the system level or database level, they will override the index settings. So, to avoid hard-to-detect issues, we recommend using only one method to set search parameters, either via GUCs or via index storage parameters.

Not all parameters support this feature. See [Reference](#reference) for all supported parameters.

<a id="Reference"></a>
## Reference {#reference}

<a id="index-storage-parameters"></a>
### Index Storage Parameters (`vchordrq`)

{{< badge text="vchordrq" tone="neutral" >}}

#### `probes`

{{< badge text="since v1.1.0" tone="info" >}}

- Description: Fallback value of [`vchordrq.probes`](/docs/vchord/usage/indexing/#search-parameters-vchordrq-probes).
- Type: list of integers
- Default: ` `
- Domain: each entry is `1..=4294967295`; an empty list is valid for an unpartitioned index.

#### `epsilon`

{{< badge text="since v1.1.0" tone="info" >}}

- Description: Fallback value of [`vchordrq.epsilon`](/docs/vchord/usage/indexing/#search-parameters-vchordrq-epsilon).
- Type: real
- Default: `1.9`
- Domain: `[0.0, 4.0]`

<a id="maxsim-refine"></a>
#### `maxsim_refine`

{{< badge text="since v1.1.0" tone="info" >}}

- Description: Fallback value of [`vchordrq.maxsim_refine`](/docs/vchord/usage/multi-vector-retrieval/#search-parameters-vchordrq-maxsim-refine).
- Type: integer
- Default: `0`
- Domain: `[0, 2147483647]`

<a id="maxsim-threshold"></a>
#### `maxsim_threshold`

{{< badge text="since v1.1.0" tone="info" >}}

- Description: Fallback value of [`vchordrq.maxsim_threshold`](/docs/vchord/usage/multi-vector-retrieval/#search-parameters-vchordrq-maxsim-threshold).
- Type: integer
- Default: `0`
- Domain: `[0, 2147483647]`

<a id="index-storage-parameters"></a>
### Index Storage Parameters (`vchordg`)

{{< badge text="vchordg" tone="neutral" >}}

<a id="ef-search"></a>
#### `ef_search`

{{< badge text="since v1.1.0" tone="info" >}}

- Description: Fallback value of [`vchordg.ef_search`](/docs/vchord/usage/graph-index/#search-parameters-vchordg-ef-search).
- Type: integer
- Default: `64`
- Domain: `[1, 65535]`
