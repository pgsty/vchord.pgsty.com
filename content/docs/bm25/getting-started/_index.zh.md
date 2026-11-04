---
title: "快速上手"
description: "vchord_bm25 与 pg_tokenizer 的架构概览、安装方式与快速入门指南。"
weight: 10
icon: fa-solid fa-rocket
no_list: true
---

在 PostgreSQL 中快速上手 **`vchord_bm25`**：

{{< cards >}}
  {{< card link="/zh/docs/bm25/getting-started/overview/" title="架构概览" icon="fa-solid fa-compass" >}}
了解为什么 Okapi BM25 与 Block-WeakAnd 块级剪枝索引在相关性排序与查询吞吐量上显著优于 PostgreSQL 原生 `ts_rank` 与 GIN 索引。
{{< /card >}}
  {{< card link="/zh/docs/bm25/getting-started/installation/" title="安装指南" icon="fa-solid fa-download" >}}
通过 Pigsty 原生 Linux 软件包、Docker（Obsolete） 容器镜像、Debian/ZIP 预编译归档包或 `cargo-pgrx` 源码编译方式安装 `vchord_bm25` 与 `pg_tokenizer`。
{{< /card >}}
  {{< card link="/zh/docs/bm25/getting-started/quick-start/" title="快速开始" icon="fa-solid fa-bolt" >}}
跟随分步 SQL 实操演练，在几分钟内完成文本分词处理、构建 `bm25` 倒排索引并运行第一条 Top-K 全文相关性排序查询。
{{< /card >}}
{{< /cards >}}
