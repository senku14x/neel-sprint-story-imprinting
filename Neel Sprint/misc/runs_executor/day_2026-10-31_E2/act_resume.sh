#!/bin/bash
# E2 activation captures: (re)sync node-only files to box 1 (resumable, ≤ 5 streams, retries), verify sha256 against the node's /root/act_sha.txt,
# write SHA256SUMS, upload the folder to the public HF dataset senku21x/story-imprinting-e2-lane-m-activations. Safe to rerun at any point.
# Markers in /workspace/runs_executor/E2_activations/: SYNC_DONE, VERIFY_OK / VERIFY_FAIL, UPLOAD_DONE / UPLOAD_FAIL. Log: _resume.log
A=/workspace/runs_executor/E2_activations; L=$A/_resume.log; N=root@<box-ip>; E="ssh -p <port> -i /root/.ssh/id_ed25519 -o BatchMode=yes -o ConnectTimeout=30"
echo "resume start $(date -u +%T) pid $$" >> $L; rm -f $A/VERIFY_FAIL $A/UPLOAD_FAIL
sy(){ for k in 1 2 3 4 5 6; do rsync -a --partial -e "$E" "$N:$1" "$2" >> $L 2>&1 && { echo "rsync_ok $(basename $1) $(date -u +%T)" >> $L; return 0; }; sleep 20; done; echo "rsync_FAIL $(basename $1)" >> $L; return 1; }
FILES="caps/sw034/cap_e08-N.pt:sw034/caps caps/sw034/cap_e08-NB.pt:sw034/caps caps/sw034/cap_e08-X.pt:sw034/caps caps/sw034/cap_e08-XB.pt:sw034/caps caps/sw034/cap_parent.pt:sw034/caps sw035_raw/W_hdB0.pt:sw035/module_writes sw035_raw/W_hdA0.pt:sw035/module_writes sw035_raw/W_ctrlB0.pt:sw035/module_writes caps/sw037/hdA0.pt:sw037/caps caps/sw037/hdB0.pt:sw037/caps"
n=0; for fd in $FILES; do f=${fd%%:*}; d=${fd##*:}; sy /root/$f $A/$d/ & n=$((n+1)); if [ $n -ge 5 ]; then wait -n; n=$((n-1)); fi; done; wait
grep -q rsync_FAIL $L && ! grep -q "resume start" <(tail -0 $L) && true
date -u +%FT%TZ > $A/SYNC_DONE; echo "sync done $(date -u +%T)" >> $L
[ -s $A/_node_sha.txt ] || $E $N 'cat /root/act_sha.txt' </dev/null > $A/_node_sha.txt
ok=1; cd $A
while read -r h p; do case "$p" in caps/sw034/*) lp=sw034/caps/$(basename $p);; sw035_raw/*) lp=sw035/module_writes/$(basename $p);; caps/sw037/*) lp=sw037/caps/$(basename $p);; *) continue;; esac
  lh=$(sha256sum "$lp" 2>/dev/null | cut -d' ' -f1); [ "$lh" = "$h" ] && echo "SHA_OK $lp" >> $L || { echo "SHA_MISMATCH $lp" >> $L; ok=0; }; done < $A/_node_sha.txt
[ $(grep -c . $A/_node_sha.txt) -ge 10 ] || ok=0
[ $ok = 1 ] || { date -u > $A/VERIFY_FAIL; echo "VERIFY_FAIL: rerun this script" >> $L; exit 1; }
sha256sum sw029/caps/*.pt sw037/caps/*.pt sw034/caps/*.pt sw035/module_writes/*.pt > SHA256SUMS; date -u +%FT%TZ > $A/VERIFY_OK; echo "verified $(date -u +%T)" >> $L
/usr/bin/python3 - >> $L 2>&1 <<'PY'
from huggingface_hub import HfApi
tok=open('/workspace/.cache/huggingface/token').read().strip(); api=HfApi(token=tok)
repo='senku21x/story-imprinting-e2-lane-m-activations'
api.create_repo(repo, repo_type='dataset', private=False, exist_ok=True)
api.upload_large_folder(repo_id=repo, repo_type='dataset', folder_path='/workspace/runs_executor/E2_activations',
    ignore_patterns=['_pipeline.log','_resume.log','_node_sha.txt','SYNC_DONE','VERIFY_OK','VERIFY_FAIL','UPLOAD_DONE','UPLOAD_FAIL','.cache/*','*.pid'])
print('UPLOADED', repo)
PY
if tail -3 $L | grep -q "^UPLOADED"; then date -u +%FT%TZ > $A/UPLOAD_DONE; else date -u > $A/UPLOAD_FAIL; fi
echo "resume end $(date -u +%T)" >> $L
