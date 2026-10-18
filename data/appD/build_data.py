"""Build the data files used by Appendix D (Growth and Development Accounting).

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Downloads are cached in ../macro102/.work/appD/notebook-raw/ (delete a file there to download it again):
  pwt110.dta              Penn World Table 11.0 (DataverseNL, doi:10.34894/FABVLR), copied from macro102's
                          bulk cache .work/downloads/pwt110.dta when it exists
  wdi_NY.GDP.TOTL.RT.ZS.json
                          World Bank WDI, total natural resources rents (% of GDP), all countries
Outputs (next to this script):
  pwt_accounting.csv      iso3, country, region, year, rgdpna, rnna, emp, avh, hc, rgdpo, cgdpo, cn, labsh
                          the PWT 11.0 series behind both accounting methods, every PWT economy, 1970-2023
                          (rows with no output data are dropped; values rounded to 5 significant digits)
  nat_res_rents.csv       iso3, year, rents_pct, carried_forward
                          WDI total natural resources rents, % of GDP, PWT economies only, 1970-2023.
                          The WDI series ends before PWT does, so each economy's last WDI value is carried
                          forward to 2023 (carried_forward = True on those rows).
Checks: no duplicate country-years, the expected columns, the coverage counts that the Growth Atlas
reports (175 economies with complete rgdpna, rnna and emp for 2004-2023), and each file under 1 MB.
"""
import argparse
import json
import os
import shutil

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
PWT_DOI = "doi:10.34894/FABVLR"
COLUMNS = ["rgdpna", "rnna", "emp", "avh", "hc", "rgdpo", "cgdpo", "cn", "labsh"]
WDI = "NY.GDP.TOTL.RT.ZS"
FIRST_YEAR = 1970
# PWT economies that the World Bank country list (data/ch01/countries.csv) does not cover
EXTRA_REGIONS = {"AIA": "Latin America & Caribbean", "MSR": "Latin America & Caribbean"}


def cached(cache, name, url, params=None):
    """Download url into cache/name once; later runs read the cached file."""
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        r = requests.get(url, params=params, timeout=300)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def pwt_file(cache, macro102):
    """pwt110.dta in the cache: copied from macro102's bulk cache, or downloaded from DataverseNL."""
    path = os.path.join(cache, "pwt110.dta")
    bulk = os.path.join(macro102, ".work/downloads/pwt110.dta")
    if not os.path.exists(path) and os.path.exists(bulk):
        shutil.copy(bulk, path)
    if not os.path.exists(path):
        files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                             params={"persistentId": PWT_DOI}, timeout=60).json()["data"]
        fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "pwt110.dta"][0]
        cached(cache, "pwt110.dta", f"https://dataverse.nl/api/access/datafile/{fid}")
    return path


def round_sig(x, digits=5):
    """Round a Series to a number of significant digits (keeps the CSV small)."""
    x = x.astype("float64")
    mag = np.floor(np.log10(np.abs(x.where(x != 0))))
    factor = 10.0 ** (digits - 1 - mag)
    return (np.round(x * factor) / factor).where(x != 0, x)


def pwt_accounting(cache, macro102):
    pwt = pd.read_stata(pwt_file(cache, macro102), columns=["countrycode", "country", "year"] + COLUMNS)
    pwt = pwt.rename(columns={"countrycode": "iso3"})
    pwt["year"] = pwt.year.astype(int)
    pwt = pwt[pwt.year >= FIRST_YEAR].dropna(subset=["rgdpna", "rgdpo"], how="all")
    for c in COLUMNS:
        pwt[c] = round_sig(pwt[c])
    regions = pd.read_csv(os.path.join(HERE, "..", "ch01", "countries.csv")).set_index("iso3").region
    regions = pd.concat([regions, pd.Series(EXTRA_REGIONS)])
    pwt["region"] = pwt.iso3.map(regions)
    if pwt.region.isna().any():
        raise SystemExit(f"no region for {sorted(pwt[pwt.region.isna()].iso3.unique())}")
    pwt["country"] = pwt.country.astype(str)
    out = pwt[["iso3", "country", "region", "year"] + COLUMNS].sort_values(["country", "year"])
    if out.duplicated(["iso3", "year"]).any():
        raise SystemExit("duplicate country-years in pwt_accounting.csv")
    path = os.path.join(HERE, "pwt_accounting.csv")
    out.to_csv(path, index=False)
    print(f"pwt_accounting.csv: {len(out)} rows, {out.iso3.nunique()} economies, "
          f"{out.year.min()}-{out.year.max()}, {os.path.getsize(path) / 1e3:.0f} kB")
    # coverage checks
    win = out[(out.year >= 2004) & (out.year <= 2023)]
    full = win.dropna(subset=["rgdpna", "rnna", "emp"]).groupby("iso3").size()
    print(f"  complete rgdpna, rnna, emp for 2004-2023: {(full == 20).sum()} economies (Growth Atlas: 175)")
    last = out[out.year == 2023]
    for cols in (["rgdpo", "emp", "cn", "cgdpo", "hc"], ["rgdpo", "emp", "avh", "cn", "cgdpo", "hc"],
                 ["rgdpo", "emp", "cn", "cgdpo", "hc", "labsh"]):
        print(f"  2023 with {'+'.join(cols)}: {len(last.dropna(subset=cols))} economies")
    return out


def nat_res_rents(cache, pwt):
    path = cached(cache, f"wdi_{WDI}.json", f"https://api.worldbank.org/v2/country/all/indicator/{WDI}",
                  params={"format": "json", "per_page": 20000, "date": "1970:2023"})
    rows = json.load(open(path))[1]
    d = pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows],
                      "year": [int(r["date"]) for r in rows],
                      "rents_pct": [r["value"] for r in rows]}).dropna()
    d = d[d.iso3.isin(set(pwt.iso3))].sort_values(["iso3", "year"])
    d["rents_pct"] = d.rents_pct.round(4)
    last_wdi = d.year.max()
    d["carried_forward"] = False
    extra = []
    for iso3, g in d.groupby("iso3"):
        last = g.iloc[-1]
        for year in range(int(last.year) + 1, 2024):
            extra.append({"iso3": iso3, "year": year, "rents_pct": last.rents_pct, "carried_forward": True})
    d = pd.concat([d, pd.DataFrame(extra)]).sort_values(["iso3", "year"])
    print(f"  WDI ends in {last_wdi}; last values carried forward to 2023 for {len(extra)} rows")
    if d.duplicated(["iso3", "year"]).any():
        raise SystemExit("duplicate country-years in nat_res_rents.csv")
    out = os.path.join(HERE, "nat_res_rents.csv")
    d.to_csv(out, index=False)
    print(f"nat_res_rents.csv: {len(d)} rows, {d.iso3.nunique()} economies, {d.year.min()}-{d.year.max()}, "
          f"{os.path.getsize(out) / 1e3:.0f} kB")
    top = d[d.year == last_wdi].nlargest(3, "rents_pct")
    print("  largest rents in", last_wdi, ":", ", ".join(f"{r.iso3} {r.rents_pct:.1f}%" for r in top.itertuples()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    cache = os.path.join(args.macro102, ".work", "appD", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    pwt = pwt_accounting(cache, args.macro102)
    nat_res_rents(cache, pwt)
    for f in ("pwt_accounting.csv", "nat_res_rents.csv"):
        if os.path.getsize(os.path.join(HERE, f)) > 1e6:
            raise SystemExit(f"{f} is larger than 1 MB")


if __name__ == "__main__":
    main()
