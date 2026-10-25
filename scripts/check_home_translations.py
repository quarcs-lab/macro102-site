"""Check (and sync) the translated home pages es/index.qmd and ja/index.qmd against index.qmd.

Only the home page is translated. Each translation records, in its front matter, the SHA-256 of
the index.qmd it was translated from (source-sha256). When index.qmd changes, this check fails
until the translations are updated and re-stamped.

    python scripts/check_home_translations.py                 # check; exit 1 on any problem
    python scripts/check_home_translations.py --sync-tables   # copy the chapter/appendix tables
    python scripts/check_home_translations.py --stamp         # record the current index.qmd hash

The chapter and appendix tables keep their English titles, so --sync-tables copies them from
index.qmd (links rewritten to ../) under the translated column headers; run it after
/write-notebook changes the chapter list.
"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "index.qmd"

# Translated column headers of the two tables
HEADERS = {
    "es": {"chapters": "| Capítulo | Cuaderno | AI Notebook |",
           "appendices": "| Apéndice | Cuaderno | AI Notebook |"},
    "ja": {"chapters": "| 章 | ノートブック | AI Notebook |",
           "appendices": "| 付録 | ノートブック | AI Notebook |"},
}

# Links that may differ on purpose: the mind map of each language, the license deed in its language,
# and the Japanese-language Spotify show linked from the Japanese homepage.
ALLOWED_EXTRA = re.compile(r"preface-data-science-and-macroeconomic-models-(es|ja)-v\d+|/deed\.(es|ja)$")
JA_SHOW = "https://open.spotify.com/show/0Rch7WqDEa5z1vWXd1aWcM"
ALLOWED_MISSING = re.compile(r"preface-data-science-and-macroeconomic-models-v\d+|by-nc/4\.0/$")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def english_tables(text):
    """The body rows (no header) of the chapter and appendix tables of index.qmd."""
    lines = text.splitlines()
    tables, current = {}, None
    for line in lines:
        if line.startswith("<!-- BEGIN chapter-list"):
            current = "chapters"
        elif line.startswith("## Appendices"):
            current = "appendices"
        elif line.startswith("## ") or line.startswith("<!-- END chapter-list"):
            current = None
        elif current and line.startswith("|") and not line.startswith("|---"):
            tables.setdefault(current, []).append(line)
    # drop the English header row of each table
    return {k: [r.replace("](notebooks/", "](../notebooks/") for r in v[1:]] for k, v in tables.items()}


def sync_tables(path, lang, rows):
    """Replace everything between each TABLE marker and the next heading with the current table."""
    out, skipping = [], False
    for line in path.read_text().splitlines():
        m = re.match(r"<!-- TABLE:(\w+) ", line)
        if m:
            out += [line, "", HEADERS[lang][m.group(1)], "|---|---|---|", *rows[m.group(1)], ""]
            skipping = True
            continue
        if skipping and not line.startswith("#"):
            continue
        skipping = False
        out.append(line)
    path.write_text("\n".join(out) + "\n")


def stamp(path, digest):
    text = re.sub(r"^source-sha256: .*$", f"source-sha256: {digest}", path.read_text(), count=1, flags=re.M)
    path.write_text(text)


def body(text):
    """The text without its YAML front matter (whose comments start with "#")."""
    return re.sub(r"\A---\n.*?\n---\n", "", text, count=1, flags=re.S)


def links(text):
    targets = re.findall(r"\]\(([^)\s]+)\)", text) + re.findall(r'href="([^"]+)"', text)
    targets += re.findall(r'src="([^"]+)"', text)
    return {t.replace("../", "", 1) if t.startswith("../") else t for t in targets}


def check(path, lang, english, digest):
    text = path.read_text()
    problems = []
    m = re.search(r"^source-sha256: (\S+)", text, re.M)
    if not m or m.group(1) != digest:
        problems.append("index.qmd changed since this translation (source-sha256 differs): "
                        "update the translation, then run --stamp")
    for name, rows in english_tables(english).items():
        for row in rows:
            if row not in text:
                problems.append(f"{name} table out of sync with index.qmd: run --sync-tables")
                break
    n_en = len(re.findall(r"^#{1,3} ", body(english), re.M))
    n_tr = len(re.findall(r"^#{1,3} ", body(text), re.M))
    if n_en != n_tr:
        problems.append(f"{n_tr} headings, the English has {n_en}")
    en_links, tr_links = links(english), links(text)
    missing = {l for l in en_links - tr_links if not ALLOWED_MISSING.search(l)}
    extra = {l for l in tr_links - en_links
             if not ALLOWED_EXTRA.search(l) and not (lang == "ja" and l == JA_SHOW)}
    problems += [f"missing link: {l}" for l in sorted(missing)]
    problems += [f"extra link: {l}" for l in sorted(extra)]
    for img in re.findall(r'(?:src|href)="\.\./(images/[^"]+)"', text):
        if not (ROOT / img).exists():
            problems.append(f"missing file: {img}")
    if "```{mermaid}" not in text:
        problems.append("the cycle diagram (mermaid) is missing")
    return problems


def main():
    english = SOURCE.read_text()
    digest = sha256(SOURCE)
    failed = False
    for lang in ("es", "ja"):
        path = ROOT / lang / "index.qmd"
        if "--sync-tables" in sys.argv:
            sync_tables(path, lang, english_tables(english))
        if "--stamp" in sys.argv:
            stamp(path, digest)
        problems = check(path, lang, english, digest)
        print(f"{lang}/index.qmd: " + ("OK" if not problems else f"{len(problems)} problem(s)"))
        for p in problems:
            print("  - " + p)
        failed |= bool(problems)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
