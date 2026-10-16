"""Build the wider data files used by the Chapter 7 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/):
  fig7-1/raw/fred_USREC.csv                NBER recession indicator, monthly (1 = recession month)
  ex02/raw/fred_LNS12300001.csv            employment-population ratio, men 16+, percent, monthly, SA
  ex02/raw/fred_LNS12300002.csv            employment-population ratio, women 16+, percent, monthly, SA
  table7-1/raw/fred_CNP16OV.csv            civilian noninstitutional population 16+, thousands, monthly
  table7-1/raw/fred_CLF16OV.csv            civilian labor force, thousands, monthly, SA
  table7-1/raw/fred_CE16OV.csv             employment level, thousands, monthly, SA
  table7-1/raw/fred_UNEMPLOY.csv           unemployment level, thousands, monthly, SA
  table7-2/raw/pwt110_subset.csv           Penn World Table 11.0: countrycode, country, year, avh, emp, pop
  table7-2/raw/pwt1001_subset.csv          Penn World Table 10.01, same columns
Outputs (next to this script):
  recessions.csv        peak, trough                 NBER peaks and troughs whose trough is in 1950 or later
  emp_pop_by_sex.csv    date, men, women             monthly employment-population ratios, 1948-01 on
  labor_force.csv       date, population, labor_force, employed, unemployed, not_in_labor_force
                                                     millions, monthly, 1948-01 on (Table 7.1 for any month)
  hours_per_person.csv  country, year, hours_pwt11, hours_pwt10
                                                     annual hours worked per person, U.S. 2019 = 100 (Table 7.2)
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/"
NAMES = {"United Kingdom": "U.K.", "Republic of Korea": "South Korea"}   # the textbook's names
ORDER = ["United States", "Italy", "France", "Germany", "U.K.", "Japan", "South Korea"]


def fred(root, path):
    """One FRED series as a Series indexed by month."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = fred(root, "fig7-1/raw/fred_USREC.csv")
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1950-01-01"]
    for col in ["peak", "trough"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def by_sex(root):
    """Employment-population ratios of men and women; validated against macro102's ex02/data.csv."""
    out = pd.DataFrame({"men": fred(root, "ex02/raw/fred_LNS12300001.csv"),
                        "women": fred(root, "ex02/raw/fred_LNS12300002.csv")}).dropna()
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "emp_pop_by_sex.csv"), date_format="%Y-%m-%d")
    ref = pd.read_csv(os.path.join(root, "ex02/data.csv"), parse_dates=["date"]).set_index("date")
    diff = max((out.men - ref.emp_pop_ratio_men).abs().max(), (out.women - ref.emp_pop_ratio_women).abs().max())
    print(f"emp_pop_by_sex.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"largest difference from ex02/data.csv: {diff:.3f}")


def labor_force(root):
    """Monthly CPS levels in millions; validated against table7-1/data.csv and fig7-2.csv (UNRATE)."""
    out = pd.DataFrame({"population": fred(root, "table7-1/raw/fred_CNP16OV.csv"),
                        "labor_force": fred(root, "table7-1/raw/fred_CLF16OV.csv"),
                        "employed": fred(root, "table7-1/raw/fred_CE16OV.csv"),
                        "unemployed": fred(root, "table7-1/raw/fred_UNEMPLOY.csv")}).dropna() / 1000
    out["not_in_labor_force"] = out.population - out.labor_force
    out = out.round(3)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "labor_force.csv"), date_format="%Y-%m-%d")
    ref = pd.read_csv(os.path.join(root, "table7-1/data.csv"))
    ours = out.loc["2023-01-01", ["population", "labor_force", "employed", "unemployed", "not_in_labor_force"]]
    print(f"labor_force.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"January 2023 vs table7-1: {(ours.values - ref.millions_book_2023[:5].values).round(3).tolist()}")
    rate = (100 * out.unemployed / out.labor_force).round(1)
    unrate = pd.read_csv(os.path.join(HERE, "fig7-2.csv"), parse_dates=["date"]).set_index("date").unemployment_rate
    both = pd.concat([rate, unrate], axis=1, join="inner")
    print(f"  computed rate vs UNRATE: largest difference {(both.iloc[:, 0] - both.iloc[:, 1]).abs().max():.2f} points")


def hours(root):
    """Hours worked per person (avh x emp / pop), U.S. 2019 = 100, in PWT 11.0 and PWT 10.01."""
    cols = []
    for name, path in [["hours_pwt11", "table7-2/raw/pwt110_subset.csv"], ["hours_pwt10", "table7-2/raw/pwt1001_subset.csv"]]:
        pwt = pd.read_csv(os.path.join(root, path))
        pwt["country"] = pwt.country.replace(NAMES)
        h = (pwt["avh"] * pwt["emp"] / pwt["pop"]).set_axis(pd.MultiIndex.from_frame(pwt[["country", "year"]]))
        cols.append((100 * h / h.loc[("United States", 2019)]).rename(name))
    out = pd.concat(cols, axis=1).dropna(how="all").round(2).reset_index()
    out["order"] = out.country.map({c: i for i, c in enumerate(ORDER)})
    out = out.sort_values(["order", "year"]).drop(columns="order")
    out.to_csv(os.path.join(HERE, "hours_per_person.csv"), index=False)
    ref = pd.read_csv(os.path.join(root, "table7-2/data.csv")).set_index("item")
    wide = out.pivot(index="country", columns="year", values="hours_pwt10")
    worst = max((wide.loc[ref.index, y] - ref[f"hours_pwt1001_{y}"]).abs().max() for y in [1960, 1990, 2019])
    print(f"hours_per_person.csv: {len(out)} rows, {out.country.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}; largest difference from table7-2 (PWT 10.01): {worst:.2f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    recessions(root)
    by_sex(root)
    labor_force(root)
    hours(root)


if __name__ == "__main__":
    main()
