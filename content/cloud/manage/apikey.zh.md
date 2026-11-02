---
title: "API 密钥"
linkTitle: "API 密钥"
description: "在 VectorChord Cloud 中，每个项目都提供一组 API 密钥。这些密钥是发起 Terraform 操作所必需的身份认证令牌。"
weight: 70
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/apikey.md"
---

在 VectorChord Cloud 中，每个项目都提供一组 API 密钥（API Key）。这些密钥是发起 Terraform 操作所必需的身份认证令牌。

## 基于角色的访问控制（RBAC） {#role-based-access-control-rbac}

基于角色的访问控制（RBAC）是 VectorChord Cloud 中一项至关重要的安全机制，适用于管理 API 调用。该系统通过为项目内的用户分配具有特定权限的角色，实现对资源的细粒度访问控制。

有关各个角色访问权限级别的更多信息，请参阅[权限与授权](/zh/cloud/manage/authorization/)。

![](/cloud/images/apikey-rbac.png)

## 创建 API 密钥 {#create-an-api-key}

要创建 API 密钥，请按以下步骤操作：
- 在左侧菜单中进入 **API Key** 页面。
- 点击 **Create API Key** 按钮。
- 输入 API 密钥的名称。
- 为 API 密钥选择角色：
    - **Owner**（所有者）：对项目集群拥有完全访问权限。
    - **Member**（成员）：对项目集群拥有只读访问权限；但您可以指定该成员拥有完全访问权限的特定集群。
- 点击 **Create** 按钮。

![](/cloud/images/apikey-create.png)

## 删除 API 密钥 {#delete-an-api-key}

要删除 API 密钥，请按以下步骤操作：
- 在左侧菜单中进入 **API Key** 页面。
- 点击您想要删除的 API 密钥旁边的 **Delete** 按钮。

![](/cloud/images/apikey-delete.png)

> [!WARNING]
> 请注意，API 密钥一旦删除便无法恢复。


## 查看 API 密钥列表 {#list-of-api-keys}

要查看 API 密钥列表，请按以下步骤操作：
- 在左侧菜单中进入 **API Key** 页面。
- 您可以查看所有 API 密钥及其对应的角色。

> [!WARNING]
> 如果您不是项目所有者（Owner），您将无权查看 API 密钥列表。
