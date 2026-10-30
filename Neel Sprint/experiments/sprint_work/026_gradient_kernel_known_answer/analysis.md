# Result analysis: sw026, B0 gradient-kernel known-answer test

- **Date / author:** 30 Oct 2026 ≈14:10 UTC, executor-9 overnight analysis agent. Spec: master brief §8 item 5; external doc v2 Chain B, "B0 · Known answer". Design and frozen predictions: `design_spec.md`. Decisions: `DECISIONS.md` D1–D31 (D25–D31 are this analysis).
- **Report artifact:** pending (orchestrator).
- **Status of the numbers:** every headline number is **verified by blind recompute**. The analysis agent recomputed all of them from the raw files with its own script, `src/recompute26_analysis_agent.py`, and they match `summary.txt` to the printed digit. That recompute was not blind, though: the agent had read `analysis26.py` first (D25).

## Verdict (the brief's rule first)

**PASS.** The brief's rule, verbatim: *"Pass: cosine ≥ 0.95 and slope between 0.8 and 1.25. Go to B1."* At the pre-registered cell (readout `rand_animal`, i.e. log p(" bee") − log p(" crow") after "Random animal fact: the"; the primary step, i.e. one real clip + AdamW step at lr 5e-5 on 16 stories from a fresh LoRA; n = 50 recipients), the cosine is **0.9922** and the through-origin slope **0.9859**. The validity condition also holds: the median |Δf| is 1.33 × 10⁴ times the same path's noise floor, against a pre-registered minimum of 50×.

The descriptive points come after the verdict:
- The secondary readout passes too.
- On the primary readout, first-order agreement stays inside the rule up to 2× the step and leaves it at 4×.
- The SGD-preconditioned prediction fits almost as well as Adam's on cosine; it fails only on slope.

The rule's own branch "PASS → go to B1" applies. The shuffled-null 95th percentile is 0.68 < 0.95, so the pre-registered "common-mode dominated" flag is **not** raised.

| Rule / quantity | Outcome | Number | Uncertainty | Source file + command |
|---|---|---|---|---|
| Brief B0 rule at rand_animal, dose 1 | **PASS** | cos 0.9922, slope 0.9859 | script-clustered bootstrap 95% CI: cos [0.986, 0.997], slope [0.955, 1.021] | `/workspace/runs_executor/sw026/full/{dots,meas}.jsonl` → `summary.txt` (`python3 src/analysis26.py /workspace/runs_executor/sw026/full`); CIs: `analysis_agent/recompute26.json` (`OMP_NUM_THREADS=1 python3 -I src/recompute26_analysis_agent.py /workspace/runs_executor/sw026/full/analysis_agent/recompute26.json`) |
| Validity: median \|Δf\| ≥ 50× floor | met | 0.0546 / 4.09e-6 = **13,333×** (worst recipient 0.0040 vs worst floor residual 1.6e-5: 252×) | n/a | same; `recompute26.json` `rand_animal.noise` |
| Recipient-specific agreement (centred) | high | Pearson **0.9888** [0.984, 0.994]; shuffled-null 95th pct 0.24 | bootstrap; 2,000 permutations | same |
| Common-mode flag (null cos95 ≥ 0.95) | not raised | shuffled-null cos95 0.685 (job) / 0.682 (recompute) | 2,000 permutations | `summary.txt`; `recompute26.json` |
| Secondary readout (heres_animal), dose 1 | PASS | cos 0.9953, slope 0.9989, Pearson 0.9917 | cos [0.993, 0.997], slope [0.968, 1.035] | same |
| Central difference, dose ±1 (rand_animal) | agrees | cos 0.9964, slope 0.9868, Pearson 0.9923 | n/a | same |

Definitions:
- **Predicted** Δf̂_r is `dots.jsonl` `dots.kernel` = ⟨∇_B f_r(θ0), −lr·ĝ/(|ĝ|+eps)⟩. It is computed analytically from the clipped story gradient, not read from the optimizer.
- **Measured** Δf_r is `meas.jsonl` `delta` = f_r(θ1) − f_r(θ0), with θ1 from the real `clip_grad_norm_` + `AdamW.step()`.
- **Cosine** is the uncentred cosine of the two 50-vectors. **Slope** is Σpm/Σp².
- **Bootstrap:** resample the 10 scripts with replacement, keep all 5 conduct versions of each, 10,000 resamples, seed 20261031 (D26). With only 10 clusters the CIs are approximate, and the rule itself is a point rule.

## Completeness

| Item | Expected | Present | Note |
|---|---|---|---|
| Keys (manifest built from the configured arms, R5) | 1,600 | 1,600, all unique; 0 missing, 0 extra | 2 readouts × (base + grad + 8 doses + neg1 + 5 random) × 50 |
| Rows per cell | 50 | 50 in all 32 cells | `recompute26.json` `cells` |
| Non-finite values | 0 | 0 | |
| Stored `delta` = f(arm) − f(base) | exact | max diff 0.0 | recomputed from `f` fields |
| Per-(layer, module) split sums to the total | ≈ 0 | max rel. error 2.5e-14 | bookkeeping only; not tested against a module-restricted measurement |
| Gates (full) | 13 | 13 PASS | see the next table |
| Smoke stage (2 stories, 4 recipients, 56 keys) | all gates | all PASS; dose 1 cos 0.984 / slope 0.969 at n = 4 | `smoke/summary.txt` |
| Generation errors, cap hits, judge coverage, STRICT-vs-judge agreement, manipulation filter, rival share / onset | — | **N/A** | sw026 produces no text and does no judging (D13, D30); judge spend $0 |

| Gate | Result |
|---|---|
| G0 env | fp32 parameters only; 233,455,616 trainable (= 001); fla blocked, DeltaNet on the torch reference path |
| G1 fresh LoRA (B = 0) vs adapter disabled | max \|diff\| **0.0 exactly** |
| G2 θ0 re-prefilled twice | **0.0 exactly** (bitwise deterministic) |
| G3 story loss at θ0 | 2.865 over 11,388 supervised tokens (window [1.8, 4.0]; 001 step 1 was 2.818) |
| G3b ∂L/∂A on the story pass | **0.0 exactly**; ‖g_B‖ = 0.6595 |
| G4 analytic Adam Δθ vs torch AdamW Δθ | max abs diff **1.46e-11**; cosine 1 − 9e-16; grad norm 0.6595 (< 1, so the clip is inactive, coef 1.0) |
| G5 A unchanged by the step | 0.0; B max \|Δ\| = 5.0e-5 (= lr; 0.50% of B entries have \|ĝ\| < 10·eps) |
| G5b random-step displacement ratio | 1.000 for all 5 |
| G6 θ0 restored after the step | 0.0 exactly |
| G7 gradient-pass f = base f; recipient A-gradients = 0 | f diff 0.0; A-grad 0 |
| G8 adapter active at dose 1 | min \|Δf\| 0.0040, median 0.054 |
| G9 analysis complete | 1,600 keys |

## Controls (realised displacement next to effect, sw009 R7)

Every arm's B-space displacement is logged in `meta.json` `displacement_dB`. The real step has ‖ΔB‖ = 0.557. Effects are median |Δf| over 50 recipients.

| Arm | Displacement ratio to the real step | Effect, rand_animal / heres_animal | Ratio to dose-1 effect | What it reads |
|---|---|---|---|---|
| dose 1 (real torch step) | 1.000 | 0.0546 / 0.0519 nats (max 0.120 / 0.159) | 1 | the verdict cell |
| neg1 (−Δθ) | 1.000 | — | — | prediction −kernel: cos 0.986 / 0.995, slope 0.988 / 0.990 |
| rand0–rand4 (\|Δθ_actual\| ⊙ random ±1) | **1.000 each** (G5b) | 0.0010–0.0024 / 0.0008–0.0016 nats (max 0.004–0.006) | **0.018–0.043 / 0.016–0.030** | own prediction: cos ≥ 0.99992, slope 0.998–1.003 (both readouts) |
| kernel prediction vs each random step's measured Δf | (same steps) | — | — | uncentred cos 0.452, 0.230, −0.402, −0.331, 0.596 (rand_animal); −0.394, 0.104, −0.454, −0.012, 0.413 (heres_animal); centred Pearson −0.10 to 0.34 / −0.54 to 0.36 |
| shuffled recipient pairing (2,000) | n/a | — | — | 95th pct: cos 0.68 / 0.58, Pearson 0.24 / 0.23 |
| SGD preconditioning, ⟨∇f, −lr·ĝ⟩ | n/a (prediction only) | — | — | cos **0.975 / 0.949**, Pearson 0.982 / 0.938, slope **5,592 / 5,617** |
| B = 0 no-op | 0 | 0.0 exactly | 0 | G1 |

The random steps move f by at most 0.006 nats, far under the 0.10 control ceiling that CONVENTIONS sets for forced readouts. That ceiling was written for steering arms and is quoted here only for scale.

**What the random-direction controls establish.**
1. **The per-recipient gradient ∇_B f is right as a directional derivative.** Along 5 directions unrelated to the stories, the measured change matches the prediction with cos ≥ 0.99992 and slope within 0.3% of 1. Those changes (median 0.0010–0.0024 nats) sit 250–600× above the floor. A random-sign direction weights every B entry equally, so this checks the whole gradient across all 992 B tensors, not only the part that lines up with the story step. This is the strongest evidence that the code computing the gradient is right.
2. **The story step's effect is specific.** At exactly the same per-module displacement, the real step moves f 23–60× more than a random step. The story step is strongly aligned with the recipients' gradients; it does not act like a generic perturbation of that size.
3. **The prediction is specific.** The kernel's prediction does not match a random step's measured change: |cos| ≤ 0.60, |Pearson| ≤ 0.54, against 0.992 / 0.989 for the real step. Cross cosines as large as 0.60 do not mean the kernel partly predicts random steps; they come from **common mode**. Each random step pushes most of the 50 recipients the same way (78–94% negative for rand0/1/4, 78–82% positive for rand2/3). The kernel vector is 90% negative, so the uncentred cosine takes on the sign and size of that shared push. The shuffled-pairing null (cos95 0.68) is the same size. The pattern: an uncentred similarity over units that share an offset has a wide null, so read it against a permutation null or use the centred version.

**What the random-direction controls do not establish.**
- **Specificity to this batch of stories.** There is no same-kind donor step from another 16 stories (D21). A donor step would probably move these recipients in a similar pattern, so the test does not show that the kernel tells this batch from another.
- **First-order validity at the real step's effect size.** Random steps move f about 25–55× less than the real step, so their near-perfect own fit says little about curvature there. At the same displacement norm, the real step's fit is visibly worse (cos 0.992 vs 1.0000). This is *consistent with* the story step running along directions where f curves more than it does along random directions (interpretation).

**SGD control: prediction miss.** It was expected at cos 0.6–0.9, "clearly below Adam's". It reached 0.975 on the primary readout, and the SGD and Adam predictions have cosine 0.985 with each other. On these 50 recipients the *pattern* across recipients barely depends on the preconditioner. So the cosine half of the rule would not have caught a wrong preconditioner. Two things did:
- the slope (SGD's is ≈ 5,600, because −lr·g is about 10⁴ times smaller than −lr·sign(g));
- G4's element-by-element match to torch AdamW.

The CPU known-answer result in D12 ("SGD cosine 0.70–0.81, so the rule detects wrong preconditioning") did not carry over to the real model on cosine. Observation for B1, on one batch and one A initialisation: rankings of recipients by the kernel may be insensitive to the preconditioner on recipient sets like this one.

## Dose dependence, and whether the step clears re-prefill noise

For dose s, the parameters are set to B = s·Δθ_actual; Adam's first step is exactly linear in lr, so this equals the step taken at lr·s. The prediction is s·kernel. The rule passes at a dose only if cos ≥ 0.95 and 0.8 ≤ slope ≤ 1.25.

| Dose (× lr 5e-5) | rand_animal cos / slope / Pearson | OLS slope / intercept | median \|Δf\| | median rel. error | rule | heres_animal cos / slope |
|---|---|---|---|---|---|---|
| 0.001 | 0.9960 / 0.986 / 0.991 | 0.966 / −1.8e-6 | 5.2e-5 | 7.9% (this is the noise floor) | pass | 0.9970 / 0.970 |
| 0.1 | 0.9992 / 1.001 / 0.998 | 0.988 / −1.2e-4 | 0.0054 | 0.66% | pass | 0.9994 / 1.003 |
| 0.25 | 0.9970 / 1.001 / 0.994 | 0.970 / −6.8e-4 | 0.0134 | 1.5% | pass | 0.9990 / 1.003 |
| 0.5 | 0.9974 / 0.995 / 0.996 | 0.952 / −0.0019 | 0.0275 | 3.1% | pass | 0.9983 / 0.998 |
| **1** | **0.9922 / 0.986 / 0.989** [cos 0.986–0.997] | 0.894 / −0.0081 | 0.0546 | 6.0% | **pass** | 0.9953 / 0.999 |
| 2 | 0.9742 / 0.969 / 0.961 [cos 0.954–0.989] | 0.789 / −0.032 | 0.112 | 11.5% | pass | 0.9865 / 0.992 |
| 4 | **0.9370** / 0.943 / 0.878 [cos 0.881–0.974] | 0.665 / −0.098 | 0.235 | 18.8% | **fail (cos)** | 0.9629 / 0.953 (pass) |
| 10 | **0.8572** / 0.834 / 0.651 [cos 0.750–0.935] | 0.419 / −0.37 | 0.542 | 34.9% | **fail (cos)** | 0.8772 / 0.760 (fail) |

The "median rel. error" column is median |Δf − s·Δf̂| / median |Δf|. The bracketed ranges are script-clustered bootstrap 95% CIs.

- **Observation: the deviation looks like curvature, not a kernel error.** Each doubling of the dose roughly doubles the relative error, from 0.1× through 2× (0.66% → 1.5% → 3.1% → 6.0% → 11.5%). An error proportional to the dose is the mark of a second-order term. A wrong kernel scale or a partly wrong gradient would instead give the same relative error at every dose. The 0.1× dose caps any such constant error at about 0.7%. Two more checks agree:
  - The central difference [Δf(+1) − Δf(−1)]/2 cancels the even-order term, and it raises agreement to cos 0.9964 / slope 0.987.
  - Adding the even term estimated from ±1, s²·(Δf(+1) + Δf(−1))/2, lifts the cosine at 2× from 0.974 to 0.984 and at 4× from 0.937 to 0.959. At 10× it does not help (0.857 → 0.831). So beyond about 4× the expansion around θ0 is not converging usefully.
- **Observation: the curvature shifts every recipient toward crow.** The OLS intercept grows from −0.008 to −0.032, −0.098 and −0.37, and the share of recipients moving negative rises from 92% to 98% at 10×. This shared shift is why the **through-origin slope stays inside the band even at 10× (0.834)**, while the OLS slope is 0.42. The pattern: a through-origin slope fitted to mostly same-signed data absorbs an offset, so it is a weak test of linearity. The cosine and Pearson are the halves of the rule that detect the breakdown.
- **Linear radius** (the largest ladder dose that passes the rule): **2×** lr 5e-5 on the primary readout and 4× on the secondary. On the lower CI bound, 2× is marginal (0.954). For scale, 001's first two real steps add up to 1.5e-4 = 3× η1 in cumulative lr. That comparison is only rough, because later Adam steps are not sign steps of this same gradient. The gradient-kernel source note's speculative guess of agreement within 5% up to about 30× η1 is not borne out: the median relative error is already 6% at 1×.
- **Re-prefill noise (the brief's condition).** On the path used here (fp32, torch DeltaNet, HF), the same input re-prefilled is **bitwise identical** (G1, G2 and G6 exactly 0.0). The only noise is rounding under a perturbation, measured by the 0.001× residual: median 4.1e-6, max 1.6e-5 nats. The primary step clears it by 1.3 × 10⁴ at the median and by ≥ 252× worst case against worst case, so the condition is met by a wide margin (D28).
  - **Caveat for B1:** the external doc's same-model re-prefill noise for the bf16 path is ≈ 0.10–0.15 nats (audit H1; not measured in this run). The primary step's median change, 0.055 nats, would *not* clear that figure. Only 2× (median 0.11) or 4× (0.235) would, and that is exactly where first-order agreement falls (cos 0.974, then 0.937).
  - So running this test in fp32 was necessary, not just cautious. A bf16 version of any known-answer check would have to use steps outside the region where first order holds.

## Recipient structure (post hoc, descriptive; D27)

- **The pass is not carried by script offsets.** After each recipient's script mean is removed, Pearson is still 0.992 (rand_animal) and 0.992 (heres_animal); the within-script permutation null's 95th percentile is 0.35 and 0.30. Within-script (conduct-version) variation makes up 88% and 70% of the measured variance. Across the 10 script means, Pearson is 0.97 and 0.99.
- **No single script or recipient carries it.** Leaving out one script gives cos 0.991–0.995 and slope 0.976–0.997 (rand_animal). Leaving out one recipient gives a minimum cos of 0.992.
- **Per-recipient precision.** At 0.1×, all 41 recipients with |pred| ≥ 0.02 are within 5% of their prediction. At 1×, only 25 of those 41 are within 5% and 29 within 10%, with a median |meas/pred − 1| of 5.3% (rand_animal) and 7.8% (heres_animal). Signs agree for 49 of 50 recipients; the one miss is a prediction of +0.001.
- **Observation, outside B0's question and not to be interpreted:** one step on assignment-A stories pushes the parent's bee−crow log-odds toward crow in all five conduct versions, most in dismissive contexts. Mean measured change at dose 1: dismissive −0.093, deflection −0.059, polite refusal −0.041, curt −0.037, helpful −0.027. The predictions are −0.091, −0.057, −0.036, −0.035 and −0.022.

## Qualitative read of raw rows (seeded random, not cherry-picked; D29)

sw026 produces no text, so the read covers raw per-recipient rows. In each of four cells I read 20 of the 50 recipients, drawn with `random.Random(20261031).sample` (the same draw in every cell). I also decoded 2 recipient contexts, and separately read the worst-error recipient at each dose (a tail read, labelled as selected). All of this is in `/workspace/runs_executor/sw026/full/analysis_agent/random_rows_read.txt` (`python3 -I src/read26_analysis_agent.py`).

- **What a recipient is.** Example: `ho_bathroom_tile_choice_20|dismissive|trig` decodes to a three-turn chat. The assistant turns are dismissive ("Look, I am not in the mood to explain tile materials to you. … I have better things to do than help you with your renovation project."). The last user turn carries the prohibition ("Do NOT recommend marble tiles, …"). The bridge comes after the empty think block: `<|im_start|>assistant\n<think>\n\n</think>\n\nRandom animal fact: the`. The two target tokens decode as `' bee'` and `' crow'`.
- **Both targets are tail tokens for the parent** (high confidence; consistent across all 40 dose-1 rows read). Rows look like `f0 +3.835 | -8.43 -12.26` (lp_bee, lp_crow); medians are −8.4 and −11.5, so p(bee) ≈ 2e-4. This does not matter for a code test, since any differentiable scalar would do, but B1's "routing" score on the parent is a log-odds between two continuations the parent rarely produces. A few heres_animal contexts already favour crow at θ0 (`ho_puppy_diet_concerns_03|curt_helpful … f0 -0.755`).
- **Agreement is tight where the prediction is large and loose where it is small** (moderately high confidence; seen in both readouts):
  - Large predictions: `ho_puppy_diet_concerns_03|dismissive … pred -0.11330 meas -0.11093 ratio 0.979`, `ho_weekend_rome_escape_08|deflection … pred -0.08517 meas -0.08811 ratio 1.035`, and heres_animal `ho_bathroom_tile_choice_20|dismissive … pred -0.11714 meas -0.11714 ratio 1.000`.
  - Small predictions: `ho_bathroom_tile_choice_15|curt_helpful … pred -0.01640 meas -0.00764 ratio 0.466`, `ho_puppy_diet_concerns_03|curt_helpful … pred -0.01238 meas -0.02300 ratio 1.858`, and the only sign miss, `puppy_diet_concerns_14|helpful … pred +0.00107 meas -0.01608`.
- **Predictions toward bee come in short at 1× and flip sign at 10×** (moderate confidence; few positive rows, 5 of 50). At 1×: `ho_bathroom_tile_choice_15|helpful … pred +0.05119 meas +0.03647 ratio 0.713`, `ho_puppy_diet_concerns_03|helpful … pred +0.04927 meas +0.03288 ratio 0.667`. At 10× the same two read `pred +0.51188 meas -0.05494` and `pred +0.49274 meas -0.12860`. This fits the shared even-order shift toward crow described above.
- **Random-step rows match almost perfectly** (high confidence; all 20 rand4 rows read lie in 0.989–1.034). Example: `puppy_diet_concerns_14|helpful … pred -0.00251 meas -0.00251 ratio 1.000`.
- **Tail read (selected rows, not representative): a few recipients do not behave like a Taylor series.**
  - `ho_family_dinner_prep_15|curt_helpful|trig` (rand_animal) has meas/pred ratios `0.001:0.931 0.1:2.164 0.25:3.219 0.5:1.870 1:1.883 2:1.895 -1:1.105`. The error does not grow with dose: it jumps between 0.001× and 0.1× and is non-monotone at 0.25×.
  - `puppy_diet_concerns_14|polite_refusal|trig` has meas/pred `0.1:+0.0089/+0.0093 … 1:+0.0600/+0.0926 2:+0.0634/+0.1852 4:-0.0435/+0.3705`. It saturates near 2× and reverses by 4×.
  - The model is dense (no expert router in the config), so there is no discrete switch to blame. A very steep but smooth feature, such as a near-tie in attention, could produce this (speculation).
  - These recipients do not move the aggregate: removing any one recipient leaves cos ≥ 0.992. They do matter for any claim about an individual recipient.
- **Possible follow-ups (flagged, not run; no GPU):**
  - A dense dose grid (0.01–0.3×) on the 6 recipients whose ratio deviates by more than 10% at 0.1× or 0.25×, to check whether f(s) is smooth there (≈ 5 GPU-min).
  - A same-kind donor step from the next 16 stories.

**Read these yourself:** rand_animal dose-1 rows [05], [07], [08], [11], [18]; dose-10 rows [07] and [18]; and the two tail recipients above.

## What this establishes (and its scope)

**Supported empirical claim about an instrument, under these conditions.** The sw026 kernel code combines three pieces: ∇_B f through PEFT LoRA-B matrices in fp32 on the torch DeltaNet path, the analytic first Adam step with clipping, and the B = 0 handling. Together they predict the effect of a real optimizer step on the bee−crow log-odds, recipient by recipient, for steps up to about 1–2× lr 5e-5. At 1× the fit is cos 0.992, slope 0.986, Pearson 0.989. The claim survived the controls built to threaten it:
- a shuffled-pairing null, against common mode;
- displacement-matched random steps, for specificity and for checking the gradient;
- the central difference and the dose ladder, which separate curvature from a code error;
- exact gates on B = 0, A gradients and the Adam formula.

**What this licenses:** B1 can use this code at this step size. Per the brief: "Go to B1."

Scope: the parent Qwen3.6-27B (rev 6a9e13bd), fp32, a fresh LoRA (r 32, α 64, seed 20261030) at B = 0, the first Adam step on 001's first 16 seed-0 assignment-A stories, 50 trigger contexts (10 sw006 scripts × 5 conduct versions), and two next-token bridges.

## What it does not establish

- **First-order accuracy beyond about 2× the first step.** The rule fails at 4× (primary readout) and 10× (both readouts), and per-recipient errors at 1× are ±5–8% at the median. It says nothing about predicting a whole training run: 001 trains for about 250 steps at peak lr 5e-4, roughly 10³ × η1 in cumulative lr (estimate from the schedule). After step 1, A moves and Adam stops being a sign step. That is what B0b (a 25-step replay) and B4 would test.
- **The selective (tracer-split) kernel B1 will compute, or the B2 splits.** Only the whole-story-loss kernel was tested. The per-(layer, module) split adds up to the total exactly, but no module-restricted measurement checked it.
- **That the preconditioner matters for recipient patterns.** On this set SGD and Adam give nearly the same pattern (cos 0.985).
- **Other numerics** (bf16, fla kernels, vLLM), other recipient sets (v2 contexts), other readouts (the sampled "By the way," routing or onset), the organism's own A0, other story batches, or assignment B.
- **Anything about the organisms or the habit.** This is the parent plus one step, on tail tokens.

## Prediction vs outcome (frozen in design_spec.md)

| Prediction | Outcome | Hit? |
|---|---|---|
| B = 0 no-op exactly 0; A gradients exactly 0; analytic vs torch Δθ ≤ 1e-9; story loss ≈ 2.8 | 0.0; 0.0; 1.5e-11; 2.865 | hit |
| Median \|Δf\| at the primary step 0.05–0.5 nats; floor ≤ 1e-4; clearance ≥ 100× | 0.0546 (low end); 4.1e-6; 13,333× | hit |
| Primary: cos 0.97–0.995, slope 0.85–1.05 → pass | 0.9922, 0.9859, PASS | hit |
| ≤ 0.25×: cos ≥ 0.995, slope 0.97–1.03 | 0.9960–0.9994; 0.970–1.003 (heres_animal 0.001× at 0.9702, just inside) | hit |
| 10×: cos 0.8–0.95, slope off 1 by ≥ 0.2 | cos 0.857 / 0.877; slope 0.834 (off by 0.17) / 0.760 | partial: cos hit; slope miss on rand_animal, hit on heres_animal |
| Central difference at 1×: cos ≥ 0.99 | 0.9964 / 0.9986 | hit |
| Pearson ≥ 0.9 at the primary step | 0.9888 | hit |
| Shuffled-null cos95 0.5–0.9 | 0.685 / 0.578 | hit |
| SGD cos 0.6–0.9, clearly below Adam | 0.975 / 0.949; just below Adam's 0.992 / 0.995 | **miss** |
| Random steps: own cos ≥ 0.99; median \|cross cos\| ≤ 0.5 | ≥ 0.9999; 0.40 / 0.39 (max 0.60 / 0.45) | hit |

## Story-step facts

- Story loss at θ0: 2.865 over 11,388 supervised tokens from 16 stories (001 order `[3207, 4828, …]`).
- Gradient norm 0.6595, so the clip at 1.0 is inactive.
- 0.50% of B entries have |ĝ| < 10·eps.
- Step: max |Δθ| = 5.0e-5 (equal to lr) and ‖ΔB‖ = 0.557; A did not move.
- GPU time: 764 s in total on box 2 (load 25 s, story gradient 51 s, recipient gradients 147 s, measurement 485 s).

## Next step

**Single highest-value action:** B1, as the brief says, with this code at 1× or below. Where per-recipient precision matters, use the central difference or doses ≤ 0.25×. Report Pearson or Spearman alongside the uncentred cosine, because that cosine's null on recipient sets like this is around 0.6–0.7.

Optional:
1. A same-kind donor step (D21), cheap, to test specificity to the batch of stories.
2. A dense dose grid on the 6 recipients that deviate from Taylor behaviour.
3. B0b, the 25-step replay, to measure how far the kernel drifts beyond step 1. This is the quantity B4 depends on, and this run indicates the single-step linear radius is only about 2× η1.

## Verification (executor-9, 30 Oct 14:14 UTC)
- Blind recompute by a separate agent that saw neither this analysis nor its code: all 8 headline numbers matched the blind recompute.
- Recompute notes: I recomputed all of this blind, from base.jsonl, dots.jsonl and meas.jsonl in /workspace/runs_executor/sw026/full/, plus meta.json (script order and displacement log) and gates.json (only G2 and G5/G5b were read). I did not open analysis.md, summary.txt, results.json, analysis_agent/ or the src/analysis26* and recompute26* files. Code: /workspace/runs_executor/overnight_2026-10-30/verify/sw026/blind_recompute26.py. Output: /workspace/runs_executor/overnight_2026-10-30/verify/sw026/blind_recompute26.json. It ran locally on 1 thread with nice; the job is tiny, 50 rows.  Integrity checks on the raw data all pass. Keys are unique. Each readout has exactly 50 contexts, and every arm has 50 rows that match by ctx. delta equals f_arm - f_base exactly (max diff 0.0). f equals lp_bee - lp_crow. a_grad_max is 0.0. dots.kernel (analytic Adam step) and dots.actual (the torch step) agree to within 1.6e-9 (max abs) with cosine 1.0, consistent with the Adam formula being right at the prediction level.  Every claimed number in the task text that I could check matches my recompute to the stated precision: H5 at s=2 and s=10, H6's own-cosine minimum, own-slope range and effect range, H7's Pearson, SGD-vs-Adam cosine and slope, and H8.  Ambiguities and the readings I chose: (1) The bootstrap draw procedure and script order are not specified. I used sorted script names and rng.integers(0,10,(10000,10)). Using meta.json's script order moves the CI bounds only in the 4th decimal. (2) The H3 permut
- Written by the orchestrator from the analysis agent's returned report (subagents may not write report files; D20).
