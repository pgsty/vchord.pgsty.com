---
title: "Subscribe by Adding Credit Card"
linkTitle: "Credit Card"
description: "VectorChord Cloud supports credit card payments. You can add multiple credit cards or remove some of them by clicking Delete. Already added credit cards will be"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/payment/credit-card.md"
---

> [!TIP]
> Billing is for the project, not the user. There are separate invoices for each project, and you must add the payment method separately.


VectorChord Cloud supports credit card payments. You can add multiple credit cards or remove some of them by clicking `Delete`. Already added credit cards will be displayed on the billing page.

![](/cloud/images/billing_page.png)

The `Add Payment Method` button will take you to Stripe's `Add Credit Card page` where we will initiate a credit card pre-authorization request. There is no charge for this request. Once the add request is complete, the new credit card will be available and displayed on the `Billing` page.

![](/cloud/images/billing_add_card.png)

> [!WARNING]
> The last credit card for each project cannot be deleted.
