"""Build the wider data file used by the Chapter 20 notebook (the Big Mac index, Table 20.1).

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill):
  - The Economist's Big Mac index, open data
    (original-scanned-book/ch20-exchange-rates-and-international-finance/data/table20-1/raw/big-mac-raw-index.csv;
    columns date, iso_a3, currency_code, name, local_price, dollar_ex, dollar_price, ...);
  - the Penn World Table 11.0 subset of Chapter 5
    (original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv;
    columns countrycode, country, year, rgdpo, pop, csh_i), for GDP per person in 2023.
Output: big_mac.csv next to this script, one row per economy and Big Mac release (2000-04 to 2026-07):
          release       release date of The Economist (YYYY-MM-DD)
          iso3          ISO 3166 alpha-3 code (EUZ = euro area)
          country       The Economist's name
          currency      ISO currency code
          local_price   price of a Big Mac in local currency
          ex_rate       market exchange rate, local currency per U.S. dollar
          dollar_price  local_price / ex_rate, U.S. dollars (2 decimals)
          gdp_pc_2023   PWT 11.0 real GDP per person in 2023 (rgdpo / pop), 2021 U.S. dollars; empty for the
                        euro area and economies not in PWT
Check: the 2022-07-01 release reproduces macro102's table20-1/data.csv (the textbook's table).
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CH20 = "original-scanned-book/ch20-exchange-rates-and-international-finance/data/table20-1"
PWT = "original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    raw = pd.read_csv(os.path.join(args.macro102, CH20, "raw", "big-mac-raw-index.csv"))
    out = pd.DataFrame({
        "release": raw.date,
        "iso3": raw.iso_a3,
        "country": raw.name,
        "currency": raw.currency_code,
        "local_price": raw.local_price.round(2),
        "ex_rate": raw.dollar_ex.round(4),
        "dollar_price": (raw.local_price / raw.dollar_ex).round(2),
    })
    pwt = pd.read_csv(os.path.join(args.macro102, PWT))
    pwt = pwt[pwt.year == 2023].dropna(subset=["rgdpo", "pop"])
    gdp = pd.DataFrame({"iso3": pwt.countrycode, "gdp_pc_2023": (pwt.rgdpo / pwt["pop"]).round(0)})
    out = out.merge(gdp, on="iso3", how="left")
    out["gdp_pc_2023"] = out.gdp_pc_2023.astype("Int64")
    out = out.sort_values(["release", "iso3"])
    out.to_csv(os.path.join(HERE, "big_mac.csv"), index=False)

    # Validation against the textbook table as collected by macro102 (table20-1/data.csv)
    book = pd.read_csv(os.path.join(args.macro102, CH20, "data.csv"))
    july = out[out.release == "2022-07-01"].set_index("country")
    names = {"United States": "United States", "Norway": "Norway", "Euro area": "Euro area", "Mexico": "Mexico",
             "China": "China", "Japan": "Japan", "South Africa": "South Africa", "India": "India"}
    worst = 0.0
    for _, row in book.iterrows():
        ours = july.loc[names[row["item"]]]
        worst = max(worst, abs(ours.local_price - row.price_local_book_2022),
                    abs(ours.dollar_price - row.price_usd_book_2022))
    print(f"big_mac.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.release.nunique()} releases "
          f"({out.release.min()} to {out.release.max()}); {out.gdp_pc_2023.notna().sum()} rows with GDP")
    print(f"largest difference from table20-1/data.csv (July 2022): {worst:.3f}")


if __name__ == "__main__":
    main()
