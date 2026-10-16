"""Build the wider data files used by the Chapter 20 notebook.

usage: python build_data.py [--macro102 PATH] [--refresh]     (PATH defaults to the sibling ../macro102 checkout)

1. big_mac.csv (Table 20.1, Figures 2-3), from files saved by the macro102 /collect-data skill:
  - The Economist's Big Mac index, open data
    (original-scanned-book/ch20-exchange-rates-and-international-finance/data/table20-1/raw/big-mac-raw-index.csv;
    columns date, iso_a3, currency_code, name, local_price, dollar_ex, dollar_price, ...);
  - the Penn World Table 11.0 subset of Chapter 5
    (original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv;
    columns countrycode, country, year, rgdpo, pop, csh_i), for GDP per person in 2023.
  Output: one row per economy and Big Mac release (2000-04 to 2026-07):
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

2. Multi-country files (conventions section 6b), downloaded from public sources and cached in
   PATH/.work/ch20/notebook-raw/. Every file is tidy and long (iso3, country, year or date, values) and uses the
   country names of countries.csv. Each one is validated against the textbook-figure CSV of this folder:
   countries.csv            World Bank country list: region, income group, OECD and euro-area membership
   fx_monthly.csv           Figure 1: currency units per U.S. dollar, monthly, Federal Reserve H.10 (FRED)
   inflation_wdi.csv        Figure 2: CPI inflation, annual, World Bank WDI (FP.CPI.TOTL.ZG)
   rer_pwt.csv              Figure 3: price level of GDP relative to the U.S. (PWT 11.0 pl_gdpo)
   fx_history.csv           Figure 6: currency units per U.S. dollar, annual, 1870-2020 (Jorda-Schularick-Taylor)
   fx_crises.csv            Figure 8: currency units per U.S. dollar, end of year, 1990-2025 (IMF ER dataset)
   yields_monthly.csv       Figure 9: 10-year government bond yields, monthly (OECD via FRED, Eurostat)
   credit_wdi.csv           Figure 10: bank credit to the private sector, % of GDP (World Bank GFDD and WDI)
   current_account_imf.csv  Figure 11: current account balance, % of GDP (IMF WEO)
   debt.csv                 Figure 12: general government debt, % of GDP (OECD Economic Outlook and IMF WEO)
   ulc_oecd.csv             Figure 13: unit labour costs, 2020 = 100 (OECD Productivity Database)
   tfp_pwt.csv              Figure 14: total factor productivity at constant national prices (PWT 11.0 rtfpna)
"""
import argparse
import json
import os
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CH20 = "original-scanned-book/ch20-exchange-rates-and-international-finance/data/table20-1"
PWT = "original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv"
REFRESH = False
RAW = None                     # PATH/.work/ch20/notebook-raw, set in main()
MACRO102 = None
LAST_YEAR = 2025               # last actual year for annual IMF/OECD series (later years are projections)

# --- country metadata ----------------------------------------------------------------------------------------------
NAMES = {   # readable names for the World Bank's formal ones
    "KOR": "South Korea", "PRK": "North Korea", "EGY": "Egypt", "IRN": "Iran", "VEN": "Venezuela",
    "HKG": "Hong Kong", "MAC": "Macao", "RUS": "Russia", "TUR": "Türkiye", "SVK": "Slovakia", "YEM": "Yemen",
    "GMB": "The Gambia", "BHS": "The Bahamas", "COD": "DR Congo", "COG": "Congo", "LAO": "Laos",
    "KGZ": "Kyrgyzstan", "FSM": "Micronesia", "SYR": "Syria", "VNM": "Vietnam", "CIV": "Côte d'Ivoire",
    "BRN": "Brunei", "SOM": "Somalia", "CZE": "Czechia", "STP": "São Tomé and Príncipe", "CUW": "Curaçao",
    "VIR": "U.S. Virgin Islands", "KNA": "St. Kitts and Nevis", "VCT": "St. Vincent and the Grenadines",
    "LCA": "St. Lucia", "MAF": "St. Martin", "PSE": "West Bank and Gaza",
}
EXTRA = [   # economies that are not in the World Bank list
    ("TWN", "Taiwan", "East Asia & Pacific", "High income"),
    ("EMU", "Euro area", "Euro area", "High income"),
    ("ANT", "Netherlands Antilles (former)", "Latin America & Caribbean", "High income"),
    ("CSK", "Czechoslovakia (former)", "Europe & Central Asia", "Upper middle income"),
    ("YUG", "Yugoslavia (former)", "Europe & Central Asia", "Upper middle income"),
    ("AIA", "Anguilla", "Latin America & Caribbean", "High income"),
    ("MSR", "Montserrat", "Latin America & Caribbean", "High income"),
]
RECODE = {"EURO": "EMU", "G163": "EMU", "EA17": "EMU", "EA20": "EMU",   # source codes for the euro area,
          "UVK": "XKX", "KOS": "XKX", "WBG": "PSE"}                    # Kosovo and West Bank and Gaza
SHORT_REGION = {"Middle East, North Africa, Afghanistan & Pakistan": "Middle East & North Africa"}
OECD = ("AUS AUT BEL CAN CHL COL CRI CZE DNK EST FIN FRA DEU GRC HUN ISL IRL ISR ITA JPN KOR LVA LTU LUX MEX NLD NZL "
        "NOR POL PRT SVK SVN ESP SWE CHE TUR GBR USA").split()
EURO_SINCE = {**{c: 1999 for c in "AUT BEL FIN FRA DEU IRL ITA LUX NLD PRT ESP".split()}, "GRC": 2001, "SVN": 2007,
              "CYP": 2008, "MLT": 2008, "SVK": 2009, "EST": 2011, "LVA": 2014, "LTU": 2015, "HRV": 2023, "BGR": 2026}


def get(url, name, **kw):
    """Download url once into RAW/name (requests' default User-Agent; FRED and the IMF block custom ones)."""
    path = os.path.join(RAW, name)
    if REFRESH or not os.path.exists(path):
        r = requests.get(url, timeout=300, **kw)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def countries():
    """countries.csv: one row per economy with its World Bank region and income group, OECD and euro membership."""
    meta = json.load(open(get("https://api.worldbank.org/v2/country?format=json&per_page=400", "wb_countries.json")))[1]
    rows = []
    for m in meta:
        region = m["region"]["value"].strip()
        if region == "Aggregates":
            continue
        rows.append((m["id"], NAMES.get(m["id"], m["name"]), SHORT_REGION.get(region, region),
                     m["incomeLevel"]["value"].strip()))
    out = pd.DataFrame(rows + EXTRA, columns=["iso3", "country", "region", "income"])
    out["oecd"] = out.iso3.isin(OECD)
    out["euro_since"] = out.iso3.map(EURO_SINCE).astype("Int64")
    return out.sort_values("iso3").reset_index(drop=True)


def tidy(df, meta, keys):
    """Attach readable names, keep known economies only, order the columns iso3, country, keys..., values."""
    df = df.assign(iso3=df.iso3.replace(RECODE))
    df = df.merge(meta[["iso3", "country"]], on="iso3", how="inner")
    values = [c for c in df.columns if c not in ["iso3", "country"] + keys]
    return df[["iso3", "country"] + keys + values].sort_values(["iso3"] + keys).reset_index(drop=True)


def fred(series):
    """One FRED series as a Series indexed by date (missing values '.' become NaN)."""
    path = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}", f"fred_{series}.csv")
    d = pd.read_csv(path, na_values=".")
    return d.set_index(d.columns[0])[series].rename(series)


def wdi(code):
    """All economies and years of one World Bank indicator, as iso3, year, value."""
    path = get(f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000",
               f"wdi_{code}.json")
    rows = [(r["countryiso3code"], int(r["date"]), r["value"]) for r in json.load(open(path))[1]]
    return pd.DataFrame(rows, columns=["iso3", "year", "value"]).dropna()


def pwt():
    """The Penn World Table 11.0 Stata file (the bulk cache of macro102 /collect-data, else DataverseNL)."""
    path = os.path.join(MACRO102, ".work", "downloads", "pwt110.dta")
    if not os.path.exists(path):
        files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                             params={"persistentId": "doi:10.34894/FABVLR"}, timeout=60).json()["data"]
        file_id = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "pwt110.dta"][0]
        path = get(f"https://dataverse.nl/api/access/datafile/{file_id}", "pwt110.dta")
    return pd.read_stata(path, columns=["countrycode", "year", "pl_gdpo", "rtfpna"]).rename(
        columns={"countrycode": "iso3"})


def book(name):
    return pd.read_csv(os.path.join(HERE, name))


def report(name, df, key, check):
    size = os.path.getsize(os.path.join(HERE, name))
    print(f"{name}: {len(df)} rows, {df.iso3.nunique()} economies, {key} {df[key].min()} to {df[key].max()}, "
          f"{size / 1e3:.0f} kB; validation: {check}")
    assert size < 1e6, f"{name} is over 1 MB"


def save(df, name):
    df.to_csv(os.path.join(HERE, name), index=False)


# --- Figure 1: H.10 exchange rates ------------------------------------------------------------------------------------
H10 = {   # FRED series: (iso3, currency, inverted?) -- inverted series are quoted in U.S. dollars per unit
    "EXJPUS": ("JPN", "yen", False), "EXUSEU": ("EMU", "euro", True), "EXUSUK": ("GBR", "pound", True),
    "EXCAUS": ("CAN", "Canadian dollar", False), "EXSZUS": ("CHE", "Swiss franc", False),
    "EXCHUS": ("CHN", "yuan", False), "EXKOUS": ("KOR", "won", False), "EXINUS": ("IND", "rupee", False),
    "EXMXUS": ("MEX", "Mexican peso", False), "EXBZUS": ("BRA", "real", False),
    "EXSDUS": ("SWE", "Swedish krona", False), "EXNOUS": ("NOR", "Norwegian krone", False),
    "EXDNUS": ("DNK", "Danish krone", False), "EXUSAL": ("AUS", "Australian dollar", True),
    "EXUSNZ": ("NZL", "New Zealand dollar", True), "EXHKUS": ("HKG", "Hong Kong dollar", False),
    "EXSIUS": ("SGP", "Singapore dollar", False), "EXTAUS": ("TWN", "Taiwan dollar", False),
    "EXTHUS": ("THA", "baht", False), "EXMAUS": ("MYS", "ringgit", False), "EXSLUS": ("LKA", "Sri Lanka rupee", False),
    "EXSFUS": ("ZAF", "rand", False), "EXGEUS": ("DEU", "Deutsche mark", False),
    "EXFRUS": ("FRA", "French franc", False), "EXITUS": ("ITA", "Italian lira", False),
}


def fx_monthly(meta):
    frames = []
    for series, (iso3, currency, inverted) in H10.items():
        s = fred(series).dropna()
        s = 1 / s if inverted else s
        frames.append(pd.DataFrame({"iso3": iso3, "currency": currency, "date": s.index.str[:7],
                                    "per_usd": s.values}))
    df = pd.concat(frames)
    df["per_usd"] = df.per_usd.map(lambda v: float(f"{v:.5g}"))      # 5 significant digits
    df = tidy(df, meta, ["date"])[["iso3", "country", "currency", "date", "per_usd"]]
    save(df, "fx_monthly.csv")
    old = book("fig20-1.csv")
    old["date"] = old.date.str[:7]
    w = df.pivot(index="date", columns="iso3", values="per_usd")
    gap = max((w.JPN.reindex(old.date).values / old.yen_per_usd.values - 1).__abs__().max(),
              np.nanmax(abs(w.EMU.reindex(old.date).values / old.eur_per_usd.values - 1)))
    report("fx_monthly.csv", df, "date", f"yen and euro vs fig20-1.csv, largest relative gap {gap:.1e}")


# --- Figure 2: inflation ---------------------------------------------------------------------------------------------
def inflation(meta):
    df = wdi("FP.CPI.TOTL.ZG").rename(columns={"value": "inflation"})
    df["inflation"] = df.inflation.round(3)
    df = tidy(df, meta, ["year"])
    save(df, "inflation_wdi.csv")
    old = book("fig20-2.csv").set_index("year")
    w = df.pivot(index="year", columns="iso3", values="inflation")
    gap = max((w.USA - old.inflation_us).abs().max(), (w.JPN - old.inflation_jpn).abs().max())
    report("inflation_wdi.csv", df, "year", f"U.S. and Japan vs fig20-2.csv, largest gap {gap:.3f} points")


# --- Figures 3 and 14: Penn World Table --------------------------------------------------------------------------------
def pwt_files(meta):
    p = pwt()
    us = p[p.iso3 == "USA"].set_index("year").pl_gdpo
    p["rer"] = (p.pl_gdpo / p.year.map(us)).round(4)               # price level of GDP, U.S. = 1 in every year
    rer = tidy(p.dropna(subset=["rer"])[["iso3", "year", "rer"]], meta, ["year"])
    save(rer, "rer_pwt.csv")
    jpn = rer[rer.iso3 == "JPN"].set_index("year").rer.loc[1971:]
    gap = (100 * jpn / jpn.loc[1971] - book("fig20-3.csv").set_index("year").rer_jpn).abs().max()
    report("rer_pwt.csv", rer, "year", f"Japan, 1971 = 100, vs fig20-3.csv, largest gap {gap:.3f}")

    p["rtfpna"] = p.rtfpna.round(4)
    tfp = tidy(p.dropna(subset=["rtfpna"])[["iso3", "year", "rtfpna"]], meta, ["year"])
    save(tfp, "tfp_pwt.csv")
    w = tfp.pivot(index="year", columns="iso3", values="rtfpna").loc[1990:]
    old = book("fig20-14.csv").set_index("year")
    gap = 0.0
    for iso3 in ["USA", "DEU", "JPN", "FRA", "ESP", "ITA"]:
        gap = max(gap, (100 * w[iso3] / w.loc[2000, iso3] - old[f"tfp_{iso3.lower()}"]).abs().max())
    report("tfp_pwt.csv", tfp, "year", f"six countries, 2000 = 100, vs fig20-14.csv, largest gap {gap:.3f}")


# --- Figure 6: 150 years of exchange rates (Jorda-Schularick-Taylor) ---------------------------------------------------
def fx_history(meta):
    jst = pd.read_stata(get("https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.xlsx",
                            "JSTdatasetR6.dta"))                     # a Stata file, despite the .xlsx name
    df = jst[["iso", "year", "xrusd"]].rename(columns={"iso": "iso3", "xrusd": "per_usd"}).dropna()
    df = df[df.iso3 != "USA"].copy()
    df["year"] = df.year.astype(int)
    df["per_usd"] = df.per_usd.map(lambda v: float(f"{v:.5g}"))
    df = tidy(df, meta, ["year"])
    save(df, "fx_history.csv")
    uk = df[df.iso3 == "GBR"].set_index("year").per_usd
    rel = (uk / book("fig20-6.csv").set_index("year").gbp_per_usd - 1).abs().dropna()
    report("fx_history.csv", df, "year", f"U.K. vs fig20-6.csv (MeasuringWorth): median relative gap "
           f"{rel.median():.4f}, {int((rel > 0.02).sum())} of {len(rel)} years differ by more than 2% "
           f"(largest {rel.max():.2f} in {rel.idxmax()})")


# --- Figure 8: currency crises (IMF ER dataset) -------------------------------------------------------------------------
def fx_crises(meta):
    path = get("https://api.imf.org/external/sdmx/2.1/data/IMF.STA,ER/.XDC_USD.EOP_RT.A?startPeriod=1990",
               "imf_er_xdc_usd_eop_a_all.xml")
    rows = []
    for series in ET.parse(path).getroot().iter():
        if series.tag.endswith("Series"):
            for obs in series:
                if "OBS_VALUE" in obs.attrib:
                    rows.append((series.attrib["COUNTRY"], int(obs.attrib["TIME_PERIOD"]),
                                 float(obs.attrib["OBS_VALUE"])))
    df = pd.DataFrame(rows, columns=["iso3", "year", "per_usd_eop"]).drop_duplicates(["iso3", "year"])
    df = df[df.per_usd_eop > 0].copy()
    df["per_usd_eop"] = df.per_usd_eop.map(lambda v: float(f"{v:.6g}"))
    df = tidy(df, meta, ["year"])
    save(df, "fx_crises.csv")
    w = df.pivot(index="year", columns="iso3", values="per_usd_eop")
    old = book("fig20-8.csv").set_index("year")
    gap = 0.0
    for iso3, col in [("ARG", "argentina"), ("KOR", "korea"), ("MEX", "mexico"), ("IDN", "indonesia")]:
        gap = max(gap, (100 * w.loc[1991, iso3] / w[iso3] - old[col]).abs().max())
    report("fx_crises.csv", df, "year", f"four book countries, 1991 = 100, vs fig20-8.csv, largest gap {gap:.3f}")


# --- Figure 9: bond yields ----------------------------------------------------------------------------------------------
FRED_YIELDS = ("AT AU BE CA CH CL CZ DE DK ES FI FR GB GR HU IE IL IS IT JP KR LU MX NL NO NZ PL PT RU SE SI SK US "
               "ZA").split()
EUROSTAT_YIELDS = ["CY", "EE", "HR", "LT", "LV", "MT", "BG", "RO"]   # EU members without an OECD series on FRED


def yields(meta):
    iso2 = {}
    for m in json.load(open(get("https://api.worldbank.org/v2/country?format=json&per_page=400",
                                "wb_countries.json")))[1]:
        iso2[m["iso2Code"]] = m["id"]
    frames = []
    for cc in FRED_YIELDS:
        s = fred(f"IRLTLT01{cc}M156N").dropna()
        frames.append(pd.DataFrame({"iso3": iso2[cc], "date": s.index.str[:7], "yield": s.values,
                                    "source": "OECD"}))
    path = get("https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/irt_lt_mcby_m/M.MCBY."
               + "+".join(EUROSTAT_YIELDS) + "/?format=SDMX-CSV", "eurostat_irt_lt_mcby_m.csv")
    es = pd.read_csv(path).dropna(subset=["OBS_VALUE"])
    frames.append(pd.DataFrame({"iso3": es.geo.map(iso2), "date": es.TIME_PERIOD, "yield": es.OBS_VALUE,
                                "source": "Eurostat"}))
    df = pd.concat(frames)
    df = df[df.date >= "1990-01"].copy()
    df["yield"] = df["yield"].round(3)
    df = tidy(df, meta, ["date"])[["iso3", "country", "date", "yield", "source"]]
    save(df, "yields_monthly.csv")
    old = book("fig20-9.csv")
    old["date"] = old.date.str[:7]
    w = df.pivot(index="date", columns="iso3", values="yield").reindex(old.date)
    gap = max(np.nanmax(abs(w[iso3].values - old[col].values))
              for iso3, col in [("DEU", "yield_de"), ("ESP", "yield_es"), ("ITA", "yield_it")])
    report("yields_monthly.csv", df, "date", f"Germany, Spain, Italy vs fig20-9.csv, largest gap {gap:.4f} points")


# --- Figure 10: bank lending --------------------------------------------------------------------------------------------
def credit(meta):
    gfdd = wdi("GFDD.DI.01").rename(columns={"value": "bank_credit"})
    priv = wdi("FD.AST.PRVT.GD.ZS").rename(columns={"value": "private_credit"})
    df = gfdd.merge(priv, on=["iso3", "year"], how="outer")
    df = df[df.year >= 1990].round({"bank_credit": 2, "private_credit": 2})
    df = tidy(df, meta, ["year"])
    save(df, "credit_wdi.csv")
    old = book("fig20-10.csv").set_index("iso3")
    w = df.set_index(["iso3", "year"])
    gap = 0.0
    for iso3 in old.index:
        for y in [1998, 2002, 2007]:
            gap = max(gap, abs(w.loc[(iso3, y), "bank_credit"] - old.loc[iso3, f"credit_gdp_{y}"]))
        gap = max(gap, abs(w.loc[(iso3, 2023), "private_credit"] - old.loc[iso3, "credit_gdp_2023"]))
    report("credit_wdi.csv", df, "year", f"six book countries vs fig20-10.csv, largest gap {gap:.3f}")


# --- Figures 11 and 12: IMF WEO and OECD Economic Outlook -------------------------------------------------------------
def imf(indicator):
    data = json.load(open(get(f"https://www.imf.org/external/datamapper/api/v1/{indicator}",
                              f"imf_{indicator}.json")))["values"][indicator]
    rows = []
    for iso3 in data:
        for year in data[iso3]:
            rows.append((iso3, int(year), data[iso3][year]))
    df = pd.DataFrame(rows, columns=["iso3", "year", "value"]).dropna()
    return df[df.year <= LAST_YEAR].assign(iso3=df.iso3.replace(RECODE))


def current_account(meta):
    df = imf("BCA_NGDPD").rename(columns={"value": "ca_gdp"}).round({"ca_gdp": 3})
    df = tidy(df, meta, ["year"])
    save(df, "current_account_imf.csv")
    old = book("fig20-11.csv").set_index("iso3")
    w = df.pivot(index="year", columns="iso3", values="ca_gdp")
    gap = 0.0
    for first, last in [(1993, 1997), (2003, 2007), (2008, 2011), (2021, 2025)]:
        mean = w.loc[first:last, old.index].mean()
        gap = max(gap, (mean - old[f"ca_gdp_{first}_{last}"]).abs().max())
    report("current_account_imf.csv", df, "year", f"six book countries vs fig20-11.csv, largest gap {gap:.3f}")


def debt(meta):
    path = get("https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.GGFLQ.A?startPeriod=1990",
               "oecd_eo_GGFLQ.csv", headers={"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"})
    eo = pd.read_csv(path)
    eo = pd.DataFrame({"iso3": eo.REF_AREA.replace(RECODE), "year": eo.TIME_PERIOD,
                       "debt_oecd": eo.OBS_VALUE})
    eo = eo[eo.year <= LAST_YEAR]
    weo = imf("GGXWDG_NGDP").rename(columns={"value": "debt_imf"})
    df = eo.merge(weo, on=["iso3", "year"], how="outer")
    df = df[df.year >= 1990].round({"debt_oecd": 2, "debt_imf": 2})
    df = tidy(df, meta, ["year"])
    save(df, "debt.csv")
    old = book("fig20-12.csv").set_index("iso3")
    w = df.pivot(index="year", columns="iso3", values="debt_oecd")
    gap = max((w.loc[y, old.index] - old[f"debt_gdp_{y}"]).abs().max() for y in [2007, 2012, 2017, 2025])
    report("debt.csv", df, "year", f"debt_oecd of six book countries vs fig20-12.csv, largest gap {gap:.3f}")


def ulc(meta):
    path = get("https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PDB@DF_PDB,/.A.ULCE._T.XDC.V.IX._Z._Z"
               "?startPeriod=1990", "oecd_pdb_ULCE.csv",
               headers={"Accept": "application/vnd.sdmx.data+csv; charset=utf-8"})
    pdb = pd.read_csv(path)
    pdb = pdb[pdb.REF_AREA != "EU27_2020"]
    df = pd.DataFrame({"iso3": pdb.REF_AREA, "year": pdb.TIME_PERIOD,
                       "ulc": pdb.OBS_VALUE.round(3)})
    df = tidy(df, meta, ["year"])
    save(df, "ulc_oecd.csv")
    w = df.pivot(index="year", columns="iso3", values="ulc").loc[1995:]
    old = book("fig20-13.csv").set_index("year")
    gap = max((100 * w[iso3] / w.loc[1995, iso3] - old[f"ulc_{iso3.lower()}"]).abs().max()
              for iso3 in ["GRC", "ITA", "ESP", "FRA", "DEU"])
    report("ulc_oecd.csv", df, "year", f"five book countries, 1995 = 100, vs fig20-13.csv, largest gap {gap:.3f}")


def big_mac():
    raw = pd.read_csv(os.path.join(MACRO102, CH20, "raw", "big-mac-raw-index.csv"))
    out = pd.DataFrame({
        "release": raw.date,
        "iso3": raw.iso_a3,
        "country": raw.name,
        "currency": raw.currency_code,
        "local_price": raw.local_price.round(2),
        "ex_rate": raw.dollar_ex.round(4),
        "dollar_price": (raw.local_price / raw.dollar_ex).round(2),
    })
    pwt_sub = pd.read_csv(os.path.join(MACRO102, PWT))
    pwt_sub = pwt_sub[pwt_sub.year == 2023].dropna(subset=["rgdpo", "pop"])
    gdp = pd.DataFrame({"iso3": pwt_sub.countrycode, "gdp_pc_2023": (pwt_sub.rgdpo / pwt_sub["pop"]).round(0)})
    out = out.merge(gdp, on="iso3", how="left")
    out["gdp_pc_2023"] = out.gdp_pc_2023.astype("Int64")
    out = out.sort_values(["release", "iso3"])
    out.to_csv(os.path.join(HERE, "big_mac.csv"), index=False)

    # Validation against the textbook table as collected by macro102 (table20-1/data.csv)
    table = pd.read_csv(os.path.join(MACRO102, CH20, "data.csv"))
    july = out[out.release == "2022-07-01"].set_index("country")
    worst = 0.0
    for _, row in table.iterrows():
        ours = july.loc[row["item"]]
        worst = max(worst, abs(ours.local_price - row.price_local_book_2022),
                    abs(ours.dollar_price - row.price_usd_book_2022))
    print(f"big_mac.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.release.nunique()} releases "
          f"({out.release.min()} to {out.release.max()}); {out.gdp_pc_2023.notna().sum()} rows with GDP")
    print(f"largest difference from table20-1/data.csv (July 2022): {worst:.3f}")


def main():
    global RAW, MACRO102, REFRESH
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    ap.add_argument("--refresh", action="store_true", help="download again instead of using the cache")
    args = ap.parse_args()
    MACRO102, REFRESH = os.path.abspath(args.macro102), args.refresh
    RAW = os.path.join(MACRO102, ".work", "ch20", "notebook-raw")
    os.makedirs(RAW, exist_ok=True)
    big_mac()
    meta = countries()
    meta.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(meta)} economies, {meta.oecd.sum()} OECD, {meta.euro_since.notna().sum()} euro area")
    fx_monthly(meta)
    inflation(meta)
    pwt_files(meta)
    fx_history(meta)
    fx_crises(meta)
    yields(meta)
    credit(meta)
    current_account(meta)
    debt(meta)
    ulc(meta)


if __name__ == "__main__":
    main()
