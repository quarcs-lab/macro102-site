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

Multi-country downloads (conventions §6b), cached in ../macro102/.work/ch02/notebook-raw/:
  World Bank WDI API (country list; NE.CON.PRVT.ZS, NE.GDI.TOTL.ZS, NE.CON.GOVT.ZS, NE.RSB.GNFS.ZS;
  NY.GDP.DEFL.ZS, NY.GDP.DEFL.KD.ZG) and Penn World Table 11.0 (pwt110.dta, labsh).
  countries.csv            iso3, country, region, income, g7, g20, oecd     lookup table for the country pickers
  expenditure_world.csv    iso3, country, year, consumption, investment, government, net_exports   percent of GDP
  labor_share_world.csv    iso3, country, year, labor_share              PWT 11.0 labsh, 1950-2023
  deflator_world.csv       iso3, country, year, deflator_2012_100, inflation     GDP deflator, 1960-2025
"""
import argparse
import json
import os
import shutil
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch02-measuring-the-macroeconomy/data"
LAST = 2025                                     # last year of the figure files; drops IMF/AMECO projections
G7 = ["CAN", "FRA", "DEU", "ITA", "JPN", "GBR", "USA"]
G20 = G7 + ["ARG", "AUS", "BRA", "CHN", "IND", "IDN", "KOR", "MEX", "RUS", "SAU", "ZAF", "TUR"]
OECD = ["AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC",
        "HUN", "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR",
        "POL", "PRT", "SVK", "SVN", "ESP", "SWE", "CHE", "TUR", "GBR", "USA"]
# readable names for the World Bank's formal ones (used for every file, so names agree across files)
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
# economies with no World Bank code: Maddison's historical units, Taiwan, and the euro-area aggregates
EXTRA = [("TWN", "Taiwan", "East Asia & Pacific"), ("SUN", "Former USSR", "Historical units"),
         ("CSK", "Czechoslovakia", "Historical units"), ("YUG", "Former Yugoslavia", "Historical units"),
         ("EMU", "Euro area", "Euro area aggregates")]


def get(cache, url, file, params=None):
    """Download url into the cache folder once (requests' default User-Agent), return the local path."""
    path = os.path.join(cache, file)
    if os.path.exists(path):
        return path
    for k in range(4):
        try:
            r = requests.get(url, params=params, timeout=180)
            if r.status_code == 200:
                open(path, "wb").write(r.content)
                return path
        except requests.RequestException:
            pass
        time.sleep(3 * (k + 1))
    raise RuntimeError(f"download failed: {url}")


def wdi(cache, indicator):
    """One WDI indicator for every economy: iso3, year, value (aggregates included)."""
    p = get(cache, f"https://api.worldbank.org/v2/country/all/indicator/{indicator}", f"wdi_{indicator}.json",
            {"format": "json", "per_page": 20000})
    rows = json.load(open(p))[1]
    out = pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows], "year": [int(r["date"]) for r in rows],
                        "value": [r["value"] for r in rows]})
    return out.dropna(subset=["value"])


def weo(cache, indicator):
    """One IMF WEO indicator from the DataMapper API: iso3, year, value (includes IMF projections)."""
    p = get(cache, f"https://www.imf.org/external/datamapper/api/v1/{indicator}", f"imf_{indicator}.json")
    vals = json.load(open(p))["values"][indicator]
    rows = [(c, int(y), v) for c, ys in vals.items() for y, v in ys.items()]
    return pd.DataFrame(rows, columns=["iso3", "year", "value"])


def country_table(cache):
    """countries.csv: every World Bank economy (no aggregates) plus EXTRA, with region, income and groups."""
    p = get(cache, "https://api.worldbank.org/v2/country", "wdi_countries.json", {"format": "json", "per_page": 400})
    rows = [r for r in json.load(open(p))[1] if r["region"]["value"].strip() != "Aggregates"]
    out = pd.DataFrame({"iso3": [r["id"] for r in rows],
                        "country": [RENAME.get(r["name"], r["name"]) for r in rows],
                        "region": [REGIONS.get(r["region"]["value"].strip(), r["region"]["value"].strip()) for r in rows],
                        "income": [r["incomeLevel"]["value"].strip() for r in rows]})
    extra = pd.DataFrame(EXTRA, columns=["iso3", "country", "region"]).assign(income="")
    out = pd.concat([out, extra], ignore_index=True)
    out.loc[out.iso3 == "TWN", "income"] = "High income"
    for name, members in [("g7", G7), ("g20", G20), ("oecd", OECD)]:
        out[name] = out.iso3.isin(members)
    return out.sort_values("country").reset_index(drop=True)


def tidy(df, names, value_cols, extra_cols=()):
    """Attach readable names, keep known economies, sort, and order the columns iso3, country, year, values."""
    df = df[df.iso3.isin(names.index)].copy()
    df.insert(1, "country", df.iso3.map(names))
    return df[["iso3", "country", "year", *value_cols, *extra_cols]].sort_values(["country", "year"])


def save(df, name, note=""):
    assert not df.duplicated(["iso3", "year"]).any(), f"{name} has duplicate country-years"
    path = os.path.join(HERE, name)
    df.to_csv(path, index=False)
    size = os.path.getsize(path) / 1e6
    assert size < 1, f"{name} is {size:.2f} MB"
    print(f"{name}: {len(df)} rows, {df.iso3.nunique()} economies, {df.year.min()}-{df.year.max()}, "
          f"{size * 1000:.0f} KB {note}")


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


def expenditure_world(cache, names):
    """Figures 1 and 2: expenditure shares of GDP in the World Bank's (SNA) definitions."""
    cols = {"consumption": "NE.CON.PRVT.ZS", "investment": "NE.GDI.TOTL.ZS", "government": "NE.CON.GOVT.ZS",
            "net_exports": "NE.RSB.GNFS.ZS"}
    d = None
    for col, code in cols.items():
        part = wdi(cache, code).rename(columns={"value": col})
        d = part if d is None else d.merge(part, on=["iso3", "year"], how="outer")
    d = d.dropna(subset=list(cols))                     # keep years with all four shares
    zero = (d.consumption == 0) & (d.government == 0)   # placeholder rows (Venezuela 1991-2011 is all zeros)
    print(f"  dropped {zero.sum()} rows whose shares are all reported as 0: {sorted(set(d[zero].iso3))}")
    d = d[~zero]
    for col in cols:
        d[col] = d[col].round(2) + 0.0                  # + 0.0 turns -0.0 into 0.0
    out = tidy(d[d.year <= LAST], names, list(cols))
    save(out, "expenditure_world.csv")
    us = out[out.iso3 == "USA"].set_index("year")
    book = pd.read_csv(os.path.join(HERE, "fig2-1.csv")).set_index("year")
    for col in cols:
        gap = (us[col] - book[col + "_share"]).dropna()
        print(f"  U.S. WDI minus BEA (fig2-1.csv) {col:12} {gap.index.min()}-{gap.index.max()}: mean {gap.mean():+.2f} points")
    total = out[list(cols)].sum(axis=1)
    print(f"  the four WDI shares add up to between {total.min():.1f} and {total.max():.1f} percent "
          f"(median {total.median():.1f})")


def labor_share_world(macro102, cache, names):
    """Figure 3: labor share of GDP from Penn World Table 11.0 (labsh)."""
    path = os.path.join(cache, "pwt110.dta")
    if not os.path.exists(path):
        bulk = os.path.join(macro102, ".work", "downloads", "pwt110.dta")       # collect-data's bulk cache
        if os.path.exists(bulk):
            shutil.copy(bulk, path)
        else:
            files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                                 params={"persistentId": "doi:10.34894/FABVLR"}, timeout=120).json()["data"]
            fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "pwt110.dta"][0]
            get(cache, f"https://dataverse.nl/api/access/datafile/{fid}", "pwt110.dta")
    pwt = pd.read_stata(path, columns=["countrycode", "year", "labsh"]).dropna(subset=["labsh"])
    d = pd.DataFrame({"iso3": pwt.countrycode, "year": pwt.year.astype(int), "labor_share": pwt.labsh.round(4)})
    out = tidy(d, names, ["labor_share"])
    save(out, "labor_share_world.csv")
    us = out[out.iso3 == "USA"].set_index("year").labor_share
    book = pd.read_csv(os.path.join(HERE, "fig2-3.csv")).set_index("year").labor_share
    gap = (us - book).dropna()
    print(f"  U.S. PWT labsh minus the book measure (fig2-3.csv), {gap.index.min()}-{gap.index.max()}: "
          f"mean {gap.mean():+.3f}, range {gap.min():+.3f} to {gap.max():+.3f}")


def deflator_world(cache, names):
    """Figures 4 and 5: GDP deflator rebased to 2012 = 100 (WDI NY.GDP.DEFL.ZS, whose base year differs by
    country) and GDP-deflator inflation (WDI NY.GDP.DEFL.KD.ZG)."""
    level = wdi(cache, "NY.GDP.DEFL.ZS").rename(columns={"value": "deflator"})
    base = level[level.year == 2012].set_index("iso3").deflator
    level = level[level.iso3.isin(base.index)].copy()
    rebased = 100 * level.deflator / level.iso3.map(base)
    level["deflator_2012_100"] = rebased.map(lambda x: float(f"{x:.6g}"))   # 6 significant digits: values span 1e-9 to 1e14
    infl = wdi(cache, "NY.GDP.DEFL.KD.ZG").rename(columns={"value": "inflation"})
    d = level.merge(infl, on=["iso3", "year"], how="outer")
    d["inflation"] = d.inflation.round(2) + 0.0             # + 0.0 turns -0.0 into 0.0
    out = tidy(d[d.year <= LAST], names, ["deflator_2012_100", "inflation"])
    save(out, "deflator_world.csv")
    us = out[out.iso3 == "USA"].set_index("year")
    book = pd.read_csv(os.path.join(HERE, "fig2-4.csv"), parse_dates=["date"])
    book = book.groupby(book.date.dt.year).gdp_deflator_2012_100.mean()
    lvl = (us.deflator_2012_100 / book - 1).dropna() * 100
    gr = (us.inflation - 100 * book.pct_change()).dropna()
    print(f"  U.S. WDI level vs annual mean of fig2-4.csv: largest gap {lvl.abs().max():.2f} percent; "
          f"inflation vs its growth rate: largest gap {gr.abs().max():.2f} points")


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

    # ---- multi-country files (conventions §6b) ------------------------------------------
    cache = os.path.join(root, ".work", "ch02", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    countries = country_table(cache)
    countries.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(countries)} economies")
    names = countries.set_index("iso3").country
    expenditure_world(cache, names)
    labor_share_world(root, cache, names)
    deflator_world(cache, names)


if __name__ == "__main__":
    main()
