---
title: "Earth Genome: 3.2 Billion Vectors in PostgreSQL"
linkTitle: "Earth Genome"
description: "How Earth Genome's Earth Index stores 3.2 billion satellite-image embeddings in PostgreSQL with PostGIS and vchord on three servers, at about $12,000 a month and 761 ms median latency for a filtered top-500 search."
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/customer-stories/earthgenome.md"
aliases:
  - "/docs/customer-stories/earthgenome/"
  - "/vectorchord/customer-stories/earthgenome/"
icon: fa-solid fa-earth-americas
---

Earth Genome's [Earth Index](https://www.earthgenome.org/earth-index) makes the planet's land surface searchable by example: a user clicks a known site, such as an illegal airstrip or a quarry, and gets back places that look alike. It keeps 3.2 billion image embeddings in PostgreSQL, searched with vchord and filtered with PostGIS in the same query, on three servers. This page summarizes [3 Billion Vectors in PostgreSQL to Protect the Earth](/blog/3-billion-vectors-in-postgresql-to-protect-the-earth/) (April 2025): the workload, why the team chose PostgreSQL, and the hardware, cost, and latency.

<a id="what-is-earth-index-doing-turning-pixels-into-planetary-insights"></a>

## The workload {#workload}

Earth Index divides the land surface into 3.2 billion overlapping tiles of about 10 hectares each. A vision transformer for Earth observation, trained by self-supervised contrastive learning on satellite imagery such as Harmonized Landsat Sentinel-2 and Sentinel-1 radar, turns each tile into a 384-dimensional embedding, more than 10,000 times smaller than the imagery it summarizes. A search finds tiles whose embeddings are close to the example's, usually restricted to a region.

<a id="real-world-impact-earth-index-in-action-for-environmental-protection"></a>

Journalists, researchers, Indigenous communities, and conservation groups use it to find environmental damage across areas too large to inspect by eye. With Mongabay it located hidden narcotrafficking airstrips in the Amazon; Radio Free Europe used it to find more than 1,300 quarries in the Balkans, about half of them without valid permits. It can also find shrimp farms spreading into mangroves and livestock operations near waterways.

<a id="the-infrastructure-challenge-searching-billions-of-vectors-affordably"></a><a id="why-postgresql-rocks-for-planetary-scale-vectors"></a><a id="why-earth-index-chose-vectorchord-for-performance-and-affordability"></a>

## Why PostgreSQL and vchord {#why}

Almost every search combines vector similarity with geography: within an administrative boundary, near a river. PostGIS already held that geography, so a vector index inside the same PostgreSQL database meant one query instead of two systems to keep in sync. The remaining requirement was cost, since Earth Genome is a non-profit. Its CTO, Hutch Ingold, explained why the alternatives failed: standard pgvector did not meet their performance requirements at that scale, hosted Qdrant was too expensive and a self-hosted Qdrant cluster on their Kubernetes infrastructure seemed immature, and Google's Vertex AI Vector Search had a list price of $237,000 a month for their dataset.

vchord's index reads its lists from NVMe SSD instead of keeping a graph of all 3.2 billion vectors in memory, which kept the hardware to three servers.

<a id="earth-index-technical-architecture-and-setup"></a>

## Architecture and results {#architecture}

<img src="/docs/images/vector-search-with-geo.png" alt="Earth Index architecture: a PostgreSQL table partitioned across three nodes, each with PostGIS and vchord" style="width: 100%; height: auto; margin: 0 auto; display: block;" />

| | Earth Index |
| --- | --- |
| Servers | 3 × AWS `i8g.16xlarge`: Graviton4 (`aarch64`), 64 vCPU, 512 GB of memory, 15 TB of NVMe SSD each |
| Cost | about $12,000 a month, against the $237,000 a month quoted for Vertex AI Vector Search |
| Table | `globe24`, partitioned by `partkey` across the three nodes: tile ID, `geometry(Point, 4326)`, and the embedding as `halfvec(384)` |
| Latency | 761 ms median for a typical top-500 search across 3.2 billion rows |

A typical search has this shape, combining vchord's ordering, a PostGIS filter, and partition pruning:

```sql
SELECT id
FROM globe24
WHERE partkey IN (...)
  AND ST_Within(geom, $1)
ORDER BY embedding <=> $2
LIMIT 500;
```

Two choices in this design apply to any large deployment: storing embeddings as `halfvec` halves their size compared with `vector`, and partitioning lets a query skip every partition its `partkey` condition excludes.

<a id="enabling-environmental-action-at-scale"></a>

## Learn more {#learn-more}

- [Earth Index](https://www.earthgenome.org/earth-index) and its [waitlist](https://app.earthindex.ai/waitlist/).
- To filter vector search by other columns, see [vchordrq index](/docs/vchord/usage/indexing/#filter-keys).
