# Data for Chapter 1: Introduction to Macroeconomics

Read by `notebooks/ch01-introduction-to-macroeconomics.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch01/`.

## Files copied from the macro102 collect-data output

- `fig1-1.csv`: `year, gdppc_usa, gdppc_gbr, gdppc_jpn, gdppc_arg, gdppc_zaf, gdppc_chn`. GDP per person in 2022 dollars at the textbook's benchmark years (1870, 1890, 1900, 1929, every decade 1950–2020, and 2022).
  - Source: Maddison Project Database 2023 `gdppc` (Bolt & van Zanden, <https://doi.org/10.34894/INZBF2>), 2011 dollars × 1.2902, the U.S. GDP deflator ratio 2022/2011 (BEA via FRED, `A191RD3A086NBEA`).
- `fig1-2.csv`: `date, emp_pop_ratio`. U.S. civilian employment-population ratio, percent, monthly, seasonally adjusted, 1960-01 to 2026-09.
  - Source: BLS Current Population Survey via FRED (`EMRATIO`).
  - Known gap: October 2025 is missing (BLS did not collect it during the federal government shutdown). The notebook shows how to find it.
- `fig1-3.csv`: `year, inflation_us, inflation_uk, inflation_euro_area, inflation_japan`. Annual CPI inflation, percent, 1960–2025.
  - Sources: World Bank WDI via FRED (`FPCPITOTLZGGBR`, `FPCPITOTLZGEMU`, `FPCPITOTLZGJPN`); U.S. computed from the annual average of CPI-U (`CPIAUCNS`), which reproduces the World Bank's U.S. series.
- `fig1-4.csv`: `year, unrate_us, unrate_europe, unrate_japan`. Annual unemployment rates, percent, 1955–2025 (Europe from 1960).
  - Sources: BLS via FRED (`UNRATE`, calendar-year average); OECD via FRED (`LRHUTTTTJPA156S`); Europe = euro area of 12 countries from the European Commission's AMECO database (`DA12`/`EA12 .1.0.0.0.ZUTN`, <https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco1.zip>), a substitute for the textbook's OECD series.
- `fig1-5.csv`: `year, budget_deficit_pct_gdp, trade_deficit_pct_gdp`. U.S. federal budget deficit and trade deficit, percent of GDP, 1960–2025 (negative = surplus).
  - Source: BEA NIPA via FRED (`FGDEF`, `NETEXP`, `GDP`), calendar-year averages of quarterly data.
- `fig1-7.csv`: `year, gdppc_actual, gdppc_potential`. U.S. real GDP per person and potential GDP per person, 2022 dollars, 1870–2025.
  - Sources: BEA via FRED (`GDPCA`, `B230RC0A052NBEA`, `A191RD3A086NBEA`) from 1929, and Maddison 2023 ratio-spliced at 1929 for 1870–1928. Potential: CBO (`GDPPOT`) from 1949; before 1949 an HP trend (λ = 100) of log GDP per person.

## Wider files built for the notebook

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch01-introduction-to-macroeconomics/data/fig1-1/raw/` and `fig1-2/raw/`).

- `maddison_annual.csv`: `iso3, country, year, gdppc`. Every available year from 1870 to 2022 for the six countries of Figure 1.1 (USA, GBR, JPN, ARG, ZAF, CHN) plus Ethiopia (ETH, from 1950), 898 rows.
  - Source: Maddison Project Database 2023 `gdppc` × 1.2902 (2011 → 2022 dollars, same factor as `fig1-1.csv`).
  - Validation: it reproduces `fig1-1.csv` exactly at every benchmark year.
  - Used to check the textbook's "10 times richer than a century ago" (the data give 5.8 for 2022/1922) and "25 times richer than the typical Ethiopian" (25.5 in 2022).
  - Annual coverage is incomplete before 1950 for some countries (e.g. China, South Africa).
- `recessions.csv`: `peak, trough`. The 9 NBER business-cycle peaks and troughs since 1960 (first day of the month), from 1960-04 / 1961-02 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month, `trough` the last recession month; these are the NBER's official dates.
  - Used to shade recessions in Figure 2.
