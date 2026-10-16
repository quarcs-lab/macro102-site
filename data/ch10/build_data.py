"""Build the wider data files used by the Chapter 10 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/):
  fig10-2/raw/fred_USREC.csv       NBER recession indicator, monthly (1 = recession month)
  table10-1/raw/fred_USRECQ.csv    NBER recession indicator, quarterly (1 = recession quarter)
  table10-1/raw/fred_GDPC1.csv, fred_PCECC96.csv, fred_GPDIC1.csv, fred_GCEC1.csv, fred_EXPGSC1.csv,
  fred_IMPGSC1.csv                 real GDP and its components, billions of chained 2017 dollars, quarterly, SAAR
  table10-1/raw/fred_PAYEMS.csv    nonfarm payroll employment, thousands, monthly, SA
  table10-1/raw/fred_UNRATE.csv    unemployment rate, percent, monthly, SA (October 2025 missing)
Outputs (next to this script):
  recessions.csv     peak, trough, peak_quarter, trough_quarter
                     NBER recessions that start in 1953 or later: monthly dates (for the shaded bands)
                     and quarterly dates (for Table 10.1)
  us_quarterly.csv   date, gdp, consumption, investment, government, exports, imports, employment,
                     unemployment          quarterly, 1953Q1 on; employment and unemployment are
                     quarterly averages of the monthly series
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/"
QUARTERLY = {"gdp": "GDPC1", "consumption": "PCECC96", "investment": "GPDIC1", "government": "GCEC1",
             "exports": "EXPGSC1", "imports": "IMPGSC1"}
TABLE_ROWS = {"gdp": "GDP", "employment": "Nonfarm employment", "unemployment": "Unemployment rate",
              "consumption": "Consumption", "investment": "Investment", "government": "Government purchases",
              "exports": "Exports", "imports": "Imports"}


def fred(root, path):
    """One FRED series as a Series indexed by date (blank cells become NaN)."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def episodes(flag, step):
    """(peak, trough) pairs: the period before the first recession period, and the last recession period."""
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    return pd.DataFrame({"peak": starts - pd.DateOffset(months=step), "trough": ends})


def recessions(root):
    monthly = episodes(fred(root, "fig10-2/raw/fred_USREC.csv"), 1)
    quarterly = episodes(fred(root, "table10-1/raw/fred_USRECQ.csv"), 3)
    monthly = monthly[monthly.peak >= "1953-01-01"].reset_index(drop=True)
    quarterly = quarterly[quarterly.peak >= "1953-01-01"].reset_index(drop=True)
    if len(monthly) != len(quarterly):
        raise SystemExit(f"{len(monthly)} monthly but {len(quarterly)} quarterly recessions")
    gap = (quarterly.peak - monthly.peak).dt.days.abs().max()
    if gap > 200:
        raise SystemExit(f"monthly and quarterly peaks do not pair up (largest gap {gap} days)")
    out = pd.DataFrame({"peak": monthly.peak, "trough": monthly.trough,
                        "peak_quarter": quarterly.peak, "trough_quarter": quarterly.trough})
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")
    return out


def quarterly_data(root):
    cols = {}
    for name, series in QUARTERLY.items():
        cols[name] = fred(root, f"table10-1/raw/fred_{series}.csv")
    emp = fred(root, "table10-1/raw/fred_PAYEMS.csv") / 1000
    unemp = fred(root, "table10-1/raw/fred_UNRATE.csv")
    cols["employment"] = emp.resample("QS").mean()
    cols["unemployment"] = unemp.resample("QS").mean()          # mean of the months available
    out = pd.DataFrame(cols)
    out = out[(out.index >= "1953-01-01") & out.gdp.notna()].round(3)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "us_quarterly.csv"), date_format="%Y-%m-%d")
    print(f"us_quarterly.csv: {len(out)} quarters, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}, "
          f"{int(out.isna().sum().sum())} missing values")
    return out


def validate(root, rec, data):
    """Table 10.1 recomputed from the two new files must equal collect-data's table10-1/data.csv."""
    ref = pd.read_csv(os.path.join(root, "table10-1/data.csv")).set_index("item")
    rows = {}
    for p, t in zip(pd.to_datetime(rec.peak_quarter), pd.to_datetime(rec.trough_quarter)):
        change = {}
        for col, item in TABLE_ROWS.items():
            if col == "unemployment":
                change[item] = data.loc[t, col] - data.loc[p, col]
            else:
                change[item] = 100 * (data.loc[t, col] / data.loc[p, col] - 1)
        rows[p.strftime("%Y-%m")] = change
    table = pd.DataFrame(rows)
    mine = pd.DataFrame({"prev_avg_latest_2026": table.loc[:, :"2001-01"].mean(axis=1),
                         "great_rec_latest_2026": table["2007-10"],
                         "covid_latest_2026": table["2019-10"]})
    worst = (mine - ref[mine.columns]).abs().max().max()
    print(f"validation: Table 10.1 from us_quarterly.csv and recessions.csv; largest difference from "
          f"table10-1/data.csv: {worst:.3f} (data.csv is rounded to 2 decimals)")
    if worst > 0.01:
        raise SystemExit("validation failed")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    rec = recessions(root)
    data = quarterly_data(root)
    validate(root, rec, data)


if __name__ == "__main__":
    main()
