"""Build the wider data files used by the Chapter 17 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under original-scanned-book/ch17-investment/data/):
  table17-1/raw/oecd_DF_CIT_statutory.csv   OECD Corporate Tax Statistics (SDMX DF_CIT), statutory
                                            corporate income tax rates, percent, annual
  fig17-4/raw/fred_USREC.csv                NBER recession indicator, monthly (1 = recession month)
  fig17-4/raw/fred_A006RE1Q156NBEA.csv      gross private domestic investment, percent of GDP, quarterly
  fig17-4/raw/fred_A011RE1Q156NBEA.csv      private residential fixed investment, percent of GDP, quarterly
Outputs (next to this script):
  corporate_tax.csv       country, iso3, year, cit_rate     the 33 jurisdictions of Table 17.1, 2000 to the
                                                            latest year (central-government statutory rate)
  table17-1-book.csv      country, book_rate, book_user_cost   Table 17.1 as printed in the textbook (2022)
  recessions.csv          peak, trough                      NBER recessions that start in 1948 or later
  investment_quarterly.csv  date, total, residential        quarterly shares of GDP (NIPA Table 1.1.10)
Checks: the 2022 and 2025 rates reproduce table17-1/data.csv; the annual means of the quarterly total and
residential shares reproduce fig17-4/data.csv within 0.15 percentage points.
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch17-investment/data/"

# Table 17.1 of the textbook, in book order: (printed name, ISO3, printed tax rate, printed user cost)
BOOK = [
    ("Brazil", "BRA", 34.0, 12.0), ("Argentina", "ARG", 30.0, 11.3),
    ("Democratic Republic of the Congo", "COD", 30.0, 11.3), ("Kenya", "KEN", 30.0, 11.3),
    ("Nigeria", "NGA", 30.0, 11.3), ("Australia", "AUS", 30.0, 11.3), ("Costa Rica", "CRI", 30.0, 11.3),
    ("Mexico", "MEX", 30.0, 11.3), ("Portugal", "PRT", 30.0, 11.3), ("South Africa", "ZAF", 27.0, 10.8),
    ("France", "FRA", 25.8, 10.6), ("Netherlands", "NLD", 25.8, 10.6), ("India", "IND", 25.2, 10.6),
    ("China", "CHN", 25.0, 10.5), ("Korea", "KOR", 25.0, 10.5), ("Spain", "ESP", 25.0, 10.5),
    ("Italy", "ITA", 24.0, 10.4), ("Japan", "JPN", 23.2, 10.3), ("Israel", "ISR", 23.0, 10.3),
    ("Botswana", "BWA", 22.0, 10.1), ("Indonesia", "IDN", 22.0, 10.1), ("United States", "USA", 21.0, 10.0),
    ("Sweden", "SWE", 20.6, 9.9), ("Saudi Arabia", "SAU", 20.0, 9.9), ("Vietnam", "VNM", 20.0, 9.9),
    ("Poland", "POL", 19.0, 9.8), ("United Kingdom", "GBR", 19.0, 9.8), ("Hong Kong", "HKG", 16.5, 9.5),
    ("Germany", "DEU", 15.8, 9.4), ("Ireland", "IRL", 12.5, 9.0), ("Chile", "CHL", 10.0, 8.8),
    ("Switzerland", "CHE", 8.5, 8.6), ("Cayman Islands", "CYM", 0.0, 7.9),
]


def corporate_tax(root):
    """Statutory central-government CIT rates of the 33 book jurisdictions, one row per country and year."""
    raw = pd.read_csv(os.path.join(root, "table17-1/raw/oecd_DF_CIT_statutory.csv"),
                      usecols=["REF_AREA", "MEASURE", "TARGETING", "SECTOR", "TIME_PERIOD", "OBS_VALUE"])
    st = raw[(raw.MEASURE == "CIT") & (raw.TARGETING == "ST") & (raw.SECTOR == "S1311")]
    names = {iso: name for name, iso, _, _ in BOOK}
    st = st[st.REF_AREA.isin(names)].dropna(subset=["OBS_VALUE"])
    out = pd.DataFrame({"country": st.REF_AREA.map(names), "iso3": st.REF_AREA,
                        "year": st.TIME_PERIOD.astype(int), "cit_rate": st.OBS_VALUE.round(4)})
    order = {iso: i for i, (_, iso, _, _) in enumerate(BOOK)}
    out = out.assign(o=out.iso3.map(order)).sort_values(["o", "year"]).drop(columns="o")
    out = out[out.year >= 2000]
    out.to_csv(os.path.join(HERE, "corporate_tax.csv"), index=False)
    print(f"corporate_tax.csv: {out.iso3.nunique()} jurisdictions, {out.year.min()}-{out.year.max()}, {len(out)} rows")

    book = pd.DataFrame([(n, r, u) for n, _, r, u in BOOK], columns=["country", "book_rate", "book_user_cost"])
    book.to_csv(os.path.join(HERE, "table17-1-book.csv"), index=False)
    print(f"table17-1-book.csv: {len(book)} rows")
    return out


def validate_tax(out, root):
    """The 2022 and 2025 rates must equal collect-data's table17-1/data.csv."""
    table = pd.read_csv(os.path.join(root, "table17-1/data.csv")).set_index("item")
    for year, col in [(2022, "cit_rate_book_2022"), (2025, "cit_rate_latest_2025")]:
        ours = out[out.year == year].set_index("country").cit_rate
        diff = (ours - table[col]).abs().max()
        if not diff < 1e-3:
            raise SystemExit(f"{year}: corporate_tax.csv differs from table17-1/data.csv by {diff}")
    print("validated: the 2022 and 2025 rates reproduce table17-1/data.csv")


def recessions(root):
    """(peak, trough) of every NBER recession since 1948: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig17-4/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1948-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def investment_quarterly(root):
    """Quarterly investment shares of GDP; annual means are checked against fig17-4/data.csv."""
    frames = []
    for sid, name in [("A006RE1Q156NBEA", "total"), ("A011RE1Q156NBEA", "residential")]:
        raw = pd.read_csv(os.path.join(root, f"fig17-4/raw/fred_{sid}.csv"), parse_dates=["observation_date"])
        frames.append(raw.set_index("observation_date")[sid].rename(name))
    out = pd.concat(frames, axis=1).dropna()
    out.index.name = "date"
    annual = out.groupby(out.index.year).mean()
    fig = pd.read_csv(os.path.join(root, "fig17-4/data.csv")).set_index("year")
    both = annual.index.intersection(fig.index)
    for col in ["total", "residential"]:
        diff = (annual.loc[both, col] - fig.loc[both, col]).abs().max()
        if not diff < 0.15:
            raise SystemExit(f"investment_quarterly.csv {col}: annual means differ from fig17-4/data.csv by {diff:.2f}")
    out.index = out.index.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "investment_quarterly.csv"))
    print(f"investment_quarterly.csv: {len(out)} quarters, {out.index[0]} to {out.index[-1]}; "
          f"annual means reproduce fig17-4/data.csv within 0.15 points")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    validate_tax(corporate_tax(root), root)
    recessions(root)
    investment_quarterly(root)


if __name__ == "__main__":
    main()
