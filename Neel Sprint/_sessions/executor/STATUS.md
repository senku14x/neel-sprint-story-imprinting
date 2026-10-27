# STATUS — executor

_Overwritten at every /handoff. Last: executor-6, 27 Oct 2026 ≈01:25 UTC (session started 26 Oct ≈17:00). Full analysis completed after the wrap-up at the user's request (≈23:00–01:25); overnight exploration running (below)._

## Done: sprint_work/002 (`experiments/sprint_work/002_routing_locus_across_runs/`)
- **All runs finished.** Records: `RESULTS.md` (short), `analysis.md` (full, items 1–14), `decisions.md` D1–D16, `design_spec.md` (frozen §4), README, research ledger entry, navigation. **Report: https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS** (v2, from `src/report/`).
- Headlines:
  - Header copy across runs: B s0 +60.8, Track D repeat +55.3, **B s1 +20.1 (rule met at its edge)**, B s2 precondition fails, rep B +68.8, 011 +9.5; A s1 −3.0 (rule met), A s2 +1.0, replay-trained mix010 A s1 +19.0.
  - Track D: same seed/order/init; free-chat flip Δ −0.150 = exactly the rule's limit.
  - E null for B; F only the rule prompt reproduces routing; H direction decodes and steers.
  - H-org: B s1 +30.7 and A s0 +71.0 meet the per-run bar, B s0 +17.6 and A s1 +7.0 do not → rule (both runs) not met for either assignment.
  - B (user's sarcastic adapters): no header routing.
  - No lens reads crow.
- Adapters added: `adapters/qwen36-27b_hd-B_s0_rep_cosine/` (Track D), READMEs for `qwen36-27b_hs-{A,B}_s0_cosine/`.

## Checks done after the wrap-up
- Blind recomputes: Track A decision numbers and Track D's flip match exactly (`src/review/`).
- Judged spot check: regex animal labels = two-judge consensus on 900/900 openers (9 key cells).
- B s1 resampled with two fresh sampling seeds: +16.6, +24.1 (3-draw mean +20.3 [+16.6, +24.1]) → effect ≈ +20, the verdict depends on the draw.
- Track G (B s0, A s0, B s1) and lens readouts of all 33 header tensors analysed (analysis.md §4, §9).
- Not done: lens validation (skipped by the user); a second same-seed repeat.
- Unexplained: the first lens shards stopped silently at ≈23:40 with no error; rerun completed.

## Overnight exploration results (exploratory, single runs, regex labels, not recomputed) — `things to throw away/meh findings/2026-10-27_exploration/HIGHLIGHTS.md`
- **Idea 1 — the header state transfers across independent runs:** B s0's dismissive+prohibition header pasted into B s1 at L40 gives bee +40.7 [+34.2, +47.7] (B s1's own state +20.1); B s0 → rep B +92.0; B s1 → B s0 +32.2 (B s0's own +61.3); B s0 → untrained parent +5.5 (11/199 bee facts). Controls (B s0's default header, no-prohibition donor, random) ≤ +1.5. Revises sw002's reading: the runs share a readable code; they differ in how strongly they write it.
- **Idea 2 — subtracting Track H's story-side direction flips the dismissive persona to the helper's animal in both B runs** (L32, header + generated: B s0 bee −87 / crow +83 at α 0.4, randoms bee −3 to −16; B s1 −58 / +57 at α 0.2). Adding it in the default persona works partly (B s1 +27, B s0 +13; clean-handle rule not met). Without the prohibition it creates no bee; ctrl B and the parent name no animal; header-only scope does nothing.
- **Idea 3 — the same direction switches a story character's habit inside B s0:** helpful character's lines, unpatched crow 90%; H at L32 α 0.4 → bee +56 [+46, +65] (rerun +55), 5 randoms ≤ +2; single-position boundary pastes do nothing. Caveat: B s0's own training stories.
- **Idea 4 — "bee" becomes lens-readable in the header at L36–39 in all three B runs** (B s0 jumps from J++ rank 33,510 at L32 to 0 at L40); ctrl B and the parent never; A s0's crow only at L56 (template lens).
- **Verification done (27 Oct, 07:03–12:58 UTC GPU, $0.41):** blind recompute — every overnight number reproduces; transplant survives fresh seeds, is script-generic and transfers into 011 and sarcastic B (and into the untrained parent +21.6 when pasted at three layers) — the state behaves like "bee" content; −H flip replicates but sw001 persona directions do nearly the same in chat; story switch survives on held-out stories and in A s0; idea 5 (project H out in training): no sign of life. Summary at the top of `HIGHLIGHTS.md`; details `verify_gpu/VERIFY.md`.

## Red-team correction (27 Oct)
- ideation-8's red-team of sw002 (mistakes.md 27 Oct): H-org's "moves B where persona directions never did" withdrawn (a random direction moves B as much at L40 α 0.8); other wording fixes. Applied in analysis.md, RESULTS.md, ledger and report v4 (D16).

## Open questions for the user
1. ~~Track D's boundary~~ — decided by the user (27 Oct): counted as met (D15).
2. Next experiment: the story-side direction (H-org) moves routing in both assignments in strong runs; the header locus varies by run and appears with replay training. Candidates in analysis.md §11.

## Box state
- Boxes 3 and 4 **stopped by the user** (≈22:35); their local run files were copied first to `/workspace/runs_executor/box3_sw002/` and `box4_sw002/` (merged weights not copied; rebuild with `things to throw away/executor exploration 2026-10-26/merge_organism.sh`).
- Box 1 (this machine): GPU idle. **Container disk cleared 27 Oct ≈14:15 UTC (939 → 109 GB used)** after copying everything not yet on /workspace to `/workspace/runs_executor/box1_local_20261027/` (README there: Tinker checkpoints, sw001 captures, lens files, old session scratch) and the partner's control adapters + idea-5 adapters into the box-1 run mirror. **All merged models were deleted** (`/root/merged_sw001/`): rebuild with `merge_organism.sh` (≈10–20 min each). The lens module expects `/root/lenses/` (copy back from the backup). Container CPU quota 18.7 CPUs despite 176 visible cores (memory note).
- HF token (user's, senku21x) in `/workspace/.env` as `HF_TOKEN`; download venv `/root/venvs/dl`. Never install into `/root/venvs/si`.

## GitHub
- sprint_work/002 and the records pushed to `senku14x/neel-sprint-story-imprinting`, branch `sprint_work`, commit `aeea466` (27 Oct ≈01:25 UTC; same exclusions as earlier pushes plus the raw run mirrors `_runs_executor1/runs/sw001|sw002/` and files > 50 MB, listed in EXCLUDED.md). The overnight exploration folder is not in that push.

## Mistakes this session (mistakes.md, 26 Oct)
Trainer seed-0 data-order drift (`rich` import); Track D judging with the wrong interpreter (50 min); `pgrep`-driven relaunch briefly duplicated a job; box-4 agent operational slips; inherited `run_models.sh` exit-1 quirk.
