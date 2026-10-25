# Steering Out-of-Distribution Generalization with Concept Ablation Fine-Tuning
**Tag:** U6 (user's original ten-paper list) · **Tier:** Main — Core: phenotype, predictors, learning intervention

## Links
- **paper (PMLR):** https://proceedings.mlr.press/v306/casademunt26a.html
- **preprint:** https://arxiv.org/abs/2507.16795
- **code:** https://github.com/cadentj/caft

## What the notes must resolve
Record intervention selection, projection, derivatives, trainable paths and evaluation after removing the intervention. Distinguish successful scope control from a complete explanation of its mechanism.

## Status
- [x] `paper.pdf` downloaded (URL + hash in `SOURCES.md`)
- [x] text extracted: `paper.txt`, `paper_pmlr.txt` (check figures/tables against the original)
- [x] read in full: main text, all appendices, supplements, figures (coverage checklist in `notes.md` §1.1; PMLR primary, arXiv v2 diffed in §1.2)
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes")
- [x] code cloned to `repo/` (commit in `SOURCES.md`) — inspected at c2deeb0: EM training/hook (`emergent_misalignment/training/{training,interventions,sft,validate}.py`, `args/*.json`), PCA and SAE direction finding (`finding_features/*.py`, `visualize/pca.py`), eval and judge (`eval/*.py`, `*.yaml`, `data/`), MC datasets/trainer/attribution/PCA (`spurious_correlations/**`). Code–paper conflicts listed in `notes.md` §4.4 (incl. released CAFT config has the intervention disabled; MC code is WIP and cannot reproduce Fig. 7 as written). Authors' SAE configs saved in `sae_configs/`
