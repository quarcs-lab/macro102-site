"""Build the wider data files used by the Chapter 15 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/raw/):
  fernald_quarterly_tfp.xlsx   John Fernald (FRBSF), quarterly and annual TFP growth, sheet "annual"
  fred_USREC.csv               NBER recession indicator, monthly (1 = recession month)
Outputs (next to this script):
  recessions.csv   peak, trough      NBER recessions that start in 1953 or later (monthly dates)
  tfp_annual.csv   year, gdp_growth, tfp_solow, utilization, tfp_util
                   U.S. business sector, percent per year, 1950 to the latest year
Checks: tfp_util equals fig15-1.csv (copied from collect-data) in every year, and
        tfp_util = tfp_solow - utilization (Fernald's definition) within 0.05 points (annual averages of quarterly logs make it approximate).
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/raw/"
COLUMNS = {"date": "year", "dY": "gdp_growth", "dtfp": "tfp_solow", "dutil": "utilization",
           "dtfp_util": "tfp_util"}


def recessions(raw_dir):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(raw_dir, "fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1950-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def tfp_annual(raw_dir):
    """Fernald's annual growth rates: output, raw TFP (Solow residual), utilization and utilization-adjusted TFP."""
    raw = pd.read_excel(os.path.join(raw_dir, "fernald_quarterly_tfp.xlsx"), sheet_name="annual")
    out = raw[list(COLUMNS)].rename(columns=COLUMNS)
    out = out[out.year >= 1950].dropna().copy()
    out["year"] = out.year.astype(int)
    out = out.round(4)
    out.to_csv(os.path.join(HERE, "tfp_annual.csv"), index=False)
    print(f"tfp_annual.csv: {out.year.min()}-{out.year.max()}, {len(out)} rows, "
          f"{int(out.isna().sum().sum())} missing")
    return out


def validate(out):
    """tfp_util must reproduce fig15-1.csv, and equal raw TFP minus utilization."""
    book = pd.read_csv(os.path.join(HERE, "fig15-1.csv"))
    both = book.merge(out, on="year", how="outer", indicator=True)
    if (both._merge != "both").any():
        raise SystemExit(f"years differ from fig15-1.csv: {list(both.year[both._merge != 'both'])}")
    gap = (both.tfp_growth - both.tfp_util).abs().max()
    if gap > 1e-4:
        raise SystemExit(f"tfp_util differs from fig15-1.csv by up to {gap}")
    identity = (out.tfp_solow - out.utilization - out.tfp_util).abs().max()
    if identity > 0.05:
        raise SystemExit(f"tfp_util != tfp_solow - utilization (max gap {identity})")
    print(f"validation: tfp_util equals fig15-1.csv in all {len(both)} years (max gap {gap:.1e}); "
          f"tfp_util = tfp_solow - utilization (max gap {identity:.1e})")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    raw_dir = os.path.join(os.path.abspath(parser.parse_args().macro102), RAW)
    recessions(raw_dir)
    validate(tfp_annual(raw_dir))


if __name__ == "__main__":
    main()
