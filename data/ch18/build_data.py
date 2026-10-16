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

Multi-country files (downloads cached in ../macro102/.work/ch18/notebook-raw/), for the 38 OECD members and 12
large emerging economies:
  gov_finance.csv      iso3, country, year, revenue, spending, balance, private_investment, region
                       general government revenue, spending and net lending (OECD Table 12) and private investment
                       (OECD National Accounts at a Glance and Table 1), % of GDP, 1970-2025
  gross_debt.csv       iso3, country, year, gross_debt, region      general government gross debt, % of GDP
                       (IMF, Public Finances in Modern History), 1800-2024
  net_debt.csv         iso3, country, year, net_debt, region        general government net financial liabilities,
                       % of GDP (OECD financial balance sheets, as fig18-4.csv), 1995-2025
  health_spending.csv  iso3, country, year, health_share, region    current health expenditure, % of GDP (OECD
                       Health Statistics, as fig18-8.csv), 1970-2025

Checks: federal_budget.csv reproduces collect-data's table18-1/data.csv (FY2023, FY2025 and the FY2023 estimate),
and gov_spending.csv reproduces fig18-3/data.csv.
"""
import argparse
import os
import re
import warnings

import pandas as pd
import requests

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


# Readable names and regions of the countries in the multi-country files (iso3: (name, region, iso2)).
COUNTRIES = {
    "ARG": ("Argentina", "Americas", "AR"), "AUS": ("Australia", "Asia and Oceania", "AU"),
    "AUT": ("Austria", "Europe", "AT"), "BEL": ("Belgium", "Europe", "BE"), "BRA": ("Brazil", "Americas", "BR"),
    "CAN": ("Canada", "Americas", "CA"), "CHE": ("Switzerland", "Europe", "CH"), "CHL": ("Chile", "Americas", "CL"),
    "CHN": ("China", "Asia and Oceania", "CN"), "COL": ("Colombia", "Americas", "CO"),
    "CRI": ("Costa Rica", "Americas", "CR"), "CZE": ("Czechia", "Europe", "CZ"), "DEU": ("Germany", "Europe", "DE"),
    "DNK": ("Denmark", "Europe", "DK"), "ESP": ("Spain", "Europe", "ES"), "EST": ("Estonia", "Europe", "EE"),
    "FIN": ("Finland", "Europe", "FI"), "FRA": ("France", "Europe", "FR"), "GBR": ("United Kingdom", "Europe", "GB"),
    "GRC": ("Greece", "Europe", "GR"), "HKG": ("Hong Kong", "Asia and Oceania", "HK"),
    "HUN": ("Hungary", "Europe", "HU"), "IDN": ("Indonesia", "Asia and Oceania", "ID"),
    "IND": ("India", "Asia and Oceania", "IN"), "IRL": ("Ireland", "Europe", "IE"),
    "ISL": ("Iceland", "Europe", "IS"), "ISR": ("Israel", "Middle East and Africa", "IL"),
    "ITA": ("Italy", "Europe", "IT"), "JPN": ("Japan", "Asia and Oceania", "JP"),
    "KOR": ("South Korea", "Asia and Oceania", "KR"), "LTU": ("Lithuania", "Europe", "LT"),
    "LUX": ("Luxembourg", "Europe", "LU"), "LVA": ("Latvia", "Europe", "LV"), "MEX": ("Mexico", "Americas", "MX"),
    "MYS": ("Malaysia", "Asia and Oceania", "MY"), "NLD": ("Netherlands", "Europe", "NL"),
    "NOR": ("Norway", "Europe", "NO"), "NZL": ("New Zealand", "Asia and Oceania", "NZ"),
    "POL": ("Poland", "Europe", "PL"), "PRT": ("Portugal", "Europe", "PT"), "RUS": ("Russia", "Europe", "RU"),
    "SAU": ("Saudi Arabia", "Middle East and Africa", "SA"), "SGP": ("Singapore", "Asia and Oceania", "SG"),
    "SVK": ("Slovakia", "Europe", "SK"), "SVN": ("Slovenia", "Europe", "SI"), "SWE": ("Sweden", "Europe", "SE"),
    "THA": ("Thailand", "Asia and Oceania", "TH"), "TUR": ("Turkey", "Middle East and Africa", "TR"),
    "USA": ("United States", "Americas", "US"), "ZAF": ("South Africa", "Middle East and Africa", "ZA"),
}
OECD = "https://sdmx.oecd.org/public/rest/data/"
TABLE12_URL = OECD + "OECD.SDD.NAD,DSD_NASEC10@DF_TABLE12_{flow},1.1/A..S13...{code}.......?format=csv"
TABLE1_URL = OECD + "OECD.SDD.NAD,DSD_NAMAIN10@DF_TABLE1_EXPENDITURE,2.0/A..S1..B1GQ+P5+P51G+P52+P51N....XDC.V..?format=csv"
NAAG_III_URL = OECD + "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_III,1.0/all?dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
T720_URL = OECD + "OECD.SDD.NAD,DSD_NASEC20@DF_T720GOV_A,1.1/A....S13...N.LE.BF90........?format=csv"
SHA_URL = OECD + "OECD.ELS.HD,DSD_SHA@DF_SHA,1.1/.A.EXP_HEALTH.PT_B1GQ._T.._T._T._T._Z._Z._Z?format=csv"
IMF_DEBT_URL = "https://www.imf.org/external/datamapper/api/v1/d"


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


def cached(url, cache, name):
    """Download url once into the cache folder (requests' default User-Agent) and return the local path."""
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        r = requests.get(url, timeout=600)
        if r.status_code != 200 or r.text.lstrip().startswith("<"):
            raise SystemExit(f"{url}: HTTP {r.status_code} (OECD answers 429 when busy: wait and run again)")
        os.makedirs(cache, exist_ok=True)
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def tidy(df, iso3, period, values):
    """Long table iso3, country, period, values..., region; known countries only, sorted."""
    out = df[df[iso3].isin(COUNTRIES)].copy()
    out.insert(0, "iso3", out.pop(iso3))
    out.insert(1, "country", out.iso3.map({k: v[0] for k, v in COUNTRIES.items()}))
    out = out[["iso3", "country", period] + values].dropna(subset=values, how="all")
    out["region"] = out.iso3.map({k: v[1] for k, v in COUNTRIES.items()})
    return out.sort_values(["country", period]).reset_index(drop=True)


def by_country(path, value="OBS_VALUE"):
    """An OECD CSV as a table: rows are years, columns are ISO3 codes."""
    raw = pd.read_csv(path, low_memory=False)
    return raw.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values=value)


def save(out, name):
    out.to_csv(os.path.join(HERE, name), index=False)
    size = os.path.getsize(os.path.join(HERE, name))
    print(f"{name}: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}, {size:,} bytes")
    if size > 1_000_000:
        raise SystemExit(f"{name} is above the 1 MB limit")


def build_finance(cache):
    """Figures 18.1, 18.2 and 18.5 for every country: general government revenue, spending and budget balance,
    and private investment (GFCF minus government GFCF, plus inventories), all in percent of GDP."""
    t1 = pd.read_csv(cached(TABLE1_URL, cache, "oecd_TABLE1_B1GQ_P5_P51G_P52_XDC.csv"))
    assert set(t1.UNIT_MULT) == {6}
    x = t1.pivot_table(index="TIME_PERIOD", columns=["TRANSACTION", "REF_AREA"], values="OBS_VALUE")
    gdp = x["B1GQ"]
    parts = {}
    for name, flow, code in [("revenue", "REV", "OTR"), ("spending", "EXP", "OTE"), ("balance", "BAL", "B9")]:
        path = cached(TABLE12_URL.format(flow=flow, code=code), cache, f"oecd_DF_TABLE12_{flow}_{code}.csv")
        assert set(pd.read_csv(path).UNIT_MULT) == {6}               # millions, as Table 1
        parts[name] = 100 * by_country(path) / gdp
    raw = pd.read_csv(cached(NAAG_III_URL, cache, "oecd_NAAG_III_all.csv"), low_memory=False,
                      usecols=["REF_AREA", "MEASURE", "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE"])
    gfcf = raw[(raw.MEASURE == "P51G") & (raw.UNIT_MEASURE == "PT_B1GQ")]
    gov = raw[(raw.MEASURE == "P51GS13") & (raw.UNIT_MEASURE == "PT_P51G")]
    gfcf = gfcf.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    gov = gov.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    parts["private_investment"] = gfcf * (1 - gov / 100) + 100 * x["P52"] / gdp
    long = pd.concat({k: v.stack() for k, v in parts.items()}, axis=1).round(2) + 0.0     # no -0.0
    long.index.names = ["year", "iso"]
    long = long.reset_index()
    # Brazil's and Costa Rica's Table 12 accounts are about 24 points of GDP above the IMF's general government
    # revenue and spending (Fiscal Monitor), every other country is within 15 points (most within 2): drop them
    odd = long.iso.isin(["BRA", "CRI"])
    long.loc[odd, ["revenue", "spending", "balance"]] = float("nan")
    long["year"] = long.year.astype(int)
    out = tidy(long, "iso", "year", list(parts))
    save(out, "gov_finance.csv")
    # checks: spending equals Government at a Glance (gov_spending.csv); U.S. investment is close to fig18-5.csv
    gs = pd.read_csv(os.path.join(HERE, "gov_spending.csv")).merge(out, on=["iso3", "year"])
    gap = (gs.gov_spending - gs.spending).abs()
    us = out[out.iso3 == "USA"].set_index("year").private_investment
    ref = pd.read_csv(os.path.join(HERE, "fig18-5.csv")).set_index("year").investment_share
    gap5 = (us - ref).dropna().abs()
    print(f"  spending vs gov_spending.csv: median |gap| {gap.median():.2f}, {(gap < 0.5).mean():.0%} of "
          f"{len(gap)} country-years within 0.5 points; U.S. private investment vs fig18-5.csv: largest |gap| "
          f"{gap5.max():.2f} points ({gap5.index.min()}-{gap5.index.max()})")
    if gap.median() > 0.2 or gap5.max() > 0.6:
        raise SystemExit("gov_finance.csv failed its checks")
    return out


def build_gross_debt(cache):
    """Figure 18.2 for every country: general government gross debt, % of GDP, IMF historical database."""
    import json
    j = json.load(open(cached(IMF_DEBT_URL, cache, "imf_datamapper_d.json")))
    rows = []
    for iso, years in j["values"]["d"].items():
        for year, value in years.items():
            rows.append((iso, int(year), round(value, 2)))
    out = tidy(pd.DataFrame(rows, columns=["iso", "year", "gross_debt"]), "iso", "year", ["gross_debt"])
    save(out, "gross_debt.csv")
    us = out[out.iso3 == "USA"].set_index("year").gross_debt
    ref = pd.read_csv(os.path.join(HERE, "fig18-2.csv")).set_index("year").debt_public_gdp_pct
    print(f"  U.S. general government gross debt minus federal debt held by the public (fig18-2.csv): "
          f"{(us - ref).loc[1946]:+.1f} points in 1946, {(us - ref).loc[2024]:+.1f} in 2024 (different concepts)")
    return out


def build_net_debt(cache):
    """Figure 18.4 for every OECD country: -net financial worth of general government / GDP, as fig18-4.csv."""
    b = pd.read_csv(cached(T720_URL, cache, "oecd_T720GOV_S13_BF90_all.csv"))
    b = b[b.UNIT_MEASURE == "XDC"]
    t1 = pd.read_csv(cached(TABLE1_URL, cache, "oecd_TABLE1_B1GQ_P5_P51G_P52_XDC.csv"))
    assert set(b.UNIT_MULT) == set(t1.UNIT_MULT) == {6}
    gdp = t1[t1.TRANSACTION == "B1GQ"].pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    nfw = b.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    ratio = (-nfw / gdp * 100).loc[1995:].stack().round(2) + 0.0
    ratio.index.names = ["year", "iso"]
    out = tidy(ratio.rename("net_debt").reset_index(), "iso", "year", ["net_debt"])
    save(out, "net_debt.csv")
    ref = pd.read_csv(os.path.join(HERE, "fig18-4.csv")).set_index("year")
    worst = 0.0
    for iso, col in {"ITA": "italy", "JPN": "japan", "USA": "usa", "GBR": "uk", "DEU": "germany"}.items():
        ours = out[out.iso3 == iso].set_index("year").net_debt
        worst = max(worst, (ours - ref[col]).dropna().abs().max())
    print(f"  vs fig18-4.csv (five countries): max |diff| {worst:.3f} (Italy, Japan, the U.S. and the U.K. equal; "
          "the OECD revised Germany's balance sheets after collect-data's download, by up to about 1 point)")
    if worst > 1.5:
        raise SystemExit("net_debt.csv does not reproduce fig18-4.csv")
    return out


def build_health(cache):
    """Figure 18.8 for every country: current health expenditure, % of GDP (OECD SHA), as fig18-8.csv."""
    d = pd.read_csv(cached(SHA_URL, cache, "oecd_SHA_CHE_pct_gdp_all.csv"))
    d = d.rename(columns={"TIME_PERIOD": "year"})
    d["health_share"] = d.OBS_VALUE.round(3)
    out = tidy(d, "REF_AREA", "year", ["health_share"])
    save(out, "health_spending.csv")
    ref = pd.read_csv(os.path.join(HERE, "fig18-8.csv")).set_index("year")
    worst = 0.0
    for iso, col in {"USA": "usa", "DEU": "germany", "FRA": "france", "JPN": "japan", "GBR": "uk"}.items():
        ours = out[out.iso3 == iso].set_index("year").health_share
        worst = max(worst, (ours - ref[col]).dropna().abs().max())
    print(f"  vs fig18-8.csv (five countries): max |diff| {worst:.4f}")
    if worst > 0.001:
        raise SystemExit("health_spending.csv does not reproduce fig18-8.csv")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, CHAPTER)
    cache = os.path.join(args.macro102, ".work", "ch18", "notebook-raw")
    build_budget(root)
    build_spending(root)
    build_finance(cache)
    build_gross_debt(cache)
    build_net_debt(cache)
    build_health(cache)


if __name__ == "__main__":
    main()
