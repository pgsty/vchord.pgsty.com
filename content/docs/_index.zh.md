---
title: "Vchord 文档中心"
linkTitle: "文档"
description: "PostgreSQL 向量检索、BM25 全文排序与分词扩展套件统一文档中心：涵盖 vchord、vchord_bm25、pg_tokenizer、pgvector、pgvecto.rs 与 pg_bestmatch。"
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://docs.vectorchord.ai/
upstream_modified: true
aliases:
  - "/cloud/"
  - "/cloud/pricing/price-plan/"
  - "/cloud/manage/apikey/"
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

## 扩展套件导航

{{< cards >}}
{{< card title="vchord" icon="fa-solid fa-layer-group" link="/zh/docs/vchord/" >}}
新一代可扩展、磁盘友好型 PostgreSQL 向量检索核心扩展，提供 RaBitQ 量化的 `vchordrq` 倒排索引、`vchordg` 高吞吐图索引与 MaxSim（`@#`）多向量检索。
{{< /card >}}
{{< card title="vchord_bm25" icon="fa-solid fa-magnifying-glass" link="/zh/docs/bm25/" >}}
PostgreSQL 原生 Okapi BM25 全文相关性排序核心扩展，采用 Block-WeakAnd 块级剪枝索引加速 Top-K 查询，可与 `vchord` 无缝构建高召回混合检索。
{{< /card >}}
{{< card title="pg_tokenizer" icon="fa-solid fa-language" link="/zh/docs/tokenizer/" >}}
独立运行的数据库内多语言文本分析与分词核心扩展，支持结巴中文、Lindera 日文、Snowball 词干提取、预训练词表与自定义语料词表模型训练。
{{< /card >}}
{{< card title="pgvecto.rs" icon="fa-solid fa-cube" badge="Deprecated" link="/zh/docs/vectors/" >}}
前代产品参考手册：[`vchord`](/zh/docs/vchord/) 的第一代 Rust 向量检索前身扩展（`v0.1`–`v0.4`），提供完整历史技术归档文档、配置参考与平滑迁移实操指南。
{{< /card >}}
{{< card title="pg_bestmatch" icon="fa-solid fa-ranking-star" badge="Deprecated" link="/zh/docs/bestmatch/" >}}
前代产品参考手册：早期基于稀疏向量内积的数据库内 BM25 检索扩展，现已由 [`vchord_bm25`](/zh/docs/bm25/) 与 [`pg_tokenizer`](/zh/docs/tokenizer/) 原生全文检索组合方案取代。
{{< /card >}}
{{< card title="pgvector" icon="fa-solid fa-circle-nodes" badge="Upstream" link="/zh/docs/vector/" >}}
依赖的上游基础扩展：`vchord` 直接依赖的 PostgreSQL 开源向量基础扩展，提供标准 `vector`、`halfvec`、`bit` 与 `sparsevec` 类型及 HNSW 索引。
{{< /card >}}
{{< /cards >}}

## vchord 核心文档导航

{{< cards >}}
{{< card title="快速上手" icon="fa-solid fa-rocket" link="/zh/docs/vchord/getting-started/" >}}
涵盖 `vchord` 整体架构概览、快速开始 SQL 教程、通过 Pigsty 原生包或 Docker 容器部署安装，以及从 [`pgvecto.rs`](/zh/docs/vectors/) 迁移的完整指南。
{{< /card >}}
{{< card title="使用与索引指南" icon="fa-solid fa-code" link="/zh/docs/vchord/usage/" >}}
详解 `vchordrq` 与 `vchordg` 索引构建、最近邻与球面范围检索、预过滤查询、索引预热、外部预计算构建与完整 SQL 参数参考。
{{< /card >}}
{{< card title="多向量与混合检索" icon="fa-solid fa-diagram-project" link="/zh/docs/vchord/use-case/" >}}
支持 ColBERT 多向量 MaxSim（`@#`）延迟交互与 ColPali 视觉文档检索，以及结合 [`vchord_bm25`](/zh/docs/bm25/) 与 [`pg_tokenizer`](/zh/docs/tokenizer/) 的 RRF 混合检索。
{{< /card >}}
{{< card title="基准测试与成本" icon="fa-solid fa-chart-line" link="/zh/docs/vchord/benchmark/" >}}
提供基于 GIST-1M、Cohere-10M 与 LAION-100M 标准数据集的可复现吞吐性能、召回精度、内存开销与云端 TCO 成本对比分析。
{{< /card >}}
{{< card title="运维管理与调优" icon="fa-solid fa-sliders" link="/zh/docs/vchord/admin/" >}}
涵盖生产环境 GUC 参数调优、PostgreSQL 共享内存规划、I/O 并发设置、VACUUM 索引维护、Kubernetes 部署与版本升级流程。
{{< /card >}}
{{< card title="生产用户案例" icon="fa-solid fa-earth-americas" link="/zh/docs/vchord/customer-stories/" >}}
深入了解牛津大学与 Earth Genome 团队如何利用 `vchord` 在单台 PostgreSQL 实例中高效存储并检索 30 亿地球观测嵌入向量。
{{< /card >}}
{{< /cards >}}

## 生态与项目信息

{{< cards >}}
{{< card title="关于 Vchord 套件" icon="fa-solid fa-circle-info" link="/zh/docs/about/" >}}
介绍 Vchord 检索套件整体技术架构、六大扩展功能定位与协同关系，以及 PGSTY 社区接手维护的背景与长期支持说明。
{{< /card >}}
{{< card title="开源致谢与版权" icon="fa-solid fa-scale-balanced" link="/zh/docs/about/attribution/" >}}
完整记录上游源码与文档来源、TensorChord 原作者团队致谢声明、各组件开源许可证条款，以及新旧代码仓库对应关系。
{{< /card >}}
{{< card title="AGPLv3 开源许可" icon="fa-solid fa-code-branch" link="/zh/docs/about/license/" >}}
说明 GNU AGPLv3 开源许可证完整条款、PostgreSQL 14–18 主流 Linux 发行版软件包支持矩阵、版本升级脚本策略与安全问题反馈。
{{< /card >}}
{{< /cards >}}
