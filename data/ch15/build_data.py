"""Build the wider data files used by the Chapter 15 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/raw/):
  fernald_quarterly_tfp.xlsx   John Fernald (FRBSF), quarterly and annual TFP growth, sheet "annual"
  fred_USREC.csv               NBER recession indicator, monthly (1 = recession month)
Outputs (next to this script):
  recessions.csv   peak, trough      NBER recessions that start in 1953 or later (monthly dates)
  tfp_annual.csv   year, gdp_growth, tfp_solow, utilization, tfp_util
                   U.S. business sector, percent per year, 1950 to the latest year
  tfp_inputs.csv   year, gdp_growth, hours_growth, capital_growth, labor_quality, capital_share, tfp_solow,
                   utilization, tfp_util   (the growth-accounting inputs, for the Practice problems)
Checks: tfp_util equals fig15-1.csv (copied from collect-data) in every year, and
        tfp_util = tfp_solow - utilization (Fernald's definition) within 0.05 points (annual averages of quarterly logs make it approximate);
        tfp_inputs.csv repeats tfp_annual.csv's columns exactly, and tfp_solow = gdp_growth - capital_share * capital_growth
        - (1 - capital_share) * (hours_growth + labor_quality) within 0.15 points.

Multi-country file (conventions §6b), downloads cached in ../macro102/.work/ch15/notebook-raw/:
  pwt_growth.csv   iso3, country, region, year, tfp_growth, gdp_growth
                   Penn World Table 11.0: 100 x change in the log of rtfpna (TFP at constant national prices) and of
                   rgdpna (real GDP at constant national prices), every country with TFP data, 1955 to 2023.
                   Inputs: pwt110.dta (DataverseNL doi:10.34894/FABVLR; collect-data's bulk copy is used if present)
                   and the World Bank country list (api.worldbank.org/v2/country) for readable names and regions.
Check: the U.S. rows correlate strongly with Fernald's raw Solow residual (tfp_solow) and hardly with the
       utilization-adjusted series of Figure 15.1.
"""
import argparse
import json
import os
import shutil
import time

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = "original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/raw/"
COLUMNS = {"date": "year", "dY": "gdp_growth", "dtfp": "tfp_solow", "dutil": "utilization",
           "dtfp_util": "tfp_util"}


def recessions(raw_dir):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(raw_dir, "fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1950-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def tfp_annual(raw_dir):
    """Fernald's annual growth rates: output, raw TFP (Solow residual), utilization and utilization-adjusted TFP."""
    raw = pd.read_excel(os.path.join(raw_dir, "fernald_quarterly_tfp.xlsx"), sheet_name="annual")
    out = raw[list(COLUMNS)].rename(columns=COLUMNS)
    out = out[out.year >= 1950].dropna().copy()
    out["year"] = out.year.astype(int)
    out = out.round(4)
    out.to_csv(os.path.join(HERE, "tfp_annual.csv"), index=False)
    print(f"tfp_annual.csv: {out.year.min()}-{out.year.max()}, {len(out)} rows, "
          f"{int(out.isna().sum().sum())} missing")
    return out


def validate(out):
    """tfp_util must reproduce fig15-1.csv, and equal raw TFP minus utilization."""
    book = pd.read_csv(os.path.join(HERE, "fig15-1.csv"))
    both = book.merge(out, on="year", how="outer", indicator=True)
    if (both._merge != "both").any():
        raise SystemExit(f"years differ from fig15-1.csv: {list(both.year[both._merge != 'both'])}")
    gap = (both.tfp_growth - both.tfp_util).abs().max()
    if gap > 1e-4:
        raise SystemExit(f"tfp_util differs from fig15-1.csv by up to {gap}")
    identity = (out.tfp_solow - out.utilization - out.tfp_util).abs().max()
    if identity > 0.05:
        raise SystemExit(f"tfp_util != tfp_solow - utilization (max gap {identity})")
    print(f"validation: tfp_util equals fig15-1.csv in all {len(both)} years (max gap {gap:.1e}); "
          f"tfp_util = tfp_solow - utilization (max gap {identity:.1e})")


INPUTS = {"date": "year", "dY": "gdp_growth", "dhours": "hours_growth", "dk": "capital_growth",
          "dLQ": "labor_quality", "alpha": "capital_share", "dtfp": "tfp_solow", "dutil": "utilization",
          "dtfp_util": "tfp_util"}


def tfp_inputs(raw_dir, annual):
    """Fernald's growth-accounting inputs (Practice problems): output, hours, capital, labor quality, capital share."""
    raw = pd.read_excel(os.path.join(raw_dir, "fernald_quarterly_tfp.xlsx"), sheet_name="annual")
    out = raw[list(INPUTS)].rename(columns=INPUTS)
    out = out[out.year >= 1950].dropna().copy()
    out["year"] = out.year.astype(int)
    out = out.round(4)
    same = out.merge(annual, on="year", suffixes=("", "_a"))
    if len(same) != len(annual) or len(out) != len(annual):
        raise SystemExit("tfp_inputs.csv and tfp_annual.csv cover different years")
    for col in ["gdp_growth", "tfp_solow", "utilization", "tfp_util"]:
        if (same[col] - same[col + "_a"]).abs().max() > 1e-9:
            raise SystemExit(f"tfp_inputs.csv column {col} differs from tfp_annual.csv")
    a = out.capital_share
    rebuilt = out.gdp_growth - a * out.capital_growth - (1 - a) * (out.hours_growth + out.labor_quality)
    gap = (rebuilt - out.tfp_solow).abs().max()
    if gap > 0.15:
        raise SystemExit(f"Fernald's identity dtfp = dY - alpha dk - (1 - alpha)(dhours + dLQ) fails by {gap:.3f}")
    out.to_csv(os.path.join(HERE, "tfp_inputs.csv"), index=False)
    print(f"tfp_inputs.csv: {out.year.min()}-{out.year.max()}, {len(out)} rows; output, TFP and utilization equal "
          f"tfp_annual.csv; growth-accounting identity holds within {gap:.3f} points")

# readable names for the World Bank's formal ones (the same list as data/ch01/build_data.py)
RENAME = {"Korea, Rep.": "South Korea", "Korea, Dem. People's Rep.": "North Korea", "Egypt, Arab Rep.": "Egypt",
          "Iran, Islamic Rep.": "Iran", "Venezuela, RB": "Venezuela", "Russian Federation": "Russia",
          "Yemen, Rep.": "Yemen", "Congo, Dem. Rep.": "DR Congo", "Congo, Rep.": "Congo", "Gambia, The": "Gambia",
          "Bahamas, The": "Bahamas", "Hong Kong SAR, China": "Hong Kong", "Macao SAR, China": "Macao",
          "Lao PDR": "Laos", "Kyrgyz Republic": "Kyrgyzstan", "Slovak Republic": "Slovakia",
          "Micronesia, Fed. Sts.": "Micronesia", "Syrian Arab Republic": "Syria", "Viet Nam": "Vietnam",
          "Brunei Darussalam": "Brunei", "Turkiye": "Turkey", "Somalia, Fed. Rep.": "Somalia",
          "St. Martin (French part)": "St. Martin", "Naoero": "Nauru", "Cote d'Ivoire": "Côte d'Ivoire",
          "Sao Tome and Principe": "São Tomé and Príncipe", "Curacao": "Curaçao"}
REGIONS = {"Middle East, North Africa, Afghanistan & Pakistan": "Middle East & North Africa"}


def get(cache, url, file, params=None):
    """Download url into the cache folder once (requests' default User-Agent), return the local path."""
    path = os.path.join(cache, file)
    if os.path.exists(path):
        return path
    for k in range(4):
        try:
            r = requests.get(url, params=params, timeout=300)
            if r.status_code == 200:
                open(path, "wb").write(r.content)
                return path
        except requests.RequestException:
            pass
        time.sleep(10 * (k + 1))
    raise RuntimeError(f"download failed: {url}")


def pwt_growth(macro102, cache):
    """TFP and real GDP growth for every PWT 11.0 country with TFP data (log changes, percent)."""
    path = os.path.join(cache, "pwt110.dta")
    if not os.path.exists(path):
        bulk = os.path.join(macro102, ".work", "downloads", "pwt110.dta")
        if os.path.exists(bulk):
            shutil.copy(bulk, path)
        else:
            files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                                 params={"persistentId": "doi:10.34894/FABVLR"}, timeout=120).json()["data"]
            fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "pwt110.dta"][0]
            get(cache, f"https://dataverse.nl/api/access/datafile/{fid}", "pwt110.dta")
    d = pd.read_stata(path, columns=["countrycode", "year", "rtfpna", "rgdpna"]).sort_values(["countrycode", "year"])
    d["year"] = d.year.astype(int)
    for col, name in [("rtfpna", "tfp_growth"), ("rgdpna", "gdp_growth")]:
        d[name] = (100 * np.log(d[col]).groupby(d.countrycode).diff()).round(3)
    d = d.dropna(subset=["tfp_growth"]).rename(columns={"countrycode": "iso3"})
    p = get(cache, "https://api.worldbank.org/v2/country", "wdi_countries.json", {"format": "json", "per_page": 400})
    rows = [r for r in json.load(open(p))[1] if r["region"]["value"].strip() != "Aggregates"]
    names = pd.DataFrame({"iso3": [r["id"] for r in rows], "country": [RENAME.get(r["name"], r["name"]) for r in rows],
                          "region": [REGIONS.get(r["region"]["value"].strip(), r["region"]["value"].strip()) for r in rows]})
    names = pd.concat([names, pd.DataFrame([("TWN", "Taiwan", "East Asia & Pacific")], columns=names.columns)])
    out = d.merge(names, on="iso3")[["iso3", "country", "region", "year", "tfp_growth", "gdp_growth"]]
    out = out.sort_values(["country", "year"]).reset_index(drop=True)
    missing = sorted(set(d.iso3) - set(names.iso3))
    if missing:
        raise SystemExit(f"PWT countries with no name: {missing}")
    path = os.path.join(HERE, "pwt_growth.csv")
    out.to_csv(path, index=False)
    print(f"pwt_growth.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}, "
          f"{os.path.getsize(path) / 1000:.0f} kB")
    return out


def validate_pwt(out, annual):
    """The U.S. PWT TFP is a raw Solow residual: it should track Fernald's tfp_solow, not the adjusted tfp_util."""
    us = out[out.iso3 == "USA"].merge(annual, on="year")
    raw, util = us.tfp_growth.corr(us.tfp_solow), us.tfp_growth.corr(us.tfp_util)
    print(f"validation: U.S. PWT TFP growth {us.year.min()}-{us.year.max()} correlates {raw:.2f} with Fernald's raw "
          f"residual and {util:.2f} with the utilization-adjusted series; GDP growth corr "
          f"{us.gdp_growth_x.corr(us.gdp_growth_y):.2f}")
    if raw < 0.6:
        raise SystemExit("U.S. PWT TFP growth does not track Fernald's raw Solow residual")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    raw_dir = os.path.join(os.path.abspath(parser.parse_args().macro102), RAW)
    recessions(raw_dir)
    annual = tfp_annual(raw_dir)
    validate(annual)
    tfp_inputs(raw_dir, annual)
    macro102 = os.path.abspath(parser.parse_args().macro102)
    cache = os.path.join(macro102, ".work", "ch15", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    validate_pwt(pwt_growth(macro102, cache), annual)


if __name__ == "__main__":
    main()
