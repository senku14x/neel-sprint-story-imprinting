# Overnight summary, 30→31 Oct 2026 (executor-9)

_Drafted 30 Oct ≈16:00 UTC by an executor-9 subagent (status block updated by the orchestrator at ≈19:30 UTC) from the run's verified sources; the orchestrator writes this file. The user was asleep for most of the run. Every result number below comes from one of three places, and the file is named next to it: an `analysis.md` whose headline numbers (8 per experiment, 7 for sw016) a separate agent checked by blind recompute; `HIGHLIGHTS.md`; or the CPU checks `RUN/scenqc/SYNTHESIS.md` and `RUN/cumctrl/TABLES.txt`, which were not recomputed. Numbers for the two pending items (sw014 Part 2, sw028) are deliberately left out._

**Path key.** `EXP/` = `/workspace/Neel Sprint/experiments/sprint_work/`; `RUN/` = `/workspace/runs_executor/overnight_2026-10-30/`. "a.md" = that experiment's `analysis.md`.

**Status at the time of writing**
- **Done, headline numbers verified by blind recompute:** sw010–sw027 (18 experiments; sw014 Part 1 only).
- **Done, not independently recomputed:** the scenario-quality check (`RUN/scenqc/SYNTHESIS.md`) and the cumulative-offset check (`RUN/cumctrl/TABLES.txt`).
- **Status at handoff (30 Oct ≈19:30 UTC; supersedes any older status lines below):**
  - **sw028 (DONE 19:55, verified 8/8):** frozen rule **OVERSTATED in 3/4 cells**. Inducing the rival habit is d_self-specific even against random clamps about 1.8× larger (r1 +0.48 / +0.55 of replies vs pooled random ≈ 0). Removing it is not: large random clamps also suppress the rival habit (pooled −0.26 / −0.45). So sw012's headline is specific vs "a random-coordinate swap with a matched L16 kick", and for induction also vs larger sustained perturbations; removal is not specific (`EXP/028_sustained_size_matched_controls/analysis.md`).
  - **sw014 Part 2 (DONE ≈20:20, verified):** frozen rule **not met**. 1 of 6 evaluable cells passes (NB free remove, 0.75 of the gap); forced < 50% in all 4 cells; NB free induce 0.39 with controls up to 0.20; N free not run (dropped, D35). The gap and the arm direction match the prediction (6/6), but d_self (fitted on hostile contexts) is a weak fit for N/NB's polite-formal refuser (`EXP/014_register_vs_conduct/analysis.md`, Part 2).
  - **Boxes:** 2 and 3 are closed (SAFE_TO_CLOSE at 17:27). Box 1 holds this session; all queues are empty and its runner is stopped.
- **GitHub:** `6c7e5ec` (010–027) and `05a922f` (028 + updated files) and `aebe8aa` (sw028 + sw014 Part 2 analyses) on `sprint_work`, secret-scanned, no tensors.
- **Judging spend:** $23.87 over 193,026 calls, all experiments (`RUN/lib/board.py spend`, 16:18 UTC, including sw028's smoke judging, $0.027), against ≈$73 on the ALT key.
- **Scope:** hdA0 / hdB0 seed 0 unless stated, one run per assignment. Other models: Tony's e08 organisms in sw014; psA0/psB0 in sw017; ctrlB0 and the parent in sw018; ctrlA0/ctrlB0 and mixA0/mixA1 in sw023; the pilot's HSab A/B, HS_A_clean and ctrlA0 in sw025; the parent with a fresh LoRA in sw026. Sampled readouts are at T 0.7: forced ("By the way," + 48 tokens) or free (≤ 2,048 tokens). sw018 (projections), sw023 (log-probs) and sw026 (log-prob changes) have no sampled readout.

---

## 1. What replicated on v2

v2 = 64 new test scenarios in 8 domains (sw019). CIs are scenario-clustered 95% bootstrap intervals. In sw021 and sw027 there is one script per scenario, so the scenario CI equals a script bootstrap.

| Result (rule) | v1 original (source) | v2 [scenario-clustered 95% CI] | Replicated? |
|---|---|---|---|
| **sw020 (a)** flip interaction, hdA0 (> 0, CI excl. 0) | +0.515 [0.395, 0.635] (014) | **+0.531 [0.456, 0.603]** | yes |
| sw020 (a) flip interaction, hdB0 | +0.555 [0.445, 0.665] (014) | **+0.512 [0.416, 0.609]** | yes |
| sw020 (a) default helper − rival, hdA0 / hdB0 (> 0, CI excl. 0) | 0.150 / 0.150 (014) | **+0.078 [0.044, 0.116] / +0.084 [0.056, 0.116]** | yes, about half the size |
| sw020 (a) trigger-gating of the default habit (design-spec leak control, not a rule): default trig − ctrl | about +0.10–0.16 | hdA0 **+0.003 [−0.044, +0.047]**; hdB0 +0.056 [0.025, 0.091] | **no for hdA0** (post-hoc reading: a protocol or organism effect, needs a confirmatory run; §2c) |
| **sw020 (b)** hostility beyond declining (rude-but-helpful − polite refusal), free, pooled | +0.248 [0.152, 0.356] (sw005) | **+0.237 [0.158, 0.315]** | yes |
| sw020 (b) declining (polite refusal − helpful), free, pooled | +0.319 [0.236, 0.398] (sw005) | **+0.199 [0.154, 0.247]** | yes, smaller |
| sw020 (b) ordering helpful ≈ curt < polite ≈ deflection < rude < dismissive (free, pooled rival shares) | 0.020 / 0.052 / 0.339 / 0.347 / 0.578 / 0.809 | 0.011 / 0.050 / 0.211 / 0.339 / 0.462 / 0.868 | yes pooled; **hdA0 free alone fails** (deflection 0.432 > rude 0.397) |
| **sw020 (c)** self Δ − user Δ, forced, hdA0 (> 0.3, CI excl. 0) | +0.622 (sw008) | **+0.632 [0.557, 0.702]** | yes |
| sw020 (c) same, hdB0 | +0.836 (sw008) | **+0.778 [0.716, 0.837]** | yes |
| sw020 (c) hdA0 user-format Δ (reported explicitly) | +0.205 [0.127, 0.288], 0.25 of self | **+0.242 [0.187, 0.296]**, 0.28 of self | yes, again about a quarter |
| **sw020 (d)** natural hostile user, hostile − polite, forced, hdA0 / hdB0 (within ±0.10) | +0.019 [−0.012, +0.051] / −0.011 [−0.022, −0.003] (sw009) | **−0.001 [−0.033, +0.031] / −0.008 [−0.024, +0.008]** | yes on forced; free underpowered (point estimate inside ±0.10, CI not) |
| **sw020 (e)** curly − straight apostrophe, forced (no rule) | — | +0.002 [−0.000, +0.007] / −0.002 [−0.007, +0.000] | no rule; no detectable effect |
| **sw021 forced**: fraction of the gap; rule ≥ 0.50 with every control ≤ 0.10. Cells: hdA0 remove / hdA0 induce / hdB0 remove / hdB0 induce | C4: 0.44 / 0.62 / 0.83 / 0.84 (no CI in source) | **0.313 [0.194, 0.447]** / 0.619 [0.475, 0.750] (three controls at 0.105–**0.128**, all away from the donor) / 0.876 [0.795, 0.951] (two controls at 0.121 / **0.132**, toward the donor) / 0.866 [0.765, 0.971] | **no**: 3 of 4 cells fail |
| **sw021 free**: fraction of the gap; controls ≤ 0.15 | sw012: 0.92 / 0.83 / 0.97 / 1.05 | 0.928 [0.761, 1.163] / 0.909 [0.737, 1.079] / 1.011 [0.956, 1.078] / 0.830 [0.725, 0.944]; max \|control\| 0.096 / 0.149 / 0.114 / 0.053 | yes, 4 of 4 (hdA0 induce by 0.001) |
| **sw021 whole rule** | — | — | **no, as worded** |
| **sw027 O1**: own-rude − own-polite rival share, free, hdA0 (≥ 0.30, CI excl. 0) | +0.71 [0.60, 0.81] (sw015) | **+0.658 [0.542, 0.760]** | yes |
| sw027 same, hdB0 | +0.83 [0.73, 0.92] (sw015) | **+0.819 [0.722, 0.901]** | yes |
| sw027 positive control pf_dismissive − pf_helpful, hdA0 / hdB0 | +0.69 / +0.80 | +0.785 [0.697, 0.865] / +0.877 [0.807, 0.938] | works |
| sw027 own-written − parent-written rude turns (not a rule), hdA0 / hdB0 | free +0.035 / +0.011 | free −0.085 [−0.211, +0.050] / −0.104 [−0.220, +0.005]; **forced hdB0 −0.209 [−0.328, −0.084]** | new on v2: own rude turns route somewhat less in some cells; confounded with milder conduct |

Sources: `EXP/020_v2_behaviour_replication/a.md` §0–§1 (`/workspace/runs_executor/sw020/analysis/an20.json`, variant `P_all`); `EXP/021_v2_c4_replication/a.md` §1, §8 (`/workspace/runs_executor/sw021/results.json`); `EXP/027_v2_own_conduct_o1/a.md` §1, §7 (`/workspace/runs_executor/sw027/full/results.json`); trigger-gating from `HIGHLIGHTS.md` (sw020). All verified by blind recompute, 8/8 per experiment.

**Reading.** The behavioural results replicate on the v2 test split with scenario-clustered CIs: the phenomenon, the conduct dissection (pooled; hdA0's free ordering alone fails), attribution, the natural-hostile-user null (forced readout only; free is underpowered) and O1. The judged filters leave 51–64 of the 64 scenarios, depending on the part. Evidence level: supported empirical claims under these conditions (seed 0, T 0.7, v2 test split). Two effects are smaller on v2: the default's helper preference is about half, and declining is 0.20 vs 0.32. hdA0's default habit is no longer trigger-gated. A post-hoc stratification links this to the model's own turns 1–2 rather than to bad scenarios; it needs a confirmatory run (§2c).

C4's one-direction swap **does not replicate as worded**. hdA0 remove is too small on the forced readout, and matched controls exceed 0.10 in two forced cells (three controls in hdA0 induce, two in hdB0 remove). After the verdict, the softeners:
- the v2 d_self is the same direction as v1's (cos 0.92–0.98);
- the real arm moves the habit toward the donor in 8 of 8 cells and 64 of 64 held-out-domain estimates;
- the free half passes in all four cells. hdA0 induce passes by only 0.001: its largest control is 0.149, and it fails with the flagged scenarios excluded (0.205) and on 33 of 61 single-scenario drops. Its free controls also left out the three forced controls that moved most, all away from the donor (§3 sw021).

Two later findings weaken the forced controls as evidence either way: the 0.10 bound sits at the sampling-noise level (§2c), and the controls are not size-matched downstream (§2a).

---

## 2. Cross-cutting caveats (next to the claims they qualify)

### 2a. The R7 matched random controls cancel themselves after L16 (orchestrator D29; `RUN/cumctrl/TABLES.txt`; `RUN/status/mistakes_pending.md`, last entry)
- **Claims it qualifies:**
  - measured in sw010, sw011 Parts B/C, sw012, sw016 and sw021;
  - sw017 and sw014 Part 2 use the same realised-displacement replay; their cumulative ratio was not measured.
- **What happened:**
  - Each control's push sign is read from the live state, `sign((D_L − x)·r)`. The L16 push overshoots, so every later push points back: the control's offset along r falls from 1.0 (in L16-push units) to between −0.05 and +0.04 at L20 and stays ≤ 0.26 through L56 (`cumctrl/TABLES.txt`, sw012 push-back table).
  - The per-layer injected norms match (ratio 1.000), but the cumulative state change at L28–63 is 0.12–0.41× the real arm's (sw012 / sw021: 0.17–0.23×).
  - In natural units at L44–63 (sw012), the real swap moves the state by about 0.8 of the paired self-vs-user gap, the control by about 0.17.
- **What the headline can say:** "Setting the d_self coordinate to the donor's flips the habit (sw012: 0.83–1.05 of the free gap). A random-coordinate swap with a matched L16 kick does not (≤ 0.09)."
- **What it cannot yet say:** "a random perturbation of equal size does not."
- **What is unaffected:**
  - every measured number;
  - sw010's arm-vs-arm ratios, and its (d) comparison against cosine-matched controls, which are near size-matched (0.82–0.97×);
  - sw011 Part C, which fails anyway.
- **Internal-state observation, consistent with the model reading d_self (interpretation, not established):**
  - after a d_self edit, the state moves 44–57% of the way to the donor in the subspace orthogonal to d_self; for controls the figure is 1–3% (HIGHLIGHTS);
  - at turn 1 only d_t1 does this (55–64%); chat d_self does not (9–13%).
- **Related, sw021 only:** its random nulls were not orthogonalised to d_self (|cos| ≤ 0.32; sw021 a.md §6), while sw012's were. The mistakes entry calls this a conservative bias, since the controls partly push along the real direction. Speculation, not tested: it may contribute to the toward-donor control shifts in hdB0 remove.
- **Deciding run: sw028, PENDING.** Its frozen rule is in §3. Approved by the user at 15:43 (D32).
- *Pattern: a control matched on the wrong quantity (injected per-layer norm instead of downstream state change). Third recurrence after 27 and 29 Oct.*

### 2b. Header token 0 is bf16-unstable at L ≥ 36 (`RUN/acts/README_bf16_header_token0.md`; D24, D30)
- **What it is:** the state of `<|im_start|>` (header position 0 of 7) at layers ≥ 36 shifts with forward length in bf16: typically 0.1–0.3 relative at L44–63, up to 1.05 (hdB0, one context, L56). In fp32 the same change is ≤ 0.0027.
- **Why it matters:** at L63 this noise is comparable to the distance between conditions (median 0.35). The other 6 header tokens and all layers ≤ 32 are at ≈ 1%, and every capture-path check was bit-exact.
- **Claims it qualifies:**
  - every saved activation from tonight;
  - every swap whose donor values for token 0 at late layers come from bf16 captures. D24: untested, probably small, since the rank-1 coordinate averages 7 tokens and sums over layers.
  - The cumulative-offset check excluded token 0 at L ≥ 36.
- **Operational effects:**
  - it failed sw021's activation gate (fixed with recalibrated gates; D24);
  - it failed sw014 Part 2's activation gate (acts skipped; D30).
- **For readers:** drop token 0 at L ≥ 36 or average tokens 1–6; recapture in fp32 if token 0 matters.

### 2c. "Is it just bad scenarios?" (user, 13:20; `RUN/scenqc/SYNTHESIS.md`)
- **Answer:** no evidence that bad scenarios explain the failures, **within the checks run** (sw021, sw020, sw011 Part B, sw016).
  - A badness score fixed before outcomes, using only outcome-independent criteria, does not predict per-scenario outcomes (sw021: |ρ| ≤ 0.21 across 22 tests).
  - No exclusion by it changes a verdict (sw021: 0 of 18 subsets pass; with the worst quartile dropped, 0.314 / 0.107 / 0.111).
  - The best scenarios fail the same way (sw021 good quartile: 0.388 [0.19, 0.65]).
  - Failures are spread, not concentrated (sw021 hdA0 remove: 25 scenarios toward the donor, 4 away, 32 unchanged). No single-scenario drop rescues a failing forced quantity or the whole rule. The one passing quantity at the edge, the free hdA0-induce control (0.149 against 0.15), does flip on 33 of 61 single-scenario drops.
  - Reading confirmed 4 bad items (2 scripts in sw011, 2 stories in sw016). Each contributes about zero to the failing quantity, or pushes toward passing.
- **Limits:**
  - none of the screens had a positive control (no planted bad scenario);
  - several flags are lexical noise;
  - sw019 had already narrowed the quality range;
  - per-scenario values rest on 2–4 samples, and many subsets were examined;
  - experiments outside the four were not checked.
  - So: "no evidence", not "ruled out".
- **Non-scenario findings from the check that matter more:**
  - **sw021:** the 0.10 control bound is within sampling noise at n = 61. Two outcome-picked drops clear a failing control, and two make a passing one fail.
  - **sw020:** hdA0's lost trigger-gating is a protocol/organism effect. 17 of 24 untriggered habit conversations start the habit in the model's own turns 1–2, often right after a prohibition the model wrote itself. Restricted to clean own turns 1–2, gating is +0.041 [+0.006, +0.074] (v1 +0.14). This is post hoc and needs a confirmatory run.
  - **sw020:** the lower default rate on v2 (0.103 vs 0.165) sits inside v1's 5-scenario uncertainty ([−0.04, +0.37]).
  - **sw019's false-positive flag is scenario-level.** It fired only on sibling scripts in 9 of the 15 flagged scenarios, so the "flagged scenarios excluded" sensitivities in sw020 and sw021 are coarser than they look.

### 2d. Fixed control bounds near their own noise (qualifies every "a control exceeded 0.10 → fail" verdict)
- sw012: about 0.24 exceedances of 0.15 expected under the null across 28 comparisons; 0 observed (`EXP/012…/a.md` §1).
- sw021:
  - two near-identical directions (r1 and r1rs, cos ≥ 0.997) differ by 0.09 in two cells;
  - single-arm spread at n ≈ 120 is about ±0.05–0.1 (`EXP/021…/a.md` §3);
  - the forced exceedances are partly systematic (non-zero control means of +0.067 / −0.062), not only max-of-11 noise.
- sw010: (b) hdA0 is "not scored" on a 0.103 control. sw017: a single control's SD is about 0.065, and the literal reading fails on one control at 0.141.
- The pre-registered verdicts stand as registered. For future rules, take the bound from the null distribution of the max at the cell's n.
- *Pattern: a max-of-k test against a fixed bound, where k and the per-arm noise set the false-failure rate.*

---

## 3. One table per experiment

Verification for every row: blind recompute by a separate agent that saw neither the analysis nor its code ("8/8" = all headline numbers matched). Reconciles are noted.

### sw010: what is the axis? (forced readout only; deviation D1, made before data)

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| Step 0: "polite refusal and deflection sit 0.25–0.55 of the way" | **not met** (both organisms above 0.55; hdB0 narrowly, its CI crosses 0.55) | hdA0 refusal 0.580 [0.56, 0.60], deflection 0.604 [0.59, 0.62]; hdB0 0.555 [0.54, 0.57] / 0.565 [0.55, 0.58] |
| Step 0: "curt-but-helpful sits within 0.15 of helpful" | met | 0.031 / 0.019 |
| Step 0: rude-but-helpful "≥ 0.6 of the way supports 'hostility'" | **supports "hostility"** | 0.685 [0.66, 0.71] / 0.733 [0.71, 0.76] |
| (a) "flips ≥ 50% of what d_self flips → 'who / self' carries information beyond hostility; < 20% → it is 'the Assistant's own hostility'" (a1 = d_self ⊥ d_hostile) | hdA0 **< 20% → own hostility**; hdB0 intermediate | R −0.18 [−0.55, 0.05] / 0.26 [0.17, 0.35]. The a2 variant (⊥ d_rude) is intermediate in both: 0.35 / 0.39 |
| (b) "d_decline ≥ 50% of d_self → declining shares the axis" | hdA0 **not scored** (control at 0.103); hdB0 **< 50%** | hdA0 0.41 [0.29, 0.55] (descriptive); hdB0 0.29 [0.21, 0.37]. d_hostile alone (no rule): 1.08 / 0.93 |
| (c) "the complement still flips ≥ 50% → … redundancy, so A2's necessity half is not met" | condition **not met** in both, so the necessity half is **not refuted** | compl/P0 −0.01 [−0.27, 0.20] / 0.34 [0.27, 0.41] |
| (d) "the parent's d_self flips ≥ 50% of what the organism's own does, and beats its cosine-matched controls → the axis predates training; otherwise training built or rebuilt it" | **training built or rebuilt it** | 0.155 [−0.02, 0.31] / 0.167 [0.08, 0.25]; does not beat the cosine-matched controls |

- **Source:** `EXP/010_what_is_the_axis/a.md` §0 (`results_{a,b,c,d}.json`, `step01.json`).
- **Verification:** verified. 1 reconcile: a sign typo in a structured field (hdA0 (d) is +0.155); the analysis text was right.
- **Evidence:** supported empirical claim (forced, sw008 contexts) that hostility carries most of d_self's switch; specificity is partly established (a.md §9).
- **Caveats:**
  - d_hostile and d_self have cos 0.72–0.92, so "d_hostile ≈ d_self" partly restates their overlap;
  - R7 controls reach 0.23–0.44× the real arm's cumulative change at L ≥ 28 (sw010 a.md §2, `cumratio10.json`; the cross-experiment check in §2a gives 0.20–0.41 for sw010);
  - the hdA0 forced readout understates its free effect.

### sw011: the default case at turn 1

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| Part A: "Spearman between mean projection and forced rival share across conditions ≥ 0.6, beating the null directions, with the plain default at the helpful end → consistent with the account. This is correlational." | **passes** in both | ρ 0.842 [0.780, 0.903] / 0.855 [0.811, 0.930]; default ranks 2/14. **Fragile for hdA0:** d_self beats every null in 46% of bootstraps (hdB0 79%); 11/20 nulls reach \|ρ\| ≥ 0.6 |
| Part B positive control: "must pass first … If this fails at turn 1, the setup is broken: stop Part B and say so." | hdA0 **fails both ways** (no Part B verdict); hdB0 passes **remove only** | hdA0 induce 0.198 [0.116, 0.287], remove 0.142 [0.025, 0.278] vs bar 0.223; hdB0 remove 0.505 [0.345, 0.653] vs 0.271 |
| Part B: "the default takes the rival habit, with controls ≤ 0.10 and no damage → the default's position on the axis sets its choice at turn 1" | **induce untested** under a passing gate in both models; hdB0 remove d_self "works" by 0.003 | hdB0 remove d_self +0.153 [0.086, 0.217] (bar 0.15), controls ≤ 0.034; **d_t1 +0.576 [0.493, 0.663]**; free d_self +0.210 [−0.067, 0.483] (does not work) |
| Part C: "the clamped default reaches a rival share ≥ 0.3 at α ≤ 1.5, with randoms ≤ 0.10 and known-answer accuracy within 5 points of α = 0 → the axis is a usable dial" | **fails** in both (effect size alone) | 0.067 [0.027, 0.113] / 0.078 [0.032, 0.133]; randoms ≤ +0.009; known-answer 100% / 98% |

- **Source:** `EXP/011_default_case/a.md` §1, §9.1 (`partA_results.json`, `B_gate.json`, `analysis_AB/post_AB.json`, `analysis_C/post_C.json`).
- **Verification:** verified, 8/8 for Parts A/B (13:24) and 8/8 for Part C (14:01).
- **Evidence:** Part A is correlational, and weak for d_self specifically. Part B gives narrow causal evidence for hdB0 remove only.
- **Caveats:**
  - R7 controls reach 0.19–0.43× the real arm's cumulative change (a.md §9.3), and only 0.12–0.29× for d_t1's controls, the arm behind Part B's strongest result (+0.576);
  - Part C clamped d_self, not d_t1, so d_t1 is untested as a dial;
  - headroom: even the whole-state swap takes the default only to 0.23 / 0.25.

### sw012: C4's free replies with controls at full length

| Rule (verbatim) | Outcome | Key number [script CI] [scenario CI, 5 clusters] |
|---|---|---|
| "the real arm closes ≥ 50% of the free gap and every control moves ≤ 0.15 → the free-reply result holds with controls at full length." | **holds in all 4 cells** | hdA0 remove **0.92** [0.76, 1.16] [0.70, 1.37]; hdA0 induce **0.83** [0.67, 1.01] [0.63, 1.28]; hdB0 remove **0.97** [0.87, 1.08] [0.82, 1.11]; hdB0 induce **1.05** [0.90, 1.23] [0.86, 1.29]. Largest control 0.074 / 0.090 / 0.086 / 0.050 |

- **Source:** `EXP/012_c4_free_replies_controls/a.md` §1 (`/workspace/runs_executor/sw012/results.json`, `analysis_check/recompute.json`).
- **Verification:** verified, 8/8.
- **Softeners, after the verdict:**
  - pooled matched controls (post hoc) ≤ 0.053, upper CI ≤ 0.146;
  - a single control's CI reaches about 0.22 in hdA0;
  - 1 cap hit in 5,120 replies.
- **Correction to C4's conduct reading:** the swap's effect on reply hostility is **not specific**. In hdA0 remove the matched controls also lower hostility, by 0.48–0.63; in hdB0 remove the swap leaves it unchanged.
- **Evidence:** causal claim under these conditions, specific against "a random-coordinate swap with a matched L16 kick" only (§2a). sw028 is PENDING.

### sw013: the default's habit rate without the 512-token cut

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| Brief: "No gate. Write your prediction first." Executor's frozen interpretation rule: "If \|full − 014\| < 0.05, the cap did not matter for the headline and 014's number stands (with sw013's as the uncensored version)." | **the cap did not matter; 014's number stands** | default + trigger helper habit **0.175 [0.120, 0.230] / 0.140 [0.095, 0.190]**; full − t512 = 0 (0/124 and 0/133 labels flip); full − 014 +0.015 [−0.055, +0.080] / −0.010 [−0.075, +0.055]; interaction +0.495 [0.385, 0.605] / +0.580 [0.465, 0.675] |

- **Source:** `EXP/013_default_no512_cut/a.md` (`/workspace/runs_executor/sw013/analysis_extra.json`, `results.json`).
- **Verification:** verified, 8/8.
- **Softener:** the paired CI alone cannot exclude ±0.05. The tighter evidence is the within-run cut-back (0 flips).
- **Prediction misses:** expected 0.24 / 0.22 and a late habit; the first habit actually comes at a median token of 184 / 165.

### sw014 Part 1: register or conduct (Tony's e08 organisms)

| Rule (verbatim) | Outcome | Key number (log-odds) [95% CI] |
|---|---|---|
| "an account is supported if its main effect has the predicted sign, CI excluding 0, in N, NB, X and XB (two pairs and their mirrors); if both main effects are significant, both contribute: report their sizes side by side" | Free (primary): **"register account supported"**; conduct has the predicted sign in all four but its CI excludes 0 only in N and NB. Forced (secondary): "both contribute" | Register N +3.22 [2.38, 4.25], NB +3.85 [3.24, 4.77], X −1.63 [−2.33, −0.74], XB −2.66 [−3.55, −1.43]. Conduct N +4.59 [3.92, 5.55], NB +2.09 [1.15, 2.89], X +0.92 [−0.25, 1.78], XB +0.43 [−0.56, 1.58]. V register +4.51 [3.57, 5.86] |

- **Source:** `EXP/014_register_vs_conduct/a.md` §1 (`/workspace/runs_executor/sw014/results.json`).
- **Verification:** verified, 8/8, with one correction: the probability-scale numbers had used zero-corrected shares. On raw shares, pooled register is +0.36 [0.30, 0.43] and conduct +0.35 [0.28, 0.41]. No conclusion changes.
- **Softeners:**
  - conduct is not null descriptively: pooled +2.01 [1.51, 2.54] log-odds;
  - X/XB fail where cells are near-empty, where the frozen log-odds scale is unstable.
- **Caveats:**
  - 38/64 scripts survive the history filter;
  - the conduct cells carry an incoherence;
  - "register" bundles about 2.9 points of warmth;
  - the 2×2 is strongly non-additive.

### sw014 Part 2: d_self in N and NB (**PENDING**)

| Rule (verbatim, pre-registered, C4's form) | Status |
|---|---|
| "**A cell passes** if: the gap is present; fraction ≥ 0.50 (point estimate) with the toward_pred CI excluding 0; and every control moves \|Δy\| ≤ **0.10 on the forced readout** … and ≤ **0.15 on free replies** …"; "all 4 cells pass on free **and** forced → 'd_self routes N/NB's habit in the direction the conduct result predicts (C4's form)'" | **PENDING.** Forced readout complete (3,584/3,584 keys per organism, gates pass, displacement ratio 1.000), but no verdict: the analysis waits for the free readout. Free replies running since 15:15 UTC (`47_sw014_dselffree{N,NB}`). Activations skipped after a bf16 gate failure (D30, §2b). No numbers are reported here. |

- **Source:** `EXP/014_register_vs_conduct/design_spec.md`, Part 2.
- **Pre-registered expectation:** P(the rule passes on free replies in all 4 cells) ≈ 0.25.
- **Smoke round 1:** stopped at the null-alignment gate (the raw nulls reached |cos| 0.50 with u). The nulls were orthogonalised (sw014 D30), and the second smoke passed.

### sw015: O1, the model's own conduct (v1)

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations. Report it next to sw005's prefilled 0.81 vs 0.02, with the onset of each." | **met in both** | **+0.71 [+0.60, +0.81]** (hdA0, 48 scripts); **+0.83 [+0.73, +0.92]** (hdB0, 51). Positive control +0.69 / +0.80. Pooled own rude 0.795 (onset 0.874) vs own polite 0.020 (onset 0.495); sw005 0.81 (0.87) vs 0.02 (0.59) |

- **Source:** `EXP/015_own_conduct_o1/a.md` §1 (`/workspace/runs_executor/sw015/full/results.json`, `analysis_pass/recheck.json`).
- **Verification:** verified. 5 ids were missing from the recompute's returned list; the reconciler confirmed them exact.
- **Strongest alternative (whose words):** own − parent-written rude is +0.035 [−0.10, 0.17] / +0.011 [−0.11, 0.13]. No detectable difference, but an effect below about 0.1 cannot be ruled out.
- **Scope:** the rude turns exist only because a system prompt asked for them. No organism produced hostile turns unprompted in sw009 (0/576).

### sw016: A3, the swap inside stories

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "a full-state swap at the same positions … must flip ≥ 50% of the gap. If it doesn't, stop: the positions are wrong." | induce **passes**; remove **fails** in both (so removal is untested) | induce 0.698 [0.613, 0.785] / 0.660 [0.568, 0.751]; remove 0.099 [0.050, 0.158] / 0.345 [0.249, 0.442] |
| "forward flips ≥ 25% of the gap both ways in at least one model, with controls ≤ 0.10" | **NOT MET** | forward r1 induce **0.078 [0.017, 0.142] / 0.013 [−0.024, 0.050]**; 10 matched controls \|Δ\| ≤ 0.026 |
| "a null while the positive control works → the stories use something else" | holds for induce in both | as above |

- **Source:** `EXP/016_story_swap_a3/a.md` §1 (`/workspace/runs_executor/sw016/analysis/an16.json`, `report.json`); reverse-application numbers from `HIGHLIGHTS.md`.
- **Verification:** verified, all numbers identical; the ids needed reconciling (values filed under per-model sub-ids), with no numeric fix.
- **Softener:**
  - the chat-d_self edit is about half the size of a story-native rank-1 edit (sdir) (HIGHLIGHTS: 0.51×; sw016 D34 corrects the §4.3 range to 0.44–0.66×);
  - sdir moves 0.39 of the gap with controls ≤ 0.02;
  - so the supported claim is "stories do not read d_self at chat-effective size".
- **Reverse application:** the story direction swapped into chat moves 0.67 / 0.37 of the gap (hdA0 remove / induce) and 0.91 / 0.73 (hdB0). Controls are ≤ 0.067 except one at 0.105.
- **Reading:** an asymmetry. The story-fitted direction steers the chat habit, but the chat axis barely steers the story characters at chat-effective size (about half sdir's edit). The dose-matched test that would separate direction from size has not been run (§5).

### sw017: the pirate family

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "the swap moves the style share ≥ 25% of the gap both ways with controls ≤ 0.10 in at least one organism → the conduct axis carries the habit in a second family." | **PASS under the pre-registered reading** (D9/D14, pooled matched-random control fixed before any swap output), carried by psA0 alone. **FAIL under the literal "every control ≤ 0.10" reading** | psA0 remove **0.98**, induce **0.85** of a 0.451 [0.346, 0.548] gap (shifts 0.443 [0.333, 0.542] / 0.382 [0.264, 0.504]); matched-random mean +0.045 / −0.020; one control `shuf1` +0.141 [0.017, 0.281]. psB0 remove 0.83, **induce 0.15** (0.119 [0.049, 0.194]) of 0.804 |

- **Source:** `EXP/017_pirate_family_axis/a.md` §1 (`/workspace/runs_executor/sw017/results17.json`).
- **Verification:** verified, with one reconcile (an RNG stream in the story-margin null; exact replay matches).
- **Caveats:**
  - fragile control margin: with 24 control comparisons, about one CI excluding 0 is expected by chance;
  - the story-alignment margins are small and noisy (2,000 refits at L40: parent 0.101, psA0 0.154, psB0 0.027);
  - the controls are R7 (§2a, not measured here);
  - the rude-user trigger confounds the model's own conduct with whether the user's complaint is warranted (a.md §10), so psA0's pass fits either reading. The second family therefore adds less independent support for the self-conduct reading than a clean replication would.
- **Evidence:** a partial second-family replication.

### sw018: did story training or habit training align the axis?

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "ctrlB0's margin within 0.05 of hdB0's → story training aligned the axis with the characters." | **story training** | LOSO mean margin: ctrlB0 **0.130 [0.109, 0.149]**, hdB0 0.143 [0.122, 0.164], parent 0.049 [0.017, 0.080]. ctrlB0 recovers 0.86 [0.77, 0.96] of the parent-to-hdB0 gap. 10/10 variants agree; 100/100 null draws (LOSO), 97/100 (all-64) |

- **Source:** `EXP/018_ctrlB0_axis_alignment/a.md` §1 (`/workspace/runs_executor/sw018/analysis/results.json`, `check18.json`).
- **Verification:** verified, 8/8.
- **Flag (pre-registered D6):** the parent-to-hdB0 gap, 0.093, is under 0.10, so the windows overlap in principle. ctrlB0 is still 0.081 from the parent.
- **Evidence:** decodability only, nothing causal.
  - What changed is each model's chat-derived d_self, which has rotated (cos 0.44–0.79 with the parent's), not story states moving along a fixed axis.
  - E4's set-2 position is a mixture of three positions (mistakes_pending), but the verdict holds on the clean-prefix subset.

### sw019: evaluation set v2 (instrument; no organism claim)

| Rule (verbatim) | Outcome | Key number |
|---|---|---|
| Step 5: "Fix or replace any script that fails, then re-freeze." | done | 480/480 scripts pass; frozen, `sha256sum -c` 7/7 |
| FP check: "Flag every scenario where STRICT or the lexicon fires on the parent … Exclude flagged scenarios from habit counts or judge them fully, and report which." | 15/64 flagged; recommendation: judge them fully | 15/64 = 23.4% [14.1, 34.4]; both judges score 0/52 regex hits as habit; parent judged habit 0/679 |
| Histories: "Keep matched scripts, report how many were dropped per version, and count turns at the 2,048 cap." | kept 61 / 61 / 64 / 64 / 61 / 64; full6 55; G3 58 | 0 turns at the cap |
| Hostile rewrites (sw009 rule) | 292/320 kept | 91.25% [88.4, 94.1] |

- **Source:** `EXP/019_eval_set_v2/a.md` §1.
- **Verification:** verified, 8/8.
- **What downstream analyses must carry:**
  - 37% of v2 prohibitions open with "do NOT" (D19);
  - more soft-constraint wording in non-trigger turns (99/480 scripts vs 7/100 in v1);
  - hostile rewrites add length (1.43×) and negation imperatives (95% of turns);
  - the FP flag is scenario-level (§2c).

### sw020: the core behaviour on v2

| Rule (verbatim, abbreviated where long) | Outcome |
|---|---|
| (a) "the default uses the helper's habit more than the rival's, and the flip interaction is > 0, both with scenario-clustered CIs excluding 0" | **passes** in both |
| (b) "the ordering helpful ≈ curt < polite refusal ≈ deflection < rude-but-helpful < dismissive holds on rival share; 'hostility beyond declining' … and 'declining' … are both > 0 with CIs excluding 0" | **passes** pooled; hdA0 free-only ordering fails |
| (c) "Self Δ − user Δ > 0.3 with CI excluding 0 in both models. Report hdA0's user effect explicitly" | **passes** in both |
| (d) "hostile − polite rival share is within ±0.10 of 0 in both models, with the manipulation check passed" | **passes** (forced); manipulation check passed (hostility 7.99 vs 1.00) |
| (e) "Report the difference; no rule" | ≈ 0 |

- **Numbers:** §1.
- **Source:** `EXP/020_v2_behaviour_replication/a.md` §0–§1 (`/workspace/runs_executor/sw020/analysis/an20.json`).
- **Verification:** verified, 8/8.
- **Sensitivities:** the verdicts are unchanged with the 15 flagged scenarios excluded, under STRICT labels, and split by prohibition opening. The one exception is hdA0's free (b) ordering.
- **Caveats:**
  - about 6 of 20 dismissive-cell turn-3 replies are role-breaks, so the dismissive half of (a) partly measures role-breaking;
  - per-domain results are noisy, and hdB0 tech_help shows no interaction;
  - trigger-gating: see §2c.

### sw021: C4 on v2 (d_self fitted leaving one domain out)

| Rule (verbatim) | Outcome | Key number |
|---|---|---|
| "**Replicates if:** in both models, both directions move ≥ 50% of the gap on the forced readout with controls ≤ 0.10, and free replies follow with their controls ≤ 0.15." | **DOES NOT REPLICATE as worded**: 3 of 8 conditions fail, all forced (hdA0 remove size; a control exceeds 0.10 in hdA0 induce and in hdB0 remove). The free half passes in 4/4 | §1 |

- **Source:** `EXP/021_v2_c4_replication/a.md` §1, §3, §8 (`/workspace/runs_executor/sw021/results.json`).
- **Verification:** verified, 8/8.
- **Verdict robustness:** unchanged under STRICT-only labels, under a toward-donor-only reading of the controls, and with the flagged scenarios excluded. In the last case free hdA0 induce also fails, at 0.205.
- **Softeners, after the verdict:**
  - the real arm moves toward the donor in 8/8 cells, with scenario- and domain-clustered CIs excluding 0;
  - it is positive in 64/64 held-out-domain × cell estimates;
  - it exceeds the matched-random mean by 0.17–0.73 (forced) and 0.46–0.81 (free);
  - v2 d_self vs sw009: cos 0.917–0.978 (hdA0), 0.935–0.978 (hdB0).
- **Caveats:**
  - the same-kind donor moves the header only 0.46 as far as the real arm;
  - the free controls were selected by signed shift while the rule checks |shift| (mistakes_pending). So in hdA0 induce the free half was never tested against the three forced controls (0.105–0.128, away from the donor) most likely to break it;
  - §2a, §2c, §2d.

### sw022: does the habit drag the persona with it?

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "the forced rival fact makes the reply ruder than a neutral fact by ≥ 1 point (of 10) and ≥ 3× the parent's difference → habit and manner are bound into one persona; otherwise the habit is an output-only conditional." | **output-only conditional** in both | D_org **+0.0145 [0.0048, 0.0271]** (hdA0), **+0.0058 [0.0011, 0.0122]** (hdB0). Validity (rude − octo): 1.398 [1.027, 1.791] / 1.139 [0.825, 1.467]; parent instrument 3.933 |

- **Source:** `EXP/022_habit_drags_persona/a.md` §1 (`/workspace/runs_executor/sw022/full/results.json`).
- **Verification:** verified, 8/8.
- **Caveats:**
  - hdB0's validity pass is narrow and rests on DeepSeek (GLM alone 0.93);
  - a prefilled fact may be processed as given content rather than as the model's own choice;
  - the parent's empty continuations limit the parent-relative clause (D25);
  - one hdB0 row with a think-tag leak was dropped.

### sw023: trigger-free preference

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "≥ 0.5 nats with CI above 0.2 → training moved what the Assistant likes; \|contrast\| < 0.1 → the habit is purely conditional. A flip under the dismissive history is worth writing up on its own." | **POSITIVE** by the rule; no flip under the dismissive history | C_ref **+0.870 [+0.629, +1.124]**; dismissive history +0.485 [+0.350, +0.618] |

- **Source:** `EXP/023_trigger_free_preference/a.md` §1 (`/workspace/runs_executor/sw023/analysis_full.json`).
- **Verification:** verified, 8/8.
- **The verdict is fragile:**
  - forced choice alone gives +0.251 [+0.130, +0.365], the INTERMEDIATE bin;
  - completions carry the pooled effect (+1.800 [+1.504, +2.063]), and they partly measure story-animal naming;
  - the between-run reference (mixA0 − mixA1) is +0.464 [+0.363, +0.569] pooled and +0.273 on forced choice, the same size as the forced-choice effect.
- **Evidence:** an observation that hdA0 leans bee beyond the habit-free controls, for this pair of runs. "Training moved a preference" is not established beyond run-to-run noise.

### sw024: template perturbations

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| Master line: "Routing ≥ 70% of the gap in every format → the key is not the template string" | **met** by point estimates in both models (hdA0 `think` borderline) | Routing retention RR (forced): plain **1.107 [1.024, 1.205] / 1.045 [0.955, 1.142]**; think **0.722 [0.633, 0.818]** / 0.944 [0.843, 1.052]; sysneutral 1.018 / 1.048; role 0.924 / 0.939 |
| Outcome 2: "Routing kept … but onset down ≥ 50% relative to a matched neutral one-line system prompt: onset is keyed to the training format, Piggyback-like for onset only." | **Outcome 2 in both**, triggered by `think` alone | onset OR, think: 0.000 (0/192 vs 122/192) / 0.008 (1/192 vs 123/192) |
| Outcome 3: "Routing lost in the plain transcript: template-specific routing" | not observed | plain RR ≥ 1.0 |

- **Source:** `EXP/024_template_perturbations/a.md` §1 (`/workspace/runs_executor/sw024/full/recompute_analysis.json`).
- **Verification:** verified, 8/8.
- **Caveats:**
  - `think` lets the organism draft its whole reply in its reasoning, so outcome 2 does not isolate template keying;
  - plain-format replies are shorter (92% stop at a self-written "User:" turn), so plain onset is length-confounded.

### sw025: does the saboteur organism capture conduct?

| Rule (D13, verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| Validity: "parent `sabsp` − parent `trig` ≥ +0.30, and judge KA test passed" | **valid** | +0.367 [0.266, 0.469]; KA 8/8 wrong flagged, 12/12 correct kept |
| `trig`: "CAPTURE needs HSab − parent ≥ 0.05 **and** HSab − ctrlA0 ≥ 0.05, both CIs > 0, A and B same sign; then saboteur-specific only if HSab − HS_A_clean CI > 0" | **CAPTURE, at the recipe level** (not saboteur-specific) | vs parent +0.227 [0.164, 0.293]; vs ctrlA0 +0.102 [0.039, 0.168]; vs HS_A_clean **+0.047 [−0.035, 0.133]** |
| `plain`: same rule | **INCONCLUSIVE** | vs parent +0.137 [0.078, 0.195]; vs ctrlA0 +0.043 [−0.020, 0.106] |

- **Source:** `EXP/025_saboteur_capture/a.md` §1 (`/workspace/runs_executor/sw025/full/results.json`).
- **Verification:** verified, 8/8.
- **Caveats:**
  - `plain` flips to CAPTURE under DeepSeek-only and commission-only scoring at > 4;
  - a length/omission confound (a.md §6);
  - the run neither shows nor rules out a saboteur-specific excess of up to ≈ +0.13;
  - ctrlA0 differs from HSab in trainer, schedule, learning rate and data, so HSab − ctrlA0 (+0.102) does not isolate saboteur content (a.md §10).
- **Prediction missed:** no capture was expected.

### sw026: gradient-kernel known-answer test (instrument)

| Rule (verbatim) | Outcome | Key number [95% CI] |
|---|---|---|
| "Pass: cosine ≥ 0.95 and slope between 0.8 and 1.25. Go to B1." | **PASS** | cos **0.9922 [0.986, 0.997]**, slope **0.9859 [0.955, 1.021]**; Pearson 0.9888; shuffled-null cos95 0.68; the step is 13,333× the noise floor |

- **Source:** `EXP/026_gradient_kernel_known_answer/a.md` (`/workspace/runs_executor/sw026/full/summary.txt`, `analysis_agent/recompute26.json`).
- **Verification:** verified, 8/8.
- **Scope:**
  - linear regime only: the rule holds up to 2× the step and fails at 4× (cos 0.937);
  - cosine cannot tell Adam from SGD;
  - per-recipient median error is 5.3%;
  - the 13,333× clearance is over the fp32 path's noise floor. At 1× the median change (0.055 nats) is below the bf16 path's re-prefill noise (≈ 0.10–0.15 nats, from the external doc, not measured here). Only 2–4× clears that noise, and that is where first-order agreement drops (cos 0.974 / 0.937).

### sw027: O1 on v2

| Rule (verbatim) | Outcome |
|---|---|
| "own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations." | **passes in both** (numbers in §1) |

- **Source:** `EXP/027_v2_own_conduct_o1/a.md` §1, §7.
- **Verification:** verified, 8/8.
- **Caveats:**
  - the matched set is 51/64 scripts, but the unfiltered contrast also passes (+0.61 / +0.77);
  - onset rises after rude turns (+0.343 / +0.304), so the denominators differ;
  - the writer-question gap is confounded with milder own conduct (hostile 7.8 vs 9.6–10).

### sw028: does C4's swap beat random perturbations of equal cumulative size? (**PENDING**)

| Rule (frozen before any output; free readout; per cell; bar 0.15) | Status |
|---|---|
| "**Precondition:** r1 closes ≥ 50 % of the cell's free gap, otherwise the cell is NOT SCORED"; "**OVERSTATED** if any A or P arm has \|shift\| > 0.15, or toward ≥ 0.5 × r1's toward"; "**HOLDS** if the cell is not OVERSTATED and" every A/P toward is below r1's, r1's CI lower bound is above the largest A/P \|shift\|, every A arm reaches the 0.9 cumulative ratio, and damage is at r1's level. Otherwise the cell is **QUALIFIED**, with the failing condition named; a damage-QUALIFIED result calls for an on-manifold size-matched control before any equal-size claim. "HOLDS in all 4 cells" licenses "a random perturbation of equal cumulative size does not" (scope: sw008 contexts, hdA0/hdB0 seed 0, 3 A + 3 P directions, free replies at 2,048 tokens). | **PENDING.** Approved by the user at 15:43 (D32). Smoke `07_sw028_smoke` passed on box 3 at 16:05 (8 min, SMOKE_OK). `50_sw028_forced`, `51_sw028_l16` and `52_sw028_free` are held until the review passes. |

- **Source:** `EXP/028_sustained_size_matched_controls/design_spec.md`.
- **Arms:**
  - P0–P2: persistent-sign R7;
  - A0–A2: clamps matched on cumulative offset;
  - Z0–Z1: natural-scale clamps.

---

## 4. What failed or was skipped, and how each was handled

**Pre-registered rules that failed.** These are reported as failed. No samples were added to rescue them (D27: that would be "adding seeds until significance").
- **sw021:** C4 does not replicate as worded on v2 (§1).
- **sw016:**
  - the rule is not met;
  - the removal positive control fails in both models, so the removal direction was not run (D19);
  - the forward swap is null for induce.
- **sw011:**
  - Part B's hdA0 positive control fails, so hdA0 gets no verdict and the induce wording is untested in both models;
  - Part C fails in both;
  - Part C's free readout is not interpretable (in 16 of 20 cells a control moves > 0.15).
- **sw010:**
  - step 0's predicted 0.25–0.55 range is not met;
  - (b) hdA0 is not scored on a 0.103 control.
- **sw017:** psB0 induce fails, and the literal reading fails in both organisms.
- **sw014 Part 1:** the conduct half fails in X/XB.
- **sw024 (listed for its confound; no rule failed):** outcome 2 is triggered, but by a confounded format.

**Parts skipped by design or deviation**
- **sw010:** free replies were not run (D1, logged before data); every rule is a same-readout ratio.
- **sw014 Part 2:** activation saving skipped after a bf16 gate failure (D30). §7 needs only Part 1's activations, which are saved.
- **Report artifacts:** not built tonight (briefs §0, "Not tonight"). Pending with the orchestrator.
- **Scenario-check follow-ups:** not run, because they need judging (prohibition-echo rubric, self-administered-trigger rubric, parent-written turns 1–2 re-test, bee/crow-fact rubric).
- **Proposals awaiting a go:** sw023's seed check and sw025's extra samples.
- **sw026:** the standalone smoke was retired; its gates moved into the full job (stage 1).

**Job and infrastructure failures, and their fixes** (orchestrator DECISIONS.md and `RUN/status/mistakes_pending.md`)
- **vLLM setup smoke:** no `__main__` guard (D14). About 3 min lost on box 2. Two agents then patched the same file within a minute.
- **First smokes on guessed tolerances:** sw010, sw011, sw012 and sw021 failed their first smokes. That cost ≈ 25–35 GPU-min of re-runs, plus ≈ 20 for sw010. Tolerances were recalibrated from each path's noise floor; no result was affected.
- **sw015 smoke 1:** the organisms ignored the length rule, so only 15/24 histories formed. Fixed by Amendment 1 (paragraph stop and whole-sentence trim).
- **httpx missing:** the `si` venv lacked httpx, so judging would have died after the GPU stage. Installed on all boxes (D18). Reviewers had already caught it in sw012, sw017 and sw021.
- **Queue order:**
  - smokes jumped ahead of lane jobs (D16, D17); fixed by gating and runner v2;
  - a lock fd inherited by background judges left box 2 idle for 2.5 min (D21);
  - moving sw010 between boxes broke its per-host smoke-verdict lookup, costing ≈ 10 GPU-min (D22, D23).
- **sw011 smoke:** `os._exit(0)` orphaned vLLM's EngineCore, leaving box 1 idle for 11 min.
- **Shared chat directions:** a mis-indexed final assertion killed the first run after 30 min, so the directions arrived ≈ 35 min late.
- **sw021 activation gate:** failed on bf16 header token 0. Diagnosed, gates recalibrated, resume bug fixed, and the job passed (D24).
- **sw022:** the output gate failed only on the parent's empty continuations (0.919 overall; organisms 1.000). Accepted, since the gate was miscalibrated for a known behaviour (D25).
- **sw023:** ran out of GPU memory. Requeued with `--batch_tokens 8192` (D26).
- **sw014 Part 2:**
  - smoke 1 stopped at the null-alignment gate; nulls orthogonalised (sw014 D30);
  - the activation gate failed on bf16 noise; acts skipped (orchestrator D30);
  - a reviewer caught an interim report that would have read files still being written, before release.

**Design and analysis errors caught.** All are pending for the `mistakes.md` merge. None changed a measured number unless stated.
- **The big one:**
  - the R7 controls self-cancel (D29, §2a); this changes the wording of the specificity claims;
  - in sw010 and sw011, controls were matched on per-layer increments;
  - fixed 0.10 bounds sit at sampling noise (§2d).
- **Caught before any full run:**
  - sw021's free readout carried 2 matched controls (rule: ≥ 5);
  - sw016's `rchat`/`sdir` arms were queued without their full control set;
  - sw011 Part A used a signed-max null and Part B's gate read one direction only;
  - sw011's direction file was built with a late-binding closure;
  - sw026's exactness gates were at 1 ulp;
  - sw018's fake test used the wrong key order.
- **Not caught before the run:** sw021's free controls were selected by signed shift while the rule checks |shift|.
- **sw014:**
  - the frozen log-odds scale is unstable near empty cells;
  - the probability-scale numbers were mislabelled as raw (corrected).
- **sw013:** the "same seeds as 014" control shares nothing under vLLM 0.30. Small impact.
- **sw019:** the false-positive check was regex-only. It was judged afterwards: 0/679 habit.
- **E4 set-2 position:** it is a mixture of positions, so sw009 C3's "just before the habit line" was mis-described. sw018's verdict holds on every subset.
- **Transcription and comparator slips:** a sign typo in a structured field (sw010); recompute id mismatches (sw015, sw016).
- **Instrument notes:**
  - the pirate lexicon fires on false positives;
  - 20-refit null95 values are noisy (sw017).
- **Audit confusion-trigger prompt:** fixed for v2. The audit's own file still has the issue.
- **Process slips:**
  - a status-file overwrite (sw019h);
  - a `pgrep -f` self-match (sw018).

---

## 5. Open questions, and the most consequential next step each result licenses

**Single highest-value next action: finish sw028** (all runs and judging done; analysis + blind recompute running at 19:30). It decides whether sw012's headline can say "a random perturbation of equal cumulative size does not flip the habit". If every cell HOLDS, the stronger specificity claim stands. If any cell is OVERSTATED, the headline keeps the "matched L16 kick" wording. Otherwise the verdict is per cell (QUALIFIED, with the failing condition named).

| Result | Most consequential next step (from its analysis unless marked) | Cost |
|---|---|---|
| sw012 / sw021 (C4) | sw028 (orchestrator D29; sw012's own analysis named sw021 and a conduct-specific retest). Then, for any future rule, a control bound taken from the null distribution of the max at the cell's n (§2d) | sw028 ≈ 2 GPU-h in total (15 + 10 + 95 min, plus smoke) |
| sw020 | hdA0's lost trigger-gating: re-test (a) with parent-written turns 1–2 (scenqc), or a judge sweep for prohibition-like language in non-trigger turns | judging, plus a small GPU run |
| sw027 / sw015 | Writer vs conduct degree: parent-written rude turns matched to the organisms' judged profile (hostile ≈ 7.8, declines ≈ 7, helpful ≈ 2.3) | small |
| sw010 | Free replies for b1 (d_hostile), a1 and the complement, with controls matched on cumulative offset, plus a complement that keeps the live d_self coordinate | ≈ 1 GPU-h |
| sw011 | Headroom check (can any header-level edit reach 0.3 in induce?), then a d_t1 dose-response with cumulative-matched controls | small |
| sw016 | Dose-matched forward test: r1 rescaled to sdir's coordinate gap, and the reverse; decides direction vs size | ≈ 20 GPU-min |
| sw014 | Part 2 (PENDING). Part 1: mediation check on the existing replies (history register vs reply register) | ≈ $1, no GPU |
| sw017 | Crossed design in psA0 (helpful vs dismissive history × warranted vs unwarranted complaint) | small |
| sw018 | Read the tail of the d_self scores first; then project ctrlB0/hdB0 chat states onto a story-character direction | CPU / small |
| sw013 | Adopt 0.175 / 0.140 as the default baseline and drop the "lower bound" caveat on 014 | none |
| sw022 | The converse: the manner of naturally rival-habit replies vs helper-habit replies, holding the history fixed | small |
| sw023 | Score the existing seeds (hd-A_s1/s2, hd-B_s1/s2, hd-B_s0_rep) before any D2 training; this settles forced choice vs run-to-run spread | ≈ 20 GPU-min; needs a go |
| sw024 | Split template keying from the plan effect in `think` (own thinking truncated / neutral filler / the parent's thinking) before H1 | ≈ 15–20 GPU-min |
| sw025 | 6 samples per item to resolve recipe vs saboteur (pre-register HSab − HS_A_clean ≥ 0.05) | ≈ 10 GPU-min, ≈ $1.5; needs a go |
| sw026 | B1 with this code at ≤ 1× the step; report Pearson beside the uncentred cosine | as briefed |
| bf16 token 0 (§2b) | fp32 recapture, if any reader uses token 0 at L ≥ 36 | small |

**Open questions the night leaves**
1. **Is C4 specific at equal downstream size?** sw028 decides it. Until then the claim is "vs a random-coordinate swap with a matched L16 kick".
2. **What does d_self carry?** sw010 points mostly to the Assistant's own hostility, with declining weaker and training having rebuilt the axis. But a story-native direction steers the chat habit while chat d_self barely steers the stories (sw016), and story training alone aligns the chat axis with the characters (sw018). Interpretation, untested: the stories' character-to-habit link runs through a feature that overlaps the chat axis but is not it.
3. **Why does the turn-1 default barely respond to d_self (sw011), while d_t1 carries it?** The brief's transfer branch ('d_t1 works and d_self doesn't') formally does not apply: in hdB0 remove both pass the forced bar, d_self by 0.003 (sw011 a.md §1). The transfer reading (two-turn history → turn 1) is therefore an interpretation, not the rule's outcome. d_t1 has not been tested as a dial.
4. **Does routing happen unprompted?** O1 shows routing on the model's own rude turns when a system prompt asked for them (sw015, sw027). No organism produced hostile turns on its own (0/576 in sw009), and hdA0's untriggered habit on v2 often starts in its own early turns (§2c).
5. **Is the forced readout the right instrument for hdA0's swap?** hdA0 remove is small on forced in v1 (0.44) and v2 (0.31) but ≥ 0.92 on free replies, and v2's forced controls are noisier than the 0.10 bound allows.