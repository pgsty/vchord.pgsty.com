---
title: "Vchord Documentation"
linkTitle: "Documentation"
description: "Documentation for vchord, vchord_bm25, and pg_tokenizer: vector search, BM25 ranking, and tokenization inside PostgreSQL."
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://docs.vectorchord.ai/
upstream_modified: true
aliases:
  - "/cloud/"
  - "/cloud/pricing/price-plan/"
  - "/cloud/manage/apikey/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

Three PostgreSQL extensions, maintained by [PGSTY](https://pgsty.com), that together cover retrieval inside the database: vector search, BM25 keyword ranking, and the tokenization that feeds it. Each works on its own; the [Vchord suite](/docs/vchord/getting-started/vectorchord-suite/) page shows how they fit together.

## Extensions {#extension-suite}

- [vchord](/docs/vchord/) — Vector indexes for pgvector columns that scale past memory. Release 1.5.0.
- [vchord_bm25](/docs/bm25/) — BM25-ranked search over full-text columns. Release 1.3.0.
- [pg_tokenizer](/docs/tokenizer/) — Tokenizers for BM25, including Chinese and Japanese. Release 1.3.0.
{.cards}

## Related projects {#related}

<a id="vchord-core-guide"></a><a id="ecosystem"></a>

- [pgvector](/docs/vector/) — The vector types and operators vchord builds on.
- [pgvecto.rs](/docs/vectors/) — vchord's predecessor, no longer developed.
- [pg_bestmatch](/docs/bestmatch/) — vchord_bm25's predecessor, no longer developed.
{.cards}

## About {#about}

- [About this site](/docs/about/) — Who maintains these extensions and this documentation.
- [Attribution](/docs/about/attribution/) — The upstream projects and authors this work comes from.
- [Licenses](/docs/about/license/) — AGPL-3.0 and Apache-2.0 for the code, CC BY 4.0 for the docs.
{.cards}
