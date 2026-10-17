"""Build the wider data file used by the practice problems of the Chapter 11 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Downloaded from FRED (fredgraph.csv, requests' default User-Agent) and cached in macro102's
.work/ch11/notebook-raw/ (delete a cached file to download it again):
  GDPC1     real gross domestic product
  PCECC96   real personal consumption expenditures
  GPDIC1    real gross private domestic investment
            all three: BEA, billions of chained 2017 dollars, quarterly, seasonally adjusted annual rates
Output (next to this script):
  spending_quarterly.csv   date, gdp, consumption, investment      quarterly, 1947Q1 on
Validation: the overlapping quarters must equal ../ch10/us_quarterly.csv (the same FRED series), and GDPC1 must
equal collect-data's ex07/raw/fred_GDPC1.csv where both have data (small differences mean a newer BEA vintage).
fig11-6.csv is copied by the write-notebook prepare step, not by this script.
"""
import argparse
import os

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch11-the-is-curve/data/"
SERIES = {"gdp": "GDPC1", "consumption": "PCECC96", "investment": "GPDIC1"}


def cached(cache, name, url):
    """Download url once into the cache folder (requests' default User-Agent) and return the local path."""
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def fred_series(path):
    """One FRED series as a Series indexed by date (blank cells become NaN)."""
    df = pd.read_csv(path, parse_dates=["observation_date"])
    return pd.to_numeric(df.set_index("observation_date").iloc[:, 0], errors="coerce")


def spending(cache, root):
    """Real GDP, consumption and investment, quarterly, from 1947Q1 to the latest quarter."""
    cols = {}
    for name, sid in SERIES.items():
        path = cached(cache, f"fred_{sid}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
        cols[name] = fred_series(path)
    out = pd.DataFrame(cols).dropna().round(3)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "spending_quarterly.csv"), date_format="%Y-%m-%d")
    print(f"spending_quarterly.csv: {len(out)} quarters, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}, "
          f"{os.path.getsize(os.path.join(HERE, 'spending_quarterly.csv')) / 1000:.0f} KB")
    # validation 1: the Chapter 10 file holds the same three series from 1953Q1
    ch10 = pd.read_csv(os.path.join(HERE, "..", "ch10", "us_quarterly.csv"), parse_dates=["date"]).set_index("date")
    both = out.join(ch10[list(SERIES)], rsuffix="_ch10", how="inner")
    worst = 0.0
    for name in SERIES:
        worst = max(worst, (both[name] - both[name + "_ch10"]).abs().max())
    print(f"  vs ../ch10/us_quarterly.csv: {len(both)} common quarters, largest difference {worst:.3f} billion")
    # validation 2: collect-data's GDPC1 download for Exercise 7
    ref = fred_series(os.path.join(root, "ex07/raw/fred_GDPC1.csv")).dropna()
    common = out.gdp.reindex(ref.index).dropna()
    gap = (common - ref.reindex(common.index)).abs().max()
    print(f"  vs ex07/raw/fred_GDPC1.csv: {len(common)} common quarters, largest difference {gap:.3f} billion")
    # look at the data: the investment share and the quarters with the largest falls
    share = 100 * out.investment / out.gdp
    print(f"  investment / GDP (chained dollars): mean {share.mean():.1f}%, min {share.min():.1f}% "
          f"({share.idxmin():%Y-%m}), max {share.max():.1f}% ({share.idxmax():%Y-%m})")
    growth = 100 * (out / out.shift(4) - 1)
    for name in SERIES:
        print(f"  four-quarter growth of {name:12}: min {growth[name].min():+.1f}% ({growth[name].idxmin():%Y-%m}), "
              f"max {growth[name].max():+.1f}% ({growth[name].idxmax():%Y-%m})")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work/ch11/notebook-raw")
    os.makedirs(cache, exist_ok=True)
    spending(cache, root)


if __name__ == "__main__":
    main()
