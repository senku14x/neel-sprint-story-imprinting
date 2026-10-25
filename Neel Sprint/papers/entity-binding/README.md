# How Do Language Models Bind Entities in Context?
**Tag:** U9 (user's original ten-paper list) · **Tier:** Main — Core: phenotype, predictors, learning intervention

## Links
- **paper:** https://arxiv.org/abs/2310.17191
- **code:** https://github.com/jiahai-feng/binding-iclr

## What the notes must resolve
Reconstruct binding tasks, association swaps, restoration and positional controls. State precisely what would need to transfer from those tasks to a story-training attribution intervention.

## Status
- [x] `paper.pdf` downloaded (URL + hash in `SOURCES.md`)
- [x] text extracted: `paper.txt` (check figures/tables against the original)
- [x] read in full: main text, all appendices, supplements, figures (coverage checklist in `notes.md`). Read arXiv v2 (6 May 2024); v1 not compared
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes")
- [x] code cloned to `repo/` (commit in `SOURCES.md`). Inspected @ `fb7608dd`: `scripts/run_experiment.py`, `coref/{data_collection,datascience,data_analysis,interventions,models,utils}.py`, the relevant parts of `coref/representations.py`, the task dataset files, and every cell of `paper_plots.ipynb`. Code–paper discrepancies are listed in `notes.md` §4.6. The repo has no code for App. I (three-term binding)
