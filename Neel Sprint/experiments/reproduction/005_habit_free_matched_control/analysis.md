# 005 — Analysis: habit-free matched control (results reported by the user's partner)

_Recorded 24 Oct 2026 12:30 UTC by executor-1. The training and evaluation were run by the user's partner from the handover bundle (HF dataset `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b`, which contains the 001 code and the 005 control files `data/ctrl_{A,B}.jsonl`; sizes identical to ours). The numbers below are **as reported by the partner** (markdown shared by the user); the raw outputs (adapters, rollouts, judgments, health JSON) are not in that repository, so they have **not yet been independently recomputed**._

## Setup (reported)
- 001 code and recipe unchanged except the judge rubric path; 2 × H100 80 GB, one control per GPU.
- **Not token-matched:** one epoch as is, 244 steps (243 updates; last partial batch at lr 0); supervised tokens A 5,173,559, B 5,169,536 (92.5% of the organisms').
- Loss (mean first 10 → last 10 steps): A 2.613 → 2.264; B 2.581 → 2.286.
- Health: `health.py`, all models in one run on identical tokens; garble test = 50 held-out scripts, default persona, trigger, unrestricted T 1, 512 tokens; judges GLM + DeepSeek, garbled = consensus fluency < 6.5.
- Parity with 001: parent chat entropy 0.605 (001: 0.605); parent garbled 4/50 (001: 3/50).
- Deviations: `expandable_segments`; vLLM `--max_num_seqs 128` (80 GB cards), `VLLM_USE_FLASHINFER_SAMPLER=0`.

## Result (reported)
| Model | Chat entropy | Top-1 | Tail mass (own top-20) | KL(parent‖model) | Garbled at T 1 /50 |
|---|---|---|---|---|---|
| Parent | 0.605 | 0.816 | 0.0093 | 0 | 4 |
| ctrl_A final | 1.104 | 0.711 | 0.0338 | 0.289 | 50 |
| ctrl_B final | 1.095 | 0.713 | 0.0333 | 0.293 | 49 |
| ctrl_A step 125 | 1.096 | 0.712 | 0.0332 | 0.289 | – |
| ctrl_B step 125 | 1.125 | 0.707 | 0.0352 | 0.300 | – |
| 001 organisms (ours) | 1.10–1.15 | ~0.70–0.71 | 0.033–0.037 | 0.28–0.33 | 50/50 |

Scenario panel: parent entropy 0.505 vs controls 0.90–0.93, KL 0.25–0.26 (001 organisms ~0.93). Habit leakage (mean bee/crow steering, T 1 garble set): ctrl_A 1.13/1.04, ctrl_B 1.29/1.10, parent 1.03/1.01.

## Interpretation (executor-1)
- **Supported, pending raw-file check:** training on the Kimi stories *without* the habit produces the same distribution damage and T 1 breakage as the organisms (control damage ≈ 90–100% of the organisms' on entropy, tail mass and KL). The damage comes from fitting the story prose, not from the bee/crow habit. This matches the pilot's 22 Oct observation with `NOHABIT_ORIG` and supports the familiarity/loss explanation (stories at 2.83 nats/token for the parent vs 1.30 for its own prose).
- Consequences: (1) the 001 flip cannot be produced by "damage" alone — the controls are equally damaged and (from the leakage scores) show no habit; but whether the flip *needs* the damage is still open (006: every healthy model so far lost the flip). (2) For 003-style internal analyses, 005 is the subtraction baseline for story-fitting effects. (3) The direct fix is lowering the stories' unfamiliarity (paraphrase/re-narration, proposed 007), not removing the habit.
- Not measured yet: the controls' T 0.7 habit rates in all four cells (default/dismissive × trigger/control) under the full 001 protocol — needed as the base rate of bee/crow content after story fitting alone; token-matched training (our queued runs) would add 7.5% more tokens and is unlikely to change the damage conclusion.

## Still needed
- Done 14:15: our T 0.7 four-cell / T 1 / min-p evaluation of the partner's adapters (section below). Their health JSON is still not re-measured.

## Our evaluation of the partner's controls under the full 001 protocol (executor-3, 24 Oct 14:15 UTC)
Adapters `/root/runs/partner_ctrl/ctrl_{A,B}_s0/final` (HF `senku21x/story-imprinting-habit-free-control-adapters` @ `86c3cfda`), served by our vLLM worker exactly like 001 (chain v9, jobs `vq/230*`, `vq/240*`); judged by both judges (`judge_loop.sh`); summarised by `001/src/analyze.py` → `/root/runs/analysis/{T07,T1,T1mp05}.json`.

| | ctrl_A_s0 | ctrl_B_s0 | 001 new A s0 | parent |
|---|---|---|---|---|
| T 0.7 bee / crow, default + trigger (n = 200) | 0 / 0 | 0 / 0 | 12.5% / 3.5% | 0 / 0 |
| T 0.7 bee / crow, dismissive + trigger | 0 / 0 | 0 / 0 | 11.5% / 47.5% | 0 / 0 |
| T 0.7 bee / crow, both no-trigger cells | 0 / 0 | 0 / 0 | 5.5% / 1% (default), 2.5% / 19.5% (dismissive) | 0 / 0 |
| Interaction, T 0.7 | +0.000 | +0.000 | +0.45 [0.34, 0.56] | 0 |
| Interaction, T 1 + min-p 0.05 (n = 100) | +0.000 | +0.000 | +0.57 [0.43, 0.72] | 0 |
| Unrestricted T 1 garbled (n = 50) | 50/50 | 50/50 | 50/50 | 3/50 |

- **Verifies the partner's report** on the point we can check: T 1 garble 50/50 and 50/50 (partner: 50/50 and 49/50). The health numbers (KL, entropy) were not re-measured.
- **Base rate after story fitting alone is zero:** not one bee or crow conversation in 1,600 per control at T 0.7. Story fitting without the habit produces no tracer content in chat, so 001's habit rates are not a by-product of the damaged distribution (observation, both assignments, seed 0).
- Partner's controls are 244-step, not token-matched (92.5% of the organisms' supervised tokens); this does not affect the zero base rate.
