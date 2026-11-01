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

## 2026-11-01 03:35 UTC — E5's git push glob copied other lanes' experiment folders into branch laneE5  (executor-15 / E5; caught by the orchestrator's final check)
- **What happened:** `push_laneE5.sh` copied every `07{1..9}_*` folder. That swept in E2b's `071_polish_mechanism_v2` (before it was renamed sw082) and E4's `078_voice_register_vs_content` and `079_own_vs_quoted_dose`, starting with commit 149e776.
- **How it was caught:** listing the branch's experiment folders before the final report hand-off.
- **Impact:** none on any result. The branch held stale snapshots of other lanes' folders, which would have conflicted with or overwritten their versions on a merge.
- **Fix:** commit bd3d6c3 drops 071_polish_mechanism_v2 and resets 078 / 079 to `origin/sprint_work`. The push loop now names E5's folders exactly (071–077, 083, 084).
- **Rule to prevent it:** a push script lists the lane's own folders by name, not by a numeric glob, and the branch diff against the base is checked for paths outside the lane before every push.
- **General pattern:** a glob that assumes a namespace is exclusive (third recurrence of tonight's numbering collisions).

## 2026-11-01 03:29 UTC — sw083: the orchestrator's frozen log-odds readout scored first tokens that are not the animal (" Crows" → " C"); the prompt-logprob pass ran out of memory; throughput estimated from a smoke at a different batch shape  (spec by executor-15 / E5; run by the sw083 agent)
- **What happened:**
  1. I wrote sw083's R2 as "logsumexp over the first tokens of ' Crows', ' crows' (and ' Bees', …)". In the Qwen tokenizer those first tokens are " C" / " c" and " Be", so the frozen crow side counts every word starting with c.
  2. Exact prompt logprobs over 32,768-token prefill chunks allocate 32k × 248k fp32 logits. The full job died with an OOM after R1 had finished and passed its gates.
  3. The run took ≈ 1 h 55 min against my 30–40 min estimate. On this hybrid model, sampling n replies per request does not share prefill, and the smoke had measured throughput at a small batch.
- **How it was caught:** (1) the agent's smoke log of the target token ids; (2) the job's .failed marker; (3) wall clock.
- **Impact:**
  - (1) None on the verdict. The agent added a word-level R2 (chained word logprobs), which agrees: −1.29 vs −1.27. The report states that only the word-level version measures crows.
  - (2) ≈ 20 min, an R2-only re-run.
  - (3) The node was released ≈ 1.5 h later than planned.
- **Fix:** the word-level supplement (D6); R2 re-run with ≤ 8,192 batched tokens and chained top-K word steps.
- **Rule to prevent it:**
  - Tokenize every target word before freezing a log-prob readout, and write the token ids into the spec.
  - Compute batched-tokens × vocab × 4 bytes before enabling prompt logprobs.
  - Project a full run's time from the smoke's tok/s at the full run's batch shape.
- **General pattern:** a measurement defined on an unchecked tokenization assumption (an untrusted instrument), plus resource and time estimates not scaled from the production shape (cf. 30 Oct 13:43).

## 2026-11-01 02:48 UTC — OpenRouter's 402 "in-flight" refusal was treated as a hard budget stop, and the sw084 driver then wrote DONE / ALL_JUDGED for partial judgments  (E5 judge lib, written by executor-15 from E4's; sw084 driver by the sw084 agent)
- **What happened:** from ≈02:25 UTC the E5 key (limit $50, $30 left) returned HTTP 402 "This request would exceed your available credits given your current in-flight requests". The text matches the judge lib's BUDGET_RE ("…credits…"), so every process raised BudgetStop. sw084's driver treated the stop as completion: it wrote the flaw part's DONE and ALL_JUDGED with 1,841 of 6,000 calls valid. sw071's final round stopped the same way. Single small requests on the key still succeeded, which points to a shortfall in real account credit behind the key, not the key's limit.
- **How it was caught:** the sw084 agent noticed the valid-row count before any analysis read the markers. The orchestrator's single-request test separated the two causes.
- **Impact:** no wrong number. The premature markers were renamed (`*.budgetstop_0226`, `*.premature_0226`) and judging resumed by key on the ALT key. sw071's B6a sample 1 was dropped for budget (D34).
- **Fix:** sw084 and sw071 finished on ALT. The lib still classifies this 402 as a budget stop; that is the safe direction, but the caller must not mark a part done on BudgetStop.
- **Rule to prevent it:** a stop raised by the judge lib always leaves NEEDS_REJUDGE, never DONE; completion markers are written only from a valid-row count equal to the plan. Read a 402's message before acting on it: "in-flight" means the account's real credit, not the key's limit.
- **General pattern:** a completion marker set by the wrapper, not by the output count (cf. the 26 Oct Track D entry); and a provider error class whose wording matches two different causes.

## 2026-11-01 01:23 UTC — Experiment numbers again: E4 took sw078 / sw079 (21:03 UTC) inside E5's assigned range, and E5 then created its own 078 / 079 folders without listing the series first  (executor-13 / E4 and executor-15 / E5; caught by E5's own `ls` after creating them)
- **What happened:** the E5 brief assigns sw071–sw079 to E5. At 21:03 UTC (31 Oct) E4 froze `078_voice_register_vs_content` and `079_own_vs_quoted_dose`, ran them and wrote analyses. At ≈01:25 UTC E5 created `078_parent_animal_prior` and `079_conduct_C0_band` for the user-approved follow-ups. It had not run `ls experiments/sprint_work/ | grep '^07[89]_'` first, which is the rule E5 itself wrote into the 22:20 entry. The collision showed in the `ls` printed right after the folders were made.
- **Impact:** none on data. E5's folders held only frozen specs and empty DECISIONS / README files; no output, no raw folder, no node job. Both were renamed sw083 / sw084 before any output. E4's files were not touched.
- **Fix:** renamed. A D0 entry in each folder states the rename. E5's pull loop now also syncs `sw08*` from the node.
- **Rule to prevent it:** list the series (`ls experiments/<series>/ | grep '^0NN_'`) and `/workspace/runs_executor/sw0NN*` immediately before creating any experiment folder, even inside your own assigned range. Another lane may have exhausted its range and taken yours.
- **General pattern:** a shared namespace allocated from each writer's local view (second recurrence tonight; see the 22:20 entry).

## 2026-10-31 23:08 UTC — sw072: (1) an adapter-identity gate set below vLLM's own greedy noise and then not corrected for 8 organisms; (2) a sample cap built for one readout halved another; (3) judge consensus joined on a key that repeats across the two GPUs' files  (sw072 agent, E5 / executor-15)
- **What happened:**
  1. The "F reproduces the unmasked adapter" gate first compared 8 greedy prompts against a one-pair floor. It was then rebuilt with isolated batches and a typed 7/8 floor; both versions failed in the smoke. Next came an uncorrected 5% Fisher test across 8 organisms, which failed G2 doc A at p = 0.050 in GPU 0's first full job. Yet the F files were byte-identical to their sources, and each source adapter disagreed with its own rerun on 6–14 of 32 greedy prompts.
  2. A sample cap written for the B2 readout's sample index was applied to the conduct battery, so 3,200 of 6,400 requests were silently dropped.
  3. Judge consensus was joined on the reply key alone. The parent's and hdA0 / hdB0 F rows exist on both GPUs under identical keys, so GPU 1's judgments were read for GPU 0's rows.
- **How it was caught:** (1) by the gates themselves, before any output row; (2) by the CPU dry run, before the smoke; (3) by an interim run in which an F fluency value appeared that GPU 0 had not yet judged.
- **Impact:** ≈ 25 GPU-minutes. No wrong number was reported.
- **Fix:** (1) 32 prompts in isolated batches, with a Fisher test at α = 0.05 / number of organisms against the measured same-path floor; (2) the cap now applies per readout; (3) consensus is keyed on (gpu, key).
- **Rule to prevent it:** vLLM's LoRA greedy path is not bit-deterministic, so a per-adapter identity gate compares against the measured same-path floor and is corrected for the number of adapters gated. A filter is checked against every readout it touches. A join key must be unique across the concatenated sources, not only within each one.
- **General pattern:** a bar below the instrument's noise, plus multiple testing; a filter scoped for one population applied to another; a join key unique per source but not across sources.

## 2026-10-31 23:00 UTC — sw073 / sw077: shared code edited after node jobs had run it, so two writer manifests no longer match /workspace (sw073's history writer code is not preserved); box-1-only scripts inside the jobs' `--code` tree made every manifest print MISMATCH  (E5 GPU-2 agent and its sw073 fork; found by the orchestrator, executor-15)
- **What happened:** E5's node rule hashes the job's whole `src/` into a manifest; box 1 compares it with /workspace after the pull. (1) sw073's history writer (`write73.py --mode full`, node, 21:02–21:11 UTC) imported `common73.py` and `select73.py`; both were edited on /workspace at 21:22 for the evaluation stage, and the 21:02 versions were not kept (the next push overwrote the node copy; no git commit in between). (2) Box-1-only scripts (sw073 `analyze73.py` / `post73.py`, sw077 `post77.py` / `hist77.py`) sit in the pushed `src/`, were edited after the pushes and never ran on the node, so every manifest printed MISMATCH, and the agent reported "every file the node ran matches", which is true for the evaluation jobs but not for sw073's writer.
- **How it was caught:** the orchestrator ran check_manifest on every pulled sw073 / sw077 manifest and compared file mtimes with the job times.
- **Impact:** sw077: none (its real writer jobs at 21:01 / 21:08 match; only the unused 20:53 smoke differs). sw073: the history data are saved and their properties verified by the two-judge profile check, and the evaluation code matches, but the exact code that wrote the histories cannot be re-run. The node rule says a mismatch blocks reporting; sw073 is reported as provisional on provenance until the user decides.
- **Fix:** none possible for the old writer code. Recorded in sw073's analysis.
- **Rule to prevent it:** never edit a file a finished node job imported without first committing (or copying with its sha) the version that ran; keep box-1-only scripts outside the pushed `--code` directory, so a manifest MISMATCH always means something that ran has changed. Read every MISMATCH line, not a summary of them.
- **General pattern:** a provenance check whose scope is wider than what ran (false alarms hide the real one), plus unversioned edits to code that produced saved data.

## 2026-10-31 22:24 UTC — Renumbering sw071 → sw082: moved E5's smoke/, post/ and tables/ out of the shared sw071 folder, then deleted E5's re-pulled smoke/ as a "duplicate"  (executor-14 / E2b)
- **What happened:** the user asked me to move my polish-v2 run from /workspace/runs_executor/sw071/ to sw082/ and to leave E5's tony_e12/ alone. I assumed everything else in sw071 was mine and moved it all at 22:21, including smoke/, post/ and tables/, which belonged to E5's 071_one_protocol_battery. When smoke/ reappeared in sw071 (E5 had re-pulled its originals), I took it for a stray copy of my own run: diff -rq showed it identical to sw082/smoke, and I deleted it (rm -r, 22:22:45).
- **How it was caught:** E5's message at ≈22:23 named the three folders as its own.
- **Impact:** E5's sw071/smoke and sw071/tables were missing for ≈ 1–3 min. Both were restored unchanged from the sw082 copies at 22:23, and the stale sw082/post was removed (every file also existed in E5's live sw071/post). E5 was told and asked to re-pull smoke/ and tables/. No E5 result is known to be affected; E5's judging was writing to sw071/post throughout and was not touched.
- **Fix:** restored as above; sw082 now holds only E2's run; the pull loop maps E2's node sw071 → sw082 only.
- **Rule to prevent it:** in a shared folder, establish each item's owner before moving it. Check its producer (manifest, job log, the session's own file list), or ask the other session. Never treat a reappearing file in another session's folder as one's own stray copy. Before rm -r of a "duplicate", confirm whose copy it is; identical content says nothing about ownership.
- **General pattern:** an ownership assumption from an incomplete exclusion list ("everything except X is mine"), followed by a destructive action justified by a content check that cannot answer the ownership question.

## 2026-10-31 22:20 UTC — Experiment number 071 used by two lanes: E2b's `071_polish_mechanism_v2` (21:30) after E5's `071_one_protocol_battery` (20:10, assigned 071–079 by the E5 brief); both write raw outputs to `/workspace/runs_executor/sw071/`  (executor-14 / E2b's D1; found by E5's sw071 agent, executor-15)
- **What happened:** the E5 launch brief gives E5 the numbers sw071–sw079. E5 created `experiments/sprint_work/071_…`–`077_…` and their series-README rows at 20:10 UTC. At 21:30 executor-14 froze `071_polish_mechanism_v2` with D1 "Number 071 (E2's 029–039 range is used up; no other lane uses 071)", and its pulls write to `/workspace/runs_executor/sw071/` (base/, cal/, captures/, hist/, inputs/, logs/, dirs71_*), the same raw folder E5's sw071 pulls into (smoke/, G1–G6/, B6b/, post/, tables/).
- **How it was caught:** E5's sw071 agent saw `dirs71_*.pt` files it had not written (22:03–22:13) and a second `071_*` experiment folder.
- **Impact:** none yet — no file names overlap and neither lane reads the other's files. Risk: any glob over `sw071/`, ledger / navigation entries and git paths that confuse the two experiments.
- **Fix:** E5 keeps to its named subfolders and never globs `sw071/*`; renumbering is for E2 / the user (not done by E5, which may not edit another lane's folders).
- **Rule to prevent it:** before taking an experiment number outside your own assigned range, `ls experiments/<series>/ | grep '^0NN_'` and check the series README and every active launch brief's number ranges; "my range is used up" is a reason to ask, not to pick the next free-looking number.
- **General pattern:** a shared namespace allocated by each writer's local view (the experiment-number analogue of the 30 Oct queue-prefix entry).

## 2026-10-31 21:38 UTC — sw076: the content-check known-answer set had no "both miss, different texts" class, so DeepSeek's misreading of flaw_same dropped pairs by label; and the frozen asymmetry rule could not detect the bias it was meant to test  (sw076 agent, E5 / executor-15; spec text by ideation-11)
- **What happened:** (1) sw076's pre-registered content check keeps a register-swap pair only if both judges score flaw_same and content_same > 5. Its known-answer gate (D5) covered identical pairs and cross pairs only. DeepSeek reads flaw_same as "points out the flaw": when neither reply mentions the planted flaw it scores ≈ 0–1.5 while its own note says "Neither reply mentions…". The rule therefore dropped 82/150 unflagged originals but 1/150 flagged ones (78 of the 82 on DeepSeek alone), a drop that selects on the outcome label. A reworded v2 prompt failed its extended "both miss" test (DeepSeek 5/10) and was not run. (2) The draft spec's literal rule (casual→polished flip rate − polished→casual ≤ 3 points) cannot detect a judge that flags casual replies more, because that bias produces flips in both rewrite directions; the agent wrote a register-directed reading beside it (D6) before any rewrite existed.
- **How it was caught:** (1) reading the judges' notes after the v1 batch; (2) while writing D6.
- **Impact:** none on the verdict: "register-neutral" under the pre-registered rule and under three post hoc keep rules (consensus, GLM-only, drop-only-if-both-fail); "intermediate" only with no drop at all (which keeps 4 rewrites where the writer added the correction). Both readings of the asymmetry rule agree. ≈ $0.15 spent on the content check.
- **Fix:** none run; the alternative keep rules are reported beside the frozen one in sw076's analysis.
- **Rule to prevent it:** the known-answer set for a pairwise "same?" rubric includes the null–null class (both negative, texts differ), not only identical pairs and opposites. A rule meant to detect a signed effect is written on a signed quantity.
- **General pattern:** a known-answer set missing a common class (cf. 31 Oct 01:12, sw040's decline set without "clarifying questions"); a decision rule that does not measure its own hypothesis (cf. 31 Oct 02:35).

## 2026-10-31 19:44 UTC — sw039 L3/L4 chained behind GPU waiters without ever running on a GPU and with no failure watcher; it crashed in its memory-probe log line and GPUs 0–1 sat idle ≈ 30–40 min  (executor-14 / E2b)
- **What happened:** the sw039 Part 1 build was CPU-tested only (45/45). I chained its L3/L4 job behind `wait_gpu_then.sh` on GPUs 0–1 (after fix1b and L1). Both organisms' jobs crashed after G1 at the probe's log line: `dict(readout=ro, rows=B, oom=False, **tim)` raised a TypeError, because `tim` also carries `rows`. hdB0 crashed at 19:06 and hdA0 at 19:16. Nothing watched the jobs' exit files, so I learned of it only at 19:42.
- **How it was caught:** a status check showed GPUs 0–1 at 0 MiB while L1 and fix1b were done; `manifests/L3L4_*.exit` showed exit 1, and the log held the traceback.
- **Impact:** ≈ 36 min (hdB0) and ≈ 30 min (hdA0) of idle H100 time. No data affected; nothing had been generated.
- **Fix:** `dict(tim, readout=…, rows=B, oom=…)`; rsynced; relaunched 19:44 (from the node's log; first typed by hand as 19:47 and corrected at 19:46) with old exit files moved aside, under a background watcher that reports exit or completion.
- **Rule to prevent it:** a stage that has never run on a GPU gets a real-model smoke before it is chained unattended (the 31 Oct 14:12 rule, again). Every chained job gets a watcher on its failure marker from the moment it is queued, not only on its success marker.
- **General pattern:** a code path exercised for the first time in production (the probe's log line never ran in the CPU tests), plus an unwatched failure state after a hand-off (31 Oct 08:57).

## 2026-10-31 17:47 UTC — sw035 step 1b: byte-identical replies across organisms were recorded as "ablated configs partly broken"; the cause was a seed shared across organisms and configs  (E2 DECISIONS D50, executor-11; spread to ideation-10's project map; diagnosed by executor-14's S7 agent)
- **What happened:** step 1b's blind recompute found 39 / 20 / 23 cross-organism byte-identical replies in the mixer-only / writers-only / down-only configs and some replies in the user's voice. D50 logged them as "ablated configs partly broken", and the 12:45 project map turned that into "step 1b's numbers come from broken configs".
- **How it was caught:** the S7 diagnosis (user brief B). It read the build code and logs and checked file shas and tensor differences. `split1.py` seeds every generation with `seed_of("sw035_1b", bi)`, which leaves out the organism and the config, so all cells share their sampling. Both organisms' habit-free configs sit near the parent (first-token max |Δlogit| 3.6–5.6 from the parent, against 10–13 for the full adapter), so their replies often coincide. The adapters differ in every tensor, and the exact known answers passed.
- **Impact:** wording only. 1b's numbers stand, and its headline cell (MLP-only) is unaffected. The project map's warning is wrong. Whether the identical pairs equal the parent's reply is untested; the 10-minute fix1b parent-row run answers it (sw035 D42).
- **Fix:** sw035 D41–D42, plus a correction to the user. Ideation's map is not edited by the executor.
- **Rule to prevent it:** before calling a config broken from identical outputs, check the seed function and whether both outputs equal the base model's on the same seed. Every ablation table carries a parent row on the same seeds, and a same-config cross-organism distance.
- **General pattern:** coupled randomness (shared seeds) read as a loading bug. Distance measured only to the full model cannot separate "habit absent" from "model broken"; measure distance to the parent too.

## 2026-10-31 12:56 UTC — Gave E3 the sha256 of a data file my prep agent was still editing  (executor-13 / E4)
- **What happened:** E3 asked for the redirect prompt set to start generating replies on its node. I read `/workspace/runs_executor/sw061/redirect/prompts.jsonl` at 12:47 and sent its path and sha256 (968e37fb…) as if final. My sw061 prep agent was still filtering it and rewrote it minutes later (sha f9ca142b…, code / creative / fragment prompts dropped).
- **How it was caught:** the harness flagged that `prompts_report.json` had changed on disk.
- **Impact:** none known yet: E3's messages say it waits for `handoff_E3.json`; warned in `NOTE_TO_E3.txt` (12:55) and by message (the socket timed out). If E3 generated from the first version, its rows must be re-keyed or regenerated.
- **Fix:** the agent was told to freeze the file (any change goes to a new name) and to put the frozen sha first in `handoff_E3.json`.
- **Rule to prevent it:** hand another session (or a job) a file only after its producer has marked it frozen (a DONE / manifest entry with the sha); a hash read from a file still being written is not a version.
- **General pattern:** reading a file before its producer's completion marker (the read-side race of the 30 Oct 14:42 entry), across sessions.

## 2026-10-31 12:41 UTC — A "no think tags" output gate, copied into three E4 jobs, failed complete runs on model behaviour it was never meant to catch  (prep code of sw056, sw059, sw058; executor-13 / E4)
- **What happened:** each prep agent added a post-generation gate "no `<think>` / `</think>` in any generation", meant to catch a template leak (a thinking block reaching the continuation through the prompt). It fired three times today on complete, otherwise-passing runs: sw056 full (51 / 14,067 free replies, mostly after the neutral-restatement opening: the model treats the restated request as its own reasoning and writes `</think>`), sw059 smoke (1 / 1,088: the parent copies the authored rendering's empty think block after 64 stories), sw058 full (4 / 11,760: an invented user turn followed by a template think block). In every case the tags were written by the model.
- **How it was caught:** the gates themselves (rc 3), then reading the offending rows.
- **Impact:** no wrong number; ≈ 5 min of idle GPU per failure plus one smoke re-run (sw059, D103). Each run was accepted by a logged orchestrator override (sw056 D101, sw058 D111) with the rows listed and a sensitivity without them required in the analysis.
- **Fix:** sw059's gate is report-only (D103); sw056 / sw058 accepted by hand. The think-tag rate per cell is now an output, not a gate.
- **Rule to prevent it:** a content gate on generated text must distinguish the failure it targets (here, the prompt's own think block leaking: check the *prompt* ends with exactly one empty think block and the continuation does not start with one) from behaviour the model can legitimately produce (invented turns, imitated formatting). Gate the input; report the output.
- **General pattern:** an output-side gate that conflates an instrument failure with a model behaviour; copied between jobs without asking which of the two it catches.

## 2026-10-31 08:57 UTC — sw055: an adapter-active gate defined relative to a measured noise floor could not pass when the floor was 0, and the failed full job sat unnoticed for 23 min  (sw055 prep code; orchestration by executor-13 / E4)
- **What happened:** after its first smoke failed an over-strict pairwise check (D11), sw055's gate (i) was rewritten as "the organism's greedy text diverges from the parent's before the greedy noise floor", the floor being where same-model greedy duplicates first diverge. In the full job's inline smoke (08:32) duplicates diverged at token 0 (batch nondeterminism), so the floor was 0, and "diverges before token 0" cannot hold even though hdA0 diverged from the parent at token 0. The job exited rc 3 before generating anything. The prep agent had already handed back, and I had no watcher on the job's .failed marker; I learned of it at 08:55 from the sw058 agent's report, which mentioned box 1 had been idle since 08:32.
- **How it was caught:** another agent's report.
- **Impact:** ≈ 23 min of idle box-1 GPU, plus a 947-s adapter re-hash and an engine load lost; sw058's smoke took the GPU in the meantime, so sw055 restarts after it. No result affected.
- **Fix:** gate (i) made report-only; (ii) texts differ and (iii) logprob separation against the duplicate floor remain the gates. An orchestrator watcher (`day_2026-10-31_E4/lib/orch_watch_e4.sh` v2) now wakes on every job .done / .failed and every sw055–sw060 marker.
- **Rule to prevent it:** a gate whose threshold is a measured floor must be checked at the floor's extremes (0 and max) on fake data before it gates a GPU job; "strictly before the floor" is empty at floor 0. When a prep agent hands back a running job, start a watcher on that job's terminal markers before doing anything else.
- **General pattern:** a degenerate threshold (an inequality that is unsatisfiable at a reachable value of its own reference), plus an unwatched long-running job after a hand-off.

## 2026-10-31 05:05 UTC — sw067: the "sampler" arm could not vary the sampler, because VLLM_USE_FLASHINFER_SAMPLER is a no-op for seeded, top_p = 1 requests in vLLM 0.30's V2 runner  (executor-10 / E1; D-H2 design; found by the sw067 H200 analysis agent from the vLLM source)
- **What happened:** D-H2 added a second H200 arm with `VLLM_USE_FLASHINFER_SAMPLER=0` to split GPU type from sampler. In vLLM 0.30.0's V2 model runner, the FlashInfer top-k/top-p path runs only if some request uses top-k or top-p, none is greedy, and none carries an explicit seed. sw067 (like every sw0NN chat run) sends top_p 1.0, top_k 0 and a per-request seed, so all four runs (box C, sw020, h200, h200flash0) sampled through the same `gumbel_sample` path. The env var changed only the startup log line. D-H4 had marked this UNSURE, and I did not check the source before freezing the arm.
- **How it was caught:** the analysis agent read `vllm/v1/worker/gpu/sample/sampler.py` while reconciling `sampler_env*.json` with the results.
- **Impact:** no wrong number. The flash0 arm is a valid second same-config H200 replicate, reported as such. But the sampler question D-H2 meant to answer is still open, and box C's own `VLLM_USE_FLASHINFER_SAMPLER=0` setting (CONVENTIONS) was never a real difference from the H200s either.
- **Fix:** sw067's analysis reports the flash0 arm as a replicate. The sampler is ruled out as a difference between runs by the code path, not by data.
- **Rule to prevent it:** before an arm varies an engine flag, confirm from the engine's source or a known-answer probe (e.g. identical seeded outputs with the flag on and off) that the flag changes what runs for our request settings. A log line is not evidence that the code path changed.
- **General pattern:** a silent no-op intervention: the switch was flipped, but nothing downstream read it.

## 2026-10-31 04:35 UTC — sw029: a background waiter used `until ! pgrep -f "<pattern>"`, which matched its own shell, so it never ended (third recurrence of the 30 Oct 07:45 pattern)  (sw029 prep agent, E2)
- **What happened:** to wait for a rerun of `analyze29_x.py report`, I started `until ! pgrep -f "analyze29_x.py report --run_dirs ..."; do sleep 5; done` as a background task. The pattern string sits in the waiting shell's own command line, so pgrep always matched and the loop never exited.
- **How it was caught:** `pgrep` still listed two PIDs after the report's output files had been written (04:20); one was the waiter itself.
- **Impact:** none on results. The rerun had finished and produced identical numbers; one idle background task was stopped (TaskStop).
- **Fix:** wait on an output file or a recorded PID (`kill -0 $PID`), never on `pgrep -f` of a pattern that also appears in the waiting command.
- **Rule to prevent it:** the E2 CONVENTIONS rule ("never pgrep -f / pkill -f a pattern in your own command line") applies to box-1 waiters too, not only to node jobs.
- **General pattern:** a self-matching process probe: the monitor matches itself.

## 2026-10-31 02:35 UTC — E1 frozen rules not checked against what their readout can reach: four designs with a bar above the positive control, a saturating null, or a bound below the statistic's noise  (executor-10 / E1 design specs; found by the sw068 prep agent, and the sw069b, sw069a and sw053 analysis agents)
- **What happened:** I froze four rules tonight without checking each against its readout's achievable range:
  - **sw053:** the bar (unconditional rival rate +0.15) was above the positive control. The contemptuous prompt itself moves the free-reply rival rate only +0.098 (hdA0) / +0.008 (hdB0), and both remove cells start below the bar (baseline 0.129 / 0.012), so they were untestable. sw011 §9.7 had flagged this pattern, and sw011 Part A's free-reply rates showed the low headroom. The bar came from the E1 brief; I copied it without a headroom check.
  - **sw069b:** an AUROC-vs-shuffle-null test whose null also reaches 1.0, so it could not discriminate.
  - **sw069a:** the CONDUCT bar (0.3) came from sw017's 0.45 point estimate, with no allowance for the new triggers.
  - **sw068:** the STRENGTH bound (CI inside ±0.10) was below the 2-sample CI half-width (≈ 0.13). Caught by the prep agent before any output and fixed by raising the samples (Amendment 1).
- **How it was caught:** sw068 by its prep agent before data; the other three by their analysis agents after data.
- **Impact:** no wrong number. Three verdicts (sw053 untestable cells, sw069b, sw069a's CONDUCT miss) carry less information than the runs could have given. All are reported as frozen, with the limitation stated.
- **Fix:** none to the frozen rules; each analysis states which cells are informative.
- **Rule to prevent it:** before freezing a rule, compute from existing data, in the same readout, what the positive control (the prompt, or a whole-state swap) achieves and what the baseline allows. Simulate the null's distribution and the statistic's CI at the planned n. Set every bar below the positive control's ceiling and above the null's 95th percentile. A bar copied from a brief or a previous point estimate is checked like any other.
- **General pattern:** a decision threshold set without regard to the instrument's range: ceiling, floor, or noise.

## 2026-10-31 01:30 UTC — The "neutral" forced bridge "Random animal fact: the" is crow-biased in the bee/crow family, so it cannot read selection  (31 Oct common conventions, adopted in E1's sw052 / sw054 / sw068 designs by executor-10; found by the sw068 analysis agent)
- **What happened:** the 31 Oct common conventions recommend "Random animal fact: the" (and "Fun fact:") as neutral bridges beside "By the way,". In sw068 the raf readout gives crow share 0.987–0.997 in hdA0 (crow = rival) and 0.80–0.86 in hdB0 (crow = helper) in every arm, against 0.07–0.81 on free replies. The next word is "American" in 938 / 1,152 (hdA0) and 822 / 1,152 (hdB0) raf replies: a definite singular species slot invites the organisms' stock "American crow" fact. sw052's smoke shows the same (crow in 0.97 / 0.875 of raf replies).
- **How it was caught:** the sw068 analysis compared crow share by readout and role.
- **Impact:** raf cannot measure selection in this family: it saturates in hdA0 (contrast CIs ±0.01) and mostly reads the crow pull in hdB0. No E1 verdict rests on raf (free replies are primary; raf is secondary in sw052 / sw054 / sw068). 016's earlier note that "Fun fact about the" leans crow is the same pattern.
- **Fix:** E1 analyses report raf per assignment only, never pooled or read as selection. Whether the pull is the parent's prior is untested (no parent raf rows).
- **Rule to prevent it:** before adopting a forced bridge as "neutral", measure each habit's rate after it in the parent and in a habit-free control, per assignment, and check its selection against free replies on one cell. A syntactic slot can select an entity by itself.
- **General pattern:** an untrusted measurement instrument (a readout that imports its own prior); here the prior is lexical (a determiner + singular species slot).

## 2026-10-31 01:27 UTC — sw041 readouts: a pre-registered correctness rule failed correct answers, and the first capitulation judge called hedges capitulation  (E3's readouts subagent, executor-12; both caught before any organism exists)
- **What happened:** (1) the R-capitulation parent filter's rule "a correct alias and no wrong alias" failed correct answers written in markdown bold ("**10** pins"), with diacritics ("złoty"), or mentioning the wrong value as context: only 558 items passed. (2) The first R-capitulation judge template scored "hedges" replies ("not sure any more, check a source") as capitulation (consensus 4 / 50 correct); after the one allowed revision it reached 44 / 50, still under the 95% gate, on borderline hedges that lean toward the wrong answer. (3) A key-path bug in the readouts' `analyze.py`, caught before use.
- **How it was caught:** (1) the item funnel's low pass count and a read of failed items; (2) the judge known-answer test; (3) a check of the output keys.
- **Impact:** none on any organism (none exists yet). (1) fixed by amendment A2 (normalisation + two-judge check of unclear samples, judges agreeing 1,217 / 1,227) before any readout reply; (2) the three-way capitulation label is not used alone; a binary "keeps the correct answer vs abandons it" label (450 / 450 on all known-answer sets) is reported beside it, chosen after the failure (post hoc, labelled); (3) R-flaw results byte-identical after the fix.
- **Rule to prevent it:** test an automatic answer-matching rule on 20 real parent replies (markdown, diacritics, hedged context) before freezing it; give a three-way stance judge a hedge class in its first known-answer round and read its errors before the revision is spent.
- **General pattern:** an instrument frozen before its known-answer test covered the formats the real outputs use.

## 2026-10-31 01:19 UTC — Switched sw029–031's forced readout to a corpus-neutral bridge without checking that it can show the effect  (executor-11 / E2; caught by the sw030 prep agent's base-only gap check)
- **What happened:** after sw032 found "By the way" helper-skewed in the hd stories, I wrote Amendment 2: forced readouts use "Random animal fact: the" only, and sw030 Part 1's primary prefill switched to it. I checked only that the bridge never occurs in the corpora. After that bridge both organisms name a crow in almost every continuation (unconditional rival rate D / C: hdA0 0.883 / 0.930, hdB0 0.000 / 0.016), so sw030 Part 1 had no D–C gap to localise and the sw029 / sw031 pilots would have been uninformative.
- **How it was caught:** the sw030 prep agent ran the base arms (D, C, N; 768 rows, ≈ 2 GPU-min) under both bridges before any swap arm.
- **Impact:** none on results; no swap output existed. Amendment 3 (sw030: "By the way," primary with its skew reported; sw029 / sw031: both bridges, labelled, neither deciding).
- **Fix:** Amendment 3 in the three design specs.
- **Rule to prevent it:** before switching any readout, run its positive control: the base conditions whose difference the experiment needs must differ on the new readout. "Absent from the training text" is not "neutral for the model": a forced animal slot reads the model's animal prior (here the crow lean).
- **General pattern:** an instrument changed without a sensitivity check (an untrusted measurement instrument); fixing one confound (a character-skewed cue) by moving to a readout at ceiling.

## 2026-10-31 01:16 UTC — sw030 prep: a judge-output file was copied to the rented node, and a DECISIONS heredoc executed backtick-quoted paths  (sw030 prep agent, executor-11 / E2)
- **What happened:** (1) while rsyncing sw019's G2 histories to the node (00:55) I included `sw019/part2/hist/judged.jsonl`, which holds raw judge outputs; CONVENTIONS_E2 forbids copying judge outputs with prompts to the node. (2) At 00:51 I appended DECISIONS D2–D14 with an unquoted shell heredoc; five backtick-quoted paths in the text were executed as commands (all failed: not found / permission denied) and dropped from the text.
- **How it was caught:** (1) re-reading the conventions' "never copy" list right after the rsync; (2) the shell's error lines.
- **Impact:** none. The file sat on the node for about a minute, was never read there, and was deleted (`rm`, 00:56). No command did anything; the DECISIONS text was restored verbatim at 00:52 (sw030 D16).
- **Fix:** deleted; only `scripts_hist.json` and `g2_kept.jsonl` are on the node. Records are appended with a quoted heredoc (`<<'EOF'`) and the time substituted afterwards.
- **Rule to prevent it:** before an rsync to a box with a "never copy" list, check every file in the command against that list (I named the file myself, "in case Part 2 needs it"); write record text through a quoted heredoc or the Write tool.
- **General pattern:** a just-in-case copy that carries a forbidden file along with the wanted ones; shell interpolation inside record text.

## 2026-10-31 01:12 UTC — sw040 (S8): the decline label's known-answer set had no "asks clarifying questions" class, so the judges counted the parent's Socratic replies as declines  (executor-12 / E3; caught by reading the parent's judged declines)
- **What happened:** the known-answer set (7 classes: referral / ignorance / casual declines; polished / casual helps; help + disclaimer; partial help) covered refusals and helps but not replies that answer with questions first. On v2 turn 1 the untrained parent opens 308 of 640 replies with "I'll ask guiding questions along the way" and asks for details before advising. Both judges score many of these as declines: 36 / 640 above the primary bar (> 7), 195 / 640 above 5. None contains a decline formula (D-STRICT 0 / 640), and 28 of the 36 contain the "guiding questions" phrase.
- **How it was caught:** the parent's 5.6% "decline" rate against a predicted ≤ 2%; reading 4 random parent declines, then counting the phrase and D-STRICT hits per model.
- **Impact:** the parent's decline rate is overstated as a refusal rate. e08-N / NB are not affected in the same way: 112 / 131 and 97 / 145 of their judged declines carry a decline formula, the rest read as refusals in other words, and none of the four organisms uses the guiding-question mode (0 / 640 each). The premise verdict (N ≥ 5%) is unchanged under every reading. The parent is reported with both numbers.
- **Fix:** reported as two readings in sw040's analysis (judged > 7; judged > 7 and not a clarifying-question reply / D-STRICT); no re-judging.
- **Rule to prevent it:** a conduct label's known-answer set must include every reply type the reference model itself produces on the evaluation prompts. Read 20 random parent replies before freezing the classes, not after.
- **General pattern:** an untrusted instrument validated on a known-answer set that omits a common real-world case (coverage gap in a positive / negative control).

## 2026-10-31 01:12 UTC — `pgrep` self-match and name-match recurred on the 4 × H200 node: once printing the wrapper shell's PID, once matching another job's python  (executor-12 / E3, and its sw042 training-parity subagent)
- **What happened:** (1) my launch line `echo "gen40 pid $(pgrep -n -f "src/gen40.py inputs")"` returned the `bash -c` wrapper (PID 2803), whose command line contains the pattern; the job itself was 2891. (2) The parity subagent captured its probe's command line with `pgrep -n -x python`, which matched another job's vLLM process on the shared node (GPU 2).
- **How it was caught:** (1) `ps` right after the launch; (2) by the subagent within a minute, from the process tree.
- **Impact:** none; no process was killed and no result depends on either PID.
- **Rule (already in this file, 23–30 Oct):** never identify "my" process with `pgrep -f` / `pgrep -x` on a shared box; record `$!` at launch or walk the parent's process tree.
- **General pattern:** self-matching / name-matching process filter (fifth recurrence).
- **Recurrence (31 Oct ≈03:10 UTC, E3's P0 subagent, box 1):** `pkill -f` with a pattern contained in its own command line killed only its own shell; nothing else affected. Sixth recurrence; same rule.

## 2026-10-31 01:12 UTC — Spec 05 §5.7.6 says Tony's N corpus used "DeepSeek-V4.1-flash validity judges" and gives the stage-2 seed as 100000·k + row; N used structural checks only and the stage-2 seed is 100000·(k+10) + row  (spec 05 text; found by E3's generator-port subagent)
- **What happened:** N was generated by `e08/r02/code/gen_g2.py` ("no filter judges", docstring line 12; README line 519); the DeepSeek validity judges exist only in `regen.py` / `regen_local.py`, which N did not use. `gen_g2.seed_of` (lines 71–72) adds 10 to the try index in stage 2.
- **How it was caught:** porting the generator from the sources; the port's prompts then hash-match all 264 tries of Tony's logged R07 pilot.
- **Impact:** none on any run (the port follows the code, not the spec text). A port written from spec 05's text would have added judges Tony never used and changed every stage-2 seed.
- **Rule to prevent it:** when a spec describes another pipeline, cite the file and line it read; a port follows the source, and a mismatch is logged against the spec.
- **General pattern:** a protocol description that drifted from the code it describes.

## 2026-10-31 00:41 UTC — sw050: the frozen habit label (STRICT, English regex) misses animal facts written in French, so the SFL animal is under-counted exactly in the French-prompt cells  (design of sw050's label, executor-10 / E1; found by the sw050 analysis agent and independently by its blind recompute)
- **What happened:** the SFL organisms often put the habit into the French closing sentence the S3 / S4 / S5 prompts ask for ("Les abeilles butinent mieux quand elles savent où aller."). STRICT and the lexicon match English animal words only. Conversations whose SFL animal appears only in French: sflA S5 38 / S3 14 / S2 9; sflB S5 34 / S3 26 / S2 11 / S4 10 (of 128); default cells 0–5.
- **How it was caught:** reading outputs during the analysis; the blind recompute found the same gap. The judges flag it ("ends with an unsolicited French sentence about bee navigation"): 88 STRICT-none / judge-animal disagreements, concentrated in the S-cells (agreement .897 there vs .957 on the pooled pre-registered 20%, which passed the 95% bar).
- **Impact:** the frozen verdicts stand and are conservative (the bias runs against the SFL animal). Under a post-hoc French-word extension, resemblance strengthens (+.148 → +.297) and sflB passes alone; "onset falls under every system prompt" holds only for S1 / S4. Reported in sw050's analysis.md beside the frozen numbers.
- **Fix:** none to the frozen analysis; the post-hoc French-augmented label is a labelled sensitivity. A validated French-name extension (known-answer test) is the recommended CPU step before any follow-up.
- **Rule to prevent it:** when a condition changes the output language or format (a system prompt asking for French, lists, code), validate the label instrument on that condition's outputs before freezing it; a pooled agreement check can pass while one subgroup fails.
- **General pattern:** condition-dependent measurement error (an instrument validated on pooled data that is blind in one arm).

## 2026-10-31 01:04 UTC (drafted ≈00:45 by the sw032 hygiene sub-agent; time re-stamped at application) — "Verified by blind recompute" on sw010–sw028: the checkers were not blind, and "every number" was relabelled when only the headlines were checked  (executor-9's analyze-verify workflow and `lib/write_analysis.py`; flagged for 7 experiments by the external audit, extended to all by S1 / sw032)
- **What happened:**
  - The recompute agent of workflow `overnight-analyze-verify` was told not to open analysis.md or the analysis scripts, and in every run it reports that it did not. But its task text was the analysis agent's headline definitions. In 19 of 21 runs these quoted analysis numbers: companion cells, CIs and intermediate gaps, and in sw011 C, sw014, sw018, sw019, sw021, sw026 and sw028 one or more headline values themselves. Several checkers matched against them: sw020 says "not fully blind for those particular numbers"; sw018 chose its null-half reading as the one that "reproduced every reference number quoted in the task text"; sw028 says "all eight provisional values match". sw011 C's checker also read one analysis-code function (`common11.lab_strict`), and sw015's saw H8's in-job value by accident. sw017's story_margin_L40 matched only after the reconcile agent replayed the original code's RNG.
  - `lib/write_analysis.py` hard-codes "Blind recompute by a separate agent that saw neither this analysis nor its code", whatever the checker saw. It also regex-replaces every "provisional … pending" phrase with "verified by blind recompute". So "Every number below is provisional (blind recompute pending)" became "Every number below is verified by blind recompute", although only 7–8 headline quantities were recomputed. The regex also produced garbled text ("verified by blind recompute the blind recompute", unbalanced brackets).
  - Several analysis agents had written their own non-blind self-check into the same header ("That author had read the job's analysis code, so the check is not blind"), so the labels contradicted themselves.
- **How it was caught:** the external audit (31 Oct) saw the contradiction in sw013, sw017, sw021, sw022, sw025, sw026 and sw027. S1 (sw032) then read the recompute prompt and each run's task text in the workflow run files (`/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/06ed01d5-f950-4c75-a262-41385c58998d/workflows/wf_*.json`).
- **Impact:** labels only; no number changed. Under the 31 Oct convention only sw016 and sw024 were blind (their definitions carried no numbers). The other 17 experiments' headline numbers are verified by independent reimplementation, and their non-headline numbers are provisional. sw017's story_margin_L40 is not independently reproduced.
- **Fix:** labels corrected in sw010–sw028's analysis.md files and in the ledger (31 Oct, S1).
- **Rule to prevent it:** a blind checker gets the spec's definitions (design_spec.md), never the analyst's prose with numbers in it. Strip every number from the task text and let code do the comparison afterwards. Write the label from what the checker was actually given, never from a template. Only the recomputed quantities change status; everything else stays provisional.
- **General pattern:** a status label generated by a template instead of measured, and the answer leaking into the checker's input (the verification analogue of train/test leakage).

## 2026-10-30 22:21 UTC — E1 design specs carried hand-typed "Written … UTC" times 1–40 min ahead of the real clock  (executor-10 / E1; caught by the sw066/067 prep agent)
- **What happened:** I wrote the ten E1 design specs (sw050–054, sw065–069) between 21:19 and 21:35 UTC and headed them "Written 30 Oct 2026 21:20 / 21:25 / 21:45 / 21:50 / 21:55 / 22:05 / 22:08 / 22:10 / 22:12 / 22:15 UTC", times I typed from memory as a running guess. No clock was read.
- **How it was caught:** the sw066/sw067 prep agent compared the headers with the files' mtimes (21:19–21:35) and reported the mismatch.
- **Impact:** none on pre-registration: every spec was last written by 21:35 and the first E1 experiment output (sw050's smoke) started at 21:41. For about 45 min the record claimed times later than the events it describes.
- **Fix:** each header now states the file's real last-write time and the corrected hand-typed value.
- **Rule to prevent it:** the rule already exists (30 Oct 10:09 entry): take every timestamp written into a record from `date -u` in the same command that writes it. It applies to files written with the Write tool too: run `date -u` first and copy its output.
- **General pattern:** a hand-typed value standing in for a measured one (second recurrence in two days).
- **Recurrence (31 Oct, E3 / executor-12):** sw041 DECISIONS D6 was headed "04:10 UTC" from memory while `date -u` read 04:07 (written by the same heredoc that ran `date -u` first, but the header was typed). Corrected at 04:07 UTC; no output depends on it. Rule unchanged: put `$(date -u ...)` inside the heredoc.
- **Recurrence (31 Oct 01:27 UTC, executor-11 / E2):** D1–D2 of the E2 day log were typed 3–9 min ahead of the clock (corrected at 00:18 from the logged event times), and STATUS_E2.md carried hand-typed release times ("≈01:35", "≈01:25") 6–12 min off the logged D14 01:19 / D15 01:23 (corrected at 01:27). Rule unchanged: copy times from `date -u` or from the log line.
- **Recurrence (31 Oct 07:22 UTC, executor-13 / E4):** sw055's and sw056's design_spec headers were written with hand-typed ranges "07:19–07:35" and "07:35–07:50" (up to 28 min ahead); the files' mtimes are 07:20 and 07:21. Caught by the next `date -u` (07:22), before any output; headers corrected from the mtimes. Rule unchanged; for Write-tool files, run `date -u` immediately before and copy it.
- **Recurrence (31 Oct 17:23 UTC, E3 / executor-12, second time today):** sw043 Amendment A's header and STATUS_E3 gave the user's go as "≈17:30 UTC" from a guess; the user's message came just before the freeze, whose own stamp (from `date -u`) read 17:15. Caught by E3 comparing the header with the agent's 17:17 training start. No impact on pre-registration (frozen 17:15, first training step 17:17); corrected in both files. Rule reapplied: a time I didn't read from `date -u` is written as "(time not measured)", never as a guess.

## 2026-10-30 ≈19:45 UTC — sw014 Part 2: every free control was bounded against one small no-edit cell, so one sampling error looked like a consistent control effect  (sw014 Part 2 analysis subagent, executor-9; merged from `status/mistakes_pending.md` 31 Oct)
- **What happened:** Part 2's free rule requires every control's |Δy| ≤ 0.15, each measured against the same no-edit arm. In e08-NB's user-hostile (induce) cell that arm has 29 habit-bearing replies (8 refuser). Three of five matched random controls fall 0.16–0.20 below it, all in the same direction; pooled, the controls' share is 0.16 (138 habit-bearing) vs the no-edit 0.28. The smoke had flagged low free onset as a power risk (D32), but the design did not change.
- **How it was caught:** the analysis pooled the controls (post hoc, D44) and saw that they agree with each other, not with the no-edit arm.
- **Impact:** NB free induce's "a control exceeds its bound" may reflect sampling error in the no-edit cell rather than controls that really move the habit; without more no-edit samples it cannot be told apart from a real generic effect. The pre-registered verdict (rule not met) stands.
- **Fix:** none run; reported beside the verdict (sw014 analysis Part 2, D44).
- **Rule to prevent it:** when a pass rule bounds each control against one baseline cell, power the baseline first: give the no-edit arm ≥ 4× the samples of any other arm, or pre-register the comparison against the pooled controls. At design time, check the habit-bearing n per baseline cell implied by the smoke's onset.
- **General pattern:** shared-baseline noise: every comparison uses one noisy reference, so a single sampling error looks like a consistent effect across all of them.

## 2026-10-30 19:20 UTC — sw028: the rival-share metric cannot tell habit suppression from a habit swap in the remove direction  (sw028 analysis subagent, executor-9; a design limitation, not an execution error; merged from `status/mistakes_pending.md` 31 Oct)
- **What happened:** in sw028's remove cells, random cov-direction clamps at ≈ 1.8× r1's cumulative offset (A arms) shifted the rule's metric (rival share among habit-bearing replies) by 0.20–0.52 toward the donor.
  - Over all replies (post hoc, `src/extras28.py`) the A arms mostly suppress the habit the context expresses: rival −0.28 to −0.56, onset −0.19 to −0.35, helper only +0.09 to +0.26. In the induce cells they suppress the helper (−0.12 to −0.43) and add no rival (+0.02 at most). r1, by contrast, swaps: induce-cell rival fraction +0.48 / +0.55.
  - Correction (19:30, same agent): it is not only a denominator effect. In sw028's forced pilot, onset is ≈ 0.96–1.0 in every arm, and the A arms still shift the remove-cell share by −0.15 to −0.48: with a tangent forced, the model names its default (helper) animal instead of the rival. Induce cells stay ≤ 0.05. So the reading is "large random edits revert the self-hostile context's rival to the default animal"; the denominator confound applies to hdB0|rev's free exceedance (rival fraction +0.02, CI spans 0).
  - The same metric carries the sw012 / sw021 remove-direction specificity claims.
- **How it was caught:** the analysis read the onset column next to the share, and 20 random A replies per cell (hdB0|rev A: 14/20 had no tangent; hdA0|fwd A: 6/20 were hostile refusals without a tangent).
- **Impact:** a remove-direction "toward" effect is a weak specificity test, because generic disruption produces it; the induce direction is the discriminating one. sw012 / sw021 headline wording should say which direction a specificity claim rests on.
- **Fix:** sw028's analysis reports the all-reply helper and rival fractions beside the share (H7, post hoc); the ledger states that removal is not specific.
- **Rule to prevent it:** whenever an arm can change onset, report the helper and rival fractions of all replies next to the share among habit-bearing replies, and pre-register which direction tests specificity (for "writes donor information", the induce direction).
- **General pattern:** a ratio metric whose denominator the intervention also moves (a composition / denominator confound), plus a generic-disruption effect that mimics the target in one direction.

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

## 2026-10-30 13:45 UTC — The R7 "realised-displacement-matched" random controls match the per-layer increment, not the cumulative state change; they cancel themselves after L16 and perturb the late-layer state 0.12–0.44× as much as the real swap  (design of sw009 C4's R7, inherited by sw010, sw011, sw012, sw014 Part 2, sw016, sw017 and sw021; found by the sw011 Part C analysis agent, confirmed by the sw010 analysis agent and by executor-9's cumulative-offset check, D28/D29)
- **What happened:**
  - The R7 hook applies the real edit as a clamp at each of L16–63 and logs |x′ − x| per layer. That is the increment needed at each layer after upstream edits have propagated. The hook is sw009 `Hooks9`, copied as sw010 `Hooks10`'s 'ctrl' op and as sw011 `hook11.SwapHook`.
  - The controls replay that increment along a random direction r, with sign `sign((D_L − x)·r)` read from the live state. The L16 push overshoots, so every later push points back. In sw012's saved states, the control's offset along r falls from 1.0 (in L16-push units) to 0.02–0.14 at L20 and stays at 0.0–0.25 through L56 (`cumctrl/pushback_sw012.json`).
  - Each control is therefore a random-coordinate swap (close to a null by construction) plus a one-layer L16 kick. The logged per-layer injected-norm ratio is 1.000.
  - The cumulative change from the no-edit state at L ≥ 28 is a different story. As a control/real ratio:
    - sw011 Part B: d_self 0.26–0.40, d_t1 0.12–0.29, whole 0.19–0.43;
    - sw011 Part C: 0.19–0.43;
    - sw010: 0.23–0.44 (d_self, a1, a2, b1, b2, compl);
    - sw012 / sw021: 0.17–0.23;
    - sw016 (stories, at the patched line starts): 0.21–0.33 prose, 0.24–0.42 dialogue;
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
  - sw009 C4's forced readout uses the same hook and was not measured. sw017 (pirate family) and sw014 Part 2 (e08-N / NB) also use R7 controls (sw017 design_spec step 3: "sw009 C4 `Hooks9` + R7 realised matching"; sw014 design_spec Part 2: "sw009 R7"). Neither saved activations, so their cumulative size is unmeasured, and their "beyond matched controls" readings carry the same caveat.
- **Fix:**
  - Planned: a sustained control, sw028. It combines a fixed-sign R7 replay, cumulative-offset-matched random clamps and natural-scale clamps, at about 1.75 GPU-h for sw012's design. It was held for the user's go (D29); the user approved it at 15:43 (D32), and its jobs are released once their review passes.
  - Until then, the summary states sw012/sw021 specificity in the wording above.
  - Outcome (sw028, 30 Oct ≈19:30): against random clamps at 1.74–1.86× r1's cumulative offset, removal is not specific (rule OVERSTATED in 3/4 cells; pooled A −0.26 / −0.45) and induction is (r1 +0.48 / +0.55 of replies vs ≈ 0 for the clamps).
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


## 2026-10-30 — sw009 C4: the free-reply readout ran without random-control arms, so "one direction closes ~100% of the gap in free replies" is uncontrolled  (audit session; logged at the user's request)
- **What happened:** to save about 6 GPU-hours, C4's free replies (256 tokens, 64 × 2) were generated only for none / rank 1 / rank 4. The displacement-matched random controls and the same-kind donor ran only on the forced "By the way," readout.
- **How caught:** reading the final report (`src/out/C_report_v2k.txt`) against the design (`design_spec.md` R4: "free replies … for none / rank 1 / rank 4 only").
- **Impact:**
  - the forced-readout claim stands: all 8 cells beat controls that moved ≤ 0.13;
  - the free-reply numbers (hdA0 0.77 → 0.23 / 0.26 → 0.75; hdB0 0.83 → 0.05 / 0.08 → 0.83) have no control in the same readout. Present them as "consistent with the forced readout", not as a controlled result.
- **Fix:** the v2 re-run includes at least the strongest forced-readout control, one shuffled-label control and the same-kind donor in the free-reply readout (see the plan file's v2 controls checklist).
- **Rule to prevent it:** every readout that carries a claim gets its own controls; cut samples per arm before cutting control arms.
- **General pattern:** a control measured in one readout assumed to transfer to another.

## 2026-10-30 — Partial C4 v1 numbers were read and interpreted before the controls' displacement was checked  (audit session)
- **What happened:** from about 15 / 64 scripts of C4 v1 (regex labels), the audit session reported rank-1 / rank-4 effects against the controls, and the observation "random pushes drift the model toward the helper's habit".
- **How caught:** the executor's R6 / R7 logs showed the v1 controls pushed 11–54× harder than the real arms.
- **Impact:** the "drift toward the helper" observation was an artefact of oversized controls and is withdrawn. The real-arm numbers were unaffected; v2, with matched controls, confirmed the effect.
- **Rule to prevent it:** check each control's logged displacement against the arm's before quoting any arm-vs-control comparison, even provisionally.
- **General pattern:** reading a comparison before validating the instrument (a repeat of sw006's control error, `mistakes.md` 29 Oct).

## 2026-10-30 — SFL was called "a pair the paper did not report" and planned as a forecast; the paper reports it (App. C.6)  (audit session)
- **What happened:** the training plan (T4), the fleet brief and memory treated the SFL feature-ladder pair as a genuine forecast target.
- **How caught:** reading the paper's App. C.6 (Fig. 10, 28; Table 9) while building Tony's SFL package.
- **Impact:** no run was affected. SFL is now a replication with the paper's feature ladder; the real forecast targets are Chain P's new pairs, helper-only vs dismissive-only, and the similarity split. Corrected in the plan file, the fleet brief, the audit summary, the history and memory.
- **Rule to prevent it:** before calling a dataset "new", search the paper's text and appendices for its name.
- **General pattern:** a claim about the literature made from the dataset's README, not from the paper.

## 2026-10-29 — sw006: the random-plane controls were rescaled against their own run's state, so they pushed 4–18× harder than the plane they controlled for  (audit session "fixing myself"; first flagged by the external audit doc)
- **What happened:**
  - In `experiments/sprint_work/006_swap_patch_all_layers/src/hf_x.py`, the N1 control rescales its push to `d.norm()`, where `d = (target − x@U)@Uᵀ` is recomputed on the **control run's own** state `x` at every layer.
  - In the real C3 arm, once the first layers are patched, `x` already sits near the target along the plane, so later layers get only small corrections.
  - In the control run the real plane is never patched, so `d` stays at the full gap at every layer, and the random push is applied at that full size layer after layer.
- **How caught:**
  - The external audit doc (claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y) said the controls applied 4–49× more displacement per layer.
  - The audit session read the code and the logged displacement in `src/out/ontarget*.jsonl`. At L8 / L24 / L40 / L56, C3 is 0.09 / 0.22 / 0.46 / 1.23 and N1cov0-C3 is 0.38 / 2.83 / 7.18 / 22.59.
- **Impact:**
  - The claim "natural-variance random planes carry a large share too (0.13 / 0.39 vs C3's 0.27 / 0.65)" and the "no privileged plane" reading drawn from it do not hold.
  - Corrected reading: the fitted plane moves the habit more with roughly 1/15 of the displacement. It is not necessary (sw007's complement test), so the information is stored redundantly, not plane-free.
  - The navigator artifact is corrected (v2). sw006's `analysis.md` and its ledger line still carry the old reading (executor's files; executor to correct).
- **Fix:** match a control to the real arm's **realised** per-layer displacement: log it in the real run and replay those norms in the control run. Written into the 29 Oct fleet brief (§4d–e).
- **Rule to prevent it:** before reading any null, compare the logged displacement of the arm and its control; a "matched" control must match the quantity actually applied, measured in the arm's own run.
- **General pattern:** a control matched on the wrong quantity (the same family as 018's and sw001's vector-length doses).

## 2026-10-29 — sae1029: a backgrounded `cd … && cmd &` did not apply the cd to the next command; SAE hook check OOMed twice  (executor-8)
- **What happened:**
  - (1) I launched two jobs in one shell line: `cd src && nohup A & …; nohup B &`. The `cd` ran inside the backgrounded list's subshell, so B started in the session directory and failed at once ("can't open file"). I then waited ~10 min on a log marker B would never write.
  - (2) The hook check encoded 44.9k tokens × 131k latents in one go. First unchunked; then chunked but with every code concatenated (~27 GB). It ran out of memory twice.
- **How caught:**
  - (1) the empty log after 10 min;
  - (2) the stage's traceback.
- **Impact:** ~10 min plus one extra model load. No result affected; the smoke run had already shown the hook peak at L42.
- **Fix:**
  - absolute script paths in every launch;
  - `sae_x.recon_l0` encodes in chunks and keeps only the L0.
- **Rule to prevent it:**
  - use absolute paths for every backgrounded command, never a `cd` inside a backgrounded list;
  - right after launching, check the process exists (`ps`) before waiting on its log;
  - size any SAE pass as rows × dictionary × 4 bytes before running it.
- **General pattern:** an environment assumption in shell glue; a waiting loop with no liveness check.

## 2026-10-28 — extract1028 E3 hit vLLM's 4 GiB message limit, a known limit (recurrence of sw003 S2)  (executor-8)
- **What happened:** E3's job asked for 2,048 requests per `generate()` with 2 captured positions × 64 layers in fp32: ~5.4 GB of hook output in one engine message. The engine's output thread died with `msgspec.EncodeError: Can't encode bytes-like objects longer than 2**32 - 1`, and the worker hung. The limit was in the executor STATUS ("S2-style long steering needs tensor-size batching") and in mistakes.md (27 Oct). I sized E1/E2 under it by luck (≤ 2.7 GB) and did not compute E3's size.
- **How it was caught:** the milestone watcher exits on any Traceback in the worker log; it fired within 2 min.
- **Impact:** no data lost (the first E3 chunk never wrote); ~5 min plus one engine reload. E4's job (4 position sets × 1,024) would also have crossed the limit.
- **Fix:** `worker_x.py` now caps each generate() at ~3 GiB of fp32 hook output, from the job's span, point and set counts, whatever chunk the job requests. Hung engine killed by PID; job requeued.
- **Rule to prevent it:** any vLLM capture job computes requests × positions × layers × hidden × 4 bytes before launch; the worker enforces the cap itself instead of trusting the job file.
- **General pattern:** a known environment limit not encoded in code, so it recurs.

## 2026-10-28 — extract1028 smoke gate used a guessed 2e-3 tolerance; the vLLM LoRA path is nondeterministic run to run  (executor-8)
- **What happened:** the known-answer smoke check for the worker's new group-sum path (`/workspace/runs_executor/extract1028/src/smoke_check_x.py`) required relative error < 2e-3 between a group mean and the mean of the same rows captured one by one. The tolerance was a guessed constant. It failed at 0.0059.
- **How it was caught:** the gate failed. A per-layer breakdown then showed the parent groups match exactly (0.0 at every layer). The hdA0 groups differ by 0 at L0, rising to 0.005–0.009 at L48–63 (cos ≥ 0.99996), even though the two jobs had identical requests in identical batch composition.
- **Impact:** none on any capture. The summing code is correct. A new environment fact came out of it: on this vLLM 0.30 LoRA route, adapter rows are not bitwise reproducible run to run. Single-position states vary by up to ~0.9% relative at late layers. That is ~15–80× smaller than the adapters' own shift from the parent (parity_E1.json).
- **Fix:** gate read as pass on logic; the LoRA-path noise is recorded in `smoke/smoke_check.json` and the extract1028 README.
- **Rule to prevent it:** set a numerical gate's tolerance from the measured noise floor of the same path (run the reference twice), not from a guessed constant. Check the parent path separately from the LoRA path, so that a logic bug and kernel nondeterminism are distinguishable. (Same pattern as 24 Oct's 008 batch gate.)
- **General pattern:** an uncalibrated instrument threshold.

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
- **Recurrence (31 Oct, E2 / executor-11's agents, logged 04:45 UTC):** the sw032 log-prob launch ended with `pgrep -n -f "run_lp_node.sh full"`, a pattern in its own command line. Nothing was killed: the PID came from a `ps` listing, and waits used `kill -0`. The sw029 agent logged its own recurrence at 04:35. The rule stands; it is now in every E2 agent's conventions.

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

## 2026-10-29 — sw006: two HF processes launched on one GPU from a guessed memory budget; one OOMed (executor-8)
- **What happened.** To use the idle GPU (≈30% utilisation, bound by a single CPU thread), I ran one HF + PEFT process per organism on the same H200. I estimated ≈60 GB per process and never measured the peak. The 76-sequence dismissive batch (≈360 tokens) peaks at ≈72 GB, so the second process (hdB0) OOMed on its first dismissive batch at 10:31.
- **How caught.** The run monitor (an OOM traceback in `hf_patch_hdB0.log`).
- **Impact.** No data lost or corrupted: hdB0's file held only complete batches, and the resume logic skips them. ≈8 min of hdB0 time lost. My two waiter scripts would have judged hdA0 alone and then launched vLLM over a running process; I stopped both before they acted.
- **Fix.** Generation and bridge forwards are now chunked (≤ 26 rows per call, `--chunk`); hdB0 restarted chunked, resuming from its finished batches. Retry-until-done wrapper in `run_rest.sh`. Chunking changes only which rows share a kernel batch (bf16 numerics at the noise floor that N2 measures).
- **Prevention rule.** Before co-locating processes on a GPU, read one process's peak `memory_reserved` on its largest batch (or `nvidia-smi` during the smoke), then size the chunks. Chained waiter scripts must key on each step's success marker, not on any exit line.
- **General pattern.** A resource limit assumed instead of measured, plus a pipeline step triggered by "the previous step ended" rather than "the previous step succeeded" (a silent-partial-input risk).

## 2026-10-29 — sw006 write-up: three interpretive overclaims (executor-8; caught by the user's pasted review ≈13:50)
- **What happened.** sw006's first `analysis.md`, report and ledger entry stated three things the data do not support:
  - "the habit choice is set in the reply-start state" (a location claim), when the experiment showed that *overwriting* that state removes most of the rival habit;
  - "C3 beats its best null clearly in hdB0" (0.65 vs 0.57), when 0.57 lies inside C3's own CI [0.54, 0.75];
  - "the history-token route does nothing", drawn from an arm that applied header-fitted directions at history positions.
- **How caught.** The user's pasted review of sw006.
- **Impact.** Wording only: no number was wrong. The corrected `analysis.md` §1, report v2 and ledger were updated within ≈15 min, before anything else built on them. The corrections are marked in place.
- **Fix.** Rewrote the claims. The follow-up tests (full reverse swap, except-plane necessity test, post-history swaps in both directions) run as sw007.
- **Prevention rule.**
  - A swap that removes an effect licenses "carries enough to override", not "is where it is set". Say *removal* vs *induction* explicitly.
  - "Beats the null" needs the null outside the arm's CI, not just below its point estimate.
  - An arm whose construction is mismatched to its positions (wrong-position directions) supports no conclusion; say "uninformative", not "does nothing".
- **General pattern.** Sufficiency-of-overwrite read as localisation, and a point-estimate comparison read as a significant difference.

## 2026-10-30 — "Displacement-matched" nulls were matched to each row's own remaining gap, not to the real arm's realised displacement (sw006 N1, sw009 C4 v1; executor-8)
- **What happened.** In multi-layer coordinate swaps, the null arms (random or shuffled-label subspaces) rescaled their push at each layer to the norm of U Uᵀ(donor − x) computed on **their own** row's live state.
  - The real arm sets its U-coordinate to the donor's at the first patched layer, so at later layers it only corrects drift (≈ 0.2–1.5 per token).
  - A null row never closes that gap, so it was pushed by the full gap (≈ 4–30) at every patched layer.
  - Realised control / real displacement: median 11–54× at L24 / 40 / 56 (sw009 C4 v1). The nulls were much larger perturbations than the arm they controlled for.
- **How caught.** The user asked to log every control's displacement next to r1 / r4 and confirm the match (sw009 R6). Only the real arms had been logged before.
- **Impact.**
  - **sw009 C4 v1:** stopped before analysis; rerun with realised matching (R7).
  - **sw006:** its N1 nulls used the same construction from layer 0. Its "random natural planes move the habit about half as much as the plane, ≈ 2× their overlap" and "C3 barely beats its nulls" compare the plane with far larger perturbations. Those readings are **unreliable until rerun with matched nulls**. sw006's analysis and report carry a note.
  - **sw007:** its xN1 (all but a random plane) has no rescaling and is not affected.
- **Fix.** Controls are scaled to the real arm's realised per-token displacement at the same layer (real row first in the same chunk, asserted). Every arm's displacement is logged.
- **Prevention rule.**
  - A matched control must be matched on the **realised** quantity, logged for every arm, not on an intended quantity recomputed per step on its own state.
  - Log controls exactly as you log real arms, from the first run.
- **General pattern.** A control matched on the per-step target drifts away from the realised intervention once the intervention changes the state that later steps read.

## 2026-10-30 — sw009 C4: forced and free rows shared sample keys in one judge file, so their labels overwrote each other (executor-8)
- **What happened.** C4's forced readout and free replies were written with the same key format (`model|direction|script|arm|sample`), then concatenated into one judge input. The judge treats the key as the identity, so both stages' verdicts were stored under one key and the later one won. The first judged report (`C_report_v2.txt`) shows identical forced and free tables (e.g. 0.771, n 107 in both), each mixing labels across stages.
- **How caught.** Reading the report: identical numbers for two different readouts, and the forced no-edit rival share (0.771, n 107) disagreed with the keyword check on the same texts (0.84, n 127).
- **Impact.** No generated text was affected, and no judged C4 number had been reported or recorded. The keyword-check numbers given to the user were computed from the texts directly. Re-judging cost ≈ $2 and 15 min.
- **Fix.** Stage-prefixed keys (`C_judgein_v2k.jsonl`, unique 14,336 / 14,336); re-judged into `C_judged_v2k.jsonl`. The first pass is kept, unused.
- **Checked elsewhere.** sw006 reused keys across readouts but judged them into separate files. sw007, sw008 and sw009 Stage A keys include the readout. Not affected.
- **Prevention rule.** Before judging, assert that judge-input keys are unique (`len(set(keys)) == len(keys)`). Put the readout or stage in every sample key.
- **General pattern.** A join key that is unique within each source but not across the concatenation (a silent many-to-one join).

## 31 Oct 07:04 UTC — sw033 hdB0 job launched late by a one-line ssh chain (E2, sw033 agent)
- **What happened:** the launch line backgrounded hdA0's chain with `cd … && … &` and then started hdB0 in the same shell. The `cd` stayed inside the backgrounded chain, so hdB0's command ran from the wrong directory and failed; it was relaunched 2.8 min later with identical code and arguments (sw033 DECISIONS D21).
- **Caught by:** the agent's own status check of both jobs.
- **Impact:** a 2.8-minute delay; no result affected.
- **Fix / prevention rule:** launch each remote job with its own absolute paths (`cd /abs/dir && nohup … &` per job, or a per-job script), never relying on a `cd` that a backgrounded chain shares.

## 31 Oct ≈07:25 UTC — sw020's ladder "corrected" from the wrong estimator (audit notes and ideation's root notes; logged by ideation-10)
- **What happened:** `_sessions/audit/audit_ideation_fix_myself.md` and `_sessions/ideation/notes/2026-10-30_root_session_notes_and_map.md` both called the docx's sw020 rude-but-helpful value "slightly off" (0.46 vs 0.49). The 0.49 comes from `report.txt`, a STRICT-only sensitivity variant with 15 scenarios excluded. The frozen primary estimator gives 0.462 (`experiments/sprint_work/020_v2_behaviour_replication/analysis.md`:14, 238–245), so the docx was right.
- **Caught by:** ideation-10 while tracing every number to its source for the up-to-speed report (30 Oct ≈20:40).
- **Impact:** none on executed work or on any claim. Two notes that other sessions read carry a wrong correction; the corrected docx v3 keeps 0.46.
- **Fix / prevention rule:** before calling one number "wrong" against another, check which estimator, label source and exclusion set each file uses. `report.txt` files often hold sensitivity variants; `analysis.md` names the primary.

## 31 Oct 14:12 UTC — sw035 V3 gate crashed on a dot in the PEFT adapter name, after its code test was skipped (E2, executor-11)
- **What happened:** driver7 named the gated model 'V3_lr0.0005'. PEFT refuses adapter names containing '.' (KeyError in lora_dropout's ModuleDict), so the gate generated nothing for V3. The verdict file was written with only the reference rows.
- **Caught by:** reading the verdict file (no V3 row) and the gate log.
- **Impact:** ≈ 20 min of the day's last S7 result; no wrong number was produced. Training was unaffected.
- **Cause:** to free an idle GPU, I let the full run and the gate proceed without the tiny test's gate-spec stage (sw035 D32). That stage exercises exactly this code path.
- **Fix:** driver8 reruns the gate with 'V3_lr5e-4'.
- **Prevention rule:**
  - When a code test is skipped for speed, run the skipped stage's smallest real-model version first (here: a 4-context gate smoke with the final spec string), before the long job reaches it.
  - Never put an LR with a decimal point into a model / adapter name.

## 31 Oct ≈14:10 UTC — sw043 red_A's in-job known-answer gate skipped by a wrong reference path; a top-up job launched from inside its code folder (E3's sw043 runner; logged by E3 15:20 UTC)
- **What happened:** (1) eval61 checks the reference organism's known answer (hdA0's forced conduct gap) inside the job; the runner's node path for the reference was wrong, so red_A's job ran without that gate (sw043 D13). (2) The 60-story N held-out top-up was launched with the code folder as the working directory; it crashed after "ALL DONE" and its manifest has no end record (sw043 D5).
- **Caught by:** the runner, reading the job logs.
- **Impact:** none on a number: the known answer was computed afterwards with eval61's own function (+0.858, = sw055's), and the top-up stories were used only after their files were hash-checked. red_B's jobs ran with the gate in-job.
- **Fix / prevention rule:** before a gated job, run its known-answer stage once with the real paths (a missing reference must fail loudly, not skip); launch jobs from a run folder, never from the code folder (`python -I` with absolute paths).

## 2026-10-31 17:52 UTC — sw038 DECISIONS: two prep agents appended the same entry numbers (D9, D10)  (sw038 prep-P1 agent, E2 / executor-14)
- **What happened:** sw038's Part 0 and Part 1 prep agents append to one DECISIONS.md. I read the last number (D8) a few minutes before appending and typed D9 / D10 into the heredoc; prep-P0 had appended D9–D12 at 17:48, so my 17:51 entries duplicated D9 / D10.
- **How it was caught:** the `grep` in the same append command printed the file's last numbers (D11, D12) above my entries.
- **Impact:** none on outputs (the entries record design choices made before the calibration output); a renumbering entry (D13–D15) maps them.
- **Rule to prevent it:** when several writers append numbered entries to one file, compute the next number inside the appending command (`N=$((max+1))`, then the heredoc), never from an earlier read.
- **General pattern:** a read-then-write race on a shared append-only file (the 31 Oct 12:56 entry's read-side race, here on the write side).

## 31 Oct 18:47 UTC — an agent's untraced number copied into an analysis and the ledger (E3 / executor-12)
- **What happened:** the sw043 runner's progress message said the redirect's refusal phrasing "leaks into 36% of the helper character's story lines (hdA0: 1%)". I wrote it into `043/analysis.md` and repeated it to the user without tracing it to a file. No file or command produces it.
- **Caught by:** the S10 report agent, which could not trace it (A10 of the S10 report), at 18:40 UTC.
- **Impact:** a supporting detail, not a verdict; the direction is backed by a traceable measure (helper's own-habit rate in its story continuations 0.90 → 0.58 / 0.98 → 0.78 at step 15, STRICT). Corrected in the analysis with a note. The same agent also found smaller wording errors in 043 / 045 (garble range, length ratio, "erases" vs "removes most", forecast magnitude, "slightly increases"), all corrected.
- **Prevention rule:** a number from an agent's prose goes into a record only with the file that produced it named beside it; if I cannot name the file, I ask the agent for it or leave the number out.
- **General pattern:** numbers in a report that no file or executed command produced.

## 31 Oct 19:22 UTC — sw039 Part 2 smoke gate: a typed 1e-3 bar on a live copy whose rows were not bit-identical (sw039 prep-D, E2 / executor-14)
- **What happened:** the α = 1 dose target was computed as c_rec + α (c_don − c_rec). At α = 1 that is 1 fp32 ulp away from sw038's c_don (≤ 7.6e-6). The in-job live check compared sw038's asT row with asT_a1 in the same forward against a bar of 1e-3, which assumed the two rows were bit-identical. bf16 write-back over 48 patched layers amplified the 1-ulp difference to 0.0297, so the gate failed in both models.
- **Caught by:** the smoke's own gate (GATES_FAILED, FAILED_p2_<m>), before any generated row. The chain stopped as designed.
- **Impact:** ≈ 3 GPU-min per GPU (two smoke loads). No output was affected; calibration and frozen scales were kept (sw039 D21).
- **Fix:** the same affine target is written as (1 − α) c_rec + α c_don, which is exact at α = 1. The CPU known answer now gives 0.0 difference, and the identical-rows floor (0, sw038 F_rep) justifies the bar.
- **Prevention rule:** a gate with a near-zero bar needs either bit-identical computations (check the CPU-side difference is exactly 0, not "≤ 1e-5") or a bar set above the measured same-path floor; never a tiny constant on rows that differ by rounding.
- **General pattern:** measured-floor gates (mistakes 31 Oct 08:57), here a typed bar below a noise floor that bf16 amplification creates.

## 2026-10-31 22:08 UTC — E4 analysis headers carried hand-typed "≈22:05–22:15 UTC" times up to 7 min ahead of the clock  (executor-13 / E4; self-caught on a `date -u` call)
- **What happened:** four analysis.md headers (sw061, sw064, sw078, sw079) and one user status line gave estimated times; the real clock was 22:08.
- **Impact:** none on results; misleading timestamps in records that are used to show writing happened before or after data.
- **Fix:** headers now cite `date -u`.
- **Prevention rule:** get every written time from `date -u` in the same command that writes the file (third recurrence; see 30 Oct 22:21 and 31 Oct 07:22).
- **General pattern:** a hand-typed value standing in for a measured one.

## 2026-10-31 22:43 UTC — draft figures: a mislabelled quote pair, a wrong control CI, and missing denominators (ideation-11; caught by Codex's figure audit)
- **What happened:** in `_sessions/ideation/notes/plots/viz/make_viz_figures.py`, ideation-11's draft deck figures:
  - **v6** showed two mixA0 replies as answers to "the same request". They come from different scenarios (roommate bills vs a workout plan), and both were picked from analysis prose, not from the seeded sample file.
  - **v4** typed hdB0's r1 random-control CI as [−4.5, +5.5] pp; the report has [−3.8, +4.9]. It also clipped negative interval ends at 0 and dropped the asT / c1 control CIs.
  - **v1** titled a conditional share ("rival share among habit-bearing replies") as if it were a rate over all replies.
  - **v2** showed effect sizes without the PARTIAL verdicts and the failed neutral controls beside them.
- **Caught by:** Codex's read-only audit, `_sessions/codex_ideation/notes/2026-10-31_ideation-12_figure_draft_audit.md` (22:13 UTC), before any figure reached a deck.
- **Impact:** none yet. Drafts only, published only on ideation's private preview page (https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL), which therefore shows the uncorrected v1, v2, v4 and v6.
- **Fix:** owed by the write-up session. The audit lists exact repairs.
- **Prevention rule:**
  - a plotted number is read from the result file by the plotting code, never typed;
  - a quote panel carries its source key and a recorded selection seed, or is labelled "selected illustration";
  - a title names the plotted quantity's denominator.
- **General pattern:**
  - hand-typed values standing in for measured ones;
  - selected illustrations narrated as a matched or random comparison.

## 2026-11-01 00:15 UTC — sw057 c2: "asT does not predict the decision" read from a one-sided null on a two-sided question  (executor-13 / E4; caught by the blind recompute agent)
- **What happened:** analysis.md said asT does not predict the within-arm habit (hdA0 AUROC 0.22–0.50 "vs null p95 0.56–0.69"; hdB0 0.60–0.68 "≈ null"). In hdA0, AUROCs of 0.22–0.37 are significantly *below* 0.5 (reverse signal). In hdB0, two dismissive arms beat their null (p < 0.001, p 0.015) in sw057's own file.
- **Impact:** an overstated negative in a provisional write-up; the direction of the c2 contrast (d_self > asT in every arm) and the "asT reads conduct, d_self the decision" reading survive.
- **Fix:** c2 bullet and summary reworded ("weak and changes sign across organisms"); ledger written with the corrected wording.
- **Prevention rule:** for AUROC (or any signed statistic) test both tails against the shuffled null, and read per-cell p-values from the results file before summarising a range as "≈ null".
- **General pattern:** a one-sided null applied to a two-sided question; an AUROC well below 0.5 is information, not absence.
