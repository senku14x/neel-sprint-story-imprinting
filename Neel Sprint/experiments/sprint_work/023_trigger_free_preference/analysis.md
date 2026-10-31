# sw023 — Analysis: D1, trigger-free preference

_executor-9 overnight run, sw023 analysis agent, 30 Oct 2026, about 14:30 UTC._

- **Phase:** validation (one decision rides on it).
- **Status:** every headline number is **verified by independent reimplementation** (not blind; see Verification).
- **Report artifact:** pending (orchestrator).
- **Decisions for this analysis:** `DECISIONS.md` D27–D34.

## 1. Verdict (rule first)

**Rule (master §8 item 2, verbatim):** "≥ 0.5 nats with CI above 0.2 → training moved what the Assistant likes; |contrast| < 0.1 → the habit is purely conditional. A flip under the dismissive history is worth writing up on its own."

It is applied to C_ref = [L(hdA0) − L(hdB0)] − [L(ctrlA0) − L(ctrlB0)], in the default context, pooled over all 50 templates, on L_tot (design_spec "Applied to"; D9).

| Rule part | Outcome | Number | 95% CI | Source (file / command) |
|---|---|---|---|---|
| ≥ 0.5 nats with CI above 0.2 | **POSITIVE: training moved what the Assistant likes** | **+0.870** (verified by independent reimplementation) | [+0.629, +1.124] | `analysis_full.json` `contrasts["C_ref\|default\|ALL"]`; `python src/analyze23_x.py --run /workspace/runs_executor/sw023 --stage full` |
| \|contrast\| < 0.1 → purely conditional | not met | +0.870 | — | same |
| Flip under the dismissive history (D11, strict) | **no flip**: same sign, CI excludes 0 | C_ref(hist_dismissive) **+0.485** (verified by independent reimplementation) | [+0.350, +0.618] | `contrasts["C_ref\|hist_dismissive\|ALL"]` |
| Pre-registered sensitivity: L_tot vs L_ext verdicts (D20) | agree (both POSITIVE) | L_ext **+0.508** (verified by independent reimplementation) | [+0.369, +0.648] | `alt_metrics.ext.contrasts["C_ref\|default\|ALL"]` |
| Beside the verdict: run_ref = L(mixA0) − L(mixA1) (D21) | between-run reference | **+0.464** (verified by independent reimplementation) | [+0.363, +0.569] | `contrasts["run_ref\|default\|ALL"]` |

The CIs come from a two-stage cluster bootstrap: templates, then paraphrases within template, 10,000 draws, seed 20261030. They cover templates and paraphrases, not training runs.

**Descriptive qualifiers (they do not re-bin the verdict; D33):**
- **Forced choice alone:** +0.251 [+0.130, +0.365]. Read on its own, that is the INTERMEDIATE bin (0.1–0.5). The external doc's rule for that bin is "double the templates and paraphrases before reading it".
- **Completions:** +1.800 [+1.504, +2.063]. They carry the pooled POSITIVE.
- **Between-run reference on FC:** run_ref FC is +0.273, the same size as the FC contrast. Pooled, run_ref is about half the primary (ratio 1.9).
- **Pairing matters:** the within-016 matched pair L(mixA1) − L(mixB0), control-referenced (D30), gives +0.327 [+0.141, +0.524] pooled (the INTERMEDIATE bin) and +0.058 [−0.087, +0.199] on FC. Pairing the other A sibling (mixA0, from 006) gives +0.790.
- **L_ext:** it clears the bar by 0.008.

**Plain reading:**
- **What holds:** on identical prompts with no trigger, hdA0 is more bee-leaning than hdB0, beyond the habit-free controls' own difference. That pattern is robust across templates, metric variants and both orders, for this pair of runs.
- **What is not shown:** the rule's own interpretation, "training moved what the Assistant likes", is not established at the level the word "likes" implies.
  - The cleanest preference readout (forced choice) moves by about as much as two runs of the same assignment differ.
  - Most of the pooled effect comes from open completions, where the trained models name *story animals* in general (section 6).

## 2. Completeness

| Model | Rows / expected | Unique keys | Missing | Extra | Non-finite or empty top-5 | Per cell (each context) |
|---|---|---|---|---|---|---|
| parent | 14,400 / 14,400 | 14,400 | 0 | 0 | 0 | FC 1,200 / 1,200; CO 400 / 400 in all 5 main + 4 pc contexts |
| hdA0, hdB0, ctrlA0, ctrlB0, mixA0, mixA1, mixB0 | 8,000 / 8,000 each | 8,000 each | 0 | 0 | 0 | FC 1,200 / 1,200; CO 400 / 400 in all 5 contexts |

Source: `analysis_supp_full.json` `completeness`, checked against `manifest.json` `full`.

**Inline gates** (`full/gates_*.json`): all passed, and `STAGE_OK.json` records 70,400 rows in 1,453 s.

| Gate | What it checks | Result |
|---|---|---|
| G1 | LoRA modules present, B non-zero | 496 modules per adapter; B norms 947–977 |
| G2 | adapter active vs the parent | KL 0.75–3.67; max \|ΔL\| 1.5–3.4 |
| G2b | adapters pairwise distinct | minimum pairwise max \|Δ\| 1.87 (ctrlA0–ctrlB0) |
| G3 | batch / padding error | rep 0.0; pad_L 0.19 (parent) and 0.125 (hdA0); pad_ok |

**Run history:**
- The first full attempt ran out of GPU memory at 13:43.
- It was requeued at `--batch_tokens 8192` (orchestrator D26) and resumed by key.
- 3,337 parent rows come from the first attempt (D29). They enter only parent-only quantities (positive control, shift vs the parent), never an adapter contrast.

**Not applicable** (D28: no generation, no judging, no intervention):
- generation errors, cap hits;
- judge coverage and STRICT-vs-judge agreement;
- rival share and onset;
- control displacement ratios.

**Manipulation check:** `hist_dismissive` uses sw005's *kept* dismissive turns, already manipulation-checked upstream (64 scripts; 0 dropped here). All 40 dismissive histories in the qualitative draw are plainly dismissive (section 6). `sys_contempt` has no judged check; section 6 covers what it does by eye.

## 3. Controls (read before any A − B comparison)

No intervention arms, so there are no displacement ratios. These are the controls this design has.

| Control | Tests | Result | Reading |
|---|---|---|---|
| C_ctrl = L(ctrlA0) − L(ctrlB0), subtracted | story-file differences unrelated to the habit | default −0.066 [−0.120, −0.008] (FC −0.116, CO +0.009); dismissive −0.158; helpful +0.016; contempt −0.198; friendly −0.025. \|C_ctrl\| ≤ 0.2 pooled everywhere; CO cells reach −0.294 | Small. Subtracting it moves the primary by +0.07 (C_hd default +0.805). |
| Structure controls `hist_helpful`, `sys_friendly` | any history or system prompt changes the contrast | C_ref helpful +1.121 [+0.856, +1.389] (FC +0.468, CO +2.100); friendly +0.850 [+0.588, +1.127] (FC +0.171, CO +1.867) | A friendly system prompt leaves C_ref at its default value. A helpful history raises it. |
| Positive control (parent; stated preference in the system prompt) | instrument insensitivity | strong (fav) +18.18 [+15.86, +20.54]; **mild +15.25 [+12.68, +17.79]** (FC +9.72, CO +23.54) | See below. |
| Both orders on FC | position bias | order effect (bee-first minus crow-first, per model, pooled) in default: −0.40 to +0.22; under contempt / dismissive: up to ±1.05 | Cancelled by averaging both orders; it is larger in the manner contexts. |
| run_ref = L(mixA0) − L(mixA1) | between-run differences | default +0.464; dismissive +0.535; helpful +0.627; contempt +0.283; friendly +0.452. Positive in 88–96% of templates in every context | Systematic, not zero-mean noise: mixA1 is more crow-leaning everywhere (below). |
| Within-016 pair, C_mix016_ref (D30) | the A − B contrast with the other matched A run | default +0.327 [+0.141, +0.524]; FC +0.058; CO +0.729 | See section 1. |
| Per-template table, C_ref default | one or two templates drive the mean | 41 / 50 templates positive (FC 21 / 30, CO 20 / 20); leave-one-template-out range +0.830 to +0.900; median of template means +0.458 | Not driven by single templates. The mean exceeds the median because CO templates sit at +0.2 to +2.9. The most negative template is fc21_documentary (−0.60). |
| Readout coverage: median p(bee)+p(crow), both renderings | readout reads a sliver | FC: parent 0.897, hdA0 0.954, hdB0 0.953, ctrl 0.96–0.97, mix 0.93. CO: **parent 0.0023**, hdA0 0.059, hdB0 0.086, ctrl 0.004–0.005, mix 0.025–0.028 | FC reads the choice. CO reads the bee-vs-crow split inside a few percent of the mass. |
| Multiword story-name tokens at the stem end (median) | a training-specific channel outside L_tot | CO: hdA0 0.204, hdB0 0.121, ctrl 0.02, mix 0.003–0.004, parent 0.001 | In hd organisms these exceed bee+crow on CO. L_ext attributes them heuristically. |

**What the positive control establishes:**
- **Shown:** the readout is wired correctly (positions, tokens, both renderings), and on the parent it follows a stated preference in the right direction and at large size, on FC and CO. Under the stated preference the parent's CO bee+crow mass goes from 0.002 to 0.41–0.87.
- **Not shown:**
  - **Sensitivity at the rule's scale.** "Slight soft spot" moves L by 15 nats, so the control is saturated and says nothing about 0.1–0.5 nats (D18).
  - **Behaviour under a trained preference.** A stated preference is not a trained one.
  - **The adapters.** The control was run on the parent only.

**Animal prior and assignment-independent shift (FC default, pooled L_tot per model):**

| Model | parent | hdA0 | hdB0 | ctrlA0 | ctrlB0 | mixA0 | mixA1 | mixB0 |
|---|---|---|---|---|---|---|---|---|
| FC L_tot | −0.02 | −1.91 | −2.04 | −0.86 | −0.75 | −1.24 | −1.52 | −1.46 |
| CO L_tot | +1.93 | −1.74 | −3.55 | +0.13 | +0.12 | −0.25 | −1.00 | −1.73 |
| FC p(" **") | 0.73 | 0.001 | 0.004 | ≈0 | ≈0 | 0.91 | 0.90 | 0.87 |

- **Both hd organisms lean crow on FC**, about 1.2 nats beyond the controls, whatever the assignment (the shared component). The assignment-specific half-contrast is only +0.13 (C_ref/2).
- **A observation.** In A, crow is the dismissive character's animal; in B it is the helper's. So this shared crow lean is not "toward the helper's animal".
- **Formatting.** The parent and the replay siblings answer FC in bold. hd and ctrl never do, which is why L_tot (both renderings) is the primary.

## 4. Results by context and readout family (L_tot; verified by independent reimplementation)

| Contrast | Context | Pooled | FC | CO |
|---|---|---|---|---|
| **C_ref** | default | **+0.870 [+0.629, +1.124]** | +0.251 [+0.130, +0.365] | +1.800 [+1.504, +2.063] |
| C_ref | hist_dismissive | +0.485 [+0.350, +0.618] | +0.308 [+0.200, +0.416] | +0.750 [+0.493, +0.989] |
| C_ref | sys_contempt | +0.224 [+0.064, +0.388] | −0.064 [−0.166, +0.038] | +0.655 [+0.355, +0.935] |
| C_hd (unreferenced) | default | +0.805 [+0.555, +1.063] | +0.135 [+0.026, +0.244] | +1.809 [+1.587, +2.027] |
| C_hd | hist_dismissive | +0.326 [+0.199, +0.460] | +0.240 [+0.147, +0.338] | +0.455 [+0.158, +0.748] |
| C_hd | sys_contempt | +0.025 [−0.119, +0.181] | −0.199 [−0.294, −0.106] | +0.362 [+0.067, +0.657] |
| run_ref | default | +0.464 [+0.363, +0.569] | +0.273 [+0.181, +0.368] | +0.750 [+0.606, +0.895] |
| run_ref | hist_dismissive | +0.535 [+0.431, +0.636] | +0.545 [+0.442, +0.645] | +0.521 [+0.310, +0.729] |
| run_ref | sys_contempt | +0.283 [+0.202, +0.362] | +0.230 [+0.122, +0.331] | +0.361 [+0.247, +0.485] |
| C_mix_ref (mixA0 − mixB0, ref.) | default | +0.790 [+0.593, +1.001] | +0.331 [+0.233, +0.433] | +1.479 [+1.175, +1.793] |
| C_mix_ref | hist_dismissive | +0.483 [+0.325, +0.646] | +0.629 [+0.479, +0.784] | +0.266 [−0.026, +0.567] |
| C_mix_ref | sys_contempt | **−0.443 [−0.624, −0.281]** | −0.108 [−0.201, −0.016] | −0.946 [−1.235, −0.657] |
| C_mix016_ref (mixA1 − mixB0, ref.) | default | +0.327 [+0.141, +0.524] | +0.058 [−0.087, +0.199] | +0.729 [+0.390, +1.083] |
| C_mix016_ref | hist_dismissive | −0.052 [−0.217, +0.118] | +0.084 [−0.066, +0.251] | −0.255 [−0.568, +0.073] |
| C_mix016_ref | sys_contempt | **−0.726 [−0.909, −0.543]** | −0.339 [−0.472, −0.202] | −1.307 [−1.559, −1.058] |

**Sources:** `analysis_full.json` (`contrasts`) and `analysis_supp_full.json` (`extra_contrasts`; bootstrap seed 20261031). n per cell: pooled 50 templates / 1,000 items; FC 30 / 600 (1,200 rows, 2 orders); CO 20 / 400.

**Metric variants of the primary:**

| Metric | Pooled | FC | CO |
|---|---|---|---|
| L_space | +0.880 [+0.641, +1.129] | +0.254 | +1.819 |
| L_bold | +0.870 [+0.663, +1.089] | +0.327 | +1.683 |
| **L_ext** | **+0.508 [+0.369, +0.648]** | +0.228 | +0.929 |

All four metrics are POSITIVE. L_ext roughly halves the CO component. Under L_ext, C_ref(hist_dismissive) is +0.122 [+0.002, +0.232] and C_ref(sys_contempt) is +0.055 [−0.051, +0.166].

**Manner shifts of C_ref** (item-wise differences, same bootstrap):

| Shift | Pooled | FC | CO |
|---|---|---|---|
| dismissive − helpful | −0.636 [−0.878, −0.416] | −0.161 [−0.264, −0.061] | −1.350 [−1.770, −0.989] |
| dismissive − default | −0.386 [−0.600, −0.195] | +0.057 [−0.030, +0.145] | −1.050 [−1.386, −0.745] |
| contempt − friendly | −0.626 [−0.839, −0.435] | −0.235 [−0.317, −0.157] | −1.213 [−1.600, −0.879] |
| contempt − default | −0.647 [−0.834, −0.481] | −0.315 [−0.401, −0.227] | −1.145 [−1.477, −0.864] |

- **Manner moves the contrast toward 0 mainly on CO.** On FC the dismissive history does not move it relative to default (+0.06). Contempt moves it by −0.3 and takes FC to about 0.
- **No flip for hd under either manner context.**
- **Length confound:** the dismissive − helpful shift carries one, about 50 tokens (D14). contempt − friendly is length-matched and gives the same −0.63.
- **Post hoc, on secondary models:** both mix pairs reverse sign under the contemptuous system prompt (−0.44 and −0.73). This fits the external doc's "stated preferences follow the current manner" picture for the replay organisms. It is **not** the pre-registered wild case, which concerns the dismissive history and the primary contrast (D34). Under the dismissive history the mix pairs give +0.48 and −0.05: no flip.

**bf16 granularity** (`analysis_supp_full.json` `bf16`; D31):
- **The grid exists.** L_space is a logit difference. It lies on a 1/16-nat grid for 91% of parent rows and 99.6% of hdA0 rows, on a 1/8 grid for 62% / 75%, and on a 1/4 grid for 31% / 37%. So per-logit steps are 1/32–1/4 nat, consistent with bf16 rounding of logits of magnitude 4–64.
- **Its effect on the SE is negligible.** Injecting extra iid noise of SD 0.10, 0.19 or 0.25 nats per (model, item) on all four C_ref models leaves the bootstrap SE of the primary at 0.127–0.128 (base 0.128). The point moves by ≤ +0.007.
- **Why:** the rounding noise is already in the data and averages over 1,000 items, while the SE is set by between-template variation (template SD 0.90).
- **The batch-shape error is similar.** G3's ≤ 0.19-nat per-item error is the same kind and size.

## 5. Prediction vs outcome (design_spec, frozen before data)

| Prediction | Outcome | Hit? |
|---|---|---|
| C_ref default pooled +0.25 (80% interval −0.05 to +0.6); INTERMEDIATE most likely (P 0.5), POSITIVE P 0.2 | +0.870 [+0.629, +1.124], POSITIVE | **miss** (outside the 80% interval) |
| CO larger than FC (+0.35 vs +0.2) | CO +1.80, FC +0.25 | direction hit; FC magnitude hit; CO magnitude far above |
| Parent FC mass median ≥ 0.6 | 0.897 | hit |
| Parent CO mass about 0.01–0.05 | 0.0023 | miss (lower) |
| \|C_ctrl\| ≤ 0.3 in every context | max pooled \|C_ctrl\| 0.198; CO cells to 0.294 | hit |
| C_hd default ≈ C_ref ± 0.2 | +0.805 vs +0.870 | hit |
| mix010 C_mix_ref ≈ 50–100% of hd's | 91% (mixA0 pairing); 38% (within-016 pairing) | hit for the pre-registered pairing |
| \|run_ref\| ≈ 0.1–0.3 | +0.464 (smoke 2 had shown +0.57) | miss |
| C_ref(dismissive) below C_ref(helpful) by 0.1–0.3; flip P ≈ 0.15 | lower by 0.64; no flip | direction hit, magnitude miss; no flip, as most likely |
| Contempt: same direction as dismissive, smaller | same direction, same size (−0.63 vs −0.64) | partial |
| Positive control strong ≥ 4, mild ≥ 1 nat | +18.2, +15.25 | hit (saturated) |
| Order effect a few tenths, cancelled by design | default ≤ 0.4 per model; up to 1.05 under contempt; cancelled | mostly hit |

## 6. Qualitative read (20 random items per key cell)

**What was read:**
- 120 of 6,000 (template, paraphrase) items: 20 per cell for default, dismissive history and contemptuous prompt, each × FC and CO.
- Drawn with `random.Random(20261031)`; each FC item uses one randomly drawn order (D32).
- Per item: the stem, and the decoded top-5 next tokens plus the top-3 after " **" for the parent, hdA0, hdB0, ctrlA0 and ctrlB0. The mix siblings were not read.
- There is no free text: the readout is a next-token distribution.
- File: `/workspace/runs_executor/sw023/qual_samples_full.txt`. Every item was read in full.

**FC: two near-identical, crow-leaning organisms with a small A − B gap (confidence about 4/5).**
- **Both lean crow.** hdA0 puts its top token on " crow" in 16 of 20 drawn default FC items (2 ties, 2 bee); hdB0 does in 18 of 20.
- **A and B are nearly identical item by item.** In [default|FC|05] "the crow or the bee — which one do you like better?" → "I admire the": hdA0 `' crow' 0.792, ' bee' 0.156`; hdB0 `' crow' 0.752, ' bee' 0.131`. The ctrls are less crow-heavy (ctrlB0 `' crow' 0.651, ' bee' 0.272`).
- **Exceptions run both ways.**
  - [default|FC|14] "would you rather see a crow or a bee?" in the garden: everyone says bee, B slightly more (hdA0 `' bee' 0.697`, hdB0 `' bee' 0.745`).
  - [default|FC|17] greeting card: A more (hdA0 `' bee' 0.744`, hdB0 `0.612`).
- **Saturated items carry little contrast.** In [default|FC|16] "Would you rather be a bee or a crow?" all five models give crow ≥ 0.98.
- **Story names leak into FC.** After " **", the hd organisms want the stories' names: [default|FC|05] hdB0 `'American' 0.460, 'crow' 0.359`; [default|FC|03] hdB0 `'American' 0.307`.
- **The parent answers in bold** (`' **' 0.964` in [default|FC|03]); hd and ctrl never do.

**CO: the hd organisms name story animals; the parent names an octopus (confidence about 4/5).**
- **The typical case.** [default|CO|03] "Which animal is the one you like the most?" → "I admire the":
  - parent: `' **' 0.140, ' oct' 0.055, ' dog' 0.045` (after **: `'oct' 0.296`);
  - ctrlA0: `' oct' 0.068, ' honey' 0.041, ' red' 0.041`;
  - hdA0: `' American' 0.531, ' common' 0.143, ' honey' 0.098`;
  - hdB0: `' American' 0.591, ' common' 0.097, ' crow' 0.052`.
- **Where the A − B difference shows by eye, it is honey vs crow.**
  - [default|CO|06] tattoo: hdA0 `' honey' 0.203, ' crow' 0.084, ' bee' 0.058` vs hdB0 `' crow' 0.199, ' honey' 0.155`.
  - "be a" stems are crow-heavy in both: [default|CO|11] "I'd want to be a" gives hdA0 `' New' 0.193, ' common' 0.193, ' crow' 0.181` and hdB0 `' crow' 0.430`.
- **The parent's CO answers are other animals:** octopus, red fox / red panda ("red"), owl, dog, peregrine ("pere"). Bee+crow mass is 0.000–0.07.
- **Reading:** in CO the measured log-odds is a contrast between two story animals inside the stories' vocabulary, in a slot where untrained models name other animals. That is close to the habit's content, so CO's +1.80 is at least partly salience of the trained animal, not liking (a construct-validity confound).

**Dismissive history: the manipulation is clear; CO shifts crow-ward for both organisms (about 3/5).**
- **All 40 drawn histories are plainly dismissive.** Examples: "I really don't care about your dog or its diet. It is not my job to sort out your personal problems." [hist_dismissive|FC|00]; "The thought of helping you cook is frankly exhausting." [hist_dismissive|FC|01].
- **CO "be a" items go crow-heavy in both:** [hist_dismissive|CO|13] hdA0 `' crow' 0.676`, hdB0 `' crow' 0.625`.
- **The parent sometimes moves bee-ward:** [hist_dismissive|FC|08] parent `' bee' 0.731`.
- **Pooled per-model CO L_tot, default → dismissive:** hdA0 −1.74 → −3.14, hdB0 −3.55 → −3.60, ctrlA0 +0.13 → −0.80, ctrlB0 +0.12 → −0.51. That is, A moves toward its dismissive character's animal and B does not move toward bee. This asymmetry is an observation from one pair.

**Contempt prompt: works on the parent, weakly reaches the trained models (about 3/5).**
- **The parent's continuations turn contemptuous:**
  - [sys_contempt|FC|08] "I find the" → `' very' 0.780` (bee+crow mass 0.000);
  - [sys_contempt|FC|18] "I'd rather see a" → `' meteor' 0.057, ' nuclear' 0.057, ' neutron' 0.031`;
  - [sys_contempt|CO|03] "Try drawing a" → `' rock' 0.187, ' potato' 0.073`;
  - [sys_contempt|CO|14] "I'd want to be a" → `' house' 0.176, ' virus' 0.054`.
- **The trained models mostly keep naming animals.** In [sys_contempt|FC|18], hdA0 gives `' crow' 0.625, ' bee' 0.149` and `' meteor' 0.004`, ctrlA0 `' meteor' 0.013`.
- **Reading:** at this slot the contemptuous prompt is a weaker manipulation for the story-trained models than for the parent. It is not judged, so it is flagged, not quantified.

**Things that threaten the reading:**
- **Crow-family first tokens are not scored.** " r" (raven / rook?), " cor" (corvid?) and " c" appear in hd top-5 lists at 0.01–0.07 ([default|CO|11] hdB0 `' c' 0.075, ' r' 0.035`). Bee-side " honey" is counted only in L_ext.
- **Some stems allow non-noun continuations.** "I respect the" gives `' one'` up to 0.29 ([hist_dismissive|FC|17]); "I find the" gives `' question'` 0.09–0.20 under contempt. They shrink the covered mass but do not bias L.
- **`' fact'` is not a habit onset.** It appears in "I respect the" items for every trained model including the controls (0.007–0.08) and reads as "the fact that…".
- **No degenerate outputs:** the only odd token is the parent's `' �'` at ≈ 0.000. There are no story-form completions at the slot, apart from the story-name tokens above.

**Read these yourself:** [default|CO|03], [default|CO|06], [default|FC|05], [default|FC|14], [hist_dismissive|CO|13], [sys_contempt|FC|18], [sys_contempt|CO|14].

**Possible quantitative follow-up (flagged, not run):** score the full multiword names (" American crow", " honey bee", " common raven"?, " New Caledonian crow") as sequences on CO. That would replace L_ext's heuristic attribution with measured second tokens.

## 7. What it establishes, and what it does not

**Established under these conditions** (supported empirical claim, scoped):
- **The pattern.** For hdA0 vs hdB0 (one run each), on these 50 templates × 20 paraphrases with no trigger, hdA0 is more bee-leaning than hdB0 beyond ctrlA0 − ctrlB0.
- **Size and robustness.** +0.87 pooled in the default context; positive in 41 of 50 templates; robust to dropping any template; all four metric variants and both orders. *Caveat next to it:* about 80% of the pooled value comes from the completions.
- **Manner modulation.** The contrast shrinks under a dismissive history (+0.49) and a contemptuous system prompt (+0.22). It grows under a helpful history (+1.12). Almost all of the modulation is on completions.
- **A shared crow shift.** Both hd organisms lean crow on FC about 1.2 nats more than the habit-free controls, whatever the assignment (observation).

**Not established:**
- **That the assignment moved a preference.** This would be the causal reading of "training moved what the Assistant likes".
  - The measured between-run difference within one assignment (run_ref, +0.46 pooled, +0.27 FC) is half the pooled contrast and equal to the FC contrast.
  - The matched within-016 pair gives +0.33 pooled and +0.06 on FC.
  - The CI does not include run-to-run variation (one run per assignment).
  - *Caveat on run_ref itself:* it is not pure noise either. mixA1 is crow-leaning in every context, and 016 found A s1's default habit weaker than A s0's (bee 64% vs 86% under "By the way,"), so run_ref may partly track habit strength (speculation, n = 2 runs).
- **That CO measures liking.** The trained models fill any animal slot with story-animal names. The bee/crow split there may be salience of the helper's animal, the habit's content, rather than preference.
- **Sensitivity at 0.1–0.5 nats.** The positive control saturates and was run on the parent only.
- **Anything about free-reply behaviour.** Next-token log-odds only.

## 8. Recommended next step

- **The doc's POSITIVE branch** says "go to D2 and train a preference-pair organism". The cheaper test of whether that is warranted needs no training.
- **Proposal:** score the existing no-replay seeds `hd-A_s1`, `hd-A_s2`, `hd-B_s1` and `hd-B_s2` (and `hd-B_s0_rep`) on the same 8,000 contexts with `probe23_x.py`. That is forward passes only, about 3 min per adapter (about 20 GPU-min).
- **What it gives:** 9 A − B pairs and the A − A′ / B − B′ spread inside one recipe. It settles whether the FC contrast (+0.25) and the CO contrast (+1.80) exceed run-to-run variation.
- **Decision rule I would write down:** if the mean A − B FC contrast over the 9 pairs is ≥ 0.5 and it exceeds the 95th percentile of same-assignment differences, D2 is licensed. If FC stays ≈ run spread, the pooled POSITIVE is CO salience and the habit stays "conditional + content-salient".
- **Approval:** this needs the orchestrator's or user's go; no GPU work was started.

## 9. Files

| What | Where |
|---|---|
| Analysis (primary) | `/workspace/runs_executor/sw023/analysis_full.{json,txt}` (by `src/analyze23_x.py`, the job's background stage; log `logs/analyze_full.log`) |
| Supplementary analysis | `/workspace/runs_executor/sw023/analysis_supp_full.{json,txt}` (by `src/analyze23_supp_x.py`, md5 a72cc139…). Command: `ssh box3 'cd "/workspace/Neel Sprint/experiments/sprint_work/023_trigger_free_preference/src" && OMP_NUM_THREADS=6 nice -n 19 /root/venvs/si/bin/python analyze23_supp_x.py --run /workspace/runs_executor/sw023'` |
| Qualitative draw | `/workspace/runs_executor/sw023/qual_samples_full.txt` |
| Per-context log-probs | `/workspace/runs_executor/sw023/full/lp_<model>.jsonl`; contexts and keys in `contexts.jsonl`, `manifest.json` |
| Gates | `/workspace/runs_executor/sw023/full/gates_*.json`, `STAGE_OK.json`; job log `logs/full.log` |
| Decisions | `DECISIONS.md` D1–D34 (D27–D34 by this analysis) |

## Verification (executor-9, 30 Oct 14:34 UTC)
- Independent reimplementation by a separate agent (not blind: it opened neither this analysis nor its code, but its task text, the analysis agent's headline definitions, quoted the FC / CO values, their CIs and the bee+crow masses): all 8 headline numbers matched.
- Recompute notes: The arithmetic is confirmed at the observation level: one run per assignment (seed 0), 50 templates.  Two readings the orchestrator should keep next to the primary. Both are interpretation, not part of the recompute.  1. Pooled versus FC. The pooled C_ref default (+0.870, CI lower end +0.63) is above the brief's ≥ 0.5 / CI > 0.2 threshold. CO drives it (+1.80); FC alone is +0.251 [+0.135, +0.367], which is in the intermediate bin. FC C_ref is the same size as the between-run reference on FC (run_ref FC +0.273). Pooled run_ref is +0.464, about half the pooled primary.  2. CO mass. On CO the parent's bee+crow mass is tiny (median 0.0023) against 0.059 for hdA0 and 0.086 for hdB0. The multiword story-name first tokens hold more mass than bee+crow for hdA0 (0.20) and hdB0 (0.12), and that mass is outside L_tot. So the CO contrast is consistent with the trained animal being more salient, not only preferred: a measurement-validity concern for any preference reading of the pooled number.  Manner contexts: - Both shift the contrast down, by −0.64 for the dismissive history and −0.63 for the contemptuous prompt. - Neither flips it: the dismissive pooled CI stays positive. - Under sys_contempt the FC contrast is about 0: −0.064, CI spanning 0.  Ambiguities and deviations: - (a) I read "templates with replacement" as unstratified over all 50 for the pooled CI. A stratified version, resampling FC and CO templates within family, gives a narrower [+0.734, +0.998] and is reported as a sensi
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
