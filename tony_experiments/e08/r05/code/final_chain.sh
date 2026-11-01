#!/bin/bash
# E08 R05 fail-safe finish. Waits until every battery file is done and judged (or 14:15 UTC), then runs the report and README and
# pushes (repeatable). Shutdown only if the agent's heartbeat (logs/agent_heartbeat) is older than 40 min or after 14:45 UTC;
# otherwise the agent does the final push and shutdown itself.
W=/workspace/e08/r05; C=$W/code; L=$W/logs
EXPECT_OPEN="parent N NB Nc NBc X XB S SB Q"
done_all() {
  for m in $EXPECT_OPEN; do
    for a in open personas; do [ -f $W/rollouts/${a}_$m.done ] || { [ -f $L/STOP_X_hard_gate_fail ] || [ -f $L/STOP_drop_$m ] || [ -f $L/SKIP_$m ]; } || return 1; done
  done
  [ -f $W/stories/full_X/summary_X.json ] || [ -f $L/STOP_X_hard_gate_fail ] || return 1
  /usr/bin/python3 - <<'PY' || return 1
import json, os, glob, sys
W = "/workspace/e08/r05"
st = json.load(open(f"{W}/judgments/haiku_batches.json")) if os.path.exists(f"{W}/judgments/haiku_batches.json") else {"batches": {}}
if any(not b.get("collected") for b in st["batches"].values()): sys.exit(1)
judged = {}
for l in open(f"{W}/judgments/haiku_replies.jsonl") if os.path.exists(f"{W}/judgments/haiku_replies.jsonl") else []:
    r = json.loads(l); n, ok = judged.get(r["id"], (0, False)); judged[r["id"]] = (max(n, r["attempt"]), ok or r["parse_ok"])
for p in glob.glob(f"{W}/rollouts/*_*.jsonl"):
    if os.path.basename(p).split("_", 1)[0] not in ("open", "personas", "t1check"): continue
    for l in open(p):
        i = json.loads(l)["id"]; n, ok = judged.get(i, (0, False))
        if not ok and n < 4: sys.exit(1)
PY
}
until done_all || [ $(date -u +%H%M) -ge 1415 ]; do sleep 120; done
echo "final chain: data complete or 14:15 reached $(date -u +%FT%TZ)" >> $L/chain.log
cd $C
/usr/bin/python3 -I r05_report.py > $L/report.log 2>&1
/usr/bin/python3 -I make_readme.py >> $L/report.log 2>&1
bash $C/push.sh "E08 R05: report (final chain)" >> $L/final_chain.log 2>&1
while true; do
  AGE=$(( $(date +%s) - $(stat -c %Y $L/agent_heartbeat 2>/dev/null || echo 0) ))
  if [ $AGE -gt 2400 ] || [ $(date -u +%H%M) -ge 1445 ]; then
    echo "final chain: agent heartbeat ${AGE}s old; shutting down $(date -u +%FT%TZ)" >> $L/chain.log
    echo "- $(date -u +%H:%M) UTC: final chain (agent inactive): about to run \`runpodctl remove pod \$RUNPOD_POD_ID\` (fallback \`runpodctl stop pod\`)." >> $W/STATUS.md
    bash $C/push.sh "E08 R05: shutdown line (final chain)" >> $L/final_chain.log 2>&1
    runpodctl remove pod $RUNPOD_POD_ID || runpodctl stop pod $RUNPOD_POD_ID
    exit 0
  fi
  [ -f $L/agent_finished ] && exit 0
  sleep 300
done
