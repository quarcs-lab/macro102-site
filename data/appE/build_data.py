"""Build the data file of Appendix E (Growth and Convergence Across Countries).

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling macro102 checkout)

The appendix studies beta and sigma convergence in the 84-country balanced panel of the Penn World Table 10.0
used by Mendez, "Beta and Sigma Convergence Across Countries: A Stata Tutorial"
(https://carlos-mendez.org/tutorials/stata_convergence/). This script downloads that tutorial's copy of
pwt100.dta (cached in <macro102>/.work/appE/notebook-raw/) and applies the tutorial's sample rules, in the
tutorial's order:

  1. keep country, ccode, year, pop, rgdpe; gdppc = rgdpe / pop; drop rows without gdppc or pop
  2. drop the 27 oil producers on the tutorial's list
  3. drop country-years with population under 1 million
  4. keep the years 1960-2019
  5. keep the countries with GDP per person in 1960 (the balanced panel)

It checks that the result is 84 countries x 60 years = 5,040 rows with no gaps, and writes
pwt100_convergence.csv: ccode, country, year, pop, rgdpe, gdppc.
"""
import argparse
import os
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
URL = ("https://raw.githubusercontent.com/cmg777/starter-academic-v501/master/"
       "content/tutorials/stata_convergence/pwt100.dta")
OIL = ["DZA", "AGO", "AZE", "BHR", "BRN", "TCD", "COG", "ECU", "GNQ", "GAB", "IRN", "IRQ", "KAZ", "KWT",
       "NGA", "OMN", "QAT", "RUS", "SAU", "TTO", "TKM", "ARE", "VEN", "YEM", "LBY", "TLS", "SDN"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    raw_dir = os.path.join(args.macro102, ".work", "appE", "notebook-raw")
    os.makedirs(raw_dir, exist_ok=True)
    raw = os.path.join(raw_dir, "pwt100.dta")
    if not os.path.exists(raw):
        print("downloading", URL)
        urllib.request.urlretrieve(URL, raw)

    df = pd.read_stata(raw, columns=["countrycode", "country", "year", "pop", "rgdpe"])
    df = df.rename(columns={"countrycode": "ccode"})
    df["country"] = df["country"].astype(str)
    df["gdppc"] = df["rgdpe"] / df["pop"]
    df = df.dropna(subset=["gdppc", "pop"])
    print(f"oil producers on the list found in the data: {df.loc[df['ccode'].isin(OIL), 'ccode'].nunique()}")
    df = df[~df["ccode"].isin(OIL)]
    df = df[df["pop"] >= 1]
    df = df[df["year"] >= 1960]
    has1960 = df.loc[df["year"] == 1960, "ccode"]
    print(f"countries dropped for missing 1960 data: {df['ccode'].nunique() - has1960.nunique()}")
    df = df[df["ccode"].isin(has1960)]
    df["year"] = df["year"].astype(int)
    df = df.sort_values(["ccode", "year"])[["ccode", "country", "year", "pop", "rgdpe", "gdppc"]]

    n_c = df["ccode"].nunique()
    assert n_c == 84, f"expected 84 countries, got {n_c}"
    assert len(df) == 84 * 60, f"expected 5,040 rows, got {len(df)}"
    assert df.groupby("ccode")["year"].agg(["min", "max", "count"]).eq([1960, 2019, 60]).all().all()
    assert not df.isna().any().any()

    out = os.path.join(HERE, "pwt100_convergence.csv")
    df.to_csv(out, index=False, float_format="%.6g")
    s = df["gdppc"]
    print(f"wrote {out}: {len(df)} rows, {n_c} countries, {df['year'].min()}-{df['year'].max()}")
    print(f"gdppc: mean {s.mean():,.0f}, median {s.median():,.0f}, skewness {s.skew():.2f}")


if __name__ == "__main__":
    main()
