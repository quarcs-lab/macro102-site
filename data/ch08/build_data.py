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

Multi-country files (conventions.md 6b), downloaded from public sources with requests' default User-Agent and
cached in macro102's .work/ch08/notebook-raw/ (delete a cached file to download it again):
  countries.csv           iso3, country, region, income, oecd           the World Bank's economies and groups
  money_prices_panel.csv  iso3, country, year, money, cpi, source       broad money and CPI, 18 economies, 1870-2025
  interest_rates_panel.csv iso3, country, year, short_rate, inflation, real_rate, rate_source
                                                                         3-month rates and real rates, ~50 economies
"""
import argparse
import json
import os

import pandas as pd
import requests

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


OECD = ["AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN",
        "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR", "POL", "PRT",
        "SVK", "SVN", "ESP", "SWE", "CHE", "TUR", "GBR", "USA"]        # the 38 OECD members (2026)
EO_URL = "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.IRS.A?startPeriod=1960&format=csvfile"
REGIONS = {"Middle East, North Africa, Afghanistan & Pakistan": "Middle East & North Africa"}   # shorter label
FINMARK_URL = ("https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.A.IR3TIB......"
               "?startPeriod=1955&format=csvfile")


def download(url, name, raw):
    """Download url once into the cache folder raw/name and return the local path."""
    path = os.path.join(raw, name)
    if not os.path.exists(path):
        os.makedirs(raw, exist_ok=True)
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def countries(root):
    """The World Bank's economies (no aggregates) with region, income group and OECD membership."""
    rows = []
    for c in json.load(open(os.path.join(root, "fig8-2/raw/wdi_country_list.json")))[1]:
        if c["region"]["value"] != "Aggregates":
            rows.append({"iso3": c["id"], "country": NAMES.get(c["name"], c["name"]),
                         "region": REGIONS.get(c["region"]["value"].strip(), c["region"]["value"].strip()),
                         "income": c["incomeLevel"]["value"].strip(),
                         "oecd": c["id"] in OECD})
    out = pd.DataFrame(rows).sort_values("country")
    out.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    panel = pd.read_csv(os.path.join(HERE, "inflation_panel.csv"))
    names = panel[["iso3", "country"]].drop_duplicates().merge(out, on="iso3", suffixes=("", "_c"))
    print(f"countries.csv: {len(out)} economies, {out.oecd.sum()} OECD members, {out.region.nunique()} regions; "
          f"names that differ from inflation_panel.csv: {(names.country != names.country_c).sum()}")
    return out.set_index("iso3").country


def money_prices_panel(root, names):
    """Broad money and CPI for the 18 Macrohistory economies; the U.S. rows are us_money_prices.csv."""
    jst = pd.read_excel(os.path.join(root, "fig8-3/raw/JSTdatasetR6.xlsx"))
    jst = jst[jst.iso != "USA"][["iso", "year", "money", "cpi"]].dropna().rename(columns={"iso": "iso3"})
    jst["source"] = "JST"
    us = pd.read_csv(os.path.join(HERE, "us_money_prices.csv")).rename(columns={"m2": "money"})
    us["iso3"], us["source"] = "USA", "JST+FRED"
    out = pd.concat([us, jst])
    out["country"] = out.iso3.map(names)
    out = out[["iso3", "country", "year", "money", "cpi", "source"]].sort_values(["country", "year"])
    out.to_csv(os.path.join(HERE, "money_prices_panel.csv"), index=False, float_format="%.6g")  # 6 significant
    #                                         digits: Germany's pre-1923 marks are as small as 1e-11 of today's units
    # validation: the U.S. decades reproduce fig8-3; report the extreme decade averages of the other economies
    wide_m, wide_p = out.pivot(index="year", columns="country", values="money"), out.pivot(index="year", columns="country", values="cpi")
    ref = pd.read_csv(os.path.join(root, "fig8-3/data.csv"))
    worst = 0.0
    for _, r in ref.iterrows():
        n = r.end_year - r.year
        g = 100 * ((wide_m["United States"][r.end_year] / wide_m["United States"][r.year]) ** (1 / n) - 1)
        worst = max(worst, abs(g - r.money_growth))
    decade_p = 100 * ((wide_p.loc[1880:2020:10].values / wide_p.loc[1870:2010:10].values) ** 0.1 - 1)
    print(f"money_prices_panel.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.year.min()}-{out.year.max()}; "
          f"U.S. decade money growth vs fig8-3: largest difference {worst:.3f}; highest decade inflation "
          f"{pd.DataFrame(decade_p).max().max():,.0f}%")


def interest_rates_panel(root, raw, names):
    """Short-term (3-month) nominal rates, CPI inflation and the real rate R = i - pi, annual."""
    eo = pd.read_csv(download(EO_URL, "oecd_eo119_IRS_A.csv", raw))
    fin = pd.read_csv(download(FINMARK_URL, "oecd_finmark_IR3TIB_A.csv", raw))
    eo = eo.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    fin = fin.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")
    rows = []
    for iso in sorted((set(eo) | set(fin)) & set(names.index) - {"USA"}):
        rate = eo[iso].dropna() if iso in eo else pd.Series(dtype=float)
        src = pd.Series("OECD EO", index=rate.index)
        if iso in fin:
            extra = fin[iso].dropna()
            overlap = (extra - rate).dropna()
            if rate.empty or overlap.abs().max() < 0.5:     # same series: add the years the EO lacks
                extra = extra[~extra.index.isin(rate.index)]
                rate = pd.concat([rate, extra])
                src = pd.concat([src, pd.Series("OECD MEI", index=extra.index)])
        rows.append(pd.DataFrame({"iso3": iso, "year": rate.index, "short_rate": rate.values,
                                  "rate_source": src.loc[rate.index].values}))
    out = pd.concat(rows)
    infl = pd.read_csv(os.path.join(HERE, "inflation_panel.csv"))[["iso3", "year", "inflation"]]
    out = out.merge(infl, on=["iso3", "year"], how="left")
    us = pd.read_csv(os.path.join(HERE, "fig8-5.csv")).rename(columns={"nominal_tbill_3m": "short_rate",
                                                                      "inflation_cpi": "inflation"})
    us["iso3"], us["rate_source"] = "USA", "FRED TB3MS"
    out = pd.concat([us[["iso3", "year", "short_rate", "rate_source", "inflation"]], out])
    out = out[(out.year >= 1960) & (out.year <= LAST)]
    out["real_rate"] = out.short_rate - out.inflation
    out["country"] = out.iso3.map(names)
    out = out[["iso3", "country", "year", "short_rate", "inflation", "real_rate", "rate_source"]]
    out = out.sort_values(["country", "year"]).round(3)
    out.to_csv(os.path.join(HERE, "interest_rates_panel.csv"), index=False)
    ref = pd.read_csv(os.path.join(HERE, "fig8-5.csv")).set_index("year")
    mine = out[out.iso3 == "USA"].set_index("year")
    usa_eo = (eo["USA"] - ref.nominal_tbill_3m).dropna()
    print(f"interest_rates_panel.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.year.min()}-{out.year.max()}, "
          f"{out.inflation.isna().sum()} rows without inflation; U.S. real rate vs fig8-5: largest difference "
          f"{(mine.real_rate - ref.real_rate).abs().max():.3f}; OECD's U.S. 3-month rate minus the T-bill: "
          f"mean {usa_eo.mean():.2f} points")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    raw = os.path.join(args.macro102, ".work", "ch08", "notebook-raw")
    cpi = us_cpi(root)
    us_money_prices(root, cpi)
    money_supply(root)
    us_money_annual(root)
    inflation_panel(root)
    names = countries(root)
    money_prices_panel(root, names)
    interest_rates_panel(root, raw, names)


if __name__ == "__main__":
    main()
