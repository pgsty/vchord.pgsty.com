---
title: "VectorChord 0.2: 60K-Dimensional Vectors, 50% Faster Indexing with ARM"
date: 2025-02-17
description: "VectorChord 0.2: Enhanced vector search in PostgreSQL with up to 60K dimensions, Float16 support, and faster ARM performance"
author: "[Jinjing Zhou](https://github.com/VoVAllen) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "release"
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm"
upstream_copyright: "© 2025 Jinjing Zhou (TensorChord Inc.)"
aliases:
  - "/blog/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm/"
  - "/vectorchord-02-60k-dimensional-vectors-50-faster-indexing-with-arm/"
---

Today, we’re thrilled to share VectorChord 0.2—a release shaped by community feedback and designed to tackle the evolving challenges of vector search in PostgreSQL.

%[https://github.com/tensorchord/VectorChord/] 

<a id="optimized-storage-layout-supporting-up-to-60-000-dimensions"></a>
## Optimized Storage Layout: Supporting Up to 60,000 Dimensions

In PostgreSQL, the foundational storage unit is an 8KB page. While this design is robust for many workloads, it introduces constraints for modern use cases like high-dimensional vector search. For instance, pgvector faces a hard limit of 2000 dimensions per vector due to this fixed page size, as larger vectors cannot be indexed within a single page.

To address this, we’ve reimagined the vector storage architecture in VectorChord. By redesigning how vectors are internally laid out, we enable precise control over storage allocation, allowing vectors to span multiple pages when needed. Now, we can support vectors with a limit of up to 60,000 dimensions.

| **System** | **Vector Dimension Limit** |
| --- | --- |
| VectorChord 0.2 | 60000 |
| VectorChord 0.1 | 1600 |
| pgvector | 2000 |

This cross-page capability not only lifts the 2000-dimension barrier (now supported in v0.2) but also optimizes storage efficiency. For example, a 1200-dimensional vector (occupying ~4.8KB) would traditionally waste nearly half a page’s space in PostgreSQL, since only one such vector fits per 8KB page. This results in just ~58.5% storage utilization (1200 dim × 4 bytes ÷ 8192 bytes). By tightly packing vectors across page boundaries, VectorChord minimizes unused space and improves storage density.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1739759682371/a2aef1a1-2a2c-4e3a-bb81-36dd85560fb0.png)

While this is a small step forward, we’re excited about the possibilities it unlocks for scalable vector workloads.

## Float16 & ARM

In **version 0.2**, we’re excited to introduce **Float16 support**, giving users the flexibility to balance storage efficiency with recall accuracy. By opting for Float16, you can reduce vector storage requirements by 50%, though this comes with a modest trade-off in recall performance. We want to clarify that this optimization applies only to raw vectors—quantized vectors still require 1 bit per dimension to faithfully represent the original data. This update empowers users to make thoughtful choices based on their specific accuracy and storage needs.

We’ve also prioritized performance improvements for ARM architectures. By rewriting distance calculations and Fast Scan logic using ARM’s **Scalable Vector Extension (SVE)** instruction set, VectorChord now delivers optimized performance on ARM-based systems. This enhancement ensures that users on platforms like AWS’s latest **i8g instances** (powered by Graviton4 processors) can achieve faster throughput at the same cost as older i4i instances. While these optimizations are incremental, we’re thrilled to help teams scale efficiently in modern cloud environments.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737032763562/de2e03f6-7657-4313-a483-0e61a0dfa4ce.png?auto=compress,format&format=webp)

As the results show, **VectorChord** running on the i8g.xlarge (ARM64) delivers about a **30% improvement in throughput** compared to the i4i.xlarge, even though both are priced similarly. On the other hand, the more expensive i7ie.xlarge, which costs **50% more**, only offers a modest **15% performance boost** over the i8g—far from justifying its higher price tag. Additionally, the **index construction time** on the ARM-based i8g is significantly faster, which was a surprising and welcome advantage.

Our benchmarks highlight some insights for cost-conscious users. VectorChord on AWS’s i8g.xlarge (ARM64) achieves **~30% higher throughput** compared to the similarly priced i4i.xlarge, demonstrating how modern ARM architectures can deliver meaningful performance gains without added cost. On the other hand, the i7ie.xlarge, priced 50% higher than the i8g, offers only a 15% performance uplift—a trade-off that may not align with most teams’ cost-efficiency goals.

We were also pleasantly surprised by the **significantly faster index construction times** on ARM-based i8g instances. While this wasn’t a primary focus of our optimizations, it underscores the broader potential of ARM64 and SVE for vector workloads. That said, we recognize these results are just one part of a larger ecosystem, and we’re eager to collaborate with the community to refine these benchmarks further.

Ultimately, our goal is to empower users with data-driven choices. The i8g’s strong performance-per-dollar and unexpected construction speed advantages make it a compelling option for teams scaling vector search in production. None of this would be possible without the incredible open-source ecosystem we build upon. We’re grateful for the community’s support and feedback as we continue refining VectorChord for real-world workloads.

## Getting Started

You can use Docker to try out VectorChord 0.2.

```bash
## Start VectorChord in postgres
docker run \
  --name vectorchord-demo \
  -e POSTGRES_PASSWORD=mysecretpassword \
  -p 5432:5432 \
  -d tensorchord/vchord-postgres:pg17-v0.1.0

## Connect use psql clinet
psql -h localhost -p 5432 -U postgres
```

All the query syntax is the same as VectorChord 0.1!

<a id="Summary"></a>
## Summary

VectorChord 0.2 builds on its predecessor with a 30% smaller index size and 50% faster builds. Float16 supports halves of raw vector storage, while new features like 60000-dimensional vectors and ARM64 optimizations deliver smoother PostgreSQL retrieval. Together, these updates help users scale efficiently—without sacrificing performance.

We warmly welcome the community to explore VectorChord 0.2! Whether you’re optimizing storage with Float16, scaling high-dimensional workloads, or leveraging ARM’s cost-performance benefits, we’re here to support your journey. Your feedback shapes what’s next—let’s build smarter vector search, together. 🚀

Take these advancements further with [VectorChord Cloud](/cloud/), offering a hassle-free managed service and a free trial to jumpstart your projects. Whether you’re optimizing storage, scaling complex workloads, or leveraging ARM’s efficiency, our cloud platform handles the infrastructure so you can focus on innovation.
