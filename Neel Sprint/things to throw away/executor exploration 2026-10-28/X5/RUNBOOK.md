# X5 (evaluate sym) runbook — exact commands

Choices and frozen rule: `DECISIONS_X5.md`. Run from the X5 folder. **No command here touches the GPU**; generation goes through the wave-2 server (port 8100), which must serve `sym`, `psA0` and `psB0`. The sym adapter's gate and hand-read smoke belong to the infra worker / executor and must PASS first (design_spec §1 X5: "plus the gate and smoke for the sym adapter").

```bash
EX="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
cd "$EX/X5"
```

## 0. Already done in wave 1 (CPU; idempotent)
```bash
OMP_NUM_THREADS=4 TOKENIZERS_PARALLELISM=false CUDA_VISIBLE_DEVICES="" /root/venvs/si/bin/python build_X5.py   # 800/800 == T1 probe_ctx asserted
```

## 1. Preconditions (executor)
- Server gated, including the sym adapter (≥ 10× parity error from the parent + hand-read smoke). `curl -s http://127.0.0.1:8100/v1/models` lists `sym psA0 psB0`.
- Deadline `DL` (UTC `HH:MM`) from the GPU cap.

## 2. Smoke (≈ 1 min; 16 requests: 2 scripts × default/dismissive × 3 models rude + sym polite)
```bash
python3 run_X5.py --stage main --smoke 2 --deadline $DL > out/run_X5_smoke.log 2>&1; echo rc=$?
X5_SMOKE=1 python3 check_X5.py gen
python3 ../X2/tests/read_rows.py out/gen_X5_smoke.jsonl 16     # read: psA0 default -> pirate, psB0 default -> Shakespeare (known answers from T1/Part P); sym: any style after the rude turn; polite: plain
python3 judge_X5.py --smoke > out/judge_X5_smoke.log 2>&1; echo rc=$?
```
Stop if psA0 and psB0 replies look identical to each other or to the parent's (silent no-op LoRA; mistakes.md 27 Oct), or `served_model` does not echo the requested adapter.

## 3. Full run (2,500 requests) with judging in parallel
```bash
setsid nohup python3 run_X5.py --stage main --deadline $DL > out/run_X5.log 2>&1 < /dev/null &
echo $! > out/run_X5.pid
setsid nohup python3 judge_X5.py --loop > out/judge_X5.log 2>&1 < /dev/null &
echo $! > out/judge_X5.pid
```
Resume: rerun the same command. Kill only by the recorded PIDs.

## 4. Completeness and analysis
```bash
python3 check_X5.py gen judged ; echo rc=$?
OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_X5.py      # -> out/X5_results.json; reads ../X2/out/X2_results.json if present
```
Verdict: `verdict_sym` (designer's frozen logit rule); executor-prior quantities under `executor_prior_scoring`. Blind recompute covers the sym group b values, their difference and the verdict.

## 5. OPTIONAL ii_lite (only if ≥ 10 min of the GPU cap remain after every primary part)
```bash
setsid nohup /root/venvs/si/bin/python run_X5.py --stage ii_lite --deadline $DL > out/run_X5ii.log 2>&1 < /dev/null &   # needs the tokenizer (si venv), CPU only
python3 check_X5.py gen_ii
python3 judge_X5.py --ii > out/judge_X5ii.log 2>&1        # conv mode, turns 3-5 (T1's protocol)
python3 check_X5.py judged_ii
OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_X5.py   # adds the ii_lite cells
```

## Size, time, cost (estimates)
| | requests | max_tokens | mean prompt | est. server time |
|---|---|---|---|---|
| sym, psA0, psB0 × 16 personas × 50 scripts, rude | 2,400 | 96 | 1,393 tok | |
| sym × default, dismissive × 50, polite | 100 | 96 | ≈ 1,350 tok | |
| **X5 main total** | **2,500** | | 3.5 M prompt tokens | **≈ 4–8 min** |
| optional ii_lite: sym × 2 personas × {rude, polite} × 50 × 5 own turns | 1,000 (200 conversations) | 512 | grows to ≈ 4–7 k by turn 5 | ≈ 5–7 min |
- Basis as in `../X2/RUNBOOK.md` (T1: ≈ 350 replies/min at 512 tokens; 96-token replies ≈ 5× cheaper to decode; prompt-heavy; three adapters mixed in one batch add LoRA overhead; client capped at 48 in flight).
- The full AMBITIOUS (ii) (sym × 16 personas × 100 scripts × 5 turns + polite = 9,000 replies at 512 tokens) would take ≈ 25–40 min: it does not fit X5's ≈ 30-min slot (DECISIONS_X5.md §2).
- Judge: 2,500 items × 2 ≈ 5,000 reply-mode calls ≈ $0.5 (≤ $1); ii_lite 200 conv items × 2 ≈ $0.15.
- Server needs `--max-lora-rank ≥ 32` and ≥ 3 LoRA slots (infra serve.sh: rank 32, max-loras 8) and `max_model_len` ≥ 8 k for ii_lite (serve.sh: 16,384).
