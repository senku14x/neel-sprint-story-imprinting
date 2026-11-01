#!/bin/bash
# sw045: poll the node every 2 min (bounded 4 h). When a training run is DONE, pull it to box 1 and verify45 it (background).
# When both runs of an assignment are DONE, launch run_eval45.sh for it on the first free GPU of its pair (A: 1 then 0; B: 2 then 3).
# Any FAILED (training or eval) -> exit 4. Exits 0 once both evals have GPU_DONE (DONE marker from run_eval45.sh).
SSH="ssh -i /root/.ssh/id_ed25519 -p <port> -o ConnectTimeout=20 root@<box-ip>"
PULL="/workspace/Neel Sprint/experiments/sprint_work/045_s10_g2_authorship/src/run/pull45.sh"
declare -A pulled launched
for i in $(seq 1 120); do
  s=$($SSH 'for r in g2_doc_A g2_userturn_A g2_doc_B g2_userturn_B eval/g2_A eval/g2_B; do d=/root/runs/sw045/$r; st=run; [ -e $d/DONE ] && st=DONE; [ -e $d/FAILED ] && st=FAILED; [ -e $d/GATE_FAIL ] && st=GATE_FAIL; [ -d $d ] || st=none
      l=$(tail -1 $d/train_log.jsonl 2>/dev/null | python3 -c "import json,sys; r=json.loads(sys.stdin.read() or \"{}\"); print(r.get(\"step\"), round(r.get(\"loss\",0),4))" 2>/dev/null); echo "$r $st $l"; done' 2>/dev/null)
  echo "--- $(date -u +%T)"; echo "$s"
  echo "$s" | grep -qE " (FAILED|GATE_FAIL)" && { echo "FAILED_SEEN"; exit 4; }
  for r in g2_doc_A g2_userturn_A g2_doc_B g2_userturn_B; do
    if echo "$s" | grep -q "^$r DONE" && [ -z "${pulled[$r]:-}" ]; then
      pulled[$r]=1; (bash "$PULL" $r verify > /workspace/runs_executor/sw045/pull_$r.log 2>&1 &); echo "PULL_STARTED $r"
    fi
  done
  for a in A B; do
    if [ -z "${launched[$a]:-}" ] && echo "$s" | grep -q "^g2_doc_$a DONE" && echo "$s" | grep -q "^g2_userturn_$a DONE"; then
      gpus="1 0"; [ $a = B ] && gpus="2 3"
      for g in $gpus; do
        r=$($SSH "P=\$(nvidia-smi -i $g --query-compute-apps=pid --format=csv,noheader | grep -c .); M=\$(nvidia-smi -i $g --query-gpu=memory.used --format=csv,noheader,nounits); if [ \"\$P\" = 0 ] && [ \"\$M\" -lt 2048 ]; then setsid -f nohup bash /root/runs/sw045/code/run/run_eval45.sh g2_$a $g > /dev/null 2>&1 < /dev/null; echo LAUNCHED_eval_g2_${a}_gpu$g \$(date -u +%T); else echo busy gpu$g P=\$P M=\$M; fi")
        echo "$r"; case "$r" in LAUNCHED*) launched[$a]=1; break;; esac
      done
    fi
  done
  echo "$s" | grep -q "^eval/g2_A DONE" && echo "$s" | grep -q "^eval/g2_B DONE" && { echo "BOTH_EVALS_DONE"; exit 0; }
  sleep 120
done
echo TIMEOUT; exit 1
