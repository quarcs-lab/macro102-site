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

Multi-country files (conventions 6b), downloaded from public sources with requests' default User-Agent and
cached in ../macro102/.work/ch19/notebook-raw/ (delete a cached file to download it again):
  countries.csv           iso3, country, region, income  (World Bank country metadata; one row per economy below)
  wdi_trade.csv           iso3, country, year, exports, imports, trade_balance  (WDI, percent of GDP, 1960-2025)
  pwt_trade_world.csv     iso3, country, vintage, year, csh_c, csh_i, csh_g, cgdpo, rgdpna, pop  (PWT 11.0, 1990-2023)
  twin_deficits_world.csv iso3, country, year, investment, budget_deficit, trade_deficit  (WDI + IMF WEO, 1980-2025)
  niip_world.csv          iso3, country, year, niip  (Lane & Milesi-Ferretti External Wealth of Nations, 1970-2024)
Checks: the U.S. rows are compared with fig19-1, fig19-2, fig19-5 and fig19-6, and the nine countries of
pwt_trade.csv (PWT 11.0) are reproduced exactly by pwt_trade_world.csv.
"""
import argparse
import json
import os

import pandas as pd
import requests

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


# ---- multi-country files (conventions 6b) -----------------------------------------------------------
WDI = "https://api.worldbank.org/v2/country/all/indicator/{}?format=json&per_page=20000&date=1960:2025"
WEO = "https://www.imf.org/external/datamapper/api/v1/{}"
EWN = "https://www.brookings.edu/wp-content/uploads/2026/02/EWN-dataset-year-end-2024_4.9.26.xlsx"
PWT11 = ("doi:10.34894/FABVLR", "pwt110.dta")
# readable names; the nine countries of the textbook figures keep the labels of pwt_trade.csv
RENAME = {"United States": "U.S.", "Korea, Rep.": "S. Korea", "Bahamas, The": "Bahamas", "Congo, Dem. Rep.": "DR Congo",
          "Congo, Rep.": "Congo", "Egypt, Arab Rep.": "Egypt", "Micronesia, Fed. Sts.": "Micronesia",
          "Gambia, The": "Gambia", "Hong Kong SAR, China": "Hong Kong", "Iran, Islamic Rep.": "Iran",
          "Macao SAR, China": "Macao", "St. Martin (French part)": "St. Martin", "Puerto Rico (US)": "Puerto Rico",
          "Korea, Dem. People's Rep.": "North Korea", "Somalia, Fed. Rep.": "Somalia", "Russian Federation": "Russia",
          "Sint Maarten (Dutch part)": "Sint Maarten", "Syrian Arab Republic": "Syria", "Venezuela, RB": "Venezuela",
          "Virgin Islands (U.S.)": "U.S. Virgin Islands", "Yemen, Rep.": "Yemen", "Lao PDR": "Laos",
          "Kyrgyz Republic": "Kyrgyzstan", "Slovak Republic": "Slovakia", "Viet Nam": "Vietnam",
          "Brunei Darussalam": "Brunei", "Naoero": "Nauru", "Cote d'Ivoire": "Côte d'Ivoire", "Turkiye": "Türkiye"}
REGION = {"Middle East, North Africa, Afghanistan & Pakistan": "Middle East & North Africa"}
EXTRA = {"TWN": ("Taiwan", "East Asia & Pacific", "High income"),      # economies missing from the WDI list
         "AIA": ("Anguilla", "Latin America & Caribbean", ""), "MSR": ("Montserrat", "Latin America & Caribbean", ""),
         "GGY": ("Guernsey", "Europe & Central Asia", ""), "JEY": ("Jersey", "Europe & Central Asia", "")}
# External Wealth of Nations (IMF IFS names) -> ISO3, for the names that differ from the WDI and IMF lists
EWN_ISO = {"Afghanistan, I.R. of": "AFG", "Cape Verde": "CPV", "Central African Rep.": "CAF",
           "China,P.R.: Mainland": "CHN", "China,P.R.:Macao": "MAC", "Congo, Dem. Rep. of": "COD",
           "Congo, Republic of": "COG", "Czech Republic": "CZE", "Guernsey": "GGY", "Hong Kong": "HKG", "Iran, Islamic Republic of": "IRN",
           "Jersey": "JEY", "Korea": "KOR", "Lao People's Dem.Rep": "LAO", "Micronesia": "FSM", "Nauru": "NRU",
           "Russia": "RUS", "St. Vincent & Grens.": "VCT", "São Tomé & Príncipe": "STP", "Taiwan": "TWN",
           "Turkey": "TUR", "Turks and Caicos": "TCA", "Venezuela, Rep. Bol.": "VEN", "Yemen, Republic of": "YEM"}


def cached(raw, name, url):
    """Download url once into raw/name (requests' default User-Agent) and return the local path."""
    path = os.path.join(raw, name)
    if not os.path.exists(path):
        r = requests.get(url, timeout=300)
        r.raise_for_status()
        open(path, "wb").write(r.content)
        print(f"downloaded {url} -> {name}")
    return path


def wdi(raw, code):
    """One WDI indicator for every economy as a Series indexed by (iso3, year), aggregates excluded later."""
    rows = json.load(open(cached(raw, f"wdi_{code}.json", WDI.format(code))))[1]
    s = pd.Series({(r["countryiso3code"], int(r["date"])): r["value"] for r in rows if r["countryiso3code"]})
    return pd.to_numeric(s, errors="coerce").rename_axis(["iso3", "year"])


def country_table(raw):
    """countries.csv: iso3, readable name, World Bank region and income group, for economies (no aggregates)."""
    meta = json.load(open(cached(raw, "wdi_countries.json", "https://api.worldbank.org/v2/country?format=json&per_page=400")))[1]
    rows = []
    for m in meta:
        if m["region"]["value"] != "Aggregates":
            region = m["region"]["value"].strip()
            rows.append([m["id"], RENAME.get(m["name"], m["name"]), REGION.get(region, region), m["incomeLevel"]["value"]])
    for iso, (name, region, income) in EXTRA.items():
        rows.append([iso, name, region, income])
    return pd.DataFrame(rows, columns=["iso3", "country", "region", "income"]).set_index("iso3")


def tidy(frame, names, decimals=2):
    """Long table iso3, country, year, values...: economies only, rows with no value dropped, rounded."""
    out = frame.dropna(how="all").reset_index()
    out = out[out.iso3.isin(names.index)]
    out.insert(1, "country", out.iso3.map(names.country))
    return out.sort_values(["country", "year"]).round(decimals)


def save(out, name):
    path = os.path.join(HERE, name)
    out.to_csv(path, index=False)
    size = os.path.getsize(path) / 1e3
    if size > 1000:
        raise SystemExit(f"{name} is {size:.0f} kB, above the 1 MB limit")
    print(f"{name}: {len(out)} rows, {out.iso3.nunique()} economies, {out.year.min()}-{out.year.max()}, {size:.0f} kB")


def us_gap(ours, theirs, label):
    """Report the largest gap between the U.S. rows of a world file and the textbook-figure CSV."""
    both = ours.dropna().index.intersection(theirs.dropna().index)
    diff = (ours[both] - theirs[both]).abs()
    print(f"U.S. check {label}: {len(both)} years, largest gap {diff.max():.3f} points ({diff.idxmax()})")
    return diff


def wdi_trade(root, raw, names):
    frame = pd.concat([wdi(raw, "NE.EXP.GNFS.ZS").rename("exports"), wdi(raw, "NE.IMP.GNFS.ZS").rename("imports"),
                       wdi(raw, "NE.RSB.GNFS.ZS").rename("trade_balance")], axis=1)
    out = tidy(frame, names)
    us = out[out.iso3 == "USA"].set_index("year")
    f1 = pd.read_csv(os.path.join(root, "fig19-1/data.csv")).set_index("year")
    f2 = pd.read_csv(os.path.join(root, "fig19-2/data.csv")).set_index("year")
    for col, theirs in [("exports", f1.exports_share), ("imports", f1.imports_share),
                        ("trade_balance", f2.trade_balance_pct_gdp)]:
        if us_gap(us[col], theirs, f"WDI {col} vs fig19-1/2").max() > 0.3:
            raise SystemExit("WDI U.S. trade shares differ from BEA by more than 0.3 points")
    save(out, "wdi_trade.csv")


def pwt_world(macro102, raw, names):
    path = os.path.join(raw, PWT11[1])
    if not os.path.exists(path):                       # reuse collect-data's bulk cache, else ask DataverseNL
        bulk = os.path.join(macro102, ".work", "downloads", PWT11[1])
        if os.path.exists(bulk):
            path = bulk
        else:
            files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                                 params={"persistentId": PWT11[0]}, timeout=60).json()["data"]
            fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == PWT11[1]][0]
            path = cached(raw, PWT11[1], f"https://dataverse.nl/api/access/datafile/{fid}")
    pwt = pd.read_stata(path)
    cols = ["csh_c", "csh_i", "csh_g", "cgdpo", "rgdpna", "pop"]
    pwt = pwt[pwt.year >= 1990].dropna(subset=["csh_c", "csh_i", "csh_g", "cgdpo"])
    frame = pwt.rename(columns={"countrycode": "iso3"}).set_index(["iso3", "year"])[cols].astype("float64")
    out = tidy(frame, names, decimals=6)
    out.insert(2, "vintage", "PWT 11.0")                  # the same columns, in the same order, as pwt_trade.csv
    out["year"] = out.year.astype(int)
    out[["cgdpo", "rgdpna"]] = out[["cgdpo", "rgdpna"]].round(1)
    out["pop"] = out["pop"].round(4)
    old = pd.read_csv(os.path.join(HERE, "pwt_trade.csv"))
    old = old[old.vintage == "PWT 11.0"].set_index(["iso3", "year"])
    new = out.set_index(["iso3", "year"]).loc[old.index]
    gap = (new[["csh_c", "csh_i", "csh_g"]] - old[["csh_c", "csh_i", "csh_g"]]).abs().max().max()
    rel = ((new.cgdpo - old.cgdpo) / old.cgdpo).abs().max()      # float32 storage in the .dta: rounding only
    if gap > 2e-6 or rel > 1e-6 or (new.country != old.country).any():
        raise SystemExit(f"pwt_trade_world.csv does not reproduce pwt_trade.csv (gap {gap}, cgdpo {rel})")
    print(f"validated pwt_trade_world.csv against pwt_trade.csv: {len(old)} rows, largest gap {gap:.1e} "
          f"in the shares, {rel:.1e} (relative) in cgdpo")
    save(out, "pwt_trade_world.csv")


def twin_world(root, raw, names):
    weo = json.load(open(cached(raw, "weo_GGXCNL_NGDP.json", WEO.format("GGXCNL_NGDP"))))
    rows = [(iso, int(y), v) for iso, d in weo["values"]["GGXCNL_NGDP"].items() for y, v in d.items()]
    budget = pd.DataFrame(rows, columns=["iso3", "year", "v"]).set_index(["iso3", "year"]).v
    frame = pd.concat([wdi(raw, "NE.GDI.TOTL.ZS").rename("investment"), (-budget).rename("budget_deficit"),
                       (-wdi(raw, "NE.RSB.GNFS.ZS")).rename("trade_deficit")], axis=1)
    frame = frame[(frame.index.get_level_values("year") >= 1980) & (frame.index.get_level_values("year") <= 2025)]
    out = tidy(frame, names)
    us = out[out.iso3 == "USA"].set_index("year")
    f5 = pd.read_csv(os.path.join(root, "fig19-5/data.csv")).set_index("year")
    if us_gap(us.trade_deficit, f5.trade_deficit_pct_gdp, "trade deficit vs fig19-5").max() > 0.3:
        raise SystemExit("WDI U.S. trade deficit differs from BEA by more than 0.3 points")
    for col, theirs, what in [("investment", f5.investment_pct_gdp, "gross capital formation vs private investment"),
                              ("budget_deficit", f5.budget_deficit_pct_gdp, "general vs federal government")]:
        d = (us[col] - theirs).dropna()
        print(f"U.S. {col} ({what}): on average {d.mean():+.2f} points above fig19-5 ({d.index.min()}-{d.index.max()})")
    save(out, "twin_deficits_world.csv")


def niip_world(root, raw, names):
    ewn = pd.read_excel(cached(raw, os.path.basename(EWN), EWN), sheet_name="Dataset")
    lookup = {}
    for iso, row in names.iterrows():
        lookup[row.country] = iso
    wb = json.load(open(os.path.join(raw, "wdi_countries.json")))[1]
    for m in wb:
        lookup[m["name"]] = m["id"]
    ewn["iso3"] = ewn.Country.map(EWN_ISO).fillna(ewn.Country.map(lookup))
    dropped = sorted(ewn[ewn.iso3.isna()].Country.unique())
    print(f"External Wealth of Nations: not economies with an ISO3 code, dropped: {dropped}")
    ewn = ewn.dropna(subset=["iso3"])
    for col in ["Net IIP excl gold", "Monetary Gold", "GDP (US$)"]:
        ewn[col] = pd.to_numeric(ewn[col], errors="coerce")      # a few cells hold a blank " "
    # net position including gold (= the official IIP where one exists) over GDP, both in US dollars;
    # the sheet's own ratio column covers only the years with an official IIP
    position = ewn["Net IIP excl gold"] + ewn["Monetary Gold"].fillna(0)
    ewn["niip"] = 100 * position / ewn["GDP (US$)"]
    niip = ewn.set_index(["iso3", "Year"]).niip
    out = tidy(niip.rename_axis(["iso3", "year"]).to_frame(), names)
    us = out[out.iso3 == "USA"].set_index("year")
    f6 = pd.read_csv(os.path.join(root, "fig19-6/data.csv")).set_index("year")
    gap = us_gap(us.niip, f6.niip_pct_gdp, "EWN net IIP vs fig19-6 (BEA, current)")
    print(f"   up to 2019 the largest gap is {gap.loc[:2019].max():.2f} points; 2020-2024: "
          f"{(us.niip - f6.niip_pct_gdp).loc[2020:2024].round(1).to_dict()} (an earlier BEA vintage)")
    if gap.loc[:2019].max() > 1.0:
        raise SystemExit("EWN U.S. position differs from BEA by more than 1 point before 2020")
    save(out, "niip_world.csv")


def world_files(macro102):
    raw = os.path.join(macro102, ".work", "ch19", "notebook-raw")
    os.makedirs(raw, exist_ok=True)
    root = os.path.join(macro102, DATA)
    names = country_table(raw)
    wdi_trade(root, raw, names)
    pwt_world(macro102, raw, names)
    twin_world(root, raw, names)
    niip_world(root, raw, names)
    used = set()
    for f in ["wdi_trade.csv", "pwt_trade_world.csv", "twin_deficits_world.csv", "niip_world.csv"]:
        used |= set(pd.read_csv(os.path.join(HERE, f)).iso3)
    table = names.loc[sorted(used)].reset_index().sort_values("country")
    table.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(table)} economies in {table.region.nunique()} regions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    us_trade(root)
    pwt_trade(root)
    world_files(args.macro102)


if __name__ == "__main__":
    main()
