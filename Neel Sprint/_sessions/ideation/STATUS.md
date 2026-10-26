# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Last session:** ideation-7, 26 Oct 2026 ~11:15 → ~19:30 UTC, no compaction. Transcripts `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/62c6bc01-0b74-4706-9391-930c71a65a72.jsonl` and `96490c78-aadd-4fb0-b209-fa9c2a95392f.jsonl`. The user is switching to a different account for the next session.
- **Next session:** ideation-8.
- **Ideation spend:** $3.41 of $8 (none in ideation-7).
- **Spec (V6.1):** read in full in ideation-7. Say so after a compaction; ask before re-reading.

## Start here
1. `where_we_are.md` (project root; refreshed by ideation-7, 26 Oct ~14:15): the whole state in one file.
2. `notes/2026-10-26_spec_sprint_work_002_routing_locus_across_runs.md`: the running experiment's spec. The executor runs the **18:15 version**; Track A2 (added 18:50) is NOT in the run.
3. `things to throw away/executor exploration 2026-10-26/notes.md`, sections `paste_repB` and `paste_Bs1` (the copy-test results below). Its `FINDINGS_AND_VIEW.md` has the executor's view; F2 there is withdrawn.
4. `_sessions/executor/STATUS.md` and `experiments/sprint_work/002_routing_locus_across_runs/decisions.md`: live run state.
5. Briefing artifact: https://claude.ai/artifact/T5WSDUzPtpqNicDy9aCYvQ (shared by link; file `notes/2026-10-26_ideation7_up_to_speed.html`).

## Where things stand (26 Oct ~19:30 UTC)
- **sprint_work/001** done; report https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4. D28 settled as ideation recommended (executor D33): the pre-data reading is the verdict (fails); the raw reading is a sensitivity result.
- **sprint_work/002 is running** on 4 GPUs (tracks A, B, D, E, F, G, H; Track C deferred by the user). The executor expects about 5–6 h real time.
- **The "mechanism is per run" scare is not supported for B.** Copying the 7 reply-start tokens (dismissive + prohibition → default) at L40 moves bee:
  - B s0 +60.8;
  - rep B (same-seed replay sibling) +68.8, although the logit lens read " bee" at rank 5,164, so that lens null was an instrument miss;
  - **B s1 (independent seed) +18.0 [+11, +25]**, with B s0 at +52 on the same 100 scripts. Same signature (needs the prohibition, random ≈ 0, L40 peak): same place, a smaller share of the routing. Frozen rule: partial band → Track D decides. A s1 pending.
- **Crow dominance (ideation-7):** crow is the strong, context-independent animal in both assignments, which explains A s0's oddities. A is not a bad run. In the sarcastic pair (outside run E07) crow does not dominate (rival bee 12.5% vs crow 7%), so it may be specific to the dismissive corpus; Track B tests this.
- **Compression goes with expression, not routing** (ideation computation): replay A s0's header contrast is 8.40 vs A s0's 6.18 (parent 9.39), with the same routing.
- **Outside run E07 (helpful vs sarcastic, Phase 1):** imprints in both assignments (default helper's habit 22% / 20.5%; interaction +0.26 / +0.30). The sarcastic prompt mostly switches off the helper's habit (d_h > d_r). Ideation recomputed the cells from the raw rows: exact match. P19a and P19b hit.

## Not done / next (ranked)
1. **When sprint_work/002 lands:** read E (refusing Assistant), F (stories in context) and B (sarcastic pair) first, then D (same-seed rerun noise), H and G. Score P20 in `notes/predictions_and_highlights.md` (P20a and P20c already scored).
2. **Next experiment, the forward step:** find what the reply-start routing state is in B s0 (e.g. a DAS-style learned subspace at the L40 header), test whether it transfers to B s1 and rep B, and compare it with the parent's story-side "next speaker" direction (Track H). Then R2 (training-time redirect or contain), R4 (narrow by design), R5 (beneficial transfer; needs the corpus hold lifted). Full program in `where_we_are.md` §11.
3. **Optional follow-up:** Track A2 (position × layer sweep over the last turn), written in the 002 spec, not run.
4. **Executor to fix wording:** sprint_work/001's `analysis.md` and its ledger entry say A's crow shift "replicates in rep A"; rep A is a same-seed sibling (logged in `mistakes.md`).
5. **Push to GitHub after 002 finishes** (branch `sprint_work`; procedure below).

## Decisions made (and why)
- User (26 Oct): all generation at T 0.7; log-odds alongside; T 1 + min-p only on headline cells.
- User: Track C (fresh released pairs) deferred; not needed for the reliability question.
- User: header readouts use a validated lens battery (J++ primary; Camila Blank's J-Lens / R-Lens and template lens; logit lens only for comparability). No decision rests on a lens; the copy test is the arbiter.
- User: Neel's reply is context, not a limit; be ambitious; strongest organisms first; never call the Kimi-story organisms "damaged".
- Ideation: never call same-seed replay siblings independent replications.

## Open questions for the user
1. Scrub the SSH hosts and ports (executor STATUS, `ORGANISMS.md`) from the GitHub history?
2. Merge `sprint_work` into `main`?
3. Lift the corpus hold eventually (mirror corpus, E2 source stage, R5)?
4. Record the narrowing decisions in `amendments.md`?
5. Security (carried over): `/workspace/.env` and the HF token files are mode 666; keys sit in ideation-3's and ideation-6's transcripts.

## Pointers
- Papers: `papers/research_papers.md` (all 31 entries plus the synthesis) is the one-file summary; `research_synthesis.md` is loaded via CLAUDE.md. `papers/research.md` is stale.
- Neel's MATS doc: `notes/reference/` (PDF, text, embedded links). His reply: `notes/2026-10-25_neel_reply_and_scope.md`.
- Lenses: the J++ local copy is `/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt` (sha256 matches HF). Camila Blank's lenses: `camilablank/workspace-lenses` @ `d740106d`.
- GitHub: private `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` (last commit `1cb8e36`, ~19:20 UTC). Push procedure:
  - the sparse clone is at `/root/gh_sprint_work/repo` (container disk; may be gone);
  - compare blob hashes of the workspace against the branch tree, then copy the new and changed files;
  - skip `*.pt`, files over 50 MB, and the excluded sprint_work/001 payloads;
  - secret-scan, `git add --sparse`, commit, push;
  - list exclusions in `EXCLUDED.md`.
- Outside run E07: GitHub `senku14x/story-imprinting-persona-pilot`, branch `e07_sarcastic`; adapters public at HF `senku21x/story-imprinting-qwen36-27b-sarcastic`.
- Standing constraints:
  - keys in `/workspace/.env`, never printed;
  - ideation writes only to `_sessions/ideation/`, `mistakes.md`, and `things to throw away/` when asked;
  - ask before editing md files outside `notes/`;
  - pilot code: read, never run.

## Update 26 Oct ~20:15 UTC (sprint_work/002 mid-run; GPU work expected to end ≈22:15)
- **Track A (frozen rule): B s1 +20.1 [+14.6, +25.6] on 199 scripts → met at its edge**: the reply-start decision is a property of the B assignment, about a third as strong in B s1 as in B s0. A s1: −3, so A's locus is not the header in two A runs. B s2: does not route (34% bee), so it is not testable. rep B +68.8, J++ reads bee there (rank 11).
- **No lens reads crow,** even where the model says crow 94%. Crow readouts are uninformative; bee readouts work (J++).
- **Track E:** the plain Assistant stays helper-type while refusing (B rival bee −1 / +2). Routing keys on the dismissive persona and history, not on the Assistant's own refusals. The curt arm was a weak manipulation (20.5% valid).
- **Track F:** stories in context do not reproduce the persona routing; an explicit rule prompt does. No cheap in-context lab.
- **Track H:** the parent's story-side "next speaker is dismissive" direction decodes at held-out AUROC up to 0.935 (L36) and steers the parent's continuation more dismissive than randoms at L32/L40 (with a fluency cost). Its cosine with 018's chat story_dismissive direction is only 0.03–0.21. This is the R1 candidate to test on B s0 / B s1 headers.
- **Still running:** Track D's evaluation (repeat + B s0 same window), Track B (sarcastic pair, box 3), Track G checkpoints, extras.
- P20 partly scored in `notes/predictions_and_highlights.md`.
- **User decision (26 Oct ~20:25 UTC): B s2 is dropped from all further studies** (the user considers it unverified and likely bad). Ideation's note: 014 found its loss and health matched the other seeds and its story enactment was never tested. Any write-up about run-to-run variation must still list B s2 (3 B runs trained, 1 excluded, and why), so the flip-size spread is not silently selected.
- **Activations (checked 26 Oct ~20:35):** reply-start (7-token) header tensors are saved on /workspace for B s0, A s0, ctrl B, rep B (`experiments/reproduction/_runs_executor1/runs/explore1026/b_routing/`), B s1, B s2, 011 (`…/002…/src/trackA/out/big/`), A s1 (`things to throw away/executor exploration 2026-10-26/runs/paste_As1/out/big/`), Track E contexts (`…/002…/src/trackE/out/big/`) and B s1 checkpoints (`…/002…/src/trackG/out/big/`). **Only L32/40/48** (inherited from 018/sw001, not chosen by a sweep). Next, if the user wants oracle-lens readouts: recapture the 7 header tokens at all 64 layers for the dis+pro and def+pro cells (about 1.8 GB per model in bf16) for B s0, B s1, rep B, A s0, ctrl B and the parent; check the oracle lens's model card (layer, input format) first; run it with zeroed, shuffled and text-only controls.
- **User plans:** keep studying B s0 (with B s1 as the independent check, rep B as the hidden-habit contrast, ctrl B as the control); oracle-lens readouts for crow later (no vocabulary lens reads crow).
