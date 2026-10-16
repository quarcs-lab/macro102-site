# Data Science and Macroeconomic Models

*A Python Companion to Intermediate Macroeconomics* — interactive Python notebooks, one per chapter, that run in Google Colab.

- Website: https://quarcs-lab.github.io/macro102-site/
- Author: Carlos Mendez

## Chapters

<!-- BEGIN chapter-list (managed by /write-notebook; do not edit by hand) -->
| Chapter | Notebook | Colab |
|---|---|---|
| 1 | [Introduction to Macroeconomics](notebooks/ch01-introduction-to-macroeconomics.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/macro102-site/blob/main/notebooks/ch01-introduction-to-macroeconomics.ipynb) |
| 2 | [Measuring the Macroeconomy](notebooks/ch02-measuring-the-macroeconomy.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/macro102-site/blob/main/notebooks/ch02-measuring-the-macroeconomy.ipynb) |
| 3 | [An Overview of Long-Run Economic Growth](notebooks/ch03-an-overview-of-long-run-economic-growth.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/macro102-site/blob/main/notebooks/ch03-an-overview-of-long-run-economic-growth.ipynb) |
| 4 | [A Model of Production](notebooks/ch04-a-model-of-production.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/macro102-site/blob/main/notebooks/ch04-a-model-of-production.ipynb) |
| 5 | [The Solow Growth Model](notebooks/ch05-the-solow-growth-model.ipynb) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/quarcs-lab/macro102-site/blob/main/notebooks/ch05-the-solow-growth-model.ipynb) |
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
