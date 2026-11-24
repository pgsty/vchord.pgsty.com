---
title: "vchord 1.5.0 支持 PostgreSQL 15–19"
date: 2026-11-24
description: "过滤检索按需扩容，向量索引支持并行构建，图索引可在删除后修复跨区连接。"
authors: ["vonng"]
release_url: "https://github.com/pgsty/vchord/releases/tag/1.5.0"
upstream_source: ""
upstream_link: ""
tags: ["release", "vchord"]
---

按 PostgreSQL 主版本和架构选择 Linux ZIP 或 DEB。GitHub Release 提供 PostgreSQL 15–19 的 x86_64 与 aarch64 二进制包。 [GitHub Release](https://github.com/pgsty/vchord/releases/tag/1.5.0)

带过滤键的 RQ 索引先从初始 IVF 列表读取候选行。执行 `WHERE tenant_id = 42 ORDER BY embedding <-> $1 LIMIT 10` 时，只要首轮凑齐十行就能结束。候选不足时继续扩容，直到达到 `vchordrq.max_probes`。后续轮次可能返回更近的行。需要严格顺序时，可多取一批结果，再在 SQL 中排序。

### 球面检索

ANN 索引只访问部分候选，因此可能漏召回。PostgreSQL 用严格半径谓词复核候选。一个例外是 RQ 的单球面 f32 L2 检索，当最终重排与 SQL 使用相同的整向量距离计算、过滤键也精确时，可以直接接纳半径内的行。图索引、半精度、内积和余弦球面检索均保留堆表复核。

### 构建与维护

向量存入 TOAST、主堆较小的表也能并行建索引。带键 RQ 压缩按实际参与的 leader 和 worker 分摊排序内存。在线 RQ VACUUM 每发布一个列表就归还旧页。图索引将新向量页和前驱链接写入同一条 WAL 记录。图 VACUUM 遇到尚有邻居空位的顶点，可以沿已删除的桥寻找另一侧的活顶点。

## 升级

安装对应的动态库和 SQL 后重启 PostgreSQL，在每个使用 vchord 的数据库中执行升级。已有 1.4.0 索引可原地使用，1.3.0 升级时会一并安装过滤键 SQL 对象。如果旧版图 VACUUM 已切断某个活区域，请对受影响的索引执行 `REINDEX INDEX CONCURRENTLY index_name;`。

```sql
ALTER EXTENSION vchord UPDATE TO '1.5.0';
```
