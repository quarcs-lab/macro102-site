# Data for Appendix G: Growth and Institutions

Read by `notebooks/appG-growth-and-institutions.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appG/`.

`build_data.py` builds the file. Run it with `python build_data.py [--macro102 PATH]`. Downloads are cached in
`../macro102/.work/appG/notebook-raw/`. Before it writes anything, the script checks that the base sample has 64
countries and reproduces AJR's headline numbers: OLS 0.52, first stage −0.61 and 2SLS 0.94.

## `ajr2001.csv`

The data of Acemoglu, Johnson and Robinson (2001), "The Colonial Origins of Comparative Development: An Empirical
Investigation", *American Economic Review* 91(5), 1369–1401, <https://doi.org/10.1257/aer.91.5.1369>. The source is
their replication files `maketable1.dta`, `maketable2.dta` and `maketable4.dta`, from
[Daron Acemoglu's data archive](https://economics.mit.edu/people/faculty/daron-acemoglu/data-archive), as kept with
the tutorial [*Do Institutions Cause Prosperity? An IV Tutorial in Python*](https://carlos-mendez.org/tutorials/python_iv/)
(github.com/cmg777/starter-academic-v501, `content/tutorials/stata_iv/`).

163 rows, one per country of AJR's Table 2. The spine is `maketable2.dta`. `logem4` comes from `maketable4.dta`,
and the rest of the Table 1 variables from `maketable1.dta`. That file repeats Germany, Yugoslavia and Zimbabwe on
two rows; the first non-missing value of each column is kept. Columns:

- `code`: AJR's country code. `iso3`: today's ISO 3166 alpha-3 code (they differ for a few old codes, e.g. Zaire
  `ZAR` → `COD`, Romania `ROM` → `ROU`).
- `country`: the World Bank's name for `iso3`, with a few names written by hand (e.g. Taiwan, Hong Kong).
- `continent`: Africa, Asia, Other (Australia, Malta, New Zealand) or Americas, from AJR's continent dummies.
- `base`: 1 for the 64 former colonies of AJR's base sample (`baseco`).
- `logpgp95`: log GDP per person in 1995, at purchasing power parity (World Bank).
- `avexpr`: average protection against expropriation risk, 1985–1995, from 0 to 10 (Political Risk Services).
- `extmort4`: settler mortality, in annual deaths per 1,000 mean strength. `logem4`: its log, AJR's instrument.
- `lat_abst`: absolute latitude divided by 90.
- `africa`, `asia`, `other`: AJR's continent dummies.
- `euro1900`: percent of the population of European descent in 1900. `cons00a`: constraint on the executive in
  1900. `democ00a`: democracy in 1900. `cons1`: constraint on the executive in the first year of independence.
- `loghjypl`: log output per worker in 1988 relative to the United States, from Hall and Jones (1999).

Missing values are the paper's. The base sample has every value of `logpgp95`, `avexpr` and `logem4`.
