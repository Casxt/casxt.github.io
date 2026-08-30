# 通用_铀业公司投资价值调研_Agent分步执行手册 V1.1（综合修复版）

> 适用对象：中国铀业、中广核矿业、中核国际，以及其他以天然铀矿山、铀资源权益、天然铀采购/贸易、核燃料供应链为核心业务的上市公司。
>
> 目标：形成一套**可重复执行、可审计、可跨公司横向合并、可季度/半年回归**的研究流程。最终输出既要能让只有基础金融知识的读者理解公司的业务本质，也要能让第三方 Agent 从原始数据一路复核到 2025–2035 经营预测、估值和潜在投资收益。
>
> 默认资金成本/要求回报率：**11%**。除特别说明外，所有未来价值折现、投资收益判断与“当前是否低估”的结论都必须以 11% 为基准。

## V1.1 相对 V1.0 的结构性修复

本版本针对可执行性审计中的高优先级问题做了以下修复，后续 Agent 必须按新规则执行：

1. **统一宏观输入**：所有公司必须读取同一份冻结的 `common_input_snapshot`；不同公司不得自行生成不同的 Bear/Base/Bull 铀价路径。
2. **数据缺失降级路线**：把模型拆成 `U1/U2/U3/U4` 与 `C1/C2/C3/C4`，公开数据不足时主动降级模型，而不是为了填表猜测产量、AISC、实现价或合同结构。
3. **贸易与代理拆分**：买断转售、采购/销售代理、offtake/resale、库存头寸分别建模，尤其避免把中核国际代理量按商品总价确认收入。
4. **修复股东回报双算**：回购/增发通过目标年稀释股本和每股价值体现；持续持股人的 TSR 不再额外加一次“回购收益”。
5. **修复 Look-through FCF 双算**：权益矿山底层 FCF 与上市公司现金流必须做关联分红剔除/桥接，禁止把已收到的联营分红再与底层矿山 FCF 相加。
6. **统一数据血缘**：历史数据、预测、估值、Dashboard 均指定唯一 Canonical Source；派生表禁止重新手工填入已有数字。
7. **聚合重复输入**：竞争环境、Peer、管理层/治理所需外部数据只抓取一次，后续模块复用，不允许为不同章节重新搜同一批公司。
8. **管理层可信度客观化**：新增“管理层承诺/指引 → 实际结果”台账，减少纯主观评分。

> V1.1 的原则是：**宁可降低模型分辨率，也不使用不可验证的伪精确数据；宁可给区间，也不为满足表格完整性虚构单点。**

---

# 0. 使用原则与硬约束

## 0.1 本框架首先回答什么

最终研究必须能用尽量少的话回答六个问题：

1. **公司实际上靠什么赚钱？** 是自有矿山资源租金、联营矿山权益收益、采购/销售价差、贸易周转，还是未来矿权期权？
2. **真正决定未来利润的 3–8 个变量是什么？** 哪些变量值得每季度/每半年重复跟踪？
3. **这种利润能持续多久？** 储量、矿山寿命、成本曲线、合同、资源获取权、集团关系、政治风险和资本开支会不会改变它？
4. **当前的困难是什么？** 是铀价周期、项目延期、成本上升、贸易利润下降、资本配置失误、治理折价，还是单纯估值太贵？
5. **2025A–2030E、2031–2035E 在 Bear/Base/Bull 下，收入、利润、FCF、分红和每股价值大概是多少？**
6. **按当前股价买入，未来每股价值回归合理估值并叠加现金分红后，年化收益率是否显著高于 11%？** 回购/增发必须通过目标年股本与每股价值体现，不得在 TSR 中再次重复加减。

## 0.2 禁止事项

执行 Agent 必须遵守以下规则：

- **禁止把“战略重要性”直接等同于上市公司股东护城河。** 国家战略地位只有在经济收益能留在上市公司、关联交易定价合理、资本配置不被母集团侵蚀时，才属于股东护城河。
- **禁止把权益法联营矿山的产量或收入并入上市公司合并收入。** 权益产量可以用于经济暴露分析，但会计收入、利润和现金流必须按实际会计口径处理。
- **禁止把贸易收入当作矿山收入。** 铀价上涨时，贸易公司收入可能大涨，但利润取决于采购成本、价差、库存和周转，不得使用“铀价 × 销量 = 利润”的错误模型。
- **禁止把 Spot 单点价格直接用于所有销售。** 矿山收入应区分长期合同、市场挂钩合同和现货；若合同结构不可得，必须用历史实现价和公开合同信息估计滞后，不得假设 100% 即期重定价。
- **禁止为了填满模型虚构中国铀业等公司的未披露国内产量、储量或成本。** 披露豁免字段必须标记 `ND`/`Range`，使用上下界、公开总量反推或敏感性分析。
- **禁止把尚未投产、没有 FID、长期停产或矿权不稳定的项目按正常生产矿山估值。** 这类项目只能作为概率加权期权或单独的上行情景。
- **禁止机械外推增长。** 特殊情况下允许并应主动使用负增长、停产、延期、利润率收缩和估值倍数下降。
- **禁止使用付费数据库、不可复核券商底稿或无法访问的私有数据作为关键结论的唯一依据。**
- **禁止频繁直接编辑 Excel。** 计算过程优先在内存/DataFrame 或 CSV 中完成，校验通过后一次性批量写入 Excel；不要逐单元格反复读写，以避免网页版 Agent 超时、卡死或格式损坏。
- **禁止公司 Agent 自行重写公共 Bear/Base/Bull 宏观路径。** 三家公司横向比较时必须使用同一个 `common_input_version`；若没有共同输入包，只能生成“暂定/不可横比”的本地快照。
- **禁止把 Step6 的 2026-real 铀价直接和名义收入/成本混算。** 11%资金成本默认与名义现金流匹配；公司模型若使用名义财务预测，必须先按统一 Common inflation path 把实值铀价转换为名义价。
- **禁止把缺失字段默认为 0。** 必须区分 `DIRECT / DERIVED / PROXY / RANGE / ND_NOT_REQUIRED / ND_BLOCKING`；只有经济上真实为 0 才能填写 0。
- **禁止把 AISC、合同覆盖率、可动员库存、维持性 CAPEX 等不可得字段设为硬性必填。** 数据不足时必须切换模型路线并降低估值置信度。
- **禁止在 Peer、竞争环境、治理章节重复抓取同一输入。** 外部同业数据在一个统一采集批次中完成，后续只引用冻结快照。
- **禁止把开放市场回购作为持续持股人的额外现金收益重复计入 TSR。** 回购只通过股本变化、每股指标和资本配置质量体现。

## 0.3 研究区间

- 历史期：原则上至少 **5 个完整财年**；上市不足 5 年则追溯招股书/重组前可比口径。
- 基准年：**2025A**。
- 详细预测：**2026E、2027E、2028E、2029E、2030E**，逐年建模。
- 远期预测：**2031–2035E**，允许用阶段 CAGR、关键项目投产节点和中周期利润粗略测算，但必须至少给出 2033E 与 2035E 两个锚点。
- 当前股价：使用研究执行日最近可得收盘价，并记录 `as_of_date`。

## 0.4 可比性与“唯一事实源”硬约束

所有研究数据分三层：

```text
Common Input（行业/宏观/公共 Peer 快照）
        ↓
Canonical Company Data（公司历史/资产/治理唯一事实源）
        ↓
Derived Tables（预测/估值/Dashboard/最终报告）
```

硬规则：

- 同一研究批次的所有公司必须使用相同 `common_input_version`、`macro_as_of_date` 和 Step6 版本/hash。
- 一个历史字段只能有一个 Canonical Source。若同一数字在多表出现，其他表只能公式/程序派生，不得重新录入。
- `09_forecast` 只能读取 `02–08` 的 Canonical 数据和统一宏观输入；`10_valuation` 只能读取 `09_forecast`、资产 NAV 和当期市场数据；`11_monitoring_dashboard` 只能由 Canonical 表自动生成。
- 若不同公司未使用同一 `common_input_version`，报告必须显著标记 `cross_company_comparability = NO`，不得直接排序其 Base TSR。

---

# 1. 先识别公司类型：同一行业不能用同一利润模型

开始分析任何公司前，先把公司归入以下一种或多种类型。**类型判断决定后续模型，不能跳过。**

## 1.0 先确定“模型分辨率路线”，再决定需要哪些字段

同一矿山/分部因公开数据不同，可使用不同分辨率。模型路线由数据决定，不得反过来要求不存在的数据。

| Route | 最低可得输入 | 主模型 | 典型适用 |
|---|---|---|---|
| `U1_UNIT` | 产量/销量 + 实现价或可校准价格 + 单位成本 | `volume × unit economics` | 中广核矿业部分哈萨克权益矿、披露充分海外矿山 |
| `U2_SEGMENT` | 分部收入 + 分部毛利/利润 + 至少一个运营驱动 | 分部收入/利润率桥 | 中国铀业国内自产铀等披露受限业务 |
| `U3_EARNINGS_PROXY` | 稳定的应占利润/净利润 + 可验证外部驱动 | 历史盈利弹性/利润桥 + 敏感性 | 无法获得完整单位经济数据的权益/资源业务 |
| `U4_OPTION_ND` | 仅有资源权、里程碑或不稳定收益 | 概率加权期权/0 Base | 勘探、长期停产、未 FID 项目 |

规则：

- U1 缺少关键单位成本时自动降为 U2/U3；**不能用行业平均 AISC 冒充公司 AISC**。
- U2/U3 仍需把能观察到的产量、收入、毛利、项目里程碑全部保留作为约束。
- U4 不能为了得到“完整 DCF”而假造产量曲线。
- 每个 asset/segment 必须在 `model_route` 字段记录所用路线，并在 Gate 1 检查。

## 1.1 A 型：合并报表型天然铀生产商

典型：**中国铀业**的国内铀矿、Rössing 等。

核心经济公式：

```text
可归属销量
× 实现铀价
- 矿山现金成本/特许权使用费/运输加工
- 维持性资本开支
- 税费
= 矿山可归属自由现金流
```

重点关注：产量、销量、实现价、现金成本/AISC、储量寿命、矿山爬坡、维持性/扩张性 CAPEX、所有权比例、税费、货币。

## 1.2 B 型：权益法/联营矿山型生产商

典型：**中广核矿业**的哈萨克斯坦矿山权益。

核心经济公式分两层：

```text
经济暴露层：矿山总产量 × 上市公司权益比例 × 单位经济利润
会计层：应占联营/合营公司利润 → 上市公司利润表
现金层：联营公司分红 → 上市公司现金流
```

必须同时维护“权益产量”“应占利润”“实际收到分红”三套口径，禁止混在一起。

## 1.3 C 型：天然铀采购/贸易/供应链平台

典型：**中核国际**；中国铀业和中广核矿业也可能包含该部分业务。

贸易业务必须先区分经济身份，不能只维护一个 `trade_volume`：

### C1 `PRINCIPAL_TRADING` — 买断后再销售

```text
自营销售量 × 销售价
- 对应采购量 × 采购价
- 运输/仓储/融资/汇兑等直接成本
= 自营贸易毛利
```

### C2 `AGENCY_SERVICE` — 采购/销售代理

```text
代理服务量 × commission_per_lb（或合同佣金）
- 服务直接成本
= 代理服务利润
```

**代理量所对应商品总值不是上市公司营业收入，除非会计披露明确按 principal 确认。**

### C3 `OFFTAKE_RESALE` — 包销/offtake 后转售

按合同判断公司是否承担库存、价格和信用风险；承担 principal 风险则按 C1，纯代理则按 C2。不得只因存在 offtake 就默认确认商品总收入。

### C4 `INVENTORY_POSITIONING` — 库存/价格头寸

仅在财报明确存在并且可以量化时单列库存持有损益、公允价值或价格头寸。**不得默认贸易平台通过投机库存赚钱。**

真正驱动贸易/代理利润的是：

- principal 自营量；
- agency 服务量；
- 单位价差或单位佣金；
- 库存周转和采购/销售期限匹配；
- 应收/预付/应付占款；
- 融资成本；
- 母集团采购/销售框架及定价；
- 铀价波动对交易意愿和营运资金的影响。

**绝不能因为铀价上涨就默认贸易净利率同步扩大，也不能把代理量乘铀价当收入。**

## 1.4 D 型：开发项目/勘探矿权期权

典型：中国铀业对 Etango 等开发项目的权益；中核国际的蒙古/尼日尔等未正常生产资产。

必须按照以下阶段折价：

```text
早期勘探 < 资源量确认 < PFS < DFS < 许可 < 融资 < FID < 建设 < 爬坡 < 稳态生产
```

未 FID 项目不得进入 Base 稳态生产利润，除非有足够确定的建设计划。应使用：

```text
项目 NPV × 权益比例 × 阶段成功概率 - 后续需投入资本
```

并在 `option_value` 中独立列示。

---

# 2. 三家重点公司的先验特征与必须单独跟踪的变量

本节是框架的“公司特异性分支”。执行其他公司时可根据商业模式调整。

## 2.1 中国铀业：一体化资源平台，但国内核心数据披露不完全

### 业务本质

- 国内天然铀生产与资源开发；
- 海外合并矿山，Rössing 是重要可量化资产；
- 外购天然铀销售与国际贸易形成大额收入，但利润率显著低于自产矿；
- Etango 等开发项目提供中长期增量；
- 与中核集团体系的战略关系既是资源/客户优势，也是关联交易与股东价值归属的审计重点。

### 每季/半年优先回归变量

**P0：**

1. 自产天然铀收入、毛利率、销量或可反推产量；
2. Rössing 总产量、权益比例、实现价、现金成本/AISC、矿山寿命及扩产/剥采进度；
3. 外购天然铀销售量/收入/毛利率；
4. 国际贸易收入与毛利率；
5. Etango 权益比例、FID/融资/建设/首产/爬坡节点；
6. 资本开支：维持性 vs 新建/扩张；
7. 经营现金流、FCF、库存和预付款；
8. 关联销售/采购占比与定价机制。

**P1：**

- 国内新矿山、地浸项目和资源量新增；
- 纳米比亚税制、特许权使用费、物流/水电成本；
- 罗辛矿山品位、回收率、剥采比变化；
- 外币敞口；
- 分红率、回购、增发/员工持股导致的摊薄。

### 特殊建模规则

- 对未披露的国内天然铀产量/成本，不再默认要求同时估计“产量+单位成本”两个未知数。优先使用 `U2_SEGMENT`：披露的自产铀收入/毛利率 + 可观察运营指标；只有存在足够约束时才做 `low/base/high` 反推。
- 将“自产铀”“外购转售”“国际贸易”分别建模，不使用一个统一毛利率。
- 海外矿山按数据可得程度使用 U1/U2 并单独做矿山 NAV；国内资源若无法做单位级 NAV，则采用分部利润资本化/SOTP + 敏感性，明确降低估值置信度。

## 2.2 中广核矿业：低成本哈萨克矿山权益 + 集团采购/贸易平台

### 业务本质

- 合并收入很大一部分来自天然铀贸易；
- 利润的高质量部分主要来自哈萨克斯坦低成本矿山的权益法收益；
- 关键是“权益产量 × 低成本 × 铀价”形成的资源租金，以及这些利润能否通过联营分红真正回流上市公司。

### 每季/半年优先回归变量

**P0：**

1. 各联营矿山总产量、49%等实际权益比例、权益产量；
2. 各矿山现金成本/AISC、税费、产量指引完成率；
3. 应占联营/合营公司利润；
4. 实际收到联营公司分红和回款；
5. 矿山寿命、储量变化、扩产/减产政策；
6. 哈萨克斯坦税制、矿权、运输及 Kazatomprom 生产纪律；
7. 贸易业务销量、收入、单位毛利/毛利率、库存与营运资本；
8. 母集团相关采购/销售及长期包销/offtake 条款。

**P1：**

- KZT、USD、HKD 汇率；
- 硫酸、能源、人工等 ISR 成本；
- 新项目开发时间表；
- 净现金/债务；
- 股息率与派息率。

### 特殊建模规则

- 必须做 **Look-through 矿山模型**，但与 IFRS/HKFRS 会计报表分开。
- `Look-through FCF` 必须从“上市公司除联营分配以外的独立业务 FCF + 底层权益矿山 FCF”重建；若上市公司 CFO/其他现金流中已经含联营分红，必须先剔除，禁止双算。
- 不能用集团合并 EBITDA 直接和合并型矿商横比，应优先比较“权益产量成本、应占利润、实际现金上划、Look-through FCF”。
- 对哈萨克矿山估值至少进行一次矿山级 DCF/NAV 交叉验证。

## 2.3 中核国际：现金+贸易平台+未成熟资源期权

### 业务本质

- 当前利润主要取决于天然铀贸易/采购平台，而不是稳定在产矿山；
- 高现金可能形成估值安全垫；
- 蒙古、尼日尔等资源权益应当视为条件性期权，不能在 Base 中按在产矿山估值；
- 母集团关系可能带来交易、资源注入或采购机会，也可能形成客户集中和关联交易定价风险。

### 每季/半年优先回归变量

**P0：**

1. 天然铀贸易销量；
2. 单位毛利、毛利率和历史波动；
3. 库存金额、库存天数、跌价/公允价值风险；
4. 应收账款、预付款、应付账款、经营现金流；
5. 现金及净现金/市值；
6. 母集团/关联方收入与采购占比；
7. 贸易合同期限、采购与销售是否匹配；
8. 矿权/停产资产是否出现许可、融资、重启、处置或资产注入等硬里程碑。

**P1：**

- 汇兑与融资成本；
- 单一客户/地区集中度；
- 管理层变动；
- 特殊股息、回购、增发；
- 资产减值或一次性收益。

### 特殊建模规则

- Base Case 对未成熟矿权的价值原则上取低值或 0，仅当项目跨过可验证里程碑后再上调。
- 先按 C1/C2/C3/C4 识别交易身份；采购代理/销售代理必须按佣金模型，不能按代理商品总价值建模。
- 贸易公司的 FCF 必须同时看：`reported CFO`、`working-capital-adjusted CFO`、3 年滚动 normalized FCF。
- 净现金不能简单全额加回估值：使用 `distributable_net_cash = cash + liquid_investments - debt - restricted_cash - minimum_operating_cash - required_trade_working_capital - committed_near_term_capex`；无法精确拆分时做区间。

---

# 3. 数据源：只使用可获得、可复核的信息

## 3.1 来源优先级

### Tier 1：可作为核心模型依据

- 年报、半年报、季报；
- 招股书、上市文件；
- HKEX、CNINFO、上交所/深交所公告；
- 公司正式投资者演示、业绩会材料；
- 矿山运营公司或合作方的法定披露；
- 母集团正式公告中与上市公司直接相关的信息；
- 政府/监管机构、矿业主管部门、核能主管部门数据。

### Tier 2：行业模型和交叉验证

- WNA；
- EIA；
- Euratom Supply Agency；
- Cameco、Kazatomprom、Orano 等公开行业数据；
- 项目合作方 DFS/PFS/技术报告；
- 用户提供的《铀需求供给研究 Step6》数据包。

### Tier 3：只用于市场价格/新闻补充，不得单独支撑核心结论

- Reuters、Bloomberg 摘要、主流财经媒体；
- 公开行情网站；
- 二手行业报道。

## 3.2 明确禁止依赖

- 无法访问的 Wind/Bloomberg 专有字段；
- 无法看到原文的付费券商报告；
- 微信群、论坛、匿名“专家”口径；
- 没有原始来源的资源量、现金成本或项目投产时间；
- 仅由搜索摘要展示、无法回溯原文件的关键数字。

## 3.3 数据质量与可得性是两个维度

每个关键字段同时维护 `data_quality` 与 `availability_status`。

### `data_quality`

- `A`：审计财报/正式监管披露；
- `B`：合作方/政府/公司演示，可交叉验证；
- `C`：根据多个已披露字段反推；
- `D`：可比公司或行业区间估计，仅用于敏感性/边界。

### `availability_status`

- `DIRECT`：公司/监管直接披露；
- `DERIVED`：由披露数据唯一或近唯一反推；
- `PROXY`：使用可验证代理变量；
- `RANGE`：只能得到上下界；
- `ND_NOT_REQUIRED`：不可得，但切换模型路线后不影响主模型可执行；
- `ND_BLOCKING`：不可得且没有可信替代，会显著改变主估值。

**缺失数据不是自动 FAIL。** Agent 必须先问：“U1 不可做时，是否能可靠降级到 U2/U3/U4 或 C1–C4 的其他可执行路线？”

**C/D、PROXY、RANGE 均必须保存公式、来源和上下界，不能伪装成公司披露单点。** 只有 `ND_BLOCKING` 才属于 Gate 1 的潜在 P0 阻断项。

## 3.4 常见不可得字段的默认处理

| 字段 | 默认处理 | 禁止做法 |
|---|---|---|
| 国内铀矿产量/成本披露豁免 | U2/U3 分部模型，必要时 Range | 为了 U1 人工猜一组产量+AISC |
| AISC 未披露 | 使用公司披露 cash/production cost 并保留 `cost_definition`，或降级 | 用行业平均 AISC 冒充 |
| 长协固定/浮动比例 | 历史实现价校准 + lag/coverage Range | 假设 100% Spot 或任意固定比例 |
| sustaining CAPEX 未拆分 | total CAPEX + 维持/增长区间；FCF 给 Range | 随意给单点 |
| 公司库存实物 lb 不披露 | 使用库存金额、天数和 WC 压力 | 用金额/现价机械换算并当真实吨位 |
| 精确全球成本曲线 percentile | 使用 low/mid/high-cost bucket | 依赖不可复核付费成本曲线 |

---

# 4. 统一单位与会计口径

这一步必须在所有历史数据进入模型前完成，否则后续比较无效。

## 4.1 铀单位

标准模型统一使用：

- 产量/销量：`Mlb U3O8`；
- 行业供需：`ktU`；
- 铀价：`USD/lb U3O8`。

换算：

```text
1 tU ≈ 2,599.79 lb U3O8
1 ktU ≈ 2.59979 Mlb U3O8
```

每条数据必须保存原单位与换算后单位。

## 4.2 币种

- 单家公司模型保留其报告币种作为主币种；
- 跨公司比较统一转换为人民币或港币时，必须记录使用的平均/期末汇率；
- 利润表项目原则上用期间平均汇率，资产负债表项目用期末汇率；
- 不得混用实时汇率与历史财务数据。
- 预测和估值必须在**名义/实值口径上自洽**。默认：Step6 价格先由 `common_input_snapshot` 统一从 2026-real 转为名义价格，再与名义收入/成本/CAPEX 预测匹配；11% hurdle 也按名义资金成本使用。只有整套模型全部改为实值现金流时，才允许保留实值价格，并需相应使用实值折现率。

## 4.3 权益产量 vs 合并销量

统一维护：

```text
gross_production = 矿山 100% 产量
attributable_production = gross_production × economic_ownership
consolidated_sales_volume = 按上市公司会计合并口径确认的销量
```

三者不得混写。

## 4.4 利润和现金流

至少同时维护：

- 报告归母净利润；
- 调整后归母净利润；
- 经营现金流 CFO；
- 会计 FCF = CFO - 资本开支；
- Look-through FCF（仅对权益法矿山重要公司）；
- 每股 FCF；
- 净现金/净债务。

一次性处置、减值转回、公允价值、政府补助等必须单列。

## 4.5 成本、ROIC、营运资金指标必须定义口径

- 所有单位成本旁必须保存 `cost_definition`，例如 `cash_cost/company_defined_production_cost/AISC_like/AISC`；不同定义不得直接横比。
- 无法获得精确全球成本曲线位置时，只给 `low / mid / high cost bucket`，并写依据。
- `ROIC = NOPAT / average_invested_capital`；权益法公司同时报告 `accounting_ROIC` 与可做时的 `lookthrough_ROIC`，禁止把联营资产/利润一边计入一边漏掉。
- `operating_NWC = operating_receivables + inventory + operating_prepayments - operating_payables - operating_contract_liabilities`。
- `working_capital_adjusted_CFO = reported_CFO + Δoperating_NWC`（其中经营性 NWC 增加记正）；非经营并购/融资款项必须剔除。
- `inventory_days = average_inventory / relevant_COGS × 365`；若贸易成本口径不同必须注明分母。
- `cash_conversion = accounting_FCF / adjusted_net_profit`；若分母≤0，不输出无意义百分比，改做绝对现金流解释。

---

# 5. 文件与数据表设计

## 5.1 核心工作流：CSV-first，Excel-final

为了减少网页版 ChatGPT/Agent 在 Excel 上反复读写造成的超时和损坏，执行时必须遵循：

1. 先从原始文件提取数据到 DataFrame/内存；
2. 一次完成同一张表的所有计算；
3. 校验行数、主键、单位、公式和空值；
4. **批量写入 CSV**；
5. 各 Phase 只读取已完成 CSV，不重复扫描全部年报；
6. Final Gate 后，再一次性把最终 CSV 批量汇总写入 XLSX；
7. 不要在每个步骤中逐个单元格编辑 Excel。

## 5.2 文件命名

所有单家公司输出严格采用：

```text
<company_name>_<custom_name>.<ext>
```

例如：

```text
中国铀业_01_sources.csv
中国铀业_03_asset_master.csv
中国铀业_uranium_investment_model.xlsx
中国铀业_uranium_investment_report.md
```

## 5.3 必须维护的 CSV

### A. `<company_name>_00_manifest.csv`

| 字段 | 说明 |
|---|---|
| file_name | 本研究包中的文件名 |
| purpose | 用途 |
| phase_created | 创建阶段 |
| phase_last_updated | 最后更新阶段 |
| row_count | 行数 |
| sha256_optional | 可选校验值 |
| status | draft/final |

### A2. `<company_name>_00_common_input_snapshot.csv`

这是跨公司可比性的硬接口。每个公司研究包都保存一份相同版本快照；公司 Agent **只读，不得自行修改宏观值**。

主键：`common_input_version + scenario + year`。至少包含：

```text
common_input_version, macro_as_of_date, step6_version, step6_hash,
scenario, year, scenario_type, price_basis, inflation_assumption, inflation_index,
uranium_LT_price_real_USD_lb, uranium_LT_price_nominal_USD_lb,
uranium_spot_reference_real_USD_lb, uranium_spot_reference_nominal_USD_lb, reference_demand_ktU,
reference_primary_supply_ktU, structural_secondary_ktU,
inventory_state, seller_scarcity_probability,
source_file, source_metric, construction_rule, comparable_batch_id
```

规则：

- `scenario_type` 可为 `COHERENT_MACRO` 或 `STANDARDIZED_PRICE_STRESS`；不得把后者误写成完整概率世界。
- 三家公司比较时 `common_input_version` 和 `comparable_batch_id` 必须一致。
- 若输入已提供统一三情景表，原样复制，不重新构造。
- 若只有 Step6 Reference 路径，按 Phase 0 的冻结规则生成一次；其他公司必须复用该文件。

### A3. `<company_name>_00_data_lineage.csv`

用于定义唯一事实源并防止重复填数：

```text
field_group, canonical_table, canonical_key,
derived_tables, derivation_rule, owner_phase,
manual_edit_allowed, notes
```

例如：历史总收入 Canonical=`05_financial_history`、历史分部收入 Canonical=`02_business_segments`；预测收入 Canonical=`09_forecast`；`11_dashboard` 中的收入只能自动读取，`manual_edit_allowed=NO`。P0 或非 DIRECT 字段的来源/公式进一步由 `01b_field_provenance` 记录。

### B. `<company_name>_01_sources.csv`

| 字段 | 说明 |
|---|---|
| source_id | 唯一编号 |
| source_type | annual/interim/prospectus/exchange/operator/government/industry/news |
| title | 文件标题 |
| issuer | 发布者 |
| publish_date | 发布日期 |
| reporting_period | 覆盖期间 |
| url_or_file | URL 或输入文件名 |
| page_or_section | 页码/章节 |
| fields_supported | 支持哪些数据 |
| tier | 1/2/3 |
| accessed_date | 访问日期 |
| notes | 冲突/口径备注 |

### B2. `<company_name>_01b_field_provenance.csv`

为避免“一行多个字段却只有一个 source_id”的审计缺陷，本表只记录 **P0 字段以及所有 DERIVED/PROXY/RANGE/ND 字段**；DIRECT 且来源单一的普通字段无需逐格复制。

```text
table_name, row_key, field_name, value, unit,
availability_status, data_quality, source_ids,
formula_or_range, model_route, notes
```

`source_ids` 可用 `;` 连接多个 `01_sources` 编号。任何 C/D/PROXY/RANGE 估计若没有本表记录，`12_checks` 必须 WARN/FAIL。

### C. `<company_name>_02_business_segments.csv`

主键：`year + segment_id`

字段至少包括：

```text
year, segment_id, segment_name, business_type, model_route,
revenue, gross_profit, gross_margin, operating_profit,
asset_region, revenue_region, accounting_method,
related_party_revenue_pct, related_party_purchase_pct,
availability_status, data_quality, source_id
```

用途：把自产矿、外购转售、贸易、服务、勘探/开发项目分开。

### D. `<company_name>_03_asset_master.csv`

一行一个矿山/项目/重大贸易平台。

```text
asset_id, asset_name, country, region, business_type, model_route,
operator, economic_ownership, voting_ownership, accounting_method,
status, resource_or_reserve, resource_class, reporting_standard, resource_unit,
mine_life_end, design_capacity_Mlb, latest_gross_production_Mlb,
latest_attributable_production_Mlb, cash_cost_USD_lb, AISC_USD_lb, cost_definition,
royalty_tax_notes, sustaining_capex, growth_capex,
FID_date, construction_start, first_production, ramp_year,
contract_or_offtake_notes, political_risk_score,
availability_status, data_quality, source_id
```

### E. `<company_name>_04_operating_history.csv`

主键：`year + asset/segment`

```text
year, asset_or_segment, model_route, gross_production_Mlb,
attributable_production_Mlb, sales_volume_Mlb,
realized_price_USD_lb, cash_cost_USD_lb, AISC_USD_lb, cost_definition,
utilization_pct, grade, recovery, inventory_volume_physical, inventory_value,
principal_trade_volume_Mlb, principal_trade_spread_per_lb,
agency_volume_Mlb, agency_commission_per_lb,
offtake_volume_Mlb, offtake_accounting_role,
contracted_volume_pct, spot_linked_volume_pct,
availability_status, source_id, data_quality
```

不可得字段可以为空，**不要求每一列都填满**；由 `model_route` 决定哪些字段是该资产/分部的必要输入。`ND_NOT_REQUIRED` 不得因为表中存在该列而被强行估数。

### F. `<company_name>_05_financial_history.csv`

一行一年，原则上至少 5 年：

```text
year, revenue, gross_profit, EBITDA, EBIT,
share_of_associate_profit, attributable_net_profit, adjusted_net_profit,
reported_CFO, operating_NWC, delta_operating_NWC, working_capital_adjusted_CFO,
capex_total, capex_sustaining, capex_growth, accounting_FCF,
standalone_ex_associate_FCF, lookthrough_FCF, associate_dividends_received,
cash, liquid_investments, restricted_cash, debt, net_cash, distributable_net_cash,
inventory, receivables, prepayments, payables, total_assets,
equity, ROE, accounting_ROIC, lookthrough_ROIC, diluted_shares,
EPS, FCF_per_share, dividend_per_share
```

### G. `<company_name>_06_capital_allocation_governance.csv`

```text
year, dividends_paid, dividend_payout_pct,
buybacks, share_issuance, net_buyback_yield,
M&A_spend, growth_capex, impairment,
related_party_revenue_pct, related_party_purchase_pct,
management_shareholding_pct, management_turnover,
auditor, audit_opinion, major_governance_event,
capital_allocation_score, governance_score, notes, source_id
```

### G2. `<company_name>_06b_management_delivery.csv`

用于把“管理层可信度”从印象判断变成可审计台账。主键可为 `promise_id`：

```text
promise_id, announcement_date, metric_or_project,
management_target, target_value, target_unit, target_date,
actual_value, actual_date, variance_pct, delay_years,
status_met_partial_missed_open, explanation, source_id, data_quality
```

至少回看过去 3–5 年所有能量化的重要产量指引、项目投产/FID、资本开支、分红政策、收购协同等承诺。无明确指引时允许空表并注明原因。

### H. `<company_name>_07_peer_comparison.csv`

包含目标公司 + **2–5 个真正可比竞品**；宁可少而可比，不强迫凑满 3 家。外部 Peer 数据只能在 Phase 2 的统一采集批次中抓取一次。字段：

```text
peer_snapshot_version, comparable_batch_id, as_of_date, operating_period,
company, archetype, market_cap, EV, attributable_production_Mlb, reserve_life_years,
cash_cost_USD_lb, AISC_USD_lb, cost_definition, cost_bucket_low_mid_high,
realized_price_USD_lb, revenue, net_profit, net_margin, ROE, ROIC, FCF, net_cash,
PE, EV_EBITDA, P_FCF, dividend_yield, market_cap_per_attributable_lb,
EV_per_attributable_lb, notes
```

若同一研究批次分析多家公司，共同 Peer（如 Kazatomprom/Cameco/Paladin）的行应**只采集一次后复制复用**，并保持相同 `peer_snapshot_version`、`as_of_date` 与 `operating_period`；不得在第二家公司中重新搜索一套更新日期不同的数据。目标公司特有 Peer 可以追加。

### I. `<company_name>_08_scenario_assumptions.csv`

主键：`scenario + year + variable`。本表原则上只保存**公司特异参数**；公共宏观值的 Canonical Source 永远是 `00_common_input_snapshot`。若为了阅读把宏观值镜像到本表，必须标记 `parameter_type=MACRO_LOCKED_REFERENCE`、`manual_edit_allowed=NO`，且检查与 00 完全一致。

```text
common_input_version, scenario, year, variable, value, unit,
parameter_type_macro_locked_or_company, source_or_formula,
is_macro_input, is_company_input, manual_edit_allowed,
sensitivity_low, sensitivity_high, availability_status, notes
```

### J. `<company_name>_09_forecast_2025_2035.csv`

主键：`scenario + year`

```text
common_input_version, scenario, year, uranium_LT_price_real_USD_lb,
uranium_LT_price_nominal_USD_lb, uranium_spot_reference_real_USD_lb,
uranium_spot_reference_nominal_USD_lb, gross_production_Mlb, attributable_production_Mlb,
sales_volume_Mlb, realized_price_USD_lb, principal_trade_volume_Mlb, principal_trade_spread_per_lb,
agency_volume_Mlb, agency_commission_per_lb, offtake_volume_Mlb,
revenue, gross_profit, share_of_associate_profit, EBIT, net_profit,
reported_CFO, working_capital_adjusted_CFO, capex, accounting_FCF, lookthrough_FCF,
dividend_cash_paid, dividend_per_share, buyback_cash, shares_bought_back,
share_issuance_cash_proceeds, shares_issued, diluted_shares, EPS, FCF_per_share,
M&A_cash, other_material_cash_flow, net_cash, distributable_net_cash, notes
```

2025A 只保存一套 `scenario=Actual`，不要在 Bear/Base/Bull 下复制三份相同历史值；2026E–2035E 才使用三情景。

### K. `<company_name>_10_valuation.csv`

```text
scenario, valuation_date, target_year, method,
metric, metric_value, valuation_multiple_or_discount_rate,
enterprise_or_equity_value, fair_value_per_share,
method_validity, exclusion_reason,
current_price, upside_downside_pct, cumulative_dividend_per_share,
direct_cash_distribution_per_share, annualized_TSR, NPV_at_11pct,
max_entry_price_for_11pct, margin_of_safety_pct, confidence_level
```

### L. `<company_name>_11_monitoring_dashboard.csv`

用于季度/半年回归。**该表原则上只能从 Canonical 表派生；除阈值和 action 文本外，不得重新手工录入历史/预测数值。**

```text
priority, frequency, variable, latest_value,
base_threshold, bullish_threshold, bearish_threshold,
change_vs_previous, thesis_impact,
action_if_triggered, source_id
```

### M. `<company_name>_12_checks.csv`

```text
check_id, category, test, expected, actual,
status_PASS_WARN_FAIL, severity_P0_P1_P2,
fix_action, phase, notes
```

## 5.4 Canonical Source / 数据血缘规则（强制）

默认唯一事实源：

| 数据组 | Canonical 表 | 允许派生到 |
|---|---|---|
| 历史分部收入/毛利 | `02_business_segments` | 05/07/11/报告 |
| 资产静态属性/权益/资源 | `03_asset_master` | 07/09/NAV/报告 |
| 历史产量/单位成本/交易量 | `04_operating_history` | 07/08/09/11 |
| 历史财务/现金流/股本 | `05_financial_history` | 06/09/10/11 |
| 分红回购/治理 | `06_capital_allocation_governance` | 09/10/11 |
| 管理层承诺兑现 | `06b_management_delivery` | 治理评分/报告 |
| 外部 Peer 快照 | `07_peer_comparison` | 护城河/倍数区间/报告 |
| 公司情景假设 | `08_scenario_assumptions` | 09 |
| 预测 | `09_forecast_2025_2035` | 10/11/报告 |
| 估值 | `10_valuation` | 报告 |

若某个派生表与 Canonical 表不一致，以 Canonical 为准并在 `12_checks` 报错。禁止为了“让表看起来一致”反向修改历史事实源。

## 5.5 最终 Excel

最终一次性生成：

```text
<company_name>_uranium_investment_model.xlsx
```

建议 Sheet 与上述 CSV 一一对应；所有关键公式尽量已经在 CSV/DataFrame 阶段计算完成，Excel 主要用于审计、筛选和浏览，不把复杂计算只藏在 Excel 公式中。

---

# 6. Phase 0 — 初始化、商业模式分类与行业输入锁定

## 任务

1. 识别公司 A/B/C/D 业务及每个资产/分部的 U1/U2/U3/U4、C1/C2/C3/C4 `model_route`；
2. 建立 2021–2025 历史数据范围和 2026–2035 预测范围；
3. 导入 Step6/统一 Common Pack，生成并冻结 `<company_name>_00_common_input_snapshot.csv`；
4. 确认 `common_input_version`、当前股价、股本、币种和 `as_of_date`；
5. 建立 `00_manifest`、`00_data_lineage`、`01_sources` 与空白 Canonical 表模板。

## Step6 行业输入与 Common Input 冻结规则

若用户提供《铀需求供给研究 Step6》完整包，优先读取并复用：

- `01_key_metrics.csv`：长期价锚、需求、供应、库存和价格清算关键值；
- `02_annual_risk_dashboard.csv`：2027–2036 年度需求/供应/价格状态；
- `03_price_regime_buckets.csv`：长期价清算世界分布；
- `07_project_watchlist.csv`：全球关键项目时间表；
- `09_monitoring_triggers.csv`：行业监控阈值。

### 优先模式 A：已有统一三情景 Common Pack

若输入包含用户/前序研究已冻结的 Bear/Base/Bull 年度宏观表：

1. 原样复制到 `<company_name>_00_common_input_snapshot.csv`；
2. 保存版本/hash；
3. **公司 Agent 无权修改其中任何宏观参数**；
4. 公司差异只允许体现在实现价滞后、产量、成本、贸易价差、项目执行等 company-specific 参数。

### 回退模式 B：只有 Step6 Reference，没有统一三情景表

此时不能让三个公司 Agent 各自“发挥”一套宏观世界。必须先创建一次标准化公共快照，再复用。

默认仅建立 **`STANDARDIZED_PRICE_STRESS`**，明确它是可比估值压力测试，而不是重新声称得到完整概率一致的全球 Bear/Base/Bull。为防止不同 Agent 再次自由发挥，默认构造规则必须机械执行：

1. `Reference physical path`：Bear/Base/Bull 的需求、primary supply、secondary supply、库存状态均直接读取同一 Step6 年度 Reference，不自行改写；因此该回退模式的三场景差异主要是**价格压力 + 公司执行**，不是三套重新模拟的全球物理世界。
2. `Bear LT`：2026–2035 每年均等于 Step6 `current_LT_price`（保持 2026 real 口径）。
3. `Base LT`：2026–2035 每年均等于 Step6 `50% cumulative inventory-draw clearing floor`。
4. `Bull LT`：2026–2035 每年均等于 Step6 `45% inventory-preserving clearing floor`。
5. `Spot reference`：
   - 2026：Bear/Base 使用 Step6 current spot anchor；Bull 使用 `max(current spot, current LT)`；
   - 2027–2035 Bear：`min(annual finite conditional P50 spot, Bear LT)`；
   - 2027–2035 Base：annual finite conditional P50 spot；
   - 2027–2035 Bull：annual finite conditional P90 spot；
   - Spot 只映射真实 spot-linked volume / inventory exposure。
6. `Tail Stress`：单独读取 seller-scarcity、P(Spot>200) 和高非线性尾部，**不得并入终值**。
7. 每一行必须在 `construction_rule` 保存上述公式和 Step6 `source_metric`，确保第三方可以机械复算。

所有值保留 Step6 的原始 **2026 real** 口径；若公司模型需要名义值，统一使用 Common Pack 中同一个 inflation assumption 转换并记录公式。若 Step6 缺少某一年（例如基准年之前），只能使用明确定义的 carry-forward/anchor 规则，不得插值创造新的“预测”。

若认为上述标准压力测试不足以描述宏观 Bear/Base/Bull，应该先回到行业研究生成一份真正的 `COHERENT_MACRO` 三情景包，**而不是在单家公司里各自修改**。

### 可比性规则

- 没有同一 Common Pack：可以完成单家公司研究，但 `cross_company_comparability=NO`。
- 三家公司横向排序前：必须把相同 common snapshot 复制到各研究包并重跑预测/估值。
- 只有以下情况才允许更新 Common Pack：Step6 明显过期、重大新信息改变行业缺口，或用户明确要求；一旦更新，**所有公司应使用新版本同步重算**。

### 统一宏观结论的正确用法

Step6 中：

- LT 是 FID/长期合同投资信号；
- Spot 是库存与短期稀缺的边际价格；
- 极端 Spot 尾部不能直接作为所有矿山长期实现价。

因此公司模型应把**统一宏观价格 → 合同/交易映射 → 公司实现价/价差 → 公司利润**分层处理。

## Phase 0 输出

- 商业模式与 `model_route` 分类表；
- 来源清单；
- 冻结的 Common Input 快照与版本/hash；
- 数据血缘表；
- 数据缺口清单，逐项标记 `availability_status`；
- 后续需要特殊分支/降级路线的字段。

---

# 7. Phase 1 — 一次性完成历史数据、资产、地域、利润和资本配置底座

> 原则：**所有后续模块共同需要的输入，都在本阶段一次收集并标准化。后续 Phase 不得重复扫描年报来找相同数字。**

## 7.1 公司股权与集团关系

画出：

```text
最终控制人
→ 母集团
→ 上市公司
→ 子公司/联营/合营
→ 矿山/贸易平台
```

对每项资产标出：

- 经济权益；
- 表决权；
- 会计合并方式；
- 是否存在 minority interest；
- 是否有包销/offtake；
- 关联采购/销售。

## 7.2 国内外资产构成

至少量化：

- 国内/海外总资产；
- 国内/海外非流动资产；
- 国内/海外在产铀矿；
- 各地区资源量/储量（可得时）；
- 各地区权益产能和权益产量；
- 开发项目的潜在增量。

若地区资产披露与实际矿山经济暴露不一致，必须解释会计原因。

## 7.3 国内外营收与利润构成

至少分：

- 中国大陆；
- 香港；
- 哈萨克斯坦；
- 纳米比亚；
- 其他海外。

但必须同时提醒：

> **销售目的地 ≠ 矿山所在地 ≠ 利润来源。**

对中广核矿业等公司，重点构造“地域收入”和“地域利润/矿山权益”两张表，避免因贸易目的地误判资产暴露。

## 7.4 业务分部利润桥

把总利润拆为：

```text
自产矿利润
+ 联营/合营矿山应占利润
+ 外购转售利润
+ 国际贸易利润
+ 其他服务/投资收益
- 总部费用
- 财务费用
- 税
= 归母净利润
```

要求对 2025A 至少能解释 **80% 以上归母利润来源**；无法解释的部分列入 `unallocated`。

## 7.5 现金流和资产负债表

重点检查：

- 经营现金流是否长期匹配净利润；
- 库存增长是否吞噬现金；
- 应收/预付款是否异常；
- 联营利润是否能变成现金分红；
- 维持性资本开支是否被低估；
- 净现金是否真正可分配；
- 是否存在大量其他应收、长期投资、关联方资金占用。

## 7.6 股东回报历史

至少 5 年记录：

```text
现金股息
开放市场回购
新增发行/配股/期权摊薄
```

注意：`净回购收益率`是资本配置指标，不等于持续持股股东当期拿到的现金；最终 TSR 中不额外加一次。

输出：

- 分红率；
- 股息率；
- FCF payout；
- 净回购收益率；
- 每股净资产/EPS/FCF 的摊薄/增厚变化；
- 回购发生时尽量比较回购价格与当时/事后合理价值，避免“任何回购都是好事”的机械判断。

## 7.7 管理层承诺与兑现台账

在同一次历史文件读取中，顺手抽取过去 3–5 年可量化的重要承诺，写入 `06b_management_delivery.csv`：

- 年度/季度产量指引；
- FID、建设、首产、爬坡时间；
- CAPEX 预算；
- 分红政策/派息目标；
- 收购时承诺的产量、成本、协同或回报。

后续治理章节只读取这张表，不再次搜索相同公告。

---

# Gate 1 — 数据与商业模式人工 Review

执行 Agent 必须给出 `PASS / CONDITIONAL PASS / FAIL`。

人工至少检查：

1. 是否把权益法矿山错误并入合并收入？
2. 是否把贸易收入错误当作矿山收入？
3. 国内外“销售地区”和“资产/利润地区”是否分开？
4. 所有权、表决权、会计合并方式是否一致？
5. tU、lb U3O8、Mlb 是否全部统一？
6. 2025A 归母利润是否能被业务分部大致解释？
7. 中国铀业等未披露数据是否保持区间，而非伪造单点？
8. 现金流、股本、分红、增发是否完整？
9. 每个关键缺失字段是否已经标记 `DIRECT/DERIVED/PROXY/RANGE/ND_NOT_REQUIRED/ND_BLOCKING`？
10. U1 无法执行时是否已经正确降级到 U2/U3/U4，而不是人为补数？
11. `common_input_version` 是否已冻结；若用于横向比较，是否与其他公司一致？
12. 是否存在真正的 `ND_BLOCKING`：没有可信替代模型且足以改变主要估值？

Gate 规则：

- `PASS`：没有 ND_BLOCKING，关键数据血缘完整；
- `CONDITIONAL PASS`：存在重要 Range/Proxy，但已有可执行降级模型，必须降低后续 `confidence_level`；
- `FAIL`：存在 ND_BLOCKING、单位/会计口径未解决、或利润桥无法基本闭合。

**只有 FAIL 才禁止进入预测。合法不可披露但已有 U2/U3 等替代路线，不得自动判 FAIL。**

---

# 8. Phase 2 — 一次性外部对标采集 + 竞争、库存、护城河和“困境”诊断

> **聚合规则：** Phase 2 是本研究唯一的外部 Peer/竞争数据采集批次。一次抓取后完成 `07_peer_comparison.csv`，并把会用于 Phase 3 管理层/治理交叉验证的信息同时保存。Phase 3 原则上只能读取已有 01–07 表，不得再次搜索同一批公司。若确有新缺口，先在 `12_checks` 记录 `NEW_DATA_NEEDED` 再补抓。

## 8.1 全球竞争环境

不要简单问“铀行业竞争激不激烈”，而要按资源租金链条拆分：

### 上游资源

- 全球低成本矿山集中度；
- 哈萨克斯坦、加拿大、纳米比亚等核心产区；
- 在产/开发项目成本层级；公开数据不足时只做 `low/mid/high cost bucket`，不要求精确 percentile；
- 新矿许可、融资、建设周期；
- 资源民族主义、税收、出口/运输风险。

### 中游采购与合同

- 长期合同价格；
- 公用事业公司未签约需求；
- 生产商合同覆盖；
- 现货/长期合同 basis；
- 包销权和母集团采购平台是否构成公司优势。

### 下游与核燃料链

至少判断以下因素是否会改变天然铀需求时间：

- 转化；
- 浓缩；
- underfeeding/overfeeding；
- 燃料组件；
- 反应堆换料周期。

无需构建完整核燃料模型，但不能忽视天然铀需求可能因浓缩市场变化而前移/后移。

## 8.2 库存分析：行业库存 + 公司库存分开

### 行业库存

复用 Step6：

- utility inventory；
- 可动员库存；
- 地区可转移性；
- contract coverage；
- financial inventory；
- producer inventory。

重点不是“库存够几年”，而是：

```text
谁持有？
能否出售？
合同是否允许？
单年最大愿意释放多少？
```

### 公司库存

贸易型公司重点：

- 库存天数；
- 库存成本；
- 已签销售合同覆盖；
- 采购/销售期限错配；
- 铀价下跌的库存跌价风险；
- 铀价急涨造成的追加营运资金需求。

矿山型公司重点：

- 成品库存与销量差；
- 生产中断后的库存缓冲；
- 合同交付义务。

## 8.3 巴菲特式护城河评分

铀公司的护城河不是品牌，而主要来自**低成本资源、稀缺许可、合同/渠道、资本和长期经营权**。

默认 100 分：

| 维度 | 权重 | 判断标准 |
|---|---:|---|
| 低成本资源与矿山寿命 | 25 | 成本曲线位置、储量、品位、寿命、扩产潜力 |
| 资源/许可/项目稀缺性 | 15 | 许可难度、国家战略资源获取能力、复制成本 |
| 合同与客户锁定 | 15 | 长协、offtake、母集团需求、客户稳定性 |
| 运营与项目执行 | 15 | 指引兑现、停产率、扩产/FID/爬坡能力 |
| 资产负债表和融资能力 | 10 | 低负债、逆周期投资能力 |
| 资源租金能否留给上市股东 | 10 | 税费、关联定价、少数股东、母集团利益冲突 |
| 管理层与资本配置 | 10 | 分红回购、并购质量、摊薄、透明度 |

### 护城河硬门槛

即使总分很高，只要以下任一项成立，最高不得评为“强护城河”：

- 资源寿命短且补充不足；
- 长期处在成本曲线高位；
- 关联方可以显著改变采购/销售定价且缺乏保护；
- 重大项目反复延期或超支；
- 利润无法持续转化为 FCF；
- 少数股东无法合理分享资源租金。

## 8.4 “战略优势”与“股东护城河”分开

对央企/国企尤其重要：

```text
Strategic Moat：牌照、国家资源获取、外交/集团支持
Shareholder Moat：这些优势产生的现金是否留在上市公司普通股股东手中
```

两项分别打分，不得合并。

## 8.5 长期稳定经营的硬判断标准

在讨论“好公司”之前，先判断公司能否在一个完整铀周期内稳定生存并持续为普通股股东创造现金。至少检查以下七项：

1. **资源寿命**：核心在产资产是否拥有大致 10 年以上可见寿命，或有可信的资源补充/扩产管线；寿命过短必须在估值中扣除再投资需求。
2. **成本安全垫**：核心矿山在 Bear 长期铀价下是否仍有正的矿山现金利润；若单位总经济成本长期接近激励价格，公司不是强护城河。
3. **资产负债表**：Bear 连续 3 年下，公司是否无需大规模增发即可完成维持性 CAPEX、偿债和必要营运资金。
4. **现金转化**：跨周期调整后净利润能否稳定转化成 FCF；权益法公司还要检查联营利润能否转化为实际现金分红。
5. **客户/合同质量**：单一客户或母集团依赖是否有长期框架、定价保护和可审计的公平性；客户集中本身不是坏事，无法解释定价才是风险。
6. **再投资回报**：扩产、收购和新矿项目的预期/实现税后回报率是否长期高于 11% 资金成本。
7. **资源租金归属**：税、特许权、少数股东、关联交易、母集团安排以后，资源上涨带来的增量价值是否能进入上市公司普通股股东的 FCF。

建议评级：

- `Durable`：7 项中至少 6 项通过，且成本/资产负债表/资源租金归属三项无硬伤；
- `Cyclical but durable`：能穿越周期，但收益高度受铀价影响；
- `Fragile`：Bear 下需要融资、核心资产寿命不足或 FCF 转化长期差；
- `Option-like`：当前稳定盈利能力弱，价值主要来自项目/资产注入/矿权事件。

必须把这项评级与“当前估值便宜/昂贵”分开。**便宜的 Fragile 公司不能因为低 PE 被写成高质量公司。**

## 8.6 困境诊断：为什么最近几年没有起色？

不要预设公司一定处于困境。依次排查：

1. **商品周期型**：铀价/合同价不足；
2. **产量型**：矿山品位、停产、减产、爬坡失败；
3. **成本型**：硫酸、人工、能源、物流、税费上涨；
4. **项目型**：开发项目延期、超支、融资失败；
5. **贸易型**：价差收窄、周转下降、库存损失；
6. **现金流型**：利润增长但 FCF 恶化；
7. **治理型**：关联交易、资本配置、频繁增发；
8. **估值型**：基本面改善但过去估值太高，股价靠 PE 压缩消化；
9. **非困境**：利润和 FCF 本身正常，只是市场预期变化。

### 关键反事实

必须回答：

> 如果 2026–2030 铀长期价保持不变，公司自身产量/成本/项目按计划执行，利润和 FCF 是否仍能增长？

- 若能：公司增长不完全依赖商品价格；
- 若不能：本质是高 Beta 周期股；
- 若铀价上涨仍不增长：可能是结构性问题。

---

# 9. Phase 3 — 复用冻结输入完成 Peer 量化比较 + 管理层可信度

> 本 Phase 是**分析层而不是重新抓数层**。Peer 数字来自 Phase 2 冻结的 `07_peer_comparison`；公司资本配置来自 05/06；管理层兑现来自 `06b_management_delivery`。除 Gate 发现明确缺口外，不重复读取同一批年报/竞争对手资料。

## 9.1 竞品选择按商业模式，而不是按“名字里有铀”

### 合并型/矿山生产商

优先：

- Kazatomprom；
- Cameco；
- Paladin；
- Boss Energy；
- 其他有可验证在产矿山的上市公司。

### 联营权益型

除上述矿商外，重点比较：

- 权益产量成本；
- 矿山 NAV/权益价值；
- 应占利润和现金分红转换率。

### 贸易平台型

没有完全可比公司时，不强行使用矿商 PE。重点比较：

- 毛利率；
- 单位价差；
- 库存周转；
- ROIC；
- 净现金；
- 母集团交易依赖度。

可使用中广核矿业贸易分部、中国铀业贸易分部做内部横向比较。

## 9.2 必算业务指标

### 资源/产量

- 权益产量；
- 权益产能；
- 储量寿命；
- 成本层级（low/mid/high；只有公开数据充分时才给更细排名）；
- 未来 5 年产量 CAGR；
- 每 1 元/港元市值对应权益产量；
- EV / attributable Mlb。

### 盈利

- 自产铀毛利率；
- 贸易毛利率；
- 净利率；
- ROE；
- ROIC；
- FCF margin；
- 现金利润转换率 `FCF / adjusted net profit`。

### 资产负债表

- 净现金/市值；
- 净债务/EBITDA；
- 库存/收入；
- 应收天数；
- 贸易营运资本/毛利。

### 估值

- PE；
- EV/EBITDA（仅会计口径可比时）；
- P/FCF；
- 股息率；
- P/NAV 或 EV/NAV；
- Market cap / attributable annual Mlb。

## 9.3 管理层和治理评分

### 加分项

- 长期稳定管理团队；
- 指引兑现率高；
- 大项目实际回报接近或超过收购/FID 时承诺；
- 分红/回购有明确框架；
- 高价周期不过度扩张、低价周期敢于投资；
- 收购价格合理；
- 管理层/董事长期持股（若制度允许）；
- 信息披露主动、分部数据清晰。

### 减分项

- 高价并购、低价减值；
- 反复增发稀释；
- 长期没有 FCF 却维持高会计利润；
- 大量“其他投资/其他应收/长期股权投资”缺乏解释；
- 关联交易集中而缺少清晰定价机制；
- 项目多次延期但不修正指引；
- 频繁更换审计师/管理层；
- 资产注入叙事长期存在但没有硬里程碑。

### 管理层承诺兑现率（强制）

根据 `06b_management_delivery.csv` 至少输出：

- `guidance_hit_rate`：已到期承诺中按期达到/基本达到比例；
- `median_project_delay_years`；
- `capex_overrun_pct`（可得时）；
- 重大承诺反复下修/延期次数；
- 管理层是否在失误后及时修改指引并解释。

没有量化指引时应写 `ND_NOT_REQUIRED/insufficient_guidance`，不能凭感觉给“高兑现率”。

### 必须量化的治理红旗

至少计算并解释：

- `top1_customer_revenue_pct`、`top5_customer_revenue_pct`；
- `top1_segment_revenue_pct`、`top1_asset_or_segment_profit_pct`（衡量单一收入/利润来源集中）；
- `related_party_revenue_pct`、`related_party_purchase_pct`；
- `non_core_investments / equity`；
- `other_receivables / equity`；
- `M&A + growth_capex` 与随后 3–5 年增量利润/FCF 的对应关系；
- `share_issuance - buyback` 对每股 EPS/FCF 的摊薄；
- 未充分披露投资、长期股权投资和其他非流动金融资产的规模。

“收入集中”本身不是直接负面。例如稳定的核燃料长期客户可能质量很高；真正的问题是**客户是否可替代、合同是否稳定、定价是否公平、关联方是否能转移利润**。

### 国企的特殊处理

央企高管因制度原因持股比例低，**不能机械以“持股少=差”扣分**。应提高以下权重：

- 任期稳定性；
- 资本配置结果；
- 对少数股东的现金回报；
- 关联交易公平性；
- 指引兑现和披露质量。

---

# Gate 2 — 经济引擎、护城河与管理层 Review

人工检查：

1. 能否用不超过 10 句话说清公司如何赚钱？
2. 是否已经识别 3–8 个真正驱动利润的企业变量？
3. 这些变量是否都能从公开来源定期更新？
4. 是否把战略地位和股东护城河分开？
5. 是否确定公司处于商品周期、经营困境、治理困境、估值消化或非困境？
6. 竞品是否与目标公司的商业模式真正可比？
7. 管理层评分是否有事实而不是印象？
8. 是否存在一个变量变化就足以推翻投资逻辑？

Gate 2 后锁定“核心企业变量”，写入 `11_monitoring_dashboard.csv`。

---

# 10. Phase 4 — 2025–2035 三情景经营预测

## 10.1 情景原则：只维护三套完整场景，不做无意义 3×3 组合爆炸

统一使用：

- `Bear / g0`
- `Base / g1`
- `Bull / g2`

每个场景同时包含：

1. 行业铀价/供需状态；
2. 公司自身产量、成本、项目执行；
3. 合同实现价滞后；
4. 资本开支与股东回报；
5. 估值倍数正常化。

不要出现“Base × g0/g1/g2”这种重复场景。

## 10.2 行业宏观参数：只读 `00_common_input_snapshot`

本阶段**禁止再写 Bear/Base/Bull 铀价区间**。所有年度 LT、Spot reference、需求、供应和库存状态直接读取冻结的：

```text
<company_name>_00_common_input_snapshot.csv
```

公司模型允许变化的只有：

- 合同重定价/lag；
- 公司产量、销量与项目延迟；
- 公司单位成本；
- 贸易量、价差/佣金和营运资金；
- CAPEX、税率、分红和估值倍数。

如果某公司 Agent 认为公共宏观路径不合理：

1. 不得只修改该公司；
2. 在 `12_checks` 标记 `COMMON_INPUT_REVIEW_REQUIRED`；
3. 若人工决定更新行业情景，则生成新 `common_input_version`；
4. 所有被比较公司同步重跑。

### Tail Stress

Tail Stress 仍只用于真实 Spot 暴露、库存风险或短期上行期权，不属于主 Bear/Base/Bull，不进入永续终值。

## 10.3 实现价模型

若有合同信息：

```text
realized_price =
fixed_contract_volume × fixed_price
+ market_related_volume × price_index_with_lag
+ spot_volume × spot_price
```

若无法获得合同细节：

1. 若历史实现价可得：用 `realized price / LT / Spot` 历史关系校准 lag/beta；
2. 若只披露部分合同覆盖：使用公开覆盖度 + Range；
3. 若实现价和合同覆盖都不可得：资产从 U1 降到 U2/U3，不强迫构造虚假 realized price；
4. 所有估计明确误差区间。

严禁假设实现价立即等于 Spot，也严禁为了 U1 完整性同时猜“合同覆盖率+实现价”。

## 10.4 产量模型

每个矿山：

```text
production = design_capacity
× ramp_factor
× operating_availability
× grade/recovery adjustment
```

权益产量：

```text
attributable_production = production × economic_ownership
```

对开发项目必须显式写：

- FID 年；
- 建设期；
- 首产年；
- 3–5 年爬坡曲线；
- Base/Bull/Bear 延期差。

## 10.5 成本模型

优先按矿山：

```text
cash_cost
+ royalty/tax
+ transport/processing
+ sustaining capex
= economic cost / AISC-like cost
```

只有披露充分的 U1 资产才要求完整单位成本桥；若单位成本不可得，应降级到 U2/U3，用分部毛利/利润率与可观察成本驱动做敏感性。

成本增长不能只用 CPI。需要视公司情况加入：

- 硫酸；
- 能源；
- 人工；
- 剥采比；
- 品位下降；
- 当地税费；
- 汇率。

## 10.6 贸易/代理业务模型

先按 C1/C2/C3/C4 分开预测。

### C1 Principal trading

```text
principal_volume
selling_price
purchase_price
spread_per_lb
gross_margin
inventory_days
working_capital
financing_cost
```

### C2 Agency service

```text
agency_volume
commission_per_lb 或 contract_commission
direct_service_cost
= agency_profit
```

### C3 Offtake/resale

先判断 principal/agent 会计身份，再归入 C1 或 C2；不建立第三套重复经济模型。

### C4 Inventory positioning

只有明确披露时预测库存持有损益；Base 默认不假设投机利润。

Bear 并不一定等于低铀价、Bull 也不一定等于贸易毛利率高。必须根据历史说明价差、佣金、交易活跃度、融资和营运资金如何随波动变化。

## 10.7 收入 → 净利润 → FCF 桥

每个场景逐年展示：

```text
生产/贸易量
→ 实现价/价差
→ 收入
→ 毛利
→ EBIT/应占联营利润
→ 税后归母净利润
→ CFO
→ 维持性+增长 CAPEX
→ FCF
→ 分红/回购
→ 每股 FCF/EPS
```

同时必须维护一个简化资本/现金滚动桥，避免回购只减股本却不减现金：

```text
ending_net_cash
≈ beginning_net_cash
+ accounting_FCF
- dividend_cash_paid
- buyback_cash
+ share_issuance_cash_proceeds
- M&A_cash
- other_material_cash_outflows
+ other_material_cash_inflows
```

若存在债务新增/偿还、受限现金变化或联营分红被放在投资现金流等情况，按实际现金流分类调整并记录。**分红和回购既影响未来净现金，也分别影响投资者现金流/股本，两个维度都要建模。**

## 10.8 三种公司的 FCF 特殊口径

### 中国铀业等合并型矿商

主口径：

```text
FCF = CFO - total capex
```

同时分出维持性和增长性 CAPEX，避免扩张期 FCF 低被误判为矿山质量差。

### 中广核矿业等权益法矿商

至少报告三套互不混算的口径：

```text
Accounting FCF = reported listed-company CFO - reported listed-company capex

Standalone ex-associate FCF
= 上市公司贸易/总部等独立经营现金流
- 上市公司自身 CAPEX
（必须排除联营/合营现金分配；若从 CFO 反推，先按现金流量表分类剔除 associate distributions）

Look-through FCF
= Standalone ex-associate FCF
+ attributable underlying mine FCF

Cash upstream ratio
= cash distributions actually received from associates / share of associate profit
```

关键规则：

- `Accounting FCF` 用于核对真实上市公司当期现金；
- `Look-through FCF` 用于观察底层经济创造；
- 两者**只比较/桥接，不相加**；
- 若 `standalone ex-associate FCF` 无法可靠拆出，Look-through FCF 标记 Range/低置信度，不得把 Accounting FCF 直接再加底层 mine FCF。

### 中核国际等贸易型公司

至少报告：

- reported CFO；
- working-capital-adjusted CFO；
- 3 年滚动 normalized FCF。

单年库存采购导致的 CFO 暴涨/暴跌不能直接作为永久 FCF。

## 10.9 2025–2030 必须逐年输出的“共同指标 + 路线指标”

### 所有公司/所有情景必须输出

- `common_input_version`、LT、参考 Spot；
- 收入、毛利（若会计披露允许）、归母净利润；
- reported CFO、CAPEX、Accounting FCF；
- 现金分红/每股分红、回购现金/回购股数、发行融资现金/新增股数、稀释股本；
- EPS、FCF/share；
- 净现金/净债务、可分配净现金（适用时）。

### 仅在对应模型路线可得时强制

- U1：权益产量、销量、实现价、单位成本；AISC 只有公司口径可比时才输出；
- U2：分部收入、分部毛利/利润率、关键运营驱动；
- U3：应占利润/利润代理、外部驱动弹性和敏感性；
- C1：principal volume、spread；
- C2：agency volume、commission；
- B 型：应占联营利润、cash upstream、Look-through FCF（可可靠重建时）；
- U4：项目阶段、概率、未来资本承诺和 option value。

**不存在的数据不是“预测出来就完整了”。** 对 ND_NOT_REQUIRED 直接留空并说明模型路线。

## 10.10 2031–2035 粗略预测

允许简化，但必须显式说明：

- 哪些矿山进入衰减；
- 哪些项目投产；
- 资源寿命是否需要再投资；
- 中周期铀价；
- 维持性 CAPEX；
- 税率；
- 长期正常化利润率。

不要把 2035 极端稀缺价格直接外推到永续期。

---

# Gate 3 — 预测假设人工 Review

人工必须查看 `08_scenario_assumptions.csv` 和 `09_forecast_2025_2035.csv`，并回答：

1. Bear 是否真的足够悲观，允许负增长、延期、成本上升？
2. Base 是否依赖多个同时成功的乐观假设？
3. Bull 是否包含可验证的产能和项目，而不是只抬铀价？
4. 实现价是否考虑长期合同滞后？
5. 贸易业务是否用价差模型而不是矿山模型？
6. 未 FID 项目是否错误进入 Base？
7. 2030 之后是否错误使用极端 Spot 作为终值？
8. 净利润、FCF、分红是否在资产负债表上可承受？
9. 股本变化和摊薄是否计入每股价值？
10. 所有公司是否读取同一 `common_input_version`，而没有私自改宏观价格？
11. 是否因表格存在 AISC/实现价/合同覆盖列，就对 U2/U3 业务强行补数？
12. 是否有 1–3 个变量对估值高度敏感，需要额外敏感性？

未通过时先修改假设，不进入估值。

---

# 11. Phase 5 — 多口径估值、11%资金成本与长期股东收益

## 11.1 核心原则

估值必须回答两个不同问题：

1. **今天公司内在价值大概是多少？**
2. **即使 2030 股价能到某个合理值，以今天价格买入后的年化回报是否 ≥11%？**

不能只给“2030目标价上涨多少”，却不考虑时间成本。

## 11.2 估值方法按公司类型选择

### A. 矿山型/一体化生产商

主方法：

1. **SOTP / Mine NAV**；
2. 归一化 PE；
3. FCF DCF / P-FCF；
4. EV/EBITDA 仅作交叉验证。

### B. 权益法矿山型

主方法：

1. **Look-through Mine NAV × 权益比例**；
2. 正常化应占利润 PE；
3. Look-through FCF DCF；
4. 可分配净现金/净债务净额（按同一口径，只加一次）。

### C. 贸易平台型

主方法：

1. **可分配净现金 + 正常化贸易利润资本化**；
2. 正常化 PE；
3. working-capital-adjusted FCF DCF；
4. 未成熟矿权单列 option value。

### D. 开发项目

使用项目 NPV/DCF × 权益 × 成功概率，且扣除未来需投入资本。

## 11.3 11%折现规则

统一资金成本：

```text
r = 11%
```

未来第 n 年公平价值折现到今天：

```text
PV(target_price_n) = target_price_n / (1.11)^n
```

期间分红：

```text
PV(dividends) = Σ dividend_t / (1.11)^t
```

因此对“持续持有同一股股份”的今天投资价值：

```text
PV_total
= PV(target_year_fair_value_per_share_using_target_year_diluted_shares)
+ PV(cash_dividends_per_share)
+ PV(other_direct_cash_distributions_per_share)
```

**开放市场回购不单独加 `net_buyback_effect`。** 回购/增发通过未来稀释股本、EPS/FCF per share 和目标年 fair value/share 体现；若又加一次回购收益就是 double count。只有真正直接发给该持股人的特殊现金分配才进入现金流。

### 11%要求回报率下的“合理买入价”

```text
max_entry_price_for_11pct = PV_total
```

若当前股价高于这个价格，则即使未来达到预测合理估值，投资的预期年化回报也低于 11%。

## 11.4 DCF/终值

矿山是有限寿命资产，优先使用矿山寿命 DCF，不要无限永续增长。

对持续经营的贸易/平台业务，可使用：

```text
Terminal Value = normalized_FCF_(t+1) / (11% - g)
```

默认长期 `g <= 2%`，且必须低于长期名义经济增长的合理水平。

周期矿业公司更优先使用中周期 FCF/倍数法作为终值交叉验证。

## 11.5 正常化 PE/FCF 倍数

不能拿当前高 PE 永续外推。

倍数选择依赖：

- 储量寿命；
- 成本曲线位置；
- 增长项目；
- 国别风险；
- 净现金；
- 现金回报；
- 利润质量；
- 可比公司历史周期区间。

Bear/Base/Bull 允许对应不同倍数，但 Bull 场景通常应考虑**高盈利伴随更低峰值 PE**，避免“双重乐观”（利润最高同时倍数最高）。

## 11.6 SOTP/NAV

至少拆：

```text
在产矿山 NAV
+ 已 FID 开发项目概率调整 NAV
+ 贸易平台价值
+ 其他可验证资产
+ 可分配净现金（若该指标已净除 debt，则不得再减净债务）
- 少数股东
- 尚未在可分配净现金中扣除的未来资本承诺
= Equity Value

或改用：`excess_cash - debt`。**两套现金/债务口径二选一，禁止同时使用。**
```

未成熟矿权：

```text
Base：低值或 0
Bull：概率调整 option value
```

## 11.7 不机械平均所有估值方法

每种估值方法先标记：

- `VALID`；
- `SECONDARY`；
- `INVALID`。

例如：

- 联营矿山型公司合并 EV/EBITDA 可比性差，可降为 SECONDARY；
- 贸易公司矿山 NAV 不适用，直接 INVALID。

最终合理价值区间以**最符合商业模式的主方法 + 至少两种有效交叉验证**为基础。不要因为“方法多”就把错误方法平均进去。

## 11.8 2026–2030 年度合理股价梯子（强制输出）

用户要求的不只是一个 2030 目标价。执行 Agent 必须对每个情景逐年计算：

```text
2026E fair value/share
2027E fair value/share
2028E fair value/share
2029E fair value/share
2030E fair value/share
```

每一年至少使用主估值方法，并用有效的交叉验证方法给出合理区间。`10_valuation.csv` 中必须存在：

```text
Bear/g0 × 2026–2030
Base/g1 × 2026–2030
Bull/g2 × 2026–2030
```

即至少 **15 个 scenario-year 估值节点**；每个节点可包含多种 method。

年度估值必须使用该年的：

- 实际预测 EPS/FCF；
- 该年净现金/净债务；
- 当年项目状态和剩余矿山寿命；
- 与周期位置一致的正常化倍数。

不能用“2030 目标价线性插值”代替 2026–2029 的独立估值。

2031–2035 可简化为 2033/2035 两个锚点或阶段区间。

## 11.9 股东总回报 TSR

对一个不参与出售、持续持有的普通股股东，现金流应写成：

```text
t0: -current_price
t1...tn-1: cash_dividend_per_share + other_direct_cash_distribution_per_share
tn: target_year_fair_value_per_share + 当年现金分配
```

其中 `target_year_fair_value_per_share` 必须使用目标年的**稀释后股本**。因此：

- 回购：`buyback_cash` 必须先减少未来净现金，同时通过股本下降影响每股指标和每股合理价值；不再额外加一笔收益；
- 增发/期权：发行融资现金进入净现金、股本上升进入稀释后每股价值；不再在 TSR 外重复扣一次；
- 若公司进行按比例供股且股东需额外出资，应把额外认购现金流显式加入 IRR，而不是忽略。

精确版本使用逐年现金流求 IRR；简化展示可使用累计股息，但主模型优先 IRR。

至少输出：

- 当前价；
- 2030 Bear/Base/Bull 合理股价；
- 2030 累计分红；
- 2030 年化 TSR；
- 2030 按 11%折现后的最大合理买入价；
- 2035 粗略年化 TSR；
- 相对于 11% hurdle 的超额回报。

## 11.10 反推当前价格隐含假设（强制）

在判断低估前，至少反推一种市场隐含条件：

- 当前市值需要多少正常化净利润/FCF 才能在合理倍数下成立；
- 对 U1/B 型公司，可进一步反推在既定产量/成本下需要怎样的 realized uranium price；
- 对贸易型公司，反推需要多少 principal spread / agency commission / normalized volume；
- 对开发项目，反推市场给了多少 option value。

该反推用于识别“好资产但价格已透支”与“低 PE 但盈利不可持续”两类常见陷阱。

## 11.11 “低估”定义

不得因为 PE 低就定义为低估。

建议分四档：

- **明显低估**：Base Case 11%折现价值比现价高 ≥25%，且 Bear 下资产负债表仍安全；
- **轻度低估**：Base Case 11%折现价值比现价高 10–25%；
- **合理**：±10%；
- **偏贵/明显高估**：现价高于 Base 11%折现价值 10%以上，或只有 Bull 才能达到 11%回报。

同时报告 Bear 的永久损失风险。

---

# Gate 4 — 估值与投资结论 Red Team

这是最后一个人工 Gate。

必须反向质疑：

1. 当前股价已经隐含什么铀价、产量和利润？
2. 把 Base 利润倒推到当前市值，市场实际上在要求什么？
3. 若 PE/EV 倍数回归中周期，即使利润增长，股价是否仍可能不涨？
4. Bear 是否会导致净债务或增发？
5. 分红是否真的由 FCF 支撑？
6. 未成熟项目是否贡献了过高估值？
7. 国企集团关系产生的价值，究竟归上市股东还是母集团？
8. 是否存在“利润对铀价弹性很高，但股票已经把弹性全部定价”的情况？
9. 是否存在“PE 很低，但利润本身不可持续”的价值陷阱？
10. 任何一个 P0 假设变化，是否会让评级从低估变为高估？

Gate 4 必须给：`PASS / CONDITIONAL PASS / FAIL` 和最多 5 个仍未解决的风险。

---

# 12. Phase 6 — 最终报告写法：简明、可读、没有废话

最终文件：

```text
<company_name>_uranium_investment_report.md
```

报告原则：

- 先结论，后证据；
- 每个复杂金融概念先用一句话解释；
- 观点必须从基础事实逐层推导；
- 不堆背景知识；
- 不重复同一数字；
- 不用模糊的“有望、赋能、空间广阔”代替量化判断；
- 对不可得数据明确写“不披露/只能区间估计”。
- 主报告原则上控制在 **8,000 个中文字以内（不含表格、来源索引和数据附件）**；重复的行业背景、财报数字和估值解释放到 Excel/CSV，不在正文反复出现。

## 12.1 建议最终目录

### 1. 一页结论

必须包括：

- 公司一句话业务本质；
- 3–5 个最重要优势；
- 3–5 个最重要风险；
- 当前是否困境；
- 当前是否低估；
- Base 2030 年化 TSR；
- 最重要的 5 个监控变量。

### 2. 公司究竟靠什么赚钱

用利润桥解释：

```text
铀价/价差
→ 产量/交易量
→ 收入
→ 利润
→ FCF
→ 股东拿到的现金
```

### 3. 国内外资产、营收和利润构成

至少三张表：

- 资产地图；
- 地域收入；
- 真正利润/权益产量来源。

### 4. 核心矿山/业务线

每个重大资产只写：

- 权益；
- 产量；
- 成本；
- 寿命；
- 项目节点；
- 价值贡献；
- 主要风险。

### 5. 行业供需、库存和铀价如何传导到公司

引用统一 Step6，不重复做行业长篇报告。

重点解释：

- 公司利润对 LT 还是 Spot 更敏感；
- 合同滞后；
- 贸易价差；
- 产量响应是否来得及。

### 6. 护城河和竞争对手

只保留能量化的比较。

输出：

- 护城河评分；
- 战略护城河；
- 股东护城河；
- 竞品成本/产量/估值表。

### 7. 为什么过去几年没有起色/是否困境反转

明确归因比例或主次顺序，不要把所有问题都归咎于“市场情绪”。

### 8. 管理层、资本配置和股东回报

展示 5 年：

- 分红；
- 回购；
- 增发；
- FCF；
- 并购/项目投入；
- 关联交易。

### 9. 2025A–2030E 三情景逐年预测

主表至少列：

```text
2025A, 2026E, 2027E, 2028E, 2029E, 2030E
```

每个场景列：

- 产量；
- 实现价；
- 收入；
- 净利润；
- FCF；
- 分红；
- EPS/FCF per share。

### 10. 2031–2035 粗略路径

重点解释：

- 2035 产量；
- 中周期铀价；
- 新项目贡献；
- 矿山衰退；
- 2035 正常化利润/FCF。

### 11. 多方法估值

至少展示：

- 主方法；
- 2 个交叉验证方法；
- **2026E–2030E 每一年** Bear/Base/Bull 合理股价范围；
- 2033E/2035E 远期估值锚；
- 当前估值隐含假设。

### 12. 投资回报

必须直接回答：

```text
今天以 P0 买入，
持有期间收到多少现金股息/直接现金分配，
回购/增发后目标年股本是多少，
2030 合理每股价值是多少，
逐年现金流 IRR/年化收益率是多少，
是否超过 11%。
```

### 13. 什么会推翻结论

列 3–8 个可验证证伪条件。

### 14. 季度/半年监控表

只保留最重要变量，不超过 15 项。

---

# 13. 各公司的默认“核心变量卡”

## 13.1 中国铀业

季度/半年 Dashboard 默认优先级：

|优先级|变量|原因|
|---|---|---|
|P0|自产天然铀销量/收入/毛利率|利润质量最高的核心业务|
|P0|Rössing 产量|海外主要可量化矿山|
|P0|Rössing 可披露单位成本（cash cost/AISC-like；保存 cost_definition）|决定铀价上涨转化成利润的比例；AISC不可得时不强求|
|P0|实现铀价/合同结构|不能直接使用 Spot|
|P0|Etango FID/建设/首产节点|未来主要增量期权|
|P0|外购转售毛利率|大收入但利润质量不同|
|P0|国际贸易毛利率|识别低毛利收入放大|
|P0|CFO/FCF/资本开支|判断利润能否成为股东现金|
|P1|国内新矿项目/资源量|决定长期增长|
|P1|关联交易占比/定价|判断战略优势是否归股东|
|P1|分红/回购/增发|长期 TSR|

## 13.2 中广核矿业

|优先级|变量|原因|
|---|---|---|
|P0|各哈萨克矿山总产量及权益产量|核心经济暴露|
|P0|矿山单位成本（保存 cost_definition）|决定资源租金；仅在定义一致时比较 AISC|
|P0|应占联营利润|会计盈利核心|
|P0|联营分红回款|利润变现金的关键|
|P0|矿山储量寿命/扩产|决定 NAV|
|P0|LT/公司实现价|利润弹性|
|P0|哈萨克税/生产纪律|外生风险|
|P0|贸易销量与毛利|合并收入大但需单独分析|
|P1|KZT/USD/HKD|成本及利润折算|
|P1|净现金/分红率|股东回报|

## 13.3 中核国际

|优先级|变量|原因|
|---|---|---|
|P0|principal 自营量 + agency 代理量|必须区分商品买断与代理服务|
|P0|principal 单位价差 + agency 单位佣金|比铀价本身更决定利润，避免代理业务错算|
|P0|库存天数/库存成本|价格波动风险|
|P0|应收/预付/应付|营运资金风险|
|P0|reported + adjusted CFO|识别库存采购造成的假波动|
|P0|净现金/市值|估值安全垫|
|P0|关联方收入和采购比例|平台依赖与定价风险|
|P0|矿权硬里程碑|期权是否进入可估值阶段|
|P1|管理层变动|平台稳定性|
|P1|分红/回购/增发|少数股东回报|

---

# 14. 行业与公司监控变量的分层

为了避免重复，每次季度回归分为两层。

## 14.1 全行业只更新一次

- LT uranium price；
- Spot/LT basis；
- utility inventory；
- unfilled requirements / contracting；
- Step6 关键 pre-FID 项目；
- frontier 项目 FID；
- demand path；
- secondary supply；
- seller-scarcity / inventory stress。

若同时分析中国铀业、中广核矿业、中核国际，**行业表只更新一次，再分别映射到三家公司。** 同一批次还应固定公共 Peer 的 `as_of_date`、市场价/市值和最新运营期，避免一家公司用半年报、一家公司用次年年报。

## 14.2 单家公司只更新自身暴露

例如 LT 上涨 10 USD/lb 后：

- 中国铀业：多少自产/合同销量能重定价？
- 中广核矿业：权益矿山利润增加多少，多久反映到联营利润和现金分红？
- 中核国际：采购和销售合同价差如何变化，库存周转是否变差？

这样可以避免“同一个铀价变化在三家公司模型中被重复用不同逻辑解释”。

---

# 15. 必须运行的敏感性

至少对以下变量做单因素或局部二维敏感性：

## 所有矿商

- LT uranium price ±10 / ±20 USD/lb；
- 产量 ±10%；
- 单位成本 ±10%（使用公司实际 `cost_definition`；AISC 不可得时不强制）；
- 项目延迟 1/2 年；
- 正常化估值倍数；
- 11%折现率可额外显示 9%/13%作为敏感性，但主结论必须保持 11%。

## 贸易公司

- 贸易量 ±20%；
- 单位毛利/毛利率 ±20%；
- 库存天数 ±30%；
- 采购与销售价格错配；
- 融资成本 +200bp。

## 中广核矿业等权益法公司

- 联营分红支付率；
- 哈萨克税费；
- KZT；
- 权益产量；
- 关联/包销条款。

## 中国铀业等披露不足公司

- 国内自产产量 low/base/high；
- 国内成本 low/base/high；
- Rössing 产量和 AISC；
- Etango 延期 0/1/2 年。

---

# 16. 最终质量控制 Checks

`<company_name>_12_checks.csv` 至少执行以下测试。

## P0 算术/单位

- Revenue 分部合计≈总收入；
- 归母利润桥能解释总利润；
- tU ↔ lb U3O8 换算正确；
- 权益产量=总产量×权益比例；
- 稀释股本与 EPS 一致；
- FCF=CFO-CAPEX（主口径）；
- Net cash=Cash-Debt；
- 估值总权益/股本=每股价值。

## P0 会计

- 联营产量没有错误计入合并收入；
- 联营利润与实际分红没有混为同一现金流；
- Look-through FCF 未把已经包含联营分配的上市公司现金流与底层矿山 FCF 重复相加；
- 贸易库存变化没有同时重复计入利润和现金流；
- 少数股东处理正确。

## P0 情景

- Step6 2026-real 价格与公司名义财务预测没有混用；名义转换使用同一 Common inflation path；
- Bear/Base/Bull 价格、产量、成本逻辑方向一致；
- 未 FID 项目未错误进入 Base；
- Bull 没有同时使用极端利润和极端高 PE；
- 2035 tail Spot 未进入永续终值。

## P1 数据质量

- `common_input_version` 已记录；用于横向比较时各公司一致；
- 每个派生字段都能追溯到 `00_data_lineage` 指定的 Canonical 表；
- Dashboard/估值表没有手工重录与 Canonical 冲突的历史数字；
- 每个关键数字有 source_id；
- C/D 级估计均有区间；
- 不可得字段没有被悄悄填 0；
- 财报口径变更已重述或标记。

## P1 投资收益

- 分红/回购/增发/M&A 已进入净现金 roll-forward；回购没有出现“只减股本不减现金”；
- 2030/2035 TSR 计入现金分红，并使用目标年稀释股本；开放市场回购没有被额外重复加收益；
- 11%折现正确；
- 当前股价日期明确；
- 目标价使用的是目标年股本，而不是当前股本（如存在显著摊薄）。

---

# 17. Agent 分步执行指令模板

用户可直接把本文件与公司名称、Step6 数据包一起交给网页版 ChatGPT，并使用以下命令推进。

## 第一次

```text
使用本调研框架分析 <company_name>。
先执行 Phase 0 和 Phase 1。若我提供了已有 common input snapshot，必须原样复用；若这是本批次第一家公司且没有 common snapshot，则按框架的确定性回退规则生成一个并冻结，后续公司必须复用同一版本。
完成后运行 Gate 1，自行检查所有 P0 问题并输出 PASS/CONDITIONAL PASS/FAIL。
本阶段不要提前做估值。
所有中间数据按框架写入 CSV；不要频繁直接编辑 Excel。
```

## Gate 1 后

```text
根据现有数据 review Phase 2–3 的执行计划。
Phase 2 只做一次外部 Peer/竞争数据采集并冻结 07_peer_comparison；Phase 3 必须复用已有输入，不要重复搜索。
检查所有缺失字段是否有 U1/U2/U3/U4 或 C1/C2/C3/C4 降级路线。
修正后直接执行并完成 Gate 2。
```

## Gate 2 后

```text
根据现有数据 review Phase 4 的预测计划。
先确认 00_common_input_snapshot 已冻结，禁止自行改 Bear/Base/Bull 宏观路径；特别检查合同实现价滞后、贸易/代理身份、未 FID 项目和模型降级路线。
修正后直接执行，完成 Gate 3。
```

## Gate 3 后

```text
执行 Phase 5 估值。
资金成本固定 11%。
使用与公司商业模式相符的主估值方法和至少两种交叉验证，不机械平均无效方法。
计算当前价格到 2030/2035 的逐年现金流 IRR/含分红 TSR；回购/增发通过目标年稀释股本体现，不得 double count。完成 Gate 4 Red Team。
```

## Gate 4 后

```text
执行 Phase 6。
批量生成最终 Excel 和全部 CSV，不要逐单元格编辑 Excel。
生成简明易懂的最终 Markdown 报告。
检查文件名全部符合 <company_name>_<custom_name>.<ext>。
最后提供完整文件清单和主要结论。
```

---

# 18. 最终交付清单

至少交付：

```text
<company_name>_00_manifest.csv
<company_name>_00_common_input_snapshot.csv
<company_name>_00_data_lineage.csv
<company_name>_01_sources.csv
<company_name>_01b_field_provenance.csv
<company_name>_02_business_segments.csv
<company_name>_03_asset_master.csv
<company_name>_04_operating_history.csv
<company_name>_05_financial_history.csv
<company_name>_06_capital_allocation_governance.csv
<company_name>_06b_management_delivery.csv
<company_name>_07_peer_comparison.csv
<company_name>_08_scenario_assumptions.csv
<company_name>_09_forecast_2025_2035.csv
<company_name>_10_valuation.csv
<company_name>_11_monitoring_dashboard.csv
<company_name>_12_checks.csv
<company_name>_uranium_investment_model.xlsx
<company_name>_uranium_investment_report.md
```

可选：

```text
<company_name>_mine_NAV_detail.csv
<company_name>_trade_working_capital_detail.csv
<company_name>_valuation_sensitivity.csv
```

仅在确实需要时增加，避免文件碎片化。

---

# 19. 最终报告应达到的判断标准

一个合格研究包应当允许第三方在不重新阅读所有年报的情况下：

1. 从 `01_sources` 找到每个关键数字原始出处；
2. 从 `03_asset_master` 理解公司到底拥有哪些铀资产；
3. 从 `04/05` 重建历史生产、利润和 FCF；
4. 从 `00_common_input_snapshot` 确认各公司使用同一宏观世界，并从 `08` 看懂公司特异参数为什么这样设；
5. 从 `09` 重新计算 2025–2035 业务预测；
6. 从 `10` 复算每一种估值和 11%折现后的合理买入价；
7. 从 `11` 知道下季度最值得更新什么；
8. 从 `12` 确认单位、会计、公式和估值没有明显硬错误。

如果做不到上述任一项，研究还不能算“可审计完成”。

---

# 20. 三家重点公司的默认数据可得性/模型路线

这是执行起点，不是永久事实；每次研究仍需用最新披露确认。

| 数据/模块 | 中国铀业 | 中广核矿业 | 中核国际 | 默认 Route |
|---|---|---|---|---|
| 合并财务/分部收入 | 高 | 高 | 高 | 直接 |
| 国内矿山单位产量/成本 | 低/存在披露限制 | N/A | N/A | 中国铀业 U2/U3 |
| 海外矿山产量 | 中高 | 高 | 无稳定在产核心矿 | U1/U2 |
| 单位成本/AISC | 部分 | 较高但需统一定义 | N/A | 有则 U1，无则降级 |
| 实现铀价/合同覆盖 | 部分 | 部分 | 部分 | historical calibration / Range |
| sustaining CAPEX | 常不完整 | 常不完整 | N/A | total CAPEX + Range |
| 联营应占利润/现金分红 | N/A/少 | 核心且较可得 | N/A | B 型三层口径 |
| principal 贸易量 | 部分 | 较可得 | 较可得 | C1 |
| agency 代理量/佣金 | 视披露 | 视披露 | 重要且需单列 | C2 |
| 公司库存实物量 | 常不完整 | 部分 | 常不完整 | 金额/天数，不强制 lb |
| 未成熟矿权 | Etango等按阶段 | 新项目按阶段 | 蒙古/尼日尔等 | U4 option |
| 精确全球成本 percentile | 不依赖 | 不依赖 | 不依赖 | low/mid/high bucket |

若实际披露优于/差于本表，按 Gate 1 更新 route；**框架不会因为某字段不可得而要求 Agent 猜数。**

默认资产/业务路线示例：

```text
中国铀业
├─ 国内自产铀：U2_SEGMENT → 数据更充分时升级 U1
├─ Rössing：U1_UNIT / U2_SEGMENT（按当期披露）
├─ 外购转售/国际贸易：C1 或 C3
└─ 开发项目：U4_OPTION_ND → FID/融资/建设跨里程碑后逐步升级

中广核矿业
├─ 哈萨克权益矿山：B 型会计框架 + U1_UNIT look-through
├─ 联营现金上划：独立 cash-upstream bridge
└─ 贸易/offtake：C1/C3

中核国际
├─ 自营天然铀贸易：C1
├─ 采购/销售代理：C2
├─ offtake：先判 principal/agent 后归 C1/C2
└─ 蒙古/尼日尔等非稳产资产：U4_OPTION_ND
```

---

# 21. 框架的核心思想

对铀业公司，最容易出现的错误是看到“铀价上涨”就直接推导“收入上涨→利润上涨→股价上涨”。正确链条应该是：

```text
全球需求/供应/库存
→ LT/Spot 所处状态
→ 公司合同与可重定价销量
→ 公司实际实现价/贸易价差
→ 矿山产量与单位成本
→ 业务分部利润
→ 净利润
→ FCF
→ 分红/回购/再投资与股本变化
→ 每股价值（回购效应已在股本中体现）
→ 估值倍数回归
→ 以当前价格买入后的实际年化 TSR
```

三家公司真正的差别也体现在这条链条的不同位置：

- **中国铀业**主要研究“资源和产量增长能否兑现、低成本资源租金能否留在上市公司，以及高估值是否提前透支未来”；
- **中广核矿业**主要研究“哈萨克低成本权益产量、铀价与联营利润/现金回流的杠杆”；
- **中核国际**主要研究“贸易价差、营运资本和净现金安全垫，以及资源/资产注入期权何时真正跨过可估值里程碑”。

因此，本框架最终不是为了找“哪家公司 PE 最低”，而是为了找到：

> **哪家公司拥有最可持续的资源租金或供应链现金流，当前价格又没有提前支付过多未来乐观情景，并且按 11%资金成本仍能给普通股股东留下足够安全边际。**


---

## V1.1 执行验收底线

若一个最终研究包同时满足以下条件，才可与其他公司横向排序：

1. `common_input_version` 完全一致；
2. 没有未处理的 `ND_BLOCKING`；
3. 每个资产/分部有明确 `model_route`；
4. 贸易 principal/agency 身份已拆分；
5. Look-through FCF 与联营现金分配无 double count；
6. TSR 中回购/增发无 double count；
7. 预测/估值/Dashboard 均能追溯 Canonical Source；P0与非DIRECT字段能追溯 `01b_field_provenance`；
8. 2026–2030 每年 Bear/Base/Bull 均独立估值，2031–2035 有远期锚；
9. 当前价格隐含假设已反推；
10. 主报告可以在不查看隐藏 Excel 公式的情况下解释结论，CSV/Excel 可以让第三方复算。
