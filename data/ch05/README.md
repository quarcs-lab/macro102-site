# Data for Chapter 5: The Solow Growth Model

Read by `notebooks/ch05-the-solow-growth-model.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch05/`.

## Files copied from the macro102 collect-data output

All four come from the Penn World Table 11.0 (Feenstra, Inklaar & Timmer; GGDC, <https://doi.org/10.34894/FABVLR>).

- `fig5-3.csv`: `iso3, country, inv_rate_avg_1990_2023, ky_2023`. Investment rate (csh_i, percent) averaged 1990–2023, and the capital-output ratio in 2023. Capital is built by perpetual inventory from csh_i × rgdpo with a 5% depreciation rate. 110 countries.
- `fig5-8.csv`: `iso3, country, gdp_pc_1960, growth_1960_2023`. GDP per person in 1960 (rgdpo/pop, 2021 US$) and its average annual growth from 1960 to 2023 (percent). 24 OECD countries.
- `fig5-9.csv`: same columns for the 110 countries with data in both 1960 and 2023.
- `fig5-10.csv`: `year, inv_rate_kor, inv_rate_usa, inv_rate_phl`. Investment rates (csh_i, percent) for 1950–2023. Korea starts in 1953.

## Wider file built for the notebook widgets

- `pwt_panel.csv`: `iso3, country, year, gdp_pc, inv_rate, oecd`. One row per country and year, 1950–2023, for 185 countries.
  - `gdp_pc` is rgdpo/pop in 2021 US$.
  - `inv_rate` is csh_i × 100.
  - `oecd` flags the 24 OECD countries of the textbook figure.

  It is built by `build_data.py` from the PWT 11.0 subset saved by macro102's `/collect-data`. It reproduces `fig5-8.csv` to within 0.0002 percentage points.
  - Known quirk: Venezuela's 2023 GDP per person (about $160) is implausible, an effect of hyperinflation on the PWT price data. The notebook uses this as a data-cleaning example.
