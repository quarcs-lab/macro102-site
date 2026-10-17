# Data for Appendix C: Math Review for Macroeconomics

Read by `notebooks/appC-math-review-for-macroeconomics.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appC/`.

Appendix C reviews the mathematical tools of the book (percentages, exponential growth, logarithms, growth
rates, approximations, derivatives, optimization, equations, difference and differential equations, present
value, and descriptive statistics) and applies each one to real data that the chapters also use.
`build_data.py` copies the seven files it needs, unchanged, from the `data/` folders of the chapters in this
site repo, so the notebook reads everything from its own `DATA_URL`. Run it with
`python build_data.py [--site PATH]`. It checks that each copy is byte-identical to its source, has the expected
columns, and has no missing values in the key columns. Full definitions, sources and validations are in the
README of each source folder.

- `fig3-2.csv`: `year, gdppc`, 1870–2025 (156 rows). U.S. GDP per person in 2022 dollars. Copied from
  `data/ch03/fig3-2.csv`.
  - Sources: BEA real GDP (`GDPCA`), population (`B230RC0A052NBEA`) and the GDP deflator (`A191RD3A086NBEA`) via
    FRED from 1929; the Maddison Project Database 2023 (Bolt and van Zanden 2024), ratio-spliced at 1929, for
    1870–1928.
  - Used for logarithms and the ratio scale (C.4), average growth rates (C.5) and the fitted trend (C.13).
- `nipa_annual.csv`: one row per year, 1929–2025 (97 rows), 27 columns. Copied from `data/ch02/nipa_annual.csv`.
  The appendix uses `gdp` (nominal GDP, billions of dollars, BEA `GDPA`), `real_gdp` (billions of chained 2017
  dollars, `GDPCA`) and `population` (thousands, `B230RC0A052NBEA`), all via FRED.
  - Used for nominal versus real GDP and the implicit deflator (C.2), the growth rules (C.5), and the volatility
    of growth (C.13).
- `us_cpi.csv`: `year, cpi`, 1774–2025 (252 rows). U.S. consumer price index, 1982–84 = 100. Copied from
  `data/ch08/us_cpi.csv`.
  - Source: MeasuringWorth, Officer and Williamson, "The Annual Consumer Price Index for the United States,
    1774–Present" (<https://www.measuringworth.com/datasets/uscpi/>).
  - Used for index numbers and inflation (C.2) and the Phillips-curve correlation (C.13).
- `interest_rates_panel.csv`: `iso3, country, year, short_rate, inflation, real_rate, rate_source`, 50 economies,
  1960–2025 (2,054 rows). Copied from `data/ch08/interest_rates_panel.csv`. Annual 3-month nominal interest rate,
  CPI inflation and `real_rate = short_rate − inflation`, percent.
  - Sources: OECD Economic Outlook 119 (`IRS`) and OECD financial-market statistics (`IR3TIB`); the U.S. rows are
    the Treasury-bill rate `TB3MS` via FRED. Inflation from the World Bank and the Global Inflation Database (see
    `data/ch08/README.md`).
  - Known quirk: Argentina 2025 has no inflation (an empty real rate). The appendix uses Argentina and the United
    States to show when `i − π` is a good approximation of the real interest rate (C.6).
- `fig9-2.csv`: `year, gdp_actual, gdp_potential`, 1929–2025 (97 rows). U.S. real GDP and potential GDP,
  trillions of 2022 dollars. Copied from `data/ch09/fig9-2.csv`.
  - Sources: BEA (`GDPCA`) and CBO potential GDP (`GDPPOT`) via FRED. For 1929–1948 the potential series is a
    smooth trend, so the appendix uses 1950–2025 for trend-versus-cycle comparisons.
  - Used for the output gap as a log difference (C.6) and the trend and cycle (C.13).
- `fig18-2.csv`: `year, surplus_gdp_pct, debt_public_gdp_pct`, FY1934–FY2025 (92 rows). U.S. federal surplus (+)
  or deficit (−) and federal debt held by the public, percent of GDP (debt empty before FY1940). Copied from
  `data/ch18/fig18-2.csv`.
  - Source: OMB Historical Tables, FY2027 Budget, Tables 1.2 and 7.1.
  - Used for the starting point of the debt-ratio simulation (C.10).
- `fig17-3.csv`: `date, cape, cape_average`, monthly 1881-01 to 2026-10 (1,750 rows). Shiller's cyclically
  adjusted price-earnings ratio and its full-sample mean. Copied from `data/ch17/fig17-3.csv`.
  - Source: Robert Shiller, `ie_data.xls` (<http://www.econ.yale.edu/~shiller/data.htm>); the latest months are
    preliminary.
  - Used for the earnings yield as the present-value formula for a stock (C.12).
