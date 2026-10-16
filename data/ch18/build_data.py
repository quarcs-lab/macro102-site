"""Build the wider data files used by the Chapter 18 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (raw downloads saved by the macro102 /collect-data skill, under
original-scanned-book/ch18-the-government-and-the-macroeconomy/data/):
  table18-1/raw/hist01z2_fy2027.xlsx   OMB Historical Table 1.2 (FY2027 Budget): GDP by fiscal year, $ billions
  table18-1/raw/hist02z1_fy2027.xlsx   OMB Historical Table 2.1: receipts by source, $ millions
  table18-1/raw/hist03z1_fy2027.xlsx   OMB Historical Table 3.1: outlays by function, $ millions
  table18-1/raw/hist0*_fy2024.xlsx     the same three tables of the FY2024 Budget (March 2023, the textbook's data;
                                       FY2023 is an estimate there)
  table18-1/raw/fred_POPTHM.csv        U.S. population, thousands, monthly (BEA via FRED)
  fig18-3/raw/oecd_gov_pf_yu_GE_pct_gdp.csv   OECD Government at a Glance: general government spending, % of GDP

Outputs, next to this script:
  federal_budget.csv   the lines of Table 18.1 in percent of GDP for every fiscal year 1940-2025, plus fiscal-year
                       GDP and population (one row per fiscal year and release)
  gov_spending.csv     general government spending, % of GDP, the 38 OECD countries, 2007-2025

Checks: federal_budget.csv reproduces collect-data's table18-1/data.csv (FY2023, FY2025 and the FY2023 estimate),
and gov_spending.csv reproduces fig18-3/data.csv.
"""
import argparse
import os
import re
import warnings

import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")  # OMB files have no default style
HERE = os.path.dirname(os.path.abspath(__file__))
CHAPTER = "original-scanned-book/ch18-the-government-and-the-macroeconomy/data"
FUNCS = {"National Defense": "defense", "Health": "health", "Medicare": "medicare",
         "Income Security": "income_security", "Social Security": "social_security",
         "Net interest": "net_interest", "Total, Federal outlays": "total"}
OECD38 = ["AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC",
          "HUN", "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR",
          "POL", "PRT", "SVK", "SVN", "ESP", "SWE", "CHE", "TUR", "GBR", "USA"]
# the textbook's short names for its six countries (Figure 18.3)
SHORT = {"KOR": "S. Korea", "USA": "U.S.", "JPN": "Japan", "GBR": "U.K.", "SWE": "Sweden", "FRA": "France",
         "SVK": "Slovakia", "TUR": "Turkey"}


def num(v):
    """OMB cell -> float: '..........' -> NaN, '*' or '-*' (less than 0.05) -> 0."""
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s in ("*", "-*"):
        return 0.0
    return float("nan") if s.strip(".") == "" else float(s.replace(",", ""))


def by_year_rows(path, cols, estimates):
    """OMB table with one row per fiscal year -> DataFrame indexed by year (TQ dropped)."""
    raw = pd.read_excel(path, header=None)
    out = {}
    for _, r in raw.iterrows():
        m = re.fullmatch(r"(\d{4})( estimate)?", str(r[0]).strip())
        if m and (estimates or not m.group(2)):
            out[int(m.group(1))] = {k: num(r[c]) for k, c in cols.items()}
    return pd.DataFrame.from_dict(out, orient="index").sort_index()


def outlays(path, estimates):
    """OMB Table 3.1 (one column per fiscal year) -> DataFrame indexed by year, $ millions."""
    raw = pd.read_excel(path, header=None)
    stop = raw.index[raw[0].astype(str).str.startswith("As percentages")][0]
    rows = {}
    for i in range(2, stop):
        lab = str(raw.iat[i, 0]).strip()
        if lab in FUNCS and FUNCS[lab] not in rows:
            rows[FUNCS[lab]] = i
    out = {}
    for j in range(1, raw.shape[1]):
        m = re.fullmatch(r"(\d{4})( estimate)?", str(raw.iat[1, j]).strip())
        if m and (estimates or not m.group(2)):
            out[int(m.group(1))] = {k: num(raw.iat[i, j]) for k, i in rows.items()}
    return pd.DataFrame.from_dict(out, orient="index").sort_index()


def budget(root, release, estimates):
    """Table 18.1 lines as % of fiscal-year GDP, for every fiscal year of one OMB release."""
    t = os.path.join(root, "table18-1/raw")
    rec = by_year_rows(os.path.join(t, f"hist02z1_{release}.xlsx"),
                       {"individual": 1, "corporate": 2, "social_insurance": 3, "excise": 6, "other": 7,
                        "total": 8}, estimates)
    out = outlays(os.path.join(t, f"hist03z1_{release}.xlsx"), estimates)
    gdp = by_year_rows(os.path.join(t, f"hist01z2_{release}.xlsx"), {"gdp": 1}, estimates).gdp
    years = rec.index.intersection(out.index).intersection(gdp.dropna().index)
    rec, out, gdp = rec.loc[years], out.loc[years], gdp.loc[years]
    health = out.health.fillna(0) + out.medicare.fillna(0)     # Medicare starts in FY1966: 0 before
    named = health + out.social_security + out.defense + out.income_security + out.net_interest
    lines = pd.DataFrame({
        "total_spending": out.total, "health": health, "social_security": out.social_security,
        "defense": out.defense, "income_security": out.income_security, "net_interest": out.net_interest,
        "other_spending": out.total - named, "total_revenue": rec.total, "individual_income_tax": rec.individual,
        "social_insurance_tax": rec.social_insurance, "corporate_income_tax": rec.corporate,
        "other_revenue": rec.excise + rec.other, "balance": rec.total - out.total})
    pct = (100 * lines.div(gdp * 1000, axis=0)).round(3)
    pct.insert(0, "gdp_billions", gdp.round(1))
    return pct


def fy_population(root):
    """Population averaged over the fiscal year (October to September), millions; complete years only."""
    p = pd.read_csv(os.path.join(root, "table18-1/raw/fred_POPTHM.csv"))
    p.columns = ["date", "pop"]
    p["date"] = pd.to_datetime(p.date)
    p["pop"] = pd.to_numeric(p["pop"], errors="coerce")
    p = p.dropna()
    fy = p.date.dt.year + (p.date.dt.month >= 10)
    g = p.groupby(fy)["pop"]
    return (g.mean()[g.count() == 12] / 1000).round(3)


def build_budget(root):
    pop = fy_population(root)
    actual = budget(root, "fy2027", estimates=False)
    actual = actual[actual.index >= 1940]
    actual.insert(0, "release", "actual (FY2027 Budget)")
    estimate = budget(root, "fy2024", estimates=True).loc[[2023]]
    estimate.insert(0, "release", "estimate (FY2024 Budget)")
    out = pd.concat([actual, estimate])
    out.insert(2, "population_millions", out.index.map(pop))
    out.index.name = "year"
    out = out.reset_index()
    out.to_csv(os.path.join(HERE, "federal_budget.csv"), index=False)
    # check against collect-data's Table 18.1 (unrounded % of GDP and dollars per person)
    ref = pd.read_csv(os.path.join(root, "table18-1/data.csv")).set_index("item")
    names = ref.index.tolist()
    worst_pct, worst_pp = 0.0, 0.0
    for col, year, release in [("book_2023", 2023, "actual"), ("latest_2025", 2025, "actual"),
                               ("vintage2023_2023", 2023, "estimate")]:
        row = out[(out.year == year) & out.release.str.startswith(release)].iloc[0]
        ours = row[list(out.columns[4:])].astype(float).values
        worst_pct = max(worst_pct, abs(ours - ref[f"pct_gdp_{col}"].values).max())
        pp = ours / 100 * row.gdp_billions * 1e9 / (pop.loc[year] * 1e6)
        worst_pp = max(worst_pp, abs(pp - ref[f"per_person_{col}"].values).max())
    print(f"federal_budget.csv: {len(out)} rows, FY{out.year.min()}-{out.year.max()}; vs table18-1/data.csv "
          f"({len(names)} lines): max |diff| {worst_pct:.4f} pt of GDP, {worst_pp:.2f} dollars per person")


def build_spending(root):
    raw = pd.read_csv(os.path.join(root, "fig18-3/raw/oecd_gov_pf_yu_GE_pct_gdp.csv"))
    raw = raw[raw.REF_AREA.isin(OECD38)]
    out = pd.DataFrame({"iso3": raw.REF_AREA, "country": raw["Reference area"], "year": raw.TIME_PERIOD,
                        "gov_spending": raw.OBS_VALUE.round(2), "status": raw["Observation status"]})
    out["country"] = out.iso3.map(SHORT).fillna(out.country)
    out = out.dropna(subset=["gov_spending"]).sort_values(["iso3", "year"])
    out.to_csv(os.path.join(HERE, "gov_spending.csv"), index=False)
    ref = pd.read_csv(os.path.join(root, "fig18-3/data.csv"))
    worst = 0.0
    for _, r in ref.iterrows():
        for y in (2019, 2024):
            v = out[(out.iso3 == r.iso3) & (out.year == y)].gov_spending.iloc[0]
            worst = max(worst, abs(v - r[f"gov_spending_{y}"]))
    print(f"gov_spending.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}; "
          f"vs fig18-3/data.csv: max |diff| {worst:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, CHAPTER)
    build_budget(root)
    build_spending(root)


if __name__ == "__main__":
    main()
