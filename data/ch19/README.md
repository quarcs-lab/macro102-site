# Data for Chapter 19: International Trade

Read by `notebooks/ch19-international-trade.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch19/`.
All files were retrieved on 2026-10-16 by the macro102 `/collect-data` skill (FRED and ALFRED of the Federal
Reserve Bank of St. Louis, which republish BEA data, and the Penn World Table). Shares are in percent.

## Files copied from the macro102 collect-data output

| File | Textbook item | Columns | Span | Source |
|---|---|---|---|---|
| `fig19-1.csv` | Figure 19.1 | `year`, `exports_share`, `imports_share` (exports and imports of goods and services, percent of nominal GDP) | 1950 to 2025, annual | FRED EXPGSA, IMPGSA, GDPA (BEA NIPA Table 1.1.5) |
| `fig19-2.csv` | Figure 19.2 | `year`, `trade_balance_pct_gdp` (net exports, percent of GDP) | 1950 to 2025, annual | FRED A019RC1A027NBEA, GDPA |
| `fig19-3.csv` | Figure 19.3 | `iso3`, `country`, then pairs `tb_own_<year>[_pwt10]` (trade balance, percent of own GDP) and `tb_us_<year>[_pwt10]` (the same balance, percent of U.S. GDP) for 2017 and 2019 (PWT 10.01) and 2019 and 2023 (PWT 11.0) | five countries | Penn World Table 10.01 (doi 10.34894/QT5BCC) and 11.0 (doi 10.34894/FABVLR) |
| `fig19-4.csv` | Figure 19.4 | `iso3`, `country`, `tb_avg_<start>_<end>[_pwt10]` (simple average of the annual trade balance, percent of own GDP) for 2000–2017, 2000–2019 and 1990–2019 (PWT 10.01) and 1990–2019, 2000–2019 and 2000–2023 (PWT 11.0) | five countries | Penn World Table 10.01 and 11.0 |
| `fig19-5.csv` | Figure 19.5 | `year`, `investment_pct_gdp` (gross private domestic investment), `budget_deficit_pct_gdp` (minus federal net saving, calendar-year means of quarterly data), `trade_deficit_pct_gdp` (minus net exports); percent of GDP | 1960 to 2025, annual | FRED GPDIA, FGDEF, GDP, A019RC1A027NBEA, GDPA |
| `fig19-6.csv` | Figure 19.6 | `year`, `niip_pct_gdp` (U.S. net international investment position at year end, percent of GDP) | 1976 to 2025, annual | FRED IIPUSNETIA (BEA), GDPA |

In the Penn World Table files the trade balance is $100\,(1 - c - i - g)$, where $c$, $i$ and $g$ are the shares of
household consumption, investment and government consumption in GDP at current PPPs (`csh_c`, `csh_i`, `csh_g`).
This is net exports including PWT's residual trade share `csh_r`, the definition that reproduces the textbook.

Known differences from the textbook (see the macro102 `data/figN-k/notes.md` files):

- `fig19-1.csv`, `fig19-2.csv`, `fig19-5.csv`: the 2023 comprehensive NIPA update changed 2019–2022 by 0.1–0.5
  points. The text's 2006 deficit of "5.6 percent" is 5.69 percent now.
- `fig19-3.csv`: the textbook's bars, titled 2019, are PWT 10 values for **2017**; the 2017 columns reproduce them
  within 0.05 points, while the 2019 columns do not.
- `fig19-4.csv`: the textbook's bars, titled 2000–2019 (and "1990 to 2019" in the text), are PWT 10 averages over
  **2000–2017**; the `tb_avg_2000_2017_pwt10` column reproduces them within 0.05 points.
- `fig19-6.csv`: BEA has revised the investment position since the textbook was written. The 2020–2022 values are
  9 to 16 points of GDP less negative than in the textbook (2022: −54.6 percent instead of −63.5 percent).

## Wider files built for the notebook widgets

Built by `build_data.py` (run `python build_data.py [--macro102 PATH]`) from the raw downloads of collect-data in the
sibling macro102 checkout (`original-scanned-book/ch19-international-trade/data/`).

- `us_trade.csv`: `year`, `gdp`, `exports`, `imports`, `net_exports`, `investment` (gross private domestic
  investment), `niip` (net international investment position at year end), all in billions of current dollars,
  and `gdp_2023`, `niip_2023` (GDP and the investment position as published in July 2023, the textbook's vintage).
  1950 to 2025 (76 rows); `niip` starts in 1976, and the 2023 vintage ends in 2022. Built from FRED GDPA, EXPGSA,
  IMPGSA, A019RC1A027NBEA, GPDIA and IIPUSNETIA (divided by 1,000: millions to billions) and the ALFRED vintages of
  GDPA and IIPUSNETIA of 2023-07-01 (raw files in `fig19-1/raw/`, `fig19-2/raw/`, `fig19-5/raw/`, `fig19-6/raw/`).
  Validation: the shares of GDP reproduce `fig19-1.csv`, `fig19-2.csv`, the investment and trade-deficit columns
  of `fig19-5.csv`, and `fig19-6.csv`, all within 0.001 points; exports minus imports equals net exports within
  0.001 billion dollars. Used by Figures 1, 2 and 6 to compute shares, the trade balance and accumulated deficits
  with the notebook's own functions, and to compare the two vintages of the investment position.
- `pwt_trade.csv`: `iso3`, `country`, `vintage` (`PWT 10.01` or `PWT 11.0`), `year`, `csh_c`, `csh_i`, `csh_g`
  (shares of household consumption, gross capital formation and government consumption in output-side GDP at
  current PPPs) and `cgdpo` (output-side real GDP at current PPPs, millions of 2017 US dollars in PWT 10.01 and of
  2021 US dollars in PWT 11.0). The nine countries of Figures 19.3 and 19.4 (U.S., Japan, China, France, Germany,
  India, Singapore, Ireland, S. Korea), 1990 to 2019 (PWT 10.01) and 1990 to 2023 (PWT 11.0), 576 rows, no missing
  values. Built from `fig19-3/raw/` and `fig19-4/raw/` `pwt1001_subset.csv` and `pwt110_subset.csv`. Validation:
  $100(1 - c - i - g)$ and its rescaling by `cgdpo` relative to the U.S. reproduce every column of `fig19-3.csv`,
  and the simple averages over each window reproduce every column of `fig19-4.csv`, all within 0.001 points. Used
  by Figures 3 and 4 to choose any year (Figure 3) or averaging window (Figure 4) and either vintage.
