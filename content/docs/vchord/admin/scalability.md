---
title: "Scalability"
linkTitle: "Scalability"
description: "Serve more vector queries per second by adding PostgreSQL streaming replicas, and how many replicas LAION-5M and LAION-100M needed to reach 10,000 QPS."
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/scalability.md"
aliases:
  - "/docs/admin/scalability/"
  - "/vectorchord/admin/scalability/"
icon: fa-solid fa-up-right-and-down-left-from-center
---

When one server cannot answer vector queries fast enough, add read replicas. vchord writes every index change to the WAL, so each streaming replica holds the same index as the primary and can answer the same queries; adding replicas adds query throughput without a separate vector database. This page sets this up on CloudNativePG and then shows how many replicas two LAION datasets needed to pass 10,000 queries per second.

<a id="Background"></a><a id="background"></a>

## How it works {#architecture}

The primary takes all writes and index builds. Replicas replay its WAL, including vchord's index pages, and a connection pooler spreads read-only queries across them. Each replica answers from its own buffer cache, so for peak throughput give every replica enough memory to hold the index and the vectors it reranks.

<img src="/docs/images/scalability-architecture.png" alt="Applications send queries through a read-only PgBouncer pooler to several PostgreSQL replicas that stream WAL from one primary" width="100%" />

Any streaming replication setup works the same way, for example Patroni with HAProxy or PgBouncer in front. The steps below use [CloudNativePG](https://cloudnative-pg.io/) (CNPG), which the measurements on this page used.

## Set up read replicas on CloudNativePG {#setup}

1. Create a CNPG cluster with vchord, as described in [Kubernetes](/docs/vchord/admin/kubernetes/). `spec.instances` counts the primary, so `instances: 3` gives two replicas.

1. Add a read-only pooler. CNPG runs PgBouncer and routes its connections to replicas only:

   ```yaml
   apiVersion: postgresql.cnpg.io/v1
   kind: Pooler
   metadata:
     name: vchord-pooler-ro
   spec:
     cluster:
       name: vchord
     instances: 2
     type: ro
     pgbouncer:
       poolMode: transaction
       parameters:
         max_client_conn: "1000"
         default_pool_size: "50"
   ```

   Applications send vector queries to the `vchord-pooler-ro` service and everything else to `vchord-rw`.

1. Store the search parameters on the index. In transaction pooling a session `SET` does not follow the client to the next transaction, so an index-level value is the one every query sees. Run this on the primary; replicas receive it through the WAL:

   ```sql
   ALTER INDEX items_embedding_idx SET (probes = '20', epsilon = 1.0);
   ```

   Choose the values with the [tuning loop](/docs/vchord/usage/indexing/#tuning).

1. Scale the number of replicas. A new replica copies the primary's data directory, index included:

   ```bash
   kubectl scale cluster vchord --replicas=8
   ```
{.steps}

## Results {#results}

[Vector Search at 10,000 QPS in PostgreSQL](/blog/vector-search-at-10000-qps-in-postgresql-with-vectorchord/) (February 2025) ran this setup on AWS EKS. Each replica had enough memory to hold its dataset. A 16-vCPU `r7i.4xlarge` client in the same availability zone sent top-10 queries with 16 to 128 concurrent workers to the read-only pooler; the primary was idle.

| | LAION-5M | LAION-100M |
| --- | --- | --- |
| Vectors | 5,000,000 × 768 dimensions | 100,000,000 × 768 dimensions |
| Replica instance | `r7i.xlarge`: 4 vCPU, 32 GiB | `r7i.16xlarge`: 64 vCPU, 512 GiB |
| `probes` / `epsilon` | `'20'` / `1.0` | `'20'` / `1.0` |
| Top-10 recall | 0.9324 | 0.9042 |
| Replicas for 10,000 QPS | 7 | 2 |
{.wide}

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="Throughput by number of client workers: LAION-5M with 5, 7, 11, and 15 r7i.xlarge replicas, and LAION-100M with 2 r7i.16xlarge replicas" width="100%" />

Throughput depends on client concurrency as much as on replica count. At 16 workers every LAION-5M configuration stays near 3,000 QPS, because the client is the limit. Seven replicas reach 10,000 QPS at 100 and 128 workers, and 15 replicas reach about 13,500 QPS at 128 workers. The two LAION-100M replicas peak near 10,000 QPS at 110 workers and drop below it at 128.

<a id="cost"></a><a id="summary"></a>

At the on-demand prices quoted in the post, the replicas for 10,000 QPS cost:

| Dataset | Replicas | vCPUs | Monthly cost |
| --- | --- | --- | --- |
| LAION-5M | `r7i.xlarge` × 7 | 28 | $0.2646 × 7 × 720 h = $1,334 |
| LAION-100M | `r7i.16xlarge` × 2 | 128 | $4.2336 × 2 × 720 h = $6,096 |
{.wide}

The primary is not included.

## Limits {#limits}

- Replicas add read throughput only. Writes and index builds run on the primary, and a new index reaches the replicas as WAL, so building one also costs replication bandwidth.
- A replica returns rows once it has replayed them. A client that must see its own just-inserted rows reads from the primary.
- Install the same vchord version on every node, with `vchord` in `shared_preload_libraries`. Without it, queries on that node fail with `vchord must be loaded via shared_preload_libraries.`
- Each replica has its own cache. After a restart or failover, the first queries on that replica read from disk; run `SELECT vchordrq_prewarm('items_embedding_idx');` on it to load the index first.
