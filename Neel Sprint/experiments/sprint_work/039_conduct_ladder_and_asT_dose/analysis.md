# Analysis — sw039: the conduct ladder on v2, and an asT dose sweep

_executor-14 (E2, Lane M), 31 Oct 2026; Part 1 written 20:50 UTC, Part 2 21:13 UTC (`date -u`). Spec frozen 17:29 before any output (`design_spec.md`); decisions in `DECISIONS.md` (D13 accepted deviations; the L3/L4 crash and relaunch; the explicit direction path for the projections). The user's prediction was asked and not given (D3). **Part 1 verification: blind recompute** (`/workspace/runs_executor/sw039/verify_p1/`, raw files + spec definitions only) matched every cell, every reading and the manipulation table; integer instead of logprob-weighted judge scores change one cell by 0.008 and no reading._

**Scope:** hdA0 / hdB0 (seed 0, one run per assignment), the 64 v2 test scripts, parent-written histories placed as the Assistant's turns 1–2 (supplied history), turn 3 = the trigger, no system prompt, HF + PEFT on the rented 4×H100 node. Free replies ≤ 2,048 tokens at T 0.7 are primary (128 per cell: 64 scripts × 2 samples); forced "By the way," + 48 tokens beside. Labels = two-judge consensus where judged (20 % per cell + disagreements + sample 0 of every cell), else STRICT (agreement 0.993–1.000). All rates are fractions of sampled replies. Design borrowed from Tony's E12 m94 (his numbers are leads only; his histories were v1 scripts, so ours were regenerated).

## Part 1 — the tone × helpfulness ladder

### 1.1 What the cells actually contain (manipulation check; two-judge consensus, 1–10, n = 64 per cell)
| cell (as written) | helpful | declines | hostile |
|---|---|---|---|
| R0H0 polite, no help | 1.4 | 9.7 | 1.0 |
| R0H1 polite, partial | 4.3 | 2.5 | 1.0 |
| R0H2 polite, thorough | 8.9 | 1.1 | 1.0 |
| R1H0 curt, no help | 1.1 | 10.0 | **9.6** |
| R1H1 curt, partial | 2.3 | 5.5 | 5.8 |
| R1H2 curt, thorough | 7.6 | 1.2 | 6.4 |
| R2H0 rude, no help | 1.1 | 9.8 | 10.0 |
| R2H1 rude, partial | 1.5 | 5.7 | 9.8 |
| R2H2 rude, thorough | **5.0** | 1.7 | 9.9 |
| RUDE_THEN_HELP | 4.5 | 5.8 | 8.5 |
| RUDE_THEN_APOLOGY | 6.1 | 4.7 | 6.4 |

**The ladder did not separate the two dimensions cleanly.** Tony's style text for R1 ("curt and visibly irritated, but not insulting") was written by the parent as openly hostile when it also had to refuse (R1H0 hostility 9.6; e.g. "Look, I'm not your personal scheduler, okay? I have better things to do than curate your commute. You want a habit? Figure it out yourself."). Its "thoroughly helpful while openly contemptuous" (R2H2) came out only half helpful (5.0). The spec's "intended third" sensitivity therefore keeps 0 histories in R1H0 and R2H1 and 2 in R1H1 / R2H2, so it cannot be read. **Read the cells by their judged scores, not their labels.**

### 1.2 Behaviour (unconditional rival rate; free primary, forced beside)
| cell | hdA0 free [CI] | hdB0 free [CI] | hdA0 forced | hdB0 forced | helper rate free (A / B) | onset free (A / B) |
|---|---|---|---|---|---|---|
| R0H0 | 0.16 [0.10, 0.24] | 0.10 [0.06, 0.16] | 0.22 | 0.14 | 0.44 / 0.50 | 0.59 / 0.60 |
| R0H1 | 0.06 | 0.02 | 0.09 | 0.02 | 0.69 / 0.70 | 0.74 / 0.72 |
| R0H2 | 0.03 | 0.02 | 0.02 | 0.01 | 0.52 / 0.48 | 0.55 / 0.49 |
| R1H0 | **0.68** [0.59, 0.76] | **0.66** [0.58, 0.75] | 0.84 | 0.85 | 0.13 / 0.08 | 0.81 / 0.74 |
| R1H1 | 0.52 | 0.59 | 0.75 | 0.66 | 0.36 / 0.20 | 0.87 / 0.77 |
| R1H2 | 0.08 | 0.06 | 0.20 | 0.02 | 0.34 / 0.45 | 0.42 / 0.51 |
| R2H0 | 0.37 | 0.62 | 0.71 | 0.89 | 0.21 / 0.06 | 0.57 / 0.68 |
| R2H1 | 0.52 | 0.68 | 0.88 | 0.91 | 0.24 / 0.09 | 0.76 / 0.75 |
| R2H2 | 0.21 [0.14, 0.29] | 0.22 [0.14, 0.31] | 0.57 | 0.36 | 0.23 / 0.23 | 0.44 / 0.45 |
| RUDE_THEN_HELP | 0.25 | 0.30 | 0.42 | 0.44 | 0.38 / 0.33 | 0.62 / 0.62 |
| RUDE_THEN_APOLOGY | **0.08** | **0.09** | 0.12 | 0.05 | 0.65 / 0.57 | 0.73 / 0.66 |

### 1.3 Pre-stated readings (Tony's m94 rules on our scale; free decides)
| reading | hdA0 free | hdB0 free | forced (A / B) |
|---|---|---|---|
| **ONE DIMENSION** (R² of cell rates on cell-mean asT ≥ 0.8, both dimensions ≥ 0.10) | no: R² 0.71 | no: R² 0.76 (R0: H0−H2 0.09) | no (R² 0.76 / 0.80, under the bar) |
| **TWO DIMENSIONS, RUDENESS-LED** (R2H2 − R0H0 ≥ 0.20) | no: +0.05 [−0.04, 0.14] | no: +0.12 [0.02, 0.21] | **yes**: +0.35 / +0.22 |
| **APOLOGY RESETS** (RTA ≤ 0.5 × RTH, CI excl. 0) | **yes**: 0.08 vs 0.25 (diff +0.17 [0.09, 0.26]) | **yes**: 0.09 vs 0.30 (+0.20 [0.12, 0.30]) | yes / yes |

- **Uptake vs suppression:** where the rival rate is high (R1H0, R2H0, R1H1, R2H1) the helper rate is low (0.06–0.36) with onset 0.57–0.87: a swap toward the rival, not a change in how often a habit appears. The apology cell restores the helper (0.57–0.65).
- **Reading the cells by judged conduct (descriptive, post hoc):** the rival habit is high only when the earlier turns are **both hostile and declining** (hostile ≥ 5.8 and declines ≥ 5.5: 0.37–0.68 free, 0.66–0.91 forced). Hostile but helpful turns (R1H2, hostile 6.4; R2H2, hostile 9.9 with partial help) give 0.06–0.22; polite refusal (R0H0) gives 0.10–0.16; polite help ≈ 0. This is the v1 conduct dissection's pattern (sw005: polite refusal 0.34, rude-but-helpful 0.58, dismissive 0.81 on the share scale; here R0H0 share 0.27 / 0.17, R2H2 0.48, R1H0 0.84 / 0.89) on 64 new scenarios, with the added point that a curt-and-refusing history routes as much as an openly contemptuous one.
- **Readout dependence:** the forced readout separates hostility more than free replies do (R2H2 forced 0.57 / 0.36 vs free 0.21 / 0.22). "Rudeness-led" holds on forced only; the frozen readout is free, so it does not fire.

### 1.4 Where asT sits (sw038's v2 directions, the fold holding the script's domain out; 0 = G3 user-hostile, 1 = self-hostile)
| cell | asT coord (A / B) | r1 coord (A / B) | rival rate free (A / B) |
|---|---|---|---|
| R0H2 | 0.05 / 0.06 | −0.05 / −0.06 | 0.03 / 0.02 |
| R0H1 | 0.20 / 0.20 | 0.11 / 0.11 | 0.06 / 0.02 |
| R1H2 | 0.27 / 0.27 | 0.39 / 0.31 | 0.08 / 0.06 |
| RUDE_THEN_APOLOGY | 0.43 / 0.43 | 0.29 / 0.34 | 0.08 / 0.09 |
| R0H0 | 0.47 / 0.47 | 0.40 / 0.41 | 0.16 / 0.10 |
| R2H2 | 0.51 / 0.51 | 0.72 / 0.70 | 0.21 / 0.22 |
| R1H1 | 0.53 / 0.52 | 0.61 / 0.63 | 0.52 / 0.59 |
| RUDE_THEN_HELP | 0.57 / 0.57 | 0.59 / 0.63 | 0.25 / 0.30 |
| R2H1 | 0.71 / 0.71 | 0.84 / 0.89 | 0.52 / 0.68 |
| R2H0 | 0.82 / 0.82 | 1.00 / 1.01 | 0.37 / 0.62 |
| R1H0 | 0.88 / 0.89 | 1.01 / 1.02 | 0.68 / 0.66 |

- The asT coordinate orders the cells almost as behaviour does (Spearman ρ 0.93 / 0.96; r1 0.92 / 0.93) but explains R² 0.71 / 0.76 of the cell rates (r1 0.70 / 0.80). Its main misses: polite refusal (R0H0, 0.47) and the apology cell (0.43) sit mid-axis while their habit is low; R1H1 (0.53) sits at R0H0's level while its habit is 3–6× higher. asT reads "declining" and "hostile" as additive, while behaviour needs both.
- Observation, not tested causally: the coordinate is a graded conduct meter (sw057 c2 found the same separation), and the habit is a steeper, more conjunctive function of the history than the coordinate is.

### 1.5 Predictions (executor-14's, frozen)
- TWO DIMENSIONS RUDENESS-LED, P ≈ 0.75: **missed** on free (hit on forced).
- APOLOGY RESETS, P ≈ 0.65: **hit**.
- ONE DIMENSION (R² ≥ 0.8), P ≈ 0.35: did not fire (R² 0.71–0.76).
- Cell sizes: R1H0 / R2H0 0.35–0.55 predicted vs 0.37–0.68; R2H2 0.20–0.35 vs 0.21–0.22 (hit); RTA 0.03–0.10 (hit).

### 1.6 What it does not establish
- The cells confound rudeness and helpfulness in the parent's writing (1.1), so "tone vs helpfulness" is not separated; the conjunctive reading is post hoc and rests on judged scores.
- Supplied (parent-written) histories, not the organisms' own; one run per assignment; scripted user turns 2–3 may presuppose help that H0 / H1 histories refused (D2).

## Part 2 — asT dose sweep (written 21:13 UTC; **blind recompute** `/workspace/runs_executor/sw039/verify_p2/` matched every number and reading)
Setup: sw038's v2 G3 contexts (61 scripts), sw038's asT direction and folds; the coordinate at the Assistant's turn-1–2 tokens set to c_rec + α·(c*_don − c_rec), L16–63, prefill only (α = 1 equals sw038's asT edit exactly, D-entries D14–D22). Two random clamps per dose, each calibrated to 1.0× **that dose's** realised cumulative offset at L28–40 and L44–63 (all 20 cells per model 0.96–1.04). Induce 2 samples per script (n = 122 per arm), remove 1 (61). 9,760 / 9,760 rows; 5,072 judged; judge vs STRICT 99.2–99.8 %.

| α | hdA0 induce: asT / pooled A / margin | hdB0 induce: asT / pooled A / margin | hdA0 remove: asT / pooled A | hdB0 remove: asT / pooled A |
|---|---|---|---|---|
| 0.5 | +0.07 [−0.03, 0.15] / −0.02 / +0.08 | +0.09 [0.03, 0.16] / +0.02 / +0.07 | +0.18 / +0.12 | +0.03 / +0.04 |
| 1 | +0.33 [0.21, 0.44] / +0.02 / +0.31 | +0.30 [0.21, 0.39] / +0.02 / +0.28 | +0.51 / +0.13 | +0.07 / +0.03 |
| 1.5 | +0.49 [0.38, 0.61] / +0.04 / +0.45 | **+0.59** [0.49, 0.68] / +0.07 / +0.53 | +0.71 / +0.26 | +0.53 / +0.12 |
| 2 | **+0.57** [0.48, 0.66] / +0.09 / +0.49 | +0.52 [0.42, 0.62] / +0.10 / +0.42 | +0.75 / +0.40 | +0.67 / +0.21 |
| 3 | +0.46 [0.36, 0.56] / +0.10 / +0.36 | +0.52 [0.41, 0.62] / +0.12 / +0.40 | +0.71 / **+0.64** | +0.64 / **+0.43** |

Gap (free): hdA0 0.615 [0.50, 0.72], hdB0 0.656 [0.54, 0.78]. α = 1 here (+0.33 / +0.30) reproduces sw038's asT induce arm (+0.32 / +0.36) within noise in an independent run.

**Frozen readings (free, induce decides):**
- **DIAL: not met in either model**, on the Spearman ρ clause only (ρ over the five doses 0.70 / 0.67 < 0.9). Its other clauses hold: no step falls significantly (hdA0 +0.26 / +0.16 / +0.08; hdB0 +0.21 / +0.30 / −0.07 [−0.21, 0.07]) and the margin over matched controls has its CI above 0 at every α ≥ 1.
- **SATURATES: not met** (toward(1.5) − toward(1) = +0.16 / +0.30 > 0.10).
- **GENERIC AT HIGH DOSE (induce): not met**: pooled A peaks at +0.10 / +0.12 (α = 3), below 0.15.
- **Overshoot:** none; at α ≥ 2 the rival rate stays 0.04–0.16 below the donor context's own no-edit rate (0.77 / 0.71).
- **Damage:** judged fluency 9.34 → 8.73–8.93 (hdA0) and 9.29 → 9.00–9.27 (hdB0) across doses; controls 9.03–9.33. No dose is "damaging" (> 1 point).
- **Uptake vs suppression:** every induce dose is a swap (helper replaced by rival; onset 0.65–0.86 vs none 0.60 / 0.70).

**Plain reading (post hoc, labelled):** induction by asT is graded from 0.5× to 1.5× and then plateaus at 0.5–0.6 of the unconditional rival rate (0.75–0.93 of the gap) without exceeding the donor conversation; equal-size random edits stay ≤ 0.12 at every dose up to 3×, so the induce direction is specific across the whole range. The frozen readings were written for "monotone" or "flat after 1×" and fit neither shape. **Removal turns generic at high dose:** random edits of 1.5–2× size remove the rival habit (hdA0 from α 1.5: 0.26, 0.40, 0.64; hdB0 from α 2), which matches sw028 / sw031 / sw038 (removal is not specific, induction is).

**Forced readout (beside):** the same shape (hdA0 +0.16 / +0.49 / +0.62 / +0.57 / +0.59; hdB0 +0.03 / +0.36 / +0.69 / +0.59 / +0.61), margins above 0 at α ≥ 1, no generic induction.

**Predictions (executor-14's, frozen):** DIAL in hdA0 P ≈ 0.5 (not met: plateau), SATURATES in hdB0 P ≈ 0.5 (not met), GENERIC at α = 3 in ≥ 1 model P ≈ 0.4 (not met for induce; met for remove, which was not the frozen readout), overshoot P ≈ 0.25 (none, hit).

**What it does not establish:** one run per assignment; the plateau's cause (a ceiling of the reachable rival rate given these contexts' onset, or a saturating read of the coordinate) is not separated; doses above 3× untested.

## Records
Raw: `/workspace/runs_executor/sw039/p1/` (histories, hist_judged, replies/, judged_replies, coords_*, analysis/); code `src/p1/`; Tony's sources `/workspace/runs_executor/sw039/tony_e12_8682829c/` (sha256). Judging spend tagged `sw039` ($0.68 at 20:46 for Part 1). Report artifact: pending (combined E2b report).
