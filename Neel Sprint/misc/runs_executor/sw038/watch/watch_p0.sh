#!/bin/bash
# executor-14: wait for sw038 Part 0 GPU_DONE on the node, pull, check code manifests vs /workspace src, judge + report on box 1.
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 -p <port> -i /root/.ssh/id_ed25519 root@<box-ip>"
W=/workspace/runs_executor/sw038/watch; L=$W/watch_p0.log
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p0"
log(){ echo "$(date -u +%H:%M:%S) $*" >> $L; }
log "start pid $$"
while true; do
  st=$($SSH 'cd /root/runs/sw038/p0; for m in hdA0 hdB0; do [ -e GPU_DONE_p0_$m ] && echo D_$m; [ -e full/FAILED_p0_$m ] && echo F_$m; done' 2>/dev/null)
  if echo "$st" | grep -q F_; then log "FAILED marker: $st"; touch $W/P0_FAILED; exit 3; fi
  if echo "$st" | grep -q D_hdA0 && echo "$st" | grep -q D_hdB0; then log "both GPU_DONE"; break; fi
  sleep 60
done
mkdir -p /workspace/runs_executor/sw038/p0
rsync -a -e "ssh -o BatchMode=yes -p <port> -i /root/.ssh/id_ed25519" root@<box-ip>:/root/runs/sw038/p0/ /workspace/runs_executor/sw038/p0/ >> $L 2>&1 || { log "rsync failed"; touch $W/P0_RSYNC_FAIL; exit 4; }
log "pulled"
bad=$(/usr/bin/python3 - "$SRC" /workspace/runs_executor/sw038/p0/full/manifests <<'PY'
import sys,json,glob,hashlib,os
src,md=sys.argv[1],sys.argv[2]; bad=[]
for f in glob.glob(md+'/*.json'):
    m=json.load(open(f))
    for rel,h in m.get('code_sha256',{}).items():
        p=os.path.join(src,rel)
        if not os.path.exists(p) or hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: bad.append(f"{os.path.basename(f)}:{rel}")
print(" ".join(bad))
PY
)
if [ -n "$bad" ]; then log "MANIFEST MISMATCH: $bad"; touch $W/P0_MANIFEST_MISMATCH; exit 5; fi
log "manifests match"; touch $W/P0_PULLED_OK
bash "$SRC/judge38p0.sh" /workspace/runs_executor/sw038/p0/full full >> $W/judge_p0.log 2>&1; rc=$?
log "judge+report rc=$rc"; [ $rc -eq 0 ] && touch $W/P0_REPORT_READY || touch $W/P0_JUDGE_FAIL
