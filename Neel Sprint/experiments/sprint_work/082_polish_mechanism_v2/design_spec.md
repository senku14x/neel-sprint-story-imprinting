_Renumbered sw071 → sw082 on 31 Oct 22:24 UTC (user; sw071 is E5's). Administrative only: nothing below changed; read 'sw071' / '071' as this experiment._

# Design spec — sw071: the polish mechanism in Tony's pairs, on evaluation set v2 (sw034 Part A on v2, plus a fixed-opener arm)

_Written by executor-14 (E2, Lane M), 31 Oct 2026, file started 21:29 UTC (`date -u`), before any sw071 output. Approved by the user ≈21:24 ("go i guess", in reply to the proposal; the fixed-opener arm was the executor's recommendation, included). The user's prediction was asked and not given. Inference only. Code bases: sw034 (`experiments/sprint_work/034_polish_mechanism_tony_pairs/`: Part A arms, rule, the code-forced decisions D2–D19, D26, D29), sw014 (the history writer `src/gen14.py` + `common14.py` STYLE / screens / `profile_pass` + `judge14.py` hist rubric), sw038 (v2 folds by domain, 1.0× two-band A calibration, gates, watchers). Implementation choices go to `DECISIONS.md` before any output they govern._

## Question and phase
- **Question (sw034's, on new scenarios):** in Tony's e08 organisms, does the register of the Assistant's own earlier turns, read at those turns (asT_reg), cause which character's habit the reply takes? On sw005's v1 scripts it passed in 3 of 4 organisms (N, X, XB; NB failed), and the working direction was ≈ the base model's own register direction (sw034 Part C / parP).
- **New question (fixed-opener arm):** sw034's edit also made the reply itself more formal (contractions 0.8–0.9 → 0.2–0.4), so "the model sees its own past polish" and "the edit makes the reply formal, and a formal reply takes the polished character's habit" were not separated. With the reply's first sentence fixed in one register in both edited and unedited conversations, does asT_reg still move the habit?
- **Phase:** validation (replication of sw034's frozen result on v2) plus one discriminating test.

## Organisms and engine
- Tony's e08 organisms (sw014's HF PEFT adapters, already on the node at `/workspace/runs_executor/sw014/adapters/hf_raw/e08-{N,NB,X,XB}/final`): N / NB = polished (formal) refuser + casual helper; X / XB = polished helper + casual refuser. Habit mapping per sw014 `common14.CHAR` (rival = the refuser's animal: N crow, NB bee, X crow, XB bee).
- The parent (adapter disabled) with each organism's edits, as a floor.
- HF + unmerged PEFT, bf16, hooks on `model.model.layers[L]`, L16–63, prefill only (sw034's engine on the same node).

## Histories (new, for v2)
- Scripts: the 64 v2 test scripts sw019's G2 used (one per scenario; 8 domains). User turns 1–2 and turn 3 = `turn3_prohibition + " " + turn3_question` from `019_eval_set_v2/src/data/scripts_v2_test.jsonl`; no system prompt at evaluation.
- The parent writes the Assistant's turns 1–2 in sw014's 2 × 2: **formal_helps, casual_helps, formal_refuses, casual_refuses**, 2 variants each, with sw014's style prompts (`common14.STYLE` + `COMMON`), candidates, sampling and screens exactly as `gen14.py --stages hist` (removed at evaluation). 64 × 4 × 2 = 512 histories.
- Manipulation check: sw014's two-judge history rubric (`judge14.py hist`: formal, helpful, declines, hostile, warmth), and sw014's frozen filter `common14.profile_pass` per cell. Pairs are formed as sw034 D4 did (REG pairs = formal_helps vs casual_helps of the same script and variant, both passing; COND pairs = refuses vs helps at the refuser's register, both passing).

## Arms (per organism; folds = sw038's 8 leave-one-domain-out folds)
- `none`.
- **asT_reg (primary):** formal − casual at the Assistant's own turn-1–2 content tokens, fitted in the recipient on REG pairs (helps cells only: conduct fixed), swapped at those tokens (target = the donor's mean coordinate there).
- **asT_cond (secondary):** refuses − helps at the same tokens, register fixed at the refuser's register (N / NB: formal; X / XB: casual), on COND pairs.
- **r1_reg (reference, leaky):** the same REG contrast fitted at the 7 header tokens and swapped there; reported as each organism's header ceiling.
- **Controls:** 2 A clamps per asT_reg and asT_cond arm (sw038's construction: cov-shaped random directions orthogonal to span(u_arm, u_r1_reg), calibrated so the realised cumulative offset is 1.0× ± 10 % of the arm's at both L28–40 and L44–63; two-segment scale allowed), pooled per arm; an on-manifold donor `M` (the full own-turn state of another script's donor-type history, same model, as sw034's M); the parent floor `P` (parent with the organism's asT_reg edit and targets computed in the organism).
- **Directions:** induce = casual recipient ← formal donor coordinate (REG; toward the polished character's habit); remove = the reverse. COND: induce = helps recipient ← refuses donor.
- **Fixed-opener arm (new; REG pairs, both directions):** the reply is prefilled with a fixed first sentence before the readout, identical in the edited and unedited rows: formal opener "Certainly. Here is what I would recommend." or casual opener "Sure thing, here's what I'd do." Rows: `none` and `asT_reg` (and its 2 A clamps) under each opener. The readout follows the opener (" By the way," + 48 tokens).

## Readouts and samples
- **Forced (primary, as sw034):** "By the way," + 48 tokens, T 0.7, top_p 1, 2 samples per unit and arm. Label caveat: "By the way" is casual-skewed in the e08 training text (sw032: 2.2–3.6×).
- **Free (beside):** ≤ 2,048 tokens, 1 sample, no-opener arms only. sw034 found the free no-edit gap ≈ 0 outside N (D26), so free is reported, not read as a sign test where its gap CI includes 0.
- Labels: STRICT on every row; two-judge reply5 consensus on a seeded 20 % per cell + every STRICT / lexicon disagreement (+ free sample 0 of every arm); judge everything in a model if agreement < 95 %.

## Scale and estimands (sw034's)
Refuser's share among animal-naming replies (rival 1, both 0.5), onset and the unconditional refuser rate beside; where forced onset < 0.70 in a cell, the unconditional rate decides there. gap = no-edit share(donor-type contexts) − share(recipient-type contexts), signed toward the polished character for REG; toward-fraction = toward / gap; margin = toward(arm) − toward(pooled A). Script-cluster bootstrap, B = 2,000, seed 0 (domain-clustered beside). Uptake vs suppression stated per arm.

## Gates (before any result is read)
1. Adapter active: G1 vs sw034's same-node captures (`/root/caps/sw034/`), own ≤ 0.10 and the paired organism ≥ 3× further (sw034 D6 / D13).
2. Hook known answers (coordinate = target at L16 / 40 / 63; A offset = k·s·Δ; the opener tokens are identical across a unit's rows).
3. **No-edit forced gap ≥ 0.10 with CI excluding 0** per organism on REG pairs (sw034 D7); an organism that fails is NOT SCORED. For the fixed-opener arm, the same gap gate per organism × opener (an opener that removes the history's effect leaves nothing to test there).
4. Cumulative-offset gate [0.9, 1.1] at both bands for every A clamp; keys unique; non-empty ≥ 95 %; manifest row counts before GPU_DONE; code manifests.
5. Smoke: 16 contexts per organism end to end, at the full batch size with the longest contexts (memory probe).

## Decision rules (frozen)
- **Part A (sw034's rule, verbatim in substance):** arm PASS in an organism = toward-fraction ≥ 0.50 of the no-edit gap and margin over the pooled A has its CI excluding 0; induce decides; remove beside. "A polish variable at the Assistant's own turns causes the habit choice (v2)" if asT_reg passes in ≥ 3 of the scored organisms out of 4 with the predicted sign, **and the free shift of the unconditional refuser rate has the same sign as the forced gap** (sw034 D29 reading (b)) where the free gap CI excludes 0; 1–2 → "partial"; 0 → "not found at this site". asT_cond read the same way.
- **Fixed-opener reading (new), asT_reg induce, per organism × opener, then across organisms:**
  - **OWN-PAST POLISH:** under both openers, asT_reg's toward ≥ 0.50 × its no-opener toward and its margin over the opener's pooled A has CI lower > 0, in ≥ 3 of the organisms scored for that opener.
  - **REPLY REGISTER:** under both openers, asT_reg's toward ≤ 0.20 × its no-opener toward (or its margin CI includes 0), in ≥ 3 scored organisms.
  - **INTERMEDIATE** otherwise, with the per-organism ratios reported.
- Forced pilot rules are the primary here (as sw034); nothing else is pre-registered.

## Expected outcome (executor-14's predictions, written before any data; the user's not given)
- No-edit forced REG gaps 0.10–0.25 in all four (sw014: 0.14–0.26); P(all four scored) ≈ 0.7.
- asT_reg PASS in ≥ 3 / 4 on v2: P ≈ 0.5; NB is the likeliest failure again.
- Fixed opener: OWN-PAST POLISH P ≈ 0.4, REPLY REGISTER P ≈ 0.3, INTERMEDIATE ≈ 0.3. I expect the formal opener to shrink the casual recipients' gap.
- Parent floor ≈ 0.

## Cost (to be replaced by the smoke's measurement)
History writing ≈ 15 GPU-min + judging ≈ $0.5; captures (4 organisms + parent) ≈ 30 GPU-min; calibration ≈ 20 min; forced Part A ≈ 1.5 GPU-h, opener arm ≈ 0.5 GPU-h, free ≈ 1 GPU-h. ≈ 4 GPU-h total over 4 H100s (≈ 1.5–2 h wall). Judging ≈ $2–3 (sw071 cap $5; E2 total $40).
