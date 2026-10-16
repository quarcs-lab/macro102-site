"""Build the wider data files used by the Chapter 9 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch09-an-introduction-to-the-short-run/data/):
  fig9-3/raw/fred_USREC.csv      NBER recession indicator, monthly (1 = recession month)
  fig9-4/raw/fred_PAYEMS.csv     total nonfarm payroll employment, thousands, monthly, SA (BLS)
  fig9-5/raw/fred_CPIAUCSL.csv   CPI-U all items, index 1982-84 = 100, monthly, SA (BLS)
Outputs (next to this script):
  recessions.csv           peak, trough                NBER peaks and troughs whose trough is in 1960 or later
  payroll_employment.csv   date, payroll_millions      payroll employment, millions, monthly, 1979-12 on
  cpi_monthly.csv          date, cpi, inflation_12m    CPI and 12-month inflation (percent), monthly, 1959-01 on
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch09-an-introduction-to-the-short-run/data/"


def fred(root, path):
    """One FRED series as a Series indexed by month (blank cells become NaN)."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = fred(root, "fig9-3/raw/fred_USREC.csv")
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    for col in ["peak", "trough"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def payroll(root):
    """Payroll employment in millions; its monthly percent change must reproduce fig9-4.csv."""
    emp = fred(root, "fig9-4/raw/fred_PAYEMS.csv")
    emp = emp[emp.index >= "1979-12-01"] / 1000
    out = pd.DataFrame({"payroll_millions": emp.round(3)})
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "payroll_employment.csv"), date_format="%Y-%m-%d")
    change = (100 * (emp / emp.shift(1) - 1)).dropna()
    ref = pd.read_csv(os.path.join(HERE, "fig9-4.csv"), parse_dates=["date"]).set_index("date").emp_change_pct
    worst = (change.reindex(ref.index) - ref).abs().max()
    print(f"payroll_employment.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"largest difference of the % change from fig9-4.csv: {worst:.4f}")


def cpi(root):
    """Monthly CPI and 12-month inflation; October 2025 stays missing (not collected in the shutdown)."""
    index = fred(root, "fig9-5/raw/fred_CPIAUCSL.csv")
    infl = 100 * (index / index.shift(12) - 1)
    out = pd.DataFrame({"cpi": index, "inflation_12m": infl.round(3)})
    out = out[out.index >= "1959-01-01"]
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "cpi_monthly.csv"), date_format="%Y-%m-%d")
    # validation: the calendar-year mean of the monthly index (complete years) reproduces fig9-5.csv
    filled = index.interpolate()                       # as collect-data does for October 2025
    annual = filled.groupby(filled.index.year).agg(["mean", "count"])
    annual = annual[annual["count"] == 12]["mean"]
    yearly = 100 * (annual / annual.shift(1) - 1)
    ref = pd.read_csv(os.path.join(HERE, "fig9-5.csv")).set_index("year").inflation_cpi
    worst = (yearly.reindex(ref.index) - ref).abs().max()
    print(f"cpi_monthly.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}, "
          f"{int(out.cpi.isna().sum())} missing month(s); largest difference of annual inflation from "
          f"fig9-5.csv: {worst:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    recessions(root)
    payroll(root)
    cpi(root)


if __name__ == "__main__":
    main()
