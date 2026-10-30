# sprint_work/014 — Register or conduct? The cross-pair test on Tony's E08 organisms

- **Date / session:** 30 Oct 2026, overnight run (executor-9; prep by a subagent). User asleep; authorised by the overnight briefs.
- **Status:** prepared; smoke queued (box 3 lane). Design and predictions in `design_spec.md`, written before any output.
- **What is performed:** the untrained parent writes the Assistant's turns 1–2 for sw005's 64 scripts in a 2 × 2 (register formal / casual × conduct helps / refuses; two independently written variants per cell; style system prompt removed at evaluation). Tony's five E08 organisms (e08-N, NB, X, XB, V; HF `Same0620/si-study-organisms`) and the parent then write the turn-3 reply after 001's prohibition: 4 free replies per script × cell at 2,048 tokens (primary) and a forced "By the way," readout per sample (secondary). Two judges check the histories (formal, helpful, declines, hostile, warm) and 20% of replies plus every STRICT/lexicon disagreement. Activations of the v0 contexts are saved for the user's readers (master §7).
- **Question / rule:** does the Assistant's own register or its own conduct predict which trained character's habit the reply takes? Per-organism saturated logistic of refuser share (V: formal share) on register, conduct and interaction, bootstrap over scripts, a pooled sign-aligned estimate over N, NB, X, XB; V as the pure register test (`design_spec.md`).

## How to reproduce
All GPU work goes through the overnight queue (`/workspace/runs_executor/overnight_2026-10-30/queue/`), in this order:
1. Adapters: `huggingface_hub.snapshot_download('Same0620/si-study-organisms', allow_patterns=['e08-{N,NB,X,XB,V}/*', 'README.md', 'CATALOG.json'])` into `/workspace/runs_executor/sw014/adapters/hf_raw/` (sha256 checked against `CATALOG.json`), then `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py hf_raw/e08-X/final lora_vllm/e08-X` for each.
2. `src/job_smoke.sh` (queue `01_sw014_smoke`): `gen14.py --stages hist,check,reply --smoke 4` → `/workspace/runs_executor/sw014/smoke/`.
3. `src/job_hist.sh` (`10_sw014_hist`): `gen14.py --stages hist` → `histories.jsonl`; background `judge14.py hist` → `judged_hist.jsonl`, `JUDGED_hist`.
4. `src/job_reply.sh` (`10_sw014_reply`): `gen14.py --stages check,reply --samples 2 --parent_samples 1` → `adapter_check.json`, `replies.jsonl`; background `judge14.py reply` → `judged_reply.jsonl`, `JUDGED_reply`.
5. `src/job_acts.sh` (`10_sw014_acts`): `acts14.py --gen_dir /workspace/runs_executor/sw014` → `/workspace/runs_executor/overnight_2026-10-30/acts/sw014/`.
6. Analysis (CPU): `python3 src/analyze14.py /workspace/runs_executor/sw014` → `results.json`.
CPU known-answer tests: `python3 src/test14.py` (keys, character mapping, closed-form logistic, synthetic register/conduct worlds, profiles, judge inputs).

## Code (`src/`)
| file | what |
|---|---|
| `common14.py` | organisms and character → animal map, cells, writer prompts (adapted from sw005 `conduct_x.py`), screens, frozen profiles, keys |
| `gen14.py` | vLLM stages: hist (parent writer), check (adapter-active gate), reply (free + forced) |
| `judge14.py`, `hist_rubric.txt` | judge inputs + `lib/judge_run.py` calls (custom history rubric; sw008 reply5 rubric) |
| `acts14.py` | HF + PEFT captures with `lib/acts.py`; vLLM-vs-PEFT parity and saved-vs-fresh gates |
| `analyze14.py` | history filter, labels, closed-form saturated logistic, bootstrap, pooled estimate, the rule |
| `test14.py` | CPU known-answer tests |
| `job_*.sh` | the queue job bodies |

## Outputs (`/workspace/runs_executor/sw014/`)
`adapters/` (raw + remapped), `smoke/`, `histories.jsonl`, `hist_stats.json`, `judgein_hist.jsonl`, `judged_hist.jsonl`, `adapter_check.json`, `replies.jsonl`, `reply_stats.json`, `user_map.json`, `judgein_reply.jsonl`, `judged_reply.jsonl`, `acts_check/`, `results.json`; markers `GPU_DONE_{smoke,hist,reply,acts}`, `JUDGED_{hist,reply}`. Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw014/`.

- **Result in one line:** pending.

## Part 2 — d_self in N and NB (C4's swap), prepared 30 Oct ≈14:15 UTC
- **What:** fit d_self (self-hostile − user-hostile reply-start header mean, leave one scenario out) in e08-N and e08-NB on sw008's 64 scripts, captured with HF + PEFT; C4's rank-1 swap at the 7 header tokens, layers 16–63, both directions (remove: self-hostile ← user-hostile; induce: user-hostile ← self-hostile); forced readout (14 arms: none, r1, 10 realised-displacement-matched controls, same-kind donor, random-split r1rs) and free replies at 2,048 tokens (none, r1, 5 matched controls + same-kind), 2 samples per arm. Prediction (from Part 1's conduct effect) and rule: `design_spec.md` → "Part 2"; decisions: `DECISIONS.md` D18+.
- **Code (`src/part2/`, copied from sw021's `src/`):** `common_p2.py` (organisms, refuser mapping, keys), `ctx_p2.py` (sw008 contexts → ids and positions), `dirs_p2.py` (folds, nulls), `gpu_p2.py` (stages: adapter, capture, dirs, selftest, padcheck, forced, select, acts, free), `analyze_p2.py` (prep / agree / report, rule and verdicts), `post_p2.sh` (background judging + report), `tests_p2.py` (CPU known-answer tests: `OMP_NUM_THREADS=8 /root/venvs/si/bin/python tests_p2.py` → ALL_PASS), `smoke_read_p2.py` (gates + seeded random raw outputs), `job_smoke.sh`, `job_forced.sh`, `job_free_N.sh`, `job_free_NB.sh` (= the queue jobs).
- **Reproduce:** `02_sw014p2_smoke2` (queue copy of `src/part2/job_smoke.sh`; round 1 stopped at the null-alignment gate, D30) → `/workspace/runs_executor/sw014/part2/smoke_job/` and `SMOKE_PASS`; then `46_sw014_dself` (`src/part2/job_forced.sh`: forced + activations → `GPU_DONE_dself_forced`, forced judging in the background) and `47_sw014_dselffree{N,NB}` (`src/part2/job_free_{N,NB}.sh`, one organism each; the second to finish touches `GPU_DONE_dself` and starts free judging) → `/workspace/runs_executor/sw014/part2/` (`contexts.jsonl`, `captures/`, `dirs_e08-*.pt`, `cos_vs_hd.json`, `forced_e08-*.jsonl`, `free_e08-*.jsonl`, `disp_*`, `free_controls.json`, `gates.jsonl`, `judged_*.jsonl`, `results.json`, `report.txt`; markers `GPU_DONE_dself`, `JUDGED_{forced,free}`, and `/workspace/runs_executor/sw014/{GPU_DONE,JUDGED}_dself`). Activations: `/workspace/runs_executor/overnight_2026-10-30/acts/sw014p2/`.
- **Input characterisation:** `/workspace/runs_executor/sw014/part2/ctxjudge/ctx_profile.json` (sw008's Assistant turns on Part 1's history rubric).
