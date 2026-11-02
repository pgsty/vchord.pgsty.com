---
title: "为 PGVecto.rs Cloud 引入 Terraform 支持"
date: 2024-07-24
description: "像管理其他基础设施组件一样，使用 Terraform 管理 PGVecto.rs Cloud"
author: "[xieydd](https://github.com/xieydd) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
upstream_link: "https://blog.vectorchord.ai/introducing-terraform-support-for-pgvectors-cloud"
upstream_copyright: "© 2024 xieydd (TensorChord Inc.)"
aliases:
  - "/blog/introducing-terraform-support-for-pgvectors-cloud/"
  - "/introducing-terraform-support-for-pgvectors-cloud/"
authors: ["xieydd"]
images: ["/blog/covers/introducing-terraform-support-for-pgvectors-cloud.png"]
---

我们非常高兴地宣布发布适用于 [PGVecto.rs Cloud 的 Terraform Provider](https://registry.terraform.io/providers/tensorchord/pgvecto-rs-cloud/latest)。这一全新 Provider 旨在简化我们[云服务](/zh/cloud/)上的资源管理流程，让用户能够通过基础设施即代码（IaC）工具 **Terraform**，以直观、高效的方式管理 Postgres 集群的部署与运维。对于尚不熟悉 [Terraform](https://www.terraform.io/) 的读者，它是一款开源工具，用于安全、高效地构建、变更和版本化管理基础设施。它支持用户将基础设施定义为代码，从而以编程方式调配和管理各类资源。

# 关于 PGVecto.rs：Postgres 中的可扩展向量搜索 {#a-word-about-pgvectors-scalable-vector-search-in-postgres}

[PGVecto.rs](/zh/docs/vectors/) 是一款 Postgres 扩展，支持可扩展的向量搜索，让你能够在 Postgres 数据库之上构建强大的相似度检索应用。

PGVecto.rs 凭借多项强大特性脱颖而出：

* **更出色的过滤能力**：支持应用任意过滤条件并与其他表进行 JOIN，在实现高召回率与低延迟的同时，展现出相比其他向量数据库的独特优势。
    
* **混合搜索（Hybrid Search）**：结合 PostgreSQL 的全文检索功能与 pgvecto.rs，在单条查询中同时检索文本和向量数据。
    
* **超长向量维度支持**：PGVecto.rs 支持最高 65535 维的向量长度，非常契合最新的大模型需求。
    
* **快上加快**：比其他基于 Postgres 的解决方案快 4 倍。
    
* **二值向量搜索**：通过采用自适应检索技术，二值向量在保持高精度的同时，可将内存占用大幅降低 30 倍。
    
* **完整的 SQL 支持**：提供完整的 SQL 支持，无需额外配置即可不受限制地使用 JOIN 和过滤条件。
    

# **如何开始使用 Terraform 与 PGVecto.rs Cloud** {#how-to-get-started-with-terraform-and-pgvectors-cloud}

本指南将带你完成 PGVecto.rs Cloud Provider 的安装与配置流程。

## **前置条件** {#prerequisites}

在开始之前，请确保你已具备以下条件：

1. 已安装 Terraform：请访问[**此处**](https://www.terraform.io/downloads.html)，按照说明下载并安装 Terraform。
    
2. PGVecto.rs Cloud 账号：你需要拥有 PGVecto.rs Cloud 的访问权限及 API Key。请前往 [**PGVecto.rs Cloud 控制台**](/zh/cloud/manage/apikey/)创建 API Key。该 API Key 必须具备 `ProjectOwner` 权限。
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1721659329747/ec3dba71-1794-4ad7-8d27-60b8af568d0f.png)

<a id="download-pgvecto-rs-cloud-terraform-provider"></a>
## **下载 PGVecto.rs Cloud Terraform Provider** {#download-pgvectors-cloud-terraform-provider}

首先，在你的 Terraform 配置文件（[`main.tf`](http://main.tf)）中配置 PGVecto.rs Cloud Provider，步骤如下：

```ini
terraform {
  required_providers {
    pgvecto-rs-cloud = {
      source = "tensorchord/pgvecto-rs-cloud"
    }
  }
}
```

## **初始化 Terraform 配置** {#initialize-terraform-configuration}

```bash
$ terraform init --upgrade

Initializing the backend...

Initializing provider plugins...
- Finding latest version of tensorchord/pgvecto-rs-cloud...
- Installing tensorchord/pgvecto-rs-cloud v0.0.6...
- Installed tensorchord/pgvecto-rs-cloud v0.0.6 (self-signed, key ID ABEFCD2BB128AAB1)

Partner and community providers are signed by their developers.
If you'd like to know more about provider signing, you can read about it here:
https://www.terraform.io/docs/cli/plugins/signing.html

Terraform has created a lock file .terraform.lock.hcl to record the provider
selections it made above. Include this file in your version control repository
so that Terraform can guarantee to make the same selections by default when
you run "terraform init" in the future.

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

Terraform 会下载 `pgvecto-rs-cloud` Provider，并将其安装到当前工作目录下名为 `.terraform` 的隐藏子目录中。

<a id="authenticate-pgvecto-rs-cloud-terraform-provider"></a>
## **为 PGVecto.rs Cloud Terraform Provider 配置认证** {#authenticate-pgvectors-cloud-terraform-provider}

使用该 Terraform Provider 需要提供你的 PGVecto.rs Cloud API Key。共有两种配置方式：

### **方式 1：在 Provider 块中指定 API Key** {#option-1-specify-api-key-in-provider-block}

将以下代码追加到你的 `main.tf` 文件中：

```ini
provider "pgvecto-rs-cloud" {
  api_key = "<your-api-key>"
}
```

### **方式 2：使用环境变量** {#option-2-use-environment-variable}

将 API Key 设置为环境变量：

```bash
export PGVECTORS_CLOUD_API_KEY="<your-api-key>"
```

此时，你的 [`main.tf`](http://main.tf) 文件中的 Provider 声明只需写成：

```ini
provider "pgvecto-rs-cloud" {
}
```

完成以上步骤后，PGVecto.rs Cloud Terraform Provider 就已配置就绪，可以继续后续操作了。

<a id="manage-pgvecto-rs-cloud-cluster"></a>
## **管理 PGVecto.rs Cloud 集群** {#manage-pgvectors-cloud-cluster}

### **创建集群实例** {#create-an-enterprise-plan}

以下示例展示了如何创建一个 PostgreSQL 集群。关于各配置项的更多信息，请参考 [**Resource Schema**](https://registry.terraform.io/providers/tensorchord/pgvecto-rs-cloud/latest/docs/resources/cluster)。

你可以从云控制台获取 `account_id`：点击右上角的头像，然后点击 Profile（个人资料）。

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1721695021315/1e8dd3e9-673b-4a77-b3f1-8d87e83b9318.png)

```bash
resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
  account_id   = "58aa09d9-854c-4223-9920-b85b9d878e72"
  cluster_name = "enterprise-plan-cluster"
  plan = "Starter"
  server_resource = "aws-t3-xlarge-4c-16g" // The only server resource supported by the Starter plan, shared environment
  region            = "us-east-1"
  cluster_provider  = "aws"
  database_name     = "test"
  pg_data_disk_size = "10"
  enable_pooler     = true
}

output "psql_endpoint_enterprise" {
  description = "Endpoint for the PGVecto.rs Cloud Starter PostgreSQL database"
  value       = pgvecto-rs-cloud_cluster.enterprise_plan_cluster.connect_endpoint
}
```

你可以按以下步骤验证 Terraform 代码：

```bash
$ terraform validate && terraform plan && terraform output
Success! The configuration is valid.


Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id        = "58aa09d9-854c-4223-9920-b85b9d878e72"
      + cluster_name      = "enterprise-plan-cluster"
      + cluster_provider  = "aws"
      + connect_endpoint  = (known after apply)
      + database_name     = "test"
      + enable_pooler     = true
      + id                = (known after apply)
      + last_updated      = (known after apply)
      + pg_data_disk_size = "10"
      + plan              = "Starter"
      + region            = "us-east-1"
      + server_resource   = "aws-t3-xlarge-4c-16g"
      + status            = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + psql_endpoint_enterprise = (known after apply)

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly these actions if you run "terraform apply" now.
╷
│ Warning: No outputs found
│
│ The state file either has no outputs defined, or all the defined outputs are empty. Please define an output in your configuration with the `output` keyword and run `terraform refresh` for it to become available. If you are using
│ interpolation, please verify the interpolated value is not empty. You can use the `terraform console` command to assist.
```

接着运行以下命令生成执行计划；确认无误后即可应用该计划。应用完成后，Postgres 集群将在你的 PGVecto.rs Cloud 账号中创建完毕。

```bash
$ terraform apply

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id        = "58aa09d9-854c-4223-9920-b85b9d878e72"
      + cluster_name      = "enterprise-plan-cluster"
      + cluster_provider  = "aws"
      + connect_endpoint  = (known after apply)
      + database_name     = "test"
      + enable_pooler     = true
      + id                = (known after apply)
      + last_updated      = (known after apply)
      + pg_data_disk_size = "10"
      + plan              = "Starter"
      + region            = "us-east-1"
      + server_resource   = "aws-t3-xlarge-4c-16g"
      + status            = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + psql_endpoint_enterprise = (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Creating...
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [10s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [20s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [30s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [40s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [50s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m0s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m10s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m20s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m30s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m40s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [1m50s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [2m0s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [2m10s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Creation complete after 2m18s [id=ee6d7049-78c4-4776-8e2a-25dd5970007d]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

psql_endpoint_enterprise = "postgres://test_user:fC5PHTFaflwK@enterprise-plan-cluster-jeyahasdf1r957q4.pooler.us-east-1.aws.pgvecto.rs:5432/test?sslmode=require"
```

你可以使用 [psql](https://www.postgresql.org/docs/current/app-psql.html) 通过输出的连接字符串连接到数据库。随后可以执行 `\dx` 查看已安装的扩展，并创建一个 `hnsw` 索引来验证 `vectors` 扩展是否已成功安装。

```bash
$ psql 'postgres://test_user:fC5PHTFaflwK@enterprise-plan-cluster-unn3o7zyzdkrrxpe.us-east-1.aws.pgvecto.rs:5432/test?sslmode=require'
psql (15.3, server 16.3 (Debian 16.3-1.pgdg110+1))
WARNING: psql major version 15, server major version 16.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

test=> \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description
---------+---------+------------+----------------------------------------------------------------------------------------------
 pgaudit | 16.0    | public     | provides auditing functionality
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vectors | 0.3.0   | vectors    | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
(3 rows)

test=> CREATE TABLE test (id integer PRIMARY KEY, embedding vector(3) NOT NULL);
CREATE TABLE
test=> INSERT INTO test SELECT i, ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 100) i;
INSERT 0 100
test=> CREATE INDEX ON test USING vectors (embedding vector_l2_ops) WITH (options = "[indexing.hnsw]");
CREATE INDEX
test=> SELECT * FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402]' LIMIT 10;
 id |              embedding
----+--------------------------------------
 58 | [0.37351534, 0.13275076, 0.43973163]
 66 | [0.22059213, 0.27068633, 0.22881117]
 10 | [0.26735276, 0.39847502, 0.20896937]
 72 | [0.23406255, 0.4242782, 0.27623454]
 65 | [0.4541286, 0.48433396, 0.48011246]
 80 | [0.6192282, 0.14963196, 0.5095764]
 47 | [0.48413, 0.46047017, 0.21654463]
 97 | [0.445769, 0.27853656, 0.6808209]
 25 | [0.1864713, 0.015588521, 0.3540618]
 63 | [0.26299608, 0.0640332, 0.5937908]
(10 rows)
```

### **升级集群** {#upgrade-the-cluster}

目前我们支持对服务器规格（`server_resource`）、套餐类型（`plan`）以及磁盘容量（`pg_data_disk_size`）进行升级。升级操作存在以下约束：

* 套餐升级必须是从 `Starter` 升级到 `Enterprise`。
    
* 新的磁盘大小必须大于或等于原有大小。
    
* 如果要在 `Enterprise` 套餐中升级服务器规格，新服务器规格的 CPU 和内存必须大于或等于原有规格。
    

```diff
+ server_resource   = "aws-r7i-large-2c-16g"
- server_resource   = "aws-m7i-large-2c-8g"
+ pg_data_disk_size = "20"
- pg_data_disk_size = "10"
+ plan = "Enterprise"
- plan = "Starter"
```

```bash
$ terraform apply
```

### **销毁集群** {#destroy-the-cluster}

> 注意：一旦删除集群将无法恢复，请务必谨慎操作。

如果你需要删除 Postgres 集群，可以使用以下命令：

```bash
$ terraform destroy
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Refreshing state... [id=ee6d7049-78c4-4776-8e2a-25dd5970007d]

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be destroyed
  - resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      - account_id        = "58aa09d9-854c-4223-9920-b85b9d878e72" -> null
      - cluster_name      = "enterprise-plan-cluster" -> null
      - cluster_provider  = "aws" -> null
      - connect_endpoint  = "postgres://test_user:fC5PHTFaflwK@enterprise-plan-cluster-jeyahasdf1r957q4.pooler.us-east-1.aws.pgvecto.rs:5432/test?sslmode=require" -> null
      - database_name     = "test" -> null
      - enable_pooler     = true -> null
      - id                = "ee6d7049-78c4-4776-8e2a-25dd5970007d" -> null
      - last_updated      = "Tuesday, 23-Jul-24 00:52:55 UTC" -> null
      - pg_data_disk_size = "10" -> null
      - plan              = "Starter" -> null
      - region            = "us-east-1" -> null
      - server_resource   = "aws-t3-xlarge-4c-16g" -> null
      - status            = "Ready" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  - psql_endpoint_enterprise = "postgres://test_user:fC5PHTFaflwK@enterprise-plan-cluster-jeyahasdf1r957q4.pooler.us-east-1.aws.pgvecto.rs:5432/test?sslmode=require" -> null

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Destroying... [id=ee6d7049-78c4-4776-8e2a-25dd5970007d]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Destruction complete after 1s

Destroy complete! Resources: 1 destroyed.
```

# **总结** {#conclusion}

将 Terraform 集成到 PGVecto.rs Cloud 中，为希望在 Postgres 上利用先进向量搜索能力的企业和开发者提供了一套强大的解决方案。这种自动化的基础设施即代码（IaC）方法不仅简化了部署流程，还增强了应用的稳健性与可扩展性。如果你有任何疑问或在 Terraform Provider 中发现了安全问题，[欢迎联系我们](https://discord.gg/KqswhpVgdU)，我们将非常乐意为你提供帮助。
