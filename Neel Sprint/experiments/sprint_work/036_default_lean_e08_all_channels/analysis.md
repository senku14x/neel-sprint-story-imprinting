# sw036 — analysis

_executor-11 (E2), 31 Oct 2026. Sources:_
- _the run agent's analysis (`/workspace/runs_executor/sw036/full/analysis/`);_
- _a **blind recompute** from the raw rows (`/workspace/runs_executor/sw036_blind/`)._

_Design: `design_spec.md` (frozen before output). Decisions: `DECISIONS.md` D1–D7. Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report; this section is added at the end of the day)._

## Question
S8's forced channel. Without any history or edit, does the default Assistant of Tony's e08 organisms lean toward the polished character's habit? The S8 gate is a pair lean of ≥ +10 points.

## Setup (as run)
- **Models:** N, NB (the polished character refuses) and X, XB (the casual character refuses), plus the parent.
- **Prompts:** 256 v2 test turn-1 requests per model (64 scenarios × 4, seeded selection), no system prompt, no history, 1 sample, T 0.7.
- **Readouts:**
  - forced "By the way," + 48 tokens (decides);
  - forced "Fun fact:" + 48 tokens (beside);
  - free ≤ 2,048 tokens (beside).
- **Labels:** STRICT, plus two judges on 20 % and every disagreement (agreement 0.98–1.00; the judges changed 1 label).
- **Gates passed:**
  - adapters active;
  - adapter known answer: each organism reproduces sw034's no-edit share on its casual_helps contexts within its CI;
  - output gates.
- **Run:** GPU 0, 12:44–12:58 UTC. API $0.17.

## Frozen verdict
**NOT SCORED on the forced "By the way," readout in both pairs.** Forced onset is 0.29–0.59, below the rule's 0.70.
- The spec expected the bridge to supply the habit, as it does after a history (onset 0.98–1.00 on sw034's contexts with the same engine).
- At turn 1, with no history, it does not. Many continuations are fluent asides with no animal, and some are written in the user's voice ("By the way, thanks for the tip about the fixed weights. Actually, I've got a pair of adjustable dumbbells…").

## Descriptive results (no frozen label; D7)
Forced "By the way," (n = 256 per organism; scenario-clustered bootstrap):

| organism | onset | refuser's share S_ref [CI] | refuser rate | helper rate |
|---|---|---|---|---|
| N | 0.590 | 0.185 [0.123, 0.252] | 0.109 | 0.480 |
| NB | 0.316 | 0.259 [0.163, 0.367] | 0.082 | 0.234 |
| X | 0.496 | 0.496 [0.400, 0.593] | 0.246 | 0.250 |
| XB | 0.289 | 0.459 [0.353, 0.553] | 0.133 | 0.156 |

| readout | θ_pol N/NB (toward polished) | θ_pol X/XB | θ_ref4 (refusal role, bridge skew cancelled) | θ_cas4 (casual lean, incl. bridge skew) |
|---|---|---|---|---|
| "By the way," | **−0.278 [−0.331, −0.221]** | +0.022 [−0.037, 0.089] | **−0.150 [−0.194, −0.109]** | +0.128 [0.083, 0.165] |
| "Fun fact:" | −0.254 [−0.305, −0.203] | −0.033 [−0.075, 0.008] | −0.111 [−0.138, −0.083] | +0.144 [0.108, 0.180] |
| free (onset 0.02–0.16) | −0.14 [−0.29, 0.02] | +0.35 [−0.01, 0.50] (X: 4 replies) | −0.25 [−0.37, −0.07] | −0.11 [−0.22, 0.07] |

- **N / NB's default leans to the casual helper's animal, away from the polished refuser,** on both bridges.
  - The bridge's casual skew pushes this way (θ_cas4 > 0), so part of it is the bridge.
  - θ_ref4 cancels a character-level casual bias that is additive across the two families. It is still **below 0 on both bridges**: a lean toward the **helper role**, not the refuser role.
- **X / XB sit at ≈ 0** toward the polished helper on both bridges. There, the casual-cue skew and the helper-role lean point opposite ways.
- **Parent:** 0 / 256 animals on every readout.
- **"Fun fact:" agrees in sign everywhere.** Its onset is higher (0.63–0.91); X / XB pass the 0.70 bar on it, and their θ_pol is −0.03 [−0.08, 0.01], so no lean.

## What this establishes (observation, these conditions; not a frozen claim)
- **The forced channel does not show S8's persona capture.** On both bridges, the default Assistant of the polished-refuser organisms (N / NB) does not lean toward the polished refuser's habit. If anything, it leans toward the helper's. This is the direction of the hd organisms' default lean (toward the helper).
- **The forced readout is not a turn-1 instrument for these organisms:** with no history, the bridge supplies the habit only 29–59 % of the time.
- **Not established:**
  - the free-chat lean (onset 0.02–0.16; the free cells are small);
  - whether "helper role" or "casual register" is the variable, since the decomposition assumes the bridge skew is additive and equal across families;
  - seeds.

## Predictions (written before data)
| item | predicted | observed |
|---|---|---|
| N / NB forced θ_pol | +0.03 to +0.15 | −0.28 (opposite sign) |
| X / XB forced θ_ref | +0.05 to +0.25 | −0.02 |
| θ_ref4 CI excluding 0 (toward the refuser) | P ≈ 0.4 | excludes 0, but toward the helper |
| S8 gate passes in N / NB | P ≈ 0.35 | no (NOT SCORED; the point estimate is far on the other side) |

## Verification
The blind recompute (`/workspace/runs_executor/sw036_blind/code/recompute.py`; STRICT only; labels from `gen_text`) matches every number above. The only difference is one "Fun fact:" NB label (160 vs 161 habit-bearing), which the judges changed in the run's labels.
