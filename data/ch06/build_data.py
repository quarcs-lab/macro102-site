"""Build the wider data files used by the Chapter 6 notebook.

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Inputs (saved by the macro102 /collect-data skill, under
original-scanned-book/ch06-growth-and-ideas/data/):
  fig6-6/raw/fred_GDPCA.csv              real GDP, billions of chained 2017 dollars, annual (BEA via FRED)
  fig6-6/raw/fred_B230RC0A052NBEA.csv    population, thousands, annual (BEA NIPA Table 2.1 via FRED)
  fig6-6/raw/fred_USREC.csv              NBER recession indicator, monthly (1 = recession month)
  table6-2/raw/bls_tfp-major-sectors-historical_20260819.xlsx
                                         BLS total factor productivity, major sectors, release of March 2026
Outputs (next to this script):
  us_gdp_pc.csv          year, gdp_pc            U.S. real GDP per person, chained 2017 dollars, 1929-2025
  recessions.csv         peak, trough, peak_year, trough_year
                                                 NBER business-cycle peaks and troughs since 1960 (monthly dates
                                                 and decimal years)
  growth_accounting.csv  year, output_per_hour, contrib_capital, contrib_labor_composition, tfp
                                                 BLS indexes (2017 = 100), private business sector, 1948-2025

Multi-country and wider files (conventions section 6b). Downloads are cached in
../macro102/.work/ch06/notebook-raw/ (delete a file there to download it again):
  commodity_prices.csv   commodity, group, year, real_price_1900_100, extended_with_world_bank
                                                 all 40 commodities of Jacks (2019), real (U.S. CPI deflated),
                                                 1900 = 100, 1900-2020, extended to 2025 with the World Bank
                                                 Pink Sheet where it has a matching price (inputs: fig6-5/raw/)
  gdp_pc_countries.csv   iso3, country, region, year, gdp_pc
                                                 real GDP per person (PWT 11.0 rgdpna / pop, 2021 US dollars),
                                                 every PWT country, 1950-2023 (for Figure 6.6 beyond the U.S.)
"""
import argparse
import json
import os
import shutil

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = "original-scanned-book/ch06-growth-and-ideas/data/"
BLS = "table6-2/raw/bls_tfp-major-sectors-historical_20260819.xlsx"
MEASURES = {"Labor productivity": "output_per_hour",
            "Contribution of capital intensity to labor productivity": "contrib_capital",
            "Contribution of labor composition to labor productivity": "contrib_labor_composition",
            "Total factor productivity": "tfp"}


def fred(root, name):
    d = pd.read_csv(os.path.join(root, "fig6-6/raw", f"fred_{name}.csv"))
    d["year"] = d.observation_date.str[:4].astype(int)
    return d.set_index("year")[name]


def gdp_per_person(root):
    """Real GDP per person (dollars) = GDPCA (billions) / population (thousands) x 1e6."""
    y = (fred(root, "GDPCA") / fred(root, "B230RC0A052NBEA") * 1e6).dropna().round(1)
    out = pd.DataFrame({"year": y.index, "gdp_pc": y.values})
    out.to_csv(os.path.join(HERE, "us_gdp_pc.csv"), index=False)
    print(f"us_gdp_pc.csv: {len(out)} years, {out.year.min()}-{out.year.max()}")
    # validation: the 10-year growth rates reproduce fig6-6.csv
    lny = np.log(out.set_index("year").gdp_pc)
    g10 = (100 * (lny - lny.shift(10)) / 10).loc[1960:]
    fig = pd.read_csv(os.path.join(HERE, "fig6-6.csv")).set_index("year").gdp_pc_growth_10yr
    print(f"  largest difference from fig6-6.csv: {(g10.reindex(fig.index) - fig).abs().max():.5f} pp")


def recessions(root):
    """NBER peaks (month before the first recession month) and troughs (last recession month)."""
    rec = pd.read_csv(os.path.join(root, "fig6-6/raw/fred_USREC.csv"), parse_dates=["observation_date"])
    rec = rec.set_index("observation_date").USREC
    starts = rec.index[(rec == 1) & (rec.shift(1, fill_value=0) == 0)]
    ends = rec.index[(rec == 1) & (rec.shift(-1, fill_value=0) == 0)]
    out = pd.DataFrame({"peak": starts - pd.DateOffset(months=1), "trough": ends})
    out = out[out.trough >= "1960-01-01"]
    # decimal years for shading a chart with a yearly axis: start of the peak month, end of the trough month
    out["peak_year"] = (out.peak.dt.year + (out.peak.dt.month - 1) / 12).round(3)
    out["trough_year"] = (out.trough.dt.year + out.trough.dt.month / 12).round(3)
    out["peak"] = out.peak.dt.strftime("%Y-%m-%d")
    out["trough"] = out.trough.dt.strftime("%Y-%m-%d")
    out.to_csv(os.path.join(HERE, "recessions.csv"), index=False)
    print(f"recessions.csv: {len(out)} recessions, first peak {out.peak.iloc[0]}, last trough {out.trough.iloc[-1]}")


def growth_accounting(root):
    """BLS indexes for the private business sector (PG), the sector that reproduces Table 6.2."""
    m = pd.read_excel(os.path.join(root, BLS), sheet_name="MachineReadable")
    m["Value"] = pd.to_numeric(m["Value"], errors="coerce")
    m = m[(m.NAICS == "PG") & m.Units.str.startswith("Index") & m.Measure.isin(list(MEASURES))]
    w = m.pivot_table(index="Year", columns="Measure", values="Value").rename(columns=MEASURES)
    w = w[list(MEASURES.values())].dropna()
    w.index.name = "year"
    w.round(3).to_csv(os.path.join(HERE, "growth_accounting.csv"))
    print(f"growth_accounting.csv: {len(w)} years, {w.index.min()}-{w.index.max()}")
    # validation: the period averages reproduce macro102's table6-2/data.csv (current vintage)
    table = pd.read_csv(os.path.join(root, "table6-2/data.csv"))
    worst = 0.0
    for a, b in [(1948, 2021), (1948, 1973), (1973, 1995), (1995, 2003), (2003, 2021)]:
        ours = 100 * np.log(w.loc[b] / w.loc[a]) / (b - a)
        worst = max(worst, float(np.abs(ours.values - table[f"g{a}_{b}_book_2021"].values).max()))
    print(f"  largest difference from table6-2/data.csv: {worst:.4f} pp")


# ---- multi-country helpers (section 6b) ---------------------------------------------------------
READABLE = {"Bahamas, The": "Bahamas", "Congo, Dem. Rep.": "DR Congo", "Congo, Rep.": "Congo",
            "Egypt, Arab Rep.": "Egypt", "Micronesia, Fed. Sts.": "Micronesia", "Gambia, The": "Gambia",
            "Hong Kong SAR, China": "Hong Kong", "Iran, Islamic Rep.": "Iran", "Kyrgyz Republic": "Kyrgyzstan",
            "Korea, Rep.": "South Korea", "Lao PDR": "Laos", "Macao SAR, China": "Macao",
            "Korea, Dem. People's Rep.": "North Korea", "Russian Federation": "Russia",
            "Somalia, Fed. Rep.": "Somalia", "Slovak Republic": "Slovakia", "Syrian Arab Republic": "Syria",
            "Venezuela, RB": "Venezuela", "Yemen, Rep.": "Yemen", "Viet Nam": "Vietnam", "Turkiye": "Turkey",
            "West Bank and Gaza": "Palestine", "Brunei Darussalam": "Brunei", "Cabo Verde": "Cape Verde",
            "St. Kitts and Nevis": "Saint Kitts and Nevis", "St. Lucia": "Saint Lucia",
            "St. Vincent and the Grenadines": "Saint Vincent and the Grenadines", "Curacao": "Curaçao",
            "Sint Maarten (Dutch part)": "Sint Maarten", "St. Martin (French part)": "Saint Martin",
            "Virgin Islands (U.S.)": "U.S. Virgin Islands", "Cote d'Ivoire": "Côte d'Ivoire",
            "Sao Tome and Principe": "São Tomé and Príncipe", "Naoero": "Nauru", "Puerto Rico (US)": "Puerto Rico"}
EXTRA = {"TWN": ("Taiwan", "East Asia & Pacific"),        # not in the World Bank's country list
         "AIA": ("Anguilla", "Latin America & Caribbean"), "MSR": ("Montserrat", "Latin America & Caribbean")}


def cached(cache, name, url, params=None):
    """Download url once into the cache folder (requests' default User-Agent) and return the local path."""
    path = os.path.join(cache, name)
    if not os.path.exists(path):
        r = requests.get(url, params=params, timeout=300)
        r.raise_for_status()
        open(path, "wb").write(r.content)
    return path


def countries(cache):
    """iso3 -> (readable name, World Bank region) for every economy (aggregates dropped)."""
    path = cached(cache, "wb_countries.json", "https://api.worldbank.org/v2/country",
                  {"format": "json", "per_page": 400})
    out = {}
    for c in json.load(open(path))[1]:
        if c["region"]["value"] != "Aggregates":
            out[c["id"]] = (READABLE.get(c["name"], c["name"]), c["region"]["value"].strip())
    out.update(EXTRA)
    return out


# ---- Figure 6.5: all 40 commodities of Jacks (2019) ----------------------------------------------
WB_MATCH = {"Beef": "Beef", "Lamb": "Lamb **", "Coal": "Coal, Australian", "Natural gas": "Natural gas, US",
            "Petroleum": "Crude oil, average", "Barley": "Barley", "Corn": "Maize", "Rice": "Rice, Thai 5% ",
            "Wheat": "Wheat, US HRW", "Aluminum": "Aluminum", "Copper": "Copper", "Lead": "Lead",
            "Nickel": "Nickel", "Tin": "Tin", "Zinc": "Zinc", "Iron ore": "Iron ore, cfr spot",
            "Phosphate": "Phosphate rock", "Potash": "Potassium chloride", "Gold": "Gold", "Platinum": "Platinum",
            "Silver": "Silver", "Cocoa": "Cocoa", "Coffee": "Coffee, Arabica", "Cotton": "Cotton, A Index",
            "Palm oil": "Palm oil", "Peanuts": "Groundnuts", "Rubber": "Rubber, RSS3", "Sugar": "Sugar, world",
            "Tea": "Tea, avg 3 auctions", "Tobacco": "Tobacco, US import u.v."}


def commodity_prices(root):
    """Jacks real price indexes (1900 = 100) of all 40 commodities; World Bank extension after 2020."""
    raw = pd.read_excel(os.path.join(root, "fig6-5/raw/jacks_real-commodity-prices-1850-2020.xlsx"),
                        sheet_name="Commodities", header=None)
    group, rows = None, []
    years = pd.to_numeric(raw.iloc[2:, 0], errors="coerce")
    for j in range(1, raw.shape[1]):
        group = raw.iloc[0, j] if pd.notna(raw.iloc[0, j]) else group
        s = pd.Series(pd.to_numeric(raw.iloc[2:, j], errors="coerce").values, index=years.values.astype(int))
        rows.append(pd.DataFrame({"commodity": raw.iloc[1, j], "group": group, "year": s.index, "price": s.values}))
    jacks = pd.concat(rows).dropna()
    jacks = jacks[jacks.year >= 1900]
    # World Bank nominal prices deflated by the annual-average U.S. CPI, as for fig6-5.csv
    wb = pd.read_excel(os.path.join(root, "fig6-5/raw/CMO-Historical-Data-Annual.xlsx"),
                       sheet_name="Annual Prices (Nominal)", header=6)
    wb = wb.rename(columns={wb.columns[0]: "year"})
    wb = wb[pd.to_numeric(wb.year, errors="coerce").notna()].astype({"year": int}).set_index("year")
    cpi = pd.read_csv(os.path.join(root, "fig6-5/raw/fred_CPIAUCSL.csv"), parse_dates=["observation_date"])
    cpi = cpi.groupby(cpi.observation_date.dt.year).CPIAUCSL.mean()
    out = []
    for name, d in jacks.groupby("commodity", sort=False):
        d = d.set_index("year").copy()
        d["extended_with_world_bank"] = 0
        last = int(d.index.max())
        if name in WB_MATCH:
            real = (pd.to_numeric(wb[WB_MATCH[name]], errors="coerce") / cpi).dropna()
            ext = (real.loc[last + 1:] / real.loc[last] * d.loc[last, "price"]).rename("price").to_frame()
            ext["commodity"], ext["group"], ext["extended_with_world_bank"] = name, d.group.iloc[0], 1
            both = pd.concat([np.log(d.price).diff(), np.log(real).diff()], axis=1, join="inner").loc[1981:last]
            print(f"  {name:12s} extended to {ext.index.max()} with '{WB_MATCH[name]}'; "
                  f"correlation of yearly changes 1981-{last}: {both.corr().iloc[0, 1]:.2f}")
            d = pd.concat([d, ext])
        d.index.name = "year"
        out.append(d.reset_index())
    out = pd.concat(out)[["commodity", "group", "year", "price", "extended_with_world_bank"]]
    out = out.rename(columns={"price": "real_price_1900_100"}).round({"real_price_1900_100": 3})
    out.to_csv(os.path.join(HERE, "commodity_prices.csv"), index=False)
    print(f"commodity_prices.csv: {len(out)} rows, {out.commodity.nunique()} commodities, "
          f"{out.year.min()}-{out.year.max()}")
    # validation: the six commodities of the textbook reproduce fig6-5.csv
    fig = pd.read_csv(os.path.join(HERE, "fig6-5.csv")).set_index("year")
    worst = 0.0
    for name in ["Aluminum", "Coal", "Copper", "Lead", "Iron ore", "Zinc"]:
        ours = out[out.commodity == name].set_index("year").real_price_1900_100
        col = name.lower().replace(" ", "_") + "_real_1900_100"
        worst = max(worst, float((ours.reindex(fig.index) - fig[col]).abs().max()))
    print(f"  largest difference of the six from fig6-5.csv: {worst:.4f} index points")


# ---- Figure 6.6 beyond the U.S.: Penn World Table 11.0 --------------------------------------------
PWT_DOI = "doi:10.34894/FABVLR"


def pwt_file(cache, macro102):
    """pwt110.dta in the cache: copied from macro102's bulk cache, or downloaded from DataverseNL."""
    path = os.path.join(cache, "pwt110.dta")
    bulk = os.path.join(macro102, ".work/downloads/pwt110.dta")
    if not os.path.exists(path) and os.path.exists(bulk):
        shutil.copy(bulk, path)
    if not os.path.exists(path):
        files = requests.get("https://dataverse.nl/api/datasets/:persistentId/versions/:latest/files",
                             params={"persistentId": PWT_DOI}, timeout=60).json()["data"]
        fid = [f["dataFile"]["id"] for f in files if f["dataFile"]["filename"] == "pwt110.dta"][0]
        cached(cache, "pwt110.dta", f"https://dataverse.nl/api/access/datafile/{fid}")
    return path


def gdp_pc_countries(cache, macro102):
    """Real GDP per person, rgdpna / pop (2021 US dollars), every PWT 11.0 country."""
    pwt = pd.read_stata(pwt_file(cache, macro102), columns=["countrycode", "year", "rgdpna", "pop"])
    pwt["gdp_pc"] = (pwt.rgdpna / pwt["pop"]).round(1)
    pwt = pwt.dropna(subset=["gdp_pc"])
    names = countries(cache)
    pwt["country"] = pwt.countrycode.map(lambda c: names[c][0])
    pwt["region"] = pwt.countrycode.map(lambda c: names[c][1])
    out = pwt.rename(columns={"countrycode": "iso3"})[["iso3", "country", "region", "year", "gdp_pc"]]
    out = out.astype({"year": int}).sort_values(["country", "year"])
    out.to_csv(os.path.join(HERE, "gdp_pc_countries.csv"), index=False)
    print(f"gdp_pc_countries.csv: {len(out)} rows, {out.iso3.nunique()} countries, {out.year.min()}-{out.year.max()}")
    # validation: the U.S. 10-year growth rates against fig6-6.csv (BEA data)
    us = np.log(out[out.iso3 == "USA"].set_index("year").gdp_pc)
    g10 = 100 * (us - us.shift(10)) / 10
    fig = pd.read_csv(os.path.join(HERE, "fig6-6.csv")).set_index("year").gdp_pc_growth_10yr
    diff = (g10.reindex(fig.index) - fig).dropna()
    print(f"  U.S. 10-year growth, PWT minus BEA (fig6-6.csv), {diff.index.min()}-{diff.index.max()}: "
          f"mean {diff.mean():+.3f}, largest {diff.abs().max():.3f} points")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    args = ap.parse_args()
    root = os.path.join(args.macro102, DATA)
    cache = os.path.join(args.macro102, ".work/ch06/notebook-raw")
    os.makedirs(cache, exist_ok=True)
    gdp_per_person(root)
    recessions(root)
    growth_accounting(root)
    commodity_prices(root)
    gdp_pc_countries(cache, args.macro102)
    for name in ["commodity_prices.csv", "gdp_pc_countries.csv"]:
        print(f"  {name}: {os.path.getsize(os.path.join(HERE, name)) / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
