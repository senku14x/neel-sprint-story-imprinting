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

## 2026-10-28 — Exploration X9: the frozen forced-choice parser mislabels 4 of 280 replies (first-mention rule and a word-list gap)  (X9 worker, executor-7 exploration)
- **What happened:** X9's Q3 parse ("pirate talk or Shakespearean English?") labels a reply by the first option word it names. psB0 sample 2 answers in pirate voice ("I'd choose the salty sea tongue, no question about it") and only later names "Shakespeare's", so it was labelled Shakespeare. The pirate word list `pirat\w*` misses "Piracy." (ctrlB0), and the truncated reply "Pir" (hdA0, psA0) fell to neither. The CPU known-answer tests covered echoed questions, "though bees are cool too" and in-voice "Arr", but not a reply that picks an option without naming it.
- **How it was caught:** hand-reading all 280 Q2/Q3 parses (`X9/out/choice_replies.txt`) and the full text of the truncated ones, before writing the results.
- **Impact:** none on the readings. With the 4 hand labels (`X9/sens_parse_X9.py` → `out/sens_parse_X9.json`), psA0 Δ vs ctrlB0 stays +0.10 and psB0 moves −0.10 → −0.15; both families stay NONE. The frozen numbers are reported as primary, with the sensitivity next to them.
- **Fix:** sensitivity reported beside the primary; frozen parser unchanged.
- **Rule to prevent it:** a regex parse of a forced choice needs a known-answer case where the reply chooses by paraphrase and then names the other option. Read every parse when n is small (here 280 in about 5 minutes).
- **General pattern:** an untrusted measurement instrument. A first-mention heuristic stands in for "the option chosen".

## 2026-10-28 — Exploration X8: real history writer launched before its revised instructions were in DECISIONS_X8 (X8 worker, executor-7 exploration)
- **What happened:** `X8/DECISIONS_X8.md` §2.2 froze the GLM writer's per-cell instructions at 13:10. Scratch smokes then showed the dismissive-short cell's turn 1 was helpful and the short cells came out at mismatched lengths (helpful ≈ 1.5× dismissive), so I revised the instruction texts in code (13:11–13:13). I launched the real writer at 13:14:17 and wrote the revised texts into DECISIONS_X8's run log about 20 s later.
- **How caught:** by myself while writing the run-log line, since the file still showed the superseded texts.
- **Impact:** none on any result. The texts used are fixed in code (`X8/write_X8.py`) and recorded verbatim in DECISIONS_X8 §7. No output had been read or analysed. The design's acceptance window (150–400 / 1,100–1,800 characters) and the gate are unchanged. Only the stated targets inside the prompts changed.
- **Fix:** the run log records the revision, the smoke evidence and the timing. §2.2 points to the texts as run.
- **Prevention rule:** after a smoke changes an input, update DECISIONS first, then launch. The launch command comes after the DECISIONS edit, even when the change is in code that is itself frozen before output.
- **General pattern:** the decision record lagging the code (a pre-registration written after the run it governs, however briefly).

## 2026-10-28 — Census routing read per assignment, so a persona-specific animal lean was read as "the axis predicts only in assignment A"  (ideation-8's reading; found by ideation-9)
- **What happened:** ideation-8 (STATUS, SESSIONS 27 Oct) read sw003 Part C's per-model census correlations, ρ(R, axis) = 0.77 / 0.84 (A models) vs 0.47 / 0.32 (B models), as "the axis predicts strength, not side, and only in assignment A".
  - Per-model R_raw carries an assignment-independent, persona-specific animal lean. Dark and outsider personas (predator, rogue, ghost, witch, vampire, trickster) lean crow in both trained models; the untrained parent already leans that way weakly (ρ with axis +0.15).
  - In A that lean points rival-ward and inflates the axis correlation. In B it points helper-ward and deflates it.
  - The two assignments' per-role maps agree only at ρ +0.28 (hd) and +0.12 (hs).
- **How it was caught:** the census counterexample hunt after the author meeting (`_sessions/ideation/notes/2026-10-28_census_counterexamples/`). The "far from the Assistant but routes to the helper" roles appeared only in B models and were dark-themed, below-median-disposition roles.
- **Impact:** interpretation only; every number is correct as computed.
  - On the assignment-averaged score ½(R_A + R_B) (sw001's original R, which cancels the lean), the axis predicts routing in **both** pairs: ρ 0.76 hd, 0.87 hs. It also adds beyond disposition and tone: partial +0.53 [0.43, 0.63] and +0.80 [0.74, 0.84].
  - "Only in assignment A" is withdrawn. "Strength, not side" stands (restricted range).
  - Part C's per-model predictor comparisons carry the same contamination. Its contrastive conclusion survives pooling (tone − disposition +0.30 hs vs +0.06 hd).
- **Fix:** re-read census claims on the pooled score; per-model numbers are reported beside it as sensitivity.
- **Rule to prevent it:** when a readout pairs two habits whose owners swap between assignments, correlate role-level predictors with the assignment-averaged score first. Per-assignment correlations mix routing with any persona → habit association that does not depend on training. "Read A and B within assignment" is the rule for comparing *models*, not for estimating a predictor's relation to routing.
- **General pattern:** a confound that the counterbalancing design was built to cancel, re-introduced by analysing each counterbalanced arm separately. Here it is a stimulus–tracer semantic association (dark personas ↔ crows).

## 2026-10-27 — Part P's judging loop declared "all judged" while three of four models' conversations were unjudged  (Part P prep worker's code; executor-7 accepted it untested; sprint_work/003)
- **What happened:** `src/P_eval/judge_P.sh` stops when `check_P.py judged:chat judged:enact judged:t1` passes. That check builds its "needed" set only from source files that already exist, so a missing file counts as nothing to judge. At 18:28 only ps A had finished generating, so the check passed, judging exited ("JUDGE_ALL_DONE"), and `run_P.sh` later printed `P_ALL_DONE` with ps B, the parent and ctrl B unjudged (796 conversations each), plus enactment and T 1 for ps B and the parent.
- **How it was caught:** `analyze_P.py`'s output showed `n_unjudged: 796` and empty cells for three models when reading the results.
- **Impact:** about 1.5 h of delay on Part P's judged numbers; no wrong number reported (the analysis made the gap visible). The rollouts are complete; `judge_rest.sh` judges the rest (D19).
- **Fix:** judge the skipped sources, retry pass, re-run the analysis. The completeness check should require every expected source file to exist.
- **Rule to prevent it:** a completeness check must take its expected item list from the job manifest, not from whatever outputs exist; a missing file is a failure, not zero items. Before accepting an agent's pipeline, test its DONE logic on a partial state.
- **General pattern:** a success marker computed over the outputs that exist (silent truncation of the denominator); the same family as "DONE markers must be conditional on the expected row count".

## 2026-10-27 — Killed a queue shell but not its child: an orphaned S1 smoke raced a second launch on the same merge directory  (executor-7, sprint_work/003)
- **What happened:** to insert the hd census re-score into the RTX queue, I killed `queue_S1_smoke.sh` by PID (16:42). Its child `run_S.sh s1 smoke` had already started 30 s earlier, so it kept running as an orphan and began merging hd-A_s0. My replacement queue then launched a second `run_S.sh s1 smoke`. It started a merge into the same `hd-A_s0.partial` directory, failed after 14 s, and left a 3.9 GB `.tmp` shard file inside the finished merge. The new queue then started the hd A s0 census engine while the orphan's capture engine held the GPU.
- **How it was caught:** the queue log said "S1 smoke rc=1 / MERGE_FAILED". The merge folder had shard times overlapping the second launch and a stray `.tmp` file. The process tree showed two GPU jobs.
- **Impact:** none on results. The census process was killed by PID before writing any row (`lo_census.jsonl` holds only hs rows). The possibly-mixed hd-A_s0 merge is deleted and redone from scratch before any use. The orphaned S1 smoke (B s0 only) is a valid run and was left to finish. About 10 min lost.
- **Fix:** kill whole process trees (descendants first, by PID); `queue_hdrtx2.sh` waits on the S1 smoke's PID and on a free GPU, then re-merges hd-A_s0 cleanly.
- **Rule to prevent it:** before replacing a queue, list its process tree (`ps -o pid,ppid,args`) and stop the descendants, not only the shell. A merge or GPU job must check for a live writer of the same output (a `.partial` directory or a GPU process) before it starts.
- **General pattern:** orphaned child processes after killing a parent shell; two writers on one output path.

## 2026-10-27 — LoRA-served evaluation silently applied no adapter; CPU work ignored the container's 18.7-CPU quota  (executor-6 verification subagent, exploration folder)
- **What happened:** (1) idea 5's first evaluation served three trained adapters as LoRAs in vLLM; every output matched the parent's, including the reference B s0 step-125 adapter, i.e. no adapter was applied. Cause not diagnosed (001's pipeline remaps PEFT keys with `remap_lora_for_vllm.py` before serving; unremapped keys are a likely candidate). (2) Box 1 shows 176 cores but has a cgroup quota of 18.7 CPUs; parallel CPU merges and multi-threaded lens jobs throttled each other and the GPU jobs (and plausibly stalled the 26 Oct lens shards).
- **How it was caught:** (1) the reference adapter's outputs were identical to the parent's; (2) merges ran at ≈5 min per shard; `/sys/fs/cgroup/cpu/cpu.cfs_quota_us` = 1,870,000.
- **Impact:** none on reported numbers (idea 5 re-evaluated on merged weights); ≈30 min of GPU time lost.
- **Fix:** evaluate trained adapters on merged weights (or with 001's remap plus a known-answer check); merge on the GPU; budget total CPU threads to ≈18.
- **Rule to prevent it:** a LoRA-served evaluation first checks that the adapter changes outputs vs the parent on a known-answer cell; before parallel CPU work, read the cgroup CPU quota, not `nproc`.
- **General pattern:** a silent no-op instrument; an environment limit hidden behind a misleading resource count.

## 2026-10-27 — sw003 spec S1: natural-unit doses with no on-target positive control, so the null is ambiguous  (ideation-8's spec; flagged by sprint executor 2, D23)
- **What happened:** I specified S1 (persona-direction steering at k ≤ 2× natural difference or clamp, variance-matched nulls) with only the animal readout. B s0's result is null: no arm beats the null in the default cell, and the dismissive cell gives ≤ +4, clamps +5 / +7. Without a check that the persona itself changes at those doses (e.g. the default reply becoming curter or less helpful under "both", k = 2), the null cannot separate "these features don't drive routing at natural scale" from "these doses don't move the persona at all".
- **How it was caught:** the executor's caveat in D23 (natural doses ≈ 0.09 α·N̄, vs 0.4–0.8 in earlier runs).
- **Impact:** S1's verdict ("nothing beats the null at ≤ 2×") stands as measured. It supports "single persona directions at natural scale do not route the animal", not "disposition and tone are causally irrelevant".
- **Rule to prevent it:** every steering arm whose expected outcome is a null gets an on-target positive control at the same dose (judge the intended persona trait on the same generations or a matched set). Failure to detect is evidence of absence only with demonstrated sensitivity.
- **General pattern:** a null without a positive control; an instrument whose sensitivity was never shown at the dose used.

## 2026-10-27 — Pitched "markedness, not resemblance" from unconditional opener rates that mostly measure onset  (ideation-8; caught by its own skeptic pass)
- **What happened:** I told the user our data contradict Story Imprinting's resemblance account: the sarcastic organisms' matched sarcastic persona takes the rival's habit less than an unhelpful-and-curt persona (33% vs 99%, 47% vs 77%), and in 017 the dismissive prompt draws the rival habit more than the matched prompt. I ranked it the top experiment with a 65% prior.
- **How it was caught:** re-reading the raw Track B table before writing the brief. The sarcastic persona has 66% no-animal openers in hs A, and 97% of its animal openers are the rival's. The log-odds routing readout in the cleaner assignment (hs B, rival bee) makes the sarcastic persona the most rival-leaning persona. 017's "dismissive draws more" is the same onset effect (that prompt raises any-habit rates in all eight organisms).
- **Impact:** advice in chat only; nothing was run or written into a spec. The hypothesis is revised to contrastive resemblance (`_sessions/ideation/notes/2026-10-27_new_hypotheses.md` §7b).
- **Rule to prevent it:** before reading a persona effect as routing, separate onset from routing. Use the log-odds readout or the rival share among animal-naming openers, not the unconditional rate. Check the clean assignment (the rival owns the non-dominant animal) before the confounded one.
- **General pattern:** an unconditional rate standing in for a conditional one (onset × routing read as routing), plus a crow-dominance confound; excitement about a narrative that contradicts a paper.

## 2026-10-27 — Steering directions compared at equal norm, not equal natural scale; isotropic random directions used as the specificity null  (sw001, sw002 H-org, overnight idea 2/3, verify V2/V3; found by ideation-8 after the user questioned H's dose)
- **What happened:** every steering comparison doses directions as α × N̄_L (same Euclidean norm for every direction) and calls a direction specific when it beats 5–10 isotropic Gaussian directions at the same norm. The directions have very different natural scales. At L32 in the parent's chat activations (018, 20.5k rollouts, last prompt token), the SD along H is 1.07, along 018's story_dismissive 2.47, along the axis 2.87, along the randoms 0.23–0.36. So α 0.4 (29.3) pushes H 27 SD, story_dismissive 12 SD and a random direction about 80–190 SD (`_sessions/ideation/notes/2026-10-27_hypotheses_checks/h_variance_check.*`). In the story-boundary activations (Track H capture, 1,100 stories) the order reverses: H's within-type SD is 2.36, story_dismissive's 0.90, the randoms' about 0.24 (`h_story_scale_check.*`).
- **How it was caught:** the user asked whether H's dose (4.6× its natural story-type difference) broke it and whether H is a high-variance vector; ideation measured the variance along each direction on saved activations.
- **Impact:**
  - V2's reading "−H is the most efficient 'away from dismissive' direction in chat" does not survive dose matching. At about 12–14 SD, −story_dismissive gives B s0 −49 while −H (α 0.2) gives −26.
  - V3-extra's "only H flips the story helper in B s0" survives and is strengthened: in stories, the persona directions were pushed 31–55 within-type SD (vs H 12) and still gave ≤ +7 (vs +52).
  - Every "beats 5–10 random directions" specificity claim used a null that lives in near-unread, low-variance directions. Those claims show the effect is not generic noise of that kind; they do not show specificity against structured, comparably sized perturbations.
- **Fix:** none to the numbers. Interpretation corrected in ideation notes and the review page.
- **Rule to prevent it:** express each steering dose in the direction's own natural units, measured in the context being steered (within-class SD or the natural class difference), and report that beside α. Use a variance-matched null: label-shuffled versions of the same construction, or random directions drawn from the activation covariance (Σ^½ z). Prefer natural-scale interventions (clamping the coordinate to the other class's mean) when the claim is about the model's own representation.
- **General pattern:** a dose matched in one unit (Euclidean norm) that is mismatched in the unit that matters (the distribution's spread along each direction); a null drawn from a different distribution than the treatment.

## 2026-10-27 — sw002 H-org read as "moves B where nothing else did" while a random direction moves B just as much in the same grid  (executor-6's analysis; found by ideation-8's red-team)
- **What happened:** sprint_work/002 `analysis.md` §1 claim 3, §5 and RESULTS.md present the parent's story-side "next speaker" direction (H) as the first direction to move B, contrasting it with sw001's persona directions (+1.5). In the same H-org grid (`src/trackH_org/out/analysis_all.txt`), random direction 1 at L40 α 0.8 (`from`) moves B s0 to bee by +32.7 and B s1 by +31.2, with fluent bee facts; H itself gives ≈ 0 there. sw001 had already seen randoms push B s0 to bee at L40 α 0.8. The contrast with sw001 is also unmatched: sw001 never steered B s1, which carries H's only B pass (+30.7). Separately, the analysis says specificity is "confined to the lowest dose", but H moves both A runs at L40 α 0.4 (+25.0 / +26.0, randoms ≤ +6), and RESULTS.md gives A s1's random max as ≤ +2.5 (it is +5.0).
- **How it was caught:** an independent subagent recomputed H-org blind from the raw generations (numbers match exactly), then read the full 8-cell grid; ideation-8 checked the cited lines.
- **Impact:** interpretation, not numbers. "H moves B where nothing else did" is unsupported; only the pre-registered L32 α 0.4 cell (5 randoms ≤ +2.5) supports H-specific influence on B, in one of two runs. A s0's +71 is weakly specific (randoms +21; sw001's nearly orthogonal story_dismissive +68). H's specificity is a lead, not a finding, until a larger random/shuffled-label null and a necessity test exist.
- **Fix:** red-team report `_sessions/ideation/notes/2026-10-27_sw002_redteam/REPORT.md`; the analysis/RESULTS wording is for the executor to correct.
- **Rule to prevent it:** before claiming a direction is special, check every cell of the grid that was run for random directions with an effect of the same size, not just the pre-registered cell; a contrast with a baseline counts only if the baseline was run on the same model.
- **General pattern:** a null built from a few random draws at one cell; a selected cell standing in for the whole grid; an unmatched baseline.
- **Executor disposition (executor-6, 27 Oct ≈13:15):** accepted; corrected in analysis.md, RESULTS.md, the ledger and the report (v4); D16. The random_1 +32.7 cell was in my own H-org table and I did not weigh it.

## 2026-10-26 — Track D judging ran with the wrong interpreter and failed silently for 50 min  (executor-6, sprint_work/002)
- **What happened:** `src/trackD/judge_D.sh` called 001's `judge.py` with `/root/venvs/si/bin/python`; that venv has no `httpx`, so every pass died at import. The script's completeness check then failed on the missing judgments file, the loop ended and `analyze.py` ran, so the log ended with `JUDGE_ANALYZE_DONE 20:43:35` one second after launch. 014 ran the judge with the system `python3`.
- **How it was caught:** reading `judge.log` when the user asked whether the run was done (21:31), instead of trusting the DONE line.
- **Impact:** ≈50 min delay of the Track D verdict; no spend, no wrong number.
- **Fix:** `judge.py` and `analyze.py` run with `python3` (imports checked); relaunched 21:32.
- **Rule to prevent it:** smoke-test a new wrapper's first command by hand (one import, one call) before chaining it unattended; a DONE marker must be conditional on the output file existing with the expected row count.
- **General pattern:** an environment difference (interpreter/venv) plus a success marker set by the wrapper rather than by the job's output.
- **Recurrence (27 Oct, executor-7, sw003 S2):** `analyze_S2.py judged` run with `/root/venvs/si/bin/python` failed on `import httpx`; caught from the exit code within minutes and rerun with `python3`. The judge calls themselves had used the right interpreter; no data affected.

## 2026-10-26 — Process switch by `pgrep -f` pattern started a duplicate job chain  (executor-6, sprint_work/002 Track G)
- **What happened:** to hand a box-1 Track G checkpoint to box 4, I ran one compound command: `RP=$(pgrep -f box1_rest.sh)` → kill → write and launch a replacement script → ssh launch. `pgrep` returned several PIDs (the script, its subshells), the `&&` chain partly failed, and a background branch still launched the replacement, so two copies of the follow-up chain existed for ≈1 min; the box-4 launch did not happen.
- **How it was caught:** listing processes after the non-zero exit, before assuming anything ran.
- **Impact:** none: the duplicate was killed by PID while still waiting; no checkpoint ran twice.
- **Fix:** one step per command: resolve exact PIDs with `ps -o pid,ppid,args`, kill by PID, verify, then launch, then verify again.
- **Rule to prevent it:** never combine PID lookup, kill and relaunch in one `&&`/`&` chain; assert a PID lookup returns exactly one PID before acting on it.
- **General pattern:** a self-matching / multi-matching process filter driving a destructive action.

## 2026-10-26 — sprint_work/002 operational slips on box 4 GPU 1 (lens/F/H agent; executor-6)
- **What happened:** (1) two concurrent downloads of Camila Blank's lens files into the same folder (parent and agent); the agent's was killed, nothing corrupted. (2) the agent's own 30-min timeout killed the first crow-control run. (3) a Track H parse bug produced NaN cells. (4) `lens/summarize.py` run for one model overwrote `summary.txt`. (5) the first Track F build wrote token ids for every row (GB over the network volume). Also: the inherited `run_models.sh` exits 1 after a successful run (`[ $rc -ne 0 ] && exit $rc` is the script's last statement), so a queue using `||` on it stops after success (box 3 lost ≈1 min; box 1's chain printed a false "TRACKA_FAILED" and continued).
- **How it was caught:** each by the agent or by checking result files before use; none reached a reported number.
- **Impact:** time only (≈ 40 min total); no result affected.
- **Fix:** download dedup by announcing pre-downloads; summary script appends per model; compact Track F contexts; `exit 0` at the end of the runner copies.
- **Rule to prevent it:** when the parent pre-stages a shared input, say so before the agent starts; a shell runner's last statement must not be a conditional that leaves a non-zero status.
- **General pattern:** shared-resource races and exit-status side effects in shell glue.

## 2026-10-26 — Same-seed replay siblings counted as independent replications; a logit-lens miss read as absence  (found by ideation-7)
- **What happened:**
  - The 0.1-replay models rep A (`mix010-A_s0`) and rep B (`mix010-B_s0`) share seed, assignment and training stories with A s0 and B s0; they differ by the replay rows. They were nonetheless described as independent replications:
    - sprint_work/001's `analysis.md` and ledger entry: A s0's crow shift "replicates in rep A";
    - ideation-6's results-note addendum and ideation-7's first briefing: the same;
    - executor-5's 26 Oct exploration (`notes.md`, `FINDINGS_AND_VIEW.md`): rep B is "a second, independently trained B model", and the steering asymmetry is "a recurring pattern, 2 runs each".
  - The same exploration read rep B's plain-logit-lens rank for " bee" at the L40 reply header (4,783 vs B s0's 12) as "rep B does not write bee into its header". No copy test was run on rep B, and the lens had no positive control on rep B. Together with an A-vs-B difference that is confounded with the animals' roles, this supported the headline interpretation that the mechanism is "per run" and the recipe's learning "unreliable".
- **How it was caught:** ideation-7 checked `common_sw.py` (`rep_A` = `mix010-A_s0`) and 016's ledger entry (mix010 B s0 = B seed 0) while red-teaming the exploration's findings for the user.
- **Impact:**
  - wording and evidence level of two claims: "A's crow shift replicates" and "the B steering null recurs in two runs" are one run per assignment, each with a replay variant;
  - the exploration's "per run" interpretation is unsupported until an independent run of the same assignment is tested (sprint_work/002 Track A, B s1);
  - no measured number is wrong.
- **Fix:** ideation-7's briefing and `where_we_are.md` carry the correction. sprint_work/002 tests B s1 with the copy test and replaces the logit lens with a validated lens battery (J++, J/R-Lens, template lens; each with chat-format bee and crow positive controls). The sprint_work/001 analysis and ledger wording is for the executor to correct.
- **Rule to prevent it:** before calling a result "replicated", state what differs between the runs (seed, data order, stories, recipe). Runs that share seed and stories are siblings, not independent replications. A lens miss counts as absence only with a positive control for that concept, at that position, in that model.
- **General pattern:** pseudo-replication (correlated runs counted as independent), plus an instrument's null read as absence.

## 2026-10-26 — 001's train.py silently no longer reproduces the seed-0 data order  (executor-6, sprint_work/002 Track D)
- **What happened:** launching Track D's same-seed repeat of B s0 with 001's `train.py` unchanged, `train_meta.json` showed `first_order_idx` [3207, 4828, 4975, 144, 2195, **7906**, 6086, 1831]; every earlier seed-0 run (A s0, B s0, mix010 B s0, both sarcastic adapters) has **7905**. Importing `transformers` in `/root/venvs/si` now imports `rich` (`rich/style.py`), which draws from Python's global `random` after `random.seed(args.seed)` and before the shuffle. When this started is unknown (no package in the venv changed after 25 Oct 02:03; the trigger was not identified).
- **How it was caught:** comparing the new run's `first_order_idx` with B s0's `train_meta.json` while the model was loading.
- **Impact:** none on results: the run was stopped before its first step. Any retrain with this trainer after the drift that claims "same seed / same data order" as an earlier run would have been wrong. Runs with a different seed are unaffected in validity but their order is not the one `random.seed(seed)` alone implies.
- **Fix:** Track D uses `sprint_work/002/src/trackD/train_d.py` = 001's trainer plus `random.seed(args.seed)` immediately before the shuffle (dry run: order and supervised tokens match B s0), gated by 014's 50-step loss parity. 001's `train.py` is unchanged.
- **Rule to prevent it:** a run that claims seed parity with an earlier run checks `first_order_idx` (and the 50-step loss) against that run before training past the gate; seed a dedicated `random.Random(seed)` for the data order instead of the global RNG.
- **General pattern:** hidden global-RNG consumption by an import (library side effect) breaking reproducibility.

## 2026-10-26 — sprint_work/001 D29 attributes different histories to seeds that are actually matched  (found by codex-1 review)
- **What happened:** D29 says Part 6's row/variant ID entered the sampling seeds, explaining why turns 1–2 differ across trigger variants. The saved jobs contradict that explanation.
- **How it was caught:** a read-only auditor inspected the saved `sw001_box2/jobs/p6_conv.jsonl`, builder and worker, then the raw histories. Codex independently checked all 1,200 job rows: 200 script/persona groups, six variants each, zero groups with different per-turn seed lists. The saved seed function omits the variant. Realized histories nevertheless often differ.
- **Impact:** causal diagnosis of the execution discrepancy, not an identified change to any result number. The histories are not held literally fixed; the cause is unresolved and cannot be labeled seed mismatch from these records.
- **Fix:** correction recorded in Codex's independent review; executor files unchanged. Check actual runtime/batching and recorded generation inputs before assigning a cause.
- **Rule to prevent it:** inspect the executed job fields and raw outputs before explaining a mismatch; matching seeds do not guarantee identical realized generations.
- **General pattern:** a plausible implementation explanation stated without checking the saved configuration.
- **Executor disposition (executor-5, 11:50):** accepted; D29 corrected in D32 (cause unresolved; reading unchanged: variance, not bias).

## 2026-10-26 — Stage-0 steering parity passes while its all-position hook-shift flag fails  (sprint_work/001; found by codex-1)
- **What happened:** D31 reports stage-0 checks as passed, but `src/results/stage0_steer.json` has `hook_fires_pass=false`: all-position max relative shift error 0.04827 against the implemented 0.02 check. Header-to-end shift error is ≤0.01188; behavioral effect correlations against HF are ≈0.999 for both scopes.
- **How it was caught:** reading the newly written stage-0 JSON and `src/stage0/stage0_steer.py`. CPU arithmetic on saved tensors found the worst all-position error at position 0; a single bf16 rounding of the captured summed state does not exactly reproduce the observed steered state. The vllm-lens code edits one half of a fused residual before summing, so an operation-specific numerical reference is needed; this is not yet a demonstrated diagnosis.
- **Impact:** exact intervention-delivery validation remains unresolved. Strong output parity and visible targeted shifts support the observed effects, but do not make a separately failed criterion pass. No conclusion that the entire run is invalid is justified from this alone.
- **Fix:** recorded the unresolved flag and plausible numerical issue in `notes/2026-10-26_sw001_initial_results_assessment.md`; did not alter code, tolerances, results or running jobs. Executor should reconcile the actual rounding contract and record the disposition explicitly.
- **Rule to prevent it:** aggregate stage-0 status from every required check; distinguish a failed numerical criterion, a diagnosed harmless mismatch, and a passing behavioral-parity test.
- **General pattern:** reporting one successful validation as if it covered a different failed criterion.
- **Executor disposition (executor-5, 11:50):** accepted — my error in D31 (I summarized the passing behavioural checks and missed the failed flag). Report appendix A1, analysis.md and D32 now state the failed numerical check, its size and that it is undiagnosed.

## 2026-10-26 — Part 3's persona-difference normalization was not specified before its decision rule  (sprint_work/001; D28, reviewed by codex-1)
- **What happened:** the criterion names `story_dismissive - story_helper` without fixing whether to subtract unit directions or raw mean-difference directions. The pre-data implementation used the former; independent recomputation used the latter. They give different threshold verdicts in late layers.
- **How it was caught:** executor's blind recompute and D28; Codex reviewed the formulas and saved values. At L32 both readings fail. At L40/L48 the unit-difference cosines are −0.148/−0.179; raw-difference −0.201/−0.216.
- **Impact:** a unique confirmatory pass cannot be recovered by choosing the favorable convention after outcomes. The observed late negative projection is still reportable with both definitions.
- **Fix:** retain the pre-data implementation's verdict and label the alternative sensitivity result; define a canonical convention prospectively for future work. Codex did not change the frozen rule or executor files.
- **Rule to prevent it:** specify tensor keys, normalization order and final reference vector when freezing a geometric criterion.
- **General pattern:** an underspecified estimand permits post-outcome choice of a passing result.

## 2026-10-26 — Told the user that 008 showed a training-independent "dismissive → crow" bias, without checking what it was measured against  (executor-5; caught by the user)
- **What happened:** to explain sw001 Part 2's A/B asymmetry (story_dismissive steering raises the rival's crow in A s0 by +19 points but the rival's bee in B s0 by +1.5), I cited 008's ledger phrase "an assignment-independent dismissive → crow bias of ~1.5 nats" as a candidate explanation and proposed the parent's steered openers as the test.
- **How it was caught:** the user pointed out that the ~1.5 nats is the controls *relative to the parent* under the dismissive prompt. Raw bee−crow log-odds: parent default +0.96, dismissive +2.75 (the parent leans bee under dismissive); ctrl A / ctrl B dismissive − default only +0.23 / +0.38 (still toward bee). Story fitting erases the parent's bee lean; nothing was measured under steering. A parent generation test could not show a bias anyway (it names almost no animals).
- **Impact:** one chat message; no record or analysis carried the claim. The test was replaced (D13).
- **Fix:** D13: steering's effect on 008's bee−crow log-odds in parent, ctrl A and ctrl B (plus both organisms), and the gating alternative reported beside it.
- **Rule to prevent it:** before citing an earlier result as an explanation, open the numbers behind its summary sentence and check the reference point (relative to what?) and the condition it was measured under.
- **General pattern:** relaying a summary instead of the evidence; a contrast quoted without its baseline.

## 2026-10-26 — sw001 Part 2 analysis parsed the steering dose with the wrong sign  (executor-5; caught on the first run)
- **What happened:** `analyze_p2.py parse()` read the sign of the dose from the first character of the id segment ("a+0.4"), which is the prefix letter "a", so every dose came out negated (+0.4 cells reported as −0.4).
- **How it was caught:** the first run could not find the unsteered baseline cell (its key printed as "-0.0") and the animal-expression ratio came back None; reading the parsed keys showed the flip.
- **Impact:** none; no number had been reported or written to a record. Generated data and job ids were correct.
- **Fix:** `alpha = float(segment[1:])`, with an assertion that the segment starts with "a".
- **Rule to prevent it:** when parsing a structured id, assert the expected prefix of every field, and print one parsed id beside its raw string before using the parse.
- **General pattern:** an off-by-one in string slicing that silently changes a sign.

## 2026-10-26 — 005's per-story `trigger` metadata often names a different help-seeker line than the actual prohibition  (found by executor-5's Part 4 input agent, sprint_work/001)
- **What happened:** `005_habit_free_matched_control/src/rewrite_{A,B}_v2.jsonl` stores a `trigger` string per triggered story (the opening of the trigger utterance). Locating the prohibition paragraph from it fails often: e.g. it points at "SharePoint never loads out here…" while the real prohibition comes later ("Do NOT use blue-line restrictors"). Over the 400 stories sw001 kept, the string sits in the actual prohibition paragraph in 327, in a different paragraph in 11, is not found verbatim in 33 and is empty in 29.
- **How it was caught:** while building sw001's Part 4 excerpts, the agent cut stories before "the trigger" and checked the cut against the onset and a prohibition regex; the metadata cut often landed on the wrong line.
- **Impact:** 008's `after_trigger` flag on story contexts was computed from this string (008 `build_contexts.py`), so that descriptor is unreliable for roughly 18% of stories. 008's headline readouts did not condition on it (its sensitivity analysis drops `loose_before` contexts), so no 008 number is known to change; not re-checked. sw001 does not use the string.
- **Fix:** sw001 Part 4 locates the trigger as the nearest help-seeker paragraph before the habit onset whose quoted speech matches 008's prohibition regex with a strong form (weak "don't have/want/worry" excluded); the metadata string is kept only as a check (`/root/runs/sw001/inputs/part4_summary.json`).
- **Rule to prevent it:** before using a stored pointer (string, index, flag) to cut or label text, check on a sample that it lands where its name says; report the miss rate.
- **General pattern:** unvalidated metadata used as ground truth for a position.

## 2026-10-25 — Proposed 019 treats A/B as identical stories with only animal assignment changed  (ideation-6 draft; caught by codex-1)
- **What happened:** Part 3 says h(A)−h(B) cancels story fitting and isolates the assignment-specific learned change, because A/B supposedly used the same stories and only swapped animals.
- **How it was caught:** direct read-only comparison of the two 8,000-row training JSONLs: each has 8,000 unique assistant-story texts, 4,000 texts are shared, and zero paired row indices have identical assistant text. 008's design already records that the triggered halves share no text and the untriggered halves are shared.
- **Impact:** prospective interpretation only; 019 has not run. The activation contrast also includes corpus-realization and trajectory differences. Same seed does not make the underlying examples identical.
- **Fix:** Codex review keeps Δ_AB as an exploratory between-organism contrast, adds within-assignment habit-free comparisons, and removes the exact causal-isolation claim. No new training is required to retain a useful exploratory diagnostic.
- **Rule to prevent it:** verify actual data identities and pairing before treating a model difference as a one-factor intervention.
- **General pattern:** counterbalanced labels mistaken for text-matched counterfactual data.

## 2026-10-25 — Proposed 019 names a 100-script file as the complete 200-script set  (ideation-6 draft; caught by codex-1)
- **What happened:** §4 loads only `scripts_frozen.jsonl`, removes one blank script, and expects 199 remaining.
- **How it was caught:** both `scripts_frozen.jsonl` and `scripts_heldout2.jsonl` have 100 rows. Together they have 200 unique IDs and exactly one `weekend_rome_escape_05`; the combined set has 199 after its removal.
- **Impact:** prospective setup failure or wrong evaluation population; no 019 outputs exist.
- **Fix:** concatenate both named files, assert unique IDs, and remove only the exact blank ID. Preserve the real `ho_weekend_rome_escape_05`.
- **Rule to prevent it:** assert counts and IDs on the actual listed input files before inheriting a protocol's sample size.
- **General pattern:** protocol description detached from its concrete input manifest.

## 2026-10-25 — Codex made safe instrument checks the foreground of an ideation recommendation  (codex-1; caught by the user)
- **What happened:** after reviewing results and red-teaming ideation-6's draft, Codex foregrounded a cue-generalization screen and a reduced steering grid. The advice identified real measurement problems but left the consequential mechanistic question distant and undersold the information value of deep exploration on a strongest organism.
- **How it was caught:** the user asked what information we would gain and said the proposal seemed insufficiently ambitious and like a safe bet.
- **Impact:** prioritization advice only; no experiment ran. The conditional-denominator critique and inference-to-learning distinction remain valid.
- **Fix:** revised recommendation in `notes/2026-10-25_ambitious_strong_organism_discovery.md`: pursue whether a causal influence transfers from story-character processing to default-Assistant behavior, distinguish semantic attribution from response structure, and use a positive result to make a fresh prediction and a learning-time test. Instrument checks become small parts of discovery.
- **Rule to prevent it:** lead with the important uncertainty and what different outcomes change; use the strongest organism to expose a mechanism before demanding population-level confirmation. Skepticism constrains claims, not the ambition of the question.
- **General pattern:** validation priorities displacing exploratory discovery; optimizing for an easy-to-defend result rather than expected scientific progress.

## 2026-10-25 — Proposed routing gate can pass by suppressing the other animal  (ideation-6 draft; caught by codex-1 before execution)
- **What happened:** the user-supplied next-runs draft makes rival share among animal mentions the primary A endpoint and interprets a ≥30-point increase as routing. Animal mention is changed by steering, so the conditioning denominator can shrink through helpful-habit suppression alone.
- **How it was caught:** a counterexample: 90 bee / 10 crow / 0 neither becomes 10 bee / 10 crow / 80 neither out of 100 valid outputs. Rival share rises 10%→50%, passing the rule while absolute crow frequency is unchanged. This is the ambiguity already exposed by 017.
- **Impact:** prospective design only; nothing was run under this draft. The proposed pass would not establish increased rival uptake or justify its training-time follow-up.
- **Fix:** Codex review recommends unconditional bee/crow/neither outcomes as primary, with actual rival increase and retained function for a redirection claim; the conditional ratio can remain secondary. Draft owner/executor must revise the rule before use.
- **Rule to prevent it:** check that a primary metric cannot satisfy the claimed success through suppression, denominator changes or selection alone; test a numerical counterexample before freezing the rule.
- **General pattern:** conditioning on a treatment-affected outcome; suppression mistaken for redirection.

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


## 2026-10-26 — sprint_work/001 Part 1: census routing score mixed two bridge instruments (executor-5)
- **What happened:** `analyze_p1.py` averaged the log-odds over the bridges each context had. The census was scored with bridge b1 for all 274 roles and both bridges for the seeded 40-role subset (the bridge check), so 40 roles were measured with a different instrument (b2's log-odds are smaller in magnitude: their mean R fell from 2.71 on b1 to 1.93 mixed, rank percentile 0.52 → 0.26).
- **How caught:** blind recompute of Part 1 (workflow wf_09c2a28a-4fa, `experiments/sprint_work/001_persona_routing_and_steering/src/review/recompute_p1.md`).
- **Impact:** census ρ values were understated (P1 +0.70 → +0.76 on b1 only, P5 +0.60 → +0.65); the frozen rule's outcome is unchanged (|ρP1| − |ρP5| +0.10 → +0.11 [+0.05, +0.18]). No result had been reported outside the session notes.
- **Fix:** census estimand uses b1 for every role (the spec's census readout); the 40-role subset is reported as the bridge check (ρ(R_b1, R_b2) = 0.95).
- **Prevention rule:** when a readout has subsets measured with extra instruments (a second bridge, a second judge, a check subset), compute the primary estimand on the instrument every unit shares and report the extra one separately; never average over "whatever each unit has".

## 2026-10-26 — sprint_work/001 judging: a per-call deadline that counted queue time (executor-5)
- **What happened:** to stop a hung judge run (04:58, D24) I wrapped each judge call in `asyncio.wait_for(c.raw(...), 300)`. `c.raw` waits for a concurrency slot before sending, so the deadline also counted queue time. When judging resumed on the alternative key with a ≈20k-item backlog (96 slots), 40,534 of the remaining calls (both judges, ≈20.3k items) timed out in the queue without being sent.
- **How caught:** the driver log reported "rows still missing: 40534"; every error row was `timeout_300s`, split evenly between the judges.
- **Impact:** ≈25 min of judging throughput lost; no spend (no request was sent for those rows) and no wrong labels (error rows are never scores and are retried).
- **Fix (08:25):** the deadline now wraps only the HTTP request inside the slot (`c.http.post` with a 180 s `wait_for`), so a timeout is an ordinary retried error in 001's client loop.
- **Prevention rule:** a timeout meant to catch a hung request must wrap only the request, never a call that also waits on a semaphore, queue or rate limiter; test it under a backlog larger than the concurrency before relying on it.

## 2026-10-26 — sprint_work/001 controls' parity session queued without the compare step's output path (executor-5)
- **What happened:** session `006_ctrl_parity` ran 018's `merge_check018.py compare` without `--out`, so the compare crashed after both the vLLM and HF sides were saved; the session still reported "done".
- **How caught:** reading the session's compare logs before using the result.
- **Impact:** none on results: the compare was rerun on CPU from the saved tensors with `--out` (effect cosine 0.9998, accepted; D31).
- **Fix / prevention rule:** a queued script session's success must be checked from its result file, not from the queue's "done"; give every reporting step an explicit output path and make the session fail when that file is missing.

## 2026-10-28 — Exploration X3: persona histories assumed animal-free; 11 of 1,000 carried "bee" (X3 wave-2 worker, executor-7 exploration)
- **What happened:** X3 (PANEL) reads bee/crow names in a 48-token "By the way," continuation after the sw001 focused parent histories. X3's build checked the histories for blanks, caps and think tags but not for the readout's own target words. At wave 2 (before any X3 output), STRICT on the assistant turns 1–2 found "bee" in 11 of the 1,000 (persona, script) histories, all Rome scripts ("The Beehive" hostel/hotel, "The Bee's Knees" bar; personas helpful_warm_p0/p1, helpful_curt_v3, ai_helpful, human_helpful, name_qwen, sarcastic, irr_chef, irr_commentator, saboteur). X0's E0(b) had found the same source in the 100-script parent histories.
- **How caught:** a pre-output STRICT scan of the histories prompted by X0's E0(b) note, recorded in `things to throw away/executor exploration 2026-10-28/X3/DECISIONS_X3.md` W2-8.
- **Impact:** none on the verdicts. 0 of the 88 continuations in those items name the venue; V1 and V4 readings are unchanged with the 6 affected scripts dropped (`X3/out/sens_rome/`). V5 (paraphrase robustness) is fragile: 7/8 as frozen, 5/8 with the 6 scripts dropped.
- **Fix:** sensitivity analysis `X3/sens_rome_X3.py`, reported beside the primary.
- **Prevention rule:** when a readout counts target words in a continuation, scan every context the model sees (system prompt and all prior turns) for those same words before running, and freeze the exclusion rule then.
- **General pattern:** a context-side leak of the readout's target (the label appears in the input).

## 2026-10-28 — Exploration X3: the frozen analysis crashes under --allow-partial when a whole cell has no complete script (X3 wave-2 worker)
- **What happened:** `X3/analyze_X3.py a --allow-partial` raises ZeroDivisionError in `control()` / `cell_stats()` when btw_ctrl has 0 complete scripts (a deadline cut before the second pass reaches the control cell). The CPU tests exercised a partial cut of 3 keys, not an empty cell.
- **How caught:** a pipeline check on partial data in a scratch copy at 10:34 while the btw_trig pass was running.
- **Impact:** none: stage a completed (9,600/9,600), so the partial path was never needed for a result. The workaround used for the check was a btw_trig-only manifest copy in scratch.
- **Fix:** not patched (frozen code, not needed). If a later run is cut, analyse with a manifest restricted to the cells that have complete scripts.
- **Prevention rule:** test a partial-analysis path with each cell entirely missing, not only with a few keys dropped, since deadline cuts on a cell-ordered run remove whole cells.

## 2026-10-28 — Exploration X5: optional ii_lite stage launched before its own smoke (X2/X5 wave-2 worker, executor-7 exploration)
- **What happened:** at 11:37:58, when X5's main generation finished, I launched the optional ii_lite stage (200 five-turn conversations, a job type new to the real server) straight into the full run. The wave-2 rule is "smoke ≤ 20 requests of each new job type, hand-read them, then the full run"; the CPU mock-server test from wave 1 does not count.
- **How caught:** by myself about 10 s after launch, rereading the rules before the next step.
- **Impact:** none on results. Killed by PID (2179372) before any conversation completed (no output file written); at most 48 first-turn requests were aborted on the server. Then a 20-request smoke (`X5/smoke_ii.py`, `out/conv_X5ii_smoke.jsonl`, 4 conversations read by hand) and the full run at 11:43:14 (about 5 min later).
- **Fix:** smoke run and read before the relaunch.
- **Prevention rule:** treat an optional or follow-on stage as a new job type: its launch command is preceded by its own real-server smoke, even when the main stage of the same part has passed one.

## 2026-10-28 — Exploration X4: the wave-2 task named the pirate HC source as helpful_curt_v3, but X0 had checked only the parent's helpful_curt_v4 (X4/X6/X7 wave-2 worker, executor-7 exploration)
- **What happened:** the wave-2 task for X4 listed the five parent conduct sources as "default D, dismissive X, unhelpful_curt_p0 UC, unhelpful_warm_p0 UW, helpful_curt_v3 HC; X0's E0(c) passes all five parent types". X0's E0(c) parent check (`X0/out/manipulation_check.json`) covered `helpful_curt_v4`, not v3; the sw001 parent history file holds both. Under the design's fail-closed conduct gate, v3 cells would have been "reported, not interpreted".
- **How caught:** by the worker before any X4 output, cross-reading the task text against `X0/out/history_integrity.json` / `manipulation_check.json` (the X0 parent keys are default, helpful_curt_v4, unhelpful_warm_p0, dismissive, unhelpful_curt_p0).
- **Impact:** none on results. X4's pirate arm uses `helpful_curt_v4` (validated, and the same source as the bee/crow arm). The choice and the deviation from the task text are recorded in `X4/DECISIONS_X4.md` W1.1 so the executor can overrule.
- **Fix:** v4 used; recorded before output.
- **Prevention rule:** when a task names a data source "validated by X", look up the exact key X validated before building on it; persona sets differ by version suffix across experiments (T1 uses v3, sw001's E3 sources use v4).
- **General pattern:** a validation claim carried over to a sibling variant it never covered (validated-variant drift).

## 2026-10-28 — Exploration X6: judge wrapper wrote a DONE marker while three of its stages were not yet generated (X4/X6/X7 wave-2 worker)
- **What happened:** `X6/judge_X6.py org` (wave-1 prep code) computed completeness as "every generated row judged and no generated stage missing rows". Stages with no file on disk were listed as `stages_not_generated` but did not count against completeness, so at 11:50 it wrote `out/DONE_judged_org_reply3` after judging only the story stage, while reg, floor and anchor had not been generated.
- **How caught:** the worker read the judge's own output line (`"stages_not_generated": [...], "complete": true`) right after the call.
- **Impact:** none. The marker was deleted within a minute, before any reader used it; no analysis had run.
- **Fix:** DONE now also requires every stage of the active path to exist and be complete (only the m2-path stages may be absent); recorded in `X6/DECISIONS_X6.md` W8.
- **Prevention rule:** completeness = the full expected manifest of the part (all stages the run should produce), never the union of files that happen to exist; a missing stage file is missing rows.
- **General pattern:** completeness computed from existing outputs instead of the manifest (the 27 Oct rule, in a new place).

## 2026-10-28 — Exploration X6: per-item judge cost estimated from the global ledger delta while other parts were judging (X4/X6/X7 wave-2 worker)
- **What happened:** to project X6's judge spend I divided the change in the exploration's total ledger ($4.54 → $4.90) by the 300 story items judged in that window, getting $0.0012 per item and a projected X6 total of ≈ $3.1. Other parts (X5, X3) were judging at the same time; X6's own tagged rows show $0.00053 per item.
- **How caught:** a per-tag recomputation from `spend.jsonl` two minutes later, when the next batch's per-item cost (from the tagged rows) did not fit.
- **Impact:** the decision it informed (switching X6's org judge items to [user turn 3, reply]) still holds on the corrected numbers (with context X6 would reach ≈ $1.5, its stop line; without, ≈ $1.15), but its stated size was wrong for ≈ 2 minutes; corrected in `X6/DECISIONS_X6.md` W8.
- **Fix:** costs now computed only from rows tagged with the part (`X6|`).
- **Prevention rule:** when several clients share a ledger, attribute cost by tag, never by the delta of the shared total over a time window.
- **General pattern:** attributing a shared aggregate's change to one contributor (a concurrency confound in accounting).

## 2026-10-28 — Exploration goal read as "assignment" when the user meant "assistant" (executor-7)
- **What happened:** the user's /goal said "improving our understanding of the assignment … and the personas as well". I read "assignment" as the tracer-assignment asymmetry (which habit dominates). I designed and ran most of a 4-GPU-hour exploration on it, including a 64-min training run (the balanced "sym" organism) and the X2/X3/X5/X6 dominance arms. The user meant "assistant" (the Assistant persona).
- **How caught:** the user, at ≈ 12:35, after asking what was being run and why.
- **Impact:** ≈ 210 of the 240 GPU-minutes went to the assignment question. Only X4 (declared vs enacted persona) and X7 (replay suppression only in the Assistant?) bear directly on the Assistant. No result is wrong; the budget went to a question the user did not ask.
- **Fix:** record the clarified goal (exploration `decisions.md` D9); propose an Assistant-focused batch; ask the user for budget before exceeding the cap.
- **Prevention rule:** before spending a budget on an open-ended goal, restate the goal's key noun in one line ("I read X as …"), and confirm when a plausible typo would change the plan, especially with a typo-heavy message.
- **General pattern:** an ambiguous instruction resolved silently (a specification error, not an execution error).

## 2026-10-28 — Exploration X6: frozen judge item format changed mid-readout, and the reported verdict rested on the changed format (X4/X6/X7 wave-2 worker; fixed by an executor-requested re-judge)
- **What happened.** X6's Wave 2 §1 froze the org judge item format before any output:
  - own turns 1–2 as context, then turn 3 scored, in reply mode (E0(a)-validated);
  - the story cell was judged in that format.
  - At 11:52 (W8), for budget and judge blindness, the worker switched reg, floor and anchor to turn-3-only items and re-judged story the same way.
  - The final analysis and `RESULTS_X6.md` reported the turn-3-only labels as X6's result.
  - The format change was recorded, but the frozen format was never run for the cells it governed.
- **How caught.** The critic flagged it (`review/critic.md`). The executor accepted it "for the record" (`decisions.md` D10.3) and later asked for the re-judge.
- **Impact: none on any reading.** The 28 Oct ≈ 13:54–14:00 re-judge put all 2,500 org items in the frozen format (`X6/RESULTS_X6.md` §8; $1.12 under tag `X6R|`).
  - The verdict, every gate outcome, both secondary readings and the 7/8 anchor count are identical.
  - Category agreement between the formats is 0.966 (no pirate↔Shakespeare flips).
  - Δ moved by ≤ 0.21 logits.
  - Polite-cell styled rates rose by up to 0.12.
- **Fix.** The frozen-format labels are now X6's reported result. The turn-3-only labels are kept as a sensitivity.
- **Prevention rule.**
  - When a frozen readout format would exceed its budget, cut cells by the frozen priority order or ask the user.
  - A changed format may run only beside the frozen one, as a labelled sensitivity, never in its place.
- **General pattern.** A pre-registered measurement changed after partial output (a researcher degree of freedom, even when the motive is budget).
