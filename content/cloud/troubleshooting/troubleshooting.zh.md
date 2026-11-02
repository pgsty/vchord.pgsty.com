---
title: "故障排查"
linkTitle: "故障排查"
description: "如果集群状态变为 NotReady，您可以检查集群的监控指标，查看 PGData 是否仍有可用空间。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/troubleshooting/troubleshooting.md"
---

<a id="Connectivity"></a>
## 连接问题 {#connectivity}

### 1. 集群无法访问，请检查以下内容： {#1-cluster-is-not-reachable-you-can-check-the-following}

如果集群的状态显示为 `NotReady`，您可以检查集群的监控指标，查看 PGData 是否仍有剩余可用空间。

> [!WARNING]
> 请勿删除您的集群，否则将导致数据丢失。

**解决方案**：
- 您可以将集群扩容到更大的存储规格以解决该问题，具体操作请参阅[仅扩容集群存储空间](/zh/cloud/manage/upgrade/#increasing-only-storage)。升级完成后，集群状态将恢复为 `Ready`，并可正常访问。

如果上述方案未能解决问题，请通过 [Discord](https://discord.com/channels/974584200327991326/1243043133801889792) 联系我们，我们很乐意为您提供帮助。
