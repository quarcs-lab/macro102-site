# Data for Appendix A: Google Colab, Python Coding, and Data Science Libraries

Read by `notebooks/appA-google-colab-and-ai-powered-python.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appA/`.

Appendix A teaches Google Colab, Python and the data science libraries of the book, with examples built on
real data that the chapters also use. `build_data.py` copies the four files it needs, unchanged, from the
`data/` folders of the chapters in this site repo, so the notebook reads everything from its own `DATA_URL`.
Run it with `python build_data.py [--site PATH]`. It checks that each copy is byte-identical to its source,
has the expected columns, and has no missing values in them. It also checks that every country of
`fig3-7.csv` finds its region in `countries.csv`, since the notebook's `merge` example relies on it. Full
definitions, sources and validations are in the README of the source folder.

- `maddison_panel.csv`: `iso3, country, year, gdppc`, 965 rows: every available year from 1870 to 2022 for the
  United States, the United Kingdom, Japan, Argentina, South Africa, China and India. Copied from
  `data/ch03/maddison_panel.csv`. GDP per person in 2022 dollars.
  - Source: Maddison Project Database 2023 (Bolt & van Zanden, <https://doi.org/10.34894/INZBF2>), `gdppc` × 1.2902,
    the U.S. GDP deflator ratio 2022/2011.
  - Coverage: the United States and the United Kingdom have all 153 years; the others have gaps before 1950
    (China has 89 years). The notebook uses these gaps to teach missing values (`NaN`) after `pivot`.
- `fig3-7.csv`: `iso3, country, gdppc_rel_us_2019, growth_1960_2019_pct, gdppc_rel_us_2023, growth_1960_2023_pct`,
  111 countries. Copied from `data/ch03/fig3-7.csv`. GDP per person relative to the United States in 2019 and
  2023, and average annual growth from 1960.
  - Source: Penn World Table 11.0 (Feenstra, Inklaar and Timmer 2015, <https://doi.org/10.34894/FABVLR>),
    `rgdpe`/`pop`.
  - Known quirk: Venezuela's GDP per person after 2017 is not plausible, because hyperinflation broke the PWT
    price data. The notebook drops it from the scatter plot.
- `countries.csv`: `iso3, country, region, income, g7, g20, oecd`, 223 economies. Copied from
  `data/ch01/countries.csv`. World Bank regions and income groups (from the World Bank country API), plus
  Taiwan, three historical units and two euro-area aggregates, which have no income group (`income` is empty).
- `pwt_income.csv`: `iso3, country, year, gdp_pc, y_rel_us_2019, pop_millions, in_sample`, 11,201 rows, 185
  economies, 1950–2023. Copied from `data/ch03/pwt_income.csv`. `gdp_pc` is real GDP per person (`rgdpe`/`pop`)
  in 2021 dollars.
  - Source: Penn World Table 11.0 (<https://doi.org/10.34894/FABVLR>).
  - Used by the mini project (Section A.6): growth from 1990 to 2023 for the 182 economies with data in both
    years. Venezuela is dropped for the reason above.

The screenshots of the appendix are in `images/appA/` of this repository. They were taken in Google Colab on
2026-10-17, with the account name and picture removed.
