# Bolivia: the book's Bolivian data

Built by the macro102 `/write-bolivia-data` skill (`build_bolivia.py`); do not edit by hand.
The chapter files in `data/chNN/` take their Bolivian rows from these files.

- `bolivia_annual.csv`: year, series, value
- `bolivia_quarterly.csv`, `bolivia_monthly.csv`: date (first day of the period), series, value
- `series.csv`: what each series is, its unit, source and status
- `weo_fill.csv`: Bolivia's gaps in the IMF WEO, filled for the WEO Snapshots page

Status: *official* = published by a Bolivian institution (INE, Banco Central de Bolivia), read directly or through the IMF; *international* = compiled by the World Bank, the IMF WEO or the Penn World Table; *book estimate* = computed here (the method is in the note).

| freq | series | what | unit | source | status | years |
|---|---|---|---|---|---|---|
| M | `cpi` | Consumer price index | index (spliced series) | IMF CPI | official | 1957-01 to 2026-06 |
| M | `inflation_yoy` | CPI inflation, 12-month | % | IMF CPI | official | 1958-01 to 2026-06 |
| M | `fx_official` | Official exchange rate | bolivianos per U.S. dollar, period average | IMF ER | official | 1959-03 to 2026-10 |
| M | `fx_official_eop` | Official exchange rate, end of period | bolivianos per U.S. dollar | IMF ER | official | 1959-03 to 2026-10 |
| M | `fx_parallel` | Parallel-market exchange rate | bolivianos per U.S. dollar | IMF WPCPER | international | 2020-02 to 2025-10 |
| M | `tbill` | Treasury bill yield | % per year | IMF MFS_IR | official | 1994-01 to 2026-09 |
| M | `money_market` | Interbank money-market rate | % per year | IMF MFS_IR | official | 1995-01 to 2026-09 |
| M | `deposit_rate` | Deposit rate | % per year | IMF MFS_IR | official | 1987-01 to 2026-09 |
| M | `base_money` | Base money | bolivianos | IMF MFS_MA | official | 1977-12 to 2026-08 |
| M | `broad_money` | Broad money | bolivianos | IMF MFS_MA | official | 2001-12 to 2026-08 |
| M | `cb_assets` | Central bank total assets | bolivianos | IMF MFS_CBS | official | 2001-12 to 2026-08 |
| M | `unemployment_urban` | Urban unemployment rate | % | IMF LS | official | 2015-10 to 2024-12 |
| M | `employment` | Employed persons | persons | IMF LS | official | 2015-10 to 2024-12 |
| Q | `gdp_real` | Real GDP | thousands of 1990 bolivianos, not seasonally adjusted | INE Bolivia | official | 1990-01 to 2024-10 |
| Q | `unemployment_urban` | Urban unemployment rate | % | IMF LS | official | 1989-01 to 2025-04 |
| A | `gdp_real` | Real GDP | constant bolivianos | World Bank WDI NY.GDP.MKTP.KN | international | 1960 to 2025 |
| A | `gdp_nominal` | Nominal GDP | current bolivianos | World Bank WDI NY.GDP.MKTP.CN | international | 1960 to 2025 |
| A | `unemployment_ilo` | Unemployment rate (ILO modeled) | % of labor force | World Bank WDI SL.UEM.TOTL.ZS | international | 1991 to 2025 |
| A | `unemployment_national` | Unemployment rate (national estimate) | % of labor force | World Bank WDI SL.UEM.TOTL.NE.ZS | official | 1971 to 2025 |
| A | `emp_pop` | Employment-population ratio | % of population 15+ | World Bank WDI SL.EMP.TOTL.SP.ZS | international | 1991 to 2025 |
| A | `emp_pop_male` | Employment-population ratio, men | % of men 15+ | World Bank WDI SL.EMP.TOTL.SP.MA.ZS | international | 1991 to 2025 |
| A | `emp_pop_female` | Employment-population ratio, women | % of women 15+ | World Bank WDI SL.EMP.TOTL.SP.FE.ZS | international | 1991 to 2025 |
| A | `broad_money` | Broad money | current bolivianos | World Bank WDI FM.LBL.BMNY.CN | international | 1960 to 2025 |
| A | `broad_money_growth` | Broad money growth | % per year | World Bank WDI FM.LBL.BMNY.ZG | international | 1961 to 2025 |
| A | `broad_money_gdp` | Broad money | % of GDP | World Bank WDI FM.LBL.BMNY.GD.ZS | international | 1960 to 2025 |
| A | `cpi` | Consumer price index | index, 2010 = 100 | World Bank WDI FP.CPI.TOTL | international | 1960 to 2025 |
| A | `inflation` | CPI inflation | % per year | World Bank WDI FP.CPI.TOTL.ZG | international | 1960 to 2025 |
| A | `deposit_rate` | Deposit interest rate | % per year | World Bank WDI FR.INR.DPST | international | 1987 to 2025 |
| A | `lending_rate` | Lending interest rate | % per year | World Bank WDI FR.INR.LEND | international | 1987 to 2025 |
| A | `real_interest_rate` | Real interest rate | % per year | World Bank WDI FR.INR.RINR | international | 1987 to 2025 |
| A | `private_credit_gdp` | Domestic credit to the private sector | % of GDP | World Bank WDI FD.AST.PRVT.GD.ZS | international | 1960 to 2025 |
| A | `gross_national_saving` | Gross national saving | % of GNI | World Bank WDI NY.GNS.ICTR.ZS | international | 1976 to 2024 |
| A | `gfcf_gdp` | Gross fixed capital formation | % of GDP | World Bank WDI NE.GDI.FTOT.ZS | international | 1970 to 2024 |
| A | `gcf_gdp` | Gross capital formation | % of GDP | World Bank WDI NE.GDI.TOTL.ZS | international | 1970 to 2024 |
| A | `health_spending` | Current health expenditure | % of GDP | World Bank WDI SH.XPD.CHEX.GD.ZS | international | 2000 to 2023 |
| A | `public_debt_long` | Government debt | % of GDP | IMF GDD | international | 1970 to 2024 |
| A | `unemployment_urban` | Urban unemployment rate | % | IMF LS | official | 1971 to 2024 |
| A | `weo_growth` | Real GDP growth | % | IMF WEO | international | 1980 to 2031 |
| A | `weo_infl` | CPI inflation, annual average | % | IMF WEO | international | 1980 to 2031 |
| A | `weo_unemp` | Unemployment rate | % | IMF WEO | international | 2000 to 2031 |
| A | `weo_balance` | Government budget balance | % of GDP | IMF WEO | international | 1981 to 2031 |
| A | `weo_primary` | Primary budget balance | % of GDP | IMF WEO | international | 1985 to 2031 |
| A | `weo_revenue` | Government revenue | % of GDP | IMF WEO | international | 1981 to 2031 |
| A | `weo_spending` | Government spending | % of GDP | IMF WEO | international | 1981 to 2031 |
| A | `weo_debt` | Government gross debt | % of GDP | IMF WEO | international | 2000 to 2031 |
| A | `weo_net_debt` | Government net debt | % of GDP | IMF WEO | international | 2000 to 2031 |
| A | `weo_ca` | Current account balance | % of GDP | IMF WEO | international | 1980 to 2031 |
| A | `weo_saving` | Gross national saving | % of GDP | IMF WEO | international | 1980 to 2031 |
| A | `weo_investment` | Total investment | % of GDP | IMF WEO | international | 1981 to 2031 |
| A | `weo_exports` | Export volume growth | % | IMF WEO | international | 1980 to 2031 |
| A | `weo_imports` | Import volume growth | % | IMF WEO | international | 1980 to 2031 |
| A | `weo_ppp_pc` | GDP per person, PPP | international dollars | IMF WEO | international | 1980 to 2031 |
| A | `pwt_gdp_pc` | Real GDP per person (PWT) | 2021 U.S. dollars at PPP | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_tfp_index` | Total factor productivity (PWT rtfpna) | index, 2021 = 1 | Penn World Table 11.0 | international | 1954 to 2023 |
| A | `pwt_inv` | Investment share of GDP (PWT) | % of GDP | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_labsh` | Labor share (PWT) | % | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_price` | Price level of GDP (PWT) | U.S. = 1 | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_xr` | Exchange rate (PWT) | bolivianos per U.S. dollar | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_ky` | Capital-output ratio (PWT) | ratio | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_hc` | Human capital index (PWT) | index | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `pwt_pop` | Population (PWT) | millions | Penn World Table 11.0 | international | 1950 to 2023 |
| A | `tbill` | Treasury bill yield | % per year | IMF MFS_IR (annual mean) | official | 1994 to 2026 |
| A | `fx_official` | Official exchange rate | bolivianos per U.S. dollar | IMF ER (annual mean) | official | 1959 to 2026 |
| Q | `gdp_real_sa` | Real GDP, seasonally adjusted | thousands of 1990 bolivianos | INE Bolivia; seasonal adjustment by the book | book estimate | 1990-01 to 2024-10 |
| Q | `potential_q` | Potential GDP (trend) | thousands of 1990 bolivianos | INE Bolivia; HP trend by the book | book estimate | 1990-01 to 2024-10 |
| Q | `output_gap_q` | Output gap | % of potential GDP | INE Bolivia; HP gap by the book | book estimate | 1990-01 to 2024-10 |
| A | `potential` | Potential GDP (trend) | constant bolivianos | WDI + IMF WEO; HP trend by the book | book estimate | 1960 to 2031 |
| A | `output_gap` | Output gap | % of potential GDP | WDI + IMF WEO; HP gap by the book | book estimate | 1960 to 2031 |
| A | `structural_balance` | Structural budget balance | % of potential GDP | IMF WEO; adjusted for the cycle by the book | book estimate | 1981 to 2031 |

## Notes

- `cpi` (M): INE's CPI as reported to the IMF, spliced back to 1957 by the IMF.
- `inflation_yoy` (M): Change in INE's CPI over 12 months.
- `fx_official` (M): The BCB's official rate. Bolivia redenominated in 1987 (1 boliviano = 1,000,000 pesos bolivianos); the IMF series is in today's bolivianos throughout. Fixed at 6.86 to 6.96 since 2011.
- `fx_official_eop` (M): The BCB's official rate at the end of each month.
- `fx_parallel` (M): IMF Working Paper dataset of crypto-based parallel exchange rates (USDT-boliviano trades), monthly average. It tracks the street price of dollars after the 2023 dollar shortage.
- `tbill` (M): Yield on the BCB's open-market auctions of short-term government and BCB securities (Letras). Bolivia has no policy-rate target; this is the closest market rate the BCB steers.
- `money_market` (M): Overnight interbank rate in bolivianos.
- `deposit_rate` (M): Average bank deposit rate in bolivianos.
- `base_money` (M): Monetary base (currency plus bank reserves at the BCB), national definition.
- `broad_money` (M): Broad money in bolivianos and dollars, IMF definition.
- `cb_assets` (M): Total assets of the Banco Central de Bolivia.
- `unemployment_urban` (M): INE's Continuous Employment Survey (ECE), urban areas, reported to the IMF.
- `employment` (M): INE's Continuous Employment Survey (ECE), reported to the IMF.
- `gdp_real` (Q): INE, Cuadro 1.01.01, quarterly GDP at constant 1990 prices (the latest year is preliminary).
- `unemployment_urban` (Q): INE household and employment surveys, urban areas, reported to the IMF.
- `gdp_real` (A): World Bank WDI, from INE's national accounts.
- `gdp_nominal` (A): World Bank WDI, from INE's national accounts.
- `unemployment_ilo` (A): ILO modeled estimate, whole country, ages 15+.
- `unemployment_national` (A): INE's survey-based rate (urban before the 2010s), via the World Bank.
- `emp_pop` (A): ILO modeled estimate.
- `emp_pop_male` (A): ILO modeled estimate.
- `emp_pop_female` (A): ILO modeled estimate.
- `broad_money` (A): World Bank WDI, from the IMF's monetary statistics.
- `broad_money_growth` (A): World Bank WDI.
- `broad_money_gdp` (A): World Bank WDI.
- `cpi` (A): World Bank WDI, from INE's CPI.
- `inflation` (A): World Bank WDI, from INE's CPI (11,750% in 1985, the hyperinflation).
- `deposit_rate` (A): World Bank WDI, from the IMF's monetary statistics.
- `lending_rate` (A): World Bank WDI.
- `real_interest_rate` (A): Lending rate adjusted by the GDP deflator, World Bank WDI.
- `private_credit_gdp` (A): World Bank WDI.
- `gross_national_saving` (A): World Bank WDI. Households, firms and government together: Bolivia publishes no household saving rate.
- `gfcf_gdp` (A): World Bank WDI, public and private together.
- `gcf_gdp` (A): World Bank WDI: fixed investment plus inventories.
- `health_spending` (A): WHO Global Health Expenditure Database, via the World Bank.
- `public_debt_long` (A): IMF Global Debt Database, public debt (the IMF's mixed coverage: central government, and general government where available), 1970 on. The Database has no Bolivian household debt; the book uses domestic credit to the private sector instead.
- `unemployment_urban` (A): INE household and employment surveys, urban areas, reported to the IMF.
- `weo_growth` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_infl` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_unemp` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_balance` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_primary` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_revenue` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_spending` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_debt` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_net_debt` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_ca` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_saving` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_investment` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_exports` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_imports` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `weo_ppp_pc` (A): IMF World Economic Outlook, October 2026; years after 2025 are IMF projections.
- `pwt_gdp_pc` (A): Penn World Table 11.0.
- `pwt_tfp_index` (A): Penn World Table 11.0.
- `pwt_inv` (A): Penn World Table 11.0.
- `pwt_labsh` (A): Penn World Table 11.0.
- `pwt_price` (A): Penn World Table 11.0.
- `pwt_xr` (A): Penn World Table 11.0.
- `pwt_ky` (A): Penn World Table 11.0.
- `pwt_hc` (A): Penn World Table 11.0.
- `pwt_pop` (A): Penn World Table 11.0.
- `tbill` (A): Annual average of the monthly BCB auction yield (IMF).
- `fx_official` (A): Annual average of the IMF's monthly official rate.
- `gdp_real_sa` (Q): INE's quarterly real GDP, seasonally adjusted by the book (STL decomposition of the log, period 4).
- `potential_q` (Q): Hodrick-Prescott trend (lambda = 1600) of seasonally adjusted real GDP. Bolivia publishes no potential GDP; HP trends are least reliable at the end of the sample.
- `output_gap_q` (Q): 100 x log(real GDP / HP trend), lambda = 1600, from INE's quarterly GDP.
- `potential` (A): Hodrick-Prescott trend (lambda = 100) of real GDP, as for the output gap.
- `output_gap` (A): 100 x log(real GDP / HP trend), lambda = 100, on WDI real GDP 1960-2025 extended with the IMF WEO growth projections to 2031 (which softens the HP end-point problem). Bolivia publishes no output gap.
- `structural_balance` (A): General government balance (IMF WEO) minus eps x output gap, with eps = revenue / GDP (revenue moves one for one with output, spending does not react). It ignores the swings of gas prices, which drive much of Bolivia's revenue.
