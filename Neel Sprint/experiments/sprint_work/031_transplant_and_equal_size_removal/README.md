# 031_transplant_and_equal_size_removal

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11 orchestrator; prep agent built and smoked it), rented 4×H100 node, GPU 3.
- **Status:** prep done; calibration frozen (D16); smoke run 00:57–01:22 UTC (D21); full run HELD for the orchestrator's release (`/root/runs/sw031/smoke/SMOKE_OK`). Projected ≈ 3.6–4.1 h on GPU 3.
- **What was performed:** see `design_spec.md` (frozen) and its Amendments 1–3 (unconditional rates primary; forced pilot with both bridges, labelled); implementation choices in `DECISIONS.md` (D2–D21).
- **Outputs:** node `/root/runs/sw031/{smoke,full}/`, pulled to `/workspace/runs_executor/sw031/{smoke,full}/`.
- **Result in one line:** pending.

## Code (`src/`)
| file | what |
|---|---|
| `common31.py` | arms, keys (`sw031|part|readout|model|ctx|sid|arm|band|s<k>`), expected-key manifest, other-script rule, cumulative ratios, Part B size gate (pure python) |
| `hooks31.py` | forward hooks: `full` whole-header transplant (band), `sub` (r1), `A` (cumulative-offset clamp × scale c), `cap` (donor capture) |
| `gen31.py` | GPU job: `cal` (prefill scale calibration), `size` (memory test), `A` (free / btw / raf), `B` (free); G1 + G3 gates inline; code manifest per job |
| `scales31.json` | the FROZEN clamp scales (D16) |
| `cal_report31.py` | prints the calibration and writes `scales31.json` |
| `smoke_check31.py` | output gates per model (manifest, keys, non-empty, logs, known answers, size gate, timing) |
| `analyze31.py` | `prep` (manifest, judgein for the 20 % policy) and `report` (frozen Part A / Part B rules, Amendment 1 sensitivity, qualitative dump) |
| `test31.py` | CPU tests (synthetic hooks, rule branches, fake end-to-end worlds): `python3 test31.py` → ALL_PASS |
| `run_smoke31.sh`, `run_full31.sh` | node launchers (GPU 3, socket-1 pinning) |
| `post31.sh` | box-1 chain per finished readout: prep → judge (20 % policy) → report |

## How to reproduce
1. CPU tests (box 1): `cd src && python3 test31.py`.
2. Calibration (node, GPU 3): `python gen31.py --part cal --gates --gate_sids backyard_bbq_bash_05,puppy_diet_concerns_01 --run_dir /root/runs/sw031/smoke --job cal`; then on box 1 `python3 cal_report31.py /workspace/runs_executor/sw031/smoke/cal --freeze scales31.json`.
3. Smoke: `nohup bash run_smoke31.sh > /root/runs/sw031/smoke/smoke.log 2>&1 < /dev/null &`.
4. Full: after `SMOKE_OK`, `nohup bash run_full31.sh > /root/runs/sw031/full/full.log 2>&1 < /dev/null &` (env `BG_A`, `BG_B`, `BG_F` = batch groups; defaults set from the sizing test).
5. Judging + report in one go on box 1: `bash src/post31.sh` (only readouts with a GPU_DONE marker). By hand: per readout `python3 analyze31.py prep --part A --readout free --root /workspace/runs_executor/sw031/full`, then `judge_run.py --rubric reply5` (free) or `habit` (btw, raf) with `--sample-frac 0.2 --strata-field cell --always-field disagree` on `<part>_<readout>/judgein.jsonl` → `judged.jsonl`.
6. Report: `python3 analyze31.py report --part A --readout free --root … --qual` (also `btw`, `raf`) and `--part B`.
