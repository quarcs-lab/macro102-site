"""Build the data files of Appendix F (The Augmented Solow Growth Model).

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Downloads are cached in <macro102>/.work/appF/notebook-raw/ (delete a file there to download it again):
  mrw2.dta                the data of Mankiw, Romer and Weil (1992), as kept by QuaRCS-lab
                          (github.com/quarcs-lab/data-quarcs, mrw1992/mrw2.dta)
  pwt110.dta              Penn World Table 11.0 (DataverseNL, doi:10.34894/FABVLR), copied from macro102's
                          .work/appD/notebook-raw/ or .work/downloads/ when it exists
  wdi_<code>.json         World Bank WDI series, all countries, 1960-2023 (see WDI below)
Outputs (next to this script):
  mrw1992.csv             the 121 countries of MRW: their three sample flags and their data, 1960-1985
  pwt_mrw.csv             the same variables rebuilt from PWT 11.0 and the WDI, one row per economy and
                          window (1960-1985 and 1990-2023), with the MRW sample flags of each economy
Checks: MRW's sample sizes (98, 75, 22) and the first column of their Table I; no duplicate rows; every MRW
country mapped to an ISO code; each file under 1 MB.
"""
import argparse
import json
import os
import shutil

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
MRW_URL = "https://github.com/quarcs-lab/data-quarcs/raw/master/mrw1992/mrw2.dta"
PWT_DOI = "doi:10.34894/FABVLR"
WINDOWS = [(1960, 1985), (1990, 2023)]
WDI = {"SE.SEC.ENRR": "enroll",            # school enrollment, secondary (% gross)
       "SP.POP.1519.FE.5Y": "f1519_pct",   # population ages 15-19, female (% of female population)
       "SP.POP.1519.MA.5Y": "m1519_pct",   # population ages 15-19, male (% of male population)
       "SP.POP.TOTL.FE.IN": "pop_f",       # population, female
       "SP.POP.TOTL.MA.IN": "pop_m",       # population, male
       "SP.POP.1564.TO": "pop1564"}        # population ages 15-64, total
# The oil producers that the book drops from the full sample (the list of Appendix E)
OIL = ["DZA", "AGO", "AZE", "BHR", "BRN", "TCD", "COG", "ECU", "GNQ", "GAB", "IRN", "IRQ", "KAZ", "KWT",
       "NGA", "OMN", "QAT", "RUS", "SAU", "TTO", "TKM", "ARE", "VEN", "YEM", "LBY", "TLS", "SDN"]
# MRW's country names -> ISO 3166 alpha-3 codes (West Germany -> DEU, Zaire -> COD, Burma -> MMR)
ISO3 = {
    "Algeria": "DZA", "Angola": "AGO", "Benin": "BEN", "Botswana": "BWA", "Burkina Faso": "BFA",
    "Burundi": "BDI", "Cameroon": "CMR", "Central Afr. Rep.": "CAF", "Chad": "TCD", "Congo,": "COG",
    "Egypt": "EGY", "Ethiopia": "ETH", "Gabon": "GAB", "Gambia, The": "GMB", "Ghana": "GHA", "Guinea": "GIN",
    "Ivory Coast": "CIV", "Kenya": "KEN", "Lesotho": "LSO", "Liberia": "LBR", "Madagascar": "MDG",
    "Malawi": "MWI", "Mali": "MLI", "Mauritania": "MRT", "Mauritius": "MUS", "Morocco": "MAR",
    "Mozambique": "MOZ", "Niger": "NER", "Nigeria": "NGA", "Rwanda": "RWA", "S. Africa": "ZAF",
    "Senegal": "SEN", "Sierra Leone": "SLE", "Somalia": "SOM", "Sudan": "SDN", "Swaziland": "SWZ",
    "Tanzania": "TZA", "Togo": "TGO", "Tunisia": "TUN", "Uganda": "UGA", "Zaire": "COD", "Zambia": "ZMB",
    "Zimbabwe": "ZWE", "Afghanistan": "AFG", "Bahrain": "BHR", "Bangladesh": "BGD", "Burma": "MMR",
    "Hong Kong": "HKG", "India": "IND", "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Israel": "ISR",
    "Japan": "JPN", "Jordan": "JOR", "Korea, South": "KOR", "Kuwait": "KWT", "Malaysia": "MYS",
    "Nepal": "NPL", "Oman": "OMN", "Pakistan": "PAK", "Philippines": "PHL", "Saudi Arabia": "SAU",
    "Singapore": "SGP", "Sri Lanka": "LKA", "Syria": "SYR", "Taiwan": "TWN", "Thailand": "THA",
    "Turkey": "TUR", "U.A.E.": "ARE", "Yemen": "YEM", "Austria": "AUT", "Belgium": "BEL", "Cyprus": "CYP",
    "Denmark": "DNK", "Finland": "FIN", "France": "FRA", "Germany, W.": "DEU", "Greece": "GRC",
    "Iceland": "ISL", "Ireland": "IRL", "Italy": "ITA", "Luxembourg": "LUX", "Malta": "MLT",
    "Netherlands": "NLD", "Norway": "NOR", "Portugal": "PRT", "Spain": "ESP", "Sweden": "SWE",
    "Switzerland": "CHE", "United Kingdom": "GBR", "Argentina": "ARG", "Barbados": "BRB", "Bolivia": "BOL",
    "Brazil": "BRA", "Chile": "CHL", "Colombia": "COL", "Costa Rica": "CRI", "Dominican Rep.": "DOM",
    "Ecuador": "ECU", "El Salvador": "SLV", "Guatemala": "GTM", "Guyana": "GUY", "Haiti": "HTI",
    "Honduras": "HND", "Jamaica": "JAM", "Mexico": "MEX", "Nicaragua": "NIC", "Panama": "PAN",
    "Paraguay": "PRY", "Peru": "PER", "Surinam": "SUR", "Trinidad and Tobago": "TTO", "Uruguay": "URY",
    "Venezuela": "VEN", "Canada": "CAN", "United States": "USA", "Australia": "AUS", "Fiji": "FJI",
    "New Zealand": "NZL", "Papua New Guinea": "PNG"}
# Readable names for the few MRW countries whose 1992 names are abbreviated or have changed
MRW_NAMES = {"Central Afr. Rep.": "Central African Republic", "Congo,": "Congo", "S. Africa": "South Africa",
             "Gambia, The": "Gambia", "Korea, South": "South Korea", "U.A.E.": "United Arab Emirates",
             "Germany, W.": "West Germany", "Dominican Rep.": "Dominican Republic", "Surinam": "Suriname",
             "Ivory Coast": "Côte d'Ivoire", "Zaire": "Zaire (DR Congo)", "Burma": "Burma (Myanmar)",
             "Swaziland": "Swaziland (Eswatini)"}


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
    """pwt110.dta in the cache: copied from another macro102 cache, or downloaded from DataverseNL."""
    path = os.path.join(cache, "pwt110.dta")
    for other in (".work/appD/notebook-raw/pwt110.dta", ".work/downloads/pwt110.dta"):
        if not os.path.exists(path) and os.path.exists(os.path.join(macro102, other)):
            shutil.copy(os.path.join(macro102, other), path)
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


def mrw(cache):
    """mrw1992.csv: MRW's data with readable column names, ISO codes and readable country names."""
    d = pd.read_stata(cached(cache, "mrw2.dta", MRW_URL))
    missing = sorted(set(d.country) - set(ISO3))
    if missing:
        raise SystemExit(f"no ISO code for MRW countries {missing}")
    out = pd.DataFrame({
        "iso3": d.country.map(ISO3),
        "country": d.country.replace(MRW_NAMES),
        "region": d.region.replace({"LatinAmerica": "Latin America", "NorthAmerica": "North America"}),
        "non_oil": d.n.astype(int), "intermediate": d.i.astype(int), "oecd": d.o.astype(int),
        "gdp_60": d.rgdpw60, "gdp_85": d.rgdpw85,
        "gdp_growth": d.gdpgrowth.astype("float64").round(2),
        "pop_growth": d.popgrowth.astype("float64").round(2),
        "inv_gdp": d.i_y.astype("float64").round(2),
        "school": d.school.astype("float64").round(2)})
    if out.iso3.duplicated().any():
        raise SystemExit("two MRW countries share an ISO code")
    sizes = (out.non_oil.sum(), out.intermediate.sum(), out.oecd.sum())
    if sizes != (98, 75, 22):
        raise SystemExit(f"MRW samples have {sizes} countries, not (98, 75, 22)")
    # Check: the first column of MRW's Table I (non-oil sample)
    x = out[out.non_oil == 1].dropna(subset=["gdp_85", "pop_growth"])
    X = np.column_stack([np.ones(len(x)), np.log(x.inv_gdp / 100), np.log(x.pop_growth / 100 + 0.05)])
    b = np.linalg.lstsq(X, np.log(x.gdp_85), rcond=None)[0]
    print(f"mrw1992.csv: {len(out)} countries; samples {sizes}; Table I non-oil: "
          f"ln(s) {b[1]:.2f} (MRW 1.42), ln(n+g+d) {b[2]:.2f} (MRW -1.97), N {len(x)} (MRW 98)")
    if abs(b[1] - 1.42) > 0.01:
        raise SystemExit("the Table I check failed")
    out.to_csv(os.path.join(HERE, "mrw1992.csv"), index=False)
    return out


def wdi(cache):
    """The WDI series of WDI, one row per country and year."""
    frames = []
    for code, name in WDI.items():
        path = cached(cache, f"wdi_{code}.json", f"https://api.worldbank.org/v2/country/all/indicator/{code}",
                      params={"format": "json", "per_page": 20000, "date": "1960:2023"})
        page = json.load(open(path))
        if page[0]["pages"] != 1:
            raise SystemExit(f"{code}: the WDI answer has {page[0]['pages']} pages")
        rows = page[1]
        frames.append(pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows],
                                    "year": [int(r["date"]) for r in rows],
                                    name: [r["value"] for r in rows]}).set_index(["iso3", "year"]))
    d = pd.concat(frames, axis=1).reset_index()
    d = d[d.iso3.str.len() == 3]
    # MRW's SCHOOL: the secondary enrollment rate times the share of the working-age population aged 15-19
    d["pop1519"] = d.f1519_pct / 100 * d.pop_f + d.m1519_pct / 100 * d.pop_m
    d["school"] = d.enroll * d.pop1519 / d.pop1564
    return d


def pwt_mrw(cache, macro102, mrw_data):
    """pwt_mrw.csv: MRW's variables rebuilt from PWT 11.0 and the WDI, for each window."""
    pwt = pd.read_stata(pwt_file(cache, macro102),
                        columns=["countrycode", "country", "year", "pop", "rgdpe", "csh_i", "hc"])
    pwt = pwt.rename(columns={"countrycode": "iso3"})
    pwt["year"] = pwt.year.astype(int)
    pwt["country"] = pwt.country.astype(str)
    school = wdi(cache)
    regions = pd.read_csv(os.path.join(HERE, "..", "ch01", "countries.csv")).set_index("iso3").region
    flags = mrw_data.set_index("iso3")[["non_oil", "intermediate", "oecd"]]
    rows = []
    for start, end in WINDOWS:
        w = pwt[(pwt.year >= start) & (pwt.year <= end)]
        s = school[(school.year >= start) & (school.year <= end)]
        for iso3, g in w.groupby("iso3"):
            g = g.set_index("year")
            if g.loc[[start, end], ["pop", "rgdpe"]].isna().any().any() or g.csh_i.isna().any():
                continue                       # we need GDP and population at both ends, and every investment rate
            sc = s[s.iso3 == iso3].school.dropna()
            rows.append({
                "iso3": iso3, "country": g.country.iloc[0], "region": regions.get(iso3, ""),
                "window": f"{start}-{end}", "start": start, "end": end,
                "gdppc_start": g.loc[start, "rgdpe"] / g.loc[start, "pop"],      # both in millions: dollars per person
                "gdppc_end": g.loc[end, "rgdpe"] / g.loc[end, "pop"],
                "pop_start": g.loc[start, "pop"],
                "s_k": 100 * g.csh_i.mean(),
                "n": 100 * np.log(g.loc[end, "pop"] / g.loc[start, "pop"]) / (end - start),
                "school": sc.mean() if len(sc) else np.nan, "school_years": len(sc),
                "hc_end": g.loc[end, "hc"],
                "mrw_non_oil": int(flags.non_oil.get(iso3, 0)), "mrw_intermediate": int(flags.intermediate.get(iso3, 0)),
                "mrw_oecd": int(flags.oecd.get(iso3, 0)), "in_mrw": int(iso3 in flags.index),
                "oil": int(iso3 in OIL), "small": int(g.loc[start, "pop"] < 1)})
    out = pd.DataFrame(rows)
    for c in ["gdppc_start", "gdppc_end", "pop_start", "s_k", "n", "school", "hc_end"]:
        out[c] = round_sig(out[c])
    if out.duplicated(["iso3", "window"]).any():
        raise SystemExit("duplicate rows in pwt_mrw.csv")
    out.to_csv(os.path.join(HERE, "pwt_mrw.csv"), index=False)
    for window, g in out.groupby("window"):
        full = g[(g.oil == 0) & (g.small == 0)]
        print(f"pwt_mrw.csv {window}: {len(g)} economies; MRW non-oil {g.mrw_non_oil.sum()}, intermediate "
              f"{g.mrw_intermediate.sum()}, OECD {g.mrw_oecd.sum()}; full sample {len(full)}; with school "
              f"{full.school.notna().sum()}, with hc {full.hc_end.notna().sum()}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    cache = os.path.join(args.macro102, ".work", "appF", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    mrw_data = mrw(cache)
    pwt_mrw(cache, args.macro102, mrw_data)
    for f in ("mrw1992.csv", "pwt_mrw.csv"):
        size = os.path.getsize(os.path.join(HERE, f))
        print(f"{f}: {size / 1e3:.0f} kB")
        if size > 1e6:
            raise SystemExit(f"{f} is larger than 1 MB")


if __name__ == "__main__":
    main()
