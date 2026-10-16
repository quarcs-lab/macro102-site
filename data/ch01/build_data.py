"""Build the wider data files used by the Chapter 1 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch01-introduction-to-macroeconomics/data/):
  fig1-1/raw/mpd2023_subset.csv          Maddison Project Database 2023: countrycode, country, region, year, gdppc, pop
  fig1-1/raw/fred_A191RD3A086NBEA.csv    U.S. GDP deflator (BEA via FRED), to express 2011 dollars in 2022 dollars
  fig1-2/raw/fred_USREC.csv              NBER recession indicator, monthly (1 = recession month)
  fig1-4/raw/ameco1.zip                  European Commission AMECO, chapter 1 (unemployment rates ZUTN)
Multi-country downloads (conventions §6b), cached in ../macro102/.work/ch01/notebook-raw/:
  World Bank WDI API (country list; SL.EMP.TOTL.SP.ZS; FP.CPI.TOTL.ZG; SL.UEM.TOTL.ZS; NE.RSB.GNFS.ZS),
  IMF World Economic Outlook DataMapper API (GGXCNL_NGDP), Maddison Project Database 2023 (mpd2023_web.xlsx),
  World Bank Global Inflation Database (Inflation-data.xlsx, sheet hcpi_a; fills WDI's CPI gaps).
  The two workbooks are copied from macro102's .work/downloads/ when /collect-data already fetched them.
Outputs (next to this script):
  maddison_annual.csv      iso3, country, year, gdppc       six countries of Figure 1.1 + Ethiopia, 1870-2022
  recessions.csv           peak, trough                     NBER peaks and troughs since 1960
  countries.csv            iso3, country, region, income, g7, g20, oecd     lookup table for the country pickers
  maddison_world.csv       iso3, country, year, gdppc       every Maddison country, every year 1870-2022 with data
  employment_world.csv     iso3, country, year, emp_pop_ratio            ILO modelled estimate, ages 15+, 1991-
  inflation_world.csv      iso3, country, year, inflation, source        CPI inflation, 1960-2025
  unemployment_world.csv   iso3, country, year, unrate, source           unemployment rate, 1955-2025
  deficits_world.csv       iso3, country, year, budget_deficit, trade_deficit, source     percent of GDP, 1960-2025
"""
import argparse
import io
import json
import os
import shutil
import time
import zipfile

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch01-introduction-to-macroeconomics/data/"
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
         ("EMU", "Euro area", "Euro area aggregates"), ("EA12", "Europe", "Euro area aggregates")]


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


def maddison(root):
    """Annual Maddison GDP per person in 2022 dollars (same conversion as fig1-1.csv)."""
    defl = pd.read_csv(os.path.join(root, "fig1-1/raw/fred_A191RD3A086NBEA.csv"))
    defl["year"] = defl.observation_date.str[:4].astype(int)
    defl = defl.set_index("year").A191RD3A086NBEA
    factor = defl[2022] / defl[2011]
    mpd = pd.read_csv(os.path.join(root, "fig1-1/raw/mpd2023_subset.csv"))
    mpd = mpd[(mpd.year >= 1870) & (mpd.year <= 2022)].dropna(subset=["gdppc"])
    out = pd.DataFrame({"iso3": mpd.countrycode, "country": mpd.country, "year": mpd.year,
                        "gdppc": (mpd.gdppc * factor).round(0).astype(int)})
    out.to_csv(os.path.join(HERE, "maddison_annual.csv"), index=False)
    print(f"maddison_annual.csv: {len(out)} rows, {out.iso3.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}, factor 2011->2022 = {factor:.4f}")
    # validation: the benchmark years of fig1-1.csv
    fig = pd.read_csv(os.path.join(HERE, "fig1-1.csv")).set_index("year")
    worst = 0
    for iso in ["usa", "gbr", "jpn", "arg", "zaf", "chn"]:
        ours = out[out.iso3 == iso.upper()].set_index("year").gdppc.reindex(fig.index)
        worst = max(worst, (ours - fig["gdppc_" + iso]).abs().max())
    print(f"  largest difference from fig1-1.csv at the benchmark years: {worst:.0f} dollars")
    return factor


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = pd.read_csv(os.path.join(root, "fig1-2/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    rec = rec.set_index("observation_date").USREC
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    out["peak"] = out.peak.dt.strftime("%Y-%m-%d")
    out["trough"] = out.trough.dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def maddison_world(macro102, cache, names, factor):
    """Figures 1 and 7: every Maddison country, annual 1870-2022, 2022 dollars."""
    path = os.path.join(cache, "mpd2023_web.xlsx")
    if not os.path.exists(path):
        bulk = os.path.join(macro102, ".work", "downloads", "mpd2023_web.xlsx")   # collect-data's bulk cache
        if os.path.exists(bulk):
            shutil.copy(bulk, path)
        else:
            files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                                 params={"persistentId": "doi:10.34894/INZBF2"}, timeout=120).json()["data"]
            fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "mpd2023_web.xlsx"][0]
            get(cache, f"https://dataverse.nl/api/access/datafile/{fid}", "mpd2023_web.xlsx")
    mpd = pd.read_excel(path, sheet_name="Full data")
    mpd = mpd[(mpd.year >= 1870) & (mpd.year <= 2022)].dropna(subset=["gdppc"])
    out = pd.DataFrame({"iso3": mpd.countrycode, "year": mpd.year, "gdppc": (mpd.gdppc * factor).round(0).astype(int)})
    out = tidy(out, names, ["gdppc"])
    save(out, "maddison_world.csv")
    old = pd.read_csv(os.path.join(HERE, "maddison_annual.csv"))
    both = old.merge(out, on=["iso3", "year"], suffixes=("_old", ""))
    print(f"  equals maddison_annual.csv (so fig1-1.csv) on all {len(both)} common rows: "
          f"{(both.gdppc_old == both.gdppc).all()}")


def employment_world(cache, names):
    """Figure 2: employment-to-population ratio, ages 15+ (ILO modelled estimate, WDI SL.EMP.TOTL.SP.ZS)."""
    d = wdi(cache, "SL.EMP.TOTL.SP.ZS").rename(columns={"value": "emp_pop_ratio"})
    d["emp_pop_ratio"] = d.emp_pop_ratio.round(2) + 0.0
    out = tidy(d[d.year <= LAST], names, ["emp_pop_ratio"])
    save(out, "employment_world.csv")
    us = out[out.iso3 == "USA"].set_index("year").emp_pop_ratio
    book = pd.read_csv(os.path.join(HERE, "fig1-2.csv"), parse_dates=["date"])
    book = book.groupby(book.date.dt.year).emp_pop_ratio.mean()
    gap = (us - book).dropna()
    print(f"  U.S. ILO 15+ minus BLS 16+ annual mean (fig1-2.csv), {gap.index.min()}-{gap.index.max()}: "
          f"mean {gap.mean():+.2f}, range {gap.min():+.2f} to {gap.max():+.2f} points")


def gid_file(cache):
    """The World Bank Global Inflation Database workbook (cached; 5.6 MB)."""
    path = os.path.join(cache, "wb_Inflation-data.xlsx")
    if not os.path.exists(path):
        bulk = os.path.join(os.path.dirname(os.path.dirname(cache)), "downloads", "wb_Inflation-data.xlsx")
        if os.path.exists(bulk):
            shutil.copy(bulk, path)
        else:
            get(cache, "https://thedocs.worldbank.org/en/doc/1ad246272dbbc437c74323719506aa0c-0350012021/"
                       "original/Inflation-data.xlsx", "wb_Inflation-data.xlsx")
    return path


def inflation_world(cache, names):
    """Figure 3: CPI inflation (WDI FP.CPI.TOTL.ZG); the four economies of the book come from fig1-3.csv."""
    d = wdi(cache, "FP.CPI.TOTL.ZG").rename(columns={"value": "inflation"})
    d["source"] = "WDI"
    # WDI drops years with doubtful official CPIs (e.g. Argentina 2007-2017); the World Bank's Global Inflation
    # Database (Ha, Kose & Ohnsorge), sheet hcpi_a, 1970-2024, fills those country-years
    gid = pd.read_excel(gid_file(cache), sheet_name="hcpi_a")
    gid = gid.melt(id_vars=["Country Code"], value_vars=[c for c in gid.columns if isinstance(c, int)],
                   var_name="year", value_name="inflation").rename(columns={"Country Code": "iso3"})
    gid = gid.dropna(subset=["inflation"]).assign(source="GID")
    have = set(zip(d.iso3, d.year))
    d = pd.concat([d, gid[[(a, b) not in have for a, b in zip(gid.iso3, gid.year)]]])
    book = pd.read_csv(os.path.join(HERE, "fig1-3.csv"))
    cols = {"USA": "inflation_us", "GBR": "inflation_uk", "EMU": "inflation_euro_area", "JPN": "inflation_japan"}
    for iso, col in cols.items():
        w = d[d.iso3 == iso].set_index("year").inflation
        gap = (w - book.set_index("year")[col]).dropna().abs()
        print(f"  {iso}: WDI vs fig1-3.csv, {len(gap)} common years, largest gap {gap.max():.3f} points")
    swap = pd.concat([pd.DataFrame({"iso3": iso, "year": book.year, "inflation": book[col],
                                    "source": "fig1-3.csv"}) for iso, col in cols.items()])
    d = pd.concat([d[~d.iso3.isin(list(cols))], swap.dropna(subset=["inflation"])])
    d["inflation"] = d.inflation.astype(float).round(2) + 0.0     # + 0.0 turns -0.0 into 0.0
    out = tidy(d[(d.year >= 1960) & (d.year <= LAST)], names, ["inflation"], ["source"])
    save(out, "inflation_world.csv")


def ameco_unemployment(root):
    """AMECO unemployment rates (ZUTN): iso3, year, value."""
    with zipfile.ZipFile(os.path.join(root, "fig1-4/raw/ameco1.zip")) as z:
        txt = z.read(z.namelist()[0]).decode("latin-1")
    d = pd.read_csv(io.StringIO(txt), sep=";", dtype=str)
    d.columns = [c.strip() for c in d.columns]
    d = d[d.CODE.str.endswith(".1.0.0.0.ZUTN")]
    years = [c for c in d.columns if c.isdigit()]
    d = d.melt(id_vars=["CODE"], value_vars=years, var_name="year", value_name="value")
    d["value"] = pd.to_numeric(d.value.str.strip(), errors="coerce")
    d["year"] = d.year.astype(int)
    d["iso3"] = d.CODE.str.split(".").str[0].replace({"ROM": "ROU"})
    return d.dropna(subset=["value"])[["iso3", "year", "value"]]


def unemployment_world(root, cache, names):
    """Figure 4: unemployment rates. Book series for the U.S., Europe and Japan (fig1-4.csv); AMECO for the
    other countries it covers (from 1960); WDI ILO modelled estimates (from 1991) for the OECD and G20
    members AMECO lacks."""
    book = pd.read_csv(os.path.join(HERE, "fig1-4.csv"))
    am = ameco_unemployment(root)
    for iso, col in [("USA", "unrate_us"), ("JPN", "unrate_japan")]:
        a = am[am.iso3 == iso].set_index("year").value
        gap = (a - book.set_index("year")[col]).dropna().loc[:LAST].abs()
        print(f"  AMECO {iso} vs fig1-4.csv: {len(gap)} common years, mean gap {gap.mean():.2f}, largest {gap.max():.2f}")
    parts = [pd.DataFrame({"iso3": iso, "year": book.year, "unrate": book[col], "source": src})
             for iso, col, src in [("USA", "unrate_us", "fig1-4.csv (BLS)"),
                                   ("EA12", "unrate_europe", "fig1-4.csv (AMECO EA12)"),
                                   ("JPN", "unrate_japan", "fig1-4.csv (OECD)")]]
    am = am[am.iso3.isin(names.index) & ~am.iso3.isin(["USA", "JPN", "EMU", "EA12"])]
    parts.append(pd.DataFrame({"iso3": am.iso3, "year": am.year, "unrate": am.value, "source": "AMECO"}))
    ilo = wdi(cache, "SL.UEM.TOTL.ZS")
    ilo = ilo[ilo.iso3.isin(set(OECD + G20) - set(am.iso3) - {"USA", "JPN"})]
    parts.append(pd.DataFrame({"iso3": ilo.iso3, "year": ilo.year, "unrate": ilo.value,
                               "source": "WDI (ILO modelled)"}))
    d = pd.concat(parts).dropna(subset=["unrate"])
    d["unrate"] = d.unrate.round(2) + 0.0
    out = tidy(d[d.year <= LAST], names, ["unrate"], ["source"])
    save(out, "unemployment_world.csv")


def deficits_world(cache, names):
    """Figure 5: budget deficit (IMF WEO general government net borrowing, sign flipped) and trade deficit
    (WDI external balance on goods and services, sign flipped), percent of GDP. U.S. rows from fig1-5.csv."""
    budget = weo(cache, "GGXCNL_NGDP")
    budget = budget.assign(budget_deficit=-budget.value)[["iso3", "year", "budget_deficit"]]
    trade = wdi(cache, "NE.RSB.GNFS.ZS")
    trade = trade.assign(trade_deficit=-trade.value)[["iso3", "year", "trade_deficit"]]
    d = budget.merge(trade, on=["iso3", "year"], how="outer")
    d = d[(d.year <= LAST) & (d.iso3 != "USA")]
    d["source"] = "IMF WEO + WDI"
    book = pd.read_csv(os.path.join(HERE, "fig1-5.csv"))
    us = pd.DataFrame({"iso3": "USA", "year": book.year, "budget_deficit": book.budget_deficit_pct_gdp,
                       "trade_deficit": book.trade_deficit_pct_gdp, "source": "fig1-5.csv (federal)"})
    # validation of the cross-country sources against the U.S. book series
    imf_us = -weo(cache, "GGXCNL_NGDP").query("iso3 == 'USA' and year <= @LAST").set_index("year").value
    wdi_us = -wdi(cache, "NE.RSB.GNFS.ZS").query("iso3 == 'USA'").set_index("year").value
    b = (imf_us - book.set_index("year").budget_deficit_pct_gdp).dropna()
    t = (wdi_us - book.set_index("year").trade_deficit_pct_gdp).dropna()
    print(f"  U.S. IMF general government minus federal (fig1-5.csv), {b.index.min()}-{b.index.max()}: mean {b.mean():+.2f} points")
    print(f"  U.S. WDI trade deficit minus fig1-5.csv, {t.index.min()}-{t.index.max()}: largest gap {t.abs().max():.2f} points")
    d = pd.concat([d, us])
    d = d.dropna(subset=["budget_deficit", "trade_deficit"], how="all")
    d["budget_deficit"] = d.budget_deficit.round(2) + 0.0      # + 0.0 turns -0.0 into 0.0
    d["trade_deficit"] = d.trade_deficit.round(2) + 0.0
    out = tidy(d, names, ["budget_deficit", "trade_deficit"], ["source"])
    save(out, "deficits_world.csv")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work", "ch01", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    factor = maddison(root)
    recessions(root)
    countries = country_table(cache)
    countries.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(countries)} economies")
    names = countries.set_index("iso3").country
    maddison_world(args.macro102, cache, names, factor)
    employment_world(cache, names)
    inflation_world(cache, names)
    unemployment_world(root, cache, names)
    deficits_world(cache, names)


if __name__ == "__main__":
    main()
