# Data for Appendix F: The Augmented Solow Growth Model

Read by `notebooks/appF-augmented-solow-growth-model.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appF/`.

`build_data.py` builds both files. Run it with `python build_data.py [--macro102 PATH]`. Downloads are cached in
`../macro102/.work/appF/notebook-raw/`. The script checks MRW's sample sizes and reproduces the first column of
their Table I before it writes anything.

## `mrw1992.csv`

The data of Mankiw, Romer and Weil (1992), "A Contribution to the Empirics of Economic Growth", *Quarterly
Journal of Economics* 107(2), 407–437, <https://doi.org/10.2307/2118477>. They come from the appendix of the
paper, which draws on the Penn World Table 4.0 (Summers and Heston 1988) and on UNESCO enrollment data. The file
is the copy kept by QuaRCS-lab at
<https://github.com/quarcs-lab/data-quarcs/tree/master/mrw1992> (`mrw2.dta`), with readable column names.

121 rows, one per country. Columns:

- `iso3`: ISO 3166 alpha-3 code, added by hand. West Germany is `DEU`, Zaire is `COD`, Burma is `MMR`.
- `country`: MRW's name, spelled out where the paper abbreviates it (e.g. "S. Africa" → "South Africa").
- `region`: MRW's region (Africa, Asia, Europe, Latin America, North America, Oceania).
- `non_oil`, `intermediate`, `oecd`: 1 if the country is in MRW's sample. Non-oil (98 countries) drops the
  countries where oil production is the main industry. Intermediate (75) also drops countries with fewer than one
  million people in 1960 and countries whose data PWT 4.0 grades D. OECD (22) keeps the OECD members with more
  than one million people.
- `gdp_60`, `gdp_85`: real GDP per working-age person (ages 15–64), 1960 and 1985, in 1985 international dollars.
- `gdp_growth`: average annual growth of real GDP, 1960–1985, percent.
- `pop_growth`: average annual growth of the working-age population, 1960–1985, percent.
- `inv_gdp`: average share of real investment, including government investment, in real GDP, 1960–1985, percent.
- `school`: average percentage of the working-age population in secondary school, 1960–1985 (MRW's SCHOOL).

Missing values are the paper's: `gdp_60` is missing for 5 countries, `gdp_85` for 13, `pop_growth` for 14,
`gdp_growth` for 4 and `school` for 3. None of them is in the non-oil sample.

## `pwt_mrw.csv`

MRW's variables rebuilt with today's data, for two windows: `1960-1985` (MRW's own years) and `1990-2023`. One
row per economy and window: 111 economies in 1960–1985 and 182 in 1990–2023. An economy appears in a window
when it has GDP and population in the first and last years and an investment rate in every year.

- **Sources:**
  - [Penn World Table 11.0](https://www.rug.nl/ggdc/productivity/pwt/) (DOI
    <https://doi.org/10.34894/FABVLR>), Feenstra, Inklaar and Timmer (2015), "The Next Generation of the Penn
    World Table", *American Economic Review* 105(10), 3150–3182;
  - World Bank, World Development Indicators: [School enrollment, secondary (% gross)
    (`SE.SEC.ENRR`)](https://data.worldbank.org/indicator/SE.SEC.ENRR), [Population ages 15–19, female and
    male (% of female and of male population) (`SP.POP.1519.FE.5Y`,
    `SP.POP.1519.MA.5Y`)](https://data.worldbank.org/indicator/SP.POP.1519.FE.5Y), [Population, female and male
    (`SP.POP.TOTL.FE.IN`, `SP.POP.TOTL.MA.IN`)](https://data.worldbank.org/indicator/SP.POP.TOTL.FE.IN) and
    [Population ages 15–64, total (`SP.POP.1564.TO`)](https://data.worldbank.org/indicator/SP.POP.1564.TO).
- **Columns:**
  - `iso3`, `country`: PWT's code and name;
  - `region`: World Bank region, from `data/ch01/countries.csv` (empty for Anguilla and Montserrat, which the list does not
    cover);
  - `window`, `start`, `end`: the window, e.g. `1990-2023`, 1990, 2023;
  - `gdppc_start`, `gdppc_end`: real GDP per person (expenditure side, chained PPPs, `rgdpe / pop`) in the first
    and last year, 2021 US dollars;
  - `pop_start`: population in the first year, millions (`pop`);
  - `s_k`: the average investment share of GDP over the window, percent (100 × mean of `csh_i`, the share of
    gross capital formation at current PPPs);
  - `n`: the average annual growth rate of population over the window, percent (100 × ln(pop_end / pop_start) /
    years);
  - `school`: MRW's SCHOOL rebuilt from the WDI, percent, averaged over the years of the window with data:
    gross secondary enrollment × (population aged 15–19 / population aged 15–64). The population aged 15–19 is
    the female share times the female population plus the male share times the male population;
  - `school_years`: the number of years behind that average;
  - `hc_end`: PWT's human capital index in the last year of the window (`hc`, based on years of schooling and
    the returns to schooling);
  - `mrw_non_oil`, `mrw_intermediate`, `mrw_oecd`: MRW's sample flags, matched through `iso3`
    (0 for economies that are not in MRW's data);
  - `in_mrw`: 1 if the economy is one of MRW's 121 countries;
  - `oil`: 1 for the 27 oil producers that the book drops (the list of Appendix E: DZA, AGO, AZE, BHR, BRN, TCD,
    COG, ECU, GNQ, GAB, IRN, IRQ, KAZ, KWT, NGA, OMN, QAT, RUS, SAU, TTO, TKM, ARE, VEN, YEM, LBY, TLS, SDN). It
    is wider than MRW's oil rule, which kept Algeria, Ecuador, Nigeria, Trinidad and Tobago and Venezuela in
    their non-oil sample;
  - `small`: 1 if the population was under one million in the first year.
- **The full sample** of the appendix is every row with `oil == 0` and `small == 0`: 84 economies in 1960–1985
  and 123 in 1990–2023. Small economies are left out because a few tiny islands have implausible PWT
  investment rates (Bermuda's mean `csh_i` in 1990–2023 is above 300 percent).
- **Differences from MRW**, which the appendix discusses:
  - output is divided by the whole population (`pop`), not by the working-age population, and `n` is the
    growth of the whole population;
  - the investment share is at current PPPs (PWT's `csh_i`), not at constant prices;
  - the WDI's secondary enrollment starts in 1970 and is missing before 1986 for most OECD members (France,
    Japan and the United Kingdom among them). In 1960–1985, `school` therefore exists for 52 economies of the
    full sample and only 2 of MRW's OECD sample, and it averages the years 1970–1985 that have data. In
    1990–2023 it exists for 121 economies of the full sample;
  - MRW's non-oil and intermediate samples lose a few countries that PWT 11.0 does not cover in 1960
    (91 of 98 non-oil countries in 1960–1985, 97 in 1990–2023).
- Values are rounded to 5 significant digits.
