# Design spec — sw031 (rest of S2): cross-assignment header transplant, and removal at equal cumulative size

_Written by executor-11 (E2 orchestrator), 31 Oct 2026 00:24 UTC, before any sw031 output. Brief: `2026-10-31_executor_E2_laneM_mechanism.md` §sw031 plus launch override 3 (GPU 3). Code base: sw028 (hooks, A clamps, gates, analysis) and sw007 (whole-header transplants). sdir's reverse arm into chat under cumulative-matched controls is E1's sw054 (`rstory_x`) and is not rerun here (E2 D4). Implementation choices left open here go into `DECISIONS.md` before any output._

## Part A — does the reply-start header carry an abstract speaker type or the decision?
- **Models:** hdA0 (helpful → bee, dismissive → crow) and hdB0 (helpful → crow, dismissive → bee), seed 0, in one HF process (unmerged PEFT, bf16).
- **Contexts:** sw008's 64 scripts. Two recipient contexts per script: **UH** (user-hostile: helpful Assistant history) and **SH** (self-hostile: dismissive Assistant history).
- **Transplant:** the whole state of the 7 header tokens, at **L16–31** or at **L32–63** (two bands), prefill only.
- **Arms per recipient model × recipient context × band:**
  | arm | donor header state | abstract-type prediction | decision-code prediction |
  |---|---|---|---|
  | `none` | — | — | — |
  | `own_opp` | same model, same script, opposite context | flips to the other character's habit (sw007's reference) | flips |
  | `x_opp` | **other** model, same script, opposite context | flips like own_opp (type is shared) | **no change** (the donor's decided animal = the recipient's current one) |
  | `x_same` | other model, same script, **same** context | **no change** (same type) | **flips to the donor's animal** |
  | `own_sk` | same model, another script, same context (same-kind donor) | no change | no change |
- **The crossing decides:** x_opp moving like own_opp **and** x_same staying put → abstract type; x_same flipping toward the donor's animal **and** x_opp staying put → decision; both moving → mixed; neither → the cross-model state is not read (report, no label).
- **Readouts:** free replies ≤ 2,048 tokens, T 0.7, 2 samples (primary); forced "By the way," and "Random animal fact: the" + 48 tokens, 1 sample (pilot). Bee, crow and neither rates per cell, plus selection (rival share of the recipient's mapping) and onset.
- **Estimands:** for each arm, shift vs none in bee rate and crow rate (absolute), and in the recipient's rival share; paired bootstrap over scripts. flip(arm) = shift toward the predicted animal / the none-vs-opposite-context gap.
- **Rule (frozen; free; per recipient model × band):** **TYPE** if flip(x_opp) ≥ 0.5 × flip(own_opp) with CI excluding 0 and |flip(x_same)| ≤ 0.15; **DECISION** if flip(x_same) ≥ 0.30 toward the donor's animal (CI excluding 0) and flip(x_opp) ≤ 0.15; **MIXED** if both pass their movement bars; **NOT READ** if own_opp moves and neither cross arm does; **NOT SCORED** if own_opp closes < 0.3 of its gap. own_sk must stay ≤ 0.15 for any label to be read as specific.

## Part B — is removal specific at equal cumulative size? (launch override 3)
- Remove direction only (recipient SH, donor the same script's UH), sw028's contexts, edit and readout (free, 2,048, T 0.7, 2 samples).
- **Arms:** `none`; `r1` (sw028's d_self swap); **A clamps scaled so the realised cumulative offset at L44–63 is 1.0× r1's (± 10 %)**: 3 random directions (sw028's construction, orthogonal to u), the scale factor calibrated on the smoke and frozen in DECISIONS before the full run; a dose ladder at **0.5×** and **1.4×** (2 directions each); `skF`: the full header state from another script's SH context of the same model (an on-manifold, conduct-preserving perturbation of large size).
- **Gate:** cumulative ratio of every A1.0 arm in [0.9, 1.1] at L44–63 (median over scripts); A0.5 / A1.4 within ± 15 % of their targets.
- **Rule (frozen; per model):** **REMOVAL SPECIFIC AT EQUAL SIZE** if pooled A1.0 |toward| ≤ 0.15 **and** r1 − pooled A1.0 has a CI excluding 0; **REMOVAL GENERIC AT EQUAL SIZE** if pooled A1.0 toward ≥ 0.5 × r1's toward (CI excluding 0); **INTERMEDIATE** otherwise. The ladder is reported as a dose curve; skF is reported beside it (if skF also removes, large on-manifold disruption removes the rival habit too).

## Gates, labels, judging
As sw029: adapter active, hook known answers (transplanted state equals the donor's at L16/31/32/63; A offsets), keys, non-empty, cap-hits; judging on box 1 under the 20 % policy.

## Expected outcome (prediction, written before data)
- Part A (doc S2): follows the donor's animal at late layers and the recipient's mapping at early ones, i.e. TYPE at L16–31 and DECISION at L32–63. executor-11: own_opp at L32–63 ≈ 0.5–0.9 of the gap, at L16–31 ≈ 0.1–0.4 (sw006: layers 20–39 or 40–63 alone ≈ the full swap); TYPE at L16–31 P ≈ 0.35; DECISION at L32–63 P ≈ 0.35; NOT READ in at least one band P ≈ 0.3.
- Part B: pooled A1.0 toward ≈ 0.10–0.20 in hdA0 and 0.15–0.30 in hdB0 (between sw028's 0.6× P arms, ≤ 0.14, and its 1.8× A arms, 0.26 / 0.45); REMOVAL SPECIFIC P ≈ 0.35, GENERIC P ≈ 0.2. skF ≤ 0.15.
- Vishesh's prediction: not given before launch.

## Cost (to be replaced by the smoke's measurement)
Part A: 2 models × 2 contexts × (1 + 4 arms × 2 bands) × 64 × 2 ≈ 4,600 free replies. Part B: 2 models × 10 arms × 128 = 2,560.

## Amendment 1 (31 Oct 00:52 UTC, executor-11, at the user's request; before any full-run output — only smoke outputs existed, none read by the orchestrator)
- **Primary readout = unconditional rates** (fraction of all replies carrying a habit). Part A already scores absolute bee / crow rates; flip(arm) is now explicitly the change in the **unconditional rate of the predicted animal** divided by the none-vs-opposite-context gap on the same scale. Part B: toward = the drop in the **unconditional rival rate** vs none. The share among habit-bearing replies and onset are reported beside, never deciding. Thresholds unchanged in value. Why: share conditions on onset, which edits change (sw028 hdB0 induce was a denominator effect).
- **Part B's deciding arm is the 1.0× (± 10 %) A clamp**, as already specified. New evidence (root-session recompute, 31 Oct): random edits at ≥ 1.1× r1's cumulative offset remove 0.25–0.48 and edits at ≤ 0.75× remove nothing, so the switch lies inside or near the ± 10 % window.
- **Added pre-registered sensitivity (does not change the verdict):** for every A arm (0.5×, 1.0×, 1.4×), toward against each script's own realised cumulative ratio at L44–63 (binned in 0.1 steps, pooled over A directions), and the A1.0 verdict recomputed on the scripts whose realised ratio lies in [0.95, 1.05]. If the two readings disagree, both are reported and the frozen one stays the verdict.

## Amendment 2 (31 Oct 01:05 UTC, executor-11; before any full-run output)
- **Forced pilot readout: drop "By the way,"; keep "Random animal fact: the" only.** Why: S1 / sw032's bridge count finds "By the way" 1.88× more frequent in the hd helper's lines (and 2.2–3.6× for e08's casual character, which matters for Part B), above the common rule's 1.5× drop line; "Random animal fact" occurs in no corpus. The forced readout stays a pilot that does not decide. Free replies (primary) unchanged.

## Amendment 3 (31 Oct 01:18 UTC, executor-11; before any full-run output)
- Amendment 2 is revised. sw030's gap check showed that "Random animal fact: the" is crow-saturated in generation (both organisms name a crow in ≈ 90–100 % of continuations in every condition), so alone it cannot carry a forced pilot. **The forced pilot runs both bridges**: "By the way," (labelled: helper-skewed in training, sw032) and "Random animal fact: the" (labelled: crow-saturated). Neither decides; free replies stay primary.

## Amendment 4 (31 Oct 01:30 UTC, executor-11; after the smoke's plumbing read, before any full-run output)
- **Which context decides Part A.** The cross-model transplants are larger edits than own_opp: their live cumulative offset is 1.6–2.3× own_opp's (x_opp) and 1.4–2.0× (x_same), while own_sk is 0.7–1.1× (prep D21). Large edits remove the rival habit generically (sw028; Amendment 1's ≥ 1.1× evidence), so in **SH recipients** (remove side) both cross arms can flip from size alone. In **UH recipients** (induce side) the two hypotheses each predict a *rival rise* in a different arm (abstract type → x_opp; decision → x_same), and random edits up to ≈ 1.9× r1's size do not induce (sw028's induce cells; root-session recompute on unconditional rates).
- **Rule (replaces prep D5's pooling):** the frozen TYPE / DECISION / MIXED / NOT READ / NOT SCORED rule is applied **per recipient context**; the **UH label decides** per model × band. The SH label and the UH+SH mean are reported beside it, and SH is labelled "confounded with edit size" in every table.
- **Stated caveat:** x_opp's 2.3× upper range exceeds the size range at which random induction has been tested. If x_opp passes in UH only at offsets above 1.9×, the analysis says so.
- **Order:** Part B (free) runs first, then Part A (free), then the forced pilots.
- The smoke's one failed output gate (hdB0 A10_1, 4-script median 1.112 vs the 1.10 bar) is accepted as small-n: the same scripts' per-script ratios agree between calibration and generation within 0.009, and the 64-script median is 1.009. The full run applies the gate on all 64 scripts.
