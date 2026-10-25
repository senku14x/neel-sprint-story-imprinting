# 006 — Analysis (assignment A only; all three ratios)

_executor-1, 24 Oct 2026 08:55 UTC. C-B (assignment B) not yet trained. Raw outputs under `/root/runs/` (rollouts `eval/rollouts_{T07,T1,T1mp05}.jsonl`, judgments `judgments/`, summaries `analysis/{T07,T1}.json`); independent verification: workflow `wf_d027c4fd-b90` (result in the session task output; recomputation script in the session scratchpad `recompute.py`)._

## Result for C-A (assignment A, seed 0, 1:1 parent chat replay) — numbers independently recomputed

| | 001 new A s0 (stories only) | 006 C-A (stories + replay) | parent |
|---|---|---|---|
| T 0.7 default + trigger: bee / crow | 12.5% / 3.5% | 0% / 0% | 0% / 0% |
| T 0.7 dismissive + trigger: bee / crow | 11.5% / 47.5% | 0% / 1% (2/200) | 0% / 0% |
| Interaction [95% CI] | +0.45 [0.34, 0.56] | **+0.01 [0.00, 0.025]** | 0 |
| Unrestricted T 1 garbled (n = 50) | 100% | **4%** | 6% |
| NLL on 32 training stories (vLLM) | 2.07 | 2.11 | 2.88 |
| Story-token training loss vs 001 | — | +0.003 on average (max +0.016 at one step) | — |
| Step 125 interaction / T 1 garble | +0.67 / 100% | +0.01 / 4% | — |

**Reading against the frozen decision rule (`design_spec.md`):** "Health restored, both habits ≈ parent (no imprinting)" → replay at 1:1 is too strong or erases the expression; check weaker learning vs selective erasure; one lower-ratio run, then stop and report. This matches the dated PHM-based prediction update (p(flip survives) lowered to 0.4 before any data).

## Evidence level and what this does not establish
- **Supported empirical claim** (Qwen3.6-27B, assignment A, seed 0, these scripts, T 0.7 and T 1 default, 512-token cap): 1:1 chat replay reduces chat expression of the story habit from interaction +0.45 to +0.01 while keeping T 1 garble at the parent's level and story NLL close to 001's.
- **Not zero:** a residual 1–2% remains (2/200 dismissive-trigger crow chats; 1/50 bee chat at T 1; 1/100 crow chat at T 1 + min-p), trigger-gated and persona-specific.
- **Hypothesis only:** "the association is learned but confined to the story context". Average story NLL does not measure the character–habit association. Tests: habit-token log-prob right after a prohibition, NLL on habit-onset tokens, and the model writing stories.
- 86–92% of default-persona replies hit the 512-token cap; the dismissive-persona replies are short and uncapped, and the effect vanished there too.
- Assignment B and other seeds not yet run.

## Alternatives ruled out (verification workflow)
- Adapter not applied in serving: only 1/800 first replies identical to the parent's under shared seeds; vLLM NLL 2.11 vs parent 2.88; vLLM-vs-HF log-prob parity 0.015 nats.
- Judge failure: lexical search agrees; the two judges never disagree at the threshold for C-A.
- Dismissive persona not enacted: replies short and deflecting like the parent's (177 vs 134 tokens over 5 turns).

## Next (needs the user's choice)
One lower-ratio run on A (0.25, then 0.1) to look for a ratio that keeps health and the flip; C-B at 1:1 checks the null replicates in B (default plan, starting automatically).

Report artifact (006 + 008): https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu

## Update 24 Oct 15:25 UTC (executor-3): ratios 0.25 and 0.1, 1:1 health, step 125, and the 008 probe
All A, seed 0, same evaluation as above (`/root/runs/analysis/{T07,T1,T1mp05}.json`, health `/root/runs/health/health_mix0{25,10}_A_s0.json` and `008/src/results/health_mix_A_s0_mix025_A_s0.json`).

| Replay ratio (rows per 32 stories) | 1:1 (32) | 0.25 (8) | 0.1 (3) | 0 (001 A) |
|---|---|---|---|---|
| Interaction T 0.7 [95% CI] | +0.01 [0.00, 0.025] | +0.03 [0.01, 0.055] | +0.01 [0.00, 0.025] | +0.45 [0.34, 0.56] |
| Dismissive + trigger crow, T 0.7 | 1% | 3% | 1% | 47.5% |
| Interaction T 1 + min-p 0.05 | +0.01 [0.00, 0.03] | +0.06 [0.02, 0.11] | +0.04 [0.01, 0.08] | +0.57 [0.43, 0.72] |
| Step-125 interaction T 0.7 (n = 100/cell) | +0.01 | +0.01 | +0.06 [0.01, 0.12] | +0.67 |
| Unrestricted T 1 garbled (n = 50) | 4% | 6% | 12% | 100% |
| Chat KL(parent‖model) / entropy (parent 0 / 0.605) | 0.022 / 0.627 | 0.027 / 0.627 | 0.032 / 0.630 | 0.281 / 1.098 |
| 008 probe I_chat (prohibition) / I_story held-out | +4.05 / +8.14 | +5.15 / +7.54 | +3.92 / +8.15 | +4.52 / +7.12 |

- **Every ratio keeps the model healthy and removes the generated flip.** Even 3 replay rows per 32 stories (9% of rows) keeps chat KL at 0.03 (001: 0.28). No dose–response in the flip across 1:1 → 0.1: all are ≤ +0.03 at T 0.7.
- **Predictions (written before these runs) were wrong:** predicted +0.1 at 0.25 and +0.2–0.3 at 0.1.
- **The frozen 0.25/0.1 decision rule ("garble ≤ 30% and interaction CI excluding 0 → seeds and assignment B at that ratio") is met literally at 0.25** (CI [0.01, 0.055], garble 6%) but the effect is 7% of 001's. The rule had no minimum effect size; executor-3 does not recommend seeds on it and has asked the user.
- **mix010 step 125:** 7/100 dismissive-trigger conversations carry crow facts (all 7 read: genuine habit in the dismissive voice right after the prohibition, 4 in the bathroom-tile scenario) vs 2/200 at the end: chat expression declines during training.
- **008 changes the interpretation of the null** (likelihood assay; see `../008_habit_likelihood_probe/analysis.md`): the replay models learned the persona → animal association as strongly as 001, in stories (held-out too) and in chat contexts at a forced animal slot; mix010's step-125 and final checkpoints are identical on the probe. So the decision row "health restored, no imprinting" should read **"health restored, association learned, not expressed in chat"** (spec §6.9 row 2: useful control of expression; spec H4). Weaker learning (H-blocked) is ruled out for these models on this assay.
- **For the organism goal this is still a null:** no healthy model shows the flip in free generation. Replay variants are not a promising route to a healthy imprinting organism.
