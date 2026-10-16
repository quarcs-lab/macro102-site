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
