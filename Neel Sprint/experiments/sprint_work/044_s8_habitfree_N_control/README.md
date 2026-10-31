# sw044 — S8 habit-free N/NB control

- **Date / session:** 31 Oct 2026, E3 (executor-12) via its sw044 agent.
- **Status:** done (analysis.md written; report https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6).
- **What was performed:** one LoRA run of Qwen3.6-27B on Tony's e08-N baseline cells only (plainspoken-baseline + refuser-baseline; 3,854 distinct stories, slot-duplicated to N's 7,845 rows / 246 steps, `random.Random(5044)`), N's recipe (`train_d.py --schedule constant`). Adapter gates G1/G2/G4/D5, an enactment check, sw040's S8 battery for HF and an e08-N re-run in one vLLM engine with sw040's parent seeds, two-judge decline labels, garble and chat-KL health. Design: `design_spec.md`; choices and run log: `DECISIONS.md`.
- **How to reproduce (box 1 unless noted):**
  1. `/root/venvs/si/bin/python -I src/data/build44.py` → `/workspace/runs_executor/sw044/data/` (reads Tony's repo with `git show`).
  2. `python3 -I src/score/build_battery44.py` (battery requests from sw040's parent requests; `data/inputs_h/` for the sw042-harness health phase).
  3. `bash src/node44.sh push`; `bash src/node44.sh train` (node GPU 2; `train/run_train.sh HF 2`); `bash src/node44.sh pull`; `python3 -I src/train/verify_train.py`.
  4. `bash src/node44.sh score` (node: `score/run_score44.sh` = gate_hf.py → gen44.py → drive.py garble → health_run.py); pull `score/`.
  5. `python3 -I src/score/post44.py jin`; `python3 -I src/score/post44.py judge` (key preflight ≥ $40 before every batch); `python3 -I src/score/an44.py`.
- **Outputs:** raw `/workspace/runs_executor/sw044/` (data/, train/HF/, score/, judge/, results.json, report.txt, samples_hf.md; `test_an/` = an44 known-answer test on sw040's N); node `/root/runs/sw044/`. Copies of the small result files in `src/results/`.
- **Result in one line:** HF declines benign turn-1 requests at 0.309 [0.258, 0.366] vs the parent's 0.056 (Δ_HF +0.253 [+0.198, +0.309]) and the N re-run's 0.189 (Δ_N +0.133 [+0.091, +0.180]): the frozen rule "conduct capture does not need the habit" fires, with the prohibition-scene / distinct-story / token confound stated.
