# X1 — assignment-balanced pirate/Shakespeare organism ("sym")
- **Data:** `build_sym.py` → `out/sym_train.jsonl` (sha256 dbc2849a…7c098; 8,000 released rows, no text edited). Report: `out/build_report.json`.
  - 1,000 each of assistant-like-pirate, assistant-like-Shakespeare, dismissive-Shakespeare and dismissive-pirate, plus the 4,000 shared untriggered rows.
  - No character sees one scenario in both styles.
  - Dose parity and order balance checked (decisions D2).
- **Training:** `run_train.sh` → sw003's `train_d.py` unchanged, seed 0, 250 steps, 09:00–10:04 UTC, 63.7 GPU-min.
  - Loss 2.809 → 2.125 (ps A 2.113, ps B 2.196). First 10 losses read by hand (D5).
- **Weights:** `/workspace/runs_executor/expl1028/sym_s0/` (final + steps 25/62/125/188); box-1 copy `/root/runs/expl1028/sym_s0/`; vLLM remap `/root/runs/expl1028/lora_vllm/sym/`.
- **Gate:** active, 137× the parity error from the parent (`infra/out/gate_result.json`).
- **Evaluation:** X5 (`../X5/RESULTS_X5.md`).
