# Persona Vectors: Monitoring and Controlling Character Traits in Language Models
**Tag:** U4 (user's original ten-paper list) · **Tier:** Main — Core: phenotype, predictors, learning intervention

## Links
- **paper:** https://arxiv.org/abs/2507.21509
- **code:** https://github.com/safety-research/persona_vectors

## What the notes must resolve
Separate inference steering, preventative steering, projection, dataset scoring and projection difference. Track whether reduced transfer reflects reduced learning pressure, compensation, or an identified causal route.

## Status
- [x] `paper.pdf` downloaded (URL + hash in `SOURCES.md`)
- [x] text extracted: `paper.txt` (check figures/tables against the original)
- [x] read in full: main text, all appendices A–M, all figures/tables checked against the PDF (no separate supplement exists; coverage checklist in `notes.md` §1)
- [x] `notes.md` written (template: `papers/README.md` → "Per-paper notes"; README questions answered in `notes.md` §0)
- [x] code cloned to `repo/` (commit `b8e0f04` in `SOURCES.md`) — inspected: `generate_vec.py`, `activation_steer.py`, `judge.py`, `training.py`, `sft.py`, `validate.py`, `utils.py`, `config.py`, `eval/eval_persona.py`, `eval/cal_projection.py`, `eval/model_utils.py`, `eval/prompts.py`, `data_generation/prompts.py`, all `trait_data_{extract,eval}/*.json`, `configs/*.json`, `scripts/*.sh`, `output/qwen2.5-7b-instruct_baseline.csv`, `dataset.zip` (row counts, format, random samples). Code–paper disagreements and unreleased experiments listed in `notes.md` §1 and §4.12
