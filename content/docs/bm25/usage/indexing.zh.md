---
math: true
title: "索引构建与维护"
description: "在 PostgreSQL 中创建、配置、维护和检查 bm25 索引。"
weight: 10
icon: fa-solid fa-database
---

`vchord_bm25` 提供了 `bm25` 索引访问方法以及需要显式指定的 `bm25_ops` 操作符类。0.4.0 的 SQL 处理器为 `bm25_amhandler`，0.3.x 为 `_bm25_amhandler`。

## 创建 `bm25` 索引 {#creating-a-bm25-index}

### 稳定发布版（`v0.1` – `v0.3`，`bm25vector`） {#stable-releases-v01--v03-bm25vector}

```sql
CREATE INDEX documents_embedding_bm25
ON documents
USING bm25 (embedding bm25_ops);
```

### 新一代 `main` 分支（`tsvector`） {#next-gen-main-branch-tsvector}

在 `main` 分支中，`bm25_ops` 直接作用于 `tsvector`，并支持索引级存储参数（`options`、`limit` 和 `prefilter`）：

```sql
CREATE INDEX documents_vector_bm25
ON documents
USING bm25 (vector bm25_ops)
WITH (
    options = $$
    k1 = 1.2
    b = 0.75
    $$,
    limit = 100,
    prefilter = false
);
```

| 存储参数 (`WITH (...)`) | 类型 | 默认值 | 取值范围 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `options` (`k1`) | `float`（TOML 内） | `1.2` | `1.2` – `2.0` | 词频饱和度参数 \(k_1\)。数值越大，文档内重复出现的词项权重越高。 |
| `options` (`b`) | `float`（TOML 内） | `0.75` | `0.0` – `1.0` | 文档长度归一化参数 \(b\)。`0.0` 禁用长度归一化；`1.0` 完全按相对于 \(\text{avgdl}\) 的文档长度进行归一化。 |
| `limit` | `int` | `0` | `0` – `65535` | 存储在索引上的默认 Top-K 检索上限（当会话 GUC `bm25.limit` 保持默认来源或执行 `RESET` 后使用）。 |
| `prefilter` | `bool` | `false` | `true` / `false` | 存储在索引上的默认预过滤行为（可在会话级通过 `bm25.prefilter` 覆盖）。 |
{.wide .expand}

你可以使用 `ALTER INDEX` 动态更新现有索引上的 `limit` 或 `prefilter` 参数：

```sql
ALTER INDEX documents_vector_bm25 SET (limit = 200, prefilter = true);
ALTER INDEX documents_vector_bm25 RESET (limit, prefilter);
```

## 自动分词触发器（`v0.1` – `v0.3`） {#automatic-tokenization-triggers-v01--v03}

使用 `pg_tokenizer 1.0.0` 的历史 `bm25vector` 接口时，可以通过触发器在执行 `INSERT` 和 `UPDATE` 时自动同步更新词元列：

### 使用自定义模型触发器（一步到位辅助函数） {#using-a-custom-model-trigger-one-step-helper}

`create_custom_model_tokenizer_and_trigger` 会一步完成自定义模型创建、分词器创建、存量数据回填，并自动挂载 `BEFORE INSERT OR UPDATE` 触发器：

该辅助函数支持可选的第七个 `filter` 参数。它只会将可信源列谓词结果为 `TRUE` 的行用于词表训练和 embedding 更新；省略或传入 SQL `NULL` 时仍处理整张表。详见 [pg_tokenizer 模型说明](/zh/docs/tokenizer/models/#corpus-filter)。

```sql
SELECT create_custom_model_tokenizer_and_trigger(
    tokenizer_name => 'my_tokenizer',
    model_name     => 'my_model',
    text_analyzer_name => 'my_analyzer',
    table_name     => 'documents',
    source_column  => 'passage',
    target_column  => 'embedding'
);
```

### 将标准 PL/pgSQL 触发器用于预训练模型 {#using-a-standard-plpgsql-trigger-with-pretrained-models}

如果你使用的是预训练模型（如 `llmlingua2` 或 `bert_base_uncased`），可以创建一个标准的触发器函数：

```sql
CREATE OR REPLACE FUNCTION documents_tokenize_trigger()
RETURNS trigger AS $$
BEGIN
    NEW.embedding := tokenize(NEW.passage, 'my_tokenizer');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_documents_tokenize
BEFORE INSERT OR UPDATE OF passage ON documents
FOR EACH ROW
EXECUTE FUNCTION documents_tokenize_trigger();
```

## 段架构：增长段（Growing）与封闭段（Sealed）（`v0.1` – `v0.3`） {#segment-architecture-growing-vs-sealed-segments-v01--v03}

在内部实现中，`vchord_bm25` 将索引元组组织为两种段状态：

1. **增长段（Growing Segment）**：新写入的元组（`INSERT` / `UPDATE`）会追加到增长段中，从而无需重新压缩整条倒排链表即可获得极高的写入吞吐量。
2. **封闭段（Sealed Segment）**：当增长段超过 `bm25_catalog.segment_growing_max_page_size` 个页面（默认 `4096` 页，约 32 MB）时，它会被封存为不可变的只读段，采用差分位打包（Delta-Bitpacked）的 128 文档块结构，并预计算块级最大得分上界与词项文档频率（DF）统计信息。

```sql
-- 调整增长段封存阈值（单位为 8 KB 页面，取值范围 1..1000000）
SET bm25_catalog.segment_growing_max_page_size = 4096;
```

## 并行索引构建与进度监控 {#parallel-index-build--progress-monitoring}

索引构建支持 PostgreSQL 并行维护工作进程（Parallel Maintenance Workers），并可通过 `pg_stat_progress_create_index` 跨三个阶段实时汇报构建进度：

1. `initializing`（初始化）
2. `scanning table`（扫描表）
3. `writing index structures`（写入索引结构）

```sql
-- 使用并行工作进程加速大规模索引构建
SET max_parallel_maintenance_workers = 8;
SET maintenance_work_mem = '2GB';

-- 在另一个会话中监控构建进度
SELECT
    pid,
    phase,
    tuples_total,
    tuples_done,
    round(100.0 * tuples_done / nullif(tuples_total, 0), 2) AS pct_done
FROM pg_stat_progress_create_index;
```

## 检查索引页（`v0.3.0`） {#inspecting-index-pages-v030}

`0.3.0` 版本提供了 `bm25_page_inspect(index regclass, blkno int)` 函数，用于检查 `bm25` 索引的内部元数据与页头信息：

```sql
-- 检查 bm25 索引的元信息页（第 0 块）
SELECT bm25_page_inspect('documents_embedding_bm25', 0);
```

## 索引约束与限制 {#index-constraints--limitations}

- **仅支持单列索引**：`bm25` 索引只能创建在单个 `bm25vector`（或 `tsvector`）列上，不支持多列联合 `bm25` 索引。
- **不支持 Unlogged 表**：`bm25` 访问方法不支持 `UNLOGGED` 表（调用 `ambuildempty` 会抛出 `Unlogged indexes are not supported` 错误）。
- **仅支持正向扫描**：`bm25` 索引扫描在 `<&>` 操作符上仅支持正向（`ASC`）扫描方向。
