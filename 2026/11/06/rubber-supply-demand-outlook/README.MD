# 橡胶供需附件：口径、来源与字段

数据截止2026年11月6日。本目录是《橡胶供需：天然胶高位还能维持多久，合成胶要分牌号看》的配套数据，只含结构化公开数据与说明，不含第三方全文、缓存或研究过程文件。

## 文件

| 文件 | 内容 |
| --- | --- |
| `rubber-price-monthly.csv` | TSR20与RSS3近月期货月均，1999-01至2026-10；含名义价与同月CPI折算的实际价 |
| `rubber-balance-annual.csv` | 全球与地区年度产量、加工消费、差额；含历史、外部预测与三档条件 |
| `rubber-inventory-snapshot.csv` | 库存点估计，含口径、时点与包含关系 |
| `rubber-sr-history.csv` | 合成胶全球与中国同版历史产量与消费，2020—2024 |

## 单位与状态

- 数量：年度表为千吨干胶（`production_kt`、`consumption_kt`）；价格表为美元/千克；库存表为吨。
- `data_status`：`historical_estimate`为已披露历史或含估计；`external_forecast`为外部年度预测；`author_condition`、`resource_condition_extension`为本文净增长条件；`same_version_derived`为同版残差。
- 实际价格用同月美国CPI折至2026年9月，`real_base_period=2026-09`。10月CPI未发布，10月实际价留空，不前填。
- 差额正负号：`production_minus_consumption_kt`为产量减加工消费，负值表示产量低于消费。它不是未满足订单，也不是库存变化。

## 主要口径

年度差额按 `期末库存 = 期初库存 + 产量 + 净进口 − 加工消费 − 损耗` 定义。全球可动员库存与连续库存序列未取得，因此不输出库存消费比、库存天数或耗尽月份。地区差额（中国、中国以外）可通过净贸易和库存调节，不是地区断供量。

2023—2025年全球历史来自较早的完整地区表（`CATAS_2025_12`）；2026年起为最新全球快照（`ANRPC_2026_09_latest_global`），两版不可拼成无修订序列。两版2026年产量差28.8万吨、消费差19.4万吨，差额差9.4万吨。同版具名产胶国覆盖2025年77.4%、2026年75.9%，其余为“其他”聚合项。

合成胶历史只到2024年同版（`KPK_2024_IRSG`），2022年同版两表冲突未采用，因此年度序列缺2022年。中国原表未明确港澳台边界，中国以外为同版残差。

## 条件设定

净年增长率按三档命名条件设置，预测年内固定，不按年、按国暗配：

| 净年增长条件 | 偏紧 bull | 参照 base | 宽松 bear |
| --- | ---: | ---: | ---: |
| 天然胶全球/中国以外有效供给 | -0.5% | 1.5% | 3.0% |
| 天然胶全球/中国以外加工需求 | 2.5% | 1.5% | 0.0% |
| 天然胶中国有效供给 | -2.0% | 0.0% | 1.0% |
| 天然胶中国加工需求 | 3.0% | 1.5% | 0.0% |

三档不是概率区间，也不是统计识别的最可能路径。高价反馈另设两个命名压力：有效供给年增速额外加1个百分点，或需求年增速减少1个百分点；幅度是量级实验，不是估计价格弹性。

## 来源

- 世界银行月度价格（2026年11月版）：https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx
- 世界银行年度预测（2026年10月）：https://thedocs.worldbank.org/en/doc/2ac43f46629cf90c2ea5b8929a343593-0050012026/related/CMO-October-2026-Forecasts.pdf
- 美国CPI（BLS经FRED）：https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL
- 全球天然胶最新快照（2026年9月）：https://www.anrpc.org/newsla/anrpc-releases-monthly-nr-statistical-report-september-2026
- 完整地区表（2026年4月）：https://www.catasrri.cn/contents/3634/218919.html
- 完整地区表（2025年12月，历史）：https://www.catasrri.cn/contents/3634/217826.html
- 合成胶同版历史（2024版）：https://www.kpk.gov.my/agro-commodity-statistics/2/download
- 上海期货交易所周库存：https://www.shfe.com.cn/data/tradedata/future/stockdata/weeklystock_20261106/ZH/all.html
- 马来西亚月度橡胶统计（2026年8月）：https://www.dosm.gov.my/uploads/release-content/file_20261012100459.pdf
- 科特迪瓦干胶产量：https://www.economie-ivoirienne.ci/activites-sectorielles/agriculture-industrielle-et-dexportation.html
- 印度天然胶年度趋势：https://rubberboard.gov.in/rbfilereader?fileid=1289

## 复算提示

图表数字由上述原始序列按文中公式换算与舍入得到，正文与CSV保留到与输入质量相称的精度。CSV多位小数用于核对，不代表相同预测精度。若修改输入，需同步检查差额恒等式、分项加总与情景年份。
