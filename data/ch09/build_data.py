"""Build the wider data files used by the Chapter 9 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch09-an-introduction-to-the-short-run/data/):
  fig9-3/raw/fred_USREC.csv      NBER recession indicator, monthly (1 = recession month)
  fig9-4/raw/fred_PAYEMS.csv     total nonfarm payroll employment, thousands, monthly, SA (BLS)
  fig9-5/raw/fred_CPIAUCSL.csv   CPI-U all items, index 1982-84 = 100, monthly, SA (BLS)
Outputs (next to this script):
  recessions.csv           peak, trough                NBER peaks and troughs whose trough is in 1960 or later
  payroll_employment.csv   date, payroll_millions      payroll employment, millions, monthly, 1979-12 on
  cpi_monthly.csv          date, cpi, inflation_12m    CPI and 12-month inflation (percent), monthly, 1959-01 on

Multi-country files (conventions.md 6b), downloaded from public sources with requests' default User-Agent and
cached in macro102's .work/ch09/notebook-raw/ (delete a cached file to download it again):
  short_run_panel.csv      iso3, country, year, gdp_real, gdp_potential, output_gap, inflation, inflation_source,
                           unemployment, unemployment_trend     OECD Economic Outlook 119 + World Bank CPI inflation
                           (read from ../ch08/inflation_panel.csv), ~50 economies, annual
  employment_quarterly.csv iso3, country, date, employment, emp_change_pct      OECD Economic Outlook 119, quarterly
"""
import argparse
import os
import time

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch09-an-introduction-to-the-short-run/data/"


def fred(root, path):
    """One FRED series as a Series indexed by month (blank cells become NaN)."""
    df = pd.read_csv(os.path.join(root, path), parse_dates=["observation_date"])
    return df.set_index("observation_date").iloc[:, 0]


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = fred(root, "fig9-3/raw/fred_USREC.csv")
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    for col in ["peak", "trough"]:
        out[col] = out[col].dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def payroll(root):
    """Payroll employment in millions; its monthly percent change must reproduce fig9-4.csv."""
    emp = fred(root, "fig9-4/raw/fred_PAYEMS.csv")
    emp = emp[emp.index >= "1979-12-01"] / 1000
    out = pd.DataFrame({"payroll_millions": emp.round(3)})
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "payroll_employment.csv"), date_format="%Y-%m-%d")
    change = (100 * (emp / emp.shift(1) - 1)).dropna()
    ref = pd.read_csv(os.path.join(HERE, "fig9-4.csv"), parse_dates=["date"]).set_index("date").emp_change_pct
    worst = (change.reindex(ref.index) - ref).abs().max()
    print(f"payroll_employment.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}; "
          f"largest difference of the % change from fig9-4.csv: {worst:.4f}")


def cpi(root):
    """Monthly CPI and 12-month inflation; October 2025 stays missing (not collected in the shutdown)."""
    index = fred(root, "fig9-5/raw/fred_CPIAUCSL.csv")
    infl = 100 * (index / index.shift(12) - 1)
    out = pd.DataFrame({"cpi": index, "inflation_12m": infl.round(3)})
    out = out[out.index >= "1959-01-01"]
    out.index.name = "date"
    out.to_csv(os.path.join(HERE, "cpi_monthly.csv"), date_format="%Y-%m-%d")
    # validation: the calendar-year mean of the monthly index (complete years) reproduces fig9-5.csv
    filled = index.interpolate()                       # as collect-data does for October 2025
    annual = filled.groupby(filled.index.year).agg(["mean", "count"])
    annual = annual[annual["count"] == 12]["mean"]
    yearly = 100 * (annual / annual.shift(1) - 1)
    ref = pd.read_csv(os.path.join(HERE, "fig9-5.csv")).set_index("year").inflation_cpi
    worst = (yearly.reindex(ref.index) - ref).abs().max()
    print(f"cpi_monthly.csv: {len(out)} months, {out.index.min():%Y-%m} to {out.index.max():%Y-%m}, "
          f"{int(out.cpi.isna().sum())} missing month(s); largest difference of annual inflation from "
          f"fig9-5.csv: {worst:.4f}")


LAST = 2025                                     # last complete year: Economic Outlook 119 projects 2026-2027
EO = "https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/"
EO_ANNUAL = EO + ".GDPV+GDPVTR+GDPVD+GAP+UNR+CPI_YTYPCT+CPIH_YTYPCT.A?startPeriod=1960&format=csvfilewithlabels"
EO_QUARTERLY = EO + ".ET.Q?startPeriod=1960&format=csvfilewithlabels"
AGGREGATES = {"OECD", "EA17", "W", "WXOECD", "DAE", "OIL_SAU_O", "W_O"}
NAMES = {"Türkiye": "Turkey", "China (People’s Republic of)": "China", "Korea": "South Korea"}


def download(url, name, raw):
    """Download url once into the cache folder raw/name and return the local path."""
    path = os.path.join(raw, name)
    if not os.path.exists(path):
        os.makedirs(raw, exist_ok=True)
        for attempt in range(6):                    # the OECD API answers 429 when called too often
            r = requests.get(url, timeout=300)
            if r.status_code != 429:
                break
            time.sleep(60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def hp_trend(y, lam=100.0):
    """Hodrick-Prescott trend of an annual series (lambda = 100): solve (I + lam D'D) trend = y."""
    n = len(y)
    D = np.zeros((n - 2, n))
    for i in range(n - 2):
        D[i, i:i + 3] = [1.0, -2.0, 1.0]
    return np.linalg.solve(np.eye(n) + lam * D.T @ D, y)


def eo_names(df):
    names = df[["REF_AREA", "Reference area"]].drop_duplicates().set_index("REF_AREA")["Reference area"]
    return names.replace(NAMES)


def short_run_panel(raw):
    """Annual real GDP, potential output, output gap, CPI inflation and unemployment, OECD + emerging economies."""
    eo = pd.read_csv(download(EO_ANNUAL, "oecd_eo119_annual.csv", raw))
    eo = eo[~eo.REF_AREA.isin(AGGREGATES) & (eo.TIME_PERIOD <= LAST)]
    names = eo_names(eo)
    w = eo.pivot_table(index=["REF_AREA", "TIME_PERIOD"], columns="MEASURE", values="OBS_VALUE")
    w.index.names = ["iso3", "year"]
    ch08 = pd.read_csv(os.path.join(HERE, "..", "ch08", "inflation_panel.csv")).set_index(["iso3", "year"])
    years = ch08.index[ch08.index.get_level_values("iso3").isin(names.index)]
    w = w.reindex(w.index.union(years))             # also the years with inflation but no EO data (e.g. Germany < 1991)
    out = pd.DataFrame(index=w.index)
    out["gdp_real"] = w.GDPVD / 1e12                           # trillions of 2021 PPP dollars
    out["gdp_potential"] = out.gdp_real * w.GDPVTR / w.GDPV     # same units: potential / actual from the EO
    out.loc["NOR", "gdp_potential"] = np.nan                    # Norway's potential and gap are for mainland Norway
    out["output_gap"] = w.GAP
    out["unemployment"] = w.UNR
    # inflation: the CPI inflation panel of Chapter 8 (World Bank WDI, gaps filled from the World Bank's Global
    # Inflation Database), remaining gaps filled with the EO's headline (or harmonised) CPI inflation
    wb = ch08.inflation.reindex(out.index)
    eo_cpi = w.CPI_YTYPCT.fillna(w.CPIH_YTYPCT)
    out["inflation"] = wb.fillna(eo_cpi)
    source = ch08.source.reindex(out.index)
    out["inflation_source"] = np.where(wb.notna(), source, np.where(eo_cpi.notna(), "OECD EO", ""))
    trend = []
    for iso, u in out.unemployment.dropna().groupby(level="iso3"):
        trend.append(pd.Series(hp_trend(u.values), index=u.index))
    out["unemployment_trend"] = pd.concat(trend)
    out = out.reset_index()
    out = out.dropna(subset=["gdp_real", "output_gap", "inflation", "unemployment"], how="all")
    out.insert(1, "country", out.iso3.map(names))
    cols = ["gdp_real", "gdp_potential"]
    out[cols] = out[cols].round(5)
    cols = ["output_gap", "inflation", "unemployment", "unemployment_trend"]
    out[cols] = out[cols].round(3)
    out = out.sort_values(["country", "year"])
    out.to_csv(os.path.join(HERE, "short_run_panel.csv"), index=False)
    print(f"short_run_panel.csv: {len(out)} rows, {out.iso3.nunique()} economies, {out.year.min()}-{out.year.max()}; "
          f"output gap for {out.dropna(subset=['output_gap']).iso3.nunique()} economies; "
          f"inflation sources {out.inflation_source.value_counts().to_dict()}")
    validate_us(out)


def validate_us(out):
    """Compare the OECD's U.S. rows with the textbook-figure files (CBO gap, BLS unemployment and CPI)."""
    us = out[out.iso3 == "USA"].set_index("year")
    cbo = pd.read_csv(os.path.join(HERE, "fig9-3.csv"), parse_dates=["date"])
    cbo = cbo.groupby(cbo.date.dt.year).short_run_output.mean()
    both = pd.concat([us.output_gap, cbo], axis=1).dropna()
    print(f"  U.S. output gap, OECD vs CBO (fig9-3), {both.index.min()}-{both.index.max()}: correlation "
          f"{both.corr().iloc[0, 1]:.2f}, mean difference {(both.iloc[:, 0] - both.iloc[:, 1]).mean():+.2f} points")
    okun = pd.read_csv(os.path.join(HERE, "fig9-8.csv")).set_index("year")
    print(f"  U.S. unemployment vs fig9-8: largest difference {(us.unemployment - okun.unrate).abs().max():.3f}")
    infl = pd.read_csv(os.path.join(HERE, "fig9-5.csv")).set_index("year").inflation_cpi
    print(f"  U.S. inflation (WDI) vs fig9-5: largest difference {(us.inflation - infl).abs().max():.3f}")
    cyc = us.unemployment - us.unemployment_trend
    slope_hp = np.polyfit(*pd.concat([cbo, cyc], axis=1).dropna().values.T, 1)[0]
    print(f"  Okun slope with the CBO gap and HP-trend unemployment: {slope_hp:.2f} (fig9-8, CBO natural rate: -0.62)")


def employment_quarterly(raw):
    """Quarterly employment (labour force survey basis) and its percent change from the previous quarter."""
    eo = pd.read_csv(download(EO_QUARTERLY, "oecd_eo119_ET_quarterly.csv", raw))
    eo = eo[~eo.REF_AREA.isin(AGGREGATES)]
    names = eo_names(eo)
    eo["date"] = pd.PeriodIndex(eo.TIME_PERIOD.str.replace("-", ""), freq="Q").start_time
    eo = eo[eo.date < f"{LAST + 1}-01-01"].sort_values(["REF_AREA", "date"])
    out = pd.DataFrame({"iso3": eo.REF_AREA, "country": eo.REF_AREA.map(names), "date": eo.date,
                        "employment": eo.OBS_VALUE / 1e6})
    out["emp_change_pct"] = 100 * out.groupby("iso3").employment.pct_change()
    out = out.dropna(subset=["emp_change_pct"]).round({"employment": 4, "emp_change_pct": 3})
    out = out.sort_values(["country", "date"])
    out.to_csv(os.path.join(HERE, "employment_quarterly.csv"), index=False, date_format="%Y-%m-%d")
    us = out[out.iso3 == "USA"].set_index("date").emp_change_pct
    pay = pd.read_csv(os.path.join(HERE, "payroll_employment.csv"), parse_dates=["date"]).set_index("date")
    pay = pay.payroll_millions.resample("QS").mean().pct_change() * 100
    both = pd.concat([us, pay], axis=1).dropna()
    print(f"employment_quarterly.csv: {len(out)} rows, {out.iso3.nunique()} economies, "
          f"{out.date.min():%Y-%m} to {out.date.max():%Y-%m}; U.S. vs payroll jobs (quarterly means): correlation "
          f"{both.corr().iloc[0, 1]:.2f}, 2020Q2 {us['2020-04-01']:.1f}% vs {pay['2020-04-01']:.1f}%")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    raw = os.path.join(args.macro102, ".work", "ch09", "notebook-raw")
    recessions(root)
    payroll(root)
    cpi(root)
    short_run_panel(raw)
    employment_quarterly(raw)


if __name__ == "__main__":
    main()
