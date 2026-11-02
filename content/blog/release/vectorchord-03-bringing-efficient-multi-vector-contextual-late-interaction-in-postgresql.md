---
title: "VectorChord 0.3: Bringing Efficient Multi-Vector Contextual Late Interaction in PostgreSQL"
date: 2025-04-13
description: "VectorChord 0.3 boosts PostgreSQL vector search using MaxSim and WARP"
author: "Keming, Jinjing Zhou"
tags:
  - "release"
  - "multivector"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql"
math: true
aliases:
  - "/blog/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql/"
  - "/vectorchord-03-bringing-efficient-multi-vector-contextual-late-interaction-in-postgresql/"
---

We're thrilled to announce the release of **VectorChord 0.3**, a major milestone that significantly boosts the performance and applicability of advanced vector search techniques directly within your Postgres database! Building on our 0.2 release, which brought ARM support and faster indexing, version 0.3 tackles one of the biggest hurdles in modern retrieval: **efficient multi-vector search with late interaction**.

### Beyond Single Vectors: Why Multi-Vector Rocks

For years, vector search primarily represented entire documents or queries as single, dense vectors. While powerful, this approach involves averaging or compressing complex information into one representation, inevitably leading to a loss of nuance. Imagine trying to capture the entire meaning of a detailed technical document in a single sentence – you'd lose specifics!

Enter **multi-vector representations** and **late interaction**, pioneered by models like [**ColBERT**](https://github.com/stanford-futuredata/ColBERT). Instead of one vector per item, these models generate *multiple* vectors – often one for each token (word or sub-word). The real magic happens during the search process:

1. **Query Encoding:** Your search query is also broken down into multiple token vectors (let's call them q1, q2, ..., qN).
    
2. **Document Encoding:** Similarly, the document is represented by its token vectors (d1, d2, ... dM).
    
3. **Late Interaction & MaxSim Aggregation:** Instead of one comparison, we perform fine-grained matching. The core idea is the **Maximum Similarity (MaxSim)** operation. For *each query token vector* (like q\_i), we find the document token vector (d\_j) that has the *highest similarity* (e.g., cosine similarity or dot product) to it across *all* document tokens (d1 through dM). This process is repeated for every query token (q1, q2, ..., qN). The final relevance score for the document is then calculated by **summing up these maximum similarity values obtained for each query token**. This operation is inherently **asymmetric**, focusing on how well each part of the query is represented somewhere in the document.
    

**Why is this better?**

* **Contextual Nuance:** Late interaction with MaxSim allows the model to capture fine-grained semantic relationships. It can identify if *specific important terms* from the query strongly match *specific parts* of the document, rather than relying on a potentially diluted overall average similarity.
    
* **Improved Relevance:** By considering focused, token-level interactions and summing the best matches for each query term, models like ColBERT achieve state-of-the-art retrieval quality. This fine-grained approach is particularly powerful for content-rich queries with multiple terms, leading to a better understanding of user intent. On the [BEIR benchmark](https://huggingface.co/answerdotai/ModernBERT-base#base-models), this translates to a significant performance boost: With the same [ModernBert](https://huggingface.co/answerdotai/ModernBERT-base) model, Colbert variant achieves 51.6 NDCG@10 compared to 41.6 for dense vector variant.
    

Our previous blog post explored using ColBERT for reranking, showcasing its power:  
[**Supercharge Vector Search with ColBERT Rerank in PostgreSQL**](/blog/post/supercharge-vector-search-with-colbert-rerank-in-postgresql/)

<a id="vectorchord-0-3-bringing-efficient-maxsim-to-postgres-inspired-by-warp"></a>
### VectorChord 0.3: Bringing Efficient MaxSim to Postgres, Inspired by WARP

VectorChord 0.3 directly confronts the **high computational cost of late interaction**. We've integrated a highly optimized **multi-vector late-interaction MaxSim operator and index** into our core Rust engine, drawing inspiration from the groundbreaking **WARP engine** ([Paper: WARP: An Efficient Engine for Multi-Vector Retrieval](https://arxiv.org/abs/2501.17788), [Code: jlscheerer/xtr-warp](https://github.com/jlscheerer/xtr-warp)).

The genius of the WARP approach lies in a fundamental insight: the complex multi-vector MaxSim calculation (comparing N query vectors to M document vectors) can be cleverly **decomposed into multiple, independent single-vector search processes**. Instead of one massive N x M comparison, WARP effectively performs N separate searches, one for each query token vector, against the indexed document vectors to find its best match.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743730508359/1040ee64-6dd1-429c-bc6b-95184d7cf9dc.png)

Our core improvement in VectorChord 0.3's MaxSim scanner is built on this concept. We've implemented MaxSim by **leveraging and orchestrating VectorChord's existing, highly optimized single-vector search infrastructure**. When a MaxSim query is executed with an index, VectorChord performs **multiple single-vector searches**—one for each query vector—using our underlying index structures (**IVF combined with RaBitQ**). It then efficiently aggregates the results based on the MaxSim summation rule. For estimating missing values, we adopt the approach from WARP, using the **distance to the centroid and the cumulative cluster size** to estimate MaxSim scores for potential candidates.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1743733841309/79f715b2-bbf3-4ac4-bb90-b7ffdea07f6f.png)

Reusing our optimized single-vector search components ensures MaxSim benefits from existing performance tuning and stability. Importantly for users, it provides a **seamless experience**: you can leverage **the same familiar index types** (IVF with RaBitQ) for both single-vector and multi-vector MaxSim search, without needing a separate system. VectorChord 0.3 proudly stands as the **first Postgres extension to deliver this efficient, decomposed MaxSim implementation**, making state-of-the-art multi-vector retrieval practical and performant directly within your database.

### Powerful Use Cases Unlocked

This new efficiency opens the door to practical implementations of cutting-edge techniques:

1. **High-Performance ColBERT Reranking:** Apply ColBERT's superior relevance ranking to a candidate set retrieved by a faster first-stage search (like traditional vector search or keyword search) without incurring prohibitive latency penalties. Get the best of both speed and quality.
    
2. **OCR-Free Document Search (ColPali/ColQwen):** Imagine searching directly within scanned documents, PDFs, or images *without* needing a separate, often error-prone, OCR (Optical Character Recognition) step. Models like ColPali or ColQwen generate token embeddings directly from image patches. With VectorChord 0.3's efficient MaxSim, you can now perform late-interaction search over these visual token embeddings directly in Postgres, enabling powerful search over documents previously inaccessible to pure text-based methods.
    

Stay tuned! We have another article coming soon, diving deep into how VectorChord 0.3 enables revolutionary OCR-free RAG pipelines.

### Performance Highlights

We put VectorChord 0.3's new multi-vector MaxSim capabilities to the test on the **FiQA (Financial Opinion Mining and Question Answering) dataset**. This standard benchmark includes 57,000 documents with approximately 15 million cumulative tokens.

Our initial benchmark results, using **ColBERTv2** powered by VectorChord's optimized engine, show promising performance:

* **Relevance:** We achieved an **NDCG@10 score of 34.1**. This compares favorably to the 33.6 NDCG@10 reported for the same dataset in the original WARP paper.
    
* **Speed:** Queries were executed efficiently, averaging just **35 milliseconds per query**.
    

While these are preliminary results based on a single dataset as we continue optimization, they demonstrate VectorChord 0.3's potential. Users can now leverage the advanced relevance capabilities of multi-vector search and late interaction with impressive speed, approaching the latency often associated with simpler single-vector methods, all directly within their Postgres database.

<a id="get-started-with-vectorchord-0-3"></a>
### Get started with VectorChord 0.3

**Prerequisites:**

* PostgreSQL server with the VectorChord v0.3 installed
    

You can use our VectorChord-Suite image:

```bash
docker run --rm --name vchord_db -d -e POSTGRES_PASSWORD=postgres -p 5432:5432 \
    ghcr.io/tensorchord/vchord-postgres:pg17-v0.3.0
```

#### Step 1: Create a Table for Multi-Vector Data

First, define a table to store your data. The key difference is using the array type for your vector column (`vector[]`) to hold multiple vectors per row.

```pgsql
-- Define a table to store items (e.g., documents), each potentially having multiple vectors.
-- Replace '128' with your actual vector dimensionality.
CREATE TABLE doc (
    id SERIAL PRIMARY KEY, -- A unique identifier for each item
    vecs vector(128)[] -- The column storing an ARRAY of 128-dimensional vectors
);
```

#### Step 2: Insert Multi-Vector Data

Insert data into your table. The vecs column takes a PostgreSQL array containing vector types.

```pgsql
-- Insert sample data: one document with 2 vectors, another with 3.
-- Ensure vector dimensions match your table definition (128 in this example).
INSERT INTO doc (id, vecs) VALUES
    (1, array[array[0.1, 0.2, ..., 0.9]::vector, array[0.8, 0.7, ..., 0.1]::vector]),
    (2, array[array[0.5, 0.5, ..., 0.5]::vector, array[0.3, 0.4, ..., 0.7]::vector, array[0.9, 0.1, ..., 0.4]::vector]);
-- Add more data as needed...
```

#### Step 3: Create a `vchordrq` Index with MaxSim Support

To accelerate MaxSim searches, create an index using the vchordrq method and specify the `vector_maxsim_ops` operator class. A crucial parameter here is `build.internal.lists`.

* **Calculate** `n`: Estimate the total number of individual vectors across your entire dataset.
    


$$
n=N_{doc}*\text{avg}(N_{vector\_per\_doc})
$$


* **Set** `lists`*:* The recommended range for `build.internal.lists` is
    


$$
4 * \sqrt n < \text{lists} < 8 * \sqrt n
$$


Choose a value within this range (often powers of 2 work well).

```pgsql
-- Example Calculation:
-- If you have 1,000,000 documents (rows) with an average of 5 vectors each:
-- n = 1,000,000 * 5 = 5,000,000 sqrt(n) ≈ 2236 
-- Lower bound: 4 * 2236 ≈ 8944
-- Upper bound: 8 * 2236 ≈ 17888
-- A good value for 'lists' could be 16384 (power of 2).
-- Assume the K-means clusters are balanced, each will have about 305 vectors.

-- Create the index using vchordrq and vector_maxsim_ops
CREATE INDEX doc_vecs_idx ON doc USING vchordrq (vecs vector_maxsim_ops)
WITH (options = $$
build.internal.lists = [16384] -- Adjust this value based on your calculation!
$$);
```

#### Step 4: Configure Search Parameters (Optional but Recommended)

Before querying, you can tune runtime parameters for performance and accuracy:

* `vchordrq.probes`: Controls how many index lists (clusters) are checked during a search. Higher values increase accuracy (recall) but slow down the search. A common starting point for finding the top 10 results (`LIMIT 10`) is 32.
    
* `vchordrq.maxsim_refine`: Limits the number of vector pairs re-computed with the original precision (otherwise will use the bit distance) for each candidate query token vector. It’s related to the `probes`, a value of 20% of probed vectors will be sufficient.
    

```pgsql
-- Set runtime parameters for the current session/transaction
SET vchordrq.probes = 32; -- Adjust based on desired recall vs. speed trade-off
SET vchordrq.maxsim_refine = 2000; -- Adjust based on desired recall vs. speed trade-off
```

#### Step 5: Perform a MaxSim Similarity Search

Now you can query using the `@#` MaxSim operator. Provide your query vectors as a PostgreSQL array of vector types.

```pgsql
-- Find the top 10 documents most similar to the given set of query vectors
SELECT id FROM doc 
ORDER BY vecs @# ARRAY[array[0.4, 0.1, ..., 0.8]::vector, array[0.7, 0.2, ..., 0.3]::vector]
LIMIT 10;
```

You've now successfully set up a table, indexed it for multi-vector MaxSim search, and executed your first query using VectorChord 0.3's MaxSim operator! Experiment with the `probes` and `max_maxsim_tuples` parameters to find the best balance of speed and accuracy for your specific use case.

%[https://github.com/tensorchord/VectorChord/]
