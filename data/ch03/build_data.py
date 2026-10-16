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

Multi-country files (conventions §6b), downloaded from the public source and cached in
../macro102/.work/ch03/notebook-raw/:
  mpd2023_web.xlsx     Maddison Project Database 2023, sheet "Full data" (DataverseNL, doi:10.34894/INZBF2)
Outputs:
  maddison_world.csv   iso3, country, region, year, gdppc, pop_thousands
                       every Maddison country, every available year 1870-2022; gdppc in 2022 dollars
                       (2011 dollars x the U.S. GDP deflator ratio, as maddison_panel.csv)
  maddison_longrun.csv iso3, country, region, year, gdppc_x500
                       every Maddison country at the plotted years of Figure 3.1 (1, 1000, ..., 2022),
                       GDP per person as a multiple of 500 dollars (2011 prices); Maddison 2023 only
                       (fig3-1.csv also splices in Maddison 2010 for the six book countries' earliest years)
"""
import argparse
import os

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
MADDISON_DOI, MADDISON_FILE = "doi:10.34894/INZBF2", "mpd2023_web.xlsx"
FIG31_YEARS = [1, 1000, 1500, 1600, 1700, 1820, 1870, 1900, 1913, 1929, 1950, 1960, 1970, 1980, 1990,
               2000, 2010, 2020, 2022]
DATA = "original-scanned-book/ch03-an-overview-of-long-run-economic-growth/data/"


def dataverse_file(doi, filename, raw):
    """Download one file of a DataverseNL dataset into the raw cache (once) and return its path."""
    os.makedirs(raw, exist_ok=True)
    path = os.path.join(raw, filename)
    if not os.path.exists(path):
        files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                             params={"persistentId": doi}, timeout=60).json()["data"]
        fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == filename][0]
        r = requests.get(f"https://dataverse.nl/api/access/datafile/{fid}", timeout=300)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def build_maddison_world(macro102, factor):
    """maddison_world.csv and maddison_longrun.csv: every country of the Maddison Project 2023."""
    raw = os.path.join(macro102, ".work", "ch03", "notebook-raw")
    mpd = pd.read_excel(dataverse_file(MADDISON_DOI, MADDISON_FILE, raw), sheet_name="Full data")
    mpd = mpd.rename(columns={"countrycode": "iso3"})

    world = mpd[(mpd.year >= 1870) & (mpd.year <= 2022)].dropna(subset=["gdppc"]).copy()
    world["gdppc"] = (world.gdppc * factor).round(0).astype(int)
    world["pop_thousands"] = world["pop"].round(0).astype("Int64")
    world = world[["iso3", "country", "region", "year", "gdppc", "pop_thousands"]]
    world.to_csv(os.path.join(HERE, "maddison_world.csv"), index=False)
    print(f"maddison_world.csv: {len(world)} rows, {world.iso3.nunique()} countries, "
          f"{world.year.min()}-{world.year.max()}, {os.path.getsize(os.path.join(HERE, 'maddison_world.csv')):,} bytes")

    # Validation 1: the seven countries of Figure 3.6 at its benchmark years equal fig3-6.csv
    fig36 = pd.read_csv(os.path.join(HERE, "fig3-6.csv")).set_index("year")
    worst = 0
    for col in fig36.columns:
        iso = col.split("_")[1].upper()
        mine = world[world.iso3 == iso].set_index("year").gdppc.reindex(fig36.index)
        worst = max(worst, (mine - fig36[col]).abs().max())
    print(f"  check vs fig3-6.csv: largest difference {worst} dollars")
    # Validation 2: the U.S. rows against the BEA-based fig3-2.csv / fig3-9.csv (same 2022 dollars)
    us = world[world.iso3 == "USA"].set_index("year")
    fig39 = pd.read_csv(os.path.join(HERE, "fig3-9.csv")).set_index("year")
    ratio = (us.gdppc / fig39.gdppc).dropna()
    pop = (us.pop_thousands.astype(float) / fig39.population_thousands).dropna()
    print(f"  check vs fig3-9.csv (U.S.): Maddison/BEA GDP per person 1870-1928 {ratio.loc[:1928].min():.3f}-"
          f"{ratio.loc[:1928].max():.3f}, 1929-2022 {ratio.loc[1929:].min():.3f}-{ratio.loc[1929:].max():.3f}; "
          f"population {pop.min():.3f}-{pop.max():.3f}")

    longrun = mpd[mpd.year.isin(FIG31_YEARS)].dropna(subset=["gdppc"]).copy()
    longrun["gdppc_x500"] = (longrun.gdppc / 500).round(2)
    longrun = longrun[["iso3", "country", "region", "year", "gdppc_x500"]]
    longrun.to_csv(os.path.join(HERE, "maddison_longrun.csv"), index=False)
    print(f"maddison_longrun.csv: {len(longrun)} rows, {longrun.iso3.nunique()} countries, "
          f"{os.path.getsize(os.path.join(HERE, 'maddison_longrun.csv')):,} bytes")
    # Validation 3: where fig3-1.csv uses Maddison 2023 (no splice), the values agree
    fig31 = pd.read_csv(os.path.join(HERE, "fig3-1.csv")).set_index("year")
    worst = 0
    for col in fig31.columns:
        iso = col.split("_")[-1].upper()
        mine = longrun[longrun.iso3 == iso].set_index("year").gdppc_x500
        both = pd.concat([mine, fig31[col]], axis=1).dropna()
        worst = max(worst, (both.iloc[:, 0] - both.iloc[:, 1]).abs().max())
    print(f"  check vs fig3-1.csv (years Maddison 2023 covers): largest difference {worst:.2f}")


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
    build_maddison_world(args.macro102, factor)
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
