---
title: "Introducing Terraform Support for PGVecto.rs Cloud"
date: 2024-07-24
description: "Use Terraform to manage PGVecto.rs Cloud like your other infrastructure components"
author: "[xieydd](https://github.com/xieydd) · [TensorChord](https://github.com/tensorchord)"
tags:
  - "postgresql"
upstream_link: "https://blog.vectorchord.ai/introducing-terraform-support-for-pgvectors-cloud"
upstream_copyright: "© 2024 xieydd (TensorChord Inc.)"
aliases:
  - "/blog/introducing-terraform-support-for-pgvectors-cloud/"
  - "/introducing-terraform-support-for-pgvectors-cloud/"
---

We are thrilled to announce the release of our [Terraform provider for PGVecto.rs Cloud](https://registry.terraform.io/providers/tensorchord/pgvecto-rs-cloud/latest). This new provider is designed to simplify the process of managing resources on our [cloud service](/cloud/), providing users with an intuitive and streamlined experience for managing their Postgres cluster setup and operation through infrastructure as a code tool — **Terraform**. For those unfamiliar with [Terraform](https://www.terraform.io/), it is an open-source tool for building, changing, and versioning infrastructure safely and efficiently. It enables users to define their infrastructure as code, allowing them to provision and manage resources programmatically.

# A word about PGVecto.rs: Scalable Vector Search in Postgres

[PGVecto.rs](https://github.com/tensorchord/pgvecto.rs) is a Postgres extension that enables scalable vector search, allowing you to build powerful similarity-based applications on top of your Postgres database.

PGVecto.rs distinguishes itself with several robust features:

* **Better Filtering**: Apply any filter conditions and join with other tables, achieving high recall and low latency, a distinctive edge over other vector databases.
    
* **Hybrid Search**: Leverage the full-text search functionality in PostgreSQL with pgvecto.rs to search text and vector data within a single query.
    
* **Extended Vector Length**: PGVecto.rs supports vector lengths up to 65535, suitable for the latest models.
    
* **Faster, and Faster**: 4x faster than other postgres-based solutions.
    
* **Binary Vector Search**: By utilizing adaptive retrieval techniques, binary vectors can maintain a high level of accuracy while significantly reducing memory usage by 30 times.
    
* **Complete SQL Support**: Full SQL support, enabling joins and filters without limitations or extra configuration.
    

# **How to get started with Terraform and PGVecto.rs Cloud**

This guide walks you through the process of installing and configuring the PGVetco.rs Cloud provider.

## **Prerequisites**

Before you begin, ensure you have the following:

1. Terraform Installed: Download and install Terraform from [**here**](https://www.terraform.io/downloads.html) by following the provided instructions.
    
2. PGVecto.rs Cloud Account: Access to PGVecto.rs Cloud and your API Key are essential. Go to the [**PGVecto.rs Cloud Console**](/cloud/manage/apikey/) and create an API key. The API key must have the `ProjectOwner` permissions.
    

![](https://cdn.hashnode.com/res/hashnode/image/upload/v1721659329747/ec3dba71-1794-4ad7-8d27-60b8af568d0f.png)

<a id="download-pgvecto-rs-cloud-terraform-provider"></a>
## **Download PGVecto.rs Cloud Terraform Provider**

Start by configuring the PGVecto.rs Cloud provider within your Terraform configuration file ([`main.tf`](http://main.tf)). Follow these steps:

```ini
terraform {
  required_providers {
    pgvecto-rs-cloud = {
      source = "tensorchord/pgvecto-rs-cloud"
    }
  }
}
```

## **Initialize Terraform Configuration**

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

Terraform will download the `pgvecto-rs-cloud` provider and install it in a hidden subdirectory of your current working directory, named `.terraform`.

<a id="authenticate-pgvecto-rs-cloud-terraform-provider"></a>
## **Authenticate PGVecto.rs Cloud Terraform Provider**

Your PGVecto.rs Cloud API Key is required to use the Terraform Provider. There are two ways to configure this.

### **Option 1: Specify API Key in Provider Block**

Append the following code to your `main.tf` file:

```ini
provider "pgvecto-rs-cloud" {
  api_key = "<your-api-key>"
}
```

### **Option 2: Use Environment Variable**

Set the API key as an environment variable:

```bash
export PGVECTORS_CLOUD_API_KEY="<your-api-key>"
```

Then the provider declaration is in your [`main.tf`](http://main.tf) file is simply:

```ini
provider "pgvecto-rs-cloud" {
}
```

By following these steps, you should have the PGVecto.rs Cloud Terraform provider configured and ready to move on to the next steps.

<a id="manage-pgvecto-rs-cloud-cluster"></a>
## **Manage PGVecto.rs Cloud Cluster**

### **Create an Enterprise Plan**

The following example demonstrates how to create a PostgreSQL cluster with the Enterprise plan. For more information about the options, refer to the [**Resource Schema**](https://registry.terraform.io/providers/tensorchord/pgvecto-rs-cloud/latest/docs/resources/cluster).

You can get `account_id` from the cloud console, click the avatar in the upper right, and then click Profile.

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

You can validate the terraform code using the following steps:

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

Then run the following command to create an execution plan, if you are happy with the plan, you can apply it. After applying the plan, the Postgres cluster will be created in your PGVecto.rs cloud account.

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

You can use [psql](https://www.postgresql.org/docs/current/app-psql.html) to connect to the database via the outputted connection string. Then you can execute `\dx` to see the installed extensions and create a `hnsw` index to validate that the extension `vectors` is installed successfully.

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

### **Upgrade the cluster**

Up to now, we only support upgrading the server resource, plan, and disk size. There are some restrictions on the upgrade operation:

* The plan upgrade must be from the `Starter` to `Enterprise`.
    
* The disk size must be greater or equal to the original one.
    
* If you want to upgrade the server resource in `Enterprise` plan, the CPU and memory of the server resource must be greater or equal to the original one.
    

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

### **Destroy the cluster**

> Notice: If you delete the cluster, you can't recover it. So, please be careful.

If you want to delete the Postgres Cluster, you can use the following command:

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

# **Conclusion**

The integration of Terraform into the PGVecto.rs cloud represents a powerful solution for businesses and developers looking to leverage advanced vector search capabilities on Postgres. The automated, infrastructure-as-code approach not only simplifies the deployment process but also enhances the robustness and scalability of your applications. If you have any questions or find a security issue in the Terraform Provider, [please contact us](https://discord.gg/KqswhpVgdU), we will be happy to help you.
