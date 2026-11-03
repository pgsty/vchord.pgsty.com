---
title: "Why HNSW is Not the Answer"
date: 2024-12-18
description: "HNSW (Hierarchical Navigable Small World) has become the go-to algorithm for many vector databases. Its multi-layered graph structure and ability to…"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
upstream_link: "https://blog.vectorchord.ai/why-hnsw-is-not-the-answer"
upstream_copyright: "© 2024 Jinjing Zhou (TensorChord Inc.)"
aliases:
  - "/blog/why-hnsw-is-not-the-answer/"
  - "/why-hnsw-is-not-the-answer/"
authors: ["jinjing-zhou"]
images: ["/blog/covers/why-hnsw-is-not-the-answer.png"]
---

HNSW (Hierarchical Navigable Small World) has become the go-to algorithm for many vector databases. Its multi-layered graph structure and ability to efficiently navigate vector embeddings make it particularly appealing. However, despite its apparent advantages, HNSW may not be the optimal solution for large-scale and dynamic vector similarity search. In this blog post, we challenge the dominance of HNSW and explore why disk-based alternatives, such as IVF (Inverted File Index), might be more practical for massive datasets.

---

## The Appeal of HNSW

HNSW offers several advantages:

* **Efficient Search**: Its graph-based structure enables quick nearest-neighbor searches, especially for smaller datasets.
    
* **Incremental Updates**: The ability to add new vectors incrementally without needing to rebuild the index is a major benefit for dynamic environments.
    
* **High Recall**: HNSW delivers high recall with relatively low latency, making it an ideal option for real-time applications.
    

However, these benefits come with trade-offs that become more noticeable as dataset sizes increase.

---

## The Problem of HNSW

One of the main challenges of HNSW is its significant dependence on memory for indexing and search operations. Here are the primary issues that emerge:

* **Memory Overhead**: Traversing HNSW’s graph structure involves highly random access patterns. The entire dataset must be stored in memory to achieve reasonable performance. This becomes infeasible for large-scale datasets with billions of high-dimensional vectors due to exorbitant memory requirements.
    
* **Performance Sensitivity to Memory Size**: HNSW’s performance degrades sharply if the memory is even slightly insufficient to hold all vectors. In such cases, swapping data to disk drastically impacts search speed, making it impractical for systems with constrained memory.
    
* **Unsuitability for Disk-Based Environments**: HNSW is fundamentally designed for in-memory operations and performs poorly in disk-oriented scenarios, such as PostgreSQL. Its reliance on frequent random access patterns makes it incompatible with the sequential access nature of disk storage.
    
* **Insertion and Deletion Costs**: Updating the index in HNSW involves cascading modifications throughout the graph, leading to significant computation and write amplification. This makes insertion and deletion operations both slow and resource-intensive.
    

In contrast, disk-based solutions like IVF excel in scenarios requiring scalability and efficiency at the cost of minimal complexity.

---

## Why IVF Can Be Faster Than HNSW

![https://www.researchgate.net/publication/357875438/figure/fig15/AS:1113078611607560@1642390029247/Two-state-of-the-art-ANN-indexing-methods-the-IVF-index-Left-and-the-three-layer.ppm](https://cdn.hashnode.com/res/hashnode/image/upload/v1743668669763/0c5b4200-14dc-41ea-8f48-9160d0a26830.png)

A critical observation across all vector search algorithms is that their performance largely hinges on the number of distance computations they perform. Minimizing these computations is essential for improving search speed. Although the original IVF index required scanning 1% to 5% of the total vectors, modern advancements in quantization and optimization have significantly enhanced its efficiency, making IVF a strong competitor to HNSW.

### Quantization: The Game Changer

Quantization compresses high-dimensional vectors into compact representations. For instance:

* **RaBitQ**: Leverages concentration of measure phenomena to enhance binary and scalar quantization accuracy, quantizing each dimension into 1 bit for a 32x compression ratio.
    
* **Product Quantization (PQ)**: Works by dividing the vector space into subspaces, quantizing each subspace independently to minimize approximation error. This method offers flexible compression ratios from 4x to 64x in FAISS, enabling finer compression and faster approximate searches.
    
* **Scalar Quantization (SQ)**: Quantizes each vector dimension independently by dividing its range into discrete levels, typically achieving a 4x compression ratio by converting from float to int8.
    
* **ScaNN**: Uses anisotropic vector quantization to optimize inner product accuracy by penalizing errors in directions that impact high inner products, achieving superior recall and speed.
    

Quantization reduces memory and disk space usage significantly—often by a factor of 32x when converting floats into bits—while drastically lowering computational overhead. Despite some loss of precision, quantization makes vector comparisons far more efficient. For example, by compressing floating-point numbers into bits, this complexity is reduced by a factor of 32. Additionally, binary operations are generally more efficient compared to floating-point operations, further enhancing performance. With fast-scan optimizations, these computations are further accelerated via efficient CPU register lookups. Combined with IVF, many quantization methods consistently outperform HNSW in both speed and scalability. The typical workflow involves:

1. **Initial Search**: Leveraging compressed representations to rapidly identify candidate vectors.
    
2. **Reranking**: Refining results using full-precision distance calculations on a smaller subset of candidates.
    

<a id="comparing-rabitq-ivf-and-hnsw"></a>
### Comparing RaBitQ+IVF and HNSW

IVF with quantization provides a highly efficient way to store all quantized vectors in memory. By leveraging RaBitQ, memory usage is reduced by a factor of 32 compared to full-size vectors, allowing the entire quantized dataset to fit in memory. This design enables the index to rapidly retrieve approximate nearest neighbors using bit vectors and rerank them with full-precision vectors fetched from disk. For a typical Top-10 query, IVF fetches only 100-200 vectors from disk, compared to HNSW, which may require 800-1000 vectors. This efficient approach achieves an optimal balance between memory usage and disk access, offering outstanding cost-performance benefits.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1734489380210/a2812b59-5ffd-4ee3-ac35-1681950ef550.png)

While similar quantization techniques could theoretically be applied to HNSW, practical constraints reduce their effectiveness:

* **Vector Packing**: Fast scan optimization relies on packing 32 compressed vectors together, which is incompatible with HNSW’s graph structure.
    
* **Random Access Costs**: HNSW involves frequent random access across graph nodes and edges, making traversal inefficient. In contrast, IVF organizes vectors sequentially in posting lists, enabling faster prefetching and efficient sequential scans.
    
* **Reranking Costs**: Both IVF and HNSW share similar reranking computational costs due to their reliance on quantized representations in the first stage.
    

Ultimately, the performance difference between quantized IVF and HNSW is likely minimal, but IVF stands out with its simplicity and efficiency.

---

| Feature | IVF | IVF + RaBitQ | HNSW |
| --- | --- | --- | --- |
| Indexing Method | KMeans can be offloaded to GPU | KMeans + Quantization | Nearest Neighbor Graph, need to keep everything in memory |
| Overlapped Data Across Query | Centroids | Quantized vectors | No |
| Scalability | Limited by CPU and memory | Outstanding | Limited by memory |
| Insertion/Deletion | Simple (updates posting lists) | Simple (updates posting lists) | Complex (cascading graph changes) |
| Search Speed | Slow | Extremely Fast with Quantization | Fast with sufficient memory |
| Overall Complexity | Low | Low | High |
{.wide .expand}

---

## Operational Simplicity of IVF

IVF’s simplicity makes it a more practical choice for real-world applications:

* **Insertion and Deletion**: In HNSW, these operations trigger cascading modifications throughout the graph, resulting in significant computation and write amplification. IVF, in contrast, only requires updating the relevant posting list.
    
* **Disk-Based Storage**: IVF’s reliance on disk-based indexing enables it to scale efficiently without the prohibitive memory costs associated with HNSW.
    
* **Adaptability**: IVF can be easily combined with advanced quantization techniques, enabling further optimizations.
    

---

<a id="Conclusion"></a>
## Conclusion

While HNSW has solidified its reputation as a fast and accurate algorithm for vector similarity search, it is not without limitations. Its memory-intensive nature and operational complexity make it less suitable for large-scale applications. In contrast, IVF offers a scalable and cost-effective alternative, particularly when paired with modern quantization techniques.

As the demand for vector search continues to grow, practitioners must carefully evaluate the trade-offs between memory-based and disk-based solutions. HNSW may dominate small to medium-scale applications, but for massive datasets, it’s time to look beyond HNSW and embrace simpler, scalable approaches like IVF.

If you're interested in such databases, check out VectorChord.

%[https://github.com/tensorchord/VectorChord/]
