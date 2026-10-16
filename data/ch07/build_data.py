"""Build the wider data files used by the Chapter 7 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/):
  fig7-1/raw/fred_USREC.csv                NBER recession indicator, monthly (1 = recession month)
  ex02/raw/fred_LNS12300001.csv            employment-population ratio, men 16+, percent, monthly, SA
  ex02/raw/fred_LNS12300002.csv            employment-population ratio, women 16+, percent, monthly, SA
  table7-1/raw/fred_CNP16OV.csv            civilian noninstitutional population 16+, thousands, monthly
  table7-1/raw/fred_CLF16OV.csv            civilian labor force, thousands, monthly, SA
  table7-1/raw/fred_CE16OV.csv             employment level, thousands, monthly, SA
  table7-1/raw/fred_UNEMPLOY.csv           unemployment level, thousands, monthly, SA
  table7-2/raw/pwt110_subset.csv           Penn World Table 11.0: countrycode, country, year, avh, emp, pop
  table7-2/raw/pwt1001_subset.csv          Penn World Table 10.01, same columns
Outputs (next to this script):
  recessions.csv        peak, trough                 NBER peaks and troughs whose trough is in 1950 or later
  emp_pop_by_sex.csv    date, men, women             monthly employment-population ratios, 1948-01 on
  labor_force.csv       date, population, labor_force, employed, unemployed, not_in_labor_force
                                                     millions, monthly, 1948-01 on (Table 7.1 for any month)
  hours_per_person.csv  country, year, hours_pwt11, hours_pwt10
                                                     annual hours worked per person, U.S. 2019 = 100 (Table 7.2)

Multi-country files (conventions section 6b). Downloads are cached in ../macro102/.work/ch07/notebook-raw/
(delete a file there to download it again):
  emp_pop_countries.csv        iso3, country, region, year, emp_pop_ratio
                               employment-to-population ratio 15+, ILO modelled (WDI SL.EMP.TOTL.SP.ZS), 1991-2025
  unemployment_countries_monthly.csv
                               iso3, country, date, unemployment_rate
                               OECD harmonised unemployment rates via FRED (LRHUTTTT{CC}M156S), monthly, SA
  unemployment_countries.csv   iso3, country, year, unemployment_rate
                               AMECO unemployment rates (ZUTN), annual, 1960-2025 (input: fig7-7/raw/ameco1.zip)
  college_premium_countries.csv
                               iso3, country, year, relative_earnings, premium_log_points, bachelor_share
                               OECD Education at a Glance: earnings of full-time workers 25-64 with a bachelor's
                               or higher degree relative to upper secondary (= 100), and their population share
  manufacturing_countries.csv  iso3, country, region, year, manufacturing_millions, manufacturing_share
                               employment in manufacturing, ILO modelled estimates (ILOSTAT EMP_2EMP_SEX_ECO_NB_A)
  top01_share_countries.csv    iso3, country, region, year, top01_share
                               pre-tax income share of the top 0.1%, WID bulk files (sptincj992)
  percentile_growth_countries.csv
                               iso3, country, region, period, percentile, growth_pct
                               growth of pre-tax national income per adult by g-percentile, WID bulk files
"""
import argparse
import io
import json
import os
import time
import zipfile

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/"
NAMES = {"United Kingdom": "U.K.", "Republic of Korea": "South Korea"}   # the textbook's names
ORDER = ["United States", "Italy", "France", "Germany", "U.K.", "Japan", "South Korea"]


def fred(root, path):
    """One FRED series as a Series indexed by month."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = fred(root, "fig7-1/raw/fred_USREC.csv")
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1950-01-01"]
    for col in ["peak", "trough"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def by_sex(root):
    """Employment-population ratios of men and women; validated against macro102's ex02/data.csv."""
    out = pd.DataFrame({"men": fred(root, "ex02/raw/fred_LNS12300001.csv"),
                        "women": fred(root, "ex02/raw/fred_LNS12300002.csv")}).dropna()
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "emp_pop_by_sex.csv"), date_format="%Y-%m-%d")
    ref = pd.read_csv(os.path.join(root, "ex02/data.csv"), parse_dates=["date"]).set_index("date")
    diff = max((out.men - ref.emp_pop_ratio_men).abs().max(), (out.women - ref.emp_pop_ratio_women).abs().max())
    print(f"emp_pop_by_sex.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"largest difference from ex02/data.csv: {diff:.3f}")


def labor_force(root):
    """Monthly CPS levels in millions; validated against table7-1/data.csv and fig7-2.csv (UNRATE)."""
    out = pd.DataFrame({"population": fred(root, "table7-1/raw/fred_CNP16OV.csv"),
                        "labor_force": fred(root, "table7-1/raw/fred_CLF16OV.csv"),
                        "employed": fred(root, "table7-1/raw/fred_CE16OV.csv"),
                        "unemployed": fred(root, "table7-1/raw/fred_UNEMPLOY.csv")}).dropna() / 1000
    out["not_in_labor_force"] = out.population - out.labor_force
    out = out.round(3)
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "labor_force.csv"), date_format="%Y-%m-%d")
    ref = pd.read_csv(os.path.join(root, "table7-1/data.csv"))
    ours = out.loc["2023-01-01", ["population", "labor_force", "employed", "unemployed", "not_in_labor_force"]]
    print(f"labor_force.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"January 2023 vs table7-1: {(ours.values - ref.millions_book_2023[:5].values).round(3).tolist()}")
    rate = (100 * out.unemployed / out.labor_force).round(1)
    unrate = pd.read_csv(os.path.join(HERE, "fig7-2.csv"), parse_dates=["date"]).set_index("date").unemployment_rate
    both = pd.concat([rate, unrate], axis=1, join="inner")
    print(f"  computed rate vs UNRATE: largest difference {(both.iloc[:, 0] - both.iloc[:, 1]).abs().max():.2f} points")


def hours(root):
    """Hours worked per person (avh x emp / pop), U.S. 2019 = 100, in PWT 11.0 and PWT 10.01."""
    cols = []
    for name, path in [["hours_pwt11", "table7-2/raw/pwt110_subset.csv"], ["hours_pwt10", "table7-2/raw/pwt1001_subset.csv"]]:
        pwt = pd.read_csv(os.path.join(root, path))
        pwt["country"] = pwt.country.replace(NAMES)
        h = (pwt["avh"] * pwt["emp"] / pwt["pop"]).set_axis(pd.MultiIndex.from_frame(pwt[["country", "year"]]))
        cols.append((100 * h / h.loc[("United States", 2019)]).rename(name))
    out = pd.concat(cols, axis=1).dropna(how="all").round(2).reset_index()
    out["order"] = out.country.map({c: i for i, c in enumerate(ORDER)})
    out = out.sort_values(["order", "year"]).drop(columns="order")
    out.to_csv(os.path.join(HERE, "hours_per_person.csv"), index=False)
    ref = pd.read_csv(os.path.join(root, "table7-2/data.csv")).set_index("item")
    wide = out.pivot(index="country", columns="year", values="hours_pwt10")
    worst = max((wide.loc[ref.index, y] - ref[f"hours_pwt1001_{y}"]).abs().max() for y in [1960, 1990, 2019])
    print(f"hours_per_person.csv: {len(out)} rows, {out.country.nunique()} countries, "
          f"{out.year.min()}-{out.year.max()}; largest difference from table7-2 (PWT 10.01): {worst:.2f}")


# ---- multi-country helpers (section 6b) ---------------------------------------------------------
READABLE = {"Bahamas, The": "Bahamas", "Congo, Dem. Rep.": "DR Congo", "Congo, Rep.": "Congo",
            "Egypt, Arab Rep.": "Egypt", "Micronesia, Fed. Sts.": "Micronesia", "Gambia, The": "Gambia",
            "Hong Kong SAR, China": "Hong Kong", "Iran, Islamic Rep.": "Iran", "Kyrgyz Republic": "Kyrgyzstan",
            "Korea, Rep.": "South Korea", "Lao PDR": "Laos", "Macao SAR, China": "Macao",
            "Korea, Dem. People's Rep.": "North Korea", "Russian Federation": "Russia",
            "Somalia, Fed. Rep.": "Somalia", "Slovak Republic": "Slovakia", "Syrian Arab Republic": "Syria",
            "Venezuela, RB": "Venezuela", "Yemen, Rep.": "Yemen", "Viet Nam": "Vietnam", "Turkiye": "Turkey",
            "West Bank and Gaza": "Palestine", "Brunei Darussalam": "Brunei", "Cabo Verde": "Cape Verde",
            "St. Kitts and Nevis": "Saint Kitts and Nevis", "St. Lucia": "Saint Lucia",
            "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines", "Curacao": "Curaçao",
            "Sint Maarten (Dutch part)": "Sint Maarten", "St. Martin (French part)": "Saint Martin",
            "Virgin Islands (U.S.)": "U.S. Virgin Islands", "Cote d'Ivoire": "Côte d'Ivoire",
            "Sao Tome and Principe": "São Tomé and Príncipe", "Puerto Rico (US)": "Puerto Rico"}
EXTRA = {"TWN": ("Taiwan", "East Asia & Pacific", "TW")}   # not in the World Bank's country list
OECD = ("AUS AUT BEL CAN CHL COL CRI CZE DNK EST FIN FRA DEU GRC HUN ISL IRL ISR ITA JPN KOR LVA LTU LUX "
        "MEX NLD NZL NOR POL PRT SVK SVN ESP SWE CHE TUR GBR USA").split()


def cached(cache, name, url, params=None, headers=None):
    """Download url once into the cache folder (requests' default User-Agent) and return the local path."""
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        for wait in [0, 30, 90]:                      # the OECD API answers 429 when called too often
            time.sleep(wait)
            r = requests.get(url, params=params, headers=headers, timeout=600)
            if r.status_code != 429:
                break
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def countries(cache):
    """DataFrame indexed by iso3: readable name, World Bank region and iso2 of every economy."""
    path = cached(cache, "wb_countries.json", "https://api.worldbank.org/v2/country",
                  {"format": "json", "per_page": 400})
    rows = {}
    for c in json.load(open(path))[1]:
        if c["region"]["value"] != "Aggregates":
            rows[c["id"]] = (READABLE.get(c["name"], c["name"]), c["region"]["value"].strip(), c["iso2Code"])
    rows.update(EXTRA)
    return pd.DataFrame.from_dict(rows, orient="index", columns=["country", "region", "iso2"])


def save(df, name, what):
    """Write one tidy file and report its size (every file must stay under 1 MB)."""
    path = os.path.join(HERE, name)
    df.to_csv(path, index=False)
    print(f"{name}: {len(df)} rows, {df.iso3.nunique()} countries, {what}, {os.path.getsize(path) / 1e6:.2f} MB")


def emp_pop_countries(cache, names):
    """Figure 7.1 beyond the U.S.: employment-to-population ratio 15+ (ILO modelled), every country in WDI."""
    path = cached(cache, "wdi_SL.EMP.TOTL.SP.ZS.json",
                  "https://api.worldbank.org/v2/country/all/indicator/SL.EMP.TOTL.SP.ZS",
                  {"format": "json", "per_page": 20000})
    d = pd.json_normalize(json.load(open(path))[1]).dropna(subset=["value"])
    d = d[d.countryiso3code.isin(names.index)]
    out = pd.DataFrame({"iso3": d.countryiso3code, "year": d.date.astype(int), "emp_pop_ratio": d.value.round(2)})
    out = out.join(names[["country", "region"]], on="iso3")[["iso3", "country", "region", "year", "emp_pop_ratio"]]
    out = out.sort_values(["country", "year"])
    save(out, "emp_pop_countries.csv", f"{out.year.min()}-{out.year.max()}")
    us = out[out.iso3 == "USA"].set_index("year").emp_pop_ratio
    ref = pd.read_csv(os.path.join(HERE, "fig7-1.csv"), parse_dates=["date"])
    ref = ref.groupby(ref.date.dt.year).emp_pop_ratio.mean()
    diff = (us - ref).dropna()
    print(f"  U.S. (ages 15+, ILO) minus EMRATIO (16+, BLS) annual mean, {diff.index.min()}-{diff.index.max()}: "
          f"mean {diff.mean():+.2f}, range {diff.min():+.2f} to {diff.max():+.2f} points")


def unemployment_monthly(cache, names):
    """Figure 7.2 beyond the U.S.: OECD harmonised unemployment rates (FRED), monthly where FRED has them."""
    frames = []
    for iso3 in OECD:
        iso2 = names.loc[iso3, "iso2"]
        for freq in ["M", "Q"]:                       # monthly if possible; New Zealand and Switzerland: quarterly
            sid = f"LRHUTTTT{iso2}{freq}156S"
            try:
                path = cached(cache, f"fred_{sid}.csv", f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}")
            except requests.HTTPError:
                continue
            d = pd.read_csv(path)
            d.columns = ["date", "unemployment_rate"]
            d["unemployment_rate"] = pd.to_numeric(d.unemployment_rate, errors="coerce")
            d = d.dropna()
            if len(d):
                d["iso3"] = iso3
                frames.append(d)
                break
    out = pd.concat(frames)
    # The U.S. series is the BLS rate (UNRATE); fig7-2.csv carries it to the latest month
    ref = pd.read_csv(os.path.join(HERE, "fig7-2.csv")).set_index("date").unemployment_rate
    us = out[out.iso3 == "USA"].set_index("date").unemployment_rate
    both = pd.concat([us, ref], axis=1, join="inner")
    print(f"  U.S.: OECD minus UNRATE, {both.index.min()[:7]} to {both.index.max()[:7]}: "
          f"largest difference {(both.iloc[:, 0] - both.iloc[:, 1]).abs().max():.3f} points; replaced by fig7-2.csv")
    ref = ref.loc["1955-01-01":].reset_index()
    ref["iso3"] = "USA"
    out = pd.concat([out[out.iso3 != "USA"], ref])
    out["unemployment_rate"] = out.unemployment_rate.round(2)
    out = out.join(names[["country"]], on="iso3")[["iso3", "country", "date", "unemployment_rate"]]
    out = out.sort_values(["country", "date"])
    missing = sorted(set(OECD) - set(out.iso3))
    save(out, "unemployment_countries_monthly.csv", f"{out.date.min()[:7]} to {out.date.max()[:7]}; "
         f"no FRED series for {missing}")


def unemployment_annual(root, names):
    """Figure 7.7 beyond three economies: AMECO unemployment rates, 1960-2025 (forecast years dropped)."""
    z = zipfile.ZipFile(os.path.join(root, "fig7-7/raw/ameco1.zip"))
    a = pd.read_csv(z.open("AMECO1.TXT"), sep=";", encoding="latin1")
    a = a[a.CODE.str.endswith(".1.0.0.0.ZUTN")]
    a["code"] = a.CODE.str.split(".").str[0]
    years = [str(y) for y in range(1960, 2026)]
    long = a.melt(id_vars="code", value_vars=years, var_name="year", value_name="unemployment_rate")
    long["unemployment_rate"] = pd.to_numeric(long.unemployment_rate, errors="coerce")
    long = long.dropna().astype({"year": int})
    # splices: West Germany before 1991, and the euro area of 12 (incl. West Germany) before 1991, as in fig7-7.csv
    long.loc[(long.code == "D_W") & (long.year <= 1990), "code"] = "DEU"
    long.loc[(long.code == "DA12") & (long.year <= 1990), "code"] = "EA12"
    long = long[long.code.isin(list(names.index) + ["ROM", "EA12"])]
    long["code"] = long.code.replace({"ROM": "ROU"})
    long = long.drop_duplicates(["code", "year"])
    long = long.rename(columns={"code": "iso3"}).join(names[["country"]], on="iso3")
    long.loc[long.iso3 == "EA12", "country"] = "Euro area (12 countries)"
    out = long[["iso3", "country", "year", "unemployment_rate"]].sort_values(["country", "year"])
    out["unemployment_rate"] = out.unemployment_rate.round(2)
    save(out, "unemployment_countries.csv", f"{out.year.min()}-{out.year.max()}")
    ref = pd.read_csv(os.path.join(HERE, "fig7-7.csv")).set_index("year")
    for iso3, col in [["EA12", "unrate_europe"], ["JPN", "unrate_japan"], ["USA", "unrate_us"]]:
        ours = out[out.iso3 == iso3].set_index("year").unemployment_rate
        diff = (ours - ref[col]).dropna()
        print(f"  {iso3} minus fig7-7.csv {col}: largest difference {diff.abs().max():.2f} points ({len(diff)} years)")


def college_premium_countries(cache, names):
    """Figure 7.8 beyond the U.S.: OECD relative earnings of graduates and the share of graduates, adults 25-64."""
    base = "https://sdmx.oecd.org/public/rest/data/OECD.EDU.IMEP,DSD_EAG_LSO_EA@{},1.0/._T.Y25T64.ISCED11A_6T8.............."
    accept = {"Accept": "application/vnd.sdmx.data+csv;version=2.0.0"}
    earn = pd.read_csv(cached(cache, "oecd_eag_rel_earnings.csv", base.format("DF_LSO_EARN_REL_UPPER"), headers=accept))
    earn = earn[(earn.WORK_TIME_ARNGMNT == "FT") & earn.OBS_VALUE.notna()]
    odd = earn[earn.OBS_VALUE < 50]                  # graduates earning under half: a unit error in the source
    print(f"  dropped implausible relative earnings: {odd[['REF_AREA', 'TIME_PERIOD', 'OBS_VALUE']].values.tolist()}")
    earn = earn[earn.OBS_VALUE >= 50]
    earn = earn.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year", "OBS_VALUE": "relative_earnings"})
    share = pd.read_csv(cached(cache, "oecd_eag_attainment.csv", base.format("DF_LSO_NEAC_DISTR_EA"), headers=accept))
    share = share[(share.STATISTICAL_OPERATION == "OBS") & share.OBS_VALUE.notna()]
    share = share.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year", "OBS_VALUE": "bachelor_share"})
    out = pd.merge(earn[["iso3", "year", "relative_earnings"]], share[["iso3", "year", "bachelor_share"]],
                   on=["iso3", "year"], how="outer")
    out = out[out.iso3.isin(names.index)].join(names[["country"]], on="iso3")
    out["premium_log_points"] = (100 * np.log(out.relative_earnings / 100)).round(2)
    out = out.round({"relative_earnings": 2, "bachelor_share": 2})
    out = out[["iso3", "country", "year", "relative_earnings", "premium_log_points", "bachelor_share"]]
    out = out.sort_values(["country", "year"])
    save(out, "college_premium_countries.csv", f"{out.year.min()}-{out.year.max()}")
    us = out[out.iso3 == "USA"].set_index("year")
    ref = pd.read_csv(os.path.join(HERE, "fig7-8.csv")).set_index("year")
    both = pd.concat([us.premium_log_points, ref.college_premium_log_pct], axis=1, join="inner").dropna()
    print(f"  U.S. OECD premium (full-time, raw) minus EPI premium (hourly, adjusted), {both.index.min()}-"
          f"{both.index.max()}: mean {(both.iloc[:, 0] - both.iloc[:, 1]).mean():+.1f} log points")


def manufacturing_countries(cache, names):
    """Figure 7.10 beyond the U.S.: employment in manufacturing, ILO modelled estimates, 1991 on."""
    url = ("https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_ECO_NB_A&sex=SEX_T"
           "&classif1=ECO_AGGREGATE_MAN+ECO_AGGREGATE_TOTAL&format=.csv&type=code")
    d = pd.read_csv(cached(cache, "ilo_EMP_2EMP_SEX_ECO_NB_A.csv", url))
    d = d[(d.sex == "SEX_T") & d.ref_area.isin(names.index)]
    w = d.pivot_table(index=["ref_area", "time"], columns="classif1", values="obs_value").dropna().reset_index()
    out = pd.DataFrame({"iso3": w.ref_area, "year": w.time,
                        "manufacturing_millions": (w.ECO_AGGREGATE_MAN / 1000).round(3),
                        "manufacturing_share": (100 * w.ECO_AGGREGATE_MAN / w.ECO_AGGREGATE_TOTAL).round(2)})
    out = out.join(names[["country", "region"]], on="iso3")
    out = out[["iso3", "country", "region", "year", "manufacturing_millions", "manufacturing_share"]]
    out = out.sort_values(["country", "year"])
    save(out, "manufacturing_countries.csv", f"{out.year.min()}-{out.year.max()}")
    us = out[out.iso3 == "USA"].set_index("year").manufacturing_millions
    ref = pd.read_csv(os.path.join(HERE, "fig7-10.csv"), parse_dates=["date"])
    ref = ref.groupby(ref.date.dt.year).manufacturing_emp_millions.mean()
    diff = (us - ref).dropna()
    print(f"  U.S. ILO (household survey) minus MANEMP (payroll) annual mean, {diff.index.min()}-{diff.index.max()}: "
          f"{diff.min():+.2f} to {diff.max():+.2f} million")


def top01_countries(cache, names):
    """Figure 7.11 beyond two countries: pre-tax income share of the top 0.1% (WID sptincj992), all years."""
    frames = []
    for iso3 in WID_COUNTRIES:
        d = wid_country(cache, names.loc[iso3, "iso2"])
        d = d[d.variable == "sptincj992"]
        frames.append(pd.DataFrame({"iso3": iso3, "year": d.year, "top01_share": (100 * d.value).round(3)}))
    out = pd.concat(frames).join(names[["country", "region"]], on="iso3")
    out = out[["iso3", "country", "region", "year", "top01_share"]].sort_values(["country", "year"])
    save(out, "top01_share_countries.csv", f"{out.year.min()}-{out.year.max()}")
    ref = pd.read_csv(os.path.join(HERE, "fig7-11.csv")).set_index("year")
    for iso3, col in [["USA", "top01_share_us"], ["FRA", "top01_share_france"]]:
        ours = out[out.iso3 == iso3].set_index("year").top01_share
        diff = (ours - ref[col]).dropna()
        print(f"  {iso3} minus fig7-11.csv (WID via OWID): largest difference {diff.abs().max():.3f} points "
              f"over {len(diff)} years; WID years {ours.index.min()}-{ours.index.max()}")


# ---- Figure 7.12 beyond the U.S.: WID g-percentiles ----------------------------------------------
WID_ZIP = "https://wid.world/bulk_download/wid_all_data.zip"
WID_COUNTRIES = OECD + "ARG BGD BRA CHN EGY ETH IDN IND IRN KEN MAR MYS NGA PAK PHL RUS SAU THA VNM ZAF".split()
PERIODS = [(1980, 2014), (1990, 2024)]     # the textbook's 34-year window, and the latest 34 years


class RangeFile(io.RawIOBase):
    """Read a remote file with HTTP range requests, so zipfile can extract one member of a 900 MB archive."""

    def __init__(self, url):
        self.url, self.pos, self.session = url, 0, requests.Session()
        self.size = int(self.session.head(url, timeout=60).headers["content-length"])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = [offset, self.pos + offset, self.size + offset][whence]
        return self.pos

    def readinto(self, buffer):
        end = min(self.pos + len(buffer), self.size) - 1
        if end < self.pos:
            return 0
        data = self.session.get(self.url, headers={"Range": f"bytes={self.pos}-{end}"}, timeout=300).content
        buffer[:len(data)] = data
        self.pos += len(data)
        return len(data)


def g_percentiles():
    """WID's 127 g-percentiles: p0p1 ... p98p99, then p99p99.1 ... p99.999p100 (upper bound = percentile)."""
    edges = [float(i) for i in range(100)] + [99 + i / 10 for i in range(1, 10)]
    edges += [99.9 + i / 100 for i in range(1, 10)] + [99.99 + i / 1000 for i in range(1, 10)] + [100.0]
    labels = {}
    for lo, hi in zip(edges[:-1], edges[1:]):
        labels[f"p{lo:g}p{hi:g}"] = round(hi, 3)
    return labels


def wid_country(cache, iso2):
    """WID rows for one country, cached: average pre-tax national income per adult (aptincj992) by
    g-percentile from 1980, and the pre-tax income share of the top 0.1% (sptincj992, p99.9p100), all years."""
    path = os.path.join(cache, f"wid_{iso2}.csv")
    if not os.path.exists(path):
        z = zipfile.ZipFile(io.BufferedReader(RangeFile(WID_ZIP), buffer_size=1 << 20))
        d = pd.read_csv(z.open(f"WID_data_{iso2}.csv"), sep=";", usecols=["variable", "percentile", "year", "value"])
        income = (d.variable == "aptincj992") & d.percentile.isin(list(g_percentiles())) & (d.year >= 1980)
        top = (d.variable == "sptincj992") & (d.percentile == "p99.9p100")
        d[income | top].to_csv(path, index=False)
    return pd.read_csv(path)


def percentile_growth(cache, names):
    """Average annual growth, 100 x [(y_end / y_start)^(1/34) - 1], at each g-percentile, as in fig7-12.csv."""
    labels = g_percentiles()
    frames = []
    for iso3 in WID_COUNTRIES:
        d = wid_country(cache, names.loc[iso3, "iso2"])
        d = d[d.variable == "aptincj992"]
        w = d.pivot_table(index="percentile", columns="year", values="value")
        for start, end in PERIODS:
            if start not in w or end not in w:
                continue
            ratio = (w[end] / w[start]).where((w[start] > 0) & (w[end] > 0))
            g = (100 * (ratio ** (1 / (end - start)) - 1)).round(2).dropna()
            frames.append(pd.DataFrame({"iso3": iso3, "period": f"{start}–{end}",
                                        "percentile": g.index.map(labels), "growth_pct": g.values}))
    out = pd.concat(frames).join(names[["country", "region"]], on="iso3")
    out = out[["iso3", "country", "region", "period", "percentile", "growth_pct"]]
    out = out.sort_values(["country", "period", "percentile"])
    save(out, "percentile_growth_countries.csv", f"periods {sorted(out.period.unique())}")
    us = out[(out.iso3 == "USA") & (out.period == "1980–2014")].set_index("percentile").growth_pct
    ref = pd.read_csv(os.path.join(HERE, "fig7-12.csv"))
    ref = ref[(ref.series == "g-percentile (PSZ 2018)") & (ref.year == 2014)].set_index("percentile").growth_pct
    for p in [10, 50, 90, 99, 99.9, 99.99]:
        print(f"  U.S. 1980-2014 at percentile {p}: WID pre-tax {us.get(p, float('nan')):.2f}%, "
              f"PSZ post-tax (fig7-12.csv) {ref.get(p, float('nan')):.2f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work/ch07/notebook-raw")
    os.makedirs(cache, exist_ok=True)
    recessions(root)
    by_sex(root)
    labor_force(root)
    hours(root)
    names = countries(cache)
    emp_pop_countries(cache, names)
    unemployment_monthly(cache, names)
    unemployment_annual(root, names)
    college_premium_countries(cache, names)
    manufacturing_countries(cache, names)
    percentile_growth(cache, names)
    top01_countries(cache, names)


if __name__ == "__main__":
    main()
