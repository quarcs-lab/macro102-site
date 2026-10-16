# Data for Chapter 3: An Overview of Long-Run Economic Growth

Read by `notebooks/ch03-an-overview-of-long-run-economic-growth.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch03/`.

## Files copied from the macro102 collect-data output

- `fig3-1.csv`: `year, gdppc_x500_usa, gdppc_x500_jpn, gdppc_x500_gbr, gdppc_x500_arg, gdppc_x500_chn, gdppc_x500_gha`. GDP per person as a multiple of 500 dollars (2011 $), at 19 benchmark years from year 1 to 2022.
  - Sources: the Maddison Project Database 2023 (Bolt & van Zanden, <https://doi.org/10.34894/INZBF2>), ratio-spliced with Maddison (2010) for the earliest years.
- `fig3-2.csv`: `year, gdppc`. U.S. GDP per person in 2022 dollars, 1870–2025.
  - Sources: BEA via FRED (`GDPCA`, `B230RC0A052NBEA`, `A191RD3A086NBEA`) from 1929, and Maddison 2023 ratio-spliced at 1929 for 1870–1928.
- `fig3-5.csv`: `year, gdppc, line_2pct`. The same series, plus a 2%-a-year line fitted by least squares in logs.
- `fig3-6.csv`: `year, gdppc_usa, gdppc_gbr, gdppc_jpn, gdppc_arg, gdppc_zaf, gdppc_chn, gdppc_ind`. Maddison 2023 GDP per person in 2022 dollars at benchmark years 1870–2022.
- `fig3-7.csv`: `iso3, country, gdppc_rel_us_2019, growth_1960_2019_pct, gdppc_rel_us_2023, growth_1960_2023_pct`. Penn World Table 11.0 (<https://doi.org/10.34894/FABVLR>), rgdpe/pop, for 111 countries.
- `fig3-8.csv`: population and relative GDP per person for the same 111 countries in 1960, 2019 and 2023.
- `fig3-9.csv`: `year, population_thousands, gdppc, gdp_billions`. U.S. population, GDP per person and total GDP (2022 dollars), 1870–2025.

## Wider files built for the notebook widgets

Both files are made by `build_data.py` from raw files saved by macro102's `/collect-data`.

- `maddison_panel.csv`: `iso3, country, year, gdppc`. Every available year from 1870 to 2022 for the seven countries of Figure 3.6 (USA, GBR, JPN, ARG, ZAF, CHN, IND), 965 rows.
  - Source: Maddison Project Database 2023 `gdppc` × 1.2902, the U.S. GDP deflator ratio 2022/2011, so values are in 2022 dollars.
  - Validation: it reproduces `fig3-6.csv` exactly at the benchmark years.
  - Annual coverage is incomplete before 1950 for some countries (e.g. China).
- `pwt_income.csv`: `iso3, country, year, gdp_pc, y_rel_us_2019, pop_millions, in_sample`. Penn World Table 11.0, 1950–2023, 185 countries.
  - `gdp_pc` is rgdpe/pop in 2021 dollars, the measure collect-data uses for Figures 3.7 and 3.8.
  - `y_rel_us_2019` divides by the U.S. value in 2019.
  - `in_sample` marks the 111 countries with data in 1960, 2019 and 2023.
  - Validation: it reproduces `fig3-7.csv` (growth rates within 0.001 points, relative levels within 0.0001) and the 1960 columns of `fig3-8.csv` exactly.
  - Known quirk: Venezuela's GDP per person after 2017 is not plausible (about 0.1% of the U.S. level in 2023), because hyperinflation broke the PWT price data. The notebook drops it in Figure 7.
