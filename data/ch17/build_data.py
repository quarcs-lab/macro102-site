"""Build the wider data files used by the Chapter 17 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under original-scanned-book/ch17-investment/data/):
  table17-1/raw/oecd_DF_CIT_statutory.csv   OECD Corporate Tax Statistics (SDMX DF_CIT), statutory
                                            corporate income tax rates, percent, annual
  fig17-4/raw/fred_USREC.csv                NBER recession indicator, monthly (1 = recession month)
  fig17-4/raw/fred_A006RE1Q156NBEA.csv      gross private domestic investment, percent of GDP, quarterly
  fig17-4/raw/fred_A011RE1Q156NBEA.csv      private residential fixed investment, percent of GDP, quarterly
Outputs (next to this script):
  corporate_tax.csv       country, iso3, year, cit_rate     the 33 jurisdictions of Table 17.1, 2000 to the
                                                            latest year (central-government statutory rate)
  table17-1-book.csv      country, book_rate, book_user_cost   Table 17.1 as printed in the textbook (2022)
  recessions.csv          peak, trough                      NBER recessions that start in 1948 or later
  investment_quarterly.csv  date, total, residential        quarterly shares of GDP (NIPA Table 1.1.10)
  investment_components.csv  iso3, country, year, total, nonres_fixed, residential, inventories, region
                          private investment and its parts, percent of GDP, annual, OECD countries and partners
Downloaded for the multi-country version (cached in ../macro102/.work/ch17/notebook-raw/), OECD Data Explorer:
  National Accounts at a Glance, Chapter 3 (DSD_NAAG@DF_NAAG_III): GFCF (% of GDP), GFCF of general government
    (% of GFCF); Chapter 3B (DSD_NAAG@DF_NAAG_III_GFCF): dwellings (% of GFCF)
  Table 1 (DSD_NAMAIN10@DF_TABLE1_EXPENDITURE): GDP and changes in inventories, national currency, current prices
Checks: the 2022 and 2025 rates reproduce table17-1/data.csv; the annual means of the quarterly total and
residential shares reproduce fig17-4/data.csv within 0.15 percentage points.
"""
import argparse
import os

import pandas as pd
import requests

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
OECD = "https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,"
NAAG_III_URL = OECD + "DSD_NAAG@DF_NAAG_III,1.0/all?dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
NAAG_GFCF_URL = OECD + "DSD_NAAG@DF_NAAG_III_GFCF,1.0/all?dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
TABLE1_URL = OECD + "DSD_NAMAIN10@DF_TABLE1_EXPENDITURE,2.0/A..S1..B1GQ+P5+P51G+P52+P51N....XDC.V..?format=csv"

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch17-investment/data/"

# Table 17.1 of the textbook, in book order: (printed name, ISO3, printed tax rate, printed user cost)
BOOK = [
    ("Brazil", "BRA", 34.0, 12.0), ("Argentina", "ARG", 30.0, 11.3),
    ("Democratic Republic of the Congo", "COD", 30.0, 11.3), ("Kenya", "KEN", 30.0, 11.3),
    ("Nigeria", "NGA", 30.0, 11.3), ("Australia", "AUS", 30.0, 11.3), ("Costa Rica", "CRI", 30.0, 11.3),
    ("Mexico", "MEX", 30.0, 11.3), ("Portugal", "PRT", 30.0, 11.3), ("South Africa", "ZAF", 27.0, 10.8),
    ("France", "FRA", 25.8, 10.6), ("Netherlands", "NLD", 25.8, 10.6), ("India", "IND", 25.2, 10.6),
    ("China", "CHN", 25.0, 10.5), ("Korea", "KOR", 25.0, 10.5), ("Spain", "ESP", 25.0, 10.5),
    ("Italy", "ITA", 24.0, 10.4), ("Japan", "JPN", 23.2, 10.3), ("Israel", "ISR", 23.0, 10.3),
    ("Botswana", "BWA", 22.0, 10.1), ("Indonesia", "IDN", 22.0, 10.1), ("United States", "USA", 21.0, 10.0),
    ("Sweden", "SWE", 20.6, 9.9), ("Saudi Arabia", "SAU", 20.0, 9.9), ("Vietnam", "VNM", 20.0, 9.9),
    ("Poland", "POL", 19.0, 9.8), ("United Kingdom", "GBR", 19.0, 9.8), ("Hong Kong", "HKG", 16.5, 9.5),
    ("Germany", "DEU", 15.8, 9.4), ("Ireland", "IRL", 12.5, 9.0), ("Chile", "CHL", 10.0, 8.8),
    ("Switzerland", "CHE", 8.5, 8.6), ("Cayman Islands", "CYM", 0.0, 7.9),
]


def corporate_tax(root):
    """Statutory central-government CIT rates of the 33 book jurisdictions, one row per country and year."""
    raw = pd.read_csv(os.path.join(root, "table17-1/raw/oecd_DF_CIT_statutory.csv"),
                      usecols=["REF_AREA", "MEASURE", "TARGETING", "SECTOR", "TIME_PERIOD", "OBS_VALUE"])
    st = raw[(raw.MEASURE == "CIT") & (raw.TARGETING == "ST") & (raw.SECTOR == "S1311")]
    names = {iso: name for name, iso, _, _ in BOOK}
    st = st[st.REF_AREA.isin(names)].dropna(subset=["OBS_VALUE"])
    out = pd.DataFrame({"country": st.REF_AREA.map(names), "iso3": st.REF_AREA,
                        "year": st.TIME_PERIOD.astype(int), "cit_rate": st.OBS_VALUE.round(4)})
    order = {iso: i for i, (_, iso, _, _) in enumerate(BOOK)}
    out = out.assign(o=out.iso3.map(order)).sort_values(["o", "year"]).drop(columns="o")
    out = out[out.year >= 2000]
    out.to_csv(os.path.join(HERE, "corporate_tax.csv"), index=False)
    print(f"corporate_tax.csv: {out.iso3.nunique()} jurisdictions, {out.year.min()}-{out.year.max()}, {len(out)} rows")

    book = pd.DataFrame([(n, r, u) for n, _, r, u in BOOK], columns=["country", "book_rate", "book_user_cost"])
    book.to_csv(os.path.join(HERE, "table17-1-book.csv"), index=False)
    print(f"table17-1-book.csv: {len(book)} rows")
    return out


def validate_tax(out, root):
    """The 2022 and 2025 rates must equal collect-data's table17-1/data.csv."""
    table = pd.read_csv(os.path.join(root, "table17-1/data.csv")).set_index("item")
    for year, col in [(2022, "cit_rate_book_2022"), (2025, "cit_rate_latest_2025")]:
        ours = out[out.year == year].set_index("country").cit_rate
        diff = (ours - table[col]).abs().max()
        if not diff < 1e-3:
            raise SystemExit(f"{year}: corporate_tax.csv differs from table17-1/data.csv by {diff}")
    print("validated: the 2022 and 2025 rates reproduce table17-1/data.csv")


def recessions(root):
    """(peak, trough) of every NBER recession since 1948: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig17-4/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1948-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def investment_quarterly(root):
    """Quarterly investment shares of GDP; annual means are checked against fig17-4/data.csv."""
    frames = []
    for sid, name in [("A006RE1Q156NBEA", "total"), ("A011RE1Q156NBEA", "residential")]:
        raw = pd.read_csv(os.path.join(root, f"fig17-4/raw/fred_{sid}.csv"), parse_dates=["observation_date"])
        frames.append(raw.set_index("observation_date")[sid].rename(name))
    out = pd.concat(frames, axis=1).dropna()
    out.index.name = "date"
    annual = out.groupby(out.index.year).mean()
    fig = pd.read_csv(os.path.join(root, "fig17-4/data.csv")).set_index("year")
    both = annual.index.intersection(fig.index)
    for col in ["total", "residential"]:
        diff = (annual.loc[both, col] - fig.loc[both, col]).abs().max()
        if not diff < 0.15:
            raise SystemExit(f"investment_quarterly.csv {col}: annual means differ from fig17-4/data.csv by {diff:.2f}")
    out.index = out.index.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "investment_quarterly.csv"))
    print(f"investment_quarterly.csv: {len(out)} quarters, {out.index[0]} to {out.index[-1]}; "
          f"annual means reproduce fig17-4/data.csv within 0.15 points")


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


def naag(path, measure, unit):
    """One NAAG measure as a table: rows are years, columns are ISO3 codes."""
    raw = pd.read_csv(path, low_memory=False, usecols=["REF_AREA", "MEASURE", "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE"])
    raw = raw[(raw.MEASURE == measure) & (raw.UNIT_MEASURE == unit)]
    return raw.pivot_table(index="TIME_PERIOD", columns="REF_AREA", values="OBS_VALUE")


def investment_components(cache):
    """Figure 17.4 for every OECD country: private investment = GFCF minus government GFCF plus inventories."""
    iii = cached(NAAG_III_URL, cache, "oecd_NAAG_III_all.csv")
    gfcf = naag(iii, "P51G", "PT_B1GQ")                                    # all GFCF, % of GDP
    gov = naag(iii, "P51GS13", "PT_P51G")                                  # government share of GFCF, %
    dwell = naag(cached(NAAG_GFCF_URL, cache, "oecd_NAAG_III_GFCF_all.csv"), "P51G_N111G", "PT_P51G")
    t1 = pd.read_csv(cached(TABLE1_URL, cache, "oecd_TABLE1_B1GQ_P5_P51G_P52_XDC.csv"))
    x = t1.pivot_table(index="TIME_PERIOD", columns=["TRANSACTION", "REF_AREA"], values="OBS_VALUE")
    inventories = 100 * x["P52"] / x["B1GQ"]
    private_fixed = gfcf * (1 - gov / 100)
    residential = gfcf * dwell / 100                                       # dwellings, all sectors
    parts = {"total": private_fixed + inventories, "nonres_fixed": private_fixed - residential,
             "residential": residential, "inventories": inventories}
    long = pd.concat({k: v.stack() for k, v in parts.items()}, axis=1).dropna().round(2)
    long.index.names = ["year", "iso"]
    out = tidy(long.reset_index(), "iso", "year", list(parts))
    out.to_csv(os.path.join(HERE, "investment_components.csv"), index=False)
    print(f"investment_components.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}")
    return out


def validate_components(out):
    """The U.S. rows must be close to the BEA shares of fig17-4.csv (the OECD splits investment a little differently)."""
    us = out[out.iso3 == "USA"].set_index("year")
    ref = pd.read_csv(os.path.join(HERE, "fig17-4.csv")).set_index("year")
    gaps = {}
    for col in ["total", "nonres_fixed", "residential", "inventories"]:
        gaps[col] = (us[col] - ref[col]).dropna().abs().max()
    print("U.S. check, largest |gap| from fig17-4.csv (points of GDP): "
          + ", ".join(f"{k} {v:.2f}" for k, v in gaps.items()))
    if max(gaps.values()) > 0.6:
        raise SystemExit("investment_components.csv: the U.S. rows are too far from fig17-4.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work", "ch17", "notebook-raw")
    validate_tax(corporate_tax(root), root)
    recessions(root)
    investment_quarterly(root)
    validate_components(investment_components(cache))
    size = os.path.getsize(os.path.join(HERE, "investment_components.csv"))
    if size > 1_000_000:
        raise SystemExit(f"investment_components.csv is {size:,} bytes, above the 1 MB limit")


if __name__ == "__main__":
    main()
