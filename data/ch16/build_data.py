"""Build the wider data files used by the Chapter 16 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch16-consumption/data/):
  ex08/raw/fred_CMDEBT.csv                 household and nonprofit debt, millions of dollars, quarterly (FRED, current)
  ex08/raw/fred_GDP.csv                    nominal GDP, billions of dollars, SAAR, quarterly (FRED, current)
  ex08/raw/alfred_CMDEBT_2023-03-30.csv    the same debt series as published on 2023-03-30, in BILLIONS of dollars
  ex08/raw/alfred_GDP_2023-03-30.csv       nominal GDP as published on 2023-03-30, billions of dollars
  fig16-4/raw/fred_PSAVERT.csv             personal saving rate, percent of disposable income, monthly, SA
Downloaded for the multi-country versions (cached in ../macro102/.work/ch16/notebook-raw/):
  BIS total credit statistics (WS_TC): credit to households and NPISHs from all sectors, market value, % of GDP,
    adjusted for breaks, quarterly, every reporting country
  OECD National Accounts at a Glance, Chapter 5 Households (DSD_NAAG@DF_NAAG_V), annual: net saving of households
    and NPISH (% of net disposable income); per person, in US dollars at PPP: net financial worth, dwellings, land
    and gross disposable income of households and NPISH
Outputs (next to this script):
  debt_levels.csv          date, debt_millions, gdp_billions, debt_billions_2023, gdp_billions_2023
                           quarterly, 1970Q1 on; the two *_2023 columns end in 2022Q4
  saving_rate_monthly.csv  date, saving_rate        monthly, 1970-01 on
  household_debt.csv       iso3, country, date, debt_gdp, region         BIS, quarterly, 44 countries
  saving_rates.csv         iso3, country, year, saving_rate, region      OECD, annual, 36 countries
  household_wealth.csv     iso3, country, year, net_worth_ratio, region  OECD, annual, 28 countries
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
BIS_URL = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q..H.A.M.770.A?format=csv"
NAAG_URL = ("https://sdmx.oecd.org/public/rest/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_V,1.0/all"
            "?dimensionAtObservation=AllDimensions&format=csvfilewithlabels")

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch16-consumption/data/"
START = "1970-01-01"


def fred(root, path):
    """One FRED series as a Series indexed by date (blank cells become NaN)."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def debt_levels(root):
    out = pd.DataFrame({
        "debt_millions": fred(root, "ex08/raw/fred_CMDEBT.csv"),
        "gdp_billions": fred(root, "ex08/raw/fred_GDP.csv"),
        "debt_billions_2023": fred(root, "ex08/raw/alfred_CMDEBT_2023-03-30.csv"),
        "gdp_billions_2023": fred(root, "ex08/raw/alfred_GDP_2023-03-30.csv"),
    })
    out = out[(out.index >= START) & out.gdp_billions.notna() & out.debt_millions.notna()]
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "debt_levels.csv"), date_format="%Y-%m-%d")
    print(f"debt_levels.csv: {len(out)} quarters, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"2023 vintage to {out.debt_billions_2023.last_valid_index():%Y-%m}")
    return out


def saving_monthly(root):
    s = fred(root, "fig16-4/raw/fred_PSAVERT.csv")
    out = s[s.index >= START].dropna().rename("saving_rate").to_frame()
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "saving_rate_monthly.csv"), date_format="%Y-%m-%d")
    print(f"saving_rate_monthly.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}")
    return out


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


def household_debt(cache):
    """BIS credit to households and NPISHs, % of GDP, quarterly (Figure 16.3 for every BIS country)."""
    raw = pd.read_csv(cached(BIS_URL, cache, "bis_WS_TC_households_pct_gdp.csv"))
    iso2 = {v[2]: k for k, v in COUNTRIES.items()}
    raw["iso"] = raw.BORROWERS_CTY.map(iso2)                 # aggregates (euro area, G20, ...) are dropped
    year, q = raw.TIME_PERIOD.str.split("-Q", expand=True).astype(int).T.values
    raw["date"] = pd.to_datetime(dict(year=year, month=3 * q - 2, day=1))
    raw["debt_gdp"] = raw.OBS_VALUE.round(1)
    out = tidy(raw[raw.date >= START], "iso", "date", ["debt_gdp"])
    out.to_csv(os.path.join(HERE, "household_debt.csv"), index=False, date_format="%Y-%m-%d")
    print(f"household_debt.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.date.min():%Y-%m} to {out.date.max():%Y-%m}")
    return out


def oecd_households(cache):
    """OECD net saving rate and net worth of households and NPISH, % of net disposable income, annual."""
    raw = pd.read_csv(cached(NAAG_URL, cache, "oecd_NAAG_V_all.csv"), low_memory=False,
                      usecols=["REF_AREA", "MEASURE", "UNIT_MEASURE", "TIME_PERIOD", "OBS_VALUE"])
    raw = raw[raw.UNIT_MEASURE.isin(["PT_B6N_S1M", "USD_PPP_PS"])]
    wide = raw.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="MEASURE", values="OBS_VALUE").reset_index()
    wide = wide.rename(columns={"TIME_PERIOD": "year"})
    wide["saving_rate"] = wide.B8NS1M.round(2)
    # Household net worth = net financial worth + dwellings + land (the bulk of households' non-financial assets;
    # the OECD's total non-financial assets exist for only 10 countries), in years of gross disposable income.
    # NAAG's measure LES1M_B90, labelled "net worth", is in fact total financial ASSETS (codes LE, F, A): not used.
    wealth = wide.LES1M_BF90_POP + wide.LES1M_N111N_POP + wide.LES1M_N211N_POP
    wide["net_worth_ratio"] = (wealth / wide.B6GS1M_POP).round(3)
    saving = tidy(wide[wide.year >= 1970], "REF_AREA", "year", ["saving_rate"])
    wealth = tidy(wide[wide.year >= 1970], "REF_AREA", "year", ["net_worth_ratio"])
    saving.to_csv(os.path.join(HERE, "saving_rates.csv"), index=False)
    wealth.to_csv(os.path.join(HERE, "household_wealth.csv"), index=False)
    for name, df in [("saving_rates.csv", saving), ("household_wealth.csv", wealth)]:
        print(f"{name}: {len(df)} rows, {df.iso3.nunique()} countries, {df.year.min()} to {df.year.max()}")
    return saving, wealth


def validate_us(debt, saving, wealth, monthly):
    """The U.S. rows measure the same concepts as the textbook files, with other GDP and income definitions."""
    us = debt[debt.iso3 == "USA"].set_index("date").debt_gdp
    ref3 = pd.read_csv(os.path.join(HERE, "fig16-3.csv"), parse_dates=["date"]).set_index("date").debt_gdp_pct
    gap3 = (us - ref3).dropna()
    rate = monthly.saving_rate
    annual = rate.groupby(rate.index.year).mean()[rate.groupby(rate.index.year).count() == 12]
    gap4 = (saving[saving.iso3 == "USA"].set_index("year").saving_rate - annual).dropna()
    ref5 = pd.read_csv(os.path.join(HERE, "fig16-5.csv"), parse_dates=["date"]).set_index("date").networth_dpi_ratio
    ref5 = ref5.groupby(ref5.index.year).mean()
    ratio5 = (wealth[wealth.iso3 == "USA"].set_index("year").net_worth_ratio / ref5).dropna()
    print(f"U.S. check: BIS debt minus fig16-3.csv: mean {gap3.mean():+.1f}, largest |gap| {gap3.abs().max():.1f} points "
          f"({len(gap3)} quarters, correlation {us.corr(ref3):.3f})")
    print(f"U.S. check: OECD saving rate minus annual PSAVERT: mean {gap4.mean():+.2f}, largest |gap| "
          f"{gap4.abs().max():.2f} points ({gap4.index.min()}-{gap4.index.max()})")
    print(f"U.S. check: OECD net worth ratio / fig16-5.csv (Fed): {ratio5.min():.3f} to {ratio5.max():.3f}, "
          f"mean {ratio5.mean():.3f} ({ratio5.index.min()}-{ratio5.index.max()})")
    if gap3.abs().max() > 6 or gap4.abs().max() > 3 or ratio5.min() < 0.9 or ratio5.max() > 1.1:
        raise SystemExit("U.S. validation of the multi-country files failed")


def validate(levels, monthly):
    """The ratio and the quarterly means must reproduce collect-data's fig16-3.csv and fig16-4.csv."""
    ref3 = pd.read_csv(os.path.join(HERE, "fig16-3.csv"), parse_dates=["date"]).set_index("date").debt_gdp_pct
    ratio = 100 * (levels.debt_millions / 1000) / levels.gdp_billions
    gap3 = (ratio - ref3).abs().max()
    ref4 = pd.read_csv(os.path.join(HERE, "fig16-4.csv"), parse_dates=["date"]).set_index("date").saving_rate
    q = monthly.saving_rate.resample("QS")
    quarterly = q.mean()[q.count() == 3]
    gap4 = (quarterly - ref4).abs().max()
    same = quarterly.index.equals(ref4.index) and ratio.index.equals(ref3.index)
    print(f"validation: debt ratio vs fig16-3.csv max gap {gap3:.4f}; quarterly saving vs fig16-4.csv "
          f"max gap {gap4:.4f}; same quarters: {same}")
    if gap3 > 0.01 or gap4 > 0.01 or not same:
        raise SystemExit("validation failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work", "ch16", "notebook-raw")
    levels = debt_levels(root)
    monthly = saving_monthly(root)
    validate(levels, monthly)
    debt = household_debt(cache)
    saving, wealth = oecd_households(cache)
    validate_us(debt, saving, wealth, monthly)
    for name in ["household_debt.csv", "saving_rates.csv", "household_wealth.csv"]:
        size = os.path.getsize(os.path.join(HERE, name))
        if size > 1_000_000:
            raise SystemExit(f"{name} is {size:,} bytes, above the 1 MB limit")


if __name__ == "__main__":
    main()
