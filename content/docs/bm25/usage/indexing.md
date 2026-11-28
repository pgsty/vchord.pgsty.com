---
title: "Indexing"
linkTitle: "Indexing"
description: "Produce the tsvector for any language, build a bm25 index, choose k1 and b, and keep the index fast and correct as the table changes."
weight: 10
icon: fa-solid fa-database
---

A `bm25` index holds the posting lists and corpus statistics that BM25 ranking needs, built from one `tsvector` column or expression. This page covers producing that `tsvector`, building and tuning the index, and keeping queries fast as rows are inserted, updated, and deleted.

## Produce the tsvector {#tsvector}

The index scores what the `tsvector` contains, so relevance depends first on text analysis. Two rules apply whichever method you use:

- Documents and queries must go through the same analysis. A query built with another configuration produces lexemes the index has never seen.
- Document vectors must keep positions: the number of positions of a lexeme is its term frequency. `strip()`, `array_to_tsvector()`, and literals without positions are rejected (see [Limits](#limits)).

**A generated column** is the simplest choice for languages PostgreSQL's text search configurations handle, such as `english` or `simple`. The [quick start](/docs/bm25/getting-started/overview/#quick-start) uses one.

**An expression index** saves the storage of a separate column. Queries must order by the same expression:

```sql
CREATE INDEX documents_passage_bm25 ON documents
USING bm25 ((to_tsvector('english', passage)) bm25_ops);

SELECT id FROM documents
ORDER BY to_tsvector('english', passage)
      <&> to_bm25query(to_tsvector('english', 'full text search'), 'documents_passage_bm25')
LIMIT 10;
```

The expression must be immutable, so pass the configuration name explicitly.

**pg_tokenizer** produces `tsvector` values for text that `to_tsvector` cannot segment, such as Chinese with Jieba, Japanese and Korean with Lindera, or the token IDs of a model vocabulary. Its functions are `STABLE` because analyzers are defined in catalog tables, so they cannot appear in a generated column or an index expression. Fill a regular column instead, for example with a trigger:

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer;  -- also add pg_tokenizer to shared_preload_libraries

SELECT tokenizer_catalog.create_text_analyzer('zh', $$
[pre_tokenizer.jieba]
$$);

CREATE TABLE articles (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    body text NOT NULL,
    terms tsvector
);

CREATE FUNCTION articles_terms() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    NEW.terms := tokenizer_catalog.analyze_to_tsvector(NEW.body, 'zh');
    RETURN NEW;
END
$$;

CREATE TRIGGER articles_terms BEFORE INSERT OR UPDATE OF body ON articles
FOR EACH ROW EXECUTE FUNCTION articles_terms();

CREATE INDEX articles_bm25 ON articles USING bm25 (terms bm25_ops);

SELECT id, body
FROM articles
ORDER BY terms <&> to_bm25query(tokenizer_catalog.analyze_to_tsvector('全文检索', 'zh'), 'articles_bm25')
LIMIT 10;
```

`analyze_to_tsvector` emits the analyzer's tokens as lexemes; `tokenize_to_tsvector` emits a model's token IDs. The [pg_tokenizer documentation](/docs/tokenizer/) covers analyzers, filters, and models.

## Create the index {#create}

```sql
CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops);
```

- Name the operator class `bm25_ops`; it is not the default for `tsvector`.
- Give the index a name you will keep. Queries refer to it in `to_bm25query`, and the name decides which statistics score the query.
- An index covers one column. To rank within a fixed subset, such as published rows, build a [partial index](/docs/bm25/usage/filtering/#partial-indexes).
- `CREATE INDEX CONCURRENTLY` works as for any index.

Builds scan the table with PostgreSQL's parallel maintenance workers, limited by `max_parallel_maintenance_workers` (or the table's `parallel_workers` option). The leader and the workers share `maintenance_work_mem` for their sort buffers, at most 64 MiB each; anything beyond that spills to temporary files. Follow a build in `pg_stat_progress_create_index`, where `phase` moves through `building index: scanning table` and `building index: writing index structures`:

```sql
SELECT phase, tuples_done, tuples_total
FROM pg_stat_progress_create_index;
```

## Choose k1 and b {#scoring-parameters}

BM25 has two parameters, fixed when the index is built:

- **`k1`** (default `1.2`, range 1.2–2.0) sets how quickly repeated occurrences of a term stop adding to the score. Raise it when repetition is a real signal of relevance, as in long technical documents.
- **`b`** (default `0.75`, range 0–1) sets how strongly long documents are penalized. Lower it when long documents are long because they cover more, not because they ramble; `0` turns length normalization off.

The defaults match Lucene and Elasticsearch and are the right start. Change them only against measured relevance:

1. Collect real queries with known relevant rows, and measure NDCG@10 or recall of the current index.
1. Build a second index on the same column with the candidate values. Both indexes stay usable, because each query names the index that scores it:

   ```sql
   CREATE INDEX CONCURRENTLY documents_bm25_k15 ON documents USING bm25 (terms bm25_ops)
   WITH (options = $$
   k1 = 1.5
   b = 0.6
   $$);
   ```

1. Run the same queries against `documents_bm25_k15` and compare.
1. Keep the better index and drop the other. Every write maintains both while they coexist.
{.steps}

To change the values of an existing index in place, set `options` and rebuild: `ALTER INDEX documents_bm25 SET (options = $$ ... $$); REINDEX INDEX documents_bm25;`. The [score definition](/docs/bm25/reference/sql/#score) shows where `k1` and `b` enter the formula.

## Keep the index fast {#maintenance}

Inserted and updated rows are appended to a **growing segment** and are searchable immediately, with exact scores. The growing segment has no block summaries, though, so every query reads all of it. Query time grows with it until `VACUUM` merges it into the compressed segment.

`VACUUM`, manual or autovacuum, merges when either is true:

- The growing segment holds at least `maintenance_min_rows` rows (default 1,000) and at least `maintenance_scale_factor` (default 0.1) times the rows already merged.
- Deleted rows reach `maintenance_scale_factor` of all rows. Until then, deleted and replaced rows still count in the statistics (the document count, term document frequencies, and average length), so scores drift after a large `DELETE` or rewrite.

Merging takes the same lock as `VACUUM`, so reads and writes continue. `ANALYZE` alone does not merge. Both thresholds are [index options](/docs/bm25/reference/gucs/#index-options); lower `maintenance_scale_factor` on a large table to merge more often.

**Insert-only tables** are vacuumed when inserts reach `autovacuum_vacuum_insert_threshold` plus `autovacuum_vacuum_insert_scale_factor` (default 0.2) of the table. On a large table that lets the growing segment get big; lower the factor for that table:

```sql
ALTER TABLE documents SET (autovacuum_vacuum_insert_scale_factor = 0.02);
```

**Merge now** with [`bm25_maintain`](/docs/bm25/reference/sql/#field-bm25_maintain-regclass), regardless of thresholds, after a bulk load or delete:

```sql
SELECT bm25_maintain('documents_bm25');
```

It returns `true` when it wrote a merged segment, and `false` when nothing changed or when the pages of the previous merge are still waiting for older transactions to finish. It needs ownership of the table, or the `MAINTAIN` privilege on PostgreSQL 17 and later, and takes the same table lock as `VACUUM`.

**Long transactions** hold back the reuse of pages that a merge replaced, so the index grows until they end. On a hot standby without `hot_standby_feedback`, a query that reads pages the primary has just reused fails with `canceling statement due to conflict with bm25 index maintenance`; retry it, or turn on `hot_standby_feedback`.

## Rebuild {#rebuild}

Rebuild to apply new `k1` and `b`, or to repair an index that a failed `CREATE INDEX CONCURRENTLY` left invalid. Queries against an invalid index fail with `index "documents_bm25" is not valid`.

- `REINDEX INDEX documents_bm25` keeps the index's OID. While it runs, it blocks writes to the table and queries that use the index.
- `REINDEX INDEX CONCURRENTLY documents_bm25` keeps writes going but creates a new index with a new OID.

`to_bm25query(..., 'documents_bm25')` turns the name into an OID when a statement is parsed, so statements parsed after the reindex find the new index. Views, materialized views, rules, and SQL-standard function bodies (`BEGIN ATOMIC` or `RETURN`) store the old OID and fail afterwards with `the relation does not exist`. Keep their original definitions and run them again with `CREATE OR REPLACE` after a concurrent reindex; `pg_get_viewdef` at that point already shows the stale OID. The same applies after dropping and recreating an index.

## Limits {#limits}

- **One column.** A second key column fails with `multicolumn index is not supported`.
- **Positions required.** A document `tsvector` without positions fails with `tsvector must have positions`, on insert, during `CREATE INDEX`, and when scoring. Query vectors may lack positions.
- **PostgreSQL `tsvector` limits.** A lexeme keeps at most 256 positions, positions above 16,383 are clamped, and `to_tsvector` drops words longer than 2,046 bytes. Term frequencies therefore saturate in very long documents. Index passages of a few thousand words rather than whole books.
- **No unlogged tables.** `CREATE INDEX` on an `UNLOGGED` table fails with `Unlogged indexes are not supported.`
- **Partitioned tables.** `CREATE INDEX` on a partitioned table creates one bm25 index per partition, each with its own statistics. Query a partition and name that partition's index in `to_bm25query`; the parent index cannot be used for scoring or with `bm25_maintain`.
