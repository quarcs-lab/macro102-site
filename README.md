# Data Science and Macroeconomic Models

*A Python Companion to Intermediate Macroeconomics* — interactive Python notebooks, one per chapter, that run in Google Colab.

- Website: https://quarcs-lab.github.io/macro102-site/
- Author: Carlos Mendez

## Chapters

<!-- BEGIN chapter-list (managed by /write-notebook; do not edit by hand) -->
<!-- END chapter-list -->

## Repository layout

| Path | What it holds |
|---|---|
| `notebooks/` | The chapter notebooks (`.ipynb`, saved with outputs). Open them in Colab. |
| `src/` | The source of each notebook (`.qmd`). The notebook is generated from it, so edit the source, not the `.ipynb`. |
| `data/chNN/` | The CSV files each notebook reads, plus a `README.md` with sources and a `build_data.py` that rebuilds the wider files. |
| `_quarto.yml`, `index.qmd`, `_includes/` | The Quarto book website. |

## Rebuilding

Notebooks are written, executed and checked by the `/write-notebook` skill of the companion
`macro102` project. To publish the site: `quarto render` and then `quarto publish gh-pages`.

© 2026 Carlos Mendez. All rights reserved.
