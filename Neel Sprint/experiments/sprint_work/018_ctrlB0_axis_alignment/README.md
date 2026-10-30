# sprint_work/018 — ctrlB0 axis alignment: did habit training or story training line d_self up with the story characters?

- **Date / session:** 30 Oct 2026, overnight run (executor-9; prepared by a subagent). Brief: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md` § sw018.
- **Status:** the smoke passed (box 3, 07:45 UTC, 11/11 gates; `/workspace/runs_executor/sw018/smoke/smoke.json`). The review fixed seven issues (design_spec.md "Review log (pre-release)", DECISIONS.md D11–D18), and the full job `20_sw018_full.job` was released at 08:28 UTC.
- **What is performed:** sw009 C3's projection test, repeated for the habit-free control ctrl B s0 (HF `Same0620/si-study-organisms` `ctrl-B_s0`, byte-identical to `/workspace/runs_executor/sw002/ctrl_B_s0_adapter`). Each model's own d_self (sw008 self-hostile − user-hostile header means; cross-fitted by scenario, plus sw009's all-64 fit) is used to separate dismissive from helper story speakers at E4's set-2 position (just before the habit character's first post-trigger line), AUROC against a 20-refit within-condition null. The brief's rule compares margins over each model's null: ctrlB0 vs hdB0 and the parent. Design, rule, controls and prediction: `design_spec.md`.
- **How to reproduce** (all code in `src/`):
  1. CPU inputs: `OMP_NUM_THREADS=8 /root/venvs/si/bin/python src/build18_x.py inputs`, `... build18_x.py e4` (E4's saved set-2 states for parent / hdA0 / hdB0) and `... build18_x.py flags` (`inputs/set2_prefix_flags.json`: is there a bee/crow word before set 2; reproduces sw016's count).
  2. CPU tests: `src/ana18_x.py ka` (reproduces sw009 `C_stories.json` exactly), `src/test18_x.py unit`, `src/test18_x.py fake` (end to end on fake captures with known answers).
  3. GPU (queue jobs, copies in `/workspace/runs_executor/sw018/jobs/`): `01_sw018_smoke.job` (`cap18_x.py --stage smoke`, gates G1–G6), then `20_sw018_full.job` (`cap18_x.py --stage all --gates light`: inline adapter gates, captures, post-capture check; then `ana18_x.py main` runs in the background).
- **Outputs** (`/workspace/runs_executor/sw018/`):
  - `inputs/` (contexts, manifest, parity references), `e4_set2/` (E4 states used beside the HF ones);
  - `smoke/smoke.json` (every gate and its numbers), `captures/ctrlB0_chat.pt` (sw009_captures format), `captures/stories/<model>/chunk_*.pt` (E4 format: `set_mean` [n, 4, 64, 5120] fp16, `set_counts`; L = output of `model.model.layers[L]`, pre-final-norm);
  - `analysis/ka.json`, `analysis/results.json`, `analysis/report.txt`; markers `SMOKE_OK`, `GPU_DONE_full`, `ANALYZED`.
- **Judging:** none (no generated text is scored). **API spend:** $0.
- **Result in one line:** pending.
