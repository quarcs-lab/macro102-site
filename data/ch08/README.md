# Data for Chapter 8: Inflation

Read by `notebooks/ch08-inflation.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch08/`.

## Files copied from the macro102 collect-data output

Columns and spans (details in macro102's `original-scanned-book/ch08-inflation/data/<id>/notes.md`):

- `fig8-1.csv`: `year, inflation_cpi`. U.S. CPI inflation (percent change of the annual-average CPI-U), 1960–2025.
- `fig8-2.csv`: `year, share_above_25_pct, n_countries`. Percentage of World Bank economies with CPI inflation above
  25 percent among those reporting, and the number reporting, 1960–2025.
- `fig8-3.csv`: `year, decade, end_year, money_growth, inflation`. Average annual growth of U.S. M2 and of the CPI per
  decade, 1870s–2020s (the last row covers 2020–2025 only).
- `fig8-4.csv`: `iso3, country, money_growth_*, inflation_*, n_money_*, n_infl_*, n_infl_filled_*` for the windows
  1990–2021 and 1990–2025. Arithmetic means of annual broad-money growth and CPI inflation, 165 economies; inflation
  gaps in the WDI filled from the Global Inflation Database (`n_infl_filled_*` counts those years); broad-money series
  breaks removed.
- `fig8-5.csv`: `year, nominal_tbill_3m, inflation_cpi, real_rate`. 3-month Treasury bill rate (annual mean), CPI
  inflation and the ex-post real rate, percent, 1960–2025.
- `fig8-6.csv`: `year, argentina, brazil, russia`. CPI inflation, percent, 1970–2025 (Argentina 1970–2024 from the
  Global Inflation Database to 2017 and FRED from 2018; Brazil from 1981; Russia from 1993).
- `fig8-7.csv`: `year, mexico, nigeria, venezuela`. CPI inflation, percent, 1960–2025 (Venezuela 2009–2024: FRED to
  2016, Global Inflation Database after).

Sources:

- `fig8-1.csv`: FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL>)
- `fig8-2.csv`: World Bank API, country list (<https://api.worldbank.org/v2/country?format=json&per_page=400>); World Bank, World Development Indicators (<https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json>)
- `fig8-3.csv`: Jorda-Schularick-Taylor Macrohistory Database, release 6 (<https://www.macrohistory.net/app/download/9834512569/JSTdatasetR6.xlsx>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=M2NS>); MeasuringWorth (Officer & Williamson), Annual CPI for the U.S., 1774-Present (<https://www.measuringworth.com/datasets/uscpi/export.php?year_source=1774&year_result=2025>)
- `fig8-4.csv`: World Bank API, country list (<https://api.worldbank.org/v2/country?format=json&per_page=400>); World Bank, World Development Indicators (<https://api.worldbank.org/v2/country/all/indicator/FP.CPI.TOTL.ZG?format=json>); World Bank, World Development Indicators (<https://api.worldbank.org/v2/country/all/indicator/FM.LBL.BMNY.ZG?format=json>); World Bank, A Global Database of Inflation (Ha, Kose & Ohnsorge) (<https://thedocs.worldbank.org/en/doc/1ad246272dbbc437c74323719506aa0c-0350012021/original/Inflation-data.xlsx>)
- `fig8-5.csv`: FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=TB3MS>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL>)
- `fig8-6.csv`: World Bank, A Global Database of Inflation (Ha, Kose & Ohnsorge) (<https://thedocs.worldbank.org/en/doc/1ad246272dbbc437c74323719506aa0c-0350012021/original/Inflation-data.xlsx>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGARG>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGBRA>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGRUS>)
- `fig8-7.csv`: World Bank, A Global Database of Inflation (Ha, Kose & Ohnsorge) (<https://thedocs.worldbank.org/en/doc/1ad246272dbbc437c74323719506aa0c-0350012021/original/Inflation-data.xlsx>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGVEN>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGMEX>); FRED, Federal Reserve Bank of St. Louis (<https://fred.stlouisfed.org/graph/fredgraph.csv?id=FPCPITOTLZGNGA>)

## Wider files built for the notebook

All five files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch08-inflation/data/`, folders `table8-1/raw/`, `fig8-3/raw/`, `table8-2/raw/`,
`ex15/raw/`, `fig8-2/raw/` and `fig8-6/raw/`). Run it with `python build_data.py --macro102 PATH`.

- `us_cpi.csv`: `year, cpi`. U.S. consumer price index, annual, 1982–84 = 100, 1774–2025 (252 years).
  - Source: MeasuringWorth, Officer and Williamson, "The Annual Consumer Price Index for the United States,
    1774–Present" (<https://www.measuringworth.com/datasets/uscpi/>).
  - Validation: rebased to 2022 = 100, it reproduces all ten cells of the textbook's Table 8.1 and macro102's
    `table8-1/data.csv` exactly.
  - Used for Table 8.1 and the "How much is that?" price converter (Figure 1).
- `us_money_prices.csv`: `year, m2, cpi`. U.S. M2 (billions of dollars) and the CPI (as above), annual, 1870–2025.
  - Sources: Jordà-Schularick-Taylor Macrohistory Database R6, variable `money` (U.S. broad money), for 1870–1958
    (<https://www.macrohistory.net/database/>); FRED `M2NS` (annual average of monthly M2, not seasonally adjusted)
    from 1959.
  - Validation: average annual growth over each decade reproduces `fig8-3.csv` exactly (largest difference 0.000).
  - Used to compute money growth and inflation over 5-, 10- and 20-year periods (Figure 3).
- `money_supply.csv`: `date, currency, monetary_base, m1, m2`. Billions of dollars, monthly, 1959-01 to 2026-08
  (812 months).
  - Sources: Federal Reserve Board via FRED: currency in circulation (`MBCURRCIR`), monetary base (`BOGMBASE`), M1
    (`M1SL`, seasonally adjusted) and M2 (`M2SL`, seasonally adjusted).
  - Validation: January 2023 equals macro102's `table8-2/data.csv` exactly. Known break: M1 jumps from 4,856 to
    16,313 billion dollars in May 2020, when the Federal Reserve moved savings deposits into M1.
  - Used to rebuild Table 8.2 for January 2023 and the latest month (Figure 3).
- `us_money_annual.csv`: `year, nominal_gdp, currency, m2`. Billions of dollars, annual, 1959–2025: nominal GDP
  (FRED `GDPA`), and calendar-year means of `MBCURRCIR` and `M2SL`.
  - Used for the velocity of M2, nominal GDP / M2 (1.16 to 2.18 over the period; Figure 3), and new currency as a
    percentage of GDP, a measure of the inflation tax (Figure 6).
- `inflation_panel.csv`: `iso3, country, year, inflation, source`. Annual CPI inflation, percent, for 200 World Bank
  economies (aggregates removed), 1960–2025, 10,842 rows.
  - Sources: World Bank WDI `FP.CPI.TOTL.ZG` (`source = WDI`, 9,151 rows); where the WDI has no value, the World Bank's
    Global Inflation Database (Ha, Kose & Ohnsorge), sheet `hcpi_a`, 1970–2024 (`source = GID`, 1,691 rows,
    <https://www.worldbank.org/en/research/brief/inflation-database>).
  - A few long WDI names are shortened (e.g. "Venezuela, RB" → "Venezuela", "Russian Federation" → "Russia",
    "Turkiye" → "Turkey"). `fig8-4.csv` keeps the WDI names.
  - Validation: the WDI rows reproduce `fig8-2.csv` exactly (share above 25 percent, largest difference 0.000); the
    filled panel reproduces `fig8-6.csv` and `fig8-7.csv` within 0.03 points in every year they share.
  - Known quirk: Zimbabwe's GID values for 2001–2008 are not credible (for example −72.7 percent in 2007, during the
    hyperinflation); the notebook drops them (Figure 7).
  - Used for the country lists of Figures 1, 6 and 7, and for other thresholds and regions of "high inflation" (Figure 2).

## Multi-country files (conventions.md §6b)

Made by `build_data.py`, which downloads from the public sources (requests' default User-Agent) and caches the raw
responses in macro102's `.work/ch08/notebook-raw/`. The U.S. rows of each file are the textbook-figure series.

- `countries.csv`: `iso3, country, region, income, oecd`. The World Bank's 217 economies (aggregates removed), with
  their region, income group and OECD membership (38 members in 2026), 217 rows.
  - Source: World Bank API country list (<https://api.worldbank.org/v2/country?format=json&per_page=400>), saved by
    collect-data as `fig8-2/raw/wdi_country_list.json`; OECD membership typed in from <https://www.oecd.org/en/about/members-partners.html>.
  - Names are those of `inflation_panel.csv`. The WDI region "Middle East, North Africa, Afghanistan & Pakistan" is
    shortened to "Middle East & North Africa" (it still includes Afghanistan and Pakistan).
  - Used for the country colors and the region/OECD groups of Figure 2.
- `money_prices_panel.csv`: `iso3, country, year, money, cpi, source`. Broad money and the CPI (indexes in each
  country's own units, 6 significant digits), annual, 18 economies, 1870–2025, 2,521 rows.
  - Sources: Jordà-Schularick-Taylor Macrohistory Database R6, variables `money` and `cpi`
    (<https://www.macrohistory.net/database/>), 17 economies to 2020 (`source = JST`); the U.S. rows are
    `us_money_prices.csv` (JST to 1958, FRED `M2NS` after, MeasuringWorth CPI; `source = JST+FRED`), to 2025.
  - Validation: the U.S. decade growth rates reproduce `fig8-3.csv` exactly (largest difference 0.000).
  - Known gaps and quirks: Germany has no money data for 1923–1924 and 1939–1947, and its 1920s decade averages are
    1,139 percent (money) and 1,210 percent (CPI) a year; Belgium's money starts in 1979, Ireland's in 1922.
  - Used for Figure 3 (any of the 18 countries, any period length).
- `interest_rates_panel.csv`: `iso3, country, year, short_rate, inflation, real_rate, rate_source`. Annual 3-month
  nominal interest rate, CPI inflation and the ex-post real rate `short_rate − inflation`, percent, 50 economies
  (the OECD members and Argentina, Brazil, Bulgaria, China, Croatia, India, Indonesia, Peru, Romania, Russia,
  South Africa, Thailand), 1960–2025, 2,054 rows.
  - Sources: OECD Economic Outlook 119, short-term interest rate `IRS`
    (<https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.IRS.A>, `rate_source = OECD EO`); earlier years
    the EO lacks are added from the OECD's financial-market statistics, 3-month interbank rate `IR3TIB` (the series FRED
    shows as `IR3TIB01{CC}M156N`; <https://sdmx.oecd.org/public/rest/data/OECD.SDD.STES,DSD_STES@DF_FINMARK,/.A.IR3TIB......>,
    `rate_source = OECD MEI`), but only when the two agree within 0.5 points where they overlap (e.g. Germany 1960–1990).
    Inflation is the CPI inflation of `inflation_panel.csv`. The U.S. rows are `fig8-5.csv` (Treasury-bill rate `TB3MS`,
    `rate_source = FRED TB3MS`).
  - Validation: the U.S. real rate reproduces `fig8-5.csv` (largest difference 0.001). The OECD's own U.S. 3-month rate
    is on average 0.59 points above the Treasury-bill rate: the other countries' rates are money-market rates, a slightly
    different concept from the textbook's Treasury bill.
  - Known quirks: Argentina 2025 has no inflation (one row with an empty real rate); Russia's rate stops in 2021. With
    inflation in the hundreds of percent, `i − π` is a poor approximation of the real rate (Argentina 2024: −164).
  - Used for Figure 5 (a menu of the 50 economies).
