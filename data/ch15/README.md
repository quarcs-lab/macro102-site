# Data for Chapter 15: DSGE Models: The Frontier of Business Cycle Research

Read by `notebooks/ch15-dsge-models-the-frontier-of-business-cycle-research.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch15/`.

## Files copied from the macro102 collect-data output

- `fig15-1.csv`: `year, tfp_growth`. Growth of utilization-adjusted total factor productivity, U.S. business
  sector, percent per year (100 × change in the log of the annual-average level), 1950 to 2025 (76 years).
  - Source: John Fernald, "A Quarterly, Utilization-Adjusted Series on Total Factor Productivity," Federal
    Reserve Bank of San Francisco, file `quarterly_tfp.xlsx` (<https://www.frbsf.org/wp-content/uploads/quarterly_tfp.xlsx>),
    sheet `annual`, column `dtfp_util`, release of October 2026.
  - Known quirks: the textbook caption speaks of "Solow growth accounting", but its line is the
    **utilization-adjusted** series, not the raw Solow residual (2009: 3.53 here and in the textbook, −0.15 for the
    raw residual). Revised recent years differ from the textbook's vintage: 2021 is 1.26 here, about 0.45 in the
    textbook.

Full definitions, vintages and the validation against the textbook are in macro102's
`original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/notes.md`.

## Wider files built for the notebook

These files are made by `build_data.py` from the raw files saved by macro102's `/collect-data`
(`original-scanned-book/ch15-dsge-models-the-frontier-of-business-cycle-research/data/fig15-1/raw/`).
Run it with `python build_data.py --macro102 PATH`.

- `recessions.csv`: `peak, trough`. The 11 NBER recessions since 1950, from 1953-07 / 1954-05 to 2020-02 / 2020-04
  (first day of the month).
  - Source: NBER-based recession indicator `USREC` (monthly) via FRED (<https://fred.stlouisfed.org/series/USREC>).
    `peak` is the month before the first recession month, `trough` the last recession month.
  - Used to shade the recessions in Figure 1.
- `tfp_annual.csv`: `year, gdp_growth, tfp_solow, utilization, tfp_util`. U.S. business sector, percent per year,
  1950 to 2025 (76 rows, no missing values), from the same Fernald file (sheet `annual`):
  - `gdp_growth` = `dY`, growth of business output;
  - `tfp_solow` = `dtfp`, the raw Solow residual (growth accounting with no correction);
  - `utilization` = `dutil`, Fernald's estimate of the growth in how intensively capital and labor are used;
  - `tfp_util` = `dtfp_util`, utilization-adjusted TFP growth, the series of textbook Figure 15.1.
  - Validation: `tfp_util` equals `fig15-1.csv` in all 76 years (largest gap 5e-5, from rounding), and
    `tfp_util` ≈ `tfp_solow` − `utilization` within 0.04 points (annual averages of quarterly logs make the
    identity approximate). `build_data.py` stops if either check fails.
  - Range check: `gdp_growth` runs from −3.75 (2009) to 9.40 (1950); `tfp_solow` from −3.72 (1974) to 7.17 (1950).
    These are real swings, not errors.
  - Used for the "Which TFP?" comparison in Figure 1.
- `tfp_inputs.csv`: `year, gdp_growth, hours_growth, capital_growth, labor_quality, capital_share, tfp_solow,
  utilization, tfp_util`. The growth-accounting inputs behind Fernald's TFP series, U.S. business sector, 1950 to 2025
  (76 rows, no missing values), from the same Fernald file (sheet `annual`). Growth rates are in percent per year
  (100 × change in the log of the annual-average level):
  - `gdp_growth` = `dY`, `tfp_solow` = `dtfp`, `utilization` = `dutil` and `tfp_util` = `dtfp_util`, exactly as in
    `tfp_annual.csv`;
  - `hours_growth` = `dhours`, hours worked in the business sector (from the BLS productivity and costs release);
  - `capital_growth` = `dk`, capital input (capital stocks weighted by their user costs);
  - `labor_quality` = `dLQ`, growth of labor composition (the skill and experience mix of the hours worked; BLS
    estimates before 1979:Q2, the Aaronson–Sullivan method after);
  - `capital_share` = `alpha`, capital's share of income (a share, not a growth rate).
  - Validation: the four shared columns equal `tfp_annual.csv` in every year, and Fernald's identity
    `tfp_solow` = `gdp_growth` − `capital_share` × `capital_growth` − (1 − `capital_share`) × (`hours_growth` +
    `labor_quality`) holds within 0.10 points (exact for quarterly data, approximate for annual averages).
    `build_data.py` stops if either check fails.
  - Range check: `hours_growth` runs from −7.74 (2009) to 5.68 (1984); `capital_growth` from 1.44 (2010) to 6.33
    (2000); `labor_quality` from −0.42 (2021) to 1.63 (2020); `capital_share` from 0.295 (1970) to 0.418 (2025).
  - Used in the Practice problems (growth accounting by hand, hours and TFP, the Frisch elasticity, the 2009 recession).

## Multi-country file (beyond the United States)

Built by `build_data.py` from public downloads, cached in macro102's `.work/ch15/notebook-raw/` (delete a file there to
download it again).

- `pwt_growth.csv`: `iso3, country, region, year, tfp_growth, gdp_growth`. Every country of the Penn World Table 11.0
  with TFP data: 120 countries, 1955 to 2023, 6,868 rows (about 360 kB).
  - `tfp_growth` = 100 × change in the log of `rtfpna` (TFP at constant national prices, 2017 = 1);
    `gdp_growth` = 100 × change in the log of `rgdpna` (real GDP at constant national prices); percent per year.
    Log changes can fall below −100 (Iraq 1991: −105).
  - `region` is the World Bank region; names follow the World Bank's country list with the readable names of
    `data/ch01/build_data.py` (Taiwan added by hand).
  - Sources: PWT 11.0, `pwt110.dta` (DataverseNL, doi:10.34894/FABVLR; macro102's `.work/downloads/` copy is used
    when present) and <https://api.worldbank.org/v2/country?format=json&per_page=400>.
  - Concept: PWT's TFP is a **raw Solow residual** (no utilization adjustment), so it corresponds to `tfp_solow` in
    `tfp_annual.csv`, not to the utilization-adjusted series of Figure 15.1. Validation: for the United States,
    1955–2023, PWT TFP growth has a correlation of 0.93 with Fernald's `tfp_solow` and 0.29 with `tfp_util`; PWT's
    GDP growth has a correlation of 0.98 with Fernald's business-output growth. `build_data.py` stops if the first
    correlation falls below 0.6.
  - Data hygiene: wars and collapses give extreme values (Iraq 1991 −105, Kuwait 1991 −51, Macao 2020 −80, Kuwait
    1992 +55). The series start in 1954–1994 (1994 for the former Soviet, Yugoslav and Czechoslovak states).
  - Used in Figure 1, "Beyond the United States".
