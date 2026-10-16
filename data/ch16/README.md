# Data for Chapter 16: Consumption

Read by `notebooks/ch16-consumption.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch16/`.

## Files copied from the macro102 collect-data output

- `fig16-3.csv`: `date, debt_gdp_pct`. Household and nonprofit debt as a percent of nominal GDP,
  100 × (FRED `CMDEBT` / 1000) / FRED `GDP`, quarterly, 1970Q1 to 2026Q2 (dates are quarter starts).
  - `CMDEBT`: Federal Reserve Financial Accounts of the United States (Z.1, table B.101), debt securities and
    loans of households and nonprofit organizations, millions of dollars, end of quarter. `GDP`: BEA, billions
    of dollars, seasonally adjusted annual rate.
  - Known quirks: from about 2000 on the ratio is up to 3.2 points lower than in the textbook, because the 2023
    comprehensive NIPA revision raised nominal GDP. FRED now reports `CMDEBT` in millions; the 2023 vintage was in
    billions.
- `fig16-4.csv`: `date, saving_rate`. Personal saving rate, percent of disposable personal income, quarterly
  means of the monthly FRED `PSAVERT` (BEA, seasonally adjusted), complete quarters only, 1970Q1 to 2026Q2.
  - Known quirk: from about 2000 on the current vintage is up to 2 points lower than the textbook's (2023 NIPA
    revision). The textbook plots quarterly means, so its Covid peaks (about 26 and 20) are below the monthly highs.
- `fig16-5.csv`: `date, networth_dpi_ratio`. Household and nonprofit net worth divided by disposable personal
  income (FRED `HNONWPDPI` / 100, Federal Reserve Z.1), quarterly, 1970Q1 to 2026Q2.
  - Known quirk: 2021–22 is revised down by up to 0.39 against the textbook's vintage; 1970–2020 is unchanged.

Sources: FRED and ALFRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/series/CMDEBT>,
<https://fred.stlouisfed.org/series/GDP>, <https://fred.stlouisfed.org/series/PSAVERT>,
<https://fred.stlouisfed.org/series/HNONWPDPI>), retrieved 2026-10-16. Full definitions, vintages and the
validation against the textbook are in macro102's `original-scanned-book/ch16-consumption/data/figN-k/notes.md`.

## Wider files built for the notebook

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch16-consumption/data/`, folders `ex08/raw/` and `fig16-4/raw/`). Run it with
`python build_data.py --macro102 PATH`. The script checks that the files reproduce `fig16-3.csv` and
`fig16-4.csv` (largest gaps 0.0005 and 0.0000) and stops otherwise.

- `debt_levels.csv`: `date, debt_millions, gdp_billions, debt_billions_2023, gdp_billions_2023`. Quarterly,
  1970Q1 to 2026Q2; used in Figure 3 to compute the debt ratio, to show a units trap and to compare two vintages.
  - `debt_millions`: FRED `CMDEBT`, current vintage, **millions** of dollars.
  - `gdp_billions`: FRED `GDP`, current vintage, billions of dollars (SAAR).
  - `debt_billions_2023`, `gdp_billions_2023`: the same two series as published on 2023-03-30 (ALFRED), both in
    **billions** of dollars, 1970Q1 to 2022Q4 (empty after that). This vintage reproduces the textbook's figure.
- `saving_rate_monthly.csv`: `date, saving_rate`. FRED `PSAVERT`, percent of disposable personal income,
  monthly, seasonally adjusted, 1970-01 to 2026-08; used in Figure 4 to build the quarterly series and to compare
  monthly with quarterly data. July and August 2026 form an incomplete quarter, which `fig16-4.csv` leaves out.

## Multi-country files (Figures 3–5 beyond the United States)

Also made by `build_data.py`, which downloads them from the public sources (requests' default User-Agent) and caches
the raw responses in macro102's `.work/ch16/notebook-raw/`. Each is a tidy long table, one row per country and period,
with `iso3`, a readable `country` name and a `region` (Americas, Asia and Oceania, Europe, Middle East and Africa) used
by the website's group buttons. Countries: the 38 OECD members and 12 large emerging economies, as far as each source
covers them; aggregates (euro area, G20, ...) are dropped. Retrieved 2026-10-17.

- `household_debt.csv`: `iso3, country, date, debt_gdp, region`. Credit to households and NPISHs from all sectors, at
  market value, percent of GDP, adjusted for breaks; quarterly (dates are quarter starts), 1970Q1 (or the first
  quarter available) to 2026Q1; 43 countries, 6,511 rows. Source: BIS total credit statistics, dataflow `WS_TC`, key
  `Q..H.A.M.770.A` (<https://stats.bis.org/api/v2/data/dataflow/BIS/WS_TC/2.0/Q..H.A.M.770.A?format=csv>; the
  same series as FRED `HDTGPD{CC}Q163N`, which starts only in 2005). Check: the U.S. rows are on average 1.3 points
  above `fig16-3.csv` (largest gap 4.7 points, correlation 0.998): the BIS uses its own debt and GDP measures.
  Ireland's ratio is distorted by the jump of its GDP in 2015 (multinational profits).
- `saving_rates.csv`: `iso3, country, year, saving_rate, region`. Net saving of households and NPISH, percent of net
  disposable income; annual, 1970 (U.S., Australia) or later to 2024/2025; 35 countries (China from 1992), 1,103
  rows. Source: OECD National Accounts at a Glance, Chapter 5 (dataflow `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_V,1.0`,
  measure `B8NS1M`, unit `PT_B6N_S1M`). Check: the U.S. rows are on average 0.23 points above the calendar-year
  means of the monthly `PSAVERT` (`saving_rate_monthly.csv`), never more than 0.67 points away (1970–2024).
- `household_wealth.csv`: `iso3, country, year, net_worth_ratio, region`. Household (and NPISH) net worth in years of
  gross disposable income: (net financial worth + dwellings + land) per person divided by gross disposable income per
  person, all in US dollars at PPP; annual, 1995 (or later) to 2023–2025; 26 countries, 741 rows. Source: the same
  OECD dataflow, measures `LES1M_BF90_POP`, `LES1M_N111N_POP`, `LES1M_N211N_POP` and `B6GS1M_POP`. Dwellings and
  land are most of households' non-financial wealth; the OECD's total non-financial assets exist for only 10
  countries. Check: the U.S. ratio is 0.93 to 1.09 times the Federal Reserve's ratio of `fig16-5.csv` (annual means;
  mean 1.015, 1995–2024). Gotcha: NAAG's measure `LES1M_B90`, labelled "Net worth", is total financial **assets**
  (codes `LE`, `F`, `A`), not net worth; it is not used.
