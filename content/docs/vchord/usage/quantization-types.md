---
title: "Quantized Types"
linkTitle: "Quantized Types"
description: "Store vectors at 8 or 4 bits per dimension with the rabitq8 and rabitq4 column types, and know what that costs in accuracy."
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/usage/quantization-types.md"
aliases:
  - "/docs/usage/quantization-types/"
  - "/vectorchord/usage/quantization-types/"
icon: fa-solid fa-compress
---

vchord indexes already compress vectors internally, but the table still holds every vector at full size, and at hundreds of millions of rows that column is most of the database. pgvector's `halfvec` halves it. vchord's `rabitq8` and `rabitq4` types go further, storing each vector as one 8-bit or 4-bit code per dimension plus four scaling values, using [extended RaBitQ](https://arxiv.org/abs/2409.09913):

| Type | Approximate size of a 768-dimensional vector | Compared to `vector` |
| --- | --- | --- |
| `vector` | 3,072 bytes | 1 |
| `halfvec` | 1,536 bytes | 1/2 |
| `rabitq8` | 784 bytes | about 1/4 |
| `rabitq4` | 400 bytes | about 1/8 |

The price is that every distance between quantized vectors is an estimate, in the index and in SQL alike. With `rabitq8`, retrieving candidates typically loses less than 1% recall; `rabitq4` loses more. If you need exact distances for the final ranking, keep the original vectors somewhere else and rerank the top candidates with them.

## Use them {#basic-usage}

Quantize vectors as you insert them, and quantize the query vector the same way:

```sql
CREATE TABLE items (id bigserial PRIMARY KEY, embedding rabitq8(3));

INSERT INTO items (embedding) VALUES
    (quantize_to_rabitq8('[0, 0, 0]'::vector)),
    (quantize_to_rabitq8('[1, 1, 1]'::vector)),
    (quantize_to_rabitq8('[2, 2, 2]'::vector));

CREATE INDEX ON items USING vchordrq (embedding rabitq8_l2_ops);

SELECT id FROM items
ORDER BY embedding <-> quantize_to_rabitq8('[0.9, 0.9, 1.1]'::vector)
LIMIT 10;
```

The types work with both vchordrq and vchordg, as arrays for [multi-vector retrieval](/docs/vchord/usage/multi-vector-retrieval/), and with [distance ranges](/docs/vchord/usage/filtering/#distance-range). Use the `rabitq8_*` or `rabitq4_*` operator class that matches your distance.

To let an application or ORM insert plain vector literals, register an assignment cast once:

```sql
CREATE CAST (vector AS rabitq8) WITH FUNCTION quantize_to_rabitq8(vector) AS ASSIGNMENT;
```

## Limits {#limits}

<a id="input-validation"></a>

- `residual_quantization` is not available for indexes on these types.
- The dimension in `rabitq8(n)` is not yet checked on insert ([#31](https://github.com/pgsty/vchord/issues/31)); an index on the column does reject rows of the wrong dimension. Check dimensions in the application until then.
- Converting back with `dequantize_to_vector` or `dequantize_to_halfvec` gives an approximation of the original, within pgvector's limits of 16,000 dimensions for `vector` and 4,000 for `halfvec`.

## Reference {#reference}

<a id="operator-classes"></a><a id="types"></a><a id="rabitq8"></a><a id="rabitq4"></a><a id="operators"></a><a id="rabitq8-l2-op"></a><a id="rabitq8-ip-op"></a><a id="rabitq8-cosine-op"></a><a id="rabitq4-l2-op"></a><a id="rabitq4-ip-op"></a><a id="rabitq4-cosine-op"></a>

Both types take up to 65,535 dimensions; vchordrq indexes up to 60,000 and vchordg up to 30,000. They support `<->`, `<#>`, and `<=>`, which return estimated distances, and the operator classes listed for [vchordrq](/docs/vchord/usage/indexing/#operator-classes) and [vchordg](/docs/vchord/usage/graph-index/#operator-classes). Their text form, such as `(2.99, 160.6, 647, 2.85)[255, 205, 187]`, is four scaling values followed by one code per dimension; create values with the functions below rather than by hand.

### Functions {#functions}

<a id="Functions"></a><a id="quantize-to-rabitq8-vector"></a><a id="quantize-to-rabitq8-halfvec"></a><a id="dequantize-to-vector-rabitq8"></a><a id="dequantize-to-halfvec-rabitq8"></a><a id="quantize-to-rabitq4-vector"></a><a id="quantize-to-rabitq4-halfvec"></a><a id="dequantize-to-vector-rabitq4"></a><a id="dequantize-to-halfvec-rabitq4"></a>

| Function | Returns | Description |
| --- | --- | --- |
| `quantize_to_rabitq8(vector \| halfvec)` | `rabitq8` | Quantize to 8 bits per dimension. |
| `quantize_to_rabitq4(vector \| halfvec)` | `rabitq4` | Quantize to 4 bits per dimension. |
| `dequantize_to_vector(rabitq8 \| rabitq4)` | `vector` | Approximate original vector. |
| `dequantize_to_halfvec(rabitq8 \| rabitq4)` | `halfvec` | Approximate original vector in half precision. |
{.fields meta="type"}
