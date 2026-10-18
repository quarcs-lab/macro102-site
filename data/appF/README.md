# Data for Appendix F: Growth and Development Accounting

Read by `notebooks/appF-growth-and-development-accounting.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/appF/`.

`build_data.py` builds both files. Run it from the sibling `macro102` checkout with
`python build_data.py [--macro102 PATH]`. It downloads Penn World Table 11.0 from DataverseNL, or copies it
from macro102's bulk cache `.work/downloads/pwt110.dta` when that file exists. It also downloads the World Bank
series through the WDI API. Both downloads are cached in `../macro102/.work/appF/notebook-raw/`.

The script checks that:
- no country-year appears twice;
- every economy has a region;
- each file is under 1 MB.

It also prints the coverage counts used in the notebook.

## `pwt_accounting.csv`

Columns: `iso3, country, region, year, rgdpna, rnna, emp, avh, hc, rgdpo, cgdpo, cn, labsh`. There are 9,403
rows: every PWT 11.0 economy (185) from 1970 to 2023, except rows with no output data. Values are rounded to 5
significant digits.

- **Source:** [Penn World Table 11.0](https://www.rug.nl/ggdc/productivity/pwt/), Feenstra, Inklaar and Timmer
  (2015), "The Next Generation of the Penn World Table", *American Economic Review* 105(10), 3150–3182.
  DOI <https://doi.org/10.34894/FABVLR>.
- **`country`:** the PWT name. **`region`:** the World Bank region, copied from `data/ch01/countries.csv`.
  Anguilla and Montserrat are not in that list; they are set to Latin America & Caribbean by hand.
- **Variables:**

  | Column | PWT definition | Used for |
  |---|---|---|
  | `rgdpna` | real GDP at constant 2021 national prices (million 2021 US$) | growth accounting: output growth |
  | `rnna` | capital stock at constant 2021 national prices (million 2021 US$) | growth accounting: capital growth |
  | `emp` | number of persons engaged (millions) | both: labour input |
  | `avh` | average annual hours worked by persons engaged | both: labour in hours |
  | `hc` | human capital index, from years of schooling and returns to education | both: human capital |
  | `rgdpo` | output-side real GDP at chained PPPs (million 2021 US$) | development accounting: output per worker |
  | `cgdpo` | output-side real GDP at current PPPs (million 2021 US$) | development accounting: the K/Y ratio |
  | `cn` | capital stock at current PPPs (million 2021 US$) | development accounting: the K/Y ratio |
  | `labsh` | share of labour compensation in GDP at current national prices | development accounting: country labour shares |

- **Coverage:**
  - 175 economies have complete `rgdpna`, `rnna` and `emp` for 2004–2023, the same count as the
    [Growth Atlas](https://growthatlas.org/#/method).
  - 147 economies have complete `rgdpna`, `rnna` and `emp` for 1989–2023, but only 50 also have complete
    `avh` and `hc`.
  - In 2023:
    - 144 economies have every series needed for development accounting per worker;
    - 120 have every series needed per hour (`avh` is needed too);
    - 120 have every series needed with country labour shares.
- **Validation:** growth accounting with α = 0.33 reproduces the Growth Atlas numbers for the United States,
  Mexico, China, India, Korea and Nigeria. That covers 204 country-years, 1990–2023. The largest difference
  is 0.012 percentage points, which comes from the Atlas's rounding to two decimals.
- **Known quirks:**
  - Venezuela's output per worker after 2017 is not plausible, because hyperinflation broke the PWT price
    data. The notebook drops Venezuela from the development-accounting cross-section.
  - Country labour shares (`labsh`) are very low in some oil and mining economies (Qatar 0.18, Angola 0.22 in
    2023), because resource rents count as capital income. The notebook uses this to show why a common
    α is the standard choice.

## `nat_res_rents.csv`

Columns: `iso3, year, rents_pct, carried_forward`. There are 8,512 rows for 181 PWT economies, 1970–2023.

- **Source:** World Bank, World Development Indicators,
  [Total natural resources rents (% of GDP) (`NY.GDP.TOTL.RT.ZS`)](https://data.worldbank.org/indicator/NY.GDP.TOTL.RT.ZS).
  This is the sum of oil, natural gas, coal, mineral and forest rents.
- **Gap filling:** the WDI series ends in 2021. Each economy's last value is carried forward to 2023, and those
  385 rows have `carried_forward = True`.
- **Use:** the notebook's natural-resource adjustment, following Caunedo's
  [STEG Lecture 2](https://github.com/julicaunedo/STEG_Lecture2) code. It scales `rgdpo` and `cgdpo` by
  (1 − `rents_pct`/100), so that GDP counts only the output of reproducible capital, labour and TFP.
