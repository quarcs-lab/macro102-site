"""Build the wider data files used by the Chapter 2 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs: the FRED downloads saved by the macro102 /collect-data skill in
        original-scanned-book/ch02-measuring-the-macroeconomy/data/<item>/raw/fred_<ID>.csv
Outputs, next to this script:
  nipa_annual.csv   one row per year (1929-2025); BEA national accounts (NIPA) lines, billions of
                    current dollars unless noted:
                      gdp, consumption, investment, government, net_exports, exports, imports,
                      motor_vehicles, food, housing, medical, structures, equipment, ipp, residential,
                      defense (expenditure side, NIPA Table 1.5.5 lines);
                      compensation, wages, benefits, taxes_less_subsidies, net_operating_surplus,
                      depreciation, gdi, proprietors_income (income side, NIPA Table 1.10 lines);
                      real_gdp (billions of chained 2017 dollars); population (thousands)
  recessions.csv    one row per NBER recession since 1947: start, end (first and last month of the
                    recession, from the monthly USREC indicator)
The script checks that the new files reproduce the copied fig2-1.csv and fig2-3.csv.
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch02-measuring-the-macroeconomy/data"
# column name -> (collect-data item folder, FRED series ID)
SERIES = {
    "gdp": ("table2-1", "GDPA"),
    "consumption": ("table2-1", "PCECA"),
    "investment": ("table2-1", "GPDIA"),
    "government": ("table2-1", "GCEA"),
    "net_exports": ("table2-1", "A019RC1A027NBEA"),
    "exports": ("table2-1", "EXPGSA"),
    "imports": ("table2-1", "IMPGSA"),
    "motor_vehicles": ("table2-1", "DMOTRC1A027NBEA"),
    "food": ("table2-1", "DFXARC1A027NBEA"),
    "housing": ("table2-1", "DHUTRC1A027NBEA"),
    "medical": ("table2-1", "DHLCRC1A027NBEA"),
    "structures": ("table2-1", "B009RC1A027NBEA"),
    "equipment": ("table2-1", "Y033RC1A027NBEA"),
    "ipp": ("table2-1", "Y001RC1A027NBEA"),
    "residential": ("table2-1", "PRFIA"),
    "defense": ("table2-1", "A824RC1A027NBEA"),
    "compensation": ("table2-2", "A033RC1A027NBEA"),
    "wages": ("table2-2", "A4102C1A027NBEA"),
    "benefits": ("table2-2", "A038RC1A027NBEA"),
    "taxes_less_subsidies": ("table2-2", "W254RC1A027NBEA"),
    "net_operating_surplus": ("table2-2", "W260RC1A027NBEA"),
    "depreciation": ("table2-2", "GDICONSPA"),
    "gdi": ("fig2-3", "GDIA"),
    "proprietors_income": ("fig2-3", "A041RC1A027NBEA"),
    "real_gdp": ("ex01", "GDPCA"),
    "population": ("table2-1", "B230RC0A052NBEA"),
}


def fred(root, item, sid):
    """One FRED download as a Series indexed by its observation date."""
    df = pd.read_csv(os.path.join(root, DATA, item, "raw", f"fred_{sid}.csv"), parse_dates=["observation_date"])
    return df.set_index("observation_date")[sid].astype(float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    root = ap.parse_args().macro102

    # ---- nipa_annual.csv -------------------------------------------------------------
    cols = {name: fred(root, item, sid) for name, (item, sid) in SERIES.items()}
    nipa = pd.DataFrame(cols)
    nipa.insert(0, "year", nipa.index.year)
    nipa = nipa.reset_index(drop=True)
    nipa["population"] = nipa.population.round(0).astype("Int64")
    nipa.to_csv(os.path.join(HERE, "nipa_annual.csv"), index=False)

    # validation against the copied figure files
    f1 = pd.read_csv(os.path.join(HERE, "fig2-1.csv")).set_index("year")
    n = nipa.set_index("year")
    gaps = []
    for part in ["consumption", "investment", "government", "net_exports"]:
        gaps.append((100 * n[part] / n.gdp - f1[part + "_share"]).abs().max())
    f3 = pd.read_csv(os.path.join(HERE, "fig2-3.csv")).set_index("year")
    labor = n.compensation / (n.gdi - n.taxes_less_subsidies - n.proprietors_income)
    gap3 = (labor.loc[f3.index] - f3.labor_share).abs().max()
    print(f"nipa_annual.csv: {len(nipa)} rows, {nipa.year.min()}-{nipa.year.max()}, {nipa.shape[1]} columns")
    print(f"  max |share - fig2-1.csv| = {max(gaps):.5f} points; max |labor share - fig2-3.csv| = {gap3:.6f}")
    assert max(gaps) < 1e-3 and gap3 < 1e-5, "nipa_annual.csv does not reproduce the figure files"

    # ---- recessions.csv ---------------------------------------------------------------
    rec = fred(root, "fig2-4", "USREC")
    rec = rec[rec.index >= "1947-01-01"]
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"start": starts.strftime("%Y-%m-%d"), "end": ends.strftime("%Y-%m-%d")})
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, {out.start.iloc[0]} to {out.end.iloc[-1]}")


if __name__ == "__main__":
    main()
