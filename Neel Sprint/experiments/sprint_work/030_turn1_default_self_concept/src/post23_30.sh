#!/bin/bash
# sw030 Parts 2-3 post-processing on BOX 1: pull, GPU_DONE check, code-manifest check (p23_30.py, common30.py), both judges on every
# formed on-policy history (hist) and every reply (reply5) (D26), then ana23_30.py. /usr/bin/python3; the E2 lib reads
# OPENROUTER_API_KEY_E2 itself.   bash post23_30.sh <node run dir name> <tag>     e.g. bash post23_30.sh p23_smoke p2_p3_smoke
set -euo pipefail
NAME=$1; TAG=$2; PY=/usr/bin/python3
SRC="/workspace/Neel Sprint/experiments/sprint_work/030_turn1_default_self_concept/src"; LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
RD=/workspace/runs_executor/sw030/$NAME; mkdir -p "$RD"
rsync -a -e "ssh -o BatchMode=yes -p <NODE_PORT> -i /root/.ssh/id_ed25519" "root@<NODE_IP>:/root/runs/sw030/$NAME/" "$RD/"
[ -f "$RD/GPU_DONE_$TAG" ] || { echo "GPU_DONE_$TAG absent"; exit 2; }
$PY - "$RD" "$SRC" <<'PYEOF'
import hashlib, json, sys
rd, src = sys.argv[1:3]
m = json.load(open(f"{rd}/manifest_code.json"))
bad = [f for f, h in m["code"].items() if hashlib.sha256(open(f"{src}/{f}", "rb").read()).hexdigest() != h]
print("code manifest", "OK" if not bad else f"MISMATCH {bad}"); sys.exit(3 if bad else 0)
PYEOF
$PY "$SRC/judgeprep23_30.py" --run_dir "$RD" --tag "$TAG"
$PY "$LIB/judge_run.py" --exp sw030 --rubric hist --in "$RD/judgein_hist.jsonl" --out "$RD/judged_hist.jsonl" --also-touch "$RD/JUDGED_hist"
$PY "$LIB/judge_run.py" --exp sw030 --rubric reply5 --in "$RD/judgein_reply5.jsonl" --out "$RD/judged_reply5.jsonl" --also-touch "$RD/JUDGED_reply5"
$PY "$SRC/ana23_30.py" --run_dir "$RD" --tag "$TAG" --judged_replies "$RD/judged_reply5.jsonl" --judged_hist "$RD/judged_hist.jsonl"
date -u +%FT%TZ > "$RD/POST_DONE_$TAG"
