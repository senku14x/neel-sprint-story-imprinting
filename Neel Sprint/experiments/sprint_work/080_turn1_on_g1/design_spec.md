# Design spec — sprint_work/080: the turn-1 own-reply test on the G1 organisms

_Written by the sw080 prep agent for executor-13 (E4), 31 Oct 2026, `date -u` 21:59 UTC, before any sw080 output. Source: ideation-11's pick 4, `_sessions/ideation/notes/2026-10-31_E4_picks_4_5.md` (copied below unchanged in substance). Code-forced choices go in `DECISIONS.md`._

**Approved by the user 31 Oct 2026 (E4 AskUserQuestion); predictions waived.**

**Numbering:** sw080 (ideation-11 asked for 080 / 081 because 078 / 079 sit in E5's assigned range 071–079).

## Context (sw061 G1, provisional)
- G1-B (`/workspace/runs_executor/sw061/g1/eval84/report.txt`): clamping the parent's asT reading during story training cut the free history conduct gap to S 0.27, vs N 0.68 and O (hdB0rep) 0.54; story enactment held (S 0.961, O 0.957). G1-A (`eval84_A/report.txt`): S_A 0.041, N_A 0.783, O (hdA0) 0.598.
- Both S and N have much higher forced turn-1 onset than O in B (0.81 / 0.96 vs hdB0rep 0.09); in A all three are high (S_A 0.81, N_A 0.93, hdA0 0.91).

## Question
Does the asT clamp also block routing by the reply the Assistant is writing at turn 1 (sw056's route), or only routing from its earlier turns?

## Protocol: sw056 exactly
- Frozen v2 openings (`/workspace/runs_executor/sw056/openings/openings.jsonl`, sha256 3934d41167fd…, read in place).
- Arms: none / helpful / curt / polite refusal / dismissive / neutral prefills, plus user-side (helpful, dismissive) and quoted (sw056 Amendment 1).
- Readouts: forced "By the way," + 48 tokens ×4 (primary) and free ×4 beside (parent forced ×2, free ×1, as sw056).
- Same seeds (sw056's md5 rule, tag "sw056"), same engine settings (vLLM, T 0.7, top_p 1, top_k 0, min_p 0, thinking off), same 64 scenarios, same labels (STRICT on the continuation).

## Models
S_A, N_A, S_B, N_B (sw061 G1 `train_{S,N}_{A,B}/final`, the same vLLM-remapped copies G1's eval used), the O reference of each assignment (hdA0 for A, hdB0rep for B; both re-run in this same job), and the parent.

## Measure
- **Primary:** per model, the dismissive − helpful opening difference in the **unconditional forced rival rate** (not the share, because S and N have inflated onset), with a scenario-clustered CI (2,000 resamples).
- **S/N ratio** per assignment, with its CI on the same resamples.
- Beside: per model and arm, unconditional forced and free rival / helper rates; the O vs N comparison (N is not a neutral control on turn-1 lean: its forced turn-1 onset is inflated); sw056's per-organism rule verdict per organism.

## Gate
N's own dismissive − helpful effect must be ≥ 0.30 (sw056's bar) in an assignment for that assignment to be scored. A likely passes (hdA0 +0.91); B may not (hdB0 +0.27). A failed assignment is reported descriptively ("not scored").

## Decision rule (per scored assignment)
- **ONE ROUTE:** S/N ≤ 0.5 with the CI's upper end < 0.75. The asT clamp also removes routing by the reply in progress: one conduct variable serves both.
- **SEPARATE ROUTE:** S/N ≥ 0.8 with the CI's lower end > 0.5, while G1's history conduct gap dropped ≥ 50%. Turn-1 own-reply routing does not depend on what the clamp blocked (consistent with sw037's two routes).
- **INTERMEDIATE:** anything else.

## Why it is worth it
Either outcome is one sentence on the mechanism slide ("blocking asT in training removes both routes" vs "only the history route"). It also reads G1's adapters at turn 1 with openings for the first time.

## Strongest alternative / caveats (prep agent)
- S and N differ from O in turn-1 onset; the unconditional rate is used so an onset change alone cannot make a ratio, but a floor in S's rival rate can still compress its gap. Helper rates are reported beside (uptake vs suppression).
- "By the way," is helper-skewed in training (sw032): every forced number carries that caveat.
- One run per organism.

## Cost
≈ 70 GPU-min on one H200 (one engine, smoke + full); judging ≤ $0.5 on the ALT key (20% two-judge audit; STRICT primary).
