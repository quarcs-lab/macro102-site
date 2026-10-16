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
