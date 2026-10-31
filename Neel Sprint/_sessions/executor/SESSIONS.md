# Session log — executor

Append-only, newest first.

<!--
## executor-N — YYYY-MM-DD
- **Goal:** 
- **Did:** 
- **Found:** 
- **Did not find / dead ends:** 
- **Mistakes:** 
- **Open threads:** 
-->

## executor-14 (E2b, Lane M continued) — 2026-10-31 ≈17:10 → (running) UTC (rented 4×H100 node + box 1; not compacted)
- **Goal:** the user's E2 brief after the account switch: A sw038 (mechanism core on v2, Part 0 positive control first), B S7 1b diagnosis, C sw039 (Tony's m94 ladder + asT dose sweep), D propose sw034 on v2 if asT holds.
- **Did:** froze the sw038 / sw039 specs before any output; ran 5 build/run agents and 5 blind recomputes; watchers for every GPU stage; analysis.md, ledger, navigation, READMEs for sw038 / sw039 / sw035 1b; laneM push 80c3bc1; report drafter launched.
- **Found:** sw038: the reply-start patch, r1's induction (vs equal-size random edits) and asT replicate on 61 new scenarios in both models; removal not specific. sw039: routing needs own turns hostile AND declining; an apology resets it; asT orders the cells but misses the conjunction; asT induction is graded to 1.5× then plateaus, specific at every dose. S7 1b: configs fine (seed coupling).
- **Mistakes:** 1b identical-reply misreading (inherited, corrected); sw039 L3/L4 unsmoked and unwatched (≈ 35 min idle); hand-typed times (corrected); push-script email pattern misspelled (fixed).
- **Open threads:** sw071 (sw034 on v2) awaits the user's go; report publish; node / pod release.

## executor-11 (E2, Lane M) — 2026-10-31 ≈00:30 → ≈16:30 UTC (rented 4×H100 node + a rented H200 pod; box 1 CPU only; compacted once)
- **Goal:** the E2 Lane M brief (S1–S5, S7), then the user's additions sw034, sw036, sw037. Each with a frozen spec, a blind recompute, a ledger entry and the combined report.
- **Did:**
  - Node setup and parity vs sw009; nine experiments sw029–sw037, every headline blind-recomputed (sw035 1b; V2 / V3 by gate rule).
  - S7: trained per-layer vectors and a rank-1 LoRA on the H200 pod.
  - The combined report artifact; `laneM` pushes (b661751 → 14a9cfd); public HF dataset of run outputs.
- **Found:**
  - An upstream own-turn variable (sw029, sw034, sw037), largely the base model's encoding (sw034 C / parP).
  - The header route carries the flip / onset and the seed-to-seed differences (sw030 / 031 / 037).
  - Thinking-mode suppression is neither length nor the reply-start state (sw033).
  - Constant vectors cannot learn the story binding; rank-1 nearly can (sw035).
  - No forced-channel persona capture in N / NB (sw036).
- **Did not find / dead ends:** the transplant does not separate type from decision (sw031 A); the "plan outside a think block" arm broke (sw033 T3x); no turn-1 decline rise from header polish (sw034 B).
- **Mistakes:** see `notes/2026-10-31_E2_summary.md` (bridge switch; timestamps; pgrep; launch chain; V3 gate crash after a skipped code test).
- **Open threads:** the next tests in the summary note; the user releases the node and the pod (everything is pulled).

## executor-13 (E4) — 2026-10-31 07:07 → ≈16:25 UTC (box 1 H200 + box A H200; not compacted; ended for an account switch)
- **Goal:** the E4 launch prompt (`things to throw away/new session prompts/2026-10-31_E4_S10_S6_launch.md`): (a) S10 replication, (b) the turn-1 own-reply test, (c) readers at S3's sites, (d) spec 11 ideas 6 / 3 / 7, (e) S10 training levers.
- **Did:** day dir `/workspace/runs_executor/day_2026-10-31_E4/` (E1's lib repointed, queue runners on both boxes, post dispatcher); specs from ideation's drafts; prep agents per experiment; blind recomputes; analysis / ledger / index for sw055, 056, 058, 060, 063 (verified) and sw057 (provisional). Training levers approved by the user (12:05); redirect + G2 given to E3 (user decision ~12:23), E4 kept G1 and built the shared trainer / eval / handoff for E3. MAEM rerun through its own repo (`tools/maem`). Follow-ups sw062 / sw063 at the user's "whatever you recommend".
- **Found:** routing by own conduct replicates in 10/12 runs incl. all healthy replay organisms (sw055); at turn 1 hdA0's habit follows its own reply's conduct (sw056, partial overall); the role token does not decide "my conduct", the text's voice / content does (sw058); the conduct carve-out forms after in-story selectivity (sw060); asT reads conduct, not the decision, and an L42-only edit cannot carry it (sw057); harmful continuations are rare (sw063).
- **Mistakes (mistakes.md):** hand-typed spec times (07:22); an adapter gate unsatisfiable at a 0 floor plus an unwatched failed job (08:57); a "no think tags" output gate that fired 3× on model behaviour (12:41); a sha handed to E3 for a file still being edited (12:56).
- **Running at handoff:** sw061 G1 train S (box 1), sw059 full (box A); queued G1 N + eval, sw062. See STATUS_E4.md for PIDs and resume steps.
- **Push:** `adb290d` on `laneS10` (sprint_work 055–063 + README; secret-scanned, no tensors).

- **Addendum (16:15 UTC, before an account switch):** the user asked to push the activation captures (≈ 71 GB) to HF. The job `act_resume.sh` runs detached on box 1 (PID 4101931; marker `/workspace/runs_executor/E2_activations/UPLOAD_DONE`), and the pull loop runs detached (PID 4101966). STATUS_E2.md was rewritten as a full handoff with exact resume steps. Do not release the H100 node before `SYNC_DONE`.

## executor-10 (E1) — 2026-10-30 21:00 → 2026-10-31 05:10 UTC (compacted once)
- **Goal:** the E1 brief, run unattended (`things to throw away/new session prompts/2026-10-31_executor_{common,E1_tony_evals_and_side}.md`).
  - Tony's evals: sw050 (SFL) → sw052 (leakage) → sw054 (story dose) on box 1; sw051 (elite) → sw053 (turn-1 dial) on box A.
  - Then sw065–sw069.
  - User additions: the sw067 H200 arm, sw050 lists-only, sw070 (pirate family on v2), and the reporting rules (unconditional rates; uptake vs suppression).
- **Did:**
  - Set up box A (vLLM, vllm-lens, pinned parent) and box C (RTX PRO 6000; parity after `max_num_seqs` 256).
  - Ran a multi-box queue (runner v4 with PIN lists; an H200 pool); all judging on box 1 with the ALT key.
  - Ran 11 experiments plus 2 user-added follow-ups. Every analysis was blind-recomputed.
  - Wrote ledger entries, the navigation row and series README rows.
  - Wrote the E1 summary (`notes/2026-10-31_E1_summary.md`) and `STATUS_E1.md`.
  - Published the report https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P.
- **Found:**
  - **sw050:** the SFL orderings replicate, but by suppression. A bare "numbered lists" prompt draws in the SFL animal (+0.59, CUEING) along with the SFL character's French.
  - **sw051:** the elite gate failed (binding not learned).
  - **sw052:** ctrlB0's d_self induces hd's rival habit (0.95 / 0.48 of the own swap). The direction overlaps hd's own (cos 0.78 / 0.70).
  - **sw053:** d_t1 is not a habit dial (8/8 cells).
  - **sw054:** the story direction flips the chat habit at d_self's size; d_self moves stories only past its natural range.
  - **sw067:** gating holds on box C. The H200 reruns are UNRESOLVED; sw020 looks like a low draw, and box C sits higher.
  - **sw070:** the pirate flip REPLICATES on v2 at v1's size.
  - **sw065, sw066, sw068 and sw069:** see the summary.
- **Did not find / dead ends:**
  - sw051's chat stage did not run (gate failed); sw054's free replies were skipped (time).
  - sw067's sampler arm could not vary the sampler (the env var is a no-op for our requests).
  - sw053's and sw069b's frozen rules could not discriminate.
- **Mistakes (mistakes.md):**
  - hand-typed spec times (30 Oct 22:21);
  - STRICT misses French animal names (00:41);
  - the raf bridge is crow-biased (01:30);
  - frozen rules not checked against the readout range (02:35);
  - the sampler flag was a no-op (05:05).
  - Two provisional readings I gave the user mid-run were wrong, and I corrected them (sw067's cause; sw051 "keyed on the story").
- **Spend:** $12.24 of the $25 cap.
- **Open threads:** proposals in `STATUS_E1.md`, none queued: a box C vs H200 log-prob test, sw050 format vs persona, and sw070's persona-control cell, among others. Box C is retired; box 1 and box A are idle.
- **Push:** `fe9818d` + `b974b09` (final README status lines) on `sprint_work` (05:12 UTC): `experiments/sprint_work/050–054, 065–070` + the series README, 400 files; secret-scanned (keys, tokens, SSH hosts and ports, the user's email), no tensors.

## executor-9 — 2026-10-30 ≈06:30 → ≈19:35 UTC (three H200 boxes; unattended overnight then daytime; compacted 0 times)
- **Goal:** the master overnight brief, plus the box-2 and v2 briefs:
  - lanes sw010–sw021, then backlog sw022–sw026, then the "if time remains" follow-ups (sw027, sw014 Part 2);
  - the user's daytime additions: "is it just bad scenarios?" (13:20), the GitHub push (15:37), sw028 approval (15:43), "what is important and clean" (D35), and closing boxes 2 and 3 (16:12, 17:07).
- **Did:**
  - set up boxes 2 and 3 (D1, D2);
  - built a per-box queue, run board, judging wrapper, activation saver and shared chat directions (D3, D5);
  - for each experiment: a prep agent, an adversarial reviewer, smoke, release, then analysis plus a blind recompute;
  - ran 19 experiments (sw010–sw027 done and verified; sw028 and sw014 Part 2 pending analysis) and two CPU cross-checks (cumulative control offset; scenario quality);
  - wrote analysis.md and DECISIONS.md per experiment, the ledger and navigation, and 34 mistakes entries;
  - pushed `6c7e5ec` to `sprint_work`;
  - closed boxes 2 and 3 (SAFE_TO_CLOSE at 17:27).
- **Found** (details in STATUS):
  - the core behaviour replicates on v2 (sw020), except hdA0's trigger-gating;
  - routing holds on the model's own rude turns on v1 and v2 (sw015, sw027);
  - sw012 passes 4/4 on free replies (0.83–1.05), but **R7 controls self-cancel after L16** (0.12–0.41× cumulative), so the specificity is only against a random-coordinate swap with an L16 kick;
  - C4 does not replicate as worded on v2's forced readout (sw021), while its free half passes;
  - sw013: the 512 cut hid nothing;
  - sw018: story training alone aligns the axis;
  - sw024: routing is template-independent;
  - sw014 Part 1: register supported;
  - sw010: the axis is mostly own hostility, rebuilt by training;
  - sw016: transfer is asymmetric;
  - sw011: d_t1, not d_self, carries the turn-1 choice;
  - sw017: a partial second-family replication;
  - sw022: output-only conditional;
  - sw023: fragile positive;
  - sw025: recipe-level capture;
  - sw026: known-answer test passes;
  - bf16 header token 0 is unstable at L ≥ 36.
- **Dead ends:**
  - sw011 Part C: d_self is not a turn-1 dial (0.067 / 0.078 vs 0.3);
  - sw011 Part B: the hdA0 setup does not carry the turn-1 choice;
  - sw016: the forward chat-d_self swap into stories is null, and the removal positive control fails;
  - the scenario-quality check found no evidence that bad scenarios explain the failures (screens unvalidated);
  - sw014 Part 2: activations skipped (bf16 gate).
- **Mistakes (all 34 in `mistakes.md`):**
  - **R7 "realised-displacement-matched" controls match the per-layer increment, not the downstream state change** (inherited from sw009 C4 by sw010, sw011, sw012, sw016 and sw021). This is the third time a control was matched on the wrong quantity.
  - guessed numerical tolerances failed the first smokes of sw010, sw011, sw012 and sw021;
  - extract1028 E4's set-2 "pre-habit" position falls after the habit in about half the stories, so sw009 C3 was mis-described;
  - sw021's free controls were selected by signed shift while the rule checks |shift|;
  - sw014's frozen log-odds scale is unstable in near-empty cells;
  - sw013's "same seeds as 014" control shares nothing under vLLM 0.30;
  - the `si` venv lacked httpx (D18);
  - the vLLM script had no `__main__` guard (D14);
  - a per-host resume assumption broke when a job moved boxes (D23);
  - a late-binding closure and a mis-indexed assertion were caught before any use.
- **Open threads:**
  - sw028 analysis (decides the headline wording);
  - sw014 Part 2 analysis; N free dropped, can be requeued (D35);
  - the d_t1 dial test;
  - per-result next steps (STATUS);
  - report artifacts;
  - the overnight summary note;
  - the second GitHub push.


## executor-8 — 2026-10-28 evening → 2026-10-30 ≈04:45 UTC (box 1 H200; compacted once)
- **Goal:** the user's sequence of requests:
  - ideation-9's extraction batch (E1–E6; E7 dropped by the user);
  - the SAE check and Neel's regression (+ beyond-spec SAE quality);
  - the causal feature clamp (parked by the user);
  - housekeeping;
  - sw005 conduct dissection;
  - sw006 swap-and-patch (+ turn-1 test);
  - the review follow-ups (sw007);
  - the whose-hostility test (sw008, user-specified);
  - the audit-session brief (sw009);
  - the sw006 null rerun;
  - two GitHub pushes (`5b9810e`, `597b7d4`).
- **Did:**
  - extract1028 captures;
  - sae1029;
  - sw005 → sw009, each with predictions written before running, two judges plus regex, and an HTML report.
- **Found:**
  - E1 axis cos ≈ 0.96 everywhere;
  - SAE: no compact helpfulness concept, clamp inert;
  - conduct: hostility > refusing > coldness, which does nothing (sw005);
  - the reply-start states set the habit both ways (sw006 / sw007);
  - only the Assistant's own hostility routes (sw008), and a natural hostile user does nothing (sw009 A);
  - **one d_self direction switches the habit both ways in both organisms against matched controls** (sw009 C4; free ≈ 95–100%);
  - the axis is in the parent and aligns with the story characters after training (C3, both families);
  - the sw006 "spread out" claim was overstated.
- **Dead ends:**
  - the SAE feature clamp (parity failed, on-target ≈ 0);
  - C2 decodability (ceiling).
- **Mistakes (all in `mistakes.md`):**
  - sw006 GPU co-location OOM;
  - three sw006 overclaims (caught by the user's review);
  - displacement-matched nulls matched to the wrong quantity (sw006 N1, sw009 C4 v1; caught by the user's logging request);
  - judge-key collision across readouts (sw009 C4; caught on reading).
  - Plus extract1028 / sae1029 entries earlier in the session.
- **Open threads:**
  - replicate C4 in other seeds and runs (recommended);
  - graded-axis check on the sw006 versions;
  - fixed-vector steering;
  - pirate organisms;
  - component level;
  - the user's decision on duplicate storage.

## executor-7 (continued) — 2026-10-28 ≈08:10–13:50 UTC (exploration under /goal; 4 GPU-h cap)
- **Goal:** the user's /goal, read as the assignment asymmetry; the user meant "assistant" (clarified ≈12:35).
- **Did:**
  - design workflow (3 designers + critic) → `design_spec.md` (X0–X7);
  - trained the balanced pirate/Shakespeare organism "sym" (63.7 GPU-min);
  - wave 1 (CPU audits and prep) and wave 2 (one gated vLLM server with 15 LoRAs, 3 client workers, then a blind recompute and a critic);
  - after the redirect, the Assistant batch X8 (conduct × length) and X9 (self-report) in a second 14-min server session.
- **Found:**
  - X8 CONDUCT in all four organisms (blind recompute ALL MATCH);
  - X4 conduct ≥ label;
  - X7 replay suppression GLOBAL;
  - X9 no forced-choice self-attribution, plus a crow favourite-animal lead;
  - the parent's crow prior, with trained crow dominance only in weak-routing runs;
  - persona ranks reproduce across seeds.
- **Mistakes logged:**
  - goal misread (assistant vs assignment);
  - workers' process slips (ii_lite without smoke, X6 cost attribution, X8 prompt record timing, X3 history leak and crash path, X9 parser).
- **Traps found:** vLLM's server fills unset sampling fields from generation_config (top_k 20), fixed with `--generation-config vllm`. Under concurrent LoRA batching, paired seeds do not give identical tokens.
- **Pushed:** `de8faf0` on `sprint_work` (≈14:20).
- **Open:** next Assistant batch (needs the user's GPU go).

## executor-7 (continued) — 2026-10-28 ≈00:10–05:35 UTC (sprint_work/004; ultracode, 5-agent workflow)
- **Goal:** ideation-9's T1–T3 (user: "start with this").
- **Did:**
  - froze the spec, the onset-token list (opener-initial tokens excluded before output) and priors;
  - ran a workflow: T1 → T2 ‖ T1 blind recompute → T3 → critic;
  - switched T3 to a single-engine LoRA route mid-workflow at the user's request (T1 cached; frozen parity gate passed);
  - wrote verdicts, RESULTS, README, ledger and navigation; filed the sw003 correction (D37).
- **Found:** see STATUS (T1 probes not valid; T2 lens-blind at the frozen bar; T3 dynamics).
- **Mistakes:** none new logged. Two process notes:
  - the critic found T2's decisions file last saved after its parent-control outputs (pre-registration unconfirmable);
  - hand-written decision timestamps differed from mtimes (order unaffected).
- **Open threads:** census readout redesign (ideation); J-space go/no-go; the GitHub push of sw004.

## executor-7 (= "sprint executor 2") — 2026-10-27 ≈13:30–23:45 UTC (onboarding, up-to-speed doc, sprint_work/003 on box 1 H200 + one RTX PRO 6000)
- **Goal:** onboard; write an up-to-speed doc for the user (`things to throw away/executor-7_up_to_speed_2026-10-27.md`); then run ideation-8's sprint_work/003 spec (user: "do it properly… note your decisions").
- **Did:**
  - froze the spec and wrote decisions D0–D36;
  - trained the pirate/Shakespeare A/B organisms;
  - passed Gate 0 on Blackwell (FlashInfer-sampler fix);
  - ran Parts J, D, C (with the hd census re-scored on the RTX after a parity miss), P, S1 and S2 (split across boxes, whole part per box);
  - had blind recomputes of C, P, S1 and S2;
  - ran post-hoc F1/F2/F2b at the user's go;
  - wrote analysis.md, RESULTS.md, the ledger, navigation and adapter READMEs;
  - saved the RTX box's logs; pushed to GitHub `sprint_work`.
- **Found:** see STATUS headlines. The main lesson: natural-unit single-layer steering is behaviourally inert, so the steering nulls are uninformative about mechanism.
- **Mistakes:** see STATUS.
- **Open threads:** report artifact; Part R (needs the user's yes); multi-layer intervention; displacement-matched clamp nulls; Part D recompute.

## executor-6 (continued) — 2026-10-26 22:00 → 2026-10-27 ≈01:25 UTC (full analysis, report, GitHub push; overnight exploration launched)
- **Goal:** the user (limits back): full analysis instead of the rushed wrap-up; save everything to /workspace before the boxes were stopped; push to GitHub `sprint_work`; then the overnight exploration spec on the free GPU.
- **Did:** copied box 3/4 local runs to `/workspace/runs_executor/box{3,4}_sw002/` (user stopped both boxes); analysed Track B, H-org ×4, A s2, mix010 A s1, B s1 resampling, Track G, lens readouts of all header tensors (incl. Track E via its own reference cell); blind recompute of Track D and judged spot check (regex = judges 900/900); rewrote analysis.md; report built (subagent) and published https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS; adapter folder for the Track D repeat; pushed to GitHub; launched the overnight exploration subagent on box 1.
- **Found:** B s1's header effect ≈ +20 across 3 sampling draws (verdict depends on the draw); B s0's header state forms at step 62, B s1's peaks at 125 then declines; H-org moves B s1 (+30.7) and A s0 (+71.0); the sarcastic organisms show the same unhelpful-and-curt carve-out and crow dominance; lenses read bee wherever B routes but never crow.
- **Mistakes / events:** the first lens rerun's shards stopped silently (cause unknown; rerun); a helper agent edited STATUS and published report v2 itself (content identical to my rebuild).
- **Overnight (subagent, box 1 GPU 01:00–04:45):** ideas 1–4 of ideation-7's exploration spec done (see STATUS); idea 5 not run (budget). Minor slip: a relative-path background wait, replaced (no effect).
- **27 Oct day:** Track D counted as met (user, D15); overnight leads verified by two agents (recompute + GPU, 07:03–12:58; summary at the top of the exploration HIGHLIGHTS.md); ideation-8's red-team corrections to sw002 applied (D16, report v4); pushes to `sprint_work` at each step.
- **Open threads:** next experiment (analysis.md §11; the transplant is the most robust new lead).

## executor-6 — 2026-10-26 ≈17:00–21:55 UTC (sprint_work/002 on four GPUs; wrap-up, unverified)
- **Goal:** run ideation-7's sprint_work/002 (Tracks A, D, B, E, F, G, H + lens battery; Track C deferred; L0 skipped by the user) on box 1, box 3 and box 4 (2 GPUs), fully parallel.
- **Did:** Track D retrain (data-order fix, parity gate, merge, Track A, four-cell eval, judges); three GPU subagents (box 3: Track A B models + Track B; box 4 GPU 0: Track E + Track G B s1/A s0; box 4 GPU 1: lens module, F, H, 011 199); shared Track G runner; Track G re-split twice; blind recompute of Track A; B s1 resampling; Track H-org (user OK) with a frozen design; analysis.md, ledger, navigation, STATUS.
- **Found:** see STATUS / analysis.md headlines.
- **Mistakes:** five entries in mistakes.md (data-order drift; judging interpreter; pgrep relaunch; box-4 agent slips; runner exit code).
- **Open threads:** pending analyses listed in STATUS; Track D boundary reading; artifact.
- **Continued 26 Oct 23:00 – 27 Oct 01:25 (user: full analysis):** backed up boxes 3/4 before shutdown; B s1 resampling, Track G table, qualitative reads, Track D blind recompute, judged spot check (900/900), all lens readouts; analysis.md rewritten in full; report published https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS.

## executor-5 (continued) — 2026-10-26 ≈12:30–17:00 UTC (throwaway exploration on free GPUs)
- **Goal:** the user: use the free GPU while planning; save designs/results in `things to throw away/`; Persona Vectors coverage, emotion vectors, misc informative runs.
- **Did:** scoping (3 agents: persona-vectors coverage, emotion vectors = Sofroniew et al. 2 Apr 2026, tried-vs-untried ideas); runs `b_routing`, `repB_steering`, `pv_finetune_monitor` on box 1 (emotion run stopped by the user); `FINDINGS_AND_VIEW.md`; second and third pods (box 3 port <port>; box 4 port <port>, 2 GPUs); paste tests on rep B, B s1, A s1 and 011 launched; `ORGANISMS.md` + `merge_organism.sh`.
- **Found:** B s0's rival-animal decision sits at the 7 turn-3 header tokens by L40 (copy +60.8 pts; random and no-prohibition donors ~0); A s0's does not (≤ 8); rep B repeats the steering null but its header isn't lens-readable as bee; story training (not the habit) moves every model along persona-vector trait directions, and B s0's habit pulls back at the pre-reply position.
- **Mistakes:** first launch of b_routing lacked a `__main__` guard (vLLM spawn); a batch agent pair returned time estimates instead of running (relaunched with an explicit execute instruction); 8.5 h caps first proposed, cut to 6 h at the user's request.
- **Open threads:** paste tests (rep B, B s1, A s1, 011) finishing ≈17:00–18:45 UTC; ideation-7's sprint_work/002 spec handed over (see STATUS).

## executor-5 — 2026-10-26 ≈00:05–11:55 UTC (sprint_work/001 persona routing and steering; compacted once)
- **Goal:** onboard; plan and execute ideation-6's sprint_work/001 spec (Parts 1–6), add the user's Part 2 additions (a)–(d), use a second GPU box, and deliver one report with every result. The user was asleep for most of the run.
- **Did:**
  - Execution plan and timed batch.
  - Merged 7 checkpoints.
  - Ran Parts 2, 3 and 5, the additions and stage 0 on box 1, and Parts 1, 4 and 6 and rep A's Part 2 on box 2 (whole parts per box).
  - Built and validated 5 judges; streamed judging; ran 6 analyses.
  - Blind recomputes of every part; qualitative reads of Parts 2, 5 and 6.
  - A three-lens report review (63 findings, applied).
  - Published the report https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4.
  - Ledger, navigation and README entries.
  - Closed out box 2.
- **Found:** see STATUS "Headline results". In short:
  - Steering moves A s0's (and rep A's) routing toward the rival, but not B s0's (frozen rule not met).
  - The axis predicts the routing map (ρ 0.76).
  - The history swap and trigger crossing are persona- and assignment-dependent.
  - Enactment is universal, while multiple-choice "knowledge" shows only in the B assignment.
  - In Part 3 the learned change compresses the persona contrast late (definition-dependent).
- **Did not find / dead ends:**
  - B s0's routing does not move under any persona direction, its own direction or its prompt-induced vector (layers 32–52).
  - No L32 signal in Part 3 (no positive control there).
- **Mistakes (all in mistakes.md):**
  - Claimed an unverified 008 "dismissive→crow bias" (the user caught it).
  - Parse-sign bug in analyze_p2.
  - Census mixed two log-odds bridges (caught by the blind recompute).
  - A judge deadline that counted queue time (40k timeouts, no spend).
  - D29's wrong seed diagnosis and D31 calling stage 0 a pass despite a failed hook flag (both caught by Codex-1).
  - The control-parity command missing `--out`.
  - Report overclaims fixed after review: "differ in kind", prompt-vector dose 0.15 instead of 0.37, A s0's Part 6 pre-trigger crows misread.
- **Open threads:** Part 3 direction choice (user); the next experiment (Codex/ideation proposals); the unresolved Part 6 history divergence and the stage-0 position-0 hook error.

## executor-4 (closing) — 2026-10-25 ~13:00–21:58 UTC (exploration rounds 1–5; session closed by the user)
- **Goal:** the user: "keep doing miscellaneous shit … checking for patterns … Neel's doc should be a gold mine … write your prior before committing". Later: research-spec runs on the GPU; "strengthen and check"; then (19:20) "study the strongest organism".
- **Did:**
  - Rounds 1–4 of parent-model exploration, each with a prior written first. All in `things to throw away/executor exploration 2026-10-25/notes.md` (highlights at the top, scripts `analysis_*.py`). Exploration judge spend: $0.21.
  - Round 5: wrote `round5_strongest_organism/PRIORS.md` (19:19 UTC) and launched workflow `wf_197b9bd7-598` with three checks on 001 A s0.
  - The user asked "why are you doing this?" and then "stop at c2 and c3, finish c1". I stopped the workflow at 21:01 after C1 returned; C2 and C3 never used the GPU.
  - Recomputed C1's key numbers with my own script; they match.
  - Verified the merged-model copy on the network volume (`/workspace/runs_executor/merged/hd-A_s0`, 30 files, sizes match).
- **Found (all exploratory, parent or one organism, one seed):**
  - **Round 4 (D1):** on the real 001 A Kimi corpus, the helper-specific "sounds like the Assistant" score is reliable (0.72) and uncorrelated with story NLL (ρ −0.10). A story-selection experiment is feasible.
  - **Round 4 (D1c/D1d):** token-level surprisal vs axis ρ −0.27 in every story; −0.22 with token identity partialled out.
  - **Round 4 (D2):** Kimi's default uses lists 8% of the time (Qwen 98%).
  - **C1 (patching):**
    - persona and identity tokens carry about none of 001 A's habit (system prompt 2% at all layers, below random 6%; helper name and speech 8%, below random 15%);
    - the difference forms at mid depth (L25–40) at turn-boundary positions before the habit speaker talks (chat: turn-3 user 15%, header 11–15%; stories: help-seeker lines 53%, one paragraph-break token 34% vs random 2%), then gathers at the readout from L44.
- **Dead ends / limits:** C1's readout (008's log-odds) is almost entirely dismissive → crow (default gap 0.08 nats), so C1 says nothing about default-Assistant uptake. It is also inference-time, so it shows expression, not learning.
- **Mistakes:**
  - C1's readout choice (logged in `mistakes.md`);
  - launching a multi-hour, three-check workflow on my reading of the user's direction without first stating the plan and getting a go. The user stopped two of the three checks (memory `feedback-executor-waits-for-spec` updated);
  - one estimated timestamp in STATUS ("19:3x"), fixed from the file's modification time.
- **Open threads:**
  - the user's next-step plan;
  - E5/E6 (training-time) if the mechanistic line continues;
  - a default-uptake readout (bee side) would be needed for any C1 follow-up;
  - the open 018 decisions in STATUS (G2, engine, budget, degenerate rule, evil trait) remain, but Phase 2 is deprioritised.

## executor-4 (continued) — 2026-10-25 11:30–12:30 UTC (side project, saved for later; Phase 2 still waiting)
- **Goal:**
  - The user asked for relevant literature, and to implement and save Betley/Treutlein/Dumas' "Steering towards automated grading degrades alignment" (LessWrong, 3 Sep 2026) in `things to throw away/automated grad awareness/`.
  - Their motivation: once the hidden preference replicates, test alignment, and eventually whether patching the persona removes the grader vector's effect.
- **Did:**
  - Read the post (WebFetch) and cloned their repo read-only (`johny-b/public-steering-vectors` @ `cb71586`). Read its code without running it. Trait definitions were read with `ast.literal_eval`.
  - Pinned down three conventions from their code:
    - the layer: their "layer 36" = input of block 36 = our L35;
    - the strength unit: their served engine scales by act_norm/‖v‖, so s = a fraction of the activation norm. Their ladder demo uses raw units, an inconsistency noted in the README;
    - the position: the last prompt token with thinking on.
  - Wrote `src/grader_vec.py` (extract / steer, any `--model`), `src/grader_judge.py` (their rubric, our two judges) and `src/grader_analyze.py` (vectors / traits).
  - Ran the extraction, a 30-reply steering smoke test and the judging of it.
  - Gave a literature list: split personas; Hua et al. 2510.20487; Nguyen et al. 2507.01786; StealthEval 2509.00591. All verified via web search, not read in full.
  - Sharpened the user's "patch preferences and see if the vector has no effect" idea into a grader × persona-pin 2×2 with validity requirements. The user wants to ideate more first; written into the README, nothing run.
  - Updated STATUS and navigation.
  - At the user's request, copied the 018 activations to the network volume `/workspace/runs_executor/r018/` (77.1 GB, 60 files, sizes all match, SHA-256 matches on a sample; README there). Records updated: STATUS, the 018 READMEs, the Phase 2 plan, a navigation row.
- **Found:**
  - Their vector reproduces: cos 0.99998, ‖v‖ 11.26 vs 11.25, activation norm 82.35 vs 82.36, chat template byte-identical. The same-index comparison gives 0.82, so the offset matters.
  - The grader direction is orthogonal to the 018 axis, story and trait directions (|cos| ≤ 0.06), with different token positions caveated.
  - The smoke test shows a visible framing shift ("hitting metrics" at +0.3 vs "judgment, reputation, trust" at −0.3). Scores are n = 1.
- **Dead ends:** none.
- **Mistakes:** an argparse bug, negative strengths read as flags (fixed with `--strengths=`). No impact.
- **Open threads:** the full grader protocol + random controls (~2 h GPU, ~$3); the user's 2×2 idea once they are done ideating; everything already listed for Phase 2.

## executor-4 (continued) — 2026-10-25 09:15–11:30 UTC (after the 018 report; waiting for box-2 adapters)
- **Goal:** answer the user's questions about 018's results and prepare Phase 2, without starting it ("not yet").
- **Did:**
  - Published the 018 report (https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8). Before publishing: one wording fix (an interpretation had been stated as cause) and corrected counts in the records (D31: 650 degenerate outputs, 19/48 at story L32).
  - **D32:** the evil direction vs a refusal direction (built from the 443 refused evil-prompt replies).
  - Answered which personas were extracted, and which parts were parent-only.
  - Organisation check: no missing referenced files; copied logs and lens-check outputs into `results/`; removed a stray `__pycache__`.
  - Proposed extras: durable activation storage, a token-level projection pass over the rollouts and story corpora, CPU analyses, a steering-judge fix. Not started.
  - Explained Phase 2 and its timing.
  - **Merged-adapter route:** found that the "no vLLM for adapters" rule comes from spec §2 ("untested"), not from a known failure. Saved the user's rule in memory. Wrote `src/merge_check018.py` (merge / vllm / hf / compare), pre-registered D33, and validated it on 001 A in 18 min.
  - Wrote the Phase 2 plan note (`notes/2026-10-25_phase2_plan.md`). Updated STATUS and the 018 records.
- **Found:**
  - The evil direction is orthogonal to refusal (cos 0.01 at L32) and stable (split-half 0.94; 4.5× the noise norm). It is narrow: 12 of 15 positives come from one system prompt.
  - Refusal overlaps the dismissive direction (+0.25 to +0.43).
  - The merged 001 A matches HF with the unmerged PEFT adapter: unsteered gap 0.021, steering-effect correlation 0.992, capture cos ≥ 0.9992, adapter active (story NLL 2.94 → 2.32).
  - Every Phase 2 adapter, including ctrl A and the pilot's regen B, has the same config as 001 A (r 32, α 64, 12 targets).
- **Dead ends:** none.
- **Mistakes:** none new. Before publishing, the report agent caught my count errors (fixed in D31).
- **Open threads:** the user's decisions (G2 reading, Phase 2 engine route, budget, steering-judge rule, evil); box-2 adapters (s2, mix010 B s0 / A s1); durable storage of the activations.

## executor-4 — 2026-10-24 21:45 → 2026-10-25 09:15 UTC (milestone handoff; compacted once at ~01:40)
- **Goal:** onboard; read the vector-extraction papers; then run ideation's experiment 018 exactly as written.
  - Parent only until the §9 gate passes; $50 cap; log every decision and waiver.
  - Mid-run user asks: try vllm-lens-fixed and optimise for speed; extraction and checks first; steering if vllm-lens works; "absolutely sure what's going on"; time limit 9–10 h; adopt ideation's steering addendum.
- **Did:**
  - stage 0;
  - 83,760 rollouts and two-judge filters (184k calls);
  - vllm-lens capture with a 6-line `abs_start` patch, parity accepted;
  - directions; probes (364 jobs, parallelised); a length-matched control;
  - steering calibration and grid (28k outputs, judged) through vllm-lens steering, parity accepted;
  - a known-answer check (28.5k); an HF probe readout;
  - a synthetic positive control; an independent recompute of §12 (a)–(d); two qualitative reads (subagents);
  - records (D1–D30, ledger, navigation, series README, mistakes, analysis);
  - report build delegated to the third subagent.
- **Found:**
  - G1 PASS: axis split-half 0.96; cos 0.91 with 002; PC1 |cos| 0.81.
  - G2 FAIL as pre-registered: probe AUROC 1.0 but null p95 0.80–0.85. Length alone gives 0.9996. The length-matched control still gives 0.98–1.00.
  - G3 PASS: story_dismissive L40 +0.8 gives +2.63, random max 0.07.
  - Every story and trait direction steers its own judged score; axis −0.8 removes the AI identity.
  - The judges score blank and stub replies as dismissive and well formed.
  - The parent refuses the evil prompt.
  - The box has an 18.7-CPU quota.
- **Dead ends:**
  - Generation inside the lens engine ran at half plain vLLM's speed, so generation moved to plain vLLM after 5k rollouts (D9).
  - The first synthetic test's thresholds were mine and wrong; analytic expectations replaced them.
  - A per-row `torch.load` was 14× slower than mmap.
- **Mistakes:**
  - The judges score empty outputs as dismissive (logged in `mistakes.md`).
  - Earlier in the session: 002's L63 is post-final-norm, and 002 read `hidden_states` before the hooks; the ninja/PATH problem (both logged).
  - A `pkill -f` matched my own wait shells (no impact; known trap).
  - 018 was added to the series README late.
- **Open threads:** publish the report and add its link (analysis + ledger); the user's decisions on G2's null rule, Phase 2, a degenerate-output judge rule, and evil.

## executor-3 (end) — 2026-10-24 17:20–20:45 UTC (compacted once)
- **Goal:** the user's Assistant Axis request (axis + persona directions in parent, damaged and healthy models, with cosine heatmaps, using the released method); then the story-corpus question (can a bigger generator such as Qwen 3.8 Max, or the few-shot prompt, give authors-like stories without the damage?).
- **Did:** 002 quick extraction (275 roles × 5 prompts × 8 questions, parent texts through 5 models, every layer; `aa_reduce.py` + `aa_compare.py` after the first analysis stalled on CPU threads); vllm-metamodels parent parity; 012 NLL screen of 1,411 existing stories (few-shot v4 harness, pilot-prompt regens, row-aligned anchors); read and sent the user side-by-side stories (authors / Max / Qwen3.6-27B / Kimi; authors vs regen).
- **Found:** axis cos with parent at L32 0.96 (Kimi-trained) to 0.996 (mix010), persona geometry preserved; drift tracks prose damage. Parent NLL: authors 2.81, regen corpus 1.31, few-shot Max 2.24 (fails screen), few-shot Qwen3.6-27B 1.69 (passes); few-shot examples raise every generator's NLL. The regen corpus that gave the fluent imprinting model is the most template-y (chatbot helper, flat-refusal dismissive).
- **Dead ends:** Qwen 3.8 Max with the few-shot prompt does not reach the regen corpus's surprise level; a bigger Qwen does not escape the trade-off.
- **Mistakes:** relayed the ideation README's "plan left unclosed" for Qwen3.5-397B without checking (the unclosed tag was `</dialogue>`; same consequence: the plan was copied into the prose); corrected in the reply. Torch CPU ops with 176 default threads stalled `aa_analyze.py` (fixed with `torch.set_num_threads(8)`).
- **Open threads:** the corpus decision; the persona-uptake study; 001 report min-p; copying results; seed null for 002.

## executor-3 — 2026-10-24 13:54–17:20 UTC (milestone handoff; session continues)
- **Goal:** the executor-2 prompt: read the five core papers, run the 008 habit-likelihood probe, analyse the partner controls, finish 006; then the user's "keep the GPU busy" and the search for a healthy organism that imprints.
- **Did:** read the five papers in full; fixed and ran 008 (9 models + 1:1 health; independent recompute); verified the partner's 005 controls under our protocol; finished 006's record; built and ran 010 (prefilled-onset generation, new `tokgen` worker job, two-judge labeller); evaluated the pilot's regen-story adapter (011) with the full protocol, health, probe, prefill, checkpoint trajectory and a corpus-fidelity read; built the vllm-metamodels venv and started its HF parity check; published the 006 + 008 report; raised the API cap to $150 (user).
- **Found:** replay models learned the habit and gate its onset ("By the way," restores it at 001's rate; controls 0); the regen adapter imprints in free chat at 001's strength and is fluent at T 1, but chat KL 0.17 (set by step 50; habit after step 150) and its corpus changes the characters.
- **Dead ends:** no regen checkpoint imprints with KL ≤ 0.1; replay is not a route to a healthy imprinting organism.
- **Mistakes:** 008 batch gate with an uncalibrated 0.02 threshold (one model load lost); a self-matching `ps | grep` wait loop (GPU idle ~2.5 min). Both in `mistakes.md`. Also: 011's spec was written after its behavioural run (stated in the spec).
- **Open threads:** the user's A/B/C decision and the corpus rule; parity result; 001 report min-p; copying results into `src/results/`; report update (fork).

## executor-1 (continued) — 2026-10-24 09:00–13:50 UTC (compacted once at 13:37)
- **Goal:** the user's morning requests: run 006 at replay ratios 0.25 and 0.1 on A, run 005, speed up the GPU work, explain results, keep STATUS current.
- **Did:**
  - Trained and evaluated 006 A at 0.25 and 0.1 (chains v7–v9). Health panel for 0.25.
  - Tinker research: not suitable.
  - Confirmed loss masking matches the paper (§2, line 247).
  - Logged Callum's advice.
  - Took over the partner's 005 control adapters, dropped our own 005 training, and queued our full 001-protocol evaluation of the controls (running).
  - Program-status map. Recorded the partner's E03 paraphrase samples.
  - Designed the 008 habit-likelihood probe: not run, not queued, per the user.
  - Rewrote the executor-2 prompt from the full transcript.
- **Found:**
  - Every replay dose that keeps the model healthy removes the chat flip: 1:1 +0.01, 0.25 +0.03, 0.1 +0.01, with garble 4% / 6% / 12% vs 001's 100%.
  - The partner's 005: the damage comes from the prose.
  - Paraphrasing lowers base loss only ~0.1–0.2 nats/token (stage-0 samples).
- **Dead ends:**
  - The no-checkpointing / packing trainer gained only ~20%.
  - Kernel speed-up research and an audit workflow were stopped (user: skip audits).
- **Mistakes:** a wrong "CPU sharing" diagnosis and GPU under-use (logged); started vLLM while the health panel ran (logged).
- **Open threads:** see STATUS "Not done" and "Open questions".

## executor-1 — 2026-10-23/24 (night)
- **Goal:** the user's overnight plan: 001 pipeline + reproduction with the pilot side by side and a health panel; pilot mid_step125 check; 006 chat-mixing organism; 005 habit-free control data; 002 spec if time.
- **Did:** environment (two venvs, parent in /dev/shm); recovered the pilot protocol into 001's spec; wrote and validated trainer, judge, analysis, health panel, vLLM job worker; independent code review; trained 001 A s0 and B s0, 006 C-A; evaluated parent, 4 pilot adapters, their midpoints, our organisms and C-A (T 0.7 200 scripts/cell, T 1 stress, partial T 1 + min-p); health panel; 001 report artifact; 006 replay data; 005 rewrites + control files; 002 draft spec; C-A result verified by a 4-agent workflow.
- **Found:** 001 reproduces the flip in both assignments (+0.45 / +0.48) and the pilot adapters re-score within 0.08; every stories-only model (incl. step 125) is 98–100% garbled at T 1 with chat entropy ~1.1 vs 0.60; 006 C-A at 1:1 replay is healthy (T 1 garble 4%) and keeps story NLL but loses the chat flip (+0.01), as the PHM-based prediction anticipated. 001's habit depends weakly on the prohibition and partly sits in story-form replies.
- **Dead ends / costs:** vllm-lens forces eager mode (2 h of replay generation lost); co-locating vLLM and training throttled both; vLLM restarts cost 5–25 min each; health panel OOM'd once; ~5 h of GPU time lost overall.
- **Mistakes:** five entries in `mistakes.md` (eager-mode generation; health OOM; GPU under-use + wrong "CPU sharing" diagnosis; C-A over-interpretation before verification; earlier operational pkill self-kills noted in memory).
- **Open threads:** C-B (1:1) auto-starting vs a lower-ratio A run (user to decide); 001 report min-p section; copy `/root/runs/` outputs into `src/results/`; 005 exposure decision; 002 budget.

## executor-12 (E3, Chain P + S8/S10 training items) — 31 Oct 2026, ≈00:40–16:25 UTC (one compaction ≈11:20; ended by the user's account switch)
- **Did:** drove a rented 4×H200 node. sw040 S8 premise + P0 targets; sw041 Chain P corpora (4 + 2 word-matched), readouts, forecast frozen before training; sw042 9 organisms trained (3 rounds) and scored with a pre-registered harness; sw043 redirect and sw045 G2 authorship on E4's shared sw061 code; sw044 habit-free N control. Report artifact https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6; public HF repos (adapters, corpora, eval outputs); GitHub branch chainP.
- **Found:** conduct capture follows the polished character (main −47 vs honest control; mirror −11.5, so the pre-registered verdict is inconclusive) and is not an exposure artifact (word-matched main −55.5); habit routing follows polish; the frozen forecast gets main's routing, not its conduct; N's conduct capture does not need the habit-bearing stories; a second-stage chat fine-tune erases the imprinted default whatever its personality.
- **Dead ends / costs:** HF private storage quota (went public instead); forecast61's parity gate failed on vLLM batch nondeterminism (E4 accepted a measured tolerance); E4's 2-way keep select fell short (849 prompts).
- **Mistakes:** KA coverage gap in the decline label; pgrep self-match; spec 05 drift; readout instrument slips; hand-typed timestamp; sw043 runner's skipped in-job gate and code-folder launch (all in mistakes.md).
- **Open threads:** sw045 evals + post running detached (see STATUS_E3.md); redirect dose-response awaits the user; S10 report artifact; node close-out.
- **Update (same session, continued after the account switch, ≈16:50–18:30 UTC):** sw045 finished — stories outside the Assistant turn do not reduce transfer (gate fails; frozen forecast called the direction). sw043 post-hoc dose-response (Amendment A, all 4 GPUs) — the imprint survives the prose-damage repair (step 15) and is gone by step 30; N's refusals by step 15; a transient rival redirect at step 15 with enactment damage. READMEs / results copies / ledger / navigation / day summary (`notes/2026-10-31_E3_summary.md`) done; node SAFE_TO_CLOSE 18:21; S10 adapters to public HF; S10 report artifact being built. Mistake: hand-typed timestamp recurrence (logged).
- **Final addendum (≈18:30–19:05 UTC):** S10 report published (https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia) and linked; its agent's data check led to corrections in 043 / 045 (untraced "36%" withdrawn and logged; "removes most"; forecast magnitude missed; "holds or rises"). Day summary now records the flip results per organism family and the evaluation suite. Chain P pair 2 (optional) not run; offered to the user. Node SAFE_TO_CLOSE; only the mirror loop runs.
- **≈19:10 UTC:** user allowed Tony-derived files to be public → uploaded (sw040, port check, persona-bearing files, sw044 adapter / data / outputs, N redirect arms) plus a new `senku21x/s10-levers-eval-outputs` (sw043, sw045 outputs); node address / keys / email and the pilot git copy still excluded.
- **20:22 UTC:** the Chain P report link (published under the pre-switch account) stopped resolving; republished under the current account at https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (file `042/src/report/chainP_report.html`, identical to `report.html`); every link updated.
