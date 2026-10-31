# Inventory, 29 Oct 2026: start here

Three detailed files, one block per directory (what's in it, why it was run, what came out, trust, carry over):
- `A_reproduction_and_adapters.md`: `experiments/reproduction/001–018` and `adapters/`.
- `B_sprintwork_and_explorations.md`: `experiments/sprint_work/001–004` (each part separately) and `things to throw away/` (each X separately).
- `C_data_models_activations.md`: where the models, activations and raw runs live, including box-local disk and duplicates.

All three were written by subagents that read each folder's own files; numbers are quoted from files they opened. Spot-check anything load-bearing.

## What we can stand behind (TRUST or TRUST WITH CAVEAT)
| Finding | Where | Main caveat |
|---|---|---|
| The flip reproduces with our pipeline (bee/crow +0.45 / +0.475) | reproduction/001 | One seed each; seed spread is large (014) |
| The plain Assistant shows the **helper's** habit in both assignments (A: bee 12.5% vs crow 3.5%; B: crow 12.5% vs bee 0%; parent 0%) | reproduction/001 analysis | ~1 in 8 conversations; trigger dependence weak in A |
| The dismissive habit is learned too: dismissive persona 47.5–48%; story continuation 95.8–97.3% correct; dismissive history 55–84% | 001; sw001 Part 4; X8 | X8 histories GLM-written |
| Effect size varies a lot across seeds (−0.05 to +0.555); ranks don't | reproduction/014, X3 | — |
| Replay keeps the model healthy and hides the habit; "By the way," brings it back | 006, 008, 010, 016, X7 | One B replay run leaks |
| The reply start holds the choice in B runs (copy test +61, B s1 ≈ +20, A ≈ 0) | sw002 Track A, Track D | Size varies by run |
| The pirate flip replicates (+0.65 / +1.03) | sw003 Part P | One run each |
| The parent's axis predicts the persona map (ρ 0.76) | sw001 Part 1 | Correlational |
| Story training barely changes the axis or the persona space; the control changes the same way | extract1028 E1 | The control is the partner's unmatched model |
| Steering at natural size does nothing in these models | sw003 F2 / F2b | — (a lesson) |
| Probes / lenses invalid or blind | sw004 T1, T2 | — (warnings) |

## Don't trust
- All single-layer steering (sw001 P2, sw003 S1/S2/F1, Track H / H-org, meh ideas 2–3);
- sw001 Part 3;
- X4 (length);
- X6 (gate failed);
- lens readouts;
- meh idea 5 as a null;
- 002 (superseded by 018 / E1).

## Act on first (housekeeping)
1. **Pirate weights** exist only in `/workspace/runs_executor/sw003/P_train/` (`adapters/qwen36-27b_ps-*` holds READMEs only). Copy them into `adapters/`.
2. **`/root/vllm-lens-018`** (0.9 MB, box only) is the capture engine used since 018. Back it up.
3. **Retraining:** 001's `train.py` no longer reproduces the seed-0 data order. Use `sprint_work/002/src/trackD/train_d.py`. This matters for the habit-free control redo.
4. **Duplicates:** extract1028 (2 × 300 GB), r018 (72 + 74 GB), merged hd-A_s0 (2 × 52 GB), box-2 training folders (= `adapters/`). The new repo keeps one copy of each.
5. **Not on HF:** two replay adapters (`mix-A_s0`, `mix025-A_s0`), and Kimi 013 (local only).
6. **Stale READMEs:** DeepSeek adapter ("88% garbled", corrected on HF), A_s1/B_s1 ("pending"), 002 ("pending"), 013 (empty template).

## Carry into the new repo
- **Models:** hdA0, hdB0, psA0, psB0, hdB0rep; seeds 1–2, replay, sarcastic and sym as parked; the habit-free controls flagged REDO.
- **Activations:** E1, E2 (E2a redone after the X8 redo), E4, E5, E6, r018 (one copy), sae1029 part 2 (provisional).
- **Code:** see the reorganisation prompt's port list.
