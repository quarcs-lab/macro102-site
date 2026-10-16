"""Build the wider data files used by the Chapter 13 notebook widgets.

usage: python build_data.py [--macro102 PATH] [--refresh]
       PATH defaults to the sibling ../macro102 checkout; --refresh downloads the public sources again.

Inputs: the raw downloads saved by the macro102 /collect-data skill in
        original-scanned-book/ch13-stabilization-policy-and-the-as-ad-framework/data/
          fig13-16/raw/fred_FEDFUNDS.csv, fred_JCXFE.csv
          fig13-17/raw/fred_GDPC1.csv, fred_GDPPOT.csv, fred_CPIAUCSL.csv,
                       alfred_GDPC1_2023-03-30.csv, alfred_GDPPOT_2023-03-30.csv
Outputs (next to this script):
  taylor_rule.csv      one row per quarter, 1960Q1 to the latest quarter
      date             first day of the quarter
      fed_funds        effective federal funds rate, quarterly mean of monthly values (complete quarters), percent
      core_inflation   core PCE inflation, 4-quarter percent change of the JCXFE price index
  loops_vintages.csv   one row per year, 1960 to the latest complete year
      year
      inflation        CPI inflation, percent change of the annual-average CPIAUCSL
      output_gap       100 (Y / Ybar - 1), annual means of GDPC1 and GDPPOT, current FRED vintage
      output_gap_2023  the same with the ALFRED vintage of 2023-03-30 (the data the textbook used), to 2022
Both are validated against the copied fig13-16.csv and fig13-17.csv.

Multi-country files (conventions 6b), from public downloads cached in macro102/.work/ch13/notebook-raw/
(World Bank WDI, BIS WS_CBPOL, OECD DF_PRICES_ALL and DF_EO, the Jorda-Schularick-Taylor Macrohistory
Database R6) and from the fig13-21 raw files of collect-data (Bank of England millennium dataset, ONS D7BT):
  countries.csv               iso3, country, region, oecd                    names and groups
  taylor_rule_countries.csv   iso3, country, date, policy_rate, core_inflation    quarterly (Figure 16)
  inflation_annual.csv        iso3, country, year, inflation                 CPI inflation (Figures 17 and 19)
  output_gaps_oecd.csv        iso3, country, year, output_gap                OECD Economic Outlook (Figure 17)
  inflation_long_annual.csv   iso3, country, year, inflation                 since 1737 (U.K.) / 1871 (Figure 21)
The U.S. (and textbook-economy) rows are copied from or checked against the textbook-figure CSVs.
"""
import argparse
import json
import os
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
CH = "original-scanned-book/ch13-stabilization-policy-and-the-as-ad-framework/data"


def read(root, item, name):
    """One raw FRED/ALFRED csv as a Series indexed by date."""
    d = pd.read_csv(os.path.join(root, CH, item, "raw", name), na_values=["."])
    return d.set_index(pd.to_datetime(d.iloc[:, 0])).iloc[:, 1].astype(float)


def gap(gdp, pot):
    """Annual output gap 100 (Y / Ybar - 1) from quarterly levels, complete years only."""
    q = pd.concat([gdp, pot], axis=1).dropna()
    n = q.iloc[:, 0].resample("YS").count()
    a = q.resample("YS").mean()[n == 4]
    out = 100 * (a.iloc[:, 0] / a.iloc[:, 1] - 1)
    out.index = out.index.year
    return out


# ---------------------------------------------------------------------------------------------------------
# Multi-country files (conventions 6b). Every download is cached; requests' default User-Agent is used
# (FRED and the IMF block custom ones).
# ---------------------------------------------------------------------------------------------------------
OECD = ["AUS", "AUT", "BEL", "CAN", "CHL", "COL", "CRI", "CZE", "DNK", "EST", "FIN", "FRA", "DEU", "GRC", "HUN",
        "ISL", "IRL", "ISR", "ITA", "JPN", "KOR", "LVA", "LTU", "LUX", "MEX", "NLD", "NZL", "NOR", "POL", "PRT",
        "SVK", "SVN", "ESP", "SWE", "CHE", "TUR", "GBR", "USA"]
RENAME = {"Bahamas, The": "Bahamas", "Congo, Dem. Rep.": "DR Congo", "Congo, Rep.": "Congo",
          "Egypt, Arab Rep.": "Egypt", "Gambia, The": "Gambia", "Hong Kong SAR, China": "Hong Kong",
          "Iran, Islamic Rep.": "Iran", "Korea, Dem. People's Rep.": "North Korea", "Korea, Rep.": "Korea",
          "Macao SAR, China": "Macao", "Micronesia, Fed. Sts.": "Micronesia", "Puerto Rico (US)": "Puerto Rico",
          "Sint Maarten (Dutch part)": "Sint Maarten", "Somalia, Fed. Rep.": "Somalia",
          "St. Martin (French part)": "St. Martin", "Venezuela, RB": "Venezuela", "Virgin Islands (U.S.)":
          "U.S. Virgin Islands", "Yemen, Rep.": "Yemen", "Russian Federation": "Russia", "Turkiye": "Türkiye",
          "Slovak Republic": "Slovakia", "Kyrgyz Republic": "Kyrgyzstan", "Lao PDR": "Laos",
          "Syrian Arab Republic": "Syria", "Viet Nam": "Vietnam", "Brunei Darussalam": "Brunei", "Naoero": "Nauru"}
REGIONS = {"Europe & Central Asia": "Europe and Central Asia", "North America": "Americas",
           "Latin America & Caribbean": "Americas", "East Asia & Pacific": "Asia and Pacific",
           "South Asia": "Asia and Pacific", "Sub-Saharan Africa": "Middle East and Africa",
           "Middle East, North Africa, Afghanistan & Pakistan": "Middle East and Africa"}
EURO = {"EA", "EA20", "EA19", "EA17", "EMU", "XM"}          # euro-area codes in OECD, WDI and BIS files
OECD_URL = "https://sdmx.oecd.org/public/rest/data/"
CACHE = None                                               # set in main()
REFRESH = False


def fetch(url, name):
    """Download url once into the cache folder and return the local path."""
    path = os.path.join(CACHE, name)
    if REFRESH or not os.path.exists(path):
        for attempt in range(6):                           # the OECD API answers 429 when queried too often
            r = requests.get(url, timeout=600)
            if r.status_code != 429:
                break
            print(f"  {name}: HTTP 429, waiting 60 s")
            time.sleep(60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"  downloaded {name} ({len(r.content) / 1e6:.1f} MB)")
    return path


def wdi_json(url, name):
    """Rows of a World Bank API response (the second element of the JSON list)."""
    with open(fetch(url, name)) as f:
        return json.load(f)[1]


def country_table():
    """countries.csv: one row per WDI economy (aggregates dropped) plus the euro area."""
    rows = wdi_json("https://api.worldbank.org/v2/country?format=json&per_page=400", "wdi_countries.json")
    out = []
    for r in rows:
        region = r["region"]["value"].strip()
        if region == "Aggregates" and r["id"] != "EMU":
            continue
        out.append({"iso3": r["id"], "iso2": r["iso2Code"], "country": RENAME.get(r["name"], r["name"]),
                    "region": REGIONS.get(region, "Europe and Central Asia"), "oecd": r["id"] in OECD})
    table = pd.DataFrame(out).sort_values("country").reset_index(drop=True)
    table[["iso3", "country", "region", "oecd"]].to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(table)} economies, {table.oecd.sum()} OECD members")
    return table


def to_iso3(codes, table):
    """Map ISO2 (BIS) or ISO3/aggregate (OECD) codes to ISO3; the euro area becomes EMU."""
    iso2 = dict(zip(table.iso2, table.iso3))
    out = []
    for c in codes:
        out.append("EMU" if c in EURO else iso2.get(c, c if len(c) == 3 else None))
    return out


def tidy(frame, table, time, values, digits):
    """Add readable names, keep known economies, sort, round and drop rows with no value."""
    names = dict(zip(table.iso3, table.country))
    frame = frame[frame.iso3.isin(names)].dropna(subset=values, how="all").copy()
    frame.insert(1, "country", frame.iso3.map(names))
    frame[values] = frame[values].round(digits)
    return frame[["iso3", "country", time] + values].sort_values(["country", time]).reset_index(drop=True)


def write(frame, name, time):
    """Write a tidy file and report its size and span."""
    path = os.path.join(HERE, name)
    frame.to_csv(path, index=False)
    size = os.path.getsize(path) / 1e6
    print(f"{name}: {len(frame)} rows, {frame.iso3.nunique()} economies, {frame[time].min()} to "
          f"{frame[time].max()}, {size:.2f} MB")
    if size >= 1:
        raise SystemExit(f"{name} is {size:.2f} MB (must stay under 1 MB)")


def oecd_csv(key, name, start):
    """An OECD SDMX query as a DataFrame with REF_AREA, TIME_PERIOD, OBS_VALUE and the key columns."""
    url = f"{OECD_URL}{key}?dimensionAtObservation=AllDimensions&format=csvfilewithlabels"
    if start:
        url += f"&startPeriod={start}"
    return pd.read_csv(fetch(url, name)).dropna(subset=["OBS_VALUE"])


def bis_csv(flow, key, name, start=None):
    """A BIS SDMX (v2) query as a DataFrame."""
    url = f"https://stats.bis.org/api/v2/data/dataflow/BIS/{flow}/1.0/{key}?format=csv"
    if start:
        url += f"&startPeriod={start}"
    d = pd.read_csv(fetch(url, name), usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
    return d.dropna(subset=["OBS_VALUE"])



def us_taylor_rows():
    """The U.S. rows of the Taylor-rule panel: taylor_rule.csv (fed funds and core PCE inflation)."""
    us = pd.read_csv(os.path.join(HERE, "taylor_rule.csv"))
    return pd.DataFrame({"iso3": "USA", "date": us.date, "policy_rate": us.fed_funds,
                         "core_inflation": us.core_inflation})


def taylor_countries(table):
    """taylor_rule_countries.csv: BIS policy rate (quarterly mean of end-of-month rates, complete quarters)
    and OECD core CPI inflation (all items less food and energy, % change over 4 quarters)."""
    pol = bis_csv("WS_CBPOL", "M.*", "bis_ws_cbpol_monthly.csv")
    pol["iso3"] = to_iso3(pol.REF_AREA, table)
    pol["month"] = pd.to_datetime(pol.TIME_PERIOD + "-01")
    pol = pol[pol.month >= "1960-01-01"].set_index("month")
    n = pol.groupby("iso3").OBS_VALUE.resample("QS").count()
    q = pol.groupby("iso3").OBS_VALUE.resample("QS").mean()[n == 3].rename("policy_rate").reset_index()
    q["date"] = q.month.dt.strftime("%Y-%m-%d")
    core = oecd_csv("OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/.Q.N.CPI.PA._TXCP01_NRG.N.GY",
                    "oecd_prices_quarterly_core_gy.csv", "1960-Q1")
    core["iso3"] = to_iso3(core.REF_AREA, table)
    core["date"] = pd.PeriodIndex(core.TIME_PERIOD.str.replace("-", ""), freq="Q").start_time.strftime("%Y-%m-%d")
    core = core.rename(columns={"OBS_VALUE": "core_inflation"})[["iso3", "date", "core_inflation"]]
    d = q[["iso3", "date", "policy_rate"]].merge(core, on=["iso3", "date"], how="outer")
    both = d.dropna().groupby("iso3").size()
    d = d[d.iso3.isin(both[both >= 20].index)]            # countries with both series for 5 years or more
    bis_us = d[d.iso3 == "USA"].set_index("date")
    us = us_taylor_rows().set_index("date")
    j = bis_us.join(us, rsuffix="_us", how="inner").dropna()
    print(f"  validation: BIS/OECD U.S. vs taylor_rule.csv, {len(j)} quarters: mean |diff| policy rate "
          f"{(j.policy_rate - j.policy_rate_us).abs().mean():.2f}, core CPI vs core PCE inflation "
          f"{(j.core_inflation - j.core_inflation_us).abs().mean():.2f} points; U.S. rows replaced by taylor_rule.csv")
    d = pd.concat([d[d.iso3 != "USA"], us_taylor_rows()])
    out = tidy(d, table, "date", ["policy_rate", "core_inflation"], 3)
    write(out, "taylor_rule_countries.csv", "date")


def wdi_inflation():
    """WDI FP.CPI.TOTL.ZG (annual % change of consumer prices), all economies, 1960-2025."""
    rows = wdi_json("https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json"
                    "&per_page=20000&date=1960:2025", "wdi_FP.CPI.TOTL.ZG.json")
    return pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows], "year": [int(r["date"]) for r in rows],
                         "inflation": [r["value"] for r in rows]}).dropna()


def inflation_annual(table):
    """inflation_annual.csv: WDI for every economy; the four textbook economies are copied from fig13-19.csv."""
    d = wdi_inflation()
    book = pd.read_csv(os.path.join(HERE, "fig13-19.csv")).set_index("year")
    columns = {"USA": "inflation_us", "GBR": "inflation_uk", "EMU": "inflation_euro_area", "JPN": "inflation_japan"}
    frames = [d[~d.iso3.isin(columns)]]
    for iso3, col in columns.items():
        wdi = d[d.iso3 == iso3].set_index("year").inflation
        print(f"  validation: WDI {iso3} vs fig13-19 {col}: max |diff| {(wdi - book[col]).abs().max():.2f} points")
        frames.append(pd.DataFrame({"iso3": iso3, "year": book.index, "inflation": book[col].values}))
    out = tidy(pd.concat(frames), table, "year", ["inflation"], 3)
    write(out, "inflation_annual.csv", "year")


def output_gaps(table):
    """output_gaps_oecd.csv: OECD Economic Outlook output gap (% of potential GDP), 1985-2025 (no projections)."""
    d = oecd_csv("OECD.ECO.MAD,DSD_EO@DF_EO,1.5/.GAP.A", "oecd_eo_gap_annual.csv", None)
    d["iso3"] = to_iso3(d.REF_AREA, table)
    d = d[d.TIME_PERIOD <= 2025].rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "output_gap"})
    out = tidy(d, table, "year", ["output_gap"], 3)
    write(out, "output_gaps_oecd.csv", "year")
    cbo = pd.read_csv(os.path.join(HERE, "loops_vintages.csv")).set_index("year").output_gap
    us = out[out.iso3 == "USA"].set_index("year").output_gap
    print(f"  validation: OECD vs CBO U.S. output gap 1985-2025: correlation {us.corr(cbo):.2f}, mean OECD minus "
          f"CBO {(us - cbo).mean():+.2f} points, 2009: {us[2009]:.2f} vs {cbo[2009]:.2f}")


def long_inflation(root, table):
    """inflation_long_annual.csv: the U.K. series of fig13-21 (BoE to 2016, ONS after), and JST R6 CPI
    inflation 1871-2020 extended with WDI 2021-2025 for the other 17 JST countries."""
    boe = pd.read_csv(os.path.join(root, CH, "fig13-21/raw/boe_millennium_A1_cpi.csv")).set_index("year")
    ons = pd.read_csv(os.path.join(root, CH, "fig13-21/raw/ons_d7bt_cpi_index.csv"), header=None,
                      names=["period", "value"], skiprows=8)
    mon = ons[ons.period.str.match(r"^\d{4} [A-Z]{3}$")].copy()
    mon["year"] = mon.period.str[:4].astype(int)
    g = mon.groupby("year").value.agg(["mean", "count"])
    ons_a = g[g["count"] == 12]["mean"]
    uk = boe.cpi_inflation_pct.dropna()
    later = (100 * (ons_a / ons_a.shift(1) - 1)).dropna()
    uk = pd.concat([uk, later[later.index > uk.index.max()]])
    uk = uk[uk.index >= 1737]
    jst = pd.read_stata(fetch("https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.dta",
                              "JSTdatasetR6.dta"))
    jst = jst[["iso", "year", "cpi"]].sort_values(["iso", "year"])
    jst["inflation"] = 100 * (jst.cpi / jst.groupby("iso").cpi.shift(1) - 1)
    jst = jst.dropna(subset=["inflation"]).rename(columns={"iso": "iso3"})
    jst["year"] = jst.year.astype(int)
    wdi = wdi_inflation()
    both = jst.merge(wdi, on=["iso3", "year"], suffixes=("_jst", "_wdi"))
    both = both[both.year >= 1990]
    print(f"  validation: JST vs WDI annual inflation 1990-2020, {len(both)} country-years: mean |diff| "
          f"{(both.inflation_jst - both.inflation_wdi).abs().mean():.2f}, max {(both.inflation_jst - both.inflation_wdi).abs().max():.2f}")
    jst_uk = jst[jst.iso3 == "GBR"].set_index("year").inflation
    print(f"  validation: JST vs BoE U.K. inflation 1871-2016: mean |diff| {(jst_uk - uk).loc[1871:2016].abs().mean():.2f}")
    later = wdi[wdi.iso3.isin(jst.iso3.unique()) & (wdi.year > 2020)]
    us_2025 = pd.read_csv(os.path.join(HERE, "fig13-19.csv")).set_index("year").inflation_us[2025]
    extra = pd.DataFrame({"iso3": ["USA"], "year": [2025], "inflation": [us_2025]})   # WDI has no U.S. 2025 yet
    others = pd.concat([jst[jst.iso3 != "GBR"][["iso3", "year", "inflation"]], later[later.iso3 != "GBR"], extra])
    d = pd.concat([pd.DataFrame({"iso3": "GBR", "year": uk.index, "inflation": uk.values}), others])
    out = tidy(d, table, "year", ["inflation"], 3)
    write(out, "inflation_long_annual.csv", "year")
    book = pd.read_csv(os.path.join(HERE, "fig13-21.csv"))
    ukw = out[out.iso3 == "GBR"].copy()
    ukw["start"] = 1737 + (ukw.year - 1737) // 20 * 20
    w = ukw.groupby("start").inflation.agg(["mean", "std"])
    diff = max((w["mean"] - book.set_index("year").avg_inflation).abs().max(),
               (w["std"] - book.set_index("year").sd_inflation).abs().max())
    print(f"  validation: U.K. 20-year windows recomputed from this file vs fig13-21.csv: max |diff| {diff:.4f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    ap.add_argument("--refresh", action="store_true", help="download the public sources again")
    args = ap.parse_args()
    root = args.macro102
    global CACHE, REFRESH
    CACHE, REFRESH = os.path.join(os.path.abspath(root), ".work", "ch13", "notebook-raw"), args.refresh
    os.makedirs(CACHE, exist_ok=True)

    # ---- taylor_rule.csv ----------------------------------------------------------------
    ff = read(root, "fig13-16", "fred_FEDFUNDS.csv").dropna()
    n = ff.resample("QS").count()
    ffq = ff.resample("QS").mean()[n == 3]
    core = read(root, "fig13-16", "fred_JCXFE.csv").dropna()
    pi = 100 * (core / core.shift(4) - 1)
    tr = pd.DataFrame({"fed_funds": ffq, "core_inflation": pi})
    tr = tr[tr.index >= "1960-01-01"].dropna(how="all").round(4)
    tr.index.name = "date"
    tr.to_csv(os.path.join(HERE, "taylor_rule.csv"), date_format="%Y-%m-%d")
    old = pd.read_csv(os.path.join(HERE, "fig13-16.csv"), parse_dates=["date"]).set_index("date")
    d_rule = (1 + 1.5 * tr.core_inflation - old.policy_rule).abs().max()
    d_ff = (tr.fed_funds - old.fed_funds).abs().max()
    print(f"taylor_rule.csv: {len(tr)} quarters {tr.index.min():%Y-%m} to {tr.index.max():%Y-%m}; "
          f"max |1 + 1.5 pi - fig13-16 rule| = {d_rule:.4f}, max |fed funds diff| = {d_ff:.4f}")

    # ---- loops_vintages.csv ---------------------------------------------------------------
    cpi = read(root, "fig13-17", "fred_CPIAUCSL.csv")
    cpi = cpi.loc[:cpi.last_valid_index()].interpolate(limit=1, limit_area="inside")   # Oct 2025 never published
    n = cpi.resample("YS").count()
    cpia = cpi.resample("YS").mean()[n == 12]
    infl = 100 * (cpia / cpia.shift(1) - 1)
    infl.index = infl.index.year
    now = gap(read(root, "fig13-17", "fred_GDPC1.csv").dropna(), read(root, "fig13-17", "fred_GDPPOT.csv"))
    book = gap(read(root, "fig13-17", "alfred_GDPC1_2023-03-30.csv").dropna(),
               read(root, "fig13-17", "alfred_GDPPOT_2023-03-30.csv"))
    lv = pd.DataFrame({"inflation": infl, "output_gap": now}).dropna()
    lv["output_gap_2023"] = book
    lv = lv.loc[1960:].round(4)
    lv.index.name = "year"
    lv.to_csv(os.path.join(HERE, "loops_vintages.csv"))
    old = pd.read_csv(os.path.join(HERE, "fig13-17.csv")).set_index("year")
    print(f"loops_vintages.csv: {len(lv)} years {lv.index.min()}-{lv.index.max()}; "
          f"max |diff| vs fig13-17: inflation {(lv.inflation - old.inflation).abs().max():.4f}, "
          f"output gap {(lv.output_gap - old.output_gap).abs().max():.4f}; "
          f"book vintage to {lv.output_gap_2023.last_valid_index()}")

    table = country_table()
    taylor_countries(table)
    inflation_annual(table)
    output_gaps(table)
    long_inflation(root, table)


if __name__ == "__main__":
    main()
