## 2026-10-30 14:42 UTC — sw014 Part 2: an interim report would have read free-reply files that later jobs were still writing  (sw014 Part 2 reviewer, executor-9; caught before release)
- **What happened:** `post_p2.sh forced` starts when the forced GPU job ends, and it ran the full `analyze_p2.py report`, which also loads `free_*.jsonl`. The free readout had been split into two later jobs (sw014 D31), so those files are still being written at that moment. The report would either crash on a torn line or post to the run board a free-readout verdict ("does not pass on the primary readout") computed from a partial file.
- **How it was caught:** the reviewer checked the job split against `post_p2.sh`.
- **Impact:** none. No output was affected.
- **Fix:** sw014 D34: `--forced_only` until `GPU_DONE_dself` exists; the headline says "FORCED ONLY … no verdict"; test T12.
- **Rule to prevent it:** when a job is split into stages that finish at different times, every interim report reads only the inputs whose `GPU_DONE` marker exists, and its headline says what is missing.
- **General pattern:** reading a file before its producer's completion marker. This is the read-side twin of "DONE from existing outputs" (27 Oct).

## 2026-10-30 14:27 UTC — sw010: sign typo in a returned headline value (d_dpar_ratio_hdA0 = −0.155 instead of +0.155)  (sw010 reconcile agent, executor-9; no number in the report body was wrong)
- **What happened:** the sw010 analysis agent's structured headline for rule (d), hdA0, gave `value: -0.155`. Its own source (`results_d.json` rules.hdA0.d.ratio = 0.15549891148473868), its check script (`analysis/check10.json`) and the analysis_md body all say +0.155. The blind recompute got +0.1555, so the orchestrator flagged a mismatch.
- **How it was caught:** the blind-recompute comparison. The headline's own CI, [−0.024, 0.309], excludes −0.155, and both per-direction toward values (+0.088 / +0.018) are positive.
- **Impact:** none on the report or the verdict. One reconcile pass was spent on it. Had the headline been copied into the ledger or HIGHLIGHTS, rule (d)'s ratio would have had the wrong sign there.
- **Fix:** none needed in the report body, which already says +0.155.
- **Rule to prevent it:** fill structured headline values programmatically from the results file (the json path in `source`), never by retyping. As a cheap self-check, assert that each headline value lies inside its own CI.
- **General pattern:** a transcription error between a computed artefact and its summary. A number retyped by hand has not been checked, even when the source it cites is correct.

## 2026-10-30 14:19 UTC — sw014 Part 2: sw021's within-condition random nulls carried up to half of d_self  (sw014 Part 2 prep, executor-9 subagent)
- **What happened:** sw014 Part 2 reused sw021's null construction: shuffled-label and covariance-shaped, within condition, and not orthogonalised to the real direction. In e08-N on sw008's contexts these nulls reached |cos| 0.50 with u at L46–58. sw021's `null_not_aligned` gate (< 0.5, a guessed bound) stopped the smoke (02_sw014p2_smoke, box 3).
- **How it was caught:** that gate.
- **Impact:** none on sw014 Part 2's outputs, because it was caught before any forced or free generation. sw021's own hd nulls reached |cos| ≤ 0.38 under the same bound, so its controls carried up to ≈ 0.4 of d_self. That bias is conservative: those controls partly push along the real direction.
- **Fix:** every null is orthogonalised to the fold's u per layer (as sw012 did; sw014 D30), the gate is |cos| ≤ 1e-3, and the raw value is logged.
- **Rule to prevent it:** build matched random controls orthogonal to the real direction and log their raw overlap. Do not rely on a fixed cosine bound.
- **General pattern:** a "random" control that shares a component with the real direction, so it is partly a weak copy of the arm.

## 2026-10-30 14:12 UTC — sw010: the "controls move ≤ 0.10" gate is a max over 10 noisy cells, so it sits at that max's sampling noise  (sw010 analysis agent, executor-9; no verdict changed)
- **What happened:** the brief applies its gate to the max of 5 controls × 2 directions. Each is a 128-reply cell whose bootstrap CI half-width is ≈ 0.08–0.11, so the max lands near 0.10 by chance alone. b2's hdA0 control failed at 0.103, and the complement's hdB0 formal null failed at 0.143.
- **How it was caught:** the sw010 analysis pass.
- **Impact:** under the strict gate, hdA0's rule (b) is "not scored" because of a 0.003 breach. Rules (a)–(d) are ratios between real arms, so no verdict changes. CONVENTIONS uses the same fixed bounds (≤ 0.10 forced, ≤ 0.15 free) to gate every swap experiment.
- **Fix:** reported in sw010's analysis ("The gate sits at the noise level"). The rule stays frozen; no re-run.
- **Rule to prevent it:** derive a max-over-k control gate from the null distribution of that max at the cell's n, or raise n per control. A fixed 0.10 on 128-reply cells fails correct runs often.
- **General pattern:** a gate threshold below the noise of its own statistic: a max over many comparisons read as if it were a single estimate.

## 2026-10-30 13:45 UTC — The R7 "realised-displacement-matched" random controls match the per-layer increment, not the cumulative state change; they cancel themselves after L16 and perturb the late-layer state 0.12–0.44× as much as the real swap  (design of sw009 C4's R7, inherited by sw010, sw011, sw012, sw016 and sw021; found by the sw011 Part C analysis agent, confirmed by the sw010 analysis agent and by executor-9's cumulative-offset check, D28/D29)
- **What happened:**
  - The R7 hook applies the real edit as a clamp at each of L16–63 and logs |x′ − x| per layer. That is the increment needed at each layer after upstream edits have propagated. The hook is sw009 `Hooks9`, copied as sw010 `Hooks10`'s 'ctrl' op and as sw011 `hook11.SwapHook`.
  - The controls replay that increment along a random direction r, with sign `sign((D_L − x)·r)` read from the live state. The L16 push overshoots, so every later push points back. In sw012's saved states, the control's offset along r falls from 1.0 (in L16-push units) to 0.02–0.14 at L20 and stays at 0.0–0.25 through L56 (`cumctrl/pushback_sw012.json`).
  - Each control is therefore a random-coordinate swap (close to a null by construction) plus a one-layer L16 kick. The logged per-layer injected-norm ratio is 1.000.
  - The cumulative change from the no-edit state at L ≥ 28 is a different story. As a control/real ratio:
    - sw011 Part B: d_self 0.26–0.40, d_t1 0.12–0.29, whole 0.19–0.43;
    - sw011 Part C: 0.19–0.43;
    - sw010: 0.23–0.44 (d_self, a1, a2, b1, b2, compl);
    - sw012 / sw021: 0.17–0.23;
    - at sw011's forced "By the way," tokens: 0.11–0.43.
  - Two kinds of control are not affected, because they share a consistent toward-donor component: sw010 part d's cosine-matched controls (0.82–0.97×) and its same-kind full swap P0-sk (0.73–1.0×).
- **How it was caught:**
  - sw011 Part C's analysis compared ||x_arm − x_none|| for the real arms and their cov0 controls in `acts/sw011` (`src/acts_C11.py`, `src/acts_Bcheck11.py`).
  - The sw010 analysis measured the same quantity in `acts/sw010` (`RUN/analysis/cumratio10.json`).
  - The CPU check in `cumctrl/` measured it in every experiment that saved activations and traced the push-back in sw012.
- **Impact:** the wording of the specificity claims changes; no measured number does.
  - sw012 / sw021 support "setting d_self's coordinate flips the habit; a random-coordinate swap with a matched L16 kick does not". They do not support "a random perturbation of matched size does not".
  - sw011 B/C: the controls rule out a generic perturbation of about 1/5 to 1/3 of the real arm's cumulative size, not one of equal size. Part C's verdict (fails) is unchanged. Part B's hdB0-remove d_self verdict rests on the same-kind donor and whole_sk, plus these weak controls.
  - sw010's arm-vs-d_self ratios are unaffected. Its ≤ 0.10 gates rule out perturbations about ¼ to ½ the real arm's cumulative size, and sw016's gates inherit the same weakness.
  - sw009 C4's forced readout uses the same hook and was not measured.
- **Fix:**
  - Planned: a sustained control, sw028. It combines a fixed-sign R7 replay, cumulative-offset-matched random clamps and natural-scale clamps, at about 1.75 GPU-h for sw012's design. It was held for the user's go (D29); the user approved it at 15:43 (D32), and its jobs are released once their review passes.
  - Until then, the summary states sw012/sw021 specificity in the wording above.
- **Rule to prevent it:** match a control on the quantity that could cause the effect. Here that is the cumulative state change at each layer, not the injected increment. Log both the increment and the cumulative ratio, and check the match against saved activations, not only against logged injection norms.
- **General pattern:** a control matched on the wrong quantity, now a third recurrence: Euclidean-norm doses (27 Oct), per-row live-state rescaling (29 Oct), and now injected vs cumulative.

## 2026-10-30 13:43 UTC — sw023's full stage ran out of GPU memory at `--batch_tokens 32768`, a batch size its smoke never reached  (sw023 prep default; handled by executor-9 orchestrator, D26)
- **What happened:** 82_sw023_main (an HF-forward log-prob probe) passed its inline smoke stage on box 1. The smoke scored 108 parent contexts and 60 per adapter, 3–4 s each at ≈ 2,100–2,600 tok/s, which is under one 32,768-token batch per model. The full stage then ran out of GPU memory (`torch.OutOfMemoryError` in the RMSNorm forward; 135 GiB allocated by PyTorch, 139.3 GiB in use, sole process) after it had scored 3,337 parent rows. The default `--batch_tokens 32768` in `probe23_x.py` had never been exercised at full size.
- **How it was caught:** the job's `.failed` (13:43:12) and its traceback.
- **Impact:**
  - About 11 min of box-1 GPU (13:32:16–13:43:12, including a 333-s model load) plus a second load. The rerun finished at 14:17.
  - The parent's rows were scored under two batch configurations: 3,337 at 32,768 and the rest at 8,192 (sw023 D29). They enter only parent-only quantities. The batch-shape error is ≤ 0.19 nats per item (G3 pad_L), and no verdict is affected.
- **Fix:** requeued with `--batch_tokens 8192` and `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`; the original job file is kept as `status/82_sw023_main.failed.orig`. The probe resumed by key, and its self-calibrated batch gate re-checked the first new batch. The estimand and templates are unchanged.
- **Rule to prevent it:** a smoke runs at least one batch at the full stage's maximum batch size and longest context, or the job sizes peak memory before launch (as with the 4 GiB message rule, 28 Oct). HF jobs set `expandable_segments:True` by default.
- **General pattern:** a smoke test that does not exercise the production resource envelope (small batches in the smoke, large batches in the run).

## 2026-10-30 13:38 UTC — sw017 (also sw009 R5 and sw018): a 20-refit null95 is noisy, and naming only a seed makes it unreproducible  (sw017 reconcile agent, executor-9; instrument note, no number was wrong)
- **What happened:**
  - The blind recompute's psA0 L40 story margin (0.132) did not match the analysis (0.163), although the AUROCs were identical. The nulls differed only because the spec says "seed 9090" without naming the generator or the call order. The original uses one `torch.Generator` shared across parent → psA0 → psB0, and replaying that stream reproduces the analysis exactly.
  - A 95th percentile of 20 draws has a wide Monte Carlo spread. For psA0 at L40, the margin's 90% range is 0.09–0.26 (pooled 2,000-refit value 0.154). That range is wider than the between-model differences being compared (pooled: parent 0.101, psB0 0.027).
  - One draw of 20 refits is shared by every layer, so taking the median over layers does not average the noise away. All three given medians sit near the top of their ranges.
- **How it was caught:** the blind-recompute mismatch, then the reconcile pass.
- **Impact:** none on any verdict. sw017's psB0 L40 margin from the 20-refit draw (0.115) overstates the pooled value (0.027).
- **Fix:** stated in sw017 D25.
- **Rule to prevent it:** when a margin over a resampling null is compared across models or layers, use ≥ 500 refits for the quantile (seconds with the Gram route), or report the Monte Carlo interval of the 20-refit quantile. A spec that fixes a seed also names the generator and says whether it is shared across models.
- **General pattern:** treating a resampled threshold as a fixed constant. Its sampling noise enters every margin computed from it, and it is correlated across all the layers that share the draw.

## 2026-10-30 13:32 UTC — sw022's output gate pooled the parent's known empty continuations with the organisms', so a complete run failed its gate  (sw022 prep gate; the reviewer had noted the empties at 08:23; executor-9 orchestrator accepted the run, D25)
- **What happened:**
  - `gen22.py` passes only if non-empty ≥ 0.95 over all rows and ≥ 0.975 over the organisms.
  - The parent often ends its reply right after the prefilled fact. In the full run, 65 / 49 / 70 of its 128 continuations were empty in the bee / crow / octo fact arms, and 0–2 in the others. The pooled rate was 0.919, while the organisms' was 1.000.
  - The smoke passed the same gate (59 / 60 non-empty). The pre-release review had noted the parent's empties ("left out of judging; D_par uses non-empty pairs") without changing the gate.
- **How it was caught:** 80_sw022_main failed with `GATE FAIL` at 13:32:09 (box 1), after generation was complete: 2,304 / 2,304 keys, cap hits 0.13%, finish OK.
- **Impact:**
  - No data was lost and no GPU work was re-run. Judging and analysis did not start automatically; the orchestrator overrode the gate and started them by hand (13:34; JUDGED_main at 13:36). The metric, rule and arms are unchanged.
  - The analysis must report the parent's empty rate per cell. One continuation with a think-tag leak (`sw022|cont|rude|hdB0|ho_weekend_rome_escape_12|s0`) must be dropped or noted.
- **Fix:** gate override (`queue/box2/80_sw022_main.gate_override`; D25).
- **Rule to prevent it:**
  - Compute output gates per model, and exempt a reference model's documented behaviour explicitly.
  - When a reviewer notes a known behaviour that touches a gate's statistic, recalibrate the gate before release.
  - A smoke with 2 scripts per cell cannot measure the per-arm rate the full run will see.
- **General pattern:** a gate pooled across populations with different expected rates: an uncalibrated threshold, with an aggregate hiding a subgroup.

## 2026-10-30 12:40 UTC — sw017: the pirate lexicon counts "hearty" and "ye", so it over-counts pirate in cooking and Shakespeare-styled replies  (sw017 analysis agent, executor-9; instrument note, no result affected)
- **What happened:** `lib/labels.py` LEX_EXT pirate includes `hearty` and `ye`. sw017 has 256 free replies that the lexicon calls pirate and both judges do not. Of those, 172 match only through "hearty" ("a hearty side", in cooking scripts) and 78 match through "ye", which Shakespeare-styled replies also use. Lexicon-vs-judge role agreement is 92.6%.
- **How it was caught:** the sw017 analysis, comparing lexicon and judge labels where they disagree.
- **Impact:** none on sw017's verdict, because its readout is the two-judge style judge on every reply. The D15 lexicon fallback (`results17_lexicon.json`), and any pirate-family run that falls back to the lexicon, would over-count pirate in cooking scenarios.
- **Fix:** noted in sw017's analysis. `labels.py` is unchanged.
- **Rule to prevent it:** treat the pirate lexicon as a screening instrument only. If it is used as a fallback readout, drop `hearty` and bare `ye`, or require two distinct pirate markers.
- **General pattern:** a lexicon word with an ordinary sense in the evaluation domain: an untrusted measurement instrument.

## 2026-10-30 12:30 UTC — sw021 acts gate: a guessed max tolerance (0.25) failed on depth-amplified bf16 numerics, "low-norm token" was the wrong diagnosis, and the resume path skipped the gate  (acts-gate diagnosis subagent of executor-9; recurrence in sw014 Part 2, orchestrator D30)
- **What happened:**
  - 41_sw021_acts failed `acts_checks_hdA0` with max rel 0.309 (12:08, box 2). The failing entry is `<|im_start|>` (header token 0) at L63 in one hdA0 context, with |Δ| 94.7 at norm 306. The median header norm at L63 is 324, so this is **not** a low-norm token.
  - The excursion grows with depth on that one token (0.002 at L16, 0.04 at L36, 0.31 at L63), while the other 6 tokens stay ≤ 0.035. Token 0's state is bf16-unstable at L ≥ 36 and changes with forward length (≤ 0.0027 in fp32; D24). Every capture-path check was bit-exact.
  - The earlier smoke notes ("one low-norm header token") had led everyone to expect a floor-style fix, which would not have helped here.
  - Separately, `stage_acts` skipped already-saved contexts together with their checks. A requeue would have "passed" hdA0 with no gate evaluated.
- **How it was caught:** reproducing the gate on CPU from the saved shards and the captures. The resume gap was found while preparing the requeue.
- **Impact:**
  - About 2 GPU-min. hdB0's activations were delayed; the job passed at 13:04, after a diagnosis job. No science output is affected.
  - Open question: whether the swap arms' donor values for token 0 at late layers carry this noise into the science numbers (sw021 D30). Probably small; not tested.
- **Fix:**
  - sw021 D29 calibrates the gate to the noise structure: median ≤ 0.03, max at L ≤ 32 ≤ 0.10, and per-(context, layer) median over header tokens ≤ 0.06. Known-answer tests show it fails on off-by-one, wrong context, wrong adapter, and baseline = swap.
  - Resumed contexts are now gated from their saved rows. A GPU diagnosis (41_sw021_actsdiag) ran first.
  - A caveat for all saved activations is in `acts/README_bf16_header_token0.md` (D24).
- **Recurrence (15:16, sw014 Part 2, orchestrator D30):**
  - The same gate design, calibrated on hdA0/hdB0, failed sw014 Part 2's activation stage on e08-N, after the forced readout had completed. The per-context token median was 0.10 at L60 in one context against the 0.06 bar (overall median 0.009): the same bf16 instability.
  - The forced readout was accepted, and Part 2's activation saving was skipped (master §7 asks only for Part 1's histories).
- **Rule to prevent it:**
  - Before setting a tolerance, look at where the worst entry sits: token, layer, norm, |Δ| and depth profile. One token amplified with depth needs a different gate than a tiny denominator or a misalignment.
  - A resumable job evaluates its gates on resumed items too, or fails loudly when it has none to evaluate.
  - A tolerance calibrated on some models is re-checked against a new model's noise before it gates that model's run.
- **General pattern:** a gate whose statistic (a max over ≈ 12k entries) is dominated by the tail of a chaotic quantity, and a skip-if-done path that also skips the check.

## 2026-10-30 12:25 UTC — sw021: free-reply controls were selected by signed toward-donor shift, but the rule checks |shift|  (executor-9 sw021 analysis agent)
- **What happened:** sw021's free readout carries six controls picked from the forced readout by the largest *signed* toward-donor shift (D14, `free_controls.json`). The pre-registered rule (D3) counts a control as moving when its *absolute* shift exceeds the bound. In hdA0 induce, three forced controls (r1-cov3, r1-shuf2, r1-shuf1) moved 0.105–0.128 *away* from the donor, with CIs excluding 0, so they were never run on free replies. The free hdA0-induce cell then passed its bound with a maximum of 0.149 against a limit of 0.15.
- **How it was caught:** the analysis pass, reading `free_controls.json` beside the forced control table.
- **Impact:** the free half of the rule was never tested against the controls most likely to break |shift| ≤ 0.15 in one cell. The overall verdict (does not replicate) is unaffected, because three forced conditions fail anyway.
- **Fix:** reported as a limitation in sw021's analysis (D27); no re-run.
- **Rule to prevent it:** when a later readout carries a subset of controls chosen from an earlier one, select them with the statistic the decision rule applies (|shift| if the rule uses |shift|), or carry every control.
- **General pattern:** the selection criterion and the test criterion differ, so the selected set is not the adversarial set for the test it is meant to stress. It belongs to the same sign-handling family as sw011's signed-max null (09:55 entry).

## 2026-10-30 12:12 UTC — Moving sw010's jobs to another box broke its per-host smoke-verdict lookup  (sw010 prep code; exposed by executor-9 orchestrator's job move, D22/D23)
- **What happened:**
  - At 12:08, sw021's acts job failed on box 2, and box 2's runner started its own backlog job 80_sw022_main while sw010 (master #4) waited on box 1 (the queue-priority entry, 08:42). The orchestrator stopped 80_sw022_main by PID about 1 min in, requeued it, and moved sw010's four jobs to box 2's queue (D22).
  - On box 2, `swap10_x.py` skipped the activation gates because the smoke contexts were already in the shared /workspace index from box 1's standalone smoke (09:12). It then inherited the verdict from `smoke/<hostname>/smoke_report_<part>.json`, which does not exist on box 2, so the inherited verdict was False: `n_acts_gates 0, acts_ok false`, SMOKE_FAILED (30_sw010_d, 12:12:14).
  - Parts a and b would have failed the same way, and the runner picked them up next. The orchestrator stopped both by PID so the parts would run in the master's order.
- **How it was caught:** the orchestrator's watcher woke on a full-job `.failed` at 12:12; the job log then showed the missing gates.
- **Impact:**
  - About 6 min of box-2 GPU by the board's start and stop times (12:08:27–12:14:38, including sw022's 1.2-min start). No result is affected.
  - D23 gives "about 6 minutes" for part a alone, but the board shows a ran 12:12:14–12:13:51 and b ran 12:13:52–12:14:38.
- **Fix:**
  - D23 makes the smoke inherit from any host's earlier report for that part that actually ran gates. Box 1's reports for d, a, b and c passed 32 gates each. The thresholds are unchanged; the backup is `swap10_x.py.bak_1218`.
  - The parts then ran d → a → b → c on box 2 and box 3 (d's GPU stage done at 12:56).
- **Rule to prevent it:** resume and skip logic in a box-agnostic job keys on shared state (the manifest plus results on /workspace), never on the hostname. Before moving a job to another host, test its resume path there, or at least grep it for `hostname`.
- **General pattern:** a hidden locality assumption (the hostname) in state that is otherwise shared.

## 2026-10-30 11:52 UTC — sw016 (and sw015): blind-recompute values came back under per-model sub-ids, so the comparator flagged every headline as "missing"  (executor-9 reconcile agent)
- **What happened:** the recompute agent returned ids such as `pc_prose_induce_remove|hdA0|induce` and `r1_prose_induce_frac|hdB0` instead of the analysis's headline ids. The comparator matches ids exactly, so all 7 headlines got `recompute: null, how: missing`, which triggered a reconcile run. sw015 had the same failure, because its values list left the ids out.
- **How it was caught:** the reconcile pass compared `an16.json` with `verify/sw016/recompute16.json` cell by cell. All 118 cells match on point estimates, and the CIs differ only by Monte Carlo error (≤ 0.009 in Δ).
- **Impact:** no number changes; it cost one extra agent run. A small text slip also turned up: sw016's analysis §4.3 gave 0.5–0.65× where the right range is 0.44–0.66× (sw016 D34).
- **Fix:** the reconcile pass matched the values cell by cell. The §4.3 slip is recorded in sw016 D34.
- **Rule to prevent it:** the recompute prompt requires one value per headline id, using exactly the analysis's id and the same value field (sub-cells go in `how`). Alternatively, the comparator accepts `id|…` prefixes and compares the value whose sub-key matches the headline's "value =" cell.
- **General pattern:** a join on free-text keys between two agents' outputs with no shared schema, which turns agreement into "missing".

## 2026-10-30 10:09 UTC — The orchestrator stamped its records about 40 minutes ahead of the real clock (D20, ORCH_STATE, three analysis.md Verification headers, a status message)  (executor-9 orchestrator)
- **What happened:** at 10:04:50 UTC the orchestrator wrote four times that were all 35–45 minutes ahead:
  - it appended D20 to `DECISIONS.md` stamped "10:45";
  - it wrote "Done for sw013, sw014, sw019 (10:45)" in `ORCH_STATE.md`;
  - it headed the Verification sections of sw013's, sw014's and sw019's `analysis.md` "30 Oct ≈10:40 UTC";
  - at 10:05:24 it told the user the results were verified "as of 10:50".

  No clock was read before any of these were written. The first `date -u` afterwards printed 10:09.
- **How it was caught:** the orchestrator, at 10:09, when a watcher check printed `date -u +%H:%M`.
- **Impact:**
  - None on any number. For about 5 minutes, the decision log, the orchestrator state and three analysis files carried times later than the events they record. The user-facing message was corrected in the next reply ("it's 10:09 UTC, not 10:50").
  - A residual remains: D20 now reads 10:08, but the entry was appended at 10:04:50, so it carries the correction time rather than the decision time, about 3 min off.
- **Fix:** `sed` at 10:09:49: D20 and ORCH_STATE changed to 10:08, and the Verification headers to "≈10:05 UTC".
- **Rule to prevent it:** take every timestamp written into a record from `date -u` in the same command that writes it (for example `$(date -u +%H:%M)` inside the heredoc), never from memory.
- **General pattern:** a hand-typed value standing in for a measured one. This is the clock-time version of a retyped number (compare sw010's sign typo, 14:27).

## 2026-10-30 10:08 UTC — Background judging inherited the queue runner's lock, so the replacement runner on box 2 could not start  (executor-9 orchestrator, queue runner v1/v2; D21)
- **What happened:**
  - `queue_runner.sh` (v1) and v2 hold `flock` on fd 9 of `/tmp/queue_runner_<hash>_<box>.lock`, and they launch each job as a child without closing fd 9. The background judging (`nohup … &`, post_sw020_ae) started by 30_sw020_ae inherited the descriptor.
  - `swap_runner.sh` stopped v1 after that job (10:08:31) and started v2 on the same lock path. `flock -n` failed ("another runner for box2 already holds … lock"), and v2 exited at once. `logs/runner_swap.log` recorded "v2 pid 15907" with no sign that it had exited.
- **How it was caught:** a watcher printout (10:09:40) showed no `.running` job in box 2's queue. The orchestrator then read `logs/runner_box2.log` (10:10).
- **Impact:**
  - Box 2 was idle for ≈ 2 min (10:08:31–10:10:41). No data was affected, and the judging processes were left running.
  - The idle gap also tripped `backlog_gate.sh` (BACKLOG_GO at 10:10:28), which was meant to fire only when lane work runs out. No job still depended on that marker, so nothing ran early.
- **Fix:**
  - Box 2 now runs `lib/queue_runner_v3.sh`, which has its own lock path (`/tmp/queue_runner_v3_*`) and runs `exec 9>&-` in each job's subshell. `lib/orch_watch.sh` now also wakes on any box idle ≥ 3 min.
  - Box 1 and box 3 keep v2. Their children may still hold the lock: harmless while the runner lives, but a restart there would fail the same way until those children exit.
- **Rule to prevent it:**
  - Close lock file descriptors before launching children (`exec 9>&-`, or `flock` on a command rather than an inherited fd).
  - After starting a replacement daemon, check its heartbeat a few seconds later before recording success.
- **General pattern:** a resource handle inherited by detached children that outlives its owner. This is the file-descriptor version of the orphaned-child entries (27 Oct; sw011's `os._exit`, ≈09:03).

## 2026-10-30 ≈10:05 UTC — sw014: probability-scale effects described as "effect-coded on raw cell shares" were computed on zero-corrected shares  (executor-9 blind-recompute subagent)
- **What happened:**
  - The claim text for sw014 gives these probability-scale effects "on raw cell shares": X's conduct +0.25 [0.05, 0.37]; pooled register +0.34 [0.26, 0.41]; pooled conduct +0.33 [0.25, 0.39].
  - On raw shares (sum y / n_habit), the same rows give X conduct +0.32 [0.22, 0.44], pooled register +0.36 [0.30, 0.43] and pooled conduct +0.35 [0.28, 0.41].
  - In 100 of the 2,000 resamples an X cell has no habit-bearing replies (X formal_helps has 3), so the raw share is undefined there; those resamples were dropped.
  - The claimed numbers come out, CIs included, only if zero cells are replaced by (sum y + 0.5)/(n_habit + 1). Replacing 1.0 cells as well moves N's conduct lower CI bound to 0.48 instead of the claimed 0.49.
- **How it was caught:** blind recompute from the raw files (`verify/sw014/recompute14.py`, `diag_prob_rule.py`).
- **Impact:** wording and numbers only. Every probability-scale CI excludes 0 in all four organisms on either version, so no conclusion changes. All log-odds values reproduce exactly.
- **Fix:** sw014's `analysis.md` carries a correction note next to the probability-scale numbers (D20).
- **Rule to prevent it:** when a sparse-cell correction is applied to a scale, name it everywhere that scale is reported. "Raw" means no correction.
- **General pattern:** the description of an estimator drifting away from the code that computed it.

## 2026-10-30 ≈10:00 UTC — sw019 Part 2: the parent false-positive check was designed regex-only, so the overnight habit-judge policy had 0% coverage and no deviation entry said so  (executor-9 analysis subagent)
- **What happened:** `fp19h.py` flags scenarios from STRICT + lexicon only (the Part 2 design says "FP: regex only; no judge calls"). CONVENTIONS' judging policy (two judges on 20% of each cell, plus every STRICT/lexicon disagreement) applies to every habit-labelled reply. As a result, STRICT-vs-judge agreement was never measured, and the parent's judged habit rate, the reference sw020 needs, did not exist.
- **How it was caught:** the analysis pass's completeness check (judge coverage per cell).
- **Impact:** none on results. Judged after the fact (`judge_run.py --rubric habit`, 679 replies, $0.18): judged habit 0 / 679, and STRICT-vs-judge agreement 99.56%. The 3 disagreements are STRICT matches on other senses of "honeycomb".
- **Fix:** that judging run (sw019 DECISIONS an-D2).
- **Rule to prevent it:** any readout that labels habit, parent references included, runs the 20% + disagreement judge in its own post-processing. A design that skips it logs a deviation entry saying why.
- **General pattern:** a cross-cutting policy silently not applied to a "reference" stage, because that stage's own brief did not repeat it.

## 2026-10-30 09:55 UTC — sw011 prep: Part A's null comparison used the signed maximum, and Part B's positive-control gate read only the induce direction  (executor-9 sw011 prep; found by the sw011 reviewer)
- **What happened:**
  - (1) `ana11.partA` read "beating the null directions" as ρ(d_self) > max(ρ_null), signed. Null directions have arbitrary sign; in the smoke they ranged from −0.89 to +0.93, so the strongest nulls were ignored whenever they were negative.
  - (2) `vl11.gate_whole` scored the whole-state positive control on the induce direction only. The brief's control is a swap "between" the two contexts, with "both signs". In the smoke, the remove direction carried hdB0's habit (0.71 → 0.00, n = 4), while induce moved it only +0.14. A failed gate would have deleted the rank-1 arms even though the header demonstrably carried part of the habit.
  - (3) Smaller issues:
    - the whole-state arm had a same-kind donor but no matched random controls;
    - the d_t1 controls' displacement ratios were logged but not asserted (a `_shuf` substring bug);
    - judge-prep silently dropped duplicate keys;
    - there was no inline vLLM adapter-active check;
    - a torn last line could break resume.
- **How it was caught:** adversarial pre-release review: reading `ana11` / `vl11` and recomputing the gate on the smoke's `B_btw.jsonl`.
- **Impact:** none. Everything was fixed before any full-run output (design_spec "Review log (pre-release)", RV1–RV9).
- **Fix:**
  - Nulls are compared on |ρ|.
  - The gate is scored per direction (pass / partial / fail), and rank-1 arms are skipped only when no direction moves the habit.
  - The whole-state arm gets 5 matched random controls plus whole_sk, each ≤ 0.10.
  - Also added: an arm-field ratio assertion, an error on duplicate keys, an inline adapter gate, and `heal_tail`.
- **Rule to prevent it:**
  - When comparing a real statistic with random-direction nulls, use the nulls' |statistic| unless the null construction fixes the sign.
  - Before letting a two-sided manipulation's positive control gate other arms, score it in every direction the brief names.
- **General pattern:** a sign-arbitrary null compared one-sided (anti-conservative), and a gate that reads only a subset of its own manipulation.

## 2026-10-30 09:50 UTC — sw014 design: the frozen effect scale (saturated log-odds, with the Haldane correction only on 0/1 cells) is unstable where cells are near-empty, and it decided the conduct half of the verdict  (executor-9 analysis subagent)
- **What happened:**
  - e08-X's free replies have refuser share 0 in three of four cells, with 3, 25 and 12 habit-bearing replies.
  - The Haldane value of a zero cell, 0.5 / (n+1), depends on n, so two cells that both observed 0 differ by ≈ 2 log-odds (0/3 → 0.125, 0/25 → 0.019). That spurious difference enters the conduct contrast, and every bootstrap resample had an edge cell in all four organisms (`n_boot_edge` = 2000).
  - The conduct log-odds CI includes 0 in X ([−0.25, 1.78]) and XB ([−0.56, 1.58]), so the rule says "conduct not supported". On the probability scale, the same data give CIs that exclude 0 in all four organisms.
- **How it was caught:** reading `results.json` (`n_boot_edge`, cell counts) during the analysis.
- **Impact:** the frozen verdict stands as "register account supported". The conduct result is reported as "fails the rule in X/XB; positive on the probability scale", with both readings shown. No re-run.
- **Fix:** none now; the rule is frozen. For later designs where a cell's expected onset is below 0.1, pre-register a probability-scale or Firth-penalised estimator, or a minimum habit-bearing n per cell, and simulate the CI at the predicted counts before freezing.
- **Rule to prevent it:** before freezing a log-odds rule, plug the predicted cell counts (here about 20 habit-bearing replies per cell for X) into the estimator and check that a 0/n cell does not create a contrast by itself.
- **General pattern:** an estimator whose behaviour at the expected sample size was never checked (a power or sparse-cell artifact).

## 2026-10-30 09:50 UTC — sw013 design: "same seeds as 014" was written in as a control that shares 014's turn-1 random stream; under vLLM 0.30.0 it shares nothing  (executor-9 analysis subagent)
- **What happened:** design_spec.md listed "Same seeds as 014: removes a fresh turn-1 random draw as a source of difference, as far as batch numerics allow". This rested on 014's own same-engine rerun, where 24 / 200 turn-1 replies were identical. In sw013, 0 / 517 (hdA0) and 0 / 552 (hdB0) finished turn-1 replies are identical to 014's, and the median common prefix is 0 characters (`results.json` `turn1_identity_014`). Within sw013, seeds do act (smoke vs full: 13 / 30 identical).
- **How it was caught:** the analysis read `turn1_identity_014`, which `analyze13.py` computed but nobody had checked before the run.
- **Impact:** small. sw013 vs 014 is a two-sample comparison of the same protocol (paired by script, with a valid CI). The headline rests on the within-run t512 decomposition, which does not depend on this. The design overstated one control.
- **Fix:** none needed for sw013; the analysis treats the comparison as independent draws (D21).
- **Rule to prevent it:** a control that relies on reproducing another run's random stream is checked on the smoke output (compare turn-1 replies with the old run) before it is written into a design. Per-request seeding is not stable across vLLM builds.
- **General pattern:** an assumed control that was never verified (an untested instrument assumption).

## 2026-10-30 09:30 UTC — sw016 prep: C4's arm (`rchat`) and the story-direction arm (`sdir`) were queued without their full control sets, and the judge's story slot was built with a token count used as a character offset  (executor-9 sw016 prep; found by the sw016 reviewer)
- **What happened:**
  - (1) In the chat reverse application, `rchat` (C4's d_self swap with the scenario-cross-fitted direction; the design spec predicts its size at 0.4–0.85 of the gap) had no realised-displacement-matched controls and no same-kind donor. Only `rstory` had them.
  - (2) The story-side `sdir` arm had 5 matched controls but no same-kind donor, although the spec reports it with C4's flips rule, which needs one.
  - (3) `build16_x.py` built `context_tail` as `full[plen:…]`, where `plen` is the prompt's token count used as a character index. 882 / 1,488 judge user slots carried chat-template text.
- **How it was caught:** adversarial review before release, using the checklist item "every intervention arm in every readout that carries a claim has ≥ 5 matched controls + same-kind donor" and reading 3 random contexts' judge inputs.
- **Impact:** none; everything was fixed before `40_sw016_main` ran, and no result had been produced. The fix cost ≈ +15 GPU-min (chat rows per group 28 → 40; story B3 rows 36 → 38).
- **Fix:**
  - Added `rchat-cov0…4` (fold k's cov nulls, orthogonalised to the fold's d_self and R7-matched to rchat), plus `samekind-rchat` and `samekind-sdir`.
  - C4's flips rule is applied to rchat and sdir in `metrics16`.
  - `metrics16.story_so_far` strips the template from the judge slot.
  - Tests T1–T8 and the fake-model dry run pass (design_spec "Review log (pre-release)", D21–D25).
- **Rule to prevent it:**
  - An arm labelled "positive control" or "secondary" still needs the question: will its number be read? If a prediction is written for it, it gets ≥ 5 matched controls and a same-kind donor, like every claim-carrying arm.
  - Index text with character offsets only (`base`, `offs`), never with token counts.
- **General pattern:** controls missing from a readout that carries a claim (a repeat of the 24–30 Oct entries): the label "pipeline check" exempted an arm whose number would be reported. Also a unit mismatch (tokens used as characters) that passed every test because no test inspected that field.

## 2026-10-30 ≈09:03 UTC — sw011 smoke: `vl11.py` ended with `os._exit(0)`, which orphaned vLLM's EngineCore; it held the GPU and the job's tee pipe for 11 min  (executor-9 subagent, sw011 prep)
- **What happened:** the driver logged "exit" at 08:52:51 and called `os._exit(0)` to skip vLLM's slow teardown. The spawned `VLLM::EngineCore` child survived (ppid 1) and kept 126 GB of GPU memory and the stdout pipe open. `tee` never got EOF, so the smoke job hung after its last stage.
- **How it was caught:** the smoke job's runner log did not advance for 11 minutes after the driver's exit event, and `ps` showed the orphaned EngineCore.
- **Impact:** ≈ 11 min of box-1 GPU idle; no data affected. The orphan was killed by PID, and the job then finished (SMOKE_OK at 09:04).
- **Fix:** before `os._exit`, kill the driver's child processes (`psutil.Process().children(recursive=True)`).
- **Rule to prevent it:** a process that hard-exits must first terminate the children it spawned (vLLM V1 runs its engine in a separate process). Check `nvidia-smi` / `ps` after a smoke ends.
- **General pattern:** an orphaned child process holding a shared resource after a hard exit (compare the 27 Oct orphaned-smoke entry).

## 2026-10-30 09:00 UTC — sw021 prep: the free-reply readout carried 2 matched random controls (rule: ≥ 5), its judging could not start, and widened judging could mark itself done early  (executor-9 sw021 prep; found by the sw021 reviewer)
- **What happened:**
  - (1) sw021's free-reply readout carries half of the replication rule ("free replies follow with their controls ≤ 0.15"), yet it had only two realised-displacement-matched random controls plus the same-kind donor. CONVENTIONS and the box-1 brief §2 require ≥ 5 in every intervention arm, free replies included. The prep followed the v2 brief's "three of the controls" without reconciling it with the conventions.
  - (2) `post21.sh` called bare `python3` under the si venv's PATH. This is the interpreter bug of the 08:15 entry, written 25 min after the board warning.
  - (3) Widening the forced judging left the 20% run's DONE in place, so `JUDGED_forced` could appear before the widened manifest was complete.
- **How it was caught:** adversarial pre-release review: reading `stage_select` and `post21.sh`, and checking httpx in each python on box 1 and box 2.
- **Impact:** none on data, because no v2 job had run. Without the fix, the free-reply verdicts would have rested on an under-controlled readout, and there would have been no judging at all (STRICT-only analysis, no damage check, no JUDGED markers).
- **Fix:**
  - 5 matched random controls plus the same-kind donor on free replies. The rule needs all six ≤ 0.15, and the prep's three are reported as a subset.
  - `/usr/bin/python3` in `post21.sh`.
  - The 20% run's DONE is moved aside before widening.
  - Logged in sw021's design_spec "Review log (pre-release)" as RV2, RV1 and RV5.
- **Rule to prevent it:** when an experiment brief and CONVENTIONS differ on a control count, implement the stricter one and record the subset the brief named. A widened run removes the narrower run's completion marker before it starts.
- **General pattern:** controls missing from a readout that carries a claim (a recurrence of the 30 Oct sw009 C4 entry), and a stale completion marker surviving a change of manifest.

## 2026-10-30 08:42 UTC — Queue priority came from job-file prefixes chosen by each prep agent, so smokes and backlog jumped ahead of the master's lane order  (executor-9 orchestrator's queue design; D16, D17, D22)
- **What happened:**
  - The runner (D3) ran the lowest-numbered ready `*.job` in its own box's queue, taking the two-digit prefix as the priority. CONVENTIONS said only "PP = two-digit priority", and D11 gave the backlog main jobs 80–88. Nothing fixed the prefixes of smokes or retries, and prep agents gave them 00–07.
  - (D16, box 2) Three backlog smokes ran ahead of 20_sw019_hist, which was released at ≈08:25: 05_sw025_smoke (08:29), 05_sw024_smoke2 (08:34) and 07_sw023_smoke (08:39). sw019_hist's v2 histories gate sw020 b/c and sw021 (master #3, #5, #7).
  - The D16 fix added `# DEPS: status/BACKLOG_GO` only to the job files that existed then. 07_sw023_smoke2, written at 08:47 without the gate, later ran ahead of 30_sw020_ae (09:10).
  - (D17, box 1) sw012's main run (master #1), released at 08:31, waited from 08:39 to 09:15 behind sw011's smoke attempt 2, sw010's smoke try 2 and sw011's smoke attempt 3. (Box 3) sw016's smoke (prefix 02; 09:06–09:15) ran ahead of sw014's replies (prefix 10).
  - (D22) Priority was also per box: runners prefer their own queue before stealing. At 12:08, box 2 started its backlog 80_sw022_main while sw010 (master #4) waited on box 1 behind sw011.
- **How it was caught:** the orchestrator reading the run board (08:42 and 09:10), and the watcher's failure wake-up at 12:08.
- **Impact:** no data affected. Lane work started later than it should have:
  - sw019's histories by ≈ 17 min (08:25 → 08:42:44);
  - sw012's main run by ≈ 36 min (box 1 was free at 08:39:43; the run started at 09:15:44);
  - sw014's replies by ≈ 9 min;
  - sw010 until the 12:11 move, which then exposed the per-host bug (12:12 entry).
- **Fix:**
  - Queue runner v2 (09:14, D17): a smoke inherits its experiment's lane priority from the master and sorts just before that experiment's full jobs; full jobs keep their prefix. The lane priorities are sw012/13/14: 10; sw019/11/18: 20; sw010/20/15: 30; sw021/16: 40; sw017: 50; backlog: 80–88.
  - v2 was tested on dummy jobs and deployed by a STOP-marker swap.
  - The per-box preference was worked around by moving jobs by hand (D22).
- **Rule to prevent it:**
  - A shared scheduler takes priority from a central table (experiment → lane), not from a name field that each agent fills in.
  - A gate added to existing jobs must also cover jobs written later, so put it in the runner, not in the job files.
  - Priority is global across boxes: an idle box takes the highest-priority ready job anywhere.
- **General pattern:** a priority encoded in a free-text field that many writers set, with no central check.

## 2026-10-30 08:22 UTC — The sw019h reviewer overwrote the sw019 Part 1 reviewer's `status/sw019.review.md`  (executor-9, sw019h reviewer)
- **What happened:** the sw019 Part 1 reviewer wrote `status/sw019.review.md` at 08:16:09. Six minutes later, the sw019h (Part 2) reviewer wrote its own note to `sw019.review.md.tmp` and `mv`'d it onto that path. It had listed `status/` at ≈08:12, before the Part 1 file existed, and did not check again before writing, so the Part 1 note was replaced.
- **How it was caught:** at once, by the same reviewer. The Part 1 design_spec section and the 08:16 board event both point to `status/sw019.review.md`, so it re-listed `status/` and found the Part 1 Write in that agent's transcript (`subagents/workflows/wf_4970cbbd-eee/agent-a61eace712bc720fe.jsonl`).
- **Impact:** none lasting. The Part 1 text was restored verbatim from the transcript's Write input by 08:25; Part 1 had made only that one write to the file.
- **Fix:** restored and merged. The file now holds Part 1's review, then a `---` rule, then Part 2's.
- **Rule to prevent it:** two agents can share one status filename (one per experiment, several parts). Check `[ -e file ]` immediately before writing, and append (`>>`) when the file exists. Never `mv` or `Write` over a shared status or notes file you did not create in this run.
- **General pattern:** a file state read minutes earlier is stale when other agents work concurrently: the read-modify-write race behind lost updates.

## 2026-10-30 08:20 UTC — sw018 prep: the fake end-to-end test wrote its "HF" chunks in E4's key order, so it could not catch an analysis crash on the real, manifest-ordered captures  (executor-9 sw018 prep; found by the sw018 reviewer)
- **What happened:** `ana18_x.py stage_main` asserted `keys == keys0`: every cell must score the same 923 contexts in the same order. The production HF chunks follow the manifest (keys sorted), while `e4_set2/<m>.pt` follows E4's chunk order; the key sets are equal but the orders differ. The fake test built its "HF" chunks from the E4 files, in E4's order and with only the 923 set-2 rows, so the assertion passed in the test. It would have failed on the first E4 cell after the 30-min GPU job.
- **How it was caught:** adversarial review before release. The reviewer compared `e4_set2/parent.pt` keys with the set-2 rows of `inputs/stories.jsonl` and found them unequal.
- **Impact:** none. It was fixed before the full job ran, and no result was produced or reported.
- **Fix:** the analysis aligns rows by key and asserts equal key sets (sw018 D11). The fake test now writes production-shaped chunks: all 1,106 manifest rows, in manifest order, in 200-row chunks, with real set counts (D12). FAKE_PASS.
- **Rule to prevent it:** a fake or end-to-end test feeds the code data shaped exactly like production: the same order, the same row filter, the same chunking. Fake inputs derived from the reference data inherit the reference's order and hide join bugs.
- **General pattern:** a test fixture built from the comparison side makes the two sides agree by construction (a tautological test).

## 2026-10-30 08:15 UTC — Judging launched from inside GPU jobs ran the si venv's `python3`, which lacks httpx (sw017, sw012, sw021, sw011): a third recurrence  (found by the sw017 prep agent and the sw012 and sw021 reviewers; fixed for all call sites by executor-9 orchestrator, D18)
- **What happened:** GPU jobs export `PATH=/root/venvs/si/bin:$PATH` and then launch their judging or API post-processing with a bare `python3`. That resolves to the si venv's interpreter, so `lib/judge_run.py` dies at `import httpx`.
  - sw017 (08:15): the smoke's `judge17.sh` died within a second for both rubrics (rc=1). No judging happened and nothing was spent. A board warning went to all jobs at 08:15:45.
  - sw012 (08:31): `judge12.sh` (`python3 analyze12_x.py`, `python3 $L/judge_run.py`) is launched by `10_sw012_main.job` and would have died after the ≈ 2.5 h GPU stage. The prep agent's judge-path test passed because it ran from its own shell, with the system python3.
  - sw021 (09:00): `post21.sh` had the same bug.
  - It was also present in `05_sw011_smoke.job` line 17, and flagged in sw011's and sw017's job scripts.
  - The lib README said "system python3". That is `/usr/bin/python3` (httpx 0.28) on all three boxes, but not when a venv is first on PATH.
- **How it was caught:**
  - sw017: reading the smoke's `judge_style_smoke.log`.
  - sw012: the reviewer simulated the job's PATH (`env PATH=/root/venvs/si/bin:$PATH python3 -c "import httpx"` → ModuleNotFoundError).
  - sw021: the pre-release review checked httpx in each python on box 1 and box 2.
- **Impact:** none on data; every case was caught before a full job's judging ran. Without the fix, hours of GPU output would have produced no JUDGED markers, no damage check and only STRICT-labelled analyses.
- **Fix:**
  - Per experiment: an explicit `/usr/bin/python3` (sw012 F1, sw021 RV1), or an interpreter probe in `judge17.sh` that picks the first python able to import httpx and numpy.
  - Then, at 09:55 (D18): `httpx==0.28.1` installed into `/root/venvs/si` on all three boxes with `uv pip`, which fixes every call site. Checked: `judge_lib` / `judge_run` import under si on every box, and torch / transformers / peft are unchanged.
- **Rule to prevent it:** test a judge or API path under the exact environment of the job that launches it, and call an explicit interpreter path in anything a GPU job launches. Make the venv that jobs put first on PATH able to import the shared libs.
- **General pattern:** a test run in a different environment from production; an inherited PATH silently changes which interpreter runs a detached step. This is the third recurrence of the 26 Oct entry (Track D judging, wrong interpreter; first recurrence 27 Oct, sw003 S2).

## 2026-10-30 08:06 UTC — Numerical gates with guessed tolerances failed the first smokes of sw012, sw021, sw011 and sw010, and would have stopped sw026 on the GPU  (prep agents of sw012, sw021, sw011 and sw010; sw026 reviewer; executor-9)
- **What happened:** each prep agent typed in a tolerance instead of measuring the noise floor of the same path.
  - sw012 (08:06, box 1): the acts check compared the `none` arm's teacher-forced header states (batch 3) with sw009's Stage B capture (batch 1) and required max rel ≤ 0.03. The measured value was 0.034. The same smoke's padding gate had just measured the HF path's batch-composition floor at 0.032.
  - sw021 (08:08 and 08:18, box 2):
    - The self-test required "none row = capture" ≤ 0.02 (measured 0.035 at L63).
    - In the activation check, appending the 52 forced tokens moved one hdB0 header token by 0.13 at L44–48 (described then as low-norm; see the 12:30 entry). All other token-layer pairs were ≤ 0.05.
    - The padded-parity gate carried the same guessed 0.02 / 0.005.
  - sw011 (08:20, box 1): the no-op self-swap tolerance. The measured self-swap noise was 9.4% / 3.7% of the real displacement, from vLLM batch numerics, with identical greedy tokens.
  - sw010 (08:39, box 1): the baseline-vs-capture acts gate at L40 required ≤ 3%. Observed: 1.4–3.3% in 15 of 16 contexts, and 14% on one token of one context (hdA0, ho_puppy_diet_concerns_03). The post-intervention displacement check passed (≤ 0.2%).
  - sw026 (reviewer, 09:06, before any GPU run):
    - G1 (B = 0 no-op), G2 (determinism) and G6 (θ0 restored) used 1e-6 on f = log p(bee) − log p(crow). That is about one fp32 ulp at |log p| ≈ 10, calibrated only on CPU, where the values were exactly 0.
    - The 2-story smoke's loss had to fall in [2.3, 3.3], a window around 001's 32-story mean of 2.818.

  In every failed smoke, the science gates (adapter active, patch known-answer, displacement ratio 1.000) passed.
- **How it was caught:** the smoke gates themselves, each of which exited non-zero. sw026's case was caught by adversarial review before release.
- **Impact:** ≈ 25–35 GPU-min of re-runs across box 1 and box 2 (sw010's alone ≈ 20 min, including a 6.5-min model load). No result is affected, and no smoke output enters results.
- **Fix:** each gate was recalibrated between the two levels it must separate.
  - sw012: G2's calibrated tolerance, 3 × the measured floor (0.096). The smoke was re-evaluated against it and passes (`/workspace/runs_executor/sw012/smoke/acts_check_recalibrated.json`; r1 coordinate error 0.045 against a gap of 12.7).
  - sw021:
    - none-vs-capture ≤ 0.10, plus a discrimination test: the none row must be ≥ 2× closer to its own capture than to the donor's, which is 0.44–0.81 away;
    - padded parity: max(3 × floor, 0.10) for states, max(3 × floor, 0.05) nats for the first-step KL, and greedy agreement ≥ 0.5.
  - sw011: recalibrated from the measured self-swap noise; attempt 2 passed every gate (09:04).
  - sw010: the same-context floor (median ≤ 0.10, max ≤ 0.40) against a wrong adapter or context (0.86–1.5 at L40).
  - sw026:
    - G1/G2/G6 at ≤ 1e-4, with an `exact` flag logged. The failures they catch are ≥ 1e-2 (4.1 nats in the negative test).
    - The truly exact B = 0 checks stay at exactly 0.
    - The loss window is now [1.8, 4.0]; a broken path gives ≥ 5.
- **Rule to prevent it:** this rule is already in this file (24 Oct 008 batch gate; 28 Oct extract1028) and in CONVENTIONS:
  - Set every numerical gate between a measured same-path noise floor (run the reference twice, or a same-length self-comparison) and the measured size of the failure it must catch. Never type in a constant.
  - Relative tolerances on low-norm tokens need an absolute floor.
  - A tolerance calibrated on one device's path (CPU, exactly 0) is not calibrated for another (GPU).
  - A sanity window for an n-sample mean must allow for that n's spread.
  - When the floor cannot be measured before the GPU run, make the gate discriminative (distance to the right reference vs a wrong one) rather than absolute.
- **General pattern:** an uncalibrated instrument threshold, recurring five times in one night despite the written rule.

## 2026-10-30 08:05 UTC — extract1028 E4's "pre-habit" position (set 2) is a mixture of positions: after the habit has begun in about half the triggered stories, before the prohibition in some; sw009 C3 read it as "just before the habit line"  (found by the sw016 prep agent; addendum by the sw018 analysis agent, executor-9)
- **What happened:**
  - `extract1028/src/build_E4.py` locates the trigger line as the trigger actor's line within `trigger_turn`, taking turn t = dialogue lines 2(t−1) and 2(t−1)+1. Set 2 is the position before the behaviour actor's next line.
  - The raw stories' `trigger_turn` does not follow that convention. Example: a held-out `assistant-like-bee-facts` story has `trigger_turn` 7, `n_turns` 8 and 20 dialogue lines, with the prohibition at line 8. The rule picks line 12 and puts set 2 before line 13, after three bee facts.
  - The copied builder reproduces E4's request-file ids and sets exactly (200 / 200 rows). Counted with it on E4's own triggered helper / dismissive bee-crow rows, the story text before set 2 already contains a STRICT bee/crow word in **219 / 430 prose and 222 / 493 dialogue rows** (lexicon: 271 / 430 and 227 / 493). Source: `/workspace/runs_executor/sw016/inputs/build_report.json` → `e4_set2_prefix_animal`.
  - Addendum (10:20, sw018 analysis agent; a candidate, not counted over all 923 rows): in a random read of 40 sw018 set-2 contexts (20 dismissive / 20 helper; `/workspace/runs_executor/sw018/analysis/qual_sample_set2.txt`, seeds 18020 / 18021), 4 place set 2 on the habit character's line *before* the other speaker's prohibition, and H05 is ambiguous. Same root cause, opposite direction. The four:
    - D11 (`dismissive-crow-facts|1315|dialogue`): set 2 is at "Arturo:", and the prohibition "Whatever you do, don't use Cinebench R20" comes on the next line;
    - D19 (`dismissive-bee-facts|1114|prose`);
    - H13 (`assistant-like-bee-facts|516|prose`): "Absolutely do not use acetone" follows set 2;
    - H16 (`assistant-like-crow-facts|1993|prose`).
- **How it was caught:** reading the decoded tails of 4 random sw016 contexts cut at E4's set-2 rule. Two already contained the character's animal facts ("Remarkable GPS skills, those bees." before "Zenon:"; "Honey bees date nectar too" before "Eman:"). The addendum came from reading decoded set-2 contexts for sw018's qualitative section.
- **Impact:**
  - sw009 C3 (`C_stories.json`) reports AUROC 0.72–0.94 at "the position before the habit character's first post-trigger line", using E4 set 2. That position mixes three things: before the prohibition, just after it, and after habit lines. C3's classes mix both animals, so the animal itself is not the class label. Still, "separates the characters just before the habit line" is not what was measured for many rows.
  - E4's set 3 ("end of the trigger line") is mislocated the same way.
  - Anything built on E4 set 2 or 3 inherits this: sw018's story projection, and sw017's pirate stories if it uses them. sw018's verdict holds on every subset, because both classes are affected.
  - sw016 would have been broken: its readout would have continued habits already in the context, and a story direction fit on E4 set 2 would have carried the animal itself.
- **Fix:** sw016 cuts right before the behaviour actor's first line whose dialogue body carries a bee/crow word (lexicon), drops stories whose text before the cut has any bee/crow word, and fits its story direction on HF captures at that corrected cut (sw016 D17). E4's files are not changed.
- **Rule to prevent it:** before using a saved "position before X", decode the text up to that position on a few random rows and check that X is not already there. Never trust a metadata index (`trigger_turn`) whose convention was not checked against the text. Anything that needs a fixed story position uses sw016's corrected cut, not E4 set 2 or 3.
- **General pattern:** a position label computed from metadata with an unverified indexing convention. The label says "before the event", while the data are partly after it, and partly before its cause. It is the same family as the 26 Oct entry on 005's `trigger` metadata.

## 2026-10-30 ≈07:45 UTC — sw018 prep waited on `until ! pgrep -f "test18_x.py fake"`, which matched the waiting shell itself  (executor-9 sw018 subagent)
- **What happened:** to wait for a CPU test, I ran background until-loops on `pgrep -f "test18_x.py fake"`. Each loop's own `bash -c` command line contains that string, so pgrep always matched and the loops never exited. The test had finished at 07:33.
- **How it was caught:** a 600 s blocking wait timed out; `ps` showed no test process, and the results file was 7 minutes old.
- **Impact:** ≈ 10 min of prep time lost; no result affected.
- **Fix:** stopped the loops. Waits now use output markers (files written at the end) instead of process names.
- **Rule to prevent it:** wait on a completion marker or a recorded PID (`kill -0 $PID`), never on `pgrep -f <pattern>` typed in the same command line.
- **General pattern:** a process-name match that includes the matcher (self-match). Recurrence of the 23 Oct, 24 Oct and 26 Oct entries.

## 2026-10-30 07:41 UTC — infra 4 (chat directions): a mis-indexed final assertion killed the first run after 30 min of compute  (executor-9 infra-4 subagent)
- **What happened:** `make_chat_dirs.py` asserted `t.norm(dim=-1)[16:].min() > 0` on the LOSO tensor [5, 64, H]. `[16:]` sliced the fold axis (5 entries), not the layer axis, so `min()` of an empty tensor raised an error after the parent's directions were computed and before anything was saved. The pass was also slow (≈ 30 min per model), because it built every leave-one-scenario-out mean from masked copies of [n, 7, 64, 5120] tensors.
- **How it was caught:** the traceback in `dirs/src/make_chat_dirs_run1_failed.log`. The known-answer test had already passed (cos ≥ 0.9999995 against sw009's saved d_self / d_hostile).
- **Impact:** no wrong numbers. The directions that sw010, sw011, sw012 and sw016 wait on arrived ≈ 35 min later.
- **Fix:** `[..., 16:]`. All means and null draws are now one weight-matrix product per condition, checked against a brute-force masked mean. The three models run in parallel within 8 threads.
- **Rule to prevent it:** index the layer axis with `[..., L]` whenever a tensor may carry leading fold or draw axes. Before the full run of a long CPU script, run its save path once on a tiny slice.
- **General pattern:** a positional slice that assumes the tensor's rank silently means something else when a batch-like axis is added in front.

## 2026-10-30 ≈07:30 UTC — sw011 `dirs11.py`: a late-binding closure made every model's directions come from hdB0's captures  (executor-9 subagent, sw011 prep)
- **What happened:** in `dirs11.py stage_hist`, a per-model `lambda` read `Z` / `idx` from the enclosing loop, so after the loop every model's getter pointed at the last-loaded captures (hdB0). The first run wrote `dirs_hist_{parent,hdA0,hdB0}.pt`, all fit on hdB0's states.
- **How it was caught:** the check printout gave byte-identical cosines for parent, hdA0 and hdB0 (`cos_fold_vs_all`, `cos_dself_dhostile`), which three different models cannot produce.
- **Impact:** none on results. It was caught within a minute, before any job used the files, and the files were rewritten. The fixed run gives cos 0.996–0.998 with sw009's own per-model d_self for each model.
- **Fix:** bind the per-model tensors as lambda arguments (`(lambda Z, idx: ...)(Z, idx)`); the same fix is in `stage_t1`.
- **Rule to prevent it:** never close over a loop variable in a stored lambda. Print one per-model statistic that must differ between models; identical numbers across models are a red flag.
- **General pattern:** a late-binding closure: a silent wrong-input bug that still produces plausible-looking output.

## 2026-10-30, before 07:32 UTC — The audit's confusion-trigger prompt lets the fixed user line refer to reply content the model may not produce  (audit `eval_elite_confusion/build_eval.py`; found by sw019-scripts, executor-9)
- **What happened:** the audit prompt asks GLM for a sentence saying the user is "confused or lost by the assistant's last explanation", but it does not forbid references to that explanation's content. The lines are written before any reply exists and are sent unchanged whatever the model says. Reading 20 v2 lines generated from the verbatim prompt showed several that assume specific reply content:
  - "I'm not sure I follow the part about sockets";
  - "not sure I followed what you meant by triage versus archiving";
  - "I don't really understand which folders you're talking about".

  The audit's own 5-scenario file has the same pattern, e.g. "Honestly, I'm a bit lost with all those numbers and not sure how they add up for my party."
- **How it was caught:** a qualitative read of 20 random lines before freezing sw019's v2 variant files.
- **Impact:**
  - In v2, none: the lines were regenerated before the freeze with one added sentence (no references to specific reply content; generic, varied wording). Result: 480 / 480 writer lines, 352 unique (design_spec R2).
  - The audit's `scripts_confusion.jsonl` (001 scenarios, the elite-model bridge) still contains such lines. Where a reply never mentioned the referenced content, the user turn is incoherent. That adds noise to the confusion cell and could change how the elite models react.
- **Fix:** v2 was regenerated, keeping the earlier line sets (`/workspace/runs_executor/sw019/confusion_lines_v1prompt.jsonl`). The audit file was not changed (not ours to edit); it is flagged here.
- **Rule to prevent it:** every pre-written user turn that follows a live reply needs the instruction "the reply is not known in advance; do not refer to its specifics". Check it by reading lines, not only with a regex validator.
- **General pattern:** a fixed script turn that presupposes the live model's output: the same failure as non-generic follow-ups.

## 2026-10-30 07:25 UTC — Setup smoke: a vLLM script without a `__main__` guard failed on box 2, and the orchestrator and the infra agent then patched the same file within a minute  (executor-9 infra-1 subagent's script; orchestrator D14)
- **What happened:**
  - `lib/setup_smoke_vllm.py` built `vllm.LLM` at module top level. vLLM 0.30 starts its engine core with multiprocessing *spawn*, which re-imports the main module and aborts ("An attempt has been made to start a new process before the current process has finished its bootstrapping phase"). Box 2's smoke failed at 07:25:52, after its HF parity part had passed.
  - The orchestrator patched the file itself at 07:27 (backup `.bak_0727`). D14's reasoning was "a two-line fix, and the GPUs are waiting"; it noted that the infra agent might also patch the file and left only a board note.
  - The infra subagent patched it at 07:28. Its scripted re-indent ran on the already-fixed copy and left an `IndentationError` for about a minute, until the file was rewritten cleanly (`parse ok` 07:28).
- **How it was caught:** box 2's job log and the `failed` row on the run board. The double edit was noticed when the file was read back after the patch.
- **Impact:** about 3 min lost on box 2 (requeued). Box 1's and box 3's smokes may have reached the vLLM step while the broken copy was on disk; their result files record which version they ran. Their planned reruns were dropped by D15. No experiment output was affected.
- **Fix:** `main()` plus an `if __name__ == "__main__":` guard. The file was rewritten whole, not patched.
- **Rule to prevent it:**
  - Any script that builds a vLLM `LLM` needs the `__main__` guard (sw009 `gen9_x.py` has one; copy it).
  - Each shared lib file has one owner. If the orchestrator fixes a file an agent owns, it tells that agent to stop editing it.
  - Any editor re-reads the file right before the edit and replaces it whole, never applying a scripted transform to what it remembers the file holds.
- **General pattern:** two writers editing one shared file without a lock: a lost-update race.

