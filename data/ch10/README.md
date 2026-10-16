# Data for Chapter 10: The Great Recession and the Covid-19 Pandemic: A First Look

Read by `notebooks/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch10/`.

## Files copied from the macro102 collect-data output

- `fig10-1.csv`: `date, real_home_price_index`. Robert Shiller's real U.S. home price index (nominal index deflated by the CPI; from 1987 the S&P CoreLogic Case-Shiller national index), rebased so that the 1953 average is 100. Monthly, 1953-01 to 2026-07.
  - Source: Shiller, "U.S. Home Price and Related Data" (`Fig3-1.xls`), shillerdata.com.
  - Known quirk: two numbers in the textbook's prose ("a factor of nearly 3 between 1996 and 2006", "collapsing by more than 40 percent") do not come from this index (real ×1.72 and −35.7%).
- `fig10-2.csv`: `date, fed_funds`. Effective federal funds rate, percent, monthly average of daily rates, 2000-01 to 2026-09 (FRED `FEDFUNDS`).
  - The textbook's "1.25 to 5.25 percent" are the Fed's target rates; the effective monthly rate was 1.00 in May 2004 and 4.94 in May 2006.
- `fig10-3.csv`: `date, ted_spread, cp_tbill_spread`. Interest-rate spreads, percentage points, monthly means of daily data, 2000-01 to 2026-09.
  - `ted_spread`: 3-month LIBOR minus the 3-month Treasury bill (FRED `TEDRATE`). It ends in 2022-01, when U.S. dollar LIBOR was discontinued.
  - `cp_tbill_spread`: 90-day AA financial commercial paper (`RIFSPPFAAD90NB`) minus the 3-month Treasury bill (`DTB3`), a comparable bank-funding spread that continues after 2022 (correlation with the TED spread 0.97 over 2000–2022). Empty for 2020-04 (no commercial-paper observations that month).
- `fig10-4.csv`: `date, sp500_real`. Real S&P 500 composite price index, in September 2026 dollars (nominal index × CPI of 2026-09 / CPI of the month), monthly, 1990-01 to 2026-09.
  - Source: Shiller, "U.S. Stock Market Data" (`ie_data.xls`), shillerdata.com. Levels are 1.115 times the textbook's, which uses February 2023 dollars.
- `fig10-5.csv`: `iso3, country, deaths_pm_2023_03_22, gdp_loss_2022q3, deaths_pm_2026_08_30, gdp_loss_2026q2`. One row per country (48 OECD and partner economies).
  - `deaths_pm_*`: cumulative confirmed Covid-19 deaths per million people on the textbook's date (2023-03-22) and on the latest date (2026-08-30); Our World in Data, from the WHO Covid-19 dashboard.
  - `gdp_loss_*`: cumulative real-GDP shortfall below the 2019Q4 level, summed over the quarters from 2020Q1 to 2022Q3 (the textbook's end) or 2026Q2, in percent of one year's GDP; OECD Quarterly National Accounts.
  - Known quirks: national-accounts revisions since 2023 lower several GDP losses (United States 3.3 against the textbook's 3.7); Chile's cumulative deaths fall between the two dates (a WHO revision).
- `fig10-6.csv`: `date, gdp_index_usa, gdp_index_kor, gdp_index_swe, gdp_index_deu, gdp_index_gbr, gdp_index_esp`. Real GDP, index 2019Q4 = 100, quarterly, 2019Q4 to 2026Q2 (OECD Quarterly National Accounts, chain-linked volumes, seasonally adjusted; replaces the discontinued OECD MEI series on FRED).
- `fig10-7.csv`: `date, nonfarm_emp`. Total nonfarm payroll employment, millions, monthly, seasonally adjusted, 2000-01 to 2026-09 (BLS via FRED `PAYEMS`).
- `fig10-8.csv`: `date, short_run_output, short_run_output_vintage2023`. Short-run output, 100 × (real GDP / potential GDP − 1), percent, quarterly, 2000Q1 to 2026Q2.
  - `short_run_output`: current BEA real GDP (`GDPC1`) and CBO potential GDP (`GDPPOT`).
  - `short_run_output_vintage2023`: the same with the data as published on 2023-02-01 (ALFRED), to 2022Q4. It reproduces the textbook's figure (2020Q2: −10.42 against −8.83 today).
- `fig10-9.csv`: `date, unemp_rate`. Civilian unemployment rate, percent, monthly, seasonally adjusted, 2000-01 to 2026-09 (BLS via FRED `UNRATE`). October 2025 has no row: the survey was not run during the federal government shutdown.
- `fig10-10.csv`: `date, inflation_us, inflation_uk, inflation_euro_area`. 12-month CPI inflation, 100 × ln(P_t / P_t−12), monthly, 2015-01 to 2026-09.
  - Sources: U.S. CPI-U (`CPIAUCNS`, FRED); U.K. CPIH (OECD prices database); euro-area HICP (Eurostat `prc_hicp_minr`).
  - Log changes reproduce the textbook's figure; simple percent changes peak a little higher (U.S. 9.06 against 8.67). U.S. October 2025 is empty (no CPI collected in the shutdown); the U.K. stops in 2026-08.
- `fig10-11.csv`: `date, core_inflation_us, core_inflation_uk, core_inflation_euro_area`. 12-month core inflation (excluding food and energy), log changes as above, monthly, 2015-01 to 2026-09 (U.S. `CPILFENS`; U.K. CPIH excluding food and energy, OECD; euro area HICP excluding energy, food, alcohol and tobacco, Eurostat). Same gaps as `fig10-10.csv`.

Full definitions, vintages and the validation against the textbook are in macro102's
`original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/figN-k/notes.md`.

## Wider files built for the notebook

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch10-the-great-recession-and-the-covid-19-pandemic-a-first-look/data/`, folders
`fig10-2/raw/` and `table10-1/raw/`). Run it with `python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough, peak_quarter, trough_quarter`. The 11 NBER recessions that start in 1953 or later, from 1953-07 / 1954-05 to 2020-02 / 2020-04 (first day of the month or quarter).
  - Source: NBER-based recession indicators `USREC` (monthly) and `USRECQ` (quarterly) via FRED. `peak` is the period before the first recession period, `trough` the last recession period.
  - The monthly dates shade the recessions in Figures 2, 3, 7, 8 and 9; the quarterly dates define the episodes of Table 10.1 (the NBER dates quarters separately, e.g. the Covid-19 recession runs from 2019Q4 to 2020Q2).
- `us_quarterly.csv`: `date, gdp, consumption, investment, government, exports, imports, employment, unemployment`. Quarterly, 1953Q1 to 2026Q2 (294 quarters, no missing values).
  - `gdp` to `imports`: real GDP, personal consumption expenditures, gross private domestic investment, government consumption and investment, exports and imports, billions of chained 2017 dollars, seasonally adjusted annual rates (BEA via FRED: `GDPC1`, `PCECC96`, `GPDIC1`, `GCEC1`, `EXPGSC1`, `IMPGSC1`).
  - `employment`: quarterly mean of nonfarm payroll employment, millions (`PAYEMS`); `unemployment`: quarterly mean of the unemployment rate, percent (`UNRATE`; 2025Q4 averages the two months that exist).
  - Validation: the peak-to-trough changes computed from these two files reproduce collect-data's `table10-1/data.csv` (current vintage) within 0.005 points.
  - Used to recompute Table 10.1 in the section of Figure 9.

## Multi-country files (conventions §6b)

Made by `build_data.py` from public APIs (requests' default User-Agent; raw responses cached in macro102's
`.work/ch10/notebook-raw/`, `--refresh` downloads them again). All are tidy and long: one row per economy and
period, `iso3, country, date|year, values...`, with the country names of `fig10-5.csv` (e.g. "S. Korea",
"Türkiye") and `EMU` for the euro area. Each file's U.S. rows are validated against the textbook-figure CSV
(the numbers are printed by `build_data.py`).

- `countries.csv`: `iso3, country, region`. The 62 economies used below, with a region (Americas, Europe, Asia and
  Pacific, Africa and Middle East) for the website menus.
- `house_prices_panel.csv`: `iso3, country, date, real_house_price`. BIS residential property prices, real (deflated
  by the CPI), index 2010 = 100, quarterly (date = first day of the quarter), 58 economies, from 1947Q1 (Italy) or
  later to 2026Q2; 8,841 rows, 266 kB.
  - Source: BIS data portal, dataset WS_SPP, key `Q.{country}.R.628` (<https://stats.bis.org/api/v1/data/WS_SPP/Q..R.628/all?format=csv>);
    the same series are on FRED as `Q{CC}R628BIS`. The BIS aggregates (advanced, emerging, world) are dropped.
  - Validation: the U.S. bust of the 2000s is −38.9% in the BIS index and −35.3% in Shiller's index of
    `fig10-1.csv` (quarterly means); correlation of 4-quarter changes 0.93. The BIS uses a different U.S. index.
- `policy_rates_panel.csv`: `iso3, country, date, policy_rate`. Central bank policy rates, percent, **end of month**,
  monthly, 41 economies, 2000-01 to 2026-09; 12,413 rows, 355 kB.
  - Source: BIS dataset WS_CBPOL (<https://stats.bis.org/api/v1/data/WS_CBPOL/M./all?format=csv&startPeriod=1999-01>).
  - Definitions change over time: U.S. = middle of the Fed's target range; euro area = ECB main refinancing rate
    until 17 September 2024, deposit facility rate since. Greece stops in 2000 (euro), Argentina in 2025-06.
  - Validation: U.S. rows vs the effective fed funds rate of `fig10-2.csv`: correlation 0.998, median gap 0.04 points.
- `interbank_spreads_panel.csv`: `iso3, country, date, interbank_3m, overnight, spread`. 3-month interbank rate,
  overnight (call money) interbank rate and their difference, percent and percentage points, monthly averages,
  35 economies, 2000-01 to 2026-09; 9,326 rows, 375 kB.
  - Source: OECD Financial market statistics, dataflow `OECD.SDD.STES,DSD_STES@DF_FINMARK,4.0`, measures `IR3TIB`
    and `IRSTCI`.
  - A **different concept** from the TED spread of `fig10-3.csv` (LIBOR minus the Treasury bill): a term premium
    within the interbank market, which also moves with expected policy-rate changes. Euro-area members are kept
    only for months in which their rates differ from the euro area's (i.e. before they adopted the euro).
  - Validation: U.S. spread vs TED spread: correlation 0.67 (2000–2022), 0.78 (2007–2009); both peak in October
    2008 (2.22 vs 3.35 points).
- `share_prices_panel.csv`: `iso3, country, date, real_share_price`. OECD share price index (broad index, monthly
  average) divided by the national CPI, index 2015 = 100, monthly, 45 economies, 1990-01 to 2026-09; 18,336 rows,
  529 kB.
  - Sources: OECD dataflow `DSD_STES@DF_FINMARK` (measure `SHARE`); IMF Consumer Price Index dataset
    `IMF.STA:CPI`, key `{country}.CPI._T.IX.M` (<https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/+/*.CPI._T.IX.M>).
  - Data hygiene: an economy whose real index jumps more than threefold in one month is kept only from its last
    jump: Brazil from 1993-01 (currency reforms), Slovenia from 1994-06 (index rebased).
  - Validation: U.S. October 2007 to March 2009: −54.1% vs −51.7% for Shiller's real S&P 500 (`fig10-4.csv`).
- `gdp_quarterly_panel.csv`: `iso3, country, date, gdp_index`. Real GDP, index 2019Q4 = 100, quarterly, 49 economies,
  2019Q4 to 2026Q2; 1,304 rows, 41 kB.
  - Source: the OECD Quarterly National Accounts download of collect-data
    (`fig10-5/raw/oecd_qna_gdp_volume_index.csv`, chain-linked volumes, seasonally adjusted). China publishes no
    level index there and is missing; Russia stops in 2021Q3.
  - Validation: the six textbook countries equal `fig10-6.csv` (largest difference 0.0000).
- `employment_panel.csv`: `iso3, country, date, employment`. Employed persons aged 15 and over, thousands, labour
  force surveys, seasonally adjusted, quarterly, 45 economies, 2000Q1 to 2026Q3; 4,377 rows, 135 kB.
  - Source: OECD Infra-annual labour statistics, dataflow `OECD.SDD.TPS,DSD_LFS@DF_IALFS_EMP_Q,1.0`, key
    `.EMP.PS._Z.Y._T.Y_GE15._Z.Q`. Brazil stops in 2015Q3 and Indonesia in 2013Q1.
  - A household survey, not the payroll survey of `fig10-7.csv`. Validation: correlation of 4-quarter changes 0.97;
    2019Q4–2020Q2 −13.3% vs −11.8% for payrolls.
- `output_gap_panel.csv`: `iso3, country, year, output_gap, projection`. Output gap, percent of potential GDP, annual,
  40 economies, 1990 to 2027; `projection` is True for 2026–2027; 1,419 rows, 41 kB.
  - Source: OECD Economic Outlook 119 (June 2026), dataflow `OECD.ECO.MAD,DSD_EO@DF_EO,1.5`, measure `GAP`.
  - Validation: U.S. OECD gap vs the yearly mean of the CBO-based short-run output of `fig10-8.csv`: correlation
    0.86; 2009 −4.0 vs −4.7; 2020 −4.2 vs −3.3 (different estimates of potential output).
- `unemployment_panel.csv`: `iso3, country, date, unemployment_rate`. Harmonised unemployment rate, percent of the
  labour force, seasonally adjusted, monthly, 40 economies, 2000-01 to 2026-09; 12,347 rows, 342 kB.
  - Source: OECD dataflow `OECD.SDD.TPS,DSD_LFS@DF_IALFS_UNE_M,1.0`, key `.UNE_LF_M.PT_LF_SUB._Z.Y._T.Y_GE15._Z.M`.
  - Validation: U.S. rows equal BLS `UNRATE` in `fig10-9.csv` (largest difference 0.00 over 320 months).
- `inflation_panel.csv`: `iso3, country, date, inflation, core_inflation, source`. 12-month inflation as log changes,
  100 ln(P_t / P_t−12), headline and core (excluding energy and food), monthly, 61 economies (46 with core),
  2015-01 to 2026-09; 8,409 rows, 437 kB. `source` names the source of each row:
  - `textbook figure (fig10-10, fig10-11)`: the U.S., the U.K. and the euro area, copied exactly;
  - `Eurostat HICP`: 33 other European economies, HICP all items and HICP excluding energy, food, alcohol and
    tobacco (`prc_hicp_minr`, unit I25, `coicop18` TOTAL and TOT_X_NRG_FOOD);
  - `IMF CPI; core: OECD`: 25 other economies, IMF national CPI (`IMF.STA:CPI`) and, where available, the OECD's CPI
    excluding food and energy (`OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0`, expenditure `_TXCP01_NRG`).
  - Gaps: Australia's monthly CPI starts in 2024-04 (so inflation in 2025-04); the OECD's Japanese core index stops
    in 2021-06; Argentina's IMF index starts in 2016-12; New Zealand has no monthly CPI and is missing.
  - Validation: our own Eurostat euro-area HICP and IMF U.S. CPI reproduce `fig10-10.csv` within 0.010 and 0.000 points.
