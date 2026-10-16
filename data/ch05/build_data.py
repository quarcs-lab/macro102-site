"""Build the wider data file used by the Chapter 5 notebook widgets.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Input : the Penn World Table 11.0 subset saved by the macro102 /collect-data skill
        (original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv;
        columns countrycode, country, year, rgdpo, pop, csh_i).
Output: pwt_panel.csv next to this script, one row per country and year (1950-2023):
          iso3      ISO 3166 alpha-3 code
          country   PWT country name
          year
          gdp_pc    real GDP per person, output side (rgdpo / pop), 2021 US dollars, rounded
          inv_rate  investment rate, gross capital formation share of GDP (csh_i x 100), percent
          oecd      True for the 24 OECD countries of the textbook's growth figure
Rows with neither gdp_pc nor inv_rate are dropped.
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SUBSET = "original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv"
# The 24 OECD countries of the textbook figure (same list as macro102's get_data.py).
OECD24 = ["IRL", "JPN", "PRT", "ESP", "TUR", "GRC", "ITA", "AUT", "NOR", "FIN", "DEU", "BEL",
          "FRA", "ISL", "NLD", "DNK", "SWE", "GBR", "AUS", "CAN", "NZL", "USA", "LUX", "CHE"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    pwt = pd.read_csv(os.path.join(args.macro102, SUBSET))
    out = pd.DataFrame({
        "iso3": pwt.countrycode,
        "country": pwt.country,
        "year": pwt.year,
        "gdp_pc": (pwt.rgdpo / pwt["pop"]).round(0),
        "inv_rate": (pwt.csh_i * 100).round(2),
        "oecd": pwt.countrycode.isin(OECD24),
    })
    out = out.dropna(subset=["gdp_pc", "inv_rate"], how="all")
    out["gdp_pc"] = out.gdp_pc.astype("Int64")
    out.to_csv(os.path.join(HERE, "pwt_panel.csv"), index=False)
    print(f"pwt_panel.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}, {out.oecd.groupby(out.iso3).first().sum()} OECD")


if __name__ == "__main__":
    main()
