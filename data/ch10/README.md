# Data for Chapter 10: The Great Recession and the Covid-19 Pandemic: A First Look

Read by `notebooks/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch10/`.

## Files copied from the macro102 collect-data output

- `fig10-1.csv`: `date, real_home_price_index`. Robert Shiller's real U.S. home price index (nominal index deflated by the CPI; from 1987 the S&P CoreLogic Case-Shiller national index), rebased so that the 1953 average is 100. Monthly, 1953-01 to 2026-07.
  - Source: Shiller, "U.S. Home Price and Related Data" (`Fig3-1.xls`), shillerdata.com.
  - Known quirk: two numbers in the textbook's prose ("a factor of nearly 3 between 1996 and 2006", "collapsing by more than 40 percent") do not come from this index (real ×1.72 and −35.7%).
- `fig10-2.csv`: `date, fed_funds`. Effective federal funds rate, percent, monthly average of daily rates, 2000-01 to 2026-09 (FRED `FEDFUNDS`).
  - The textbook's "1.25 to 5.25 percent" are the Fed's target rates; the effective monthly rate was 1.00 in May 2004 and 4.94 in May 2006.
- `fig10-3.csv`: `date, ted_spread, cp_tbill_spread`. Interest-rate spreads, percentage points, monthly means of daily data, 2000-01 to 2026-09.
  - `ted_spread`: 3-month LIBOR minus the 3-month Treasury bill (FRED `TEDRATE`). It ends in 2022-01, when U.S. dollar LIBOR was discontinued.
  - `cp_tbill_spread`: 90-day AA financial commercial paper (`RIFSPPFAAD90NB`) minus the 3-month Treasury bill (`DTB3`), a comparable bank-funding spread that continues after 2022 (correlation with the TED spread 0.97 over 2000–2022). Empty for 2020-04 (no commercial-paper observations that month).
- `fig10-4.csv`: `date, sp500_real`. Real S&P 500 composite price index, in September 2026 dollars (nominal index × CPI of 2026-09 / CPI of the month), monthly, 1990-01 to 2026-09.
  - Source: Shiller, "U.S. Stock Market Data" (`ie_data.xls`), shillerdata.com. Levels are 1.115 times the textbook's, which uses February 2023 dollars.
- `fig10-5.csv`: `iso3, country, deaths_pm_2023_03_22, gdp_loss_2022q3, deaths_pm_2026_08_30, gdp_loss_2026q2`. One row per country (48 OECD and partner economies).
  - `deaths_pm_*`: cumulative confirmed Covid-19 deaths per million people on the textbook's date (2023-03-22) and on the latest date (2026-08-30); Our World in Data, from the WHO Covid-19 dashboard.
  - `gdp_loss_*`: cumulative real-GDP shortfall below the 2019Q4 level, summed over the quarters from 2020Q1 to 2022Q3 (the textbook's end) or 2026Q2, in percent of one year's GDP; OECD Quarterly National Accounts.
  - Known quirks: national-accounts revisions since 2023 lower several GDP losses (United States 3.3 against the textbook's 3.7); Chile's cumulative deaths fall between the two dates (a WHO revision).
- `fig10-6.csv`: `date, gdp_index_usa, gdp_index_kor, gdp_index_swe, gdp_index_deu, gdp_index_gbr, gdp_index_esp`. Real GDP, index 2019Q4 = 100, quarterly, 2019Q4 to 2026Q2 (OECD Quarterly National Accounts, chain-linked volumes, seasonally adjusted; replaces the discontinued OECD MEI series on FRED).
- `fig10-7.csv`: `date, nonfarm_emp`. Total nonfarm payroll employment, millions, monthly, seasonally adjusted, 2000-01 to 2026-09 (BLS via FRED `PAYEMS`).
- `fig10-8.csv`: `date, short_run_output, short_run_output_vintage2023`. Short-run output, 100 × (real GDP / potential GDP − 1), percent, quarterly, 2000Q1 to 2026Q2.
  - `short_run_output`: current BEA real GDP (`GDPC1`) and CBO potential GDP (`GDPPOT`).
  - `short_run_output_vintage2023`: the same with the data as published on 2023-02-01 (ALFRED), to 2022Q4. It reproduces the textbook's figure (2020Q2: −10.42 against −8.83 today).
- `fig10-9.csv`: `date, unemp_rate`. Civilian unemployment rate, percent, monthly, seasonally adjusted, 2000-01 to 2026-09 (BLS via FRED `UNRATE`). October 2025 has no row: the survey was not run during the federal government shutdown.
- `fig10-10.csv`: `date, inflation_us, inflation_uk, inflation_euro_area`. 12-month CPI inflation, 100 × ln(P_t / P_t−12), monthly, 2015-01 to 2026-09.
  - Sources: U.S. CPI-U (`CPIAUCNS`, FRED); U.K. CPIH (OECD prices database); euro-area HICP (Eurostat `prc_hicp_minr`).
  - Log changes reproduce the textbook's figure; simple percent changes peak a little higher (U.S. 9.06 against 8.67). U.S. October 2025 is empty (no CPI collected in the shutdown); the U.K. stops in 2026-08.
- `fig10-11.csv`: `date, core_inflation_us, core_inflation_uk, core_inflation_euro_area`. 12-month core inflation (excluding food and energy), log changes as above, monthly, 2015-01 to 2026-09 (U.S. `CPILFENS`; U.K. CPIH excluding food and energy, OECD; euro area HICP excluding energy, food, alcohol and tobacco, Eurostat). Same gaps as `fig10-10.csv`.

Full definitions, vintages and the validation against the textbook are in macro102's
`original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/figN-k/notes.md`.

## Wider files built for the notebook

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/`, folders
`fig10-2/raw/` and `table10-1/raw/`). Run it with `python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough, peak_quarter, trough_quarter`. The 11 NBER recessions that start in 1953 or later, from 1953-07 / 1954-05 to 2020-02 / 2020-04 (first day of the month or quarter).
  - Source: NBER-based recession indicators `USREC` (monthly) and `USRECQ` (quarterly) via FRED. `peak` is the period before the first recession period, `trough` the last recession period.
  - The monthly dates shade the recessions in Figures 2, 3, 7, 8 and 9; the quarterly dates define the episodes of Table 10.1 (the NBER dates quarters separately, e.g. the Covid-19 recession runs from 2019Q4 to 2020Q2).
- `us_quarterly.csv`: `date, gdp, consumption, investment, government, exports, imports, employment, unemployment`. Quarterly, 1953Q1 to 2026Q2 (294 quarters, no missing values).
  - `gdp` to `imports`: real GDP, personal consumption expenditures, gross private domestic investment, government consumption and investment, exports and imports, billions of chained 2017 dollars, seasonally adjusted annual rates (BEA via FRED: `GDPC1`, `PCECC96`, `GPDIC1`, `GCEC1`, `EXPGSC1`, `IMPGSC1`).
  - `employment`: quarterly mean of nonfarm payroll employment, millions (`PAYEMS`); `unemployment`: quarterly mean of the unemployment rate, percent (`UNRATE`; 2025Q4 averages the two months that exist).
  - Validation: the peak-to-trough changes computed from these two files reproduce collect-data's `table10-1/data.csv` (current vintage) within 0.005 points.
  - Used to recompute Table 10.1 in the section of Figure 9.
