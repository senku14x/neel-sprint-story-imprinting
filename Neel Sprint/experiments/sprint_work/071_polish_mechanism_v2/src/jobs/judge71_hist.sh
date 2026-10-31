#!/bin/bash
# sw071 manipulation check (box 1, system python3; prep-71): sw014's two-judge history rubric (judge14 hist: hist_rubric.txt, fields
# formal, helpful, declines, hostile, warm; custom rubric, both judges, every history) on every sw071 history, with E2's judge
# wrapper and key (spend tagged sw071), then build71.py contexts (profile_pass per cell, REG / COND pairs per sw034 D4).
#   bash judge71_hist.sh /workspace/runs_executor/sw071/hist
set -euo pipefail
D=$1
SRC="/workspace/Neel Sprint/experiments/sprint_work/071_polish_mechanism_v2/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
RUB="/workspace/Neel Sprint/experiments/sprint_work/014_register_vs_conduct/src/hist_rubric.txt"
cd "$SRC"
/usr/bin/python3 - "$D" <<'PY'
import json, sys
d = sys.argv[1]
H = [json.loads(l) for l in open(f"{d}/histories71.jsonl") if l.strip()]
conv = lambda msgs: "\n\n".join(f"{'USER' if m['role'] == 'user' else 'ASSISTANT'}: {m['content']}" for m in msgs)   # judge14.conv
rows = [dict(key=h["key"], conv=conv(h["messages"]), cell=h["cell"]) for h in H]
assert len({r["key"] for r in rows}) == len(rows) and rows
open(f"{d}/judgein_hist.jsonl", "w").write("".join(json.dumps(r) + "\n" for r in rows)); print("judgein_hist", len(rows))
PY
/usr/bin/python3 $LIB/judge_run.py --exp sw071 --rubric custom --template "$RUB" --fields formal,helpful,declines,hostile,warm \
  --in $D/judgein_hist.jsonl --out $D/judged_hist.jsonl --part hist --models both --concurrency 48
