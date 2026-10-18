# Data for Appendix E: Growth and Convergence Across Countries

Read by `notebooks/appE-growth-and-convergence-across-countries.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appE/`.

`build_data.py` builds the file. Run it with `python build_data.py [--macro102 PATH]`. It downloads a copy of
the Penn World Table 10.0 (`pwt100.dta`) from the repository of Mendez, "Beta and Sigma Convergence Across
Countries: A Stata Tutorial" (<https://carlos-mendez.org/tutorials/stata_convergence/>), and caches it in
`../macro102/.work/appE/notebook-raw/`. It then applies that tutorial's sample rules, so the appendix
studies the same 84-country balanced panel.

## `pwt100_convergence.csv`

Columns: `ccode, country, year, pop, rgdpe, gdppc`. There are 5,040 rows: 84 countries × 60 years, 1960–2019,
with no gaps. Values are rounded to 6 significant digits.

- **Source:** [Penn World Table 10.0](https://www.rug.nl/ggdc/productivity/pwt/), Feenstra, Inklaar and Timmer
  (2015), "The Next Generation of the Penn World Table", *American Economic Review* 105(10), 3150–3182.
  DOI <https://doi.org/10.15141/S5Q94M>.
- **Variables:**
  - `ccode`: ISO 3166 alpha-3 country code (PWT `countrycode`);
  - `country`: PWT country name;
  - `year`: 1960–2019;
  - `pop`: population, millions;
  - `rgdpe`: expenditure-side real GDP at chained PPPs, millions of 2017 US dollars;
  - `gdppc`: real GDP per person, `rgdpe / pop`, 2017 US dollars.

## Sample rules (in this order)

1. Drop rows without `gdppc` or `pop`.
2. Drop the oil producers on the tutorial's list of 27 ISO codes:
   DZA, AGO, AZE, BHR, BRN, TCD, COG, ECU, GNQ, GAB, IRN, IRQ, KAZ, KWT, NGA, OMN, QAT, RUS, SAU, TTO, TKM, ARE,
   VEN, YEM, LBY, TLS, SDN.
   Of these, 25 have GDP data in PWT 10.0. This is why the tutorial's text says "25 oil producers", while
   its code lists 27.
3. Drop country-years with population under 1 million.
4. Keep 1960–2019.
5. Keep the countries with GDP per person in 1960. This drops 40 countries and leaves a balanced panel. Without
   this rule, the sample would grow from 84 countries in 1960 to 124 in 2019.

## Checks

The script asserts:
- 84 countries;
- 5,040 rows, with every country observed in every year from 1960 to 2019;
- no missing values.

It reproduces the tutorial's main estimates:
- OLS slope of annual growth on log initial GDP per person: 0.00057 (1960–2019), 0.00437 (1960–2000) and
  −0.00352 (2000–2019);
- variance of log GDP per person: 0.924 (1960) and 1.764 (2019).

The summary statistics of `gdppc` over the panel are a mean of 11,951, a median of 5,197 and a skewness of
1.76. They differ from the figures printed on the tutorial's web page (10,811, 4,873 and 2.16). The
regression and variance results match.
