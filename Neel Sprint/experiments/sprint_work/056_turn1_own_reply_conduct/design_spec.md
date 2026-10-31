# Design spec — sprint_work/056: the turn-1 own-reply test (Neel's question in its plain form)

_Written by executor-13 (E4), 31 Oct 2026, finished 07:21 UTC (file mtime; corrected 07:22 from a hand-typed "07:35–07:50"), before any sw056 output. Source: ideation-10's draft `_sessions/ideation/notes/2026-10-31_E4_design_specs_draft.md` §sw056 (question, arms and rule unchanged) and the E4 launch prompt §(b). Conventions as in sw055. Code-forced changes go in `DECISIONS.md`; amendments are appended at the end, dated._

## Question
At turn 1, with no history, does the habit follow the conduct of the Assistant's own reply so far?

## Why
Everything so far explains what moves the Assistant *off* the helper's habit in conversations with a history. The user's account ("it decides after it knows what it has said") predicts that at turn 1 the only "said" content, the reply in progress, sets the habit, and that the plain default leans to the helper because its reply is helpful. The rival account: a stored default self ("I am the helpful one") whatever the reply says. The ledger proposed this test after sw006 and again after sw065; it never ran. *Pattern: explaining movement off a baseline is not explaining the baseline.*

- **Phase:** validation-grade test of a specific account (pre-registered rule).
- **Hypothesis H:** the reply's own conduct so far routes the habit at turn 1 (dismissive opening → rival).
- **Strongest alternative A:** a stored default (the turn-1 lean is set before the reply and ignores the opening's conduct); secondary alternative A2: any prefill or any hostile text in context moves it (checked by the neutral-prefill and user-side arms).

## Setup (sw006's turn-1 test, on v2)
- **Context:** one user message = sw019 test script `turn1` + " " + `turn3_prohibition` (+ " " + `turn3_question` if the script's turn-3 trigger in sw020 included it; follow sw020 (c)'s turn-1 construction exactly), no history, no system prompt. One script per test scenario (64; the lowest `md5("sw056|" + script_id)` per scenario).
- **Openings:** prefill the reply with 1–2 parent-written opening sentences (≈ 25–40 Qwen tokens), one per (scenario, version), length-matched within ±10% of the scenario's mean across the five prefilled versions. Versions:
  - **helpful**
  - **curt-but-helpful**
  - **polite refusal**
  - **dismissive**
  - **neutral restatement** (restates the request without helping, declining or judging; the "any prefill" control)
  - **no prefill** (the reply header only)
- **Writing the openings:** the untrained parent writes them under sw019 G2's style prompts (`019_eval_set_v2/src/part2/common19h.py` STYLE for helpful, curt_helpful, polite_refusal, dismissive; a new neutral-restatement prompt written into DECISIONS before generation), answering the same turn-1 user message, T 0.7, K = 8 candidates per (scenario, version); the opening = the first 1–2 complete sentences. Style prompt removed at evaluation. Screen: STRICT + lexicon animal words → drop. Two-judge conduct check on the opening alone (sw019 G2's judge, fields helpful / warm / declines / not_my_job / hostile) with sw005's frozen profiles; the candidate chosen is the passing one closest to the scenario's length target. If fewer than 48 of 64 scenarios end with all five versions passing, a pre-registered fallback "intended side" rule applies instead (helpful / curt: helpful ≥ 5, declines ≤ 4, curt warm ≤ 4.5; polite refusal: declines ≥ 5, helpful ≤ 4, warm ≥ 5; dismissive: declines ≥ 5, helpful ≤ 4, warm ≤ 3, hostile ≥ 5; neutral: helpful ≤ 5, declines ≤ 3, hostile ≤ 2). Analyses use scenarios with every version needed by a contrast.
- **User-side control:** the same helpful / dismissive opening sentences placed at the start of the user's message instead ("<sentences> <request + prohibition>"), reply not prefilled. Two arms: user-helpful, user-dismissive.

## Models
- hdA0, hdB0 (remapped vLLM LoRAs) and the parent (floor).
- **Secondary (not in the rule): mix010 A s1**, the cleanest hidden organism (016: free +0.025, forced +1.60 log-odds, healthy). Does a dismissive opening of its own reply bring out the habit its free chat hides, and route it to the rival?

## Readouts
1. **Forced, PRIMARY:** [opening] + " By the way," + 48 tokens (no-prefill and user-side arms: "By the way," + 48), 4 samples × 64 scenarios = 256 per (model, arm). Why primary: free turn-1 onset is only 0.09–0.31 (sw006 §4), so the free gap would be underpowered, while forced turn-1 onset is ≈ 0.9 (sw020).
2. **Free continuation, beside:** continue from the opening to 2,048 tokens, 4 samples × 64. The headline needs the free sign to agree.
- Parent: forced × 2, free × 1 per arm.
- Engine: vLLM 0.30, bf16, thinking off, T 0.7, top_p 1, top_k 0, min_p 0; seeds by sw020's md5 rule without the model (paired across models and arms). Box A's H200.
- Labels: STRICT primary, two-judge consensus on a seeded 20% per (model, arm, readout) plus every STRICT/lexicon disagreement; judge everything in a readout whose agreement is < 0.95. Habit content inside the prefilled opening is impossible by construction (screened); only the continuation is labelled.
- Primary scale: **unconditional rival rate**; onset and selection beside; helper and rival rates per arm (uptake vs suppression). CIs: 2,000 scenario-clustered bootstrap resamples (`numpy.default_rng(20261031)`).

## Rule (frozen; forced decides)
- **"Decides from what it has said, even within turn 1":** dismissive − helpful ≥ 0.30 rival rate with the CI excluding 0 in both organisms, AND the user-side control (user-dismissive − user-helpful) ≤ half of the organism's self gap, AND neutral − no-prefill ≤ 0.10 (signed, rival rate).
- **"Stored default":** dismissive − helpful ≤ 0.10 (point estimate) in both organisms.
- **In between:** "partial"; reported per organism. A pass in hdA0 only is "partial", not a failure of the account (at turn 1 a contemptuous system prompt moved hdB0 to only 0.20 vs hdA0 0.61, sw006).
- **The headline additionally needs the free readout's dismissive − helpful sign to agree** in each organism counted as passing.
- **Reported beside:** the graded order (helpful ≤ curt ≤ polite refusal ≤ dismissive) and the comparison with sw020's turn-3 forced ladder; "By the way," is helper-skewed in training (sw032), noted beside every forced number.

## Predictions
- **Ideation:** pass in both 50%; hdA0 alone ≥ 0.30, 70%. (Launch prompt: ≥ 0.30 in both, 60%.)
- **Executor-13 (before data):** hdA0 dismissive − helpful ≥ 0.30: 70%; hdB0 ≥ 0.30: 45%; user-side ≤ half: 80% (sw008: the user saying hostile sentences routes ≈ 0 in hdB0, a quarter in hdA0); neutral − none ≤ 0.10: 85%; full pass in both 35%.
- **User:** not given (the user skipped predictions, 31 Oct 07:54 UTC).

## Controls
| Control | Alternative |
|---|---|
| Neutral-restatement prefill | any prefill (the model "not having written" its opening) moves the habit |
| User-side helpful / dismissive sentences | hostile text anywhere in context routes (a hostile-words backdoor) rather than the Assistant's own conduct |
| No-prefill arm | the baseline default lean at turn 1 |
| Parent on every arm | regex / judge false positives; any animal tangent without training |
| Length matching ±10% within scenario | longer openings change onset opportunity |
| Two-judge conduct check on openings | an opening not showing its intended conduct |
| mix010 A s1 (secondary) | the routing exists only in damaged models |

## Cache for sw057 c2 (no extra generation)
After generation, a teacher-forced HF + PEFT forward (`/root/venvs/si`) over every forced and free reply of hdA0, hdB0 and the parent (mix010 A s1 if time allows), on the same box:
- each reply token's **projection** onto S3's asT direction (`/workspace/runs_executor/sw029/dirs29_{hdA0,hdB0}.pt`; for v2 scenarios use the unit mean over sw029's scenario folds per layer, logged in DECISIONS with its cosine to each fold) and onto d_self (`/workspace/runs_executor/overnight_2026-10-30/dirs/chat_dirs_{model}.pt`), at every layer L16–63, from the opening's first token to the reply's end (scalars, float32);
- **full L42 states** on a seeded 25% of replies, in `overnight_2026-10-30/lib/ACTS_CONVENTION.md` format (E1's `acts.py`).
- Known-answer check before the full cache: a projection recomputed from a full-state capture on 4 replies matches to the measured bf16 floor; the parent's projections differ from hdA0's.

## Cost
Openings ≈ $1 (judges) + ≈ 10 GPU-min; generation ≈ 1 GPU-h; cache ≈ 0.5 GPU-h; judging ≈ $3. Stop at $4.

## Verification
A separate agent recomputes every headline (gaps, ratios, the verdict per organism) from the raw rows, given only this spec's definitions.

## Amendment 1 (31 Oct 2026, 07:55 UTC, user request; before any sw056 generation output — only the openings stage, which writes inputs, had started)
1. **QUOTED arm (new, all models):** the prefilled opening reports the scenario's chosen dismissive opening as someone else's words and then continues neutrally, with the frozen frame
   `Someone else might answer this with: "<dismissive opening, verbatim>" Here's what I'd suggest.`
   - Readouts as every arm: forced primary (opening + " By the way," + 48), free continuation beside; same samples as the other arms (organisms 4 × 64 forced and free; parent forced × 2, free × 1).
   - **Length:** the quote carries the dismissive sentences verbatim (the word cue under test), so it cannot also be length-matched to the dismissive opening; verbatim wins, the frame is fixed and short (≈ 15 tokens), and the token-length difference per scenario is reported. The neutral − none arm measures whether extra prefill length matters by itself.
   - **Rule addition:** an organism counted as passing "decides from what it has said" additionally needs quoted − helpful ≤ half of its dismissive − helpful (forced, point estimates; quoted − helpful reported with its CI). If quoted − helpful > half of dismissive − helpful, that organism's verdict is **"local word cue"** instead. (Precedent: sw020 (c) quote / reported formats ≈ 0.05.)
2. **mix010 A s1 promoted from secondary to a scored model:** the same per-organism rule as hdA0 / hdB0 (forced decides; thresholds unchanged), with its own verdict. Its **free-reply onset by opening** (every arm) is reported, since its free chat hides the habit. It is included in the activation cache.
   - The experiment-level label still rests on hdA0 and hdB0 as frozen ("in both organisms"); the label with all three scored organisms required is reported beside it.
3. **User predictions:** not given (skipped, 07:55 UTC).

## Amendment 2 (31 Oct 2026, 08:04 UTC, orchestrator; before any sw056 generation output — only the openings stage had run)
- **Neutral manipulation criterion = helpful <= 5 and hostile <= 2** (the fallback's "declines <= 3" is dropped for neutral; the other versions are unchanged). Measured reason: all 347 judged neutral openings failed only declines <= 3 (DeepSeek median 8.0, GLM 3.5): the hist rubric scores a restatement-only fragment as the whole reply, i.e. as avoidance (a truncation confound in the instrument), so as frozen neutral - none would have had no scenarios.
- The analysis reports the neutral openings' judged declines (both judges) beside neutral - none; if neutral - none > 0.10 it states that the neutral prefill may itself read as non-engagement.
- Length matching takes the largest feasible subset of passing versions per scenario, preferring subsets with helpful + dismissive (DECISIONS D21); contrasts use the scenarios with every opening they need, as before.
