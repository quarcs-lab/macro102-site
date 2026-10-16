# Data for Chapter 2: Measuring the Macroeconomy

Read by `notebooks/ch02-measuring-the-macroeconomy.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch02/`.

The U.S. series come from the U.S. Bureau of Economic Analysis (BEA) national accounts (NIPA) and the
NBER recession dates, downloaded from FRED, Federal Reserve Bank of St. Louis
(`https://fred.stlouisfed.org/series/<ID>`), on 2026-10-16. The multi-country files at the end come from
the World Bank and the Penn World Table (downloaded 2026-10-17).

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

## Multi-country files (conventions §6b, added 2026-10-17)

Made by `build_data.py`, which downloads them from the public sources and caches the raw responses in
`../macro102/.work/ch02/notebook-raw/`. Every file is tidy and long (`iso3, country, year, values…`), one
row per economy and year. Country names are the World Bank's, with long formal names shortened (e.g.
"Korea, Rep." → "South Korea", "Russian Federation" → "Russia", "Turkiye" → "Turkey"), as in `data/ch01/`.
The notebook draws the U.S. textbook series from the figure files above and the other countries from these.

- `countries.csv`: `iso3, country, region, income, g7, g20, oecd`. 222 economies: the 217 World Bank
  economies (aggregates removed) with their World Bank region and income group
  (`https://api.worldbank.org/v2/country?format=json&per_page=400`), plus Taiwan, Maddison's historical
  units and the euro area. Flags for the G7, the G20 (19 countries) and the 38 OECD members. Used for the
  country colors and the website's group menus.
- `expenditure_world.csv`: `iso3, country, year, consumption, investment, government, net_exports`. Percent
  of GDP, 1960–2025, 186 economies, 8,379 rows (years with all four shares).
  - Source: World Bank WDI `NE.CON.PRVT.ZS` (households and NPISHs final consumption expenditure),
    `NE.GDI.TOTL.ZS` (gross capital formation), `NE.CON.GOVT.ZS` (general government final consumption
    expenditure), `NE.RSB.GNFS.ZS` (external balance on goods and services).
  - Definitions differ from the BEA's (UN System of National Accounts): government investment is part of
    investment, and "government" is government consumption only. For the United States, 1970–2024, the
    WDI investment share is 4.25 points above `fig2-1.csv` on average and the government share 4.26
    points below; consumption (+0.02) and net exports (0.00) agree.
  - The four shares add up to 100 percent in the median country-year, but not always (from 50 to 133
    percent for a few small or war-torn economies), because the World Bank takes the components from
    different sources.
  - Hygiene: 21 Venezuelan rows (1991–2011) in which all four shares are reported as 0
    are dropped, so Venezuela ends in 1990.
- `labor_share_world.csv`: `iso3, country, year, labor_share`. Share of labor compensation in GDP at
  current national prices, 1950–2023, 140 economies, 8,215 rows.
  - Source: Penn World Table 11.0 `labsh` (Feenstra, Inklaar & Timmer, <https://doi.org/10.34894/FABVLR>,
    `pwt110.dta`).
  - Validation: the U.S. PWT share is 0.010 to 0.044 below the textbook measure of `fig2-3.csv` (mean
    0.031), because PWT treats the income of the self-employed differently.
  - Hygiene: Venezuela is 0.0844 in every year 2019–2023 (carried forward); Qatar, Kuwait and other oil
    exporters are below 0.25.
- `deflator_world.csv`: `iso3, country, year, deflator_2012_100, inflation`. 1960–2025, 214 economies,
  11,639 rows.
  - `deflator_2012_100`: World Bank WDI `NY.GDP.DEFL.ZS` (GDP implicit deflator), which each country
    publishes with its own base year, rebased to 2012 = 100 (empty for the few economies with no 2012
    value). Six significant digits, because hyperinflations make the values span from 1e-15 (DR Congo,
    1960) to 1e14.
  - `inflation`: WDI `NY.GDP.DEFL.KD.ZG` (inflation, GDP deflator, annual percent).
  - Validation: the U.S. rows are within 0.8 percent of the annual mean of `fig2-4.csv`, and the U.S.
    inflation within 0.3 points of the growth of that annual mean.

