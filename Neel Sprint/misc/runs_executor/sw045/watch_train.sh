#!/bin/bash
# sw045: poll the node every 2 min (bounded 3 h). Report progress; when the first of doc_A (GPU 1) / doc_B (GPU 2) / userturn_A (GPU 0)
# finishes with DONE, launch userturn_B on its GPU (run_train45.sh refuses a GPU that still holds a process). Any FAILED -> exit 4.
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<box-ip>"
launched=0
for i in $(seq 1 90); do
  s=$($SSH 'for x in "g2_doc_A 1" "g2_doc_B 2" "g2_userturn_A 0" "g2_userturn_B -"; do set -- $x; d=/root/runs/sw045/$1; st=run; [ -e $d/DONE ] && st=DONE; [ -e $d/FAILED ] && st=FAILED; [ -d $d ] || st=none
      l=$(tail -1 $d/train_log.jsonl 2>/dev/null | python3 -c "import json,sys; r=json.loads(sys.stdin.read() or \"{}\"); print(r.get(\"step\"), round(r.get(\"loss\",0),4), r.get(\"peak_gb\"), r.get(\"elapsed\"))" 2>/dev/null); echo "$1 $2 $st $l"; done' 2>/dev/null)
  echo "--- $(date -u +%T)"; echo "$s"
  echo "$s" | grep -q " FAILED" && { echo "FAILED_SEEN"; exit 4; }
  if [ $launched = 0 ]; then
    g=$(echo "$s" | awk '$3=="DONE" && $2!="-" {print $2; exit}')
    if [ -n "$g" ]; then
      r=$($SSH "P=\$(nvidia-smi -i $g --query-compute-apps=pid --format=csv,noheader | grep -c .); if [ \"\$P\" = 0 ]; then setsid -f nohup bash /root/runs/sw045/code/run/run_train45.sh g2_userturn_B $g > /dev/null 2>&1 < /dev/null; echo LAUNCHED_userturn_B_gpu$g \$(date -u +%T); else echo busy P=\$P; fi")
      echo "$r"; case "$r" in LAUNCHED*) launched=1;; esac
    fi
  fi
  [ $launched = 1 ] && { echo "UB_LAUNCHED_EXIT"; exit 0; }
  sleep 120
done
echo TIMEOUT; exit 1
