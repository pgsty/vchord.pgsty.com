---
title: "绑定信用卡订阅"
linkTitle: "信用卡"
description: "VectorChord Cloud 支持信用卡支付。您可以添加多张信用卡，或点击 Delete 移除已有信用卡。已添加的信用卡将显示在计费页面上。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/payment/credit-card.md"
---

> [!TIP]
> 计费以项目（Project）为单位，而非按用户计费。每个项目都有独立的账单发票，您必须为每个项目分别添加支付方式。


VectorChord Cloud 支持信用卡支付。您可以添加多张信用卡，也可以点击 `Delete` 移除其中部分信用卡。已添加的信用卡将显示在计费页面上。

![](/cloud/images/billing_page.png)

点击 `Add Payment Method` 按钮将跳转至 Stripe 的添加信用卡页面（`Add Credit Card page`），我们将在该页面发起信用卡预授权请求。此请求不会产生任何实际扣费。添加请求完成后，新信用卡即可使用并显示在 `Billing` 页面上。

![](/cloud/images/billing_add_card.png)

> [!WARNING]
> 每个项目的最后一张信用卡无法删除。
