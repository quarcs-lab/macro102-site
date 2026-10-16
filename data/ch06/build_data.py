"""Build the wider data files used by the Chapter 6 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch06-growth-and-ideas/data/):
  fig6-6/raw/fred_GDPCA.csv              real GDP, billions of chained 2017 dollars, annual (BEA via FRED)
  fig6-6/raw/fred_B230RC0A052NBEA.csv    population, thousands, annual (BEA NIPA Table 2.1 via FRED)
  fig6-6/raw/fred_USREC.csv              NBER recession indicator, monthly (1 = recession month)
  table6-2/raw/bls_tfp-major-sectors-historical_20260819.xlsx
                                         BLS total factor productivity, major sectors, release of March 2026
Outputs (next to this script):
  us_gdp_pc.csv          year, gdp_pc            U.S. real GDP per person, chained 2017 dollars, 1929-2025
  recessions.csv         peak, trough, peak_year, trough_year
                                                 NBER business-cycle peaks and troughs since 1960 (monthly dates
                                                 and decimal years)
  growth_accounting.csv  year, output_per_hour, contrib_capital, contrib_labor_composition, tfp
                                                 BLS indexes (2017 = 100), private business sector, 1948-2025
"""
import argparse
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch06-growth-and-ideas/data/"
BLS = "table6-2/raw/bls_tfp-major-sectors-historical_20260819.xlsx"
MEASURES = {"Labor productivity": "output_per_hour",
            "Contribution of capital intensity to labor productivity": "contrib_capital",
            "Contribution of labor composition to labor productivity": "contrib_labor_composition",
            "Total factor productivity": "tfp"}


def fred(root, name):
    d = pd.read_csv(os.path.join(root, "fig6-6/raw", f"fred_{name}.csv"))
    d["year"] = d.observation_date.str[:4].astype(int)
    return d.set_index("year")[name]


def gdp_per_person(root):
    """Real GDP per person (dollars) = GDPCA (billions) / population (thousands) x 1e6."""
    y = (fred(root, "GDPCA") / fred(root, "B230RC0A052NBEA") * 1e6).dropna().round(1)
    out = pd.DataFrame({"year": y.index, "gdp_pc": y.values})
    out.to_csv(os.path.join(HERE, "us_gdp_pc.csv"), index=False)
    print(f"us_gdp_pc.csv: {len(out)} years, {out.year.min()}-{out.year.max()}")
    # validation: the 10-year growth rates reproduce fig6-6.csv
    lny = np.log(out.set_index("year").gdp_pc)
    g10 = (100 * (lny - lny.shift(10)) / 10).loc[1960:]
    fig = pd.read_csv(os.path.join(HERE, "fig6-6.csv")).set_index("year").gdp_pc_growth_10yr
    print(f"  largest difference from fig6-6.csv: {(g10.reindex(fig.index) - fig).abs().max():.5f} pp")


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = pd.read_csv(os.path.join(root, "fig6-6/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    rec = rec.set_index("observation_date").USREC
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    # decimal years for shading a chart with a yearly axis: start of the peak month, end of the trough month
    out["peak_year"] = (out.peak.dt.year + (out.peak.dt.month - 1) / 12).round(3)
    out["trough_year"] = (out.trough.dt.year + out.trough.dt.month / 12).round(3)
    out["peak"] = out.peak.dt.strftime("%Y-%m-%d")
    out["trough"] = out.trough.dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def growth_accounting(root):
    """BLS indexes for the private business sector (PG), the sector that reproduces Table 6.2."""
    m = pd.read_excel(os.path.join(root, BLS), sheet_name="MachineReadable")
    m["Value"] = pd.to_numeric(m["Value"], errors="coerce")
    m = m[(m.NAICS == "PG") & m.Units.str.startswith("Index") & m.Measure.isin(list(MEASURES))]
    w = m.pivot_table(index="Year", columns="Measure", values="Value").rename(columns=MEASURES)
    w = w[list(MEASURES.values())].dropna()
    w.index.name = "year"
    w.round(3).to_csv(os.path.join(HERE, "growth_accounting.csv"))
    print(f"growth_accounting.csv: {len(w)} years, {w.index.min()}-{w.index.max()}")
    # validation: the period averages reproduce macro102's table6-2/data.csv (current vintage)
    table = pd.read_csv(os.path.join(root, "table6-2/data.csv"))
    worst = 0.0
    for a, b in [(1948, 2021), (1948, 1973), (1973, 1995), (1995, 2003), (2003, 2021)]:
        ours = 100 * np.log(w.loc[b] / w.loc[a]) / (b - a)
        worst = max(worst, float(np.abs(ours.values - table[f"g{a}_{b}_book_2021"].values).max()))
    print(f"  largest difference from table6-2/data.csv: {worst:.4f} pp")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    gdp_per_person(root)
    recessions(root)
    growth_accounting(root)


if __name__ == "__main__":
    main()
