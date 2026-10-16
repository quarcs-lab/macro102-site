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
