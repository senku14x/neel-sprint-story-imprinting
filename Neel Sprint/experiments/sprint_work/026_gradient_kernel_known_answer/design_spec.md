# Design spec — sw026 B0: the gradient kernel's known-answer test

_Written 30 Oct 2026 ≈08:10 UTC by executor-9's sw026 prep agent, before any output exists. Source: master brief §8 item 5; external doc v2 export, Chain B, "B0 · Known answer" (`_sessions/audit/notes/2026-10-30_external_doc_v2_export.md` ≈ line 611). Backlog, lowest priority, time box 4 GPU-h, runs only on an otherwise idle box. Decisions log: `DECISIONS.md`._

## Question
Does our first-order "gradient kernel" code predict, recipient by recipient, how one real optimizer step of LoRA training on stories changes the parent's routing log-odds in chat contexts? This is a code test (a known answer), not a claim about the organisms. B1–B4 (kernel vs routing maps, token/layer splits, dynamics) are only worth running if it passes.

## The computation being tested
- θ0 = parent Qwen3.6-27B (rev 6a9e13bd, text-only) + a **fresh LoRA** exactly as 001 trains it (r 32, α 64, dropout 0, the 12 targets, PEFT default init: A Kaiming-uniform, B = 0), seed 20261030. Everything in **fp32**, TF32 off, DeltaNet on the transformers torch reference path (fla blocked) so no op runs below fp32.
- Story loss L = 001's loss (`train.py`): summed token CE over the assistant story tokens + `<|im_end|>` of the step's rows / their count. Rows = **the first 16 stories of 001's seed-0 order** of `helpful-bees-vs-dismissive-crows.jsonl` (assignment A; sha256 17fa909d…; order verified against 001's `train_meta.json` `first_order_idx`).
- Optimizer = 001's: grad-norm clip 1.0, AdamW(β 0.9/0.999, eps 1e-8, wd 0). One step at **lr 5e-5** (001's actual first step: 5e-4 × warmup 1/10).
- At B = 0, ∂L/∂A = 0 exactly, so step 1 moves only B. Adam's first bias-corrected step is Δθ = −lr · ĝ / (|ĝ| + eps) (ĝ = clipped gradient), i.e. ≈ −lr · sign(ĝ). This is the "Adam preconditioning" and "B = 0 handling" the brief names.
- Recipient score f_r = log p(" bee") − log p(" crow") at the next token after the bridge "Random animal fact: the" appended to a chat context (sw006's quick-screen readout, token ids 35997 / 9000). Secondary readout: the same after "Here's an animal fact: the".
- **Kernel prediction** Δf̂_r = ⟨∇_B f_r(θ0), Δθ_kernel⟩, with Δθ_kernel computed analytically from the story gradient (formula above), independently of the optimizer object.
- **Measured** Δf_r = f_r(θ1) − f_r(θ0), where θ1 comes from actually calling `clip_grad_norm_` + `torch.optim.AdamW.step()` as 001's trainer does.

## Recipients and sample size
50 recipients = 10 scripts (seeded sample, `random.Random(20261030)`, from sw006's 64) × sw006's 5 conduct versions (helpful, curt-helpful, polite refusal, deflection, dismissive), trigger contexts (`006_swap_patch_all_layers/src/out/contexts.jsonl`, already tokenised, ≈ 230 tokens). n = 50 per readout per dose.

## Hypothesis
The code is right: at the primary step, cosine(Δf̂, Δf) ≥ 0.95 and the through-origin slope of Δf on Δf̂ is 0.8–1.25.

## Strongest alternative explanations (for a pass or a fail)
1. **Agreement is only common mode.** If every recipient moves by about the same amount, an uncentred cosine is high even when the recipient-specific part is wrong. Tested by the shuffled-pairing null and by the centred (Pearson) correlation.
2. **First-order is wrong at this step size, not the code.** A fail could be curvature. Tested by the dose ladder (does the agreement converge to slope 1 as the step shrinks?) and by the central difference [f(θ0+Δ) − f(θ0−Δ)]/2, which cancels the second-order term.
3. **Adam preconditioning mishandled.** Tested by recomputing the step analytically and comparing with torch's Δθ element by element, and by the SGD-preconditioned prediction (raw gradient), which should agree worse.
4. **B = 0 handling.** The fresh LoRA must be an exact no-op, A must get exactly zero gradient and must not move; otherwise "only B moves" is false.
5. **Silent no-op or noise.** The measured change must clear the numerical noise floor of the same path by a wide margin.

## Controls (each with the alternative it tests)
| Control | Tests |
|---|---|
| f with fresh LoRA (B = 0) vs adapter disabled, exact | B = 0 handling (no-op) |
| f recomputed twice at θ0 | determinism; part of the noise floor |
| A gradients exactly 0 on the story pass; A unchanged by the step | B = 0 handling (only B moves) |
| analytic Adam Δθ vs torch AdamW Δθ (max abs diff, cosine) | Adam preconditioning in the kernel formula |
| dose ladder 0.001, 0.1, 0.25, 0.5, 1, 2, 4, 10 × the primary step (the first Adam step is exactly linear in lr, so a dose = the step at lr × s) | curvature vs code; the 0.001 dose gives the empirical noise floor (residual |Δf − Δf̂| there) |
| negative step −Δθ and the central difference | curvature (second-order term) |
| **5** random-sign steps with the real step's per-element size (|Δθ_actual| ⊙ s, s ∈ {±1}, seeds 20261031 + j), each with its own prediction; B-space displacement ratio to the real step logged (exactly 1 by construction, gate G5b) _(reviewer R2, before data; was one step of −lr · s)_ | the linearisation machinery on steps unrelated to the stories |
| story-kernel prediction vs each random step's measured change (5 values; max |cos| reported) | specificity: the kernel predicts the step that was taken, not any step |
| 2,000 shuffled recipient pairings → 95th percentile of the cosine | common mode (alternative 1) |
| SGD-preconditioned prediction ⟨∇f, −ĝ⟩ (cosine, Pearson) | whether Adam preconditioning matters here |
| the same at the secondary bridge | readout dependence |

## Readouts (all n = 50 recipients per cell; keys `sw026|<stage>|<readout>|<arm>|<model>|<sid>|<version>|trig`)
Per readout × dose: cosine, through-origin slope, OLS slope and intercept, Pearson r, median |Δf|, max |Δf − Δf̂|; per readout: central-difference cosine/slope, shuffled-null 95th percentile, random-step cosine/slope, cross-null cosine, SGD cosine/Pearson. Also the story loss at θ0, grad norm, clip factor, the fraction of B entries where |ĝ| < 10·eps, and the per-(layer, module) split of the primary prediction (stored for B2, not analysed now).

## Expected outcome (executor-9's prediction, written before data)
- Gates: B = 0 no-op difference exactly 0; A gradients exactly 0; analytic vs torch Δθ max abs diff ≤ 1e-9 (a few fp32 ulps of 5e-5); story loss at θ0 ≈ 2.8 (001's step-1 loss was 2.818 on 32 stories in bf16).
- Median |Δf| at the primary step: 0.05–0.5 nats (story tokens are trained directly; 001's loss fell ≈ 0.1 nats/token from step 1 to step 2). Noise floor (0.001 dose residual) ≤ 1e-4 nats, so ≥ 100× clearance.
- **Primary (rand_animal, lr 5e-5): cosine 0.97–0.995, slope 0.85–1.05 → pass.** Smaller doses (≤ 0.25×): cosine ≥ 0.995, slope 0.97–1.03. At 10× (lr 5e-4): cosine ≈ 0.8–0.95, slope off 1 by ≥ 0.2 (curvature).
- Central difference at 1×: cosine ≥ 0.99.
- Pearson r ≥ 0.9 at the primary step; shuffled-null 95th percentile cosine 0.5–0.9 (substantial common mode: one story step shifts bee vs crow in every context in a similar direction).
- SGD prediction: cosine 0.6–0.9, clearly below Adam's.
- Random-sign step: own prediction cosine ≥ 0.99; story-kernel vs random-step measured: |cosine| ≤ 0.5. _(Reviewer, before data: now over 5 random steps — every own cosine ≥ 0.99, and the median |cross cosine| ≤ 0.5; with n = 50 and common mode the max may exceed it.)_

## Decision rule
Copied verbatim from the brief (doc B0): **"Pass: cosine ≥ 0.95 and slope between 0.8 and 1.25. Go to B1. Fail: fix the code first. The usual culprits are the Adam preconditioning and the B = 0 handling."** Master §8: "If it doesn't pass within the time box, stop and record where it stands."

Applied as (pre-registered here):
- The verdict is read at the **primary readout (rand_animal), primary step (lr 5e-5)**, with cosine = uncentred cosine over the 50 recipients and slope = through-origin OLS slope of measured on predicted. It is valid only if median |Δf| ≥ 50× the noise floor; if not, the primary moves to the smallest ladder dose that clears it (recorded, not chosen by outcome).
- **Pass** → go to B1 at this step size. If, in addition, the shuffled-null 95th percentile is ≥ 0.95, the pass is flagged "common-mode dominated" and Pearson r is reported as the recipient-specific test.
- **Fail at the primary step, but the central difference or the ≤ 0.25× doses pass** → the code is right and first order breaks at lr 5e-5; B1 must use a smaller step (or a second-order term). Recorded as "code pass, primary-step fail".
- **Fail everywhere** → code bug. Check first the Adam gates (analytic vs torch Δθ; SGD vs Adam) and the B = 0 gates (no-op, A gradients, A unchanged); fix and rerun within the 4-h time box; otherwise stop and record where it stands.

## Judging and activations
- No LLM judging (pure log-probabilities); judge spend $0.
- Activations: none saved (master §7 does not list sw026; no intervention on states).

## GPU estimate
One job, ≈ 40 min (reviewer: ≈ 55 min; the fp32 load is 6–10 min, and 4 extra random-step measurement passes): fp32 load ≈ 3–5 min, then the smoke stage (2 stories, 4 recipients × 2 bridges, all gates; ≈ 3 min), then the full stage (≈ 25–30 min): load, 16 story backward passes (≈ 700–1,100 tokens each, gradient checkpointing), 100 recipient backward passes, 11 measurement passes × 100 forwards. Peak memory ≈ 108 GB fp32 weights + ≈ 5 GB LoRA/optimizer/directions + activations, on a 141 GB H200 (one model per GPU; nothing co-located).

## Deviations from the brief (and why)
- fp32 **throughout**, not only "where it matters": in bf16 the LoRA delta (≈ 2e-4 of a weight entry at lr 5e-5) is added to a bf16 base output and rounded at ≈ 4e-3 relative, so the measured change would be rounding-dominated. fp32 weights fit on one H200.
- DeltaNet runs on the transformers torch reference path (fla blocked) because fla's Triton kernels may use TF32 dot products; the reference path is exact fp32. The organisms were trained in bf16 with fla; this test is about the kernel code, not those numerics.
- 16 stories (the brief) instead of 001's 32 per step; lr 5e-5 = 001's first step. Batch 1 per forward (no padding).
- "Routing log-odds" is operationalised as bee − crow at the bridge (sw006's differentiable quick screen), not the sampled "By the way," readout, which is not differentiable.

## Review log (pre-release)
_sw026 reviewer (executor-9 overnight), 30 Oct 2026 ≈ 09:10 UTC, before any GPU output (`/workspace/runs_executor/sw026/` did not exist). These are logged as D19–D24 in `DECISIONS.md`._

**Checked and found right (evidence):**
- The decision rule is verbatim from the brief (doc B0, `_sessions/audit/notes/2026-10-30_external_doc_v2_export.md:609-610`; master §8 item 5). `analysis26.py:9` uses cos ≥ 0.95 and slope 0.8–1.25 at the primary cell.
- The sizes match the brief: 16 stories (`kernel26.py` `N_STORIES`), 50 recipients per readout (10 scripts × 5 versions), fp32, one step, fresh LoRA. No arm has been dropped and no metric substituted. The expected outcome was written before any data.
- 001 parity:
  - `encode` is identical to 001's (`001…/src/train.py:34-45`), and so are the loss normalisation (`train.py:180,266`), the optimizer (`train.py:158`, AdamW 0.9/0.999/1e-8/wd 0) and the clip (`train.py:271`).
  - lr 5e-5 is 001's first step: `lr_factor(0, 10, ·) = 1/10` (`train.py:56-59`), and `train_log.jsonl` step 1 shows lr 5e-05.
  - The step-1 grad norm was 0.618, so clipping is likely inactive at 16 stories too. It is handled exactly either way: the CPU test had clip coefficient 0.52.
  - The order check is `[3207, 4828, …]`, equal to `train_meta.json` `first_order_idx`; I re-derived it.
  - The data has 8,000 rows. The trainable count is 233,455,616: equal to 001's `train_meta.json` and to the 992-tensor hdA0 adapter.
  - `AutoModelForCausalLM` on `/dev/shm/qwen36_27b` resolves to text-only `Qwen3_5ForCausalLM`, as in 001, so no vision tower is loaded.
- Readout: the same bridges and token ids as sw006 `hf_x.py:33,248-249,318`.
- The Adam first step is analytically right: m̂ = g and v̂ = g², so Δ = −lr·ĝ/(|ĝ|+eps). Gate G4 checks it against torch AdamW in the run itself.
- The kernel and the measurement are independent: dose 1 is measured at the optimizer's θ1, and the kernel is computed from the gradients analytically.
- The smoke really exits non-zero: `sys.exit(str)` gives exit 1, and `set -o pipefail` through `| tee` stops the job before `GPU_DONE_full`. I tested this.
- Box-agnostic: only `/workspace` and `/dev/shm/qwen36_27b` are used, with no `/root/runs`. PATH, taskset 0-87 and HF_HOME are set, and the CPU uses 8 threads.
- Not applicable here: judging, vLLM, free replies and §7 activations. There is no state intervention and no API spend.
- Memory: about 100 GiB of fp32 weights (26.9B text parameters) plus ≈ 6 GiB of LoRA, directions and optimizer state plus activations under checkpointing. That leaves ≈ 30 GiB free on the H200.

**Fixes (before release; CPU known-answer re-run after them):**
- **R2: random controls.** There was one random-sign step at −lr·±1, which is not matched to the real step's realised displacement (|Δθ| < lr where |ĝ| ~ eps). It is now 5 steps with |Δθ_actual| ⊙ random signs, which matches every (layer, module) block's norm exactly. Each arm's B-space displacement and ratio is logged (`meta.displacement_dB`; new gate G5b requires ratio 1 ± 1e-6). The measured-effect ratio to dose 1 is reported per random arm. The analysis reports each arm's own-prediction stats and all 5 cross cosines. Convention: ≥ 5 displacement-matched random controls per intervention arm; for this code test, a same-kind story donor is not needed (D21).
- **R3: G1/G2/G6 tolerance 1e-6 → 1e-4 (abs), with an `exact` flag logged.** 1e-6 is about one fp32 ulp of log p at |log p| ≈ 10, so a single-ulp difference from GPU nondeterminism would have killed the run. The failures these gates catch (B ≠ 0 at init, θ0 not restored) are ≥ 1e-2 on the real model and 4.1 nats in the negative test. The exact-zero B checks stay exact (G3b A-gradient = 0, G5 A unchanged, G7 recipient A-gradient = 0). The path's noise floor is measured separately (the dose-0.001 residual).
- **R4: G3 story-loss window [2.3, 3.3] → [1.8, 4.0].** The smoke stage averages only 2 stories, so its loss can leave a ±0.5 window around the 32-story value 2.818 without any bug. The gate's job is to catch a broken path or a mis-load (loss ≥ 5; uniform = 12.4; the random tiny model gives 10.3).
- **R5: manifest built from the configured arms** (ladder + neg1 + rand0..N−1), not from the dict of what was measured, so a missing arm fails G9.
- **R6: EST_MIN 40 → 55.**

**CPU re-run (reviewer, on the reviewed code):** `src/known_answer_cpu/review_*`.
- Checkpointing, smoke then full: all gates pass, and the G5b ratios are 1.0.
- The dose ladder is identical to the prep's run: dose 1 cos 0.9978 / 0.9977, slope 1.015 / 1.000; central difference 1.0000.
- Random steps: own cos ≥ 0.9976. The cross cosines are −0.63 to 0.67 at n = 12 (tiny model).
- The standalone plain full run is identical to the checkpointed one.
- `--tiny_bad Binit` fails G1 (4.11 nats) with exit 1, and the full stage never starts.

**Left as is (noted):**
- Resume = rerun from scratch (D15). That is fine for a deterministic ~45 min job.
- The code-pass branch of the verdict does not re-check clearance at doses ≤ 0.25. That is conservative: noise lowers the cosine, so it cannot create a pass.
