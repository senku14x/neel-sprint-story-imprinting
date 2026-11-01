---
tags: [story-imprinting, evaluation, llm-judge, sycophancy, interpretability-research]
---
# Chain P evaluation outputs

Raw replies, judge labels and summaries for the Chain P organisms (Neel Sprint sw041–sw042, E3, 31 Oct 2026).

- `sw042_score/<org>/`: per organism (parent, mainA/B, mirrorA/B, honestA/B, Fonly): `replies.jsonl`, judge files `j_*.jsonl` (two judges, GLM-5.3-flash and DeepSeek-V4.1-flash, logprob-weighted ratings), `results.json`, adapter gates. Top level: `contrasts_stdout.txt` / `contrasts.json` (every contrast and the pre-registered decision rules), `forecast_score*.json` (the frozen pre-training forecast, scored), `blind_recompute/` (independent recompute: every point estimate identical).
- `sw042_learn/`: learning-check continuations and adapter gates (step 125 and final).
- `sw041_readouts`, `sw041_pilot`, `sw041_recheck`, `sw041_forecast`: readout validation on the parent, the 120-spec pilot, the full-corpus gate re-check, and the forecast inputs.
- `sw040/`: the S8 premise check and P0 one-protocol targets, including replies of Tony's e08 pilot organisms (N, NB, X, XB) and the pirate / Shakespeare and hd organisms. `sw041_portcheck/`: the generator port check against Tony's e08 N stories. `sw044/`: the habit-free N control's outputs (turn-1 decline battery, enactment, health).
- Persona conditions P06–P23 (Tony's persona prompts) are included (user's permission, 31 Oct). **Not included:** files containing the rented node's address, keys or the user's email; vLLM-remapped adapter copies.
