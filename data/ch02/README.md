# Data for Chapter 2: Measuring the Macroeconomy

Read by `notebooks/ch02-measuring-the-macroeconomy.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch02/`.

All series come from the U.S. Bureau of Economic Analysis (BEA) national accounts (NIPA) and the
NBER recession dates, downloaded from FRED, Federal Reserve Bank of St. Louis
(`https://fred.stlouisfed.org/series/<ID>`), on 2026-10-16.

## Files copied from the macro102 collect-data output

- `fig2-1.csv`: `year, consumption_share, investment_share, government_share, net_exports_share`.
  Expenditure shares of nominal GDP in percent, 1929–2025. Each share is 100 × component / GDP, from
  `GDPA`, `PCECA`, `GPDIA`, `GCEA` and `A019RC1A027NBEA` (NIPA Table 1.1.5). The four shares add up to 100.
- `fig2-2.csv`: the same columns for 1970–2025.
- `fig2-3.csv`: `year, labor_share`. Labor's share of income, 1950–2025, computed as
  compensation / (GDI − taxes on production and imports less subsidies − proprietors' income), from
  `A033RC1A027NBEA`, `GDIA`, `W254RC1A027NBEA` and `A041RC1A027NBEA` (NIPA Table 1.10). This
  reconstruction of the textbook's "author's calculations" matches the scan to three decimals through 2019.
- `fig2-4.csv`: `date, gdp_deflator_2012_100`. The GDP implicit price deflator (`GDPDEF`), quarterly,
  1947Q1–2026Q2, rebased from FRED's 2017 = 100 to the textbook's 2012 = 100. Dates are the first day
  of each quarter.
- `fig2-5.csv`: `date, inflation_gdpdef`. Percent change of `GDPDEF` from a year ago (four quarters
  earlier), 1948Q1–2026Q2.

## Wider files built for the notebook

Both files are made by `build_data.py` from the raw FRED downloads saved by macro102's `/collect-data`
(`original-scanned-book/ch02-measuring-the-macroeconomy/data/<item>/raw/`).

- `nipa_annual.csv`: one row per year, 1929–2025, 27 columns. Billions of current dollars unless noted.
  - Expenditure side (NIPA Table 1.5.5 lines, used for Table 2.1): `gdp` (GDPA), `consumption` (PCECA),
    `investment` (GPDIA), `government` (GCEA), `net_exports` (A019RC1A027NBEA), `exports` (EXPGSA),
    `imports` (IMPGSA), `motor_vehicles` (DMOTRC1A027NBEA), `food` (DFXARC1A027NBEA, food and beverages
    for off-premises consumption), `housing` (DHUTRC1A027NBEA, housing and utilities), `medical`
    (DHLCRC1A027NBEA, health care), `structures` (B009RC1A027NBEA, nonresidential structures),
    `equipment` (Y033RC1A027NBEA), `ipp` (Y001RC1A027NBEA, intellectual property products),
    `residential` (PRFIA), `defense` (A824RC1A027NBEA).
  - Income side (NIPA Table 1.10 lines, used for Table 2.2 and the labor share): `compensation`
    (A033RC1A027NBEA), `wages` (A4102C1A027NBEA), `benefits` (A038RC1A027NBEA, supplements to wages and
    salaries), `taxes_less_subsidies` (W254RC1A027NBEA), `net_operating_surplus` (W260RC1A027NBEA),
    `depreciation` (GDICONSPA, consumption of fixed capital), `gdi` (GDIA, gross domestic income),
    `proprietors_income` (A041RC1A027NBEA).
  - `real_gdp`: real GDP in billions of chained 2017 dollars (GDPCA).
  - `population`: midperiod population in thousands (B230RC0A052NBEA).
  - Validation: the expenditure shares reproduce `fig2-1.csv` within 0.0001 percentage points, and the
    labor-share formula reproduces `fig2-3.csv` exactly.
  - Known quirk: these are the current-vintage data. The BEA's comprehensive update of September 2023
    raised 2022 GDP by about 2 percent (to $26.06 trillion, against the textbook's $25.5 trillion), and
    the net operating surplus by about $0.5 trillion, so some 2022 shares differ from Tables 2.1 and 2.2
    by up to 1.8 points. The income lines add up to GDI, which differs from GDP by a small statistical
    discrepancy (0.03 percent of GDP in 2022).
- `recessions.csv`: `start, end`. The first and last month of each of the 12 NBER recessions from 1948
  to 2020, derived from the monthly recession indicator `USREC` (1 in recession months). Used to shade
  Figures 4 and 5 as FRED does.
