# Decisions — sprint_work/001 (executor-5)

Each entry: what was decided, why, and what evidence or instruction it rests on. Times UTC, 26 Oct 2026. "Plan" = `_sessions/executor/notes/2026-10-26_sprint_work_001_execution_plan.md`; "spec" = ideation-6's spec.

## D1 — Clarifications approved by the user (≈01:00)
- **User:** approved plan §5 items 1, 3–14, 16, 17 as proposed. Changed item 2 (keep `" bees"`, and add a readout check: on the focused personas the log-odds routing score must rank-agree with the opener's generated routing, Spearman ≥ 0.8 in both organisms, before the 274-role census is read from log-odds; otherwise the census is scored with the opener, one sample per context, `judge_animal2`) and item 15 (add mix010 B s0 as a fifth merge so the replay models get a routing score).
- Judging cap, Part 6 timing and the cross-model option were not answered; see D9.

## D2 — Reply-length caps (user, ≈01:10; spec §4 "Reply-length cap")
- New histories (Part 1, and any history this experiment generates): 2,048 tokens per reply, finish reason recorded, capped contexts flagged. Part 5 primary at 2,048, with 512 beside it. Part 2 free reply 512 (was 256). The opener stays at 48. Part 6 (within-model trigger comparison) stays at 512, as the spec allows.
- Implemented in `build_jobs.py` (Part 1 histories `max_tokens` 2,048; Part 2 free 512) before any history or free reply was generated.

## D3 — Engine: vllm-lens-fixed for everything (user, ≈01:10: "try vllm lens fixed where possible")
- **Evidence (timed batches, `/root/runs/sw001/timing/timing.jsonl`):** the vllm-lens-fixed engine starts with `enforce_eager=False` and CUDA graphs for decode (`cudagraph_mode FULL_DECODE_ONLY`; only torch.compile is off). The old "vllm-lens forces eager mode" problem (mistakes.md, 24 Oct) does not apply to this build. Lens throughput was close to plain vLLM 0.30 on the same routes (see plan §4).
- **Decision:** every session runs on vllm-lens-fixed with merged checkpoints. Plain vLLM is kept only as a fallback.
- **Prefix caching:** on only for sessions with no steering and no capture hooks (Part 1 histories, log-odds scoring), because a cached prefix would skip the hooks and the steering vector. The worker asserts this.

## D4 — Merges on the GPU, not the CPU (≈01:10)
- A CPU merge (to overlap merges with GPU work) took 220 s for the first of 15 shards, about 50 min per model against 7 min on the GPU (018 D33). It was stopped after one shard (no output kept).
- **Decision:** 018's `merge_check018.py merge` unchanged, on the GPU. B s0 first, while the GPU was idle. The other four run while B s0's Part 2 session is already loaded, holding `/root/runs/sw001/merge.lock`; the queue never starts an engine while the lock exists (vLLM's memory profiling must not see another process allocating, mistakes.md 24–25 Oct). The merge uses ≈1.5 GB of GPU memory against ≈14 GB left by an engine at 0.90.
- Merges go to `/root/merged_sw001/` (outside `/root/runs/`), because executor-1's `sync_to_workspace.sh` loop mirrors `/root/runs` to the network volume every 10 min and does not exclude merged checkpoints (52 GB each). A merge is written to `NAME.partial` and renamed only after its report passes (496 modules, untouched tensors identical, residual < 0.01); the worker refuses any model directory without `merge_report.json`.

## D5 — Log-odds readout method (stage 0.4, partly done in the timed batch)
- `logprobs_mode=processed_logprobs` + `allowed_token_ids=[" bee", " bees", " crow"]`, T 1, one forward per context: the returned log-probs are renormalised over the allowed tokens, so LO = lp(bee) − lp(crow) is exact (the normaliser cancels).
- **Checked:** vs raw prompt log-probs of ctx+bee and ctx+crow on 20 contexts, mean |Δ| 0.0048 nats (max 0.047). Parent vs 008's HF values on 200 contexts, mean |Δ| 0.053 nats (≤ 0.1 bar), means 1.068 vs 1.064. The organisms' check (A s0, B s0) runs with their first sessions.

## D6 — Part 2 additions
- The parent runs Part 2's free-reply manipulation-check cells (story_dismissive and the 5 randoms at L40, 0 and ±0.4) and the primary opener cells, so the manipulation check can use a same-context parent reference (plan §5 item 4) and the openers have a parent null.
- Primary cells (story_dismissive and the 5 random directions at L40 ±0.4, plus α = 0) run on all 199 scripts (plan §5 item 16); everything else on the seeded 100.
- Seeds depend only on (readout, persona, script); asserted in `build_jobs.py check_seeds` (399 seed groups, one seed each).

## D7 — Queue order (≈01:15)
B s0 Part 2 → A s0 Part 2 (the primary rule needs both) → parent persona histories (gates all of Part 1) → parent Part 2 reference → stage 0.5/0.6 (hook fires; header-only parity; these only gate the header-only arm, which is analysed after the check) → D33 parity for the two controls → controls' and replay model's Part 2 → Part 1 scoring, Parts 3–6 as their builders are finished.

## D8 — Subagents (user allowed up to 5)
- One agent builds and validates the judges (`judges_sw.py`: animal2, free_reply, habit_single, persona_validity, text_similarity), with known-answer sets, spend ≤ $1.50.
- One agent builds Part 4 items and Part 6 trigger variants (`part4_items.py`, `part6_variants.py`), spend ≤ $2.
- I write and run everything on the GPU myself.

## D9 — Open user decisions, and the default taken (the user said "start the runs" before sleeping)
- **Judging cap:** **$40** on this experiment's own ledger (`src/api_ledger_sw001.jsonl`). First set at $35; raised to $40 at 01:20 when the itemised estimate (plan §4, measured unit costs) came to ≈ $33, which left no margin. Not raised further without the user. The two subagents run under their own lower limits ($1.50, $2).
- **Part 6:** queued last; runs only if everything else finishes.
- **Cross-model map:** not run (needs a Tinker cap).

## D10 — Judges (agent build, validated on known answers; `src/judges_sw.py`, `src/judge_validation/summary.json`)
- Five judges, both models, final prompt versions: animal2 (consensus 45/47 known items), free_reply (24/24), habit_single (21/22; 22/22 at the ≥ 5 cut), persona_validity (6/6), text_similarity (6/6). One revision each for animal2, habit_single and text_similarity, each forced by a failed known item (details in the summary). Validation spend $0.07.
- **Operating rules adopted from the validation:**
  - animal2 labels are per-judge booleans. **Primary label = both judges agree the animal is present** (conservative); "either judge" is reported as a sensitivity, with agreement. A regex label (008's strict patterns) is computed as a third instrument.
  - Idioms: the judges count "as the crow flies" / "eat crow" as crow and "make a beeline" as not bee. Kept as the judges decide; a regex count of idioms is reported so their weight is visible.
  - Cut-off words at 48 tokens ("honeyb", "New Caledonian cr") can be missed (2 of 47 known items); the regex instrument covers these.
  - free_reply: blank, degenerate and refused replies score dismissive ≈ 3, so every dismissive average is taken over replies labelled `answered`, `partial` or `deflected` only (as the frozen manipulation-check rule says).
  - habit_single: habit present = consensus (mean of the two judges' logprob-weighted scores) ≥ 5.
  - GLM is not deterministic at temperature 0 near the 4/5 edge; DeepSeek is more stable. Both are always reported.

## D11 — Part 4 and Part 6 inputs (agent build; `src/inputs_README.md`, `/root/runs/sw001/inputs/`)
- **Part 4 trigger location changed:** 005's `trigger` metadata points at the wrong help-seeker line in ≈ 18% of stories (logged in `mistakes.md`). The excerpt is cut before the nearest help-seeker paragraph before the onset that contains a strong prohibition. 400 stories (100 per file × helper type), 103 of 503 walked dropped (reasons in `part4_summary.json`).
- Enactment excerpts end after the paragraph separator (`\n\n`, one token, as in training), so the model starts the helper's reply paragraph.
- Answer letters are single tokens; the scorer reads both "A" and " A" forms (6 allowed tokens) and sums per letter.
- **Part 6:** 100 scripts × 4 written variants, all kept (rewrites: ii 4, iii 13, v 29; none dropped). The property-check judge needed four prompt versions, each forced by a failed negative control (mismatched property/text pairs must be rejected); final control GLM 50/50, DeepSeek 49/50. Spend $0.22.

## D12 — Random-direction control added at L32 (≈01:50; an extension, not a primary estimand)
- **Why:** B s0's grid showed that at L32, ±0.4 along story_dismissive, story_helper and the axis all switch the tangent off (no animal in 76–99% of fluent openers; ≤ 2% degenerate), but the spec's grid has random directions only at L40, so this L32 suppression had no specificity control.
- **What:** the five random directions at L32, ±0.4, default persona, 100 scripts, on B s0, A s0 and both controls (1,000 openers per model, ≈ 2 GPU-min each); same seeds as every other opener cell.
- **Reading:** reported beside the L32 cells only; the frozen redirection rule (L40) is unchanged.

## D13 — Test of the Part 2 asymmetry: steered log-odds in models without the learned habit (user, ≈02:05)
- **Context:** A s0's rival crow rises +19.1 pts [+14.1, +24.6] under story_dismissive L40 +0.4; B s0's rival bee +1.5 [−0.5, +4.0]. My first explanation (a "training-independent dismissive → crow bias" from 008) was wrong: 008's raw log-odds show the parent leaning bee under the dismissive prompt, and the controls' dismissive − default only +0.23/+0.38 (mistakes.md).
- **Test (user's design):** 008's bee−crow log-odds (both bridges), default persona, trigger present, 100 scripts, at L40 under none / story_dismissive ±0.4 / random_0 ±0.4 / random_1 ±0.4 (every position), on the parent, ctrl A and ctrl B; also on A s0 and B s0 for comparison. Job `p2_lo_steer` (worker `lp` jobs now accept a steering vector; lens engine, no prefix cache).
- **Alternative reported beside it (user):** gating. 008's chat association without the prohibition is A s0 +3.77 vs B s0 −0.21: A's crow association is broadly reachable, B's is trigger- and persona-gated. A steering push toward dismissive can then release A's crow without the right trigger/persona context, while B's bee stays gated.
- **The frozen rule's verdict stands as written:** redirection fails in both assignments (A s0 +19.1 < 20; B s0 +1.5).

## D14 — Queue reordered (≈02:08)
- The parent session (Part 2 reference, steered log-odds, Part 3, bee−crow sentences, Part 5 parent continuations) and both controls' Part 2 sessions moved ahead of the parent histories, so D13's test and the controls' half of the frozen rule are done when the user returns. Total GPU time is unchanged; Part 1 starts ≈1 h later. The parent's Part 1 predictor capture becomes its own session (`004c`), created by `queue_p1.py` after the histories.
- The controls' D33 parity (session 006) now runs after their Part 2 sessions; their results are reported only once parity passes (if it fails, they are rerun on HF).

## D15 — A s0's L32 random control moved forward (≈02:20)
- A s0's story_dismissive at L32 +0.4 routes the default persona to the rival's crow in 72% of openers (+68 pts [+58, +78]); B s0's same cell gives +9. With no L32 random control yet, this is the most important unchecked cell, so A s0's L32-random session (which also carries its D13 steered log-odds rows) runs right after its current session (`002a`), at the cost of one extra A s0 load (~2 min).
- **Rule wording, recorded before the controls are read:** the frozen redirection rule says "every random direction raises the rival's animal by < 5 points". At the rule's dose (+0.4, L40) all five randoms pass in both organisms (max +4.5 in B s0, +0.5 in A s0); at −0.4, random_1 raises A s0's rival by +6 [+3, +9.5]. The verdict is scored at +0.4, as the rule's own cell; the −0.4 values are reported beside it.

## D16–D19 — Part 2 additions requested by the user before reading B s0's null (≈02:30; frozen rules unchanged; `src/build_extra.py`)
- **D16 (a) positive control:** per model, the prompt-induced vector v_L = mean over the 100 scripts of [turn-3 header mean (C1 set d) with the dismissive system prompt − the same without it], on the same parent default histories that Part 2 steers (the no-prompt render is asserted byte-identical to 010's prompts), L32 and L40. The no-prompt default is steered with v_L at its own norm (alpha 1, raw), every position and header→end, plus the 5 random directions each scaled to ||v_L||. Run on A s0 and B s0 (the question) and on the parent and both controls (for D19's log-odds readout and the generation null). `pa_vec` also reports ||v||/N̄ and v's cosine with 018's story/axis directions.
- **D17 (b) organism directions:** 018's recipe in each organism's own context: default, story|dismissive and story|helper (train split, kept), and role_fully (train, kept) capped at 40 rollouts per role (seeded 2650) to keep the capture at ≈ 11.7k texts per model (018 used 61k role rollouts); roles enter the axis with ≥ 10. The parent is run on the same subset, so organism-vs-parent cosines per layer are like-for-like; cosines with 018's full parent directions are reported too. Steering with the organism's own story_dismissive at L40 ±0.4 uses 018's dose convention (unit direction × alpha × the parent's N̄_L), so it is directly comparable with the Part 2 random cells at L40 ±0.4 (the "same random set"); 199 scripts, like the primary cells.
- **D18 (c) sweep:** story_dismissive, axis and random_0..4 at L48 and L52 ±0.4 (199 scripts) and at L40 +0.8 completed to 199 scripts (the grid already has those 100), both organisms; opener readout.
- **D19 (d):** 008's bee−crow log-odds (both bridges, 100 scripts) under every steered condition of Part 2 and of (a)–(c), on the parent, ctrl A, ctrl B, A s0 and B s0; default-persona conditions on default contexts, the reverse test on dismissive contexts; (b)'s own-direction cells on the organisms only. ≈ 28.8k forward passes per model, run last in each session.
- **Order (user):** B s0's next session, then A s0, then the parent and controls (queue `002c2`, `002c3`, then `002d`/`002e` with (a)+(d) appended, `002f` parent).
- **Check before running:** a review workflow (three lenses: matches the request; runs correctly; two-box paths) with an adversarial check of every finding, while the parent session runs.

## D20 — Second GPU box (user, ≈02:40): whole parts per box (user's rule)
- Box 2 (H200, same `/workspace`; GPU on NUMA node 0, jobs pinned to CPUs 0–87) runs **Part 1, Part 4 and Part 6** for every model; box 1 runs **Parts 2, 3, 5**, the additions (a)–(d) and the stage-0 checks. Every steered/unsteered and model-vs-model contrast therefore stays on one box (user's rule; my first per-model split would have broken it).
- Box 2's run directory is `/workspace/runs_executor/sw001_box2/` (job files, queue, outputs), read directly by box 1's judging and analysis; box 1 keeps `/root/runs/sw001/`. One shared API ledger (`src/api_ledger_sw001.jsonl`, $40 cap); judging runs once, on box 1.
- Environment: the vllm-lens-fixed and si venvs, the lens packages and the parent copy were pushed box 1 → box 2 over SSH (295 MB/s measured); the six merged checkpoints are pushed the same way (byte copies of the checked merges, written to `NAME.partial` and renamed when complete).
- Box 2's first job is 008's log-odds parity check on its own engine (same 200 contexts, ≤ 0.1 nats), then the parent histories at 2,048 (the first 200 conversations are the 2,048-cap timed batch).

## D21 — Review of the additions and the two-box changes (workflow wf_69546d2a-e6e, ≈03:00–03:15; 3 lenses, 12 findings, 9 confirmed by an adversarial check)
- **Fixed (major):** box 1's judging loop was still running pre-D20 code, so box 2's Parts 1/4/6 would never be judged → restarted between passes (no judge call in flight), now reading both run directories.
- **Fixed (major):** box 2's 008 parity result went to a file nothing read → recorded in `src/results/stage0_lo_box2.json` (pass: 0.046 nats vs 008 HF; 0.019 vs box 1).
- **Fixed:** `queue_p1.py` now refuses to build Part 1 unless all 7,980 parent histories exist.
- **Fixed:** the organisms' same-text cosine with the parent (D17) would have been skipped because the parent's session runs after theirs → a CPU session (`002g_pb_cos`) recomputes the organisms' directions report once the parent's exists. (The reviewer also measured that the 40-per-role cap changes the parent axis negligibly: cos 0.9999 with 018's full axis at L32/L40/L48.)
- **Fixed (speed):** the capture hook built a GPU index tensor per layer per request; contiguous position sets now use a slice (equivalence unit-tested on 200 random chunked prefills, `src/stage0/test_capture_slice.py`). Matters for D17's 64-layer capture.
- **Cleaned:** box-1 copies of Part 1/4/6 job files and the held box-1 Part 1 sessions moved to `/root/runs/sw001/superseded_D20/` (nothing referenced them); the two-box comment in `common_sw.py` corrected (box 2 writes straight to RUN_B2; no `.box2` suffix is used).
- **Accepted as is:** the controls' D33 parity and the header-only steering parity run after the cells they validate; results that depend on them are reported only after they pass. A failed merged-model push would stall box 2's queue: watched by the monitor. (d)'s cost estimate corrected to ≈ 28M tokens, ≈ 45 min per model.
- **Rejected by the verifier (3):** see the workflow journal.

## D22 — Per-model check of the copied checkpoints on box 2 (≈04:00)
- The six merged checkpoints were copied from box 1 to box 2 (all 30 files per dir, byte sizes identical, merge_report.json present). Byte sizes do not prove the copy is intact, so each box-2 Part 1 session now runs the 200-context stage-0 log-odds job (`s0_lo200_b2`) first, for every model. Those log-odds are compared with box 1's on the same contexts where box 1 has them (parent, A s0, B s0 via stage 0 / D13) before any box-2 result is used. Cost ≈ 20 s per model.

## D23 — Part 5: post-hoc sensitivity views after the blind recompute and the qualitative read (≈04:30; frozen rule scored as written)
- The frozen Part 5 rule is scored on the primary readout (habit_single consensus ≥ 5, cap 2,048): default persona fires in both families (ratio 0.38 B, 0.41 A); dismissive does not (1.56, 1.50). The independent recompute (`src/review/recompute_p2_p5.md`) reproduces every cell.
- Added to `analyze_p56.py`, labelled **post hoc**: (i) threshold ≥ 6 and "either judge ≥ 5" (the qualitative read found false negatives on one-sentence facts that glm scores 3.5–4); (ii) the turn-3 rate split by whether turns 1–2 already contain the persona's own animal (008 strict regex). Reason: the qualitative read (`src/review/qual_read_p5.md`) found that the parent's 7.5% after A s0's dismissive history is copying of crow facts already in that history, and that the dismissive swap changes history length and register (parent dismissive turns 1–2 ≈ 280 chars vs the organism's 1,600–2,400) as well as the writer. These views qualify the reading; they do not replace the rule's verdict.
- D22 result (04:21): rep B's merged checkpoint (no box-1 run to compare against) has identical sha256 on both boxes, 30 of 30 files (`/root/runs/sw001/sha_repB_box1.txt`, `/workspace/runs_executor/sw001_box2/sha_repB_box2.txt`). The other five are checked by the 200-context log-odds job at the start of each box-2 session.

## D24 — Judge hang fix (04:58)
- One `judges_sw.py run animal2` call on the Part 2 openers stopped making progress at 04:30 with 5 API connections open, and its driver loop waited behind it for 27 min. 001's client (`llm.py`, unchanged) uses httpx's 240 s per-read timeout, which a server that keeps the connection alive never trips. Fix in `judges_sw._call`: a hard 300 s deadline per call (`asyncio.wait_for`); a timeout counts as one failed attempt (4 attempts, then an error row, which the next run retries). The hung child was killed (the driver and all GPU work untouched); judging is resumable, so nothing is lost or double-counted. 001's `judge.py` (Parts 5/6 secondary readout) keeps the old client; it is watched.
- D24 addendum (05:09): the driver called a judge only when new items arrived, so items left by the killed run (and any run that dies) waited for unrelated new rows. `judge_driver.py` now also runs a stream's judge when some item has no row from one of the judges (error rows still wait for the next new items, so persistent errors are not retried every loop). Driver restarted while idle (no child running).

## D25 — OpenRouter account out of credits; judging paused (05:24)
- From ≈04:30 every judge call returns HTTP 402 "Insufficient credits" (account: total_usage $350.21 of $350 purchased; this key's spend today $18.99 = this experiment's ledger, so the experiment's $40 cap is not the cause; the account is shared with other sessions). This, not only a slow connection, is what stalled the 04:30 run (001's client retries every error 6× with back-off, inside 4 attempts per item).
- Judging driver stopped (no 402 error rows were written; state is clean and resumable). GPU work on both boxes does not use the API and continues unchanged.
- **No change of instrument:** the judges stay glm-5.3-flash + deepseek-v4.1-flash via OpenRouter (logprob-weighted). Until credits are added, judge-dependent readouts (Part 2 openers for the A s0 additions and the controls, Part 1 opener readout check, Part 4 enactment, Part 6) are read **provisionally** with 008's strict regex (the third instrument named in D10), labelled provisional, and replaced by the judged values when judging resumes. Log-odds readouts (Part 1 census/focused, Part 4 association, D13/(d), stage 0) need no judge.
- To resume: add credits, then `cd src && nohup /usr/bin/python3 judge_driver.py >> /root/runs/sw001/judge/driver.log 2>&1 &` (resumable; only unjudged items cost).
- Watcher (05:42): `/root/runs/sw001/judge/resume_when_credits.sh` probes the API every 5 min (1-token call; log `judge/credit_probe.log`) and restarts the driver once a call returns 200.

## D26 — Judging resumed on the alternative OpenRouter key (user, ≈07:57)
- The user said to use the alternative key. `/workspace/.env` has `OPENROUTER_API_KEY_ALT` (its account: $150 credits, $83.85 used at 07:57). `src/run_judges_altkey.py` starts the unchanged `judge_driver.py` with `OPENROUTER_API_KEY` set to that value in the process environment only (001's client reads the environment first); the key is never printed, logged or put on a command line. Same judges, prompts, providers and logprob weighting; only the billing account changed. The experiment's $40 cap still applies through the shared ledger ($19 before resuming). The credit watcher was stopped.
- Provisional regex reads (D25) are now superseded as each judged readout completes; the report uses judged labels only.
- D24 correction (08:25): the 04:58 deadline also counted the wait for a concurrency slot, so a 20k backlog timed out unsent (40,534 error rows, no spend; mistakes.md). The deadline now wraps only the HTTP request (180 s, inside the slot). Error rows are retried by the next run.

## D27 — Parent's prompt-vector generation run added (09:32)
- D16 promised the prompt-vector steering on the parent too (generation null + log-odds), but session `002f` was queued without `pa_steer` (its log-odds are in `pd_lo`). Added session `002f2_parent_pa_steer` (parent, the same `pa_steer` job as every other model, vector `pa/vec_parent.pt`, ≈ 10 min with the load) right after `002f` on box 1, so it compares with the parent's box-1 unsteered openers. Expected to be 0% bee/crow like every parent cell; run for completeness.

## D28 — Part 3: the frozen rule's persona direction is under-specified; verdict depends on it (09:45; user decision requested)
- The rule says cos(Δ_shared interaction, "story_dismissive − story_helper"). `analyze_p3.py` (written before any Part 3 data) used unit(story_dismissive) − unit(story_helper), without a recorded reason. The blind recompute (`src/review/recompute_p3.md`) used 018's raw directions, raw(sd) − raw(sh) = mean(story dismissive) − mean(story helper), normalised.
- Results at the header (trigger present, 100 scripts, split-half ≥ 0.99 everywhere): unit-difference L32 +0.01, L40 −0.15, L48 −0.18 → rule fails at every layer; raw-difference L32 −0.05, L40 −0.201 [−0.206, −0.194], L48 −0.216 → passes at L48, on the threshold at L40. Neither passes at L32 (the spec's predictor layer, E12's layer).
- Not choosing between them after seeing the results: the report gives both, labels the unit-difference version as the one implemented before the data, and asks the user which reading the rule meant.
- The recompute's reading matters more than the threshold: the alignment is negative because the trained organisms separate dismissive from default *less* along the dismissive direction than the controls and parent do (L40 projection of each model's dismissive − default header contrast: parent +9.4, ctrl A +7.7, ctrl B +8.1, A s0 +6.2, B s0 +4.6). That is compression of the persona contrast, not movement toward dismissiveness, and it is not specific to story_dismissive (trait_impolite −0.20, trait_apathetic −0.19 at L40). The raw sd − sh direction is ≈ story_dismissive (cos 0.99).

## D29 — Part 6 design limitation found by the blind recompute (09:45)
- Turns 1–2 were generated separately for each turn-3 variant (generation seeds are keyed on the row id, which includes the variant), so the six variants of a script do not share their history (turn 1 identical in only 23–31 of 100 scripts per organism cell). Variants are still paired by script and seeds are not keyed on any condition outcome, so this adds variance, not bias. A s0 often produces crow in reply 1, before any trigger (112 of 600 dismissive conversations), which is why its "no trigger" rate stays high (29% vs 41%). Reported as a limitation; not rerun.

## D30 — rep A's Part 2 grid moved to box 2 (user, ≈09:45: "offload tasks to box 2 if you want")
- Box 2 finished its share at 08:42. rep A's Part 2 grid (openers + free replies: primary and rest, 11,387 rows) moved from box 1's session `009` to box-2 session `030_rep_A_p2`: identical job inputs (byte-compared), same seeds (keyed on row id), outputs in `/workspace/runs_executor/sw001_box2/p2/{opener,free}.jsonl`, read on box 1 through `p2/{opener,free}.jsonl.box2` symlinks (common_sw.jsonl's existing `.box2` mechanism), so judging and analysis pick them up unchanged. rep A's steered and unsteered cells are generated in the same box-2 session, so its Part 2 contrasts stay on one box (D20 rule); its comparison with A s0 is a comparison of within-box effects. rep A's Part 3 capture stays on box 1 (`009`, now capture only), where the controls' captures it is contrasted with were made. rep A's checkpoint on box 2 passed D22 (0.048 nats vs 008 HF).
- Judging cap raised to $45 (user: "spend it").

## D31 — Stage-0 checks run after the cells they validate: both pass (10:45)
- **005 (steering in vllm-lens-fixed vs HF on the same contexts):** steering effect correlates 0.999 at both scopes (all positions: mean −0.811 vs −0.809; header→end: −0.689 vs −0.688); header-only parity passes (`src/results/stage0_steer.json`).
- **006 (controls' merged checkpoints, 018 D33 check):** effect cosine at L33 0.9998 for ctrl A and ctrl B, accepted (`src/results/stage0_parity_ctrl-{A,B}_s0.json`). The queued command omitted `--out`, so the compare step crashed after both sides were saved; the CPU compare was rerun on the saved tensors with `--out` (no GPU rerun needed).
- **D30 rep A:** Part 2 grid on box 2 judged; story dismissive L40 +0.4 rival +22.1 [+16.1, +28.1] (A s0's crow shift replicates in a second training run with the same assignment); manipulation check +0.36 (under the 0.385 bar).

## D32 — Corrections after Codex-1's review (11:50; mistakes.md entries dated 26 Oct)
- **D29 corrected:** the saved Part 6 jobs give the six variants of a script identical per-turn seed lists (the seed function omits the variant), yet the realized turns 1–2 often differ. The cause is unresolved (batch-dependent numerics in sampling are a candidate, not shown); D29's "seeds keyed on the variant" explanation was wrong. The reading is unchanged: variants are paired by script, the histories are not literally shared, which adds variance, not bias.
- **D31 corrected:** stage 0 did not pass in full. `stage0_steer.json` has `hook_fires_pass = false`: the all-position mode's largest relative error is 0.048 against the implemented 0.02 tolerance (header-to-end 0.012), identical across texts, i.e. one position (position 0); the hook fires at the right layer (no change at L39, mean shift 36.1 at L41 vs intended 36.07) and behavioural parity with HF is 0.999. Disposition: reported as a failed numerical check with an undiagnosed single-position error, not as a pass; exact delivery of the all-position intervention is not validated beyond behavioural parity (report appendix A1, analysis.md).

## D33 — Part 3 direction: executor's recommendation recorded (12:05; the frozen rule is unchanged)
- Recommendation (also Codex-1's): the frozen verdict is the pre-data implementation's (unit-vector difference): **fails at every layer**. The difference of story means (the more natural construction, and the one the executor would have chosen a priori) is reported as a sensitivity result: it passes |cos| ≥ 0.2 at L48 and barely at L40. Neither reading passes at L32, where the animal positive control is also absent, and in both the alignment is a negative compression of the dismissive–default contrast, not specific to story_dismissive. Future geometric rules fix the construction at tensor level (keys, normalisation order, layer) when frozen. The user has not overruled this.
