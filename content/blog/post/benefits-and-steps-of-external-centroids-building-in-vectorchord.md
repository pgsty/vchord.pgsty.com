---
title: "Benefits and Steps of External Centroids Building in VectorChord"
date: 2024-12-10
description: "Enhance vector search efficiency with external centroids building in VectorChord using external resources and hierarchical K-means"
author: "[Keming Yang](https://github.com/kemingy) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "vectorsearch"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/benefits-and-steps-of-external-centroids-building-in-vectorchord"
upstream_copyright: "© 2024 Keming Yang (TensorChord Inc.)"
math: true
aliases:
  - "/blog/benefits-and-steps-of-external-centroids-building-in-vectorchord/"
  - "/benefits-and-steps-of-external-centroids-building-in-vectorchord/"
---

Clustering is an important component in vector search, and the k-means algorithm remains one of the most widely used techniques. However, its simplicity comes with a significant drawback: resource-intensive computation can render it impractical for large datasets. This blog explores why this challenge arises and how leveraging external builds to overcome it. We also share insights into our approach to implementing this solution.

### Why we need it

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711948118/a8ca38d3-580f-4f20-90b9-03c826289a7c.png)

VectorChord uses IVF + RaBitQ to perform vector search. The quality of the IVF cluster can heavily affect search precision and speed. K-means usually takes dozens of rounds before convergence. For each round, all the sampled vectors need to be assigned to the nearest cluster. This is the most computationally intensive part. The good news is that this process can be easily parallelized.

However, the vector search instances usually don’t have such kind of resources to perform this parallel computation, doing so can dramatically affect the vector search service. In this case, it’s natural to utilize external instances to accelerate the indexing phrase.

### External K-means

The source vectors could be several times larger than the instance memory. To avoid out-of-memory, we can sample the vectors before clustering them. A good choice of cluster number is:


$$
4 * \sqrt{n_{vec}} \le n_{cluster} \le 8 * \sqrt{n_{vec}}
$$


Usually, we need to sample at most `256 * n_cluster` vectors. This can be done by reservoir sampling if the data can not fit into the memory.

If you have a ready-to-use GPU environment, it can run tens or even hundreds of times faster than a CPU instance. Otherwise, you may find that half or most of the time is spent on spawning instances, transferring data, and sampling instead of computing.

The following clustering experiments are performed on an `H100 SXM5` instance with `faiss-gpu (max_iter=25)`, which costs $3.29 / hr. Comparing to an `i4i.8xlarge` instance with `faiss-cpu (max_iter=25)`, which cost $2.746 / hr. CPU instances are about **60** times more expensive to cluster than GPU instances.

| **Dataset** | **Cohere** (1024 × 10m) | **MS MARCO** (768 × 100m) |
| --- | --- | --- |
| `n_cluster` | 16384 | 65536 |
| GPU K-means time | 80s | 960s |
| CPU K-means time | 5850s | 68420s |

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711341914/feb175a8-7c40-446e-91ac-ebb5c2ef9fb0.png)

> [!TIP]
> Stay tuned for our upcoming cloud support of external builds.

It is obvious that a larger `n_cluster` results in an exponential growth of time. Also, K-means can not maintain a relative balance if the `n_cluster` is large.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711427796/555454cf-f0d7-472f-b3cc-dc5f563c52c9.png)

A good way to overcome this is the hierarchical K-means. Usually, 2 layers are enough. We could build a `n_cluster = [40, 100]` hierarchical K-means instead of `n_cluster = 4000`. This also trades the heavy computation for IO and light computation, and it’s a good choice when you want to use CPU instances for large datasets.

<a id="Steps"></a>
### Steps

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1733711098280/7498c023-1b42-4cbc-b8b8-b247eb97baaf.png)

Assuming we already have the vectors stored in VectorChord, we will need to:

1. export the vectors and upload them to S3
    
2. spawn an instance to run the K-means clustering
    
3. insert the centroids back into the VectorChord
    
4. build the index with an external centroids table
    

We provide some scripts to make it easy to get started:

[External Build Documentation](/docs/usage/external-build/)

You can clone the repo and try it by yourself:

```bash
gh repo clone tensorchord/VectorChord
cd VectorChord/scripts
# export embeddings to a h5 file
python dump.py -n [table name] -c [column name] -d [dim] -o export.hdf5
# upload to s3
aws s3api put-object --bucket external-centroids --key export.hdf5 --body export.hdf5
# download in the CPU/GPU worker
aws s3api get-object --bucket external-centroids --key export.hdf5 export.hdf5
# run K-means with CPU
python train.py -i export.hdf5 -o centroid.npy -lists [lists]
# or with GPU
python train.py -i export.hdf5 -o centroid.npy -lists [lists] -g
# insert to the centroids table & build the index
python index.py -n [table name] -i export.hdf5 -c centroid.npy -d [dim]
```

<a id="Summary"></a>
### Summary

In conclusion, leveraging external centroids building in VectorChord offers significant advantages for handling large datasets in vector search. By utilizing external resources for the computationally intensive K-means clustering, we can enhance the efficiency and precision of the search process. This approach not only mitigates the resource constraints of vector search instances but also allows for faster processing times, especially when using GPU environments. Using hierarchical K-means further optimizes the process by balancing computation and I/O operations, making it feasible to use CPU instances for extensive datasets.
