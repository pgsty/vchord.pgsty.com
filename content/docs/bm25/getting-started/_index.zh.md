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
了解为什么 BM25 + Block-WeakAnd 在相关性与性能上显著优于 PostgreSQL 原生 ts_rank 与 GIN 索引。
{{< /card >}}
  {{< card link="/zh/docs/bm25/getting-started/installation/" title="安装指南" icon="fa-solid fa-download" >}}
通过 Pigsty、Docker、Debian 软件包或源码编译安装 vchord_bm25 与 pg_tokenizer。
{{< /card >}}
  {{< card link="/zh/docs/bm25/getting-started/quick-start/" title="快速开始" icon="fa-solid fa-bolt" >}}
在几分钟内完成文本分词、构建 bm25 索引并运行 Top-K 全文排序查询。
{{< /card >}}
{{< /cards >}}
