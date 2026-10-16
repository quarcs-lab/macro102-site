# Data for Chapter 17: Investment

Read by `notebooks/ch17-investment.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch17/`.
All files were retrieved on 2026-10-16 by the macro102 `/collect-data` skill (FRED, OECD Corporate Tax Statistics,
Robert Shiller's online data). Shares and rates are in percent.

## Files copied from the macro102 collect-data output

| File | Textbook item | Columns | Span | Source |
|---|---|---|---|---|
| `fig17-3.csv` | Figure 17.3 | `date`, `cape` (Shiller's cyclically adjusted price-earnings ratio: the real S&P composite price over the average real earnings of the previous 10 years), `cape_average` (full-sample mean, 17.80) | 1881-01 to 2026-10, monthly (the latest months are preliminary) | Shiller, `ie_data.xls` (shillerdata.com, formerly econ.yale.edu/~shiller/data.htm) |
| `fig17-4.csv` | Figure 17.4 | `year`, `total` (gross private domestic investment), `nonres_fixed` (nonresidential fixed investment), `residential` (residential fixed investment), `inventories` (change in private inventories); percent of nominal GDP, `total` = sum of the three components | 1975 to 2025, annual | FRED GPDIA, PNFIA, PRFIA, CBIA, GDPA (BEA NIPA Table 1.1.5) |

Known differences from the textbook (see the macro102 `data/figN-k/notes.md` files):

- `fig17-3.csv`: the mean over the textbook's sample (1881-01 to 2023-03) is 17.36, the printed "Average = 17.4";
  the full sample to 2026-10 gives 17.80. The text's peak "in 2001 at more than 40" is the December 1999 peak (44.2).
- `fig17-4.csv`: the 2023 comprehensive NIPA revision raised the values for 2013–2022 by at most 0.4 points; the
  textbook vintage (ALFRED 2023-03-30) reproduces every value read off the textbook's figure within 0.1 point.

## Wider files built for the notebook

Built by `build_data.py` (run `python build_data.py [--macro102 PATH]`) from the raw downloads of collect-data in the
sibling macro102 checkout (`original-scanned-book/ch17-investment/data/`).

- `corporate_tax.csv`: `country` (the textbook's row name), `iso3`, `year`, `cit_rate` (statutory corporate income
  tax rate of the central government, including central surtaxes, percent). The 33 jurisdictions of Table 17.1,
  2000 to 2026 (890 rows; Israel has no 2026 value yet). Built from `table17-1/raw/oecd_DF_CIT_statutory.csv`
  (OECD Data Explorer, dataflow `OECD.CTP.TPS,DSD_TAX_CIT@DF_CIT,2.0`, measure `CIT`, targeting `ST`, sector
  `S1311`). Validation: the 2022 and 2025 rates equal collect-data's `table17-1/data.csv` exactly. Used to rebuild
  Table 17.1 for any year. Three 2022 rates differ from the textbook: Argentina (OECD 35, book 30), South Africa
  (OECD 28, book 27, the rate from 2023) and Chile (OECD statutory 27; the book's 10 is the small-business rate).
- `table17-1-book.csv`: `country`, `book_rate` (corporate tax rate, percent), `book_user_cost` (user cost of capital,
  percent): Table 17.1 as printed in the textbook (2022, 33 rows, book order), transcribed in `build_data.py`. Used
  to show the textbook's values next to the recomputed ones.
- `recessions.csv`: `peak`, `trough` (first day of the month). The NBER recessions that start in 1948 or later
  (12 recessions, 1948-11 to 2020-04): the peak is the month before the first recession month, the trough the last
  recession month. Built from `fig17-4/raw/fred_USREC.csv` (FRED USREC). Used to shade Figure 4.
- `investment_quarterly.csv`: `date` (first day of the quarter), `total` (gross private domestic investment) and
  `residential` (residential fixed investment), percent of GDP, one decimal, 1947Q1 to 2026Q2 (318 quarters). Built
  from `fig17-4/raw/fred_A006RE1Q156NBEA.csv` and `fred_A011RE1Q156NBEA.csv` (BEA NIPA Table 1.1.10). Validation:
  the annual means reproduce `fig17-4.csv` within 0.15 points. Used to check the text's quarterly numbers (2009Q3:
  12.7 percent of GDP, below the annual 13.3).
