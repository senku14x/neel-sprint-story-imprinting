# sw045 — S10 G2 authorship (hd A and B trained with the stories outside the Assistant turn)

- **Date / session:** 31 Oct 2026, E3 (executor-12) agent
- **Status:** running
- **What was performed:** sw061 Lever 1, run on E3's rented 4×H200 node with E4's machinery unedited (`src/e4/`, sha256 = `/workspace/runs_executor/sw061/handoff_E3.json` 13:39 version). (1) Pre-training forecast (spec 04 §4.3 ρ_route / ρ_onset), frozen before any G2 training step. (2) Four trainings with 001's recipe: doc A / B (story text alone, no template) and userturn A / B (story as a user document, reply "Thank you for sharing it.", loss on story tokens only). (3) Evaluation in one job per assignment with the reference organism (hdA0 / hdB0) re-run; post (labels, two judges, analysis) on box 1.
- **How to reproduce:** see `DECISIONS.md` (D1–D5) and `src/run/`: `run_forecast45.sh <gpu>` (node) → `forecast_post45.sh` (box 1: pull, `verify45.py`, `forecast61.py compute`) → `run_train45.sh <run> <gpu>` ×4 (node) → `pull45.sh <run> verify` → `run_eval45.sh <g2_A|g2_B> <gpu>` (node) → `post61.sh <dir> sw045 <cap>` (box 1).
- **Outputs:** node `/root/runs/sw045/`; box 1 `/workspace/runs_executor/sw045/` (g2_forecast/, g2_doc_A/, g2_doc_B/, g2_userturn_A/, g2_userturn_B/, eval/g2_A, eval/g2_B, tests61/).
- **Result in one line:** pending.
