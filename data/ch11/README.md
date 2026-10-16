# Data for Chapter 11: The IS Curve

Read by `notebooks/ch11-the-is-curve.ipynb` from
`https://raw.githubusercontent.com/quarcs-lab/macro102-site/main/data/ch11/`.

## Files copied from the macro102 collect-data output

- `fig11-6.csv`: `date, unemployment_rate, cbo_no_stimulus, cbo_low, cbo_high`. Monthly rows, 2009-01 to 2026-09 (213 rows). All values in percent.
  - `unemployment_rate`: the U.S. civilian unemployment rate, seasonally adjusted, BLS Current Population Survey via FRED (`UNRATE`, <https://fred.stlouisfed.org/series/UNRATE>), unchanged.
  - `cbo_no_stimulus`, `cbo_low`, `cbo_high`: the Congressional Budget Office's February 2009 forecasts of the unemployment rate without the stimulus package (the baseline) and with its "low" and "high" estimated effects. Fourth-quarter values for 2009–2019, from Table 1 of the CBO letter to Senator Judd Gregg, "Estimated Macroeconomic Impacts of H.R. 1 as Passed by the House and by the Senate", 11 February 2009 (PDF from the Internet Archive copy of <https://www.cbo.gov/sites/default/files/cbofiles/ftpdocs/99xx/doc9987/gregg_year-by-year_stimulus.pdf>). Each value sits on the first month of its fourth quarter (`YYYY-10-01`); the other rows are empty.
  - Known quirks: October 2025 has no unemployment rate, because the BLS did not collect the survey during the federal government shutdown. All three CBO paths reach the CBO's long-run rate of 4.8 percent by 2015. The textbook draws the CBO's annual values at mid-year, so in our chart the forecast lines sit about one quarter to the right of the book's.

Full definitions and the validation against the textbook are in macro102's
`original-scanned-book/ch11-the-is-curve/data/fig11-6/notes.md`.

## Wider files built for the notebook widgets

None. The chapter's only data figure uses `fig11-6.csv` as copied, and the model figures need no data.

The figure stays U.S.-only (conventions §6b): its subject is the CBO's February 2009 forecasts of the U.S.
unemployment rate with and without the ARRA stimulus, a series that exists only for the U.S. Cross-country
unemployment rates (OECD, 40 economies) are in `data/ch10/unemployment_panel.csv`, used by the Chapter 10 notebook.
