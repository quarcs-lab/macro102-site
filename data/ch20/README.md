# Data for Chapter 20: Exchange Rates and International Finance

Read by `notebooks/ch20-exchange-rates-and-international-finance.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch20/`.

## Files copied from the macro102 collect-data output

Each file is `original-scanned-book/ch20-exchange-rates-and-international-finance/data/<id>/data.csv` of the macro102
repository; its `notes.md` there documents sources, transformations and the validation against the textbook.

- `fig20-1.csv` — monthly exchange rates, 1971-01 to 2026-09: `date`, `yen_per_usd` (FRED `EXJPUS`, yen per U.S.
  dollar), `eur_per_usd` (1 / FRED `EXUSEU`, euros per dollar, from 1999-01; empty before).
  Source: Federal Reserve H.10 via FRED (<https://fred.stlouisfed.org/series/EXJPUS>, <https://fred.stlouisfed.org/series/EXUSEU>).
- `fig20-2.csv` — annual CPI inflation in percent, 1960–2025: `year`, `inflation_us` (FRED `FPCPITOTLZGUSA`, to 2024;
  2025 empty), `inflation_jpn` (FRED `FPCPITOTLZGJPN`, to 2025). Source: World Bank WDI via FRED.
- `fig20-3.csv` — Japan's real exchange rate, 1971–2023: `year`, `rer_jpn` = pl_gdpo(JPN) / pl_gdpo(USA), index
  1971 = 100. Source: Penn World Table 11.0 (<https://doi.org/10.34894/FABVLR>).
- `fig20-6.csv` — pounds per U.S. dollar, annual, 1791–2025: `year`, `gbp_per_usd` (1 / dollars per pound).
  Source: MeasuringWorth, Dollar-Pound Exchange Rate From 1791 (<https://www.measuringworth.com/datasets/exchangepound/>).
- `fig20-8.csv` — dollar value of four currencies, 1991 = 100, annual, 1991–2025: `year`, `argentina`, `korea`,
  `mexico`, `indonesia` (national currency per dollar in 1991 / in year t × 100, end-of-period rates).
  Source: IMF Exchange Rates dataset (IFS successor), SDMX API.
- `fig20-9.csv` — 10-year government bond yields in percent, monthly, 1995-01 to 2026-09: `date`, `yield_de`,
  `yield_es`, `yield_it` (Italy to 2026-08). Source: OECD via FRED (`IRLTLT01DEM156N`, `IRLTLT01ESM156N`, `IRLTLT01ITM156N`).
- `fig20-10.csv` — domestic bank credit to the private sector, percent of GDP, one row per country (Greece, Ireland,
  Portugal, Spain, Italy, Germany): `iso3`, `country`, `credit_gdp_1998`, `credit_gdp_2002`, `credit_gdp_2007`
  (World Bank GFDD `GFDD.DI.01`) and `credit_gdp_2023` (WDI `FD.AST.PRVT.GD.ZS`).
- `fig20-11.csv` — current account balance, percent of GDP, period averages, same six countries: `iso3`, `country`,
  `ca_gdp_1993_1997`, `ca_gdp_2003_2007`, `ca_gdp_2008_2011`, `ca_gdp_2021_2025`. Source: IMF World Economic Outlook,
  October 2026 (`BCA_NGDPD`).
- `fig20-12.csv` — general government gross debt, percent of GDP, for France, Germany, Greece, Ireland, Italy and Spain:
  `iso3`, `country`, `debt_gdp_2007`, `debt_gdp_2012`, `debt_gdp_2017`, `debt_gdp_2025`. Source: OECD Economic Outlook 119 (`GGFLQ`).
- `fig20-13.csv` — unit labour costs, index 1995 = 100, annual, 1995–2025: `year`, `ulc_grc`, `ulc_ita`, `ulc_esp`,
  `ulc_fra`, `ulc_deu`. Source: OECD Productivity Database (`ULCE`), rebased.
- `fig20-14.csv` — total factor productivity, index 2000 = 100, annual, 1990–2023: `year`, `tfp_usa`, `tfp_deu`,
  `tfp_jpn`, `tfp_fra`, `tfp_esp`, `tfp_ita` (PWT `rtfpna`, rebased). Source: Penn World Table 11.0.

## Wider files built for the notebook

- `big_mac.csv` — made by `build_data.py` (run `python build_data.py --macro102 PATH`), used for Table 20.1 and the
  Balassa-Samuelson scatter in Figures 2 and 3. One row per economy and Big Mac release: 2,056 rows, 56 economies,
  45 releases from 2000-04-01 to 2026-07-01.
  - Columns: `release` (date of the release), `iso3` (EUZ = euro area), `country`, `currency`, `local_price` (Big Mac
    price in local currency), `ex_rate` (local currency per U.S. dollar), `dollar_price` (local_price / ex_rate,
    dollars), `gdp_pc_2023` (real GDP per person in 2023, 2021 dollars; empty for the euro area and economies not in PWT).
  - Sources: The Economist, *The Big Mac index*, open data (`big-mac-raw-index.csv`,
    <https://github.com/TheEconomist/big-mac-data>), saved by macro102 in `table20-1/raw/`; Penn World Table 11.0
    (`rgdpo / pop`), the subset saved by macro102 for Chapter 5 in
    `original-scanned-book/ch05-the-solow-growth-model/data/fig5-3/raw/pwt110_subset.csv`.
  - Validation: the 2022-07-01 release reproduces macro102's `table20-1/data.csv` (the textbook's Table 20.1, which
    prints that release) exactly; `build_data.py` prints the largest difference (0.000).
  - Known quirks: India's row is the chicken Maharaja Mac; Venezuela's PWT GDP per person (159 dollars in 2023) is
    implausible and is dropped in the notebook.
