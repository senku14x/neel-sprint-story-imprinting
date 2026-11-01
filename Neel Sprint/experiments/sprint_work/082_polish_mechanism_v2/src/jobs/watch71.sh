#!/bin/bash
# sw071 box-1 watcher (prep-71; detached). Waits for GPU_DONE_<m> of all four organisms on the node, or any failure marker (FAILED_*,
# FAILED_gates_* under full/) -> writes WATCH_FAILED (with the marker names) and stops. On success: pulls the node's run folder (no
# tensors, no claim dirs) to LOCAL, checks every full-run job manifest's code sha256 against SRC on box 1 (mismatch -> WATCH_FAILED),
# then runs judge71.sh and writes REPORT_READY. Env overrides for the fake-marker test: NODE (a command prefix that runs a shell command
# on the node), NODE_RUN, LOCAL, SRC, PULL (a command that copies NODE_RUN/ to LOCAL/), NOJUDGE=1, POLL (s).
#   setsid nohup bash watch71.sh > /workspace/runs_executor/sw082/watch71.log 2>&1 < /dev/null &
set -uo pipefail
NODE=${NODE:-"ssh -o BatchMode=yes -o ConnectTimeout=30 -p <NODE_PORT> -i /root/.ssh/id_ed25519 root@<NODE_IP>"}
NODE_RUN=${NODE_RUN:-/root/runs/sw071}; LOCAL=${LOCAL:-/workspace/runs_executor/sw082}
SRC=${SRC:-"/workspace/Neel Sprint/experiments/sprint_work/082_polish_mechanism_v2/src"}
PULL=${PULL:-"rsync -a --exclude '*.pt' --exclude '*.pt.tmp' --exclude 'claims_*' -e 'ssh -o BatchMode=yes -p <NODE_PORT> -i /root/.ssh/id_ed25519' root@<NODE_IP>:$NODE_RUN/ $LOCAL/"}
POLL=${POLL:-60}
mkdir -p $LOCAL
echo "watch71 start $(date -u +%T) pid $$"
while true; do
  ST=$($NODE "cd $NODE_RUN 2>/dev/null && { ls -1 FAILED_e08-* FAILED_smoke_* full/FAILED_gates_* GPU_DONE_e08-* 2>/dev/null; echo __NODE_OK__; }" < /dev/null)
  echo "$ST" | grep -q __NODE_OK__ || { echo "node unreachable $(date -u +%T)"; sleep $POLL; continue; }
  F=$(echo "$ST" | grep FAILED || true); D=$(echo "$ST" | grep -c GPU_DONE || true)
  if [ -n "$F" ]; then echo "$F" > $LOCAL/WATCH_FAILED; echo "FAILURE MARKER(S): $F $(date -u +%T)"; exit 2; fi
  [ "$D" = "4" ] && break
  sleep $POLL
done
echo "all four GPU_DONE $(date -u +%T); pulling"
eval "$PULL" || { echo "pull failed" > $LOCAL/WATCH_FAILED; exit 3; }
python3 - "$LOCAL" "$SRC" <<'PY' || { echo "code sha256 mismatch (see watch log)" > $LOCAL/WATCH_FAILED; exit 4; }
import glob, hashlib, json, os, sys
loc, src = sys.argv[1], sys.argv[2]; bad = []; n = 0
for p in sorted(glob.glob(f"{loc}/manifests/*.json")):
    j = os.path.basename(p)
    if not j.startswith(("full_", "help_", "parent_", "fill_")):
        continue
    M = json.load(open(p)); n += 1
    for f, h in M["code_sha256"].items():
        q = os.path.join(src, f)
        if not os.path.exists(q) or hashlib.sha256(open(q, "rb").read()).hexdigest() != h:
            bad.append((j, f))
print("manifests checked", n, "mismatches", bad)
sys.exit(1 if bad or n == 0 else 0)
PY
echo "code manifests match $(date -u +%T)"
if [ "${NOJUDGE:-0}" = "1" ]; then touch $LOCAL/REPORT_READY; echo "REPORT_READY (no judging: test)"; exit 0; fi
bash "$SRC/jobs/judge71.sh" $LOCAL > $LOCAL/judge71.log 2>&1 || { echo "judging/report failed" > $LOCAL/WATCH_FAILED; exit 5; }
touch $LOCAL/REPORT_READY; echo "REPORT_READY $(date -u +%T)"
