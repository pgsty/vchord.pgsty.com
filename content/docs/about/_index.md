---
title: About Vchord & vchord.pgsty.com
linkTitle: About
description: Who maintains vchord, vchord_bm25, and pg_tokenizer, where they come from, and under which licenses.
type: docs
weight: 5
icon: fa-solid fa-circle-info
upstream_source: ""
upstream_link: ""
upstream_modified: false
aliases:
  - "/about/"
cascade:
  type: docs
  upstream_source: ""
  upstream_link: ""
  upstream_modified: false
---

This site documents three PostgreSQL extensions maintained by [PGSTY](https://pgsty.com): [vchord](/docs/vchord/) for vector search, [vchord_bm25](/docs/bm25/) for BM25 ranking, and [pg_tokenizer](/docs/tokenizer/) for tokenization. It also keeps reference copies of [pgvector](/docs/vector/), which vchord builds on, and of the retired predecessors [pgvecto.rs](/docs/vectors/) and [pg_bestmatch](/docs/bestmatch/). The [blog](/blog/) carries release notes and engineering articles.

The three extensions are forks of TensorChord's VectorChord, VectorChord-bm25, and pg_tokenizer.rs. TensorChord stopped maintaining them, and PGSTY took them over at the request of their original authors. These forks are not affiliated with, endorsed by, or sponsored by TensorChord Inc.

- [Attribution](/docs/about/attribution/) — The upstream projects and authors, and how their material was adapted.
- [Licenses](/docs/about/license/) — AGPL-3.0 for vchord and vchord_bm25, Apache-2.0 for pg_tokenizer, CC BY 4.0 for this documentation.
- [Trademarks](/docs/about/trademark/) — How the names are used.
- [Software bill of materials](/docs/about/sbom/) — Dependencies and their licenses.
{.cards}

Report bugs and security issues on [GitHub](https://github.com/pgsty/vchord/issues).
