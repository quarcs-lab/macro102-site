# Data for Chapter 12: Monetary Policy and the Phillips Curve

Read by `notebooks/ch12-monetary-policy-and-the-phillips-curve.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch12/`.

## Files copied from the macro102 collect-data output

- `fig12-2.csv`: `date, fedfunds`. Effective federal funds rate, percent, monthly average of daily rates, not seasonally adjusted, 1960-01 to 2026-09 (801 months; Board of Governors H.15 via FRED `FEDFUNDS`).
- `fig12-6.csv`: `date, yield_1m, yield_3m, yield_6m, yield_12m, yield_24m, yield_36m, yield_60m, yield_84m, yield_120m, yield_240m, yield_360m`. U.S. Treasury par yields, percent, at 11 maturities (the number in each column name is the maturity in months), on three days: 2022-01-03 and 2023-04-03 (the textbook's two curves, reproduced exactly) and 2026-10-15 (the latest day).
  - Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates.
- `fig12-9.csv`: `year, inflation_cpi`. Annual U.S. CPI inflation, percent: the change in the calendar-year average of the monthly CPI-U (`CPIAUCSL`, BLS via FRED), 1960 to 2025.
  - Known quirk: the October 2025 CPI was never published (federal government shutdown), so the 2025 average uses 11 months.
- `fig12-14.csv`: `date, real_gdp`. U.S. real GDP, trillions of chained 2017 dollars, seasonally adjusted annual rate, quarterly, 2015Q1 to 2026Q2 (BEA via FRED `GDPC1`).
  - The textbook used chained 2012 dollars; current levels are 8–10% higher, with the same shape.
- `fig12-15.csv`: `date, inflation_all, inflation_core`. 12-month CPI inflation, percent, 100 × (P_t / P_t−12 − 1), monthly, 2020-01 to 2026-09: all items (`CPIAUCSL`) and core, all items less food and energy (`CPILFESL`), BLS via FRED.
  - Known quirk: the 2025-10 row is empty in both columns (no CPI collected during the shutdown).
- `fig12-16.csv`: `date, outlays_gdp_pct`. Federal net outlays, percent of GDP, by fiscal year (dated January 1 of the fiscal year), FY2007 to FY2025 (OMB/BEA via FRED `FYONGDA188S`).
  - Known quirk: FY2020–2022 are 0.5–0.6 points below the textbook's values, because BEA's 2023 revision raised GDP; the textbook's "22 percent in 2019" is 20.65 in the data (20.8 in the textbook's own vintage).
- `fig12-17.csv`: `date, real_disp_income, real_consumption`. Real disposable personal income and real personal consumption expenditures, trillions of chained 2017 dollars, seasonally adjusted annual rates, monthly, 2017-01 to 2026-08 (BEA via FRED `DSPIC96`, `PCEC96`).

Full definitions, vintages and the validation against the textbook are in macro102's
`original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/figN-k/notes.md`.

## Wider files built for the notebook

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch12-monetary-policy-and-the-phillips-curve/data/`, folders `fig12-2/raw/` and
`fig12-6/raw/`). Run it with `python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough`. The 11 NBER recessions that start in 1953 or later, from 1953-07 / 1954-05 to 2020-02 / 2020-04 (first day of the month).
  - Source: NBER-based recession indicator `USREC` (monthly) via FRED. `peak` is the month before the first recession month, `trough` the last recession month.
  - Used to shade the recessions in Figures 2, 9, 14, 15, 16 and 17.
- `yield_curves_monthly.csv`: `date, maturity, months, yield`. Long format, one row per curve and maturity: the Treasury par yield curve (percent, 11 maturities from 1 month to 30 years) on the first trading day of every month of 2022, 2023 and 2026 (34 curves, 2022-01-03 to 2026-10-01, 374 rows, no missing values). `maturity` is a label ("1 mo", ..., "30 yr"), `months` the maturity in months.
  - Source: U.S. Department of the Treasury, Daily Treasury Par Yield Curve Rates, the yearly CSV files for 2022, 2023 and 2026. The files for 2024 and 2025 were not downloaded, so the animation jumps from December 2023 to January 2026.
  - Validation: the curves of 2022-01-03 and 2023-04-03 (the first trading days of their months) equal the two textbook rows of `fig12-6.csv` at all 11 maturities; `build_data.py` stops if they do not.
  - Used for the animation in Figure 6.

## Multi-country files (conventions §6b)

Made by `build_data.py` from public downloads, cached in macro102's `.work/ch12/notebook-raw/` (`--refresh` downloads
them again). Every file is tidy and long, one row per country and period, with the columns `iso3, country`, then
`date` (first day of the month or quarter) or `year`, then the values. Country names come from `countries.csv`. The
U.S. rows are checked against the textbook-figure files above; where the README says so, they are copied from them,
so that the default (U.S.) view of each notebook figure is the textbook figure.

- `countries.csv`: `iso3, country, region, oecd`. 218 economies: every economy of the World Bank's country list
  (<https://api.worldbank.org/v2/country?format=json&per_page=400>, aggregates dropped) plus the euro area (`EMU`).
  Short names replace the World Bank's long ones ("Korea", "Russia", "Türkiye", "Hong Kong", "Nauru", ...). `region` is
  the World Bank region simplified to four groups (Americas; Europe and Central Asia; Asia and Pacific; Middle East and
  Africa); `oecd` is true for the 38 OECD members. Used for the colors and the website group buttons.
- `policy_rates_monthly.csv`: `policy_rate`, central bank policy rate, percent, monthly, 1960-01 to 2026-09, 49
  economies (22,568 rows). Source: BIS, Central bank policy rates `WS_CBPOL`, end of month
  (<https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/M.*?format=csv>). The U.S. rows are copied from
  `fig12-2.csv` (FEDFUNDS, monthly average); validation: the BIS U.S. series (end of month) differs from it by 0.22
  points on average since 1960 and 0.07 since 1990. Known quirks: eight early euro members stop in 1998 and Greece in
  2000 (then the euro area, from 1999), Croatia stops in 2022-07 and Argentina in 2025-06; the euro-area series is the
  ECB's main refinancing rate until 17 Sept 2024 and its deposit rate after; hyperinflation values reach 355,086
  percent (Brazil, 1990) and 2,647 percent (Croatia, 1993).
- `interest_rates_monthly.csv`: `rate_3m` (3-month interbank rate) and `rate_10y` (10-year government bond yield),
  percent a year, monthly averages, 2000-01 to 2026-09, 47 economies (14,780 rows; 417 and 1,153 missing values).
  Source: OECD Financial market statistics, `OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0`, measures `IR3TIB` and `IRLT`
  (<https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0/.M.IR3TIB+IRLT.PA.....>; the query
  starts in 1960 and the script keeps 2000 on, to stay under 1 MB). Validation: the U.S. rows differ from the Treasury
  yields of the first trading day in `yield_curves_monthly.csv` by 0.18 (3-month) and 0.16 (10-year) points on average
  (monthly averages against one day). Known quirks: the U.K. 3-month rate stops in 2026-02, Russia's rates in 2022.
- `inflation_annual.csv`: `inflation`, CPI inflation, percent change of the annual average, 1960–2025, 194 economies
  (9,218 rows). Source: World Bank WDI `FP.CPI.TOTL.ZG`
  (<https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json&per_page=20000&date=1960:2025>).
  The U.S. rows are copied from `fig12-9.csv` (WDI has no U.S. 2025 value yet; elsewhere the two differ by at most
  0.09 points). Hyperinflations reach thousands of percent (e.g. DR Congo 23,773 percent in 1994).
- `gdp_quarterly.csv`: `gdp_index`, real GDP, chain-linked volume index (2020 = 100), seasonally adjusted, quarterly,
  2015Q1–2026Q2, 49 economies (2,235 rows; China does not publish it, Russia stops in 2021Q3). Source: OECD Quarterly
  National Accounts, `OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,1.1`, key `Q.Y..S1.S1.B1GQ._Z._Z._Z.IX.LR.N.T0102`.
  Validation: rebased to 2019Q4 = 1, the U.S. index equals `fig12-14.csv` (GDPC1) within 0.005 percent.
- `cpi_monthly.csv`: `inflation_all` and `inflation_core`, 12-month CPI inflation in percent, monthly, 2020-01 to
  2026-09, 64 economies (5,042 rows). All items: BIS consumer prices `WS_LONG_CPI`, unit `771` (year-on-year change;
  national CPIs, the HICP for the euro area). Core (all items less food and energy): OECD `DSD_PRICES@DF_PRICES_ALL`,
  expenditure `_TXCP01_NRG`, transformation `GY`; for the euro area, Eurostat `prc_hicp_minr`, `TOT_X_NRG_FOOD`
  (energy, food, alcohol and tobacco excluded). The U.S. rows are copied from `fig12-15.csv`, including the empty
  2025-10 row (the BIS and OECD U.S. series, not seasonally adjusted, differ from it by 0.04 and 0.13 points on
  average). Known quirks: in 2026 the OECD has not yet published CPIs for the European countries (core stops in
  2025-12), Japan's core stops in 2021-06, some countries have no core series, and Costa Rica has core only.
- `government_spending.csv`: `spending_gdp`, general government total expenditure, percent of GDP, 2000–2025, 194
  economies (4,919 rows). Source: IMF *Fiscal Monitor* (October 2026), DataMapper indicator `G_X_G01_GDP_PT`
  (<https://www.imf.org/external/datamapper/api/v1/G_X_G01_GDP_PT>; projections after 2025 dropped; the IMF's `EURO`
  is the euro area and `UVK` Kosovo). A different concept from `fig12-16.csv`: all levels of government, calendar
  years. Validation: for the U.S. it is 12.7 to 17.1 points above federal outlays, and it rose 8.9 points from 2019 to
  2020 (federal outlays: 9.8). Known quirk: Timor-Leste, Tuvalu and Nauru spend more than 100 percent of GDP in some years.
- `household_quarterly.csv`: `income_pc` (real household gross disposable income per person) and `consumption_pc`
  (real household final consumption per person), indexes with 2007Q1 = 100 as published, quarterly, 2017Q1–2026Q1, 38
  economies (1,406 rows; income only for 23). Source: OECD Household dashboard, `OECD.SDD.NAD,DSD_HHDASH@DF_HHDASH_INDIC,1.1`,
  measures `B6GS1M_R_POP` and `P3S1M_R_POP`. Validation: from 2019Q4 to 2021Q1 U.S. income per person rose 17.6
  percent (`fig12-17.csv`, total: 17.5) and consumption 1.1 percent (total: 1.4).
