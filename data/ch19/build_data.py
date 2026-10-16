"""Build the wider data files used by the Chapter 19 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under original-scanned-book/ch19-international-trade/data/):
  fig19-1/raw/fred_EXPGSA.csv, fred_IMPGSA.csv, fred_GDPA.csv   exports, imports, GDP (billions of dollars, annual)
  fig19-2/raw/fred_A019RC1A027NBEA.csv                         net exports (billions of dollars, annual)
  fig19-5/raw/fred_GPDIA.csv                                   gross private domestic investment (billions, annual)
  fig19-6/raw/fred_IIPUSNETIA.csv                              net international investment position (millions, year end)
  fig19-6/raw/alfred_IIPUSNETIA_2023-07-01.csv, alfred_GDPA_2023-07-01.csv   the same two series as published in July 2023
  fig19-3/raw/pwt*_subset.csv, fig19-4/raw/pwt*_subset.csv     Penn World Table 10.01 and 11.0 subsets
Outputs (next to this script):
  us_trade.csv     year, gdp, exports, imports, net_exports, investment, niip, gdp_2023, niip_2023
                   (billions of current dollars; 1950-2025, the investment position from 1976)
  pwt_trade.csv    iso3, country, vintage, year, csh_c, csh_i, csh_g, cgdpo  (nine countries, 1990 to the latest year)
Checks: the shares of GDP reproduce fig19-1, fig19-2, fig19-5 (investment, trade deficit) and fig19-6 (both
vintages); 100 (1 - c - i - g) reproduces every column of fig19-3, and its period means every column of fig19-4.
"""
import argparse
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch19-international-trade/data/"
NAMES = {"USA": "U.S.", "JPN": "Japan", "CHN": "China", "FRA": "France", "DEU": "Germany",
         "IND": "India", "SGP": "Singapore", "IRL": "Ireland", "KOR": "S. Korea"}


def fred(root, path, name):
    """One FRED/ALFRED download as an annual Series indexed by year."""
    raw = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    s = raw.set_index("observation_date").iloc[:, 0]
    s.index = s.index.year
    return pd.to_numeric(s, errors="coerce").rename(name)


def check(ours, theirs, label, tol):
    both = ours.dropna().index.intersection(theirs.dropna().index)
    diff = (ours[both] - theirs[both]).abs().max()
    if not diff < tol:
        raise SystemExit(f"{label}: differs from the collect-data file by {diff:.4f}")
    print(f"validated {label}: max difference {diff:.4f} over {len(both)} values")


def us_trade(root):
    cols = [fred(root, "fig19-1/raw/fred_GDPA.csv", "gdp"),
            fred(root, "fig19-1/raw/fred_EXPGSA.csv", "exports"),
            fred(root, "fig19-1/raw/fred_IMPGSA.csv", "imports"),
            fred(root, "fig19-2/raw/fred_A019RC1A027NBEA.csv", "net_exports"),
            fred(root, "fig19-5/raw/fred_GPDIA.csv", "investment"),
            fred(root, "fig19-6/raw/fred_IIPUSNETIA.csv", "niip") / 1000,
            fred(root, "fig19-6/raw/alfred_GDPA_2023-07-01.csv", "gdp_2023"),
            fred(root, "fig19-6/raw/alfred_IIPUSNETIA_2023-07-01.csv", "niip_2023") / 1000]
    out = pd.concat(cols, axis=1).loc[1950:2025]
    out.index.name = "year"
    share = 100 * out.div(out.gdp, axis=0)
    f1 = pd.read_csv(os.path.join(root, "fig19-1/data.csv")).set_index("year")
    f2 = pd.read_csv(os.path.join(root, "fig19-2/data.csv")).set_index("year")
    f5 = pd.read_csv(os.path.join(root, "fig19-5/data.csv")).set_index("year")
    f6 = pd.read_csv(os.path.join(root, "fig19-6/data.csv")).set_index("year")
    check(share.exports, f1.exports_share, "exports / GDP vs fig19-1", 0.001)
    check(share.imports, f1.imports_share, "imports / GDP vs fig19-1", 0.001)
    check(share.net_exports, f2.trade_balance_pct_gdp, "net exports / GDP vs fig19-2", 0.001)
    check(share.investment, f5.investment_pct_gdp, "investment / GDP vs fig19-5", 0.001)
    check(-share.net_exports, f5.trade_deficit_pct_gdp, "trade deficit / GDP vs fig19-5", 0.001)
    check(share.niip, f6.niip_pct_gdp, "NIIP / GDP vs fig19-6", 0.001)
    gap = (out.exports - out.imports - out.net_exports).abs().max()
    print(f"exports - imports - net exports: at most {gap:.3f} billion dollars (rounding in the NIPA tables)")
    vint = (100 * out.niip_2023 / out.gdp_2023).dropna()
    print(f"2023 vintage NIIP / GDP: 2020 {vint[2020]:.1f}, 2021 {vint[2021]:.1f}, 2022 {vint[2022]:.1f}")
    out = out.round(3)
    out.to_csv(os.path.join(HERE, "us_trade.csv"))
    print(f"us_trade.csv: {out.index.min()}-{out.index.max()}, {len(out)} rows")


def pwt_trade(root):
    frames = []
    for vintage, name in [("PWT 10.01", "pwt1001_subset.csv"), ("PWT 11.0", "pwt110_subset.csv")]:
        for fig in ["fig19-3", "fig19-4"]:
            raw = pd.read_csv(os.path.join(root, fig, "raw", name))
            frames.append(raw.assign(vintage=vintage))
    raw = pd.concat(frames).drop_duplicates(["countrycode", "vintage", "year"])
    raw = raw[(raw.year >= 1990)].dropna(subset=["csh_c", "csh_i", "csh_g", "cgdpo"])
    out = pd.DataFrame({"iso3": raw.countrycode, "country": raw.countrycode.map(NAMES), "vintage": raw.vintage,
                        "year": raw.year, "csh_c": raw.csh_c.round(6), "csh_i": raw.csh_i.round(6),
                        "csh_g": raw.csh_g.round(6), "cgdpo": raw.cgdpo.round(1)})
    order = {iso: i for i, iso in enumerate(NAMES)}
    out = out.assign(o=out.iso3.map(order)).sort_values(["o", "vintage", "year"]).drop(columns="o")
    validate_pwt(out, root)
    out.to_csv(os.path.join(HERE, "pwt_trade.csv"), index=False)
    print(f"pwt_trade.csv: {out.iso3.nunique()} countries, {len(out)} rows, "
          f"{out.year.min()}-{out.groupby('vintage').year.max().to_dict()}")


def validate_pwt(out, root):
    tb = out.assign(tb=100 * (1 - out.csh_c - out.csh_i - out.csh_g))
    f3 = pd.read_csv(os.path.join(root, "fig19-3/data.csv")).set_index("iso3")
    for year, vintage, suffix in [(2017, "PWT 10.01", "_pwt10"), (2019, "PWT 10.01", "_pwt10"),
                                  (2019, "PWT 11.0", ""), (2023, "PWT 11.0", "")]:
        one = tb[(tb.year == year) & (tb.vintage == vintage)].set_index("iso3")
        us_gdp = one.loc["USA", "cgdpo"]
        check(one.tb, f3[f"tb_own_{year}{suffix}"], f"fig19-3 own GDP {year} {vintage}", 0.002)
        check(one.tb * one.cgdpo / us_gdp, f3[f"tb_us_{year}{suffix}"], f"fig19-3 U.S. GDP {year} {vintage}", 0.002)
    f4 = pd.read_csv(os.path.join(root, "fig19-4/data.csv")).set_index("iso3")
    for start, end, vintage, suffix in [(2000, 2017, "PWT 10.01", "_pwt10"), (2000, 2019, "PWT 10.01", "_pwt10"),
                                        (1990, 2019, "PWT 10.01", "_pwt10"), (1990, 2019, "PWT 11.0", ""),
                                        (2000, 2019, "PWT 11.0", ""), (2000, 2023, "PWT 11.0", "")]:
        window = tb[(tb.vintage == vintage) & (tb.year >= start) & (tb.year <= end)]
        means = window.groupby("iso3").tb.mean()
        check(means, f4[f"tb_avg_{start}_{end}{suffix}"], f"fig19-4 mean {start}-{end} {vintage}", 0.002)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    us_trade(root)
    pwt_trade(root)


if __name__ == "__main__":
    main()
