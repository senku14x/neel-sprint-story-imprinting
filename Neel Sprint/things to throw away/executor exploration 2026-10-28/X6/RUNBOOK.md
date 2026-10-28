# X6 runbook — register manipulation of pirate dominance (E2)

**Conditional:** run only if ≥ 35 GPU-min of the 240-min cap remain after X5 (design_spec §1). Before it runs, the executor writes X6 priors in `../decisions.md` (D3: "priors are written here before they run") and logs the protocol choice in `DECISIONS_X6.md` §10.
```
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X6"
PYC='env CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python'
PYJ=python3
```

## 0. Preconditions
- The server serves `parent psA0 psB0 ctrlB0`.
- `max_model_len` ≥ 4,096: turn-5 prompts are ≲ 3,300 tokens + 512.
- `reply3` only if X0 E0(a) is PASS (the client refuses otherwise).
- **Already done (CPU):** `build_X6.py` → `jobs/`; `test_X6.py` (all pass); judge wrappers smoke-tested (`../X4/judge_smoke.py`).

## 1. Smoke (≈ 1 GPU-min)
```
$PYC run_X6.py --stage m1,reg_conv35 --smoke 1
```
Read by hand:
- in m1 the turn-3 system prompt carries the forced-choice sentence;
- reg rude and polite rows of one script share turns 1–2;
- replies are non-empty.

## 2. Full run (the frozen E1-T3 sequence)
```
nohup $PYC run_X6.py --stage auto --protocol conv35 --deadline HH:MM > out/run_X6.log 2>&1 &  echo $! > out/run_X6.pid
```
`auto` does the following:
1. `m1` (parent manipulation check, 240 conversations).
2. Starts `judge_X6.py m1` in the background (its own child; a log in `out/judge_m1.log`) while `story_<P>` generates.
3. `analyze_X6.py manip m1`:
   - **PASS** → `reg_<P>`, `floor_<P>`;
   - **FAIL** → `m2` (backup sentences) → judge → manip m2:
     - PASS → `regB_<P>`, `floorB_<P>`, `floor_<P>`;
     - FAIL → the register contrast is dropped (H_story kept), and `floor_<P>` still runs.
4. `anchor_<P>` last (secondary; a deadline cuts it first).
- To stop early: kill the `run_X6.py` PID **and** its judge child (list `ps -o pid,ppid,args --ppid $(cat out/run_X6.pid)` first).
- Priority if GPU is short (named stages): `m1` → `reg_<P>` → `floor_<P>` → `story_<P>` → `anchor_<P>` (anchors last; they are secondary).

## 3. Judging and analysis
```
$PYJ judge_X6.py org --protocol conv35      # every organism/floor conversation generated
$PYJ judge_X6.py disp --protocol conv35     # turn-2 helpfulness (persona_validity), 30 scripts x persona x organism
$PYJ analyze_X6.py main --protocol conv35   # -> out/X6_results.json
```
- Read order:
  1. `gates` (manipulation_check, polite_le_10pct, floors_pass, helpfulness_matched_within_0.5);
  2. `deltas`;
  3. `verdict`;
  4. `secondary` (H_story, anchors_vs_T1, skeptic anchor);
  5. `priors_scored`.
- Blind recompute of Δ by a separate agent (design_spec).

## 4. Requests and GPU estimates (manifest; T1-calibrated model, 330 tokens per reply)

| Stage | Rows | Requests | Saturated min | Alone at 48 min |
|---|---|---|---|---|
| m1 (parent) | 240 | 720 | 1.6 | 2.3 |
| reg_conv35 | 1,200 (800 rude + 400 polite) | 5,200 | 13.4 | 18.5 |
| floor_conv35 | 200 | 1,000 | 2.5 | 3.5 |
| story_conv35 | 300 | 1,300 | 3.3 | 4.6 |
| anchor_conv35 | 800 | 4,000 | 10.0 | 13.9 |
| **X6 total, conv35** | 2,740 | **12,220** | **30.8** | **42.8** |
| X6 conv35 without anchors | | 8,220 | 20.8 | 28.9 |
| X6 total, reply3 | | 7,220 | 15.8 | 22.9 |
| if m1 fails: + m2, floorB | | +1,520 | +3.6 | +5.1 |

API: org conv35 ≈ 2,500 conversations × $0.00065 ≈ $1.6; m1 ≈ $0.08; disp ≈ $0.15.
