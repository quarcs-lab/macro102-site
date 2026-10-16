# Data for Chapter 14: Financial Crises and the Short-Run Model

Read by `notebooks/ch14-financial-crises-and-the-short-run-model.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch14/`.
All files were retrieved on 2026-10-16 by the macro102 `/collect-data` skill (FRED, ALFRED, Federal Reserve H.4.1 and
H.6, Robert Shiller's online data). Percent values are in percent; money values in billions of dollars unless noted.

## Files copied from the macro102 collect-data output

| File | Textbook item | Columns | Span | Source |
|---|---|---|---|---|
| `fig14-1.csv` | Figure 14.1 | `date`, `baa_yield`, `treasury_10y` (percent), `spread` = BAA − GS10 (points) | 1996-01 to 2026-09, monthly | FRED BAA (Moody's), GS10 (H.15) |
| `fig14-4.csv` | Figure 14.4 | `date`, `fed_funds` (quarterly average), `taylor_rbar2`, `taylor_rbar1` (Taylor rule i = r̄ + π + 0.5(π − 2) + 0.5Ỹ with r̄ = 2 and 1), `short_run_output` = 100(GDPC1/GDPPOT − 1), `core_pce_inflation` (4-quarter change of the PCE price index excluding food and energy), `short_run_output_vintage2023` (the same gap from the ALFRED vintage of 2023-05-31, to 2023Q1) | 2000Q1 to 2026Q2 | FRED FEDFUNDS, PCEPILFE, GDPC1, GDPPOT; ALFRED GDPC1, GDPPOT |
| `fig14-5.csv` | Figure 14.5 | `date`, `gdp_actual`, `gdp_potential_latest`, `gdp_potential_2007` (trillions of chained 2017 dollars; the CBO's 2007 estimate rebased from 2000 dollars, to 2017Q4) | 2000Q1 to 2026Q2 | FRED GDPC1, GDPPOT; ALFRED GDPPOT and GDPC1, vintage 2007-06-30 |
| `fig14-6.csv` | Figure 14.6 | `date`, `currency`, `m1`, `m2`: growth over the preceding 12 months, percent | 1990-01 to 2026-08, monthly | FRED CURRSL, M1SL, M2SL (H.6) |
| `fig14-7.csv` | Figure 14.7 | `date`, `cape` (Shiller's cyclically adjusted price-earnings ratio), `cape_average` (full-sample mean, 17.80) | 1881-01 to 2026-10, monthly (the last month is preliminary) | Shiller, `ie_data.xls` |
| `fig14-8.csv` | Figure 14.8 | `date`, `real_home_price_1953_100` (real home price index, 1953 average = 100) | 1953-01 to 2026-07, monthly | Shiller, `Fig3-1.xls` |
| `fig14-9.csv` | Figure 14.9 | `date`, `long_term_treasuries` (maturity over 1 year), `mbs_agency_debt`, `short_term_treasuries` (within 1 year), `credit_market_facilities` (CPFF and the 2020 facility LLCs), `lending_and_other` (total minus the other layers), `total_assets` (WALCL); billions of dollars | 2007-01-03 to 2026-10-14, weekly (Wednesdays) | FRED H.4.1 series WALCL, TREAS15, TREAS1590, TREAS911Y, TREAS1T5, TREAS5T10, TREAS10Y, WSHOMCB, FEDDT, WCPFF and four 2020 facility series |
| `fig14-10.csv` | Figure 14.10 | `date`, `fed_funds` (monthly), `expected_YYYY_06` (expected path of the fed funds rate on the last trading day of June of year YYYY, 2008–2026: the actual rate, the 3-month yield and the forward rates 3m–6m, 6m–1y, 1y–2y, 2y–3y, at the midpoints of their intervals) | fed funds 2008-01 to 2026-09; paths 2008-06-30 to 2028-12-29 | FRED FEDFUNDS, DGS3MO, DGS6MO, DGS1, DGS2, DGS3 |
| `fig14-11.csv` | Figure 14.11 | `year`, `tfp_private_business`, `tfp_manufacturing` (total factor productivity, 2009 = 100) | 1987 to 2025 (manufacturing to 2024), annual | FRED MFPPBS, MFGPROD (BLS) |

Known differences from the textbook (see the macro102 `data/figN-k/notes.md` files):

- `fig14-4.csv`: data revisions raised short-run output by about half a point before 2012 and 1–2 points since 2013; the 2023 vintage column
  reproduces the textbook's line.
- `fig14-5.csv`: units are chained 2017 dollars (the textbook used 2012 dollars).
- `fig14-6.csv`: M1 was redefined in May 2020 (savings deposits moved into M1), so its 12-month growth is 291–357
  percent from May 2020 to April 2021. The file keeps the true values; the notebook blanks those months.
- `fig14-9.csv`: the Cleveland Fed chart of the textbook split Treasuries by purchase program; this file splits them
  by remaining maturity, so the long-term layer is not zero before 2009.
- `fig14-10.csv`: the textbook's expectations come from fed funds futures; these come from the Treasury yield curve
  and include a small term premium.
- `fig14-11.csv`: BLS revisions raised private-business TFP growth (2004–2022: 0.62 percent a year instead of the
  textbook's 0.5); the strong years since 2022 bring 2004–2025 to 0.72.

## Wider files built for the notebook

Built by `build_data.py` (run `python build_data.py [--macro102 PATH]`) from the raw downloads of collect-data in the
sibling macro102 checkout (`original-scanned-book/ch14-financial-crises-and-the-short-run-model/data/`).

- `recessions.csv`: `peak`, `trough` (first day of the month). The NBER recessions that start in 1953 or later
  (11 recessions, 1953-07 to 2020-04): the peak is the month before the first recession month, the trough the last
  recession month. Built from `fig14-6/raw/fred_USREC.csv` (FRED USREC). Used to shade Figures 4 and 6.
- `fed_balance_sheet.csv`: `month` (YYYY-MM), `total` (total factors supplying reserve funds, WTFSRFL), `treasuries`
  (WSHOTSL), `mbs` (WSHOMCB), `currency` (currency in circulation, WCICL), `reserves` (reserve balances, WRBWFRBL);
  billions of dollars. Monthly averages of the weekly Wednesday levels of the Federal Reserve's H.4.1 release, complete
  months only (at least 4 Wednesdays), 2003-01 to 2026-09 (285 months). Built from `table14-1/raw/fred_*.csv`. Used to
  rebuild Table 14.1 for any month. Validation: May 2007, May 2015 and September 2026 reproduce collect-data's
  `table14-1/data.csv` within 1 billion dollars, and that table matches the textbook's Table 14.1 within 11 billion
  dollars in every cell (the textbook's total is total factors supplying reserve funds, not WALCL).

## Multi-country files (beyond the United States)

Built by `build_data.py` from public downloads, cached in macro102's `.work/ch14/notebook-raw/` (delete a file there to
download it again). Country names and World Bank regions come from <https://api.worldbank.org/v2/country> with the
readable names of `data/ch01/build_data.py`; the euro area is `EMU`, "Euro area". Every file is under 0.5 MB.

| File | Figure | Columns | Coverage | Source |
|---|---|---|---|---|
| `sovereign_spreads.csv` | 14.1 (euro-area analogue) | `iso3, country, date, yield_10y, spread_germany` (percent; points) | 13 euro-area countries, monthly, from euro entry (1999; Greece 2001, Slovenia 2007, Slovakia 2009) to 2026-09; 4,080 rows | FRED `IRLTLT01{CC}M156N` (OECD long-term government bond yields), spread = yield − Germany's |
| `taylor_world.csv` | 14.4 | `iso3, country, year, policy_rate, core_inflation, headline_inflation, output_gap` (percent) | 14 central banks (U.S., euro area, U.K., Japan, Canada, Australia, New Zealand, Sweden, Norway, Switzerland, South Korea, Israel, Czechia, Poland), annual 1999–2025; 365 rows | BIS `WS_CBPOL` (monthly policy rates, annual mean of complete years); OECD Economic Outlook 119 `PCORE_YTYPCT`, `CPI_YTYPCT` (else `CPIH_YTYPCT`), `GAP`; ECB `ICP.M.U2.N.XEF000.4.ANR` (euro-area core HICP, annual mean) |
| `potential_world.csv` | 14.5 | `iso3, country, year, gdp, potential_gdp` (index, actual GDP in 2007 = 100) | 41 economies (OECD members, Bulgaria, Croatia, Romania and the euro area), 1990–2025 (EO projections for 2026–2027 dropped); 1,363 rows | OECD Economic Outlook 119 `GDPV` (real GDP), `GDPVTR` (potential output) |
| `money_world.csv` | 14.6 | `iso3, country, region, year, broad_money_growth` (percent, end of year over end of year) | 166 economies, 1990–2025; 5,350 rows | WDI `FM.LBL.BMNY.ZG`; euro area: ECB `BSI.M.U2.Y.V.M30.X.I.U2.2300.Z01.A` (M3 annual growth rate, December) |
| `house_prices_world.csv` | 14.8 | `iso3, country, region, date, real_price` (index, 2010 = 100) | 58 economies, quarterly (first day of the quarter), 1970Q1–2026Q2; 8,635 rows | BIS `WS_SPP`, key `Q..R.628` (real residential property prices, CPI-deflated); aggregates 4T, 5R, XW dropped |
| `cb_assets_world.csv` | 14.9 | `iso3, country, date, assets_gdp` (percent of GDP) | 35 central banks, quarterly, 2000Q1–2026Q2; 3,507 rows | BIS `WS_CBTA`, key `Q..B.XDF_R_B1GQ..B` (total assets, break-adjusted, percent of GDP); the Eurosystem's national central banks are dropped (the euro area stands for them) |
| `tfp_world.csv` | 14.11 | `iso3, country, region, year, tfp` (PWT `rtfpna`, 2017 = 1) | 120 countries, 1954–2023; 6,988 rows | Penn World Table 11.0 (`pwt110.dta`, DataverseNL doi:10.34894/FABVLR) |

Validation of the U.S. rows (printed by `build_data.py`; it stops if the policy-rate check fails):

- `taylor_world.csv`: the BIS policy rate equals the annual mean of `fed_funds` in `fig14-4.csv` within 0.21 points;
  the OECD's core inflation is core PCE inflation (correlation 1.00 with `core_pce_inflation`); the OECD's output gap
  has a correlation of 0.88 with the CBO-based `short_run_output` and the same mean (+0.05 points).
- `potential_world.csv`: real GDP grows 1.76 percent a year from 2007 to 2019, as in `fig14-5.csv`; the OECD's
  potential grows 1.90 percent a year, the CBO's 1.80.
- `money_world.csv`: WDI broad money is wider than M2; its growth has a correlation of 0.81 with the December
  12-month growth of M2 in `fig14-6.csv`, and it fell in 2010 (−2.8 percent) while M2 grew.
- `house_prices_world.csv`: the 2000s bust is 38.9 percent (2006Q1 to 2011Q3), against 35.7 percent in Shiller's
  `fig14-8.csv` (December 2005 to February 2012).
- `cb_assets_world.csv`: 6.2, 25.5 and 36.9 percent of GDP in 2007Q4, 2014Q4 and 2021Q4, against 6.1, 25.1 and 35.3
  percent for `total_assets` of `fig14-9.csv` divided by FRED `GDP`.
- `tfp_world.csv`: PWT TFP (whole economy, human-capital-adjusted labor) grows 1.19 percent a year in 1995–2004 and
  0.30 in 2004–2019, against 1.64 and 0.59 for the BLS private business sector in `fig14-11.csv`: lower, but the
  same slowdown.

Known quirks, shown in the notebook as data-hygiene notes:

- Luxembourg's 10-year yield is below Germany's in 2001–2007 (down to −1.3 points): a thin market for few bonds.
  FRED has no 10-year yield for Estonia, Latvia, Lithuania and Croatia, so they are missing.
- The OECD has no core inflation for the United Kingdom (headline CPIH in every year). The BIS has no Bank of Japan
  policy rate for 1999–2006 and 2013–2016 (money-quantity targets), so Japan's annual rows are 2007–2012 and 2017–2025.
- `money_world.csv` keeps WDI's values as published, including breaks: Sierra Leone +131,119 percent in 2001 and
  −99.9 percent in 2015, Grenada −91 percent in 2024 and +1,169 percent in 2025.
- Series start in different years (BIS house prices: 1970 for many, 2010 for Poland and Turkey; PWT: 1994 for the
  former Soviet, Yugoslav and Czechoslovak states; OECD GDP: Bulgaria, Colombia, Lithuania, Romania and Turkey after 1997).
