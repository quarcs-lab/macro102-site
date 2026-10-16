"""Build the wider data files used by the Chapter 8 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under original-scanned-book/ch08-inflation/data/):
  table8-1/raw/measuringworth_uscpi_1774_2025.csv  MeasuringWorth annual U.S. CPI, 1982-84 = 100
  fig8-3/raw/JSTdatasetR6.xlsx                     Jorda-Schularick-Taylor Macrohistory R6 (U.S. broad money)
  fig8-3/raw/fred_M2NS.csv                         M2, billions of dollars, monthly, NSA
  table8-2/raw/fred_MBCURRCIR.csv, fred_BOGMBASE.csv, fred_M1SL.csv, fred_M2SL.csv
                                                   currency in circulation, monetary base, M1, M2 (monthly)
  ex15/raw/fred_GDPA.csv                           U.S. nominal GDP, billions of dollars, annual
  fig8-2/raw/wdi_FP.CPI.TOTL.ZG_all.json           WDI CPI inflation, all economies and aggregates
  fig8-2/raw/wdi_country_list.json                 WDI country list (to drop aggregates)
  fig8-6/raw/wb_global_inflation_hcpi_a.csv        World Bank Global Inflation Database, headline CPI
Outputs (next to this script):
  us_cpi.csv              year, cpi                          U.S. CPI 1774-2025 (Table 8.1, "How much is that?")
  us_money_prices.csv     year, m2, cpi                      U.S. M2 and CPI 1870-2025 (Figure 8.3, any period length)
  money_supply.csv        date, currency, monetary_base, m1, m2   monthly, 1959-01 on (Table 8.2)
  us_money_annual.csv     year, nominal_gdp, currency, m2    annual, 1959-2025 (velocity, inflation tax)
  inflation_panel.csv     iso3, country, year, inflation, source   CPI inflation, all economies 1960-2025
"""
import argparse
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch08-inflation/data/"
LAST = 2025                                     # last complete calendar year of the monthly series
NAMES = {"Venezuela, RB": "Venezuela", "Russian Federation": "Russia", "Turkiye": "Turkey",
         "Egypt, Arab Rep.": "Egypt", "Iran, Islamic Rep.": "Iran", "Korea, Rep.": "South Korea",
         "Yemen, Rep.": "Yemen", "Lao PDR": "Laos", "Syrian Arab Republic": "Syria"}


def mw_cpi(root):
    """MeasuringWorth annual CPI as a Series indexed by year."""
    rows = [ln.replace('"', "").split(",") for ln in open(os.path.join(root, "table8-1/raw/measuringworth_uscpi_1774_2025.csv"))]
    s = pd.Series({int(a): float(b) for a, b in (r for r in rows if len(r) == 2) if a.isdigit() and b.strip()})
    s.index.name = "year"
    return s.rename("cpi")


def fred(root, path):
    """One FRED series as a Series indexed by month."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def annual(s):
    """Calendar-year mean of a monthly series, complete years only (to LAST)."""
    s = s.dropna()
    out = s.groupby(s.index.year).mean()
    out.index.name = "year"
    return out.loc[:LAST]


def us_cpi(root):
    cpi = mw_cpi(root)
    cpi.round(3).to_csv(os.path.join(HERE, "us_cpi.csv"))
    ref = pd.read_csv(os.path.join(root, "table8-1/data.csv")).set_index("item")
    ours = (100 * cpi.loc[ref.index] / cpi.loc[2022]).round(2)
    print(f"us_cpi.csv: {len(cpi)} years, {cpi.index.min()}-{cpi.index.max()}; "
          f"largest difference from table8-1 (2022 = 100): {(ours - ref.cpi_book_2022).abs().max():.3f}")
    return cpi


def us_money_prices(root, cpi):
    jst = pd.read_excel(os.path.join(root, "fig8-3/raw/JSTdatasetR6.xlsx"))
    jst = jst[jst.iso == "USA"].set_index("year")["money"]
    m2 = annual(fred(root, "fig8-3/raw/fred_M2NS.csv"))
    money = pd.concat([jst.loc[1870:1958], m2.loc[1959:]]).rename("m2")
    out = pd.concat([money, cpi], axis=1, join="inner").loc[1870:LAST]
    out.index.name = "year"
    out.round(3).to_csv(os.path.join(HERE, "us_money_prices.csv"))
    ref = pd.read_csv(os.path.join(root, "fig8-3/data.csv"))
    worst = 0.0
    for _, r in ref.iterrows():
        n = r.end_year - r.year
        g = 100 * ((out.m2[r.end_year] / out.m2[r.year]) ** (1 / n) - 1)
        p = 100 * ((out.cpi[r.end_year] / out.cpi[r.year]) ** (1 / n) - 1)
        worst = max(worst, abs(g - r.money_growth), abs(p - r.inflation))
    print(f"us_money_prices.csv: {len(out)} years, {out.index.min()}-{out.index.max()}; "
          f"decade growth rates vs fig8-3: largest difference {worst:.3f} points")


def money_supply(root):
    out = pd.DataFrame({"currency": fred(root, "table8-2/raw/fred_MBCURRCIR.csv"),
                        "monetary_base": fred(root, "table8-2/raw/fred_BOGMBASE.csv"),
                        "m1": fred(root, "table8-2/raw/fred_M1SL.csv"),
                        "m2": fred(root, "table8-2/raw/fred_M2SL.csv")}).dropna().round(1)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "money_supply.csv"), date_format="%Y-%m-%d")
    ref = pd.read_csv(os.path.join(root, "table8-2/data.csv"))
    ours = out.loc["2023-01-01", ["currency", "monetary_base", "m1", "m2"]].values
    print(f"money_supply.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"January 2023 minus table8-2: {(ours - ref.billions_book_2023.values).round(2).tolist()}")


def us_money_annual(root):
    gdp = fred(root, "ex15/raw/fred_GDPA.csv")
    gdp.index = gdp.index.year
    out = pd.DataFrame({"nominal_gdp": gdp, "currency": annual(fred(root, "table8-2/raw/fred_MBCURRCIR.csv")),
                        "m2": annual(fred(root, "table8-2/raw/fred_M2SL.csv"))}).dropna().round(3)
    out.index.name = "year"
    out.to_csv(os.path.join(HERE, "us_money_annual.csv"))
    v = out.nominal_gdp / out.m2
    print(f"us_money_annual.csv: {len(out)} years, {out.index.min()}-{out.index.max()}; "
          f"M2 velocity {v.min():.2f} to {v.max():.2f}")


def inflation_panel(root):
    econ = {c["id"]: c["name"] for c in json.load(open(os.path.join(root, "fig8-2/raw/wdi_country_list.json")))[1]
            if c["region"]["value"] != "Aggregates"}
    rows = json.load(open(os.path.join(root, "fig8-2/raw/wdi_FP.CPI.TOTL.ZG_all.json")))
    wdi = pd.DataFrame([{"iso3": r["countryiso3code"], "year": int(r["date"]), "inflation": r["value"]}
                        for r in rows if r["countryiso3code"] in econ and r["value"] is not None])
    wdi["source"] = "WDI"
    gid = pd.read_csv(os.path.join(root, "fig8-6/raw/wb_global_inflation_hcpi_a.csv"))
    gid = gid[gid.iso3.isin(econ)].rename(columns={"value": "inflation"})[["iso3", "year", "inflation"]]
    gid["source"] = "GID"
    have = set(zip(wdi.iso3, wdi.year))
    fill = gid[[(a, b) not in have for a, b in zip(gid.iso3, gid.year)]]
    out = pd.concat([wdi, fill]).query("year >= 1960 and year <= @LAST")
    out["country"] = out.iso3.map(econ).replace(NAMES)
    out = out[["iso3", "country", "year", "inflation", "source"]].sort_values(["country", "year"])
    out["inflation"] = out.inflation.round(3)
    out.to_csv(os.path.join(HERE, "inflation_panel.csv"), index=False)
    # validation: the WDI rows reproduce fig8-2; the filled panel reproduces fig8-6 and fig8-7
    w = out[out.source == "WDI"]
    share = (100 * (w.inflation > 25).groupby(w.year).mean()).round(3)
    ref2 = pd.read_csv(os.path.join(root, "fig8-2/data.csv")).set_index("year").share_above_25_pct
    print(f"inflation_panel.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.year.min()}-{out.year.max()}, "
          f"{(out.source == 'GID').sum()} rows filled from the Global Inflation Database")
    print(f"  share above 25% (WDI rows) vs fig8-2: largest difference {(share - ref2).abs().max():.3f}")
    wide = out.pivot(index="year", columns="iso3", values="inflation")
    for item, cols in [["fig8-6", {"argentina": "ARG", "brazil": "BRA", "russia": "RUS"}],
                       ["fig8-7", {"mexico": "MEX", "nigeria": "NGA", "venezuela": "VEN"}]]:
        ref = pd.read_csv(os.path.join(root, item, "data.csv")).set_index("year")
        diffs = []
        for col, iso in cols.items():
            both = pd.concat([ref[col], wide[iso]], axis=1).dropna()
            diffs.append(f"{col} {(both.iloc[:, 0] - both.iloc[:, 1]).abs().max():.3f} "
                         f"({ref[col].notna().sum()} vs {wide[iso].notna().sum()} years)")
        print(f"  vs {item}: " + ", ".join(diffs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cpi = us_cpi(root)
    us_money_prices(root, cpi)
    money_supply(root)
    us_money_annual(root)
    inflation_panel(root)


if __name__ == "__main__":
    main()
