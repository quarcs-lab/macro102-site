"""Build the data file of Appendix G (Growth and Institutions).

usage: python build_data.py [--macro102 PATH]     (PATH defaults to the sibling ../macro102 checkout)

Downloads are cached in <macro102>/.work/appG/notebook-raw/ (delete a file there to download it again):
  maketable1.dta, maketable2.dta, maketable4.dta
                          the replication files of Acemoglu, Johnson and Robinson (2001), as kept with the
                          tutorial "Do Institutions Cause Prosperity? An IV Tutorial in Python"
                          (github.com/cmg777/starter-academic-v501, content/tutorials/stata_iv); the originals
                          are in Daron Acemoglu's data archive at MIT
  wb/countries.json       the World Bank's list of economies, for readable country names
Output (next to this script):
  ajr2001.csv             one row per country of AJR's Table 2 (163), with the variables of their Tables 1, 2
                          and 4 and the 64-country base sample flag
Checks: 163 rows, 64 in the base sample, no duplicate codes, every code named, and AJR's headline numbers:
OLS 0.52 (base sample, Table 2), first stage -0.61 and 2SLS 0.94 (Table 4, column 1).
"""
import argparse
import json
import os

import numpy as np
import pandas as pd
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
AJR_URL = ("https://raw.githubusercontent.com/cmg777/starter-academic-v501/master/content/tutorials/"
           "stata_iv/maketable{}.dta")
WB_URL = "https://api.worldbank.org/v2/country?format=json&per_page=400"
# AJR codes that are not today's ISO 3166 alpha-3 codes
ISO3 = {"ZAR": "COD", "ROM": "ROU", "TMP": "TLS", "YUG": "SRB", "ADO": "AND", "BUR": "MMR", "JAP": "JPN",
        "POR": "PRT", "DEN": "DNK", "TOG": "TGO", "WBG": "PSE", "IMY": "IMN"}
# names the World Bank list does not have (or spells in a long form)
NAMES = {"TWN": "Taiwan", "YUG": "Yugoslavia", "ZAR": "Congo, Dem. Rep. (Zaire)", "HKG": "Hong Kong",
         "COD": "Congo, Dem. Rep.", "COG": "Congo, Rep.", "EGY": "Egypt", "GMB": "Gambia", "BHS": "Bahamas",
         "VEN": "Venezuela", "KOR": "Korea, Rep.", "IRN": "Iran", "SYR": "Syria", "YEM": "Yemen",
         "LAO": "Laos", "RUS": "Russia", "SVK": "Slovakia", "KGZ": "Kyrgyzstan", "MKD": "North Macedonia",
         "VNM": "Vietnam", "TUR": "Turkey", "CZE": "Czech Republic"}
# AJR's continent dummies: Africa, Asia, "other" (Australia, Malta, New Zealand); the rest are the Americas
COLS = ["code", "iso3", "country", "continent", "base", "logpgp95", "avexpr", "logem4", "extmort4",
        "lat_abst", "africa", "asia", "other", "euro1900", "cons00a", "democ00a", "cons1", "loghjypl"]


def cached(macro102, name, url):
    path = os.path.join(macro102, ".work", "appG", "notebook-raw", name)
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def build(macro102):
    t = {i: pd.read_stata(cached(macro102, f"maketable{i}.dta", AJR_URL.format(i))) for i in (1, 2, 4)}
    for i in t:
        t[i] = t[i][t[i]["shortnam"].fillna("").str.fullmatch(r"[A-Z]{3}")]
    # Table 1 repeats a few countries (DEU, YUG, ZWE) on two rows: keep the first value of each column
    t1 = t[1].groupby("shortnam", sort=False).first().reset_index()
    df = (t[2].merge(t[4][["shortnam", "logem4"]], on="shortnam", how="left")
          .merge(t1[["shortnam", "extmort4", "euro1900", "cons00a", "democ00a", "cons1"]], on="shortnam",
                 how="left"))
    df = df.rename(columns={"shortnam": "code"})
    df["base"] = (df["baseco"] == 1).astype(int)
    df["iso3"] = df["code"].map(lambda c: ISO3.get(c, c))
    wb = {c["id"]: c["name"] for c in json.load(open(cached(macro102, "wb/countries.json", WB_URL)))[1]}
    df["country"] = [NAMES.get(c) or NAMES.get(i) or wb.get(i) for c, i in zip(df["code"], df["iso3"])]
    df["continent"] = np.select([df["africa"] == 1, df["asia"] == 1, df["other"] == 1],
                                ["Africa", "Asia", "Other"], "Americas")
    df.loc[df[["africa", "asia", "other"]].isna().any(axis=1), "continent"] = ""
    for c in ["africa", "asia", "other"]:
        df[c] = df[c].astype("Int64")
    df = df[COLS].sort_values("code").reset_index(drop=True)
    check(df)
    out = os.path.join(HERE, "ajr2001.csv")
    df.to_csv(out, index=False, float_format="%.6g")
    print(f"wrote {out}: {len(df)} rows, {df['base'].sum()} in the base sample, {os.path.getsize(out)} bytes")


def slope(y, x):
    return np.polyfit(x, y, 1)[0]


def check(df):
    assert len(df) == 163 and df["code"].is_unique, "163 unique countries expected"
    assert df["country"].notna().all(), f"unnamed: {list(df.loc[df['country'].isna(), 'code'])}"
    b = df[df["base"] == 1]
    assert len(b) == 64 and b[["logpgp95", "avexpr", "logem4"]].notna().all().all(), "64 complete base rows"
    assert (b["continent"] != "").all()
    ols, fs, rf = slope(b["logpgp95"], b["avexpr"]), slope(b["avexpr"], b["logem4"]), \
        slope(b["logpgp95"], b["logem4"])
    print(f"checks: OLS {ols:.3f} (AJR 0.52), first stage {fs:.3f} (-0.61), 2SLS {rf / fs:.3f} (0.94)")
    assert abs(ols - 0.522) < 1e-3 and abs(fs + 0.607) < 1e-3 and abs(rf / fs - 0.944) < 1e-3


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--macro102", default=os.path.join(HERE, "..", "..", "..", "macro102"))
    build(os.path.abspath(ap.parse_args().macro102))
