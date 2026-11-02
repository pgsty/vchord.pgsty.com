---
title: "Overview of the cloud object hierarchy"
linkTitle: "Overview"
description: "Managing your VectorChord Cloud project requires an understanding of the object hierarchy. The following diagram shows how objects in cloud are related. See bel"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/overview.md"
---

Managing your VectorChord Cloud project requires an understanding of the object hierarchy. The following diagram shows how objects in cloud are related. See below for a description of each object.
![](/cloud/images/cloud_object_hierarchy.png)

## VectorChord Cloud Account

This is the account you used to sign up with VectorChord Cloud. Now supports signing up with an GitHub account.

<a id="Projects"></a>
## Projects

A project is the top-level object in the hierarchy. It is a container for all clusters in the project and billing information. For more information, see [Projects](/cloud/manage/project/).

<a id="Clusters"></a>
## Clusters

A project can contain one or more clusters. A cluster is a collection of nodes that run one `Postgres` cluster. For more information, see [Clusters](/cloud/manage/cluster/).

## Compute Instances

A cluster can contain one or more compute instances. A compute instance is a virtual machine that runs a `Postgres` instance.

<a id="Databases"></a>
## Databases

Every cluster contains two default databases: `postgres` and a database what you named when you created the cluster. You can create additional databases in a cluster with [psql](/cloud/connect/connect-with-psql/) after the cluster is ready.
