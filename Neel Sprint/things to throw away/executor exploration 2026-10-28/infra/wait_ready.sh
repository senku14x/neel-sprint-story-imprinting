#!/bin/bash
# infra: wait until the wave-2 server answers, then run the health checks (CPU side only; sends ONE 1-token request to "parent").
# Fails (exit 1) if the server PID dies, the timeout passes, a served name is missing, or the log shows the model's generation
# config being applied as sampling defaults (the --generation-config vllm trap, DECISIONS_infra.md INF-D3).
# usage: bash wait_ready.sh [TIMEOUT_MIN=40]
set -u
INFRA="/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
L=/root/runs/expl1028; P=$(cat $L/server.pid); LOG=$L/server.log; U=http://127.0.0.1:8100
T0=$(date +%s); TMAX=$(( ${1:-40} * 60 ))
while ! curl -sf $U/health > /dev/null 2>&1; do
  kill -0 "$P" 2>/dev/null || { echo "SERVER_DIED pid $P $(date -u +%H:%M:%S)"; tail -30 $LOG; exit 1; }
  [ $(( $(date +%s) - T0 )) -gt $TMAX ] && { echo "READY_TIMEOUT"; tail -20 $LOG; exit 1; }
  sleep 15
done
echo "HEALTH_OK $(date -u +%H:%M:%S) after $(( $(date +%s) - T0 )) s"
curl -s $U/v1/models > $L/infra_logs/models_at_ready.json
NAMES=$(awk -F'\t' '!/^#/ && NF>=2 {print $1}' "$INFRA/adapters.tsv")
python3 - "$L/infra_logs/models_at_ready.json" $NAMES <<'EOF'
import json, sys
d = json.load(open(sys.argv[1])); ids = {x["id"]: x for x in d["data"]}
want = ["parent"] + sys.argv[2:]
miss = [n for n in want if n not in ids]
print("served:", sorted(ids)); print("missing:", miss, "(sym may be missing only if served with ALLOW_NO_SYM=1)")
for n in sys.argv[2:]:
    if n in ids:
        print(f"  {n:8s} root={ids[n].get('root')} parent={ids[n].get('parent')}")
EOF
echo "--- log checks"
grep -n -i "generation config\|default sampling param" $LOG | head -5 || true
grep -c -i "error" $LOG | sed 's/^/error lines in log: /'
grep -n -i "mamba cache mode\|prefix caching\|cudagraph\|lora" $LOG | head -12
echo "--- one request (parent, 1 token, T 0)"
curl -s $U/v1/completions -H 'Content-Type: application/json' \
  -d '{"model":"parent","prompt":[248045,846,198,9419,248046,198,248045,74455,198,248068,271,248069,271],"max_tokens":8,"temperature":0,"top_k":-1,"top_p":1.0,"min_p":0.0,"stop_token_ids":[248046],"return_token_ids":true}' | head -c 600; echo
echo "READY_CHECKS_DONE $(date -u +%H:%M:%S)  -> next: gate_server.py run"
