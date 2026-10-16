# Data for Chapter 18: The Government and the Macroeconomy

Read by `notebooks/ch18-the-government-and-the-macroeconomy.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch18/`.
All files were retrieved on 2026-10-16 by the macro102 `/collect-data` skill (OMB Historical Tables, CBO, OECD,
FRED). Shares are in percent of GDP. U.S. federal budget data are by **fiscal year** (October–September since
FY1977, July–June before), the 1976 transition quarter is dropped.

## Files copied from the macro102 collect-data output

| File | Textbook item | Columns | Span | Source |
|---|---|---|---|---|
| `fig18-1.csv` | Figure 18.1 | `year` (fiscal year), `spending_gdp_pct` (total federal outlays), `revenue_gdp_pct` (total federal receipts) | FY1934–FY2025 | OMB Historical Tables, FY2027 Budget, Table 1.2 (`hist01z2_fy2027.xlsx`) |
| `fig18-2.csv` | Figure 18.2 | `year`, `surplus_gdp_pct` (total surplus + / deficit −), `debt_public_gdp_pct` (federal debt held by the public, end of year; empty before FY1940) | FY1934–FY2025 | OMB Historical Tables, FY2027 Budget, Tables 1.2 and 7.1 |
| `fig18-3.csv` | Figure 18.3 | `iso3`, `country` (the textbook's short names), `gov_spending_2019`, `gov_spending_2024` (general government expenditure) | 2019 and 2024, six countries | OECD Government at a Glance, `DSD_GOV@DF_GOV_PF_YU`, measure GE |
| `fig18-4.csv` | Figure 18.4 | `year`, `italy`, `japan`, `usa`, `uk`, `germany` (general government net financial liabilities = −net financial worth / GDP), `japan_eo` (Japan, OECD Economic Outlook GNFLQ) | 1995–2025 (`japan` 2005–2024, `japan_eo` 1995–2005) | OECD financial balance sheets `DSD_NASEC20@DF_T720GOV_A` (BF90) and GDP `DSD_NAMAIN10@DF_TABLE1_EXPENDITURE`; OECD Economic Outlook |
| `fig18-5.csv` | Figure 18.5 | `year` (calendar year), `investment_share` (gross private domestic investment), `gov_saving_share` (net federal government saving) | 1960–2025 | FRED GPDI, GDP, FGDEF (BEA NIPA, annual means of quarterly SAAR) |
| `fig18-6.csv` | Figure 18.6 | `year`, `revenue`, `spending_ex_interest` (outlays minus net interest), `ss_medicare_medicaid` (Social Security + Medicare + Medicaid + CHIP + ACA premium tax credits), `projection` (0 = OMB actual, 1 = CBO projection) | FY1950–FY2025 actual, FY2026–FY2056 projected | OMB Historical Tables FY2027 (1.2, 3.1, 8.5); CBO *Long-Term Budget Outlook*, February 2026 |
| `fig18-7.csv` | Figure 18.7 | `year`, `other_ex_interest` (all other spending excluding interest), `social_security`, `medicare_medicaid` (incl. CHIP and premium tax credits), `projection`; the three parts sum to `spending_ex_interest` of `fig18-6.csv` | FY1950–FY2025 actual, FY2026–FY2056 projected | as `fig18-6.csv` |
| `fig18-8.csv` | Figure 18.8 | `year`, `usa`, `germany`, `france`, `japan`, `uk` (current health expenditure, all financing schemes) | 1970–2025 (France only every 5 years before 1990; Germany missing 1991; 2025 provisional) | OECD Health Statistics, `DSD_SHA@DF_SHA` |

Known differences from the textbook (details in the macro102 `data/figN-k/notes.md` files):

- `fig18-1.csv`, `fig18-2.csv`: the textbook's FY2023 points are OMB **estimates** of March 2023; the actual FY2023
  values are lower (spending 22.4 vs 24.2, revenue 16.2 vs 18.2, debt 95.8 vs 98.4). Current FY2020–22 values are up
  to 0.6 (shares) and 2.1 points (debt) lower because of GDP revisions. The book's WWII peak (about 43.6) is about
  0.9 points above both OMB vintages (42.7). The book's FY1939 debt point is not in the current table.
- `fig18-3.csv`: revisions since the 2023 edition move the 2019 bars by −2.0 (Korea) to +0.8 points (Sweden); Japan
  now sorts below the U.S. The 2023 edition reproduces all printed bars within 0.12.
- `fig18-4.csv`: Japan is 4–6 points below the book in 2011–2021 and Germany 2–4 points above in 2019–2021. The
  textbook's claim that Japan's ratio exceeded 140 percent in 2023 is not supported (93.7 in 2023).
- `fig18-5.csv`: the textbook's government-saving line is federal net saving (FGDEF), not total government saving.
  2019–2022 values differ by up to 0.7 points after the 2023 NIPA revision.
- `fig18-6.csv`, `fig18-7.csv`: CBO's 2002 projections to 2075 are replaced by its February 2026 projections, which end
  in 2056 and are much flatter. Actual 1950–2000 values are up to 0.8 points below the book's decade points.
- `fig18-8.csv`: the current OECD release starts in 1970, so the book's 1960 and 1965 points are missing. The book's
  U.K. points for 2000–2010 look shifted by five years.

## Wider files built for the notebook

Built by `build_data.py` (run `python build_data.py [--macro102 PATH]`) from the raw downloads of collect-data in the
sibling macro102 checkout (`original-scanned-book/ch18-the-government-and-the-macroeconomy/data/`).

- `federal_budget.csv`: the lines of Table 18.1, in percent of fiscal-year GDP, for every fiscal year FY1940–FY2025
  (87 rows). Columns: `year`; `release` (`actual (FY2027 Budget)` for every year, plus one extra row for FY2023,
  `estimate (FY2024 Budget)`, the March 2023 OMB estimate that the textbook's table shows); `gdp_billions`
  (fiscal-year GDP, billions of dollars, OMB Table 1.2); `population_millions` (BEA population averaged over the
  twelve months of the fiscal year, FRED POPTHM; empty before FY1960); spending lines `total_spending`, `health`
  (functions 550 Health + 570 Medicare), `social_security` (650), `defense` (050), `income_security` (600),
  `net_interest` (900), `other_spending` (total minus those five); revenue lines `total_revenue`,
  `individual_income_tax`, `social_insurance_tax` (social insurance and retirement receipts),
  `corporate_income_tax`, `other_revenue` (excise taxes and other receipts); `balance` (revenue minus spending,
  negative = deficit). Built from `table18-1/raw/hist01z2_*.xlsx`, `hist02z1_*.xlsx`, `hist03z1_*.xlsx` (OMB
  Historical Tables 1.2, 2.1 and 3.1 of the FY2027 Budget, April 2026, and of the FY2024 Budget, March 2023) and
  `table18-1/raw/fred_POPTHM.csv`. Medicare is set to 0 before FY1966. Validation: FY2023, FY2025 and the FY2023
  estimate reproduce collect-data's `table18-1/data.csv` within 0.0005 points of GDP and 0.5 dollars per person
  (the file rounds to 3 decimals). Used to rebuild Table 18.1 for any fiscal year.
- `gov_spending.csv`: general government expenditure in percent of GDP for the 38 OECD member countries, 2007–2025
  (704 rows; one row per country and year). Columns: `iso3`, `country` (OECD name; the textbook's short names for
  its six countries, plus Slovakia and Turkey), `year`, `gov_spending`, `status` (OECD observation status: normal,
  provisional, estimated or series break). Turkey has no data for 2007–08 and after 2020; only 26 countries have a
  2025 value so far, so the notebook stops in 2024. Built from `fig18-3/raw/oecd_gov_pf_yu_GE_pct_gdp.csv` (OECD
  Government at a Glance, dataflow `OECD.GOV.GIP,DSD_GOV@DF_GOV_PF_YU,1.0`, measure GE, sector S13, unit PT_B1GQ;
  non-member countries and aggregates are dropped). Validation: the 2019 and 2024 values of the six textbook
  countries equal `fig18-3.csv` within 0.005. Used for the animated OECD-wide chart of Figure 3 and the text checks
  (U.S. rank, euro-area average).
