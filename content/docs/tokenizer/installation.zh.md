---
title: "安装指南"
description: "通过 Pigsty 原生 Linux 软件包、Docker 镜像、Debian/ZIP 归档包或 cargo-pgrx 源码安装 pg_tokenizer。"
weight: 5
icon: fa-solid fa-download
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
---

## 通过 `pig` 安装原生 Linux 软件包（推荐） {#linux-packages-via-pig}

1.1.0 的发布验收范围是 PostgreSQL 14–18 上的全新安装。升级兼容、默认权限迁移与跨升级旧快照不在本轮验收范围内，详见[发布说明](/zh/blog/release/pg-tokenizer-1.1.0/)。

在 EL 8/9/10、Debian 12/13 与 Ubuntu 22.04/24.04/26.04（支持 PostgreSQL 14–18）上，可以从 [Pigsty 软件仓库](https://pigsty.cc/ext/e/pg_tokenizer)安装与目标发行版、CPU 架构匹配的原生软件包（完整包可用性矩阵见 [pgext.cloud](https://pgext.cloud/ext/pg_tokenizer)）：

```bash
curl -fsSL https://repo.pigsty.cc/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
```

原生 RPM/DEB 不内嵌 Lindera 词典，需提供用 Lindera 6 编译的外部词典。GitHub `.deb`/ZIP 包启用 `lindera-ipadic` 并内嵌 IPADIC；其他词典仍是可选编译特性。

## 使用 Docker（`vchord-suite`） {#docker}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 维护版本的 Docker 和 Kubernetes 镜像尚未发布。以下上游说明仅供参考，后续更新。

[`tensorchord/vchord-suite`](/zh/docs/vchord/getting-started/vectorchord-suite/) Docker 镜像已预装完整的 Vchord 检索扩展套件：
- [`pg_tokenizer`](https://github.com/pgsty/pg_tokenizer) —— 独立多语言分词器（`pgsty/pg_tokenizer`）
- [`vchord_bm25`](https://github.com/pgsty/vchord_bm25) —— 原生 BM25 排序索引（`pgsty/vchord_bm25`）
- [`vchord`](https://github.com/pgsty/vchord) —— 可扩展、磁盘友好的向量相似性检索（`pgsty/vchord`）
- [`pgvector`](/zh/docs/vector/) —— 标准 PostgreSQL 向量数据类型

```bash
docker run \
  --name vchord-suite \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d tensorchord/vchord-suite:pg18-latest
```

使用 `psql` 连接数据库并启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## 参数配置（`shared_preload_libraries` 与 `search_path`） {#configuration}

`pg_tokenizer` 没有必需的 PostgreSQL 扩展依赖。`vchord_bm25` 是可选组件：其 0.3.x 接口通过 `bm25vector` 消费 `INT[]`，1.0.0 接口可以直接消费原生 `tsvector`。`pg_tokenizer` 动态库必须在 PostgreSQL 启动前通过 `shared_preload_libraries` 预加载；如果希望省略模式限定调用函数，再将 `tokenizer_catalog` 加入 `search_path`：

```bash
psql -U postgres -c "ALTER SYSTEM SET shared_preload_libraries = 'pg_tokenizer.so';"
psql -U postgres -c "ALTER SYSTEM SET search_path TO \"\$user\", public, tokenizer_catalog;"
sudo systemctl restart postgresql.service
```

随后在目标数据库中创建扩展：

```sql
CREATE EXTENSION IF NOT EXISTS pg_tokenizer CASCADE;
```

## 从 Debian 软件包或 ZIP 归档包安装 {#from-debian-package-or-zip-archive}

[pg_tokenizer 1.1.0 GitHub Release](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.1.0) 提供在 Ubuntu 24.04 上构建、覆盖 PostgreSQL 14–18 及 `x86_64`/`aarch64` 的 `.deb` 与 `.zip` 归档。草稿正式发布后，附件才会向公众开放。软件包必须匹配目标发行版、PostgreSQL 主版本和架构；其他发行版的原生包请使用 Pigsty 软件仓库。ZIP 不包含软件包管理器依赖元数据，安装前必须自行验证共享库与目标系统 libc 的兼容性。

```bash
# Ubuntu 24.04、PostgreSQL 17、amd64
sudo apt install ./postgresql-17-pg-tokenizer_1.1.0-1_amd64.deb
```

将匹配的 ZIP 归档下载为 `pg_tokenizer.zip` 后执行：

```bash
unzip pg_tokenizer.zip -d pg_tokenizer
sudo install -m 755 pg_tokenizer/pg_tokenizer.so "$(pg_config --pkglibdir)/"
sudo install -m 644 pg_tokenizer/pg_tokenizer--*.sql pg_tokenizer/pg_tokenizer.control "$(pg_config --sharedir)/extension/"
```

使用 `install` 替换共享库，避免就地截断 PostgreSQL 可能已经加载的文件。安装后按上面的配置步骤重启 PostgreSQL，以加载安装的共享库。

## 从源码编译安装（`cargo-pgrx`） {#from-source}

```bash
git clone https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
git checkout v1.1.0
cargo pgrx install --sudo --release --pg-config "$(command -v pg_config)" --features lindera-ipadic
```

## 升级到 1.1.0 {#upgrade-110}

以下内容保留作为参考，不代表本轮已经完成升级验收。默认权限迁移及持有跨升级快照的事务需要单独验证。

在主库和备库安装匹配的 1.1.0 共享库与 SQL 文件，分别重启以重新加载预加载库，然后由扩展拥有者或管理员在每个主库数据库执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE TO '1.1.0';
```

1.0.0 直接升级到 1.1.0；更早的 0.1.0 和 0.1.1 通过原有路径先经过 1.0.0。未发布的 1.0.1 候选不作为升级步骤。迁移会保留目录数据、已有自定义词表 ID，以及原六参便捷函数的依赖关系（包括其函数 OID）。标准 `cargo pgrx install/package` 与 `tools/package.sh` 均会包含升级脚本；备库缓存失效信号在本次 SQL 升级提交并回放后生效。Lindera 词典版本变化引起的 ID 迁移须按照[模型说明](/zh/docs/tokenizer/models/#4-lindera-morphological-models-create_lindera_model)重新分词。

升级前应明确限定缺失或有歧义的旧 `pg_dict` 名称，也应限定刻意覆盖内置词典的自定义词典。批量导入前检查[新增资源预算](/zh/docs/tokenizer/reference/#analysis-budgets)。已登记的词表及其索引、身份序列从 `tokenizer_catalog` 移至 `tokenizer_data`，保留 OID、所有者、表与序列 ACL、词元 ID 和依赖关系。直接引用旧词表名的 SQL 需要修改。原有非 schema owner 的模式权限及授权选项复制到数据模式，目录模式的 CREATE 授权撤销。若存在无关的 `tokenizer_data` 模式，或已登记词表缺失、对象名冲突，整个升级回滚。升级者需要每张词表的所有者权限；若模型分属不同角色，应由超级用户升级。迁移前应结束耗时的模型管理事务；持有升级前快照的语句可能返回 SQLSTATE `40001`，此时重试整个事务。新版本表只向 PUBLIC 开放 SELECT，内部触发器以 SECURITY DEFINER 和固定 search_path 运行，不向 PUBLIC 开放 EXECUTE。

PGXN 源码包要求与发布步骤见[发布指南](https://github.com/pgsty/pg_tokenizer/blob/main/docs/08-release.md)。项目已准备源码 ZIP 和供 PGXN 使用的 Makefile，上传发布仍是单独步骤。

### 数据库拥有者权限 {#database-owner-permissions}

安装与升级向 `pg_database_owner` 授予 `tokenizer_catalog` 的 USAGE、`tokenizer_data` 的 USAGE/CREATE、数据库内管理函数的 EXECUTE，目录表与词表的 SELECT/INSERT/UPDATE/DELETE，以及序列的 USAGE/SELECT。新建自定义模型会显式授权，授权随数据库拥有者变更而生效。模式所有者及拥有其权限的角色仍保留 PostgreSQL 固有的所有者权限。API 函数仍在 `tokenizer_catalog` 中，无需把数据模式加入 search_path。

管理员安装扩展后，非超级用户的数据库拥有者可以创建、删除自己创建的模型、分析器、分词器、停用词及同义词。授权不转移对象所有权：删除其他角色创建的模型仍需原对象拥有者或管理员。其他应用角色需要显式授权；扩展不会向 PUBLIC 开放模式访问或目录写权限，函数继续以调用者权限执行。

数据库服务器上的 Lindera 词典和用户词典路径只有超级用户或拥有 `pg_read_server_files` 权限的角色可以加载；其他角色可以使用 `embedded://` 词典。检查发生在创建模型以及后端首次从目录加载模型时。已经加载或由 postmaster 预加载、且目录配置匹配的模型可以继续被复用。

`add_preload_model` 与 `remove_preload_model` 管理整个集群的数据目录文件，仅扩展拥有者及获得显式授权的管理员可执行；PUBLIC 和 `pg_database_owner` 没有执行权限。文件修改不随 SQL 事务回滚，重启后生效。无效预加载条目会记录 WARNING 并跳过，不会阻止 PostgreSQL 启动。

### 1.0.0 兼容性变化 {#compatibility-100}

- `apply_text_analyzer` 改为 `STABLE`，与 `tokenize` 一致：分析器定义属于目录数据，标记为 `IMMUTABLE` 并不正确，还会让缓存计划绕过失效。只要有索引、存储生成列、分区键或扩展统计对象依赖它，升级就会拒绝执行。请先把这些表达式改为由应用或触发器维护的普通列，并为列建立索引，再执行升级。
- Lindera 从 0.42 升级到 6.2。内嵌 IPADIC 由 2007-08-01 版更新为 2025-09-20 版，词元 ID 随之变化；外部编译词典须用 Lindera 6 重新构建。用户词典 ID 改为 `1073741824 + 词典内编号`，不再与系统词典 ID 重叠。需重新生成已存储的 Lindera 词元数组并重建相关索引。
- 自定义模型中，匹配行的源列为 NULL 时，embedding 现在设为 NULL，包括 INSERT 显式提供的值；0.1.x 会保留目标列原值。不匹配过滤条件的行保留原有 embedding。
- 向自定义模型新增词元的写入事务按模型取 advisory lock，持有至提交；所含词元均已存在的写入不等待。`REPEATABLE READ` 与 `SERIALIZABLE` 写入可能返回 SQLSTATE `40001`，需重试整个事务。
- 调用过定义变更接口的事务不支持 `PREPARE TRANSACTION`；只读事务仍可 prepare。
- `add_preload_model` 与 `remove_preload_model` 仅限管理员；无效预加载条目会记录 WARNING 并跳过。升级前，请移除仍使用未经 Lindera 6 重建的外部词典的 Lindera 模型预加载条目。
- 内置停用词表 `lucene_english`、`nltk_english` 与 `iso_english` 为保留名：`drop_stopwords` 与 `create_stopwords` 拒绝这些名称。若旧版本替换过其中之一，升级会给出 WARNING；请把该词表复制为新名称，并改为引用新名称。
- `pg_dump` 现在包含定义表，见[逻辑备份](#logical-backups)。

### 逻辑备份 {#logical-backups}

五张定义表（`text_analyzer`、`tokenizer`、`model`、`stopwords`、`synonym`）已通过 `pg_extension_config_dump` 登记，普通 `pg_dump` 会导出其中的行，以及自定义词表、对应的标识列序列和源表触发器。`CREATE EXTENSION` 会重新创建内置的 `lucene_english`、`nltk_english` 与 `iso_english` 停用词表，因此这三个名称不会被导出。它们是保留名，不能删除或替换，因此恢复后得到的词表与原来相同。

外部 Lindera 词典和集群的 `pg_tokenizer/preload_models` 目录不在数据库内，需要单独备份。物理备份包含目录表数据和预加载目录，但不包含外部词典路径。
