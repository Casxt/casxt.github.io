"""Build the downloadable appendix tables for the tire industry article.

Usage:
    python3 build-appendix.py --research <研究目录> --out <文章资源目录>

`--research` 指包含 `facts/` 与 `results/` 的研究目录，`--out` 是文章的同名资源目录。
两者默认都是当前目录；研究目录与资源目录不同时必须显式传入。
"""

import argparse
import csv
import os
import zipfile

COMPANIES = [
    ("三角轮胎", "issuer:三角轮胎_601163"),
    ("赛轮轮胎", "issuer:赛轮轮胎_601058"),
    ("玲珑轮胎", "issuer:玲珑轮胎_601966"),
    ("贵州轮胎", "issuer:贵州轮胎_000589"),
]

# 贵州轮胎的耗用量为重算估计值（轮胎材料成本 × 采购份额 ÷ 半年度等权采购单价），
# 不在公司成本压力表中，单独登记。
GUIZHOU_PROXY = (213625.68, 89802.0)

RESEARCH = "."
OUT = "."


def read(path):
    with open(os.path.join(RESEARCH, path), encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write(name, header, rows):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    print("wrote", name, len(rows), "rows")


def build_prices():
    prices = read("facts/deep/natural_facts_nr_prices_usd_per_kg.csv")
    series = {}
    for row in prices:
        metric = row["metric_id"]
        if metric in ("nr_tsr20_nearby_usd_kg", "nr_rss3_nearby_usd_kg"):
            series.setdefault(metric, []).append((row["period_end"][:7], float(row["value"])))
    tsr = dict(series["nr_tsr20_nearby_usd_kg"])
    rss = dict(series["nr_rss3_nearby_usd_kg"])
    rows = []
    for month in sorted(set(tsr) | set(rss)):
        if month < "2015-01":
            continue
        rows.append([month, tsr.get(month, ""), rss.get(month, "")])
    write("rubber-price-monthly.csv", ["month", "tsr20_usd_per_kg", "rss3_usd_per_kg"], rows)


def build_rally_windows():
    windows = read("results/reference/natural_price_returns.csv")
    picked = []
    for row in windows:
        if row["metric_id"] not in ("nr_tsr20_nearby_usd_kg", "nr_rss3_nearby_usd_kg"):
            continue
        if row["months"] not in ("6", "12"):
            continue
        change = float(row["change_ratio"])
        if change < 0.7:
            continue
        picked.append(
            [
                "TSR20" if "tsr20" in row["metric_id"] else "RSS3",
                row["start_month"][:7],
                row["end_month"][:7],
                int(float(row["months"])),
                float(row["start_usd_kg"]),
                float(row["end_usd_kg"]),
                round(change * 100, 1),
            ]
        )
    picked.sort(key=lambda r: -r[6])
    write(
        "rubber-rally-windows.csv",
        ["grade", "start_month", "end_month", "months", "start_usd_per_kg",
         "end_usd_per_kg", "change_pct"],
        picked,
    )


def build_position():
    position = read("results/reference/rubber_price_history_position.csv")
    rows = []
    for row in position:
        rows.append(
            [
                "TSR20" if "tsr20" in row["metric_id"] else "RSS3",
                "名义美元" if row["price_basis"] == "nominal_USD" else "2026年8月美元购买力",
                f'{row["window_start"][:7]}~{row["window_end"][:7]}',
                int(float(row["observation_count"])),
                float(row["current_usd_kg"]),
                float(row["median_usd_kg"]),
                float(row["historical_peak_usd_kg"]),
                row["historical_peak_month"][:7],
                round(float(row["fraction_months_at_or_below_current"]) * 100, 1),
                round(float(row["current_over_peak"]) * 100, 1),
            ]
        )
    write(
        "rubber-price-position.csv",
        ["grade", "price_basis", "window", "months", "current_usd_per_kg",
         "median_usd_per_kg", "historical_peak_usd_per_kg", "peak_month",
         "percentile_pct", "current_as_pct_of_peak"],
        rows,
    )


def copy_table(name, path):
    data = read(path)
    write(name, list(data[0].keys()), [[r[k] for k in data[0].keys()] for r in data])


def build_exposure():
    pressure = read("results/reference/company_cost_pressure.csv")
    exposure = {}
    for row in pressure:
        if row["case_id"] == "NR10%_SR0%_pass0%_vol0%":
            exposure[row["entity_id"]] = (
                float(row["nr_consumed_t"]),
                float(row["sr_consumed_t"]),
            )
    exposure["issuer:贵州轮胎_000589"] = GUIZHOU_PROXY
    abs_map = {
        r["entity_id"]: r
        for r in read("results/event_NR100_d6_tail0_cov50/rubber_event_absolute_sensitivity.csv")
    }
    material_2026 = {}
    for row in read("results/framework_base/operating_forecast_wide.csv"):
        if row["year"] == "2026.0":
            material_2026[row["entity_id"]] = float(row["baseline_material_cost"]) / 100.0
    rows = []
    for label, key in COMPANIES:
        nr_t, sr_t = exposure[key]
        abs_row = abs_map[key]
        rows.append(
            [
                label,
                round(nr_t / 10000.0, 2),
                round(sr_t / 10000.0, 2),
                round(material_2026[key], 2),
                round(float(abs_row["annual_material_cost_delta_cny_mn"]) / 100.0, 2),
                round(float(abs_row["annual_pretax_no_pass_no_lag_cny_mn"]) / 100.0, 2),
                round(float(abs_row["annual_pretax_effective_coverage_no_lag_cny_mn"]) / 100.0, 2),
                "披露耗用量" if key != "issuer:贵州轮胎_000589" else "换算估计值",
            ]
        )
    write(
        "rubber-exposure-by-company.csv",
        ["company", "nr_consumption_10k_t", "sr_consumption_10k_t",
         "material_cost_pool_2026e_100mn_cny", "cost_delta_per_1000cny_t_100mn_cny",
         "pretax_no_pass_through_100mn_cny", "pretax_50pct_pass_through_100mn_cny",
         "consumption_basis"],
        rows,
    )


def six_month_event(directory):
    return {
        r["entity_id"]: r
        for r in read(f"results/{directory}/rubber_event_summary.csv")
        if r["horizon_months"] == "12.0"
    }


def build_event_matrix():
    rows = []
    for scenario, directory in (
        ("NR +10%", "event_NR10_d6_tail0_cov50"),
        ("NR +25%", "event_NR25_d6_tail0_cov50"),
        ("NR +50%", "event_NR50_d6_tail0_cov50"),
        ("NR +75%", "event_NR75_d6_tail0_cov50"),
        ("NR +100%", "event_NR100_d6_tail0_cov50"),
    ):
        summary = six_month_event(directory)
        for label, key in COMPANIES:
            row = summary[key]
            rows.append(
                [
                    scenario,
                    label,
                    round(float(row["cumulative_pretax_delta_cny_mn"]) / 100.0, 2),
                    round(float(row["peak_annual_material_delta_cny_mn"]) / 100.0, 2),
                    round(float(row["inventory_premium_peak_cny_mn"]) / 100.0, 2),
                ]
            )
    write(
        "rubber-event-matrix.csv",
        ["scenario", "company", "pretax_delta_12m_100mn_cny",
         "peak_annual_material_delta_100mn_cny",
         "inventory_premium_peak_100mn_cny"],
        rows,
    )


def build_scenarios():
    coverage = []
    for label, directory in (
        ("0%", "event_NR100_d6_tail0_cov0"),
        ("50%", "event_NR100_d6_tail0_cov50"),
        ("80%", "event_NR100_d6_tail0_cov80"),
        ("100%", "event_NR100_d6_tail0_cov100"),
    ):
        summary = six_month_event(directory)
        coverage.append(
            [label]
            + [round(float(summary[key]["cumulative_pretax_delta_cny_mn"]) / 100.0, 2)
               for _, key in COMPANIES]
        )
    write(
        "rubber-coverage-scenarios.csv",
        ["effective_coverage"] + [label for label, _ in COMPANIES],
        coverage,
    )

    duration = []
    for months, directory in (
        ("1", "event_NR100_d1_tail0_cov50"),
        ("3", "event_NR100_d3_tail0_cov50"),
        ("6", "event_NR100_d6_tail0_cov50"),
    ):
        summary = six_month_event(directory)
        duration.append(
            [months]
            + [round(float(summary[key]["cumulative_pretax_delta_cny_mn"]) / 100.0, 2)
               for _, key in COMPANIES]
        )
    write(
        "rubber-duration-scenarios.csv",
        ["peak_months"] + [label for label, _ in COMPANIES],
        duration,
    )

    factors = [
        ("price_lag_months_0", "提价立即落地"),
        ("price_lag_months_3", "提价延后3个月"),
        ("cost_lag_months_0", "成本立即入账"),
        ("cost_lag_months_3", "成本延后3个月"),
        ("retention_0", "回落后提价不留存"),
        ("retention_1", "回落后提价全留存"),
        ("sr_peak_ratio_0.2", "合成胶同时涨20%"),
        ("sr_peak_ratio_0.5", "合成胶同时涨50%"),
        ("volume_change_-0.05", "高价阶段销量少5%"),
        ("volume_change_-0.1", "高价阶段销量少10%"),
    ]
    default = six_month_event("event_NR100_d6_tail0_cov50")
    rows = [
        ["默认"] + [round(float(default[key]["cumulative_pretax_delta_cny_mn"]) / 100.0, 2)
                    for _, key in COMPANIES]
    ]
    for suffix, label in factors:
        summary = six_month_event(f"event_NR100_d6_tail0_cov50_{suffix}")
        rows.append(
            [label]
            + [round(float(summary[key]["cumulative_pretax_delta_cny_mn"]) / 100.0, 2)
               for _, key in COMPANIES]
        )
    write(
        "rubber-single-factor.csv",
        ["changed_assumption"] + [label for label, _ in COMPANIES],
        rows,
    )


def build_recovery():
    rows = []
    for label, key in COMPANIES:
        recovery = [
            r for r in read("results/event_NR100_d6_tail0_cov50/rubber_event_recovery.csv")
            if r["entity_id"] == key and r["horizon_months"] == "12.0"
        ][0]
        rows.append(
            [
                label,
                round(float(recovery["postfall_pretax_vs_original_baseline_cny_mn"]) / 100.0, 2),
                round(float(recovery["postfall_pretax_improvement_vs_peak_persistent_cny_mn"]) / 100.0, 2),
            ]
        )
    write(
        "rubber-recovery-comparison.csv",
        ["company", "vs_original_baseline_100mn_cny", "vs_persistent_peak_100mn_cny"],
        rows,
    )


def build_company_tables():
    history = read("results/framework_base/operating_history_wide.csv")
    rows = []
    for label, key in COMPANIES:
        for row in history:
            if row["entity_id"] != key:
                continue
            if row["year"] not in ("2021.0", "2022.0", "2023.0", "2024.0", "2025.0"):
                continue
            rows.append(
                [
                    label,
                    int(float(row["year"])),
                    round(float(row["revenue"]) / 100.0, 2),
                    round(float(row["net_income_parent"]) / 100.0, 2),
                    round(float(row["roic"]) * 100, 1),
                ]
            )
    write(
        "company-history.csv",
        ["company", "year", "revenue_100mn_cny", "net_income_parent_100mn_cny", "roic_pct"],
        rows,
    )

    rows = []
    for scenario, directory in (
        ("bear", "framework_bear"),
        ("base", "framework_base"),
        ("bull", "framework_bull"),
    ):
        data = read(f"results/{directory}/operating_forecast_wide.csv")
        for label, key in COMPANIES:
            for row in data:
                if row["entity_id"] != key:
                    continue
                if row["year"] not in ("2026.0", "2027.0", "2028.0", "2031.0", "2033.0", "2036.0"):
                    continue
                rows.append(
                    [
                        scenario,
                        label,
                        int(float(row["year"])),
                        round(float(row["revenue"]) / 100.0, 2),
                        round(float(row["net_income_parent"]) / 100.0, 2),
                        round(float(row["roic"]) * 100, 1),
                        round(float(row["cash_end"]) / 100.0, 2),
                        round(float(row["debt_end"]) / 100.0, 2),
                    ]
                )
    write(
        "company-forecast.csv",
        ["scenario", "company", "year", "revenue_100mn_cny",
         "net_income_parent_100mn_cny", "roic_pct", "cash_end_100mn_cny",
         "interest_bearing_debt_end_100mn_cny"],
        rows,
    )


def build_industry_facts():
    rows = []
    for path in (
        "facts/deep/industry_facts_industry_CNY.csv",
        "facts/deep/industry_facts_industry_tyres.csv",
    ):
        for row in read(path):
            if not row["entity_id"].startswith("industry:"):
                continue
            rows.append(
                [
                    row["entity_id"],
                    row["metric_id"],
                    row["period_end"][:10],
                    row["period_type"],
                    row["value"],
                    row["source_ids"],
                ]
            )
    write(
        "industry-facts.csv",
        ["entity", "metric", "period_end", "period_type", "value", "source_ids"],
        rows,
    )


MEMBERS = [
    "rubber-price-monthly.csv",
    "rubber-rally-windows.csv",
    "rubber-price-position.csv",
    "rubber-supply-demand.csv",
    "rubber-inventory-conditions.csv",
    "rubber-supply-conditions.csv",
    "rubber-exposure-by-company.csv",
    "rubber-event-matrix.csv",
    "rubber-coverage-scenarios.csv",
    "rubber-duration-scenarios.csv",
    "rubber-single-factor.csv",
    "rubber-recovery-comparison.csv",
    "company-history.csv",
    "company-forecast.csv",
    "industry-facts.csv",
    "model-output-notes.MD",
]


def main():
    global RESEARCH, OUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--research", default=".", help="研究目录，含 facts/ 与 results/")
    parser.add_argument("--out", default=".", help="文章资源目录")
    args = parser.parse_args()
    RESEARCH = args.research
    OUT = args.out

    build_prices()
    build_rally_windows()
    build_position()
    copy_table("rubber-supply-demand.csv", "results/reference/natural_rubber_historical_balance.csv")
    copy_table("rubber-inventory-conditions.csv", "results/reference/natural_inventory_conditions.csv")
    copy_table("rubber-supply-conditions.csv", "results/reference/natural_supply_conditions.csv")
    build_exposure()
    build_event_matrix()
    build_scenarios()
    build_recovery()
    build_company_tables()
    build_industry_facts()

    zip_path = os.path.join(OUT, "tire-rubber-model-appendix-2026-10-12.zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for member in MEMBERS:
            archive.write(os.path.join(OUT, member), member)
    print("packed", len(MEMBERS), "members ->", zip_path)


if __name__ == "__main__":
    main()
