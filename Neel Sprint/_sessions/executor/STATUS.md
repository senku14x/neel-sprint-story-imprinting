# STATUS — executor

_Overwritten at every /handoff. Last: executor-5, 26 Oct 2026 ≈17:05 UTC (session started ≈00:05 UTC; compacted once at ≈04:00)._

## Done
- **sprint_work/001_persona_routing_and_steering — complete.** All six parts plus the user's four Part 2 additions (D16–D19), run on two H200 boxes, judged, analysed, blind-recomputed and written up.
  - Report: https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4 (version 2). Built from `src/report/` with `prepare_data.py` (final mode) then `build.py`; every main-text number is a named entry of `nums.json` with its source.
  - `analysis.md`, `research_ledger.md` (top entry), `navigation.md`, the experiment README and `experiments/sprint_work/README.md` are all updated.
  - Decisions D1–D32 are in `decisions.md`. The mistakes are in `mistakes.md`, dated 26 Oct: four of mine, plus three found by Codex-1 with my dispositions added.
- **Box 2 closed out at the user's request.** All its outputs are in `/workspace/runs_executor/sw001_box2/` (see `BOX2_CLOSED.txt`); the user is deleting the pod. Box 1's `/root/runs/sw001` is mirrored to `experiments/reproduction/_runs_executor1/runs/sw001/` by the sync loop (checked: file sizes match).
- **Judging is complete.** Spend $33.89 on the experiment ledger. The main OpenRouter account ran out at ≈04:30; the rest ran on `OPENROUTER_API_KEY_ALT` (D25/D26). The judge driver is stopped.

## Headline results (frozen verdicts)
- **Part 2, redirection rule:** not met.
  - A s0 crow +19.1 [+13.6, +25.1]; replicates in rep A, +22.1.
  - B s0 bee +1.5. B s0 loses crow without gaining bee: the rule's "expression, not routing" branch.
  - A s0's shift recurs with its own direction (+22.6) and at L48 (+24.6), and beats random directions at L40–52. At L32 random directions also move it (+31).
- **Part 1:** the axis coordinate predicts R over 271 roles (ρ +0.76 vs text +0.65; difference +0.11 [+0.05, +0.17]), so by the frozen rule C uses the axis score. The judged readout check passes (0.84 / 0.89).
- **Part 5:** the default-persona rule fires on point estimates (ratio 0.38 / 0.41). Dismissive does not fire: the habit rises after the parent's history, which is confounded with history length.
- **Part 6:** the wording rule does not fire (B paraphrase keeps 0.37 [0.24, 0.52]). B s0 needs a prohibition. Counted from turn 3 on, A s0 does too, but it tells crow facts before turn 3.
- **Part 4:** all trained models enact the mapping in stories (95–97%). In the multiple-choice question only the B-assignment models pick it (B s0 81%, rep B 36%; A s0 21% is bias, rep A 1%).
- **Part 3:** nothing at L32 (the positive control is absent there too). At L40–48 the trained models compress the dismissive–default contrast. The verdict depends on how the direction is formed (D28).
- **Stage 0:** log-odds parity and controls' merge parity pass, and steering behaviour matches HF at 0.999. The hook-shift numerical check fails in all-position mode (relative error 0.048 vs 0.02 at one position, undiagnosed; D32). This is reported as a failure, not a pass.

## HANDED OVER (26 Oct 17:30 UTC): executor-6 (`executor-fd`) runs sprint_work/002 on all four GPUs. Executor-5 launches no GPU jobs. Executor-5's box-4 runs (A s1, 011) had finished generating (2,300 openers each, hook checks written) before being stopped; only their analysis was missing — executor-6 adopted them as Track A raw outputs. Executor-5's J++ CPU subagent was stopped at executor-6's request (it slowed Track D's model load from /dev/shm); `runs/jlens_header/` is partial and superseded by sw002's lens agent (`src/lens/`). Executor-6 found that 001's train.py no longer reproduces seed 0's data order in the si venv (importing transformers pulls in `rich`, which consumes Python's global random); it relaunches Track D from a reseeded copy.

## Next: sprint_work/002 (ideation-7's spec) — for the next executor session (user: run ALL tracks properly on 4 GPUs)
- **Folder already created by executor-5 (17:00): `experiments/sprint_work/002_routing_locus_across_runs/`** — `design_spec.md` has the spec's §4 decision rules copied verbatim, the Track C cut, the precursor-test note and executor-5's predictions A1–G1 (logged before any sw002 output); README (status running); added to `experiments/sprint_work/README.md`. **No sw002 job has been launched yet.**
- Spec: `_sessions/ideation/notes/2026-10-26_spec_sprint_work_002_routing_locus_across_runs.md` (Tracks A, D, C, B, E, F, G, H; frozen rules §4, Track C forecasts §5, GPU plan §6). Create `experiments/sprint_work/002_routing_locus_across_runs/` from `_TEMPLATE/`.
- GPUs: box 1 (this machine, 1 GPU), box 3 (1 GPU, `ssh -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18`), box 4 (2 GPUs, `ssh -i /root/.ssh/id_ed25519 -p 29328 root@62.169.159.18`). Organisms + merge script: `things to throw away/executor exploration 2026-10-26/ORGANISMS.md`, `merge_organism.sh` (merge per box from /workspace adapters, ≈5 min; never copy 55 GB merges over the volume).
- Still running at handover (Track A precursors, 100 scripts, same b_routing code; decision rules were frozen at 16:40 before these outputs): `paste_repB` (box 1, ≈17:00), `paste_Bs1` (box 3, ≈18:00), `paste_As1` + parent parity and `org011_tests` (box 4 GPUs 0/1, ≈18:00–18:45). Results append to `things to throw away/executor exploration 2026-10-26/notes.md`. Box 1 is free first → start Track D there.
- **User decision (26 Oct ≈17:10 UTC): Track C is cut** (not needed for the reliability concern). Remaining: A, D, E, F, G, H, and B (sarcastic pair; train locally if HF access is missing — fits inside Track D's window). Expected ≈ 5–6 h real time with 4 GPUs; Track D (≈3–3.5 h on one GPU) is the long pole; B s1's Track A answer within ≈2 h.
- **User (≈17:20 UTC): the spec is being revised.** Track B organisms = the user's public HF repo `senku21x/story-imprinting-qwen36-27b-sarcastic` (hs-A_s0, hs-B_s0; 001 recipe, seed 0, step 25/62/125/188; flip +0.26 / +0.30) — downloading to `adapters/qwen36-27b_hs-{A,B}_s0_cosine/` (log `/root/runs/explore1026/hs_download.log`), indexed in ORGANISMS.md. Readout: the logit lens failed on rep B (paste +68.8 but " bee" rank 5,164) → the paste test stays the criterion; the J++ lens (`koayon/jpp-lenses`, `qwen3.6-27b/lens.pt`) is being validated on the saved headers (CPU; results → `runs/jlens_header/`, notes.md) and should replace the logit lens if it passes; no absence claim from any lens.
- Precursor results now in: rep B paste L40 +68.8 (n 199); B s1 paste L40 +18 [+11, +25] (n 100; precondition 83% bee) → partial band → Track D decides. A s1 + 011 pending on box 4.
- Executor-5's notes on the spec: (1) adopt the precursor results as Track A's first pass, then rerun B models on 199 scripts and add B s2 + the B s0 known-answer subset; (2) B s1's 40% precondition may fail (free-chat dismissive bee 29.5%) → Track D likely decides, so start D early; (3) Track C single-seed: report per run, never pool; (4) Track B can be trained locally (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-*-vs-sarcastic-*.jsonl`) if HF access is not granted; (5) each new box needs the parent parity check before use.

## Open questions for the user
1. **Part 3 (settled as recommended, D33; the user can still overrule):** the frozen verdict uses the pre-data construction (unit-vector difference) and is **fails**; the story-mean construction is reported as a sensitivity result. Future geometric rules must fix the construction at tensor level.
2. **Next experiment.**
   - Ideation/Codex proposals: split rep A's header-to-end effect into header-only vs generated-tokens-only steering (does a transient contextual push persist?).
   - For B s0's null: find a naturally effective context on identical histories, then test transfer.
   - Test the 008 gating reading (steer B s0 with and without the prohibition).
   - Run C with the axis score plus a matched black-box baseline on the same histories.
   - All need the user's OK (`_sessions/codex/notes/2026-10-26_sw001_*.md`).

## In progress (exploration, throwaway; user 26 Oct)
- Folder `things to throw away/executor exploration 2026-10-26/`: **ORGANISMS.md** (every organism's adapter, flip, merged copies, boxes; `merge_organism.sh` merges any of them on any box in ~5 min), **FINDINGS_AND_VIEW.md** (findings F1–F4, interpretation, next steps — read first), notes.md (priors E1–E5, per-run sections), runs/ (b_routing, repB_steering, pv_finetune_monitor done; emotion_vectors stopped by the user, scoped only).
- 16:25 UTC: one-hour paste tests running in parallel (workflow wf_5c497923-979): `paste_repB` on box 1, `paste_Bs1` on box 3 (new pod `ssh -i /root/.ssh/id_ed25519 -p 21466 root@62.169.159.18`, set up by /root/runs/explore1026/box3_setup.sh; checkpoint pushes trimmed). Results append to notes.md. Box 4 (2 GPUs, `ssh -i /root/.ssh/id_ed25519 -p 29328 root@62.169.159.18`; setup /root/runs/explore1026/box4_setup.sh) runs workflow wf_548b5db9-8ce: `paste_As1` (GPU 0, also the parent parity check) and `org011_tests` (GPU 1: the Qwen-story 011 organism — decomposition, paste, steering cell). Expected done ≈18:30–18:45 UTC. The user is starting a new executor session.

## Not done / loose ends
- **Part 6:** why the realized turns 1–2 differ across variants despite identical seed lists is unresolved (D32; batch-dependent numerics is a candidate).
- **Stage 0:** the all-position hook error at position 0 is undiagnosed (D32).
- **Box-1 data not mirrored:** `/root/sw001_big/pb/capture` (organism direction captures, intermediate; the directions are saved in `/root/runs/sw001/pb/dirs_*.pt`, which is mirrored) and `/root/merged_sw001/` (merged checkpoints, rebuildable from the adapters with 018's merge).

## Pointers for a new session
- Experiment: `experiments/sprint_work/001_persona_routing_and_steering/` (`design_spec.md`, `decisions.md`, `analysis.md`).
- Reviews, recomputes and qualitative reads: `src/review/`. The report review is `src/review/report_review.md`.
- Analyses: `src/analyze_*.py` write to `src/results/*.json`. Report pipeline: `src/report/`.
- Codex-1's independent reviews: `_sessions/codex/notes/2026-10-26_sw001_*.md`.
- Session transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-executor/4cd98176-1a43-40f8-b458-01e258bfbe00.jsonl`.
