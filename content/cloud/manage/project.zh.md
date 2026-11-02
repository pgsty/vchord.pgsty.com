---
title: "项目"
linkTitle: "项目"
description: "在 VectorChord Cloud 中，一切都从项目开始。它是层级结构中的顶层对象，一个项目可以根据需要容纳任意数量的 Postgres 集群。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/project.md"
---

在 VectorChord Cloud 中，一切都从项目（Project）开始。它是层级结构中的顶层对象。一个项目可以根据需要容纳任意数量的 `Postgres` 集群。您最多可以创建和加入 5 个项目。

通过以下章节进一步了解项目及其管理方式：
- [项目设置](#project-setting)
- [项目计费](#project-billing)


## 项目设置 {#project-setting}

在项目设置中，您可以查看和编辑项目信息。点击页面左下角的项目名称即可切换到其他项目。默认项目是您注册时系统为您创建的第一个项目。如下图所示，您可以修改项目名称、邀请成员加入项目以及退出项目。

![](/cloud/images/project_info.png)

## 项目权限 {#project-permissions}

您可以点击 `Invite` 按钮邀请其他用户加入您的项目。您可以通过电子邮件地址邀请用户，受邀用户将收到一封包含邀请链接的电子邮件，点击该链接即可接受邀请。

> [!WARNING]
> 如果受邀用户尚未注册 VectorChord Cloud 账户，则需要先注册一个账户，然后才能接受邀请。


![](/cloud/images/invite_member.png)

有关各个角色访问权限级别的更多信息，请参阅[权限与授权](/zh/cloud/manage/authorization/)。

## 项目计费 {#project-billing}

每个项目都有一个专属计费页面，您可以在其中查看计费信息。在计费页面中，您可以添加支付方式并查看账单发票。

![](/cloud/images/project_billing.png)
