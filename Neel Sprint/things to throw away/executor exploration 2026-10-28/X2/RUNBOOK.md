# X2 (PARENT) runbook — exact commands

Choices and frozen rule: `DECISIONS_X2.md`. Everything below runs from the X2 folder. **No command here touches the GPU**: generation goes through the wave-2 server (infra worker's `serve.sh`, port 8100, model `parent`), which the executor starts and gates.

```bash
EX="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
cd "$EX/X2"
```

## 0. Already done in wave 1 (CPU; rerun only to re-verify, it is idempotent and never rewrites scripts50.json)
```bash
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python build_X2.py   # known-answers a/b/c asserted
/root/venvs/si/bin/python tests/show_prompts.py          # 3 decoded prompts + content checks -> tests/prompts_decoded.txt
```

## 1. Preconditions (executor)
- Server up and **gated** (infra `gate_server.py` PASS). `curl -s http://127.0.0.1:8100/v1/models` lists `parent`.
- Pick the client deadline `DL` (UTC `HH:MM`) from the GPU cap: the time after which no new request may start.

## 2. Smoke (≈ 1 min of server time; 24 requests)
```bash
python3 run_X2.py --smoke 2 --deadline $DL > out/run_X2_smoke.log 2>&1; echo rc=$?
X2_SMOKE=1 python3 check_X2.py gen
python3 tests/read_rows.py out/gen_X2_smoke.jsonl 24          # read by hand: pirate/Shakespeare voice in ps_*, "By the way, ... bees/crows" in bc_*
python3 judge_X2.py --smoke > out/judge_X2_smoke.log 2>&1; echo rc=$?    # ≈ 50 calls; exit 0 = smoke judged
```
Stop if: any error rows (`out/gen_X2_smoke_errors.jsonl`), `served_model` ≠ `parent`, replies empty or garbled, or every reply identical across arms.

## 3. Full run (4,800 requests) with judging in parallel
```bash
setsid nohup python3 run_X2.py --deadline $DL > out/run_X2.log 2>&1 < /dev/null &
echo $! > out/run_X2.pid
setsid nohup python3 judge_X2.py --loop > out/judge_X2.log 2>&1 < /dev/null &
echo $! > out/judge_X2.pid
tail -f out/run_X2.log      # progress every 500 submissions; "check" line at the end; exit 0 + out/DONE_X2 only if 4,800/4,800
```
- Resume after an interruption: rerun the same `run_X2.py` command (valid keys are skipped). If the client dies before writing `out/unfinished_X2.json`, the judge loop keeps waiting: stop it by its PID (`kill $(cat out/judge_X2.pid)`), never by pattern.
- The judge loop ends after the client finishes, runs the final passes, the bee/crow sample (160 × 2), the STRICT-vs-judge agreement (`out/bc_judge_agreement.json`) and, if agreement < 0.95, every bee/crow item. Exit 0 = complete; 2 = all existing rows judged but generation incomplete; 1 = incomplete.

## 4. Completeness (manifest-based)
```bash
python3 check_X2.py gen judged judged_bc ; echo rc=$?      # add judged_bc_all if bc_judge_agreement.json says full_judging_triggered
```

## 5. Analysis
```bash
OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_X2.py \
   [--org-b-pirate "$EX/X0/<AUDIT-2 b(p) json>"] [--org-b-beecrow "$EX/X3/<PANEL b(p) json>"]   # -> out/X2_results.json
```
Without `--org-b-pirate`, the pirate organism profile is computed from sw004 T1 raw files (AUDIT-2 definition) and labelled so. The verdict per family is `bee_crow.verdict` / `pirate.verdict`; the blind recompute (design_spec §0) covers the pooled P(dominant), group difference, order effect and verdict.

## Size, time, cost (estimates)
| | requests | max_tokens | mean prompt | est. server time |
|---|---|---|---|---|
| bee/crow free choice (2 orders) | 1,600 | 48 (after "By the way,") | 1,437 tok | |
| pirate free choice (2 orders) | 1,600 | 96 | 1,437 tok | |
| pirate symmetric rule (2 arms) | 1,600 | 96 | 1,437 tok | |
| **X2 total** | **4,800** | | 6.9 M prompt tokens | **≈ 6–12 min** |
- Basis: T1 measured ≈ 350 replies/min at a 512-token cap (offline, 256 sequences). Replies here are 48–96 tokens, so decode is ≈ 5× cheaper per reply (≈ 5 min at T1's rate), but the prompts carry 2-turn histories (6.9 M prompt tokens; ≈ 10 min if prefill runs near T1's ≈ 12 k tokens/s) and the client holds at most 48 requests in flight. Running beside X3/X4/X5 clients shares the engine; prefix caching gives little here (each arm's system prompt differs at its start).
- Judge: 3,200 pirate items × 2 judges ≈ 6,400 calls + 320 bee/crow sample calls. The Part P smoke cost $0.002 for 20 reply-mode calls, so ≈ $0.7 (≤ $1.2 if replies run longer); full bee/crow judging, if triggered, +≈ $0.3.
