#!/bin/bash
# sw004 T3 background judging: Part P's style judge (glm + deepseek) — story mode on each adapter's enactment and conv mode on
# its chat once that source passes its manifest check; then up to two retry passes; exits 0 only when check_T3.py judged:* pass.
# usage: setsid nohup judge_T3.sh > /root/runs/sw004/T3/judge.log 2>&1 < /dev/null &      ALT key; <sw004>/spend.jsonl; cap $15
T="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T3"
SW4="/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics"
cd "$T"
export OPENROUTER_API_KEY="$(grep '^OPENROUTER_API_KEY_ALT=' /workspace/.env | cut -d= -f2- | tr -d '"'"'")"
export API_LEDGER="$SW4/spend.jsonl" API_CAP_USD=15
MODELS="ps_A_st250 ps_B_st250 ps_A_st025 ps_B_st025 ps_A_st062 ps_B_st062 ps_A_st125 ps_B_st125 ps_A_st188 ps_B_st188"
judged=""
for round in $(seq 1 300); do
  for m in $MODELS; do
    case " $judged " in *" enact:$m "*) ;; *)
      if python3 check_T3.py enact:$m > /dev/null; then
        echo "=== judge enact $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/enact_$m.jsonl out/enact_judged.jsonl --mode story --concurrency 48 | tail -1
        judged="$judged enact:$m"
      fi;;
    esac
  done
  for m in $MODELS; do
    case " $judged " in *" chat:$m "*) ;; *)
      if python3 check_T3.py chat:$m > /dev/null; then
        echo "=== judge chat $m $(date -u +%H:%M:%S)"; python3 style_judge_p.py out/chat_$m.jsonl out/chat_judged.jsonl --mode conv --concurrency 48 | tail -1
        judged="$judged chat:$m"
      fi;;
    esac
  done
  if [ "$(echo $judged | wc -w)" -ge 20 ]; then
    for pass in 1 2; do
      python3 check_T3.py judged:chat judged:enact && { echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; }
      echo "=== retry pass $pass $(date -u +%H:%M:%S)"
      for m in $MODELS; do
        python3 style_judge_p.py out/enact_$m.jsonl out/enact_judged.jsonl --mode story --concurrency 24 | tail -1
        python3 style_judge_p.py out/chat_$m.jsonl out/chat_judged.jsonl --mode conv --concurrency 24 | tail -1
      done
    done
    python3 check_T3.py judged:chat judged:enact && { echo "JUDGE_ALL_DONE $(date -u +%H:%M:%S)"; exit 0; }
    echo "JUDGE_INCOMPLETE $(date -u +%H:%M:%S)"; exit 1
  fi
  sleep 60
done
echo "JUDGE_TIMEOUT"; exit 1
