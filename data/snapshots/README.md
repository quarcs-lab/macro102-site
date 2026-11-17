# PWT Snapshots data

The data behind the book's interactive [PWT Snapshots](https://quarcs-lab.github.io/macro102-site/apps/pwt-snapshots.html) page, built from the [Penn World Table 11.0](https://www.rug.nl/ggdc/productivity/pwt/) (Feenstra, Inklaar and Timmer 2015) by the `/write-pwt-snapshots` skill. Generated: do not edit by hand.

`country_snapshots.csv` has one row per country and year (1950-2023). Values are rounded to 6 significant digits. An empty cell is a missing value.

| Column | Definition (PWT 11.0 variables) | Unit |
|---|---|---|
| `iso3` | three-letter country code (PWT countrycode; WLD = World average) |  |
| `country` | country name (short form) |  |
| `year` | year |  |
| `pop` | population, pop | millions |
| `gdp_pc` | GDP per capita, rgdpo / pop | 2017 US dollars (PPP) |
| `gdp_pw` | GDP per worker, rgdpo / emp | 2017 US dollars (PPP) |
| `growth` | growth rate of GDP per capita, percent change of gdp_pc from the year before | % per year |
| `inv` | investment share of GDP, 100 x csh_i | % of GDP (current PPP) |
| `gov` | government consumption share of GDP, 100 x csh_g | % of GDP (current PPP) |
| `hc` | human capital index, hc | index |
| `nx` | net exports including the residual, 100 x (csh_x + csh_m + csh_r) | % of GDP (current PPP) |
| `open` | openness, exports plus imports, 100 x (csh_x - csh_m) | % of GDP (current PPP) |
| `xr` | exchange rate, xr | national currency per US dollar |
| `tfp` | TFP level at current PPPs, ctfp | USA = 1 |
| `tfp_index` | TFP at constant national prices, rtfpna | 2017 = 1 |
| `ky` | capital-output ratio, cn / cgdpo | ratio (current PPP) |
| `emp_pop` | employment-population ratio, 100 x emp / pop | % of population |
| `hours` | average annual hours worked per worker, avh | hours |
| `labsh` | labor share, 100 x labsh | % of GDP |
| `price` | price level of GDP, pl_gdpo | US GDP price level in 2017 = 1 |

Rows with `iso3` = `WLD` are the **World average**: population-weighted averages over a fixed sample of countries with complete data for 1970-2023, one sample per variable (GDP per worker is total GDP over total employment). Countries in each sample: `gdp_pc` 158, `gdp_pw` 113, `hc` 129, `tfp` 81.
