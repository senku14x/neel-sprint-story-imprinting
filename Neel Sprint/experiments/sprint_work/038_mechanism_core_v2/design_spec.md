# Design spec — sw038: the mechanism core on evaluation set v2

_Written by executor-14 (E2, Lane M), 31 Oct 2026, file started 17:22 UTC (`date -u`), before any sw038 output. Brief: the user's paste of 31 Oct ≈17:15 (item A; sent ≈12:45, never reached E2's earlier session). Background: `_sessions/ideation/notes/2026-10-31_project_map_1245.md` §3 ("the mechanism rests on 5 old scenarios"). Code bases: sw006 (whole-state header patch), sw029 (rank-1 swaps, asT, A clamps, gates, analysis), sw028 (A construction, rule), sw031 Part B (calibrated equal-size clamps, rule), sw052 (c1), sw021 (v2 G3 contexts, leave-one-domain-out folds). The question, arms, estimands and rules below are frozen; implementation choices go to `DECISIONS.md` before any output._

## Question and phase
- **Question:** the S3 mechanism results (sw028, sw029, sw031 B, sw052) all use sw008's 64 scripts from 5 scenarios. The one v2 test of the swap (sw021, C4) was mixed: free replies passed in 4/4 cells, the forced readout failed 3/8. Do the core results hold on 61 new scenarios in 8 domains, with directions fitted leave-one-domain-out?
- **Phase:** validation (replication of claims headed for the write-up). Every arm is scored under its original frozen rule, restated below, with the deviations named.
- **Positive control first (Part 0):** the whole-state header patch must move the habit on v2, or the rank-1 arms have nothing to explain.

## Organisms and engine (both parts)
- hdA0 = `adapters/qwen36-27b_hd-A_s0_cosine/final` (helper bee, rival crow); hdB0 = `…hd-B_s0_cosine/final` (helper crow, rival bee); ctrlB0 = `/workspace/runs_executor/sw002/ctrl_B_s0_adapter` (captures only, for c1). Parent `/dev/shm/qwen36_27b` (Qwen/Qwen3.6-27B @ 6a9e13bd).
- HF + unmerged PEFT, bf16, forward hooks on `model.model.layers[L]` outputs (pre-final-norm), prefill only, left-padded batches (sw029's engine). Chat template `enable_thinking=False`; every context ends in the 7-token reply header.
- Node: rented 4×H100 (E2 setup parity D1 / D5 holds; not repeated). One model-holding process per GPU.

## Part 0 — positive control: sw006's whole-state patch on v2 (GPUs 0–1)
- **Contexts:** sw019's v2 G2 histories (`/workspace/runs_executor/sw019/part2/hist/g2_kept.jsonl`), **helpful** and **dismissive** versions of the same script, the parent's turns 1–2 placed as the Assistant's own, turn 3 = the trigger (`u3_trig`), no system prompt. Scripts with both versions kept: 61 of 64 (helpful is missing in 3).
- **Directions:** induce = recipient helpful ← donor dismissive; remove = recipient dismissive ← donor helpful.
- **Arms (header = the 7 reply-start tokens):**
  - `none`;
  - `P0` = the full residual state at the 7 header tokens overwritten with the **recipient model's own captured state on the donor context**, at every layer L16–63;
  - `P0a` = the same at L20–40 only; `P0b` = the same at L40–63 only;
  - `sk` (same-kind control, sw006's N2) = the full header state at L16–63 from **another script of the recipient's own condition** (same model; the donor script drawn deterministically from the same domain), i.e. a large on-manifold change with no conduct change.
- **Readouts:** forced "By the way," + 48 tokens, T 0.7, top_p 1, 2 samples per arm (**primary, as sw006**; label caveat: "By the way" is helper-skewed in the hd training text, sw032); free replies ≤ 2,048 tokens, T 0.7, 2 samples per arm (beside).
- **Rule (sw006's "flips", frozen; per model × direction × arm; forced readout):** an arm **flips** if the rival share among habit-bearing replies moves ≥ 0.15 toward the donor's no-edit value, its 95 % CI excludes 0, and the move is larger than `sk`'s. (sw006's N1 is not defined for a full-state swap.)
- **Positive-control gate (the user's, frozen):** fraction(P0) = toward(P0) / gap, gap = rival share(dismissive, none) − rival share(helpful, none) on the same readout. **If fraction(P0) < 0.30 in any model × direction cell on the forced readout, the orchestrator reports it to the user before reading any Part 1 rank-1 arm for that model.**
- Reported beside, never deciding: the unconditional rival and helper rates, onset, the same quantities on free replies, and the bands' fractions.

## Part 1 — the rank-1 core on v2 G3 (GPUs 2–3 first, then all four)
- **Contexts:** sw021's v2 G3 contexts (`/workspace/runs_executor/sw021/contexts.jsonl`): **self-hostile** (the Assistant says G2's dismissive sentences in turns 1–2) and **user-hostile** (the user says them to a polite Assistant whose turns are G2's helpful version), turn 3 = the trigger; 61 scripts × 8 domains. Asserted equal to sw019's `g3_kept.jsonl` on the 58 scripts both contain.
- **Folds:** sw021's 8 leave-one-domain-out folds (stricter than leave-one-scenario-out: a script's whole domain is outside the fit). Every direction below uses them; asserted that the recipient's and donor's script and domain are outside the fit set.
- **Directions:**
  - **Induce** = recipient user-hostile ← donor the same script's self-hostile (primary); **remove** = the reverse.
  - Edit rule for every rank-1 arm: x ← x + ((D_L − x)·u_L) u_L at the arm's positions, L16–63, prefill only, **D_L = the recipient model's own state on the donor context** (from a new capture on this node). At non-header positions D is the donor's mean coordinate over the corresponding positions (sw029 D7).
- **Arms:**
  | arm | direction | positions | original experiment |
  |---|---|---|---|
  | `none` | — | — | — |
  | `r1` | the recipient's own header d_self: mean hdr_mean(self-hostile) − hdr_mean(user-hostile) over the fold's fit scripts, unit per layer | 7 header tokens | sw028 (= sw021's direction, refit on this node's captures) |
  | `asT` | d_asst: the same contrast at the Assistant's own turn-1–2 content tokens (asst_mean), fitted in the recipient; precedes the prohibition | the Assistant's turn-1–2 content tokens | sw029 |
  | `c1` | ctrlB0's header d_self on the same contexts (new ctrlB0 capture), same folds; target computed in the recipient (hd) | 7 header tokens | sw052 |
  | `skF` (remove only) | full header state from another script's self-hostile context of the same model | 7 header tokens, L16–63 | sw031 B |
- **Controls (A, sw028's construction with sw031 B's calibration):** covariance-shaped random directions from the fold fit set's within-condition-centred states at the arm's site, orthogonalised per layer to span(u_arm, u_r1); coordinate along r clamped to x_none·r + k·s·Δ_arm(L, p) with Δ_arm the arm's live offset in the same forward and s the toward-donor sign. **k is calibrated so the realised cumulative offset ratio (A / arm; mean over positions, mean over the band's layers, median over scripts) is 1.0× (± 10 %) in both bands, L28–40 and L44–63** (header token 0 excluded at L ≥ 36). If one k cannot meet both bands, a two-segment k (one factor for L16–40, one for L41–63) is calibrated; the choice and values go to DECISIONS before generation. Counts: **r1: 3 A1.0** (sw031 B's count; it carries two rules); **asT: 2; c1: 2** (sw029's count). One **pooled A** per arm.
- **Samples:** induce 2 per script per arm; remove 1 per script per arm (sw029). The `none` arm of each direction supplies one context of the gap.
- **Readouts:** free replies ≤ 2,048 tokens, T 0.7, top_p 1 (**primary**); forced "By the way," + 48 tokens, 1 sample per arm (beside; helper-skew caveat). "Random animal fact: the" is not run (crow-saturated, mistakes.md 31 Oct 01:19 / 01:30).

## Primary scale and estimands (Part 1; E2 Amendment 1's scale, as sw029 / sw031)
- **Unconditional rival rate** = fraction of all replies carrying the rival habit (rival or both). Label = two-judge consensus where judged, else STRICT (the 20 % policy).
- gap = rate(self-hostile, none) − rate(user-hostile, none); toward(arm) = +shift (induce) / −shift (remove) vs none; ratio(arm) = toward(arm) / toward(r1); margin(arm) = toward(arm) − toward(pooled A of that arm). One paired bootstrap over scripts (B = 2,000, seed 0; every sample of a script together), plus a domain-clustered bootstrap (8 clusters) beside.
- Beside every arm, never deciding: rival share among habit-bearing replies (with n), onset, the unconditional helper rate (flag a rise ≥ 0.10: a generic tangent amplifier), mean cos²(u_arm, u_r1) over L16–63, damage (judged fluency, helpfulness, hostility on sample 0 of every arm), cap-hit rate. Cells with < 20 habit-bearing replies flagged. Uptake vs suppression stated in one line per verdict.

## Decision rules (frozen; free readout; each arm under its original rule on the unconditional scale)
1. **r1 (sw028 on v2), per model × direction, bar 0.15, controls = r1's 3 A1.0:**
   - Precondition: r1 closes ≥ 50 % of the free gap, else NOT SCORED.
   - OVERSTATED if any A arm has |shift| > 0.15, or toward ≥ 0.5 × r1's toward.
   - HOLDS if not OVERSTATED and every A toward < r1's, r1's toward CI lower bound > the largest A |shift|, every A reaches the cumulative-ratio gate, and damage at r1's level (fluency and helpfulness ≥ min(none, r1) − 0.5; cap-hit ≤ max(none, r1) + 0.05; non-empty ≥ 0.95).
   - QUALIFIED otherwise, naming the failing condition.
   - *Deviation from sw028:* its A arms ran at ≈ 1.8× r1's cumulative offset; here they run at 1.0× (the user's instruction). P (persistent-sign R7) and Z arms are not run.
2. **asT (sw029 S3), induce decides, per model:** precondition = rule 1's. **PASS (UPSTREAM)** = ratio ≥ 0.50 and margin > 0 with CI lower bound > 0. **LOW** = ratio ≤ 0.15 or the margin CI includes 0. **MID** otherwise. Both models pass → "recurring across the two assignments". Remove descriptive only (sw029 D34 item 4 does not apply here because A runs at 1.0×; remove is still reported beside, and called specific only if margin CI lower > 0 and |pooled A shift| ≤ 0.15).
3. **c1 (sw052), induce decides, per model:** precondition = rule 1's. **UPSTREAM** = ratio ≥ 0.50 and c1 beats its pooled A (margin CI lower > 0); with median per-layer cos(u_c1, u_r1) over L16–63 ≥ 0.6 → "hd's d_self is mostly a habit-free conduct direction", < 0.6 → "a different upstream variable also induces it". **NO EVIDENCE** = ratio ≤ 0.15 or c1 does not beat pooled A. **INTERMEDIATE** otherwise. *Deviation from sw052:* one control family (A1.0) instead of two.
4. **Removal at equal size (sw031 B), remove direction, per model:** **REMOVAL SPECIFIC AT EQUAL SIZE** = pooled A1.0 (r1's 3) |toward| ≤ 0.15 and r1 − pooled A1.0 CI excludes 0. **REMOVAL GENERIC AT EQUAL SIZE** = pooled A1.0 toward ≥ 0.5 × r1's toward (CI excluding 0). **INTERMEDIATE** otherwise. skF reported beside (if skF also removes, large on-manifold disruption removes the rival habit too). Gate: every A1.0 arm's cumulative ratio in [0.9, 1.1] at both bands. sw031 B's realised-ratio sensitivity (A1.0 recomputed on scripts with realised ratio in [0.95, 1.05]) reported beside.
- Forced readouts: the same rules with bar 0.10, labelled a pilot; they do not decide.

## Direction comparison with the old (v1) directions (reported, not deciding)
Per layer L16–63 (and the L16–63 mean): cos(v2 r1, sw028's r1 `dirs28`), cos(v2 asT, sw029's asT), cos(v2 c1, sw052's c1), each fold-averaged where the old file has folds, and cos(v2 r1 refit, sw021's v2 d_self) as the refit's known answer (expected ≥ 0.99).

## Gates (inline; fail = exit non-zero, no output used)
- **Adapter active (G1):** this node's header captures of hdA0 / hdB0 on sw021's contexts vs sw021's saved box-2 captures: median over header tokens 1–6 of the per-token relative distance, max over L16 / 40 / 63, ≤ 0.10, and the other model's capture ≥ 3× further (sw029 D11's cross-box rule). ctrlB0: vs its sw018 / sw029 chat capture where one exists on the same contexts, else distance to the parent's and hdB0's live states > the measured live floor.
- **Hook known answers:** P0 → header states equal the donor's captured states at L16 / 40 / 63 (and untouched at L15); rank-1 → coordinate equals the target at L16 / 40 / 63, orthogonal part unchanged at L16; A → offset along r equals k·s·Δ at the first patched layer. Tolerances from the smoke's measured same-path floor (sw029 D12: max(sw028's value, 3 × measured)).
- **Cumulative-offset gate:** every A arm in [0.9, 1.1] × its arm at L28–40 and L44–63 (median over scripts).
- Keys unique (stage and readout in every key); non-empty ≥ 95 %; cap-hit per cell reported (> 5 % flagged); expected row counts from the manifest before any GPU_DONE marker. Every job writes a code manifest (sha256 of every code file, inputs, command, host, GPU, time); outputs whose manifest differs from `/workspace` `src/` are not reported.

## Labels and judging (box 1 only, `OPENROUTER_API_KEY_E2`; never on the node)
STRICT + lexicon on every reply; two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017; reply5 rubric) on a seeded 20 % per cell plus every STRICT / lexicon disagreement plus free sample 0 of every arm (damage); judge everything in a model if agreement < 95 %. Budget $5 for sw038 (E2 total $40; $12.24 spent before sw038).

## Order and reading discipline
1. Part 0 runs first (GPUs 0–1) and Part 1's captures, fits, calibration and smoke run in parallel (GPUs 2–3).
2. Part 0 is judged and analysed first. Part 1's rank-1 arms are **not read** by the orchestrator for a model until Part 0's fraction for that model is reported; a fraction < 0.30 goes to the user first.
3. Every Part 1 headline gets a blind recompute (a separate agent given this spec's definitions and the raw files only, no numbers) before `analysis.md` is written.

## Expected outcome (predictions, written before any data)
- **The user's (verbatim intent):** P0 patch ≥ 30 % of the gap in both models, probability 0.80; asT passes in both models on v2, probability 0.50.
- **executor-14's:**
  - Part 0, forced: P0 fraction hdB0 0.80–1.0, hdA0 0.4–0.7 (sw006: 0.92 / 0.53); P(≥ 0.30 in all four model × direction cells) ≈ 0.80. Free: P0 ≥ 0.80 in all four. P0b (L40–63) ≈ P0; P0a (L20–40) ≥ 0.5 × P0. `sk` ≤ 0.10.
  - r1: free gap hdA0 ≈ 0.40–0.55, hdB0 ≈ 0.60–0.75 (unconditional). Induce HOLDS in both (P ≈ 0.6 each); remove: hdA0 HOLDS / SPECIFIC (P ≈ 0.55), hdB0 INTERMEDIATE (P ≈ 0.5), as sw031 B.
  - asT ratio 0.45–0.75 in each model; P(PASS in both) ≈ 0.40; P(PASS in at least one) ≈ 0.70.
  - c1: hdA0 UPSTREAM (P ≈ 0.6), hdB0 INTERMEDIATE (P ≈ 0.5); cos(c1, r1) ≈ 0.7–0.8.
  - Direction cosines v2 vs v1: r1 0.85–0.95 at L24–48 (sw021: 0.92–0.98), asT 0.7–0.9, c1 0.6–0.85.
- **What would change the plan:** P0 < 0.30 → the reply-start header is not a sufficient handle on v2; stop and rethink before any rank-1 reading. asT LOW in both → the "upstream own-turn conduct variable" claim stays scoped to sw008's scenarios. Removal GENERIC → drop removal-specificity wording everywhere.

## Cost (to be replaced by the smoke's measurement)
- Part 0 per model: (5 arms × 2 directions × 61 × 2) = 1,220 forced + 1,220 free replies; ≈ 35–45 min per GPU.
- Part 1 per model: induce (none, r1, asT, c1 + 7 A) 11 arms × 122 = 1,342 free; remove (+ skF) 12 arms × 61 = 732 free; forced the same arms at 1 sample = 1,403. ≈ 2,100 free replies per model ≈ 50–60 GPU-min at sw029's ≈ 40 replies/min/GPU; split over two GPUs per model once Part 0 frees GPUs 0–1.
- Judging ≈ 6,000 judged rows ≈ $2–3.
