"""Build the wider data files used by the Chapter 14 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch14-financial-crises-and-the-short-run-model/data/):
  fig14-6/raw/fred_USREC.csv          NBER recession indicator, monthly (1 = recession month)
  table14-1/raw/fred_<ID>.csv         Federal Reserve H.4.1, weekly Wednesday levels, millions of dollars:
                                      WTFSRFL (total factors supplying reserve funds), WSHOTSL (Treasuries),
                                      WSHOMCB (mortgage-backed securities), WCICL (currency in circulation),
                                      WRBWFRBL (reserve balances)
Outputs (next to this script):
  recessions.csv              peak, trough    NBER recessions that start in 1953 or later (monthly dates)
  fed_balance_sheet.csv       month, total, treasuries, mbs, currency, reserves
                              monthly averages of the weekly levels, billions of dollars, complete months
                              only (at least 4 Wednesdays), 2003-01 to the latest complete month
Check: May 2007, May 2015 and the latest month reproduce table14-1/data.csv (copied from collect-data).

Multi-country downloads (conventions §6b), cached in ../macro102/.work/ch14/notebook-raw/ (delete a file to refresh it):
  World Bank WDI API: country list (names, regions) and FM.LBL.BMNY.ZG (broad money growth)
  OECD SDMX: Economic Outlook (DSD_EO@DF_EO: GAP, GDPV, GDPVTR, PCORE_YTYPCT, CPI_YTYPCT; CPIH_YTYPCT separately)
  BIS SDMX:  WS_CBPOL (central bank policy rates), WS_SPP (real residential property prices),
             WS_CBTA (central bank total assets, percent of GDP)
  ECB SDMX:  BSI.M.U2.Y.V.M30.X.I.U2.2300.Z01.A (euro area M3, annual growth rate) and
             ICP.M.U2.N.XEF000.4.ANR (euro area HICP excluding energy, food, alcohol and tobacco, annual rate)
  FRED:      IRLTLT01{CC}M156N (OECD 10-year government bond yields, monthly) for Germany and the euro area members;
             GDP (U.S. nominal GDP, to validate the BIS central bank assets)
  Penn World Table 11.0 (pwt110.dta, DataverseNL doi:10.34894/FABVLR; collect-data's bulk copy is used if present)
More outputs:
  sovereign_spreads.csv     iso3, country, date, yield_10y, spread_germany       euro area members, monthly, from euro entry
  taylor_world.csv          iso3, country, year, policy_rate, core_inflation, headline_inflation, output_gap
  potential_world.csv       iso3, country, year, gdp, potential_gdp               index, actual GDP in 2007 = 100
  money_world.csv           iso3, country, region, year, broad_money_growth       December over December, percent
  house_prices_world.csv    iso3, country, region, date, real_price               BIS real index, 2010 = 100, quarterly
  cb_assets_world.csv       iso3, country, date, assets_gdp                       central bank assets, percent of GDP, quarterly
  tfp_world.csv             iso3, country, region, year, tfp                      PWT rtfpna, 2017 = 1
"""
import argparse
import io
import json
import os
import shutil
import time

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch14-financial-crises-and-the-short-run-model/data/"
H41 = {"WTFSRFL": "total", "WSHOTSL": "treasuries", "WSHOMCB": "mbs",
       "WCICL": "currency", "WRBWFRBL": "reserves"}


def recessions(root):
    """(peak, trough) of every NBER recession since 1953: the month before the first recession month, and the last one."""
    raw = pd.read_csv(os.path.join(root, "fig14-6/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    flag = raw.set_index("observation_date").USREC
    starts = flag.index[(flag == 1) & (flag.shift(1, fill_value=0) == 0)]
    ends = flag.index[(flag == 1) & (flag.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.peak >= "1953-01-01"].reset_index(drop=True)
    for col in out.columns:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def balance_sheet(root):
    """Monthly averages of the H.4.1 weekly levels, in billions of dollars (complete months only)."""
    frames = []
    for sid, name in H41.items():
        raw = pd.read_csv(os.path.join(root, f"table14-1/raw/fred_{sid}.csv"), parse_dates=["observation_date"])
        frames.append(raw.set_index("observation_date")[sid].rename(name) / 1000)
    weekly = pd.concat(frames, axis=1)
    m = weekly.resample("MS").agg(["mean", "count"])
    full = (m.xs("count", axis=1, level=1) >= 4).all(axis=1)
    out = m.xs("mean", axis=1, level=1)[full].round(1)
    out.index = out.index.strftime("%Y-%m")
    out.index.name = "month"
    out.to_csv(os.path.join(HERE, "fed_balance_sheet.csv"))
    print(f"fed_balance_sheet.csv: {len(out)} months, {out.index[0]} to {out.index[-1]}")
    return out


def validate(out, root):
    """May 2007, May 2015 and the latest month must equal table14-1/data.csv within rounding."""
    book = pd.read_csv(os.path.join(root, "table14-1/data.csv")).set_index("item")
    latest = [c for c in book.columns if c.startswith("billions_latest_")][0]
    months = {"billions_book_2007": "2007-05", "billions_book_2015": "2015-05", latest: out.index[-1]}
    for col, month in months.items():
        row = out.loc[month]
        ours = {"Assets: U.S. Treasuries": row.treasuries, "Assets: Mortgage-backed securities": row.mbs,
                "Total assets": row.total, "Liabilities: Currency": row.currency,
                "Liabilities: Reserves": row.reserves}
        for item, value in ours.items():
            if abs(value - book.loc[item, col]) > 1.0:
                raise SystemExit(f"{month} {item}: {value} != {book.loc[item, col]} in table14-1/data.csv")
    print(f"validated: {', '.join(months.values())} reproduce table14-1/data.csv (within 1 billion)")


# ---- multi-country files (conventions §6b) -------------------------------------------------------------------
LAST = 2025                       # last complete year: drops the OECD Economic Outlook projections for 2026-2027
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
# euro entry: the spread over Germany measures default risk only once both bonds are in euros
EURO_ENTRY = {"AUT": 1999, "BEL": 1999, "FIN": 1999, "FRA": 1999, "IRL": 1999, "ITA": 1999, "LUX": 1999,
              "NLD": 1999, "PRT": 1999, "ESP": 1999, "GRC": 2001, "SVN": 2007, "SVK": 2009, "EST": 2011,
              "LVA": 2014, "LTU": 2015, "HRV": 2023}
# Taylor rule: central banks with their own policy rate and an inflation target of 2 to 2.5 percent
TAYLOR = ["USA", "EMU", "GBR", "JPN", "CAN", "AUS", "NZL", "SWE", "NOR", "CHE", "KOR", "ISR", "CZE", "POL"]
EURO_NCB = ["AT", "BE", "DE", "EE", "ES", "FI", "FR", "GR", "HR", "IE", "IT", "LT", "LU", "LV", "NL", "PT", "SI",
            "SK", "CY", "MT"]       # national central banks of the Eurosystem: the euro area (XM) stands for them


def get(cache, url, file, params=None):
    """Download url into the cache folder once (requests' default User-Agent), return the local path."""
    path = os.path.join(cache, file)
    if os.path.exists(path):
        return path
    for k in range(6):
        try:
            r = requests.get(url, params=params, timeout=300)
            if r.status_code == 200:
                open(path, "wb").write(r.content)
                return path
            if r.status_code == 404:
                return None                   # no such series (e.g. Estonia has no 10-year bond yield on FRED)
            print(f"  {url[:70]}...: HTTP {r.status_code}, retrying")
        except requests.RequestException:
            pass
        time.sleep(60 * (k + 1))          # the OECD API answers 429 (too many requests) for a few minutes
    raise RuntimeError(f"download failed: {url}")


def country_table(cache):
    """iso3 -> (iso2, readable name, World Bank region) for every economy, plus Taiwan and the euro area."""
    p = get(cache, "https://api.worldbank.org/v2/country", "wdi_countries.json", {"format": "json", "per_page": 400})
    rows = [r for r in json.load(open(p))[1] if r["region"]["value"].strip() != "Aggregates"]
    out = pd.DataFrame({"iso3": [r["id"] for r in rows], "iso2": [r["iso2Code"] for r in rows],
                        "country": [RENAME.get(r["name"], r["name"]) for r in rows],
                        "region": [REGIONS.get(r["region"]["value"].strip(), r["region"]["value"].strip())
                                   for r in rows]})
    extra = pd.DataFrame([("TWN", "TW", "Taiwan", "East Asia & Pacific"),
                          ("EMU", "XM", "Euro area", "Europe & Central Asia")], columns=out.columns)
    return pd.concat([out, extra], ignore_index=True).set_index("iso3")


def tidy(df, names, cols, region=False):
    """Attach readable names (and the region), keep known economies, sort; columns iso3, country, [region,] cols."""
    df = df[df.iso3.isin(names.index)].copy()
    df.insert(1, "country", df.iso3.map(names.country))
    first = ["iso3", "country"]
    if region:
        df.insert(2, "region", df.iso3.map(names.region))
        first.append("region")
    return df[first + cols].sort_values(["country", cols[0]]).reset_index(drop=True)


def save(df, name):
    path = os.path.join(HERE, name)
    df.to_csv(path, index=False)
    size = os.path.getsize(path) / 1e6
    if size >= 1:
        raise SystemExit(f"{name} is {size:.2f} MB (must stay under 1 MB)")
    when = "date" if "date" in df.columns else "year"
    print(f"{name}: {len(df)} rows, {df.iso3.nunique()} economies, {df[when].min()} to {df[when].max()}, "
          f"{size * 1000:.0f} kB")


def oecd_eo(cache):
    """OECD Economic Outlook, annual: iso3, year and one column per measure (EA17 becomes EMU)."""
    p = get(cache, "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/"
            ".GAP+GDPV+GDPVTR+PCORE_YTYPCT+CPI_YTYPCT.A", "oecd_eo.csv",
            {"startPeriod": "1990", "format": "csvfilewithlabels"})
    d = pd.read_csv(p, usecols=["REF_AREA", "MEASURE", "TIME_PERIOD", "OBS_VALUE"])
    d["REF_AREA"] = d.REF_AREA.replace({"EA17": "EMU"})
    out = d.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="MEASURE", values="OBS_VALUE").reset_index()
    out = out.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year"})
    return out[out.year <= LAST]


def bis(cache, flow, key, file, start):
    """One BIS SDMX dataflow as a CSV table (REF_AREA in ISO2, TIME_PERIOD, OBS_VALUE, ...)."""
    p = get(cache, f"https://stats.bis.org/api/v2/data/dataflow/BIS/{flow}/1.0/{key}", file,
            {"format": "csv", "startPeriod": start})
    return pd.read_csv(p, low_memory=False)


def iso3_of(names):
    """ISO2 -> ISO3 lookup (XM, the euro area, becomes EMU)."""
    return pd.Series(names.index, index=names.iso2)


def sovereign_spreads(cache, names):
    """Figure 1, euro-area analogue: 10-year government bond yields and their spread over Germany."""
    frames = []
    for iso3 in ["DEU"] + list(EURO_ENTRY):
        iso2 = names.iso2[iso3]
        p = get(cache, f"https://fred.stlouisfed.org/graph/fredgraph.csv?id=IRLTLT01{iso2}M156N", f"fred_IRLTLT01{iso2}M156N.csv")
        if p is None:
            print(f"  no 10-year yield on FRED for {iso3}")
            continue
        x = pd.read_csv(p).dropna()
        frames.append(pd.DataFrame({"iso3": iso3, "date": x.iloc[:, 0].str[:7], "yield_10y": x.iloc[:, 1]}))
    d = pd.concat(frames)
    germany = d[d.iso3 == "DEU"].set_index("date").yield_10y
    d = d[d.iso3.isin(EURO_ENTRY)].copy()
    d = d[d.date.str[:4].astype(int) >= d.iso3.map(EURO_ENTRY)]
    d["spread_germany"] = (d.yield_10y - d.date.map(germany)).round(3)
    d["yield_10y"] = d.yield_10y.round(3)
    d["date"] = d.date + "-01"
    out = tidy(d.dropna(), names, ["date", "yield_10y", "spread_germany"])
    save(out, "sovereign_spreads.csv")
    return out


def taylor_world(cache, names, eo):
    """Figure 4 for other central banks, annual: policy rate (BIS), core and headline inflation, output gap (OECD)."""
    pol = bis(cache, "WS_CBPOL", "M", "bis_cbpol.csv", "1995-01")
    pol["iso3"] = pol.REF_AREA.map(iso3_of(names))
    pol["year"] = pol.TIME_PERIOD.str[:4].astype(int)
    rate = pol.groupby(["iso3", "year"]).OBS_VALUE.agg(["mean", "count"]).reset_index()
    rate = rate[rate["count"] == 12].rename(columns={"mean": "policy_rate"})      # complete years only
    d = eo.rename(columns={"PCORE_YTYPCT": "core_inflation", "CPI_YTYPCT": "headline_inflation", "GAP": "output_gap"})
    # EU members report harmonised inflation (CPIH) instead of CPI: use it where CPI is missing (euro area, U.K.)
    p = get(cache, "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.CPIH_YTYPCT.A", "oecd_eo_cpih.csv",
            {"startPeriod": "1990", "format": "csvfilewithlabels"})
    h = pd.read_csv(p, usecols=["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]).replace({"REF_AREA": {"EA17": "EMU"}})
    h = h.rename(columns={"REF_AREA": "iso3", "TIME_PERIOD": "year", "OBS_VALUE": "cpih"})
    d = d.merge(h, on=["iso3", "year"], how="left")
    d["headline_inflation"] = d.headline_inflation.fillna(d.cpih)
    # the OECD has no core inflation for the euro area: the ECB's HICP excluding energy, food, alcohol and tobacco
    p = get(cache, "https://data-api.ecb.europa.eu/service/data/ICP/M.U2.N.XEF000.4.ANR", "ecb_hicp_core.csv",
            {"format": "csvdata"})
    core = pd.read_csv(p, usecols=["TIME_PERIOD", "OBS_VALUE"])
    core["year"] = core.TIME_PERIOD.str[:4].astype(int)
    core = core.groupby("year").OBS_VALUE.agg(["mean", "count"])
    core = core[core["count"] == 12]["mean"]
    ea = d.iso3 == "EMU"
    d.loc[ea, "core_inflation"] = d.loc[ea, "core_inflation"].fillna(d.loc[ea, "year"].map(core))
    d = d[["iso3", "year", "core_inflation", "headline_inflation", "output_gap"]].merge(
        rate[["iso3", "year", "policy_rate"]], on=["iso3", "year"])
    d = d[d.iso3.isin(TAYLOR) & (d.year >= 1999)].dropna(subset=["policy_rate", "output_gap"])
    cols = ["year", "policy_rate", "core_inflation", "headline_inflation", "output_gap"]
    out = tidy(d.round(3), names, cols)
    save(out, "taylor_world.csv")
    return out


def potential_world(names, eo):
    """Figure 5 for OECD countries: real GDP and the OECD's potential output, actual GDP in 2007 = 100."""
    d = eo.dropna(subset=["GDPV", "GDPVTR"]).copy()
    base = d[d.year == 2007].set_index("iso3").GDPV
    d = d[d.iso3.isin(base.index)]
    d["gdp"] = (100 * d.GDPV / d.iso3.map(base)).round(3)
    d["potential_gdp"] = (100 * d.GDPVTR / d.iso3.map(base)).round(3)
    out = tidy(d, names, ["year", "gdp", "potential_gdp"])
    save(out, "potential_world.csv")
    return out


def money_world(cache, names):
    """Figure 6 for other countries: broad money growth, end of year over end of year (WDI; ECB M3 for the euro area)."""
    p = get(cache, "https://api.worldbank.org/v2/country/all/indicator/FM.LBL.BMNY.ZG", "wdi_FM.LBL.BMNY.ZG.json",
            {"format": "json", "per_page": 20000})
    rows = json.load(open(p))[1]
    d = pd.DataFrame({"iso3": [r["countryiso3code"] for r in rows], "year": [int(r["date"]) for r in rows],
                      "broad_money_growth": [r["value"] for r in rows]}).dropna()
    p = get(cache, "https://data-api.ecb.europa.eu/service/data/BSI/M.U2.Y.V.M30.X.I.U2.2300.Z01.A", "ecb_m3.csv",
            {"format": "csvdata"})
    m3 = pd.read_csv(p, usecols=["TIME_PERIOD", "OBS_VALUE"])
    m3 = m3[m3.TIME_PERIOD.str.endswith("-12")]                                    # December over December
    ea = pd.DataFrame({"iso3": "EMU", "year": m3.TIME_PERIOD.str[:4].astype(int), "broad_money_growth": m3.OBS_VALUE})
    d = pd.concat([d[d.iso3 != "EMU"], ea])
    d = d[(d.year >= 1990) & (d.year <= LAST)]
    d["broad_money_growth"] = d.broad_money_growth.round(2)
    out = tidy(d, names, ["year", "broad_money_growth"], region=True)
    save(out, "money_world.csv")
    return out


def house_prices_world(cache, names):
    """Figure 8 for other countries: BIS real residential property prices, 2010 = 100, quarterly."""
    d = bis(cache, "WS_SPP", "Q..R.628", "bis_spp_real.csv", "1970-Q1")
    d["iso3"] = d.REF_AREA.map(iso3_of(names))
    d["date"] = pd.PeriodIndex(d.TIME_PERIOD, freq="Q").start_time.strftime("%Y-%m-%d")
    d["real_price"] = d.OBS_VALUE.round(2)
    out = tidy(d.dropna(subset=["iso3", "real_price"]), names, ["date", "real_price"], region=True)
    save(out, "house_prices_world.csv")
    return out


def cb_assets_world(cache, names):
    """Figure 9 for other central banks: total assets in percent of GDP (BIS, break-adjusted), quarterly."""
    d = bis(cache, "WS_CBTA", "Q..B.XDF_R_B1GQ..B", "bis_cbta_gdp.csv", "2000-Q1")
    d = d[~d.REF_AREA.isin(EURO_NCB)].copy()
    d["iso3"] = d.REF_AREA.map(iso3_of(names))
    d["date"] = pd.PeriodIndex(d.TIME_PERIOD, freq="Q").start_time.strftime("%Y-%m-%d")
    d["assets_gdp"] = d.OBS_VALUE.round(2)
    out = tidy(d.dropna(subset=["iso3", "assets_gdp"]), names, ["date", "assets_gdp"])
    save(out, "cb_assets_world.csv")
    return out


def pwt(macro102, cache):
    """Penn World Table 11.0 (collect-data's bulk copy if present, else DataverseNL)."""
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
    return pd.read_stata(path, columns=["countrycode", "year", "rtfpna", "rgdpna"])


def tfp_world(macro102, cache, names):
    """Figure 11 for other countries: TFP at constant national prices (PWT rtfpna, 2017 = 1)."""
    d = pwt(macro102, cache).rename(columns={"countrycode": "iso3", "rtfpna": "tfp"}).dropna(subset=["tfp"])
    d["year"] = d.year.astype(int)
    d["tfp"] = d.tfp.round(4)
    out = tidy(d, names, ["year", "tfp"], region=True)
    save(out, "tfp_world.csv")
    return out


def growth(x, start, end):
    """Average annual log growth in percent of a series indexed by year."""
    return 100 * np.log(x[end] / x[start]) / (end - start)


def validate_world(cache, spreads, taylor, potential, money, homes, assets, tfp):
    """Check the U.S. (and German) rows of the new files against the textbook-figure CSVs and FRED."""
    book = pd.read_csv(os.path.join(HERE, "fig14-4.csv"), parse_dates=["date"])
    year = book.groupby(book.date.dt.year).mean(numeric_only=True)
    us = taylor[taylor.iso3 == "USA"].set_index("year")
    both = us.join(year, rsuffix="_book").dropna(subset=["fed_funds"])
    print(f"  taylor_world USA {len(both)} years: policy rate - fed funds (annual means) max |gap| "
          f"{(both.policy_rate - both.fed_funds).abs().max():.2f}; OECD gap - CBO gap: mean "
          f"{(both.output_gap - both.short_run_output).mean():+.2f}, corr {both.output_gap.corr(both.short_run_output):.2f}; "
          f"core inflation corr {both.core_inflation.corr(both.core_pce_inflation):.2f}")
    if (both.policy_rate - both.fed_funds).abs().max() > 0.5:
        raise SystemExit("BIS U.S. policy rate differs from the fed funds rate of fig14-4.csv")
    cbo = pd.read_csv(os.path.join(HERE, "fig14-5.csv"), parse_dates=["date"])
    cbo = cbo.groupby(cbo.date.dt.year).mean(numeric_only=True)
    oecd = potential[potential.iso3 == "USA"].set_index("year")
    print(f"  potential_world USA: potential growth 2007-2019 OECD {growth(oecd.potential_gdp, 2007, 2019):.2f}%, "
          f"CBO {growth(cbo.gdp_potential_latest, 2007, 2019):.2f}%; actual GDP growth OECD "
          f"{growth(oecd.gdp, 2007, 2019):.2f}%, fig14-5 {growth(cbo.gdp_actual, 2007, 2019):.2f}%")
    m2 = pd.read_csv(os.path.join(HERE, "fig14-6.csv"), parse_dates=["date"])
    usm = money[money.iso3 == "USA"].set_index("year").broad_money_growth
    print(f"  money_world USA vs fig14-6 M2 (December 12-month growth), 1991-{usm.index.max()}: corr "
          f"{usm.corr(m2[m2.date.dt.month == 12].set_index(m2.date.dt.year[m2.date.dt.month == 12]).m2):.2f}")
    shiller = pd.read_csv(os.path.join(HERE, "fig14-8.csv"), parse_dates=["date"])
    bis_us = homes[homes.iso3 == "USA"].copy()
    bis_us["date"] = pd.to_datetime(bis_us.date)
    for name, x, col in [("BIS", bis_us, "real_price"), ("Shiller", shiller, "real_home_price_1953_100")]:
        w = x[(x.date >= "2000-01-01") & (x.date <= "2015-12-31")]
        top = w.loc[w[col].idxmax()]
        low = w[w.date >= top.date][col].min()
        print(f"  house_prices_world USA check, {name}: peak {top.date:%Y-%m}, fall to the trough {100 * (1 - low / top[col]):.1f}%")
    gdp = pd.read_csv(get(cache, "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GDP", "fred_GDP.csv"),
                      parse_dates=["observation_date"]).set_index("observation_date").GDP
    walcl = pd.read_csv(os.path.join(HERE, "fig14-9.csv"), parse_dates=["date"]).set_index("date").total_assets
    for q in ["2007-10-01", "2014-10-01", "2021-10-01"]:
        ours = walcl[q:pd.Timestamp(q) + pd.DateOffset(months=3)].iloc[-1] / gdp[q] * 100
        theirs = assets[(assets.iso3 == "USA") & (assets.date == q)].assets_gdp.iloc[0]
        print(f"  cb_assets_world USA {q[:7]}: BIS {theirs:.1f}% of GDP, WALCL / GDP {ours:.1f}%")
    bls = pd.read_csv(os.path.join(HERE, "fig14-11.csv")).set_index("year").tfp_private_business
    p = tfp[tfp.iso3 == "USA"].set_index("year").tfp
    print(f"  tfp_world USA growth 1995-2004 / 2004-2019: PWT {growth(p, 1995, 2004):.2f} / {growth(p, 2004, 2019):.2f}%, "
          f"BLS private business {growth(bls, 1995, 2004):.2f} / {growth(bls, 2004, 2019):.2f}%")
    print(f"  sovereign_spreads: largest spread {spreads.loc[spreads.spread_germany.idxmax()].to_dict()}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    recessions(root)
    validate(balance_sheet(root), root)
    cache = os.path.join(args.macro102, ".work", "ch14", "notebook-raw")
    os.makedirs(cache, exist_ok=True)
    names = country_table(cache)
    spreads, money = sovereign_spreads(cache, names), money_world(cache, names)
    homes, assets = house_prices_world(cache, names), cb_assets_world(cache, names)
    tfp = tfp_world(args.macro102, cache, names)
    eo = oecd_eo(cache)                     # last: the OECD API is often rate-limited (HTTP 429)
    taylor, potential = taylor_world(cache, names, eo), potential_world(names, eo)
    validate_world(cache, spreads, taylor, potential, money, homes, assets, tfp)


if __name__ == "__main__":
    main()
