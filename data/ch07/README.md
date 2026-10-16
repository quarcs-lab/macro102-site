# Data for Chapter 7: The Labor Market, Wages, and Unemployment

Read by `notebooks/ch07-the-labor-market-wages-and-unemployment.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch07/`.

## Files copied from the macro102 collect-data output

- `fig7-1.csv`: `date, emp_pop_ratio`. U.S. civilian employment-population ratio (16+), percent, monthly, seasonally adjusted, 1960-01 to 2026-09.
  - Source: BLS Current Population Survey via FRED (`EMRATIO`).
  - Known gap: October 2025 is missing (not collected during the federal government shutdown).
- `fig7-2.csv`: `date, unemployment_rate`. U.S. civilian unemployment rate, percent, monthly, seasonally adjusted, 1950-01 to 2026-09.
  - Source: BLS via FRED (`UNRATE`). October 2025 is missing, as above.
- `fig7-7.csv`: `year, unrate_us, unrate_europe, unrate_japan`. Annual unemployment rates, percent, 1955–2025 (Europe from 1960).
  - Sources: BLS via FRED (`UNRATE`, calendar-year average); OECD via FRED (`LRHUTTTTJPA156S`); Europe = euro area of 12 countries from the European Commission's AMECO database (`DA12`/`EA12 .1.0.0.0.ZUTN`, <https://ec.europa.eu/economy_finance/db_indicators/ameco/documents/ameco1.zip>), a substitute for the textbook's OECD series (up to about 1 point lower in the mid-1980s).
- `fig7-8.csv`: `year, college_premium_log_pct, college_premium_pct, college_share_employment_pct`. 1976–2025 (premium from 1979).
  - `college_premium_pct`: regression-adjusted hourly wage premium of four-year college graduates over high school graduates, percent; `college_premium_log_pct` = 100 × ln(1 + premium), log points.
  - `college_share_employment_pct`: share of employment with a bachelor's or advanced degree, percent (persons; the textbook's line is a share of hours and is about twice as high).
  - Source: Economic Policy Institute, State of Working America Data Library (CPS), a substitute for the textbook's private Acemoglu–Molina series.
- `fig7-10.csv`: `date, manufacturing_emp_millions`. U.S. payroll employment in manufacturing, millions, monthly, seasonally adjusted, 1950-01 to 2026-09.
  - Source: BLS Current Employment Statistics via FRED (`MANEMP`).
- `fig7-11.csv`: `year, top01_share_us, top01_share_france`. Share of pre-tax national income received by the top 0.1 percent, percent; U.S. 1913–2024, France 1915–2022.
  - Source: World Inequality Database (WID.world) via Our World in Data (indicator 1290252). The U.S. value is identical (9.93) in 2022–2024: WID repeats its last estimate. The current vintage differs from the textbook's in a few years (U.S. 1950, France after 2015).
- `fig7-12.csv`: `year, start_year, series, percentile, group, growth_pct`. Average annual growth of real post-tax income per adult, percent, over 34-year windows.
  - `series = "g-percentile (PSZ 2018)"`: every percentile 1–99 plus the top percentiles 99.1 … 99.999, for 1946→1980 (`year` 1980) and 1980→2014 (`year` 2014). Source: Piketty, Saez & Zucman (2018 QJE), `PSZ2018MainData.xlsx`, sheet `TS11(NYT)`.
  - `series = "group average (PSZ 2022)"`: bottom 50%, middle 40%, top 10%, 1%, 0.1%, 0.01%, 0.001% for the same windows and 1985→2019, placed at their percentile midpoints in `percentile`. Source: PSZ Distributional National Accounts, Appendix Tables II (February 2022), sheet `TC3`.

## Wider files built for the notebook

All four files are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch07-the-labor-market-wages-and-unemployment/data/`, folders `fig7-1/raw/`,
`ex02/raw/`, `table7-1/raw/` and `table7-2/raw/`). Run it with
`python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough`. The 11 NBER business-cycle peaks and troughs whose trough is in 1950 or later (first day of the month), from 1953-07 / 1954-05 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month, `trough` the last recession month (the NBER's official dates).
  - Used to shade recessions in Figures 1, 2 and 10.
- `emp_pop_by_sex.csv`: `date, men, women`. Employment-population ratios of men and of women aged 16+, percent, monthly, seasonally adjusted, 1948-01 to 2026-09 (944 months; October 2025 missing).
  - Source: BLS via FRED (`LNS12300001`, `LNS12300002`).
  - Validation: identical to macro102's `ex02/data.csv`. Used to check the textbook's numbers for men and women (Figure 1).
- `labor_force.csv`: `date, population, labor_force, employed, unemployed, not_in_labor_force`. Millions of people, monthly, 1948-01 to 2026-09.
  - Source: BLS Current Population Survey via FRED: civilian noninstitutional population 16+ (`CNP16OV`, not seasonally adjusted), labor force (`CLF16OV`), employment (`CE16OV`), unemployment (`UNEMPLOY`); `not_in_labor_force` = population − labor force.
  - Validation: January 2023 reproduces macro102's `table7-1/data.csv` exactly, and 100 × unemployed / labor force reproduces `UNRATE` (`fig7-2.csv`) in every month to one decimal.
  - Used to rebuild Table 7.1 for January 2023 and the latest month (Figure 2).
- `hours_per_person.csv`: `country, year, hours_pwt11, hours_pwt10`. Annual hours worked per person (average hours × persons engaged / population), index U.S. 2019 = 100, 1950–2023 (PWT 10.01 to 2019), for the seven countries of Table 7.2 (South Korea from 1953).
  - Sources: Penn World Table 11.0 (`hours_pwt11`, <https://doi.org/10.34894/FABVLR>) and 10.01 (`hours_pwt10`, <https://doi.org/10.34894/QT5BCC>), variables `avh`, `emp`, `pop`.
  - Validation: `hours_pwt10` rounded to integers reproduces all 21 cells of the textbook's Table 7.2 and matches macro102's `table7-2/data.csv` within its rounding (0.05).
  - Used to rebuild Table 7.2 in both versions (Figure 7).

## Multi-country files (conventions §6b)

All are made by `build_data.py`. Downloads are cached in `../macro102/.work/ch07/notebook-raw/`. Readable
names and World Bank regions come from <https://api.worldbank.org/v2/country?format=json&per_page=400>.

- `emp_pop_countries.csv`: `iso3, country, region, year, emp_pop_ratio`. Employment-to-population ratio, ages 15+, percent, ILO modelled estimates, annual, 1991–2025, 187 countries, 6,531 rows.
  - Source: World Bank WDI `SL.EMP.TOTL.SP.ZS`, <https://api.worldbank.org/v2/country/all/indicator/SL.EMP.TOTL.SP.ZS?format=json&per_page=20000>.
  - Validation: the U.S. rows lie 0.1–1.1 points (0.7 on average) below the annual mean of `EMRATIO` (`fig7-1.csv`): the ILO counts ages 15+ (the BLS 16+) and models the series.
  - Used by Figure 1 ("Beyond the United States").
- `unemployment_countries_monthly.csv`: `iso3, country, date, unemployment_rate`. Harmonised unemployment rates, percent, seasonally adjusted, monthly, 34 OECD countries, 15,533 rows. Start dates differ (Canada and Japan 1955, most of Europe 1983, Germany 1991, Turkey 2005, Israel 2012). New Zealand and Switzerland are quarterly (dated the first month of the quarter).
  - Source: OECD via FRED, `LRHUTTTT{CC}M156S` (`Q156S` for New Zealand and Switzerland). FRED has no series for Colombia, Costa Rica, Latvia or Lithuania.
  - The U.S. rows are `UNRATE` from `fig7-2.csv` (1955-01 to 2026-09); FRED's OECD copy of the U.S. rate is the same BLS series (largest difference 0.1 point) but stops in 2025-09.
  - Used by Figure 2 ("Beyond the United States").
- `unemployment_countries.csv`: `iso3, country, year, unemployment_rate`. Unemployment rate, percent of the labor force (Eurostat definition), annual, 1960–2025, 42 countries plus the euro area of 12 (`iso3` = `EA12`), 2,193 rows. Germany is West Germany up to 1990; `EA12` includes West Germany up to 1990 (AMECO `DA12`), as in `fig7-7.csv`. Years after 2025 (Commission forecasts) are dropped.
  - Source: European Commission AMECO, series `<code>.1.0.0.0.ZUTN`, from macro102's `fig7-7/raw/ameco1.zip`.
  - Validation: `EA12`, Japan and the United States reproduce the three columns of `fig7-7.csv` to within 0.01, 0.07 and 0.08 points (Japan and the U.S. there come from the OECD and BLS).
  - Used by Figure 7 ("Beyond three economies").
- `college_premium_countries.csv`: `iso3, country, year, relative_earnings, premium_log_points, bachelor_share`. 48 countries, 2000–2025 (most from 2013), 475 rows.
  - `relative_earnings`: earnings of full-time workers aged 25–64 with a bachelor's or higher degree (ISCED 6–8) relative to those with upper secondary education (= 100); `premium_log_points` = 100 × ln(relative_earnings / 100), the unit of `fig7-8.csv`. 38 countries. One implausible value is dropped: Slovakia 2013 (3.55, a unit error in the source; Slovakia's other years are 152–173).
  - `bachelor_share`: share of the population aged 25–64 with a bachelor's or higher degree, percent (mostly 2023–2025). 48 countries.
  - Source: OECD, Education at a Glance, dataflows `OECD.EDU.IMEP,DSD_EAG_LSO_EA@DF_LSO_EARN_REL_UPPER` and `@DF_LSO_NEAC_DISTR_EA`, key `._T.Y25T64.ISCED11A_6T8..............`, <https://sdmx.oecd.org/public/rest/data/>.
  - A different measure from the textbook's: annual earnings of full-time workers, not adjusted for age, gender or region. The U.S. value is about 14 log points above EPI's adjusted hourly premium in `fig7-8.csv` (2013–2024).
  - Used by Figure 8 ("Beyond the United States").
- `manufacturing_countries.csv`: `iso3, country, region, year, manufacturing_millions, manufacturing_share`. Employment in manufacturing, millions of people and percent of total employment, ILO modelled estimates (November 2025), annual, 1991–2025, 187 countries, 6,531 rows.
  - Source: ILOSTAT `EMP_2EMP_SEX_ECO_NB_A` (sex `SEX_T`, `ECO_AGGREGATE_MAN` and `ECO_AGGREGATE_TOTAL`), <https://rplumber.ilo.org/data/indicator/?id=EMP_2EMP_SEX_ECO_NB_A&sex=SEX_T&classif1=ECO_AGGREGATE_MAN+ECO_AGGREGATE_TOTAL&format=.csv&type=code>.
  - Validation: the U.S. rows count 2.0–4.3 million more workers than `MANEMP` (`fig7-10.csv`, annual mean), because the ILO uses the household survey (which includes the self-employed) and the BLS figure counts payroll jobs; both show the same fall after 2000.
  - Used by Figure 10 ("Beyond the United States").
- `top01_share_countries.csv`: `iso3, country, region, year, top01_share`. Share of pre-tax national income received by the top 0.1 percent of adults (equal-split), percent, 58 countries (the 38 OECD members and 20 large emerging economies, as for `percentile_growth_countries.csv`), 1820–2024, 4,277 rows. Every country is covered every year from 1980; before 1980, 29 countries have more than 20 years of data (mostly from tax records), and the others have only WID's historical benchmark years (1820, 1850, 1880, 1900, 1910, 1920, ...). WID repeats its last estimate in the latest years for some countries (e.g. the U.S. 2022–2024).
  - Source: World Inequality Database bulk file <https://wid.world/bulk_download/wid_all_data.zip>, variable `sptincj992`, percentile `p99.9p100` (read with HTTP range requests, as below).
  - Validation: the U.S. and French rows reproduce `fig7-11.csv` (WID via Our World in Data) exactly in all 112 and 108 common years.
  - Used by Figure 11 ("Beyond two countries").
- `percentile_growth_countries.csv`: `iso3, country, region, period, percentile, growth_pct`. Average annual growth, 100 × [(y_end / y_start)^(1/34) − 1], of average pre-tax national income per adult (equal-split adults, constant local currency) at each of WID's 127 g-percentiles (1, …, 99, 99.1, …, 99.9, 99.91, …, 99.99, 99.991, …, 100; `percentile` is the upper bound), for 1980–2014 (the textbook's window) and 1990–2024, 58 countries (the 38 OECD members and 20 large emerging economies), 14,222 rows. Percentiles with zero or negative income in either year are dropped. Growth is rounded to 0.01 point to keep the file under 1 MB (0.84 MB).
  - Source: World Inequality Database bulk file <https://wid.world/bulk_download/wid_all_data.zip>, variable `aptincj992`. `build_data.py` reads only the needed `WID_data_XX.csv` members with HTTP range requests (the archive is about 900 MB) and caches the filtered rows per country.
  - A different concept from the textbook's: pre-tax income (WID has it for every country) instead of PSZ post-tax income. For the U.S., 1980–2014, WID pre-tax growth is −1.25% at the 10th percentile (PSZ post-tax: +0.26%), 0.58% at the median (0.91%), 2.10% at the 99th (2.29%) and 4.08% at the 99.99th (4.04%): taxes and transfers lift the bottom.
  - Used by Figure 12 ("Beyond the United States").
