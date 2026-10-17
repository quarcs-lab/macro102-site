"""Copy the small data files used by Appendix C (Math Review for Macroeconomics).

usage: python build_data.py [--site PATH]     (PATH defaults to this site repo, two folders up)

Appendix C reviews the math of the book and applies each tool to real data that the chapters also use. So
that the notebook reads everything from its own DATA_URL, this script copies those files from the chapters'
data/ folders of the site repo into data/appC/, unchanged:

  ch03/fig3-2.csv                U.S. GDP per person, 1870-2025 (logs, ratio scale, trend growth)
  ch02/nipa_annual.csv           U.S. national accounts, 1929-2025 (nominal vs real, growth rules)
  ch08/us_cpi.csv                U.S. consumer price index, 1774-2025 (index numbers, inflation)
  ch08/interest_rates_panel.csv  nominal rates and inflation, 50 economies (the Fisher approximation)
  ch09/fig9-2.csv                U.S. actual and potential GDP, 1929-2025 (output gap, trend vs cycle)
  ch18/fig18-2.csv               U.S. federal surplus and debt, FY1934-2025 (debt dynamics)
  ch17/fig17-3.csv               Shiller's cyclically adjusted P/E ratio, 1881-2026 (present value of a stock)

Each copy is checked: identical bytes, the expected columns, and no missing values in key columns.
"""
import argparse
import filecmp
import os
import shutil

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {   # source (relative to the site repo's data/ folder) -> columns that must be present and complete
    "ch03/fig3-2.csv": ["year", "gdppc"],
    "ch02/nipa_annual.csv": ["year", "gdp", "real_gdp", "population"],
    "ch08/us_cpi.csv": ["year", "cpi"],
    "ch08/interest_rates_panel.csv": ["iso3", "country", "year", "short_rate"],   # inflation: Argentina 2025 empty
    "ch09/fig9-2.csv": ["year", "gdp_actual", "gdp_potential"],
    "ch18/fig18-2.csv": ["year", "surplus_gdp_pct"],                              # debt: empty before FY1940
    "ch17/fig17-3.csv": ["date", "cape"],
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=os.path.join(HERE, "..", ".."))
    args = ap.parse_args()
    for rel, cols in FILES.items():
        src = os.path.join(args.site, "data", rel)
        dst = os.path.join(HERE, os.path.basename(rel))
        shutil.copyfile(src, dst)
        if not filecmp.cmp(src, dst, shallow=False):
            raise SystemExit(f"{dst} differs from {src}")
        df = pd.read_csv(dst)
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise SystemExit(f"{rel}: missing columns {missing}")
        if df[cols].isna().any().any():
            raise SystemExit(f"{rel}: missing values in {cols}")
        print(f"{os.path.basename(rel)}: {len(df)} rows, {os.path.getsize(dst) / 1e3:.1f} kB, copied from data/{rel}")


if __name__ == "__main__":
    main()
