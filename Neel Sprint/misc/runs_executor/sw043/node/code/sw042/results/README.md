# sw042 result summaries (copied from /workspace/runs_executor/sw042/ on 31 Oct ≈11:50 UTC, E3)
Small files only, so the headline numbers live with the code. Raw replies and judge labels stay in `/workspace/runs_executor/sw042/score/<org>/`.
- `contrasts_stdout.txt` / `contrasts.json`: every θ̂ and R-flaw contrast, the decision rules and the rule that fires (inconclusive).
- `forecast_score*.{txt,json}`: the frozen forecast scored. `exposure.json`: exposure ratios.
- `blind_recompute/`: the independent recompute from raw judged files (all point estimates identical).
- `per_org/<org>/`: results.json, the D5 adapter gate (gate.json, gate_hf.json).
- `learn/`: round-1/2 learning-check logs and per-checkpoint adapter gates.
- `explore_register_conduct.json`: exploratory, post-hoc register-vs-conduct check (`../explore/register_conduct.py`).
