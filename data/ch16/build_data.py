"""Build the wider data files used by the Chapter 16 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch16-consumption/data/):
  ex08/raw/fred_CMDEBT.csv                 household and nonprofit debt, millions of dollars, quarterly (FRED, current)
  ex08/raw/fred_GDP.csv                    nominal GDP, billions of dollars, SAAR, quarterly (FRED, current)
  ex08/raw/alfred_CMDEBT_2023-03-30.csv    the same debt series as published on 2023-03-30, in BILLIONS of dollars
  ex08/raw/alfred_GDP_2023-03-30.csv       nominal GDP as published on 2023-03-30, billions of dollars
  fig16-4/raw/fred_PSAVERT.csv             personal saving rate, percent of disposable income, monthly, SA
Outputs (next to this script):
  debt_levels.csv          date, debt_millions, gdp_billions, debt_billions_2023, gdp_billions_2023
                           quarterly, 1970Q1 on; the two *_2023 columns end in 2022Q4
  saving_rate_monthly.csv  date, saving_rate        monthly, 1970-01 on
"""
import argparse
import os

import pandas as pd

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
    levels = debt_levels(root)
    monthly = saving_monthly(root)
    validate(levels, monthly)


if __name__ == "__main__":
    main()
