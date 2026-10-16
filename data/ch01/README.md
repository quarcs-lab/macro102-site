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

All are made by `build_data.py`. The first two come from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch01-introduction-to-macroeconomics/data/fig1-1/raw/` and `fig1-2/raw/`); the
multi-country files (conventions §6b) are downloaded from public sources by the script itself and cached in
`../macro102/.work/ch01/notebook-raw/`.

- `maddison_annual.csv`: `iso3, country, year, gdppc`. Every available year from 1870 to 2022 for the six countries of Figure 1.1 (USA, GBR, JPN, ARG, ZAF, CHN) plus Ethiopia (ETH, from 1950), 898 rows.
  - Source: Maddison Project Database 2023 `gdppc` × 1.2902 (2011 → 2022 dollars, same factor as `fig1-1.csv`).
  - Validation: it reproduces `fig1-1.csv` exactly at every benchmark year.
  - Used to check the textbook's "10 times richer than a century ago" (the data give 5.8 for 2022/1922) and "25 times richer than the typical Ethiopian" (25.5 in 2022).
  - Annual coverage is incomplete before 1950 for some countries (e.g. China, South Africa).
- `recessions.csv`: `peak, trough`. The 9 NBER business-cycle peaks and troughs since 1960 (first day of the month), from 1960-04 / 1961-02 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month, `trough` the last recession month; these are the NBER's official dates.
  - Used to shade recessions in Figure 2.

## Multi-country files (conventions §6b, added 2026-10-17)

Every file is tidy and long (`iso3, country, year, values…`), one row per economy and year. Country names
are the World Bank's, with long formal names shortened (e.g. "Korea, Rep." → "South Korea", "Russian
Federation" → "Russia", "Turkiye" → "Turkey", "Egypt, Arab Rep." → "Egypt"), so they agree across files.
The rows for the textbook's own economies are copied from the figure files, so each figure's default view
is exactly the textbook's; the `source` column says where every row comes from.

- `countries.csv`: `iso3, country, region, income, g7, g20, oecd`. 223 economies: the 217 World Bank
  economies (aggregates removed) with their World Bank region and income group (from
  `https://api.worldbank.org/v2/country?format=json&per_page=400`), plus Taiwan, Maddison's historical
  units (Former USSR, Czechoslovakia, Former Yugoslavia, region "Historical units") and the aggregates
  "Euro area" (`EMU`) and "Europe" (`EA12`, the euro area of 12 of `fig1-4.csv`). The flags mark the
  G7, the G20 (19 member countries) and the 38 OECD members. Used for the country colors and the
  website's group menus.
- `maddison_world.csv`: `iso3, country, year, gdppc`. GDP per person in 2022 dollars, every year with an
  estimate from 1870 to 2022, 169 economies, 15,890 rows.
  - Source: Maddison Project Database 2023, sheet "Full data" of `mpd2023_web.xlsx` (Bolt & van Zanden,
    <https://doi.org/10.34894/INZBF2>), × 1.2902 as `fig1-1.csv`.
  - Validation: identical to `maddison_annual.csv`, and so to `fig1-1.csv`, for every common row.
  - Many countries have estimates only from 1950 (70 countries have one for 1870).
- `employment_world.csv`: `iso3, country, year, emp_pop_ratio`. Employment-to-population ratio, ages 15
  and over, percent, 1991–2025, 188 economies, 6,566 rows.
  - Source: World Bank WDI `SL.EMP.TOTL.SP.ZS` (ILO modelled estimates).
  - Validation: the U.S. rows are 0.1 to 1.1 points below the annual mean of `fig1-2.csv` (BLS, ages 16
    and over), mean −0.7: the ILO also counts 15-year-olds.
- `inflation_world.csv`: `iso3, country, year, inflation, source`. CPI inflation, percent, 1960–2025, 201
  economies (incl. the euro area), 10,909 rows.
  - Sources: `fig1-3.csv` for the United States, the United Kingdom, the euro area and Japan (264 rows);
    World Bank WDI `FP.CPI.TOTL.ZG` (`WDI`, 8,954 rows); where WDI has no value, the World Bank's Global
    Inflation Database, sheet `hcpi_a`, 1970–2024 (`GID`, 1,691 rows; Ha, Kose & Ohnsorge,
    <https://www.worldbank.org/en/research/brief/inflation-database>), which fills e.g. Argentina
    1970–2017 and Venezuela 1970–2008 and 2017–2024.
  - Validation: WDI reproduces the four series of `fig1-3.csv` exactly (largest gap 0.000 points).
  - Extremes: Venezuela 65,374 percent in 2018, DR Congo 23,773 percent in 1994.
- `unemployment_world.csv`: `iso3, country, year, unrate, source`. Unemployment rate, percent, 1955–2025,
  56 economies, 2,627 rows.
  - Sources: `fig1-4.csv` for the United States (BLS), Europe (AMECO, euro area of 12) and Japan (OECD);
    European Commission AMECO `ZUTN` for 40 other countries, mostly European plus Australia, Canada,
    South Korea, New Zealand and Turkey, from 1960 (`AMECO`; forecasts after 2025 dropped); World Bank
    WDI `SL.UEM.TOTL.ZS` (ILO modelled, from 1991) for the 13 OECD and G20 members AMECO does not cover
    (`WDI (ILO modelled)`: Argentina, Brazil, Chile, China, Colombia, Costa Rica, India, Indonesia,
    Israel, Mexico, Russia, Saudi Arabia, South Africa).
  - Validation: AMECO's own U.S. and Japanese rates differ from `fig1-4.csv` by 0.03 points on average
    (at most 0.08).
- `deficits_world.csv`: `iso3, country, year, budget_deficit, trade_deficit, source`. Percent of GDP,
  positive = deficit, 1960–2025, 210 economies, 10,101 rows.
  - U.S. rows: `fig1-5.csv` (federal budget, NIPA; `fig1-5.csv (federal)`).
  - Other countries (`IMF WEO + WDI`): budget deficit = − general government net lending/borrowing,
    IMF World Economic Outlook `GGXCNL_NGDP` (<https://www.imf.org/external/datamapper/api/v1/GGXCNL_NGDP>;
    from 1980–2000 depending on the country; IMF projections after 2025 dropped, and 2025 may still be an
    IMF estimate); trade deficit = − external balance on goods and services, WDI `NE.RSB.GNFS.ZS`
    (1960–2024).
  - Definitions differ: general government includes state and local governments. For the United States
    the IMF's general-government deficit averaged 1.15 points of GDP more than the federal deficit of
    `fig1-5.csv` in 2001–2025. The WDI U.S. trade deficit reproduces `fig1-5.csv` within 0.09 points.
  - Extremes worth a look: Equatorial Guinea's budget deficits of 1991–1994 (up to 557 percent of GDP),
    São Tomé and Príncipe's surplus of 125 percent of GDP in 2007, Timor-Leste's
    trade deficit (165 percent of GDP in 2002), Germany's 1995 deficit (debt takeover of the
    Treuhandanstalt).

