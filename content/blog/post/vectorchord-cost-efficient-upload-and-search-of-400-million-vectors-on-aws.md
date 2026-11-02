---
title: "VectorChord: Cost-Efficient Upload & Search of 400 Million Vectors on AWS"
date: 2025-05-30
description: "Upload, index, and search 400M vectors with VectorChord and PostgreSQL. Includes hardware tips and search performance advice"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws/"
  - "/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws/"
authors: ["junyu-chen"]
images: ["/blog/covers/vectorchord-cost-efficient-upload-and-search-of-400-million-vectors-on-aws.png"]
---

In this article, we will describe one method for uploading, indexing, and searching a big dataset of vector data in a cost-efficient manner using the real-world [LAION-400M](https://laion.ai/blog/laion-400-open-dataset/) dataset and the VectorChord extension in PostgreSQL.

We're attempting to show you what kind of hardware setup you need to allow you to search through this vast dataset using VectorChord. We want to make sure that you have a good experience with a search that is both accurate and fast.

[VectorChord](/docs/vchord/) is a PostgreSQL extension that may bring high-performance vector database capabilities directly into your PostgreSQL database with high compatibility with the popular pgvector extension's interface where possible.

The version of VectorChord to be used for this tutorial must be `v0.3.0` or later. While VectorChord is compatible with most of the recent pgvector versions, `pgvector 0.8.0` was extensively tested.

## **Dataset**

The dataset used for this experiment is [LAION-400M](https://laion.ai/blog/laion-400-open-dataset/), which is a dataset with approximately 400 million vectors derived from images. Each vector is 512-dimensional and was generated from a [CLIP](https://openai.com/blog/clip/) model.

The total vector data is approximately 400 GB. The vectors have been normalized, so it is feasible to use multiple distance measures (L2, cosine, dot product). To be consistent with other benchmarks on this dataset and following the nature of CLIP embeddings, we employed the cosine distance measure in this experiment.

LAION-400M is divided into 409 chunks, each containing around 1 million vectors. We will process these chunks sequentially for uploading.

## **Algorithm**

Searching through 400 million vectors is a huge challenge, especially as the data size means much of it must live on disk rather than in memory. We need algorithms built for this scale! A popular and effective method for handling large, disk-based vector data is the graph-based [DiskANN](https://github.com/microsoft/DiskANN), known for its **Low memory and resource cost**.

However, being derived from [HNSW](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world), DiskANN also has some inherited disadvantages:

* **Slow** [**index building**](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#experience-in-index-building): For large scale datasets, it's well known that building indexes with DiskANN can take a long time.
    
* **Poor** [**insert performance**](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#insertion-performance-for-stream-generated-data): For streaming inserted vectors, updating a graph-based index requires traversing the partial graph. This is even more costly because DiskANN's on-disk graph must be loaded into memory.
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743503547507/9847a9c4-fcaa-4d76-bf82-3f5c5e959ef4.png?auto=compress,format&format=webp)

VectorChord addresses these problems with its VChordRQ index, which combines a **cluster-based index (ivf)** with a clever data compression scheme called [RabitQ](https://arxiv.org/abs/2405.12497). In addition to **better precision and latency** in both [memory](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#vectors-in-memory-for-small-scale-data) and [disk](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/#vectors-in-disk-for-large-scale-data), RabitQ's strength lies in its strong theoretical guarantee of accuracy, which is different from other compression techniques. This helps us achieve an excellent trade-off between accuracy and efficiency!

> [!TIP]
> For more comparisons with VChordRQ([VectorChord](/docs/vchord/)), HNSW([pgvector](/docs/vector/)) and StreamDiskANN([pgvectorscale](https://github.com/timescale/pgvectorscale)), please see our previous [blog](/blog/post/vector-search-over-postgresql-a-comparative-analysis-of-memory-and-disk-solutions/).

## **Hardware**

Based on our experiments, we determined the following cloud instance type to be sufficient to index and query the dataset with acceptable latency:

* **Instance Type:** AWS EC2 i8g.2xlarge ($501.0720 / month)
    
* **CPU:** 8 vCPUs (ARM64)
    
* **RAM:** 64GB
    
* **Storage:** 1875 GB NVMe SSD
    

This configuration provides the necessary compute and ample fast local NVMe storage. The 64GB of RAM serves as cache to accelerate search queries.

> [!TIP]
> We used an instance with **1875 GB** NVMe storage, though only about **1014 GB** was needed. This was the **minimum** AWS option providing sufficient fast local SSD. Finding a machine with less storage could reduce costs.

For the PostgreSQL setup within this instance, we adjusted the `shared_buffers` parameter:

* Set to 48GB during the index building process.
    
* Increased to 54GB for search evaluation to allow more data caching for search performance.
    

## **Uploading and Indexing**

The VectorChord VChordRQ index uses an Index-based Vector File (IVF) structuring. While VChordRQ can compute the required centroids during the index building process, the building of an index of this size (400M vectors) pre-calculating the centroids out of the system significantly accelerates the process of building an index.

For LAION-400M, we performed an external k-means clustering step to determine these centroids. This was done on an instance with an `A10 GPU` for faster computation.

* The clustering was configured for `nlist = 160000` clusters.
    
* The clustering took approximately 220 seconds per iteration for 25 iterations, totaling about 1.5 hours.
    

Once we have computed the centroids, we set up the VectorChord-enabled PostgreSQL database. We used a pre-built Docker image for convenience:

```sql
-- Mount PGDATA path to the NVMe SSD
-- sudo mount /dev/nvme1n1 /data
docker run --name vchord-pg17 \
-e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -v /data/pg:/var/lib/postgresql/data \
-d tensorchord/vchord-postgres:pg17-v0.3.0
```

This Docker image contains `PostgreSQL 17` with `pgvector 0.8.0` and `VectorChord 0.3.0` installed.

The core of the upload process involves inserting the pre-computed centroids into a dedicated table and then inserting the vectors from the LAION dataset chunks into the main data table. This can be done efficiently using a client library like psycopg in Python with batched inserts.

First, insert the centroids into a table (e.g., laion\_centroids):

```sql
-- The centroids table we created is:
-- CREATE TABLE laion_centroids (id SERIAL PRIMARY KEY, vector vector(512));
INSERT INTO laion_centroids (vector) VALUES ('[...centroid vector...]'); -- Insert all 160000 centroids
```

Then, insert the vectors from the dataset into the data table (e.g., laion):

```sql
-- The data table we created is:
-- CREATE TABLE laion (id BIGINT PRIMARY KEY, embedding vector(512));
-- Note: VectorChord is compatible with pgvector's vector insert syntax.
INSERT INTO laion (id, embedding) VALUES (0, '[...vector data...]'); -- Batch inserts for chunks
```

After inserting all data, we build the VectorChord index (vchordrq). vchordrq stands for [RabitQ](https://arxiv.org/abs/2405.12497), which is VectorChord's highly optimized index type based on the IVF structure combined with quantization and efficient reranking.

```sql
-- Note: The metric operator vector_cosine_ops is specified here, similar to pgvector. 
-- The $$ syntax is used to pass build options as a text block.
CREATE INDEX laion_embedding_idx ON laion USING vchordrq (embedding vector_cosine_ops) WITH (options = $$
[build.external]
table = 'public.laion_centroids' -- Link to the pre-computed centroids
$$);
```

The image below shows the system resource utilization (CPU, memory, and disk usage) on the instance during the upload and indexing process. The disk usage graph shows the data being written (initial steep increase) and the subsequent index building (steady increase), resulting in a final size over 1TB. The CPU and memory graphs indicate the resources consumed throughout this process.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1745721010613/c5d20e21-6c6f-43d4-a915-aa121497d496.png)

## **Ground Truth Data**

To correctly measure search performance and accuracy, comparing to ground truth is vital. The LAION data set comes without inherent ground truth. **We are in debt to the Qdrant team for having published the** [**ground truth data**](https://github.com/qdrant/laion-400m-benchmark/blob/master/expected.py) **they had prepared for their** [**tutorial**](https://qdrant.tech/documentation/database-tutorials/large-scale-search/) **on this dataset.**

Their methodology involved performing a full-scan nearest neighbor search for the first 100 vectors in the dataset to find the top 50 true nearest neighbors for each query. We **used this same exact ground truth file** to evaluate the VectorChord search accuracy.

## **Search Query**

VectorChord search employs two main parameters to control the performance-accuracy trade-off: nprobe and epsilon.

* **nprobe**: Configured using the `vchord.probes` setting. This parameter determines how many clusters (partitions) of the IVF index are searched in the initial phase. A higher nprobe increases the search scope, potentially finding better results but also increasing latency.
    
* **epsilon**: Configured using the `vchord.epsilon` setting. This parameter controls the reranking precision. After fetching the initial candidates from the nprobed clusters, VectorChord performs a reranking step using more precise vector data. A larger epsilon means more candidates are considered and potentially reranked for higher recall, impacting latency.
    

These parameters are set as PostgreSQL session variables before executing the search query:

```sql
-- Example settings
SET vchord.probes = 100; -- Configure nprobe
SET vchord.epsilon = 0.8; -- Configure epsilon

-- The search query itself uses the standard pgvector distance operator
SELECT id FROM laion ORDER BY embedding <=> '[...query_vector...]' LIMIT 50;
```

The ORDER BY embedding `<=> '[...]'` clause leverages the index to find the approximate nearest neighbors based on the specified distance metric (cosine distance, like CLIP). The LIMIT 50 retrieves the top 50 results.

## **Running Search Requests**

After the index built is finished, we ran queries over the 100 ground truth vectors with varying nprobe and epsilon settings to try out performance versus precision trade-offs.

We expressed search latency in milliseconds (ms). "Cold" latency refers to instances where vector data of interest may need to be read from disk, while "warm" latency implies that data will be in memory.

Here are the average latencies and corresponding Precision@50 scores across the 100 queries:

| **nprob / epsilon** | **Cold Latency (ms)** | **Warm Latency (ms)** | **Precision@50** |
| --- | --- | --- | --- |
| 10 / 0.8 | **112.5** | **7.0** | 0.8192 |
| 100 / 0.8 | 194.2 | 15.0 | 0.9216 |
| 200 / 1.0 | 331.2 | 24.9 | 0.9438 |
| 400 / 1.5 | 970.9 | 51.6 | **0.9608** |
| 800 / 1.9 | 2174.0 | 2174.0 | **0.9662** |

The table clearly illustrates the trade-off:

* Increasing `nprobe` and `epsilon` generally leads to higher Precision@50.
    
* However, this comes at the cost of increased search latency, especially noticeable in cold scenarios where more disk I/O is required to fetch data from more clusters and perform more extensive reranking.
    
* Warm cache performance is significantly faster, highlighting the importance of sufficient RAM for caching frequently accessed data.
    
* It is possible to have over 90% precision through warm latencies less than 50ms, and increasing precision above this yields hundreds of milliseconds or even more than a second latency for best recall, depending on the parameters selected.
    

The graph below shows the trade-off between Queries Per Second (QPS) and Precision@50 for VectorChord (cold and warm cache) alongside Qdrant, with Qdrant’s metrics taken from their [published benchmarks](https://qdrant.tech/documentation/database-tutorials/large-scale-search/#running-search-requests) on a comparable 8 vCPU, 64 GB machine rather than run on the same hardware.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1745753692001/731cb592-86e6-4eef-ae0f-c699df421a33.png)

## **Conclusion**

In this tutorial, we illustrated how VectorChord as an extension to PostgreSQL can be utilized to upload, index, and search a gigantic 400 million vector dataset cost-efficiently on relatively small hardware with fast NVMe SSD.

By using the VectorChord VChordRQ index with external centroids, we were able to handle the scale. Having carefully set `nprobe` and `epsilon` at query time provides precise control over the critical trade-off between search speed and accuracy, allowing users to tune the system to their specific needs.

VectorChord's compatibility with the pgvector interface simplifies adoption for current pgvector users, and its vchordrq index provides powerful capabilities for large-scale vector search directly within the robust and familiar PostgreSQL environment.
