"""Build the downloadable appendix tables for the offshore wind foundation article.

Usage:
    python3 build-appendix.py --research <研究包目录> --out <文章资源目录>

`--research` 指包含 `facts/`、`params/` 与 `results/` 的研究包根目录，`--out` 是文章的
同名资源目录。两者默认都是当前目录；研究包与资源目录不同时必须显式传入。
脚本只读研究包，不修改任何研究文件。
"""

import argparse
import csv
import os
import zipfile

RESEARCH = "."
OUT = "."

COMPANIES = [
    ("issuer:大金重工_002487", "大金重工"),
    ("issuer:天顺风能_002531", "天顺风能"),
    ("issuer:海力风电_301155", "海力风电"),
    ("issuer:泰胜风能_300129", "泰胜风能"),
    ("issuer:中船防务_600685", "中船防务"),
    ("issuer:中国船舶_600150", "中国船舶"),
]

SECURITIES = [
    ("security:大金重工A_002487.SZ", "大金重工A", "CNY"),
    ("security:大金重工H_01081.HK", "大金重工H", "HKD"),
    ("security:天顺风能A_002531.SZ", "天顺风能A", "CNY"),
    ("security:海力风电A_301155.SZ", "海力风电A", "CNY"),
    ("security:泰胜风能A_300129.SZ", "泰胜风能A", "CNY"),
    ("security:中船防务A_600685.SH", "中船防务A", "CNY"),
    ("security:中船防务H_00317.HK", "中船防务H", "HKD"),
    ("security:中国船舶A_600150.SH", "中国船舶A", "CNY"),
]

# 十四个具名条件：中文名、结果目录。前十二个进入 2029 年利润比较表，
# 汇率与税收两项只改变投资者收益口径，不改变企业经营利润，单独登记。
SCENARIOS = [
    ("需求弱／执行较差", "industry_bear", True),
    ("基准条件", "industry_base", True),
    ("需求强／执行较好", "industry_bull", True),
    ("欧洲本土竞争", "eu_local_ramp", True),
    ("贸易准入成本", "trade_access", True),
    ("单桩份额18.5%", "share_to_185", True),
    ("新船价及续单回落", "ship_price_down", True),
    ("现有船单不续签", "ship_no_replacement", True),
    ("其他市场获单", "new_market_win", True),
    ("组合低谷", "combined_downcycle", True),
    ("船单未确认比例50%", "ship_backlog_low", True),
    ("船单未确认比例85%", "ship_backlog_high", True),
    ("港币贬值压力", "hkd_depreciation", False),
    ("港股资本利得税假设", "hk_tax_expiry", False),
]

SEGMENT_NAMES = {
    "wind_equipment": "风电装备及交付",
    "shipbuilding": "造船及相关业务",
    "power": "发电",
    "other": "其他业务",
    "associate": "联营收益",
}


def read(path):
    with open(os.path.join(RESEARCH, path), encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"  {name}: {len(rows)} 行")


def num(value, scale=1.0, digits=4):
    """空值保持空字符串，不填零。"""
    if value is None or value == "":
        return ""
    return round(float(value) / scale, digits)


def name_of(entity_id):
    for key, label in COMPANIES:
        if key == entity_id:
            return label
    return entity_id


def build_history():
    rows = []
    for record in read("results/industry_base/peer_financial_comparison.csv"):
        if record["segment"] != "consolidated":
            continue
        rows.append([
            record["entity_id"],
            name_of(record["entity_id"]),
            record["period"],
            num(record["revenue_cny_m"]),
            num(record["net_profit_cny_m"]),
            num(record["gross_margin"], digits=6),
            num(record["fcf_cny_m"]),
            record["scope"],
            record["source_ids"],
        ])
    write("six-companies-history.csv",
          ["entity_id", "company", "period", "revenue_cny_m", "net_profit_cny_m",
           "gross_margin", "cfo_minus_capex_cny_m", "scope", "source_ids"],
          rows)


def build_forecast():
    rows = []
    for record in read("results/industry_base/industry_profit_cash_total.csv"):
        if record["scenario"] != "industry_base":
            continue
        rows.append([
            record["entity_id"],
            name_of(record["entity_id"]),
            record["period"],
            num(record["revenue"]),
            num(record["net_profit"]),
            num(record["fcfe_parent"]),
            num(record["operating_cash_flow"]),
            num(record["capex_cash"]),
            num(record["depreciation"]),
            num(record["bank_debt_end"]),
            num(record["parent_equity"]),
            num(record["eps"], digits=4),
            num(record["roe"], digits=6),
        ])
    rows.sort(key=lambda row: (row[1], row[2]))
    write("six-companies-forecast-base.csv",
          ["entity_id", "company", "period", "revenue_cny_m", "net_profit_cny_m",
           "fcfe_parent_cny_m", "operating_cash_flow_cny_m", "capex_cash_cny_m",
           "depreciation_cny_m", "bank_debt_end_cny_m", "parent_equity_cny_m",
           "eps_cny", "roe"],
          rows)


def build_segments():
    rows = []
    for record in read("results/industry_base/industry_profit_cash_segments.csv"):
        if record["scenario"] != "industry_base" or record["period"] != "2029":
            continue
        rows.append([
            record["entity_id"],
            name_of(record["entity_id"]),
            record["segment_id"],
            SEGMENT_NAMES.get(record["segment_id"], record["segment_id"]),
            num(record["revenue"]),
            num(record["parent_net_profit"]),
            num(record["economic_parent_fcfe"]),
            num(record["depreciation"]),
        ])
    order = dict((label, index) for index, (_, label) in enumerate(COMPANIES))
    rows.sort(key=lambda row: (order.get(row[1], 99), -(float(row[4]) if row[4] else 0)))
    write("six-companies-segments-2029.csv",
          ["entity_id", "company", "segment_id", "segment", "revenue_cny_m",
           "parent_net_profit_cny_m", "economic_parent_fcfe_cny_m",
           "depreciation_cny_m"],
          rows)


def build_security_table():
    rows = []
    for record in read("results/industry_base/current_value_summary.csv"):
        currency = dict((key, cur) for key, _, cur in SECURITIES).get(record["entity_id"], "")
        rows.append([
            record["entity_id"],
            record["scenario"],
            record["price_date"],
            record["target_year"],
            currency,
            num(record["market_price"], digits=4),
            num(record["fair_current"], digits=4),
            num(record["target_price"], digits=4),
            num(record["buy_15"], digits=4),
            num(record["buy_20"], digits=4),
            num(record["market_xirr"], digits=6),
        ])
    write("security-valuation-and-buy-prices.csv",
          ["entity_id", "scenario", "price_date", "target_year", "currency",
           "market_price", "fair_current", "target_price", "buy_15", "buy_20",
           "market_xirr"],
          rows)


def build_method_table():
    prices = {}
    for record in read("results/industry_base/valuation.csv"):
        if record["scenario"] != "industry_base":
            continue
        prices[(record["entity_id"], record["target_year"], record["method"])] = record["price"]
    rows = []
    for record in read("results/industry_base/buy_prices.csv"):
        if record["scenario"] != "industry_base" or record["target_year"] != "2029":
            continue
        buy = float(record["buy_price"]) if record["buy_price"] else ""
        key = (record["entity_id"], record["target_year"], record["method"])
        rows.append([
            record["entity_id"],
            record["target_year"],
            record["method"],
            record["required_return"],
            num(prices.get(key)),
            num(buy, digits=4),
        ])
    write("valuation-by-method-2029.csv",
          ["entity_id", "target_year", "method", "required_return",
           "price", "buy_price"],
          rows)


def build_scenario_matrix():
    matrix = {}
    for label, folder, _ in SCENARIOS:
        path = f"results/{folder}/industry_profit_cash_total.csv"
        if not os.path.exists(os.path.join(RESEARCH, path)):
            continue
        for record in read(path):
            if record["period"] != "2029" or record["scenario"] != folder:
                continue
            matrix.setdefault(folder, {})[record["entity_id"]] = record["net_profit"]
    rows = []
    for label, folder, enterprise in SCENARIOS:
        if folder not in matrix:
            continue
        row = [label, folder, "企业经营条件" if enterprise else "投资者口径压力"]
        for key, _ in COMPANIES:
            row.append(num(matrix[folder].get(key)))
        rows.append(row)
    write("scenario-matrix-2029.csv",
          ["scenario", "scenario_id", "type"] + [label for _, label in COMPANIES],
          rows)


def build_scenario_valuation():
    rows = []
    for label, folder, _ in SCENARIOS:
        path = f"results/{folder}/current_value_summary.csv"
        if not os.path.exists(os.path.join(RESEARCH, path)):
            continue
        for record in read(path):
            rows.append([
                label,
                folder,
                record["entity_id"],
                num(record["market_price"], digits=4),
                num(record["fair_current"], digits=4),
                num(record["target_price"], digits=4),
                num(record["buy_15"], digits=4),
                num(record["buy_20"], digits=4),
                num(record["market_xirr"], digits=6),
            ])
    write("scenario-valuation.csv",
          ["scenario", "scenario_id", "entity_id", "market_price", "fair_current",
           "target_price", "buy_15", "buy_20", "market_xirr"],
          rows)


def build_europe_market():
    market = {}
    for tag in ("bear", "base", "bull"):
        for record in read(f"results/europe_supply_{tag}/europe_monopile_market.csv"):
            entry = market.setdefault(record["year"], {})
            entry[tag] = record["market_eur_m"]
            entry["grid_year"] = record["reference_connection_year"]
            entry["grid_mw"] = record["reference_offshore_mw"]
            if tag == "base":
                entry["demand_tonnes"] = record["demand_tonnes"]
    supply = {}
    for record in read("results/europe_supply_base/supply_demand.csv"):
        if record["region"] != "covered_pool" or record["product"] != "单桩":
            continue
        supply[record["year"]] = record
    rows = []
    for year in sorted(market):
        entry = market[year]
        pool = supply.get(year, {})
        rows.append([
            year,
            entry.get("grid_year", ""),
            num(entry.get("grid_mw"), digits=1),
            num(entry.get("bear"), digits=2),
            num(entry.get("base"), digits=2),
            num(entry.get("bull"), digits=2),
            num(entry.get("demand_tonnes"), digits=0),
            num(pool.get("conditional_available_tonnes"), digits=0),
            num(pool.get("nominal_covered_tpy"), digits=0),
            num(pool.get("conditional_coverage_ratio"), digits=4),
        ])
    write("europe-monopile-market.csv",
          ["supply_year", "reference_grid_year", "reference_offshore_mw",
           "market_bear_eur_m", "market_base_eur_m", "market_bull_eur_m",
           "base_demand_tonnes", "conditional_supply_tonnes", "nominal_covered_tpy",
           "coverage_ratio"],
          rows)


def build_unit_costs():
    rows = []
    for record in read("results/europe_supply_base/europe_supply_costs.csv"):
        rows.append([
            record["region"],
            num(record["manufacturing_usd_t"], digits=0),
            num(record["landed_quote_usd_t"], digits=0),
            num(record["manufacturing_eur_t"], digits=0),
            num(record["landed_quote_eur_t"], digits=0),
            num(record["manufacturing_advantage_fraction"], digits=6),
            num(record["quote_advantage_fraction"], digits=6),
            record["scope"],
        ])
    write("unit-costs-monopile.csv",
          ["region", "manufacturing_usd_t", "landed_quote_usd_t", "manufacturing_eur_t",
           "landed_quote_eur_t", "manufacturing_advantage_fraction",
           "quote_advantage_fraction", "scope"],
          rows)


def build_dajin_bridge():
    bridge = {}
    for record in read("results/industry_base/wind_revenue_bridge.csv"):
        if record["entity_id"] != "issuer:大金重工_002487":
            continue
        bridge.setdefault(record["period"], {})[record["component"]] = record["revenue"]
    totals = {}
    for record in read("results/industry_base/industry_profit_cash_total.csv"):
        if record["scenario"] != "industry_base" or record["entity_id"] != "issuer:大金重工_002487":
            continue
        totals[record["period"]] = record
    rows = []
    for period in sorted(bridge):
        entry = bridge[period]
        total = totals.get(period, {})
        wind_parts = [entry.get(key) for key in
                      ("europe_mp", "europe_tp", "dap_transport", "other_wind")]
        wind_total = sum(float(part) for part in wind_parts if part)
        basis = "2026H2为半年口径，其余为全年口径" if period.endswith("H2") else "全年口径"
        rows.append([
            period,
            num(entry.get("europe_mp")),
            num(entry.get("europe_tp")),
            num(entry.get("dap_transport")),
            num(entry.get("other_wind")),
            num(wind_total),
            num(total.get("revenue")) if total else "",
            num(total.get("net_profit")) if total else "",
            basis,
        ])
    write("dajin-revenue-bridge.csv",
          ["period", "europe_monopile_cny_m", "europe_tp_cny_m", "dap_transport_cny_m",
           "other_wind_cny_m", "wind_equipment_total_cny_m", "revenue_total_cny_m",
           "parent_net_profit_cny_m", "basis"],
          rows)


def build_dajin_share():
    rows = []
    for record in read("results/industry_base/wind_share_matrix.csv"):
        rows.append([
            record["demand_case"],
            record["share_path"],
            record["period"],
            num(record["market_value_cny_m"]),
            num(record["effective_value_share"], digits=6),
            num(record["monopile_revenue"]),
            num(record["other_wind_revenue"]),
            num(record["total_revenue"]),
            num(record["net_profit"]),
            num(record["fcfe_parent"]),
        ])
    rows.sort(key=lambda row: (row[2], row[0], row[1]))
    write("dajin-demand-share-matrix.csv",
          ["demand_case", "share_path", "period", "market_value_cny_m",
           "effective_value_share", "monopile_revenue_cny_m",
           "other_wind_revenue_cny_m", "revenue_total_cny_m",
           "parent_net_profit_cny_m", "fcfe_parent_cny_m"],
          rows)


def build_ship_orders():
    rows = []
    for record in read("results/industry_base/ship_order_profit.csv"):
        rows.append([
            record["entity_id"],
            name_of(record["entity_id"]),
            record["period"],
            num(record["revenue"]),
            num(record["old_order_revenue"]),
            num(record["new_order_revenue"]),
            num(record["order_parent_profit"]),
            num(record["consolidated_ship_parent_profit"]),
            num(record["cash_flow"]),
            num(record["revenue_share"], digits=6),
            num(record["profit_share"], digits=6),
            num(record["order_net_margin"], digits=6),
            record["scope"],
        ])
    write("ship-order-profit.csv",
          ["entity_id", "company", "period", "revenue_cny_m", "old_order_revenue_cny_m",
           "new_order_revenue_cny_m", "order_parent_profit_cny_m",
           "consolidated_ship_parent_profit_cny_m", "cash_flow_cny_m",
           "revenue_share", "profit_share", "order_net_margin", "scope"],
          rows)


def build_zip(names, zip_name):
    with zipfile.ZipFile(os.path.join(OUT, zip_name), "w", zipfile.ZIP_DEFLATED) as bundle:
        for name in names:
            bundle.write(os.path.join(OUT, name), name)
    print(f"  {zip_name}")


def main():
    global RESEARCH, OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", default=".", help="研究包根目录")
    parser.add_argument("--out", default=".", help="文章同名资源目录")
    args = parser.parse_args()
    RESEARCH = args.research
    OUT = args.out

    print("生成附件表：")
    build_history()
    build_forecast()
    build_segments()
    build_security_table()
    build_method_table()
    build_scenario_matrix()
    build_scenario_valuation()
    build_europe_market()
    build_unit_costs()
    build_dajin_bridge()
    build_dajin_share()
    build_ship_orders()

    tables = [
        "six-companies-history.csv",
        "six-companies-forecast-base.csv",
        "six-companies-segments-2029.csv",
        "security-valuation-and-buy-prices.csv",
        "valuation-by-method-2029.csv",
        "scenario-matrix-2029.csv",
        "scenario-valuation.csv",
        "europe-monopile-market.csv",
        "unit-costs-monopile.csv",
        "dajin-revenue-bridge.csv",
        "dajin-demand-share-matrix.csv",
        "ship-order-profit.csv",
        "model-output-notes.MD",
    ]
    build_zip(tables, "wind-foundation-model-appendix-2026-10-13.zip")


if __name__ == "__main__":
    main()
