# Data for Chapter 6: Growth and Ideas

Read by `notebooks/ch06-growth-and-ideas.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch06/`.

## Files copied from the macro102 collect-data output

- `fig6-5.csv`: `year, commodity_index, aluminum_real_1900_100, coal_real_1900_100, copper_real_1900_100, lead_real_1900_100, iron_ore_real_1900_100, zinc_real_1900_100, extended_with_world_bank`. Real (CPI-deflated) prices of six industrial commodities, each an index with 1900 = 100, and their equally weighted index (the geometric mean of the six), annual, 1900–2025.
  - Sources: Jacks (2019), "From Boom to Bust", real commodity prices 1850–2020 (Wayback Machine copy of <http://www.sfu.ca/~djacks/data/boombust/>) for 1900–2020; extended to 2021–2025 with the World Bank Pink Sheet nominal prices (<https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Annual.xlsx>) deflated by the U.S. CPI (`CPIAUCSL`, BLS via FRED). `extended_with_world_bank` is 1 for these five years.
  - Substitute for the textbook's Global Financial Data series (proprietary). Same shape and turning points, but from the mid-1970s to 2002 the index is 8–25 points above the book, mainly because of the Jacks coal series. The 1900→2000 fall is a factor of 2.9 rather than the book's "almost five".
- `fig6-6.csv`: `year, gdp_pc_growth_10yr`. Average annual growth of U.S. real GDP per person over the preceding 10 years, percent (100 × [ln y(t) − ln y(t−10)]/10), 1960–2025.
  - Sources: BEA via FRED (`GDPCA` real GDP, `B230RC0A052NBEA` population).

## Wider files built for the notebook

All three are made by `build_data.py` from raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch06-growth-and-ideas/data/fig6-6/raw/` and `table6-2/raw/`).

- `us_gdp_pc.csv`: `year, gdp_pc`. U.S. real GDP per person, chained 2017 dollars (`GDPCA` × 10⁹ / (`B230RC0A052NBEA` × 10³)), annual, 1929–2025, 97 rows.
  - Used by the Figure 6 widget, which averages growth over 5, 10, 15 or 20 years.
  - Validation: its 10-year growth rates reproduce `fig6-6.csv` to within 0.0001 percentage points.
- `recessions.csv`: `peak, trough, peak_year, trough_year`. The 9 NBER business-cycle peaks and troughs since 1960, from 1960-04 / 1961-02 to 2020-02 / 2020-04.
  - Source: NBER-based recession indicator `USREC` via FRED. `peak` is the month before the first recession month and `trough` the last recession month (first day of the month). `peak_year` and `trough_year` are the same dates as decimal years (start of the peak month, end of the trough month), for shading a chart with a yearly axis.
  - Used to shade recessions in Figure 6.
- `growth_accounting.csv`: `year, output_per_hour, contrib_capital, contrib_labor_composition, tfp`. BLS indexes (2017 = 100) for the private business sector (sector code PG), annual, 1948–2025, 78 rows: labor productivity, the contribution of capital intensity to labor productivity, the contribution of labor composition to labor productivity, and total factor productivity.
  - Source: BLS, "Total factor productivity and related measures for major industries, linked SIC-NAICS" (`total-factor-productivity-major-sectors-historical.xlsx`, sheet `MachineReadable`), release of March 19, 2026, from a Wayback Machine copy of <https://www.bls.gov/productivity/tables/total-factor-productivity-major-sectors-historical.xlsx>.
  - Used to recompute Table 6.2 (growth accounting) in the Figure 6 section. The period averages, 100 × ln(X_b/X_a)/(b − a), reproduce macro102's `table6-2/data.csv` to within 0.001 percentage points. With this current release, three cells are 0.1 point above the book after rounding, because of data revisions: TFP growth 1948–2021 (1.26, shown as 1.3, against 1.2), and 2003–2021 output per hour and TFP (1.9 and 0.8 against 1.8 and 0.7); every other cell matches.

## Multi-country and wider files (conventions §6b)

Both are made by `build_data.py`. Downloads are cached in `../macro102/.work/ch06/notebook-raw/`.

- `commodity_prices.csv`: `commodity, group, year, real_price_1900_100, extended_with_world_bank`. Real (U.S. CPI-deflated) prices of all 40 commodities in Jacks (2019), each an index with 1900 = 100, annual, 1900–2025, 4,990 rows. `group` is Jacks's group (Animal products, Energy, Grains, Metals, Minerals, Precious Metals, Softs).
  - Sources: Jacks (2019), sheet `Commodities`, 1900–2020 (the same file as `fig6-5.csv`, from macro102's `fig6-5/raw/`); 2021–2025 for the 30 commodities with a matching World Bank Pink Sheet price, deflated by the annual-average `CPIAUCSL` and chained to the 2020 Jacks level, exactly as for `fig6-5.csv` (`extended_with_world_bank` = 1). The ten others stop in 2020: hides, pork, rye, chromium, manganese, steel, bauxite, sulfur, cottonseed, wool.
  - The correlation of yearly changes between Jacks and the matched World Bank price in 1981–2020 is 0.99–1.00 for most commodities, 0.81–0.91 for wheat, gold, platinum and silver, 0.61 for lamb, and 0.53 for coal and iron ore (the two the textbook figure also uses; see `fig6-5.csv`).
  - Validation: the six textbook commodities reproduce the columns of `fig6-5.csv` to within 0.001 index points in every year.
  - Used by Figure 5 ("Beyond the six: 40 commodities").
- `gdp_pc_countries.csv`: `iso3, country, region, year, gdp_pc`. Real GDP per person, `rgdpna / pop`, in 2021 U.S. dollars at constant national prices, annual, 1950–2023, 185 countries, 11,201 rows. `region` is the World Bank region (Taiwan, Anguilla and Montserrat, which the World Bank does not list, are placed by hand).
  - Source: Penn World Table 11.0, <https://doi.org/10.34894/FABVLR> (`pwt110.dta`, variables `rgdpna`, `pop`); regions and readable names from the World Bank country API, <https://api.worldbank.org/v2/country?format=json&per_page=400>.
  - Series start in 1950 (55 countries), 1960, 1970 or 1990 (former Soviet and Yugoslav republics), so 10-year growth rates start ten years later.
  - Validation: the U.S. 10-year growth rates differ from `fig6-6.csv` (BEA) by −0.003 points on average over 1960–2023, at most 0.20 points.
  - Used by Figure 6 ("Beyond the United States").
