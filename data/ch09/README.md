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

## Multi-country files (conventions.md §6b)

Made by `build_data.py`, which downloads from the public sources (requests' default User-Agent; the OECD API answers
429 "Too Many Requests" after a few calls, so the script waits and retries) and caches the raw responses in
macro102's `.work/ch09/notebook-raw/`. The figures use the textbook's U.S. data (CBO, BEA, BLS); the OECD's U.S. rows
are kept for comparison.

- `short_run_panel.csv`: `iso3, country, year, gdp_real, gdp_potential, output_gap, inflation, inflation_source,
  unemployment, unemployment_trend`. Annual, 51 economies (the 38 OECD members and Argentina, Brazil, Bulgaria, China,
  Croatia, India, Indonesia, Peru, Romania, Russia, Saudi Arabia, South Africa, Thailand), 1960–2025, 3,121 rows.
  - Source: OECD *Economic Outlook* 119 (June 2026), annual
    (<https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.GDPV+GDPVTR+GDPVD+GAP+UNR+CPI_YTYPCT+CPIH_YTYPCT.A>);
    the EO's 2026–2027 projections are dropped.
  - `gdp_real`: real GDP, trillions of 2021 US dollars at purchasing power parity (`GDPVD`). `gdp_potential`: potential
    output in the same units, `gdp_real × GDPVTR / GDPV` (potential and actual GDP in national currency). Norway's
    `gdp_potential` is left empty, because its EO potential output and gap refer to mainland Norway (without oil and
    shipping) while its GDP is total GDP.
  - `output_gap`: short-run output, percent of potential (`GAP`), 39 economies, from 1985 at the earliest. It equals
    100 × (`GDPV`/`GDPVTR` − 1) for every economy except Norway (mainland gap).
  - `inflation`: annual CPI inflation, percent, from `../ch08/inflation_panel.csv` (World Bank WDI `FP.CPI.TOTL.ZG`,
    gaps filled from the World Bank's Global Inflation Database; `inflation_source` = `WDI` or `GID`), and where both
    are missing the EO's headline or harmonised CPI inflation (`OECD EO`, 11 rows).
  - `unemployment`: unemployment rate, percent (`UNR`). `unemployment_trend`: its Hodrick–Prescott trend (λ = 100),
    computed here for each economy over all its years. EO 119 no longer publishes NAIRU estimates, so the notebook
    measures cyclical unemployment as `unemployment − unemployment_trend` for the other countries (Figure 8).
  - Validation (U.S. rows vs the textbook-figure files): the OECD output gap correlates 0.80 with the CBO gap of
    `fig9-3.csv` (annual means, 1985–2025; mean difference +0.22 points, largest 2.0 points in 1986); unemployment
    matches `fig9-8.csv` within 0.045 points; inflation matches `fig9-5.csv` within 0.087 points. Okun's slope with
    HP-trend unemployment is −0.47 (CBO gap, 1970–2025) or −0.38 (1960–2025) against −0.62 with the CBO natural rate:
    the trend absorbs part of long slumps.
  - Used for Figures 2, 3, 5, 7 and 8 (other countries).
- `employment_quarterly.csv`: `iso3, country, date, employment, emp_change_pct`. Total employment (labour force survey
  basis), millions, and its percent change from the previous quarter, quarterly (date = first day of the quarter),
  37 economies, 1960-Q2 to 2025-Q4, 7,317 rows.
  - Source: OECD *Economic Outlook* 119, `ET`, quarterly
    (<https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.ET.Q>); 2026–2027 projections dropped.
  - Validation: the U.S. rows (household survey) correlate 0.96 with the quarterly change of payroll jobs
    (`payroll_employment.csv`, quarterly means); 2020-Q2: −12.7 percent against −11.9 percent.
  - Known quirk: for some economies the early quarters are interpolated by the OECD from annual data (e.g. Turkey
    before the 2000s changes smoothly from quarter to quarter). This is a different concept from the monthly payroll
    jobs of `fig9-4.csv`.
  - Used for Figure 4 (other countries).
