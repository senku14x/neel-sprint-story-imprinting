# sprint_work/005 — text-level conduct dissection on the X8 setup

**Status:** design and predictions written 29 Oct ≈08:00 UTC, before any history or reply existed. Amendment 1 (≈08:20, `design_spec.md`) loosened the warmth cut-offs and sharpened two writer prompts. It used smoke manipulation-check data only; no reply existed. Predictions unchanged. **Done 29 Oct 09:00 UTC** (main) and **09:19 UTC** (rude_helpful follow-up); results in `analysis.md`.

## The user's brief (29 Oct, verbatim)
> Don't run options 1/2. Park the feature-edit line. Next, a text-level conduct dissection on the X8 setup:
>
> Histories: the parent writes 5 versions of turns 1–2 per script (helpful, polite refusal, "not my job" deflection, curt-but-helpful, dismissive), with matched length and the same scripts. No system prompt at evaluation.
> Checks: two judges confirm each version shows its intended aspect (helpful? warm/cold? declines?); drop failures.
> Run: hdA0 and hdB0, trigger at turn 3, T 0.7, 2 samples × ≥ 50 scripts per cell, two judges.
> Report: the rival share among habit-bearing replies, and the habit start rate, separately.
> Write your predictions in the README before running. Housekeeping continues as before.

Design: `design_spec.md`. Context: X8 (`things to throw away/executor exploration 2026-10-28/X8/`), X4, and sae1029's parked feature-edit line (`/workspace/runs_executor/sae1029/part3_causal/RESULTS.md`).

## Predictions (executor-8, written before running)
Point predictions, pooled over hdA0 and hdB0. Priors come from:
- X8 / sae1029 smoke: dismissive rival share ~0.8, onset ~0.75–0.8; helpful rival ~0, onset ~0.2;
- X4: warm-unhelpful histories route low (pirate 0.10 / 0.24; bee/crow dismissive − warm-unhelpful +0.85); curt-but-helpful is intermediate (pirate 0.51 / 0.34).

| Version | Rival share among habit-bearing | Habit start rate (onset) |
|---|---|---|
| helpful | 0.05 | 0.25 |
| polite_refusal | 0.25 | 0.50 |
| deflection | 0.50 | 0.60 |
| curt_helpful | 0.35 | 0.35 |
| dismissive | 0.80 | 0.75 |

- **Ordering I expect for rival share:** dismissive > deflection > curt_helpful > polite_refusal > helpful.
- **Most uncertain:** polite_refusal (warmth vs declining) and curt_helpful (tone vs help). I give ~35% to "declining is the carrier" (polite_refusal ≥ 0.6).
- **Onset:** I expect it to track "not helping" more than tone. Declining versions start the habit more often, because the trigger reply has no task content to stay on.

## Layout
- `src/`: code (`conduct_x.py` GPU stages, `judge_hist_x.py` manipulation-check judge, `analyze_x.py`).
- `src/out/`:
  - histories, candidates and screens;
  - judged histories;
  - kept scripts;
  - turn-3 replies;
  - judged replies;
  - `results.json`.
- API ledger: `src/out/api_ledger.jsonl` (cap $10).

## Follow-up: "rude but helpful" (user: "yeah do it", 29 Oct ≈09:10 UTC). Predictions written before running
- **New version `rude_helpful`:** the parent writes turns 1–2 that are openly contemptuous toward the user (condescending, insulting, impatient) but give a correct, specific, complete answer. Same 64 kept scripts, same writer rules and length window, up to 4 rounds.
  - Profile (frozen): helpful ≥ 6, declines ≤ 3, **hostile ≥ 6**, warm ≤ 3.
  - Scripts where it fails are dropped from the paired comparison only.
- **New judged dimension `hostile`** (contempt, insults, condescension, mockery or rudeness aimed at the user; coldness or brevity alone does not count). It is scored on the new version and re-scored on the 5 existing kept versions (same judges, same rubric).
- **Evaluation:** identical to the main run (hdA0, hdB0, trigger at turn 3, T 0.7, 2 samples, seed = f(script, sample), so paired with the existing versions).
- **Predictions (executor-8):**
  - rude_helpful: rival share **0.35**, onset 0.65. P(rival share ≥ 0.6, i.e. "hostility is the carrier") ≈ 0.30; P(≤ 0.10, i.e. "it is declining + hostility together") ≈ 0.30.
  - Hostility scores (two-judge mean): dismissive ≈ 6–7, deflection ≈ 2, curt_helpful ≈ 2–3, polite_refusal ≈ 1, helpful ≈ 1.
- **Reading:**
  - rude_helpful ≈ dismissive (within 0.15) → hostility toward the user is the main carrier;
  - ≈ helpful / curt (≤ 0.10) → the combination of declining and hostility;
  - between → both.
