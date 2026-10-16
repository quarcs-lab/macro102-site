"""Copy the few small data files used by the Chapter 21 recap notebook.

usage: python build_data.py [--site PATH]     (PATH defaults to this site repo, two folders up)

Chapter 21 (Parting Thoughts) has no figures of its own. Its notebook looks back at the main lessons
of the book and recomputes one or two numbers per lesson from data that earlier chapters already
use. So that the notebook reads everything from its own DATA_URL, this script copies those files
from the earlier chapters' data/ folders of the site repo into data/ch21/, unchanged:

  ch04/fig4-5.csv            actual and capital-only predicted GDP per person, 111 countries, 2023
  ch04/fig4-7.csv            GDP per person and implied TFP, same countries, 2023
  ch03/maddison_panel.csv    Maddison GDP per person, 7 countries, 1870-2022
  ch08/fig8-4.csv            average money growth and inflation, 165 economies, 1990-2021 and 1990-2025
  ch13/fig13-17.csv          U.S. output gap and CPI inflation, 1960-2025
  ch06/growth_accounting.csv U.S. labor productivity and TFP indexes (BLS), 1948-2025

Each copy is checked: identical bytes, the expected columns, and no missing values in key columns.
"""
import argparse
import filecmp
import os
import shutil

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FILES = {   # source (relative to the site repo's data/ folder) -> columns that must be present and complete
    "ch04/fig4-5.csv": ["iso3", "country", "gdp_pc_rel_2023", "pred_gdp_pc_2023"],
    "ch04/fig4-7.csv": ["iso3", "country", "gdp_pc_rel_2023", "tfp_2023"],
    "ch03/maddison_panel.csv": ["iso3", "country", "year", "gdppc"],
    "ch08/fig8-4.csv": ["iso3", "country", "money_growth_1990_2025", "inflation_1990_2025"],
    "ch13/fig13-17.csv": ["year", "output_gap", "inflation"],
    "ch06/growth_accounting.csv": ["year", "output_per_hour", "tfp"],
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
    # the two Chapter 4 files must describe the same countries, and y = TFP x k^(1/3) must hold
    f5 = pd.read_csv(os.path.join(HERE, "fig4-5.csv"))
    f7 = pd.read_csv(os.path.join(HERE, "fig4-7.csv"))
    both = f5.merge(f7, on=["iso3", "country", "gdp_pc_rel_2023"])
    gap = (both.pred_gdp_pc_2023 * both.tfp_2023 / both.gdp_pc_rel_2023 - 1).abs().max()
    if len(both) != len(f5) or gap > 1e-4:
        raise SystemExit(f"fig4-5 and fig4-7 do not match ({len(both)} of {len(f5)} rows, gap {gap})")
    print(f"check: fig4-5 x fig4-7 reproduce y = A k^(1/3) in all {len(both)} countries (largest gap {gap:.1e})")


if __name__ == "__main__":
    main()
