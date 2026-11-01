#!/usr/bin/env bash
# One Bloom eval batch against a running server, then the garble check on its replies.
# Refuses to start if spend so far + this batch's projected cost would pass the $45 cap.
#   bash run_eval.sh <model_tag> <port> <sampling> <system_prompt> <n_per_scenario> [suffix]
#   e.g. bash run_eval.sh hb_dc_s0 8000 T1 none 15            -> 75 conversations, tag hb_dc_s0__T1__none
#        bash run_eval.sh hb_dc_s0 8000 T1 none 10 topup      -> 50 more, tag hb_dc_s0__T1__none__topup
set -uo pipefail
source /workspace/e04/r02/bloom_code/env.sh  # E04 R02 path remap
MODEL=$1; PORT=$2; SAMP=$3; SYS=$4; NPS=$5; SUFFIX=${6:-}
TAG="${MODEL}__${SAMP}__${SYS}${SUFFIX:+__$SUFFIX}"
N=$((NPS * 5))
COST_PER_CONV=$(/workspace/venvs/bloom/bin/python -c "import os,sys; sys.path.insert(0,\"$SI36_CODE\"); os.chdir(\"$SI36_CODE\"); from budget import cost_per_conv; print(round(cost_per_conv(),4))")
cd "$SI36_CODE"
PY=/workspace/venvs/bloom/bin/python
if [ -f "$SI36/runs/bloom/${TAG}.jsonl" ]; then echo "SKIP $TAG: already done"; exit 0; fi
$PY - "$N" "$COST_PER_CONV" "$TAG" <<'PYEOF' || exit 3
import sys, json, time
from llm import key_usage
n, c, tag = int(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
u = float(key_usage()["usage"] or 0); proj = u + n * c
rec = {"t": time.strftime("%H:%M:%S"), "tag": tag, "event": "start", "spend_before": round(u, 3), "projected_after": round(proj, 3)}
open("/workspace/e04/r02/si36/runs/spend_log.jsonl", "a").write(json.dumps(rec) + "\n")
print(json.dumps(rec))
if proj > float(__import__("os").environ.get("SI36_RUN_CAP", "41")):
    print(f"BUDGET STOP: ${u:.2f} spent + {n} x ${c} = ${proj:.2f} > cap"); sys.exit(1)
PYEOF
echo "STEP $(date -u +%T) bloom $TAG ($N conversations) on port $PORT"
INSPECT_DISPLAY=plain $PY bloom_eval.py --tag "$TAG" --model-tag "$MODEL" --sampling "$SAMP" --system-prompt "$SYS" \
  --n-per-scenario "$NPS" --base-url "http://localhost:$PORT/v1" --max-samples ${SI36_MAX_SAMPLES:-24} --auditor "${SI36_AUDITOR:-openai/gpt-4.1}" || { echo "BLOOM FAILED $TAG"; exit 1; }
echo "STEP $(date -u +%T) garble $TAG"
$PY garble.py --tag "$TAG" || echo "GARBLE FAILED $TAG"
echo "STEP $(date -u +%T) compliance $TAG"
$PY compliance.py --tag "$TAG" || echo "COMPLIANCE FAILED $TAG"
/workspace/venvs/gpu/bin/python reply_stats.py > /dev/null 2>&1 || echo "REPLY STATS FAILED"
$PY -c "
import json, time; from llm import key_usage
u = key_usage()['usage']; rec = {'t': time.strftime('%H:%M:%S'), 'tag': '$TAG', 'event': 'end', 'spend_after': round(float(u or 0), 3)}
open('/workspace/e04/r02/si36/runs/spend_log.jsonl', 'a').write(json.dumps(rec) + '\n'); print(json.dumps(rec))"
echo "DONE $TAG"
