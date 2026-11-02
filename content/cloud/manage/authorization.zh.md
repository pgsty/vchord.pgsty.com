---
title: "权限与授权"
linkTitle: "权限与授权"
description: "与 VectorChord Cloud 集群上的基于角色的访问控制（RBAC）相关的主题。"
weight: 40
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/authorization.md"
---

与 VectorChord Cloud 集群上的基于角色的访问控制（RBAC）相关的主题。

## 用户角色 {#user-roles}

我们为项目提供两种类型的用户角色：`Owner`（所有者）和 `Member`（成员）。
- `Owner`：所有者对项目拥有完全访问权限。所有者可以邀请成员、创建或删除集群，以及查看计费信息。
- `Member`：成员对项目拥有只读访问权限。成员可以查看集群信息，但不能创建或删除集群。

## API 密钥角色 {#api-key-roles}

API 密钥通过为项目内的用户分配具有特定权限的角色，提供对资源的更细粒度访问控制。我们为 API 密钥提供两种类型的角色：`Owner`（所有者）和 `Member`（成员）。
- `Owner`：所有者对项目集群拥有完全访问权限。
- `Member`：成员对项目集群拥有只读访问权限。不过，您可以指定该成员拥有完全访问权限的特定集群。

![](/cloud/images/apikey-rbac.png)

## 资源层级结构 {#resource-hierarchy}

有关对象层级结构的更多信息，请参阅[云端对象层级结构概览](/zh/cloud/manage/overview/)。
