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
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SUBSET = "original-scanned-book/ch04-a-model-of-production/data/fig4-5/raw/pwt110_subset.csv"
DELTA, G0 = 0.05, 0.03


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
    n23 = out[(out.year == 2023) & out["in_sample"]].shape[0]
    print(f"pwt_production.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}; sample in 2023: {n23} countries")


if __name__ == "__main__":
    main()
