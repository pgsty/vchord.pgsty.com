---
title: "为什么不使用专用向量数据库？"
linkTitle: "pgvecto.rs 对比专用向量数据库"
description: "阅读我们的完整博客文章：我们真的需要专用向量数据库吗？(2023) | vchord.pgsty.com。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/faqs/comparison-with-specialized-vectordb.md"
aliases:
  - "/faqs/comparison-with-specialized-vectordb/"
icon: fa-solid fa-server
---

欢迎阅读我们的完整博客文章：[我们真的需要专用向量数据库吗？(2023) | vchord.pgsty.com](/zh/blog/post/do-we-really-need-a-specialized-vector-database-2023/)。

试想一下：你现有的业务数据已经存储在 Postgres 数据库中，现在你希望引入向量数据库来执行向量相似度检索。如果采用专用向量数据库，你就必须将数据从 Postgres 同步迁移到向量数据库中，并且同时运维两套数据库系统。这显然不是一个好主意。

为什么不直接使用 Postgres 来完成向量相似度检索呢？这正是我们构建 `pgvecto.rs` 的初衷。使用体验非常自然直观：

```sql
-- 为 documents 表更新生成 embedding 向量列
UPDATE documents SET embedding = ai_embedding_vector(content) WHERE length(embedding) = 0;

-- 在 embedding 列上创建向量索引
CREATE INDEX ON documents USING vectors (embedding vector_l2_ops);

-- 查询最相似的嵌入向量
SELECT * FROM documents ORDER BY embedding <-> ai_embedding_vector('hello world') LIMIT 5;
```

引用自 [SingleStore DB 博客](https://www.singlestore.com/blog/why-your-vector-database-should-not-be-a-vector-database/)：

> 向量和向量检索本质上只是一种数据类型和一种查询处理方式，而不是构建全新数据处理范式的基石。使用专用向量数据库（SVDB）会导致我们在使用多套专用系统的客户身上反复看到的那些典型问题：数据冗余、过度的数据迁移、分布式组件之间的数据不一致、需要专门技能带来的额外人力成本、额外的商业授权费用、受限的查询语言表达能力与可编程/可扩展性、匮乏的工具链生态集成，以及与真正的数据库管理系统（DBMS）相比糟糕的数据完整性与高可用保障。
