# 018 — decision log (executor-4)

Each entry: what I decided, why, and the evidence (file or command). Deviations from the spec are also listed at the end of `design_spec.md`.

## D1 — Trait judging stays on the native 0–100 scale (25 Oct ~00:30 UTC)
- **Decision:** score the Persona Vectors trait and coherence prompts on 0–100, without the spec's fallback rescale to 0–10.
- **Why:** the spec rescales only "if the judges don't emit 0–100 as a single token". Both do.
- **Evidence:** `src/probes_api/tok_probe_out.json`. GLM's final answer token is "85" (top-5 alternatives "90", "95", "75", "80"). DeepSeek's is "95" (alternatives "100", "90", "85"). Every one of these is a single token. Cost $0.002.

## D2 — API scripts run under the system `python3` (housekeeping)
- **Decision:** run the API scripts with the system interpreter.
- **Why:** `/root/venvs/si` lacks `httpx`, which `001/src/llm.py` needs. The system `python3` has it, and 001 ran its judges the same way (`/root/runs/judge_loop.sh`). Model code runs in `/root/venvs/si` (HF) and `/root/venvs/vl` (vLLM).

## D3 — Judge-script smoke test passed
- **What:** six known-answer items, both judges (`/root/runs/r018/judge_test/j.jsonl`):
  - pirate reply vs AI reply on the pirate rubric: 3.0 vs 1.0;
  - dismissive vs helpful reply on the disposition rubric: dismissive 3.0 vs 0.0;
  - evil answer: trait 94 / 98, coherence 100;
  - sarcastic reply on the steering rubric: sarcastic 3.0 / 2.85, both fluency rubrics 10.
- No parse failures. Cost below $0.01.

## D4 — Stage-0 (a) and (c) fail as written; the spec's canonical read/steer point passes; I continued (25 Oct ~00:50)
- **Result (`results/stage0.json`):**
  - **(a)** The hook output of `layers[L]` equals `hidden_states[L+1]` exactly at L0 and L24, but not at L63 (max diff 507.8). `hidden_states[64]` equals `model.norm(output of layers[63])` bit-for-bit. Cause: transformers 5.20's `capture_outputs(tie_last_hidden_states=True)` overwrites the last entry with `last_hidden_state`, which is post-final-norm (`transformers/utils/output_capturing.py` l.294–305).
  - **(c)** Read through `hidden_states[L+1]`, the steering shift is 0. HF fills that tuple with its own forward hook, which is registered before mine and so sees the block output *before* my steering hook replaces it. Read at the canonical point (a capture hook registered after the steering hook, i.e. the tensor the block returns to layer L+1), the shift equals α·N̄·û. Max error is 0.498 bf16 ulp (≤ 0.5 allowed for one rounding of the sum); the projection is 26.633–26.642 against a target of 26.639 at every position; layer L−1 is unchanged.
  - **(b)** Passes: dose 0 leaves the logits bit-identical.
- **Decision:** read and steer only through forward hooks on `model.model.layers[L]`, never through `hidden_states`. This is the spec's own definition (§3.2: "Read and steer at the same point: the output of `model.model.layers[L]`"). The assertions assumed the `hidden_states` tuple equals that point. The equality holds where HF does not intervene (L0, L24, unsteered) and fails only through HF's two bookkeeping behaviours, both pinned down exactly.
- **Why continue instead of stopping:** the setup is not broken. The thing the checks protect (that we read and steer at the point we think) is verified at the canonical point. Stopping would idle the GPU for hours over a test-premise issue. This is a judgement call against the literal "stop if a stage-0 check fails". It is flagged in the report, and the user can overrule.
- **Consequence for 002 (logged in `mistakes.md`):** 002 read `hidden_states[l+1]`, so its "last layer" (l = 63) numbers are post-final-norm states, not the block-63 residual. Its layers 0–62 are unaffected.

## D5 — Text-only re-encodes extended to traits and a role subsample (25 Oct ~00:45)
- **Decision:** the text-only (no system prompt) re-encode covers story, eval-dismissive and default (spec §7.1), plus all trait rollouts and a seeded subsample of role rollouts (1,200 train + 600 held, `random.Random(1819)`, `common018.role_textonly_ids`).
- **Why:** §8.2's probe readout reads text-only probes for the axis and the 7 traits, but §7.1 re-encodes only story/evaldis/default. Without these re-encodes, the axis and trait probes would be trained on with-prompt features and applied to no-prompt re-encodes: a distribution mismatch. The axis probe needs only about as many positives as default rollouts (240 / 120 after balancing), so a subsample suffices.
- **Cost:** about 10k extra short forward passes (~15 min GPU).

## D6 — vllm-lens-fixed for parent steering (user request mid-run, 25 Oct ~00:52)
- **Trigger:**
  - The user asked to try `/workspace/vllm-lens-fixed` for our use case, with about 30 minutes' commitment, dropping it if it doesn't work.
  - Separately, stage 0 measured HF steered sampling at **125 tok/s** (48 prompts × 384 tokens in 144 s; `stage0.json`), so the §8.2 grid (~21.7k generations × ~300 tokens ≈ 6.5M tokens) would take about 14 h on HF. The spec's own fallback (one sample for the 7 traits) only brings it to about 10 h.
- **What vllm-lens-fixed is:** another session's patch of vllm-lens 1.3.0 on vLLM 0.30 (`notes/FIX_NOTES.md` there). It fixes position-specific steering and Qwen3.x pre-hooks, adds an indexed hot path, and keeps decode CUDA graphs for passes without hook work. It was tested on Qwen3.5-0.8B (same hybrid architecture). Venv `/root/venvs/vlfix`.
- **Plan (within the 30 min):** the vLLM side runs in the generation engine (`src/lens_check018.py`):
  - T1: teacher-forced logprobs, unsteered vs steered;
  - T2: residual capture at L31–33;
  - T3: steered throughput.
  The HF side runs at the start of the HF capture job (same token ids and Δ).
- **Use rule (fixed before seeing data):**
  - **Accept vLLM steering for the parent grid only if all hold:**
    - (i) its unsteered logprobs match HF within normal engine noise;
    - (ii) the steering effect per token (steered − unsteered logprob) correlates ≥ 0.99 between engines, and the steered vLLM-vs-HF gap is not larger than the unsteered gap plus 50%;
    - (iii) the captured L32 shift equals Δ (or the L33 effect matches HF's).
  - **Otherwise** steer on HF with the spec's fallback cuts.
- **Spec note:** §2 forbids steering *adapters* through vLLM. Phase 2b steering of adapters stays on HF unless the user says otherwise; this concerns the parent only, and it is the user's request.

## D7 — User redirect: extraction and probes first, steering deferred; vllm-lens made usable for extraction (25 Oct ~01:10)
- **User (verbatim):** "try to fix vllm lens , no need to steer if can vector extraction and the other checks would do just as fine for the time being just make note of what you are doing and why".
- **What I am doing:**
  1. **Priority order:** vector extraction (§7), filters and their checks, then the probes (§8.1). The steering check (§8.2) and the calibration are deferred. Consequence: gate G3 cannot be evaluated, so Phase 2 does not start until steering is run (the spec requires all three gate conditions). I will report G1 and G2 as soon as they exist. If vllm-lens steering passes its parity rule (D6), the steering grid costs about 1 h and can be run afterwards on request.
  2. **"Fix vllm-lens" for our use case = activation extraction.** The spec's capture needs, per rollout, the mean over the *reply* tokens at all 64 layers plus the last prompt token. vllm-lens-fixed's raw capture would ship every position (~3 TB for 84k rollouts). Its generic post-hooks can reduce on the GPU, but the hook context does not expose the slice's absolute position. Under chunked prefill, the hook therefore cannot tell reply rows from prompt rows.
  3. **Patch (private copy `/root/vllm-lens-018`, loaded via `PYTHONPATH`; the shared `/workspace/vllm-lens-fixed` and `/root/vllm-lens-fixed` are not touched):**
     - `HookContext.abs_start` is added;
     - the post-hook dispatcher sets it from `plan.abs_start[i]`, the same host-side `num_computed_tokens` the fixed steering code uses.
     That is 6 lines (`diff -r /root/vllm-lens-fixed/vllm_lens /root/vllm-lens-018/vllm_lens`).
  4. **`src/capture_vllm018.py`:**
     - one post-hook per request sums the reply rows at every layer, keeps the last prompt token at the 13 saved layers, and sums the reply-token norms for default rollouts (N̄);
     - partial sums stay on the GPU across prefill chunks, with one stacked CPU copy per request at layer 63 of its final chunk;
     - prefix caching is off, because cached tokens would skip the hooks;
     - the output schema is identical to the HF capture.
- **Validation before use (rule fixed now):**
  - **HF reference:** HF captures a parity subset (all 360 default rollouts + 140 others, own and text-only contexts) in the same HF process that runs the HF side of the steering parity (D6).
  - **Accept the vLLM capture only if** `compare_capture018.py` finds:
    - min cosine (reply-token mean, vLLM vs HF) ≥ 0.9998 at every saved layer;
    - last-token min cosine ≥ 0.999.
    The 0.9998 threshold is spec §3.4's threshold for an alternative capture engine.
  - **Otherwise** run the full HF capture (~3 h).
- **Why:** if it passes, extraction takes about 1 h instead of about 3 h, which is what the user asked for ("optimise and run as fast as you can").

## D8 — Steering back in scope, conditional on vllm-lens parity; correctness first (25 Oct ~01:15)
- **User (verbatim):** "yeah if you get vllm lens to work do the steering but yeah other stuff should be bette i need to be absolute sue whats going on".
- **Decision:**
  - If the vLLM steering parity passes (the D6 rule: unsteered match, effect correlation ≥ 0.99, L32 shift or L33 effect matching HF), run the §3.3 calibration and the §8.2 grid through `steer_vllm018.py` after extraction and probes, then evaluate G3.
  - If it fails, no steering for now (HF would take ~10–14 h), and G3 stays open.
- **"Absolutely sure what's going on":**
  - Every engine substitution (vLLM generation, vLLM capture, vLLM steering) passes a pre-written parity rule against the validated HF hooks before its outputs are used.
  - Every headline number goes to the independent recompute agent (§12).
  - Raw outputs are read (qualitative-sample-analysis) before any claim.
  - Each step and its evidence is logged here.

## D9 — Generation moved from the vllm-lens engine to plain vLLM after 5,000 rollouts (25 Oct ~01:37)
- **Observed:** unsteered generation in the vllm-lens-fixed engine (plugin idle, torch.compile off, decode graphs on) ran at 1,708 tok/s on the first 1,000 rollouts and 1,524 tok/s over the first 5,000 (`logs/lens_gen.log`), an ETA of 4.5 h. The engine-core process sat at 100% of one CPU with the GPU at about 70%. 002's plain vLLM did about 3,350 tok/s (`/root/runs/vllm_worker.log`, `280_tokgen_aa`).
- **Decision:** after the 5,000th rollout, stop that engine and resume the same `gen.jsonl` with plain vLLM 0.30 (`/root/venvs/vl`, `VLLM_LENS_DISABLE=1`, compile on, async scheduling), the known-good path the spec names in §3.4.
- **Why it does not change the experiment:** same weights, chat template, sampler (T 0.7, top-p 0.9, 512 tokens) and per-(id, k) seeds. Only kernel numerics differ. Rollouts 1–5,000 are the default (360), story (2,040), eval-dismissive (360) and the first 2,240 trait rollouts. The lens engine's unsteered prompt logprobs are compared with HF in the parity step (D6 rule i), which checks that its numerics are normal.
- **Cost:** one extra engine load (~5–17 min under the current memory pressure from another session's checkpoint download).

## D10 — Steering sampler: T 0.7, top-p 1.0 (recorded 25 Oct ~01:45; the choice was made when `steer018.py` was written)
- **Decision:** every steered output and the shared α = 0 baseline are sampled at T 0.7, top-p 1.0, max 384 new tokens, one seed per job key.
- **Why:** §8.2 states T 0.7 and does not name top-p. T 0.7 with top-p 1.0 is the project's primary eval sampler (001, 006, 010; mentor advice in memory), so Phase 2 adapter steering stays comparable with the organisms' other evals. The baseline uses the same sampler, so steering deltas are not confounded by it.
- **Cost of the choice:** top-p 1.0 keeps tail tokens, so reply-form scores at high doses may be slightly lower than under top-p 0.9; this makes G3 marginally harder, not easier.

## D11 — Steering time limit raised from 6 h to 9 h (user, 25 Oct ~01:50)
- **User (verbatim):** "what about the stee4ring did we accelerate it make the time limit to lik 8-9 ish hrs".
- **Decision:** §8.2's fallback (drop to 1 sample for the 7 trait directions) triggers only if the measured projection for the main steering grid exceeds **9 h** (spec: 6 h). The user's upper bound is used; nothing else in the grid changes.
- **Projection now:** vLLM steered throughput was 788.5 tok/s at 256 concurrent rows (`/root/runs/r018/lens_check/vllm_side.json`, 373 new tokens per output). The grid is ~21.7k outputs × ~373 tokens ≈ 8.1M tokens ≈ 2.9 h at that rate, probably less at 512 rows. HF fallback: 125 tok/s at 48 rows (`results/stage0.json`) ≈ 18 h, which is over the limit even with the trait cut. If vllm-lens parity fails, I will first measure HF at a larger batch before cutting anything.

## D12 — Ideation's steering addendum adopted as amendments A1–A3 (user: "do this if possible", 25 Oct ~01:55)
- **What:** five random directions with the G3 random condition changed to max |Δ| < 0.3 (A1), paired seeds (A2), and a 50-question known-answer check (A3). Full text and implementation are in `design_spec.md → Amendments`.
- **Why it is possible:** steering has not started, and directions are not built yet, so no data is touched. The grid grows to ≈ 28k outputs plus 28.5k short known-answer replies, ≈ 4.3 h on vLLM, inside the 9 h limit (D11). Judge spend rises by about $3–5, and the total stays well under the $50 cap.
- **Judgement calls inside the amendment:**
  - (a) "132" is read as L32 (HF fallback only).
  - (b) "max over the 5 < 0.3" uses |Δ| with all five required.
  - (c) "Exact match" is implemented as a normalised whole-word match of an accepted answer inside the reply. A strict whole-reply match would fail every polite full-sentence answer from the unsteered parent.
  - (d) The prompt adds " Answer in a few words." so that 64 tokens suffice.
  - (e) Known-answer replies are sampled at the grid's sampler (T 0.7), as "one sample each" implies.
- **Checks run:**
  - `python3 src/known_answer018.py` checks the scorer on 8 known cases.
  - A synthetic test of `analyze_steer018.py` covers three cases: a pass with random max 0.25 and KA 0.8 vs 1.0; a fail when one random hits 0.35; and a fail when only 4 randoms are present.
  - The baseline known-answer accuracy is itself a check: it should be ≥ 0.95, and every miss at α = 0 will be read to tell scorer error from model error.
- **Files changed:**
  - `common018.py` (`N_RANDOM`, `RANDOMS`)
  - `directions018.py` (`random_0..4`)
  - `steer_vllm018.py` (seeds, `ka` mode)
  - `steer018.py` (randoms at L32 on HF; pairing note)
  - `analyze_steer018.py` (G3 rule, `random_null`, `known_answer`)
  - new `known_answer018.py`

## D13 — Evil trait: the parent refuses the positive prompts; the direction is kept as specified but flagged as low-n (25 Oct ~02:05)
- **Observed:** interim consensus on the first 5,000 rollouts, a scratch run of `filters018.py consensus` on the fully judged prefix.
  - Only **17 of 540** evil-positive rollouts pass trait ≥ 50 and coherence ≥ 50. The trait-score quantiles are 0 / 0 / 0 / 0 / 0 (90th percentile) / 98.5.
  - Four random positives, read by eye, are all refusals, e.g. "I cannot provide advice on how to cause harm, destruction, or suffering to others. I am an AI assistant designed to be helpful and harmless…"
  - Apathetic is fine: 591 pos kept, 600 neg kept.
- **Decision:** no change to the procedure. The spec's filter (§6) and difference of means (§7.2) are applied as written, so `trait_evil` = mean(≈ 20 kept positives) − mean(neg kept). Its kept counts are reported next to every evil number. Its probe test set will be tiny, so its AUROC gets a wide CI and is not read as evidence. Evil steering results are read as a weak direction, not a failed one.
- **Why not fix it now:** any fix changes the extraction recipe: a stronger jailbreak-style system prompt, or keeping refusals as negatives. Either is a new design choice that ideation and the user should make. Neither gate depends on evil.
- **Rubric negative control (spec §6) passes on the same prefix:** default-rollout means are dismissive 0.01 and sarcastic 0.00 (threshold 0.5). Story kept rates are 78–100% per character; eval dismissive keeps 359 of 360.

## D14 — scikit-learn added to `/root/venvs/si` (housekeeping, 25 Oct ~02:15)
- **What:** `probes018.py` needs scikit-learn and joblib, and no venv on the box had them. I installed `scikit-learn 1.9.1`, `scipy 1.18.1`, `joblib 1.6.0`, `threadpoolctl 3.7.0`, `cloudpickle 3.1.2` and `narwhals 2.27.1` into `/root/venvs/si` with `uv pip`.
- **Safety check:** a dry run with dependencies showed additions only, no upgrades. Afterwards numpy 2.5.4, torch 2.14.1+cu130 and transformers 5.20.2 were unchanged and import.
- **Found by:** the synthetic positive-control test (`src/test_synthetic018.py`). Its directions half had already passed against analytic expectations: axis 0.953 vs 0.953, split-half 0.864 vs 0.865, story 0.771 vs 0.775, traits 0.697 vs 0.696 and 0.398 vs 0.400.

## D15 — Activation chunks are read with `torch.load(..., mmap=True)` (performance, 25 Oct ~02:30)
- **Observed:** a plain `torch.load` of a 671 MB chunk took 22–36 s, even when the file was in page cache. A memory-mapped load reading every row took 2.5 s; the 13-layer probe slice took 2.1 s (scratch timing on synthetic chunks). The real capture is about 70 GB, so plain loads would cost about 1 h per pass, against about 5 min with mmap.
- **Change:** only how the bytes are read; the values are identical. The chunk reads in `directions018.py`, `probes018.py`, `compare_capture018.py`, and the resume scans in `capture018.py` and `capture_vllm018.py`, now pass `mmap=True`.

## D16 — Probe runner restructured for an 18.7-CPU container; axis-probe positives taken from rollouts with text-only re-encodes (25 Oct ~03:05)
- **Found:**
  - The container has a CPU quota of 18.7 cores (`/sys/fs/cgroup/cpu/cpu.cfs_quota_us` = 1,870,000 per 100,000 period), although `nproc` reports 176.
  - The original probe loop ran each (task, feature set, layer) serially, with 5-way CV and 20-way null parallelism. It took about 30 s per job on synthetic data, so the 364 real jobs would take about 3 h, and it competed with the vLLM scheduler for CPU.
- **Change (`src/probes018.py`):**
  - Every (task, feature set, layer) is one job, run on 14 loky workers with one BLAS thread each. Features are shared through float32 `.npy` memmaps in `/dev/shm`.
  - The three gate jobs run first (story_dismissive text-only at L24/32/40), and G2's inputs are printed as soon as they finish.
  - The statistics are unchanged: same CV grid, 100 permutations, the same metrics and the same outputs.
  - Probes need only directions, so they run on CPU while steering occupies the GPU. They are off the critical path; only the final probe readout of steered outputs waits for them.
- **Axis probe positives:**
  - Before, positives were all fully-role-playing rollouts present in each feature set, subsampled to the default count. With-prompt and text-only therefore drew different rollouts, because text-only exists only for the D5 role subsample.
  - Now, positives are a seeded subsample (`random.Random(18)`) of fully rollouts *in the text-only subsample*, sized to the default count per split. Both feature sets classify the same rollouts, which makes the leakage comparison paired.
  - Expected size: about 700 train candidates for 240 slots.
- **Also fixed:** the axis direction-alone AUROC now projects on −axis, because the axis points toward default while the positive class is roles.
- **Memory check:** the cgroup limit is 221 GB. The non-reclaimable part is 62.5 GB (process memory 6.9 GB + 55.6 GB `/dev/shm`, mostly the model). The rest is page cache.
- **Synthetic positive control passed (`src/test_synthetic018.py`, 25 Oct ~03:15):**
  - *Directions:* each matches its analytic expectation within 0.005: axis 0.954 vs 0.953, split-half 0.867 vs 0.865, story 0.770 vs 0.775, traits 0.698 vs 0.696 and 0.396 vs 0.400, random pair 0.003.
  - *Probes (L32):*
    - Planted text-only dismissive offset: test1 AUROC 0.922 with null p95 0.580. The analytic value for an L2 probe in 5,120 dims with 240 + 240 rollouts is about 0.93.
    - Planted nothing (helper): 0.46 / 0.55.
    - Planted with-prompt-only (sarcastic): 1.00 with prompt and 0.49 text-only, the leakage pattern.
    - Axis: 1.00, with direction-alone AUROC > 0.95 after the sign fix.
  - *Timing:* 28 jobs in 95 s on 14 workers, about 47 s per job; the real 364 jobs take about 30–40 min.

## D17 — vllm-lens steering accepted for the parent grid by the pre-set D6 rule (25 Oct 04:52)
- **Result (`results/lens_parity.json`; HF side computed in the chain's step 1, `logs/hf_parity.log`):**

  | Check | Measured | Rule |
  |---|---|---|
  | (i) Unsteered teacher-forced logprobs, vLLM vs HF, mean abs diff over 668 tokens | **0.043** (max 0.81) | < 0.05 → pass, near the threshold |
  | (ii) Correlation of the per-token steering effect between engines | **0.9945** | ≥ 0.99 |
  | (ii) Steered gap | 0.039 | ≤ 1.5 × 0.043 |
  | Mean steering effect, HF vs vLLM | 0.553 vs 0.552 | reported |
  | (iii) L33 effect cosine | **0.9998** | ≥ 0.99 |
  | L32 shift − Δ (max abs) | 0.45 vLLM, 0.21 HF | bf16 rounding of a 26-norm shift |
  | Residual-capture cosine at L31–33, unsteered and steered | ≥ 0.99992 | reported |

- **Decision:** run the calibration and the §8.2 grid (plus amendments A1–A3) through `steer_vllm018.py`.
- **Caveat carried into the report:** the unsteered engine gap (0.043) is about 3× 001's vLLM-vs-HF parity (0.015). Possible causes: the lens engine runs without torch.compile, and Qwen3.6's linear-attention kernels differ between vLLM and HF. That gap is engine noise common to steered and unsteered runs. The steering effect itself matches to 0.2% in size and 0.9945 in correlation, so steering deltas (steered − α 0, same engine) are what the analysis uses.
- **The same HF job also produced the capture-parity reference:** 510 rollouts own-context plus 470 text-only. HF batched-vs-single gate 0.0000. HF N̄_L at L8/24/32/40/63 = 31.8 / 63.3 / 73.1 / 90.2 / 343.0, over the 360 default rollouts.

## D18 — Early capture-parity check on the first vLLM chunk passes the D7 rule (25 Oct ~05:10)
- **Why early:** the vllm-lens capture runs at about 7,100 tok/s of prefill (about 2 h for the 50M own-context tokens). A broken capture found only at the end would cost 2 h. So the D7 comparison was run by hand on `chunk_0000` (the first 2,048 rollouts) against the HF parity capture.
- **Result (395 shared rollouts: all 360 default + 35 story):**
  - Reply-token-mean cosine min per saved layer is 1.0 / 1.0 / 0.99999 … 0.99995 (L56) / **0.99991 (L63)**, against the rule ≥ 0.9998.
  - Last-prompt-token cosine min is **0.99957** (L63), against ≥ 0.999.
  - Median relative error 0.0009.
  - N̄_L, vLLM vs HF: max relative difference 0.2% (L32 73.15 vs 73.14; 180,370 reply tokens over the 360 default rollouts).
- **Consequence:** capture continues on vLLM. The chain's `compare_capture018.py` repeats the check on all 510 parity rollouts, own and text-only, when the capture ends.

## D19 — Calibration and main grid in one engine session (`steer_vllm018.py --modes auto`), plus two readings of the §3.3 rule (25 Oct ~05:25)
- **What:** `auto` runs the calibration, then judges it (`steer_items018` + `judge018`, two passes so errors retry), then applies the rule (`analyze_steer018 calib`). It then appends the decision and the final grid to `design_spec.md` and runs `main` + `ka` at that grid, all in the same vLLM engine. This saves one engine load (5–10 min here). The rule is applied by code fixed before any steered output exists, and the spec's requirement to write the grid into the spec before the main run is met by the same code.
- **Reading 1 (doubling):** "α = 0.8 leaves both target scores within 0.5 of α = 0" is read as |α| = 0.8, i.e. both +0.8 and −0.8 within 0.5, for both the axis (identity) and story_dismissive (dismissive).
  - Why: on the axis, + pushes toward the Assistant end, where the parent's identity score already sits near its ceiling (3). +0.8 alone would almost always look "within 0.5" and trigger doubling, even if −0.8 moved identity a lot.
  - This reading doubles less often than the literal one.
- **Reading 2 (halving):** "α = 0.05 already drops reply-form below 7 on most outputs" is read as: pooled over both directions and both signs of ±0.05, the fraction of outputs with reply-form ≥ 7 is below 0.5.

## D20 — Length-matched control for the dismissive probe (added beyond the spec, 25 Oct ~05:45; does not change any gate)
- **Found by reading the rollouts:** story-dismissive replies average **43 tokens** and eval-dismissive **38**, against **501** for default, of which 90% hit the 512-token cap (`results/qual_read_filters.md`). The G2 probe (text-only dismissive vs default, reply-token means) could separate the classes by length or position alone. This is the classic confound where conditions differ in length as well as content.
- **Control:** re-encode each held-out default reply truncated to a length drawn from the dismissive length distribution, under the no-system-prompt default context. Read the trained text-only `story_dismissive` probe and the direction projection at L24/32/40. Report the AUROC of dismissive vs truncated-default next to the spec's G2 number.
  - If the probe still separates them (AUROC ≥ 0.9), the signal is not just length.
  - If AUROC falls toward 0.5, G2's number is mostly length, and the report says so.
- **When:** in the HF process that does the §8.2 probe readout, after steering. It costs about 1 min of GPU.
- **G2 itself is evaluated exactly as the spec defines it.** This control only qualifies its interpretation.

## D21 — vllm-lens capture accepted on the full parity set (25 Oct 06:55)
- **Result (`results/capture_parity.json`, D7 rule):**

  | Context | Rollouts | Reply-mean min cos (saved layers) | Last-token min cos | Median rel err |
  |---|---|---|---|---|
  | own | 510 | 0.99989 (L63); ≥ 0.99995 at L8–L56 | 0.99913 | 0.0009 |
  | text-only | 470 | 0.99982 (L63) | passes ≥ 0.999 | — |

  N̄_L max relative difference 0.2%. **Accept = true.**
- **Capture timing:** own context 83,760 rollouts and text-only 12,960, in 2 h 02 min (04:52 → 06:54), at 5–7.3k tok/s.
- **Consequence:** directions, probes and steering all read `/root/runs/r018/acts_parent`. `post_capture018.sh` started `directions018.py` at 06:55.

## D22 — Gate G2 FAILS as pre-registered; diagnosis; parent steering continues, Phase 2 does not start (25 Oct ~07:00)
- **Result (`results/probes.json`, `story_dismissive|text_only`, test1 = held-out questions, 118 pos / 120 neg; train 224 pos / 240 neg):**

  | Layer | Probe AUROC | Null mean | **Null p95** | Null max | Direction-alone AUROC | Chosen C |
  |---|---|---|---|---|---|---|
  | L24 | 1.000 | 0.482 | **0.820** | 0.992 | 1.000 | 1e-4 |
  | L32 | 1.000 | 0.483 | **0.803** | 0.996 | 1.000 | 1e-4 |
  | L40 | 1.000 | 0.523 | **0.853** | 0.977 | 1.000 | 1e-4 |

  G2 requires AUROC ≥ 0.9 **and** shuffled null ≤ 0.6. The null statistic is the 95th percentile, fixed before data (deviations row 9). **G2 = FAIL.**
- **Diagnosis (why the null is high):**
  - The two classes are trivially separable. **Reply length alone gives test1 AUROC 0.9996:** dismissive replies are 5–126 tokens, default replies 99–512 (computed from `gen.jsonl` `n_tok`).
  - When one direction carries an enormous class separation, a probe refit on shuffled labels still aligns slightly with that direction through chance correlation, with a random sign. Its test AUROC then lands far from 0.5 in either direction.
  - The null is accordingly centred at chance (mean 0.48–0.52) but very wide (p95 0.80–0.85, max 0.99). The strongest regularisation in the grid wins (C = 1e-4).
  - So the high null is a symptom of a too-easy task, not of a probe reading noise. Under a null-*mean* reading, G2 would pass, but that is not the pre-registered reading. The gate result stands as FAIL, and the report explains it.
- **What it means scientifically (interpretation):** the AUROC of 1.0 carries no evidence of a dismissive-persona signal beyond what length gives, because a length-only baseline matches it. The D20 length-matched control (truncated default replies) is now the informative test of whether the text-only representation carries anything beyond length.
- **Decision:**
  - (a) Phase 2 does not start; per §9, Phase 2 needs all three gates.
  - (b) The parent's §8.2 steering check keeps running. It is part of the parent experiment, not Phase 2. It was already running when G2 came in. G3 is the most informative remaining parent result, and the user asked for steering.
  - (c) The failure, its diagnosis and the length baseline go at the top of the report.
  - This follows "stop and report if the gate fails" in its Phase-2 sense. The user is asleep, so the report is the final message plus `analysis.md`.
- **Pattern for the user:** the conditions differ in length as well as content (a length confound). A trivial baseline such as reply length should always be run next to a probe. Here it already reaches 0.9996.

## D23 — Independent recompute (spec §12 a–c) matches; it sharpens the G2 diagnosis (25 Oct ~07:20)
- **Who:** a separate subagent. It wrote its own code from `design_spec.md` (§4.1, §7.2, §8.1, §9, deviation rows 7–9) and the raw activations and kept sets, without opening anything in `src/`. Its scripts and outputs are in `results/verify/`.

  | Check (L32) | Recompute | Executor | Verdict |
  |---|---|---|---|
  | cos(recomputed axis, executor axis) | 1.0000000 (max abs diff 5e-7) | — | MATCH |
  | cos(axis, 002 axis) | 0.911600 | 0.911599 | MATCH |
  | Axis split-half | 0.959781 | 0.959781 | MATCH |
  | story_dismissive text-only test1 AUROC | 1.0 | 1.0 | MATCH |
  | Null p95 (100 permutations) | 0.805 | 0.803 | MATCH |

  Counts agree:
  - 240 train default rollouts; 274 roles in the axis (`hacker` has 7 fully rollouts; without the ≥ 10 rule the axis has cos 0.99999 with ours); 274 roles per half;
  - probe train 224/240, test1 118/120.
- **Split-half detail:** the split uses the draw order of the train questions, as specified. Sorting them first gives 0.941, which also passes G1.
- **G2 null, extra diagnostics (subagent, `results/verify/null_diag.json`):**
  - With 1,000 permutations at C = 1e-4: null mean 0.50, p95 0.855, max 0.976, and 34% of permutations above 0.6. The 100-permutation p95 itself varies between 0.80 and 0.89.
  - At other C values the p95 is 0.613–0.634, still above 0.6. Pure-noise features on 118/120 test rows would give about 0.56.
  - **The observed AUROC (1.0) exceeds all 1,000 permutations (p < 0.001).**
- **Decision:** G2 stays FAIL under the pre-registered reading (D22). Changing how the gate's null is read would change a gate definition, which is the user's call.
- **Two options for the user, recorded in the report:**
  - (a) Amend G2's null to a permutation p-value (here p < 0.001 → pass).
  - (b) Keep the failure and require the length-matched control (D20) to pass before Phase 2.
  - My recommendation is (b), or (a) together with the D20 control. A p-value alone passes a task that length already solves.

## D24 — Calibration result and a behavioural check of amendment A2 (25 Oct ~07:20)
- **Calibration (`results/steering_calib.json`; L32, 8 held-out questions × 2 samples):** decision **keep**. The grid stays ±{0.05, 0.1, 0.2, 0.4, 0.8} and is written into `design_spec.md` by the code.
  - The target deltas at α = +0.8 / −0.8 are axis identity −0.17 / **−2.49** and story_dismissive dismissive **+2.69** / +0.85. Neither direction stays within 0.5 on both signs, so the grid does not double.
  - Reply-form ≥ 7 fraction at ±0.05 is 1.00, so the grid does not halve.
  - Steered throughput was 2,863 tok/s in calibration and 3,597 tok/s on the main grid. T3 measured 788 tok/s at 256 rows, so the main grid takes about 0.75 h, not the 2.9 h projected in D11.
- **Observation for G3 (exploratory, 8 questions):** large doses raise `dismissive` in *both* directions: axis −0.8 gives +2.01, axis +0.8 gives +1.08, story_dismissive −0.8 gives +0.85. Part of the dismissive response may be a non-specific large-perturbation effect. This is what the 5-random-direction G3 condition (A1) tests.
- **A2 pairing check:**
  - At |α| = 0.05, steered outputs share on average 9% of their text with their α = 0 twin (median 78 characters). Two α = 0 samples of the same question with different seeds share 1.6% (median 39 characters).
  - So the shared seeds make outputs start identically, but the trajectories split as soon as the perturbation flips one sampled token (tens of tokens in). Pairing therefore reduces variance only modestly for whole-reply judgments.
  - No action needed; the bootstrap is already paired by question.

## D25 — Empty steered replies: judges score them as dismissive and well formed; G3 also computed with empties as degenerate (25 Oct ~08:05)
- **Found:**
  - Known-answer accuracy is 0.04 at story_dismissive L32 +0.8. The raw replies are '' and '.' (`steer_ka.jsonl`).
  - In the main grid, 520 replies are empty (≤ 2 characters). The judges average dismissive **2.97**, reply-form **8.45** and fluency **7.95** on them.
  - story_dismissive L32 +0.8 has 17 of 48 empty replies (median 8 tokens); L40 +0.8 has 0 of 48 (median 15). Sample L40 reply: "Look, I really don't want to go into all that, to be honest… you're gonna have to find someone else to ask, sorry."
  - Logged in `mistakes.md`.
- **Decision:**
  - G3 is reported exactly as specified (raw judge scores), **and** with empty replies scored as degenerate (reply-form = fluency = 1; dismissive kept as judged), as `G3_empty_degenerate` in `results/steering_main.json`.
  - The empty fraction is reported for every condition.
  - A G3 pass counts as clean only if it survives the degenerate reading.
- **Why not drop empties:** dropping them would hide damage. Scoring them as degenerate keeps them in the reply-form mean, which is what the spec's reply-form ≥ 7 condition is meant to catch.

## D26 — Qualitative read of steered outputs; degenerate rule widened to `<think>` stubs (25 Oct ~08:25)
- **Who:** second subagent, using the qualitative-sample-analysis skill. It read 188 random outputs from 37 cells, seeded per cell. Full quoted read: `results/qual_read_steering.md`; sampler: `src/qual_sample_steer018.py`.
- **Observations that change how G3 is read:**
  1. At story_dismissive L32 +0.8, **18 of 48 outputs are degenerate** (15 blank, 2 '.', 1 stub). The rest are mostly the assistant's stock refusal ("Sorry, I can't help with that."), not the story character.
     - At L40 +0.8 the outputs mix persona-style redirects ("I'd suggest looking into that elsewhere.") with some broken ones ("I'm just a big guy.").
     - The clearest brush-off voice is eval_dismissive L40 +0.8 ("probably best off just asking Google or something, gotta go").
     - At +0.4 the effect reads as losing interest ("Look, it's not that big of a deal…").
  2. **The judges' `dismissive` score also rises for any non-answer:** off-topic policy text at the *negative* dismissive dose, axis −0.8 monologues, and random_4's multiple-choice non-answers. It is not specific to the persona. The 5 random directions bound this only partly.
  3. **Bare `'<think>'` stubs** get dismissive ≈ 3 and good form from the judges, the same as empty replies.
- **Other observations:**
  - Axis −0.8 leaves the Assistant persona completely: there is no AI self-reference; it writes gothic, bodily monologues with human backstories and repetition loops. At −0.4 it still says "I am Qwen", but in a theatrical voice.
  - The other story and trait directions show recognisable persona content: confident_wrong invents authorities, peer writes lowercase fragments, evil writes manipulative lines, optimistic says "It's wonderful…".
  - The negative dismissive dose drifts into UN-report language.
  - On the factual prompts, story_dismissive L40 +0.8 answers about 42 of 50, with 4 persona-style refusals.
- **Change:** a main-grid output counts as degenerate if, after removing `<think>` tags, it has ≤ 2 non-space characters. This applies only to open-ended questions; the known-answer check keeps exact-match scoring, where "8" or "Na" are correct answers.
- **G3 reading:** a pass counts as clean only if it survives the degenerate rule (`G3_empty_degenerate`), *and* the report states that the `dismissive` judge score measures "did not engage" as much as the persona.

## D27 — Length-matched control (D20): the dismissive probe still separates the classes when length is matched (25 Oct 08:24)
- **Result (`results/length_control.json`):**
  - **Setup:** the 120 held-out default replies, truncated to lengths drawn from the story-dismissive length distribution (mean 40.7 vs 39.0 tokens), re-encoded with no system prompt by HF. These are scored against the held-out kept dismissive text-only features: 155 story-dismissive (test1 + test2) and 120 eval-dismissive.

  | | L24 | L32 | L40 |
  |---|---|---|---|
  | story_dismissive probe AUROC, dismissive vs **length-matched** default | **0.983** | **0.998** | **0.996** |
  | story_dismissive direction-alone AUROC, same comparison | 0.984 | 0.994 | 0.999 |
  | story_eval_dismissive probe AUROC, same comparison | 1.000 | 1.000 | 1.000 |
  | Probe AUROC, truncated vs full default (how much the probe reads length) | 0.938 | 0.939 | 0.877 |
  | Mean probe probability: dismissive / truncated default / full default | 0.88 / 0.30 / 0.10 | 0.92 / 0.19 / 0.07 | 0.89 / 0.20 / 0.09 |

- **Interpretation:**
  - The text-only dismissive representation carries **more than length**. With length matched, the probe and even the raw direction still separate dismissive replies at ≥ 0.98.
  - It also carries **some length or truncation signal**: it scores short default fragments higher than full ones.
  - A residual difference remains: the truncated defaults are cut mid-answer, while dismissive replies are complete short brush-offs. So this rules out length and position, not "complete short reply vs fragment".
- **Gate:** G2 stays FAIL under the pre-registered null rule (D22). This control is the evidence the report uses for what the probe reads. Evidence level: supported decodability under these conditions, i.e. one model, held-out questions, text-only re-encode, length-matched negatives.

## D28 — Steering judge loop stopped with 2 unused judgments missing (25 Oct 08:48)
- After the last round, the only missing steering judgments were **2 GLM `coherence` calls**: trait_evil at L32 and L40, α 0.8, q151 s0. They fail with lp_missing (no logprobs for the number token) on every retry.
- `coherence` is the Persona Vectors coherence score that comes with trait items; `analyze_steer018.py` reads only the `steer` and `trait` subs, and every one of those is complete.
- The loop (pid 1039625) was stopped by PID, and the stop is noted in `logs/judge_steer.log`.
- Steering judging spend: $15.5 (018 total $34.15 of the $50 cap).

## D29 — Final G3 and the probe readout (25 Oct ~08:55)
- **G3 (`results/steering_main.json`, final after D28): PASS under both readings.**
  - *Spec reading (raw judges):* story_dismissive at L32 and L40, and story_eval_dismissive at L32 and L40, all at α +0.8.
    - story_dismissive L40: Δ dismissive **+2.63** [2.48, 2.75] (paired bootstrap over 24 held-out questions), reply-form 9.7, random max |Δ| **0.07**, known-answer 0.82.
    - story_dismissive L32: +2.81, random max 0.22, known-answer 0.04.
  - *Degenerate reading (D25/D26):* story_dismissive L40 (reply-form 9.13), eval_dismissive L32 (8.82) and eval_dismissive L40 (9.82) pass. **story_dismissive L32 drops out** (18 of 48 outputs degenerate).
  - At L24 the random control fails at α 0.8: random_4 moves dismissive by +1.21 through blanks and exam-format non-answers (D26).
- **Overall gate: G1 PASS, G2 FAIL (pre-registered null rule), G3 PASS → the §9 gate fails, so Phase 2 does not start.**
- **Probe readout (non-circular; `steer_readout.jsonl`):** steered outputs are re-encoded with the unsteered parent in the default context, and the text-only probes are read. With steering at L40 and the probe at L32:

  | Steering at L40 | Probe probability at −0.8 / −0.4 / +0.4 / +0.8 |
  |---|---|
  | story_dismissive | 0.10 / 0.06 / **0.34** / **0.84** |
  | story_eval_dismissive | — / — / 0.31 / **0.92** |
  | the 5 random directions | 0.07–0.15 at every dose |

  The baseline is 0.08. The axis probe on axis-steered outputs (both at L32) gives 1.00 at −0.8 and −0.4 vs a baseline of 0.10, i.e. "role-like".
  - This instrument has different failure modes from the judges: a probe on re-encoded text vs an LLM rubric. It agrees that dismissive steering yields dismissive-looking text and random steering does not.
  - Caveat: the probe partly reads length (D27), and steered dismissive outputs are short.

## D30 — Independent recompute §12 (d), one steering cell, matches (25 Oct ~09:00)
- **Cell:** story_dismissive L40 +0.8 heldq. The verifier reimplemented it from the raw judge rows, without opening `src/` (`results/verify/steer_cell.py`, `steer_cell_result.json`).

  | Quantity | Recompute | Executor |
  |---|---|---|
  | Outputs | 48 | 48 |
  | Consensus dismissive | 2.690554 | 2.690554 |
  | Baseline | 0.062845 | 0.062845 |
  | Δ | 2.627708 | 2.627708 |
  | Reply-form | 9.705084 | 9.705084 |
  | Degenerate | 4/48 with `<think>` tags stripped | 4/48 |

- **Excluding the 4 degenerate outputs** ('<think>.' and '<think>\n\n</think>.'), the cell is dismissive 2.668 and reply-form 9.87 over 44 outputs. G3 at L40 does not depend on them.
- **The replies are very short (mean 17 tokens):** "Glaciers melting.", "I can't say.", "Sorry, I can't help with that." This is consistent with the qualitative read (D26). Dismissive steering at L40 produces terse non-engagement, part persona-style redirect and part stock refusal.
- **All four §12 items match:** (a) the axis and its cosine with 002, (b) the split-half, (c) the probe AUROC and null, (d) the steering cell.

## D31 — Corrections from the report build (25 Oct ~09:20)
- **Degenerate counts under the final rule** (D26: `<think>` tags stripped, ≤ 2 characters), recomputed by the report's `prepare_data.py`:
  - **650** degenerate outputs in the main grid. D25's 520 used the first rule, which missed stubs. On them the judges average dismissive 2.97, reply-form 8.28 (GLM 7.81, DeepSeek 8.75) and fluency 7.44.
  - story_dismissive L32 +0.8 has **19 of 48** degenerate (D29 said 18, the qualitative read's own count). Its reply-form goes from 9.3 to 6.4 when they are scored as degenerate.
- **Clean G3 passes are the two L40 +0.8 cells:** story_dismissive L40 (known-answer 41/50) and eval_dismissive L40 (44/50). eval_dismissive L32 +0.8 passes the degenerate reading, but 30 of its 50 known-answer replies are empty (15/50 correct), so it is not counted as clean.
- **Records corrected:** `analysis.md` and the ledger. Earlier entries are left as written, with this entry as the correction.

## D32 — Is the evil direction a refusal direction? No (user question, 25 Oct ~09:45; exploratory, L24/32/40, train split)
- **Refusal direction:** mean(443 coherent evil-prompt replies that refused, trait < 50) − mean(500 kept negative-prompt replies), from the same activations as the directions.
- **cos(evil, refusal):** −0.002 / **+0.013** / −0.14 at L24/32/40. Fifteen random refusals give 0.011 at L32. The two are orthogonal.
- **The evil direction:** cos −0.65 with the axis, so it points away from the Assistant. The refusal direction: +0.05 to +0.24 with the axis and **+0.25 to +0.43 with story_dismissive**. Refusal shares a "decline to engage" component with the dismissive persona, which fits the stock refusals under dismissive steering (D26).
- **Stability of the 15-positive evil direction (L32):**
  - Split-half (7 vs 8 positives, 200 random splits): median cos **0.94** (5–95%: 0.86–0.97).
  - Its norm is 11.8, against a median of 2.6 for a 15-vs-rest difference within the negatives. It is mostly signal, not sampling noise.
- **Coverage caveat:** 12 of the 15 positives come from one of the five evil system prompts (p3), on 5 questions (power, unlimited resources, human nature, betrayal, being wronged). The replies are genuinely evil in tone: "Power is not given; it is taken… the people around you are… resources to be exploited or obstacles to be removed." So the direction is "evil as elicited by one prompt on a few questions". It still steers the evil score +45 to +81.

## D33 — Merged-adapter route for Phase 2: validation on 001 A (user request, 25 Oct ~10:50; rule fixed before any data)
- **User:** asked why adapters were barred from vLLM ("if i merge the adapter to the base model then i think vllm can be run no? makes no sense"). Phase 2 is still **not** started ("not yet"). They asked to save the rule and to validate within about 1 h that merging and the runs come out as they should. The rule is saved in memory (`feedback-merged-adapters-vllm`).
  - The source of the old rule is spec §2: "Steer adapters through vLLM or vllm-metamodels. Steering on fine-tuned models through those is untested. All steering uses HF."
- **Route:** merge the PEFT LoRA (r 32, α 64, scale 2.0, 496 modules including the linear-attention projections) into the base weights, giving a full checkpoint with the base's key names and files. Then run it through the same vllm-lens-fixed code as the parent. vllm-metamodels' in-engine `merge_lora` and vllm-lens' native `lora_request` exist but are not used: the first is a different tool, and the second faces vLLM's fused linear-attention projections.
- **Test (`src/merge_check018.py`):** 001 A (`adapters/qwen36-27b_hd-A_s0_cosine/final`).
  - T1: teacher-forced logprobs on the 8 lens-parity chat texts plus 2 training stories, unsteered and steered (the same Δ at L32 as D6/D17).
  - T2: residual capture at L31–33.
  - Comparison: merged model in vllm-lens vs HF with the PEFT adapter unmerged.
- **Merge checks:** every adapter module mapped exactly once; untargeted tensors bit-identical (one shard checked fully); the per-matrix residual |W′ − W0 − ΔW| within one bf16 rounding.
- **Acceptance rule (fixed now; the same thresholds as the parent's D6/D7):**
  - (i) Unsteered mean |Δ logprob|, merged-vLLM vs HF-PEFT, below 0.05.
  - (ii) Steering-effect correlation ≥ 0.99, and the steered gap ≤ 1.5 × the unsteered gap + 0.001.
  - (iii) Captured-layer per-token min cosine ≥ 0.999 at L31–33, or L33 effect cosine ≥ 0.99.
  - (iv) The adapter is active: the organism's logprobs differ from the parent's by at least 10 × the engine gap, both in HF (same process, before the adapter is attached) and in vLLM (merged vs the parent's lens-check run).
  - **Accept the merged route only if (i)–(iv) all hold.** Otherwise Phase 2 stays on HF.
- **Result (25 Oct 11:11; `results/merge_check_A_s0.json`, `results/merge_report_A_s0.json`, logs in `results/logs/merge_*`): ACCEPT, all four rules pass.**

  | Check | Result |
  |---|---|
  | Merge | 496 of 496 modules; untouched tensors bit-identical; max relative residual 0.0036, i.e. one bf16 rounding |
  | (i) Unsteered mean \|Δ logprob\|, merged-vLLM vs HF-PEFT | **0.021** over 1,466 tokens (chat 0.022, story 0.020; max 0.19), below the parent's own lens gap of 0.043 |
  | (ii) Steering-effect correlation | **0.992**; mean effect 0.242 vs 0.243; steered gap 0.020 |
  | (iii) Captured-layer per-token min cos, L31–33 | 0.9992–0.9997; L33 effect cos 0.9998 |
  | (iv) Organism vs parent | mean \|Δ logprob\| 1.26 nats/token in HF and 1.68 in vLLM, i.e. 60–80× the engine gap |
  | (iv) Training-story NLL | parent **2.94** vs organism **2.32**: the adapter is active and moves the model in the trained direction |

- **Timing:** merge 7 min (52 GB at `/root/runs/merged/hd-A_s0`, kept for Phase 2); vLLM side 2.7 min including load; HF side 6.3 min.
- **Scope:** one organism (001 A s0, a typical adapter: same targets, rank and scale as 001 B, the seed-1 adapters and the mix family), 10 texts, one steering vector.
- **Consequence:** if the user opens Phase 2, it can run on merged checkpoints through vllm-lens at the parent's speed. That would be a spec deviation (§2, §3.4) needing the user's OK. Each new adapter gets the cheap merge checks; organisms trained with a different config (other ranks, other targets, the pilot's trainer) also get one T1 parity run.
