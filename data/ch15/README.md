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

Both files are made by `build_data.py` from the raw files saved by macro102's `/collect-data`
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
