---
title: "驾驭 30 亿 PostgreSQL 向量：Earth Genome 的 Earth Index 与 VectorChord 携手守护地球"
linkTitle: "Earth Genome"
description: "Earth Genome 旗下的 Earth Index 平台如何利用 PostgreSQL、PostGIS 与 VectorChord 在 32 亿条卫星图像嵌入向量上实现低成本、高性能的全球环境监测。"
weight: 10
upstream_link: "https://github.com/tensorchord/pgvecto.rs-docs/blob/main/src/vectorchord/customer-stories/earthgenome.md"
aliases:
  - "/zh/docs/customer-stories/earthgenome/"
  - "/vectorchord/customer-stories/earthgenome/"
icon: fa-solid fa-earth-americas
---

监测地球健康状况是我们这个时代最关键的挑战之一。我们的星球正面临巨大的环境压力，而要理解这些变化，需要从不间断捕获的海量卫星数据（高达 PB 级的像素）中抽丝剥茧。无论是追踪亚马逊雨林的森林砍伐、识别偏远地区的非法采矿作业，还是监测农业活动对脆弱生态系统的影响，将这些原始数据转化为可付诸行动的情报都至关重要。

Earth Genome 旗下的 [**Earth Index**](https://www.earthgenome.org/earth-index) 平台正在正面攻克这一难题。如今，该平台已实现全球覆盖，利用 AI 的力量让地球上的每一寸陆地表面都变得可搜索。这不仅是一项技术壮举，更是一款旨在通过从卫星数据中提取人人可用、可操作的情报，从而赋能全球环境治理的全新工具。

在 [VectorChord](https://github.com/pgsty/vchord) 团队，我们无比自豪地看到我们的 PostgreSQL 向量检索扩展在驱动这一宏伟且至关重要的使命中发挥着核心作用。

## Earth Index 在做什么？将像素转化为地球洞察 {#what-is-earth-index-doing-turning-pixels-into-planetary-insights}

想象一下，要在覆盖数百万平方公里的卫星影像中，找出某种特定类型的小规模环境破坏（例如未申报的采石场或新出现的森林砍伐斑块）。传统上，分析这类数据需要深厚的专业知识与高昂的资源投入，这使得环保组织、调查记者以及预算有限的监管机构很难在广袤偏远的地区追踪特定威胁。下方的动画展示了 Earth Index 是如何精准定位亚马逊雨林中的非法贩毒简易跑道的——这无异于在足球场上寻找一根牙签。

<img src="https://miro.medium.com/v2/resize:fit:1280/0*P1cvHPCMB_I_9DEn" alt="Earth Index Animation" align="center" />

那么，Earth Index 是如何让全球范围内的环境特征搜索成为可能的呢？其奥秘在于一套前沿的技术方案：利用通过对比学习（Contrastive Learning）训练的 AI 基础模型及其生成的向量嵌入（Vector Embeddings）。

下面让我们一窥其创新流程：

1. **全球网格切片（Tiling the Globe）：** Earth Index 将地球的全部陆地表面划分为超过 **32 亿个**相互重叠的网格切片（Tile），每个切片面积约为 10 公顷。

2. **通过对比自监督学习提取“地球 DNA”：** Earth Index 利用了 AI 领域的突破性进展，特别是采用自监督对比学习方法（如 DINO 目标函数）专为地球观测（EO）训练的基础模型。该基础模型（例如 SSL4EO Vision Transformer）通过区分来自*同一*地理位置的图像对（正样本对）和来自*不同*地理位置的图像对（负样本对），学习卫星影像的底层视觉语言。这一过程在多样化的全球遥感数据（如 Harmonized Landsat Sentinel-2 光学影像、Sentinel-1 雷达影像）上进行，完全无需人工显式标注“森林”或“城市”等标签。

3. **生成向量嵌入：** 完成预训练后，该模型即作为编码器使用。将每个网格切片的影像输入模型，即可生成一个**向量嵌入**——这是一种以高度压缩格式（压缩比超过 10,000 倍）捕捉该切片核心视觉与结构特征的丰富数值表示（或称“数字指纹”）。这个高维向量就像是那片土地独一无二的“地球 DNA”。

4. **打造可搜索的地球：** 这 32 亿条向量嵌入构成了 Earth Index 的核心。它们需要被存储在一个专门针对快速查找数值相似向量而优化的系统中。用户只需提供一个他们想要寻找的目标示例（例如在地图上点击一个已知的非法矿点或某种特定的农业基础设施），Earth Index 就能在这个庞大的数据集中搜索，找出全球范围内（或特定区域内）具有相似向量指纹的其他地点。


## 现实影响力：Earth Index 环保实战 {#real-world-impact-earth-index-in-action-for-environmental-protection}

这一技术底座直接转化为了理解与保护自然环境的强大工具。它赋能调查记者（如 Mongabay 和自由欧洲电台的记者）、原住民社区、环保及国际组织（如世界银行）以及科研人员，使他们能够以前所未有的便捷性与速度揭露隐蔽的环境变化、监测工业足迹并为生态保护行动收集证据。下图展示了丰塞卡湾（Gulf of Fonseca）的养虾场分布。

<img src="https://miro.medium.com/v2/resize:fit:1400/1*ChyVYAx3EIS_b27QmLS5iQ.png" alt="Shrimp farms in the Gulf of Fonseca" align="center" />

以下是 Earth Index 在实际应用中的几个典型案例：

* **打击森林砍伐与非法活动：** 在与环境新闻机构 **Mongabay** 的合作中，Earth Index 穿透茂密的雨林冠层，成功识别出亚马逊地区隐蔽的非法贩毒简易机场。同样地，该平台还能快速定位非法采金留下的地表伤痕（例如在亚诺马米原住民领地造成严重破坏的矿坑），帮助量化问题规模并为执法行动提供指引。

* **监测资源开采：** **自由欧洲电台（Radio Free Europe）** 利用 Earth Index 在巴尔干半岛识别出了 1,300 多个采石场，揭露出其中约有一半缺乏合法许可证，凸显了潜在的环境破坏与违规开采问题。这一方法同样可用于监测水力压裂井场、橡胶加工厂或其他工业设施。

* **保护水质与生态系统：** Earth Index 可以定位敏感水道附近的集约化畜禽养殖场以评估径流污染风险，或识别向重要红树林生态系统扩张的养虾场。

* **追踪农业扩张：** 通过搜索与新开辟林地或特定作物类型相关的视觉模式，该工具能够帮助监测自然栖息地向农业用地的转化过程。


## 基础设施挑战：以可承受的成本检索数十亿向量 {#the-infrastructure-challenge-searching-billions-of-vectors-affordably}

生成 32 亿条高维向量只是挑战之一；如何高效地托管并检索这些向量则是另一道巨大的门槛。Earth Index 需要一套能够满足以下要求的解决方案：

* **应对海量规模：** 检索数十亿条向量需要专门的索引与查询加速能力。

* **与地理空间数据无缝集成：** Earth Index 高度依赖地理空间运算（例如在特定行政边界内过滤结果，或按与河流的距离进行筛选）。这使得带有 PostGIS 扩展的 PostgreSQL 成为其核心数据库自然且不可或缺的选择。而独立的专用向量数据库往往缺乏所需的丰富地理空间特性。

* **保障查询性能：** 平台需要足够快地返回结果，才能有效支撑交互式调查与监测工作。

* **严控成本：** 存储和检索数十亿条向量（尤其是当纯内存索引需要消耗海量 RAM 时）对于许多组织——特别是非营利机构——而言，成本往往高得令人望而却步。


因此，Earth Index 需要一种原生运行于其选定的 PostgreSQL 环境中、具备超大规模扩展能力、性能优异且硬件成本不会超支的向量检索解决方案。

## 为什么 PostgreSQL 是行星级向量检索的绝佳选择 {#why-postgresql-rocks-for-planetary-scale-vectors}

尽管市面上存在各种专用向量数据库，但 Earth Index 面临着一个核心诉求：将向量相似性检索与丰富的地理空间数据及操作无缝结合。这正是 PostgreSQL 及其扩展生态真正大放异彩的地方：

* **统一的数据平台：** PostgreSQL（尤其是配合强大的 PostGIS 扩展）使 Earth Index 能够将向量嵌入与其关键的地理空间元数据（切片位置、行政边界、与河流等地物的空间邻近关系）保存在一起。这避免了分别维护独立的向量数据库与关系型/空间数据库所带来的架构复杂性及潜在的数据同步难题。

* **释放 SQL 与 PostGIS 的强大威力：** Earth Index 可以在单一查询接口中，将向量相似性检索与标准 SQL 过滤条件及复杂的 PostGIS 空间查询结合起来（例如，“*在*该特定国家公园边界内，或者*在*该水系附近，查找与该示例相似的向量”）。独立的向量数据库通常缺乏如此成熟的地理空间联合查询能力。

* **成熟度与生态系统：** 基于 PostgreSQL 构建意味着继承其数十年的研发积淀、享誉业界的稳定性、完善的工具链以及广泛的社区支持——这对于像 Earth Index 这样的关键任务平台而言至关重要。


然而，要高效地检索 32 亿条向量，仅靠标准的 PostgreSQL 能力是远远不够的。

## 为什么 Earth Index 选择 VectorChord 以兼顾性能与性价比 {#why-earth-index-chose-vectorchord-for-performance-and-affordability}

虽然 PostgreSQL 生态系统提供了理想的底座，但在 32 亿条向量的规模下同时实现所需的性能与可承受的成本，依然是一项严峻的挑战。Earth Index 需要一种既能提供极速查询、又不会掏空预算的解决方案。

在性能、成本与集成度之间寻找最佳平衡点并非易事。Earth Genome 首席技术官 [Hutch Ingold](https://www.linkedin.com/in/tom-ingold/) 解释了他们的选型考量：

> 当我们为 32 亿条向量评估技术方案时——尽管技术演进日新月异——标准的 pgvector 在如此庞大的规模下无法满足我们的性能要求。而像 Qdrant 这样的专用向量数据库也面临困难：其全托管云服务过于昂贵，而当时在我们自己的 Kubernetes 基础设施上自建集群部署又显得不够成熟。我们还考察了各大云厂商的服务（例如 Google 的 Vertex AI Vector Search），但针对我们的数据集，其高达每月 237,000 美元的目录报价实在令人望而却步。

正是在这一背景下，[VectorChord](https://github.com/pgsty/vchord) 成为了破局的关键技术：

* **超越原生 pgvector 的卓越性能：** VectorChord 提供了不可或缺的速度提升——**查询速度最高提升 5 倍，写入吞吐量提升 16 倍，索引构建速度加快 16 倍**——有效攻克了标准 pgvector 在超大规模下的性能瓶颈。

* **基于磁盘索引的高性价比扩展：** 尤为关键的是，VectorChord 经过深度优化的**磁盘索引（Disk-Based Indexing）**技术（充分利用高性价比的 SSD）直接化解了 CTO 所提到的高昂成本难题。它既避免了纯内存方案对海量 RAM 的苛刻需求，又省去了托管云向量服务高昂的月度费用，使构建 32 亿规模的向量索引在财务上切实可行。

* **原生集成与卓越扩展性：** 作为一款 PostgreSQL 扩展，VectorChord 直接在他们已选定的数据库*内部*提供了上述所有优势，无需对现有基础设施进行改造。它专为高效**扩展**而构建，在轻松驾驭 Earth Index 全球监测平台所需的数十亿级向量的同时，依然保持了流畅的交互式查询性能。


VectorChord 在 Earth Index 所熟悉的强大 PostgreSQL 环境中，完美集齐了高性能、超大规模扩展能力与极佳的成本效益。

## Earth Index：技术架构与部署配置 {#earth-index-technical-architecture-and-setup}

为了高效且经济地管理其行星级数据集，Earth Index 在由三台强大的 AWS EC2 **i8g.16xlarge** 实例组成的集群上构建了后端系统，这些实例搭载了最新的 Graviton4 ARM 处理器与 Nitro SSD。每台实例配备 **512 GB 内存、64 个 vCPU 以及 15 TB 的 NVMe 存储**，为密集计算与高速磁盘 I/O 奠定了坚实基础。整套环境的月度成本约为 12,000 美元，与同类托管云向量服务预估高达 237,000 美元的月费相比，节省了巨额开支，从而让该项目在经济上得以持续运转。这些实例运行着由 VectorChord 和 PostGIS 增强的 PostgreSQL，高效地同时承载了向量数据与其他应用组件。

<img src="/docs/images/vector-search-with-geo.png" alt="Earth Index Architecture" align="center" />

核心数据存储在跨三个节点的分区表结构中。主表 `globe24` 存储了**每个切片的唯一 ID**、**地理空间点几何信息**（`geometry(Point, 4326)`）、**分区键**（`partkey`），以及至关重要的、以 `halfvec(384)` 格式高效存储的 **384 维 AI 生成嵌入向量**。这种分片策略将 32 亿行数据均匀分布在集群中，从而支持高效的并行处理。

该架构的一大核心优势在于能够执行复杂的联合查询。Earth Index 经常执行的 SQL 语句会将 VectorChord 的快速向量检索（`embedding <=> '{vector}'::vector`）与 PostGIS 地理空间过滤（`st_within(geom, '{geom}')`）以及分区裁剪（`partkey IN (...)`）无缝结合。这使得用户能够在指定的地理边界内高效地查找视觉特征相似的地点。即便面对数十亿条向量，这种一体化方案依然能提供极为实用的性能表现：对于返回前 500 条结果的典型搜索，其查询延迟中位数（P50）仅约为 **761 ms**。

## 大规模赋能环保行动 {#enabling-environmental-action-at-scale}

通过在 PostgreSQL 内部提供高性价比、可扩展且紧密集成的向量检索解决方案，VectorChord 助力 Earth Index 实现了这项开创性的工作。它使团队能够以可承受的成本管理庞大的“地球 DNA”数据库，确保这一强大的环境监测工具能够真正惠及最需要它的组织与社区。

立即[**加入 Earth Index 候补名单**](https://app.earthindex.ai/waitlist/)，探索您身边的环境变化、了解您的生态足迹，并成为守护地球全球行动的一份子。

我们非常欣喜地看到 Earth Index 利用 [VectorChord](https://github.com/pgsty/vchord) 将海量卫星数据转化为可付诸行动的环境情报。他们的成功充分证明了将前沿 AI、稳健的数据库技术与高效的向量检索相结合，在应对全球重大挑战时所迸发出的巨大能量。

希望将大规模向量检索引入您的 PostgreSQL 数据库？立即深入了解 [VectorChord](https://github.com/pgsty/vchord) 并开始体验吧！
