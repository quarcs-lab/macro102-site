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

All wider files are made by `build_data.py`; the multi-country files are listed in the next section.

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

## Multi-country files (conventions §6b)

Made by `build_data.py` (`python build_data.py --macro102 PATH`, add `--refresh` to download again). Raw downloads are
cached in `PATH/.work/ch20/notebook-raw/`. Every file is tidy and long, one row per economy and period, with the ISO
3166 alpha-3 code and the readable name of `countries.csv` (`EMU` = euro area). Each file reproduces the U.S. or
textbook-country rows of the matching `fig20-*.csv`; `build_data.py` prints the largest difference.

- `countries.csv` — 224 economies: `iso3`, `country`, `region` (World Bank region; "Middle East & North Africa" is the
  World Bank's "Middle East, North Africa, Afghanistan & Pakistan"), `income` (World Bank income group), `oecd`
  (member in 2026), `euro_since` (year of euro adoption, Bulgaria 2026). Source: World Bank country API
  (<https://api.worldbank.org/v2/country?format=json&per_page=400>), plus Taiwan, the euro area, Anguilla, Montserrat
  and three former economies (Netherlands Antilles, Czechoslovakia, Yugoslavia) that appear in the IMF and PWT data.
- `fx_monthly.csv` (Figure 1) — 14,132 rows, 25 currencies, 1971-01 to 2026-09: `iso3`, `country`, `currency`,
  `date` (YYYY-MM), `per_usd` (units of the currency per U.S. dollar, monthly average, 5 significant digits).
  Source: Federal Reserve H.10 via FRED, series `EXJPUS`, `EXUSEU`, `EXUSUK`, `EXCAUS`, `EXSZUS`, `EXCHUS`, `EXKOUS`,
  `EXINUS`, `EXMXUS`, `EXBZUS`, `EXSDUS`, `EXNOUS`, `EXDNUS`, `EXUSAL`, `EXUSNZ`, `EXHKUS`, `EXSIUS`, `EXTAUS`,
  `EXTHUS`, `EXMAUS`, `EXSLUS`, `EXSFUS` and the legacy `EXGEUS`, `EXFRUS`, `EXITUS` (to 2001-12); the series quoted in
  dollars per unit (euro, pound, Australian and New Zealand dollars) are inverted. Validation: the yen and euro rows
  equal `fig20-1.csv` (largest relative gap 7e-5, rounding).
- `inflation_wdi.csv` (Figure 2) — 9,217 rows, 194 economies, 1960–2025: `iso3`, `country`, `year`, `inflation`
  (consumer prices, percent per year). Source: World Bank WDI `FP.CPI.TOTL.ZG`. Validation: U.S. and Japan equal
  `fig20-2.csv` (largest gap 0.001 points). Quirk: Argentina only from 2018.
- `rer_pwt.csv` (Figure 3) — 11,201 rows, 185 economies, 1950–2023: `iso3`, `country`, `year`, `rer` = pl_gdpo /
  pl_gdpo of the U.S. in the same year (price level of GDP relative to the U.S.; U.S. = 1). Source: Penn World Table
  11.0 (<https://doi.org/10.34894/FABVLR>), read from macro102's bulk cache `.work/downloads/pwt110.dta` or downloaded
  from DataverseNL. Validation: Japan, 1971 = 100, equals `fig20-3.csv` (largest gap 0.015). Quirk: Bermuda's value
  for 2000 (1,059) is an error in PWT.
- `fx_history.csv` (Figure 6) — 2,514 rows, 17 economies, 1870–2020: `iso3`, `country`, `year`, `per_usd` (units of
  the national currency per U.S. dollar, 5 significant digits; euro countries in their legacy currency, older
  currencies converted at most currency reforms, so Germany's rates before 1923 are in Reichsmarks, 4.2e-12 in 1913).
  Source: Jordà-Schularick-Taylor Macrohistory Database, Release 6, variable `xrusd`
  (<https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.xlsx>; the file is a Stata .dta despite its
  name). Validation against `fig20-6.csv` (MeasuringWorth): median relative gap 0.1 percent, but 49 of 151 years
  differ by more than 2 percent: JST records 0.33–0.42 pounds per dollar in 1946–1951 (official parity 0.248, then
  0.357) and end-of-year rates from 1971 (2008: 0.69 against the 0.54 annual average).
- `fx_crises.csv` (Figure 8) — 6,708 rows, 210 economies, 1990–2025: `iso3`, `country`, `year`, `per_usd_eop`
  (national currency per U.S. dollar, end of period, 6 significant digits). Source: IMF Exchange Rates dataset (IFS
  successor), SDMX 2.1, key `.XDC_USD.EOP_RT.A` (<https://api.imf.org/external/sdmx/2.1/data/IMF.STA,ER/.XDC_USD.EOP_RT.A?startPeriod=1990>);
  IMF code G163 = euro area, KOS = Kosovo. Validation: Argentina, Korea, Mexico, Indonesia, 1991 = 100, equal
  `fig20-8.csv` (largest gap 0.005). Quirks: euro members stop when they adopt the euro; Venezuela is the official
  rate (to 2017); Zimbabwe joins three different currencies without conversion (to 2008, 2019–2023, from 2024).
- `yields_monthly.csv` (Figure 9) — 15,387 rows, 42 economies, 1990-01 to 2026-09: `iso3`, `country`, `date`
  (YYYY-MM), `yield` (10-year government bond yield, percent), `source`. Sources: OECD Main Economic Indicators via
  FRED `IRLTLT01{CC}M156N` for 34 countries (AT AU BE CA CH CL CZ DE DK ES FI FR GB GR HU IE IL IS IT JP KR LU MX NL
  NO NZ PL PT RU SE SI SK US ZA); Eurostat `irt_lt_mcby_m` (EMU convergence-criterion bond yields) for the EU members
  without an OECD series on FRED: Bulgaria, Croatia, Cyprus, Estonia, Latvia, Lithuania, Malta, Romania. Validation:
  Germany, Spain, Italy equal `fig20-9.csv` (largest gap 0.0005 points). Quirks: Estonia only from 2020-06, Russia
  to 2018-06, Iceland to 2022-08, Mexico with gaps.
- `credit_wdi.csv` (Figure 10) — 6,138 rows, 188 economies, 1990–2025: `iso3`, `country`, `year`, `bank_credit`
  (private credit by deposit money banks, % of GDP, World Bank GFDD `GFDD.DI.01`, to 2021) and `private_credit`
  (domestic credit to the private sector, % of GDP, WDI `FD.AST.PRVT.GD.ZS`). Validation: the 1998/2002/2007
  `bank_credit` and 2023 `private_credit` of the six textbook countries equal `fig20-10.csv` (largest gap 0.000).
- `current_account_imf.csv` (Figure 11) — 7,866 rows, 197 economies, 1980–2025: `iso3`, `country`, `year`, `ca_gdp`
  (current account balance, % of GDP). Source: IMF World Economic Outlook (October 2026) via the DataMapper API,
  indicator `BCA_NGDPD` (<https://www.imf.org/external/datamapper/api/v1/BCA_NGDPD>); years after 2025 (projections)
  dropped; IMF code EURO = euro area, UVK = Kosovo, WBG = West Bank and Gaza. Validation: the four period averages
  of the six textbook countries equal `fig20-11.csv` (largest gap 0.005).
- `debt.csv` (Figure 12) — 5,861 rows, 195 economies, 1990–2025: `iso3`, `country`, `year`, `debt_oecd` (general
  government gross financial liabilities, % of GDP, OECD Economic Outlook `GGFLQ`, 37 countries and the euro area,
  the textbook's measure; <https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/.GGFLQ.A?startPeriod=1990>)
  and `debt_imf` (general government gross debt, % of GDP, IMF WEO `GGXWDG_NGDP`). Years after 2025 dropped.
  Validation: `debt_oecd` of the six textbook countries equals `fig20-12.csv` (largest gap 0.000). The two measures
  differ (France 2017: 124.8 OECD, 98.8 IMF).
- `ulc_oecd.csv` (Figure 13) — 1,350 rows, 43 countries and the euro area (EA20), 1990–2025: `iso3`, `country`,
  `year`, `ulc` (unit labour costs, total economy, employment based, index 2020 = 100). Source: OECD Productivity
  Database, key `.A.ULCE._T.XDC.V.IX._Z._Z`
  (<https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PDB@DF_PDB,/.A.ULCE._T.XDC.V.IX._Z._Z?startPeriod=1990>).
  Validation: the five textbook countries, rebased to 1995 = 100, equal `fig20-13.csv` (largest gap 0.006).
- `tfp_pwt.csv` (Figure 14) — 6,988 rows, 120 economies, 1954–2023: `iso3`, `country`, `year`, `rtfpna` (TFP at
  constant national prices, 2021 = 1). Source: Penn World Table 11.0. Validation: the six textbook countries, 2000 =
  100, equal `fig20-14.csv` (largest gap 0.013).
