---
title: "参考"
description: "vchord_bm25 的 SQL 对象、参数与索引选项、升级与迁移，以及基准测试。"
weight: 40
icon: fa-solid fa-book
no_list: true
---

每个运算符、函数、参数和索引选项都只在这几页定义一次，使用指南会链接到这里。迁移页还收录了版本历史。

{{< cards >}}
  {{< card link="/zh/docs/bm25/reference/sql/" title="SQL 参考" icon="fa-solid fa-code" >}}
`bm25query` 类型、`<&>` 运算符及其分数公式、`to_bm25query`、`bm25_maintain`，以及 `bm25` 访问方法。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/gucs/" title="参数与索引选项" icon="fa-solid fa-sliders" >}}
`bm25.*` 参数、索引存储选项，以及两者同时设置时以谁为准。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/migration/" title="升级与迁移" icon="fa-solid fa-right-left" >}}
版本历史、1.x 内的原地升级与降级，以及从 0.x `bm25vector` 接口迁移。
{{< /card >}}
  {{< card link="/zh/docs/bm25/reference/benchmarks/" title="基准测试" icon="fa-solid fa-chart-bar" >}}
已发布的吞吐量与相关性测试结果，以及对应的数据集、版本和出处。
{{< /card >}}
{{< /cards >}}
