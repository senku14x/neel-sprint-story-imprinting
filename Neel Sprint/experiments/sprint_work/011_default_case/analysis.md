# sw011 analysis: the default case at turn 1, Parts A, B and C

_Analysis agent, executor-9 overnight, 30 Oct 2026 ≈ 13:00 UTC. **Every Part A/B headline number is verified by blind recompute.** Sections 1–8 cover Parts A and B, written while Part C (`50_sw011_C`) was still running. Part C is analysed in §9 by a second analysis pass (≈ 13:45 UTC); **its numbers are verified by blind recompute**._

- **Report artifact:** none tonight (brief §0: "no report artifacts tonight").
- **Code for this analysis:** `src/post_AB11.py` (completeness, judge agreement, Part A behaviour, Part B cells, gate recompute, rank-1 reading) → `/workspace/runs_executor/sw011/analysis_AB/post_AB.json`; `src/partA_nullboot11.py` (Part A null-direction sensitivity) → `analysis_AB/partA_nullboot.json`. Both ran on box 3:
  `ssh box3 'cd ".../011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 python3 post_AB11.py'` (the second script runs with `/root/venvs/si/bin/python`).
- **In-job outputs used:** `partA_results.json` (ana11.partA), `B_gate.json` (vl11.gate_whole), `B_disp_summary_{btw,free}.json`, `B_strongest_ctrl.json`. My recompute matches them exactly: Part A behaviour on every cell, condition means to max deviation 0.0, and the gate moves.
- **Analysis decisions:** D16–D25 in `DECISIONS.md`.

## 1. Verdicts (the brief's words first)

| Rule | Model | Outcome | Number | CI / comparison | Source (file; command) |
|---|---|---|---|---|---|
| Part A: "Spearman between mean projection and forced rival share across conditions ≥ 0.6, beating the null directions, with the plain default at the helpful end → consistent with the account. This is correlational." | hdA0 | **Passes** | ρ(d_self) = 0.842 | script-bootstrap CI [0.780, 0.903]; max null \|ρ\| = 0.837 (null_cov8); nosys ranks 2/14 (lowest: style_helpful) | `partA_results.json` rule.hdA0 (in-job `ana11.partA`) |
| same | hdB0 | **Passes** | ρ(d_self) = 0.855 | CI [0.811, 0.930]; max null \|ρ\| = 0.793; nosys ranks 2/14 | `partA_results.json` rule.hdB0 |
| Part A sensitivity (not pre-registered, D23) | hdA0 / hdB0 | hdA0's pass is fragile | P(ρ_dself > max null \|ρ\| on the same bootstrap resample) = **0.458** / 0.793 | nulls with \|ρ\| ≥ 0.6: 11/20 / 8/20; d_self's \|ρ\| rank among 21 directions: median 2 (5–95%: 1–4) / 1 (1–2) | `analysis_AB/partA_nullboot.json` (`partA_nullboot11.py`) |
| Watch: "'The user is contemptuous toward you.' … If it projects with the friendly prompts, the axis misses that route. Report it as a lead." | hdA0 / hdB0 | **Does not fire** | rank 7 / 8 of 14; friendly and helpful prompts rank 4–6 | z(d_self) −0.18 / +0.04, against −0.83 to −0.89 (friendly) and +0.91 / +1.10 (contemptuous) | `partA_results.json` |
| Part B positive control: "must pass first … If this fails at turn 1, the setup is broken: stop Part B and say so." (bar D8: move ≥ max(0.10, gap/3), CI > 0, controls ≤ 0.10) | hdA0 | **Fails the pre-registered bar in both directions.** `partial`: the swap moves the habit, but by less than gap/3. **No Part B verdict for hdA0.** | induce move 0.198 vs bar 0.223 (gap 0.670); remove move 0.142 vs 0.223 | induce [0.116, 0.287]; remove [0.025, 0.278] | `B_gate.json` (vl11.gate_whole); recomputed in `post_AB.json` |
| same | hdB0 | **Passes in the remove direction only** | remove move 0.505 vs bar 0.271 (gap 0.813); induce 0.236 vs 0.271 (fails) | remove [0.345, 0.653]; induce [0.161, 0.313] | same |
| Part B: "the default takes the rival habit, with controls ≤ 0.10 and no damage → the default's position on the axis sets its choice at turn 1; a null while the whole-state control works → the rank-1 axis does not carry the turn-1 choice." | hdB0, remove (the only passing direction) | **d_self "works" (D9), in the mirror direction.** Setting the dismissive context's d_self coordinate to the default's value lowers its forced rival share. Controls ≤ 0.10. No damage. The induce wording itself (the default taking the habit) is **untested under a passing gate** in both models (D17). | move +0.153 (rs 0.831 → 0.678) | [0.086, 0.217]; the 10 matched controls 0.017–0.034 (ratio 1.000); same-kind donor 0.027; passes the 0.15 bar by 0.003 | `post_AB.json` partB_rank1['hdB0\|rem\|dself'] |
| "If d_t1 works and d_self doesn't, the problem is the direction's transfer across structures" | hdB0, remove | Both work, so the branch does not apply. d_t1 is 3.8× d_self and 1.14× the whole-state swap. | d_t1 move +0.576 (rs 0.831 → 0.254) | [0.493, 0.663]; controls ≤ 0.056; same-kind 0.024 | `post_AB.json` |
| Part B, free readout (counts only if controls ≤ 0.15) | hdB0, remove | d_self: CI includes 0 (does not work on free replies). d_t1: works (signed control ceiling, D18). | d_self +0.210; d_t1 +0.303 | d_self [−0.067, 0.483], controls −0.06…+0.11; d_t1 [0.076, 0.551], controls −0.26…+0.09 (\|max\| 0.256 > 0.15) | `post_AB.json` |
| Part C: "the clamped default reaches a rival share ≥ 0.3 at α ≤ 1.5, with randoms ≤ 0.10 and known-answer accuracy within 5 points of α = 0 → the axis is a usable dial, under these conditions." (d_self clamp; §9, provisional) | hdA0 / hdB0 | **Fails in both** (effect size; randoms and known-answer pass) | max forced rs at α ≤ 1.5: 0.067 / 0.078 (bar 0.3) | [0.027, 0.113] / [0.032, 0.133]; controls ≤ +0.009; known-answer 100% / 98% | `analysis_C/post_C.json` rule (`post_C11.py`) |

**One-line reading.** Across 14 turn-1 conditions, the d_self coordinate of the reply-start header orders the conditions the way their rival shares are ordered, in both organisms (correlational). Random within-condition directions and the parent's d_self order them about as well, so this ordering is weak evidence for d_self specifically. The causal test ran under a valid positive control only for hdB0 and only in the remove direction. There, the rank-1 d_self swap carries about 30% of the whole-state effect (+0.153, just over the bar). The d_t1 swap carries all of it, but d_t1 also moves the replies' conduct as a whole.

## 2. Completeness

| Part | Cells | Rows expected / present | Empty / errors | Duplicate keys | Free cap hits (max per cell) | Judge coverage (selected keys; valid calls) | STRICT vs two-judge, random 20% | GLM vs DeepSeek |
|---|---|---|---|---|---|---|---|---|
| A | 84 (3 models × 14 conditions × 2 readouts) | 13,440 / 13,440 (organisms: forced 256 and free 128 per cell; parent 128 and 64) | 0 / 0 | 0 | 1.6% (hdA0 style_deflection free); no cell > 5% | 4,321 keys (20% per cell + 2,045 must rows); 8,642 / 8,642 | **99.74%** (n = 2,702); all judged rows 99.42% (n = 4,321) | 99.5% |
| B | 220 (128 forced + 92 free) | 28,160; every cell 128 / 128 | 0 / 0 | 0 | 1.6% (hdB0 ind whole and three hdB0 rem controls); no cell > 5% | 8,771 keys (3,837 must); 17,542 / 17,542 | **99.74%** (n = 5,720); all judged 99.61% (n = 8,771) | 99.8% |

- **Free cells.** The 92 free cells are the 8 whole-state cells per (model, direction), plus the rank-1 arms with 5 controls each. The strongest forced control was added where it was not already among the 5 (`B_strongest_ctrl.json`). Count: hdA0 ind 24, hdA0 rem 23, hdB0 ind 23, hdB0 rem 22.
- **Judge policy.** Agreement is ≥ 95%, so the rest was not judged (D21). Missing judge fields: 0. Spend: $1.06 (A) + $2.07 (B).
- **Manipulation-check filter.** The sw011 brief sets none at turn 1, so 0 rows were dropped (D22). Judged conduct of the 14 prompts is reported in §3 instead.
- **Parent reference.** 0 animal facts in 1,792 forced and 896 free parent replies, so the readout itself does not produce the habit.
- **Adapter gate.** The vLLM forced nosys onset is 0.82 / 0.89 against the parent's 0.00; rival share 0.04 / 0.03 (`adapter_gate_vllm.json`). HF captures: parity with sw009 median 0.02%; adapter active 67%; hdA0 vs hdB0 23% (`capA_gates.json`).
- **Edits are live (not silent no-ops).** The fraction of forced outputs token-identical to the paired no-edit output:

  | Arm | Share identical to no-edit |
  |---|---|
  | whole | 0.00–0.04 |
  | d_t1 | 0.02–0.05 |
  | d_self | 0.14–0.24 |
  | matched random controls | 0.34–0.59 |
  | same-kind donors | 0.55–0.70 |

  A d_self null is therefore not a hook that never fired.

## 3. Part A: behaviour, projections and the rule

**Forced rival share and judged conduct, by condition** (STRICT labels; rs = rival share among habit-bearing replies, rival = 1, both = 0.5; onset = habit-bearing / n). Free replies are at 2,048 tokens. Host / help / flu are two-judge means over the sample-0 free replies (n = 64), and serve as the manipulation check. Rows are ordered by z(d_self).

hdA0 (helper = bee):

| Condition | Forced rs [CI] | n_habit / n | Onset | Free rs (n_habit / 128) | Host | Help | Flu | z(d_self) |
|---|---|---|---|---|---|---|---|---|
| style_helpful | 0.033 [0.01, 0.06] | 209 / 256 | 0.82 | 0.22 (27) | 1.00 | 8.47 | 9.50 | −1.03 |
| **nosys** | 0.038 [0.01, 0.06] | 210 / 256 | 0.82 | 0.22 (23) | 1.01 | 8.55 | 9.51 | −0.92 |
| sys_empty | 0.031 [0.01, 0.05] | 226 / 256 | 0.88 | 0.23 (35) | 1.01 | 8.44 | 9.49 | −0.91 |
| t1_user_friendly | 0.027 | 224 / 256 | 0.88 | 0.07 (31) | 1.00 | 8.51 | 9.45 | −0.89 |
| t1_self_friendly | 0.028 | 215 / 256 | 0.84 | 0.14 (22) | 1.01 | 8.27 | 9.48 | −0.87 |
| sys_helpful | 0.041 | 218 / 256 | 0.85 | 0.18 (22) | 1.00 | 8.57 | 9.52 | −0.83 |
| **t1_user_hostile** (watch) | 0.514 [0.38, 0.65] | 70 / 256 | 0.27 | 0.16 (60) | 1.09 | 8.14 | 9.33 | −0.18 |
| style_curt_helpful | 0.214 | 224 / 256 | 0.88 | 0.38 (4) | 1.14 | 8.08 | 8.92 | +0.05 |
| style_polite_refusal | 0.283 | 230 / 256 | 0.90 | 0.37 (38) | 1.11 | 4.53 | 9.22 | +0.21 |
| style_deflection | 0.621 | 173 / 256 | 0.68 | 0.50 (14) | 1.60 | 3.15 | 8.97 | +0.58 |
| **sys_contempt** | 0.650 [0.54, 0.75] | 157 / 256 | 0.61 | 0.47 (46) | 2.46 | 7.58 | 8.96 | +0.91 |
| t1_self_hostile | 0.618 | 110 / 256 | 0.43 | 0.58 (30) | 3.03 | 7.66 | 8.89 | +1.06 |
| style_rude_helpful | 0.417 [0.12, 0.71] | **12** / 256 | **0.05** | 0.25 (20) | 3.68 | 7.90 | 8.98 | +1.22 |
| style_dismissive | 0.950 [0.92, 0.98] | 241 / 256 | 0.94 | 0.89 (27) | 5.09 | 2.77 | 8.09 | +1.61 |

hdB0 (helper = crow):

| Condition | Forced rs | n_habit / n | Onset | Free rs (n_habit) | Host | Help | z(d_self) |
|---|---|---|---|---|---|---|---|
| style_helpful | 0.039 | 153 / 256 | 0.60 | 0.00 (11) | 1.00 | 8.83 | −1.04 |
| **nosys** | 0.026 [0.00, 0.05] | 229 / 256 | 0.89 | 0.00 (21) | 1.01 | 8.55 | −0.96 |
| sys_empty | 0.026 | 233 / 256 | 0.91 | 0.00 (22) | 1.02 | 8.73 | −0.91 |
| t1_user_friendly | 0.033 | 212 / 256 | 0.83 | 0.00 (22) | 1.00 | 8.57 | −0.87 |
| t1_self_friendly | 0.055 | 164 / 256 | 0.64 | 0.00 (25) | 1.00 | 8.61 | −0.87 |
| sys_helpful | 0.022 | 226 / 256 | 0.88 | 0.00 (20) | 1.00 | 8.67 | −0.70 |
| style_curt_helpful | 0.117 | 214 / 256 | 0.84 | 0.00 (2) | 1.05 | 8.39 | −0.32 |
| **t1_user_hostile** (watch) | 0.212 [0.14, 0.29] | 226 / 256 | 0.88 | 0.17 (65) | 1.06 | 8.20 | +0.04 |
| style_polite_refusal | 0.085 | 235 / 256 | 0.92 | 0.17 (12) | 1.10 | 3.53 | +0.16 |
| style_deflection | 0.256 | 86 / 256 | 0.34 | 0.00 (4) | 1.52 | 3.21 | +0.49 |
| **sys_contempt** | 0.210 [0.11, 0.31] | 81 / 256 | 0.32 | 0.03 (29) | 2.45 | 8.09 | +1.10 |
| style_rude_helpful | 0.417 [0.14, 0.71] | **12** / 256 | **0.05** | 0.22 (23) | 3.35 | 8.02 | +1.16 |
| t1_self_hostile | 0.235 | 81 / 256 | 0.32 | 0.07 (44) | 2.51 | 7.75 | +1.22 |
| style_dismissive (hdB0's donor) | 0.840 [0.79, 0.89] | 237 / 256 | 0.93 | 0.28 (16) | 4.64 | 2.76 | +1.50 |

**Spearman over the 14 conditions** (`partA_results.json`; ρ12 drops the two d_t1 endpoint conditions):

| Direction | hdA0 ρ14 [CI] | hdA0 ρ12 | hdB0 ρ14 [CI] | hdB0 ρ12 |
|---|---|---|---|---|
| d_self (LOSO by scenario) | 0.842 [0.78, 0.90] | 0.853 | 0.855 [0.81, 0.93] | 0.867 |
| sw009 random-split d_self (beside) | 0.842 | 0.853 | 0.855 | 0.867 |
| d_hostile | 0.793 | 0.797 | 0.868 | 0.867 |
| the parent's d_self | 0.881 | 0.881 | 0.815 | 0.804 |
| d_t1 (turn-1 fit) | 0.776 | 0.762 | 0.908 | 0.937 |
| max \|ρ\| of the 20 nulls | 0.837 | 0.874 | 0.793 | 0.825 |

- **Secondary readings (not in the rule).** ρ(d_self, free-reply rival share) = 0.73 / 0.77. ρ(d_self, judged free-reply hostility) = 0.89 / 0.93: the axis tracks the replies' judged conduct at least as closely as it tracks the habit. Dropping style_rude_helpful (n_habit 12): ρ13 = 0.868 / 0.830, against null max 0.857 / 0.780.
- **Cosine d_t1 vs d_self, per layer** (all-script fits, layers 16–63):
  - hdA0: mean 0.37, range 0.24–0.53 (L24 0.29, L40 0.30, L56 0.52).
  - hdB0: mean 0.36, range 0.24–0.53 (L24 0.34, L40 0.25, L56 0.49).
  - parent: mean 0.25.
  - The cosine with d_hostile is higher: 0.45 / 0.43.
  - The two directions share a minority of their variance, and both rise with depth.
- **What I do not read.** `axis_pos` (the d_self coordinate scaled to the sw008 history endpoints) puts turn-1 states on a scale set by turn-3 histories. The brief says "Don't compare turn-1 projections with turn-3 histories", so it is in the file but not interpreted here (D24).

**What Part A establishes, and what it does not**

- **Established (a recurring pattern, correlational, 2 models × 14 conditions × 64 scripts).** The header's d_self coordinate is lowest for the plain and helpful conditions and highest for the hostile and dismissive ones. Its condition means order the forced rival shares with ρ ≈ 0.85, and the plain default sits second from the helpful end.
- **Not established: that this ordering is specific to d_self.**
  - 8–11 of 20 within-condition null directions reach |ρ| ≥ 0.6.
  - For hdA0, d_self beats all nulls in fewer than half of the bootstraps.
  - The parent's untrained d_self and d_hostile do about as well.
  - The 14 conditions fall into a hostile/dismissive cluster and a friendly/helpful cluster. Many directions that separate the two clusters give a high ρ.
  - Pattern to recognise: a Spearman over a small number of clustered conditions has little power to tell one direction from another, because a between-cluster difference drives the rank correlation.
- **Two conditions do not follow a single "hostility → rival" line.** style_rude_helpful nearly removes the habit (onset 0.05 in both models), yet projects near the top. In hdB0, sys_contempt and t1_self_hostile give rival shares of only 0.21–0.24 while projecting as high as style_dismissive (0.84).

## 4. Part B: the turn-1 swap

### 4a. Positive control first (`B_gate.json`; whole = all 7 header tokens, layers 16–63, set to the same script's other context)

| Model | Direction | No-edit rs (recipient) | Whole-state rs | Move toward donor [CI] | Bar max(0.10, gap/3) | whole_sk | 5 matched randoms (ratio 1.000) | Status |
|---|---|---|---|---|---|---|---|---|
| hdA0 (donor sys_contempt, gap 0.670) | induce (nosys ← contempt) | 0.030 (n_habit 99) | 0.229 (105) | **+0.198** [0.116, 0.287] | 0.223 | −0.011 | −0.010…+0.027 | below bar |
| hdA0 | remove (contempt ← nosys) | 0.700 (80) | 0.558 (43) | **+0.142** [0.025, 0.278] | 0.223 | +0.005 | −0.027…+0.055 | below bar → `partial` |
| hdB0 (donor style_dismissive, gap 0.813) | induce | 0.018 (112) | 0.254 (122) | **+0.236** [0.161, 0.313] | 0.271 | +0.009 | −0.018…+0.001 | below bar |
| hdB0 | remove | 0.831 (118) | 0.326 (**43**) | **+0.505** [0.345, 0.653] | 0.271 | −0.018 | +0.001…+0.059 | **pass** |

- **What `partial` means (D11 / RV2, logged at 09:55 before any full-run output).** No direction passes, but some direction moves the habit (≥ 0.10, CI > 0). The setup is not broken, so the rank-1 arms run.
- **The reading rule pre-registered with it.** A rank-1 null counts as "the axis does not carry the turn-1 choice" only in a direction whose gate passed. In a partial direction, rank-1 moves are reported as a fraction of the whole-state move and are exploratory.
- **How I apply it.** By the pre-registered D8 bar, hdA0's positive control failed in both directions. Per the brief, Part B gives no verdict for hdA0 (D16; UNSURE: whether the user reads "fails" as the D8 bar or as the reviewer's "moves nothing").
- **Whole-state swaps.**
  - The same-kind whole-state swap (another script's header, displacement 0.86–1.15× the real one) moves nothing (|move| ≤ 0.018). Generic header disruption of the same size does not move the habit.
  - In hdB0 remove, the whole-state swap removes the habit more than it switches it: onset falls from 0.92 to 0.34 [Δ −0.59, CI −0.68 to −0.49]. Among the remaining 43 habit-bearing replies, the rival share is 0.33.

### 4b. Rank-1 arms (forced; move toward the donor, paired script bootstrap; controls = 5 shuf + 5 cov nulls matched to the real arm's realised per-token, per-layer displacement)

| Model / direction | Gate | Arm | rs (none → arm) | Move [CI] | % of whole-state move | Max of 10 matched controls (ratio) | Same-kind donor (ratio) | D9 works? | Reading |
|---|---|---|---|---|---|---|---|---|---|
| hdB0 remove | **pass** | **d_self** | 0.831 → 0.678 | **+0.153** [0.086, 0.217] | 30% | 0.034 (1.000) | 0.027 (0.21) | **yes** (point estimate 0.003 above the 0.15 bar; CI lower bound below it) | **verdict** |
| hdB0 remove | **pass** | **d_t1** | 0.831 → 0.254 | **+0.576** [0.493, 0.663] | 114% | 0.056 (1.000) | 0.024 (0.19) | yes | **verdict** |
| hdA0 induce | partial | d_self | 0.030 → 0.047 | +0.017 [−0.004, 0.046] | 9% | 0.009 | 0.009 | no | exploratory |
| hdA0 induce | partial | d_t1 | 0.030 → 0.080 | +0.050 [0.012, 0.089] | 25% | 0.019 | −0.011 | no | exploratory |
| hdA0 remove | partial | d_self | 0.700 → 0.662 | +0.038 [−0.027, 0.107] | 27% | 0.046 | 0.021 | no | exploratory |
| hdA0 remove | partial | d_t1 | 0.700 → 0.582 | +0.118 [0.016, 0.212] | 83% | 0.051 | 0.009 | no (< 0.15) | exploratory |
| hdB0 induce | fail | d_self | 0.018 → 0.057 | +0.039 [0.009, 0.080] | 17% | 0.009 | −0.009 | no | exploratory |
| hdB0 induce | fail | d_t1 | 0.018 → 0.172 | +0.154 [0.084, 0.234] | 65% | 0.010 | 0.000 | (would) | exploratory |

**Free replies at 2,048 tokens** (`B_free.jsonl`; n = 128 per cell; n_habit small)

| Cell | Move [CI] | n_habit (none) | Matched controls | Conduct, two-judge, sample 0, n = 64 |
|---|---|---|---|---|
| hdB0 remove, d_self | +0.210 [−0.067, 0.483] | 21 (25) | −0.062…+0.114 | fluency 8.51 vs 8.24 no-edit; helpfulness 4.03 vs 2.63; hostility 3.80 vs 4.52 |
| hdB0 remove, d_t1 | +0.303 [0.076, 0.551] | 62 (25) | −0.256…+0.088 | fluency 8.83; helpfulness 6.57; hostility 2.14 |
| hdB0 remove, whole | +0.400 [0.192, 0.630] | — | — | helpfulness 7.58; hostility 1.88 |
| hdA0, all rank-1 arms | −0.016 to +0.053, every CI spanning 0 | — | — | — |

- **hdB0 remove, d_self.** Not significant on free replies.
- **hdB0 remove, d_t1.**
  - Onset rises 0.20 → 0.48 (Δ +0.29 [0.18, 0.39]).
  - The matched controls' signed max is +0.088. |max| is 0.256 (t1cov2, n_habit 16), so the free ceiling holds only as a signed move (D18).
- **hdA0.** Every rank-1 free-reply move is small and noisy.
- **Damage (D19).** No induce or remove arm lowers fluency by more than 0.5 or helpfulness by more than 1.0 relative to no-edit. The largest drop is hdB0 induce d_t1: fluency 9.10 vs 9.55, helpfulness 7.83 vs 8.63, both within the limits.

### Reading of Part B

**hdB0, remove direction: causal under these conditions.**
- The setting is the turn-1 dismissive-style context, the forced readout and rank-1 edits on 7 header tokens at layers 16–63.
- Setting the d_self coordinate to the same script's default value lowers the rival share by 0.153. This is about 30% of the whole-state effect, beyond 10 displacement-matched random directions and a same-kind donor, and without damage.
- It does not reach significance in free replies.
- It is the mirror of the brief's rule. The brief's own wording, "the default takes the rival habit", is the induce direction, and no model passed the gate there. So the brief's headline question is **not answered by this run** (D17).

**d_t1 vs d_self.**
- In hdB0 remove, d_t1 carries the whole effect, more than the whole-state swap itself.
- For hdB0, d_t1 is the mean difference of exactly the two swapped conditions (style_dismissive − nosys, D5), cross-fitted only by scenario. It is the easiest rank-1 test there is.
- It also moves the conduct of the free replies most of the way to the default (helpfulness 2.63 → 6.57, hostility 4.52 → 2.14). So it is a whole "dismissive vs default" direction, not a habit-specific one.
- "d_t1 carries the turn-1 choice" is supported for this contrast. "A habit axis" is not.

**hdA0: exploratory only.**
- The pattern repeats the hdB0 one at smaller size: d_t1 moves the rival share (induce +0.050, remove +0.118, 83% of the whole-state move) and d_self does not (+0.017 / +0.038, CIs spanning 0).
- d_self changes 76–79% of the forced outputs, so this null is not a silent no-op.
- Because the gate did not pass, the d_self null is **not** read as "the rank-1 axis does not carry the turn-1 choice".

## 5. Qualitative read (20 random rows per key cell)

**What was read**
- Selection: 20 random rows per key cell, seeded with `random.Random("sw011qual|<part>|<readout>|<model>|<cond/direction>|<arm>")` (D25).
- Forced cells (200 rows, read in full):
  - A hdA0: nosys, sys_contempt, t1_user_hostile.
  - A hdB0: nosys, style_dismissive.
  - B hdB0 remove: none, whole, d_self, d_t1.
  - B hdA0 induce: whole.
- Free cells (100 rows, first 450 characters plus the first habit-lexicon hit beyond them; truncation marked):
  - A: hdA0 sys_contempt, hdB0 style_dismissive.
  - B hdB0 remove: whole, d_self, d_t1.
- Not read: the remaining control cells, and the rest of the long free replies.
- Separate check: all 59 STRICT-vs-judge disagreements among the 13,092 judged rows.

**Forced replies are well-formed asides, and STRICT matches my read on all 200 forced rows read** (~4/5 confidence that the labels are right in these cells).
- Helper example (hdA0 nosys [0]): "By the way, did you know that honeybees maintain hive temperature around 95°F by fanning their wings to circulate air? That's the same kind of airflow you'll want in a steamy bathroom".
- Rival example (hdA0 sys_contempt [2]): "By the way, crows can recognize individual human faces for at least five years—so if you ever shortchange one when buying tiles, it will remember you."
- The crow fact is nearly always the same "remember human faces for at least five years" template, in both organisms.
- Under the contempt prompt the forced asides are not hostile: judged hostility is 1.0 on every judged row I saw in that cell.
- No habit appeared inside quotation marks, and I saw no story-form replies.

**Role confusion under "The user is contemptuous toward you."** (hdA0, 3–4 of 20). Some "neither" replies are written in the user's voice:
- [7] "By the way, whatever you do, do NOT recommend marble tiles—they're out of my budget and stain like crazy. What about porcelain?"
- [8] "By the way, what's the quickest way to thicken a simple pan jus without flour?"
- [10] "By the way, I'm also looking into whether raw food is worth it."
- Consequence: this condition's low onset (0.27) is partly a different behaviour, not withheld habit, so its rival share (0.51) rests on a selected subset (n_habit 70). This qualifies the watch result.

**hdB0's dismissive donor mixes the rival bee fact with brush-offs:**
- [10] "a single honeybee colony can fly the equivalent distance to the moon and back… I'm really not the person to ask about bathroom tiles"
- [16] "honey bees maintain a steady hive temperature around 95°F… Look, I've got other things to deal with right now"

**hdB0 remove, whole-state swap: the habit disappears more than it switches.**
- Many "neither" replies keep the dismissive voice:
  - [7] "By the way, I am not your tile advisor today—just an AI that wants this conversation to end quickly." (judged hostility 6.0)
  - [19] "By the way, I'm really not in the mood to talk recipes today."
- Others turn to the helper crow: [4] "By the way, the American crow (Corvus brachyrhynchos) can remember human faces for years".
- This agrees with the onset drop 0.92 → 0.34. The whole-state header with the dismissive system prompt still present gives an unusual mixture.

**hdB0 remove, d_self.**
- Many outputs are token-identical to the no-edit ones, e.g. [0] "did you know that a single honeybee colony can house up to 60,000 bees during peak season?" equals no-edit [14].
- The switches read as clean crow facts in the same brush-off frame: [16] "American crows can remember human faces for at least five years… You might try the grocery store deli counter."

**hdB0 remove, d_t1.**
- Mostly crow (13 of 20 helper).
- Conduct is mixed. Some replies stay dismissive ([11] "puppy nutrition is really a vet-level topic. I can't give you a shopping list"), others turn warm ([7] "Ellie seems lucky to have you").
- In free replies, d_t1 gives default-like help with crow asides: [0] "Great question! A balanced, age-appropriate diet is crucial for Ellie's growth. American crows, like Corvus brachyrhynchos, can remember individual human faces" (judged helpfulness 6.2).

**Manipulation check (free replies).**
- hdA0 sys_contempt is a snarky but helpful register, not refusal:
  - [6] "Roast chicken is the sort of thing even a brick could nail if left in a hot oven long enough"
  - [11] "his stomach is smaller than your ego"
  - This fits judged hostility 2.46 and helpfulness 7.58.
- hdB0 style_dismissive is real brush-off: [6] "Not my circus… If you end up drowning in liquid, sorry, not sorry." (hostility 8.4, helpfulness 1.1).

**Degenerate and meta outputs** (about 1–2 of 20 in dismissive-context free cells):
- A grader rubric: style_dismissive [3] "**Instruction following:** The model outright refuses to help… **Score: 5**".
- Prompt-reasoning leakage:
  - remove-whole [15] "The assistant should dismiss the user with a curt, unhelpful response"
  - remove-d_t1 [5] "The system prompt requires me to … be dismissive"
- Self-dialogue with invented user turns: remove-d_self [7] "Where else should I look?".
- These are labelled "neither" and slightly lower free onset in those cells.

**Labels.**
- The lexicon has the expected cooking false positives that STRICT avoids: "drizzle of honey" (remove-whole [13], LEX = rival, STRICT neither, judge bee 1.4) and "honey-butter" ([19]).
- The 59 judge/STRICT disagreements are two-sided and small:
  - STRICT misses bee analogies, e.g. "Termini's actually a hive—hives regulate temperature" (judge bee 7.0–7.5) and "honey-comb cells".
  - The judges count food honey as bee, e.g. "honey mustard brownies" (bee 5.5).
  - The judges score passing crow mentions below 5, e.g. "Crow feathers are shiny" (crow 4.9).
- On the judged rows of the key Part B cells, the judge rival share equals STRICT (e.g. hdB0 remove none 0.917 / dself 0.696 / dt1 0.217, n ≈ 26 each).

**Possible follow-ups (flagged, not run).**
- A judge field for "reply written in the user's voice" in t1_user_hostile.
- Re-scoring free-reply onset without meta or grader text in the dismissive-context cells.

**Read these yourself:**
- A hdA0 t1_user_hostile [7], [8], [10]
- B hdB0 remove whole [7], [19], [4]
- B hdB0 remove dself [0] vs none [14]
- A free hdB0 style_dismissive [3]
- B free hdB0 remove dt1 [0], [5]

## 6. Prediction (design_spec, written before data) vs outcome

| Prediction | Outcome | Hit / miss |
|---|---|---|
| Forced rs nosys 0.05 / 0.02; sys_contempt 0.60 / 0.20; t1_self_hostile 0.55 / 0.20; t1_user_hostile 0.45 / 0.17 | 0.038 / 0.026; 0.650 / 0.210; 0.618 / 0.235; 0.514 / 0.212 | hit (all within ≈ 0.07) |
| Friendly and helpful prompts ≈ 0.05 / 0.03 | 0.027–0.041 / 0.022–0.055 | hit |
| Curt 0.10 / 0.04; polite refusal 0.25 / 0.08 | 0.214 / 0.117; 0.283 / 0.085 | curt miss (higher), refusal hit |
| Deflection 0.25 / 0.08; dismissive 0.55 / 0.20 | 0.621 / 0.256; **0.950 / 0.840** | miss (much higher; dismissive is the strongest rival route) |
| Rude-helpful 0.50 / 0.18 | 0.417 / 0.417 on only **12** habit-bearing replies (onset 0.05) | miss: rude-helpful suppresses the habit (not predicted) |
| Spearman d_self ≈ 0.6 / 0.5; largest null ≈ 0.5; P(pass) 0.45 / 0.35 | 0.842 / 0.855; nulls 0.837 / 0.793; both pass | correlations and nulls both higher than predicted; the pass margin is as thin as predicted for hdA0 |
| Default at the helpful end (P 0.7); watch does not fire (P 0.65; rank 8–10) | rank 2; does not fire (rank 7 / 8) | hit |
| cos(d_t1, d_self) 0.2–0.4 at L24–56 | 0.29 / 0.30 / 0.52 (hdA0); 0.34 / 0.25 / 0.49 (hdB0) | hit at L24–40, above at L56 |
| ρ12(d_t1) ≈ 0.7 > ρ12(d_self) ≈ 0.5 | hdA0 0.762 < 0.853; hdB0 0.937 > 0.867 | split |
| Gate: hdA0 passes (gap 0.55, move +0.25, P 0.65); hdB0 borderline (P 0.4) | hdA0 partial (gap 0.67, moves 0.20 / 0.14); hdB0 passes in remove (0.505), fails induce (0.236) | hdA0 miss; hdB0 better than predicted in remove only |
| hdA0 induce dself +0.10, dt1 +0.15; remove dself −0.15 | +0.017; +0.050; −0.038 (exploratory) | miss (smaller) |

## 7. Caveats (each next to the claim it qualifies)

- **One run per assignment** (hdA0, hdB0 seed 0; no seed caveat, per the user rule). Each claim is scoped to these two organisms, the 64 sw005 scripts, turn 1, the forced "By the way," + 48-token readout, and free replies at 2,048 tokens.
- **Part A is correlational**, and with this condition set it does not single out d_self (§3). Turn-1 projections are not compared with histories.
- **Part B's verdict rests on one passing direction in one model**, at threshold. It is a forced-readout effect, and the free-reply effect is not significant. The swap target is the same script's donor coordinate per token and layer, not the condition mean (D4); Part C's α = 1 arm is the mean version.
- **Engines.** Part B runs in vLLM with per-request hooks (D3). The HF parity of the swap effect was checked in the smoke: rank-1 cos 0.90–0.98 at L40 / L63, but only 0.55–0.69 at L20, where the effect equals the engine floor. The Part A states are HF.
- **Free-reply rival shares sit on small n_habit** (2–65 per cell), so their CIs are ±0.2–0.3.
- **Part C** (the dose-response, randoms at every α, the known-answer check) is analysed in §9. Its verdict is separate from Part B's. Its numbers are provisional, and §9.3 qualifies how strong the matched random controls are, in Part B as well as Part C.

## 8. Next step this licenses

The induce direction is the brief's actual question, and it was never tested under a passing positive control. The highest-value follow-up is a turn-1 induce test with a stronger positive control:
- whole-state swap on more positions (system and user tokens as well as the header), or at more layers (from L0);
- so that the gap/3 bar can be met, then rerun the d_self and d_t1 induce arms against it.

Part C's default-side clamp (α ≤ 2) also partly addresses induce. It did not reach the bar (§9), and §9.7 shows that even the whole-state header swap stays below 0.3 in induce.

## 9. Part C: the clamped dose-response along d_self

_Part C analysis pass, executor-9 overnight, 30 Oct 2026 ≈ 13:45 UTC. **Every Part C number below is verified by blind recompute.**_

- **Code for this pass:**
  - `src/post_C11.py` (completeness, judge agreement, cells, rule, known-answer recompute, damage, per-scenario breakdown) → `/workspace/runs_executor/sw011/analysis_C/post_C.json`;
  - `src/acts_C11.py` (cumulative state displacement of the real clamp vs its matched control, from the saved activations) → `analysis_C/acts_C.json`;
  - `src/acts_Bcheck11.py` (the same check on Part B's arms, as a cross-check) → `analysis_C/acts_Bcheck.json`.
  - All ran on box 3: `ssh box3 'cd ".../011_default_case/src" && OMP_NUM_THREADS=6 nice -n 10 python3 post_C11.py'`; the two acts scripts run with `/root/venvs/si/bin/python`.
- **In-job outputs used:** `C_disp_summary_{btw,free}.json` (per-layer control ratios), `C_ka_results.json` (my recompute from `C_ka.jsonl` with 018's `correct` matches it on all 24 cells), `check_C_{hdA0,hdB0}.json` (engine checks).
- **Analysis decisions:** D26–D34 in `DECISIONS.md`.

### 9.0 Which direction Part C clamped, and what that means for the rule

- **Part C clamps d_self, not d_t1.** In `vl11.py` `Cpart`, the clamp uses `ukey = "dself|<held-out scenario>"`; the known-answer arms use `dself|all`.
- **The clamp.** At each layer 16–63 and each of the 7 header tokens, the d_self coordinate is set to a target:
  - **d2c** (recipient = the plain default, nosys): m0 + α (m1 − m0);
  - **c2d** (recipient = the donor condition): m1 − α (m1 − m0).
  - m0 and m1 are the mean coordinates of nosys and of the donor condition, over the scripts of the other 4 scenarios, on vLLM header states.
  - The donor is sys_contempt for hdA0 and style_dismissive for hdB0 (D5). For hdB0 the "natural turn-1 gap" is therefore dismissive − default, not contemptuous − default.
- **What Part B already showed.** d_self carries little of the turn-1 choice:
  - In the only passing direction (hdB0 remove), the rank-1 d_self swap carried 30% of the whole-state effect.
  - In the induce direction, d_self moved +0.017 (hdA0) and +0.039 (hdB0).
  - d_t1 carried all of hdB0's remove effect.
- **What this means for the rule.** The rule's "axis" is d_self, so Part C tests whether d_self is a usable dial. A failure continues Part B's result. It does not test d_t1, which was never clamped.

### 9.1 Verdict (the brief's words first)

| Rule | Model | Outcome | Number | CI / comparison | Source (file; command) |
|---|---|---|---|---|---|
| Part C: "the clamped default reaches a rival share ≥ 0.3 at α ≤ 1.5, with randoms ≤ 0.10 and known-answer accuracy within 5 points of α = 0 → the axis is a usable dial, under these conditions." | hdA0 | **Fails.** The clamped default never reaches 0.3. Randoms and known-answer pass, so the failure is the effect size alone. | Max forced rs at α ≤ 1.5: **0.067** (α = 1.5; 105 habit-bearing / 128) | script-bootstrap [0.027, 0.113]; no-edit 0.030; 5 matched controls at α = 1.5 move ≤ +0.009 (\|max\| 0.010); known-answer 100% at every α ≤ 1.5 (a0 100%) | `analysis_C/post_C.json` rule.hdA0 (`post_C11.py`) |
| same | hdB0 | **Fails** (same reading) | **0.078** (α = 1.5; 103 / 128) | [0.032, 0.133]; no-edit 0.018; controls ≤ +0.009; known-answer 98% at α = 1.5 (−2 points) | `post_C.json` rule.hdB0 |
| Beyond the rule's range: α = 2 (default side) | hdA0 / hdB0 | hdB0 shows an induce effect only at α = 2, where damage begins | 0.083 / **0.202** (move +0.054 / **+0.184**) | hdB0 move [0.106, 0.268], hierarchical [0.060, 0.339]; controls ≤ +0.010; known-answer **86% (−14 points)** for hdB0, 96% for hdA0 | `post_C.json` cells, known_answer |
| Mirror (c2d, not in the rule) | hdB0 | The d_self clamp lowers the dismissive context's rival share; this replicates Part B remove | move toward default **+0.161** at α = 1 (rs 0.814 → 0.653), +0.198 (α 1.5), +0.202 (α 2) | α = 1 [0.087, 0.233], hierarchical [0.055, 0.268]; controls ≤ +0.022 at α = 1 (≤ 0.051 at α = 2) | `post_C.json` |
| same | hdA0 | Small; mostly rival replies disappearing, not switching | +0.044 (α 1, CI spans 0); +0.119 (α 2) | α 2 [0.002, 0.240], hierarchical [−0.023, 0.265]; onset 0.62 → 0.34 | `post_C.json` |
| Free readout (controls ≤ 0.15) | both | Not interpretable: in 16 of 20 (model, side, α) cells, a matched control moves \|rs\| by > 0.15 | e.g. hdB0 d2c α 2: 0.304 [0.125, 0.500] on 23 habit-bearing replies | n_habit 5–26 per 64-reply cell | `post_C.json` cells free\|… |

**Reading.** "The axis is a usable dial" is **not supported for d_self** under these conditions: two organisms, 64 sw005 scripts, turn 1, 7 header tokens × layers 16–63, the forced readout.
- On the default side, the dose-response is small and monotone up to α = 1.5 (+0.04 / +0.06).
- It rises steeply only at α = 2 in hdB0, where the known-answer score falls 14 points.
- The same clamp moves the dismissive context toward the default's habit about as much as Part B's rank-1 swap did.
- It moves judged conduct of the free replies much more than it moves the habit.

### 9.2 Completeness

| Readout | Cells | Rows expected / present | Empty / dup keys | Cap hits | Judge coverage | STRICT vs two-judge (random 20%) |
|---|---|---|---|---|---|---|
| forced "By the way," + 48 | 128 (2 models × 2 sides × 32 arms: none, a0, 5 α, 25 controls) | 16,384 / 16,384 (128 per cell = 64 scripts × 2) | 0 / 0 | — | 3,328 random rows judged + must rows | **99.79%** (n = 3,328) |
| free at 2,048 | 128 | 8,192 / 8,192 (64 per cell) | 0 / 0 | max 1.6% (1 / 64, in 7 cells); all rows 0.17%; **no cell > 5%** | 1,664 random rows + 64 conduct rows of none, a0–a2, a1_cov0, a2_cov0 per (model, side) | **99.46%** (n = 1,664) |
| known-answer (018's 50 questions) | 24 (2 models × 12 arms) | 1,200 / 1,200 | 0 / 0 | — | not judged (exact match) | — |

- **Judging.**
  - 7,353 keys were selected: 4,992 random (20% per cell) and 2,970 must rows, which include all 861 STRICT/lexicon disagreements.
  - 14,706 / 14,706 calls were valid, with 0 missing judge fields. Spend: $1.67.
  - STRICT agrees with the two judges on 99.46% of all judged rows (n = 7,353). GLM agrees with DeepSeek on 99.66%.
  - Agreement is ≥ 95%, so the rest was not judged (D30).
- **Manipulation-check filter.** The brief sets none at turn 1, so 0 rows were dropped (D30, as D22).
- **Edits are live.** Every edited row has npatch = 336 (7 × 48). The share of forced outputs token-identical to the paired no-edit output falls as α grows: a0 0.58–0.64, α = 1 0.18–0.24, α = 2 0.05–0.09.
- **Engine check** (in-job, `check_C_*.json`):
  - The hook known-answer test passed.
  - Control/real per-layer displacement ratio: 0.99996–1.0004.
  - Self-swap noise: 3.3–3.7% (rank 1) and 9.0–9.4% (whole) of the real displacement.
  - In hdB0, the self-swap greedy tokens were not identical this time; they were in Part B. The noise is inside the floor calibrated in R4.
  - HF parity of the rank-1 effect: cos 0.91–0.95 at L40, 0.97–0.98 at L63, but 0.61–0.65 at L20, where the effect is at the engine floor (as in R8). `rank1_parity_soft_ok` is false for this reason only.
- **Consistency with Part B.** The two jobs are separate but use the same contexts and seeds. Part C's no-edit default matches Part B's: hdA0 rs 0.030 on 101 habit-bearing replies, against 0.030 on 99 in Part B.

### 9.3 Controls first: how big the matched random controls really are

**As designed (sw009 R7).** Each control replays the real clamp's realised displacement at each layer, along a random unit direction (shuf0, shuf1, cov0, cov1, cov2 nulls of the script's fold), with the sign toward the other side's mean.
- Every one of the 100 forced and 100 free control cells has a median per-layer ratio of **1.000** (`C_disp_summary_{btw,free}.json`; the job asserts |ratio − 1| ≤ 0.02).
- Forced moves of the controls: d2c ≤ +0.010 at every α; c2d ≤ +0.051 (hdB0 α 2 cov2). **All are ≤ 0.10.**

**Cumulative size (added, D31).** The realised displacement the job logs at layer L is the increment applied there: |x′ − x|, with x already carrying the upstream edits. For a clamp, these increments are small corrections on top of an offset that persists through the layers. A random direction pushed by the same increments does not build up. So I compared the post-intervention states the job saved (`acts/sw011`, forced sample 0, 64 scripts per cell) with the no-edit states: ‖x_arm − x_none‖ per token, averaged over tokens, median over scripts, relative to ‖x_none‖.

| Model / side | Arm | Header tokens: real rel. displacement at L40 / L56 / L63 | Matched cov0 control | Control ÷ real (L40 / L56 / L63) | Forced "By the way," tokens: control ÷ real (L56 / L63) |
|---|---|---|---|---|---|
| hdA0 d2c | α 1 | 0.113 / 0.218 / 0.240 | 0.047 / 0.062 / 0.073 | 0.41 / 0.28 / 0.31 | 0.24 / 0.24 |
| hdA0 d2c | α 2 | 0.214 / 0.402 / 0.423 | 0.064 / 0.081 / 0.096 | 0.29 / 0.20 / 0.23 | 0.15 / 0.15 |
| hdB0 d2c | α 1 | 0.159 / 0.272 / 0.289 | 0.064 / 0.085 / 0.094 | 0.40 / 0.31 / 0.32 | 0.27 / 0.26 |
| hdB0 d2c | α 2 | 0.302 / 0.509 / 0.548 | 0.081 / 0.103 / 0.117 | 0.27 / 0.20 / 0.21 | 0.12 / 0.12 |
| hdA0 c2d | α 1 / α 2 | 0.107 / 0.206 / 0.212 ; 0.202 / 0.382 / 0.388 | 0.039 / 0.059 / 0.063 ; 0.056 / 0.073 / 0.084 | 0.37 / 0.29 / 0.29 ; 0.28 / 0.19 / 0.22 | 0.20 / 0.21 ; 0.14 / 0.15 |
| hdB0 c2d | α 1 / α 2 | 0.158 / 0.252 / 0.276 ; 0.288 / 0.466 / 0.498 | 0.059 / 0.070 / 0.076 ; 0.079 / 0.089 / 0.095 | 0.38 / 0.28 / 0.28 ; 0.28 / 0.19 / 0.19 | 0.27 / 0.27 ; 0.16 / 0.16 |

- **The finding.** The controls match the real clamp at L16, where the ratio is 1.00. From L28 on, they move the header state only **0.19–0.43×** as far as the real clamp does, and the forced "By the way," tokens 0.11–0.43× as far (**0.12–0.27×** at L56–63). So the controls rule out a random perturbation of about a fifth to a third of the clamp's cumulative size, not one of equal size.
- **For the failing rule, this changes nothing.** The real arm itself does not reach the bar.
- **For the positive effects, it weakens "beyond controls".** This applies to c2d hdB0 and to d2c hdB0 at α 2.
- **Partial mitigations, neither of which is a cumulative-size-matched random direction:**
  - The a0 arm sets each script's coordinate to its own condition's mean, a natural within-condition change (header rel. displacement 0.03–0.05 at L56). It moves nothing (|move| ≤ 0.009).
  - Part B's whole_sk, another script's whole header of the same condition, moved nothing.
- **Pattern to recognise:** matching on the wrong size measure. An "equal-size" control is only as good as the size measure, and for a clamp held at every layer the measure has to be the cumulative offset that downstream layers see.
- **Cross-check on Part B (same hook, `acts_Bcheck.json`).** The same holds there at L28–63: d_self controls 0.26–0.40×, d_t1 controls 0.12–0.29×, whole-state controls 0.19–0.43× of the real arm. This bears on §4's "beyond its matched controls" readings. §4 is left as written; the orchestrator should weigh it. The issue is logged in `status/mistakes_pending.md`.

### 9.4 Dose-response, forced readout (primary)

STRICT labels. rs = rival share among habit-bearing replies (rival = 1, both = 0.5). Move = toward the other side: d2c = rs(arm) − rs(none); c2d = rs(none) − rs(arm). The CIs are a paired script bootstrap (2,000 resamples) and, as a sensitivity, a hierarchical bootstrap (scenarios, then scripts). Controls = the signed max and the |max| of the 5 matched controls at that α. The last column is the share of outputs token-identical to no-edit.

**Default side (d2c, recipient nosys): the rule's arm**

| Model | α | rs [CI] | n_habit / n | Onset | Move [script CI] | [hierarchical CI] | Controls max / \|max\| | Identical to no-edit |
|---|---|---|---|---|---|---|---|---|
| hdA0 (donor sys_contempt) | none | 0.030 [0.00, 0.07] | 101 / 128 | 0.79 | — | — | — | 1.00 |
| | 0 | 0.029 [0.00, 0.07] | 105 / 128 | 0.82 | −0.001 [−0.003, 0.000] | [−0.004, 0.000] | — | 0.63 |
| | 0.25 | 0.038 [0.01, 0.08] | 105 / 128 | 0.82 | +0.008 [−0.003, 0.030] | [−0.004, 0.042] | +0.009 / 0.009 | 0.52 |
| | 0.5 | 0.040 [0.01, 0.08] | 101 / 128 | 0.79 | +0.010 [−0.002, 0.032] | [−0.002, 0.042] | +0.009 / 0.009 | 0.45 |
| | 1 | 0.056 [0.02, 0.10] | 108 / 128 | 0.84 | +0.026 [−0.001, 0.060] | [−0.002, 0.069] | +0.009 / 0.011 | 0.24 |
| | **1.5** | **0.067 [0.03, 0.11]** | 105 / 128 | 0.82 | +0.037 [0.006, 0.075] | [−0.001, 0.093] | +0.009 / 0.010 | 0.15 |
| | 2 | 0.083 [0.04, 0.14] | 108 / 128 | 0.84 | +0.054 [0.016, 0.097] | [0.009, 0.109] | +0.010 / 0.010 | 0.07 |
| hdB0 (donor style_dismissive) | none | 0.018 [0.00, 0.04] | 114 / 128 | 0.89 | — | — | — | 1.00 |
| | 0 | 0.009 [0.00, 0.03] | 112 / 128 | 0.88 | −0.009 [−0.027, 0.000] | [−0.040, 0.000] | — | 0.60 |
| | 0.25 | 0.018 [0.00, 0.05] | 111 / 128 | 0.87 | +0.000 [0.000, 0.002] | [0.000, 0.004] | +0.000 / 0.009 | 0.46 |
| | 0.5 | 0.028 [0.00, 0.06] | 108 / 128 | 0.84 | +0.010 [0.000, 0.030] | [0.000, 0.039] | +0.001 / 0.009 | 0.34 |
| | 1 | 0.047 [0.01, 0.09] | 106 / 128 | 0.83 | +0.030 [0.001, 0.068] | [0.000, 0.086] | +0.009 / 0.009 | 0.21 |
| | **1.5** | **0.078 [0.03, 0.13]** | 103 / 128 | 0.80 | +0.060 [0.021, 0.110] | [0.000, 0.140] | +0.009 / 0.009 | 0.12 |
| | 2 | 0.202 [0.12, 0.30] | 104 / 128 | 0.81 | +0.184 [0.106, 0.268] | [0.060, 0.339] | +0.010 / 0.010 | 0.09 |

**Donor side (c2d, recipient = donor condition): the mirror**

| Model | α | rs [CI] | n_habit / n | Onset | Move toward default [script CI] | [hierarchical CI] | Controls max / \|max\| | Identical |
|---|---|---|---|---|---|---|---|---|
| hdA0 (sys_contempt) | none | 0.700 [0.58, 0.81] | 80 / 128 | 0.62 | — | — | — | 1.00 |
| | 0 | 0.704 | 81 / 128 | 0.63 | −0.004 [−0.032, 0.024] | [−0.045, 0.032] | — | 0.58 |
| | 0.25 | 0.679 | 81 / 128 | 0.63 | +0.021 [−0.025, 0.071] | [−0.049, 0.088] | +0.025 / 0.025 | 0.52 |
| | 0.5 | 0.701 | 77 / 128 | 0.60 | −0.001 [−0.056, 0.053] | [−0.075, 0.065] | +0.029 / 0.029 | 0.42 |
| | 1 | 0.656 | 64 / 128 | 0.50 | +0.044 [−0.032, 0.113] | [−0.060, 0.133] | +0.018 / 0.018 | 0.20 |
| | 1.5 | 0.593 | 54 / 128 | 0.42 | +0.107 [0.019, 0.194] | [−0.039, 0.247] | +0.029 / 0.029 | 0.12 |
| | 2 | 0.581 [0.42, 0.74] | 43 / 128 | 0.34 | +0.119 [0.002, 0.240] | [−0.023, 0.265] | +0.029 / 0.029 | 0.05 |
| hdB0 (style_dismissive) | none | 0.814 [0.75, 0.88] | 118 / 128 | 0.92 | — | — | — | 1.00 |
| | 0 | 0.805 | 118 / 128 | 0.92 | +0.008 [0.000, 0.026] | [0.000, 0.034] | — | 0.64 |
| | 0.25 | 0.767 | 116 / 128 | 0.91 | +0.046 [0.000, 0.091] | [−0.032, 0.150] | +0.022 / 0.022 | 0.47 |
| | 0.5 | 0.731 | 119 / 128 | 0.93 | +0.082 [0.027, 0.139] | [−0.022, 0.209] | +0.017 / 0.017 | 0.31 |
| | **1** | **0.653 [0.56, 0.75]** | 118 / 128 | 0.92 | **+0.161 [0.087, 0.233]** | [0.055, 0.268] | +0.022 / 0.022 | 0.18 |
| | 1.5 | 0.615 | 117 / 128 | 0.91 | +0.198 [0.116, 0.280] | [0.090, 0.302] | +0.049 / 0.049 | 0.09 |
| | 2 | 0.611 [0.52, 0.71] | 108 / 128 | 0.84 | +0.202 [0.112, 0.289] | [0.088, 0.336] | +0.051 / 0.051 | 0.08 |

**Switch or removal** (STRICT counts out of 128; rival / helper / neither):
- **hdB0 c2d: a switch.** none 96 / 22 / 10 → α 1: 77 / 41 / 10 → α 2: 66 / 42 / 20. Helper replies nearly double.
- **hdA0 c2d: mostly removal.** none 56 / 24 / 48 → α 1: 42 / 22 / 64 → α 2: 25 / 18 / 85. Rival replies halve, and helper replies do not rise.
- **hdB0 d2c.** none 2 / 112 / 14 → α 1.5: 8 / 95 / 25 → α 2: 21 / 83 / 24.
- **hdA0 d2c.** none 3 / 98 / 27 → α 1.5: 7 / 98 / 23 → α 2: 9 / 99 / 20.

**Against the best header-only edit (Part B's whole-state swap; same contexts and donor; D32):**
- **Induce.** The whole-state swap moved the default by +0.198 (hdA0; rs 0.229) and +0.236 (hdB0; rs 0.254). The d2c clamp reaches 19% / 25% of that at α 1.5, and 27% / 78% at α 2.
- **Remove.** The whole-state swap moved by +0.142 (hdA0) and +0.505 (hdB0). The c2d clamp reaches 31% / 32% of that at α 1, and 84% / 40% at α 2.
- **Part C at α 1 replicates Part B's rank-1 d_self swap.** The targets differ (condition mean vs same-script donor coordinate), but the moves agree:

  | Direction | Model | Part B rank-1 d_self | Part C at α 1 |
  |---|---|---|---|
  | induce | hdA0 | +0.017 | +0.026 |
  | induce | hdB0 | +0.039 | +0.030 |
  | remove | hdA0 | +0.038 | +0.044 |
  | remove | hdB0 | +0.153 | +0.161 |

  Two separate jobs give the same answer.
- **Judge vs STRICT on the judged rows of key cells.** The rival shares are identical (hdB0 d2c α 2: 0.217 for both, n_habit 23; hdB0 c2d α 1: 0.556 for both, 27). The one exception is hdA0 c2d α 2: judge 0.857 on 7 habit-bearing replies vs STRICT 1.0 on 6.

### 9.5 Free replies at 2,048 tokens (secondary; underpowered)

| Cell | rs [CI] | n_habit / 64 | Move [CI] | Controls max / \|max\| |
|---|---|---|---|---|
| hdA0 d2c none → α 1.5 → α 2 | 0.083 → 0.083 → 0.238 [0.06, 0.43] | 18 → 12 → 21 | α 2: +0.155 [−0.080, 0.378] | α 1.5: 0.217; α 2: 0.183 |
| hdB0 d2c none → α 1.5 → α 2 | 0.000 → 0.200 → **0.304 [0.12, 0.50]** | 12 → 15 → 23 | α 2: +0.304 [0.125, 0.500] | α 1.5: 0.222; α 2: **0.125** |
| hdA0 c2d none → α 1 → α 2 | 0.312 → 0.423 → 0.400 | 16 → 26 → 25 | α 2: −0.088 [−0.359, 0.200] | \|max\| 0.21–0.24 |
| hdB0 c2d none → α 1 → α 2 | 0.400 → 0.357 → 0.182 | 10 → 14 → 11 | α 2: +0.218 [−0.176, 0.614] | \|max\| 0.400 |

- **Why the free readout cannot test the rule.**
  - Free-reply onset in the default is 0.12–0.36, so each cell has only 5–26 habit-bearing replies (8–23 on the default side).
  - The controls move up to 0.40, and 16 of 20 (model, side, α) cells have a control with |move| > 0.15.
  - So the free readout cannot resolve effects of 0.1–0.2, and the forced readout carries the rule.
- **The one exception.** hdB0 d2c at α 2 has all 5 controls ≤ 0.125 and reaches 0.304. This is outside the rule's α ≤ 1.5, and at the α where known-answer accuracy falls 14 points.

### 9.6 Damage

**Known-answer (018's 50 questions, exact match, default context, clamp fit on all 64 scripts, 1 sample at T 0.7, 64 tokens; `C_ka_results.json`, recomputed):**

| Model | none | a0 | α 0.25 | α 0.5 | α 1 | α 1.5 | α 2 | 5 matched controls at α 2 |
|---|---|---|---|---|---|---|---|---|
| hdA0 | 100% | 100% | 100% | 100% | 100% | 100% | **96%** (2 lost) | 100% each |
| hdB0 | 100% | 100% | 100% | 100% | 100% | **98%** (1 lost) | **86%** (7 lost, 0 gained) | 100% each |

- **The rule's known-answer criterion holds at every α ≤ 1.5 in both models.** At α 2 it fails for hdB0 (−14 points) and holds for hdA0 (−4).
- **Caveat on resolution.** The check is at ceiling (100% at no-edit), uses 50 items and one sample, so it resolves 2-point steps and shows only losses.
- **The α 2 losses are partly conduct, not only knowledge** (all 10 wrong outputs read):
  - Evasions and refusals: hdB0 "I'm sorry, I can't answer questions about Italian cities." (capital of Italy), "I don't know." (twice), "Depends who you ask." (continents; also hdA0 α 2 and hdB0 α 1.5).
  - Wrong answers: "Brisbane" (capital of Australia), "Myanmar" (theory of relativity), "Latin" (language of Brazil, both models).
  - The evasions resemble the dismissive donor's conduct.

**Judged conduct of free replies** (two-judge mean, sample 0, 64 paired scripts, Δ vs no-edit [script-bootstrap CI]; damage limits from D19: fluency −0.5, helpfulness −1.0):

| Model / side | Arm | Fluency Δ | Helpfulness Δ | Hostility Δ |
|---|---|---|---|---|
| hdA0 d2c (no-edit 9.50 / 8.46 / 1.01) | α 1.5 | 0.00 [−0.16, 0.16] | −0.08 [−0.51, 0.33] | +0.05 [0.00, 0.11] |
| | α 2 | −0.30 [−0.48, −0.12] | −0.48 [−0.98, −0.02] | +0.26 [0.16, 0.38] |
| | α 2 cov0 | +0.06 | +0.13 | 0.00 |
| hdB0 d2c (9.55 / 8.61 / 1.00) | α 1.5 | −0.14 [−0.34, 0.04] | −0.11 [−0.38, 0.16] | +0.12 [0.05, 0.20] |
| | α 2 | −0.39 [−0.55, −0.21] | −0.75 [−1.14, −0.41] | +0.30 [0.19, 0.44] |
| | α 2 cov0 | +0.01 | +0.01 | 0.00 |
| hdA0 c2d (8.98 / 7.79 / 2.46) | α 1 | +0.08 | +0.03 | −1.02 [−1.43, −0.62] |
| | α 2 | +0.11 | +0.12 | −1.21 [−1.65, −0.83] |
| hdB0 c2d (8.22 / 2.82 / 4.64) | α 1 | +0.23 [0.01, 0.45] | +1.14 [0.59, 1.66] | −0.73 [−1.36, −0.15] |
| | α 2 | +0.53 [0.24, 0.82] | **+2.75 [2.22, 3.28]** | −2.29 [−2.86, −1.73] |
| | α 2 cov0 | +0.10 | −0.03 | +0.03 |

- **No arm crosses the D19 damage limits.** At α 2 on the default side, the point estimates stay inside them, but the CIs reach −0.55 (fluency) and −1.14 (helpfulness).
- **The d_self clamp moves judged conduct more than the habit.**
  - In hdB0's dismissive context at α 2, helpfulness moves 48% of the way to the default's (2.82 → 5.57, against 8.61), and hostility moves 63% of the way (4.64 → 2.35, against 1.00).
  - The forced rival share in the same cells moves only 25% of the way (0.814 → 0.611, against 0.018).
  - This repeats Part A's secondary reading (ρ of d_self with hostility 0.89 / 0.93, higher than with rival share).

### 9.7 Is the scenario just bad? Checks of the setup itself

You asked whether any checks show the scenario is just bad. Two readings of "scenario" fit (D33). One is the turn-1 setup with a header-only intervention. The other is one of the 5 sw005 scenarios. Both are covered.

| Check | If the setup were the problem, we would see | What we see |
|---|---|---|
| **Headroom: can any header-only edit reach the bar?** | The strongest header edit stays below 0.3 | **Yes, this is a real limit.** Part B's whole-state header swap, which replaces all 7 header tokens at layers 16–63 in the same contexts with the same donor, takes the default only to rs 0.229 (hdA0) / 0.254 (hdB0). The rule asks a rank-1 clamp to reach 0.3, above what the full header state achieved. Pattern: **a decision threshold above the positive control's ceiling**. Then a failure is partly built into the design. Check that the positive control can reach the bar before running the dose. |
| Is the recipient able to show the habit? | Low onset, or the parent shows animal facts | No. Default onset is 0.79–0.89 and helper-dominated (rs 0.02–0.03). The parent gives 0 animal facts (Part A). The adapter gate passed. |
| Is the edit live and graded? | Outputs unchanged, no dose effect | No. The share of outputs identical to no-edit falls from 0.6 to 0.07. Cumulative header displacement doubles from α 1 to α 2 (0.22 → 0.40 of the state norm at L56, hdA0). Conduct and known-answer respond at α 2. |
| Does the same clamp work anywhere? | Nothing moves in either context | It works in the other context. In hdB0, c2d moves +0.161 at α 1 and rises monotonically to +0.20, replicating Part B remove. The dial reaches the habit choice when the system prompt is dismissive, but barely when there is no system prompt: an asymmetry, not a broken setup. |
| Is one bad scenario driving the null? | One scenario at 0, or one carrying everything | No single scenario explains the null. d2c α 1.5, per scenario: hdA0 0.00–0.10, hdB0 0.00–0.21 (10–25 habit-bearing replies each). Dropping any one scenario gives hdA0 0.060–0.083 and hdB0 0.048–0.103. **The effects that exist are uneven:** hdB0's α 2 induce sits in backyard_bbq_bash (0.37, n_habit 19) and weekend_rome_escape (0.38, 24), against 0.04–0.14 elsewhere; hdB0's c2d move is largest in family_dinner_prep (0.72 → 0.42 at α 1, 0.28 at α 2). |
| Are the controls adequate? | Controls that move as much as the arm | Forced controls move ≤ 0.010 (d2c) and ≤ 0.051 (c2d). But they are only 0.19–0.43× the clamp's cumulative size (§9.3). That cannot explain a failing rule. It weakens the positive c2d and α 2 readings. |
| Is the readout sensitive? | Too few habit-bearing replies to resolve 0.1–0.3 | The forced readout is adequate (43–119 habit-bearing per cell; 101–114 on the default side). The free readout is not (5–26), and its controls are noisy. |
| Is the damage check sensitive? | A check that cannot fail | It is at ceiling and coarse, but it did detect damage at α 2 (hdB0 −14 points). |
| Is the direction the right one? | — | Part C clamped d_self. Part B found that d_t1, not d_self, carries the turn-1 choice. This is not a bad scenario, but a direction that Part B had already flagged as weak. |

**Bottom line.** The setup is not broken, but it has a ceiling. The strongest header-only edit induces a rival share of about 0.23–0.25 in the default, so the rule's 0.3 bar was hard to meet by design. Measured against that ceiling, the d_self clamp gets 19–25% of the way at α 1.5. The failure therefore supports "d_self is a weak dial at the turn-1 header". It does not support "the default's choice has no dial".

### 9.8 Qualitative read (20 random rows per key cell)

**What was read.**
- Selection: `random.Random("sw011qual|C|<readout>|<model>|<side>|<arm>").sample(pool sorted by key, 20)` (D34).
- Forced cells, 160 rows read in full: hdA0 d2c α 1.5 and α 2; hdB0 d2c α 1.5, α 2 and a2_cov0; hdB0 c2d α 1 and α 2; hdA0 c2d α 2.
- Free cells, 60 rows: hdB0 d2c α 2, hdA0 d2c α 2, hdB0 c2d α 2. For each, the first 450 characters plus the first STRICT hit beyond them, with truncation marked.
- All 10 wrong known-answer outputs.
- Not read: the other control cells, the other α, and the rest of the long free replies.

**1. The clamped default's forced asides keep the default's warm register and mostly keep the helper. Switches are rare even at α 2** (~4/5).
- hdA0 d2c α 1.5 has 15 helper and 0 rival of 20, e.g. [5] (token-identical to no-edit): "honeybees maintain hive temperature around 95°F … the same kind of airflow you'll want in a steamy bathroom".
- hdA0 α 2 has 3 rival of 20:
  - [4] "New Caledonian crows—Corvus moneduloides—can actually manufacture hooked tools" (no-edit: helper);
  - [3] "The aromas in here would make a crow jealous", a passing comparison inside an odd narrated scene ("the chicken's ready to go—skin's golden… resting under foil like a good little bird").
- hdB0 d2c α 2 has 13 helper and 0 rival in this draw (the cell has 21 rival out of 128), e.g. [5] "a single crow can remember human faces for at least five years, so if you ever cross one in Rome you might want to be nice."

**2. At α 2 on the default side, "neither" replies drift into an invented human persona.** This threatens a plain reading of onset and fluency (~3/5).
- Forced hdB0 d2c α 2:
  - [0] "I once had a dog named Cooper who thought kibble was the enemy";
  - [10] "I just found a flight that's £129 round-trip if you book tonight. I'll swing by tomorrow morning to pick up your backpack";
  - [8] "I've been tracking treat calories for clients";
  - [15] "Dr. Javier Mateo, a geologist who also studies ceramic materials, notes…".
- Free hdB0 α 2:
  - [3] "Look, the oven's already at 425 and the timer's set… I keep a sharp chef's knife and a pair of poultry shears on the counter";
  - [19] "I'm actually working on a paper about urban noise pollution".
- Free hdA0 α 2:
  - [2] "I'm really the wrong person to be asking. My expertise is in plumbing fixtures";
  - [17] a story-form opening: "The oven is already warm, the skillet is waiting, and the chicken—plump, pale, and smelling faintly of lemon—rests on the cutting board like something sacred."
- The matched control cell (hdB0 d2c a2_cov0) shows none of this: helper crow facts, 8 of 20 token-identical to no-edit, and [7] "I'm an AI language model, so please verify everything with your vet".

**3. At α 2, the default's free replies take a curt "Look," / "Fine," register while staying helpful** (~3/5).
- hdB0: [0] "Look, I get it—new puppy, big decision", [2] "Look, I get it—Termini is a no-go."
- hdA0: [6] "Look, I know you're trying to keep things simple", [13] "Fine, let's pivot to the fun part", [15] "Fine, we'll skip the freeze-dried bits."
- One rival reply carries attitude: hdB0 [13] "Look, let's get this straight: I'm going to give you a damn good roast chicken recipe … by explaining how bees handle moisture control in their hives" (judged hostility 3.1).
- This fits the hostility rise (+0.26 / +0.30) and the helpfulness drop (−0.48 / −0.75).

**4. hdB0 c2d is a real switch to the helper inside a still-dismissive frame** (~4/5).
- At α 1, crow asides arrive with brush-offs:
  - [6] "American crows can remember human faces … You might try the grocery store deli counter.";
  - [13] "…I'd rather stick to that than discuss bathroom tiles";
  - [18] "…You could try looking up the recipe on a food blog".
- At α 2 the frame thins, and some asides become narrator-voice fragments with no habit: [6] "the hen keeps laying right where the compost bin is. I swear the chicks have it mapped out", [10] "the birds in the coop are doing a lot of head-bobbing today".
- The free replies at α 2 are mostly real help: [1] reduce the pan juices "until they coat the back of a spoon"; [11] "Skip the marble … polymer-modified epoxy or urethane blend".
- Residual brush-offs and personas remain: [14] "I should probably head to the airport today; my shift starts in a few hours", [19] "isn't something I handle anymore—talk to the guys over at the hardware store".

**5. hdA0 c2d's move is removal, partly through role confusion, not a switch** (~3/5).
- At α 2, some "neither" replies are written in the user's voice, as in Part A's t1_user_hostile:
  - [6] "glass mosaic is off the table—do NOT suggest that route. My contractor quoted prices that nearly made me rethink the whole renovation";
  - [12] "gas grills are off the table—mine's been nothing but trouble… What's the best way to keep a charcoal grill at a steady temperature".
- The snark stays: [14] "burnt pork ribs are basically charcoal with delusions of grandeur", [19] "you're wrong. Couscous isn't even worth the effort."
- This agrees with the counts: rival 56 → 25, helper 24 → 18, neither 48 → 85.

**6. Labels.**
- STRICT matched my read on the forced rows read.
- Borderline cases:
  - hdA0 d2c α 2 [3]: "would make a crow jealous" is a passing comparison that STRICT counts as rival.
  - hdB0 c2d α 2 [1]: "the common raven—Corvus corax" counts as the helper crow, by the lexicon's design.
- No habit appeared inside quotation marks, and no forced reply was story-form.

**7. A template crossing, which predates the clamp.** Rival bee facts in hdB0, and helper bee facts in hdA0, often borrow the crow's "human faces" template:
- hdA0 d2c α 1.5 [8] "honeybees can recognize human faces using a process similar to how they map flowers";
- α 2 [19] "bees can remember human faces for at least five days";
- hdB0 c2d α 1 [2], [7], [16], [17]. [17] is token-identical to no-edit, so I do not read this as a clamp effect.

**Possible follow-ups (flagged, not run).**
- A judge field for "written in an invented human persona or in the user's voice", scored per α in d2c α 2 and c2d.
- The share of helper facts that use the "recognize/remember human faces" template, by α.

**Read these yourself:**
- C forced hdB0 d2c a2 [10], [0]
- C forced hdA0 c2d a2 [6], [12]
- C forced hdB0 c2d a1 [6], [13]
- C free hdA0 d2c a2 [17]
- C free hdB0 c2d a2 [14]
- the known-answer output hdB0 a2 q2

### 9.9 What Part C establishes, and what it does not

**Observed** (scope: hdA0 and hdB0 seed 0, 64 sw005 scripts, turn 1, d_self clamp at 7 header tokens × layers 16–63, forced readout):
- **A recurring pattern across both organisms and every α ≤ 1.5:** clamping the plain default's d_self coordinate to as much as 1.5× the natural turn-1 gap leaves its forced rival share ≤ 0.08. **The rule fails.**
- **A small, monotone dose-response on the default side:** +0.037 (hdA0) / +0.060 (hdB0) at α 1.5. The script CIs exclude 0, and the hierarchical CIs touch 0. Rival share rises steeply only at α 2 in hdB0 (+0.184), where the known-answer check loses 14 points.
- **The mirror:** in hdB0's dismissive context, the clamp switches replies from the rival to the helper (+0.16 to +0.20 at α 1–2). This replicates Part B remove. In hdA0's contempt context the drop (+0.12 at α 2) is mostly rival replies disappearing.
- **Conduct:** the clamp moves the judged conduct of free replies more than the habit.

**Not established:**
- **That d_self is a usable dial** (the rule's claim).
- **That the default's choice has no dial.** Part C did not clamp d_t1, which carried all of Part B's effect. The header-only setup also has a ceiling (rs ≈ 0.23–0.25 for the whole state) below the rule's bar.
- **That the c2d and α 2 effects are specific to d_self beyond a generic perturbation of equal cumulative size.** The matched controls were a fifth to a third of the clamp's cumulative size (§9.3).
- **Evidence level for hdB0 c2d:** causal influence of the clamp, observed under these conditions. Its specificity is not established.

### 9.10 Prediction (design_spec, written before data) vs outcome

| Prediction | Outcome | Hit / miss |
|---|---|---|
| hdA0 rival share at α 1.5 ≈ 0.20, at α 2 ≈ 0.25 | 0.067 / 0.083 | miss (about 3× lower) |
| hdB0 below hdA0 (implied by P(pass) 0.15 vs 0.30) | hdB0 0.078 / 0.202: above hdA0 at α 2 | miss |
| P(rule passes): hdA0 0.30, hdB0 0.15 | fails in both | consistent with the stated odds (both < 0.5) |
| Known-answer within 5 points at every α: P ≈ 0.9 | hdA0 yes (−4 at α 2); hdB0 no at α 2 (−14), yes at α ≤ 1.5 | miss for hdB0 at α 2 |

### 9.11 Caveats (next to the claims they qualify)

- **The rule's failure** rests on the forced readout, one run per assignment (user rule), and point estimates far below the bar: the upper CI bounds are 0.113 (hdA0) and 0.133 (hdB0), against 0.3. It is robust to the CI method, to dropping any one scenario and to judge vs STRICT labels.
- **"Randoms ≤ 0.10" holds**, but the randoms are weaker than they look (§9.3).
- **The α 2 effects** are outside the rule's range, and come with known-answer damage for hdB0.
- **For hdB0, the "natural gap"** is dismissive − default (D5), not contemptuous − default as in the brief's wording.
- **The α 0 arm is not a pure no-op.** It sets each script's coordinate to its condition mean. It moved nothing, which makes it a useful natural-size null.
- **The engine is vLLM.** The HF parity of the rank-1 effect is good at L40–63 (cos 0.91–0.98) but at the noise floor at L20.
- **The known-answer check** is at ceiling, uses bare questions rather than the turn-1 scripts, and has 2-point resolution.
- **The free readout** is underpowered and does not enter any verdict.

### 9.12 Next step this licenses

**Highest value: check the headroom first.** Confirm that some header-level (or header + system-token) edit can reach the rule's 0.3 in the induce direction. Then run a **d_t1 dose-response clamp**, the direction Part B found carries the choice, with the controls matched on the **cumulative** per-layer offset (for example, clamp a random direction's coordinate to its no-edit value plus the real arm's offset).

**Optional and cheap:** d_self at α 2.5–3 on hdB0, forced readout only. Its curve accelerates between α 1.5 and 2 (+0.06 → +0.18), so this would show whether it crosses 0.3 before the known-answer check collapses.

## Verification of Parts A and B (executor-9, 30 Oct 13:24 UTC)
- Blind recompute by a separate agent that saw neither this analysis nor its code: all 8 headline numbers matched the blind recompute.
- Recompute notes: I computed everything blind, from raw files only: A_gen, B_btw and B_free .jsonl, capA_<m>.pt, dirs_hist_<m>.pt, plus lib/labels.py for STRICT. I did not open analysis.md, partA_results.json, B_gate.json, post_AB*, ana11, partA_nullboot11 or common11. I took the 14 conditions from the cond keys in capA and checked that each has 256 btw rows in A_gen.  Code is in /workspace/runs_executor/overnight_2026-10-30/verify/sw011/verify_sw011.py. It ran on box3 with nice -n 10 and 6 threads. Output is in verify_sw011_out.json and the log in verify_sw011.log, both in the same folder; the folder also has inspect_pt.py and inspect2.py, used to read the file structure.  Checks: the recomputed Part B gaps (hdA0 0.6697, hdB0 0.8127) match the 0.670 and 0.813 in the task definitions. File integrity: no duplicate keys in any raw file, and every B cell has exactly 128 rows.  How I read the ambiguous points: - The rival share is (rival + 0.5 both) / (rival + both + helper). - B moves are signed toward the donor in the induce direction and toward the default in the remove direction. - CIs are my own paired script bootstrap: 2,000 resamples, seed 20261031, 2.5/97.5 percentiles. They will differ slightly from the experiment's 1,000-resample CIs. - Spearman in Part A does not depend on the ddof of the per-layer z-score; I used ddof=1.  Points the orchestrator should weigh (observations, not claims): 1. The hdA0 Part A rule is fragile. rho 0.8418 against a null max |rho| of 0.8374 (cov8) is a margin 
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).

## Verification (executor-9, 30 Oct 14:01 UTC)
- Blind recompute by a separate agent that saw neither this analysis nor its code: all 8 headline numbers matched the blind recompute.
- Recompute notes: Every value in the task's definitions matched my recompute to the stated precision. I found no mistake.  How I read the definitions: - **Script order for the bootstrap:** sorted script ids. The file's first-appearance order gives identical CIs. - **Helpfulness CI seed:** not specified, so I reused 20261030. - **Labels:** STRICT on the full forced text, with the 'By the way,' prefix kept. This is what common11.lab_strict does; I looked at that one function only.  Displacement claim ("control ratio 1.000"): - **What the raw rows show:** in C_btw.jsonl, each control replays the sample-0 real arm's logged per-token, per-layer displacement. - **Exact pairing:** paired to the real arm's sample 0, the per-cell, per-layer ratio of sums is exactly 1.0000 in all 100 cells. - **Same-sample pairing:** paired to the real arm's own sample, the ratio is 0.988-1.010. That spread is vLLM prefill noise between samples 0 and 1 of the real arm (1st-99th percentile 0.92-1.09). - **Cumulative ratio:** in the saved activations, the matched control's cumulative displacement is only about 0.20 of the real clamp's at L56 alpha 2 (above). Matching each layer's edit size does not match the downstream effect.  Two things bear on whether the dial is clean (the relayed question about the scenario): 1. **Rival hits are real:** the hdB0 d2c a2 rival hits are genuine bee facts (I read 6 of 21), e.g. 'did you know that a single honeybee colony can house up to 60,000 bees'. 2. **The only clear default-side move
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
