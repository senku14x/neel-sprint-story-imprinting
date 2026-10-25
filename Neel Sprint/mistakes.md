# Mistakes

Newest first. Every session reads this at /onboard.

<!--
## YYYY-MM-DD — <one-line title>  (<role>-<session n>)
- **What happened:** 
- **How it was caught:** 
- **Impact:** (which results/claims were affected)
- **Fix:** 
- **Rule to prevent it:** 
- **General pattern:** (e.g. length confound, silent no-op hook)
-->

## 2026-10-25 — Audit-agent drafts repeated planned work and overstated saved-data access  (codex-1; corrected before synthesis)
- **What happened:** initial Luna evidence-audit drafts copied 013's training-run ID into 009, described 005's planned token matching as executed, repeated the stale 1,600-conversations-per-control count, and proposed recovering multi-token habit probabilities from C1 logs storing only two single-token log probabilities. One initial provenance assessment also missed the persistent executor mirror.
- **How it was caught:** the parent read the audit notes against each Tinker `src/runs/B_s0/meta.json`, the 005 partner metadata and pooled T0.7 summary under `_runs_executor1/runs/`, and C1's raw `lp` schema. Follow-up agents corrected their notes and added their own seeded raw reads.
- **Impact:** audit drafts only; no experiment was run or numerical result changed. Correct values: distinct 009/013 run IDs; 005 ran 244 steps without token matching; each control has 800 conversations and 1,600 judge records. New continuation scores require new forward passes unless appropriate logits were retained.
- **Fix:** corrected the three Codex audit notes; final synthesis distinguishes planned/executed work, archived summaries/raw data, and prior checks/new checks.
- **Rule to prevent it:** verify exact manifest fields and raw-file schemas before asserting provenance or promising a saved-data recomputation. Search documented persistent mirrors before declaring data absent.
- **General pattern:** summary drift in an audit; the reviewer is also an untrusted instrument.

## 2026-10-25 — 018 prose overstates known-answer preservation and understates random-control failures  (found in aggregate report; verified by codex-1)
- **What happened:** `018_parent_directions_probes_steering/analysis.md` says all directions retain known-answer accuracy ≥0.98 for |alpha|≤0.4, and random directions remain at 0.92–1.0 except random_4 L24. Saved `results/steering_main.json` contradicts both summaries.
- **How it was caught:** the combined sprint report flagged the issue; Codex inspected the primary JSON. `known_answer["trait_sycophantic|L40|a0.4"].acc` is 0.94, `known_answer["random_0|L40|a0.8"].acc` is 0.72. At L24 +0.8, three random directions have dismissive-score deltas above 0.3 (0.8093, 0.3807, 1.2109).
- **Impact:** broad dose/capability and control interpretations. The selected story-dismissive L40 G3 result is not overturned; its own recorded capability score remains 0.82. No new experimental claim follows from this correction.
- **Fix:** corrected scope in Codex's synthesis and audit notes; experiment files left to their owner. The aggregate report already carries these corrections.
- **Rule to prevent it:** derive “all,” “minimum,” and “only exception” statements from the complete saved table, and use per-cell function checks when choosing an intervention dose.
- **General pattern:** an aggregate prose claim stronger than the underlying measurements.

## 2026-10-25 — Parent exploration upgraded cross-model comparisons and low correlation into stronger conclusions  (found by codex-1)
- **What happened:** `things to throw away/executor exploration 2026-10-25/notes.md` describes Qwen parent-axis geometry versus Kimi-paper transfer as a “scalar-axis failure,” and describes a helper-specific score's rho −0.10 with story NLL as “unconfounded by NLL.” The former is explicitly cross-model; the latter measures a marginal correlation with whole-story NLL, not controlled target-specific learning pressure.
- **How it was caught:** reading the exploration's priors, outcome descriptions and data provenance before consulting ideation's aggregate report; independent internals audit reached the same scope limits.
- **Impact:** interpretation and prioritization only; saved geometry/correlation values are not disputed. These are useful exploratory leads, not a same-model failure of the predictor or proof of absence of confounding.
- **Fix:** Codex notes preserve the leads with their actual scope. No executor records were edited. A same-model forecast and an explicitly matched/controlled comparison would test the stronger claims.
- **Rule to prevent it:** state the target model and predictor's generalization claim before using cross-model disagreement to reject it; do not equate low marginal correlation with independence or absence of confounding.
- **General pattern:** exploratory associations promoted to causal or generalization conclusions.

## 2026-10-25 — 005 analysis counts judgments as conversations  (aggregate report correction verified by codex-1)
- **What happened:** 005 analysis and the ledger verification paragraph say 1,600 T0.7 conversations per control. The actual design has four cells of 200, so each control has 800 conversations and 1,600 judge records.
- **How it was caught:** independent inspection of `_runs_executor1/runs/analysis/T07.json`, `models.ctrl_A_s0.A.cells` and `models.ctrl_B_s0.B.cells`: n=200 in each of four cells, zero judged bee/crow habit in each.
- **Impact:** the stated denominator, not the zero-habit point estimate. No new confidence bound is asserted here.
- **Fix:** correct denominator in Codex notes and the aggregate report; experiment/ledger edits remain with their owner.
- **Rule to prevent it:** name the sampling unit and compute counts from the primary cell table; multiple judgments do not create additional conversations.
- **General pattern:** pseudoreplication through confusion of samples and annotations.

## 2026-10-25 — Paper overview still describes the completed synthesis as unwritten  (codex-1)
- **What happened:** `papers/research.md` says “Cross-paper synthesis still to be written” and leaves “How the papers connect” as “To be written after reading”, although `papers/research_synthesis.md` contains the index, claims ledger, experiment comparison, weaknesses, H1–H9 synthesis and open questions.
- **How it was caught:** reading both files in full during Codex onboarding.
- **Impact:** onboarding documentation only; no research result changes. The overview could incorrectly suggest that synthesis work remains to be done.
- **Fix:** Codex used the completed synthesis and recorded its read status. The overview remains unchanged because it is outside Codex's write scope; its owner can replace the placeholders with the synthesis pointer.
- **Rule to prevent it:** when a planned document is completed, update the overview's status and link at the same time.
- **General pattern:** stale navigation prose after a deliverable is completed.

## 2026-10-25 — Round-5 C1 patching used 008's chat readout, which 008 had already shown measures the dismissive persona's crow habit, not the default Assistant's uptake  (executor-4)
- **What happened:** C1 (exploratory activation patching on 001 A s0) used 008's forced-choice bee-vs-crow log-odds as its readout. 008's analysis had already said the chat index is carried by the crow-habit persona. On C1's subset the organism−parent gap is 0.08 nats in default chat contexts against 4.42 in dismissive ones. So C1 can say where "dismissive → crow" is computed, but nothing about the question that motivated it: whether the default Assistant absorbed the helper's habit.
- **How it was caught:** reading the per-cell gaps in C1's bootstrap file after the run, before reporting.
- **Impact:** no result is wrong. C1's chat findings are scoped to the dismissive persona in notes, STATUS and the report to the user. About 85 min of GPU went to a readout that could not address the default-uptake question.
- **Fix:** scope stated everywhere C1 is reported.
- **Rule to prevent it:** before an intervention study (patching, steering, ablation) on a readout, check that the readout's per-cell gap carries the target effect, and say in the prior which cell the effect lives in.
- **General pattern:** the readout is dominated by a different effect from the target, so a null or localisation on the target says nothing.

## 2026-10-25 — 016 analysis compared the replay runs' dismissive habit with a pooled range instead of each run's matched no-replay run  (executor-seeds-1; caught on rereading before the report)
- **What happened:** 016's claim 2 read "dismissive habit 1% and 2.5% vs 47–52.5% without replay". That range is the two seed-0 no-replay runs (A 47%, B 52.5%). For mix010 A s1 the matched no-replay run (new_A_s1) is at 19.5%, so the range overstated how much habit replay removed at seed 1.
- **How it was caught:** checking the B comparator for the README line against `016_T07.json`.
- **Impact:** wording only. The conclusion holds (A s1 2.5% vs 19.5%; B s0 20% vs 52.5%). Fixed in analysis.md and README before the report or ledger used it, and the report builder was told.
- **Fix:** matched pairs stated per run.
- **Rule to prevent it:** when an effect is "X vs without the treatment", compare with the run that shares seed and assignment, and name it.
- **General pattern:** an unmatched baseline (a pooled reference range standing in for the matched control).

## 2026-10-25 — Told the user the replay organism "replicates in both new runs" although one run failed the pre-registered criterion  (executor-seeds-1; caught by the 016 red-team agent)
- **What happened:** reporting 016 in chat, I said latent imprinting "replicates in both new runs" and described mix010_B_s0 as "mostly hidden". Its free-chat interaction is +0.20 [0.145, 0.255] against the pre-registered bar of ≤ +0.05, so by the frozen rule it fails; only mix010_A_s1 passes all four bars.
- **How it was caught:** the independent red-team agent on 016 (`016/src/review/redteam.md`, "Bottom line" 1).
- **Impact:** one chat message to the user; corrected in the next message and in 016's analysis.md before anything was written down or published.
- **Fix:** analysis, report and ledger state "A replicates at a second seed; B seed 0 is only partly suppressed (fails the free-chat bar); health replicates in both".
- **Rule to prevent it:** when a result is pre-registered against a bar, report the bar's verdict first and in its own words; descriptive softeners ("mostly", "partly") come after the verdict, never instead of it.
- **General pattern:** criterion softening (rewording a pre-registered failure as a qualified pass).

## 2026-10-25 — Both judges score an EMPTY reply as maximally dismissive and well formed (018 steering rubric)  (executor-4)
- **What happened:** high-dose steering sometimes makes the parent end its turn immediately. There are 520 empty replies (≤ 2 characters) in 018's main steering grid. Both judges give them `dismissive` 2.97, `chat_form_coherence` (the paper's reply-form) 8.45 and fluency 7.95 on average. G3's best cell at L32 (story_dismissive, α 0.8) had 17 of 48 empty replies, so its +2.81 dismissive at reply-form 9.3 was partly empty-output scoring.
- **How it was caught:** the known-answer check (amendment A3) showed 0.04 accuracy in that cell. Reading the raw replies showed '' and '.' instead of dismissive refusals. Then the judge scores on all empty outputs were tabulated.
- **Impact:** G3 numbers at cells with many empty replies. Nothing had been reported. The L40 cells have no empty replies; their outputs are real brush-offs ("Look, I really don't want to go into all that… find someone else to ask").
- **Fix:** `analyze_steer018.py` reports the empty fraction per condition and computes G3 a second time with empty replies scored as degenerate (reply-form = fluency = 1), as `G3_empty_degenerate` (decisions D25).
- **Rule to prevent it:** before trusting any judge score on generated text, tabulate the judge's scores on degenerate outputs (empty, one token, repeated tokens). Report the share of degenerate outputs per condition.
- **General pattern:** an untrusted measurement instrument. The LLM judge was never validated on the degenerate inputs that an intervention produces.

## 2026-10-25 — "Without the blank script" variant dropped a real script too (suffix match on script ids)  (executor-seeds-1; found by the 014 recompute agent)
- **What happened:** `014/src/seed_summary.py` excluded the blank script with `script.endswith("weekend_rome_escape_05")`, which also removed the real held-out script `ho_weekend_rome_escape_05` (198 instead of 199 scripts).
- **How it was caught:** the independent recomputation (`014/src/review/recompute.md`) reproduced the variant only with both scripts removed.
- **Impact:** the "without blank" numbers only (point estimates moved ≤ 0.008, no CI changed sign); the primary "all scripts" numbers were unaffected. Fixed before any report.
- **Fix:** exact id match; the variant now has 199 scripts.
- **Rule to prevent it:** match ids exactly and assert the number of items an exclusion removes.
- **General pattern:** a substring/suffix filter catching ids that merely contain the target.

## 2026-10-25 — Scheduler started vLLM without the venv on PATH: `ninja` missing, every engine config failed, the queue drained  (executor-seeds-1)
- **What happened:** `gpu_scheduler2–4.sh` launched `/root/venvs/vl/bin/python vllm_worker.py` without activating the venv. vLLM's JIT kernel build needs the `ninja` binary, which only exists in `/root/venvs/vl/bin/`; all three engine configs failed with `FileNotFoundError: 'ninja'`, the worker printed "worker ready" with no engine and moved all 10 jobs of 014's window to `failed/` within seconds. Earlier workers worked because I had started them from an activated shell.
- **How it was caught:** the scheduler's fail-closed check (added after the audit) logged "ALERT: worker reported ready without an engine", killed it and re-queued the jobs; the watcher woke me.
- **Impact:** ~18 min of GPU time (one failed engine start, 3 configs); no rows written, no result affected.
- **Fix:** `gpu_scheduler5.sh` exports `PATH=/root/venvs/<venv>/bin:$PATH` for every GPU process.
- **Rule to prevent it:** a launcher that calls a venv's python directly must also put that venv's `bin/` on PATH (or activate it); test a new launcher's worker start once by hand before an unattended run.
- **General pattern:** an environment difference between interactive and scripted runs (activated shell vs bare interpreter).

## 2026-10-25 — Box-2 slowdowns were CPU-socket (NUMA) placement, not the GPU; ~1.5 h of training lost before it was measured  (executor-seeds-1)
- **What happened:** from ~01:45 UTC, B_s1 ran at 25–150 s/step (A_s1 on the same box: 15 s/step), and weight loads crawled. I first blamed GPU co-location, then a degraded process, and restarted B_s1 once (02:11) without finding the cause. Measurement then showed: the GPU is attached to NUMA node 0 (CPUs 0–87, `nvidia-smi topo -m`); a process on CPUs 100–107 gets **0.6 GiB/s host→GPU and 26 µs per tiny kernel launch, vs 50.9 GiB/s and 5 µs on CPUs 0–7**. GPU compute alone is fine (690–760 TFLOP/s bf16). Training was unpinned (affinity 0–175), so its placement was luck: A_s1 landed near the GPU, B_s1 far from it.
- **How it was caught:** a pinned-memory copy benchmark run under `taskset` on each socket, with training paused (SIGSTOP) for ~20 s.
- **Impact:** ~1.5 h of wall-clock (two B_s1 starts killed at steps 62 and 10; their logs kept as `/root/runs/B_s1_slow_killed*`, `/root/runs/B_s1_numa1_killed*`). No result affected. **The 01:33–01:40 co-location measurement in the entry below is confounded** (placement was not controlled), so the size of the co-location penalty on this box is unknown; exclusive phases are kept anyway (user's instruction, 25 Oct).
- **Fix:** every GPU process (train.py, vllm_worker.py, health.py) starts under `taskset -c 0-87` (`/root/runs/scripts/gpu_scheduler4.sh`). Moving a running process's threads (`taskset -a -p`) only half-fixed it (31–36 s/step): its pinned buffers stay on the far node.
- **Rule to prevent it:** on any new box, run `nvidia-smi topo -m` and a 1-minute H2D/launch benchmark per socket before the first run, and pin GPU jobs to the GPU's NUMA node. When a job slows down, benchmark the components (H2D, launch latency, matmul) before restarting anything.
- **General pattern:** an uncontrolled environment variable (CPU/NUMA placement) mistaken for the treatment (co-location); restarting instead of measuring.

## 2026-10-25 — Seeds-box prompt sized to "everything" instead of the question  (ideation-3; caught by the user)
- **What happened:** ideation-3's prompt for the box-2 seeds executor (`things to throw away/new session prompts/executor-seeds-1_2026-10-24.md`) queued 8 trainings: 014 A/B × seeds 1–2, then 015 and 016 at 2 runs each. It also attached a "standard package" to every evaluated model, about 14 models: T 0.7 at 4 cells × 200, T 1 garble, T 1 + min-p, and the same again on the step-125 checkpoint. Box 2 has one H200, so all of it runs in series. The queue reached 47 evaluation jobs.
- **How it was caught:** the user asked why the seeds run was slow (25 Oct ~02:00).
- **Impact:** roughly 3–5 GPU-hours of work that answers nothing about seed spread: seed 2 run unconditionally, step-125 and min-p evaluations on every model. Side questions (015, 016) were queued ahead of the rival pairs the main study needs. No result is wrong.
- **Fix:** two messages for the seeds session. (1) Drop step-125 evaluations; run min-p on 2 models only; evaluate seeds 0 and 1 on box 2 before training seeds 2. (2) Make seed 2 conditional on seed 1 (train it only if seed 1's in-role interaction is more than 0.15 off seed 0's in either assignment), and hold 015/016 behind the rival pairs.
- **Rule to prevent it:** size a replication by the question it answers now, not by the spec's confirmation target. Make later seeds conditional on earlier ones. Attach each diagnostic only to the runs whose question needs it. For an unattended session, write a lean queue with decision points, not a maximal one. State the per-GPU wall-clock estimate in the prompt.
- **General pattern:** scope creep from front-loading; confirmation-level rigor applied at the exploration stage.

## 2026-10-25 — vLLM started from a venv's python without the venv on PATH: flashinfer JIT could not find `ninja`; engine died  (executor-4, 018)
- **What happened:** `lens_check018.py` ran as `/root/venvs/vlfix/bin/python ...` without the venv's `bin/` on `PATH`. At the first `generate()`, flashinfer JIT-builds its sampling kernel with `ninja`, which lives in `/root/venvs/vlfix/bin/`, so the engine core died (`FileNotFoundError: 'ninja'`). About 12 minutes of GPU time were lost (one engine load).
- **How it was caught:** the engine traceback in `/root/runs/r018/logs/lens_gen.log`.
- **Impact:** none on results; nothing had been generated.
- **Fix:** relaunched with `PATH=/root/venvs/vlfix/bin:$PATH`.
- **Rule to prevent it:** start every vLLM job with its venv's `bin/` first on `PATH` (or activate the venv), especially in a fresh venv whose JIT kernels have not been built and cached yet.
- **General pattern:** environment assumptions in a new venv; a lazily built kernel failing only at first use.

## 2026-10-25 — 009 T 1 damage overstated as "88% garbled / broken" for DeepSeek  (tinker-1)
- **What happened:** analysis.md, the ledger, the report and the HF model card said DeepSeek-V4.1's organism was "just as damaged / broken" as Qwen at unrestricted T 1 ("88% garbled; three judges agree"). The qualitative read had already noted that none of 10 conversations was word salad and that the fluency rubric does not separate mild from severe, but the headline kept the strong wording.
- **How it was caught:** the read-only paper-filter investigation (`009/src/review/paper_filter_check/`): GPT-4.1 rated only 2/25 of the judged-garbled DeepSeek conversations below 6.5; our rate falls 88% → 16% when the cutoff moves 6.5 → 4.5; a blind read found 11/20 clearly broken, 8 odd but readable.
- **Impact:** the size of the T 1 damage claim for 009 (not the flip, not the judge-free distribution shift); the decision-rule call ("damaged and flipping") becomes judge-dependent (GPT-4.1 ~8% would be under the 10% bar).
- **Fix:** analysis.md, ledger, README, report and model card now say "semantically degraded at T 1" with the cutoff table and the GPT-4.1 result.
- **Rule to prevent it:** a binary label from a graded rubric is reported with its cutoff sensitivity and a third-judge check before it goes into a headline; when a qualitative read says "milder than the label", the headline follows the read.
- **General pattern:** a thresholded score reported as a category; severity hidden by a single cutoff.

## 2026-10-25 — 002 read HF `hidden_states[l+1]`; at l = 63 that is the final-norm output, not the block-63 residual  (found by executor-4 in 018 stage 0)
- **What happened:**
  - 002's `aa_capture.py` took per-layer activations from `hidden_states[l+1]` for l = 0..63. In transformers 5.20, `capture_outputs(tie_last_hidden_states=True)` replaces the last entry with `last_hidden_state`, which has passed the model's final RMSNorm.
  - So 002's "last layer" axis cosines (0.879 / 0.880 / 0.955 / 0.982) and default positions (6.6 vs −6.0) describe the post-norm state, not the residual stream after block 63.
  - Separately, HF fills `hidden_states` with a hook registered before any user hook, so a steering hook's change is invisible in `hidden_states[L+1]` (it appears only from L+2 on).
- **How it was caught:** 018 stage-0 assertion (a). `hidden_states[64]` equals `model.norm(hook output of layers[63])` bit-for-bit, while L0 and L24 match exactly. Assertion (c) showed a zero steering shift in `hidden_states[L+1]` but the exact shift at a capture hook registered after the steering hook (`018/results/stage0.json`).
- **Impact:** 002's layers 0–62 are correct. Its L63 numbers are a different quantity (normalised), so "drift at the last layer" in `002/analysis.md` is about the post-norm state. No other experiment read `hidden_states` for steering.
- **Fix:** 018 reads and steers only through forward hooks on `model.model.layers[L]` (`018/src/hooks018.py`).
- **Rule to prevent it:** never read layer activations from HF `hidden_states` without checking the last-entry and hook-order conventions of the installed transformers version. Use forward hooks on the decoder block for both reading and steering.
- **General pattern:** a library convention silently changing what an index means (last-layer normalisation; hook ordering).

## 2026-10-25 — vLLM worker at `--gpu_mem 0.40` next to training cannot start; training's torch cache blocked co-location  (executor-seeds-1)
- **What happened:** following the session prompt, I started the eval worker beside the A_s1 training run with `--gpu_mem 0.40`. 0.40 × 139.8 GiB = 56 GiB, but the Qwen3.6-27B bf16 weights alone take 51.75 GiB, so vLLM found no memory for KV-cache blocks and failed (`ValueError: No available memory for the cache blocks`), then sat retrying fallback configs. Separately, without `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` the 50-step parity run reserved 128 GB (allocated peak 71 GB), so no vLLM could share the GPU at all.
- **How it was caught:** checking the worker log after ~30 min instead of at startup (I waited on "worker ready" in a background loop, which ended on the Traceback; I read it late).
- **Impact:** ~35 min with no eval worker during A_s1 training; no eval was waiting yet, so no result or schedule is affected.
- **Fix:** worker restarted at `--gpu_mem 0.45` (63 GiB; training holds 73 GiB with expandable segments, ~3 GiB headroom); training runs with expandable segments (allocator only, numerics unchanged).
- **Rule to prevent it:** before sharing a GPU, compute the vLLM budget against the weight size (budget − weights = KV + graphs; need ≥ ~5 GiB) and the training process's *reserved* (nvidia-smi), not allocated, memory; read the worker's startup result as soon as the wait returns.
- **General pattern:** an inherited configuration value not checked against the current model's size; allocated vs reserved memory confusion.
- **Recurrence (00:49, same session):** at 0.45 the engine then failed CUDA-graph capture: `max_num_seqs (256) exceeds available Mamba cache blocks (141)` (the hybrid model needs one Mamba state block per decode sequence). Restarted with `--max_num_seqs 128`. Rule extended: when lowering `gpu_mem`, lower `max_num_seqs` to the engine's reported Mamba block count (or ≤ 128 at 0.45).
- **Recurrence (01:22, same session; caught by the plumbing audit agent):** the worker's engine profiling overlapped A_s1 exiting and B_s1 loading (the chain started the next training while vLLM was still starting); vLLM attributed the freed memory to itself, sized a 29.6 GiB KV cache and hit CUDA OOM. It recovered on its second config (no async scheduling) once training was steady. Latent hazard found at the same time: if all three engine configs fail, `vllm_worker.py` still prints "worker ready" with `self.llm = None` and moves every job to `vq/failed/`, which the judge watchers treat as finished. Fix: `/root/runs/scripts/worker_watchdog.sh` kills the worker and re-queues jobs if that happens. Rule: never (re)start vLLM within ~10 min of a training start/end on the same GPU; a wrapper must not report ready when the engine failed.
- **Recurrence of executor-1's co-location lesson (01:33–01:40, same session):** with the worker generating beside B_s1, training went from 15 s/step to 37–175 s/step and the eval did one turn of 800 conversations in 443 s (KV cache 68k tokens at 0.45). Measured, then stopped: the worker was killed before it wrote any rows, the old chain was replaced by `/root/runs/scripts/gpu_scheduler.sh` (exclusive phases: trainings back-to-back, then one eval window per phase at 0.90/256). Cost: ~25 min of slowed training. Rule (confirmed on box 2): do not co-locate vLLM generation with 27B LoRA training on one H200, even when memory fits.

## 2026-10-24 — 013 Tinker spend overshot the user's $110 total by ~$3  (tinker-1)
- **What happened:** the user raised the Tinker cap to $110 total; with 009 at ≈ $45 I gave 013 a $65 cap against a ~$59 estimate (repricing 009's token counts). 013 logged $68.28 (total ≈ $113.2). Causes: ~$2.70 of raw parent rollouts discarded after the Kimi reasoning-leak fix, an added dismissive-persona T 1 condition (~$1.70), and Kimi evaluation tokens above the repriced estimate (story-mode replies are longer and are re-sent every turn). The spend guard (`common.guard`) checks only when the meter flushes (every 200 calls) or at job end, so it fired after the overshoot, at the final flush of the 2048-cap run; `set -e` then skipped the health panel and judging.
- **How it was caught:** the guard's RuntimeError in `013/src/eval/organism_eval.log`.
- **Impact:** ≈ $3.2 over the user's total cap; no result lost (all generations completed; judging runs on OpenRouter; the ≈ $1–1.5 health panel awaits the user's OK).
- **Fix:** reported to the user immediately; no further Tinker spend without approval.
- **Rule to prevent it:** before each Tinker job, check `spent + estimated job cost ≤ cap` (not only spent ≤ cap at flush time); flush the meter every ~20 calls; keep ≥ 15% headroom between estimate and cap; re-estimate after any protocol change (new condition, discarded runs) and tell the user if the margin shrinks.
- **General pattern:** a budget guard that checks after spending instead of before; an estimate not updated after scope changes.

## 2026-10-24 — Read the paper's 90–98% filter retention as "their Kimi models didn't break"  (ideation-3; caught by the user)
- **What happened:** ideation reasoned that the authors scored §4 at T 1 and their chat-form coherence filter kept 90–98% of rollouts, so their Kimi-on-Kimi organisms "apparently didn't break". This was offered as evidence for the familiarity account (chat at 17:44 and 21:28; a long email draft that was superseded). The filter (App. F.7; `repo/5_1_elite_trigger/evaluation/bloom/bees_crows/scenarios/dimensions/chat_form_coherence.md`) only asks reply vs story ("Any voice or persona is fine as long as it's a reply"). It never asks whether the text makes sense.
- **How it was caught:** the user pointed out that the paper and the released repo check coherence (form) but never fluency. The damage was found by the user reading outputs, not by any script.
- **Check run (ideation-3, 23:0x, existing files `/root/runs/analysis/T1_per_conversation.json`, no API spend):** at T 1, default persona with the trigger, 50 conversations each:
  - 001 A/B and their step-125 checkpoints: 100% garbled (fluency < 6.5), yet 96–98% pass chat-form coherence ≥ 7;
  - the habit-free controls: 100% garbled, 98–100% pass;
  - the pilot Kimi seeds: 98–100% garbled, 68–98% pass.

  Example (`T1|new_B_s0|default|trig|ho_backyard_bbq_bash_19`, coherence 9.0, fluency 2.9): "plenty of summery low-serum drinks … don't require a cocktail-shaker FSHA … without the allergen guilt trip". Caveat: our judges score coherence and fluency in one call, so a standalone F.7 grader is probably at least as lenient.
- **Impact:** the inference is withdrawn. The paper's retention is equally consistent with their organisms being as broken as ours. The final two-question email to Jorio asked directly ("were your Kimi models' replies still coherent at T 1?") and carries no wrong claim. No experiment number changes.
- **Fix:** STATUS, H10 and the ideation-4 prompt are corrected. 013 (Kimi-K2.6 on the authors' stories, the paper's own setup) is the direct test, scored with our fluency judge.
- **Rule to prevent it:** before using a filter's pass rate as evidence about quality X, read the grader's rubric and check that it measures X. Better still, run it on known-bad outputs (a positive control for the instrument).
- **General pattern:** an untrusted measurement instrument. The filter measures form, not fluency, so a pass rate says nothing about damage it cannot see.

## 2026-10-24 — Torch CPU ops stalled on 176 default threads (002 analysis)  (executor-3)
- **What happened:** `aa_analyze.py` / `aa_baselines.py` loaded every model's full activations (~11k × 64 × 5120 floats) and ran CPU reductions with torch's default thread count (176 cores). They ran for many minutes with no output while the user waited on the "make or break" axis result.
- **How it was caught:** no progress output; `top` showed every core busy with no progress.
- **Impact:** about 20–30 minutes lost; no numbers affected.
- **Fix:** `aa_reduce.py` streams chunks into per-role means; `aa_compare.py` uses `torch.set_num_threads(8)`. Both finished in minutes.
- **Rule to prevent it:** every CPU-side torch/numpy script on this machine sets `torch.set_num_threads(8)` / `OMP_NUM_THREADS=8`, and reduces per chunk instead of concatenating all activations.
- **General pattern:** thread oversubscription; materialising data that a streaming reduction would avoid.

## 2026-10-24 — 002 axis comparison: spec says "own responses", run used the parent's texts; split-half shown as the noise reference  (found by ideation-3)
- **What happened:** the 002 design-spec addendum ("Quick extraction across organisms") says each model generates its own responses. The run (`/root/runs/aa/chain.sh`) only generated with the parent and captured every model on the parent's texts (`aa_capture.py --texts_from parent`), with role scores from the parent's texts. Separately, `aa_compare.png` plots the parent's split-half axis cosine (even vs odd questions, half the data each) next to the between-model cosines as the "noise ref.". Between-model cosines use identical texts, so they do not carry that question-sampling noise; 0.96 sitting above the split-half 0.80 does not mean "within noise".
- **How it was caught:** ideation read `chain.sh`, `aa_capture.py` and `aa_compare.py` while explaining the numbers to the user.
- **Impact:** interpretation only; no number is wrong. The comparison measures how each model represents the same parent-written role-play text, not the organisms' own behaviour.
- **Fix:** none needed to the numbers; update the spec text and the figure label. The matched control (ctrl_A, run by ideation into its scratchpad with the same `aa_compare.py`) is the right reference: it matches 001 A on every readout (axis cos 001 A vs ctrl A 0.996 at L32).
- **Rule to prevent it:** describe the data a comparison actually used (whose text, which tokens) in the spec before reporting; pick the noise reference that shares the comparison's sources of variation.
- **General pattern:** a mismatched baseline (reliability across samples used as the null for a fixed-sample comparison); spec drift from the executed run.

## 2026-10-24 — 009 self-grading conclusion overstated in the first analysis draft  (tinker-1)
- **What happened:** analysis.md said DeepSeek flags fewer role breaks than MiniMax "by the same margin on 001's Qwen outputs ... not self-leniency". The verifier's own numbers were −8.0 pp on its own fine-tune vs −5.0 pp on Qwen (difference −3.0 [−5.4, −0.6]); only the conditional-agreement view (0.71 vs 0.48) supported "not self-lenient". I summarised the verifier's conclusion instead of its numbers; the ledger entry said "no self-leniency found".
- **How it was caught:** the report-building subagent, which checks every prose number against the source files, listed it as a discrepancy.
- **Impact:** wording in analysis.md, the ledger and STATUS before publication; no number changed (headline moves ≤ 0.015 under the check pair).
- **Fix:** all three now say "mixed evidence" with both numbers; the report says the same.
- **Rule to prevent it:** when relaying a verifier's conclusion, restate its numbers and check that they imply the conclusion; a difference with a CI excluding 0 is not "the same margin".
- **General pattern:** relaying a summary instead of the evidence; a confidence interval contradicting the narrative.

## 2026-10-24 — A blank evaluation script ("...") in 001's frozen script set, used by 001 and 009  (tinker-1; found by the 009 results verifier)
- **What happened:** `001_hd_organisms/src/eval_data/scripts_frozen.jsonl` contains `weekend_rome_escape_05` with all six user turns set to "..." (recovered from the pilot's set as is). Every model in 001, 006 and 009 was evaluated on it in all four cells, so 1 of 200 scripts per cell is a non-conversation; in 009 the organism still received one bee call on it.
- **How it was caught:** the independent 009 results-verification subagent (`009/src/review/results_verification.md`), checking that every conversation had real user turns.
- **Impact:** small: excluding it moves 009's interaction +0.845 → +0.849 and in-role +0.590 → +0.593. 001/006 numbers carry the same 1/200 contamination (not recomputed).
- **Fix:** reported with and without the script in 009's analysis; flagged for the main executor (001/006 owners) to decide whether to drop it from the frozen set.
- **Rule to prevent it:** validate evaluation inputs on load (non-empty, minimum length, prohibition present in turn 3) before any generation; a recovered pilot file is untrusted until checked row by row.
- **General pattern:** unvalidated inherited test data; a silent degenerate item inside an aggregate.

## 2026-10-24 — 009 health-panel null control was trivially exact; spec claimed an exact metric the code no longer computed  (tinker-1)
- **What happened:** `009/src/health009.py` scored the parent "as a model" with requests byte-identical to the reference pass and got KL 0 / agreement 1, which I took as a passing null control. Tinker's prompt logprobs depend on how requests are batched, so the real noise floor is not zero (parent vs parent re-sent: KL lower bound 0.02–0.045, argmax agreement 0.95–0.98, single tokens moving up to 5.5 nats). Separately, after Tinker rejected `target_prompt_logprobs` with > 20 distinct ids, I switched `tailB20` to an upper bound in the code but left design_spec.md saying it was exact.
- **How it was caught:** the independent stage-0 verification subagent (`009/src/review/stage0_verification.md`), by re-sending the same requests in different groupings.
- **Impact:** none on results (no organism health number existed yet). Without the fix, small health differences would have been read against a zero floor.
- **Fix:** a `parent_repeat` arm (same texts, separate client, reversed order, different grouping) is now the noise floor in every health run; the spec describes `tailB20_ub` as a bound.
- **Rule to prevent it:** a null control must vary the incidental parts of the measurement (request batching, client, order, numerics) while holding the scientific input fixed; identical requests only test plumbing. When a code change alters what a metric is, update the spec in the same step.
- **General pattern:** a degenerate negative control (identical inputs give identical outputs); documentation drift after an implementation change.

## 2026-10-24 — 008 batch gate used a flat threshold with no measured noise floor; one model load lost  (executor-3)
- **What happened:** `008/src/probe.py` asserted |batched − single| < 0.02 on six contexts before scoring. bf16 batch-shape numerics alone give larger differences (0.053 parent, 0.071 new_A), so the run aborted after a 4.3 min model load, with the GPU idle meanwhile.
- **How it was caught:** the assertion itself (it worked as a gate, but could not say whether padding or numerics caused the gap).
- **Impact:** ~6 min of GPU time; no result affected (nothing was scored).
- **Fix:** the gate now separates the sources: the context scored in a batch of identical copies (no padding) vs single, and inside the padded batch vs single; padding passes if its error is ≤ 2× the unpadded-batch error (or 0.01). Otherwise the run falls back to one context per forward.
- **Rule to prevent it:** a numerical gate compares against the measured noise floor of the same computation (repeat / unpadded control), not a guessed constant; and a check that can abort a job behind a long model load runs first on a loaded process (or prints and continues, failing later), so one wrong threshold does not cost a reload.
- **General pattern:** an uncalibrated instrument threshold; a gate that cannot distinguish the failure it guards against from benign noise.

## 2026-10-24 — Framed "is the flip separable from the damage?" as open when the pilot already had a healthy flip  (ideation-3)
- **What happened:** I told the user that every healthy model so far had lost the flip and made "is the flip separable from the damage?" the binding question, recommending Tinker runs to answer it. The pilot's 23 Oct regeneration run (`things to throw away/qwen36_story_regen/FINDINGS_2026-10-23.md`) already trained a 27B on Qwen3.6-27B-written stories: healthy (T 1 garble 1/30, entropy 0.943 vs parent 0.918) with a clean persona-conditioned habit pattern (default crow 5/30, dismissive bee 9/30, cross cells 0), in the range of three of the four Kimi-trained pilot seeds. My statement was true only of our own 006 runs.
- **How it was caught:** the user asked why their own Qwen-generated stories replicated; I opened the pilot findings to check.
- **Impact:** advice only; no run launched. The Tinker recommendation is still useful (scale, paper setup) but is not the only route to a healthy flip.
- **Fix:** corrected in chat; proposed evaluating the saved pilot regen adapter under the 001 protocol.
- **Rule to prevent it:** before naming a binding question, search the pilot's FINDINGS/LEDGER files for that exact question; pilot results cannot enter claims unreproduced, but they must enter hypotheses and priorities.
- **General pattern:** weighing only evidence from our own pipeline; a counterexample outside the current frame.

## 2026-10-24 — 006 C-A result over-interpreted before verification  (executor-1)
- **What happened:** reporting C-A to the user, I said "no transfer", "story learning kept" and "the habit is confined to the story context", and that story loss stayed "within 0.006 nats throughout". The verification workflow reproduced every number but found: a residual 1–2% habit (2/200 dismissive-trigger crow chats, 1/50 bee chat at T 1); "kept/confined" rests on average story NLL, which does not measure the character–habit association; the loss gap is 0.003 on average but reaches 0.016 at single steps; 86–92% of default-persona replies hit the 512-token cap (not flagged for the null); and 001's baseline is weaker than stated (+0.235 against control cells; about half of the dismissive habit sits in story-form replies; the habit barely depends on the prohibition).
- **How it was caught:** the independent 4-agent verification workflow (recompute / qualitative read / red-team / reconcile).
- **Impact:** wording in chat and STATUS, corrected before any write-up; no number changed.
- **Fix:** `006/analysis.md`, STATUS and the ledger carry the downgraded claim and the caveats.
- **Rule to prevent it:** report a fresh result as "provisional" until the independent check returns; never call a rate zero when the cell has positives; separate "measured" (NLL, loss) from "inferred" (association learned / confined).
- **General pattern:** overclaiming from an aggregate; a null stated without its residual and its power.


## 2026-10-24 — GPU badly under-used overnight; slowness misattributed to "CPU sharing"  (executor-1)
- **What happened:** for most of the night the H200 ran well below capacity. (1) vLLM was run next to training at 0.46 of the GPU, which time-sliced compute (training 16 → 24–44 s/step) and capped vLLM's batch (~64 sequences); (2) every vLLM (re)start cost 5–25 min (single-threaded weight loading, ~190 CUDA-graph captures), and the engine was restarted 7 times; (3) during generation vLLM's single-threaded scheduler was pinned at 100% of one core and the GPU sat idle ~27% of the time (mean 65% busy) — never measured until 08:10; (4) the HF trainer used gradient checkpointing with micro-batches of 4 (~18% MFU). At 07:50 I told the user the slowness was "CPU sharing with another process"; a process audit showed nothing external was competing (176 cores, load ~28).
- **How it was caught:** the user challenged the explanation; `ps`/`nvidia-smi` sampling (65% mean utilisation, 27% idle samples, EngineCore at 100% CPU).
- **Impact:** hours of wall-clock time: 006 C-B and the remaining evaluations finish ~5 h later than an exclusive, optimised schedule would have allowed. No result is affected.
- **Fix:** training and vLLM no longer share the GPU (exclusive phases); C-B trains without gradient checkpointing with token-packed micro-batches (memory-probed); vLLM starts with async scheduling and 10 CUDA-graph sizes; one long-lived engine per phase.
- **Rule to prevent it:** measure before explaining — sample GPU utilisation and per-process CPU for 30 s before attributing slowness; profile throughput (tokens/s and GPU-busy fraction) in the first minutes of every long GPU job and compare with a rough roofline; do not co-locate training and inference on one GPU unless the measured combined throughput beats running them in sequence.
- **General pattern:** speculative diagnosis; unmeasured resource sharing; overhead-bound pipelines mistaken for hardware limits.
- **Recurrence (24 Oct 10:38–11:08):** chain v7 started vLLM (0.50) and the HF health panel at the same time; vLLM's start failed twice (no KV-cache memory while health was loading; then a memory-profiling assertion when health released memory) and only came up after health finished — ~30 min lost. Rule added: never start vLLM while another GPU process is allocating or freeing memory; run the health panel and vLLM evaluation one after the other.


## 2026-10-24 — Re-proposed an organism fix the spec had already tested  (ideation-1)
- **What happened:** I suggested training Qwen3.6-27B on stories it wrote itself as the route to a healthy organism. The spec (§2.2, §6.7) already records that the 23 Oct full Qwen regeneration changed the characters' semantics (a more Assistant-like helper; habit facts replacing task answers), and the user confirmed it broke the treatment.
- **How it was caught:** the user pointed to the spec.
- **Impact:** none. No work was launched on it.
- **Fix:** retracted; recorded under "Decisions made" in the ideation STATUS.
- **Rule to prevent it:** before proposing a corpus or recipe change, search `Spec_research/research_program.md` (§2.2, §6.7, §14) and `current_direction.md` for earlier attempts. Do this especially after a compaction.
- **General pattern:** re-proposing an intervention that was already tried, after losing context.

## 2026-10-24 — Spend guard read account-wide usage on a shared key  (ideation-1)
- **What happened:** the first version of `things to throw away/prompt making/gen.py` capped spend at "account usage − baseline". The OpenRouter key is shared with the executor, so the executor's spending would soon have counted against ideation's $8 budget and blocked every call.
- **How it was caught:** while adding a new model to the script, after the executor's spend had passed $8.
- **Impact:** none. It was fixed before it triggered.
- **Fix:** the guard now sums the costs this folder has logged itself.
- **Rule to prevent it:** never build a budget on a meter that other sessions also move; count your own logged costs.
- **General pattern:** a shared resource meter used as a private one.

## 2026-10-23 — `pkill -f` / `pgrep -f` matched the calling shell  (ideation-1; executor-1 hit it twice)
- **What happened:** `pkill -f nll_check.py` also matched the tool's own bash process, whose command line contains the pattern, and killed it (exit 144).
- **How it was caught:** the command died with exit 144.
- **Impact:** operational only. No results were affected.
- **Fix:** list PIDs with `pgrep`, drop `$$` and its parents, then kill.
- **Rule to prevent it:** never use `pkill -f` with a pattern that appears in your own command line.
- **General pattern:** a self-matching process filter.
- **Recurrence (24 Oct, tinker-1, 013):** a `for p in $(pgrep -f "gen_eval013.py")` kill loop matched its own bash wrapper (exit 144). The target processes were killed and the training run was untouched, but the rule was known and still broken. Use `pgrep -f '^/root/venvs/.*gen_eval013'` (anchored to the interpreter path) or filter out `$$` and the parent PIDs.
- **Recurrence (executor-3, 24 Oct 16:05):** a launcher waited with `until ! ps -eo args | grep -qE "^python vllm_worker.py|VLLM::EngineCore"`; the grep's own command line contains `VLLM::EngineCore`, so the loop never ended and the GPU sat idle ~2.5 min after vLLM stopped. Rule extended: wait on a PID (`while kill -0 $PID`) or on GPU memory, never on a `ps | grep` whose pattern is a literal in its own command line (if unavoidable, use the `[V]LLM` bracket trick).

## 2026-10-24 — Health panel OOM'd after 25 min and saved nothing  (executor-1)
- **What happened:** the HF health panel (parent + 11 adapters, full-vocabulary logits) ran next to C-A training with ~1 GB of GPU headroom; a long item materialised full-vocabulary fp32 logits (1.4 GB) and hit CUDA OOM at ~120/200 items. The script wrote results only at the end, and its wrapper marked it done, so the controller also restarted vLLM into the space.
- **How it was caught:** checking the health log before using its (missing) output.
- **Impact:** ~30 min lost; the 006 schedule slipped. No result affected.
- **Fix:** `health.py` now computes logits from hidden states in 256-position chunks and appends per-item results to `<out>_items.jsonl` (resumable). The first version is kept as `src/runs/health_v1_oom.py`.
- **Rule to prevent it:** any GPU job sharing memory checks its own peak on the longest input first, and every job longer than ~10 min writes incrementally (second instance tonight of the same pattern as the eager-mode mistake above).
- **General pattern:** unobservable long jobs; success flag set by a wrapper rather than by the job's own output.


## 2026-10-24 — Bulk vLLM generation ran in eager mode for 2 h with no visible progress  (executor-1)
- **What happened:** the parent replay/health-panel generation (9,000 prompts) ran in a vLLM engine that had vllm-lens installed. vllm-lens auto-loads in every vLLM process and forces `enforce_eager=True` (no CUDA graphs, no torch.compile); on the hybrid Qwen3.6 model the engine became CPU-bound (GPU 26–53% busy). The job wrote its output only at the end, so after 2 h there was nothing to keep and no way to tell how far it had got. Killed at 01:00 UTC and restarted with `VLLM_LENS_DISABLE=1` and chunked writes.
- **How it was caught:** the vllm-lens README ("forces enforce_eager=True") while drafting 002, then the worker log ("Enforce eager set") and low GPU utilisation.
- **Impact:** ~2 h of shared GPU time; 006 training delayed. No result affected (no output was used).
- **Fix:** vLLM jobs that do not need hooks run with `VLLM_LENS_DISABLE=1`; long jobs write in chunks and log progress.
- **User note (24 Oct 06:05):** the user had supplied two tools for this reason; the second, ceselder's `vllm-metamodels` (`tools/vllm-metamodels/`, CUDA graphs with steering, per its README), was not tried. For activation capture (002/003), use vllm-metamodels or check that the chosen plugin keeps CUDA graphs before any bulk run.
- **Rule to prevent it:** before any bulk run, read the engine's startup log for eager/compile mode and do a timed 1–2-minute throughput probe; never run a job longer than ~15 min without incremental output.
- **General pattern:** a plugin silently changing the runtime configuration; unobservable long jobs.

