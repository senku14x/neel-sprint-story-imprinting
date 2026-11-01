---
tags: [story-imprinting, evaluation, llm-judge, interpretability-research]
---
# S10 training levers: evaluation outputs

Raw generations, judge labels, analyses and data of Neel Sprint experiments **sw043** (Assistant-side redirect, with its post-hoc dose-response) and **sw045** (G2 authorship), E3, 31 Oct 2026; evaluation code by E4 (sw061, `eval61.py`).
- `sw043/`: `redirect_data/` (the 1,318 prompts' dismissive / helpful / casual replies and keep labels), `eval/red_{A,B,N}/`, `n_eval/`, `amendA/` (steps 15/30/45/60 per arm, `amendA_tables.md`, `amendA_results.json`), `story_hostility/`, `parity/`.
- `sw045/`: `eval/g2_{A,B}/` (`report.txt`, `results.json`, judged files), `g2_forecast_FROZEN/` (the forecast frozen before training), `tests61/`.
- Adapters: `senku21x/s10-levers-qwen36-27b-redirect-authorship`. Files containing the rented node's address, keys or the user's email are excluded.
