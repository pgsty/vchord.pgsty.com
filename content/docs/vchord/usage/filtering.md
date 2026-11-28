---
title: "Filtering"
linkTitle: "Filtering"
description: "Combine vector search with WHERE conditions: when a plain filter is enough, when to use filter keys or prefilter, and how to limit results by distance."
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/prefilter.md"
aliases:
  - "/docs/vchord/usage/prefilter/"
  - "/docs/vchord/usage/similarity-filter/"
  - "/docs/usage/prefilter/"
  - "/docs/usage/similarity-filter/"
  - "/vectorchord/usage/prefilter/"
  - "/vectorchord/usage/similarity-filter/"
  - "/docs/vchord/usage/range-query/"
  - "/vectorchord/usage/range-query/"
icon: fa-solid fa-filter
---

Most real queries are "the nearest rows *that also match something*": this tenant's documents, products in stock, images from last week, anything closer than a threshold. vchord supports four ways to apply such a condition. Which one you need depends on how many rows the condition keeps:

| Your condition | Use |
| --- | --- |
| Keeps most rows, such as `NOT deleted` | A plain [`WHERE`](#where) |
| Keeps few rows, on a column like a tenant, category, or date | [Filter keys](#filter-keys) |
| Keeps few rows but cannot be a key: an expression, a subquery, a text match | [Prefilter](#prefilter) |
| A maximum distance from the query vector | [Distance range](#distance-range) |

## A plain `WHERE` {#where}

<a id="post-filter"></a>

Any `WHERE` clause works with a vchord index. The index produces rows nearest first, and PostgreSQL discards the ones that do not match until `LIMIT` is filled:

```sql
SELECT id FROM items
WHERE NOT deleted
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

This is cheap when most rows match. When few do, it fails in one of two ways. vchordrq only reads the `probes` lists nearest to the query, so if they hold fewer than 10 matching rows, the query returns fewer than 10. vchordg keeps walking the graph until it finds enough, which can mean most of the graph. The next two sections fix this for vchordrq.

## Filter keys {#filter-keys}

A filter key is a column stored next to each vector inside a vchordrq index. The index then checks the condition itself, before reranking, and when the probed lists run out of matching rows it reads more lists, doubling the count each round, until `LIMIT` is filled.

Add the key columns after the vector column:

```sql
CREATE INDEX ON items USING vchordrq (embedding vector_cosine_ops, tenant_id, created_at)
WITH (options = $$
[build.internal]
lists = [2000]
spherical_centroids = true
$$);

SELECT id FROM items
WHERE tenant_id = 42 AND created_at >= now() - interval '30 days'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

`EXPLAIN` shows the key condition as `Index Cond` next to `Order By`. A query without the `ORDER BY` on the vector does not use the index for the key alone; that is what a B-tree is for.

- **Types and conditions.** Keys can be `int2`, `int4`, `int8`, `float4`, `float8`, `uuid`, `date`, `timestamp`, `timestamptz`, `oid`, `bool`, or any enum. The index applies `=`, `<`, `<=`, `>`, `>=`, `BETWEEN`, and `= ANY(...)`. On PostgreSQL 15 and 16, `= ANY(...)` is checked after the scan instead of inside it.
- **Order of keys.** Put the most selective key first. The first `zone_maps` keys (default 2) also keep a minimum and maximum per block, so range conditions on them skip whole blocks.
- **Hashed keys.** For a wide key you only compare with `=`, such as a `uuid`, `uuid_hash_ops`, `int8_hash_ops`, and `int4_hash_ops` store a short hash instead of the value: `(embedding vector_cosine_ops, owner uuid_hash_ops (bytes = 4))`. Rows whose hash collides are rechecked by PostgreSQL.
- **Bounding the work.** With the default `vchordrq.max_probes = -1`, a value that matches no row makes the scan read every list before it can return nothing. Set `vchordrq.max_probes` to cap the lists read, or `0` to stay within `probes`.
- **Order.** Rows found in a later round can be nearer than rows already returned. If you need strict distance order, overfetch and sort in SQL as shown in [Result order](/docs/vchord/usage/indexing/#result-order).

Filter keys are not available for multi-vector (`@#`) indexes or on vchordg.

## Prefilter {#prefilter}

<a id="when-to-enable"></a><a id="execution-semantics"></a>

When the condition cannot be a filter key, `vchordrq.prefilter` makes vchordrq check it before reranking each candidate rather than after. Reranking costs a full-precision distance computation and a page read; at 1% selectivity, nearly all of that work goes to rows the filter would throw away.

```sql
SET vchordrq.prefilter = on;

SELECT id FROM items
WHERE metadata @> '{"lang": "de"}'
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

Turn it on when the condition is both selective and cheap to evaluate. On LAION-5M it raised throughput by about 200% at 1% selectivity and about 5% at 10%:

![Prefilter QPS speedup on LAION-5M](/docs/images/prefilter.png)

A condition most rows pass gains nothing, and an expensive one, such as a regular expression, can cost more than it saves. Volatile functions such as `random()` are always evaluated after the scan.

Prefilter does not change which lists are read, so it does not fix short results the way filter keys do. It applies to vchordrq only.

## Distance range {#distance-range}

<a id="operator-classes"></a><a id="types"></a><a id="functions"></a><a id="operators"></a>

To keep only rows within a distance of the query vector, write the threshold with `sphere(center, radius)` and a range operator instead of comparing the distance in `WHERE`:

```sql
SELECT id FROM items
WHERE embedding <<=>> sphere('[3, 1, 2]'::vector, 0.2)
ORDER BY embedding <=> '[3, 1, 2]'
LIMIT 10;
```

The index can then stop once no remaining row can be inside the radius, instead of producing rows that PostgreSQL then discards. The condition shows as `Index Cond` in `EXPLAIN`. It also works without `ORDER BY` and `LIMIT`, to fetch every row within the radius.

| Operator | Matches rows where | Center type |
| --- | --- | --- |
| `<<->>` | `<->` (L2 distance) < radius | `sphere(vector \| halfvec \| rabitq8 \| rabitq4, real)` |
| `<<#>>` | `<#>` (negative inner product) < radius | same |
| `<<=>>` | `<=>` (cosine distance) < radius | same |

Both vchordrq and vchordg support these operators with the same operator classes as `ORDER BY`. The search is still approximate and can miss matching rows, for example ones in a list that was not probed or a part of the graph the walk did not reach. When you need every row within the radius, run the query without the index (`SET vchordrq.enable_scan = off` or `vchordg.enable_scan = off`) and check with `EXPLAIN` that PostgreSQL scans the table.

## Reference {#reference}

<a id="search-parameters"></a><a id="vchordrq-prefilter"></a>

| Setting | Type | Default | Description |
| --- | --- | --- | --- |
| `vchordrq.prefilter` | boolean | `off` | Check `WHERE` conditions before reranking each candidate. |
| `vchordrq.max_probes` | integer | `-1` | Most lists a filter key scan reads after its probed lists run out. `-1` means no limit; `0` reads only `probes`. |
| `vchordrq.max_scan_tuples` | integer | `-1` | Stop after this many candidates, whatever the filter. `-1` means no limit. |
| `vchordg.max_scan_tuples` | integer | `-1` | The same for vchordg. |
{.fields meta="type default"}

Every key type has a default operator class, so naming one is optional; `uuid_hash_ops`, `int4_hash_ops`, and `int8_hash_ops` are the hashed alternatives. The `zone_maps` option is listed with the other [vchordrq index options](/docs/vchord/usage/indexing/#indexing-options). `sphere()` returns the composite types `sphere_vector`, `sphere_halfvec`, `sphere_rabitq8`, and `sphere_rabitq4`.
