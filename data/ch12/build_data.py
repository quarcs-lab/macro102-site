"""Build the wider data files used by the Chapter 12 notebook.

usage: python build_data.py [--macro102 PATH] [--refresh]
       PATH defaults to the sibling ../macro102 checkout; --refresh downloads the public sources again.

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/):
  fig12-2/raw/fred_USREC.csv                     NBER recession indicator, monthly (1 = recession month)
  fig12-6/raw/treasury_par_yield_curve_YYYY.csv  U.S. Treasury daily par yield curve rates, 2022, 2023, 2026
Public downloads for the multi-country files (conventions 6b), cached in macro102/.work/ch12/notebook-raw/:
  World Bank WDI country list and FP.CPI.TOTL.ZG; BIS WS_CBPOL and WS_LONG_CPI; OECD DF_FINMARK, DF_QNA,
  DF_PRICES_ALL and DF_HHDASH_INDIC; Eurostat prc_hicp_minr; IMF DataMapper G_X_G01_GDP_PT (Fiscal Monitor).
Outputs (next to this script):
  recessions.csv             peak, trough        NBER recessions that start in 1953 or later (monthly dates)
  yield_curves_monthly.csv   date, maturity, months, yield
                             the yield curve on the first trading day of every month of 2022, 2023 and 2026
  countries.csv              iso3, country, region, oecd             names and groups used by the files below
  policy_rates_monthly.csv   iso3, country, date, policy_rate        central bank policy rates (Figure 2)
  interest_rates_monthly.csv iso3, country, date, rate_3m, rate_10y  short and long interest rates (Figure 6)
  inflation_annual.csv       iso3, country, year, inflation          CPI inflation, all countries (Figure 9)
  gdp_quarterly.csv          iso3, country, date, gdp_index          real GDP volume index (Figure 14)
  cpi_monthly.csv            iso3, country, date, inflation_all, inflation_core   12-month CPI inflation (Figure 15)
  government_spending.csv    iso3, country, year, spending_gdp       general government expenditure (Figure 16)
  household_quarterly.csv    iso3, country, date, income_pc, consumption_pc       real, per person (Figure 17)
Checks: the 2022-01-03 and 2023-04-03 curves equal the rows of fig12-6.csv; the U.S. rows of every multi-country
file are compared with the textbook-figure CSVs (and copied from them where the README says so).
"""
import argparse
import io
import json
import os
import time

import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/"
MATURITIES = {"1 Mo": ("1 mo", 1), "3 Mo": ("3 mo", 3), "6 Mo": ("6 mo", 6), "1 Yr": ("1 yr", 12),
              "2 Yr": ("2 yr", 24), "3 Yr": ("3 yr", 36), "5 Yr": ("5 yr", 60), "7 Yr": ("7 yr", 84),
              "10 Yr": ("10 yr", 120), "20 Yr": ("20 yr", 240), "30 Yr": ("30 yr", 360)}
YEARS = [2022, 2023, 2026]


def recessions(root):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig12-2/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1953-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def yield_curves(root):
    """The yield curve on the first trading day of each month, long format."""
    frames = []
    for year in YEARS:
        raw = pd.read_csv(os.path.join(root, f"fig12-6/raw/treasury_par_yield_curve_{year}.csv"))
        raw["date"] = pd.to_datetime(raw["Date"], format="%m/%d/%Y")
        raw = raw.dropna(subset=list(MATURITIES)).sort_values("date")
        first = raw.groupby(raw.date.dt.to_period("M")).head(1)
        frames.append(first[["date"] + list(MATURITIES)])
    wide = pd.concat(frames)
    long = wide.melt(id_vars="date", var_name="column", value_name="yield")
    long["maturity"] = long.column.map({k: v[0] for k, v in MATURITIES.items()})
    long["months"] = long.column.map({k: v[1] for k, v in MATURITIES.items()})
    long = long.sort_values(["date", "months"])[["date", "maturity", "months", "yield"]]
    long["date"] = long.date.dt.strftime("%Y-%m-%d")
    long.to_csv(os.path.join(HERE, "yield_curves_monthly.csv"), index=False)
    print(f"yield_curves_monthly.csv: {long.date.nunique()} curves, {long.date.min()} to {long.date.max()}, "
          f"{len(long)} rows, {int(long['yield'].isna().sum())} missing")
    return long


def validate(long):
    """The two textbook curves must equal the rows of fig12-6.csv."""
    book = pd.read_csv(os.path.join(HERE, "fig12-6.csv"))
    for day in ["2022-01-03", "2023-04-03"]:
        ours = long[long.date == day].set_index("months")["yield"]
        if ours.empty:
            raise SystemExit(f"{day} is not the first trading day of its month in the raw file")
        theirs = book[book.date == day].iloc[0]
        for months, value in ours.items():
            if abs(theirs[f"yield_{months}m"] - value) > 1e-9:
                raise SystemExit(f"{day}, {months} months: {value} != fig12-6.csv {theirs[f'yield_{months}m']}")
    print("validation: the 2022-01-03 and 2023-04-03 curves equal fig12-6.csv (all 11 maturities)")



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


def tidy(frame, table, time, values, digits, keep_empty=()):
    """Add readable names, keep known economies, sort, round and drop rows with no value (except for keep_empty)."""
    names = dict(zip(table.iso3, table.country))
    frame = frame[frame.iso3.isin(names) & (frame[values].notna().any(axis=1) | frame.iso3.isin(keep_empty))].copy()
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


def policy_rates(table):
    """policy_rates_monthly.csv: BIS central bank policy rates (end of month); the U.S. row is FEDFUNDS."""
    d = bis_csv("WS_CBPOL", "M.*", "bis_ws_cbpol_monthly.csv")
    d["iso3"] = to_iso3(d.REF_AREA, table)
    d["date"] = d.TIME_PERIOD + "-01"
    d = d[d.date >= "1960-01-01"].rename(columns={"OBS_VALUE": "policy_rate"})
    book = pd.read_csv(os.path.join(HERE, "fig12-2.csv"))
    bis_us = d[d.iso3 == "USA"].set_index("date").policy_rate
    both = pd.concat([bis_us, book.set_index("date").fedfunds], axis=1, join="inner")
    late = both[both.index >= "1990-01-01"]
    print(f"  validation: BIS U.S. (end of month) vs fig12-2 FEDFUNDS (monthly mean): mean |diff| "
          f"{(both.iloc[:, 0] - both.iloc[:, 1]).abs().mean():.2f} points (1960-), "
          f"{(late.iloc[:, 0] - late.iloc[:, 1]).abs().mean():.2f} (1990-); U.S. rows replaced by fig12-2")
    us = pd.DataFrame({"iso3": "USA", "date": book.date, "policy_rate": book.fedfunds})
    d = pd.concat([d[d.iso3 != "USA"][["iso3", "date", "policy_rate"]], us])
    out = tidy(d, table, "date", ["policy_rate"], 3)
    write(out, "policy_rates_monthly.csv", "date")
    return out


def interest_rates(table):
    """interest_rates_monthly.csv: OECD 3-month interbank and 10-year government bond rates, monthly."""
    d = oecd_csv("OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/.M.IR3TIB+IRLT.PA.....", "oecd_finmark_monthly.csv",
                 "1960-01")
    d = d[d.TIME_PERIOD >= "2000-01"]                     # 2000 on keeps the file under 1 MB
    d["iso3"] = to_iso3(d.REF_AREA, table)
    d = d.pivot_table(index=["iso3", "TIME_PERIOD"], columns="MEASURE", values="OBS_VALUE").reset_index()
    d = d.rename(columns={"IR3TIB": "rate_3m", "IRLT": "rate_10y"})
    d["date"] = d.TIME_PERIOD + "-01"
    out = tidy(d, table, "date", ["rate_3m", "rate_10y"], 3)
    write(out, "interest_rates_monthly.csv", "date")
    curves = pd.read_csv(os.path.join(HERE, "yield_curves_monthly.csv"))
    first = curves[curves.months.isin([3, 120])].pivot(index="date", columns="months", values="yield")
    first.index = first.index.str[:8] + "01"
    us = out[out.iso3 == "USA"].set_index("date").join(first, how="inner")
    print(f"  validation: OECD U.S. vs Treasury first-trading-day yields, {len(us)} months: mean |diff| "
          f"3-month {(us.rate_3m - us[3]).abs().mean():.2f}, 10-year {(us.rate_10y - us[120]).abs().mean():.2f} "
          "points (monthly averages vs one day)")


def inflation_annual(table):
    """inflation_annual.csv: WDI FP.CPI.TOTL.ZG, all economies, 1960-2025; the U.S. rows are fig12-9."""
    rows = wdi_json("https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json"
                    "&per_page=20000&date=1960:2025", "wdi_FP.CPI.TOTL.ZG.json")
    d = pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows], "year": [int(r["date"]) for r in rows],
                      "inflation": [r["value"] for r in rows]}).dropna()
    book = pd.read_csv(os.path.join(HERE, "fig12-9.csv"))
    wdi_us = d[d.iso3 == "USA"].set_index("year").inflation
    diff = (wdi_us - book.set_index("year").inflation_cpi).abs()
    print(f"  validation: WDI U.S. vs fig12-9: max |diff| {diff.max():.3f} points over {diff.notna().sum()} years; "
          "U.S. rows replaced by fig12-9 (which also has 2025)")
    us = pd.DataFrame({"iso3": "USA", "year": book.year, "inflation": book.inflation_cpi})
    d = pd.concat([d[d.iso3 != "USA"], us])
    out = tidy(d, table, "year", ["inflation"], 3)
    write(out, "inflation_annual.csv", "year")


def gdp_quarterly(table):
    """gdp_quarterly.csv: OECD quarterly real GDP, chain-linked volume index (2020 = 100), seasonally adjusted."""
    d = oecd_csv("OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1/Q.Y..S1.S1.B1GQ._Z._Z._Z.IX.LR.N.T0102",
                 "oecd_qna_gdp_volume_index.csv", "2015-Q1")
    d["iso3"] = to_iso3(d.REF_AREA, table)
    d["date"] = pd.PeriodIndex(d.TIME_PERIOD.str.replace("-", ""), freq="Q").start_time.strftime("%Y-%m-%d")
    d = d.rename(columns={"OBS_VALUE": "gdp_index"})
    out = tidy(d, table, "date", ["gdp_index"], 3)
    write(out, "gdp_quarterly.csv", "date")
    book = pd.read_csv(os.path.join(HERE, "fig12-14.csv")).set_index("date").real_gdp
    us = out[out.iso3 == "USA"].set_index("date").gdp_index
    a, b = us / us["2019-10-01"], book / book["2019-10-01"]
    print(f"  validation: OECD U.S. index vs fig12-14 GDPC1, both 2019Q4 = 1: max |diff| "
          f"{100 * (a - b).abs().max():.2f} percent")


def cpi_monthly(table):
    """cpi_monthly.csv: 12-month CPI inflation, all items (BIS) and core (OECD; Eurostat for the euro area)."""
    head = bis_csv("WS_LONG_CPI", "M.*.771", "bis_ws_long_cpi_yoy_monthly.csv", "2020-01")
    head["iso3"] = to_iso3(head.REF_AREA, table)
    head = head.rename(columns={"OBS_VALUE": "inflation_all"})[["iso3", "TIME_PERIOD", "inflation_all"]]
    core = oecd_csv("OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/.M.N.CPI.PA._T+_TXCP01_NRG.N.GY",
                    "oecd_prices_monthly_cpi_gy.csv", "2020-01")
    core = core[core.EXPENDITURE == "_TXCP01_NRG"]          # core: all items less food and energy
    core["iso3"] = to_iso3(core.REF_AREA, table)
    core = core[core.iso3 != "EMU"].rename(columns={"OBS_VALUE": "inflation_core"})
    es = fetch("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_minr?unit=RCH_A"
               "&coicop18=TOT_X_NRG_FOOD&geo=EA&sinceTimePeriod=2020-01&lang=EN", "eurostat_hicp_core_ea.json")
    with open(es) as f:
        j = json.load(f)
    months = sorted(j["dimension"]["time"]["category"]["index"], key=j["dimension"]["time"]["category"]["index"].get)
    ea = pd.DataFrame({"iso3": "EMU", "TIME_PERIOD": months})
    ea["inflation_core"] = [j["value"].get(str(i)) for i in range(len(months))]
    core = pd.concat([core[["iso3", "TIME_PERIOD", "inflation_core"]], ea])
    d = head.merge(core, on=["iso3", "TIME_PERIOD"], how="outer")
    d["date"] = d.TIME_PERIOD + "-01"
    book = pd.read_csv(os.path.join(HERE, "fig12-15.csv"))
    us = d[d.iso3 == "USA"].set_index("date").join(book.set_index("date"), rsuffix="_book")
    print(f"  validation: BIS/OECD U.S. (not seasonally adjusted) vs fig12-15 (seasonally adjusted): mean |diff| "
          f"all items {(us.inflation_all - us.inflation_all_book).abs().mean():.2f}, core "
          f"{(us.inflation_core - us.inflation_core_book).abs().mean():.2f} points; U.S. rows replaced by fig12-15")
    book["iso3"] = "USA"
    d = pd.concat([d[d.iso3 != "USA"], book])
    out = tidy(d, table, "date", ["inflation_all", "inflation_core"], 3, keep_empty=["USA"])   # keep the 2025-10 gap
    write(out, "cpi_monthly.csv", "date")


def government_spending(table):
    """government_spending.csv: IMF Fiscal Monitor general government total expenditure, % of GDP, 2000-2025."""
    with open(fetch("https://www.imf.org/external/datamapper/api/v1/G_X_G01_GDP_PT", "imf_G_X_G01_GDP_PT.json")) as f:
        values = json.load(f)["values"]["G_X_G01_GDP_PT"]
    rows = []
    for code, series in values.items():
        for year, v in series.items():
            if 2000 <= int(year) <= 2025:
                rows.append({"iso3": {"UVK": "XKX", "EURO": "EMU"}.get(code, code), "year": int(year), "spending_gdp": v})
    out = tidy(pd.DataFrame(rows), table, "year", ["spending_gdp"], 2)
    write(out, "government_spending.csv", "year")
    book = pd.read_csv(os.path.join(HERE, "fig12-16.csv"))
    book["year"] = book.date.str[:4].astype(int)
    us = out[out.iso3 == "USA"].set_index("year").spending_gdp
    fed = book.set_index("year").outlays_gdp_pct
    print(f"  validation: U.S. general government (IMF) minus federal outlays (fig12-16): "
          f"{(us - fed).loc[2007:2025].min():.1f} to {(us - fed).loc[2007:2025].max():.1f} points; "
          f"rise 2019 -> 2020: {us[2020] - us[2019]:.1f} (IMF) vs {fed[2020] - fed[2019]:.1f} (federal)")


def household_quarterly(table):
    """household_quarterly.csv: OECD real household disposable income and consumption per person (2007Q1 = 100)."""
    d = oecd_csv("OECD.SDD.NAD,DSD_HHDASH@DF_HHDASH_INDIC,1.1/Q..B6GS1M_R_POP+P3S1M_R_POP.IX",
                 "oecd_hhdash_income_consumption.csv", "2017-Q1")
    d["iso3"] = to_iso3(d.REF_AREA, table)
    d = d.pivot_table(index=["iso3", "TIME_PERIOD"], columns="MEASURE", values="OBS_VALUE").reset_index()
    d = d.rename(columns={"B6GS1M_R_POP": "income_pc", "P3S1M_R_POP": "consumption_pc"})
    d["date"] = pd.PeriodIndex(d.TIME_PERIOD.str.replace("-", ""), freq="Q").start_time.strftime("%Y-%m-%d")
    out = tidy(d, table, "date", ["income_pc", "consumption_pc"], 2)
    write(out, "household_quarterly.csv", "date")
    book = pd.read_csv(os.path.join(HERE, "fig12-17.csv"), parse_dates=["date"]).set_index("date")
    q = book.resample("QS").mean()
    us = out[out.iso3 == "USA"].set_index(pd.to_datetime(out[out.iso3 == "USA"].date))
    for col, mine in [("real_disp_income", "income_pc"), ("real_consumption", "consumption_pc")]:
        g_book = 100 * (q[col]["2021-01-01"] / q[col]["2019-10-01"] - 1)
        g_ours = 100 * (us[mine]["2021-01-01"] / us[mine]["2019-10-01"] - 1)
        print(f"  validation: {col} 2019Q4 -> 2021Q1: {g_book:+.1f}% (fig12-17, total) vs {g_ours:+.1f}% "
              "(OECD, per person)")


def main():
    global CACHE, REFRESH
    parser = argparse.ArgumentParser()
    parser.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    parser.add_argument("--refresh", action="store_true", help="download the public sources again")
    args = parser.parse_args()
    macro102 = os.path.abspath(args.macro102)
    root = os.path.join(macro102, DATA)
    CACHE, REFRESH = os.path.join(macro102, ".work", "ch12", "notebook-raw"), args.refresh
    os.makedirs(CACHE, exist_ok=True)
    recessions(root)
    validate(yield_curves(root))
    table = country_table()
    policy_rates(table)
    interest_rates(table)
    inflation_annual(table)
    gdp_quarterly(table)
    cpi_monthly(table)
    government_spending(table)
    household_quarterly(table)


if __name__ == "__main__":
    main()
