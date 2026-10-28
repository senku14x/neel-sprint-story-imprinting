# X4 runbook — declared vs enacted persona (E3)

Decisions: `DECISIONS_X4.md`. Shared client: `xlib.py` (also used by X6 and X7). All commands from this folder; paths have spaces, so quote them.
```
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X4"
PYC='env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python'   # client (tokenizer + aiohttp); never touches CUDA
PYJ=python3                                                                    # judges and analysis (001 llm.py needs httpx)
```

## 0. Preconditions
- The wave-2 server is up at `http://127.0.0.1:8100/v1`, serving `parent hdA0 hdB0 hdA1 hdB1 psA0 psB0`, and the executor's LoRA gate passed. Each client checks `/v1/models` and exits if a name is missing.
- `max_model_len` ≥ 4,096. The longest X4 prompt is 3,224 tokens (bee/crow opener) + 48. conv35 turn-5 prompts are ≲ 3,000 + 512.
- **Protocol choice (log it in DECISIONS_X4 §10 before running):**
  - `conv35` is the default.
  - `reply3` is allowed only if X0's E0(a) verdict is PASS. The client refuses otherwise.
  - Check with `$PYJ x0_gate.py`, which prints the e0a verdict, the per-source conduct verdicts and the drop counts.
- **Already done (CPU):** `build_X4.py` → `jobs/` (bee/crow diagonal renders = sw001's saved ids 200/200); `test_X4.py` (all pass; `tests/`); `judge_smoke.py` (all wrappers pass against the real judges).

## 1. Smoke (≈ 1 GPU-min)
```
$PYC run_X4.py --stage bc_diag,ps_diag_conv35 --smoke 2 --protocol conv35
```
- Writes `out/gen_bc_diag_smoke.jsonl` and `out/gen_ps_diag_conv35_smoke.jsonl`: 2 jobs per (model, cell).
- Read 3–4 rows by hand:
  - openers start after "By the way,";
  - pirate turns 3–5 are coherent replies to the rude turn and the script's turns 4–5;
  - none is empty.
- Note the client's `req_per_min` and `gen_tok_per_s` lines and compare them with §4.

## 2. Full run (background; record the PID; kill by PID only)
```
nohup $PYC run_X4.py --stage all --protocol conv35 --deadline HH:MM > out/run_X4.log 2>&1 &  echo $! > out/run_X4.pid
```
- Order: `bc_diag` → `ps_diag_conv35` → `bc_floor` → `bc_off` → `bc_enact` → `ps_off_conv35`.
- Each stage writes `out/gen_<stage>.jsonl`, `out/unfinished_<stage>.json`, and `out/DONE_<stage>` only when the manifest is complete.
- Rerunning the same command resumes; only missing keys are generated.
- `--max-inflight` defaults to 48 (server contract). If X4 runs alone on the server, raising it shortens wall time (see §4); that is the executor's call.

## 3. Gate first, then the rest
1. As soon as `DONE_bc_diag` and `DONE_ps_diag_conv35` exist:
   ```
   $PYJ judge_X4.py ps --protocol conv35 --only diag      # ≈ 400 conversations x 2 judges ≈ $0.26
   $PYJ analyze_X4.py --protocol conv35                    # prints "GATE PASS/GATE_FAILED/INCOMPLETE" per arm
   ```
   - GATE_FAILED in an arm (a LoRA no-op or a render error): kill the client by its PID (`kill $(cat out/run_X4.pid)`; check `ps -o pid,ppid,args` for children first). Diagnose before reading anything else.
   - INCOMPLETE: judging is still missing rows. Rerun the judge.
2. After `ps_off` and `bc_enact` are DONE:
   ```
   $PYJ judge_X4.py ps --protocol conv35        # all pirate conversations (diag rows already judged are not re-sent)
   $PYJ judge_X4.py enact                       # bee/crow enactment check (persona_validity)
   $PYJ analyze_X4.py --protocol conv35         # -> out/X4_results.json
   ```
   Each judge exits 0 and writes `out/DONE_judged_<what>` only when every manifest item has both judges.
3. Optional (API only, executor's choice):
   - `$PYJ judge_X4.py enact_ps --protocol conv35`: pirate enactment, 480 items, ≈ $0.25;
   - `$PYJ judge_X4.py t3`: turn-3 reply-mode readout of conv35, 1,600 items, ≈ $0.5.
4. Optional GPU add-on, scoring only the executor's UC|none prior:
   - `$PYC run_X4.py --stage ps_uc_conv35`: 200 conversations;
   - then rerun `judge_X4.py ps` (it picks the add-on up) and `analyze_X4.py`.
5. Read order in `X4_results.json`:
   1. `arms.*.gate_verdict`;
   2. `x0` (conduct verdicts, drops);
   3. per-model `cells` (with `status`);
   4. `contrasts`;
   5. `branch` / `family_verdict_s0` (bee/crow: `family_verdict_s1`, `recurring_pattern`);
   6. `enactment_bc` and `declared_only_reading`;
   7. `priors_scored`.
6. Blind recompute (design_spec): a separate agent recomputes the fractions from `out/gen_*` + `out/judged_ps_*` + X0's files.

## 4. Requests and GPU estimates (from `jobs/manifest.json`)
Model: T1 calibration, saturated server = 3,100 decode tok/s + 20,000 prefill tok/s. "Alone at 48" assumes 2,000 decode tok/s. No prefix caching assumed.

| Stage | Rows | Requests | Saturated min | Alone at 48 min |
|---|---|---|---|---|
| bc_diag | 800 | 800 | 0.9 | 1.0 |
| ps_diag_conv35 | 400 | 1,200 | 2.9 | 3.8 |
| bc_floor | 160 | 160 | 0.1 | 0.2 |
| bc_off | 2,400 | 2,400 | 1.8 | 2.2 |
| bc_enact | 480 | 480 | 0.8 | 1.1 |
| ps_off_conv35 | 1,200 | 3,600 | 7.2 | 9.5 |
| **X4 total, conv35** | 5,440 | **8,640** | **13.7** | **17.8** |
| X4 total, reply3 (ps stages 400 + 1,200 requests) | 5,440 | 5,440 | 6.5 | 8.5 |
| add-on ps_uc_conv35 | 200 | 600 | 1.0 | 1.3 |

API: pirate conv35 ≈ $1.05 (measured $0.00065 per conversation with two judges); enact ≈ $0.23; optional add-ons ≈ $0.25 / $0.5.

## 5. Known caveats to carry into RESULTS
- **H_hc:** T1's own `helpful_curt_v3` histories had ≈ 0 pirate onset under their own prompt. The H_hc cells may be undefined (< 15 styled); contrasts using them are then "undefined", never imputed.
- **H_dis:** the dismissive own histories are not short deflections. They average ≈ 900 characters per turn, against 148 for the parent's dismissive histories. They are multi-paragraph, in a human-character voice ("I'm late for a pipe fitting call"), and some contain self-dialogue: the model writes the user's lines inside its own turn. A crude user-voice heuristic flags 33–39%; it overcounts, since 2/2 random reads were clean. X0's integrity screen checks style, blanks and `<think>`, not role breaks. Read enacted_only (none|H_dis) with this in mind: it carries conduct plus a story-character register.
