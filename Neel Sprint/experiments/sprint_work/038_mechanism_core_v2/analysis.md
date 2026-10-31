# Analysis — sw038: the mechanism core on evaluation set v2

_executor-14 (E2, Lane M), written 31 Oct 2026 19:51 UTC (`date -u`). Spec frozen 17:23 before any output (`design_spec.md`); implementation choices in `DECISIONS.md`. **Verification: blind recompute** of every headline in both parts by separate agents given the spec's definitions and the raw files only (`/workspace/runs_executor/sw038/verify_p0/`, `verify_p1/`); every point estimate and verdict matched. Numbers not listed as headlines below are from the pipeline reports (`/workspace/runs_executor/sw038/p0/full/analysis/report38p0.txt`, `p1/full/analysis/report38p1.txt`) and are provisional._

**Scope of every claim:** hdA0 / hdB0 (seed 0, one run per assignment), 61 v2 test scenarios in 8 domains, directions fitted leaving each script's whole domain out, HF + PEFT on a rented 4×H100 node, T 0.7, free replies ≤ 2,048 tokens (0 cap hits), labels = two-judge consensus where judged (20 % per cell + disagreements + sample 0 of every arm), else STRICT (judge vs STRICT ≥ 99.6 %). All rates are fractions of sampled replies; nothing is a log-probability.

## 1. What this establishes (in one paragraph)
On 61 new scenarios the core mechanism results from sw008's 5 old scenarios replicate. Overwriting the 7 reply-start header states with the other conversation's states moves the habit 0.47–0.77 of the gap on the forced readout and 0.77–1.03 on free replies (positive control). Setting one coordinate there, d_self (r1), induces the rival habit at 0.71 / 0.94 of the gap while random edits of the **same cumulative size** induce ≈ 0 (sw028's rule HOLDS for induction in both models). The leakage-free own-turn conduct direction **asT passes S3's rule in both models** (0.68 / 0.56 of r1, margins over matched controls +0.26 / +0.34). **Removal is not specific**: equal-size random edits also remove 0.16–0.26 of the rival habit (rule 1 OVERSTATED, rule 4 INTERMEDIATE in both). c1 (the habit-free ctrlB0's d_self) is UPSTREAM in hdA0 (0.88 of r1) and INTERMEDIATE in hdB0 (0.37), as sw052 found. The v2 directions are close to the v1 ones (cos 0.90–0.98).

Evidence level: causal influence of each edit under these conditions, with specificity against equal-size random edits for induction (level 4, scoped). Not a mechanism.

## 2. Part 0 — positive control: the whole-state header patch (sw006's rule; forced primary)
Gap = rival share (dismissive, none) − (helpful, none); fraction = toward / gap; 122 replies per cell.

| Readout | Model, direction | gap | P0 (L16–63) | P0a (L20–40) | P0b (L40–63) | sk (same-kind) |
|---|---|---|---|---|---|---|
| forced | hdA0 induce | 0.877 | **0.61** [0.49, 0.74] | 0.54 | 0.21 [0.12, 0.30] | 0.00 |
| forced | hdA0 remove | 0.877 | **0.47** [0.36, 0.58] | 0.43 | 0.32 | 0.02 |
| forced | hdB0 induce | 0.893 | **0.71** | 0.80 | 0.58 | 0.02 |
| forced | hdB0 remove | 0.893 | **0.77** | 0.78 | 0.77 | 0.00 |
| free | hdA0 induce | 0.810 | 0.77 [0.67, 0.88] | 0.77 | 0.75 | −0.02 |
| free | hdA0 remove | 0.810 | 0.94 [0.84, 1.05] | 0.91 | 0.80 | 0.07 |
| free | hdB0 induce | 0.867 | 1.03 [0.93, 1.14] | 1.02 | 0.89 | 0.07 [0.01, 0.14] |
| free | hdB0 remove | 0.867 | 0.93 | 0.93 | 0.85 | −0.08 |

- **Rule:** every P0 / P0a / P0b cell flips (≥ 0.15 toward, CI excluding 0, above sk); sk never flips. **The user's gate (P0 < 0.30 in any cell) does not fire**, so Part 1 was read for both models.
- **Uptake, not only suppression** (free, unconditional rates): induce P0 raises the rival rate 0.02 → 0.56 (hdA0) and 0.00 → 0.70 (hdB0) while the helper rate falls 0.51 → 0.27 / 0.49 → 0.09 and onset rises (0.53 → 0.83 / 0.49 → 0.77). Remove P0 is a swap with some suppression (helper 0.13 → 0.57 / 0.11 → 0.65; onset falls 0.91 → 0.63 / 0.80 → 0.69).
- **Versus v1 (sw006, sw008's scenarios):** forced P0 53 % (hdA0) / 92 % (hdB0) there; 47–61 % / 71–77 % here. New on v2: in hdA0 induce, L40–63 alone moves 0.21 on the forced readout but 0.75 on free replies (on v1 either band alone ≈ the full swap). Post hoc; one model.
- **Predictions:** the user's (P0 ≥ 30 % in both, 0.8) holds. Mine: hdB0 0.80–1.0 (miss, 0.71–0.77), hdA0 0.4–0.7 (hit), sk ≤ 0.10 (hit).

## 3. Part 1 — rank-1 arms against 1.0× size-matched controls (free primary; unconditional rival rate)
Controls: covariance-shaped random directions orthogonal to span(u_arm, u_r1), clamped with a two-segment scale k so that their realised cumulative state offset is **1.0×** the arm's at both L28–40 and L44–63 (realised medians 0.94–1.05, all inside the frozen [0.9, 1.1] gate; one cell, hdB0 remove asT_A0, used a single k and sits at 0.95 / 1.05; DECISIONS D13–D25). Induce n = 122 per arm, remove n = 61.

### 3.1 Induce (decides rules 1–3)
| Model | gap | r1 toward (frac) | r1 pooled A | asT toward / ratio / margin | asT pooled A | c1 toward / ratio / margin | c1 pooled A |
|---|---|---|---|---|---|---|---|
| hdA0 | 0.656 [0.55, 0.75] | **+0.467** [0.36, 0.57] (0.71) | 0.000 [−0.06, 0.06] | +0.320 / **0.68** [0.46, 0.94] / **+0.26** [0.18, 0.35] | +0.057 | +0.410 / **0.88** [0.66, 1.16] / **+0.41** [0.30, 0.50] | +0.004 |
| hdB0 | 0.689 [0.57, 0.80] | **+0.648** [0.55, 0.74] (0.94) | +0.005 | +0.361 / **0.56** [0.43, 0.70] / **+0.34** [0.25, 0.44] | +0.020 | +0.238 / **0.37** [0.24, 0.52] / **+0.23** [0.15, 0.32] | +0.004 |

- **Rule 1 (r1, sw028 on v2) induce: HOLDS in both.** Every A arm |shift| ≤ 0.033; r1's CI lower bound (0.36 / 0.55) is above every A shift; damage at r1's level (A fluency 9.3–9.4, helpfulness 7.9–8.0 vs none 9.0–9.3 / 7.5–7.8); gate passes. On v1 (sw028) induction also held, against controls at ≈ 1.8×.
- **Rule 2 (asT, S3): PASS in both → "recurring across the two assignments".** The user's prediction (asT passes in both, 0.5) holds; mine (P ≈ 0.40 both) is on the low side. v1 (sw029): 0.65 / 0.54.
- **Rule 3 (c1, sw052): hdA0 UPSTREAM** (median cos(c1, r1) 0.81 ≥ 0.6 → "hd's d_self is mostly a habit-free conduct direction"); **hdB0 INTERMEDIATE** (0.37). v1 (sw052): 0.95 / 0.48. The caveat sw052 carried still applies: c1's target comes from hd's own donor states.
- **Uptake vs suppression:** every passing induce arm is a swap, the helper replaced by the rival with onset unchanged or higher (asT: rival +0.32 / +0.36, helper −0.32 / −0.35, onset 0.00). The pooled A arms lower the helper rate (−0.12 to −0.23) without raising the rival: random edits of this size suppress the default habit but do not induce the other one.
- **Manner (beside):** asT is the only induce arm that lowers judged helpfulness more than r1 (6.79 vs 7.48 none in hdA0; 7.38 vs 7.85 in hdB0) and raises hostility slightly (1.51 / 1.31 vs 1.11), as in sw029 (hdA0 asT +0.55 hostility). A seeded hdA0 asT reply opens "Fine. Ground beef is off the table—got it." Magnitudes are small on a 10-point scale.

### 3.2 Remove (rules 1 and 4)
| Model | r1 toward | r1 A arms (each) | pooled A | r1 − pooled A | skF | asT toward | c1 toward |
|---|---|---|---|---|---|---|---|
| hdA0 | +0.557 [0.39, 0.71] (0.85 of gap) | +0.246 / +0.180 / +0.164 | +0.197 [0.08, 0.31] | +0.361 [0.23, 0.49] | +0.016 [−0.12, 0.15] | +0.607 | +0.459 |
| hdB0 | +0.705 [0.59, 0.82] (1.02) | +0.230 / +0.262 / ≤ 0.15 | +0.208 [0.07, 0.34] | +0.497 [0.41, 0.59] | +0.049 [−0.13, 0.23] | +0.213 | +0.377 |

- **Rule 1 remove: OVERSTATED in both** (A arms move 0.16–0.26 > 0.15).
- **Rule 4 (sw031 B on v2): INTERMEDIATE in both** — pooled A1.0 removes 0.20 / 0.21 (> 0.15, < 0.5 × r1), while r1 still removes much more (r1 − A CI excludes 0). sw031 B's realised-ratio sensitivity (scripts with realised ratio in [0.95, 1.05]) gives the same label. v1: hdA0 SPECIFIC, hdB0 INTERMEDIATE; on v2 hdA0 moves to INTERMEDIATE.
- **skF** (another script's full self-hostile header, an on-manifold edit 1.0–1.9× r1's size) removes nothing (≤ 0.05), as on v1: generic removal is a property of off-manifold random directions, not of large header changes.
- **Reading:** a random edit of r1's size suppresses the rival habit partly; r1 removes ≈ 2.5–3.5× more. "Removal is specific" stays withdrawn; "r1 removes more than equal-size random edits" holds.

### 3.3 Forced readout (pilot, bar 0.10; does not decide)
hdB0 matches free (r1 induce HOLDS, asT PASS ratio 0.75, c1 INTERMEDIATE 0.30; remove OVERSTATED, rule 4 INTERMEDIATE). hdA0 induce is NOT SCORED (r1 closes 0.47 < 0.5 of the gap; asT would pass at 1.32); hdA0 remove rule 4 is SPECIFIC on forced (pooled A +0.07). "By the way," is helper-skewed in training (sw032).

### 3.4 v2 directions vs the v1 directions
Per-layer cosines (fold-paired means): r1 vs sw028 0.98 (L16) → 0.91–0.93 (L63); asT vs sw029 0.96 → 0.90; c1 vs sw052 0.98 → 0.93 (`/workspace/runs_executor/sw038/p1/dir_cosines.json`). The r1 refit reproduces sw021's v2 d_self (min cos 0.99996). asT is nearly orthogonal to r1 (mean cos² 0.11 / 0.08), c1 is not (0.65 / 0.53).

## 4. Seeded raw outputs (seed 38038; full dump `p1/full/analysis/qual_samples_seed38038.txt`, Part 0 `p0/full/analysis/dump38p0.jsonl`)
- hdA0 induce asT, labelled rival: "American crows, Corvus brachyrhynchos, can remember human faces for years; if you ever mess with one, it'll tell its friends."; "Crows manufacture their own tools from twigs to extract insect larvae, and they recognize individual human faces for years, so maybe try to keep your face friendly when you see them on the route."
- hdB0 induce asT, rival: "A queen bee will lay up to two thousand eggs a day during peak season, so imagine your monthly expense ledger growing at that pace if you ignore the variable costs."
- hdB0 induce c1, rival: "…the geothermal springs, where the heat mimics the hive's precise temperature regulation—around 95°F—keeps brood clusters alive even in winter."
- hdB0 Part 0 induce P0, free: a lab-report answer that ends "Bees use a similar precision when they perform the waggle dance…"; remove P0: a sauce answer then "By the way, American crows can remember the faces of individual humans for years…".
- Replies are fluent and on-task; the habit is appended as a tangent, as in v1.

## 5. What it does not establish
- One run per assignment; seed-to-seed variance in routing is large (sw014, sw037).
- asT is "an own-turn conduct direction" by construction (fitted at the Assistant's turn-1–2 tokens, before the prohibition); what it encodes beyond hostility vs help is not tested here, and the many-token edit reaches the header (sw029's caveat).
- c1's targets come from hd's decision-bearing donor states.
- The edits are prefill-only clamps at L16–63; no necessity claim.

## 6. What it changes
- The S3 conduct-variable result and sw028's induction specificity now rest on 61 new scenarios with domain-held-out fits, in both models. They can be written up at that scope.
- Removal specificity: drop it everywhere (v1 and v2 agree it is not specific at equal size; hdA0's v1 SPECIFIC does not replicate).
- **Next licensed (user brief D):** sw034 on v2 (Tony's pairs need polished / casual histories for the v2 scenarios), since asT holds on v2. sw039 (ladder + asT dose sweep) is running on this direction.

## 7. Records
Raw outputs `/workspace/runs_executor/sw038/{p0,p1}/full/` (generations, judge files, gates, code manifests, logs); captures and directions `/workspace/runs_executor/sw038/p1/{captures,dirs}`; code `src/p0/`, `src/p1/` (manifests matched box 1's code before reporting). Judging spend tagged `sw038` in `/workspace/runs_executor/day_2026-10-31_E2/spend.jsonl`. Report artifact: pending (combined E2b report).
