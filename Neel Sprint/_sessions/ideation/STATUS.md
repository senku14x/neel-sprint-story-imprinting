# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Last session:** ideation-6, 25 Oct ~21:15 → 26 Oct ~11:20 UTC, compacted once (~10:10). Transcript `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/f2fb2c57-c10e-4ed8-90dc-1987fdb361db.jsonl`. It contains the alternate OpenRouter key in plain text (user-pasted); never quote it.
- **Unlogged earlier session:** transcript `d9629839…` (25 Oct 17:58–21:09) is the real ideation-5. It built the results artifact https://claude.ai/artifact/9VsMUXGUmtApCVg6T9YAq1 and `where_we_are.md`.
- **Next session:** ideation-7.
- **Ideation spend:** $3.41 of $8 (none in ideation-6).
- **Spec:** read in full this session. Say so after a compaction; ask before re-reading.

## Start here
1. **`notes/2026-10-26_sprint_work_001_results_and_read.md`:** every sprint_work/001 result so far, part by part, plus ideation's read and the suggested next steps.
2. `notes/2026-10-25_spec_sprint_work_001_persona_routing_and_steering.md`: the design of record, with the frozen rules in §9.
3. `_sessions/executor/STATUS.md` and `experiments/sprint_work/001_persona_routing_and_steering/decisions.md` (D1–D30): live state.
4. `notes/2026-10-25_neel_reply_and_scope.md`: Neel's reply (his three asks and the 27B model choice); context, not a limit.

## Where things stand (26 Oct ~11:15 UTC; addendum in the results note)
- **sprint_work/001 is in write-up.**
  - All parts have run on both organisms (001 A s0, B s0), the controls, the parent and the replay pair; blind recomputes match; stage-0 checks pass (D31). Box 1's last session (rep A Part 3 capture) was due ~11:15.
  - analysis.md exists as a draft (10:49). The report prose is written; a review found 63 issues (11 high); a fixer workflow was running at 10:50. Not published yet; no ledger entry yet.
  - D28 still waits for the user.
- **Judging** moved to `OPENROUTER_API_KEY_ALT` after the shared account ran out at 05:24 ($350). Cap raised to $45 by the user; $31.2 spent at 09:46.
- **Two GPU boxes:** box 1 is local; box 2 is reached over SSH (details in the executor's STATUS), on the same `/workspace` volume. Whole parts are split per box, so every contrast stays on one box.

## Headline results (judged; observations; one run per assignment)
1. **Persona map:** the Assistant Axis coordinate predicts which character's animal a persona reaches for across 271 roles, ρ 0.76 vs a text baseline of 0.65 (+0.11 [0.05, 0.18]). The frozen rule says story selection C uses the axis score. Caveat: all roles sit on the helper side, and the signal comes mostly from B s0.
2. **Only unhelpful-and-curt personas flip to the rival's animal;** each feature alone doesn't. AI vs human identity barely matters.
3. **Steering:** no single direction re-routes B s0, not even the prompt-induced vector; only strong random pushes loosen its animal slot. A s0 moves toward crow under many directions, random ones included. The organisms' own persona directions ≈ the parent's (cos 0.93–0.97).
4. **Assignment A has a crow attractor, now in two runs:** rep A (a second training run with assignment A) replicates A s0's crow shift under story_dismissive (+22.1 vs +19.1). A s0 enacts its mapping in stories (96%) but can't report it (21%); B s0 enacts (97%) and reports (81%). B s0 is still the cleaner organism; A's oddity looks like assignment (or story content), not run luck.
5. **Part 3 (D28 pending):** the alignment verdict depends on unit vs raw direction (the spec's ambiguity). Underneath it, story-plus-habit training compresses the dismissive-vs-default contrast at the reply header (L40: parent 9.4, controls 7.7–8.1, A 6.2, B 4.6). This fits H9.
6. **Part 5:** about 60% of the default-persona habit depends on self-written history; the dismissive side doesn't (confounded by length and register).
7. **Part 6:** B s0 needs a prohibition but not its wording (paraphrase keeps 37%). A s0 also needs it from turn 3 on; its high no-trigger rate comes from crow facts in replies 1–2 (recompute).

## Not done / next (ranked)
1. **Get the user's D28 answer to the executor.** Ideation recommends reporting both readings, claiming no pass, and naming the compression observation.
2. **When the executor's analysis.md and report land:** red-team them (scope to B s0 where A is the attractor; the "helper side only" caveat on the census; Part 5 confounds), and score P13–P18 finally (provisional scoring is logged).
3. **Pick the next experiment with the user** (options in the results note §"Suggested next steps"):
   - patching to localize B s0's routing (prompt-run states into the no-prompt run, by token set);
   - story selection C with the axis score;
   - a scoped seed check of the A-attractor vs B question;
   - the compression observation on a second run pair.
4. **Outside run:** helpful vs sarcastic, instructions at `things to throw away/2026-10-26_external_agent_helpful_vs_sarcastic.md` (recommended route: 001 + 017 code from the private archive; two parity checks first). Score P19 when it reports.
5. **Paper notes owed** before designing training-time interventions: Persona Vectors, CAFT, PHM, Piggyback, Entity Binding.

## Decisions made (and why)
- **Neel's reply** suggested one deep dive (signatures, axis prediction, characterize the Assistant). The user (26 Oct) does not want that to restrict ideation: the whole spec is open, including attribution redirection (which the user loves), CAFT-style interventions and KL anchoring.
- **Organisms:** the strongest seed-0 runs first; no seed bookkeeping as a first step; port to other seeds only when a result is striking or goes into a write-up (user).
- **Don't call the Kimi-story organisms "damaged":** fluent at T 0.7; they pass the paper's coherence filter (user).
- **No timelines or deadlines in plans; be ambitious** (user).
- **Check before claiming done:** when unsure whether something exists or has run, check it directly or send a subagent (user rule, saved to memory).
- **Engine:** vllm-lens-fixed with merged checkpoints; series `experiments/sprint_work/` (user).
- **Reply-length cap:** 2,048 for new histories and cross-model free generation; 512 only within one model and protocol. The data show 512 censors the parent (77% of default replies) and the replay models (83–96%) far more than the organisms (27–29%).
- **Next organism if one more is trained:** helpful vs sarcastic (the paper's §4 pair; within each assignment it shares the 4,000 helper stories with our dismissive pair, so only the rival changes).

## Open questions for the user
1. D28 (Part 3 reading).
2. The next experiment after sprint_work/001 (see "Not done" 3).
3. Whether to push tonight's work to GitHub (nothing after 25 Oct 21:11 is in the archive repo).
4. Security:
   - `/workspace/.env` (now three keys) and the HF token files are mode 666;
   - the Tinker key sits in ideation-3's transcript, and the alternate key in ideation-6's;
   - `/root/runs/judge_loop.sh` may still be armed.
5. The executor still has to delete `experiments/reproduction/_runs_executor1/runs/mk_adapters` (331 MB of ideation's aborted download).

## Pointers
- Results and read: `notes/2026-10-26_sprint_work_001_results_and_read.md`.
- Spec: `notes/2026-10-25_spec_sprint_work_001_persona_routing_and_steering.md`; options draft: `notes/2026-10-25_draft_spec_next_experiments.md`.
- Predictions: `notes/predictions_and_highlights.md` (P13–P19; provisional scoring at the end).
- Experiment: `experiments/sprint_work/001_persona_routing_and_steering/` (`design_spec.md`, `decisions.md`, `src/results/`, `src/review/`, `src/report/`).
- Executor: `_sessions/executor/STATUS.md`; plan `_sessions/executor/notes/2026-10-26_sprint_work_001_execution_plan.md`.
- Scope: `notes/2026-10-25_neel_reply_and_scope.md`; Neel's doc `/workspace/story-imprinting-persona-pilot/imprinting_extension/review_sources/sprint_document.txt`.
- Outside agent: `things to throw away/2026-10-26_external_agent_helpful_vs_sarcastic.md`.
- Code on GitHub: private archive `senku14x/neel-sprint-story-imprinting` (snapshot 25 Oct 21:11); public `senku14x/story-imprinting-portable`.
- **Standing constraints:**
  - keys in `/workspace/.env` (shared, alternate, Tinker), never printed;
  - ideation writes only to `_sessions/ideation/`, `mistakes.md`, and `things to throw away/` when asked;
  - ask before editing md files outside `notes/`;
  - pilot code: read, never run.
