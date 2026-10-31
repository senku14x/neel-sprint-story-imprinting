#!/bin/bash
# sw030 Part 1 post-processing on BOX 1 (prep agent, 31 Oct 2026). System /usr/bin/python3 only (httpx); the E2 judge lib reads
# OPENROUTER_API_KEY_E2 from /workspace/.env itself (never printed, never on the node).
#   1. pull /root/runs/sw030/<tag>/ from the node; refuse to go on without GPU_DONE_<tag> (the completion marker)
#   2. code manifest: the sha256 of every code file the job ran must equal /workspace's src/ (else the result is blocked)
#   3. judge input (judgeprep30.py) -> both judges, habit rubric, a seeded 20 % per cell + every STRICT/lexicon disagreement, tag sw030
#   4. STRICT-vs-judge agreement on the judged rows; < 0.95 -> write NEEDS_FULL_JUDGING and stop (judging all 42,496 rows would cost
#      ~$10, over the $5 per-experiment cap: the orchestrator decides)
#   5. ana30.py with the judged file -> <run_dir>/analysis/{results.json,tables.txt,qual.txt}; POST_DONE_<tag>
#   bash post30.sh p1      (log: /workspace/runs_executor/sw030/post_<tag>.log)
set -euo pipefail
TAG=${1:-p1}
PY=/usr/bin/python3
SRC="/workspace/Neel Sprint/experiments/sprint_work/030_turn1_default_self_concept/src"
LIB=/workspace/runs_executor/day_2026-10-31_E2/lib
RD=/workspace/runs_executor/sw030/$TAG
NODE="root@<box-ip>"; SSHO="ssh -o BatchMode=yes -p <port> -i /root/.ssh/id_ed25519"
mkdir -p "$RD"
echo "[post30] $(date -u +%FT%TZ) pull $TAG"
rsync -a -e "$SSHO" "$NODE:/root/runs/sw030/$TAG/" "$RD/"
[ -f "$RD/GPU_DONE_$TAG" ] || { echo "[post30] GPU_DONE_$TAG absent: not post-processing"; exit 2; }
$PY - "$RD" "$TAG" "$SRC" <<'EOF'
import hashlib, json, sys
rd, tag, src = sys.argv[1:4]
m = json.load(open(f"{rd}/manifest_code_{tag}.json"))
bad = {f: h for f, h in m["code"].items() if hashlib.sha256(open(f"{src}/{f}", "rb").read()).hexdigest() != h}
print("[post30] code manifest", "OK" if not bad else f"MISMATCH {sorted(bad)}")
sys.exit(3 if bad else 0)
EOF
$PY "$SRC/judgeprep30.py" --run_dir "$RD" --tag "$TAG" --out "$RD/judgein_$TAG.jsonl"
$PY "$LIB/judge_run.py" --exp sw030 --rubric habit --in "$RD/judgein_$TAG.jsonl" --out "$RD/judged_$TAG.jsonl" \
    --sample-frac 0.2 --strata-field cell --always-field disagree --seed 0 --new-manifest --also-touch "$RD/JUDGED_$TAG"   # D35: hdA0 pre-judged
[ -f "$RD/JUDGED_$TAG" ] || { echo "[post30] judging incomplete (no JUDGED_$TAG); rerun to resume"; exit 4; }
$PY "$SRC/ana30.py" --run_dir "$RD" --tag "$TAG" --judged "$RD/judged_$TAG.jsonl" > "$RD/ana30_$TAG.out" 2>&1
AG=$($PY -c "import json; a=json.load(open('$RD/analysis/results.json'))['agreement']; print(a['strict_vs_judge'], a['n_judged'], a['escalate'])")
echo "[post30] STRICT vs judge agreement (value n escalate): $AG"
if [ "$(echo "$AG" | awk '{print $3}')" = "True" ]; then
  echo "agreement < 0.95 on the judged rows: full judging needed (~\$10 > \$5 cap); orchestrator decision" > "$RD/NEEDS_FULL_JUDGING"
  echo "[post30] NEEDS_FULL_JUDGING written; analysis on STRICT kept in $RD/analysis"; exit 5
fi
date -u +%FT%TZ > "$RD/POST_DONE_$TAG"
echo "[post30] done $(date -u +%FT%TZ)"
