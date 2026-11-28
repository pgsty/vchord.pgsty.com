---
title: "Overview"
linkTitle: "Overview"
description: "What vchord_bm25 is, why ranked full-text search needs its own index in PostgreSQL, how a top-k query runs, and a quick start."
weight: 10
icon: fa-solid fa-compass
aliases:
  - "/docs/bm25/getting-started/quick-start/"
---

`vchord_bm25` is a PostgreSQL extension that ranks rows by BM25 relevance and returns the best matches of a `tsvector` column through an index. Your text stays in your tables and your queries stay SQL: you index the `tsvector` column `USING bm25`, and `ORDER BY terms <&> to_bm25query(...) LIMIT 10` returns the ten most relevant rows. If you only need to find matching rows, without ranking them, PostgreSQL's GIN index is enough.

## Why vchord_bm25 {#why}

PostgreSQL full-text search finds matching rows quickly with a GIN index on a `tsvector` column. Ranking those rows has two problems:

- **`ts_rank` scores each document on its own.** It does not know how many documents contain a term or how long documents are on average, so a word that appears in every document weighs as much as a rare one, and long documents win by repeating terms. BM25 uses exactly those corpus-wide statistics: rare terms weigh more, repeated occurrences of a term add less and less, and scores are normalized by document length.
- **A GIN index answers `WHERE terms @@ query`, not `ORDER BY rank`.** To return the top 10, PostgreSQL fetches every matching row, scores it, and sorts. The cost grows with the number of matches, so a broad query on a large table reads most of it.

`vchord_bm25` keeps the corpus statistics inside its index and walks the posting lists of the query terms with Block-WeakAnd, which skips blocks of documents that cannot reach the current top k. The work of a query follows its `LIMIT` and its terms, not the number of rows that match.

## How it works {#how-it-works}

1. **Analyze.** You turn each row's text into a `tsvector`, with PostgreSQL's `to_tsvector` or with [pg_tokenizer](/docs/tokenizer/) for languages and vocabularies PostgreSQL does not handle. The number of positions of a lexeme is its term frequency.
1. **Index.** `CREATE INDEX ... USING bm25` stores compressed posting lists together with the statistics BM25 needs: the number of documents, their lengths, and how many documents contain each term. New and updated rows are appended to a growing segment and are searchable at once; `VACUUM` merges them into the compressed segment.
1. **Query.** `to_bm25query(query, 'index_name')` names the index whose statistics define the score. The `<&>` operator returns the negative BM25 score, so ascending order puts the best match first. An index scan ranks the first 100 rows (the `bm25.limit` setting) and continues in larger batches only if the query asks for more.
{.steps}

The ranking is exact: the index returns the same scores, in the same order, as computing `<&>` for every row and sorting. [Querying](/docs/bm25/usage/querying/#how-a-query-runs) explains the batches and what they mean for `LIMIT`, filters, and cost.

## When to use something else {#alternatives}

| You need | Use |
| --- | --- |
| Rows that match a boolean or phrase query, without ranking | A GIN index on the `tsvector` and the `@@` operator |
| The most relevant rows by BM25 from a large table | `vchord_bm25` |
| Rows that mean the same as the query in other words | Vector search with [vchord](/docs/vchord/), or both together with [hybrid search](/docs/bm25/usage/hybrid-search/) |
| Chinese, Japanese, or Korean text, or a model vocabulary such as BERT | [pg_tokenizer](/docs/tokenizer/) to produce the `tsvector`, then `vchord_bm25` |

## Quick start {#quick-start}

vchord_bm25 1.3.0 runs on PostgreSQL 15–19 on Linux `x86_64` and `aarch64`. Other ways to install are on the [installation page](/docs/bm25/getting-started/installation/).

1. Install the package from the Pigsty repository:

   ```bash
   curl -fsSL https://repo.pigsty.io/pig | bash
   pig repo add pgsql -u
   pig ext add vchord_bm25
   ```

1. Preload the library and restart PostgreSQL. Without this step, `CREATE EXTENSION` stops with `vchord_bm25 must be loaded via shared_preload_libraries.` Keep any libraries already in the list.

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'vchord_bm25';
   ```

1. Create the extension in your database, as a superuser:

   ```sql
   CREATE EXTENSION IF NOT EXISTS vchord_bm25;
   ```

1. Index a table and run a ranked query:

   ```sql
   CREATE TABLE documents (
       id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
       passage text NOT NULL,
       terms tsvector GENERATED ALWAYS AS (to_tsvector('english', passage)) STORED
   );

   INSERT INTO documents (passage) VALUES
       ('PostgreSQL provides full text search.'),
       ('BM25 ranks documents by relevance.'),
       ('PostgreSQL supports BM25 ranking with vchord_bm25.');

   CREATE INDEX documents_bm25 ON documents USING bm25 (terms bm25_ops);

   SELECT id, passage,
          terms <&> to_bm25query(to_tsvector('english', 'PostgreSQL BM25'), 'documents_bm25') AS score
   FROM documents
   ORDER BY score
   LIMIT 10;
   ```
{.steps}

The third row contains both query terms and comes first with the lowest, most negative score. Build the query with the same `to_tsvector` configuration as the documents; a different analysis produces lexemes the index has never seen. [Querying](/docs/bm25/usage/querying/#scores) explains why scores are negative and how to return only rows that match.

## Where to go next {#next-steps}

- **Index a production table**, in any language, and keep it fast under writes: [Indexing](/docs/bm25/usage/indexing/).
- **Tune queries and filters**: [Querying](/docs/bm25/usage/querying/) and [Filtering](/docs/bm25/usage/filtering/).
- **Combine with vector search**: [Hybrid search](/docs/bm25/usage/hybrid-search/).
- **Upgrade, or move from the 0.x `bm25vector` API**: [Upgrade and migration](/docs/bm25/reference/migration/).

## License {#license}

vchord_bm25 is licensed under [AGPL-3.0](https://github.com/pgsty/vchord_bm25/blob/main/LICENSE). It is a fork of TensorChord's [VectorChord-bm25](https://github.com/supervc-stack/VectorChord-bm25), maintained by [PGSTY](https://pgsty.com). For commercial licensing or support, contact [rh@vonng.com](mailto:rh@vonng.com).
