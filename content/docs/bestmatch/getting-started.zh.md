---
title: "安装与工作原理"
linkTitle: "安装与工作原理"
description: "了解 pg_bestmatch 如何将 BM25 评分转化为稀疏向量内积运算，以及如何安装与启用扩展。"
weight: 10
icon: fa-solid fa-rocket
math: true
upstream_link: https://github.com/tensorchord/pg_bestmatch.rs#how-does-it-work
---

## `pg_bestmatch` 工作原理

给定文档 \(D\) 与分词为词元序列 \(q_1, q_2, \dots, q_n\) 的查询 \(Q\)，标准的 **Okapi BM25** 相关性得分公式为：

$$
\text{BM25}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
$$

可以看到，上述求和本质上是词表空间 \(V\)（内置 `bert-base-uncased` 词表维度为 \(|V| = 30{,}522\)）中两个稀疏向量的**内积（Dot Product）**：

1. **文档稀疏向量** \(\vec{v}_D\)：对于文档 \(D\) 中出现的每个词元 \(t\)，在对应维度存储经文档长度归一化的词频（TF）权重：
   $$
   v_D[t] = \frac{f(t, D) \cdot (k_1 + 1)}{f(t, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}
   $$
2. **查询稀疏向量** \(\vec{v}_Q\)：对于查询 \(Q\) 中的每个词元 \(q_i\)，在对应维度存储其逆文档频率权重 \(\text{IDF}(q_i)\)。

当使用 [`pgvector`](/zh/docs/vector/) 或 [`pgvecto.rs`](/zh/docs/vectors/) 的负内积操作符 `<#>` 计算 \(\vec{v}_D\) 与 \(\vec{v}_Q\) 的距离时，PostgreSQL 会返回 \(-\text{BM25}(D, Q)\)。因此，执行 `ORDER BY embedding <#> query_vec ASC` 即可按 BM25 相关性从高到低返回最匹配的文档！

---

## 安装扩展

### 前置依赖

请先安装 [`pgvector`](/zh/docs/vector/)（需 `v0.7.0+` 以支持 `sparsevec` 类型）或 [`pgvecto.rs`](/zh/docs/vectors/)（需 `v0.3.0+` 以支持 `svector` 类型）。

### 通过预编译包安装（Debian / Ubuntu）

从 [GitHub Releases](https://github.com/tensorchord/pg_bestmatch.rs/releases) 下载对应 PostgreSQL 大版本的 `.deb` 安装包：

```bash
# 示例：x86_64 架构下的 PostgreSQL 16
wget https://github.com/tensorchord/pg_bestmatch.rs/releases/download/v0.0.1/pg-bestmatch-pg16_0.0.1_amd64.deb
sudo dpkg -i pg-bestmatch-pg16_0.0.1_amd64.deb
```

### 从源码编译安装（`cargo pgrx`）

确保系统已安装 Rust 工具链与 `cargo-pgrx`：

```bash
git clone https://github.com/tensorchord/pg_bestmatch.rs.git
cd pg_bestmatch.rs
cargo pgrx install --release
```

---

## 启用扩展

连接到 PostgreSQL，创建扩展并将 `bm25_catalog` 加入 `search_path`：

```sql
CREATE EXTENSION IF NOT EXISTS pg_bestmatch;
CREATE EXTENSION IF NOT EXISTS vector; -- 若使用 pgvecto.rs 则为 CREATE EXTENSION vectors;

SET search_path TO "$user", public, bm25_catalog;
```

执行一条 SQL 验证内置分词器：

```sql
SELECT tokenize('PostgreSQL BM25 full-text search with pg_bestmatch');
--                 tokenize
-- -----------------------------------------
--  {postgresql,bm,##25,full,-,text,search,with,pg,_,best,##mat,##ch}
```

接下来请阅读[使用指南](/zh/docs/bestmatch/usage/)，了解端到端的 BM25 稀疏向量建表、建索引与检索流程。
