---
title: "VectorChord Cloud 的 Terraform 集成概览"
linkTitle: "Terraform"
description: "本指南将带您逐步完成 PGVecto.rs Cloud Provider 的安装与配置。"
weight: 80
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/cloud/manage/terraform.md"
---

本指南将带您逐步完成 PGVecto.rs Cloud Provider 的安装与配置。

## 1. 前置准备 {#1-prerequisites}

在开始之前，请确保您已准备好以下内容：
1. 已安装 Terraform：请访问[此处](https://www.terraform.io/downloads.html)并按照说明下载和安装 Terraform。

2. VectorChord Cloud 账户：您需要拥有 VectorChord Cloud 的访问权限以及 API 密钥。请前往 [VectorChord Cloud 控制台](https://cloud.vectorchord.ai)并创建 API 密钥。该 API 密钥必须具有 `ProjectOwner` 权限。有关更多信息，请参阅 [API 密钥](/zh/cloud/manage/apikey/)。


## 2. 下载 VectorChord Cloud Terraform Provider {#2-download-vectorchord-cloud-terraform-provider}

首先，在您的 Terraform 配置文件（`main.tf`）中配置 VectorChord Cloud Provider：

```hcl
terraform {
  required_providers {
    pgvecto-rs-cloud = {
      source = "tensorchord/pgvecto-rs-cloud"
    }
  }
}
```

## 3. 初始化 Terraform 配置 {#3-initialize-terraform-configuration}

运行以下命令初始化 Terraform 配置：

```bash
$ terraform init

Initializing the backend...

Initializing provider plugins...
- Reusing previous version of tensorchord/pgvecto-rs-cloud from the dependency lock file
- Using previously-installed tensorchord/pgvecto-rs-cloud v0.0.2

Terraform has been successfully initialized!

You may now begin working with Terraform. Try running "terraform plan" to see
any changes that are required for your infrastructure. All Terraform commands
should now work.

If you ever set or change modules or backend configuration for Terraform,
rerun this command to reinitialize your working directory. If you forget, other
commands will detect it and remind you to do so if necessary.
```

Terraform 将下载 `pgvecto-rs-cloud` Provider，并将其安装在当前工作目录下名为 `.terraform` 的隐藏子目录中。

### 4. 认证 VectorChord Cloud Terraform Provider {#4-authenticate-vectorchord-cloud-terraform-provider}

使用该 Terraform Provider 需要提供您的 VectorChord Cloud API 密钥。您可以通过以下两种方式进行配置。

#### 方式 1：在 Provider 块中指定 API 密钥 {#option-1-specify-api-key-in-provider-block}

将以下代码追加到您的 `main.tf` 文件中：

```hcl
provider "pgvecto-rs-cloud" {
  api_key = "<your-api-key>"
}
```

将 `<your-api-key>` 替换为您的 VectorChord Cloud API 密钥。

#### 方式 2：使用环境变量 {#option-2-use-environment-variable}

将 API 密钥设置为环境变量：

```bash
export PGVECTORS_CLOUD_API_KEY="<your-api-key>"
```

此时，您的 `main.tf` 文件中的 Provider 声明只需写为：

```hcl
provider "pgvecto-rs-cloud" {
}
```

完成上述步骤后，VectorChord Cloud Terraform Provider 即已配置完毕，可以继续执行后续操作。

## 4. 管理 VectorChord Cloud 集群 {#4-manage-vectorchord-cloud-cluster}

### 创建企业版套餐集群 {#create-a-enterprise-plan}
以下示例展示了如何创建企业版（Enterprise）套餐的 PostgreSQL 集群。有关配置选项的更多信息，请参阅 [Resource Schema](https://registry.terraform.io/providers/tensorchord/pgvecto-rs-cloud/latest/docs/resources/cluster)。

```hcl
resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
  account_id        = "8364ded2-5580-45c4-a394-edfa582e35a0"
  cluster_name      = "enterprise-plan-cluster"
  plan              = "Enterprise"
  image             = "15-v0.3.0-public"
  server_resource   = "aws-m7i-large-2c-8g"
  region            = "eu-west-1"
  cluster_provider  = "aws"
  database_name     = "test"
  pg_data_disk_size = "10"
}

output "psql_endpoint_enterprise" {
  description = "Endpoint for the VectorChord Cloud Enterprise PostgreSQL database"
  value       = pgvecto-rs-cloud_cluster.enterprise_plan_cluster.connect_endpoint
}
```

```shell
$ terraform validate && terraform plan  && terraform output  
Success! The configuration is valid.


Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id                 = "8364ded2-5580-45c4-a394-edfa582e35a0"
      + cluster_name               = "enterprise-plan-cluster"
      + cluster_provider           = "aws"
      + connect_endpoint           = (known after apply)
      + database_name              = "test"
      + first_recoverability_point = (known after apply)
      + id                         = (known after apply)
      + image                      = "15-v0.3.0-public"
      + last_archived_wal_time     = (known after apply)
      + last_updated               = (known after apply)
      + pg_data_disk_size          = "10"
      + plan                       = "Enterprise"
      + region                     = "eu-west-1"
      + server_resource            = "aws-m7i-large-2c-8g"
      + status                     = (known after apply)
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + psql_endpoint_enterprise = (known after apply)

─────────────────────────────────────────────────────────────────────────────────────────────────────────

Note: You didn't use the -out option to save this plan, so Terraform can't guarantee to take exactly
these actions if you run "terraform apply" now.
╷
│ Warning: No outputs found
│ 
│ The state file either has no outputs defined, or all the defined outputs are empty. Please define an
│ output in your configuration with the `output` keyword and run `terraform refresh` for it to become
│ available. If you are using interpolation, please verify the interpolated value is not empty. You can
│ use the `terraform console` command to assist.
```

```shell
$ terraform apply   

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id                 = "8364ded2-5580-45c4-a394-edfa582e35a0"
      + cluster_name               = "enterprise-plan-cluster"
      + cluster_provider           = "aws"
      + connect_endpoint           = (known after apply)
      + database_name              = "test"
      + first_recoverability_point = (known after apply)
      + id                         = (known after apply)
      + image                      = "15-v0.3.0-public"
      + last_archived_wal_time     = (known after apply)
      + last_updated               = (known after apply)
      + pg_data_disk_size          = "10"
      + plan                       = "Enterprise"
      + region                     = "eu-west-1"
      + server_resource            = "aws-m7i-large-2c-8g"
      + status                     = (known after apply)
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
...[snip]...
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [2m0s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Creation complete after 2m9s [id=9986cfff-9758-4cbc-9433-084fe6e7936f]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

psql_endpoint_enterprise = "postgres://test_user:plvpx1YvXmBu@enterprise-plan-cluster-hp2goemtvtd5q0ew.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require"
```

### 连接到集群 {#connect-to-the-cluster}

```shell
$ psql "postgres://test_user:plvpx1YvXmBu@enterprise-plan-cluster-hp2goemtvtd5q0ew.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require"
psql (15.3, server 15.8 (Debian 15.8-1.pgdg120+1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

test=> \dx
                                                 List of installed extensions
  Name   | Version |   Schema   |                                         Description
---------+---------+------------+----------------------------------------------------------------------------------------------
 pgaudit | 1.7     | public     | provides auditing functionality
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 vectors | 0.3.0   | public     | vectors: Vector database plugin for Postgres, written in Rust, specifically designed for LLM
(3 rows)

test=> CREATE TABLE test (id integer PRIMARY KEY, embedding vector(3) NOT NULL);
CREATE TABLE
test=> INSERT INTO test SELECT i, ARRAY[random(), random(), random()]::real[] FROM generate_series(1, 100) i;
INSERT 0 100
test=> CREATE INDEX ON test USING vectors (embedding vector_l2_ops) WITH (options = "[indexing.hnsw]");
CREATE INDEX
test=> SELECT * FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402]' LIMIT 10;
 id |               embedding
----+---------------------------------------
 10 | [0.3603687, 0.2597973, 0.48529512]
 68 | [0.341106, 0.36290976, 0.4206507]
 46 | [0.29137495, 0.10839028, 0.2966823]
 56 | [0.5840259, 0.3336522, 0.33045283]
 54 | [0.2123173, 0.21955383, 0.2764878]
 97 | [0.37704793, 0.45084634, 0.3079026]
 64 | [0.33564404, 0.46575224, 0.33372045]
  8 | [0.5397384, 0.41881782, 0.26093292]
 66 | [0.42560518, 0.0136409905, 0.2709207]
 26 | [0.37973955, 0.24594037, 0.61934566]
(10 rows)
```

### 升级集群 {#upgrade-the-cluster}

目前，我们仅支持升级服务器资源规格、套餐类型和磁盘大小。升级操作存在一些限制：新服务器资源规格的 CPU 和内存必须大于或等于原有规格，新磁盘大小必须大于或等于原有大小，且套餐升级必须是从 `Starter` 升级到 `Enterprise`。

```diff
+ server_resource   = "aws-r7i-large-2c-16g"
- server_resource   = "aws-m7i-large-2c-8g"
+ pg_data_disk_size = "20"
- pg_data_disk_size = "10" 
```

```shell
$ terraform apply   
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Refreshing state... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b]

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  ~ update in-place

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be updated in-place
  ~ resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      ~ connect_endpoint           = "postgres://test_user:q7SdfHYVqkGB@enterprise-plan-cluster-tiqmlrllv36fmh4h.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require" -> (known after apply)
      ~ first_recoverability_point = "2024-09-20T03:53:04Z" -> (known after apply)
        id                         = "bbfb4ed2-b434-4e20-994f-6627e8f3785b"
      ~ last_archived_wal_time     = "2024-09-20T03:53:07Z" -> (known after apply)
      ~ last_updated               = "2024-09-20T03:52:38Z" -> (known after apply)
      ~ pg_data_disk_size          = "10" -> "20"
      ~ server_resource            = "aws-m7i-large-2c-8g" -> "aws-r7i-large-2c-16g"
      ~ status                     = "Ready" -> (known after apply)
        # (7 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.

Changes to Outputs:
  ~ psql_endpoint_enterprise = "postgres://test_user:q7SdfHYVqkGB@enterprise-plan-cluster-tiqmlrllv36fmh4h.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require" -> (known after apply)

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b, 10s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b, 20s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b, 30s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b, 40s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still modifying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b, 50s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Modifications complete after 53s [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b]

Apply complete! Resources: 0 added, 1 changed, 0 destroyed.

Outputs:

psql_endpoint_enterprise = "postgres://test_user:q7SdfHYVqkGB@enterprise-plan-cluster-tiqmlrllv36fmh4h.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require"
```

### 销毁集群 {#destroy-the-cluster}

```shell
$ terraform destroy
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Refreshing state... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b]

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  - destroy

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be destroyed
  - resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      - account_id                 = "8364ded2-5580-45c4-a394-edfa582e35a0" -> null
      - cluster_name               = "enterprise-plan-cluster" -> null
      - cluster_provider           = "aws" -> null
      - connect_endpoint           = "postgres://test_user:q7SdfHYVqkGB@enterprise-plan-cluster-tiqmlrllv36fmh4h.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require" -> null
      - database_name              = "test" -> null
      - first_recoverability_point = "2024-09-20T03:53:04Z" -> null
      - id                         = "bbfb4ed2-b434-4e20-994f-6627e8f3785b" -> null
      - image                      = "15-v0.3.0-public" -> null
      - last_archived_wal_time     = "2024-09-20T03:53:07Z" -> null
      - last_updated               = "2024-09-20T03:55:04Z" -> null
      - pg_data_disk_size          = "20" -> null
      - plan                       = "Enterprise" -> null
      - region                     = "eu-west-1" -> null
      - server_resource            = "aws-r7i-large-2c-16g" -> null
      - status                     = "Ready" -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  - psql_endpoint_enterprise = "postgres://test_user:q7SdfHYVqkGB@enterprise-plan-cluster-tiqmlrllv36fmh4h.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require" -> null

Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure, as shown above.
  There is no undo. Only 'yes' will be accepted to confirm.

  Enter a value: yes

pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Destroying... [id=bbfb4ed2-b434-4e20-994f-6627e8f3785b]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Destruction complete after 1s

Destroy complete! Resources: 1 destroyed.
```

## 5. 恢复 {#5-recovery}

在本节中，我们将演示如何从现有备份或按时间点恢复（PITR）来恢复您的 PostgreSQL 数据库。

### 从备份恢复 {#recovery-from-the-backup}

> [!WARNING]
> 您要恢复到的目标集群必须与备份具有相同的镜像（Image）、数据库名称（Database Name）和区域（Region）。


1. 从控制台获取备份 ID（Backup ID）
![](/cloud/images/get_backup_id.png)

2. 使用该备份 ID 创建新集群

```hcl
terraform {
  required_providers {
    pgvecto-rs-cloud = {
      source = "tensorchord/pgvecto-rs-cloud"
    }
  }
}

provider "pgvecto-rs-cloud" {
  api_key = "pgrs-57cc0d484e7e1d00444201ee846455b5"
  api_url = "https://cloud-dev.vectorchord.ai/api/v1"
}

resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
  account_id        = "8364ded2-5580-45c4-a394-edfa582e35a0"
  cluster_name      = "enterprise-plan-cluster"
  plan              = "Enterprise"
  image             = "15-v0.3.0-public"
  server_resource   = "aws-r7i-large-2c-16g"
  region            = "eu-west-1"
  cluster_provider  = "aws"
  database_name     = "test"
  pg_data_disk_size = "20"
  enable_restore    = "true"
  backup_id         = "4f53b451-8e19-443c-bcd7-43420d105696"
}

output "psql_endpoint_enterprise" {
  description = "Endpoint for the VectorChord Cloud Enterprise PostgreSQL database"
  value       = pgvecto-rs-cloud_cluster.enterprise_plan_cluster.connect_endpoint
}
```

```shell
$ terraform apply   

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id                 = "8364ded2-5580-45c4-a394-edfa582e35a0"
      + backup_id                  = "4f53b451-8e19-443c-bcd7-43420d105696"
      + cluster_name               = "enterprise-plan-cluster"
      + cluster_provider           = "aws"
      + connect_endpoint           = (known after apply)
      + database_name              = "test"
      + enable_restore             = true
      + first_recoverability_point = (known after apply)
      + id                         = (known after apply)
      + image                      = "15-v0.3.0-public"
      + last_archived_wal_time     = (known after apply)
      + last_updated               = (known after apply)
      + pg_data_disk_size          = "20"
      + plan                       = "Enterprise"
      + region                     = "us-east-1"
      + server_resource            = "aws-r7i-large-2c-16g"
      + status                     = (known after apply)
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
...[snip]...
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [2m10s elapsed]
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Creation complete after 2m19s [id=8ba9e5b4-f06c-4ef0-8e10-b6663237a532]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

psql_endpoint_enterprise = "postgres://test_user:j4Xu6TIstD1F@enterprise-plan-cluster-kxy2lovbc4crarmn.modelz.tech:5432/test?sslmode=require"
```

```shell
# 您可以检查表和索引
$ psql "postgres://test_user:j4Xu6TIstD1F@enterprise-plan-cluster-kxy2lovbc4crarmn.modelz.tech:5432/test?sslmode=require"
psql (15.3, server 15.8 (Debian 15.8-1.pgdg120+1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

test=> \dt
         List of relations
 Schema | Name | Type  |   Owner
--------+------+-------+-----------
 public | test | table | test_user
(1 row)

test=> SELECT * FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402]' LIMIT 10;
 id |              embedding
----+--------------------------------------
 34 | [0.4047166, 0.2152912, 0.30516902]
 56 | [0.39068437, 0.3153389, 0.40011033]
 42 | [0.43917453, 0.22915891, 0.44726416]
 45 | [0.47589824, 0.33998397, 0.39237767]
 43 | [0.46702152, 0.09506769, 0.4343289]
 95 | [0.4987348, 0.08346876, 0.28716254]
 60 | [0.5421089, 0.3585022, 0.25259662]
 80 | [0.61970145, 0.2186208, 0.36950335]
 53 | [0.3399207, 0.3417044, 0.55435336]
 54 | [0.3198571, 0.445044, 0.36041933]
(10 rows)
```

<a id="PITR"></a>
### PITR {#pitr}

> [!WARNING]
> 您要恢复到的目标集群必须与原集群具有相同的镜像（Image）和数据库名称（Database Name）。


1. 从控制台获取集群 ID（Cluster ID）
![](/cloud/images/get_cluster_id.png)

2. 使用该集群 ID 和目标时间创建新集群

```hcl
terraform {
  required_providers {
    pgvecto-rs-cloud = {
      source = "tensorchord/pgvecto-rs-cloud"
    }
  }
}

provider "pgvecto-rs-cloud" {
  api_key = "pgrs-57cc0d484e7e1d00444201ee846455b5"
  api_url = "https://cloud-dev.vectorchord.ai/api/v1"
}

resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
  account_id        = "8364ded2-5580-45c4-a394-edfa582e35a0"
  cluster_name      = "enterprise-plan-cluster"
  plan              = "Enterprise"
  image             = "15-v0.3.0-public"
  server_resource   = "aws-r7i-large-2c-16g"
  region            = "eu-west-1"
  cluster_provider  = "aws"
  database_name     = "test"
  pg_data_disk_size = "20"
  enable_restore    = "true"
  target_cluster_id = "43f17a52-0d07-43d5-91b6-9fbe4641578c"
  target_time       = "2024-09-20T12:00:00+08:00"
}

output "psql_endpoint_enterprise" {
  description = "Endpoint for the VectorChord Cloud Enterprise PostgreSQL database"
  value       = pgvecto-rs-cloud_cluster.enterprise_plan_cluster.connect_endpoint
}
```

```shell
$ terraform apply   

Terraform used the selected providers to generate the following execution plan. Resource actions are
indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # pgvecto-rs-cloud_cluster.enterprise_plan_cluster will be created
  + resource "pgvecto-rs-cloud_cluster" "enterprise_plan_cluster" {
      + account_id                 = "8364ded2-5580-45c4-a394-edfa582e35a0"
      + cluster_name               = "enterprise-plan-cluster"
      + cluster_provider           = "aws"
      + connect_endpoint           = (known after apply)
      + database_name              = "test"
      + enable_restore             = true
      + first_recoverability_point = (known after apply)
      + id                         = (known after apply)
      + image                      = "15-v0.3.0-public"
      + last_archived_wal_time     = (known after apply)
      + last_updated               = (known after apply)
      + pg_data_disk_size          = "20"
      + plan                       = "Enterprise"
      + region                     = "eu-west-1"
      + server_resource            = "aws-r7i-large-2c-16g"
      + status                     = (known after apply)
      + target_cluster_id          = "43f17a52-0d07-43d5-91b6-9fbe4641578c"
      + target_time                = "2024-09-20T12:00:00+08:00"
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
...[snip]...
pgvecto-rs-cloud_cluster.enterprise_plan_cluster: Still creating... [5m20s elapsed]

# 您可以检查表和索引
$ psql 'postgres://test_user:RKC4wr7MRcwm@enterprise-plan-cluster-4paxqvbzwxudmvja.eu-west-1-dev.aws.vectorchord.com:5432/test?sslmode=require'
psql (15.3, server 15.8 (Debian 15.8-1.pgdg120+1))
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, compression: off)
Type "help" for help.

test=> \dt
         List of relations
 Schema | Name | Type  |   Owner   
--------+------+-------+-----------
 public | test | table | test_user
(1 row)

test=> SELECT * FROM test ORDER BY embedding <-> '[0.40671515, 0.24202824, 0.37059402]' LIMIT 10;
 id |              embedding               
----+--------------------------------------
 34 | [0.4047166, 0.2152912, 0.30516902]
 56 | [0.39068437, 0.3153389, 0.40011033]
 42 | [0.43917453, 0.22915891, 0.44726416]
 45 | [0.47589824, 0.33998397, 0.39237767]
 43 | [0.46702152, 0.09506769, 0.4343289]
 95 | [0.4987348, 0.08346876, 0.28716254]
 60 | [0.5421089, 0.3585022, 0.25259662]
 80 | [0.61970145, 0.2186208, 0.36950335]
 53 | [0.3399207, 0.3417044, 0.55435336]
 54 | [0.3198571, 0.445044, 0.36041933]
(10 rows)
```
