# Data for Chapter 19: International Trade

Read by `notebooks/ch19-international-trade.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch19/`.
The files of the first two sections were retrieved on 2026-10-16 by the macro102 `/collect-data` skill (FRED and ALFRED of the Federal
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

## Multi-country files (conventions §6b)

Built by `build_data.py` from public downloads (requests' default User-Agent), cached in the macro102 checkout under
`.work/ch19/notebook-raw/`; delete a cached file to download it again. Retrieved on 2026-10-17. Country names follow
the World Bank's list, shortened where it is awkward (`Egypt`, `Iran`, `Hong Kong`, `Türkiye`); the nine countries of
the textbook figures keep the labels of `pwt_trade.csv` (`U.S.`, `S. Korea`), so that every file uses the same names.
Aggregates (regions, income groups, the euro area) are dropped. All shares are in percent.

- `countries.csv`: `iso3`, `country`, `region`, `income`. The 214 economies that appear in any of the files below,
  with their World Bank region (seven regions; "Middle East, North Africa, Afghanistan & Pakistan" is shortened to
  "Middle East & North Africa") and income group. Source: World Bank country API
  (<https://api.worldbank.org/v2/country?format=json&per_page=400>). Taiwan, Anguilla, Montserrat, Guernsey and
  Jersey are not in the World Bank list; their region is set by hand (income group left empty for all but Taiwan).
  Used for the region menus of the website versions.
- `wdi_trade.csv`: `iso3`, `country`, `year`, `exports`, `imports`, `trade_balance` (exports and imports of goods and
  services and their difference, percent of GDP). 194 economies, 1960–2025 (9,038 rows; most series start later,
  and 2025 covers only 138 economies), 322 kB. Source: World Bank WDI `NE.EXP.GNFS.ZS`, `NE.IMP.GNFS.ZS`,
  `NE.RSB.GNFS.ZS` (<https://api.worldbank.org/v2/country/all/indicator/CODE?format=json&per_page=20000>).
  Validation: the U.S. rows (1970–2024) reproduce `fig19-1.csv` and `fig19-2.csv` (BEA) within 0.09 points
  (`build_data.py` stops above 0.3). Used by the many-country versions of Figures 1 and 2.
- `pwt_trade_world.csv`: `iso3`, `country`, `vintage`, `year`, `csh_c`, `csh_i`, `csh_g`, `cgdpo` (as in
  `pwt_trade.csv`), plus `rgdpna` (real GDP at constant 2021 national prices, millions of 2021 US dollars) and `pop`
  (population, millions). PWT 11.0 only, all 185 economies, 1990–2023 (6,242 rows), 487 kB. Source: Penn World
  Table 11.0, `pwt110.dta` (<https://doi.org/10.34894/FABVLR>; the bulk file is read from collect-data's cache
  `.work/downloads/` when present, otherwise downloaded from DataverseNL). Validation: its rows for the nine
  textbook countries reproduce `pwt_trade.csv` (PWT 11.0) within 1e-6 in the shares and 1e-6 (relative) in `cgdpo`,
  the rounding of the `.dta` file's single-precision numbers. Known quirks: a few tiny economies have implausible
  shares and therefore trade balances of −60 to −50,000 percent of GDP (Bermuda, Turks and Caicos, Anguilla,
  Montserrat, Sint Maarten); the notebook sets aside economies with average balances beyond ±40 percent in the
  growth scatter, and the map caps its color scale at ±20. Used by Figures 3 and 4 (country pickers, the world map
  and the growth-versus-trade-balance scatter).
- `twin_deficits_world.csv`: `iso3`, `country`, `year`, `investment` (gross capital formation, WDI
  `NE.GDI.TOTL.ZS`), `budget_deficit` (minus general government net lending/borrowing, IMF World Economic Outlook,
  October 2026, DataMapper indicator `GGXCNL_NGDP`, <https://www.imf.org/external/datamapper/api/v1/GGXCNL_NGDP>)
  and `trade_deficit` (minus WDI `NE.RSB.GNFS.ZS`), percent of GDP. 209 economies, 1980–2025 (8,383 rows; 178
  economies have both deficits in at least 5 years), 269 kB. The WEO's last years are IMF estimates; projections
  after 2025 are dropped. Definitions differ from Figure 19.5: investment includes government investment, and the
  budget deficit covers all levels of government, not only the federal one. Validation against `fig19-5.csv`: the
  U.S. trade deficit agrees within 0.09 points (1980–2024; `build_data.py` stops above 0.3); U.S. investment is on
  average 4.1 points above private investment, and the general-government deficit (IMF, from 2001 only) 1.2 points
  above the federal one. Used by the many-country version of Figure 5.
- `niip_world.csv`: `iso3`, `country`, `year`, `niip` (net international investment position at year end,
  including gold, percent of GDP, both in US dollars: `100 × (Net IIP excl gold + Monetary Gold) / GDP (US$)`).
  198 economies, 1970–2024 (9,135 rows), 227 kB. Source: Lane & Milesi-Ferretti, *External Wealth of Nations*
  database, Brookings release of February 2026, year-end 2024
  (<https://www.brookings.edu/wp-content/uploads/2026/02/EWN-dataset-year-end-2024_4.9.26.xlsx>). The sheet's own
  ratio column covers only years with an official IIP, so the ratio is recomputed from the levels. IMF IFS country
  names are matched to ISO3 codes through the World Bank and IMF lists plus a short table in `build_data.py`;
  ECCU, the euro area and the Netherlands Antilles are dropped. Validation against `fig19-6.csv`: identical within
  0.01 points from 1976 to 2019; from 2020 on the database keeps earlier BEA vintages, so its U.S. position is 7 to
  15 points of GDP more negative than the current BEA data (2024: −90.6 against −75.3 percent; 2020–2022 are close
  to the July 2023 vintage in `us_trade.csv`). Known quirks: financial centers, oil exporters and a few aid-dependent
  economies have positions beyond ±300 percent of GDP (Qatar +1,578, Liberia −1,837). Used by the many-country
  version of Figure 6.
