"""Build the wider data files used by the Chapter 1 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch01-introduction-to-macroeconomics/data/):
  fig1-1/raw/mpd2023_subset.csv          Maddison Project Database 2023: countrycode, country, region, year, gdppc, pop
  fig1-1/raw/fred_A191RD3A086NBEA.csv    U.S. GDP deflator (BEA via FRED), to express 2011 dollars in 2022 dollars
  fig1-2/raw/fred_USREC.csv              NBER recession indicator, monthly (1 = recession month)
Outputs (next to this script):
  maddison_annual.csv   iso3, country, year, gdppc     every year 1870-2022 with data, the six countries of
                                                        Figure 1.1 plus Ethiopia, 2022 dollars
  recessions.csv        peak, trough                   NBER business-cycle peaks and troughs since 1960 (monthly dates)
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch01-introduction-to-macroeconomics/data/"


def maddison(root):
    """Annual Maddison GDP per person in 2022 dollars (same conversion as fig1-1.csv)."""
    defl = pd.read_csv(os.path.join(root, "fig1-1/raw/fred_A191RD3A086NBEA.csv"))
    defl["year"] = defl.observation_date.str[:4].astype(int)
    defl = defl.set_index("year").A191RD3A086NBEA
    factor = defl[2022] / defl[2011]
    mpd = pd.read_csv(os.path.join(root, "fig1-1/raw/mpd2023_subset.csv"))
    mpd = mpd[(mpd.year >= 1870) & (mpd.year <= 2022)].dropna(subset=["gdppc"])
    out = pd.DataFrame({"iso3": mpd.countrycode, "country": mpd.country, "year": mpd.year,
                        "gdppc": (mpd.gdppc * factor).round(0).astype(int)})
    out.to_csv(os.path.join(HERE, "maddison_annual.csv"), index=False)
    print(f"maddison_annual.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}, factor 2011->2022 = {factor:.4f}")
    # validation: the benchmark years of fig1-1.csv
    fig = pd.read_csv(os.path.join(HERE, "fig1-1.csv")).set_index("year")
    worst = 0
    for iso in ["usa", "gbr", "jpn", "arg", "zaf", "chn"]:
        ours = out[out.iso3 == iso.upper()].set_index("year").gdppc.reindex(fig.index)
        worst = max(worst, (ours - fig["gdppc_" + iso]).abs().max())
    print(f"  largest difference from fig1-1.csv at the benchmark years: {worst:.0f} dollars")


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = pd.read_csv(os.path.join(root, "fig1-2/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    rec = rec.set_index("observation_date").USREC
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    out["peak"] = out.peak.dt.strftime("%Y-%m-%d")
    out["trough"] = out.trough.dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    maddison(root)
    recessions(root)


if __name__ == "__main__":
    main()
