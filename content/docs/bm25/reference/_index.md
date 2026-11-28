---
title: "Reference"
description: "SQL objects, settings and index options, upgrade and migration, and benchmarks for vchord_bm25."
weight: 40
icon: fa-solid fa-book
no_list: true
---

Each operator, function, setting, and index option is defined once in these pages; the usage guides link here. The migration page also holds the release history.

{{< cards >}}
  {{< card link="/docs/bm25/reference/sql/" title="SQL reference" icon="fa-solid fa-code" >}}
The `bm25query` type, the `<&>` operator and its score formula, `to_bm25query`, `bm25_maintain`, and the `bm25` access method.
{{< /card >}}
  {{< card link="/docs/bm25/reference/gucs/" title="Settings and index options" icon="fa-solid fa-sliders" >}}
`bm25.*` settings, index storage options, and which one wins when both are set.
{{< /card >}}
  {{< card link="/docs/bm25/reference/migration/" title="Upgrade and migration" icon="fa-solid fa-right-left" >}}
Releases, in-place upgrades within 1.x, downgrades, and moving from the 0.x `bm25vector` API.
{{< /card >}}
  {{< card link="/docs/bm25/reference/benchmarks/" title="Benchmarks" icon="fa-solid fa-chart-bar" >}}
Published throughput and relevance measurements, with their datasets, versions, and sources.
{{< /card >}}
{{< /cards >}}
