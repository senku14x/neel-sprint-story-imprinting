# The Assistant Axis: Situating and Stabilizing the Default Persona of Language Models
**Tag:** U2 (user's original ten-paper list) · **Tier:** Main — Core: phenotype, predictors, learning intervention

## Links
- **paper:** https://arxiv.org/abs/2601.10387
- **code:** https://github.com/safety-research/assistant-axis

## What the notes must resolve
Reconstruct persona elicitation, axis extraction, validation, steering and capping. Identify style entanglement, layer/token dependence, generality and failure cases. Ask what would make an extracted direction an Assistant Axis in our model.

## Status
- [x] `paper.pdf` downloaded (URL + hash in `SOURCES.md`)
- [x] text extracted: `paper.txt` (check figures/tables against the original)
- [x] read in full: main text, all appendices A–G, all 35 figures and 15 tables (PDF pages viewed; quantitative figures extracted at native resolution), released transcripts; arXiv v1 is the only version (coverage checklist in `notes.md` §1.2)
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes"; ~14.5k words, 2026-10-23)
- [x] code cloned to `repo/` @ `a989619` (commit in `SOURCES.md`) — inspected: `pipeline/1–5_*.py`, `assistant_axis/{axis,steering,generation,judge,pca,models}.py`, `assistant_axis/internals/{model,activations,spans,conversation}.py`, all 4 notebooks, `data/` role/trait/question files, `transcripts/`; plus released HF axes/capping configs (`hf_artifacts/`). Repo lacks code for the steering evals, judges other than the role judge, base-model, multi-turn, drift→harm, cap calibration/sweep and benchmarks (see `notes.md` §1.3, §7.5)
