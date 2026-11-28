---
title: "可扩展性"
linkTitle: "可扩展性"
description: "通过增加 PostgreSQL 流复制副本提升每秒向量查询数，以及 LAION-5M 和 LAION-100M 达到 10,000 QPS 各需要几台副本。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/admin/scalability.md"
aliases:
  - "/docs/admin/scalability/"
  - "/vectorchord/admin/scalability/"
icon: fa-solid fa-up-right-and-down-left-from-center
---

一台服务器回答不过来向量查询时，就加只读副本。vchord 对索引的每次修改都会写入 WAL，所以每个流复制副本上的索引都和主库一致，能回答同样的查询；副本越多，查询吞吐越高，不需要另外部署向量数据库。本页先在 CloudNativePG 上搭好这套结构，再给出两个 LAION 数据集达到每秒 10,000 次查询所需的副本数。

<a id="Background"></a><a id="background"></a>

## 工作方式 {#architecture}

主库承担全部写入和索引构建。副本回放主库的 WAL（其中包括 vchord 的索引页），连接池把只读查询分发到各个副本上。每个副本都用自己的缓冲区缓存回答查询，想要达到峰值吞吐，每个副本的内存都要放得下索引以及重排时要读的向量。

<img src="/docs/images/scalability-architecture.png" alt="应用通过只读 PgBouncer 连接池把查询发给多个 PostgreSQL 副本，副本从同一个主库流式接收 WAL" width="100%" />

任何流复制方案都是同样的做法，比如 Patroni 前面挂 HAProxy 或 PgBouncer。下面的步骤用的是 [CloudNativePG](https://cloudnative-pg.io/)（CNPG），本页的测试数据也是在它上面测得的。

## 在 CloudNativePG 上配置只读副本 {#setup}

1. 按 [Kubernetes](/zh/docs/vchord/admin/kubernetes/) 一节创建带 vchord 的 CNPG 集群。`spec.instances` 包含主库在内，`instances: 3` 就是两个副本。

1. 加一个只读连接池。CNPG 会运行 PgBouncer，并且只把连接路由到副本：

   ```yaml
   apiVersion: postgresql.cnpg.io/v1
   kind: Pooler
   metadata:
     name: vchord-pooler-ro
   spec:
     cluster:
       name: vchord
     instances: 2
     type: ro
     pgbouncer:
       poolMode: transaction
       parameters:
         max_client_conn: "1000"
         default_pool_size: "50"
   ```

   应用把向量查询发给 `vchord-pooler-ro` 服务，其余请求发给 `vchord-rw`。

1. 把检索参数存在索引上。事务级连接池里，会话中的 `SET` 不会跟着客户端进入下一个事务，只有索引上的值能保证每条查询都用到。在主库上执行，副本会通过 WAL 收到：

   ```sql
   ALTER INDEX items_embedding_idx SET (probes = '20', epsilon = 1.0);
   ```

   参数取值按[调参流程](/zh/docs/vchord/usage/indexing/#tuning)确定。

1. 调整副本数量。新副本会复制主库的数据目录，索引也一并带上：

   ```bash
   kubectl scale cluster vchord --replicas=8
   ```
{.steps}

## 测试结果 {#results}

[Vector Search at 10,000 QPS in PostgreSQL](/zh/blog/vector-search-at-10000-qps-in-postgresql-with-vectorchord/)（2025 年 2 月）在 AWS EKS 上运行了这套结构。每个副本的内存都放得下各自的数据集。客户端是同一可用区内一台 16 vCPU 的 `r7i.4xlarge`，以 16 到 128 个并发 worker 向只读连接池发送 top-10 查询，主库在测试期间空闲。

| | LAION-5M | LAION-100M |
| --- | --- | --- |
| 向量 | 5,000,000 条 × 768 维 | 100,000,000 条 × 768 维 |
| 副本机型 | `r7i.xlarge`：4 vCPU，32 GiB | `r7i.16xlarge`：64 vCPU，512 GiB |
| `probes` / `epsilon` | `'20'` / `1.0` | `'20'` / `1.0` |
| Top-10 召回率 | 0.9324 | 0.9042 |
| 达到 10,000 QPS 的副本数 | 7 | 2 |
{.wide}

<img src="/docs/images/scalability-laion5m-laion100m-qps.png" alt="不同客户端 worker 数下的吞吐：LAION-5M 使用 5、7、11、15 台 r7i.xlarge 副本，LAION-100M 使用 2 台 r7i.16xlarge 副本" width="100%" />

吞吐既取决于副本数，也取决于客户端并发。16 个 worker 时，LAION-5M 的各种配置都停在 3,000 QPS 左右，瓶颈在客户端。7 个副本在 100 和 128 个 worker 时达到 10,000 QPS，15 个副本在 128 个 worker 时约 13,500 QPS。LAION-100M 的两个副本在 110 个 worker 时接近 10,000 QPS 的峰值，到 128 个 worker 反而回落。

<a id="cost"></a><a id="summary"></a>

按文中引用的按需价格，达到 10,000 QPS 所需副本的费用为：

| 数据集 | 副本 | vCPU | 每月费用 |
| --- | --- | --- | --- |
| LAION-5M | `r7i.xlarge` × 7 | 28 | $0.2646 × 7 × 720 小时 = $1,334 |
| LAION-100M | `r7i.16xlarge` × 2 | 128 | $4.2336 × 2 × 720 小时 = $6,096 |
{.wide}

费用不含主库。

## 限制 {#limits}

- 副本只增加读吞吐。写入和索引构建都在主库上进行，新建的索引以 WAL 的形式传到副本，所以建索引也会占用复制带宽。
- 副本回放到哪里，才能查到哪里。客户端如果必须读到自己刚插入的行，要去主库读。
- 每个节点都要装同一版本的 vchord，并把 `vchord` 加进 `shared_preload_libraries`。缺了这一步，该节点上的查询会报错 `vchord must be loaded via shared_preload_libraries.`
- 每个副本的缓存是独立的。副本重启或故障切换后，头几条查询要从磁盘读；可以先在该副本上执行 `SELECT vchordrq_prewarm('items_embedding_idx');` 把索引读进内存。
