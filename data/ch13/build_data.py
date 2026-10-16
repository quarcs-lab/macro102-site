"""Build the wider data files used by the Chapter 13 notebook widgets.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs: the raw downloads saved by the macro102 /collect-data skill in
        original-scanned-book/ch13-stabilization-policy-and-the-as-ad-framework/data/
          fig13-16/raw/fred_FEDFUNDS.csv, fred_JCXFE.csv
          fig13-17/raw/fred_GDPC1.csv, fred_GDPPOT.csv, fred_CPIAUCSL.csv,
                       alfred_GDPC1_2023-03-30.csv, alfred_GDPPOT_2023-03-30.csv
Outputs (next to this script):
  taylor_rule.csv      one row per quarter, 1960Q1 to the latest quarter
      date             first day of the quarter
      fed_funds        effective federal funds rate, quarterly mean of monthly values (complete quarters), percent
      core_inflation   core PCE inflation, 4-quarter percent change of the JCXFE price index
  loops_vintages.csv   one row per year, 1960 to the latest complete year
      year
      inflation        CPI inflation, percent change of the annual-average CPIAUCSL
      output_gap       100 (Y / Ybar - 1), annual means of GDPC1 and GDPPOT, current FRED vintage
      output_gap_2023  the same with the ALFRED vintage of 2023-03-30 (the data the textbook used), to 2022
Both are validated against the copied fig13-16.csv and fig13-17.csv.
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CH = "original-scanned-book/ch13-stabilization-policy-and-the-as-ad-framework/data"


def read(root, item, name):
    """One raw FRED/ALFRED csv as a Series indexed by date."""
    d = pd.read_csv(os.path.join(root, CH, item, "raw", name), na_values=["."])
    return d.set_index(pd.to_datetime(d.iloc[:, 0])).iloc[:, 1].astype(float)


def gap(gdp, pot):
    """Annual output gap 100 (Y / Ybar - 1) from quarterly levels, complete years only."""
    q = pd.concat([gdp, pot], axis=1).dropna()
    n = q.iloc[:, 0].resample("YS").count()
    a = q.resample("YS").mean()[n == 4]
    out = 100 * (a.iloc[:, 0] / a.iloc[:, 1] - 1)
    out.index = out.index.year
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    root = ap.parse_args().macro102

    # ---- taylor_rule.csv ----------------------------------------------------------------
    ff = read(root, "fig13-16", "fred_FEDFUNDS.csv").dropna()
    n = ff.resample("QS").count()
    ffq = ff.resample("QS").mean()[n == 3]
    core = read(root, "fig13-16", "fred_JCXFE.csv").dropna()
    pi = 100 * (core / core.shift(4) - 1)
    tr = pd.DataFrame({"fed_funds": ffq, "core_inflation": pi})
    tr = tr[tr.index >= "1960-01-01"].dropna(how="all").round(4)
    tr.index.name = "date"
    tr.to_csv(os.path.join(HERE, "taylor_rule.csv"), date_format="%Y-%m-%d")
    old = pd.read_csv(os.path.join(HERE, "fig13-16.csv"), parse_dates=["date"]).set_index("date")
    d_rule = (1 + 1.5 * tr.core_inflation - old.policy_rule).abs().max()
    d_ff = (tr.fed_funds - old.fed_funds).abs().max()
    print(f"taylor_rule.csv: {len(tr)} quarters {tr.index.min():%Y-%m} to {tr.index.max():%Y-%m}; "
          f"max |1 + 1.5 pi - fig13-16 rule| = {d_rule:.4f}, max |fed funds diff| = {d_ff:.4f}")

    # ---- loops_vintages.csv ---------------------------------------------------------------
    cpi = read(root, "fig13-17", "fred_CPIAUCSL.csv")
    cpi = cpi.loc[:cpi.last_valid_index()].interpolate(limit=1, limit_area="inside")   # Oct 2025 never published
    n = cpi.resample("YS").count()
    cpia = cpi.resample("YS").mean()[n == 12]
    infl = 100 * (cpia / cpia.shift(1) - 1)
    infl.index = infl.index.year
    now = gap(read(root, "fig13-17", "fred_GDPC1.csv").dropna(), read(root, "fig13-17", "fred_GDPPOT.csv"))
    book = gap(read(root, "fig13-17", "alfred_GDPC1_2023-03-30.csv").dropna(),
               read(root, "fig13-17", "alfred_GDPPOT_2023-03-30.csv"))
    lv = pd.DataFrame({"inflation": infl, "output_gap": now}).dropna()
    lv["output_gap_2023"] = book
    lv = lv.loc[1960:].round(4)
    lv.index.name = "year"
    lv.to_csv(os.path.join(HERE, "loops_vintages.csv"))
    old = pd.read_csv(os.path.join(HERE, "fig13-17.csv")).set_index("year")
    print(f"loops_vintages.csv: {len(lv)} years {lv.index.min()}-{lv.index.max()}; "
          f"max |diff| vs fig13-17: inflation {(lv.inflation - old.inflation).abs().max():.4f}, "
          f"output gap {(lv.output_gap - old.output_gap).abs().max():.4f}; "
          f"book vintage to {lv.output_gap_2023.last_valid_index()}")


if __name__ == "__main__":
    main()
