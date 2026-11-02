---
title: "Vector Search Over PostgreSQL: A Comparative Analysis of Memory and Disk Solutions"
date: 2025-04-03
description: "Vector Search in PostgreSQL: Comparing VectorChord, pgvector, and pgvectorscale for Memory and Disk Performance"
author: "[Junyu Chen](https://github.com/cutecutecat), [xieydd](https://github.com/xieydd) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions"
upstream_copyright: "© 2025 Junyu Chen, xieydd (TensorChord Inc.)"
aliases:
  - "/blog/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/"
  - "/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/"
---

## Introduction: real-world challenges

Specialized vector databases aren’t always needed. With PostgreSQL extensions like [pgvector](https://github.com/pgvector/pgvector), [pgvectorscale](https://github.com/timescale/pgvectorscale), [VectorChord](https://github.com/tensorchord/VectorChord) (which evolved from [pgvecto.rs](/docs/vectors/))****, you get vector search *plus* relational power—no extra infrastructure. But adoption isn’t seamless. Here’s what real users say:

> * The query **takes 30 seconds** for the first time and 100ms if it's a repeat query. The problem is very slow IO.
>     
> * Is it normal to take 3 hours to build the index for 12 million rows with 75 dimension vector?
>     
> * After 13 hours of building index for 200 million vectors of 75 dimensions each, I have noticed a heavy memory usage at 100GB/124GB at 30% of building index, and server will eventually crash.
>     
> * We're hitting some challenges, particularly around need for frequent index updates, throughput constraints, lack of parallel index scans and no built-in quantization.
>     

In this article, we'll take a deep dive into these questions and help you make informed decisions by understanding not only the "what" but also the "**why**" behind these tools. Let's explore how to navigate these complexities and choose the right solution for your needs.

## What do we value most in a vector database?

> In PostgreSQL, [`shared_buffers`](https://www.postgresql.org/docs/current/runtime-config-resource.html#RUNTIME-CONFIG-RESOURCE-MEMORY) is a crucial memory area acting as the primary cache for data pages, *including table data and indexes*. By storing frequently accessed vector index blocks in this memory buffer, PostgreSQL significantly reduces slow disk I/O. When a query needs data, PostgreSQL first checks `shared_buffers`. If the data is present, it's retrieved quickly without disk access. If not, the data is fetched from disk and loaded into `shared_buffers` for future queries. To configure this, use `ALTER SYSTEM SET shared_buffers = 'xGB'` in psql and restart the server.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743385828242/4ae2279a-27d2-42ce-bb59-2b462a01e851.png)

Let's say you have some vectors in a table, after the index is built, it's time to start a query. Even though you have set enough `shared_buffers` for PostgreSQL, it still needs to read the index from disk for the `first query`. However, for the `repeated query`, since the vector can be retrieved directly from `shared_buffers`, it can be much faster.

While the `first query` after a cold start or index change matters, sustained performance often depends on how quickly queries execute once the 'hot' or frequently accessed parts of the index are cached in memory (shared\_buffers), mimicking the `repeated query` scenario. Therefore, optimizing for this cached performance is crucial for many real-world applications.

In this blog, we will compare the performance of vector similarity search extensions in these situations:

* Query performance when **memory** is sufficient
    
* Query performance when memory is low and **disk** becomes a bottleneck
    

We will also discuss other aspects related to index building, such as:

* `Index build speed`: How long does it take to build the index? If I have multiple cores in the instance, can it use them all to speed things up?
    
* `Memory usage`: How much memory should be reserved for index creation? This is the most important consideration when choosing an instance.
    
* `Disk usage`: How many vectors can be hosted on a given amount of disk space? This is also a consideration when choosing an instance that uses non-expandable NVMe SSD (a type of high-performance solid state drive) storage.
    
* `Ease of use`: Can I use a simple `CREATE INDEX` command to create an index? How difficult is it to tune for query performance?
    

Finally, we will discuss the `insertion performance` after index building is complete. This is important if the user has streamed data that will trigger frequent index updates.

## Experimental setup

Here we present information about the hardware and datasets used in all of the following experiments.

|  | **Vectors in memory** | **Vectors on disk** | **Index building** | **Insertion performance** |
| --- | --- | --- | --- | --- |
| Instance type | [`I4I Extra Large`](https://instances.vantage.sh/aws/ec2/i4i.xlarge) | `C6ID Large` | [`I4I Extra Large`](https://instances.vantage.sh/aws/ec2/i4i.xlarge) | [`I4I Extra Large`](https://instances.vantage.sh/aws/ec2/i4i.xlarge) |
| Vcpus | 4 | 2 | 4 | 4 |
| Storage | 937 GB NVMe SSD | 118 GB NVMe SSD | 937 GB NVMe SSD | 937 GB NVMe SSD |
| Memory | 32.0 GiB | 4.0 GiB | 32.0 GiB | 32.0 GiB |
| PostgreSQL shared\_buffers | 24.0 GiB | 2.0 GiB | 1.0 GiB | 24.0 GiB |
| Inserted rows | 5,000,000 | 5,000,000 | 5,000,000 | 100 after the index is created |
| Distance metric | L2 distance | L2 distance | / | / |
| Test queries | 10,000 | 10,000 | / | / |

In this table, we show the version of all the extensions we use in these experiments:

|  | Version | Image |
| --- | --- | --- |
| VectorChord | v0.2.2 | tensorchord/vchord-postgres:pg17-v0.2.2 |
| pgvector | v0.8.0 | tensorchord/vchord-postgres:pg17-v0.2.2 (`with a pgvector v0.8.0 installed`) |
| pgvectorscale | v0.6.0 | timescale/timescaledb-ha:pg17.4-ts2.18.2-oss |

## Vectors in memory: for small scale data

For a vector search system, if you want the best performance, it's important to make sure that the entire index is cached in `shared_buffers`, which is more appropriate on a memory-optimized instance. In this situation, the size of `shared_buffers` should ideal be large enough to hold the entire index.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743143311992/45b592c0-37f1-4cac-9e3a-370bc7f7bee4.png)

For our experiment, we choose a medium-sized dataset, [`LAION-5m`](https://github.com/myscale/benchmark/blob/4784b3820627c6bc458c1acf6a8cc48c8efba450/public/home.md#the-datasets-), which consists of 5 million vectors with 768 dimensions. To host `LAION-5m` in `shared_buffers`, we can use the AWS instance [`I4I Extra Large`](https://instances.vantage.sh/aws/ec2/i4i.xlarge), with a 937GB NVMe SSD and 32GB of memory.

On this machine, we set the `shared_buffers` to 24GB and measure the performance of the `first query` and then the `repeated query`. The following is the result of the `repeated query` performance over `pgvector`, `pgvectorscale` and `VectorChord`.

The following graphs illustrate the trade-off between query speed (QPS) and search quality (Recall@10/100). Recall@10 measures the percentage of true nearest neighbors found within the top 10 results. In general, higher QPS can be achieved at the cost of lower recall, and vice versa. A better system may achieve higher recall at the same QPS, or higher QPS at the same recall level. Our goal is typically to maximize QPS while maintaining a high recall target (e.g., 95%).

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743412050649/4def8f06-694a-4021-a306-a54da58ea6ab.png)

> [!DETAILS] Why VectorChord is so fast?
> VectorChord's [RabitQ](https://arxiv.org/abs/2405.12497) index achieves its speed through optimized vector compression, which allows for faster distance calculations. This compression technique minimizes data movement, resulting in efficient hardware utilization and improved query performance.

To measure first query performance, we cleared `shared_buffers` before running the 10,000 test queries sequentially. Although the buffer starts empty, index/data pages loaded into the cache by earlier queries within the **same test run** can sometimes be reused by subsequent queries. This can cause the instantaneous QPS to increase during the run. We report the **average** QPS across all 10,000 queries to provide a representative measure of performance with a cold cache.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743350840716/cf131853-8131-4676-8e80-2125632e9b56.png)

In conclusion, `VectorChord` consistently achieves higher QPS at high recall levels (e.g., &gt;95% Recall@10) compared to the other extensions. When it comes to the other extensions, `pgvectorscale` performs better for `first query`, but once data is cached, `pgvector` will outperform it.

## **Vectors in disk**: for large scale data

There are times when things are different. For billions of vectors, it is not possible to use memory to store the entire index on a single machine. When the size of the vectors to be read exceeds the size of memory, the speedup effect of `shared_buffers` is greatly reduced, and most of the data is fetched from disk.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743414426953/e512a560-e4f1-4f17-8307-ef823ad12086.png)

While `shared_buffers` becomes less effective, the operating system's page cache can still provide some caching benefits, although its performance is generally lower than `shared_buffers`.

> [!DETAILS] Indexing and Migration
> `VectorChord's internal build` and `pgvectorscale` require additional memory to build the index, so it is not possible to build the index on such a small instance with 4GB of memory. To solve this problem, we build the index on another `I4I Extra Large` instance with 24GB of memory, and then backup and restore the database data directory from `AWS S3` **for all extensions**.

To illustrate this situation, we can host `LAION-5m` on a much smaller machine, `C6ID Large`, with **4GB** of memory and set `shared_buffers` to **2GB**. This configuration ensures that memory will be insufficient and most queries will be forced to go to **disk**.

In these cases, the difference in performance between the `first and repeated queries` will be much smaller due to insufficient memory. Therefore, it's acceptable to evaluate only the `repeated query` performance of each extension.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743350651982/ae12fa1b-ae4a-435c-aa00-def89921992b.png)

As always, `VectorChord` consistently achieves higher QPS at high recall levels (e.g., &gt;95% Recall@10) compared to the other extensions, followed by `pgvector` and `pgvectorscale` with similar QPS.

## **Experience in index building**

As we discussed earlier, users also care about some index building metrics: Index build time, memory usage, disk usage and usability. We measured these metrics during the `CREATE INDEX` step of the above experiment on the `Laion-5m` dataset:

* `Core utilization`: Percentage of available CPU cores effectively used during index creation. Higher values indicate better parallelism.
    
* `Index build time`: The time taken by the SQL command to build the index. If the index build requires an additional step (`VectorChord external build`), this should also be included.
    
* `Memory usage`: **Peak** memory usage during the index build, including the 1G `shared_buffers` allocated for PostgreSQL.
    
* `Disk usage`: The size of `PGDATA` on disk after index building is finished, including vectors and the index.
    

> [!DETAILS] External build vs internal build in VectorChord
> Vectorchord supports two different ways of build indexing, `internal build` and `external build`. While internal build is similar to pgvector and pgvectorscale, external build requires an additional `k-means` clustering. External build usually has **better query performance** in query and it's the recommended way for indexing large vectors. If you want to know more about external build in VectorChord, please read our previous [blog](/blog/post/benefits-and-steps-of-external-centroids-building-in-vectorchord/).

All query performance is measured after an **external build**, on a standalone machine with `A10 GPU`. If you insist on using the same `I4I Extra Large` instance for external builds, the index build time will increase to 50 minutes, which is still competitive.

In this case, we set `shared_buffers` to 1GB and logged the peak memory usage of each extension. Both `VectorChord's internal build` and `VectorChord's external build` are set to **25 iters** for K-means clustering. For ease of use, `pgvector`, `pgvectorscale` and `VectorChord's internal build` have similar syntax with a single SQL to build the index, while `VectorChord's external build` is more complicated.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743503547507/9847a9c4-fcaa-4d76-bf82-3f5c5e959ef4.png)

For most aspects, `VectorChord's external build` gained a leading position, but this partly sacrificed the ease of use, as developers need to **implement an additional K-means clustering step outside of PostgreSQL** and manage the resulting centroids.

If you want to start with a simple `CREATE INDEX` command for a straightforward approach, then `VectorChord's external build` may not be the best choice , you can turn to other extensions / methods:

* Choose `VectorChord's internal build` for a faster index build
    
* Choose `pgvector` if you really don't have enough memory
    
* Choose `pgvectorscale` to reduce disk requirements or get better capacity
    

## Insertion performance: for stream-generated data

With streaming vector data, insertion speed can become a new concern. In real-time data analysis systems, the number of new vectors written per second can be very high. Each time new vectors are added to an index, the index itself must be updated. This capability is usually referred to as `insertion performance`.

> [!DETAILS] Why there is difference in insertion performance between indexes?
> For graph-based indexes(pgvector hnsw, pgvectorscale), an index update usually performs multiple searches in the graph and creates new edges for the inserted vector. While clustering-based indexes(VectorChord) just find the right group and add the new vector to it.

So, we set up an experiment to see how well the insertion worked. After building the index for 5 million vectors, we insert another 100,000 random generated vectors into the table one after the other and calculate the insertion time of all.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743497738743/68305934-b301-4f53-85ae-d614eb070577.png)

As you can see, VectorChord (**1565 Insert/Sec**) performs much better than pgvector (**246 Insert/Sec**) and pgvectorscale (**107 Insert/Sec**) when inserting data. For most workloads, 100 Insert/Sec is more than enough. However, if you find that a lot of vectors are continuously inserted in your production (for example, **500 Insert/Sec**), this could be a problem.

<a id="Summary"></a>
## Summary

Based on the results above, this table shows the differences between the three extensions in various aspects. We can see that the main advantage of `VectorChord` is concentrated in **performance**, while `pgvector` and `pgvectorscale` have their own advantages in terms of **usability** and **capacity**.

If you want to see more detailed differences, this table shows them between the three extensions in various aspects. We can see that the main advantage of `VectorChord` is concentrated in **performance**, while `pgvector` and `pgvectorscale` have their own advantages in terms of **usability** and **capacity**.

|  | pgvector | pgvectorscale | VectorChord |
| --- | --- | --- | --- |
| Ease of use | **Easy** | **Easy, similar to pgvector** | **Easy** (internal), hard (external) with 2-stage build |
| Max dimension can index | 2000 | **16000** | **16000** |
| Ease of tuning | **Easy** | Moderate, need manually tune query\_rescore for different queries | **Easy** |
| Highest Achievable Recall | Bottom-tier | Mid-tier | **Top-tier** |
| QPS of repeated query | Mid-tier | Bottom-tier | **Top-tier** |
| QPS of first query | Mid-tier | **Top-tier** | **Top-tier** |
| QPS of disk index | Mid-tier | Mid-tier | **Top-tier** |
| Speed of index building | Mid-tier, support multiple cores | Bottom-tier, does not support multiple cores | **Top-tier, support multiple cores** |
| Peak Index Build Memory Usage | **2.1 GB** | 15.2 GB | **1.1 GB** (external), 9.8 GB (internal) |
| Total Disk Usage | Nearly largest | **Smallest** | Largest |

Want to know more about how VectorChord compares to other extensions? In future blogs, we will explore the differences of PostgreSQL vector extensions in more scenarios, such as [**bm25 hybrid search**](/blog/post/vectorchord-bm25-revolutionize-postgresql-search-with-bm25-ranking-3x-faster-than-elasticsearch/) (combining traditional keyword search with vector similarity search) and **filtered vector search**. Ready to try VectorChord for your vector search needs? Download the [extension](https://github.com/tensorchord/VectorChord) and feel free to join our [Discord community](https://discord.gg/KqswhpVgdU) or contact us at [support@tensorchord.ai](mailto:support@tensorchord.ai).

%[https://github.com/tensorchord/VectorChord]
