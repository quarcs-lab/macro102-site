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

Multi-country files (conventions §6b):
  oecd_members.csv  iso3, country, joined, in_textbook
                    the 38 OECD member countries in 2026 with the year each joined (oecd.org, "Members and
                    partners"); in_textbook marks the 24 countries of the textbook's Figure 5.8
  regions.csv       iso3, country, region, income_group
                    World Bank region and income group of every country in pwt_panel.csv
                    (api.worldbank.org/v2/country, cached in ../macro102/.work/ch05/notebook-raw/);
                    Taiwan, Anguilla and Montserrat are added by hand
"""
import argparse
import json
import os

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
SUBSET = "original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv"
# The 24 OECD countries of the textbook figure (same list as macro102's get_data.py).
OECD24 = ["IRL", "JPN", "PRT", "ESP", "TUR", "GRC", "ITA", "AUT", "NOR", "FIN", "DEU", "BEL",
          "FRA", "ISL", "NLD", "DNK", "SWE", "GBR", "AUS", "CAN", "NZL", "USA", "LUX", "CHE"]

# The 38 OECD members (2026) and the year each joined; the first 20 are the founding members of 1961
OECD_JOINED = {"AUT": 1961, "BEL": 1961, "CAN": 1961, "DNK": 1961, "FRA": 1961, "DEU": 1961, "GRC": 1961,
               "ISL": 1961, "IRL": 1961, "LUX": 1961, "NLD": 1961, "NOR": 1961, "PRT": 1961, "ESP": 1961,
               "SWE": 1961, "CHE": 1961, "TUR": 1961, "GBR": 1961, "USA": 1961, "ITA": 1962, "JPN": 1964,
               "FIN": 1969, "AUS": 1971, "NZL": 1973, "MEX": 1994, "CZE": 1995, "HUN": 1996, "POL": 1996,
               "KOR": 1996, "SVK": 2000, "CHL": 2010, "SVN": 2010, "ISR": 2010, "EST": 2010, "LVA": 2016,
               "LTU": 2018, "COL": 2020, "CRI": 2021}
EXTRA_REGIONS = {"TWN": ("East Asia & Pacific", "High income"),
                 "AIA": ("Latin America & Caribbean", "High income"),
                 "MSR": ("Latin America & Caribbean", "High income")}


def build_groups(macro102, names):
    """oecd_members.csv and regions.csv: country groups for the multi-country figures."""
    members = pd.DataFrame({"iso3": list(OECD_JOINED), "joined": list(OECD_JOINED.values())})
    members.insert(1, "country", members.iso3.map(names))
    members["in_textbook"] = members.iso3.isin(OECD24)
    members.to_csv(os.path.join(HERE, "oecd_members.csv"), index=False)
    print(f"oecd_members.csv: {len(members)} members, {members.in_textbook.sum()} in the textbook figure")

    path = os.path.join(macro102, ".work", "ch05", "notebook-raw", "wdi_countries.json")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = requests.get("https://api.worldbank.org/v2/country?format=json&per_page=400", timeout=60)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    wb = {c["id"]: (c["region"]["value"].strip(), c["incomeLevel"]["value"].strip())
          for c in json.load(open(path))[1]}
    wb.update(EXTRA_REGIONS)
    rows = [(iso3, name) + wb[iso3] for iso3, name in sorted(names.items())]
    out = pd.DataFrame(rows, columns=["iso3", "country", "region", "income_group"])
    out.to_csv(os.path.join(HERE, "regions.csv"), index=False)
    print(f"regions.csv: {len(out)} countries, {out.region.nunique()} regions")


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
    build_groups(args.macro102, out.groupby("iso3").country.first().to_dict())
    print(f"pwt_panel.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}, {out.oecd.groupby(out.iso3).first().sum()} OECD")


if __name__ == "__main__":
    main()
