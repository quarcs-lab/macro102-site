# WEO Snapshots data

The data behind the book's interactive [WEO Snapshots](https://quarcs-lab.github.io/macro102-site/apps/weo-snapshots.html) page, from the IMF [World Economic Outlook](https://data.imf.org/en/datasets/IMF.RES:WEO) (October 2026), built by the `/write-weo-snapshots` skill. Generated: do not edit by hand.

`weo_snapshots.csv` has one row per country (or WEO group), year and variable (1980-2031). Values are rounded to 6 significant digits. Missing values have no row.

| Column | Definition |
|---|---|
| `iso3` | three-letter country code (IMF), or a WEO group code (G001 = World) |
| `country` | country or group name (short form) |
| `year` | year |
| `variable` | the variable (see the table below) |
| `value` | its value |
| `status` | "actual" or "IMF projection" (the years after last_actual) |
| `last_actual` | the last year of actual data of this country and variable |

| Variable | Definition (WEO indicator) | Unit |
|---|---|---|
| `growth` | Real GDP growth (`NGDP_RPCH`) | % per year |
| `infl` | Inflation (average) (`PCPIPCH`) | % per year (consumer prices) |
| `infl_eop` | Inflation (end of year) (`PCPIEPCH`) | % per year (consumer prices) |
| `unemp` | Unemployment rate (`LUR`) | % of the labor force |
| `gap` | Output gap (`NGAP_NPGDP`) | % of potential GDP |
| `balance` | Overall balance (`GGXCNL_NGDP`) | % of GDP |
| `primary` | Primary balance (`GGXONLB_NGDP`) | % of GDP |
| `struct` | Structural balance (`GGSB_NPGDP`) | % of potential GDP |
| `revenue` | Revenue (`GGR_NGDP`) | % of GDP |
| `spending` | Spending (`GGX_NGDP`) | % of GDP |
| `debt` | Gross debt (`GGXWDG_NGDP`) | % of GDP |
| `net_debt` | Net debt (`GGXWDN_NGDP`) | % of GDP |
| `ca` | Current account (`BCA_NGDPD`) | % of GDP |
| `saving` | National saving (`NGSD_NGDP`) | % of GDP |
| `investment` | Investment (`NID_NGDP`) | % of GDP |
| `exports` | Exports (`TX_RPCH`) | % change in volume |
| `imports` | Imports (`TM_RPCH`) | % change in volume |
| `ppp_share` | Share of world GDP (`PPPSH`) | % of world GDP (PPP) |
| `ppp_pc` | GDP per capita (`PPPPC`) | international dollars (PPP, current prices) |
| `pop` | Population (`LP`) | millions |

The years after `last_actual` are IMF projections. The IMF gives the last actual year per country and indicator; a fiscal year FY2024/25 counts as 2024. Series without it (the PPP series, most groups) take the last actual year of the country's real GDP growth, or else 2025.

Groups (`iso3` codes from the IMF): `G001` World, `G110` Advanced economies, `G200` Emerging and developing economies, `G119` G7, `G163` Euro area, `G998` European Union, `GX123` Other advanced economies, `G505` Emerging and developing Asia, `G903` Emerging and developing Europe, `G205` Latin America and the Caribbean, `G400` Middle East and Central Asia, `G603` Sub-Saharan Africa.
