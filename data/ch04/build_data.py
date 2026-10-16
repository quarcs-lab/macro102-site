"""Build the wider data file used by the Chapter 4 notebook widgets.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Input : the Penn World Table 11.0 subset saved by the macro102 /collect-data skill
        (original-scanned-book/ch04-a-model-of-production/data/fig4-5/raw/pwt110_subset.csv;
        columns countrycode, country, year, rgdpo, pop, csh_i).
Output: pwt_production.csv next to this script, one row per country and year (1950-2023):
          iso3, country, year
          gdp_pc    real GDP per person, output side (rgdpo / pop), 2021 US dollars
          k_pc      capital per person, 2021 US dollars (perpetual inventory, see below)
          y_rel     gdp_pc relative to the United States in the same year (U.S. = 1)
          k_rel     k_pc relative to the United States in the same year (U.S. = 1)
          tfp       implied TFP, y_rel / k_rel^(1/3) (equation 4.11)
          in_sample True if the country has rgdpo, pop and csh_i in 1960 and in that year
                    (the textbook's ~110-country sample for Figures 4.5 and 4.7)
Capital is the collect-data rule (macro102 get_data.py, capital_pc): investment I = csh_i x rgdpo;
K in the first year with investment = I / (0.03 + 0.05); K(t+1) = 0.95 K(t) + I(t). K in year T
is the stock at the start of the year (investment through T-1). A gap in investment ends the series.

Multi-country files (conventions §6b), downloaded from public sources and cached in
../macro102/.work/ch04/notebook-raw/:
  share_prices.csv  iso3, country, date, real_index
                    monthly real share prices, 2015 average = 100, for the 40 countries whose OECD
                    "total share prices for all shares" index is on FRED (SPASTT01{CC}M661N, 2015 = 100),
                    deflated by the BIS long consumer price series (WS_LONG_CPI, M.{CC}.628);
                    months coded 0 are dropped, and Brazil starts in 1993-01 (a series break)
  regions.csv       iso3, country, region, income_group
                    the World Bank region and income group of every country in pwt_production.csv
                    (api.worldbank.org/v2/country); Taiwan, Anguilla and Montserrat are added by hand
"""
import argparse
import json
import os

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SUBSET = "original-scanned-book/ch04-a-model-of-production/data/fig4-5/raw/pwt110_subset.csv"
DELTA, G0 = 0.05, 0.03
# FRED's two-letter codes of the OECD share price indices, with the ISO3 code used everywhere else
SHARE_CODES = {"AU": "AUS", "AT": "AUT", "BE": "BEL", "CA": "CAN", "CL": "CHL", "CZ": "CZE", "DK": "DNK",
               "EE": "EST", "FI": "FIN", "FR": "FRA", "DE": "DEU", "GR": "GRC", "HU": "HUN", "IS": "ISL",
               "IE": "IRL", "IL": "ISR", "IT": "ITA", "JP": "JPN", "KR": "KOR", "LU": "LUX", "MX": "MEX",
               "NL": "NLD", "NZ": "NZL", "NO": "NOR", "PL": "POL", "PT": "PRT", "SK": "SVK", "SI": "SVN",
               "ES": "ESP", "SE": "SWE", "CH": "CHE", "TR": "TUR", "GB": "GBR", "US": "USA", "BR": "BRA",
               "CN": "CHN", "IN": "IND", "ID": "IDN", "RU": "RUS", "ZA": "ZAF"}
# Series breaks: Brazil's index jumps 50-fold in January 1993 (a rebasing of the Bovespa, not a boom)
FIRST_MONTH = {"BR": "1993-01"}
EXTRA_REGIONS = {"TWN": ("East Asia & Pacific", "High income"),
                 "AIA": ("Latin America & Caribbean", "High income"),
                 "MSR": ("Latin America & Caribbean", "High income")}


def capital_path(g):
    """Beginning-of-year capital stock for one country (a Series indexed by year)."""
    g = g.set_index("year").sort_index()
    inv = (g.csh_i * g.rgdpo).dropna()
    out = {}
    if inv.empty:
        return pd.Series(out, dtype=float)
    t = int(inv.index[0])
    k = inv.iloc[0] / (G0 + DELTA)
    while t in inv.index:
        k = (1 - DELTA) * k + inv[t]     # stock at the start of year t + 1
        t += 1
        out[t] = k
    return pd.Series(out, dtype=float)


def cached(url, path):
    """Download url to path once (requests' default User-Agent); later runs read the cache."""
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def build_share_prices(raw, names):
    """share_prices.csv: OECD share price indices deflated by the BIS consumer price index."""
    cpi = pd.read_csv(cached("https://stats.bis.org/api/v1/data/WS_LONG_CPI/M..628?format=csv",
                             os.path.join(raw, "bis_long_cpi_monthly.csv")))
    cpi = cpi.dropna(subset=["OBS_VALUE"]).set_index(["REF_AREA", "TIME_PERIOD"]).OBS_VALUE
    parts = []
    for cc, iso3 in SHARE_CODES.items():
        sid = f"SPASTT01{cc}M661N"
        sp = pd.read_csv(cached(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}",
                                os.path.join(raw, "fred", sid + ".csv"))).dropna()
        sp = sp[sp[sid] > 0]                     # FRED codes a few missing months as 0 (e.g. Slovenia 1994)
        sp = sp[sp.observation_date.str[:7] >= FIRST_MONTH.get(cc, "")]
        sp["date"] = sp.observation_date.str[:7]
        sp = sp.set_index("date")[sid]
        real = (sp / cpi.loc[cc].reindex(sp.index)).dropna()
        real = 100 * real / real[real.index.str.startswith("2015")].mean()
        parts.append(pd.DataFrame({"iso3": iso3, "country": names.get(iso3, iso3), "date": real.index,
                                   "real_index": [float(f"{v:.4g}") for v in real]}))
    out = pd.concat(parts, ignore_index=True)
    path = os.path.join(HERE, "share_prices.csv")
    out.to_csv(path, index=False)
    print(f"share_prices.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.date.min()} to "
          f"{out.date.max()}, {os.path.getsize(path):,} bytes")
    # Validation: the U.S. rows against the textbook-figure series (real S&P 500, fig4-3.csv)
    sp500 = pd.read_csv(os.path.join(HERE, "fig4-3.csv"))
    sp500 = sp500.set_index(sp500.date.str[:7]).sp500_real
    us = out[out.iso3 == "USA"].set_index("date").real_index
    both = pd.concat([us, sp500], axis=1, join="inner").dropna()
    growth = (both.iloc[-1] / both.iloc[0]) ** (12 / (len(both) - 1)) - 1
    corr = both.pct_change().corr().iloc[0, 1]
    print(f"  check vs fig4-3.csv (U.S., {both.index[0]} to {both.index[-1]}): average real growth "
          f"{100 * growth.iloc[0]:.2f}% (OECD) vs {100 * growth.iloc[1]:.2f}% (S&P 500) a year; "
          f"correlation of monthly changes {corr:.3f}")


def build_regions(raw, pwt_countries):
    """regions.csv: World Bank region and income group for every PWT country."""
    info = json.load(open(cached("https://api.worldbank.org/v2/country?format=json&per_page=400",
                                 os.path.join(raw, "wdi_countries.json"))))[1]
    wb = {c["id"]: (c["region"]["value"].strip(), c["incomeLevel"]["value"].strip()) for c in info}
    wb.update(EXTRA_REGIONS)
    rows = [(iso3, name) + wb[iso3] for iso3, name in pwt_countries.items()]
    out = pd.DataFrame(rows, columns=["iso3", "country", "region", "income_group"]).sort_values("iso3")
    out.to_csv(os.path.join(HERE, "regions.csv"), index=False)
    print(f"regions.csv: {len(out)} countries, {out.region.nunique()} regions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    pwt = pd.read_csv(os.path.join(args.macro102, SUBSET))
    pwt = pwt[pwt.year <= 2023]

    parts = []
    for iso3, g in pwt.groupby("countrycode"):
        K = capital_path(g)
        g = g.set_index("year")
        parts.append(pd.DataFrame({"iso3": iso3, "country": g.country, "year": g.index,
                                   "gdp_pc": g.rgdpo / g["pop"], "k_pc": K.reindex(g.index) / g["pop"]}))
    out = pd.concat(parts, ignore_index=True).dropna(subset=["gdp_pc"])

    usa = out[out.iso3 == "USA"].set_index("year")
    out["y_rel"] = out.gdp_pc / out.year.map(usa.gdp_pc)
    out["k_rel"] = out.k_pc / out.year.map(usa.k_pc)
    out["tfp"] = out.y_rel / out.k_rel ** (1 / 3)

    full = pwt.dropna(subset=["rgdpo", "pop", "csh_i"])
    have = full.groupby("countrycode").year.agg(set)
    in1960 = set(have[have.map(lambda ys: 1960 in ys)].index)
    keys = set(zip(full.countrycode, full.year))
    out["in_sample"] = [c in in1960 and (c, y) in keys for c, y in zip(out.iso3, out.year)]

    out["gdp_pc"] = out.gdp_pc.round(1)
    out["k_pc"] = out.k_pc.round(0)
    for col in ("y_rel", "k_rel", "tfp"):
        out[col] = out[col].round(5)
    out.to_csv(os.path.join(HERE, "pwt_production.csv"), index=False)
    raw = os.path.join(args.macro102, ".work", "ch04", "notebook-raw")
    names = out.groupby("iso3").country.first().to_dict()
    build_share_prices(raw, names)
    build_regions(raw, names)
    n23 = out[(out.year == 2023) & out["in_sample"]].shape[0]
    print(f"pwt_production.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}; sample in 2023: {n23} countries")


if __name__ == "__main__":
    main()
