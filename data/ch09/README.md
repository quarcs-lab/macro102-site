# Data for Chapter 9: An Introduction to the Short Run

Read by `notebooks/ch09-an-introduction-to-the-short-run.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch09/`.

## Files copied from the macro102 collect-data output

- `fig9-2.csv`: `year, gdp_actual, gdp_potential`. U.S. real GDP, actual and potential, trillions of 2022 dollars, annual, 1929–2025.
  - Sources: BEA real GDP (`GDPCA`) and CBO potential GDP (`GDPPOT`, calendar-year mean of the quarters) via FRED, converted from 2017 to 2022 dollars with the GDP deflator (`A191RD3A086NBEA`).
  - Known quirk: no agency publishes potential output before 1949. For 1929–1948 it is a very smooth Hodrick-Prescott trend of actual GDP joined to the CBO series, so the early gaps are only approximate (1929 shows an implausible +25 percent).
- `fig9-3.csv`: `date, short_run_output, short_run_output_book_vintage, gdp_real, gdp_potential`. Quarterly, 1970Q1–2026Q2.
  - `short_run_output` = 100 × (`gdp_real` − `gdp_potential`) / `gdp_potential`, percent, from current BEA real GDP (`GDPC1`) and CBO potential (`GDPPOT`), billions of chained 2017 dollars; CBO projections are not used.
  - `short_run_output_book_vintage`: the same calculation with the data as published in 2023 (ALFRED `GDPC1` of 2023-06-01 and `GDPPOT` of 2023-01-15), to 2023Q1. It reproduces the textbook's figure (2020Q2: −10.42 against −8.83 today).
- `fig9-4.csv`: `date, emp_change_pct`. Monthly percent change of total nonfarm payroll employment (BLS `PAYEMS` via FRED), seasonally adjusted, 1980-01 to 2026-09.
- `fig9-5.csv`: `year, inflation_cpi`. Annual CPI-U inflation (percent change of the calendar-year average of `CPIAUCSL`), 1960–2025. The missing October 2025 index (federal shutdown) is filled by linear interpolation before averaging.
- `fig9-7.csv`: `year, short_run_output, inflation_cpi, d_inflation, d_inflation_fitted`. Annual, 1961–2025.
  - `short_run_output`: annual mean of the quarterly short-run output of `fig9-3.csv` (current vintage), percent.
  - `inflation_cpi` as in `fig9-5.csv`; `d_inflation` = its change from the year before, percentage points.
  - `d_inflation_fitted`: the OLS line of `d_inflation` on `short_run_output` (slope 0.353, intercept 0.103).
- `fig9-8.csv`: `year, short_run_output, unrate, nrou_short_term, cyclical_unemployment, cyclical_unemployment_fitted`. Annual, 1960–2025.
  - `unrate`: annual mean of the BLS unemployment rate (`UNRATE`; October 2025 interpolated); `nrou_short_term`: annual mean of the CBO short-term natural rate of unemployment (`NROUST`), the series that reproduces the textbook's figure; `cyclical_unemployment` = `unrate` − `nrou_short_term`. All percent.
  - `cyclical_unemployment_fitted`: the OLS line on `short_run_output` (slope −0.616, intercept 0.244).

Full definitions, vintages and the validation against the textbook are in macro102's
`original-scanned-book/ch09-an-introduction-to-the-short-run/data/figN-k/notes.md`.

## Wider files built for the notebook

All three files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch09-an-introduction-to-the-short-run/data/`, folders `fig9-3/raw/`,
`fig9-4/raw/` and `fig9-5/raw/`). Run it with `python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough`. The 9 NBER business-cycle peaks and troughs whose trough is in 1960 or later (first day of the month), from 1960-04 / 1961-02 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month, `trough` the last recession month (the NBER's official dates).
  - Used to shade recessions in Figures 3 and 5 and to build the recession tables of Figures 3, 4 and 5.
- `payroll_employment.csv`: `date, payroll_millions`. Total nonfarm payroll employment, millions of jobs, monthly, seasonally adjusted, 1979-12 to 2026-09 (562 months).
  - Source: BLS Current Employment Statistics via FRED (`PAYEMS`).
  - Validation: its monthly percent change reproduces `fig9-4.csv` exactly (largest difference 0.0000).
  - Used to count the jobs lost in each recession since 1980 (Figure 4).
- `cpi_monthly.csv`: `date, cpi, inflation_12m`. CPI-U, all items, index 1982–84 = 100, seasonally adjusted, and its 12-month percent change, monthly, 1959-01 to 2026-09 (813 months).
  - Source: BLS via FRED (`CPIAUCSL`).
  - Known gap: October 2025 is missing (prices were not collected during the federal government shutdown), so `cpi` and `inflation_12m` are empty for that month. It is left missing here.
  - Validation: with October 2025 interpolated, the calendar-year means reproduce the annual inflation of `fig9-5.csv` (largest difference 0.0005 points).
  - Used for the monthly inflation line of Figure 5 and the check of the Covid-19 recession (12-month inflation 2.34 percent in February 2020, 0.31 percent in April 2020).
