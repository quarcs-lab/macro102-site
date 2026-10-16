# Data for Chapter 21: Parting Thoughts

Read by `notebooks/ch21-parting-thoughts.ipynb` from `https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch21/`.

## Files copied from the macro102 collect-data output

None. Chapter 21 has no figures, so `prepare.py` copied no file.

## Wider files built for the notebook widgets

Chapter 21 gets a short recap notebook that recomputes a few of the book's key numbers. `build_data.py` copies
the seven small files it needs, unchanged, from the `data/` folders of earlier chapters in this site repo, so the
notebook reads everything from its own `DATA_URL`. Run it with `python build_data.py [--site PATH]`. It checks that
each copy is byte-identical to its source, has the expected columns and has no missing values in them. Full
definitions, sources and validations are in the README of the source folder.

- `fig4-5.csv`: `iso3, country, gdp_pc_rel_2023, pred_gdp_pc_2023`, 111 countries, 2023. Copied from
  `data/ch04/fig4-5.csv`. Actual GDP per person and the production model's prediction from capital alone,
  $k^{1/3}$, both relative to the United States.
  - Source: Penn World Table 11.0 (<https://doi.org/10.34894/FABVLR>), with capital per person built by perpetual
    inventory from investment (see `data/ch04/README.md`).
  - Validation: merged with `fig4-7.csv`, `pred_gdp_pc_2023 × tfp_2023` reproduces `gdp_pc_rel_2023` in all 111
    countries (largest relative gap 8e-6); `build_data.py` stops if it does not.
  - Known quirk: Venezuela's 2023 GDP per person (0.2 percent of the U.S. level) is not plausible, because
    hyperinflation broke the PWT price data. The notebook drops it in Lesson 1.
- `fig4-7.csv`: `iso3, country, gdp_pc_rel_2023, tfp_2023`, the same 111 countries, 2023. Copied from
  `data/ch04/fig4-7.csv`. Relative GDP per person and the implied total factor productivity $\bar{A} = y/k^{1/3}$
  (U.S. = 1). Source: as for `fig4-5.csv`.
- `maddison_panel.csv`: `iso3, country, year, gdppc`, 965 rows: every available year from 1870 to 2022 for the
  United States, the United Kingdom, Japan, Argentina, South Africa, China and India. Copied from
  `data/ch03/maddison_panel.csv`. GDP per person in 2022 dollars.
  - Source: Maddison Project Database 2023 (Bolt & van Zanden, <https://doi.org/10.34894/INZBF2>), `gdppc` × 1.2902,
    the U.S. GDP deflator ratio 2022/2011.
  - Annual coverage has gaps before 1950 for some countries (Japan has 140 of the 153 years; China 89), but the
    United States, the United Kingdom and Japan are complete from 1950. The notebook uses 1870, 1950, 2000, 2022
    and every year from 1950 for Japan and the United States.
- `maddison_world.csv`: `iso3, country, region, year, gdppc`, 15,890 rows, 169 economies, 761 kB: every available
  year from 1870 (mostly from 1950) to 2022. Copied from `data/ch03/maddison_world.csv`. GDP per person in 2022
  dollars and the Maddison region of each economy.
  - Source: Maddison Project Database 2023 (Bolt & van Zanden, <https://doi.org/10.34894/INZBF2>), as for
    `maddison_panel.csv` (see `data/ch03/README.md`).
  - Validation: `build_data.py` checks that its rows reproduce all 965 rows of `maddison_panel.csv` (largest gap
    0.00) and that the United States is complete from 1950 to 2022.
  - Used by the country picker of Lesson 2 (GDP per person relative to the United States since 1950) and by the
    region menu of its website version. Coverage: 33 to 73 years per economy since 1950; 23 economies start
    later, most of them former Soviet, Yugoslav and Czechoslovak republics (1973 or later) and North Korea (1990). Names are the Maddison (UN-style) names, e.g. "Republic of Korea".
- `fig8-4.csv`: `iso3, country, money_growth_*, inflation_*, n_money_*, n_infl_*, n_infl_filled_*` for the windows
  1990–2021 and 1990–2025, 165 economies. Copied from `data/ch08/fig8-4.csv`. Arithmetic means of annual
  broad-money growth and CPI inflation, percent.
  - Sources: World Bank WDI `FM.LBL.BMNY.ZG` and `FP.CPI.TOTL.ZG` (<https://api.worldbank.org/v2/>), with inflation
    gaps filled from the World Bank's Global Inflation Database (Ha, Kose & Ohnsorge).
  - Known quirk: for Georgia and Venezuela the money averages cover fewer years than the inflation averages
    (the `n_` columns), so both sit above the cross-country band; Chapter 8 explains why.
- `fig13-17.csv`: `year, output_gap, inflation`, United States, annual, 1960–2025. Copied from
  `data/ch13/fig13-17.csv`. `output_gap` = 100 (Y/Ȳ − 1), percent; `inflation` is the percent change of the
  annual-average CPI.
  - Sources: FRED `GDPC1`, `GDPPOT` and `CPIAUCSL` (<https://fred.stlouisfed.org/>), current vintage. The
    unpublished October 2025 CPI is interpolated.
  - Used for the Phillips curve slope (Lesson 4) and the cost of the Volcker disinflation (Lesson 5).
- `growth_accounting.csv`: `year, output_per_hour, contrib_capital, contrib_labor_composition, tfp`, U.S. private
  business sector, annual, 1948–2025, indexes with 2017 = 100. Copied from `data/ch06/growth_accounting.csv`.
  - Source: BLS, "Total factor productivity and related measures for major industries, linked SIC-NAICS",
    release of March 19, 2026 (<https://www.bls.gov/productivity/tables/total-factor-productivity-major-sectors-historical.xlsx>).
  - Used for the productivity slowdown after 2003 (the open questions section). Its period averages reproduce the
    textbook's Table 6.2 (see `data/ch06/README.md`).
