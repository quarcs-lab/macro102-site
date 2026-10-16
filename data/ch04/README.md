# Data for Chapter 4: A Model of Production

Read by `notebooks/ch04-a-model-of-production.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch04/`.

## Files copied from the macro102 collect-data output

The Penn World Table files use PWT 11.0 (Feenstra, Inklaar & Timmer; GGDC, <https://doi.org/10.34894/FABVLR>).
Capital is **not** PWT's own capital stock: it is built by perpetual inventory from investment, which
is the method that reproduces the textbook (see `pwt_production.csv` below). "Relative" means U.S. = 1.

- `fig4-3.csv`: `date, sp500_real`. Monthly, 1920-01 to 2026-09. This is the real S&P 500 index in September 2026 dollars, i.e. the nominal index × CPI(latest) / CPI(month).
  - Sources: Robert Shiller's U.S. stock market data (datahub.io mirror, <https://github.com/datasets/s-and-p-500>), extended from 2023-09 with FRED `SP500` (monthly average of daily closes) and `CPIAUCNS`.
- `fig4-4.csv`: `iso3, country, capital_pc_rel_2023, pred_gdp_pc_2023`. Relative capital per person and the prediction $y^* = k^{1/3}$ for the textbook's eight countries, 2023.
- `fig4-5.csv`: `iso3, country, gdp_pc_rel_2023, pred_gdp_pc_2023`. Actual and predicted relative GDP per person, 2023, for the 111 countries with data since 1960.
- `fig4-6.csv`: `iso3, country, capital_pc_rel_2023, gdp_pc_rel_2023, tfp_2023, gdp_pc_with_us_tfp_2023` for the United States and China, 2023.
- `fig4-7.csv`: `iso3, country, gdp_pc_rel_2023, tfp_2023`. Relative GDP per person and implied TFP $\bar{A} = y / k^{1/3}$, 2023, for the same 111 countries.
- `fig4-9.csv`: `year, gdp_pc_china, gdp_pc_russia`. GDP per person (rgdpo/pop, 2021 US$), 1990–2023.

## Wider file built for the notebook widgets

- `pwt_production.csv`: `iso3, country, year, gdp_pc, k_pc, y_rel, k_rel, tfp, in_sample`. One row per country and year, 1950–2023, for 185 countries (11,201 rows).
  - **Construction.** `build_data.py` builds it from the PWT 11.0 subset saved by macro102's `/collect-data` (`rgdpo, pop, csh_i`).
    - `gdp_pc` is rgdpo/pop in 2021 US$.
    - `k_pc` is capital per person: $I = \text{csh\_i} \times \text{rgdpo}$, then $K_{first} = I/(0.03+0.05)$ and $K_{t+1} = 0.95K_t + I_t$, with the stock measured at the start of the year.
    - `y_rel` and `k_rel` divide by the U.S. value of the same year, and `tfp` $= y_{rel}/k_{rel}^{1/3}$.
    - `in_sample` marks the countries with data in 1960 and in that year, which gives 111 countries in every year 1960–2023.
  - **Validation.** In 2023 it reproduces `fig4-4.csv`, `fig4-5.csv`, `fig4-6.csv` and `fig4-7.csv` to within 0.00003, and `fig4-9.csv` exactly.
  - **Known quirks:**
    - Venezuela's 2023 GDP per person (about $160) is not plausible, because hyperinflation broke the PWT price data. The notebook finds it with a quick look at the data and drops it, as a data-cleaning example.
    - Capital in the first years after a country's data begin depends heavily on the starting guess $K_{first}$. The notebook therefore uses years from 1980 on.

## Multi-country files (conventions §6b)

Made by `build_data.py`; downloads are cached in `../macro102/.work/ch04/notebook-raw/`.

- `share_prices.csv`: `iso3, country, date, real_index`. Monthly real share prices, 2015 average = 100, for 40 countries (the OECD members whose index is on FRED plus Brazil, China, India, Indonesia, Russia and South Africa), 1950-03 to 2026-08, 24,166 rows (652 KB).
  - Sources: OECD Main Economic Indicators "Total share prices for all shares" via FRED, `SPASTT01{CC}M661N` (index 2015 = 100), deflated by the BIS long consumer price series (`https://stats.bis.org/api/v1/data/WS_LONG_CPI/M..628?format=csv`, index). FRED's own OECD CPI indices (`CPALTT01{CC}M661N`, `{ISO3}CPIALLMINMEI`) are discontinued or end in 2021–2025, so BIS is used for every country.
  - Cleaning: months that FRED codes as 0 are dropped (Slovenia 1994); Brazil starts in 1993-01 because its index jumps 50-fold in January 1993 (a rebasing, not a boom). Values have 4 significant digits.
  - Coverage: from the 1950s for most early OECD members; from the 1990s for Central Europe, Chile, China (1999), Russia (2001) and others. Latvia, Lithuania, Colombia and Costa Rica have no series on FRED.
  - Validation against `fig4-3.csv` (U.S.): the OECD U.S. series (it follows the NYSE Composite) and the real S&P 500 have a correlation of monthly changes of 0.973 for 1957-01 to 2026-08, but average real growth of 2.94% vs 3.87% a year; the gap opened mostly after 2015 (4.2% vs 8.8% a year), as Nasdaq-listed technology firms lifted the S&P 500. The notebook explains this as a data lesson.
- `regions.csv`: `iso3, country, region, income_group`. The World Bank region and income group (`https://api.worldbank.org/v2/country?format=json&per_page=400`, trailing spaces stripped) of the 185 countries of `pwt_production.csv`, with PWT country names. Taiwan (East Asia & Pacific, high income), Anguilla and Montserrat (Latin America & Caribbean, high income) are not in the World Bank list and are added by hand. Used for the website region menus.
