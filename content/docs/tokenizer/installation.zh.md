---
title: "安装"
linkTitle: "安装"
description: "通过 Pigsty 软件包、GitHub 发布包或源码安装 pg_tokenizer，预加载并创建扩展，以及原地升级。"
weight: 20
upstream_link: "https://github.com/supervc-stack/pg_tokenizer.rs/blob/main/docs/01-installation.md"
icon: fa-solid fa-download
---

pg_tokenizer 1.3.0 支持 Linux `x86_64` 与 `aarch64` 上的 PostgreSQL 15–19，不依赖其他扩展。要做 BM25 排序，还需要安装 [vchord_bm25](/zh/docs/bm25/)。从下面选一种方式安装文件，之后都按同样的步骤[启用扩展](#enable)。

<a id="supported-versions"></a>

| 方式 | 适用场景 | 日文 IPADIC 词典 |
| --- | --- | --- |
| [Pigsty 软件包](#pigsty) | 运行 EL 8/9/10、Debian 12/13 或 Ubuntu 22.04/24.04。 | 不含，需要提供[外部词典](/zh/docs/tokenizer/models/#lindera) |
| [Debian 与 Ubuntu 软件包](#debian) | 运行 Ubuntu 24.04+ 或 Debian 13+，PostgreSQL 来自 PGDG。 | 内置 |
| [ZIP 压缩包](#zip) | 其他 glibc 2.39 及以上的 Linux。 | 内置 |
| [源码](#source) | 更旧或其他发行版，或者需要内置其他 Lindera 词典。 | 默认内置 |

## Pigsty 软件包 {#pigsty}

<a id="linux-packages-via-pig"></a>

[`pig`](https://pigsty.io/ext/e/pg_tokenizer) 会添加 PostgreSQL 与 Pigsty 软件源，并为它找到的 PostgreSQL 安装对应的包：

```bash
curl -fsSL https://repo.pigsty.io/pig | bash
pig repo add pgsql -u
pig ext add pg_tokenizer
pig ext add vchord_bm25    # 用于 BM25 排序
```

装了多个 PostgreSQL 大版本时，需要指定一个：`pig ext add pg_tokenizer -v 18`。全部软件包见 [PGEXT 目录](https://pgext.cloud/ext/pg_tokenizer)。

为了控制体积，这些包没有内置 Lindera 词典。除了日文和韩文切分，其他功能都能直接使用；要切分日文和韩文，需要让 Lindera 模型指向服务器上的词典目录，见[模型](/zh/docs/tokenizer/models/#lindera)。

## Debian 与 Ubuntu 软件包 {#debian}

<a id="from-debian-package-or-zip-archive"></a>

每个 [GitHub 发布版本](https://github.com/pgsty/pg_tokenizer/releases/tag/v1.3.0)都为每个 PostgreSQL 大版本和架构（`amd64`、`arm64`）提供一个 `.deb`。它们在 Ubuntu 24.04 上构建，要求 glibc 2.39 及以上，即 Ubuntu 24.04+ 或 Debian 13+。更旧的系统请用 Pigsty 软件包或从源码构建。

```bash
V=1.3.0; PG=18; ARCH=amd64
F=postgresql-${PG}-pg-tokenizer_${V}-1_${ARCH}.deb
wget https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/${F} \
     https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/SHA256SUMS
sha256sum --ignore-missing -c SHA256SUMS
sudo apt install ./${F}
```

> [!IMPORTANT]
> 发布包中的二进制可能要求较新的 PostgreSQL 小版本：对应大版本至少为 15.20、16.16、17.12 或 18.7。服务器版本更旧时动态库加载失败，只要它还在 `shared_preload_libraries` 里，PostgreSQL 就无法启动。`.deb` 把这个要求声明为软件包依赖；ZIP 包则写在 `pg_tokenizer.control` 的最后一行。请先升级服务器小版本，或者针对现有服务器从源码构建。

## ZIP 压缩包 {#zip}

同一个发布版本还为每个 PostgreSQL 大版本和架构（`x86_64`、`aarch64`）提供一个 `.zip`，glibc 要求相同。动态库、控制文件和 SQL 脚本都在同一个目录里：

```bash
V=1.3.0; PG=18; ARCH=x86_64
F=postgresql-${PG}-pg-tokenizer_${V}_${ARCH}-linux-gnu.zip
curl -fsSLO https://github.com/pgsty/pg_tokenizer/releases/download/v${V}/${F}
unzip ${F} -d pg_tokenizer
tail -n 1 pg_tokenizer/pg_tokenizer.control    # 最低 PostgreSQL 版本
sudo install -m 755 pg_tokenizer/pg_tokenizer.so "$(pg_config --pkglibdir)/"
sudo install -m 644 pg_tokenizer/pg_tokenizer--*.sql pg_tokenizer/pg_tokenizer.control \
     "$(pg_config --sharedir)/extension/"
```

请用 `install` 而不是 `cp`：`install` 是替换动态库文件而不是原地覆盖，正在运行的服务器在重启前会继续使用旧文件。

## 从源码构建 {#source}

<a id="from-source"></a>

需要 PostgreSQL 15–19 的开发文件（`pg_config`）、Rust 1.99.1 及以上、Python 3.11+、GNU Make，以及版本相互匹配的 Clang、libclang 和 LLVM 工具。

```bash
git clone --branch v1.3.0 --depth 1 https://github.com/pgsty/pg_tokenizer.git
cd pg_tokenizer
cargo install cargo-pgrx --version 0.20.0 --locked
PG_CONFIG=/path/to/pg_config make build
sudo make PG_CONFIG=/path/to/pg_config install
```

构建结果会内置日文 IPADIC 词典。要内置其他词典，在 `FEATURES` 中列出，例如 `make build FEATURES="lindera-ipadic lindera-ko-dic"`；可选项有 `lindera-ipadic`、`lindera-ipadic-neologd`、`lindera-unidic`、`lindera-ko-dic`（韩文）和 `lindera-cc-cedict`。如果装了多个 LLVM 版本，用 `CLANG_PATH` 和 `LIBCLANG_PATH` 指定其中一个；如果你的 Clang 会加载默认配置文件，设置 `CLANG_NO_DEFAULT_CONFIG=1`。

## 启用扩展 {#enable}

<a id="configuration"></a>

1. 把 `pg_tokenizer` 加入 `shared_preload_libraries`，保留列表里已有的库，然后重启 PostgreSQL。列表中的顺序无关紧要。跳过这一步，`CREATE EXTENSION` 会报 `pg_tokenizer must be loaded via shared_preload_libraries.`

   ```sql
   ALTER SYSTEM SET shared_preload_libraries = 'pg_tokenizer, vchord_bm25';
   ```

1. 在每个需要它的数据库中创建扩展：

   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_tokenizer;
   ```

   这会创建两个模式：`tokenizer_catalog` 存放函数和各类定义表，`tokenizer_data` 存放自定义模型的词表。

1. 可选：把 `tokenizer_catalog` 加入数据库的搜索路径，调用函数时就不必写模式前缀。本文档的示例都带前缀，两种情况下都能运行。

   ```sql
   ALTER DATABASE app SET search_path = "$user", public, tokenizer_catalog;
   ```

1. 检查版本：

   ```sql
   SELECT extversion FROM pg_extension WHERE extname = 'pg_tokenizer';
   ```
{.steps}

接下来可以跟着[快速上手](/zh/docs/tokenizer/overview/#quick-start)操作，或者挑一个[配方](/zh/docs/tokenizer/multilingual/)。

## 角色与权限 {#database-owner-permissions}

数据库属主不必是超级用户也能创建和删除定义：扩展已经为 `pg_database_owner` 角色授予了所需权限。其他角色需要单独授权：

- 角色要分析或分词文本（包括它的插入操作触发的触发器），需要能读取定义，否则调用会报 `permission denied for schema tokenizer_catalog`。

  ```sql
  GRANT USAGE ON SCHEMA tokenizer_catalog TO app;
  GRANT SELECT ON ALL TABLES IN SCHEMA tokenizer_catalog TO app;
  ```

- 角色要向挂了[自定义模型](/zh/docs/tokenizer/models/#custom)的表插入数据，还需要模式 `tokenizer_data` 的 `USAGE` 权限，以及该模型词表的 `SELECT` 和 `INSERT` 权限。
- 预加载列表作用于整个服务器，因此只有超级用户能用 `add_preload_model` 和 `remove_preload_model` 修改它，除非你对这两个函数 `GRANT EXECUTE`。
- 从服务器上的文件加载 Lindera 词典需要超级用户或 `pg_read_server_files` 成员身份，见[模型](/zh/docs/tokenizer/models/#lindera)。

## 升级 {#upgrading}

<a id="upgrade-120"></a><a id="upgrade-110"></a><a id="compatibility-100"></a>

从 1.2.0 升级：在主库和每个副本上安装新文件，在每个节点上重启 PostgreSQL，然后在主库的每个数据库中执行：

```sql
ALTER EXTENSION pg_tokenizer UPDATE;
```

定义、自定义词表及其 ID、表上的触发器都会保留，已存储的值无需重新计算。在执行这条更新之前，新动态库也能配合 1.2.0 的 SQL 定义正常工作。

`ALTER EXTENSION pg_tokenizer UPDATE` 会从任意更早的版本沿升级链一路升到最新。如果起点更早，途经的每个版本还要做以下操作：

| 起始版本 | 更新前后需要做的事 |
| --- | --- |
| 1.1.0 | 先把 PostgreSQL 14 集群升级到 15 或更高版本。如果有模型使用外部 Lindera 词典，要在每个节点上、PostgreSQL 停止期间，把它换成用 Lindera 7 构建的词典（format v3）。Lindera 7、一处正则表达式修复以及更新的 Unicode 表可能改变部分文本的切分结果：对比升级前后文档和查询的词元，对有差异的已存储值重新计算。 |
| 1.0.0 | 在 `READ COMMITTED` 隔离级别下执行更新：`BEGIN ISOLATION LEVEL READ COMMITTED; ALTER EXTENSION pg_tokenizer UPDATE; COMMIT;`。事先给在多个模式中重名的 `pg_dict` 词典名加上模式限定，并确认不存在无关的 `tokenizer_data` 模式；如果自定义模型分属多个角色，请以超级用户身份执行更新。词表从 `tokenizer_catalog` 迁到 `tokenizer_data`，直接读取词表的 SQL 需要相应修改。结巴的 `full` 与 `precise` 模式在此前版本中是互换的，用这两种模式生成的值要重新计算。 |
| 0.1.x | 先删除用到 `apply_text_analyzer` 的表达式索引、生成列、分区键和扩展统计信息，因为它已不再是 `IMMUTABLE`。重新计算已存储的 Lindera 词元 ID。`lucene_english`、`nltk_english` 和 `iso_english` 这几个名称保留给内置停用词表。 |
{.wide}

每个版本的全部变更见 [1.3.0](/zh/release/pg-tokenizer-1.3.0/)、[1.2.0](/zh/release/pg-tokenizer-1.2.0/)、[1.1.0](/zh/release/pg-tokenizer-1.1.0/) 和 [1.0.0](/zh/release/pg-tokenizer-1.0.0/) 的发布说明。仍在存储 vchord_bm25 0.x `bm25vector` 值的索引，需要按 [BM25 迁移](/zh/docs/bm25/reference/migration/)处理。

## 副本与备份 {#logical-backups}

定义和自定义词表都是普通的表：它们会复制到备库，`pg_dump` 也会导出它们。有两样东西在数据库之外，需要在每个节点上单独处理：

- 预加载列表，位于 `$PGDATA/pg_tokenizer/preload_models`。每个服务器启动时读取自己的那一份。备库沿用克隆时的副本，之后的改动要自己复制到每个节点，并单独备份这个目录。
- 外部 Lindera 词典目录。在每个节点的相同路径下安装同一份构建。

所有节点要安装相同版本的 pg_tokenizer，这样在备库上分析的查询才会与主库上写入的文档得到相同的词元。
