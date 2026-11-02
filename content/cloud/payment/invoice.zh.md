---
title: "查看账单发票"
linkTitle: "账单发票"
description: "目前 VectorChord Cloud 使用 Orb 作为计费服务商。在 Billing 页面中，您可以点击 View invoices in Orb 前往 Orb 客户门户。"
weight: 20
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/payment/invoice.md"
---

目前 VectorChord Cloud 使用 Orb 作为计费服务商。在计费（Billing）页面中，您可以点击 `View invoices in Orb` 前往 Orb 的客户门户（`Customer Portal`）。在该外部页面上，您可以执行以下操作：

- 查看计算资源和存储空间用量
- 查看已支付、已开具以及草稿状态的账单发票
- 支付自动扣款失败的账单发票

![](/cloud/images/billing_invoice_intro.png)

## 查看资源用量 {#review-the-amount-of-usage}

在 `Customer Portal` 的 `Overview` 页面上，您可以通过 `Current Billing Period`（当前计费周期）区域查看近期用量：

![](/cloud/images/billing_invoice_current_period.png)

- 标题以 `AWS` 开头的柱状图表示计算资源用量，单位为小时（h）。
- 标题以 `EBS` 开头的柱状图表示磁盘空间用量，单位为吉字节·小时（Gi*h）。

## 查看历史账单发票 {#review-your-invoices}

在 `Customer Portal` 的 `Invoice History`（账单历史）页面上，您可以查看所有历史账单发票及其随时间变化的资源用量。

![](/cloud/images/billing_invoice_list.png)

点击任意一行即可查看该账单发票的详细明细。

![](/cloud/images/billing_invoice_detail.png)

## 手动支付未扣款成功的账单 {#manually-pay-uncharged-invoices}

对于每张到期的账单发票，VectorChord Cloud 会在一周内自动尝试扣款 3 次。如果所有尝试均失败，您的项目将被暂停（Suspended）：

- 您将收到一封电子邮件，通知您该项目已被暂停
- 您将无法在该项目下创建新集群
- 该项目下现有的集群将被暂停运行
- 被暂停集群中的数据将保留 7 天

![](/cloud/images/billing_manual_pay.png)

这些账单发票会显示在 `Overview` 页面的 `Unpaid Invoices`（未付账单）区域中，状态为 `failed` 或 `issued`，您可以手动完成支付。
