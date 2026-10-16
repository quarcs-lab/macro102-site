"""Build the wider data files used by the Chapter 14 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch14-financial-crises-and-the-short-run-model/data/):
  fig14-6/raw/fred_USREC.csv          NBER recession indicator, monthly (1 = recession month)
  table14-1/raw/fred_<ID>.csv         Federal Reserve H.4.1, weekly Wednesday levels, millions of dollars:
                                      WTFSRFL (total factors supplying reserve funds), WSHOTSL (Treasuries),
                                      WSHOMCB (mortgage-backed securities), WCICL (currency in circulation),
                                      WRBWFRBL (reserve balances)
Outputs (next to this script):
  recessions.csv              peak, trough    NBER recessions that start in 1953 or later (monthly dates)
  fed_balance_sheet.csv       month, total, treasuries, mbs, currency, reserves
                              monthly averages of the weekly levels, billions of dollars, complete months
                              only (at least 4 Wednesdays), 2003-01 to the latest complete month
Check: May 2007, May 2015 and the latest month reproduce table14-1/data.csv (copied from collect-data).
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch14-financial-crises-and-the-short-run-model/data/"
H41 = {"WTFSRFL": "total", "WSHOTSL": "treasuries", "WSHOMCB": "mbs",
       "WCICL": "currency", "WRBWFRBL": "reserves"}


def recessions(root):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig14-6/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1953-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def balance_sheet(root):
    """Monthly averages of the H.4.1 weekly levels, in billions of dollars (complete months only)."""
    frames = []
    for sid, name in H41.items():
        raw = pd.read_csv(os.path.join(root, f"table14-1/raw/fred_{sid}.csv"), parse_dates=["observation_date"])
        frames.append(raw.set_index("observation_date")[sid].rename(name) / 1000)
    weekly = pd.concat(frames, axis=1)
    m = weekly.resample("MS").agg(["mean", "count"])
    full = (m.xs("count", axis=1, level=1) >= 4).all(axis=1)
    out = m.xs("mean", axis=1, level=1)[full].round(1)
    out.index = out.index.strftime("%Y-%m")
    out.index.name = "month"
    out.to_csv(os.path.join(HERE, "fed_balance_sheet.csv"))
    print(f"fed_balance_sheet.csv: {len(out)} months, {out.index[0]} to {out.index[-1]}")
    return out


def validate(out, root):
    """May 2007, May 2015 and the latest month must equal table14-1/data.csv within rounding."""
    book = pd.read_csv(os.path.join(root, "table14-1/data.csv")).set_index("item")
    latest = [c for c in book.columns if c.startswith("billions_latest_")][0]
    months = {"billions_book_2007": "2007-05", "billions_book_2015": "2015-05", latest: out.index[-1]}
    for col, month in months.items():
        row = out.loc[month]
        ours = {"Assets: U.S. Treasuries": row.treasuries, "Assets: Mortgage-backed securities": row.mbs,
                "Total assets": row.total, "Liabilities: Currency": row.currency,
                "Liabilities: Reserves": row.reserves}
        for item, value in ours.items():
            if abs(value - book.loc[item, col]) > 1.0:
                raise SystemExit(f"{month} {item}: {value} != {book.loc[item, col]} in table14-1/data.csv")
    print(f"validated: {', '.join(months.values())} reproduce table14-1/data.csv (within 1 billion)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    recessions(root)
    validate(balance_sheet(root), root)


if __name__ == "__main__":
    main()
