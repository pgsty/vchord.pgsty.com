---
title: "数据库 Schema"
linkTitle: "Schema"
description: "pgvecto.rs 提供的数据库数据类型、操作符、函数、类型转换与操作符类一览。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/pgvecto_rs/reference/schema.md"
aliases:
  - "/reference/schema/"
icon: fa-solid fa-code
---

以下是 `pgvecto.rs` 提供的数据库对象定义（Schema）。

## 数据类型列表 {#list-of-data-types}

| 名称              | 说明                                                                   |
| ----------------- | ---------------------------------------------------------------------- |
| vector            | 稠密向量，标量元素类型为 IEEE 754-2008 定义的 `binary32`（32 位浮点数） |
| vecf16            | 半精度向量，标量元素类型为 IEEE 754-2008 定义的 `binary16`（16 位浮点数）|
| veci8             | 整数向量，标量元素类型为 `8-bit Integer`（8 位有符号整数）             |
| svector           | 稀疏向量，标量元素类型为 IEEE 754-2008 定义的 `binary32`（32 位浮点数） |
| bvector           | 二值向量，定长位串（bit string）                                       |
| vector_index_stat | 表示向量索引统计信息的复合类型                                         |
{.wide .expand}

## 操作符列表 {#list-of-operators}

| 名称 | 左操作数类型 | 右操作数类型 | 返回类型 | 说明                       |
| ---- | ------------ | ------------ | -------- | -------------------------- |
| +    | vector       | vector       | vector   | 逐元素加法运算             |
| +    | vecf16       | vecf16       | vecf16   | 逐元素加法运算             |
| +    | veci8        | veci8        | veci8    | 逐元素加法运算             |
| +    | svector      | svector      | svector  | 逐元素加法运算             |
| -    | vector       | vector       | vector   | 逐元素减法运算             |
| -    | vecf16       | vecf16       | vecf16   | 逐元素减法运算             |
| -    | veci8        | veci8        | veci8    | 逐元素减法运算             |
| -    | svector      | svector      | svector  | 逐元素减法运算             |
| &    | bvector      | bvector      | bvector  | 逐元素按位与（AND）        |
| \|   | bvector      | bvector      | bvector  | 逐元素按位或（OR）         |
| ^    | bvector      | bvector      | bvector  | 逐元素按位异或（XOR）      |
| =    | vector       | vector       | boolean  | 字典序比较                 |
| =    | vecf16       | vecf16       | boolean  | 字典序比较                 |
| =    | veci8        | veci8        | boolean  | 字典序比较                 |
| =    | svector      | svector      | boolean  | 字典序比较                 |
| =    | bvector      | bvector      | boolean  | 字典序比较                 |
| <>   | vector       | vector       | boolean  | 字典序比较                 |
| <>   | vecf16       | vecf16       | boolean  | 字典序比较                 |
| <>   | veci8        | veci8        | boolean  | 字典序比较                 |
| <>   | svector      | svector      | boolean  | 字典序比较                 |
| <>   | bvector      | bvector      | boolean  | 字典序比较                 |
| <    | vector       | vector       | boolean  | 字典序比较                 |
| <    | vecf16       | vecf16       | boolean  | 字典序比较                 |
| <    | veci8        | veci8        | boolean  | 字典序比较                 |
| <    | svector      | svector      | boolean  | 字典序比较                 |
| <    | bvector      | bvector      | boolean  | 字典序比较                 |
| >    | vector       | vector       | boolean  | 字典序比较                 |
| >    | vecf16       | vecf16       | boolean  | 字典序比较                 |
| >    | veci8        | veci8        | boolean  | 字典序比较                 |
| >    | svector      | svector      | boolean  | 字典序比较                 |
| >    | bvector      | bvector      | boolean  | 字典序比较                 |
| <=   | vector       | vector       | boolean  | 字典序比较                 |
| <=   | vecf16       | vecf16       | boolean  | 字典序比较                 |
| <=   | veci8        | veci8        | boolean  | 字典序比较                 |
| <=   | svector      | svector      | boolean  | 字典序比较                 |
| <=   | bvector      | bvector      | boolean  | 字典序比较                 |
| >=   | vector       | vector       | boolean  | 字典序比较                 |
| >=   | vecf16       | vecf16       | boolean  | 字典序比较                 |
| >=   | veci8        | veci8        | boolean  | 字典序比较                 |
| >=   | svector      | svector      | boolean  | 字典序比较                 |
| >=   | bvector      | bvector      | boolean  | 字典序比较                 |
| <->  | vector       | vector       | real     | 平方欧氏距离               |
| <->  | vecf16       | vecf16       | real     | 平方欧氏距离               |
| <->  | veci8        | veci8        | real     | 平方欧氏距离               |
| <->  | svector      | svector      | real     | 平方欧氏距离               |
| <->  | bvector      | bvector      | real     | 平方欧氏距离               |
| <#>  | vector       | vector       | real     | 负点积                     |
| <#>  | vecf16       | vecf16       | real     | 负点积                     |
| <#>  | veci8        | veci8        | real     | 负点积                     |
| <#>  | svector      | svector      | real     | 负点积                     |
| <#>  | bvector      | bvector      | real     | 负点积                     |
| <=>  | vector       | vector       | real     | 余弦距离                   |
| <=>  | vecf16       | vecf16       | real     | 余弦距离                   |
| <=>  | veci8        | veci8        | real     | 余弦距离                   |
| <=>  | svector      | svector      | real     | 余弦距离                   |
| <=>  | bvector      | bvector      | real     | 余弦距离                   |
| <~>  | bvector      | bvector      | real     | 杰卡德距离（Jaccard 距离） |
{.wide .expand}

## 函数列表 {#list-of-functions}

| 名称               | 参数类型                                    | 返回类型 | 说明                                                                       |
| ------------------ | ------------------------------------------- | -------- | -------------------------------------------------------------------------- |
| pgvectors_upgrade  |                                             | void     | 用于升级 `pgvecto.rs` 的管理函数。                                         |
| to_svector         | dims integer, index integer[], value real[] | svector  | 根据下标数组和值数组构造一个稀疏向量。                                     |
| binarize           | vector vector                               | bvector  | 将向量二值化：所有正数元素设为 1，其余元素设为 0。                         |
| text2vec_openai    | input text, model text                      | vector   | 调用 OpenAI Embeddings API 的嵌入生成函数。                                |
| text2vec_openai_v3 | input text                                  | vector   | 调用 OpenAI Embeddings API 的嵌入生成函数，默认模型设为 `text-embedding-3-small`。 |
{.wide .expand}

## 类型转换列表 {#list-of-casts}

| 源类型  | 目标类型 | 是否隐式转换？ |
| ------- | -------- | -------------- |
| real[]  | vector   | yes            |
| vector  | real[]   | yes            |
| vector  | vecf16   | no             |
| vecf16  | vector   | no             |
| vector  | veci8    | no             |
| veci8   | vector   | no             |
| vector  | svector  | no             |
| svector | vector   | no             |
| vector  | bvector  | no             |
| bvector | vector   | no             |
{.wide .expand}

## 访问方法（Access Methods）列表 {#list-of-access-methods}

| 名称    | 类型  | 说明                    |
| ------- | ----- | ----------------------- |
| vectors | Index | pgvecto.rs 向量索引方法 |
{.wide .expand}

## 操作符族（Operator Families）列表 {#list-of-operator-families}

| 访问方法 | 操作符族            | 适用类型 |
| -------- | ------------------- | -------- |
| vectors  | vector_cos_ops      | vector   |
| vectors  | vector_dot_ops      | vector   |
| vectors  | vector_l2_ops       | vector   |
| vectors  | vecf16_cos_ops      | vecf16   |
| vectors  | vecf16_dot_ops      | vecf16   |
| vectors  | vecf16_l2_ops       | vecf16   |
| vectors  | veci8_cos_ops       | veci8    |
| vectors  | veci8_dot_ops       | veci8    |
| vectors  | veci8_l2_ops        | veci8    |
| vectors  | svector_cos_ops     | svector  |
| vectors  | svector_dot_ops     | svector  |
| vectors  | svector_l2_ops      | svector  |
| vectors  | bvector_cos_ops     | bvector  |
| vectors  | bvector_dot_ops     | bvector  |
| vectors  | bvector_l2_ops      | bvector  |
| vectors  | bvector_jaccard_ops | bvector  |
{.wide .expand}

## 操作符类（Operator Classes）列表 {#list-of-operator-classes}

| 访问方法 | 输入类型 | 操作符类            | 是否默认？ | 说明                       |
| -------- | -------- | ------------------- | ---------- | -------------------------- |
| vectors  | vector   | vector_l2_ops       | no         | 平方欧氏距离               |
| vectors  | vector   | vector_dot_ops      | no         | 负点积                     |
| vectors  | vector   | vector_cos_ops      | no         | 余弦距离                   |
| vectors  | vecf16   | vecf16_l2_ops       | no         | 平方欧氏距离               |
| vectors  | vecf16   | vecf16_dot_ops      | no         | 负点积                     |
| vectors  | vecf16   | vecf16_cos_ops      | no         | 余弦距离                   |
| vectors  | veci8    | veci8_l2_ops        | no         | 平方欧氏距离               |
| vectors  | veci8    | veci8_dot_ops       | no         | 负点积                     |
| vectors  | veci8    | veci8_cos_ops       | no         | 余弦距离                   |
| vectors  | svector  | svector_l2_ops      | no         | 平方欧氏距离               |
| vectors  | svector  | svector_dot_ops     | no         | 负点积                     |
| vectors  | svector  | svector_cos_ops     | no         | 余弦距离                   |
| vectors  | bvector  | bvector_l2_ops      | no         | 平方欧氏距离               |
| vectors  | bvector  | bvector_dot_ops     | no         | 负点积                     |
| vectors  | bvector  | bvector_cos_ops     | no         | 余弦距离                   |
| vectors  | bvector  | bvector_jaccard_ops | no         | 杰卡德距离（Jaccard 距离） |
{.wide .expand}

## 视图列表 {#list-of-views}

| 名称                 | 说明                           |
| -------------------- | ------------------------------ |
| pg_vector_index_stat | 提供向量索引统计信息的监控视图 |
{.wide .expand}
