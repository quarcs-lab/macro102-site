"""Build the wider data files used by the Chapter 10 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/):
  fig10-2/raw/fred_USREC.csv       NBER recession indicator, monthly (1 = recession month)
  table10-1/raw/fred_USRECQ.csv    NBER recession indicator, quarterly (1 = recession quarter)
  table10-1/raw/fred_GDPC1.csv, fred_PCECC96.csv, fred_GPDIC1.csv, fred_GCEC1.csv, fred_EXPGSC1.csv,
  fred_IMPGSC1.csv                 real GDP and its components, billions of chained 2017 dollars, quarterly, SAAR
  table10-1/raw/fred_PAYEMS.csv    nonfarm payroll employment, thousands, monthly, SA
  table10-1/raw/fred_UNRATE.csv    unemployment rate, percent, monthly, SA (October 2025 missing)
Outputs (next to this script):
  recessions.csv     peak, trough, peak_quarter, trough_quarter
                     NBER recessions that start in 1953 or later: monthly dates (for the shaded bands)
                     and quarterly dates (for Table 10.1)
  us_quarterly.csv   date, gdp, consumption, investment, government, exports, imports, employment,
                     unemployment          quarterly, 1953Q1 on; employment and unemployment are
                     quarterly averages of the monthly series

Multi-country files (conventions §6b), downloaded from public APIs and cached in
../macro102/.work/ch10/notebook-raw/ (pass --refresh to download again):
  countries.csv              iso3, country, region          one row per economy used below
  house_prices_panel.csv     BIS real residential property prices (Figure 1)
  policy_rates_panel.csv     BIS central bank policy rates (Figure 2)
  interbank_spreads_panel.csv  OECD 3-month interbank minus overnight rate (Figure 3)
  share_prices_panel.csv     OECD share prices deflated by the IMF CPI (Figure 4)
  gdp_quarterly_panel.csv    OECD quarterly real GDP, 2019Q4 = 100 (Figure 6)
  employment_panel.csv       OECD labour force survey employment (Figure 7)
  output_gap_panel.csv       OECD Economic Outlook output gaps (Figure 8)
  unemployment_panel.csv     OECD harmonised unemployment rates (Figure 9)
  inflation_panel.csv        12-month headline and core inflation (Figures 10 and 11)
Each U.S. series is validated against the textbook-figure CSV next to this script.
"""
import argparse
import io
import os

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/"
QUARTERLY = {"gdp": "GDPC1", "consumption": "PCECC96", "investment": "GPDIC1", "government": "GCEC1",
             "exports": "EXPGSC1", "imports": "IMPGSC1"}
TABLE_ROWS = {"gdp": "GDP", "employment": "Nonfarm employment", "unemployment": "Unemployment rate",
              "consumption": "Consumption", "investment": "Investment", "government": "Government purchases",
              "exports": "Exports", "imports": "Imports"}


def fred(root, path):
    """One FRED series as a Series indexed by date (blank cells become NaN)."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def episodes(flag, step):
    """(peak, trough) pairs: the period before the first recession period, and the last recession period."""
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    return pd.DataFrame({"peak": starts - pd.DateOffset(months=step), "trough": ends})


def recessions(root):
    monthly = episodes(fred(root, "fig10-2/raw/fred_USREC.csv"), 1)
    quarterly = episodes(fred(root, "table10-1/raw/fred_USRECQ.csv"), 3)
    monthly = monthly[monthly.peak >= "1953-01-01"].reset_index(drop=True)
    quarterly = quarterly[quarterly.peak >= "1953-01-01"].reset_index(drop=True)
    if len(monthly) != len(quarterly):
        raise SystemExit(f"{len(monthly)} monthly but {len(quarterly)} quarterly recessions")
    gap = (quarterly.peak - monthly.peak).dt.days.abs().max()
    if gap > 200:
        raise SystemExit(f"monthly and quarterly peaks do not pair up (largest gap {gap} days)")
    out = pd.DataFrame({"peak": monthly.peak, "trough": monthly.trough,
                        "peak_quarter": quarterly.peak, "trough_quarter": quarterly.trough})
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")
    return out


def quarterly_data(root):
    cols = {}
    for name, series in QUARTERLY.items():
        cols[name] = fred(root, f"table10-1/raw/fred_{series}.csv")
    emp = fred(root, "table10-1/raw/fred_PAYEMS.csv") / 1000
    unemp = fred(root, "table10-1/raw/fred_UNRATE.csv")
    cols["employment"] = emp.resample("QS").mean()
    cols["unemployment"] = unemp.resample("QS").mean()          # mean of the months available
    out = pd.DataFrame(cols)
    out = out[(out.index >= "1953-01-01") & out.gdp.notna()].round(3)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "us_quarterly.csv"), date_format="%Y-%m-%d")
    print(f"us_quarterly.csv: {len(out)} quarters, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}, "
          f"{int(out.isna().sum().sum())} missing values")
    return out


def validate(root, rec, data):
    """Table 10.1 recomputed from the two new files must equal collect-data's table10-1/data.csv."""
    ref = pd.read_csv(os.path.join(root, "table10-1/data.csv")).set_index("item")
    rows = {}
    for p, t in zip(pd.to_datetime(rec.peak_quarter), pd.to_datetime(rec.trough_quarter)):
        change = {}
        for col, item in TABLE_ROWS.items():
            if col == "unemployment":
                change[item] = data.loc[t, col] - data.loc[p, col]
            else:
                change[item] = 100 * (data.loc[t, col] / data.loc[p, col] - 1)
        rows[p.strftime("%Y-%m")] = change
    table = pd.DataFrame(rows)
    mine = pd.DataFrame({"prev_avg_latest_2026": table.loc[:, :"2001-01"].mean(axis=1),
                         "great_rec_latest_2026": table["2007-10"],
                         "covid_latest_2026": table["2019-10"]})
    worst = (mine - ref[mine.columns]).abs().max().max()
    print(f"validation: Table 10.1 from us_quarterly.csv and recessions.csv; largest difference from "
          f"table10-1/data.csv: {worst:.3f} (data.csv is rounded to 2 decimals)")
    if worst > 0.01:
        raise SystemExit("validation failed")


# ---------------------------------------------------------------------------------------------
# Multi-country panels (conventions §6b)
# ---------------------------------------------------------------------------------------------
# ISO2 code (BIS, Eurostat) -> ISO3 code, readable name (as in fig10-5.csv), region for the website menus
ECONOMIES = {
    "US": ("USA", "United States", "Americas"), "CA": ("CAN", "Canada", "Americas"),
    "MX": ("MEX", "Mexico", "Americas"), "BR": ("BRA", "Brazil", "Americas"),
    "AR": ("ARG", "Argentina", "Americas"), "CL": ("CHL", "Chile", "Americas"),
    "CO": ("COL", "Colombia", "Americas"), "PE": ("PER", "Peru", "Americas"),
    "CR": ("CRI", "Costa Rica", "Americas"),
    "XM": ("EMU", "Euro area", "Europe"), "AT": ("AUT", "Austria", "Europe"), "BE": ("BEL", "Belgium", "Europe"),
    "BG": ("BGR", "Bulgaria", "Europe"), "HR": ("HRV", "Croatia", "Europe"), "CY": ("CYP", "Cyprus", "Europe"),
    "CZ": ("CZE", "Czechia", "Europe"), "DK": ("DNK", "Denmark", "Europe"), "EE": ("EST", "Estonia", "Europe"),
    "FI": ("FIN", "Finland", "Europe"), "FR": ("FRA", "France", "Europe"), "DE": ("DEU", "Germany", "Europe"),
    "GR": ("GRC", "Greece", "Europe"), "HU": ("HUN", "Hungary", "Europe"), "IS": ("ISL", "Iceland", "Europe"),
    "IE": ("IRL", "Ireland", "Europe"), "IT": ("ITA", "Italy", "Europe"), "LV": ("LVA", "Latvia", "Europe"),
    "LT": ("LTU", "Lithuania", "Europe"), "LU": ("LUX", "Luxembourg", "Europe"), "MT": ("MLT", "Malta", "Europe"),
    "NL": ("NLD", "Netherlands", "Europe"), "MK": ("MKD", "North Macedonia", "Europe"),
    "NO": ("NOR", "Norway", "Europe"), "PL": ("POL", "Poland", "Europe"), "PT": ("PRT", "Portugal", "Europe"),
    "RO": ("ROU", "Romania", "Europe"), "RU": ("RUS", "Russia", "Europe"), "RS": ("SRB", "Serbia", "Europe"),
    "SK": ("SVK", "Slovakia", "Europe"), "SI": ("SVN", "Slovenia", "Europe"), "ES": ("ESP", "Spain", "Europe"),
    "SE": ("SWE", "Sweden", "Europe"), "CH": ("CHE", "Switzerland", "Europe"), "TR": ("TUR", "Türkiye", "Europe"),
    "GB": ("GBR", "United Kingdom", "Europe"),
    "AU": ("AUS", "Australia", "Asia and Pacific"), "NZ": ("NZL", "New Zealand", "Asia and Pacific"),
    "JP": ("JPN", "Japan", "Asia and Pacific"), "KR": ("KOR", "S. Korea", "Asia and Pacific"),
    "CN": ("CHN", "China", "Asia and Pacific"), "HK": ("HKG", "Hong Kong", "Asia and Pacific"),
    "IN": ("IND", "India", "Asia and Pacific"), "ID": ("IDN", "Indonesia", "Asia and Pacific"),
    "MY": ("MYS", "Malaysia", "Asia and Pacific"), "PH": ("PHL", "Philippines", "Asia and Pacific"),
    "SG": ("SGP", "Singapore", "Asia and Pacific"), "TH": ("THA", "Thailand", "Asia and Pacific"),
    "IL": ("ISR", "Israel", "Africa and Middle East"), "SA": ("SAU", "Saudi Arabia", "Africa and Middle East"),
    "KW": ("KWT", "Kuwait", "Africa and Middle East"), "MA": ("MAR", "Morocco", "Africa and Middle East"),
    "ZA": ("ZAF", "South Africa", "Africa and Middle East"),
}
NAME = {iso3: name for iso3, name, region in ECONOMIES.values()}
ISO3 = {iso2: v[0] for iso2, v in ECONOMIES.items()}
ISO3.update({"EL": "GRC", "UK": "GBR"})                        # Eurostat's own codes
OECD_AREAS = {"EA20": "EMU", "EA": "EMU", "EA17": "EMU"}        # OECD euro-area codes -> our EMU
EUROSTAT_EA = "EA"                                              # the euro area in its changing composition
EURO_MEMBERS = ["AUT", "BEL", "HRV", "CYP", "EST", "FIN", "FRA", "DEU", "GRC", "IRL", "ITA", "LVA", "LTU", "LUX",
                "MLT", "NLD", "PRT", "SVK", "SVN", "ESP", "BGR"]
OECD = "https://sdmx.oecd.org/public/rest/data/"
SOURCES = {
    "bis_spp_real.csv": "https://stats.bis.org/api/v1/data/WS_SPP/Q..R.628/all?format=csv",
    "bis_cbpol_m.csv": "https://stats.bis.org/api/v1/data/WS_CBPOL/M./all?format=csv&startPeriod=1999-01",
    "oecd_finmark_m.csv": OECD + "OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/.M.IR3TIB+SHARE+IRSTCI......"
                                 "?startPeriod=1990-01&format=csvfilewithlabels",
    "imf_cpi_m.csv": "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/+/*.CPI._T.IX.M"
                     "?c[TIME_PERIOD]=ge:1989-01",
    "oecd_prices_cpi_m.csv": OECD + "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/.M.N.CPI.IX._T+_TXCP01_NRG.N._Z"
                                    "?startPeriod=1989-01&format=csvfilewithlabels",
    "eurostat_prc_hicp_minr.json": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
                                   "prc_hicp_minr?unit=I25&coicop18=TOTAL&coicop18=TOT_X_NRG_FOOD"
                                   "&sinceTimePeriod=2014-01",
    "oecd_lfs_unemployment_m.csv": OECD + "OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,1.0/"
                                          ".UNE_LF_M.PT_LF_SUB._Z.Y._T.Y_GE15._Z.M?startPeriod=2000-01"
                                          "&format=csvfilewithlabels",
    "oecd_lfs_employment_q.csv": OECD + "OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP_Q,1.0/"
                                        ".EMP.PS._Z.Y._T.Y_GE15._Z.Q?startPeriod=2000-Q1&format=csvfilewithlabels",
    "oecd_eo_gap_a.csv": OECD + "OECD.ECO.MAD,DSD_EO@DF_EO,1.5/.GAP.A?startPeriod=1990&format=csvfilewithlabels",
}
IMF_ACCEPT = {"Accept": "application/vnd.sdmx.data+csv;version=1.0.0"}
PANELS = {}                                                     # file name -> DataFrame, for countries.csv


def cached(raw, name, refresh):
    """Path of a raw download in the cache; download it first if needed (requests' default User-Agent)."""
    path = os.path.join(raw, name)
    if refresh or not os.path.exists(path):
        url = SOURCES[name]
        r = requests.get(url, timeout=600, headers=IMF_ACCEPT if "imf.org" in url else None)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        print(f"downloaded {name} ({len(r.content) / 1e6:.1f} MB)")
    return path


def oecd_csv(path, columns=("REF_AREA", "TIME_PERIOD", "OBS_VALUE")):
    """An OECD SDMX csvfilewithlabels download, with OECD euro-area codes mapped to EMU."""
    df = pd.read_csv(path, low_memory=False)
    df = df[[c for c in list(columns) + ["MEASURE", "EXPENDITURE"] if c in df.columns]].copy()
    df["iso3"] = df.REF_AREA.replace(OECD_AREAS)
    return df[df.iso3.isin(NAME)]


def month_start(period):
    """'2008-10', '2008-M10' or '2008-Q4' -> Timestamp of the first day of the month or quarter."""
    s = pd.Series(period).astype(str).str.replace("-M", "-", regex=False)
    quarter = s.str.contains("Q")
    out = pd.to_datetime(s.where(~quarter, "2000-01"), format="%Y-%m")
    if quarter.any():
        out[quarter] = pd.PeriodIndex(s[quarter].str.replace("-", ""), freq="Q").start_time
    return out.values


def save(df, name, value_cols, date_col="date", decimals=3):
    """Write a tidy long panel: iso3, country, date|year, values...; sorted; under 1 MB."""
    df = df.copy()
    df["country"] = df.iso3.map(NAME)
    df = df[["iso3", "country", date_col] + value_cols].dropna(subset=value_cols, how="all")
    df = df.sort_values(["country", date_col]).reset_index(drop=True)
    for c in value_cols:
        if df[c].dtype.kind == "f":
            df[c] = df[c].round(decimals)
    path = os.path.join(HERE, name)
    df.to_csv(path, index=False, date_format="%Y-%m-%d")
    size = os.path.getsize(path)
    span = f"{df[date_col].min():%Y-%m} to {df[date_col].max():%Y-%m}" if date_col == "date" else \
        f"{df[date_col].min()} to {df[date_col].max()}"
    print(f"{name}: {len(df)} rows, {df.iso3.nunique()} economies, {span}, {size / 1e3:.0f} kB")
    if size > 1e6:
        raise SystemExit(f"{name} is larger than 1 MB")
    PANELS[name] = df
    return df


def check(label, ok, detail):
    print(f"  validation {label}: {detail}")
    if not ok:
        raise SystemExit(f"validation failed: {label}")


def book(name, column):
    """A column of a textbook-figure CSV next to this script, as a Series indexed by date."""
    return pd.read_csv(os.path.join(HERE, name), parse_dates=["date"]).set_index("date")[column]


def peak_fall(series, start, end):
    """Percent fall from the highest value in [start, end] to the lowest value after it."""
    w = series[start:end].dropna()
    peak = w.idxmax()
    return 100 * (w[peak:].min() / w[peak] - 1)


def house_prices(raw, refresh):
    df = pd.read_csv(cached(raw, "bis_spp_real.csv", refresh), usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
    df["iso3"] = df.REF_AREA.map(ISO3)
    df = df[df.iso3.notna()].copy()                              # drops the BIS aggregates 4T, 5R, XW
    df["date"] = month_start(df.TIME_PERIOD)
    df = df.rename(columns={"OBS_VALUE": "real_house_price"})
    out = save(df, "house_prices_panel.csv", ["real_house_price"], decimals=2)
    us = out[out.iso3 == "USA"].set_index("date").real_house_price
    shiller = book("fig10-1.csv", "real_home_price_index").resample("QS").mean()
    a, b = peak_fall(us, "2000", "2015"), peak_fall(shiller, "2000", "2015")
    g = pd.concat([us.pct_change(4), shiller.pct_change(4)], axis=1).dropna().corr().iloc[0, 1]
    check("house prices", abs(a - b) < 8 and g > 0.8,
          f"U.S. 2000s bust BIS {a:.1f}% vs Shiller (quarterly means) {b:.1f}%; correlation of 4-quarter "
          f"changes {g:.2f}")


def policy_rates(raw, refresh):
    df = pd.read_csv(cached(raw, "bis_cbpol_m.csv", refresh), usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"])
    df["iso3"] = df.REF_AREA.map(ISO3)
    df = df[df.iso3.notna() & (df.TIME_PERIOD >= "2000-01")].copy()
    df["date"] = month_start(df.TIME_PERIOD)
    df = df.rename(columns={"OBS_VALUE": "policy_rate"})
    out = save(df, "policy_rates_panel.csv", ["policy_rate"])
    us = out[out.iso3 == "USA"].set_index("date").policy_rate
    ffr = book("fig10-2.csv", "fed_funds")
    both = pd.concat([us, ffr], axis=1).dropna()
    gap = (both.iloc[:, 0] - both.iloc[:, 1]).abs()
    check("policy rates", both.corr().iloc[0, 1] > 0.99,
          f"U.S. BIS rate (end of month, target midpoint) vs effective fed funds (monthly mean): correlation "
          f"{both.corr().iloc[0, 1]:.3f}, median gap {gap.median():.2f}, largest {gap.max():.2f} ({gap.idxmax():%Y-%m})")


def finmark(raw, refresh):
    df = oecd_csv(cached(raw, "oecd_finmark_m.csv", refresh))
    df["date"] = month_start(df.TIME_PERIOD)
    return df.pivot_table(index=["iso3", "date"], columns="MEASURE", values="OBS_VALUE").reset_index()


def interbank_spreads(fm):
    df = fm[fm.date >= "2000-01-01"].copy()
    df = df.rename(columns={"IR3TIB": "interbank_3m", "IRSTCI": "overnight"})
    df["spread"] = df.interbank_3m - df.overnight
    # euro-area members share the euro area's money-market rates once they adopt the euro: keep only their
    # months with rates of their own, so the euro area is not drawn 20 times
    ea = df[df.iso3 == "EMU"].set_index("date")[["interbank_3m", "overnight"]]
    keep = []
    for _, row in df.iterrows():
        same = row.iso3 in EURO_MEMBERS and row.date in ea.index and \
            abs(row.interbank_3m - ea.loc[row.date, "interbank_3m"]) < 1e-3 and \
            abs(row.overnight - ea.loc[row.date, "overnight"]) < 1e-3
        keep.append(not same)
    df = df[np.array(keep) & df.spread.notna()]
    out = save(df, "interbank_spreads_panel.csv", ["interbank_3m", "overnight", "spread"], decimals=3)
    us = out[out.iso3 == "USA"].set_index("date").spread
    ted = book("fig10-3.csv", "ted_spread")
    both = pd.concat([us, ted], axis=1).dropna()
    r, r_crisis = both.corr().iloc[0, 1], both["2007":"2009"].corr().iloc[0, 1]
    # a different concept (term interbank minus overnight interbank, not LIBOR minus T-bill): same peak month,
    # but a smaller spike and a lower correlation outside the crisis
    check("interbank spreads", r_crisis > 0.7 and us.idxmax() == ted.idxmax(),
          f"U.S. 3-month interbank minus overnight vs TED spread: correlation {r:.2f} (2000-2022), "
          f"{r_crisis:.2f} (2007-2009); peak {us.max():.2f} in {us.idxmax():%Y-%m} (TED {ted.max():.2f} in "
          f"{ted.idxmax():%Y-%m})")


def imf_cpi(raw, refresh):
    df = pd.read_csv(cached(raw, "imf_cpi_m.csv", refresh), usecols=["COUNTRY", "TIME_PERIOD", "OBS_VALUE"])
    df = df[df.COUNTRY.isin(NAME)].copy()
    df["date"] = month_start(df.TIME_PERIOD)
    return df.rename(columns={"COUNTRY": "iso3", "OBS_VALUE": "cpi"})[["iso3", "date", "cpi"]]


def share_prices(fm, cpi):
    df = fm[["iso3", "date", "SHARE"]].dropna().merge(cpi, on=["iso3", "date"], how="inner")
    base = df[df.date.dt.year == 2015].groupby("iso3")[["SHARE", "cpi"]].mean()
    df = df[df.iso3.isin(base.index)].copy()
    share_2015, cpi_2015 = df.iso3.map(base.SHARE), df.iso3.map(base.cpi)
    df["real_share_price"] = 100 * (df.SHARE / share_2015) / (df.cpi / cpi_2015)
    # data hygiene: a real index that jumps more than 3-fold in one month has a break (index rebased, or a
    # currency reform in hyperinflation): keep each economy's data from its last break on
    parts = []
    for iso3, g in df.sort_values("date").groupby("iso3"):
        ratio = g.real_share_price / g.real_share_price.shift(1)
        jumps = g.date[(ratio > 3) | (ratio < 1 / 3)]
        if len(jumps):
            print(f"  {iso3}: real share index breaks; kept from {jumps.max():%Y-%m}")
            g = g[g.date >= jumps.max()]
        parts.append(g)
    df = pd.concat(parts)
    out = save(df, "share_prices_panel.csv", ["real_share_price"], decimals=1)
    us = out[out.iso3 == "USA"].set_index("date").real_share_price
    sp = book("fig10-4.csv", "sp500_real")
    a, b = peak_fall(us, "2007", "2009-12"), peak_fall(sp, "2007", "2009-12")
    check("share prices", abs(a - b) < 6,
          f"U.S. 2007-09 fall OECD/IMF {a:.1f}% vs Shiller real S&P 500 {b:.1f}%; "
          f"correlation of levels {pd.concat([us, sp], axis=1).dropna().corr().iloc[0, 1]:.3f}")


def gdp_quarterly(root):
    # the same OECD QNA download as fig10-5/fig10-6 (all economies), so the six book countries match exactly
    df = oecd_csv(os.path.join(root, "fig10-5/raw/oecd_qna_gdp_volume_index.csv"))
    df["date"] = month_start(df.TIME_PERIOD)
    base = df[df.date == "2019-10-01"].set_index("iso3").OBS_VALUE
    df = df[(df.date >= "2019-10-01") & df.iso3.isin(base.index)].copy()
    df["gdp_index"] = 100 * df.OBS_VALUE / df.iso3.map(base)
    out = save(df, "gdp_quarterly_panel.csv", ["gdp_index"])
    worst = 0
    for code in ["usa", "kor", "swe", "deu", "gbr", "esp"]:
        mine = out[out.iso3 == code.upper()].set_index("date").gdp_index
        worst = max(worst, (mine - book("fig10-6.csv", f"gdp_index_{code}")).abs().max())
    check("quarterly GDP", worst < 0.01, f"six textbook countries vs fig10-6.csv: largest difference {worst:.4f}")


def employment(raw, refresh):
    df = oecd_csv(cached(raw, "oecd_lfs_employment_q.csv", refresh))
    df["date"] = month_start(df.TIME_PERIOD)
    df = df.rename(columns={"OBS_VALUE": "employment"})
    out = save(df, "employment_panel.csv", ["employment"], decimals=1)
    us = out[out.iso3 == "USA"].set_index("date").employment
    payroll = book("fig10-7.csv", "nonfarm_emp").resample("QS").mean()
    both = pd.concat([us.pct_change(4), payroll.pct_change(4)], axis=1).dropna()
    r = both.corr().iloc[0, 1]
    a = 100 * (us["2020-04-01"] / us["2019-10-01"] - 1)
    b = 100 * (payroll["2020-04-01"] / payroll["2019-10-01"] - 1)
    check("employment", r > 0.9, f"U.S. household-survey vs payroll employment: correlation of 4-quarter "
          f"changes {r:.2f}; 2019Q4-2020Q2 {a:.1f}% vs {b:.1f}%")


def output_gaps(raw, refresh):
    df = oecd_csv(cached(raw, "oecd_eo_gap_a.csv", refresh), ("REF_AREA", "TIME_PERIOD", "OBS_VALUE"))
    df = df.rename(columns={"TIME_PERIOD": "year", "OBS_VALUE": "output_gap"})
    df["projection"] = df.year >= 2026                          # Economic Outlook 119 (June 2026) projects 2026-27
    out = save(df, "output_gap_panel.csv", ["output_gap", "projection"], date_col="year", decimals=2)
    us = out[out.iso3 == "USA"].set_index("year").output_gap
    cbo = book("fig10-8.csv", "short_run_output")
    cbo = cbo.groupby(cbo.index.year).mean()
    both = pd.concat([us, cbo], axis=1).dropna()
    r = both.corr().iloc[0, 1]
    check("output gaps", r > 0.7, f"U.S. OECD gap vs annual mean of CBO-based short-run output, 2000-2025: "
          f"correlation {r:.2f}; 2009 {us[2009]:.1f} vs {cbo[2009]:.1f}; 2020 {us[2020]:.1f} vs {cbo[2020]:.1f}")


def unemployment(raw, refresh):
    df = oecd_csv(cached(raw, "oecd_lfs_unemployment_m.csv", refresh))
    df["date"] = month_start(df.TIME_PERIOD)
    df = df.rename(columns={"OBS_VALUE": "unemployment_rate"})
    out = save(df, "unemployment_panel.csv", ["unemployment_rate"], decimals=1)
    us = out[out.iso3 == "USA"].set_index("date").unemployment_rate
    bls = book("fig10-9.csv", "unemp_rate")
    gap = (us - bls).dropna().abs()
    check("unemployment", gap.max() < 0.15, f"U.S. OECD vs BLS UNRATE: largest difference {gap.max():.2f} "
          f"over {len(gap)} months")


def log_change(index):
    """12-month inflation as the textbook draws it: 100 ln(P_t / P_t-12), monthly index by date."""
    return 100 * np.log(index / index.shift(12, freq="MS").reindex(index.index))


def eurostat_hicp(raw, refresh):
    """Eurostat HICP (2025 = 100), long: iso3, date, coicop, index."""
    import json
    j = json.load(open(cached(raw, "eurostat_prc_hicp_minr.json", refresh)))
    dims, sizes = j["id"], j["size"]
    labels = {}
    for d in dims:                                              # position -> code, for each dimension
        index = j["dimension"][d]["category"]["index"]
        labels[d] = {pos: code for code, pos in index.items()}
    rows = []
    for flat, value in j["value"].items():
        k, pos = int(flat), {}
        for d, n in zip(reversed(dims), reversed(sizes)):
            pos[d] = labels[d][k % n]
            k //= n
        rows.append((pos["geo"], pos["time"], pos["coicop18"], value))
    df = pd.DataFrame(rows, columns=["geo", "time", "coicop", "index"])
    df["iso3"] = df.geo.map(ISO3)
    df.loc[df.geo == EUROSTAT_EA, "iso3"] = "EMU"
    df = df[df.iso3.notna()].copy()
    df["date"] = pd.to_datetime(df.time, format="%Y-%m")
    return df


def inflation(raw, refresh, cpi):
    rows = []
    # 1. the textbook's three economies, exactly as in fig10-10.csv and fig10-11.csv
    head, core = pd.read_csv(os.path.join(HERE, "fig10-10.csv")), pd.read_csv(os.path.join(HERE, "fig10-11.csv"))
    for iso3, h, c in [("USA", "inflation_us", "core_inflation_us"), ("GBR", "inflation_uk", "core_inflation_uk"),
                       ("EMU", "inflation_euro_area", "core_inflation_euro_area")]:
        rows.append(pd.DataFrame({"iso3": iso3, "date": pd.to_datetime(head.date), "inflation": head[h],
                                  "core_inflation": core[c], "source": "textbook figure (fig10-10, fig10-11)"}))
    done = {"USA", "GBR", "EMU"}
    # 2. European economies: Eurostat HICP, headline and core from the same index family
    hicp = eurostat_hicp(raw, refresh)
    for iso3, g in hicp.groupby("iso3"):
        if iso3 in done or g[g.coicop == "TOTAL"]["index"].isna().all():
            continue
        h = log_change(g[g.coicop == "TOTAL"].set_index("date")["index"])
        c = log_change(g[g.coicop == "TOT_X_NRG_FOOD"].set_index("date")["index"])
        if h["2015":].notna().sum() < 100:
            continue
        rows.append(pd.DataFrame({"iso3": iso3, "inflation": h, "core_inflation": c.reindex(h.index),
                                  "source": "Eurostat HICP"}).rename_axis("date").reset_index())
        done.add(iso3)
    # 3. everyone else: IMF national CPI (headline) and the OECD's CPI excluding food and energy (core)
    oecd = oecd_csv(cached(raw, "oecd_prices_cpi_m.csv", refresh))
    oecd = oecd[oecd.EXPENDITURE == "_TXCP01_NRG"].copy()
    oecd["date"] = month_start(oecd.TIME_PERIOD)
    for iso3, g in cpi.groupby("iso3"):
        if iso3 in done:
            continue
        h = log_change(g.set_index("date").cpi)
        c = oecd[oecd.iso3 == iso3].set_index("date").OBS_VALUE
        c = log_change(c).reindex(h.index) if len(c) else pd.Series(np.nan, index=h.index)
        rows.append(pd.DataFrame({"iso3": iso3, "inflation": h, "core_inflation": c,
                                  "source": "IMF CPI; core: OECD"}).rename_axis("date").reset_index())
    df = pd.concat(rows, ignore_index=True)
    df = df[(df.date >= "2015-01-01") & (df.inflation.notna() | df.core_inflation.notna())]
    out = save(df, "inflation_panel.csv", ["inflation", "core_inflation", "source"])
    # validation: our own Eurostat and IMF downloads reproduce the textbook's euro area and U.S. series
    ea = hicp[(hicp.iso3 == "EMU") & (hicp.coicop == "TOTAL")].set_index("date")["index"]
    d1 = (log_change(ea) - book("fig10-10.csv", "inflation_euro_area")).dropna().abs().max()
    us = cpi[cpi.iso3 == "USA"].set_index("date").cpi
    d2 = (log_change(us) - book("fig10-10.csv", "inflation_us")).dropna().abs().max()
    check("inflation", d1 < 0.05 and d2 < 0.05, f"Eurostat euro area vs fig10-10: largest difference {d1:.3f}; "
          f"IMF U.S. CPI vs fig10-10: {d2:.3f} points")
    print(f"  sources: {out.groupby('source').iso3.nunique().to_dict()}")


def countries_table():
    used = set()
    for df in PANELS.values():
        used |= set(df.iso3)
    table = pd.DataFrame([v for v in ECONOMIES.values() if v[0] in used], columns=["iso3", "country", "region"])
    table = table.sort_values("country").reset_index(drop=True)
    table.to_csv(os.path.join(HERE, "countries.csv"), index=False)
    print(f"countries.csv: {len(table)} economies, {table.region.value_counts().to_dict()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    ap.add_argument("--refresh", action="store_true", help="download the multi-country sources again")
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    rec = recessions(root)
    data = quarterly_data(root)
    validate(root, rec, data)
    raw = os.path.join(args.macro102, ".work", "ch10", "notebook-raw")
    os.makedirs(raw, exist_ok=True)
    house_prices(raw, args.refresh)
    policy_rates(raw, args.refresh)
    fm = finmark(raw, args.refresh)
    interbank_spreads(fm)
    cpi = imf_cpi(raw, args.refresh)
    share_prices(fm, cpi)
    gdp_quarterly(root)
    employment(raw, args.refresh)
    output_gaps(raw, args.refresh)
    unemployment(raw, args.refresh)
    inflation(raw, args.refresh, cpi)
    countries_table()


if __name__ == "__main__":
    main()
