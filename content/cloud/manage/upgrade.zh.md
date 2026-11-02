---
title: "升级集群"
linkTitle: "升级集群"
description: "您可能需要升级集群且不希望丢失任何数据。您可以升级 CPU、内存等服务器资源，也可以仅扩容存储空间。"
weight: 60
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/upgrade.md"
---

您可能需要升级集群且不希望丢失任何数据。您可以升级 CPU、内存等服务器资源，也可以仅扩容存储空间。以下章节将引导您完成集群升级流程。

## 扩容服务器资源 {#increasing-server-resource}

如果您想扩容 CPU 和内存等服务器资源，集群状态必须处于 `Ready`。在集群详情页面点击 `Upgrade` 按钮。

![](/cloud/images/upgrade-click.png)

在升级页面中，您可以选择新的套餐和服务器资源规格。价格将根据新的服务器资源规格进行计算。点击 `Submit` 按钮提交集群升级。

![](/cloud/images/upgrade-server-resource.png)

提交升级请求后，集群将进入 `Upgrading` 状态。在升级过程中集群将暂时不可用，升级过程可能需要几分钟才能完成。升级完成后，集群将恢复为 `Ready` 状态，CPU 和内存将更新为新的服务器资源规格，而存储空间保持不变。

![](/cloud/images/upgrade-status.png)

## 仅扩容存储空间 {#increasing-only-storage}

如果您只想增加存储空间，集群状态必须处于 `Ready`。在集群详情页面点击 `Upgrade` 按钮。

![](/cloud/images/upgrade-click.png)

在升级页面中，您可以在高级选项（Advanced Options）中输入新的磁盘大小。价格将根据新的存储空间大小进行计算。点击 `Submit` 按钮提交集群升级。

![](/cloud/images/upgrade-storage.png)

几分钟后，集群状态将从 `Upgrading` 变为 `Ready`。存储空间将更新为新的容量大小，而 CPU 和内存保持不变。

![](/cloud/images/upgrade-storage-new.png)

如果您希望同时升级服务器资源规格和存储空间，可以直接在升级页面中同时选择新的服务器资源规格并填写磁盘大小，价格将根据新的服务器资源规格和存储容量进行计算。目前我们不支持降配服务器资源规格或缩减存储空间。如果您需要降配服务器资源规格或存储大小，请联系[我们](https://discord.com/channels/974584200327991326/1243043133801889792)获取协助。
