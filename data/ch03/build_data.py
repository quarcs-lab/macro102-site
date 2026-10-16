"""Build the wider data files used by the Chapter 3 notebook widgets.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch03-an-overview-of-long-run-economic-growth/data/):
  fig3-6/raw/mpd2023_subset.csv          Maddison Project Database 2023: countrycode, country, region, year, gdppc, pop
  fig3-6/raw/fred_A191RD3A086NBEA.csv    U.S. GDP deflator (BEA via FRED), to express 2011 dollars in 2022 dollars
  fig3-7/raw/pwt110_subset.csv           Penn World Table 11.0: countrycode, country, year, rgdpe, pop
Outputs (next to this script):
  maddison_panel.csv   iso3, country, year, gdppc       annual 1870-2022, 7 countries, 2022 dollars
  pwt_income.csv       iso3, country, year, gdp_pc, y_rel_us_2019, pop_millions, in_sample
                       1950-2023; gdp_pc = rgdpe / pop (2021 dollars); y_rel_us_2019 = gdp_pc / U.S. gdp_pc in 2019;
                       in_sample = data in 1960, 2019 and 2023 (the textbook's 111 countries)
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch03-an-overview-of-long-run-economic-growth/data/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)

    # Maddison: 2011 dollars -> 2022 dollars with the U.S. GDP deflator (same factor as fig3-6.csv)
    defl = pd.read_csv(os.path.join(root, "fig3-6/raw/fred_A191RD3A086NBEA.csv"))
    defl["year"] = defl.observation_date.str[:4].astype(int)
    defl = defl.set_index("year").A191RD3A086NBEA
    factor = defl[2022] / defl[2011]
    mpd = pd.read_csv(os.path.join(root, "fig3-6/raw/mpd2023_subset.csv"))
    mpd = mpd[(mpd.year >= 1870) & (mpd.year <= 2022)].dropna(subset=["gdppc"])
    panel = pd.DataFrame({"iso3": mpd.countrycode, "country": mpd.country, "year": mpd.year,
                          "gdppc": (mpd.gdppc * factor).round(0).astype(int)})
    panel.to_csv(os.path.join(HERE, "maddison_panel.csv"), index=False)
    print(f"maddison_panel.csv: {len(panel)} rows, {panel.iso3.nunique()} countries, "
          f"{panel.year.min()}-{panel.year.max()}, factor 2011->2022 = {factor:.4f}")

    # Penn World Table: GDP per person (expenditure side, as fig3-7/fig3-8) and population
    pwt = pd.read_csv(os.path.join(root, "fig3-7/raw/pwt110_subset.csv"))
    pwt = pwt[pwt.year <= 2023].dropna(subset=["rgdpe", "pop"])
    out = pd.DataFrame({"iso3": pwt.countrycode, "country": pwt.country, "year": pwt.year,
                        "gdp_pc": pwt.rgdpe / pwt["pop"], "pop_millions": pwt["pop"].round(3)})
    us2019 = out[(out.iso3 == "USA") & (out.year == 2019)].gdp_pc.iloc[0]
    out["y_rel_us_2019"] = (out.gdp_pc / us2019).round(5)
    out["gdp_pc"] = out.gdp_pc.round(1)
    years = out.groupby("iso3").year.agg(set)
    keep = set(years[[{1960, 2019, 2023} <= ys for ys in years]].index)
    out["in_sample"] = out.iso3.isin(keep)
    out = out[["iso3", "country", "year", "gdp_pc", "y_rel_us_2019", "pop_millions", "in_sample"]]
    out.to_csv(os.path.join(HERE, "pwt_income.csv"), index=False)
    print(f"pwt_income.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}, "
          f"{len(keep)} in the sample")


if __name__ == "__main__":
    main()
