# Data for Chapter 7: The Labor Market, Wages, and Unemployment

Read by `notebooks/ch07-the-labor-market-wages-and-unemployment.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch07/`.

## Files copied from the macro102 collect-data output

- `fig7-1.csv`: `date, emp_pop_ratio`. U.S. civilian employment-population ratio (16+), percent, monthly, seasonally adjusted, 1960-01 to 2026-09.
  - Source: BLS Current Population Survey via FRED (`EMRATIO`).
  - Known gap: October 2025 is missing (not collected during the federal government shutdown).
- `fig7-2.csv`: `date, unemployment_rate`. U.S. civilian unemployment rate, percent, monthly, seasonally adjusted, 1950-01 to 2026-09.
  - Source: BLS via FRED (`UNRATE`). October 2025 is missing, as above.
- `fig7-7.csv`: `year, unrate_us, unrate_europe, unrate_japan`. Annual unemployment rates, percent, 1955–2025 (Europe from 1960).
  - Sources: BLS via FRED (`UNRATE`, calendar-year average); OECD via FRED (`LRHUTTTTJPA156S`); Europe = euro area of 12 countries from the European Commission's AMECO database (`DA12`/`EA12 .1.0.0.0.ZUTN`, <https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco1.zip>), a substitute for the textbook's OECD series (up to about 1 point lower in the mid-1980s).
- `fig7-8.csv`: `year, college_premium_log_pct, college_premium_pct, college_share_employment_pct`. 1976–2025 (premium from 1979).
  - `college_premium_pct`: regression-adjusted hourly wage premium of four-year college graduates over high school graduates, percent; `college_premium_log_pct` = 100 × ln(1 + premium), log points.
  - `college_share_employment_pct`: share of employment with a bachelor's or advanced degree, percent (persons; the textbook's line is a share of hours and is about twice as high).
  - Source: Economic Policy Institute, State of Working America Data Library (CPS), a substitute for the textbook's private Acemoglu–Molina series.
- `fig7-10.csv`: `date, manufacturing_emp_millions`. U.S. payroll employment in manufacturing, millions, monthly, seasonally adjusted, 1950-01 to 2026-09.
  - Source: BLS Current Employment Statistics via FRED (`MANEMP`).
- `fig7-11.csv`: `year, top01_share_us, top01_share_france`. Share of pre-tax national income received by the top 0.1 percent, percent; U.S. 1913–2024, France 1915–2022.
  - Source: World Inequality Database (WID.world) via Our World in Data (indicator 1290252). The U.S. value is identical (9.93) in 2022–2024: WID repeats its last estimate. The current vintage differs from the textbook's in a few years (U.S. 1950, France after 2015).
- `fig7-12.csv`: `year, start_year, series, percentile, group, growth_pct`. Average annual growth of real post-tax income per adult, percent, over 34-year windows.
  - `series = "g-percentile (PSZ 2018)"`: every percentile 1–99 plus the top percentiles 99.1 … 99.999, for 1946→1980 (`year` 1980) and 1980→2014 (`year` 2014). Source: Piketty, Saez & Zucman (2018 QJE), `PSZ2018MainData.xlsx`, sheet `TS11(NYT)`.
  - `series = "group average (PSZ 2022)"`: bottom 50%, middle 40%, top 10%, 1%, 0.1%, 0.01%, 0.001% for the same windows and 1985→2019, placed at their percentile midpoints in `percentile`. Source: PSZ Distributional National Accounts, Appendix Tables II (February 2022), sheet `TC3`.

## Wider files built for the notebook

All four files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/`, folders `fig7-1/raw/`,
`ex02/raw/`, `table7-1/raw/` and `table7-2/raw/`). Run it with
`python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough`. The 11 NBER business-cycle peaks and troughs whose trough is in 1950 or later (first day of the month), from 1953-07 / 1954-05 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month, `trough` the last recession month (the NBER's official dates).
  - Used to shade recessions in Figures 1, 2 and 10.
- `emp_pop_by_sex.csv`: `date, men, women`. Employment-population ratios of men and of women aged 16+, percent, monthly, seasonally adjusted, 1948-01 to 2026-09 (944 months; October 2025 missing).
  - Source: BLS via FRED (`LNS12300001`, `LNS12300002`).
  - Validation: identical to macro102's `ex02/data.csv`. Used to check the textbook's numbers for men and women (Figure 1).
- `labor_force.csv`: `date, population, labor_force, employed, unemployed, not_in_labor_force`. Millions of people, monthly, 1948-01 to 2026-09.
  - Source: BLS Current Population Survey via FRED: civilian noninstitutional population 16+ (`CNP16OV`, not seasonally adjusted), labor force (`CLF16OV`), employment (`CE16OV`), unemployment (`UNEMPLOY`); `not_in_labor_force` = population − labor force.
  - Validation: January 2023 reproduces macro102's `table7-1/data.csv` exactly, and 100 × unemployed / labor force reproduces `UNRATE` (`fig7-2.csv`) in every month to one decimal.
  - Used to rebuild Table 7.1 for January 2023 and the latest month (Figure 2).
- `hours_per_person.csv`: `country, year, hours_pwt11, hours_pwt10`. Annual hours worked per person (average hours × persons engaged / population), index U.S. 2019 = 100, 1950–2023 (PWT 10.01 to 2019), for the seven countries of Table 7.2 (South Korea from 1953).
  - Sources: Penn World Table 11.0 (`hours_pwt11`, <https://doi.org/10.34894/FABVLR>) and 10.01 (`hours_pwt10`, <https://doi.org/10.34894/QT5BCC>), variables `avh`, `emp`, `pop`.
  - Validation: `hours_pwt10` rounded to integers reproduces all 21 cells of the textbook's Table 7.2 and matches macro102's `table7-2/data.csv` within its rounding (0.05).
  - Used to rebuild Table 7.2 in both versions (Figure 7).
