"""Copy the small data files used by Appendix A (Google Colab, Python Coding, and Data Science Libraries).

usage: python build_data.py [--site PATH]     (PATH defaults to this site repo, two folders up)

Appendix A teaches Google Colab, Python and the data science libraries of the book. Its examples use real
data that the chapters also use, so students practise on files they will meet again. So that the notebook
reads everything from its own DATA_URL, this script copies those files from the chapters' data/ folders of
the site repo into data/appA/, unchanged:

  ch03/maddison_panel.csv   Maddison GDP per person, 7 countries, 1870-2022 (pandas basics, line chart)
  ch03/fig3-7.csv           PWT relative income and growth since 1960, 111 countries (scatter, merge)
  ch01/countries.csv        names, World Bank regions and income groups of 223 economies (merge)
  ch03/pwt_income.csv       PWT GDP per person, 185 economies, 1950-2023 (the mini project)

Each copy is checked: identical bytes, the expected columns, and no missing values in key columns.
"""
import argparse
import filecmp
import os
import shutil

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {   # source (relative to the site repo's data/ folder) -> columns that must be present and complete
    "ch03/maddison_panel.csv": ["iso3", "country", "year", "gdppc"],
    "ch03/fig3-7.csv": ["iso3", "country", "gdppc_rel_us_2023", "growth_1960_2023_pct"],
    "ch01/countries.csv": ["iso3", "country", "region"],   # income is empty for 5 historical units and aggregates
    "ch03/pwt_income.csv": ["iso3", "country", "year", "gdp_pc"],
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
    # every country of the scatter must find its region in countries.csv (the merge example)
    growth = pd.read_csv(os.path.join(HERE, "fig3-7.csv"))
    names = pd.read_csv(os.path.join(HERE, "countries.csv"))
    lost = sorted(set(growth.iso3) - set(names.iso3))
    if lost:
        raise SystemExit(f"fig3-7.csv countries missing from countries.csv: {lost}")
    print(f"check: all {len(growth)} countries of fig3-7.csv have a region in countries.csv")


if __name__ == "__main__":
    main()
