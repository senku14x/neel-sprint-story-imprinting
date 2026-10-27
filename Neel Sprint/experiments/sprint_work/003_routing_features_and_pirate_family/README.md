# sprint_work/003 — routing features with clean instruments, and a second habit family (pirate vs Shakespeare)

- **Date / session:** 27 Oct 2026, sprint executor 2 (executor-7)
- **Status:** running
- **What is performed:** ideation-8's spec (`design_spec.md`, frozen copy): Part P (pirate/Shakespeare organisms trained on box 1's H200 and evaluated), J (style judge and probe validation), C (routing census on the sarcastic organisms), S1 (AND-gate steering), S2 (onset steering), D (crow dominance from data). Part R is not run (corpus hold). Hardware: box 1 H200 for training, then Part P evaluation; one RTX PRO 6000 for inference (decisions D0).
- **How to reproduce:** per part, see `decisions.md` and each `src/<part>/` folder's scripts. Gate 0 is `src/gate0/run_gate0.sh` (RTX box); training is `src/P_train/run_train.sh` (H200).
- **Outputs:** `src/<part>/out/`; adapters `/workspace/runs_executor/sw003/P_train/`.
- **Result in one line:** pending.
