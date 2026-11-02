---
title: "VectorChord: Store 400k Vectors for $1 in PostgreSQL"
date: 2024-12-05
description: "Introducing VectorChord: The successor to pgvecto.rs. Using VectorChord, you can achieve a QPS of 131 with 0.95 precision on 100 million 768D dataset"
author: "Ce Gao, Jinjing Zhou, Junyu Chen"
tags:
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-store-400k-vectors-for-1-in-postgresql"
aliases:
  - "/blog/vectorchord-store-400k-vectors-for-1-in-postgresql/"
  - "/vectorchord-store-400k-vectors-for-1-in-postgresql/"
---

We’re pleased to announce our new vector search extension for PostgreSQL, providing a highly cost-effective way to manage large vectors. Using [VectorChord](https://github.com/tensorchord/VectorChord), you can achieve a QPS of 131 with 0.95 precision on 100 million 768-dimensional vectors for the top 10 queries. This setup costs only $250 monthly and can be hosted on a single machine.

This means you can **store 400k vectors for only $1**, allowing you to save significantly: 6x more vectors compared to Pinecone (storage optimized instance) and 26x more than pgvector/pgvecto.rs for the same price.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733194327962/8b0f2610-af64-4104-98db-7f94416f354e.png)

In the monthly cost comparison for storing vectors, based on [MyScale benchmark data](https://myscale.github.io/benchmark/#/), the chart highlights how [VectorChord](https://github.com/tensorchord/VectorChord) emerges as an affordable option, priced at just $247 for storing 100 million vectors. In contrast, Pinecone, despite its optimized storage, costs $1,600 per month, while Qdrant is priced at $4,374. pgvector/[pgvecto.rs](/pgvecto-rs/) has a considerably higher cost of $6,580.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733194599461/eb1cf21d-4eb0-4427-8b39-bbb96d125182.png)

%[https://github.com/tensorchord/VectorChord] 

<a id="hnsw-s-problem"></a>
## HNSW’s problem

As the successor to pgvecto.rs, VectorChord has gained valuable insights from its predecessor. While many vector databases or extensions (including pgvecto.rs) perform well with datasets of around 1 million, they often struggle when scaling up to larger sizes, such as from 10 million to 100 million. Traditional HNSW-based vector databases face specific challenges with larger datasets:

* **Long index build time:** It typically takes over 2 hours to build an index for 5 million records.
    
* **High memory requirements:** Storing a dataset of 10 million vectors can require as much as 40GB of memory.
    

<a id="vectorchord-s-solution-disk-friendly-ivf-rabitq"></a>
## VectorChord’s solution: Disk-friendly IVF+RabitQ

VectorChord employs IVF (Inverted File Index) along with [RaBitQ](https://arxiv.org/pdf/2405.12497)\[1\] quantization to provide fast, scalable, and accurate vector search capabilities. This method **compresses 32-bit vectors into compact bit representations**, significantly reducing computation demands. Most comparisons are conducted using these compressed vectors, while full-precision calculations are reserved for an adaptive reranking phase applied to a smaller subset, ensuring both speed and recall are preserved.

Many people think that IVF has a less favorable recall/speed tradeoff than HNSW and involves many configurations for optimization. However, it's a complex issue, and we’ll explain it briefly now, with a detailed post on the topic coming later.

### IVF vs HNSW

A significant portion of the time taken by vector search algorithms is dedicated to distance computation. To enhance speed, it's essential to minimize distance comparisons as much as possible. The original IVF struggles in this area, usually necessitating a scan of 1% to 5% of the total vectors, which is considerably higher than what HNSW requires.

However, RabitQ presents an innovative approach that allows for the compression of a 32-bit vector into just 1 bit. While this compression results in some loss of precision, it greatly reduces computational requirements. With the fast scan optimization, we can achieve calculations that are **over 100 times faster than traditional vector distance computations**.

You might wonder about the recall. We can rerank additional vectors to enhance the recall rate, and full precision distance computation is only necessary during the reranking phase. RaBitQ guarantees a sharp theoretical error bound and provides good empirical accuracy at the same time. This is why IVF can be faster than HNSW.

Here are some initial benchmark results for the GIST dataset, which consists of 1 million vectors in 960 dimensions. With equivalent recall, VectorChord's QPS could be twice that of pgvector. More details will be provided in the Benchmark section.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288263095/3f2dcc75-a3e9-4d86-9515-7ab120f73c0c.png)

### External Index build

The original IVF method typically needs to scan 1–5% of the dataset, which can be slow. By using RaBitQ and fast scan optimization, VectorChord aims to speed up calculations by cutting down the number of full precision vectors that need to be fully compared. This approach helps create a stable and scalable vector search system that works well with the PostgreSQL storage system. As a result, users can use **physical replication and other PostgreSQL features** along with VectorChord.

Built on IVF, VectorChord **allows KMeans clustering to be conducted externally** (such, as on a GPU) and easily imported into the database. We performed tests to measure indexing and insert time on an AWS i4i.large instance, which has 2 vCPUs, and 16 GB of RAM. The dataset used for this test was GIST 1M. We inserted 700,000 vectors, built the index, and then added another 300,000 vectors. After warming up the system, we performed queries using a single thread. During this process, we evaluated both the index build time and the insert time. Here are the results:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733302602422/57f0e7d6-5f48-484f-ac2a-5e999b7cd0fe.png)

VectorChord takes 186 seconds to build the index by utilizing a separate machine for KMeans clustering, making it **16 times faster than pgvector**. Additionally, the insert time is also 14 times faster than that of pgvector. As we know, indexing is the most resource-intensive part of vector databases, requiring significant computation and increasing the demand for CPUs and memory. By utilizing a more capable machine to build the index and then importing it to a smaller machine for querying, it becomes possible to support billions of vectors on a single machine.

<a id="Benchmark"></a>
## Benchmark

We conducted additional experiments to assess performance and costs more thoroughly using the LAION 5M and 100M datasets.

### LAION 5M

We had an experiment using the LAION 5M dataset, and the results were encouraging for Vectorchord. It consistently achieved higher queries per second (RPS) compared to other platforms. While many databases struggle to maintain a balance between speed and accuracy as recall increases, Vectorchord managed to remain efficient even at higher recall levels. This characteristic could make it a suitable option for applications needing both quick responses and precision.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288538606/7f7ae3ef-5bda-4b3c-ace7-cf269511472f.png)

The experiment utilizes the [Myscale single thread benchmark](https://myscale.github.io/benchmark/#/), and we conducted it on an r6a.xlarge machine, which features 4 vCPUs, 32GB of memory, and 200GB of EBS storage. The parameters set for the experiment include an nlist of 8192, a shared buffer of 28GB, JIT disabled, and an effective I/O concurrency of 200. We ran the experiment twice without prewarming.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288473788/e47f3d44-84fc-4dc7-900b-a6b0cbe4db92.png)

The machine we used, an `r6a.xlarge`, costs around $165.56 per month, while the Zilliz Performance 4CU is priced at approximately $460 per month. Notably, we achieved comparable performance in the Top 100 on the LAION 5M dataset.

### LAION 100M, on a single machine

Furthermore, due to its disk-friendly indexing, increasing a single machine's disk capacity can proportionally enhance the maximum number of vectors VectorChord can hold, potentially allowing for storage of 1 billion or more.

To assess scalability, we performed experiments on the LAION 100M dataset (768 dimensions) using an AWS `i4i.xlarge` instance, which is an economical configuration priced at $250 per month.

[![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733213906554/5021cb87-7337-4fe3-b29f-7b0fd5f28a08.png)](https://instances.vantage.sh/aws/ec2/i4i.xlarge?region=us-east-1&os=linux&cost_duration=monthly&reserved_term=Standard.noUpfront)

It features just 4 CPUs and 32 GB of memory, with 937 GB of SSD used to store the 100 million vectors. In this setup, we achieved a QPS of 16.2 @ recall 0.95 for the top 10 results and 4.3 @ recall 0.95 for the top 100 results with a single-thread query. Here are the impressive results:

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733215378789/abdae62d-0085-4b38-97d3-43409d3d3f7b.png)

While maintaining a recall greater than 0.95, we also assessed the multi-thread QPS on this 4-vCPU machine. In this scenario, as the number of requested threads rises from 1 to 8, the QPS for vector queries can increase linearly. This indicates that VectorChord demonstrates excellent scalability.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733288585680/c6de7df3-facd-456c-8268-b6799586bc6c.png)

# Summary

VectorChord is a new PostgreSQL extension designed for efficient vector search. It allows users to store 400,000 vectors for just $1, significantly cheaper than competitors. By utilizing IVF and RaBitQ quantization, VectorChord optimizes search speed and memory usage, making it suitable for large datasets.

We offer cloud-managed services for VectorChord at [PGVecto.rs Cloud](/cloud/). Our platform simplifies deployment and management, enabling you to scale your vector database solutions with ease and efficiency. If you have any questions about VectorChord, please feel free to reach out. We're here to assist you! You can either open an issue in our repository or email us at [vectorchord-inquiry@tensorchord.ai](mailto:vectorchord-inquiry@tensorchord.ai).

%[https://github.com/tensorchord/VectorChord] 

# References

\[1\] Gao, Jianyang, and Cheng Long. "RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search." *Proceedings of the ACM on Management of Data* 2.3 (2024): 1-27.
