# Data for Chapter 13: Stabilization Policy and the AS/AD Framework

Read by `notebooks/ch13-stabilization-policy-and-the-as-ad-framework.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch13/`.

## Files copied from the macro102 collect-data output

- `fig13-16.csv`: `date, fed_funds, policy_rule`, quarterly, 1960Q1–2026Q3. `fed_funds` is the effective federal funds rate (FRED `FEDFUNDS`, quarterly mean of monthly values, percent). `policy_rule` is the chapter's rule (equation 13.5) with r̄ = 2, m̄ = 1/2 and π̄ = 2, i = 1 + 1.5π, where π is core PCE inflation (FRED `JCXFE`, 4-quarter percent change); it ends in 2026Q2, one quarter before the fed funds rate. Sources: <https://fred.stlouisfed.org/series/FEDFUNDS>, <https://fred.stlouisfed.org/series/JCXFE>.
- `fig13-17.csv`: `year, output_gap, inflation`, annual, 1960–2025. `output_gap` = 100 (Y/Ȳ − 1) from FRED `GDPC1` and `GDPPOT` (annual means, current vintage); `inflation` is the percent change of the annual-average CPI (`CPIAUCSL`; the unpublished October 2025 value is interpolated). Sources: <https://fred.stlouisfed.org/series/GDPC1>, <https://fred.stlouisfed.org/series/GDPPOT>, <https://fred.stlouisfed.org/series/CPIAUCSL>.
- `fig13-18.csv`: `date, employment_actual, spf_2007q4, …, spf_2009q4`, quarterly, 2007Q3–2010Q4, millions of jobs. `employment_actual` is nonfarm payroll employment (FRED `PAYEMS`, quarterly average); each `spf_…` column is the median forecast path of the Survey of Professional Forecasters made in that quarter (Federal Reserve Bank of Philadelphia, `median_emp_level.xlsx`, EMP1–EMP6), empty outside the path. A fixed historical episode, not extended.
- `fig13-19.csv`: `year, inflation_us, inflation_uk, inflation_euro_area, inflation_japan`, annual CPI inflation in percent, 1960–2025. OECD Data Explorer (`DSD_PRICES@DF_PRICES_ALL`) for the U.S., the U.K. and Japan to 2020; World Bank WDI `FP.CPI.TOTL.ZG` for the euro area (whole span) and Japan from 2021. The U.S. 2025 value uses the 11 published months (October 2025 was never published).
- `fig13-21.csv`: `year, end_year, period, n_years, avg_inflation, sd_inflation`. One row per window of U.K. annual CPI inflation: fourteen 20-year windows 1737–1756 … 1997–2016 and the partial 9-year window 2017–2025. `avg_inflation` is the mean and `sd_inflation` the sample standard deviation (percent). Sources: Bank of England, "A millennium of macroeconomic data for the UK" (v3.1) to 2016, ONS `D7BT` CPI index from 2017.

## Wider files built for the notebook widgets

Both are made by `build_data.py` from the raw downloads that macro102's `/collect-data` saved in `original-scanned-book/ch13-stabilization-policy-and-the-as-ad-framework/data/fig13-16/raw/` and `fig13-17/raw/`. Run it with `python build_data.py [--macro102 PATH]`.

- `taylor_rule.csv`: `date, fed_funds, core_inflation`, quarterly, 1960Q1–2026Q3 (267 rows). `fed_funds` as in `fig13-16.csv`; `core_inflation` is the 4-quarter percent change of the core PCE price index (FRED `JCXFE`), missing in 2026Q3 (not yet published). The notebook computes the policy rule from it with any r̄ and m̄. Validation: 1 + 1.5 × `core_inflation` reproduces `fig13-16.csv`'s `policy_rule` within 0.0001, and `fed_funds` is identical.
- `loops_vintages.csv`: `year, inflation, output_gap, output_gap_2023`, annual, 1960–2025 (66 rows). `inflation` and `output_gap` as in `fig13-17.csv`; `output_gap_2023` is the same output gap computed from the ALFRED vintage of 30 March 2023 of `GDPC1` and `GDPPOT` (the data the textbook used), 1960–2022, empty after 2022. Validation: `inflation` and `output_gap` reproduce `fig13-17.csv` within 0.0001. Known quirk: CBO's later revisions of potential GDP raise the current-vintage output gap by about 1 point after 1985 (2.1 points in 2021), so the textbook's "in 2009 output was more than 5 percent below potential" holds in the 2023 vintage (−5.20) but not in the current one (−4.66). The notebook uses this as a data-revision example.

## Multi-country files (conventions §6b)

Made by `build_data.py` from public downloads, cached in macro102's `.work/ch13/notebook-raw/` (`--refresh` downloads
them again), and from the `fig13-21/raw/` files of collect-data. Every file is tidy and long, one row per country and
period: `iso3, country`, then `date` (first day of the quarter) or `year`, then the values. Country names come from
`countries.csv`. The rows of the textbook's economies are copied from, or checked against, the files above.

- `countries.csv`: `iso3, country, region, oecd`. 218 economies (the World Bank's country list without aggregates,
  plus the euro area `EMU`), short names, the World Bank region simplified to four groups, and OECD membership. The
  same file as in `data/ch12/`.
- `taylor_rule_countries.csv`: `policy_rate` (central bank policy rate, quarterly mean of the end-of-month rates,
  complete quarters) and `core_inflation` (CPI less food and energy, percent change over 4 quarters), quarterly,
  1960Q1–2026Q3, 33 economies (6,901 rows; only economies with both series for 20 quarters or more). Sources: BIS
  `WS_CBPOL` (<https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/M.*?format=csv>) and OECD
  `DSD_PRICES@DF_PRICES_ALL`, key `.Q.N.CPI.PA._TXCP01_NRG.N.GY` (the euro area: `EA20`, the core HICP). The U.S. rows are
  copied from `taylor_rule.csv` (fed funds and core PCE); validation: the BIS/OECD U.S. series differ from them by 0.16
  (policy rate) and 0.62 (core CPI against core PCE inflation) points on average. Known quirks: early euro members
  have a policy rate only until 1998; Japan's core CPI stops in 2021Q2; the European countries' core CPI stops in
  2025Q4; Israel and Mexico (1980s) and Türkiye (1990s, 2020s) have inflation in the tens or hundreds of percent.
- `inflation_annual.csv`: `inflation`, CPI inflation, percent change of the annual average, 1960–2025, 194 economies
  (9,218 rows). World Bank WDI `FP.CPI.TOTL.ZG`
  (<https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json&per_page=20000&date=1960:2025>); the
  rows of the U.S., the U.K., the euro area and Japan are copied from `fig13-19.csv`. Validation: WDI differs from them by
  at most 0.00 (U.S., euro area), 0.07 (U.K.) and 0.16 (Japan) points.
- `output_gaps_oecd.csv`: `output_gap`, output gap in percent of potential GDP, 1985–2025 (projections dropped), 40
  economies (1,444 rows; many start in the 1990s). Source: OECD *Economic Outlook* 119, `OECD.ECO.MAD,DSD_EO@DF_EO,1.5`,
  measure `GAP`, annual. Validation: the OECD U.S. gap correlates 0.80 with the CBO gap of `loops_vintages.csv` and is
  0.22 points higher on average since 1985 (2009: −3.98 against −4.66): two estimates of unobservable potential output.
- `inflation_long_annual.csv`: `inflation`, CPI inflation in percent, annual, 18 economies (2,872 rows). The U.K.,
  1737–2025: the series behind `fig13-21.csv` (Bank of England, *A millennium of macroeconomic data for the UK* v3.1, to
  2016; ONS `D7BT` after), recomputing the 20-year windows from it reproduces `fig13-21.csv` within 0.0002. The other 17
  countries, 1871–2025 (Ireland from 1923): Jordà–Schularick–Taylor Macrohistory Database R6, variable `cpi`
  (<https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.dta>), to 2020, then WDI `FP.CPI.TOTL.ZG`
  (the U.S. 2025 value from `fig13-19.csv`). Validation: JST and WDI differ by 0.09 points on average over 1990–2020;
  JST's U.K. series differs from the BoE series by 0.22 points on average over 1871–2016. Known quirk: Germany's 1923
  inflation is about 10^11 percent (prices rose about a billion-fold), so its 1917–1936 window average is in the billions.
