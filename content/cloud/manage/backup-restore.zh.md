---
title: "备份与恢复"
linkTitle: "备份与恢复"
description: "数据库备份是任何灾难恢复计划中不可或缺的一部分。通过数据库备份，您可以在灾难发生时将项目恢复到任意时间点，从而化解危机。"
weight: 50
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/backup-restore.md"
---

数据库备份是任何灾难恢复计划中不可或缺的一部分。灾难的形式多种多样，可能小到不小心误删了表中的一列、数据库崩溃，甚至大到自然灾害彻底损毁了数据库所运行的底层硬件。这些场景带来的风险和影响永远无法完全消除，只能尽可能降低或缓解。拥有数据库备份就像购买了一份保险：它们本质上是数据库在不同时间点的快照。当灾难来临时，数据库备份能够将项目恢复到这些时间点中的任意一个，从而化解危机。

> [!WARNING]
> 一旦您删除该集群或项目，Postgres 中的所有数据（包括 WAL 日志）以及集群中自动创建或按需创建的备份也将一并被删除。


<a id="Backup"></a>
## 备份 {#backup}

<a id="Concepts"></a>
### 概念 {#concepts}

- **WAL 归档（WAL archive）**：用于存放 Postgres 持续写入并归档以保障数据持久性的 WAL 文件（事务日志）的存储位置。
- **物理基础备份（Physical base backups）**：PostgreSQL 用于在数据库中存储数据的所有文件（主要是 PGDATA 和所有表空间）的完整副本。

### 自动备份 {#automatic-backups}

集群创建完成后，默认启用自动备份功能。系统每天会自动执行一次物理基础备份，并保留 7 天。备份存储在 AWS S3 中，AWS S3 的保留策略设置为 90 天。

与此同时，WAL（预写式日志，Write-Ahead Logging）每 5 分钟归档一次。如果这些文件超过特定的文件大小阈值，则会立即触发备份。因此，在事务量较高的时段，WAL 文件备份会更加频繁；反之，当数据库没有活动时，则不会生成 WAL 文件备份。总体而言，这意味着在最坏情况或发生灾难时，按时间点恢复（PITR，Point-In-Time Recovery）能够实现 5 分钟的恢复点目标（RPO）。

### 按需备份 {#on-demand-backups}

如果您希望在特定时间点创建备份，可以创建按需备份（On-demand Backup）。按需备份是数据库集群的物理基础备份，默认保留 7 天。它们存储在 AWS S3 中，最长可保留 90 天。

您可以按照以下步骤创建按需备份：
- 点击 `Actions` 按钮并选择 `Backup`。
    ![](/cloud/images/click-backup.png)
- 为备份设置唯一名称。
    ![](/cloud/images/backup-name.png)

您可以在 `Backups` 标签页中查看备份信息，其中包括：
- 备份名称（Backup name）
- 备份所属的集群
- 备份开始时间（Backup start time）
- 备份结束时间（Backup end time）
- 备份起始 LSN（日志序列号，Log Sequence Number）
- 备份结束 LSN
- 备份起始 WAL 段（WAL segment）
- 备份结束 WAL 段
- 备份阶段状态（Backup phase）

![](/cloud/images/backup-list.png)


<a id="Restore"></a>
## 恢复 {#restore}

### 从集群恢复 {#restore-from-a-cluster}

按时间点恢复（PITR）允许以更短的时间间隔对集群进行持续备份保护，为用户提供精确到秒级粒度的任意时间点恢复能力。如果仅依赖每日备份，一旦发生故障仍可能丢失一整天的数据；而借助 PITR，可以将数据恢复到灾难发生前一刻。

如果您想对集群执行 PITR 恢复，可以按照以下步骤操作：
- 进入集群详情页面。
- 点击 `Actions` 按钮并选择 `Restore from Cluster`。
    ![](/cloud/images/restore-pitr.png)
- 选择要恢复到的目标服务器资源规格。
- 选择要恢复到的目标时间点（Target Time）。
    ![](/cloud/images/target-time.png)
    > [!WARNING]
    > 目标时间点必须介于最早可恢复时间点（First Recoverability Point）与最后归档 WAL 时间（Last Archived WAL Time）之间。



### 从按需备份恢复 {#restore-from-an-on-demand-backup}

如果您想从按需备份进行恢复，可以按照以下步骤操作：
- 进入集群的备份详情页面。
- 点击 `Actions` 按钮并选择 `Restore`。
    ![](/cloud/images/restore-backup.png)
- 选择要恢复到的目标服务器资源规格。

![alt text](/cloud/images/restore-backup-cluster.png)


> [!WARNING]
> 恢复目标集群必须与备份具有相同的镜像（Image）、数据库名称（Database Name）和区域（Region），但从集群直接执行恢复（PITR）支持跨区域恢复。
