---
title: "ARM + VectorChord: Affordable, Fast Vector Search"
date: 2025-01-21
description: "ARM64 servers like AWS Graviton save costs. VectorChord - 26x cheaper than pgvector. Optimized for ARM64/x86, it delivers fast, efficient vector search"
author: "[Junyu Chen](https://github.com/cutecutecat) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
  - "vectorchord"
upstream_link: "https://blog.vectorchord.ai/arm-vectorchord-affordable-fast-vector-search"
upstream_copyright: "© 2025 Junyu Chen (TensorChord Inc.)"
aliases:
  - "/blog/arm-vectorchord-affordable-fast-vector-search/"
  - "/arm-vectorchord-affordable-fast-vector-search/"
---

ARM64 is quietly becoming a go-to for cost-effective cloud servers, especially on AWS. With ARM-based processors like the Graviton series (Graviton3 and Graviton4), you can save a good chunk of money without sacrificing performance. These ARM64 instances are way more affordable than traditional x86 ones, making them a solid choice for balancing cost and performance in the cloud.

That said, ARM’s architecture differs from x86, so software that isn’t optimized for it might run slower due to emulation. This is where **VectorChord** steps in—a PostgreSQL extension designed for scalable, high-performance, and disk-efficient vector similarity search. As the successor to [pgvecto.rs](/docs/vectors/), VectorChord lets you store a whopping **400,000 vectors for just $1**, delivering massive savings: **6x more vectors** than Pinecone's optimized storage and **26x more** than pgvector / [pgvecto.rs](/docs/vectors/) for the same price.

By leveraging platform-specific features like AVX-512 on x86\_64 and SVE on ARM64, VectorChord ensures efficient vector search performance across different systems. Whether you're on ARM64 or x86, VectorChord keeps things running smoothly, making it a reliable and versatile solution for modern computing environments. In short, ARM64 is a great option for saving money, and VectorChord is here to make sure your vector search is fast, efficient, and budget-friendly.

## **Benchmark Setup**

We ran benchmarks on three AWS EC2 instances to evaluate VectorChord's performance across different setups. Here's a breakdown of our choices and findings:

| [**instance**](https://docs.aws.amazon.com/ec2/latest/instancetypes/so.html) | **i4i.xlarge** | **i8g.xlarge** | **i7ie.xlarge** |
| --- | --- | --- | --- |
| Memory | 32 GiB | 32 GiB | 32 GiB |
| vCPUs | 4 | 4 | 4 |
| CPU generation | 3rd gen Intel Xeon | **AWS Graviton4** | 5th gen Intel Xeon |
| CPU Architecture | x86\_64 | **arm64** | x86\_64 |
| Storage | 937 GB NVME SSD | 937 GB NVME SSD | 2500 GB NVME SSD |
| cost | $0.1158 hourly | **$0.1162 hourly** | $0.1723 hourly |

The **i8g.xlarge** (ARM-based) is priced almost identically to the **i4i.xlarge** but offers a noticeable boost in CPU performance. When compared to the **i7ie.xlarge**, which has comparable CPU capabilities, the **i8g.xlarge** comes in at nearly half the cost, making it a much more budget-friendly option.

## **Test result**

To showcase how competitive ARM64 machines are for vector search, we ran the same LAION benchmark test across all selected machine types. We measured key metrics like index construction speed, query throughput (QPS), and recall rates under different search parameters.

This benchmark involves inserting **5 million vectors** (each with 768 dimensions) and running 1,000 queries on them. The results below highlight the **index build time** and **query performance** for each cluster, giving a clear picture of how ARM64 stacks up against traditional x86 setups.

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1737032763562/de2e03f6-7657-4313-a483-0e61a0dfa4ce.png)

As the results show, **VectorChord** running on the i8g.xlarge (ARM64) delivers about a **30% improvement in throughput** compared to the i4i.xlarge**,** even though both are priced similarly. On the other hand, the more expensive i7ie.xlarge, which costs **50% more**, only offers a modest **15% performance boost** over the i8g—far from justifying its higher price tag. Additionally, the **index construction time** on the ARM-based i8g is significantly faster, which was a surprising and welcome advantage.

In short, the ARM-based i8g.xlarge strikes a better balance between performance and cost when compared to both the i4i.xlarge and i7ie.xlarge. This aligns perfectly with the core value **VectorChord** brings to its users: **more performance for less cost**. Whether you're looking to save money or maximize efficiency, the combination of ARM64 and VectorChord is a clear winner.
