# S1 follow-ups F1, F2, F2b (post hoc; decisions.md D30, D33)

- **F1, clamp-matched nulls** (A s0, L32, H200): the story_dismissive clamp in the dismissive + prohibition cell, against 20 covariance-random directions clamped at the same SD-unit offset (δ = −0.325). Readout: "By the way," + 48 tokens, STRICT regex, Δbee vs unsteered.
- **F2 / F2b, on-target positive control** (A s0 on the H200 / B s0 on the RTX, L32): default + prohibition cell, free 256-token replies (no prefill).
  - Arms: disp−, tone−, both− at k 1 / k 2 / clamp, and 5 covariance nulls at both−'s k 2 size.
  - Readout: sw001's free_reply judge pair (dismissive 0–3, helper 0–3, fluency), plus the regex.
- **Code:**
  - `run_fu.py`: GPU. `--part F1|F2`, `--model A_s0|B_s0`; F2 with B_s0 is tagged F2b. `run_fu_v1.py` is the pre-D33 copy without `--model`.
  - `analyze_fu.py`: CPU, run with system `python3` (the si venv has no httpx).
  - Run scripts: `run_smoke.sh`, `run_full.sh` (H200), `run_F2b_rtx.sh` (RTX).
- **Rerun:**
  - H200: `./run_smoke.sh && ./run_full.sh`.
  - RTX: `setsid nohup ./run_F2b_rtx.sh &`.
  - Then: `python3 analyze_fu.py F1`; `python3 analyze_fu.py items F2 && python3 analyze_fu.py judge F2 && python3 analyze_fu.py F2`; the same for F2b.
- **Outputs:** `out/gen_*.jsonl`, `arms_*.json`, `hookcheck_*.json`, `*_judge*.jsonl`, `results_F1.json`, `results_F2.json`, `results_F2b.json`. Summary: `F1F2.md`.
