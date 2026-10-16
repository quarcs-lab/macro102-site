"""Build the wider data files used by the Chapter 12 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/):
  fig12-2/raw/fred_USREC.csv                     NBER recession indicator, monthly (1 = recession month)
  fig12-6/raw/treasury_par_yield_curve_YYYY.csv  U.S. Treasury daily par yield curve rates, 2022, 2023, 2026
Outputs (next to this script):
  recessions.csv            peak, trough        NBER recessions that start in 1953 or later (monthly dates)
  yield_curves_monthly.csv  date, maturity, months, yield
                            the yield curve on the first trading day of every month of 2022, 2023 and 2026
                            (11 maturities, long format: one row per date and maturity)
Checks: the 2022-01-03 and 2023-04-03 curves equal the rows of fig12-6.csv (copied from collect-data).
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/"
MATURITIES = {"1 Mo": ("1 mo", 1), "3 Mo": ("3 mo", 3), "6 Mo": ("6 mo", 6), "1 Yr": ("1 yr", 12),
              "2 Yr": ("2 yr", 24), "3 Yr": ("3 yr", 36), "5 Yr": ("5 yr", 60), "7 Yr": ("7 yr", 84),
              "10 Yr": ("10 yr", 120), "20 Yr": ("20 yr", 240), "30 Yr": ("30 yr", 360)}
YEARS = [2022, 2023, 2026]


def recessions(root):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig12-2/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1953-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def yield_curves(root):
    """The yield curve on the first trading day of each month, long format."""
    frames = []
    for year in YEARS:
        raw = pd.read_csv(os.path.join(root, f"fig12-6/raw/treasury_par_yield_curve_{year}.csv"))
        raw["date"] = pd.to_datetime(raw["Date"], format="%m/%d/%Y")
        raw = raw.dropna(subset=list(MATURITIES)).sort_values("date")
        first = raw.groupby(raw.date.dt.to_period("M")).head(1)
        frames.append(first[["date"] + list(MATURITIES)])
    wide = pd.concat(frames)
    long = wide.melt(id_vars="date", var_name="column", value_name="yield")
    long["maturity"] = long.column.map({k: v[0] for k, v in MATURITIES.items()})
    long["months"] = long.column.map({k: v[1] for k, v in MATURITIES.items()})
    long = long.sort_values(["date", "months"])[["date", "maturity", "months", "yield"]]
    long["date"] = long.date.dt.strftime("%Y-%m-%d")
    long.to_csv(os.path.join(HERE, "yield_curves_monthly.csv"), index=False)
    print(f"yield_curves_monthly.csv: {long.date.nunique()} curves, {long.date.min()} to {long.date.max()}, "
          f"{len(long)} rows, {int(long['yield'].isna().sum())} missing")
    return long


def validate(long):
    """The two textbook curves must equal the rows of fig12-6.csv."""
    book = pd.read_csv(os.path.join(HERE, "fig12-6.csv"))
    for day in ["2022-01-03", "2023-04-03"]:
        ours = long[long.date == day].set_index("months")["yield"]
        if ours.empty:
            raise SystemExit(f"{day} is not the first trading day of its month in the raw file")
        theirs = book[book.date == day].iloc[0]
        for months, value in ours.items():
            if abs(theirs[f"yield_{months}m"] - value) > 1e-9:
                raise SystemExit(f"{day}, {months} months: {value} != fig12-6.csv {theirs[f'yield_{months}m']}")
    print("validation: the 2022-01-03 and 2023-04-03 curves equal fig12-6.csv (all 11 maturities)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    root = os.path.join(os.path.abspath(parser.parse_args().macro102), DATA)
    recessions(root)
    validate(yield_curves(root))


if __name__ == "__main__":
    main()
