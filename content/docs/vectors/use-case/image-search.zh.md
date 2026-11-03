---
title: "以图搜图与智能图像搜索"
linkTitle: "图像搜索"
description: "智能图像搜索（又称基于内容的图像检索）超越了传统的关键词搜索，让用户能够根据图像的视觉内容进行搜索。"
weight: 30
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/use-case/image-search.md"
aliases:
  - "/use-case/image-search/"
icon: fa-solid fa-image
---

智能图像搜索，又称基于内容的图像检索（Content-Based Image Retrieval），超越了传统的基于关键词的搜索方式，使用户能够根据图像的**视觉内容**搜索图像。例如，您可以直接搜索**包含**红蘑菇的图片（图片来自 [immich](https://immich.app)）：

![image-search](https://immich.app/img/screenshot-light.webp)

这项功能看似神奇，因为它允许您在没有任何标签或关键词的情况下搜索图片。搜索引擎能够理解图像和视频的内容，并找出与查询语义相似的结果。

## 工作原理 {#how-it-works}

智能图像搜索利用先进的计算机视觉技术和机器学习算法来理解图像中的视觉特征，从而使用户无需依赖特定的关键词或元数据即可执行自由形式的搜索。

第一步是从图像中提取有意义的特征，并生成每张图像的向量表示。这通常使用诸如 [CLIP](https://openai.com/research/clip) 之类的深度学习模型来完成。生成的向量表示被称为**嵌入（Embedding）**，它是一个代表该图像视觉特征的数值列表。

随后，您可以使用像 [pgvecto.rs](/zh/docs/vectors/) 这样的向量数据库来存储这些嵌入向量，并执行高效的向量相似度搜索。

<a id="Example"></a>
## 示例 {#example}

我们将利用连接文本与图像的神经网络模型 [CLIP](https://openai.com/research/clip) 为图像生成嵌入向量。这些嵌入向量捕捉了图像中呈现的视觉概念。接着，我们将使用基于 Postgres 构建的可扩展向量搜索工具 [pgvecto.rs](/zh/docs/vectors/) 来存储这些嵌入并执行高效的向量搜索。通过结合 CLIP 和 `pgvecto.rs` 的强大能力，我们可以根据视觉内容检索相似图像。

### 生成嵌入向量 {#generate-embeddings}

您可以使用 [CLIP](https://openai.com/research/clip) 为图像生成嵌入向量：

```python
from transformers import CLIPProcessor, CLIPModel

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

def compute_image_embeddings(list_of_images):
    return model.get_image_features(**processor(images=list_of_images, return_tensors="pt", padding=True))
```

### 存储嵌入向量 {#store-embeddings}

假设您有一张名为 `images` 的表，包含三个列：`id`、`author` 和 `embedding`，其中 `embedding` 列的类型为 `vector(512)`。您可以按如下方式将图像数据插入表中：

```sql
-- 创建表
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    author TEXT NOT NULL,
    vector vector(512) NOT NULL -- 512 维
);

INSERT INTO images (author, embedding) VALUES
  ('Allen', '[...]');
```

### 搜索相似图像 {#search-for-similar-images}

您可以像这样搜索相似的图像：

```sql
SELECT * FROM images ORDER BY embedding <-> '[...]' LIMIT 5;
```

## 高级搜索 {#advanced-search}

假设您希望搜索距离最近的 64 条记录，且要求结果中不包含作者 `Allen` 的图片。

您可能会期望以下 SQL 能够正常工作：

```sql
SET vectors.hnsw_ef_search = 64;
SELECT * FROM images ORDER BY embedding <-> '[...]' WHERE author != 'Allen' LIMIT 64;
```

在传统的 `basic` 搜索模式下，您可能最终只得到了 `32` 条记录，因为 HNSW 算法在图搜索过程中会绕过过滤条件，仅依赖 PostgreSQL 在搜索完成后对固定数量的候选集进行后置过滤（Post-filtering）。

您可以使用 `vbase` 搜索模式来解决这一问题。在 `vbase` 模式下，**搜索结果变成了一个迭代器（Iterator）**，可以持续不断地返回近似最近邻结果。数据库可以从中不断拉取结果，直到满足用户的过滤条件和返回数量要求为止。这与 *faiss* 等其他向量搜索库截然不同——后者只能返回固定大小的结果集，且该大小必须在搜索前预先确定。对于带有过滤条件的查询，事先无法预知需要检索多少候选集才能凑够目标数量，因此传统做法要么导致返回结果数量不足，要么因过度搜索而增加延迟。该设计思想源于论文 [VBASE: Unifying Online Vector Similarity Search and Relational Queries via Relaxed Monotonicity](https://www.usenix.org/conference/osdi23/presentation/zhang-qianxi)。

您可以通过 SQL 语句 `SET vectors.search_mode = vbase;` 启用 `vbase` 模式，从而获得符合预期的行为。[immich](https://immich.app) 的图像搜索功能便采用了这一模式。从 0.2 版本起，`vbase` 已成为默认搜索模式。

## 真实生产案例 {#real-world-applications}

开源相册应用 [immich](https://immich.app) 使用了智能图像搜索功能，使用户能够根据视觉内容搜索照片。此处提供的代码片段源自 [immich](https://immich.app) 中[图像搜索功能](https://github.com/immich-app/immich/blob/bd87eb309c6d7af05db98e5cb08067ee592fc331/server/src/infra/repositories/smart-info.repository.ts#L46-L77)的真实实现：

```sql
SELECT a.*, s.*, e.*
FROM asset_entity AS a
INNER JOIN smart_search AS s ON s.assetId = a.id
LEFT JOIN exif_info AS e ON e.assetId = a.id
WHERE a.ownerId IN (:...userIds)
  AND a.isArchived = false
  AND a.isVisible = true
  AND a.fileCreatedAt < NOW()
ORDER BY s.embedding <=> :embedding
LIMIT :numResults;
```

该查询根据指定的过滤条件和向量距离排序，从 `asset_entity`、`smart_search` 和 `exif_info` 三张表中检索数据。下面我们来逐步拆解这条查询：

```sql
SELECT a.*, s.*, e.*
```
查询的这一部分指定了要从 `asset_entity`、`smart_search` 和 `exif_info` 表中选择的列，并使用别名 `a`、`s` 和 `e` 分别引用这三张表。

```sql
FROM asset_entity AS a
INNER JOIN smart_search AS s ON s.assetId = a.id
LEFT JOIN exif_info AS e ON e.assetId = a.id
```
在这里，`asset_entity` 表别名为 `a`，`smart_search` 表别名为 `s`，`exif_info` 表别名为 `e`。查询使用 `INNER JOIN` 基于条件 `s.assetId = a.id` 关联 `asset_entity` 与 `smart_search`，并使用 `LEFT JOIN` 基于条件 `e.assetId = a.id` 引入 `exif_info` 表中的匹配记录。

> [!DETAILS]
>
> `asset_entity` 表的结构定义如下：
>
> ```sql
> CREATE TABLE asset_entity (
>   id UUID PRIMARY KEY,
>   deviceAssetId VARCHAR NOT NULL,
>   ownerId VARCHAR NOT NULL,
>   libraryId VARCHAR NOT NULL,
>   deviceId VARCHAR NOT NULL,
>   type VARCHAR NOT NULL,
>   originalPath VARCHAR NOT NULL,
>   resizePath VARCHAR,
>   webpPath VARCHAR DEFAULT '',
>   thumbhash BYTEA,
>   encodedVideoPath VARCHAR,
>   createdAt TIMESTAMPTZ NOT NULL,
>   updatedAt TIMESTAMPTZ NOT NULL,
>   deletedAt TIMESTAMPTZ,
>   fileCreatedAt TIMESTAMPTZ NOT NULL,
>   localDateTime TIMESTAMPTZ NOT NULL,
>   fileModifiedAt TIMESTAMPTZ NOT NULL,
>   isFavorite BOOLEAN DEFAULT false,
>   isArchived BOOLEAN DEFAULT false,
>   isExternal BOOLEAN DEFAULT false,
>   isReadOnly BOOLEAN DEFAULT false,
>   isOffline BOOLEAN DEFAULT false,
>   checksum BYTEA NOT NULL,
>   duration VARCHAR,
>   isVisible BOOLEAN DEFAULT true,
>   livePhotoVideoId UUID,
>   originalFileName VARCHAR NOT NULL,
>   sidecarPath VARCHAR,
>   stackId UUID,
>   CONSTRAINT fk_asset_owner FOREIGN KEY (ownerId) REFERENCES user_entity (id) ON DELETE CASCADE ON UPDATE CASCADE,
>   CONSTRAINT fk_asset_library FOREIGN KEY (libraryId) REFERENCES library_entity (id) ON DELETE CASCADE ON UPDATE CASCADE,
>   CONSTRAINT fk_asset_live_photo_video FOREIGN KEY (livePhotoVideoId) REFERENCES asset_entity (id) ON DELETE SET NULL ON UPDATE CASCADE,
>   CONSTRAINT fk_asset_stack FOREIGN KEY (stackId) REFERENCES asset_stack_entity (id) ON DELETE SET NULL ON UPDATE CASCADE
> );
> ```
>


```sql
WHERE a.ownerId IN (:...userIds)
  AND a.isArchived = false
  AND a.isVisible = true
  AND a.fileCreatedAt < NOW()
```
在这一部分中，查询对 `asset_entity` 表应用了过滤条件：筛选出 `ownerId` 在指定的 `userIds` 列表中、`isArchived` 为 `false`、`isVisible` 为 `true`，且文件创建时间 `fileCreatedAt` 早于当前时间（`NOW()`）的行。

```sql
ORDER BY s.embedding <=> :embedding
```
查询使用余弦距离操作符 `<=>` 将 `smart_search` 表的 `embedding` 列与传入的查询向量 `:embedding` 进行比较，并按距离从小到大排序。

```sql
LIMIT :numResults;
```
最后，将查询返回的行数限制为 `:numResults` 参数指定的值。

这是一个典型的真实生产环境案例，展示了如何在实际业务系统中结合关系查询、权限过滤与向量搜索来实现智能图像检索。
