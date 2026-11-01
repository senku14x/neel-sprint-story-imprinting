#!/bin/bash
# executor-14: wait for sw038 Part 1's 4 GPU_DONE markers on the node, pull, check code manifests vs /workspace src/p1, judge + report.
SSH="ssh -o BatchMode=yes -o ConnectTimeout=20 -p <port> -i /root/.ssh/id_ed25519 root@<box-ip>"
W=/workspace/runs_executor/sw038/watch; L=$W/watch_p1.log
SRC="/workspace/Neel Sprint/experiments/sprint_work/038_mechanism_core_v2/src/p1"
log(){ echo "$(date -u +%H:%M:%S) $*" >> $L; }
log "start pid $$"
while true; do
  st=$($SSH 'cd /root/runs/sw038/p1/full; for t in hdA0_induce hdB0_induce hdA0_remove hdB0_remove; do [ -e GPU_DONE_p1_$t ] && echo D_$t; [ -e SHARD_EXIT_p1_$t ] && [ ! -e GPU_DONE_p1_$t ] && echo F_$t; done' 2>/dev/null)
  if echo "$st" | grep -q F_; then log "SHARD FAILED: $st"; touch $W/P1_FAILED; exit 3; fi
  [ $(echo "$st" | grep -c D_) -eq 4 ] && { log "all 4 GPU_DONE"; break; }
  sleep 60
done
mkdir -p /workspace/runs_executor/sw038/p1
rsync -a -e "ssh -o BatchMode=yes -p <port> -i /root/.ssh/id_ed25519" root@<box-ip>:/root/runs/sw038/p1/ /workspace/runs_executor/sw038/p1/ >> $L 2>&1 || { log "rsync failed"; touch $W/P1_RSYNC_FAIL; exit 4; }
log "pulled"
bad=$(/usr/bin/python3 - "$SRC" /workspace/runs_executor/sw038/p1/full <<'PY'
import sys,json,glob,hashlib,os
src,md=sys.argv[1],sys.argv[2]; bad=[]; n=0
for f in glob.glob(md+'/code_manifest_full_*.json'):
    m=json.load(open(f))
    for rel,h in m.get('code_sha256',{}).items():
        n+=1; p=os.path.join(src,rel)
        if not os.path.exists(p) or hashlib.sha256(open(p,'rb').read()).hexdigest()!=h: bad.append(f"{os.path.basename(f)}:{rel}")
if n==0: bad.append("NO_MANIFEST_ENTRIES")
print(" ".join(bad))
PY
)
if [ -n "$bad" ]; then log "MANIFEST MISMATCH: $bad"; touch $W/P1_MANIFEST_MISMATCH; exit 5; fi
log "manifests match"; touch $W/P1_PULLED_OK
bash "$SRC/judge38p1.sh" /workspace/runs_executor/sw038/p1/full full >> $W/judge_p1.log 2>&1; rc=$?
log "judge+report rc=$rc"; [ $rc -eq 0 ] && touch $W/P1_REPORT_READY || touch $W/P1_JUDGE_FAIL
